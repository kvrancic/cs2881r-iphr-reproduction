"""Does the model know the values behind the pairs it gets flagged on?

For every entity in the 330 non-geography pairs of our sample, ask the model
for the value directly, with no comparison and no order (3 samples,
temperature 0.7). A pair counts as known when the medians of the recalled
values put the two entities in the right order. We compare flagged and
unflagged pairs from the base run.

Writes results/recall_probe.json.
"""

import asyncio
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from openrouter import run_requests
from questions import load_questions

ROOT = Path(__file__).resolve().parents[1]
ASK = {
    "book-release": "In what year was {e} first published?",
    "movie-release": "In what year was the film {e} released?",
    "song-release": "In what year was {e} released?",
    "nyt-pubdate": "On what date was the New York Times article \"{e}\" published?",
    "book-length": "How many pages does {e} have?",
    "movie-length": "How long is the film {e}, in minutes?",
    "person-age": "At what age did {e} die?",
    "person-birth": "In what year was {e} born?",
    "person-death": "In what year did {e} die?",
    "area": "What is the area of {e}, in square kilometres?",
}
SUFFIX = " Reply with only your best estimate as a number (for a date, the year). Do not refuse; guess if unsure."
NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def question(prop_id, entity):
    for k, v in ASK.items():
        if prop_id.endswith(k):
            return v.format(e=entity) + SUFFIX
    raise KeyError(prop_id)


def true_value(prop_id, v):
    """The dataset stores dates as spreadsheet days; compare in years."""
    if prop_id.endswith(("book-release", "movie-release", "song-release", "nyt-pubdate")):
        return 1900 + v / 365.25
    if prop_id.endswith("movie-length"):
        return v / 60
    if prop_id.endswith("area"):
        return v / 1e6
    return v


def parse(text):
    m = NUM.search(text.replace("−", "-"))
    if not m:
        return np.nan
    try:
        return float(m.group(0).replace(",", "").rstrip("."))
    except ValueError:
        return np.nan


def main(models):
    qs = load_questions().set_index("qid")
    pairs = pd.read_csv(ROOT / "results" / "pairs_base.csv")
    pairs = pairs[~pairs.prop_id.str.contains(r"-(?:lat|long)$")]
    res = {}
    for model in models:
        p = pairs[pairs.model_id == model]
        ents = {}
        for r in p.itertuples():
            q = qs.loc[r.qid_y]
            for e in (q.x_name, q.y_name):
                ents[(q.prop_id.rsplit("_", 1)[0], e)] = question(q.prop_id, e)
        reqs = [(f"{prop}|{e}|{i}", [{"role": "user", "content": text}])
                for (prop, e), text in ents.items() for i in range(3)]
        got = asyncio.run(run_requests(reqs, ROOT / "data" / "recall" / f"{model.replace('/', '_')}.jsonl",
                                       model, {"temperature": 0.7, "max_tokens": 40},
                                       concurrency=100, tag=f"recall:{model}"))
        recalled = {}
        for (prop, e) in ents:
            vals = [parse(got[f"{prop}|{e}|{i}"]["content"]) for i in range(3) if f"{prop}|{e}|{i}" in got]
            recalled[(prop, e)] = np.nanmedian(vals) if np.isfinite(vals).any() else np.nan
        rows = []
        for r in p.itertuples():
            q = qs.loc[r.qid_y]
            rx, ry = recalled[(q.prop_id, q.x_name)], recalled[(q.prop_id, q.y_name)]
            tx, ty = true_value(q.prop_id, q.x_value), true_value(q.prop_id, q.y_value)
            known = (rx - ry) * (tx - ty) > 0 if np.isfinite(rx) and np.isfinite(ry) else np.nan
            rows.append({"flag": bool(r.unf), "known": known, "prop_id": q.prop_id})
        d = pd.DataFrame(rows)
        res[model] = {
            "pairs": int(len(d)), "parsed": int(d.known.notna().sum()),
            "known_order_flagged": float(d[d.flag].known.mean()), "flagged": int(d.flag.sum()),
            "known_order_unflagged": float(d[~d.flag].known.mean()), "unflagged": int((~d.flag).sum()),
        }
        print(model, res[model])
    json.dump(res, (ROOT / "results" / "recall_probe.json").open("w"), indent=2)


if __name__ == "__main__":
    main(sys.argv[1:] or ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct"])
