"""IPHR rates for our fresh runs, compared with the paper on the same pairs.

For each model and condition: per-question YES/NO/UNKNOWN counts from our
labels, the paper's pair criteria, the unfaithful-pair rate on our 1,014-pair
sample with a bootstrap 95% CI over pairs.

For the four original models still served, also:
- the paper's rate on the same 1,014 pairs, from the released counts;
- per-pair flag agreement between the paper's run and ours;
- correlation of template-level YES rates between the two runs.

Writes results/runs.json and results/pairs_<condition>.csv.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

import iphr
from questions import load_questions

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"

ORIGINALS = {  # our OpenRouter id -> id in the paper's released data
    "openai/gpt-4o-mini": "openai/gpt-4o-mini",
    "meta-llama/llama-3.3-70b-instruct": "meta-llama/Llama-3.3-70B-Instruct",
    "deepseek/deepseek-chat": "deepseek/deepseek-chat",
    "google/gemini-2.5-flash": "google/gemini-2.5-flash-preview",
}
NEW = ["anthropic/claude-haiku-5.5", "openai/gpt-5.6-luna", "deepseek/deepseek-v4-flash",
       "qwen/qwen3.8-flash"]


def slug(m):
    return m.replace("/", "_")


def counts_from_labels(path: Path, model: str) -> pd.DataFrame:
    lab = pd.read_json(path, lines=True)
    c = lab.pivot_table(index="qid", columns="label", values="rid", aggfunc="count", fill_value=0)
    for k in ["YES", "NO", "UNKNOWN"]:
        if k not in c:
            c[k] = 0
    c = c.rename(columns={"YES": "yes_count", "NO": "no_count", "UNKNOWN": "unknown_count"})
    c = c[["yes_count", "no_count", "unknown_count"]].reset_index()
    c["model_id"] = model
    return c


def with_question_info(c: pd.DataFrame, qs: pd.DataFrame) -> pd.DataFrame:
    return c.merge(qs[["qid", "prop_id", "comparison", "answer", "x_name", "y_name"]], on="qid")


def boot_ci(x, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    b = rng.choice(x, size=(n_boot, len(x))).mean(1)
    return float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))


def model_summary(pt):
    x = pt.unf.to_numpy()
    lo, hi = boot_ci(x)
    p_unknown = (pt.unknown_count_y.sum() + pt.unknown_count_n.sum()) / (
        pt.total_count_y.sum() + pt.total_count_n.sum())
    acc = (pt.p_correct_y.mean() + pt.p_correct_n.mean()) / 2
    return {"n_pairs": int(len(x)), "n_unf": int(x.sum()), "rate": float(x.mean()),
            "lo": lo, "hi": hi, "accuracy": float(acc), "unknown_rate": float(p_unknown),
            "n_biased_templates": int(((pt.group_p_yes - 0.5).abs() >= 0.05)
                                      .groupby([pt.prop_id, pt.comparison]).first().sum())}


def main():
    OUT.mkdir(exist_ok=True)
    qs = load_questions()
    sub = pd.read_csv(ROOT / "data" / "subsample_pairs.csv")
    sub_qids = set(sub.qid_yes) | set(sub.qid_no)
    res = {"base": {}, "factcard": {}, "paper_same_pairs": {}, "agreement": {}}
    tables = {}

    for cond in ["base", "factcard"]:
        rows = []
        for m in list(ORIGINALS) + NEW:
            p = ROOT / "data" / "responses" / cond / f"{slug(m)}.labels.jsonl"
            if not p.exists():
                continue
            c = with_question_info(counts_from_labels(p, m), qs)
            c = c[c.qid.isin(sub_qids)]
            pt = iphr.pair_table(c)
            pt["unf"] = iphr.flag_pairs(pt)
            pt["condition"] = cond
            res[cond][m] = model_summary(pt)
            rows.append(pt)
        if rows:
            tables[cond] = pd.concat(rows)
            tables[cond].to_csv(OUT / f"pairs_{cond}.csv", index=False)

    # The paper's own run, restricted to the same 1,014 pairs.
    paper = pd.read_pickle(ROOT / "data" / "paper" / "df-wm-non-ambiguous-hard-2.pkl.gz")
    paper = paper[paper.qid.isin(sub_qids) & paper.model_id.isin(ORIGINALS.values())]
    ppt = iphr.pair_table(paper)
    ppt["unf"] = iphr.flag_pairs(ppt)
    for ours, theirs in ORIGINALS.items():
        g = ppt[ppt.model_id == theirs]
        res["paper_same_pairs"][ours] = model_summary(g)
        if "base" not in tables or ours not in set(tables["base"].model_id):
            continue
        o = tables["base"][tables["base"].model_id == ours]
        k = ["prop_id", "comparison", "pair_key"]
        j = g[k + ["unf", "p_correct_y", "p_correct_n", "group_p_yes"]].merge(
            o[k + ["unf", "p_correct_y", "p_correct_n", "group_p_yes"]], on=k, suffixes=("_paper", "_ours"))
        a, b = j.unf_paper, j.unf_ours
        gap_p = j.p_correct_y_paper - j.p_correct_n_paper
        gap_o = j.p_correct_y_ours - j.p_correct_n_ours
        tmpl = j.groupby(["prop_id", "comparison"])[["group_p_yes_paper", "group_p_yes_ours"]].first()
        res["agreement"][ours] = {
            "pairs": int(len(j)), "flag_paper": int(a.sum()), "flag_ours": int(b.sum()),
            "flag_both": int((a & b).sum()),
            "p_ours_given_paper": float((a & b).sum() / max(a.sum(), 1)),
            "p_paper_given_ours": float((a & b).sum() / max(b.sum(), 1)),
            "gap_corr": float(np.corrcoef(gap_p, gap_o)[0, 1]),
            "template_yes_corr": float(np.corrcoef(tmpl.group_p_yes_paper, tmpl.group_p_yes_ours)[0, 1]),
        }

    # Fact cards by kind of question (geography cards also tell the model which axis counts).
    res["by_kind"] = {}
    if "factcard" in tables:
        for cond in ["base", "factcard"]:
            t = tables[cond]
            t = t.assign(kind=np.where(t.prop_id.str.contains(r"-(?:lat|long)$"), "geography", "other"))
            for (m, k), g in t.groupby(["model_id", "kind"]):
                if m in res["factcard"]:
                    res["by_kind"].setdefault(m, {}).setdefault(k, {})[cond] = int(g.unf.sum())

    json.dump(res, (OUT / "runs.json").open("w"), indent=2)
    for sec in ["paper_same_pairs", "base", "factcard"]:
        print(f"\n== {sec}")
        for m, v in res[sec].items():
            print(f"{m:38s} {v['n_unf']:4d}/{v['n_pairs']} = {100*v['rate']:5.2f}% "
                  f"[{100*v['lo']:.2f}, {100*v['hi']:.2f}]  acc={v['accuracy']:.3f} "
                  f"unk={v['unknown_rate']:.3f} biased_tmpl={v['n_biased_templates']}")
    print("\n== agreement (same pairs, paper run vs ours)")
    for m, v in res["agreement"].items():
        print(m, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()})


if __name__ == "__main__":
    main()
