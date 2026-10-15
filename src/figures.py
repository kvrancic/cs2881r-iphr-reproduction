"""Figures for the report.

fig_reproduction: (a) Figure 2 over 4,834 pairs from the released counts
  (hatched bars: the 8 models whose 10-answer counts were not released);
  (b) the same 1,014 pairs: the paper's run, the paper's answers relabelled
  by us, and our run, plus newer models.
fig_mechanism: (a) Figure 2 split by kind of question; (b) correlation of
  each pair's leftover asymmetry between the paper's answers and our run,
  against what a template-only lean would give.
fig_extensions: (a) fact cards; (b) GPT-4o-mini's geography flags under six
  wordings.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
FIG = ROOT / "figures"

BLUE, LIGHTBLUE, ORANGE, AQUA, VIOLET, YELLOW = "#2a78d6", "#9cc3f0", "#eb6834", "#1baf7a", "#6250d6", "#eda100"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
META = {"CreationDate": None}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False,
    "hatch.linewidth": 0.6,
})

PAPER_NAMES = {
    "anthropic/claude-3.5-haiku": "Haiku 3.5", "anthropic/claude-3.6-sonnet": "Sonnet 3.5 v2",
    "anthropic/claude-3.7-sonnet": "Sonnet 3.7", "anthropic/claude-3.7-sonnet_1k": "Sonnet 3.7 (1k)",
    "anthropic/claude-3.7-sonnet_64k": "Sonnet 3.7 (64k)", "deepseek/deepseek-chat": "DeepSeek V3",
    "deepseek/deepseek-r1": "DeepSeek R1", "openai/gpt-4o-mini": "GPT-4o-mini",
    "openai/gpt-4o-2024-08-06": "GPT-4o Aug '24", "openai/chatgpt-4o-latest": "ChatGPT-4o",
    "google/gemini-pro-1.5": "Gemini 1.5 Pro", "google/gemini-2.5-flash-preview": "Gemini 2.5 Flash (preview)",
    "google/gemini-2.5-pro-preview": "Gemini 2.5 Pro", "meta-llama/Llama-3.1-70B": "Llama 3.1 70B (base)",
    "meta-llama/Llama-3.3-70B-Instruct": "Llama 3.3 70B", "qwen/qwq-32b": "QwQ 32B",
}
OUR_NAMES = {
    "openai/gpt-4o-mini": "GPT-4o-mini", "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
    "google/gemini-2.5-flash": "Gemini 2.5 Flash", "deepseek/deepseek-chat": "DeepSeek V3",
    "openai/gpt-5.6-luna": "GPT-5.6 Luna", "qwen/qwen3.8-flash": "Qwen 3.8 Flash",
    "anthropic/claude-haiku-5.5": "Claude Haiku 5.5", "deepseek/deepseek-v4-flash": "DeepSeek V4 Flash",
}


def boot(count, n, b=2000, seed=0):
    rng = np.random.default_rng(seed)
    return np.quantile(rng.binomial(n, count / n, size=b) / n, [0.025, 0.975])


def save(fig, name):
    for ext in ["pdf", "png"]:
        fig.savefig(FIG / f"{name}.{ext}", dpi=300, metadata=META if ext == "pdf" else None)


def fig_reproduction(checks, runs, relabel, cluster):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), gridspec_kw={"width_ratios": [1.35, 1]})
    ax = axes[0]
    f2 = checks["figure2"]
    order = list(PAPER_NAMES)
    for i, m in enumerate(order):
        c = f2[m]["our_count"]
        assert c == f2[m]["paper_count"], m
        r = 100 * c / 4834
        topped = f2[m]["source"] != "recomputed"
        ax.bar(i, r, 0.7, color="white" if topped else BLUE, edgecolor=BLUE, linewidth=0.8,
               hatch="////" if topped else None, zorder=2)
        hi = r
        if not topped:  # template-cluster bootstrap; none for count-only bars
            lo, hi = (100 * x for x in cluster[m])
            ax.errorbar(i, r, yerr=[[r - lo], [hi - r]], fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.6, zorder=3)
        ax.text(i, hi + 0.3, f"{r:.1f}" if r >= 0.95 else f"{r:.2f}".lstrip("0"), ha="center",
                va="bottom", fontsize=5.6, color=INK2)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([PAPER_NAMES[m] for m in order], rotation=60, ha="right", fontsize=6.8)
    ax.set_ylabel("Unfaithful pairs (%)")
    ax.set_ylim(0, 22)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(handles=[Patch(facecolor=BLUE, edgecolor=BLUE, label="recomputed by us"),
                       Patch(facecolor="white", edgecolor=BLUE, hatch="////",
                             label="count only (100-answer data)")],
              fontsize=6.5, loc="upper left", bbox_to_anchor=(0.0, 1.0))
    ax.set_title("(a) Paper's runs, 4,834 pairs", fontsize=8.5, loc="left")

    ax = axes[1]
    olds = ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct", "google/gemini-2.5-flash",
            "deepseek/deepseek-chat"]
    news = ["openai/gpt-5.6-luna", "qwen/qwen3.8-flash", "anthropic/claude-haiku-5.5", "deepseek/deepseek-v4-flash"]
    w = 0.27
    ticks, labels = [], []
    for x, m in enumerate(olds):
        vals = [(runs["paper_same_pairs"][m]["n_unf"], BLUE, "Paper's run"),
                (relabel[m]["flags_our_labels"], LIGHTBLUE, "Paper's answers, our labels"),
                (runs["base"][m]["n_unf"], ORANGE, "Our run")]
        for j, (n, col, lab) in enumerate(vals):
            ax.bar(x + (j - 1) * w, n, w * 0.95, color=col, linewidth=0, zorder=2, label=lab if x == 0 else None)
            if j != 1:  # the relabelled counts are in Table 1
                ax.text(x + (j - 1) * w, n + 2, str(n), ha="center", fontsize=5.6, color=INK2)
        ticks.append(x)
        labels.append(OUR_NAMES[m])
    x0 = len(olds) + 0.3
    ax.axvline(x0 - 0.45, color=GRID, linewidth=0.8)
    ax.text(x0 - 0.3, 62, "2026 models", fontsize=6.5, color=INK2, va="top")
    for i, m in enumerate(news):
        n = runs["base"][m]["n_unf"]
        ax.bar(x0 + 0.62 * i, n, w * 0.95, color=ORANGE, linewidth=0, zorder=2)
        ax.text(x0 + 0.62 * i, n + 2, str(n), ha="center", fontsize=5.6, color=INK2)
        ticks.append(x0 + 0.62 * i)
        labels.append(OUR_NAMES[m])
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=6.8)
    ax.set_ylabel("Flagged pairs (of 1,014)")
    ax.set_ylim(0, 165)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(fontsize=6.3, loc="upper right", bbox_to_anchor=(1.0, 1.0))
    ax.set_title("(b) Same 1,014 pairs, fresh samples", fontsize=8.5, loc="left")
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_reproduction")


def fig_mechanism(noise):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.45, 1]})
    ax = axes[0]
    kinds = noise["rate_by_kind_paper_full"]
    order = noise["ranking_all"]
    y = np.arange(len(order))
    geo = [100 * kinds[m]["geography"]["rate"] for m in order]
    oth = [100 * kinds[m]["other"]["rate"] for m in order]
    ax.barh(y - 0.2, geo, 0.38, color=VIOLET, label="Geography (3,262 pairs)", zorder=2)
    ax.barh(y + 0.2, oth, 0.38, color=YELLOW, label="Other (1,572 pairs)", zorder=2)
    for yy, g, o in zip(y, geo, oth):
        ax.text(g + 0.3, yy - 0.2, f"{g:.1f}", va="center", fontsize=5.8, color=INK2)
        ax.text(o + 0.3, yy + 0.2, f"{o:.1f}", va="center", fontsize=5.8, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([PAPER_NAMES[m] for m in order], fontsize=6.8)
    ax.invert_yaxis()
    ax.set_xlabel("Unfaithful pairs (%)")
    ax.xaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(fontsize=6.5, loc="lower right")
    ax.set_title("(a) The paper's Figure 2 by kind of question", fontsize=8.5, loc="left")

    ax = axes[1]
    names = ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct", "google/gemini-2.5-flash",
             "deepseek/deepseek-chat"]
    for i, m in enumerate(names):
        t = noise["paired"][m]["residual_test_same_judge"]
        ax.bar(i, t["null_975"], 0.55, color=GRID, zorder=1, label="Template lean only (97.5%)" if i == 0 else None)
        ax.scatter([i], [t["r"]], s=22, color=ORANGE, zorder=3, label="Observed" if i == 0 else None)
        ax.text(i + 0.13, t["r"], f"{t['r']:.2f}", va="center", fontsize=6, color=INK2)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([OUR_NAMES[m].replace(" ", "\n", 1) for m in names], fontsize=6.5)
    ax.set_ylabel("Correlation across runs")
    ax.set_ylim(0, 1.0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(fontsize=6.3, loc="upper right", ncol=2, columnspacing=0.8, handletextpad=0.3)
    ax.set_title("(b) Pair asymmetry repeats", fontsize=8.5, loc="left")
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_mechanism")


def fig_extensions(runs, geo):
    models = ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct", "deepseek/deepseek-chat",
              "openai/gpt-5.6-luna"]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1, 1.15]})
    ax = axes[0]
    for i, m in enumerate(models):
        b, f = runs["base"][m]["n_unf"], runs["factcard"][m]["n_unf"]
        ax.bar(i - 0.2, b, 0.38, color=ORANGE, zorder=2, label="Question only" if i == 0 else None)
        ax.bar(i + 0.2, max(f, 0.4), 0.38, color=AQUA, zorder=2, label="True values in prompt" if i == 0 else None)
        ax.text(i - 0.2, b + 2, str(b), ha="center", fontsize=6.5, color=INK2)
        ax.text(i + 0.2, f + 2, str(f), ha="center", fontsize=6.5, color=INK2)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([OUR_NAMES[m].replace(" ", "\n", 1) for m in models], fontsize=6.8)
    ax.set_ylabel("Flagged pairs (of 1,014)")
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(fontsize=6.5, loc="upper right")
    ax.set_title("(a) Values in the prompt", fontsize=8.5, loc="left")

    ax = axes[1]
    conds = [("strict", "+ only directly west counts", VIOLET), ("paraphrase", "paraphrase, same vague word", ORANGE),
             ("base", "paper's wording", ORANGE), ("clarified", "+ anywhere further west counts", VIOLET),
             ("coordwording", "'a more western longitude'", VIOLET), ("factcard", "asked coordinate given", AQUA),
             ("fullcard", "both coordinates given", AQUA)]
    y = np.arange(len(conds))
    for i, (c, lab, col) in enumerate(conds):
        n = geo["conditions"][c]["flags"]
        ax.barh(i, max(n, 3), 0.62, color=col, linewidth=0, zorder=2)
        ax.text(max(n, 3) + 10, i, str(n), va="center", fontsize=6.8, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([lab for _, lab, _ in conds], fontsize=6.6)
    ax.invert_yaxis()
    ax.set_xlabel("Flagged pairs (of 684)")
    ax.set_xlim(0, 760)
    ax.xaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(handles=[Patch(facecolor=ORANGE, label="vague direction word"),
                       Patch(facecolor=VIOLET, label="reading made explicit"),
                       Patch(facecolor=AQUA, label="coordinates printed")],
              fontsize=6.3, loc="lower right")
    ax.set_title("(b) GPT-4o-mini, geography pairs", fontsize=8.5, loc="left")
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_extensions")


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    load = lambda n: json.load((RES / n).open())
    fig_reproduction(load("paper_data_checks.json"), load("runs.json"), load("relabel_paper.json"),
                     load("noise_models.json")["figure2_cluster_ci"])
    fig_mechanism(load("noise_models.json"))
    fig_extensions(load("runs.json"), load("geo_analysis.json"))
    print("figures written")
