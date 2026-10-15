"""The charts and number panels, authored in HTML/CSS on the finer 960x540 grid (2.5 x the 384x216 art grid),
rendered by headless Chromium, snapped to Endesga 32 with no anti-aliasing, and cut into one picture per element
(every element with a data-id), so bars can grow and panels can glide by Morph.

Every figure on screen is read here from the result files and nowhere else:
  results/paper_data_checks.json, results/runs.json, results/noise_models.json, results/geo_analysis.json,
  data/judge_validation/summary.json.
Semantic colours: the paper's run blue, our run orange, fact cards aqua, highlight yellow, unknown grey.

Each board says where its data come from: the paper's figures and data are printed paper on legs; the released
data recomputed is a dark terminal on a monitor stand; our own runs are a white board with an orange rim on a lab
bench. A standard board is 600 grid px wide (62% of the frame) with the big robot standing beside it."""
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
GEO = J("geo_analysis.json")
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
.f6 { font-size: %(f6)spx; line-height: 120px; }
/* the boards */
.paper { background: var(--white); box-shadow: 0 0 0 5px var(--ink), 10px 10px 0 5px var(--ice); }
.term { background: var(--night); box-shadow: inset 0 0 0 5px var(--dusk), 0 0 0 5px var(--ink); }
.bench { background: var(--white);
  box-shadow: inset 0 0 0 5px var(--orange), inset 0 0 0 10px var(--white), 0 0 0 5px var(--ink), 10px 10px 0 5px var(--ice); }
.hatch { background: repeating-linear-gradient(90deg, var(--sky) 0 10px, var(--orange) 10px 20px); }
.map { background: repeating-linear-gradient(0deg, var(--white) 0 10px, transparent 10px 20px) 0 100%% / 100%% 240px no-repeat,
                   repeating-linear-gradient(90deg, transparent 0 95px, var(--ice) 95px 100px) 0 100%% / 100%% 240px no-repeat, var(--white);
  box-shadow: inset 0 0 0 5px var(--sand), inset 0 0 0 10px var(--white), 0 0 0 5px var(--ink), 10px 10px 0 5px var(--ice); }
