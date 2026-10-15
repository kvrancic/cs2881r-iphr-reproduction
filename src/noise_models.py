"""Zero-cost checks on how stable the flags are and what produces them.

1. Expected recurrence if unchanged. Take each question's answer rates in the
   paper's run (half a pseudo-count per label) as the truth, draw two
   independent 10-answer runs, recompute template leans in each, and measure
   how many flags of the first run recur in the second (200 simulations, with
   a 95% interval). Observed recurrence is computed two ways: the paper's run
   against ours, and the paper's answers relabelled by our labeller against
   ours (same judge on both sides).

2. Know-or-guess model. Each pair is known with probability k (both orders
   right); otherwise the model answers YES with a probability b shared by the
   whole template, and UNKNOWN at the question's observed rate. We fit k per
   pair and b per template, simulate, and count flags. This is a weak check:
   k is fitted per pair from the same data, so pair-level differences can hide
   in it.

3. Residual test. Under the know-or-guess model, each pair's accuracy
   difference minus (1-k)(2b-1) is sampling noise, so its residuals in two
   independent runs should be uncorrelated. A correlation well above the
   simulated null means pair-specific order effects that repeat across runs.

4. Paired comparison (McNemar on pairs flagged in one run only), a cutoff-free
   lean gap, flag counts over a cutoff grid, template-cluster bootstrap
   intervals for each model's rate and for the ratio of our count to the
   paper's (same judge).

5. Figure 2 by kind of question (geography vs other) and how often the model
   ranking changes across cutoffs.

Writes results/noise_models.json.
"""

import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, kendalltau

import iphr

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(0)
N_SIM = 200
GEO = r"-(?:lat|long)$"
NAMES = {"openai/gpt-4o-mini": "openai/gpt-4o-mini",
         "meta-llama/llama-3.3-70b-instruct": "meta-llama/Llama-3.3-70B-Instruct",
         "deepseek/deepseek-chat": "deepseek/deepseek-chat",
         "google/gemini-2.5-flash": "google/gemini-2.5-flash-preview"}
TEN_SAMPLE = ["anthropic/claude-3.5-haiku", "deepseek/deepseek-chat", "google/gemini-2.5-flash-preview",
              "google/gemini-pro-1.5", "meta-llama/Llama-3.1-70B", "meta-llama/Llama-3.3-70B-Instruct",
              "openai/gpt-4o-mini", "qwen/qwq-32b"]


def tmpl_of(pt):
    return (pt.prop_id + "|" + pt.comparison).to_numpy()


def flags_from_accuracy(pt, acc_y, acc_n, acc_thr=0.5, bias_thr=0.05):
    g = pd.Series((acc_y + 1 - acc_n) / 2).groupby(tmpl_of(pt)).transform("mean").to_numpy()
    lean = np.where(g > 0.5, "YES", "NO")
    low = np.where(acc_y < acc_n, "YES", "NO")
    return (np.abs(acc_y - acc_n) >= acc_thr) & (np.abs(g - 0.5) >= bias_thr) & (low != lean)


def from_accuracy(acc, p_unknown):
    """P(correct) that gives accuracy acc when UNKNOWN counts as half."""
    return np.clip(acc - 0.5 * p_unknown, 0, 1 - p_unknown)


def draw(p_correct, p_unknown, n=10):
    """Accuracy with UNKNOWN counted as half, as in the paper. p_correct is P(correct)."""
    u = RNG.binomial(n, p_unknown)
    c = RNG.binomial(n - u, np.clip(p_correct / np.maximum(1 - p_unknown, 1e-9), 0, 1))
    return (c + 0.5 * u) / n


def rates(pt, side):
    y, nn, u = pt[f"yes_count_{side}"], pt[f"no_count_{side}"], pt[f"unknown_count_{side}"]
    tot = y + nn + u + 1.5
    correct = y if side == "y" else nn
    return ((correct + 0.5) / tot).to_numpy(), ((u + 0.5) / tot).to_numpy()


def expected_recurrence(pt, seed=None):
    """With a seed, draw from a separate generator so the shared stream is untouched."""
    global RNG
    if seed is not None:
        shared, RNG = RNG, np.random.default_rng(seed)
        try:
            return expected_recurrence(pt)
        finally:
            RNG = shared
    pcy, puy = rates(pt, "y")
    pcn, pun = rates(pt, "n")
    shares = []
    for _ in range(N_SIM):
        a = flags_from_accuracy(pt, draw(pcy, puy), draw(pcn, pun))
        b = flags_from_accuracy(pt, draw(pcy, puy), draw(pcn, pun))
        if a.sum():
            shares.append((a & b).sum() / a.sum())
    return float(np.mean(shares)), [float(np.quantile(shares, 0.025)), float(np.quantile(shares, 0.975))]


