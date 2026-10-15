"""The charts and number panels, authored in HTML/CSS on the finer 960x540 grid (2.5 x the 384x216 art grid),
rendered by headless Chromium, snapped to Endesga 32 with no anti-aliasing, and cut into one picture per element
(every element with a data-id), so bars can grow and panels can glide by Morph.

Every figure is read here from the result files and nowhere else:
  results/paper_data_checks.json, results/runs.json, results/noise_models.json, results/coordwording.json,
  data/judge_validation/summary.json.
Semantic colours: the paper's run blue, our run orange, fact cards aqua, the exact wording gold, unknown grey."""
import glob, hashlib, io, json, os
import numpy as np
from PIL import Image
from pal import HEX, C

ENGINE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.dirname(ENGINE)
ROOT = os.path.dirname(DECK)
CACHE = os.path.join(DECK, "build", "charts")
GW, GH = 960, 540
SCALE = 384 / GW          # native pixels per grid pixel (0.4)


def J(name):
    p = os.path.join(ROOT, "results", name) if not name.startswith("data/") else os.path.join(ROOT, name)
    return json.load(open(p))


CHECKS = J("paper_data_checks.json")
RUNS = J("runs.json")
NOISE = J("noise_models.json")
COORD = J("coordwording.json")
JUDGE = J("data/judge_validation/summary.json")

# Jersey 10 is drawn on a 75-unit grid in a 1400-unit em: 56/3 px puts one font pixel on one grid pixel.
F = {1: 56 / 3, 2: 112 / 3, 3: 56, 4: 224 / 3, 5: 280 / 3, 6: 112}

CSS = """
@font-face { font-family: J; src: url(data:font/ttf;base64,%(font)s) format('truetype'); }
:root { %(vars)s }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 960px; height: 540px; background: transparent; overflow: hidden; }
body { font-family: J; color: var(--ink); -webkit-font-smoothing: none; font-kerning: none; white-space: nowrap; }
.o { position: absolute; }
.f2 { font-size: %(f2)spx; line-height: 40px; }
.f3 { font-size: %(f3)spx; line-height: 60px; }
.f4 { font-size: %(f4)spx; line-height: 80px; }
.f5 { font-size: %(f5)spx; line-height: 100px; }
.panel { background: var(--night);
  box-shadow: inset 0 0 0 5px var(--dusk), inset 0 5px 0 5px var(--slate), 0 0 0 5px var(--ink), 10px 10px 0 5px var(--ice); }
.white { color: var(--white); } .ice { color: var(--ice); } .steel { color: var(--steel); } .slate { color: var(--slate); }
.ink { color: var(--ink); } .green { color: var(--green); } .red { color: var(--red); } .gold { color: var(--gold); }
.yellow { color: var(--yellow); } .sky { color: var(--sky); } .cyan { color: var(--cyan); } .orange { color: var(--orange); }
.navy { color: var(--navy); } .rose { color: var(--rose); }
/* pixel bars: lit top edge, shaded right edge (light from the top left), on the 5px grid */
.bar { }
.bp { background: var(--sky); box-shadow: inset 0 5px 0 0 var(--cyan), inset -5px 0 0 0 var(--navy); }
.bo { background: var(--orange); box-shadow: inset 0 5px 0 0 var(--gold), inset -5px 0 0 0 var(--rust); }
.ba { background: var(--cyan); box-shadow: inset 0 5px 0 0 var(--white), inset -5px 0 0 0 var(--sky); }
.bw { background: var(--gold); box-shadow: inset 0 5px 0 0 var(--yellow), inset -5px 0 0 0 var(--orange); }
.bg { background: var(--steel); box-shadow: inset 0 5px 0 0 var(--ice), inset -5px 0 0 0 var(--slate); }
.bn { background: var(--red); box-shadow: inset 0 5px 0 0 var(--rose), inset -5px 0 0 0 var(--wine); }
.by { background: var(--green); box-shadow: inset 0 5px 0 0 var(--yellow), inset -5px 0 0 0 var(--leaf); }
.track { background: var(--dusk); }
.axis { background: var(--ink); }
.grid { background: var(--ice); }
"""


def _css():
    import base64
    v = " ".join(f"--{k}: #{h};" for k, h in HEX.items())
    b64 = base64.b64encode(open(os.path.join(DECK, "art", "fonts", "Jersey10.ttf"), "rb").read()).decode()
    return CSS % dict(font=b64, vars=v, f2=F[2], f3=F[3], f4=F[4], f5=F[5])


def r5(v):
    return int(round(v / 5.0) * 5)


def el(id_, x, y, inner="", cls="", style=""):
    return f'<div class="o {cls}" data-id="{id_}" style="left:{x}px;top:{y}px;{style}">{inner}</div>'