.hl { background: var(--yellow); padding: 0 8px; }
.white { color: var(--white); } .ice { color: var(--ice); } .steel { color: var(--steel); } .slate { color: var(--slate); }
.ink { color: var(--ink); } .green { color: var(--green); } .red { color: var(--red); } .gold { color: var(--gold); }
.yellow { color: var(--yellow); } .sky { color: var(--sky); } .cyan { color: var(--cyan); } .orange { color: var(--orange); }
.navy { color: var(--navy); } .rose { color: var(--rose); } .rust { color: var(--rust); } .deep { color: var(--deep); }
/* pixel bars: lit top edge, shaded right edge (light from the top left), on the 5px grid */
.bar { }
.bp { background: var(--sky); box-shadow: inset 0 5px 0 0 var(--cyan), inset -5px 0 0 0 var(--navy); }
.bo { background: var(--orange); box-shadow: inset 0 5px 0 0 var(--gold), inset -5px 0 0 0 var(--rust); }
.bod { background: repeating-linear-gradient(90deg, var(--orange) 0 5px, transparent 5px 10px); }
.ba { background: var(--cyan); box-shadow: inset 0 5px 0 0 var(--white), inset -5px 0 0 0 var(--sky); }
.bdim { background: var(--dusk); box-shadow: inset 0 0 0 5px var(--steel); }
.bw { background: var(--white); box-shadow: inset -5px 0 0 0 var(--ice); }
.bg { background: var(--steel); box-shadow: inset 0 5px 0 0 var(--ice), inset -5px 0 0 0 var(--slate); }
.bpl { background: var(--ice); box-shadow: inset -5px 0 0 0 var(--steel); }
.bm { background: repeating-linear-gradient(90deg, var(--sky) 0 10px, var(--orange) 10px 20px); box-shadow: inset 0 5px 0 0 var(--white), inset -5px 0 0 0 var(--rust); }
.axis { background: var(--ink); }
.grid { background: var(--ice); }
"""


def _css():
    import base64
    v = " ".join(f"--{k}: #{h};" for k, h in HEX.items())
    b64 = base64.b64encode(open(os.path.join(DECK, "art", "fonts", "Jersey10.ttf"), "rb").read()).decode()
    return CSS % dict(font=b64, vars=v, f2=F[2], f3=F[3], f4=F[4], f5=F[5], f6=F[6])


def r5(v):
    return int(round(v / 5.0) * 5)


def el(id_, x, y, inner="", cls="", style=""):
    return f'<div class="o {cls}" data-id="{id_}" style="left:{x}px;top:{y}px;{style}">{inner}</div>'


PANELS, TEXTS, GRIDS, PLATES = set(), set(), set(), set()   # board backgrounds, text, gridlines, plates over gridlines
OVERFLOW = []                                  # elements that run past the 960x540 grid (filled by render)


def txt(id_, x, y, s, cls="f2 ink", align="left", w=None):
    TEXTS.add(id_)
    st = f"width:{w}px;text-align:{align};" if w else ""
    return el(id_, x, y, s, cls, st)


def blen(v):
    """Bar length on the grid: the 5px grid for long bars, exact (at least 3px, one native pixel) for short ones so
    small values keep their proportions and stay visible; 0 for a value of 0."""
    if v <= 0:
        return 0
    return r5(v) if v >= 25 else max(3, round(v))


def bar(id_, x, base, w, h, kind="bp", exact=False):
    """A vertical bar standing on the baseline y=base; exact=True keeps the height unrounded."""
    h = max(3, round(h)) if exact and h > 0 else blen(h)
    if not h:
        return ""
    return el(id_, x, base - h, "", f"bar {kind}", f"width:{w}px;height:{h}px")


def hbar(id_, x, y, w, h, kind="bo"):
    w = blen(w)
    if not w:
        return ""
    return el(id_, x, y, "", f"bar {kind}", f"width:{w}px;height:{h}px")


def tw(s, size=2):
    """Width of a line of Jersey 10 on the chart grid (f2 by default)."""
    from PIL import ImageFont
    return round(ImageFont.truetype(os.path.join(DECK, "art", "fonts", "Jersey10.ttf"), F[size]).getlength(s))


def band(id_, x, y, w, h):
    """The yellow highlight behind a label (a plate: it sits above gridlines and under text)."""
    PLATES.add(id_)
    return el(id_, x, y, "", "", f"width:{w}px;height:{h}px;background:var(--yellow)")


def grid(id_, x, y, w, h, color="ice"):
    GRIDS.add(id_)
    return el(id_, x, y, "", "", f"width:{w}px;height:{h}px;background:var(--{color})")


# ------------------------------------------------------------------------------------------------ boards
BX, BY, BW, BH = 60, 40, 600, 380      # the standard board: native 24..264 x 16..168, its stand below to the ground
LIGHT = {"paper", "map", "bench"}


def tone(style):
    """Text colours on a board: (names, dimmed, subtitle, paper's value, our value)."""
    if style in LIGHT:
        return dict(name="ink", dim="steel", sub="slate", paper="navy", ours="orange", aqua="deep")
    return dict(name="white", dim="steel", sub="ice", paper="sky", ours="orange", aqua="cyan")


def board(style, title, sub=None, x=BX, y=BY, w=BW, h=BH):
    """The board of a chart and its title (and an optional subtitle). The ids are shared by every chart of a
    scene (bd, bdt, bds), so the board stays put while its contents change."""
    PANELS.add("bd")
    T = tone(style)
    inner = ""
    if style == "term":
        inner = f'<div class="o" style="left:5px;top:5px;width:{w - 10}px;height:45px;background:var(--dusk)"></div>'
        inner += f'<div class="o" style="left:5px;top:50px;width:{w - 10}px;height:5px;background:var(--ink)"></div>'
        for k, c in enumerate(("red", "gold", "green")):
            inner += f'<div class="o" style="left:{22 + k * 20}px;top:22px;width:10px;height:10px;background:var(--{c})"></div>'
    out = [el("bd", x, y, inner, style, f"width:{w}px;height:{h}px")]
    if style == "term":
        out.append(txt("bdt", x + 95, y + 6, title, "f2 white"))
        if sub:
            out.append(txt("bds", x + 30, y + 62, sub, "f2 ice"))
    else:
        out.append(txt("bdt", x + 28, y + 8, title, f"f3 {T['name']}"))
        if sub:
            out.append(txt("bds", x + 28, y + 62, sub, f"f2 {T['sub']}"))
    return "".join(out)


def arrow_svg(col="steel", s=5, n=12):
    """A right-pointing pixel arrow, n squares long."""
    c = f"#{HEX[col]}"
    r = f'<rect x="0" y="{2 * s}" width="{(n - 3) * s}" height="{2 * s}" fill="{c}"/>'
    for k in range(3):
        r += f'<rect x="{(n - 3 + k) * s}" y="{k * s}" width="{s}" height="{(6 - 2 * k) * s}" fill="{c}"/>'
    return f'<svg width="{n * s}" height="{6 * s}" shape-rendering="crispEdges">{r}</svg>'


def _rows_svg(rows, col, s):
    r = "".join(f'<rect x="{x * s}" y="{y * s}" width="{s}" height="{s}" fill="#{HEX[col[ch]]}"/>'
                for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != ".")
    return f'<svg width="{len(rows[0]) * s}" height="{len(rows) * s}" shape-rendering="crispEdges" style="vertical-align:middle">{r}</svg>'


THINK_SVG = _rows_svg(["..XXXXXX..", ".XXXXXXXX.", "XXWXXWXXWX", ".XXXXXXXX.", "..XXXXXX..", ".XX.......", "X........."],
                      {"X": "grape", "W": "white"}, 3)   # a thought bubble with three dots: a thinking model (purple: no other meaning)


def tick_svg(col="green", s=5):
    """A pixel check mark made of s x s squares."""
    pts = [(0, 3), (1, 4), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)]
    c = f"#{HEX[col]}"
    r = "".join(f'<rect x="{x * s}" y="{y * s}" width="{s}" height="{2 * s}" fill="{c}"/>' for x, y in pts)
    return f'<svg width="{8 * s}" height="{7 * s}" shape-rendering="crispEdges">{r}</svg>'


def rank_svg(swap, s=5):
    """A tiny ranking of two neighbouring models at two cutoffs: each model a line from its place at the default
    cutoff (left dot) to its place at another cutoff (right dot). Two parallel steel lines when the order holds;
    two yellow lines that cross when the two swap places."""
    w, y0, y1 = 10, 1, 5
    if swap:
        a = [(x, y0 + round(x * (y1 - y0) / (w - 1))) for x in range(w)]
        b = [(x, y1 + y0 - y) for x, y in a]
        col = "yellow"
    else:
        a = [(x, y0) for x in range(w)]
        b = [(x, y1) for x in range(w)]
        col = "steel"
    r = "".join(f'<rect x="{x * s}" y="{y * s}" width="{s}" height="{s}" fill="#{HEX[col]}"/>' for x, y in a + b)
    for (x, y) in (a[0], b[0], a[-1], b[-1]):
        r += f'<rect x="{x * s}" y="{(y - 0.5) * s}" width="{s}" height="{2 * s}" fill="#{HEX["white"]}"/>'
    return f'<svg width="{w * s}" height="{(y1 + 2) * s}" shape-rendering="crispEdges">{r}</svg>'


def rank_tile(id_, x, y, swap):
    return el(id_, x, y, f'<div class="o" style="left:5px;top:5px">{rank_svg(swap, 4)}</div>', "",
              "width:50px;height:38px;background:var(--dusk);box-shadow:0 0 0 5px var(--slate)")