def fit_know_or_guess(pt):
    acc_y, acc_n = pt.p_correct_y.to_numpy(), pt.p_correct_n.to_numpy()
    k = np.clip(acc_y + acc_n - 1, 0, 1)
    t = tmpl_of(pt)
    b = np.empty(len(pt))
    for tt in np.unique(t):
        m = t == tt
        w = 1 - k[m]
        b[m] = np.clip(0.5 + ((w * (acc_y[m] - acc_n[m])).sum() / max((w ** 2).sum(), 1e-9)) / 2, 0, 1)
    return k, b


def know_or_guess(pt):
    k, b = fit_know_or_guess(pt)
    puy = rates(pt, "y")[1]
    pun = rates(pt, "n")[1]
    py, pn = k + (1 - k) * b, k + (1 - k) * (1 - b)
    sims = [flags_from_accuracy(pt, draw(from_accuracy(py, puy), puy), draw(from_accuracy(pn, pun), pun)).sum()
            for _ in range(N_SIM)]
    return float(np.mean(sims)), [float(np.quantile(sims, 0.025)), float(np.quantile(sims, 0.975))]


def residuals(pt):
    k, b = fit_know_or_guess(pt)
    return (pt.p_correct_y - pt.p_correct_n).to_numpy() - (1 - k) * (2 * b - 1)


def residual_test(a, b):
    """Correlation of know-or-guess residuals between two runs on the same pairs."""
    key = ["prop_id", "comparison", "pair_key"]
    j = a.merge(b, on=key, suffixes=("", "_2"))
    ja = j[[c for c in j.columns if not c.endswith("_2")]]
    jb = j[key + [c for c in j.columns if c.endswith("_2")]].rename(columns=lambda c: c[:-2] if c.endswith("_2") else c)
    ra, rb = residuals(ja), residuals(jb)
    observed = float(np.corrcoef(ra, rb)[0, 1])
    keep = (ja.p_correct_y + ja.p_correct_n >= 1).to_numpy()
    observed_known = float(np.corrcoef(ra[keep], rb[keep])[0, 1])
    # Null: two runs drawn from the know-or-guess model fitted to run a.
    k, bb = fit_know_or_guess(ja)
    puy, pun = rates(ja, "y")[1], rates(ja, "n")[1]
    py, pn = k + (1 - k) * bb, k + (1 - k) * (1 - bb)
    null = []
    for _ in range(N_SIM):
        sims = []
        for _ in range(2):
            ay, an = draw(from_accuracy(py, puy), puy), draw(from_accuracy(pn, pun), pun)
            s = ja.assign(p_correct_y=ay, p_correct_n=an)
            sims.append(residuals(s))
        null.append(np.corrcoef(*sims)[0, 1])
    return {"r": observed, "r_pairs_with_k_above_0": observed_known,
            "null_mean": float(np.mean(null)), "null_975": float(np.quantile(null, 0.975))}


def lean_signed(pt, res):
    """Residual signed so that positive means more asymmetry in the template's lean direction."""
    return np.where(pt.group_p_yes.to_numpy() > 0.5, res, -res)