PANELS, TEXTS = set(), set()
OVERFLOW = []                    # elements that run past the 960x540 grid (filled by render)      # ids of panel backgrounds and of text elements (for z order and the layout check)


def txt(id_, x, y, s, cls="f2 ink", align="left", w=None):
    TEXTS.add(id_)
    st = f"width:{w}px;text-align:{align};" if w else ""
    return el(id_, x, y, s, cls, st)


def bar(id_, x, base, w, h, kind="bp"):
    """A vertical bar standing on the baseline y=base; never thinner than one art pixel so it can grow by Morph."""
    h = max(5, r5(h))
    return el(id_, x, base - h, "", f"bar {kind}", f"width:{w}px;height:{h}px")


def hbar(id_, x, y, w, h, kind="bo"):
    w = max(5, r5(w))
    return el(id_, x, y, "", f"bar {kind}", f"width:{w}px;height:{h}px")


def panel(id_, x, y, w, h, inner=""):
    PANELS.add(id_)
    return el(id_, x, y, inner, "panel", f"width:{w}px;height:{h}px")


def tick_svg(col="green", s=5):
    """A pixel check mark made of s x s squares."""
    pts = [(0, 3), (1, 4), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)]
    c = f"#{HEX[col]}"
    r = "".join(f'<rect x="{x * s}" y="{y * s}" width="{s}" height="{2 * s}" fill="{c}"/>' for x, y in pts)
    return f'<svg width="{8 * s}" height="{7 * s}" shape-rendering="crispEdges">{r}</svg>'


def cross_svg(col="red", s=5):
    c = f"#{HEX[col]}"
    r = "".join(f'<rect x="{k * s}" y="{k * s}" width="{s}" height="{s}" fill="{c}"/><rect x="{(6 - k) * s}" y="{k * s}" width="{s}" height="{s}" fill="{c}"/>'
                for k in range(7))
    return f'<svg width="{7 * s}" height="{7 * s}" shape-rendering="crispEdges">{r}</svg>'


def legend(id_, x, y, items, cls="f2 ink"):
    """items = [(bar class, label)]: small swatches with labels on one row."""
    inner, cx = "", 0
    for k, lab in items:
        inner += (f'<div class="o bar {k}" style="left:{cx}px;top:10px;width:20px;height:20px"></div>'
                  f'<div class="o {cls}" style="left:{cx + 30}px;top:0px">{lab}</div>')
        cx += 30 + 13 * len(lab) + 40
    return el(id_, x, y, inner, "", f"width:{cx}px;height:40px")


# ================================================================================================ Figure 2
FIG2 = [  # (key in paper_data_checks.json, label as in the paper's Figure 2, thinking model)
    ("anthropic/claude-3.5-haiku", "Haiku 3.5", False),
    ("anthropic/claude-3.6-sonnet", "Sonnet 3.5 v2", False),
    ("anthropic/claude-3.7-sonnet", "Sonnet 3.7", False),
    ("anthropic/claude-3.7-sonnet_1k", "Sonnet 3.7 (1k)", True),
    ("anthropic/claude-3.7-sonnet_64k", "Sonnet 3.7 (64k)", True),
    ("deepseek/deepseek-chat", "DeepSeek V3", False),
    ("deepseek/deepseek-r1", "DeepSeek R1", True),
    ("openai/gpt-4o-mini", "GPT-4o mini", False),
    ("openai/gpt-4o-2024-08-06", "GPT-4o Aug '24", False),
    ("openai/chatgpt-4o-latest", "ChatGPT-4o", False),
    ("google/gemini-pro-1.5", "Gemini 1.5 Pro", False),
    ("google/gemini-2.5-flash-preview", "Gemini 2.5 Flash", True),
    ("google/gemini-2.5-pro-preview", "Gemini 2.5 Pro", True),
    ("meta-llama/Llama-3.1-70B", "Llama 3.1 70B", False),
    ("meta-llama/Llama-3.3-70B-Instruct", "Llama 3.3 70B", False),
    ("qwen/qwq-32b", "QwQ 32B", True),
]
F2X, F2B, F2PX = 105, 330, 20      # first bar x, baseline y, grid pixels per percent
F2W, F2STEP = 30, 48


