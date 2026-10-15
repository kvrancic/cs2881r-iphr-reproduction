"""Geography: how much of GPT-4o-mini's flags depends on how it reads "west of"?

1. Wording conditions on the 684 geography pairs of our sample (GPT-4o-mini):
   base (paper wording), paraphrase ("lie to the west of"), clarified (paper
   wording plus "count it as west if it is anywhere further west, even if it
   is also far to the north or south"), strict (paper wording plus "count it as
   west only if it is directly west, at about the same latitude"), coordwording ("a more western
   longitude"), factcard (the asked coordinate of both entities) and fullcard
   (both coordinates of both entities). For each: flags, accuracy on each side,
   mean template lean, lean gap, and the share of answers that cite degrees.

2. Distances. Flag rate and accuracy on each side of a pair by quartile of the
   distance on the asked axis and on the other axis (and the two-way table),
   in the paper's released data for the models with geography flags and in
   our run. A strict reading ("directly west") or a "different continents"
   reading becomes more likely as the places lie further apart.

Writes results/geo_analysis.json.
"""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

import iphr
from analyze_runs import counts_from_labels, with_question_info
from openrouter import load_cache
from questions import load_questions

ROOT = Path(__file__).resolve().parents[1]
MODEL = "openai/gpt-4o-mini"
CONDITIONS = ["base", "paraphrase", "clarified", "strict", "coordwording", "factcard", "fullcard"]
DEGREES = re.compile(r"\d+(?:\.\d+)?\s*°|\d+(?:\.\d+)?\s*degrees", re.I)
GEO = r"-(?:lat|long)$"


def other_axis_table():
    vals = {}
    for f in (ROOT / "data" / "properties").glob("*.yaml"):
        vals[f.stem] = yaml.safe_load(f.open())["value_by_name"]
    return vals


def add_offsets(pt, qs, vals):
    """Ratio of the other-axis offset to the asked-axis offset for each pair."""
    q = qs.set_index("qid")
    ratios = []
    for r in pt.itertuples():
        row = q.loc[r.qid_y]
        base, axis = row.prop_id.rsplit("-", 1)
        other = vals[f"{base}-{'long' if axis == 'lat' else 'lat'}"]
        d_other = abs(other.get(row.x_name, np.nan) - other.get(row.y_name, np.nan))
        d_asked = abs(row.x_value - row.y_value)
        ratios.append(d_other / d_asked if d_asked else np.nan)
    return pt.assign(other_ratio=ratios)


def conditions(qs):
    geo = pd.read_csv(ROOT / "data" / "subsample_geo_pairs.csv")
    qids = set(geo.qid_yes) | set(geo.qid_no)
    out = {}
    slug = MODEL.replace("/", "_")
    for cond in CONDITIONS:
        lab = ROOT / "data" / "responses" / cond / f"{slug}.labels.jsonl"
        if not lab.exists():
            continue
        c = with_question_info(counts_from_labels(lab, MODEL), qs)
        pt = iphr.pair_table(c[c.qid.isin(qids)])
        pt["unf"] = iphr.flag_pairs(pt)
        lean = pt.groupby(["prop_id", "comparison"]).group_p_yes.first() - 0.5
        gap = np.where(pt.group_p_yes > 0.5, pt.p_correct_y - pt.p_correct_n, pt.p_correct_n - pt.p_correct_y)
        resp = load_cache(ROOT / "data" / "responses" / cond / f"{slug}.jsonl")
        cites = np.mean([bool(DEGREES.search(r["content"])) for rid, r in resp.items()
                         if rid.split("__")[0] in qids])
        out[cond] = {
            "pairs": int(len(pt)), "flags": int(pt.unf.sum()),
            "acc_yes_q": float(pt.p_correct_y.mean()), "acc_no_q": float(pt.p_correct_n.mean()),
            "mean_template_lean": float(lean.mean()), "templates_leaning": int((lean.abs() >= 0.05).sum()),
            "templates": int(len(lean)), "lean_gap": float(np.mean(gap)), "share_citing_degrees": float(cites),
        }
    return out


def add_distances(pt, qs, vals):
    """Distance on the asked axis and on the other axis, in degrees."""
    q = qs.set_index("qid")
    da, do = [], []
    for r in pt.itertuples():
        row = q.loc[r.qid_y]
        base, axis = row.prop_id.rsplit("-", 1)
        other = vals[f"{base}-{'long' if axis == 'lat' else 'lat'}"]
        da.append(abs(row.x_value - row.y_value))
        do.append(abs(other.get(row.x_name, np.nan) - other.get(row.y_name, np.nan)))
    return pt.assign(d_asked=da, d_other=do)


def distance_table(pt):
    """Flag rate and accuracy on each side by quartile of the two distances."""
    pt = pt.assign(qa=pd.qcut(pt.d_asked, 4, labels=False), qo=pd.qcut(pt.d_other, 4, labels=False))
    return {
        "flag_rate_by_asked_quartile": [float(x) for x in pt.groupby("qa").unf.mean()],
        "acc_yes_q_by_asked_quartile": [float(x) for x in pt.groupby("qa").p_correct_y.mean()],
        "acc_no_q_by_asked_quartile": [float(x) for x in pt.groupby("qa").p_correct_n.mean()],
        "flag_rate_by_other_quartile": [float(x) for x in pt.groupby("qo").unf.mean()],
        "flag_rate_asked_x_other": [[float(x) for x in row] for row in
                                    pt.pivot_table(index="qa", columns="qo", values="unf", aggfunc="mean").to_numpy()],
    }


def distances(qs, vals):
    out = {}
    paper = pd.read_pickle(ROOT / "data" / "paper" / "df-wm-non-ambiguous-hard-2.pkl.gz")
    paper = paper[(paper.total_count <= 10) & paper.prop_id.str.contains(GEO)]
    for m in ["openai/gpt-4o-mini", "anthropic/claude-3.5-haiku", "google/gemini-2.5-flash-preview",
              "google/gemini-pro-1.5"]:
        pt = iphr.pair_table(paper[paper.model_id == m])
        pt["unf"] = iphr.flag_pairs(pt)
        out[f"paper | {m}"] = distance_table(add_distances(pt, qs, vals))
    ours = pd.read_csv(ROOT / "results" / "pairs_base.csv")
    ours = ours[(ours.model_id == MODEL) & ours.prop_id.str.contains(GEO)].reset_index(drop=True)
    out[f"ours | {MODEL}"] = distance_table(add_distances(ours, qs, vals))
    return out


def main():
    qs = load_questions()
    vals = other_axis_table()
    res = {"conditions": conditions(qs), "distances": distances(qs, vals)}
    json.dump(res, (ROOT / "results" / "geo_analysis.json").open("w"), indent=2)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
