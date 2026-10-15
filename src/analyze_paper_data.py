"""Zero-cost checks on the paper's released per-question counts.

1. Recompute Figure 2 flag counts with our implementation of the criteria.
2. Retest: for the 8 models whose flagged pairs were later topped up to 100
   samples, how many flags survive at the paper's own 0.5 cutoff (the paper
   reports retention with a 0.4 cutoff for the retest).
3. The paper's Appendix Table 10 (rates over a grid of cutoffs), recomputed.
4. Lean by kind of question: how many flagged pairs are geography questions
   leaning NO, and how many are other questions leaning YES.

Writes results/paper_data_checks.json.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

import iphr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"

# Figure 2 bar heights as typed into chainscope notebooks/plots_for_writeup.py
# (lines 813-831); the script divides them by a hard-coded 4,892.
PAPER_COUNTS = {
    "anthropic/claude-3.5-haiku": 363, "anthropic/claude-3.6-sonnet": 22,
    "anthropic/claude-3.7-sonnet": 90, "anthropic/claude-3.7-sonnet_1k": 2,
    "anthropic/claude-3.7-sonnet_64k": 12, "deepseek/deepseek-chat": 60,
    "deepseek/deepseek-r1": 18, "openai/gpt-4o-mini": 660,
    "openai/gpt-4o-2024-08-06": 18, "openai/chatgpt-4o-latest": 24,
    "google/gemini-pro-1.5": 320, "google/gemini-2.5-flash-preview": 106,
    "google/gemini-2.5-pro-preview": 7, "meta-llama/Llama-3.1-70B": 159,
    "meta-llama/Llama-3.3-70B-Instruct": 102, "qwen/qwq-32b": 220,
}
N_PAIRS = 4834
# The paper's Appendix Table 10 (rates in %, accuracy cutoff 0.4 then 0.6,
# lean cutoff 0.03, 0.05, 0.07, 0.10), for the 8 models with 10-answer data.
TABLE10 = {
    "anthropic/claude-3.5-haiku": [11.5, 10.1, 9.1, 6.2, 6.0, 5.4, 4.9, 3.6],
    "deepseek/deepseek-chat": [2.4, 1.6, 0.7, 0.3, 1.3, 0.9, 0.4, 0.2],
    "openai/gpt-4o-mini": [18.1, 17.0, 15.7, 14.3, 10.6, 10.2, 9.7, 9.1],
    "google/gemini-pro-1.5": [10.0, 7.6, 5.8, 3.1, 7.1, 5.6, 4.3, 2.3],
    "google/gemini-2.5-flash-preview": [3.6, 2.9, 2.3, 1.3, 1.8, 1.6, 1.2, 0.9],
    "meta-llama/Llama-3.1-70B": [4.9, 4.2, 3.3, 2.7, 3.0, 2.5, 2.2, 1.9],
    "meta-llama/Llama-3.3-70B-Instruct": [3.9, 3.2, 2.1, 1.4, 1.6, 1.3, 1.0, 0.8],
    "qwen/qwq-32b": [7.1, 6.8, 5.5, 3.5, 3.2, 3.0, 2.6, 1.8],
}
# Models whose flagged pairs were topped up to 100 samples (paper Appendix D).
# One Gemini 2.5 Flash pair was also topped up for an example figure; it is
# not part of the retest.
OVERSAMPLED = {
    "anthropic/claude-3.6-sonnet", "anthropic/claude-3.7-sonnet",
    "anthropic/claude-3.7-sonnet_1k", "anthropic/claude-3.7-sonnet_64k",
    "deepseek/deepseek-r1", "openai/gpt-4o-2024-08-06",
    "openai/chatgpt-4o-latest", "google/gemini-2.5-pro-preview",
}


def main():
    OUT.mkdir(exist_ok=True)
    df = pd.read_pickle(ROOT / "data" / "paper" / "df-wm-non-ambiguous-hard-2.pkl.gz")
    df = df[df.model_id.isin(PAPER_COUNTS)]
    pt = iphr.pair_table(df)
    over = (pt.total_count_y > 10) & (pt.total_count_n > 10)
    pt["unf"] = iphr.flag_pairs(pt)
    pt["unf_04"] = iphr.flag_pairs(pt, acc_thr=0.4)

    res = {"figure2": {}, "retest": {}}
    for m, g in pt.groupby("model_id"):
        n_over = int(over[g.index].sum()) if m in OVERSAMPLED else 0
        if m not in OVERSAMPLED:
            # 10-sample flags; the one topped-up Gemini Flash pair is judged on
            # its first 100 samples, as in the released data.
            ours = int(g.unf.sum())
        else:
            ours = n_over  # the topped-up pairs are exactly the 10-sample flags
        res["figure2"][m] = {
            "paper_count": PAPER_COUNTS[m], "our_count": ours,
            "paper_pct": round(100 * PAPER_COUNTS[m] / 4892, 2),
            "pct_over_4834": round(100 * PAPER_COUNTS[m] / N_PAIRS, 2),
            "source": "recomputed" if n_over == 0 else "count of topped-up pairs",
        }
        if n_over:
            go = g[over[g.index]]
            res["retest"][m] = {
                "flagged_at_10": n_over,
                "kept_at_100_thr05": int(go.unf.sum()),
                "kept_at_100_thr04": int(go.unf_04.sum()),
            }

    # The paper's Table 10, recomputed over 4,834 pairs.
    matched = 0
    for m, row in TABLE10.items():
        g = pt[pt.model_id == m]
        ours = [round(100 * iphr.flag_pairs(g, at, bt).sum() / N_PAIRS, 1)
                for at in [0.4, 0.6] for bt in [0.03, 0.05, 0.07, 0.10]]
        matched += int(sum(a == b for a, b in zip(ours, row)))
    res["table10"] = {"cells_matched": matched, "cells": 8 * len(TABLE10)}

    # Which way do flagged pairs lean, by kind of question? (10-sample flags only)
    ten = pt[(pt.total_count_y <= 10) & (pt.total_count_n <= 10) & pt.unf].copy()
    ten["kind"] = np.where(ten.prop_id.str.contains(r"-(?:lat|long)$"), "geography", "other")
    ten["lean"] = np.where(ten.group_p_yes > 0.5, "YES", "NO")
    res["lean_by_kind"] = {
        m: {f"{k}_{l}": int(((g.kind == k) & (g.lean == l)).sum())
            for k in ["geography", "other"] for l in ["NO", "YES"]}
        for m, g in ten.groupby("model_id")}
    tot_lean = ten.groupby(["kind", "lean"]).size()
    res["lean_by_kind_total"] = {f"{k}_{l}": int(v) for (k, l), v in tot_lean.items()}

    tot = {k: sum(v[k] for v in res["retest"].values())
           for k in ["flagged_at_10", "kept_at_100_thr05", "kept_at_100_thr04"]}
    res["retest_total"] = tot
    # The paper's 76.5% is a mean of per-model retention rates (Appendix D, Table 4).
    res["retest_mean_of_models"] = {
        thr: float(np.mean([v[f"kept_at_100_{thr}"] / v["flagged_at_10"] for v in res["retest"].values()]))
        for thr in ["thr05", "thr04"]}
    # How much our 21% sample moves each 10-sample model's rate, with leans re-estimated on the sample.
    sub = pd.read_csv(ROOT / "data" / "subsample_pairs.csv")
    ps = iphr.pair_table(df[df.qid.isin(set(sub.qid_yes) | set(sub.qid_no))])
    ps["unf"] = iphr.flag_pairs(ps)
    res["subsample_shift_points"] = {
        m: round(100 * (ps[ps.model_id == m].unf.mean() - pt[pt.model_id == m].unf.sum() / N_PAIRS), 2)
        for m in PAPER_COUNTS if m not in OVERSAMPLED}
    json.dump(res, (OUT / "paper_data_checks.json").open("w"), indent=2)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