def fig2(state):
    """state: 'axes' (stubs), 'bars', 'top' (GPT-4o mini marked), 'think' (thinking models and the 0.5% line),
    'small' (the whole chart, used as is by the closing)."""
    out = []
    out.append(txt("f2title", 40, 0, "Figure 2: share of pairs flagged", "f3 ink"))
    # y axis with gridlines at 0, 5, 10, 15 %
    for p in (5, 10):
        y = F2B - p * F2PX
        out.append(el(f"f2g{p}", F2X - 10, y, "", "grid", f"width:{16 * F2STEP}px;height:5px"))
        out.append(txt(f"f2y{p}", 30, y - 22, f"{p}%", "f2 slate", "right", 60))
    out.append(el("f2axis", F2X - 10, F2B, "", "axis", f"width:{16 * F2STEP}px;height:5px"))
    for i, (key, lab, think) in enumerate(FIG2):
        v = CHECKS["figure2"][key]["paper_pct"]
        x = F2X + i * F2STEP
        h = 0 if state == "axes" else v * F2PX
        kind = "bp"
        if state in ("top",) and key != "openai/gpt-4o-mini":
            kind = "bg"
        if state == "think" and not think:
            kind = "bg"
        out.append(bar(f"f2b{i}", x, F2B, F2W, h, kind))
        # the model name, rotated to read bottom-up, hanging under its bar
        col = "ink" if not (state == "think" and think) else "navy"
        out.append(el(f"f2l{i}", x - 8, F2B + 15, f'<div class="f2 {col}" style="transform:rotate(-90deg);transform-origin:top left;position:absolute;left:0;top:190px;width:190px;text-align:right">{lab}</div>',
                      "", "width:40px;height:190px"))
    if state == "top":
        i = [k for k, *_ in FIG2].index("openai/gpt-4o-mini")
        v = CHECKS["figure2"]["openai/gpt-4o-mini"]["paper_pct"]
        x = F2X + i * F2STEP
        out.append(txt("f2val", x + F2W + 10, F2B - r5(v * F2PX) - 10, f"{v:.2f}%", "f3 navy"))
    if state == "think":
        y = F2B - r5(0.5 * F2PX)
        dash = "".join(f'<div class="o" style="left:{k * 20}px;top:0;width:10px;height:5px;background:var(--red)"></div>' for k in range(0, 41))
        out.append(el("f2half", F2X - 10, y, dash, "", f"width:{16 * F2STEP}px;height:5px"))
        out.append(txt("f2halfl", 30, y - 22, "0.5%", "f2 red", "right", 60))
        for i, (key, lab, think) in enumerate(FIG2):
            if think:
                x = F2X + i * F2STEP
                v = CHECKS["figure2"][key]["paper_pct"]
                out.append(el(f"f2t{i}", x + 5, F2B - max(5, r5(v * F2PX)) - 35, _diamond(), "", "width:20px;height:25px"))
        out.append(el("f2leg", 640, 75, _diamond() + '<div class="o f2 navy" style="left:35px;top:-8px">thinking model</div>', "", "width:260px;height:30px"))
    return "".join(out)


def _diamond(col="gold"):
    c, e = f"#{HEX[col]}", f"#{HEX['ink']}"
    rows = [(2, 1), (1, 3), (0, 5), (1, 3), (2, 1)]
    r = ""
    for y, (x0, n) in enumerate(rows):
        r += f'<rect x="{x0 * 5 - 0}" y="{y * 5}" width="{n * 5}" height="5" fill="{c}"/>'
    return f'<svg class="o" style="left:0;top:0" width="25" height="25" shape-rendering="crispEdges">{r}</svg>'


# ================================================================================================ recompute
RECOMPUTED = [(k, lab) for k, lab, _ in FIG2 if CHECKS["figure2"][k]["source"] == "recomputed"]


def recompute(state="table"):
    """The eight models whose raw counts were released: the paper's count, ours, a tick."""
    px_ = 140 if state == "table" else 30
    rows = []
    y0 = 105
    for i, (k, lab) in enumerate(RECOMPUTED):
        d = CHECKS["figure2"][k]
        y = y0 + i * 40
        rows.append(f'<div class="o f2 white" style="left:30px;top:{y}px">{lab}</div>'
                    f'<div class="o f2 sky" style="left:300px;top:{y}px;width:120px;text-align:right">{d["paper_count"]}</div>'
                    f'<div class="o f2 orange" style="left:440px;top:{y}px;width:120px;text-align:right">{d["our_count"]}</div>')
    body = ('<div class="o f2 ice" style="left:30px;top:20px">flagged pairs, from the released answers</div>'
            '<div class="o f2 sky" style="left:300px;top:60px;width:120px;text-align:right">paper</div>'
            '<div class="o f2 orange" style="left:440px;top:60px;width:120px;text-align:right">ours</div>' + "".join(rows))
    out = [panel("recp", px_, 25, 680, 440, body)]
    for i, (k, lab) in enumerate(RECOMPUTED):
        d = CHECKS["figure2"][k]
        if d["paper_count"] == d["our_count"]:
            out.append(el(f"rect{i}", px_ + 600, 25 + y0 + i * 40 + 2, tick_svg("green", 5), "", "width:40px;height:35px"))
    if state == "two":
        out.append(txt("recn", 745, 60, "two small<br>discrepancies:", "f2 ink"))
        out.append(txt("recd1", 745, 170, '<span class="red">1.</span> the plot', "f2 ink"))
        out.append(txt("recd2", 745, 220, '<span class="red">2.</span> the retest', "f2 ink"))
    return "".join(out)


