"""Write the report's tables from the result files, so the PDF cannot drift from them.

Writes report/table_agree.tex (Table 1).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
NAMES = {"openai/gpt-4o-mini": "GPT-4o-mini", "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
         "google/gemini-2.5-flash": "Gemini 2.5 Flash$^\\dagger$", "deepseek/deepseek-chat": "DeepSeek V3"}


def main():
    runs = json.load((RES / "runs.json").open())
    relabel = json.load((RES / "relabel_paper.json").open())
    noise = json.load((RES / "noise_models.json").open())["paired"]
    rows = []
    for m, name in NAMES.items():
        n = noise[m]
        ratio = n["ratio_ours_to_paper_answers_our_labels_ci"]
        rec = n["paper_answers_our_labels_vs_ours"]
        one = n["one_sided_lean_recurrence"]
        rows.append(
            f"{name} & {runs['paper_same_pairs'][m]['n_unf']} & {relabel[m]['flags_our_labels']} & "
            f"{runs['base'][m]['n_unf']} & {ratio[0]:.2f}--{ratio[1]:.2f} & "
            f"{n['lean_gap']['paper']:.3f} & {n['lean_gap']['ours']:.3f} & "
            f"{100 * rec['share']:.0f}\\% ({100 * n['expected_recurrence_if_unchanged']:.0f}\\%) & "
            f"{n['residual_test_same_judge']['r']:.2f} ({n['residual_test_same_judge']['null_975']:.2f}) & "
            f"{one['mean_in_other_run']:.3f} ({one['null_975']:.3f})\\\\")
    body = "\n".join(rows)
    tex = r"""\begin{tabular}{lrrrcrrccc}
\toprule
& \multicolumn{3}{c}{Flagged (of 1,014)} & Ours / paper & \multicolumn{2}{c}{Lean gap} & Recurrence & Residual $r$ & Lean-side\\
Model & paper & paper ans., & ours & ans., our & paper & ours & observed & observed & excess\\
& & our labels & & labels (95\%) & & & (unchanged) & (null 97.5\%) & (null 97.5\%)\\
\midrule
""" + body + r"""
\bottomrule
\end{tabular}
"""
    (ROOT / "report" / "table_agree.tex").write_text(tex)
    print(tex)


if __name__ == "__main__":
    main()
