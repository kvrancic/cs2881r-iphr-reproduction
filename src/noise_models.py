"""Zero-cost models of what the flags would look like under simple explanations.

1. Recurrence ceiling. If a model did not change at all, how often would a pair
   flagged in one 10-answer run be flagged again in a second? We treat each
   question's answer rates in the paper's run (with half a pseudo-count per
   label) as the truth, draw two independent runs, recompute template leans in
   each, and count how many flags of the first run recur in the second.

2. Guess-with-a-lean model. Each pair has a chance k of being known (answered
   correctly in both orders). Otherwise the model guesses, and its guess is YES
   with a probability b that depends only on the template. Then
       acc(YES question) = k + (1-k) b,   acc(NO question) = k + (1-k)(1-b).
   This model has no effect of question order beyond the template lean. We fit
   k per pair and b per template, simulate 10 answers per question, and count
   flags. If it reproduces the observed count, a per-template lean applied when
   the model does not know is enough to explain Figure 2.

3. Paired comparison of the paper's run and ours (McNemar test on the pairs
   flagged in only one run), a threshold-free measure of the lean (mean
   accuracy gap in the direction of the template lean), and flag counts over a
   grid of the two cutoffs.

Writes results/noise_models.json.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, kendalltau

import iphr

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(0)
N_SIM = 200


def flags_from_correct(df, cy, cn, n=10, acc_thr=0.5, bias_thr=0.05):
    """Flags for simulated correct counts (arrays aligned with df rows)."""
    acc_y, acc_n = cy / n, cn / n
    p_yes_y, p_yes_n = acc_y, 1 - acc_n
    tmpl = df.prop_id + "|" + df.comparison
    g = pd.Series((p_yes_y + p_yes_n) / 2, index=df.index).groupby(tmpl.values).transform("mean")
    lean = np.where(g > 0.5, "YES", "NO")
    low = np.where(acc_y < acc_n, "YES", "NO")
    return (np.abs(acc_y - acc_n) >= acc_thr) & (np.abs(g - 0.5) >= bias_thr) & (low != lean)


def recurrence_ceiling(pt):
    """pt: pair table with yes/no/unknown counts for both questions."""
    def probs(prefix, correct):
        y, nn, u = (pt[f"yes_count_{prefix}"], pt[f"no_count_{prefix}"], pt[f"unknown_count_{prefix}"])
        tot = y + nn + u + 1.5
        p_correct = ((y if correct == "YES" else nn) + 0.5) / tot
        p_unknown = (u + 0.5) / tot
        return p_correct.to_numpy(), p_unknown.to_numpy()

    pcy, puy = probs("y", "YES")
    pcn, pun = probs("n", "NO")

    def draw():
        # correct + half of unknown, as in the paper's accuracy
        def one(pc, pu):
            u = RNG.binomial(10, pu)
            c = RNG.binomial(10 - u, np.clip(pc / np.maximum(1 - pu, 1e-9), 0, 1))
            return c + 0.5 * u
        return flags_from_correct(pt, one(pcy, puy), one(pcn, pun))

    first, both = 0, 0
    for _ in range(N_SIM):
        a, b = draw(), draw()
        first += a.sum()
        both += (a & b).sum()
    return float(both / max(first, 1)), float(first / N_SIM)


def guess_with_lean(pt):
    acc_y, acc_n = pt.p_correct_y.to_numpy(), pt.p_correct_n.to_numpy()
    k = np.clip(acc_y + acc_n - 1, 0, 1)
    tmpl = (pt.prop_id + "|" + pt.comparison).to_numpy()
    b = np.empty(len(pt))
    for t in np.unique(tmpl):
        m = tmpl == t
        w = 1 - k[m]
        slope = (w * (acc_y[m] - acc_n[m])).sum() / max((w ** 2).sum(), 1e-9)
        b[m] = np.clip(0.5 + slope / 2, 0, 1)
    py = k + (1 - k) * b
    pn = k + (1 - k) * (1 - b)
    sims = [flags_from_correct(pt, RNG.binomial(10, py), RNG.binomial(10, pn)).sum()
            for _ in range(N_SIM)]
    return float(np.mean(sims)), [float(np.quantile(sims, 0.025)), float(np.quantile(sims, 0.975))]


def lean_gap(pt):
    """Mean accuracy gap between the question whose answer matches the template lean and the other."""
    lean_yes = pt.group_p_yes > 0.5
    gap = np.where(lean_yes, pt.p_correct_y - pt.p_correct_n, pt.p_correct_n - pt.p_correct_y)
    return float(np.mean(gap))


def main():
    paper = pd.read_pickle(ROOT / "data" / "paper" / "df-wm-non-ambiguous-hard-2.pkl.gz")
    ten_models = [m for m, g in paper.groupby("model_id") if (g.total_count <= 10).all() or
                  m == "google/gemini-2.5-flash-preview"]
    ten_models = [m for m in ten_models if not m.startswith("google/gemma")]
    res = {"guess_with_lean_paper_full": {}, "guess_with_lean_ours": {}, "recurrence": {},
           "paired": {}, "threshold_grid_paper_full": {}, "rank_stability": {}}

    full = paper[paper.model_id.isin(ten_models) & (paper.total_count <= 10)]
    fpt = iphr.pair_table(full)
    fpt["unf"] = iphr.flag_pairs(fpt)
    for m, g in fpt.groupby("model_id"):
        g = g.reset_index(drop=True)
        exp, ci = guess_with_lean(g)
        res["guess_with_lean_paper_full"][m] = {"observed": int(g.unf.sum()), "expected": exp, "ci": ci}

    ours = pd.read_csv(ROOT / "results" / "pairs_base.csv")
    for m, g in ours.groupby("model_id"):
        g = g.reset_index(drop=True)
        exp, ci = guess_with_lean(g)
        res["guess_with_lean_ours"][m] = {"observed": int(g.unf.sum()), "expected": exp, "ci": ci}

    # Paper's run on our pairs vs our run.
    sub = pd.read_csv(ROOT / "data" / "subsample_pairs.csv")
    qids = set(sub.qid_yes) | set(sub.qid_no)
    names = {"openai/gpt-4o-mini": "openai/gpt-4o-mini",
             "meta-llama/llama-3.3-70b-instruct": "meta-llama/Llama-3.3-70B-Instruct",
             "deepseek/deepseek-chat": "deepseek/deepseek-chat",
             "google/gemini-2.5-flash": "google/gemini-2.5-flash-preview"}
    ppt = iphr.pair_table(paper[paper.qid.isin(qids) & paper.model_id.isin(names.values())])
    k = ["prop_id", "comparison", "pair_key"]
    for o, p in names.items():
        a = ppt[ppt.model_id == p].reset_index(drop=True)
        b = ours[ours.model_id == o].reset_index(drop=True)
        a["unf"] = iphr.flag_pairs(a)
        rec, exp_flags = recurrence_ceiling(a)
        j = a[k + ["unf"]].merge(b[k + ["unf"]], on=k, suffixes=("_p", "_o"))
        only_p = int((j.unf_p & ~j.unf_o).sum())
        only_o = int((~j.unf_p & j.unf_o).sum())
        grid = {}
        for bt in [0.03, 0.05, 0.10]:
            for at in [0.4, 0.5, 0.6]:
                grid[f"bias{bt}_gap{at}"] = [int(iphr.flag_pairs(a, at, bt).sum()),
                                            int(iphr.flag_pairs(b, at, bt).sum())]
        res["recurrence"][o] = {
            "observed": float((j.unf_p & j.unf_o).sum() / max(j.unf_p.sum(), 1)),
            "ceiling_if_unchanged": rec}
        res["paired"][o] = {
            "flag_only_paper": only_p, "flag_only_ours": only_o,
            "mcnemar_p": float(binomtest(min(only_p, only_o), only_p + only_o).pvalue)
            if only_p + only_o else 1.0,
            "lean_gap_paper": lean_gap(a), "lean_gap_ours": lean_gap(b),
            "grid_paper_vs_ours": grid}

    # Threshold sensitivity of Figure 2 (8 models with 10-answer data, full set).
    base_rank = None
    for bt in [0.03, 0.05, 0.07, 0.10]:
        for at in [0.4, 0.5, 0.6]:
            counts = fpt.assign(f=iphr.flag_pairs(fpt, at, bt)).groupby("model_id").f.sum()
            res["threshold_grid_paper_full"][f"bias{bt}_gap{at}"] = {m: int(v) for m, v in counts.items()}
            if base_rank is None:
                base_rank = None
    ref = pd.Series(res["threshold_grid_paper_full"]["bias0.05_gap0.5"])
    taus = []
    for key, d in res["threshold_grid_paper_full"].items():
        s = pd.Series(d)[ref.index]
        taus.append(kendalltau(ref, s).statistic)
    res["rank_stability"] = {"min_kendall_tau": float(np.min(taus)), "mean_kendall_tau": float(np.mean(taus))}

    json.dump(res, (ROOT / "results" / "noise_models.json").open("w"), indent=2)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