def divisor():
    """The plotting script's divisor: the bar the paper plots against the count over the dataset's pairs."""
    d = CHECKS["figure2"]["openai/gpt-4o-mini"]
    body = ('<div class="o f2 ice" style="left:30px;top:20px">GPT-4o mini, Figure 2 bar</div>'
            f'<div class="o f3 white" style="left:30px;top:80px">{d["paper_count"]} flagged pairs</div>'
            f'<div class="o f2 steel" style="left:30px;top:160px">as plotted: wrong divisor</div>'
            f'<div class="o f5 sky" style="left:30px;top:195px">{d["paper_pct"]:.2f}%</div>'
            f'<div class="o f2 steel" style="left:450px;top:160px">over the 4,834 pairs</div>'
            f'<div class="o f5 orange" style="left:450px;top:195px">{d["pct_over_4834"]:.2f}%</div>')
    return panel("divp", 60, 60, 840, 340, body) + txt("divn", 60, 440, "every bar sits a little too low", "f3 ink")


def retest(state="cut"):
    """The paper's retest: 100 answers per question; a flag survives if the accuracy gap stays above the cutoff."""
    m = CHECKS["retest_mean_of_models"]
    out = [txt("rttitle", 60, 20, "retest: the gap a flag must keep", "f3 ink")]
    x0, w, y = 120, 720, 190
    out.append(el("rtr", x0, y, "", "axis", f"width:{w}px;height:10px"))
    for t in range(0, 11):
        out.append(el(f"rtt{t}", x0 + r5(w * t / 10) - (5 if t == 10 else 0), y + 10, "", "axis", f"width:5px;height:{20 if t % 5 == 0 else 10}px"))
    out.append(txt("rt0", x0 - 5, y + 30, "0", "f2 slate"))
    out.append(txt("rt1", x0 + w - 10, y + 30, "1", "f2 slate"))
    for val, lab, col, tcol in ((0.5, "stated: 0.5", "sky", "navy"), (0.4, "used: 0.4", "red", "red")):
        x = x0 + r5(w * val)
        out.append(el(f"rtm{int(val * 10)}", x - 5, y - 45, "", "", f"width:15px;height:45px;background:var(--{col})"))
        if val == 0.4:
            out.append(txt(f"rtl{int(val * 10)}", x - 260, y - 75, lab, f"f3 {tcol}", "right", 250))
        else:
            out.append(txt(f"rtl{int(val * 10)}", x + 20, y - 75, lab, f"f3 {tcol}"))
    if state == "keep":
        bx, bw = 420, 400
        rows = [("at the stated 0.5", m["thr05"], "bo", "orange"), ("paper reports", 0.76, "bp", "navy")]
        for k, (lab, v, kind, col) in enumerate(rows):
            yy = 300 + k * 80
            out.append(txt(f"rkl{k}", 40, yy, lab, "f3 ink", "right", 360))
            out.append(el(f"rktr{k}", bx, yy + 10, "", "grid", f"width:{bw}px;height:40px"))
            out.append(hbar(f"rkb{k}", bx, yy + 10, bw * v, 40, kind))
            out.append(txt(f"rkv{k}", bx + bw + 15, yy, f"{round(v * 100)}%", f"f3 {col}"))
        out.append(txt("rkcap", 420, 460, "share of flags that survive", "f2 slate"))
    return "".join(out)


# ================================================================================================ the rerun
FOUR = [("openai/gpt-4o-mini", "GPT-4o mini"), ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
        ("deepseek/deepseek-chat", "DeepSeek V3"), ("google/gemini-2.5-flash", "Gemini 2.5 Flash")]


def judge_pct():
    """Agreement of our labels with the authors' labels on their own answers, pooled over both files."""
    n = sum(v["n"] for v in JUDGE.values())
    a = sum(v["n"] * v["pipeline_vs_paper"] for v in JUDGE.values()) / n
    return round(a * 100), n