def one_sided_recurrence(a, b):
    """Pairs with excess lean-direction asymmetry in run a: does the excess return in run b?

    The cutoff is the 97.5th percentile of the lean-signed residual in run a under
    simulations of the template-only model. For the selected pairs we report the
    mean lean-signed residual in run b and the same quantity under the null.
    """
    key = ["prop_id", "comparison", "pair_key"]
    j = a.merge(b, on=key, suffixes=("", "_2"))
    ja = j[[c for c in j.columns if not c.endswith("_2")]]
    jb = j[key + [c for c in j.columns if c.endswith("_2")]].rename(columns=lambda c: c[:-2] if c.endswith("_2") else c)
    sa = lean_signed(ja, residuals(ja))
    sb = lean_signed(jb, residuals(jb))
    k, bb = fit_know_or_guess(ja)
    puy, pun = rates(ja, "y")[1], rates(ja, "n")[1]
    py, pn = k + (1 - k) * bb, k + (1 - k) * (1 - bb)

    def sim():
        ay, an = draw(from_accuracy(py, puy), puy), draw(from_accuracy(pn, pun), pun)
        s_ = ja.assign(p_correct_y=ay, p_correct_n=an)
        return lean_signed(ja, residuals(s_))

    pool = np.concatenate([sim() for _ in range(50)])
    cut, low = np.quantile(pool, 0.975), np.quantile(pool, 0.025)
    sel, anti = sa > cut, sa < low
    sims = [sim() for _ in range(N_SIM)]
    null = [x[sel].mean() for x in sims]
    null_anti = [(-x[anti]).mean() for x in sims]
    # The mirror selection is the control: stable pair-level beliefs return on both
    # sides, a lean-specific effect returns more on the lean side.
    return {"cut": float(cut), "selected_pairs": int(sel.sum()), "mean_in_other_run": float(sb[sel].mean()),
            "share_positive_in_other_run": float((sb[sel] > 0).mean()),
            "null_mean": float(np.mean(null)), "null_975": float(np.quantile(null, 0.975)),
            "anti_selected_pairs": int(anti.sum()), "anti_mean_in_other_run": float((-sb[anti]).mean()),
            "anti_null_975": float(np.quantile(null_anti, 0.975))}


def lean_gap(pt):
    lean_yes = pt.group_p_yes > 0.5
    return float(np.mean(np.where(lean_yes, pt.p_correct_y - pt.p_correct_n, pt.p_correct_n - pt.p_correct_y)))


def cluster_boot(a, b=None, n=2000):
    """Template-cluster bootstrap of the flag rate of a, or of the ratio of b's flags to a's."""
    t = tmpl_of(a)
    temps = np.unique(t)
    fa = pd.Series(a.unf.to_numpy()).groupby(t).agg(["sum", "count"])
    fb = pd.Series(b.unf.to_numpy()).groupby(tmpl_of(b)).sum().reindex(fa.index, fill_value=0) if b is not None else None
    out = []
    for _ in range(n):
        s = RNG.choice(temps, len(temps))
        if b is None:
            out.append(fa.loc[s, "sum"].sum() / fa.loc[s, "count"].sum())
        else:
            out.append(fb.loc[s].sum() / max(fa.loc[s, "sum"].sum(), 1))
    return [float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975))]