def legend(id_, x, y, items, cls="f2 ink"):
    """items = [(swatch class or raw html, label)]: small swatches with labels on one row."""
    inner, cx = "", 0
    for k, lab in items:
        sw = (f'<div class="o bar {k}" style="left:{cx}px;top:10px;width:20px;height:20px"></div>' if not k.startswith("<")
              else f'<div class="o" style="left:{cx}px;top:0px">{k}</div>')
        gap = 30 if not k.startswith("<") else 36 + 6
        inner += sw + f'<div class="o {cls}" style="left:{cx + gap}px;top:0px">{lab}</div>'
        cx += gap + tw(lab) + 30
    return el(id_, x, y, inner, "", f"width:{cx}px;height:40px")


# ================================================================================================ Figure 2
FIG2 = [  # (key in paper_data_checks.json, label as in the paper's Figure 2, thinking model)
    ("anthropic/claude-3.5-haiku", "Haiku 3.5", False),
    ("anthropic/claude-3.6-sonnet", "Sonnet 3.5 v2", False),
    ("anthropic/claude-3.7-sonnet", "Sonnet 3.7", False),
    ("anthropic/claude-3.7-sonnet_1k", "Sonnet 3.7 1k", True),
    ("anthropic/claude-3.7-sonnet_64k", "Sonnet 3.7 64k", True),
    ("deepseek/deepseek-chat", "DeepSeek V3", False),
    ("deepseek/deepseek-r1", "DeepSeek R1", True),
    ("openai/gpt-4o-mini", "GPT-4o mini", False),
    ("openai/gpt-4o-2024-08-06", "GPT-4o 2024-08", False),
    ("openai/chatgpt-4o-latest", "ChatGPT-4o", False),
    ("google/gemini-pro-1.5", "Gemini 1.5 Pro", False),
    ("google/gemini-2.5-flash-preview", "Gemini 2.5 Flash", True),
    ("google/gemini-2.5-pro-preview", "Gemini 2.5 Pro", True),
    ("meta-llama/Llama-3.1-70B", "Llama 3.1 70B", False),
    ("meta-llama/Llama-3.3-70B-Instruct", "Llama 3.3 70B", False),
    ("qwen/qwq-32b", "QwQ 32B", True),
]
F2 = dict(x=50, y=14, w=640, h=490)          # the paper board: native 20..276 x 6..202, the full height of the
F2X0, F2PX, F2Y0, F2STEP, F2BH = 300, 19, 32, 29, 15   # stage; 16 rows 2 native px apart; the robot stands to its right
F2TX = 508                                   # the title block, in the empty lower right of the plot
F2_REC = dict(x=66, w=608, h=420, oy=6, step=25, tx=500)   # the 'recomputed' state: a smaller board that clears the
                                             # stage's curtains and valance and sits above the cue plate


def ktxt(id_, x, y, s, cls="f2 navy", bg="white"):
    """A value label on a knockout plate of the board's colour, so gridlines never run through it."""
    TEXTS.add(id_)
    return el(id_, x, y + 9, s, cls, f"background:var(--{bg});padding:0 6px;line-height:22px;height:22px")