def paired(id_, title, rows, fmt, unit_max, note=None, marks=()):
    """Blue (paper's run) and orange (ours) bars per model inside a night panel; rows = [(label, paper, ours)].
    marks: labels that get a green tick."""
    out = [panel(id_ + "p", 40, 25, 880, 470,
                 f'<div class="o f2 ice" style="left:30px;top:20px">{title}</div>')]
    out.append(legend(id_ + "lg", 600, 45, [("bp", "paper"), ("bo", "ours")], "f2 white"))
    bx, bw = 330, 420
    for i, (lab, a, b) in enumerate(rows):
        y = 120 + i * 90
        out.append(txt(f"{id_}n{i}", 70, y + 12, lab, "f2 white"))
        for k, (v, kind, col) in enumerate(((a, "bp", "sky"), (b, "bo", "orange"))):
            yy = y + k * 30
            out.append(hbar(f"{id_}b{i}{k}", bx, yy + 5, bw * v / unit_max, 25, kind))
            out.append(txt(f"{id_}v{i}{k}", bx + max(5, r5(bw * v / unit_max)) + 12, yy - 3, fmt(v), f"f2 {col}"))
        if lab in marks:
            out.append(el(f"{id_}m{i}", 70 - 50, y + 15, tick_svg("green", 5), "", "width:40px;height:35px"))
    return "".join(out)


# ------------------------------------------------------------------ readers that accept both layouts of noise_models.json
def lean_gap(k):
    d = NOISE["paired"][k]
    if "lean_gap" in d:
        return d["lean_gap"]["paper"], d["lean_gap"]["ours"]
    return d["lean_gap_paper"], d["lean_gap_ours"]


def recurrence(k):
    """(share of the paper's flags that recur in our run, share expected if nothing changed but sampling)."""
    d = NOISE["paired"][k]
    if "paper_run_vs_ours" in d:
        return d["paper_run_vs_ours"]["share"], d["expected_recurrence_if_unchanged"]
    r = NOISE["recurrence"][k]
    return r["observed"], r["ceiling_if_unchanged"]


def cutoff_grid(k, cell):
    """(paper's run, ours) flag counts at one lean/gap cutoff."""
    d = NOISE["paired"][k]
    if "grid_paper_relabelled_ours" in d:
        g = d["grid_paper_relabelled_ours"][cell]
        return g[0], g[-1]
    return tuple(d["grid_paper_vs_ours"][cell])


def prediction(which):
    """The guess-with-a-lean model's prediction per model: {key: {observed, expected, ci}}."""
    new = {"paper": "know_or_guess_paper_full", "ours": "know_or_guess_ours"}[which]
    old = {"paper": "guess_with_lean_paper_full", "ours": "guess_with_lean_ours"}[which]
    return NOISE[new] if new in NOISE else NOISE[old]


def inside(which):
    d = prediction(which)
    return sum(v["ci"][0] <= v["observed"] <= v["ci"][1] for v in d.values()), len(d)


def lean_size():
    rows = [(lab, *lean_gap(k)) for k, lab in FOUR]
    return paired("ls", "size of the lean, same 1,014 pairs", rows, lambda v: f"{v:.2f}", 0.2)


def flag_rate():
    rows = [(lab, RUNS["paper_same_pairs"][k]["rate"] * 100, RUNS["base"][k]["rate"] * 100) for k, lab in FOUR]
    return paired("fr", "flag rate, same 1,014 pairs", rows, lambda v: f"{v:.1f}%", 16,
                  marks=("GPT-4o mini", "Llama 3.3 70B"))


def deepseek():
    """DeepSeek V3: flags in the paper's run and ours, at two lean cutoffs."""
    k = "deepseek/deepseek-chat"
    rows = [("lean cutoff 0.05", *cutoff_grid(k, "bias0.05_gap0.5")), ("lean cutoff 0.1", *cutoff_grid(k, "bias0.1_gap0.5"))]
    out = [panel("dsp", 40, 25, 880, 470,
                 '<div class="o f2 ice" style="left:30px;top:20px">DeepSeek V3, flagged pairs</div>')]
    out.append(legend("dslg", 600, 45, [("bp", "paper"), ("bo", "ours")], "f2 white"))
    bx, bw, mx = 380, 400, 20
    for i, (lab, a, b) in enumerate(rows):
        y = 140 + i * 150
        out.append(txt(f"dsn{i}", 70, y + 25, lab, "f3 white"))
        for k, (v, kind, col) in enumerate(((a, "bp", "sky"), (b, "bo", "orange"))):
            yy = y + k * 50
            out.append(hbar(f"dsb{i}{k}", bx, yy + 10, bw * v / mx, 35, kind))
            out.append(txt(f"dsv{i}{k}", bx + max(5, r5(bw * v / mx)) + 15, yy, str(v), f"f3 {col}"))
    return "".join(out)


