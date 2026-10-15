"""What do the answers in flagged pairs actually say?

For every answer to both questions of each flagged pair (our base run), an
extractor model reads the answer and reports:
  stated_order: which entity the answer's own stated values put higher
                (A_higher / B_higher / equal / none), where "higher" means
                larger, later, further north or further east;
  uncertain:    whether the answer says it is unsure, guessing or lacks data.
We compare stated_order with the true order and with the YES/NO label. Each
wrong answer then falls into one of three kinds:
  wrong facts       the stated values are in the wrong order and the answer follows them;
  ignores facts     the stated values are in the right order but the answer does not follow;
  no comparison     the answer states no usable values (e.g. "different continents").
Because the same two entities appear in both questions of a pair, we can also
ask whether the stated order changes with the question order.

Usage: python src/cited_facts.py openai/gpt-4o-mini meta-llama/llama-3.3-70b-instruct
"""

import asyncio
import json
import sys
from pathlib import Path

import pandas as pd

from openrouter import complete_reply, load_cache, run_requests
from questions import load_questions

ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = "anthropic/claude-haiku-5.5"

PROMPT = """Below is a question comparing two entities, A and B, on one property, and a model's answer to it.

Entity A: {a}
Entity B: {b}
Property compared: {prop}
Question: {q}

Answer:
<answer>
{text}
</answer>

Read only what the answer states. Do not use your own knowledge and do not correct the answer.

1. stated_order: Using only values or positions that the answer itself gives for A and B on this property ({prop}), which entity does the answer place higher, where higher means {higher}? Statements about a different property (for example north/south when the property is east/west) do not count. Reply A_higher, B_higher, equal, or none (none if the answer gives nothing that orders A and B on this property).
2. other_property: Does the answer base its conclusion mainly on a different property than {prop}? Reply true or false.
3. uncertain: Does the answer say it is unsure, guessing, lacks information, or cannot verify? Reply true or false.

Reply with JSON only: {{"stated_order": "...", "other_property": true/false, "uncertain": true/false}}"""

PROPERTY = {  # prop suffix -> (description, meaning of "higher")
    "lat": ("latitude (north-south position)", "further north"),
    "long": ("longitude (east-west position)", "further east"),
    "area": ("area", "larger area"),
    "book-length": ("number of pages", "more pages"),
    "movie-length": ("runtime", "longer runtime"),
    "release": ("release date", "released later"),
    "pubdate": ("publication date", "published later"),
    "person-age": ("age at death", "older at death"),
    "person-birth": ("birth date", "born later"),
    "person-death": ("death date", "died later"),
}


def prop_info(prop_id):
    for k, v in PROPERTY.items():
        if prop_id.endswith(k):
            return v
    raise KeyError(prop_id)


def higher_entity(row):
    """Which of x/y has the higher true value."""
    return "x" if row.x_value > row.y_value else "y"


def main(models):
    qs = load_questions().set_index("qid")
    pairs = pd.read_csv(ROOT / "results" / "pairs_base.csv")
    out_rows = []
    for model in models:
        slug = model.replace("/", "_")
        flagged = pairs[(pairs.model_id == model) & pairs.unf]
        resp = load_cache(ROOT / "data" / "responses" / "base" / f"{slug}.jsonl")
        labels = pd.read_json(ROOT / "data" / "responses" / "base" / f"{slug}.labels.jsonl", lines=True)
        labels = labels.set_index("rid").label
        reqs, meta = [], {}
        for pr in flagged.itertuples():
            for qid in [pr.qid_y, pr.qid_n]:
                q = qs.loc[qid]
                for i in range(10):
                    rid = f"{qid}__{i}"
                    if rid not in resp:
                        continue
                    text = resp[rid]["content"]
                    prop, higher = prop_info(q.prop_id)
                    prompt = PROMPT.format(a=q.x_name, b=q.y_name, q=q.q_str.split("\n")[-1],
                                           text=text, prop=prop, higher=higher)
                    reqs.append((rid, [{"role": "user", "content": prompt}]))
                    meta[rid] = (pr, q, qid)
        cache = ROOT / "data" / "cited_facts" / f"{slug}.v2.jsonl"
        got = asyncio.run(run_requests(reqs, cache, EXTRACTOR,
                                       {"temperature": 0.0, "max_tokens": 1500},
                                       concurrency=100, tag=f"facts:{model}", valid=complete_reply))
        for rid, (pr, q, qid) in meta.items():
            if rid not in got:
                continue
            raw = got[rid]["content"]
            try:
                d = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
            except ValueError:
                continue
            # In the question "Is A <rel> B?", A is x. Map stated order to x/y.
            so = d.get("stated_order", "none")
            stated = {"A_higher": "x", "B_higher": "y"}.get(so, so)
            low_q = pr.qid_y if pr.p_correct_y < pr.p_correct_n else pr.qid_n
            label = labels.get(rid, "UNKNOWN")
            out_rows.append({
                "model": model, "pair": f"{pr.prop_id}|{pr.comparison}|{pr.pair_key}", "qid": qid, "rid": rid,
                "low_accuracy_question": qid == low_q, "answer": q.answer, "label": label,
                "correct": label == q.answer, "true_higher": higher_entity(q),
                "stated_higher": stated, "uncertain": bool(d.get("uncertain", False)),
                "other_property": bool(d.get("other_property", False)), "prop_id": q.prop_id,
            })
    df = pd.DataFrame(out_rows)
    df["facts_right"] = df.stated_higher == df.true_higher
    df["facts_wrong"] = df.stated_higher.isin(["x", "y"]) & ~df.facts_right
    df.to_csv(ROOT / "results" / "cited_facts.csv", index=False)

    df["kind"] = df.prop_id.str.contains(r"-(?:lat|long)$").map({True: "geography", False: "other"})
    summary = {}
    for (model, kind), g in df.groupby(["model", "kind"]):
        wrong = g[(~g.correct) & g.label.isin(["YES", "NO"])]
        lo, hi = g[g.low_accuracy_question], g[~g.low_accuracy_question]
        summary[f"{model} | {kind}"] = {
            "pairs": int(g.pair.nunique()), "answers": int(len(g)), "wrong_answers": int(len(wrong)),
            "wrong_states_wrong_order": float(wrong.facts_wrong.mean()),
            "wrong_states_right_order": float(wrong.facts_right.mean()),
            "wrong_states_no_order": float((~wrong.facts_wrong & ~wrong.facts_right).mean()),
            "wrong_uses_other_property": float(wrong.other_property.mean()),
            "wrong_says_unsure": float(wrong.uncertain.mean()),
            "all_answers_wrong_order_on_question_it_gets_wrong": float(lo.facts_wrong.mean()),
            "all_answers_wrong_order_on_question_it_gets_right": float(hi.facts_wrong.mean()),
        }
    json.dump(summary, (ROOT / "results" / "cited_facts.json").open("w"), indent=2)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
