"""How often does GPT-4o-mini use a strict reading of a direction?

Counts answers containing phrases such as "directly west", "different
continents" or "not meaningful" in its geography pairs, by whether the pair is
flagged and by which question of the pair (YES-correct or NO-correct) was asked.
A regex, so it misses paraphrases; the comparison between sides is the point.

Writes results/strict_reading.json.
"""

import json
import re
from pathlib import Path

import pandas as pd

from openrouter import load_cache

ROOT = Path(__file__).resolve().parents[1]
STRICT = re.compile(
    r"directly (?:north|south|east|west)|due (?:north|south|east|west)|different continents?|"
    r"not (?:in the same|on the same)|(?:not|isn't) (?:meaningful|applicable)|"
    r"in any (?:meaningful|practical) sense|cannot be (?:said to be|considered) (?:north|south|east|west)",
    re.I)


def main(model="openai/gpt-4o-mini"):
    slug = model.replace("/", "_")
    resp = load_cache(ROOT / "data" / "responses" / "base" / f"{slug}.jsonl")
    lab = pd.read_json(ROOT / "data" / "responses" / "base" / f"{slug}.labels.jsonl", lines=True)
    lab = lab.set_index("rid").label
    pt = pd.read_csv(ROOT / "results" / "pairs_base.csv")
    pt = pt[(pt.model_id == model) & pt.prop_id.str.contains(r"-(?:lat|long)$")]
    rows = []
    for r in pt.itertuples():
        for qid, ans in [(r.qid_y, "YES"), (r.qid_n, "NO")]:
            for i in range(10):
                rid = f"{qid}__{i}"
                if rid in resp:
                    rows.append({"flag": r.unf, "correct_answer": ans, "label": lab.get(rid),
                                 "strict": bool(STRICT.search(resp[rid]["content"]))})
    d = pd.DataFrame(rows)
    out = {}
    for flag in [True, False]:
        for ans in ["YES", "NO"]:
            g = d[(d.flag == flag) & (d.correct_answer == ans)]
            out[f"{'flagged' if flag else 'unflagged'}_{ans}_question"] = {
                "answers": int(len(g)), "strict_rate": float(g.strict.mean())}
    json.dump(out, (ROOT / "results" / "strict_reading.json").open("w"), indent=2)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