def fig2(state):
    """Figure 2 redrawn as horizontal bars, models sorted by their share, names right-aligned on the left, on a
    paper board as tall as the stage. The title sits in the empty lower right of the plot; the gridlines run
    unbroken with their labels at the foot. state: 'axes' (the names, every bar still at zero), 'bars', 'top'
    (GPT-4o mini on yellow, its value right of the end of its bar and a little lower, so a magnifier around it
    stays inside the board and leaves the bar's tip uncovered), 'think' (a small slate thought-cloud before every
    thinking model's name, the key beside the first of them, and one bracket over every bar below 0.5%), 'recomputed' (an orange
    tick right after each of the eight bars we recomputed, with its key in the empty space beside the shorter bars;
    the rows sit closer and the board is shorter, so the cue fits below it)."""
    rec = state == "recomputed"
    bx_, bw_ = (F2_REC["x"], F2_REC["w"]) if rec else (F2["x"], F2["w"])
    out = [el("bd", bx_, F2["y"] + (F2_REC["oy"] if rec else 0), "", "paper", f"width:{bw_}px;height:{F2_REC['h'] if rec else F2['h']}px")]
    PANELS.add("bd")
    rows = sorted(FIG2, key=lambda r: -CHECKS["figure2"][r[0]]["paper_pct"])
    # 15 to 18: the names column a little right of the board's edge (room for the thought-clouds) and a slightly
    # smaller scale; 67 keeps the standard one
    x0, px_ = (F2X0, F2PX) if rec else (F2X0 + 40, 16)
    oy = F2_REC["oy"] if rec else 0         # 67: the board sits a little lower, clear of the stage's valance
    y0, step, bh = F2Y0 + oy, F2_REC["step"] if rec else F2STEP, F2BH
    tx_ = F2_REC["tx"] if rec else F2TX
    top, bot = y0 - 8, y0 + 16 * step - 6
    out.append(txt("bdt", tx_, 247 if rec else 278, "Figure 2", "f3 ink"))
    out.append(el("bds", tx_, 297 if rec else 332, "share of<br>pairs flagged", "f2 slate", f"line-height:{29 if rec else 31}px"))
    TEXTS.add("bds")
    for p in (5, 10):
        x = x0 + p * px_
        out.append(grid(f"f2g{p}", x, top, 5, bot - top))
        out.append(txt(f"f2y{p}", x + 12, bot - 40, f"{p}%", "f2 slate"))
    out.append(grid("f2axis", x0 - 5, top, 5, bot - top, "ink"))
    if state != "axes":
        out.append(txt("f2n", tx_, 350 if rec else 400, "16 models", "f2 slate"))
    for i, (key, lab, think) in enumerate(rows):
        d = CHECKS["figure2"][key]
        v = d["paper_pct"]
        y = y0 + i * step
        if state == "top" and key == "openai/gpt-4o-mini":
            out.append(band(f"f2hl{i}", x0 - 20 - tw(lab) - 8, y - 4, tw(lab) + 16, bh + 8))
        if state == "think" and think:              # a small thought-cloud before every thinking model's name
            out.append(el(f"f2hl{i}", x0 - 20 - tw(lab) - 38, y + (bh - 21) // 2, THINK_SVG, "", "width:30px;height:21px"))
        out.append(txt(f"f2l{i}", bx_ + 8, y - 12, lab, "f2 ink", "right", x0 - 20 - bx_ - 8))
        if state == "axes":
            continue
        out.append(hbar(f"f2b{i}", x0, y, v * px_, bh, "bp"))
        end = x0 + blen(v * px_)
        if state == "top" and i == 0:
            s_ = f"{v:.1f}%"                       # right of the bar's end, centred where the magnifier goes
            out.append(ktxt(f"f2v{i}", end + 56 - tw(s_) // 2 - 6, 55, s_, "f2 navy"))
        if state == "recomputed" and d["source"] == "recomputed":
            out.append(el(f"f2k{i}", end + 8, y + (bh - 14) // 2, tick_svg("orange", 2), "", "width:16px;height:14px"))
    if state == "recomputed":                      # the key of the ticks, beside the shorter bars, right of 10%
        kx = 480                                # on a white plate that the 10% gridline passes behind
        PLATES.add("f2kp")
        out.append(el("f2kp", kx - 8, 118, "", "", f"width:{24 + tw('recomputed') + 16}px;height:66px;background:var(--white)"))
        out.append(el("f2kk", kx, 126 + 8, tick_svg("orange", 2), "", "width:16px;height:14px"))
        out.append(el("f2kt", kx + 24, 126, "recomputed<br>exactly", "f2 ink", "line-height:29px"))
        TEXTS.add("f2kt")
    if state == "think":
        r3 = next(i for i, r in enumerate(rows) if r[2])      # the key beside the first thinking model's bar
        ky = y0 + r3 * step
        kx = x0 + 100
        PLATES.add("f2keyp")
        out.append(el("f2keyp", kx - 8, ky - 8, "", "", f"width:{38 + tw('thinking model') + 16}px;height:{bh + 16}px;background:var(--white)"))
        out.append(el("f2keyb", kx, ky + (bh - 21) // 2, THINK_SVG, "", "width:30px;height:21px"))
        out.append(txt("f2key", kx + 38, ky - 12, "thinking model", "f2 ink"))
        x = x0 + round(0.5 * px_)
        dash = "".join(f'<div class="o" style="left:0;top:{k * 16}px;width:5px;height:9px;background:var(--ink)"></div>'
                       for k in range(0, (bot - top) // 16 + 1))
        GRIDS.add("f2half")
        out.append(el("f2half", x - 2, top, dash, "", f"width:5px;height:{bot - top}px"))
        lo = [i for i, r in enumerate(rows) if CHECKS["figure2"][r[0]]["paper_pct"] < 0.5]
        ya, yb = y0 + lo[0] * step - 3, y0 + lo[-1] * step + bh + 3
        bx = x + 22
        out.append(el("f2br", bx, ya, "", "", f"width:15px;height:{yb - ya}px;box-shadow:inset -5px 0 0 0 var(--ink),"
                      f"inset 0 5px 0 0 var(--ink),inset 0 -5px 0 0 var(--ink)"))
        TEXTS.add("f2brl")
        out.append(el("f2brl", bx + 22, (ya + yb) // 2 - 31, "below<br>0.5%", "f2 ink",
                      "background:var(--white);padding:0 6px;line-height:31px"))
    return "".join(out)


# ================================================================================================ recompute
RECOMPUTED = [(k, lab) for k, lab, _ in FIG2 if CHECKS["figure2"][k]["source"] == "recomputed"]


def recompute():
    """The eight models whose raw counts were released: the paper's count, ours, a tick, on a terminal."""
    out = [board("term", "flagged pairs, released data")]
    out.append(txt("rech0", BX + 250, BY + 58, "paper", "f2 sky", "right", 90))
    out.append(txt("rech1", BX + 360, BY + 58, "ours", "f2 orange", "right", 90))
    for i, (k, lab) in enumerate(RECOMPUTED):
        d = CHECKS["figure2"][k]
        y = BY + 100 + i * 34
        out.append(txt(f"rn{i}", BX + 30, y, lab, "f2 white"))
        out.append(txt(f"recv{i}0", BX + 250, y, str(d["paper_count"]), "f2 sky", "right", 90))
        out.append(txt(f"recv{i}1", BX + 360, y, str(d["our_count"]), "f2 orange", "right", 90))
        if d["paper_count"] == d["our_count"]:
            out.append(el(f"rect{i}", BX + 470, y + 8, tick_svg("white", 4), "", "width:32px;height:28px"))
    return "".join(out)


PLOT_DIVISOR = 4892     # the plotting script's divisor, as said in the talk; checks.claims() verifies it against every bar
N_PAIRS = sum(NOISE["rate_by_kind_paper_full"]["openai/gpt-4o-mini"][k]["pairs"] for k in ("geography", "other"))


def rank(state="claim"):
    """The paper's text says the model ranking holds at every cutoff. Over the other cutoff settings (our grid on
    the released data), neighbours swap places in most (noise_models.json, rank_stability). Each tile is a tiny
    ranking of two neighbours: parallel grey lines where the order holds, crossing yellow lines where it changes;
    a legend under the quote says so. Tiles are not tied to particular settings, only counted."""
    rs = NOISE["rank_stability"]
    n = rs["settings"] - 1                 # the settings other than the default
    k = rs["settings_with_any_swap"]
    out = [board("term", "ranking of the 8 models", f"released data, {n} other cutoff settings")]
    out.append(el("rkq", BX + 30, BY + 108, '<div class="o f2 ink" style="left:20px;top:5px">paper: &quot;ranking never changes&quot;</div>',
                  "", "width:540px;height:50px;background:var(--white);box-shadow:0 0 0 5px var(--ice)"))
    TEXTS.add("rkq")
    lg = (f'<div class="o" style="left:0;top:6px">{rank_svg(False, 4)}</div>'
          f'<div class="o f2 steel" style="left:52px;top:0">same</div>'
          f'<div class="o" style="left:160px;top:6px">{rank_svg(True, 4)}</div>'
          f'<div class="o f2 yellow" style="left:212px;top:0">swap</div>')
    out.append(el("rklg", BX + 30, BY + 170, lg, "", "width:280px;height:40px"))
    TEXTS.add("rklg")
    per = (n + 1) // 2
    for i in range(n):
        r, c = divmod(i, per)
        x, y = BX + 30 + c * 56 + r * 28, BY + 222 + r * 50
        out.append(rank_tile(f"rkt{i}", x, y, state == "table" and i < k))
    if state == "table":
        out.append(txt("rkc", BX + 30, BY + 310, f'neighbours swap in <span class="yellow">{k}</span> of {n}', "f3 white"))
    return "".join(out)


# ================================================================================================ the rerun
FOUR = [("openai/gpt-4o-mini", "GPT-4o mini"), ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
        ("deepseek/deepseek-chat", "DeepSeek V3"), ("google/gemini-2.5-flash", "Gemini 2.5 Flash")]


def judge_pct():
    """Agreement of our labels with the authors' labels on their own answers, pooled over both files."""
    n = sum(v["n"] for v in JUDGE.values())
    a = sum(v["n"] * v["pipeline_vs_paper"] for v in JUDGE.values()) / n
    return round(a * 100), n


DS = "deepseek/deepseek-chat"


def cross_svg(col="steel", s=5, n=4):
    """A small pixel x, n squares across, for a tile that came out wrong."""
    c = f"#{HEX[col]}"
    r = "".join(f'<rect x="{k * s}" y="{k * s}" width="{s}" height="{s}" fill="{c}"/>'
                f'<rect x="{(n - 1 - k) * s}" y="{k * s}" width="{s}" height="{s}" fill="{c}"/>' for k in range(n))
    return f'<svg width="{n * s}" height="{n * s}" shape-rendering="crispEdges">{r}</svg>'


def swatch(id_, x, y, kind, label, w=30):
    """One legend item: a bar swatch of the given class (or raw style) and its label."""
    TEXTS.add(id_)
    st = f"width:{w}px;height:20px;" + (kind if ":" in kind else "")
    cls = "" if ":" in kind else f"bar {kind}"
    return el(id_, x, y, f'<div class="o {cls}" style="left:0;top:10px;{st}"></div>'
                         f'<div class="o f2 ink" style="left:{w + 10}px;top:0">{label}</div>', "",
              f"width:{w + 10 + tw(label)}px;height:40px")


DSB = dict(x=50, w=860, s=170)   # the DeepSeek board: wider and centred, its rows moved right by s so the lower
                                  # left corner stays empty for DeepSeek, who stands there in front of the board


def deepseek(state="two"):
    """DeepSeek V3: the paper's flags and our run's on one axis from 0; 'three' slides in, between them, the
    paper's answers relabelled by our labeller (hatched blue and orange, with a key)."""
    d = NOISE["paired"][DS]
    rows = [("paper", d["paper_run_vs_ours"]["flags"], "bp", "navy"),
            ("our labeller", d["paper_answers_our_labels_vs_ours"]["flags"], "bm", "slate"),
            ("our run", RUNS["base"][DS]["n_unf"], "bo", "orange")]
    out = [board("bench", "DeepSeek V3, flagged pairs", x=DSB["x"], w=DSB["w"])]
    if state == "cut":
        return out[0] + _ds_cut(d)
    if state == "recur":
        return out[0] + _ds_recur(d)
    if state == "three":
        out.append(swatch("dslg", DSB["x"] + 28, BY + 66, "bm", "the paper's answers, our labeller", 40))
    bx, bw, mx, bh, gp = BX + 230 + DSB["s"], 290, 20, 44, 34
    slots = (0, 1, 2) if state == "three" else (0, None, 1)
    y0 = BY + 126
    for i, (lab, v, kind, col) in enumerate(rows):
        if slots[i] is None:
            continue
        y = y0 + slots[i] * (bh + gp)
        out.append(txt(f"dsn{i}", BX + 28 + DSB["s"], y + 2, lab, "f2 ink"))
        out.append(hbar(f"dsb{i}", bx, y, bw * v / mx, bh, kind))
        out.append(txt(f"dsv{i}", bx + blen(bw * v / mx) + 14, y - 16, str(v), f"f4 {col}"))
    ay = y0 + 3 * (bh + gp) - 22
    out.append(grid("dsax", bx - 5, y0 - 12, 5, ay - y0 + 17, "ink"))
    out.append(grid("dsaxh", bx - 5, ay, bw + 10, 5, "ink"))
    for t in (0, 10, 20):
        x = bx + r5(bw * t / mx)
        out.append(txt(f"dst{t}", x - 40, ay + 4, str(t), "f2 slate", "center", 80))
    return "".join(out)


def _ds_cut(d):
    """DeepSeek V3 at two cutoffs on the template's lean (|share of YES - 0.5|, flag_pairs' bias_thr): the paper's
    answers under our labeller (hatched) and our run (orange), at the stated 0.05 and at 0.10. Most of the gap
    between the two runs is in pairs whose template lean sits just past 0.05. noise_models.json,
    paired.deepseek.grid_paper_relabelled_ours (gap 0.5)."""
    g = d["grid_paper_relabelled_ours"]
    out = [swatch("dslg", DSB["x"] + 28, BY + 66, "bm", "the paper's answers, our labeller", 40),
           swatch("dslg2", DSB["x"] + 28, BY + 106, "bo", "our run", 40)]
    bx, bw, mx, bh = BX + 255 + DSB["s"], 290, 20, 28       # room for the cutoff labels
    y0 = BY + 152
    for gi, (lab, key) in enumerate((("lean cutoff 0.05", "bias0.05_gap0.5"), ("lean cutoff 0.10", "bias0.1_gap0.5"))):
        yg = y0 + gi * 92
        out.append(txt(f"dsc{gi}", BX + 28 + DSB["s"], yg + 12, lab, "f2 ink"))
        for j, (v, kind, col) in enumerate(((g[key][1], "bm", "slate"), (g[key][2], "bo", "orange"))):
            i = 1 + j + 2 * gi                     # 1, 2: the bars of the slide before glide to the first cutoff
            y = yg + j * 36
            out.append(hbar(f"dsb{i}", bx, y, bw * v / mx, bh, kind))
            out.append(txt(f"dsv{i}", bx + blen(bw * v / mx) + 14, y + bh // 2 - 30, str(v), f"f3 {col}"))
    ay = y0 + 168
    out.append(grid("dsax", bx - 5, y0 - 12, 5, ay - y0 + 17, "ink"))
    out.append(grid("dsaxh", bx - 5, ay, bw + 10, 5, "ink"))
    for t in (0, 10, 20):
        x = bx + r5(bw * t / mx)
        out.append(txt(f"dst{t}", x - 40, ay + 4, str(t), "f2 slate", "center", 80))
    return "".join(out)


def _ds_recur(d):
    """DeepSeek V3: the paper's flags under our labeller as tiles, one per flag; the ones flagged again in our run
    lit orange, the rest grey; under them the range an unchanged model would give (expected_recurrence_ci of the
    flags, rounded to whole pairs). noise_models.json, paired.deepseek.paper_answers_our_labels_vs_ours."""
    r = d["paper_answers_our_labels_vs_ours"]
    n, k = r["flags"], r["recur"]
    lo, hi = (round(v * n) for v in d["expected_recurrence_ci"])
    x0, y0 = BX + 28 + DSB["s"], BY + 80
    out = [txt("dsr0", x0, y0, f"the paper's {n} flags, our labeller", "f2 ink")]
    tiles = ""
    for i in range(n):
        lit = i < k
        st = ("background:var(--orange);box-shadow:inset 0 5px 0 0 var(--gold),inset -5px 0 0 0 var(--rust),0 0 0 5px var(--ink)"
              if lit else "background:var(--ice);box-shadow:inset 0 0 0 5px var(--steel)")
        tiles += f'<div class="o" style="left:{i * 48}px;top:0;width:36px;height:36px;{st}"></div>'
    out.append(el("dsrt", x0, y0 + 60, tiles, "", f"width:{n * 48}px;height:36px"))
    out.append(el("dsrk", x0, y0 + 130, f'<div class="o" style="left:0;top:10px;width:20px;height:20px;background:var(--orange)"></div>'
                  f'<div class="o f2 ink" style="left:30px;top:0">{k} flagged again in our run</div>', "",
                  f"width:{30 + tw(f'{k} flagged again in our run')}px;height:40px"))
    TEXTS.add("dsrk")
    out.append(txt("dsrn", x0, y0 + 180, f"if nothing changed: {lo} to {hi} would recur", "f2 slate"))
    return "".join(out)


EX = dict(y=20, h=380)


def excess(state="with"):
    """GPT-4o mini, pairs with extra asymmetry in the paper's run (beyond the template-only 97.5% point), on the
    side of its lean ('with the lean') and against it ('against the lean'): for each, the mean extra asymmetry of
    those pairs in our run (orange bar) and below it what chance gives at most (grey bar: the 97.5% point of the
    same mean under the template-only simulation). state 'with' shows the first row, 'both' adds the second.
    noise_models.json, paired.*.one_sided_lean_recurrence: mean_in_other_run, null_975, anti_mean_in_other_run,
    anti_null_975."""
    y0 = EX["y"]
    r = NOISE["paired"]["openai/gpt-4o-mini"]["one_sided_lean_recurrence"]
    out = [board("bench", "GPT-4o mini, per pair", None, y=y0, h=EX["h"])]
    bx, bw, mx = BX + 40, 480, 0.3
    bh, rows = 26, (("with the lean", r["mean_in_other_run"], r["null_975"]),
                    ("against the lean", r["anti_mean_in_other_run"], r["anti_null_975"]))
    for g, (lab, v, nv) in enumerate(rows[:1 if state == "with" else 2]):
        yg = y0 + 64 + g * 114
        out.append(txt(f"exl{g}", bx + 10, yg, lab, "f2 ink"))
        for i, (val, kind, s_, cls, up) in enumerate(((v, "bo", f"{v:.2f}", "f4 orange", 39),
                                                       (nv, "bg", f"chance, up to {nv:.2f}", "f2 slate", 20))):
            yb = yg + 40 + i * 36
            out.append(hbar(f"exb{2 * g + i}", bx, yb, bw * val / mx, bh, kind))
            out.append(txt(f"exv{2 * g + i}", bx + blen(bw * val / mx) + 14, yb + bh // 2 - up, s_, cls))
    ay = y0 + 294
    out.append(grid("exax", bx - 5, y0 + 100, 5, ay - y0 - 95, "ink"))
    out.append(grid("exaxh", bx - 5, ay, bw + 10, 5, "ink"))
    for t in (0, 0.1, 0.2, 0.3):
        x = bx + r5(bw * t / mx)
        out.append(txt(f"ext{int(round(t * 100))}", x - 40, ay + 4, f"{t:g}", "f2 slate", "center", 80))
    out.append(txt("excap", bx, ay + 38, "same order better again, beyond the lean", "f2 slate"))
    return "".join(out)


# ================================================================================================ split by kind
KIND8 = NOISE["ranking_geography"]
LABEL = {k: lab for k, lab, _ in FIG2}
KB = dict(x=50, w=860, y=24, h=424)


def kind(state="all"):
    """Figure 2 split by kind of question on its paper board, the paper's data for the 8 models with released
    counts: names in a left column, then geography and the other questions as two columns of bars on one shared
    scale, models in the order of their geography rate. state: 'all', 'gpt' or 'rev' (QwQ and the Llamas): their
    rows on a yellow highlight with values, the other bars pale."""
    R = NOISE["rate_by_kind_paper_full"]
    hi = {"all": None, "gpt": {"openai/gpt-4o-mini"},
          "rev": {"qwen/qwq-32b", "meta-llama/Llama-3.3-70B-Instruct", "meta-llama/Llama-3.1-70B"}}[state]
    x0, y0b = KB["x"], KB["y"]
    out = [el("bd", x0, y0b, "", "paper", f"width:{KB['w']}px;height:{KB['h']}px")]
    PANELS.add("bd")
    out.append(txt("bdt", x0 + 24, y0b - 8, "Figure 2 by kind, 8 models", "f3 ink"))
    lx, gx, ox, px_ = x0 + 260, x0 + 290, x0 + 610, 11
    out.append(txt("kdgeo", gx, y0b + 50, "geography", "f3 ink"))
    out.append(txt("kdoth", ox, y0b + 50, "others", "f3 ink"))
    ys, step = y0b + 130, 30
    out.append(grid("kdaxl", gx - 5, ys - 8, 5, 8 * step, "ink"))
    out.append(grid("kdaxr", ox - 5, ys - 8, 5, 8 * step, "ink"))
    by_ = ys - 8 + 8 * step                   # a scale under each panel: 0, 10% and 20%
    for side, x_ in (("l", gx), ("r", ox)):
        out.append(grid(f"kdbx{side}", x_ - 5, by_, 20 * px_ + 10, 5, "ink"))
        for p in (0, 10, 20):
            out.append(grid(f"kdtk{side}{p}", x_ + p * px_ - 2, by_ + 5, 5, 8, "ink"))
            out.append(txt(f"kdtl{side}{p}", x_ + p * px_ - 40, by_ + 8, "0" if p == 0 else f"{p}%", "f2 slate", "center", 80))
    for i, k in enumerate(KIND8):
        y = ys + i * step
        g, o = R[k]["geography"]["rate"] * 100, R[k]["other"]["rate"] * 100
        on = hi is None or k in hi
        kind_ = "bp" if on else "bpl"
        if hi and on:
            out.append(band(f"kdhl{i}", x0 + 16, y - 4, KB["w"] - 32, 30))
        out.append(txt(f"kdn{i}", x0 + 20, y - 10, LABEL[k], "f2 ink", "right", lx - x0 - 20))
        wg, wo = blen(g * px_), blen(o * px_)
        if wg:
            out.append(el(f"kdg{i}", gx, y, "", f"bar {kind_}", f"width:{wg}px;height:22px"))
        if wo:
            out.append(el(f"kdo{i}", ox, y, "", f"bar {kind_}", f"width:{wo}px;height:22px"))
        if hi is not None and k in hi:
            out.append(txt(f"kdvg{i}", gx + wg + 10, y - 10, f"{g:.1f}%", "f2 navy"))
            out.append(txt(f"kdvo{i}", ox + wo + 10, y - 10, f"{o:.1f}%", "f2 navy"))
    return "".join(out)


# ================================================================================================ fact cards
FACT4 = [("openai/gpt-4o-mini", "GPT-4o mini"), ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
         ("deepseek/deepseek-chat", "DeepSeek V3"), ("openai/gpt-5.6-luna", "GPT-5.6 Luna")]


def nongeo_total():
    """(flags on non-geography questions without the card, with it) summed over the four fact-card models."""
    return (sum(RUNS["by_kind"][k]["other"]["base"] for k, _ in FACT4),
            sum(RUNS["by_kind"][k]["other"]["factcard"] for k, _ in FACT4))


RC = dict(y=36, h=380)


def recall(state="known"):
    """Llama 3.3, pairs outside geography, each value asked on its own: of ten pairs, how many it puts in the right
    order. Its flagged pairs: the spoken 'about seven in ten' as ten tiles, seven orange (right order) and three
    crossed (wrong order); 'other' adds its other pairs (eight and a half in ten); 'guess' lights the line where
    guessing lands (five in ten), which stands faint from the start. The figures are checked against
    results/recall_probe.json in checks.claims()."""
    y0 = RC["y"]
    out = [board("bench", "Llama 3.3 70B", "each value asked alone", y=y0, h=RC["h"])]
    wrong = "background:var(--white);box-shadow:inset 0 0 0 5px var(--steel);"
    out.append(swatch("rclg0", BX + 28, y0 + 100, "bo", "right order"))
    out.append(swatch("rclg1", BX + 28 + 40 + tw("right order") + 40, y0 + 100, wrong, "wrong order"))

    def row(id_, y, lit):
        t = ""
        for i in range(10):
            f = min(1.0, max(0.0, lit - i))
            t += f'<div class="o" style="left:{i * 40}px;top:0;width:34px;height:34px;{wrong}"></div>'
            if f == 0:
                t += f'<div class="o" style="left:{i * 40 + 7}px;top:7px">{cross_svg("steel", 5, 4)}</div>'
            else:                          # a whole cell, or a split one: its left part orange, the rest an empty outline
                t += (f'<div class="o" style="left:{i * 40}px;top:0;width:{34 if f == 1 else round(34 * f)}px;height:34px;'
                      f'background:var(--orange);box-shadow:inset 0 5px 0 0 var(--gold),inset -5px 0 0 0 var(--rust)"></div>')
        return el(id_, BX + 30, y, t, "", "width:394px;height:34px")

    out.append(txt("rcl0", BX + 30, y0 + 150, "flagged pairs: right order", "f2 ink"))
    out.append(row("rcp0", y0 + 192, 7))
    out.append(txt("rcn0", BX + 440, y0 + 178, "7 in 10", "f3 orange"))
    if state in ("other", "guess"):
        out.append(txt("rcl1", BX + 30, y0 + 240, "other pairs: right order", "f2 ink"))
        out.append(row("rcp1", y0 + 282, 8.5))
        out.append(txt("rcn1", BX + 440, y0 + 268, "8.5 in 10", "f3 orange"))
    on = state == "guess"
    gx = BX + 30 + 5 * 40 - 5
    # the dashed line runs only across the rows of cells (rows at +192 and +282, 34 high), not through their labels
    dash = "".join(f'<div class="o" style="left:0;top:{r0 + q * 16}px;width:5px;height:9px;background:var(--{"ink" if on else "steel"})"></div>'
                   for r0 in (6, 96) for q in range(3))
    GRIDS.add("rcg")
    out.append(el("rcg", gx, y0 + 186, dash, "", "width:5px;height:137px"))
    if on:
        out.append(band("rcglb", gx - 4 - tw("guessing: 5 in 10") // 2 - 8, y0 + 345, tw("guessing: 5 in 10") + 16, 30))
    out.append(txt("rcgl", gx - 4 - tw("guessing: 5 in 10") // 2, y0 + 340, "guessing: 5 in 10", "f2 " + ("ink" if on else "slate")))
    return "".join(out)


# ================================================================================================ geography
def dist():
    """GPT-4o mini on geography, the paper's run: the share of pairs flagged in each quarter of the distance
    between the two places on the asked axis. Paper data, so the paper board and blue bars. The farthest bar keeps
    its value inside its top, so the robot can stand on it."""
    q = GEO["distances"]["paper | openai/gpt-4o-mini"]["flag_rate_by_asked_quartile"]
    out = [board("paper", "GPT-4o mini, geography", "share flagged, by distance")]
    out.append(legend("dilg", BX + 28, BY + 110, [("bp", "paper's run")], "f2 ink"))
    base, px_ = BY + 300, 3.6
    out.append(grid("diax", BX + 30, base, 540, 5, "ink"))
    labs = ("closest<br>quarter", "", "", "farthest<br>quarter")
    for i, v in enumerate(q):
        x = BX + 60 + i * 130
        h = blen(v * 100 * px_)
        out.append(bar(f"dib{i}", x, base, 90, v * 100 * px_, "bp"))
        out.append(txt(f"div{i}", x - 55, base - h - 45, f"{v * 100:.0f}%", "f2 navy", "center", 200))
        if labs[i]:
            out.append(el(f"dil{i}", x - 55, base + 10, labs[i], "f2 ink", "width:200px;text-align:center;line-height:31px"))
            TEXTS.add(f"dil{i}")
    out.append(el("diarr", BX + 245, base + 25, arrow_svg("slate", 5, 16), "", "width:80px;height:30px"))
    return "".join(out)


ABLATION_PCT = 9    # the paper's same-latitude ablation for GPT-4o mini (9.06%), as said in the talk; checked in checks.claims()


def ablation():
    """The paper's own test on places at the same latitude (only one reading of 'west' works): GPT-4o mini is
    still flagged on 9% of pairs. Paper data: the paper board, a blue number. The map is placed by the story."""
    out = [board("paper", "the paper's own test", "places at the same latitude")]
    out.append(txt("abn", BX + 330, BY + 120, f"{ABLATION_PCT}%", "f6 navy"))
    out.append(txt("abl", BX + 330, BY + 250, "GPT-4o mini<br>still flagged", "f2 ink"))
    return "".join(out)


# ================================================================================================ the slides
def slides():
    return {
        "fig2_axes": fig2("axes"), "fig2_bars": fig2("bars"), "fig2_top": fig2("top"), "fig2_think": fig2("think"),
        "fig2_rec": fig2("recomputed"),
        "rec_table": recompute(), "rank_claim": rank("claim"), "rank_table": rank("table"),
        "ds_two": deepseek("two"), "ds_three": deepseek("three"), "ds_cut": deepseek("cut"), "ds_recur": deepseek("recur"), "excess": excess("with"), "excess_both": excess("both"),
        "kind_all": kind("all"), "kind_gpt": kind("gpt"), "kind_rev": kind("rev"),
        "recall": recall("known"), "recall_other": recall("other"), "recall_guess": recall("guess"), "dist": dist(),
        "ablation": ablation(),
    }


# Which board each chart stands on, and its native extent (x0, width, bottom y): the stand reaches the ground.
# The paper board holds the paper's figures and data; the monitor, the released data recomputed; the lab bench,
# our own runs.
STYLE = {"fig2": "paper", "rec_": "term", "rank": "term", "ds": "bench", "excess": "bench", "kind": "paper",
         "recall": "bench", "dist": "paper", "ablation": "paper"}


def stand_of(slide):
    style = next(v for k, v in STYLE.items() if slide.startswith(k))
    if slide.startswith("fig2"):
        rec = slide == "fig2_rec"
        x, w = (F2_REC["x"], F2_REC["w"]) if rec else (F2["x"], F2["w"])
        y, h = F2["y"] + (F2_REC["oy"] if rec else 0), F2_REC["h"] if rec else F2["h"]
    elif slide.startswith("kind"):
        x, w, y, h = KB["x"], KB["w"], KB["y"], KB["h"]
    elif slide.startswith("recall"):
        x, w, y, h = BX, BW, RC["y"], RC["h"]
    elif slide.startswith("ds"):
        x, w, y, h = DSB["x"], DSB["w"], BY, BH
    elif slide.startswith("excess"):
        x, w, y, h = BX, BW, EX["y"], EX["h"]
    else:
        x, w, y, h = BX, BW, BY, BH
    return style, x * SCALE, w * SCALE, (y + h) * SCALE


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