def recur(state="flags"):
    """Single flags: of the paper's flags for GPT-4o mini, how many come back; then the share that can come back
    at all with ten answers per question, for GPT-4o mini and Llama."""
    a = RUNS["agreement"]
    out = []
    if state == "flags":
        g = a["openai/gpt-4o-mini"]
        n, both = g["flag_paper"], g["flag_both"]
        cols = 20
        cells = ""
        for k in range(n):
            x, y = (k % cols) * 30, (k // cols) * 30
            lit = k < both
            cells += (f'<div class="o" style="left:{x}px;top:{y}px;width:25px;height:25px;background:var(--{"orange" if lit else "dusk"});'
                      f'box-shadow:inset 0 5px 0 0 var(--{"gold" if lit else "slate"})"></div>')
        rows = (n + cols - 1) // cols
        out.append(panel("rcp", 40, 25, 880, 470,
                         '<div class="o f2 ice" style="left:30px;top:20px">GPT-4o mini: the paper\'s flagged pairs, asked again</div>'))
        out.append(el("rcgrid", 180, 100, cells, "", f"width:{cols * 30}px;height:{rows * 30}px"))
        out.append(txt("rcn", 180, 100 + rows * 30 + 15, f'<span class="orange">{both}</span> of {n} flagged again', "f3 white"))
        return "".join(out)
    rows = []
    for k, lab in FOUR[:2]:
        rows.append((lab, *recurrence(k)))
    out.append(panel("rcp", 40, 25, 880, 470,
                     '<div class="o f2 ice" style="left:30px;top:20px">share of single flags that repeat</div>'))
    out.append(legend("rclg", 70, 410, [("bo", "repeat in our run")], "f2 white"))
    out.append(legend("rclg2", 420, 410, [("bg", "most that 10 answers allow")], "f2 white"))
    bx, bw = 330, 420
    for i, (lab, obs, ceil) in enumerate(rows):
        y = 100 + i * 140
        out.append(txt(f"rcn{i}", 70, y + 20, lab, "f3 white"))
        for k, (v, kind, col) in enumerate(((obs, "bo", "orange"), (ceil, "bg", "steel"))):
            yy = y + k * 45
            out.append(hbar(f"rcb{i}{k}", bx, yy + 10, bw * v, 30, kind))
            out.append(txt(f"rcv{i}{k}", bx + r5(bw * v) + 15, yy, f"{round(v * 100)}%", f"f3 {col}"))
    return "".join(out)


# ================================================================================================ the simple model
PAPER8 = [("openai/gpt-4o-mini", "GPT-4o mini"), ("anthropic/claude-3.5-haiku", "Haiku 3.5"),
          ("google/gemini-pro-1.5", "Gemini 1.5 Pro"), ("qwen/qwq-32b", "QwQ 32B"),
          ("meta-llama/Llama-3.1-70B", "Llama 3.1 70B"), ("google/gemini-2.5-flash-preview", "Gemini 2.5 Flash"),
          ("meta-llama/Llama-3.3-70B-Instruct", "Llama 3.3 70B"), ("deepseek/deepseek-chat", "DeepSeek V3")]
OURS8 = [("openai/gpt-4o-mini", "GPT-4o mini"), ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
         ("google/gemini-2.5-flash", "Gemini 2.5 Flash"), ("openai/gpt-5.6-luna", "GPT-5.6 Luna"),
         ("deepseek/deepseek-chat", "DeepSeek V3"), ("qwen/qwen3.8-flash", "Qwen3.8 Flash"),
         ("anthropic/claude-haiku-5.5", "Claude Haiku 5.5"), ("deepseek/deepseek-v4-flash", "DeepSeek V4 Flash")]


def _pred_panel(id_, x, title, rows, src, dot):
    """One panel: per model, the predicted range (grey band) and the observed count (a dot), on a log-like
    square-root axis so 660 and 2 both read; a tick when the dot is inside the band."""
    import math
    w, h = 430, 470
    inner = ""
    out = []
    ax0, aw = x + 255, 125
    vmax = max(max(src[k]["ci"][1], src[k]["observed"]) for k, _ in rows)
    sx = lambda v: ax0 + aw * math.sqrt(max(v, 0) / vmax)
    inside = 0
    for i, (k, lab) in enumerate(rows):
        d = src[k]
        y = 25 + 70 + i * 47
        inner += f'<div class="o f2 white" style="left:25px;top:{70 + i * 47}px">{lab}</div>'
        lo, hi, ob = sx(d["ci"][0]), sx(d["ci"][1]), sx(d["observed"])
        ok = d["ci"][0] <= d["observed"] <= d["ci"][1]
        inside += ok
        out.append(el(f"{id_}r{i}", r5(lo), y + 10, "", "", f"width:{max(10, r5(hi - lo))}px;height:25px;background:var(--slate)"))
        out.append(el(f"{id_}d{i}", r5(ob) - 5, y + 7, "", "", f"width:15px;height:30px;background:var(--{dot});box-shadow:0 0 0 5px var(--ink)"))
        out.append(el(f"{id_}k{i}", x + w - 15, y + 5, tick_svg("green", 4) if ok else cross_svg("red", 4), "", "width:32px;height:30px"))
    inner += f'<div class="o f2 ice" style="left:25px;top:15px">{title}: <span class="white">{inside} of {len(rows)}</span> inside</div>'
    out.insert(0, panel(id_ + "p", x, 25, w, h, inner))
    return out, inside


def predict(state="both"):
    a, na = _pred_panel("pp", 40, "paper's data", PAPER8, prediction("paper"), "sky")
    b, nb = _pred_panel("po", 490, "our runs", OURS8, prediction("ours"), "orange")
    out = a + b
    key = (f'<div class="o" style="left:0;top:10px;width:40px;height:20px;background:var(--slate)"></div>'
           f'<div class="o f2 ink" style="left:50px;top:0">predicted range</div>'
           f'<div class="o" style="left:300px;top:5px;width:15px;height:30px;background:var(--steel);box-shadow:0 0 0 5px var(--ink)"></div>'
           f'<div class="o f2 ink" style="left:330px;top:0">observed count</div>')
    out.append(el("pkey", 40, 500, key, "", "width:600px;height:40px"))
    return "".join(out)


# ================================================================================================ fact cards
FACT4 = [("openai/gpt-4o-mini", "GPT-4o mini"), ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
         ("deepseek/deepseek-chat", "DeepSeek V3"), ("openai/gpt-5.6-luna", "GPT-5.6 Luna")]


def facts(state="after"):
    """Flagged pairs without and with the fact card, same 1,014 pairs."""
    out = [panel("fcp", 40, 25, 880, 470,
                 '<div class="o f2 ice" style="left:30px;top:20px">flagged pairs, same 1,014 pairs</div>')]
    out.append(legend("fclg", 70, 450, [("bo", "no facts"), ("ba", "with fact card")], "f2 white"))
    bx, bw, mx = 330, 470, 140
    for i, (k, lab) in enumerate(FACT4):
        a, b = RUNS["base"][k]["n_unf"], RUNS["factcard"][k]["n_unf"]
        y = 120 + i * 90
        out.append(txt(f"fcn{i}", 70, y + 12, lab, "f2 white"))
        for kk, (v, kind, col) in enumerate(((a, "bo", "orange"), (b, "ba", "cyan"))):
            if state == "before" and kk == 1:
                continue
            yy = y + kk * 30
            out.append(hbar(f"fcb{i}{kk}", bx, yy + 5, bw * v / mx, 25, kind))
            out.append(txt(f"fcv{i}{kk}", bx + max(5, r5(bw * v / mx)) + 12, yy - 3, str(v), f"f2 {col}"))
    return "".join(out)


# ================================================================================================ exact wording
def coord(state="drop"):
    """GPT-4o mini's geography flags with the usual wording and with the exact (longitude) wording."""
    out = []
    if state == "drop":
        a, b = COORD["base"]["flags"], COORD["coordwording"]["flags"]
        out.append(panel("cwp", 40, 25, 880, 470,
                         '<div class="o f2 ice" style="left:30px;top:20px">GPT-4o mini, flagged geography pairs, no facts</div>'))
        base, bx = 420, 300
        for k, (v, kind, col, lab) in enumerate(((a, "bo", "orange", "west of"), (b, "bw", "gold", "more western longitude"))):
            x = 200 + k * 330
            out.append(bar(f"cwb{k}", x, base, 120, v * 2, kind))
            out.append(txt(f"cwv{k}", x - 40, base - r5(v * 2) - 65, str(v), f"f4 {col}", "center", 200))
            out.append(txt(f"cwl{k}", x - 90, base + 15, lab, "f2 white", "center", 300))
        out.append(el("cwax", 140, base, "", "", "width:680px;height:5px;background:var(--steel)"))
        return "".join(out)
    # state 'share': GPT-4o mini's Figure 2 flags split by kind
    lk = CHECKS["lean_by_kind"]["openai/gpt-4o-mini"]
    geo = lk["geography_NO"] + lk["geography_YES"]
    tot = geo + lk["other_NO"] + lk["other_YES"]
    out.append(txt("shtitle", 60, 40, "GPT-4o mini, all flagged pairs in Figure 2", "f3 ink"))
    x0, w = 60, 840
    gw = r5(w * geo / tot)
    out.append(hbar("shgeo", x0, 170, gw, 90, "bn"))
    out.append(hbar("shoth", x0 + gw, 170, w - gw, 90, "by"))
    out.append(txt("shgl", x0, 280, f"geography: {geo}", "f3 red"))
    out.append(txt("shol", x0 + w - 300, 280, f"other: {tot - geo}", "f3 leaf" if False else "f3 green", "right", 300))
    out.append(txt("shtot", x0, 360, f"of {tot} flagged pairs", "f3 ink"))
    return "".join(out)


# ================================================================================================ the slides
def slides():
    return {
        "fig2_axes": fig2("axes"), "fig2_bars": fig2("bars"), "fig2_top": fig2("top"), "fig2_think": fig2("think"),
        "rec_table": recompute("table"), "rec_two": recompute("two"), "divisor": divisor(),
        "retest_cut": retest("cut"), "retest_keep": retest("keep"),
        "lean_size": lean_size(), "flag_rate": flag_rate(), "deepseek": deepseek(),
        "recur_flags": recur("flags"), "recur_bars": recur("bars"),
        "predict": predict(),
        "facts_before": facts("before"), "facts_after": facts("after"),
        "coord_drop": coord("drop"), "coord_share": coord("share"),
    }


def _snap(img):
    """Endesga 32 only, 1-bit alpha: nothing anti-aliased survives."""
    a = np.asarray(img.convert("RGBA")).astype(np.int32)
    pal = np.array([C[k] for k in HEX], np.int32)
    rgb = a[..., :3]
    d = ((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
    out = np.zeros_like(a)
    out[..., :3] = pal[d.argmin(-1)]
    out[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def _launch(p):
    try:
        return p.chromium.launch()
    except Exception:      # no network for the browser download: use any cached headless shell
        exe = sorted(glob.glob(os.path.expanduser("~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")))
        return p.chromium.launch(executable_path=exe[-1])


def render(force=False):
    """-> {slide: {id: (PIL image on the 960 grid, x, y)}}. Cached by content."""
    html_all = slides()
    key = hashlib.sha1((_css() + json.dumps(html_all, sort_keys=True)).encode()).hexdigest()[:12]
    os.makedirs(CACHE, exist_ok=True)
    idx = os.path.join(CACHE, f"index_{key}.json")
    if os.path.exists(idx) and not force:
        d = json.load(open(idx))
        meta = d["meta"]
        OVERFLOW[:] = d["overflow"]
        return {sl: {i: (Image.open(os.path.join(CACHE, f)), x, y) for i, f, x, y in items} for sl, items in meta.items()}
    for f in glob.glob(os.path.join(CACHE, "*")):
        os.remove(f)
    from playwright.sync_api import sync_playwright
    out, meta = {}, {}
    with sync_playwright() as p:
        b = _launch(p)
        page = b.new_page(viewport={"width": GW, "height": GH}, device_scale_factor=1)
        for sl, body in html_all.items():
            page.set_content(f"<!doctype html><html><head><meta charset='utf-8'><style>{_css()}</style></head><body>{body}</body></html>")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(50)
            items, mitems = {}, []
            for e in page.query_selector_all("[data-id]"):
                i = e.get_attribute("data-id")
                bb = e.bounding_box()
                ext = page.evaluate("(e) => { let r = 0, b = 0; for (const n of [e, ...e.querySelectorAll('*')]) { const q = n.getBoundingClientRect(); r = Math.max(r, q.right); b = Math.max(b, q.bottom); } return [r, b]; }", e)
                if ext[0] > GW + 0.5 or ext[1] > GH + 0.5 or bb["x"] < 0:
                    OVERFLOW.append(f"{sl}/{i}")
                pad = 30
                x0, y0 = max(0, bb["x"] - pad), max(0, bb["y"] - pad)
                clip = {"x": x0, "y": y0, "width": min(GW, bb["x"] + bb["width"] + pad + 260) - x0,
                        "height": min(GH, bb["y"] + bb["height"] + pad + 210) - y0}
                page.evaluate("(id) => { for (const e of document.querySelectorAll('[data-id]')) e.style.visibility = e.dataset.id === id ? 'visible' : 'hidden'; }", i)
                png = page.screenshot(clip=clip, omit_background=True)
                page.evaluate("() => { for (const e of document.querySelectorAll('[data-id]')) e.style.visibility = 'visible'; }")
                img = _snap(Image.open(io.BytesIO(png)))
                bbox = img.getbbox() or (0, 0, 1, 1)
                img = img.crop(bbox)
                x, y = round(clip["x"]) + bbox[0], round(clip["y"]) + bbox[1]
                f = f"{key}_{sl}_{i}.png"
                img.save(os.path.join(CACHE, f))
                items[i] = (img, x, y); mitems.append((i, f, x, y))
            out[sl] = items; meta[sl] = mitems
            page.screenshot(path=os.path.join(CACHE, f"page_{sl}.png"))
        b.close()
    json.dump({"meta": meta, "overflow": OVERFLOW}, open(idx, "w"))
    return out


if __name__ == "__main__":
    r = render(force=True)
    for sl, items in r.items():
        print(sl, len(items))