def main():
    res = {}
    paper = pd.read_pickle(ROOT / "data" / "paper" / "df-wm-non-ambiguous-hard-2.pkl.gz")
    full = paper[paper.model_id.isin(TEN_SAMPLE)]
    fpt = iphr.pair_table(full)
    fpt["unf"] = iphr.flag_pairs(fpt)

    res["know_or_guess_paper_full"] = {}
    for m, g in fpt.groupby("model_id"):
        g = g.reset_index(drop=True)
        exp, ci = know_or_guess(g)
        res["know_or_guess_paper_full"][m] = {"observed": int(g.unf.sum()), "expected": exp, "ci": ci}
    # Template-cluster bootstrap intervals for Figure 2, for the 8 models we can recompute.
    res["figure2_cluster_ci"] = {m: cluster_boot(g.reset_index(drop=True)) for m, g in fpt.groupby("model_id")}
    above = [v["observed"] > v["expected"] for v in res["know_or_guess_paper_full"].values()]
    res["know_or_guess_paper_full_sign"] = {"above": int(sum(above)), "of": len(above),
                                           "p": float(binomtest(sum(above), len(above)).pvalue)}

    ours = pd.read_csv(ROOT / "results" / "pairs_base.csv")
    res["know_or_guess_ours"] = {}
    for m, g in ours.groupby("model_id"):
        g = g.reset_index(drop=True)
        exp, ci = know_or_guess(g)
        res["know_or_guess_ours"][m] = {"observed": int(g.unf.sum()), "expected": exp, "ci": ci,
                                        "rate_cluster_ci": cluster_boot(g)}

    sub = pd.read_csv(ROOT / "data" / "subsample_pairs.csv")
    qids = set(sub.qid_yes) | set(sub.qid_no)
    ppt = iphr.pair_table(paper[paper.qid.isin(qids) & paper.model_id.isin(NAMES.values())])
    relab = iphr.pair_table(pd.read_csv(ROOT / "results" / "paper_answers_our_labels.csv"))
    key = ["prop_id", "comparison", "pair_key"]
    res["paired"] = {}
    for o, p in NAMES.items():
        a = ppt[ppt.model_id == p].reset_index(drop=True)
        a["unf"] = iphr.flag_pairs(a)
        r = relab[relab.model_id == o].reset_index(drop=True)
        r["unf"] = iphr.flag_pairs(r)
        b = ours[ours.model_id == o].reset_index(drop=True)
        exp_paper_labels, _ = expected_recurrence(a)
        exp, exp_ci = expected_recurrence(r, seed=1)

        def recur(x):
            j = x[key + ["unf"]].merge(b[key + ["unf"]], on=key, suffixes=("_x", "_o"))
            n = int(j.unf_x.sum())
            hit = int((j.unf_x & j.unf_o).sum())
            only_x, only_o = int((j.unf_x & ~j.unf_o).sum()), int((~j.unf_x & j.unf_o).sum())
            ci = binomtest(hit, n).proportion_ci() if n else None
            return {"flags": n, "recur": hit, "share": hit / n if n else None,
                    "share_ci": [float(ci.low), float(ci.high)] if ci else None,
                    "mcnemar_p": float(binomtest(min(only_x, only_o), only_x + only_o).pvalue)
                    if only_x + only_o else 1.0}

        grid = {}
        for bt in [0.03, 0.05, 0.10]:
            for at in [0.4, 0.5, 0.6]:
                grid[f"bias{bt}_gap{at}"] = [int(iphr.flag_pairs(a, at, bt).sum()),
                                            int(iphr.flag_pairs(r, at, bt).sum()),
                                            int(iphr.flag_pairs(b, at, bt).sum())]
        res["paired"][o] = {
            "expected_recurrence_if_unchanged": exp, "expected_recurrence_ci": exp_ci,
            "expected_recurrence_paper_labels": exp_paper_labels,
            "paper_run_vs_ours": recur(a), "paper_answers_our_labels_vs_ours": recur(r),
            "ratio_ours_to_paper_answers_our_labels_ci": cluster_boot(r, b),
            "lean_gap": {"paper": lean_gap(a), "paper_answers_our_labels": lean_gap(r), "ours": lean_gap(b)},
            "residual_test_same_judge": residual_test(r, b),
            "one_sided_lean_recurrence": one_sided_recurrence(r, b),
            "grid_paper_relabelled_ours": grid,
        }

    # Figure 2 by kind of question, and ranking across cutoffs (full set, 8 models).
    fpt["kind"] = np.where(fpt.prop_id.str.contains(GEO), "geography", "other")
    res["rate_by_kind_paper_full"] = {
        m: {k: {"flags": int(h.unf.sum()), "pairs": int(len(h)), "rate": float(h.unf.mean())}
            for k, h in g.groupby("kind")} for m, g in fpt.groupby("model_id")}
    for kind in ["geography", "other"]:
        order = sorted(TEN_SAMPLE, key=lambda m: -res["rate_by_kind_paper_full"][m][kind]["rate"])
        res[f"ranking_{kind}"] = order
    res["ranking_all"] = sorted(TEN_SAMPLE, key=lambda m: -fpt[fpt.model_id == m].unf.mean())
    by = res["rate_by_kind_paper_full"]
    kt = kendalltau([by[m]["geography"]["rate"] for m in TEN_SAMPLE], [by[m]["other"]["rate"] for m in TEN_SAMPLE],
                    method="exact")
    res["kind_rank_tau"] = {"tau": float(kt.statistic), "p_exact": float(kt.pvalue)}

    grid = {}
    for bt in [0.03, 0.05, 0.07, 0.10]:
        for at in [0.3, 0.4, 0.5, 0.6, 0.7]:
            grid[(bt, at)] = fpt.assign(f=iphr.flag_pairs(fpt, at, bt)).groupby("model_id").f.sum()
    ref = grid[(0.05, 0.5)]
    taus, changed = [], 0
    for key_, s in grid.items():
        s = s[ref.index]
        taus.append(kendalltau(ref, s).statistic)
        if key_ != (0.05, 0.5) and list(s.sort_values().index) != list(ref.sort_values().index):
            changed += 1
    res["rank_stability"] = {"settings": len(grid), "settings_with_any_swap": changed,
                             "min_kendall_tau": float(np.min(taus)), "mean_kendall_tau": float(np.mean(taus))}

    json.dump(res, (ROOT / "results" / "noise_models.json").open("w"), indent=2)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
