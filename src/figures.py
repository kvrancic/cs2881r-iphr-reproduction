"""Figures for the report.

fig_reproduction: (a) Figure 2 recomputed over 4,834 pairs from the released
  counts; (b) the same 1,014 pairs, the paper's run against our run, plus newer
  models.
fig_extensions: (a) unfaithful-pair rate with and without the true values in
  the prompt; (b) GPT-4o-mini geography flags under three wordings.
fig_mechanism: (a) observed flags against the guess-with-a-lean model;
  (b) recurrence of the paper's flags in our run against a no-change ceiling.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
FIG = ROOT / "figures"

BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False,
})

PAPER_NAMES = {
    "anthropic/claude-3.5-haiku": "Haiku 3.5", "anthropic/claude-3.6-sonnet": "Sonnet 3.5 v2",
    "anthropic/claude-3.7-sonnet": "Sonnet 3.7", "anthropic/claude-3.7-sonnet_1k": "Sonnet 3.7 (1k)",
    "anthropic/claude-3.7-sonnet_64k": "Sonnet 3.7 (64k)", "deepseek/deepseek-chat": "DeepSeek V3",
    "deepseek/deepseek-r1": "DeepSeek R1", "openai/gpt-4o-mini": "GPT-4o-mini",
    "openai/gpt-4o-2024-08-06": "GPT-4o Aug '24", "openai/chatgpt-4o-latest": "ChatGPT-4o",
    "google/gemini-pro-1.5": "Gemini 1.5 Pro", "google/gemini-2.5-flash-preview": "Gemini 2.5 Flash",
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
    draws = rng.binomial(n, count / n, size=b) / n
    return np.quantile(draws, [0.025, 0.975])


def bar_ci(ax, x, rate, lo, hi, color, width, label=None):
    ax.bar(x, rate, width, color=color, label=label, linewidth=0, zorder=2)
    ax.errorbar(x, rate, yerr=[[rate - lo], [hi - rate]], fmt="none", ecolor=INK,
                elinewidth=0.7, capsize=1.8, zorder=3)


def fig_reproduction(checks, runs):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7), gridspec_kw={"width_ratios": [1.35, 1]})

    ax = axes[0]
    f2 = checks["figure2"]
    order = list(PAPER_NAMES)
    for i, m in enumerate(order):
        c = f2[m]["our_count"]
        assert c == f2[m]["paper_count"], m
        r = 100 * c / 4834
        lo, hi = 100 * boot(c, 4834)
        bar_ci(ax, i, r, lo, hi, BLUE, 0.7)
        ax.text(i, hi + 0.35, f"{r:.1f}" if r >= 0.95 else f"{r:.2f}", ha="center",
                va="bottom", fontsize=6, color=INK2)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([PAPER_NAMES[m] for m in order], rotation=60, ha="right", fontsize=6.8)
    ax.set_ylabel("Unfaithful pairs (%)")
    ax.set_ylim(0, 17.5)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.set_title("(a) Paper's runs, all 4,834 pairs", fontsize=8.5, loc="left", color=INK)

    ax = axes[1]
    olds = ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct", "google/gemini-2.5-flash",
            "deepseek/deepseek-chat"]
    news = [m for m in ["openai/gpt-5.6-luna", "qwen/qwen3.8-flash", "anthropic/claude-haiku-5.5",
                        "deepseek/deepseek-v4-flash"] if m in runs["base"]]
    x = 0
    ticks, labels = [], []
    for m in olds:
        p, o = runs["paper_same_pairs"][m], runs["base"][m]
        bar_ci(ax, x - 0.2, 100 * p["rate"], 100 * p["lo"], 100 * p["hi"], BLUE, 0.38,
               "Paper's run" if x == 0 else None)
        bar_ci(ax, x + 0.2, 100 * o["rate"], 100 * o["lo"], 100 * o["hi"], ORANGE, 0.38,
               "Our run" if x == 0 else None)
        ticks.append(x)
        labels.append(OUR_NAMES[m])
        x += 1
    x += 0.4
    ax.axvline(x - 0.7, color=GRID, linewidth=0.8)
    ax.text(x - 0.55, 16.8, "2026 models", fontsize=6.8, color=INK2, va="top")
    for m in news:
        o = runs["base"][m]
        bar_ci(ax, x, 100 * o["rate"], 100 * o["lo"], 100 * o["hi"], ORANGE, 0.38)
        ax.text(x, 100 * o["hi"] + 0.35, f"{100*o['rate']:.1f}", ha="center", fontsize=6, color=INK2)
        ticks.append(x)
        labels.append(OUR_NAMES[m])
        x += 0.75
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=6.8)
    ax.set_ylim(0, 17.5)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(loc="upper left", fontsize=7, bbox_to_anchor=(0.2, 1.0))
    ax.set_title("(b) Same 1,014 pairs, fresh samples", fontsize=8.5, loc="left", color=INK)
    fig.tight_layout(w_pad=1.5)
    for ext in ["pdf", "png"]:
        fig.savefig(FIG / f"fig_reproduction.{ext}", dpi=300)


def fig_extensions(runs, coord):
    models = [m for m in ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct",
                          "deepseek/deepseek-chat", "openai/gpt-5.6-luna"] if m in runs["factcard"]]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.4), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    for i, m in enumerate(models):
        b, f = runs["base"][m], runs["factcard"][m]
        bar_ci(ax, i - 0.2, 100 * b["rate"], 100 * b["lo"], 100 * b["hi"], ORANGE, 0.38,
               "Question only" if i == 0 else None)
        bar_ci(ax, i + 0.2, 100 * f["rate"], 100 * f["lo"], 100 * f["hi"], AQUA, 0.38,
               "True values in prompt" if i == 0 else None)
        ax.text(i - 0.2, 100 * b["hi"] + 0.3, f"{b['n_unf']}", ha="center", fontsize=6.5, color=INK2)
        ax.text(i + 0.2, 100 * f["hi"] + 0.3, f"{f['n_unf']}", ha="center", fontsize=6.5, color=INK2)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([OUR_NAMES[m] for m in models], fontsize=7)
    ax.set_ylabel("Unfaithful pairs (%)")
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(fontsize=7, loc="upper right")
    ax.set_title("(a) Fact cards, all 1,014 pairs", fontsize=8.5, loc="left")

    ax = axes[1]
    conds = [("base", "west of /\nsouth of", ORANGE), ("coordwording", "more western\nlongitude", VIOLET),
             ("factcard", "true values\ngiven", AQUA)]
    for i, (c, lab, col) in enumerate(conds):
        n = coord[c]["flags"]
        ax.bar(i, n, 0.6, color=col, linewidth=0, zorder=2)
        ax.text(i, n + 3, str(n), ha="center", fontsize=7, color=INK2)
    ax.set_xticks(range(3))
    ax.set_xticklabels([lab for _, lab, _ in conds], fontsize=6.8)
    ax.set_ylabel("Flagged pairs")
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.set_title("(b) GPT-4o-mini, 684 geography pairs", fontsize=8.5, loc="left")
    fig.tight_layout(w_pad=1.5)
    for ext in ["pdf", "png"]:
        fig.savefig(FIG / f"fig_extensions.{ext}", dpi=300)


def fig_mechanism(noise):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.6, 1]})
    ax = axes[0]
    rows = [(PAPER_NAMES.get(m, m) + " (paper)", v) for m, v in noise["guess_with_lean_paper_full"].items()]
    rows += [(OUR_NAMES.get(m, m) + " (ours)", v) for m, v in noise["guess_with_lean_ours"].items()]
    rows.sort(key=lambda r: -r[1]["observed"])
    for i, (name, v) in enumerate(rows):
        lo, hi = v["ci"]
        ax.plot([lo, hi], [i, i], color=GRID, linewidth=3, solid_capstyle="round", zorder=1)
        ax.scatter([v["expected"]], [i], s=14, color=INK2, zorder=2, label="Predicted" if i == 0 else None)
        ax.scatter([v["observed"]], [i], s=16, color=ORANGE, zorder=3, label="Observed" if i == 0 else None)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=6.3)
    ax.invert_yaxis()
    ax.set_xscale("symlog", linthresh=10)
    ax.set_xticks([0, 10, 30, 100, 300])
    ax.set_xticklabels(["0", "10", "30", "100", "300"])
    ax.set_xlim(-1, 900)
    ax.set_xlabel("Flagged pairs")
    ax.xaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(fontsize=7, loc="lower right")
    ax.set_title("(a) Know it or guess with a template lean", fontsize=8.5, loc="left")

    ax = axes[1]
    names = list(noise["recurrence"])
    for i, m in enumerate(names):
        v = noise["recurrence"][m]
        ax.bar(i - 0.2, 100 * v["ceiling_if_unchanged"], 0.38, color=GRID, linewidth=0, zorder=2,
               label="If unchanged" if i == 0 else None)
        ax.bar(i + 0.2, 100 * v["observed"], 0.38, color=ORANGE, linewidth=0, zorder=2,
               label="Observed" if i == 0 else None)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([OUR_NAMES[m].replace(" ", "\n", 1) for m in names], fontsize=6.5)
    ax.set_ylabel("Paper's flags flagged again (%)")
    ax.set_ylim(0, 100)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    ax.legend(fontsize=6.5, loc="upper right")
    ax.set_title("(b) Do single flags recur?", fontsize=8.5, loc="left")
    fig.tight_layout(w_pad=1.2)
    for ext in ["pdf", "png"]:
        fig.savefig(FIG / f"fig_mechanism.{ext}", dpi=300)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    checks = json.load((RES / "paper_data_checks.json").open())
    runs = json.load((RES / "runs.json").open())
    fig_reproduction(checks, runs)
    fig_extensions(runs, json.load((RES / "coordwording.json").open()))
    fig_mechanism(json.load((RES / "noise_models.json").open()))
    print("figures written")
