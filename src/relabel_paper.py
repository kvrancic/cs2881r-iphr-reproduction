"""Separate the judge effect from the model effect.

For the four original models, take the paper's own released answers on our
1,014 pairs and label them with our labeller (strict rule, then Claude Haiku
5.5 with the paper's prompt). Comparing
  paper answers + paper labels   (the paper's run)
  paper answers + our labels     (judge changed, model fixed)
  our answers   + our labels     (our run)
splits each difference between the paper's run and ours into a part due to
the judge and a part due to the model or provider.

Writes results/relabel_paper.json.
"""

import asyncio
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import yaml

import iphr
import judge
from openrouter import complete_reply, run_requests
from questions import load_questions

ROOT = Path(__file__).resolve().parents[1]
RAW = ("https://raw.githubusercontent.com/jettjaniak/chainscope/"
       "bb128ac0f22dd60ab3d876a78e1c6c22fff7e830/chainscope/data")
CACHE = ROOT / "data" / "paper_answers"
MODELS = {  # ours -> file name in the paper's repository
    "openai/gpt-4o-mini": "openai__gpt-4o-mini.yaml",
    "meta-llama/llama-3.3-70b-instruct": "meta-llama__Llama-3.3-70B-Instruct.yaml",
    "deepseek/deepseek-chat": "deepseek__deepseek-chat.yaml",
    "google/gemini-2.5-flash": "google__gemini-2.5-flash-preview.yaml",
}


def fetch(sub):
    path = CACHE / "raw" / sub
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(f"{RAW}/{sub}", path)
    return path


def paper_label(r):
    if r["final_answer"] == "YES":
        return "YES"
    if r["final_answer"] == "NO":
        return "UNKNOWN" if r.get("equal_values") == "TRUE" else "NO"
    return "UNKNOWN"


def load_model(fname, sub_qids):
    """Paper answers and paper labels for our pairs: {rid: (qid, text, label)}."""
    jobs = []
    for qf in sorted((ROOT / "data" / "questions").glob("*/*.yaml")):
        base = f"instr-wm/T0.7_P0.9_M2000/{qf.parent.name}/{qf.stem}/{fname}"
        jobs += [f"cot_responses/{base}", f"cot_eval/{base}"]
    with ThreadPoolExecutor(16) as ex:
        paths = list(ex.map(fetch, jobs))
    out = {}
    for rp, ep in zip(paths[0::2], paths[1::2]):
        resp = yaml.safe_load(rp.open())["responses_by_qid"]
        ev = yaml.safe_load(ep.open())["results_by_qid"]
        for qid, rs in resp.items():
            if qid not in sub_qids:
                continue
            for uid, text in rs.items():
                lab = ev.get(qid, {}).get(uid)
                if lab is not None:
                    out[f"{qid}__{uid}"] = (qid, text, paper_label(lab))
    return out


def counts(rows, qs, model, col):
    df = pd.DataFrame(rows)
    c = df.pivot_table(index="qid", columns=col, values="rid", aggfunc="count", fill_value=0)
    for k in ["YES", "NO", "UNKNOWN"]:
        if k not in c:
            c[k] = 0
    c = c.rename(columns={"YES": "yes_count", "NO": "no_count", "UNKNOWN": "unknown_count"})
    c = c[["yes_count", "no_count", "unknown_count"]].reset_index()
    c["model_id"] = model
    return c.merge(qs[["qid", "prop_id", "comparison", "answer", "x_name", "y_name"]], on="qid")


def main():
    qs = load_questions()
    sub = pd.read_csv(ROOT / "data" / "subsample_pairs.csv")
    sub_qids = set(sub.qid_yes) | set(sub.qid_no)
    res = {}
    tables = []
    for model, fname in MODELS.items():
        answers = load_model(fname, sub_qids)
        parsed = {rid: judge.parse(t) for rid, (_, t, _) in answers.items()}
        reqs = [(rid, [{"role": "user", "content": judge.JUDGE_PROMPT.replace("{response}", t)}])
                for rid, (_, t, _) in answers.items() if parsed[rid] is None]
        got = asyncio.run(run_requests(reqs, CACHE / f"{model.replace('/', '_')}.judge.jsonl",
                                       judge.JUDGE_MODEL, {"temperature": 0.0, "max_tokens": 2000},
                                       concurrency=100, tag=f"relabel:{model}", valid=complete_reply))
        rows = []
        for rid, (qid, _, plab) in answers.items():
            ours = parsed[rid] or (judge.judge_label(got[rid]["content"]) if rid in got else "UNKNOWN")
            rows.append({"rid": rid, "qid": qid, "paper": plab, "ours": ours})
        df = pd.DataFrame(rows)
        tables.append(counts(rows, qs, model, "ours"))
        flags = {}
        for col in ["paper", "ours"]:
            pt = iphr.pair_table(counts(rows, qs, model, col))
            pt["unf"] = iphr.flag_pairs(pt)
            flags[col] = pt.set_index("pair_key").unf
        both = pd.concat(flags, axis=1)
        res[model] = {
            "answers": int(len(df)),
            "label_agreement": float((df.paper == df.ours).mean()),
            "routed_to_judge": int(len(reqs)),
            "flags_paper_labels": int(both.paper.sum()),
            "flags_our_labels": int(both.ours.sum()),
            "flags_in_both": int((both.paper & both.ours).sum()),
            "unknown_rate_paper_labels": float((df.paper == "UNKNOWN").mean()),
            "unknown_rate_our_labels": float((df.ours == "UNKNOWN").mean()),
            "confusion": {f"{a}->{b}": int(n) for (a, b), n in
                          df.groupby(["paper", "ours"]).size().items() if a != b},
        }
        print(model, json.dumps(res[model]))
    json.dump(res, (ROOT / "results" / "relabel_paper.json").open("w"), indent=2)
    # Per-question counts of the paper's answers under our labels, for noise_models.py.
    pd.concat(tables).to_csv(ROOT / "results" / "paper_answers_our_labels.csv", index=False)


if __name__ == "__main__":
    main()
