"""Zero-cost checks on the paper's released per-question counts.

1. Recompute Figure 2 flag counts with our implementation of the criteria.
2. Retest: for the 8 models whose flagged pairs were later topped up to 100
   samples, how many flags survive at the paper's own 0.5 cutoff (the paper
   reports retention with a 0.4 cutoff for the retest).
3. Lean by kind of question: how many flagged pairs are geography questions
   leaning NO, and how many are other questions leaning YES.
4. Per-pair evidence: for each flagged pair, a two-sided Fisher exact test on
   correct/incorrect counts of the two questions (UNKNOWN as half, rounded
   toward the null), to see how many flags are individually distinguishable
   from equal accuracy with 10 samples per question.

Writes results/paper_data_checks.json.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

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
# Models whose flagged pairs were topped up to 100 samples (paper Appendix D).
# One Gemini 2.5 Flash pair was also topped up for an example figure; it is
# not part of the retest.
OVERSAMPLED = {
    "anthropic/claude-3.6-sonnet", "anthropic/claude-3.7-sonnet",
    "anthropic/claude-3.7-sonnet_1k", "anthropic/claude-3.7-sonnet_64k",
    "deepseek/deepseek-r1", "openai/gpt-4o-2024-08-06",
    "openai/chatgpt-4o-latest", "google/gemini-2.5-pro-preview",
}


def fisher_p(pt: pd.DataFrame) -> np.ndarray:
    ps = []
    for r in pt.itertuples():
        cy = r.p_correct_y * r.total_count_y
        cn = r.p_correct_n * r.total_count_n
        # Round the half-credit counts toward each other (conservative for the flag).
        hi_c, lo_c = (cy, cn) if cy >= cn else (cn, cy)
        hi_t, lo_t = (r.total_count_y, r.total_count_n) if cy >= cn else (r.total_count_n, r.total_count_y)
        a, b = int(np.floor(hi_c)), int(np.ceil(lo_c))
        ps.append(fisher_exact([[a, hi_t - a], [b, lo_t - b]])[1])
    return np.array(ps)


def main():
    OUT.mkdir(exist_ok=True)
    df = pd.read_pickle(ROOT / "data" / "paper" / "df-wm-non-ambiguous-hard-2.pkl.gz")
    df = df[df.model_id.isin(PAPER_COUNTS)]
    pt = iphr.pair_table(df)
    over = (pt.total_count_y > 10) & (pt.total_count_n > 10)
    pt["unf"] = iphr.flag_pairs(pt)
    pt["unf_04"] = iphr.flag_pairs(pt, acc_thr=0.4)

    res = {"figure2": {}, "retest": {}, "fisher": {}}
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
        else:
            p = fisher_p(g[g.unf])
            res["fisher"][m] = {"flagged": int(g.unf.sum()),
                                "p_lt_05": int((p < 0.05).sum()),
                                "p_lt_01": int((p < 0.01).sum())}

    # Which way do flagged pairs lean, by kind of question? (10-sample flags only)
    ten = pt[(pt.total_count_y <= 10) & (pt.total_count_n <= 10) & pt.unf].copy()
    ten["kind"] = np.where(ten.prop_id.str.contains("lat|long"), "geography", "other")
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
    json.dump(res, (OUT / "paper_data_checks.json").open("w"), indent=2)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
