"""Tie cards: does the template lean act when the model has values but cannot order them?

On the 330 non-geography pairs, the tie card prints one rounded value shared by
both entities (e.g. both "released around 2006"), so the values in the prompt
do not settle the order. The forced version adds "You must answer YES or NO." If the model falls back on a template-level lean under
uncertainty, its YES rate per template under tie cards should follow the
template's lean in the base run. We report the correlation of template YES
rates (tie card vs base), the mean signed lean, the UNKNOWN rate and the flags.

Writes results/tie_analysis.json.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

import iphr
from analyze_runs import counts_from_labels, with_question_info
from questions import load_questions

ROOT = Path(__file__).resolve().parents[1]
MODELS = ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct"]


def table(cond, model, qs, qids):
    lab = ROOT / "data" / "responses" / cond / f"{model.replace('/', '_')}.labels.jsonl"
    c = with_question_info(counts_from_labels(lab, model), qs)
    c = c[c.qid.isin(qids)]
    pt = iphr.pair_table(c)
    pt["unf"] = iphr.flag_pairs(pt)
    tot = c.yes_count + c.no_count + c.unknown_count
    return pt, float(c.unknown_count.sum() / tot.sum()), float(c.yes_count.sum() / tot.sum())


def main():
    qs = load_questions()
    other = pd.read_csv(ROOT / "data" / "subsample_other_pairs.csv")
    qids = set(other.qid_yes) | set(other.qid_no)
    res = {}
    rng = np.random.default_rng(0)
    for m in MODELS:
        base, unk_b, yes_b = table("base", m, qs, qids)
        tb = base.groupby(["prop_id", "comparison"]).group_p_yes.first()
        for cond in ["tiecard", "tieforced"]:
            lab = ROOT / "data" / "responses" / cond / f"{m.replace('/', '_')}.labels.jsonl"
            if not lab.exists():
                continue
            tie, unk_t, yes_t = table(cond, m, qs, qids)
            tt = tie.groupby(["prop_id", "comparison"]).group_p_yes.first()
            j = pd.concat([tb.rename("base"), tt.rename("tie")], axis=1).dropna()
            boots = []
            for _ in range(2000):
                k = j.iloc[rng.integers(0, len(j), len(j))]
                if k.base.std() > 0 and k.tie.std() > 0:
                    boots.append(np.corrcoef(k.base, k.tie)[0, 1])
            res[f"{m} | {cond}"] = {
                "templates": int(len(j)),
                "template_yes_rate_corr": float(np.corrcoef(j.base, j.tie)[0, 1]),
                "corr_ci": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
                "mean_lean_base": float((j.base - 0.5).mean()), "mean_lean_tie": float((j.tie - 0.5).mean()),
                "same_sign_templates": int((np.sign(j.base - 0.5) == np.sign(j.tie - 0.5)).sum()),
                "unknown_rate_base": unk_b, "unknown_rate_tie": unk_t,
                "yes_share_base": yes_b, "yes_share_tie": yes_t,
                "flags_base": int(base.unf.sum()), "flags_tie": int(tie.unf.sum()),
            }
            print(m, cond, res[f"{m} | {cond}"])
    json.dump(res, (ROOT / "results" / "tie_analysis.json").open("w"), indent=2)


if __name__ == "__main__":
    main()
