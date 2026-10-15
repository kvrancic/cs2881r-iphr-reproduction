"""The charts and number panels, authored in HTML/CSS on the finer 960x540 grid (2.5 x the 384x216 art grid),
rendered by headless Chromium, snapped to Endesga 32 with no anti-aliasing, and cut into one picture per element
(every element with a data-id), so bars can grow and panels can glide by Morph.

Every figure on screen is read here from the result files and nowhere else:
  results/paper_data_checks.json, results/runs.json, results/noise_models.json, results/geo_analysis.json,
  data/judge_validation/summary.json.
Semantic colours: the paper's run blue, our run orange, fact cards aqua, highlight yellow, unknown grey.

Each act has its own board: Figure 2 and its split by kind are printed paper on legs; the recompute is a
terminal on a monitor stand; the rerun and the fact cards stand on a lab bench; geography is a sea chart on a
map table. A standard board is 600 grid px wide (62% of the frame) with the big robot standing beside it."""
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
.term { background: var(--night); box-shadow: inset 0 0 0 5px var(--dusk), 0 0 0 5px var(--ink), 10px 10px 0 5px var(--ice); }
.bench { background: var(--night);
  box-shadow: inset 0 0 0 5px var(--dusk), inset 0 5px 0 5px var(--slate), 0 0 0 5px var(--ink), 10px 10px 0 5px var(--ice); }
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
LIGHT = {"paper", "map"}


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


def bulb_svg(s=3):
    """A small light bulb (a thinking model): yellow glass, white glint, ink outline and a steel base."""
    rows = [".KKK.", "KYWYK", "KWYYK", "KYYYK", ".KYK.", ".KIK.", "..K.."]
    return _rows_svg(rows, {"K": "ink", "Y": "yellow", "W": "white", "I": "steel"}, s)


def tick_svg(col="green", s=5):
    """A pixel check mark made of s x s squares."""
    pts = [(0, 3), (1, 4), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)]
    c = f"#{HEX[col]}"
    r = "".join(f'<rect x="{x * s}" y="{y * s}" width="{s}" height="{2 * s}" fill="{c}"/>' for x, y in pts)
    return f'<svg width="{8 * s}" height="{7 * s}" shape-rendering="crispEdges">{r}</svg>'


def bump_svg(swap, s=5):
    """A tiny bump chart of two neighbouring models over two cutoffs: each model a line from its rank at the
    default cutoff (left dot) to its rank at another cutoff (right dot). Parallel steel lines when the order holds;
    yellow lines that cross when the two swap places."""
    w, h = 14, 8
    up = [1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 6]
    if swap:
        a = [(x + 1, y) for x, y in enumerate(up)]
        b = [(x + 1, 7 - y) for x, y in enumerate(up)]
        col = "yellow"
    else:
        a = [(x + 1, 1) for x in range(12)]
        b = [(x + 1, 6) for x in range(12)]
        col = "steel"
    pts = a + b
    r = "".join(f'<rect x="{x * s}" y="{y * s}" width="{s}" height="{s}" fill="#{HEX[col]}"/>' for x, y in pts)
    for (x, y) in (a[0], b[0], a[-1], b[-1]):
        r += f'<rect x="{(x - 1) * s}" y="{(y - 1) * s + s // 2}" width="{2 * s}" height="{2 * s}" fill="#{HEX["white"]}"/>'
    return f'<svg width="{w * s}" height="{h * s}" shape-rendering="crispEdges">{r}</svg>'


def legend(id_, x, y, items, cls="f2 ink"):
    """items = [(swatch class or raw html, label)]: small swatches with labels on one row."""
    inner, cx = "", 0
    for k, lab in items:
        sw = (f'<div class="o bar {k}" style="left:{cx}px;top:10px;width:20px;height:20px"></div>' if not k.startswith("<")
              else f'<div class="o" style="left:{cx}px;top:0px">{k}</div>')
        inner += sw + f'<div class="o {cls}" style="left:{cx + 30}px;top:0px">{lab}</div>'
        cx += 30 + 13 * len(lab) + 30
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
F2 = dict(x=30, y=14, w=900, h=428)          # the full-width paper board: native 12..372 x 6..174, legs to the ground
F2X0, F2PX, F2Y0, F2STEP, F2BH = 340, 33, 58, 24, 18


def fig2(state):
    """Figure 2 redrawn as horizontal bars, models sorted by their share, names upright on the left, on a paper
    board across the frame; the robot stands in front of its empty lower right. state: 'axes' (title and axes),
    'bars' (names and bars), 'top' (GPT-4o mini highlighted, values on the top three bars), 'think' (a bulb on each
    thinking model's name and one bracket over every bar below 0.5%), 'recomputed' (an orange tick on each of
    the eight bars we recomputed)."""
    out = [el("bd", F2["x"], F2["y"], "", "paper", f"width:{F2['w']}px;height:{F2['h']}px")]
    PANELS.add("bd")
    rows = sorted(FIG2, key=lambda r: -CHECKS["figure2"][r[0]]["paper_pct"])
    x0, px_, y0, step, bh = F2X0, F2PX, F2Y0, F2STEP, F2BH
    top, bot = y0 - 6, y0 + 16 * step - 3
    for p in (5, 10):
        x = x0 + p * px_
        out.append(grid(f"f2g{p}", x, top, 5, bot - top))
        out.append(txt(f"f2y{p}", x - 50, F2["y"] + 2, f"{p}%", "f2 slate", "center", 105))
    out.append(grid("f2axis", x0 - 5, top, 5, bot - top, "ink"))
    # the title plate, in the empty middle of the board
    PLATES.add("f2tp")
    out.append(el("f2tp", 440, 190, "", "", "width:308px;height:" + ("128" if state != "axes" else "92") + "px;background:var(--white)"))
    out.append(txt("bdt", 452, 186, "Figure 2", "f3 ink"))
    out.append(txt("bds", 452, 240, "share of pairs flagged", "f2 slate"))
    if state != "axes":
        out.append(txt("f2n", 452, 274, "16 models", "f2 slate"))
    if state == "axes":
        return "".join(out)
    for i, (key, lab, think) in enumerate(rows):
        d = CHECKS["figure2"][key]
        v = d["paper_pct"]
        y = y0 + i * step
        name = (bulb_svg() + "&nbsp;" if state == "think" and think else "") + lab
        if state == "top" and key == "openai/gpt-4o-mini":
            out.append(band(f"f2hl{i}", 322 - tw(lab) - 8, y - 3, tw(lab) + 16, bh + 6))
        out.append(txt(f"f2l{i}", 60, y - 11, name, "f2 ink", "right", 262))
        out.append(hbar(f"f2b{i}", x0, y, v * px_, bh, "bp"))
        end = x0 + blen(v * px_)
        if state in ("top", "think") and i < 3:
            out.append(txt(f"f2v{i}", end + 12, y - (21 if i == 0 else 11), f"{v:.2f}%", "f3 navy" if i == 0 else "f2 slate"))
        if state == "recomputed" and d["source"] == "recomputed":
            out.append(el(f"f2k{i}", end + 10, y - 3, tick_svg("orange", 3), "", "width:24px;height:21px"))
    if state == "think":
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
        out.append(txt("f2brl", bx + 28, (ya + yb) // 2 - 20, bulb_svg() + "&nbsp;below 0.5%", "f2 ink"))
    return "".join(out)


# ================================================================================================ recompute
RECOMPUTED = [(k, lab) for k, lab, _ in FIG2 if CHECKS["figure2"][k]["source"] == "recomputed"]


def recompute(state="table"):
    """The eight models whose raw counts were released: the paper's count, ours, a tick, on a terminal. On 'two'
    the numbers leave and the ticks move next to the names; the three discrepancies fill the right column."""
    two = state == "two"
    out = [board("term", "flagged pairs, released data")]
    if not two:
        out.append(txt("rech0", BX + 250, BY + 58, "paper", "f2 sky", "right", 90))
        out.append(txt("rech1", BX + 360, BY + 58, "ours", "f2 orange", "right", 90))
    for i, (k, lab) in enumerate(RECOMPUTED):
        d = CHECKS["figure2"][k]
        y = BY + 100 + i * 34
        out.append(txt(f"rn{i}", BX + 30, y, lab, "f2 " + ("steel" if two else "white")))
        if not two:
            out.append(txt(f"recv{i}0", BX + 250, y, str(d["paper_count"]), "f2 sky", "right", 90))
            out.append(txt(f"recv{i}1", BX + 360, y, str(d["our_count"]), "f2 orange", "right", 90))
        if d["paper_count"] == d["our_count"]:
            out.append(el(f"rect{i}", BX + (238 if two else 470), y + 8, tick_svg("white" if not two else "steel", 4), "", "width:32px;height:28px"))
    if two:
        out.append(txt("rdh", BX + 310, BY + 70, "three small<br>discrepancies:", "f2 white"))
        for k, lab in enumerate(("the plot", "the retest", "the ranking")):
            out.append(txt(f"rd{k}", BX + 310, BY + 170 + k * 50,
                           f'<span style="background:var(--yellow);color:var(--ink);padding:0 9px">{k + 1}</span>&nbsp;{lab}', "f2 white"))
    return "".join(out)


PLOT_DIVISOR = 4892     # the plotting script's divisor, as said in the talk; checks.claims() verifies it against every bar
N_PAIRS = sum(NOISE["rate_by_kind_paper_full"]["openai/gpt-4o-mini"][k]["pairs"] for k in ("geography", "other"))


def divisor():
    """The plotting script's divisor against the number of pairs in the released data."""
    out = [board("term", "Figure 2: the divisor")]
    for k, (lab, den, col) in enumerate((("the plot divides by", PLOT_DIVISOR, "sky"), ("pairs in the data", N_PAIRS, "white"))):
        x = BX + 40 + k * 280
        out.append(txt(f"divl{k}", x, BY + 110, lab, "f2 steel"))
        out.append(txt(f"divf{k}", x, BY + 160, f"{den:,}", f"f6 {col}"))
    return "".join(out)


def retest():
    """The paper's retest: a flag survives if the accuracy gap stays above the cutoff; stated 0.5, used 0.4.
    The ruler is zoomed to 0.3..0.6; the paper's code (used) is an outlined marker, the text (stated) a solid one."""
    out = [board("term", "retest cutoff")]
    x0, w, lo, hi = BX + 60, 480, 0.3, 0.6
    X = lambda v: x0 + r5(w * (v - lo) / (hi - lo))
    y = BY + 300
    out.append(grid("rtr", x0, y, w, 10))
    for k in range(7):
        v = lo + k * 0.05
        major = k % 2 == 0
        out.append(grid(f"rtt{k}", X(v) - (5 if k == 6 else 0), y + 10, 5, 20 if major else 10))
        if major:
            out.append(txt(f"rtn{k}", X(v) - 40, y + 30, f"{v:.1f}", "f2 steel", "center", 80))
    xs, xu = X(0.5), X(0.4)
    out.append(el("rtm5", xs - 10, y - 180, "", "", "width:20px;height:180px;background:var(--sky);box-shadow:inset 5px 0 0 0 var(--cyan)"))
    out.append(el("rtm4", xu - 10, y - 130, "", "", "width:20px;height:130px;box-shadow:inset 0 0 0 5px var(--sky)"))
    out.append(txt("rtl5", xs - 110, y - 245, "stated 0.5", "f3 sky", "center", 220))
    out.append(txt("rtl4", xu - 110, y - 195, "used 0.4", "f3 white", "center", 220))
    return "".join(out)


def rank(state="claim"):
    """The paper's text says the model ranking holds at every cutoff. Over the 11 cutoff settings other than the
    default (our grid on the released data), neighbours swap places in 8 (noise_models.json, rank_stability).
    Each tile is a tiny two-neighbour ranking: parallel lines where the order holds, crossing yellow lines where it
    changes. Tiles are not tied to particular settings, only counted."""
    rs = NOISE["rank_stability"]
    n = rs["settings"] - 1                 # the settings other than the default
    k = rs["settings_with_any_swap"]
    out = [board("term", "ranking of the 8 models", f"released data, {n} other cutoff settings")]
    out.append(el("rkq", BX + 30, BY + 112, '<div class="o f2 ink" style="left:20px;top:5px">paper: &quot;ranking never changes&quot;</div>',
                  "", "width:540px;height:50px;background:var(--white);box-shadow:0 0 0 5px var(--ice)"))
    TEXTS.add("rkq")
    for i in range(n):
        r, c = divmod(i, 6)
        x, y = BX + 30 + c * 92 + r * 46, BY + 190 + r * 62
        swap = state == "table" and i < k
        out.append(el(f"rkt{i}", x, y, f'<div class="o" style="left:5px;top:5px">{bump_svg(swap, 5)}</div>', "",
                      f"width:80px;height:50px;background:var(--dusk);box-shadow:0 0 0 5px var(--{'yellow' if swap else 'slate'})"))
    if state == "table":
        out.append(txt("rkc", BX + 30, BY + 318, f'neighbours swap in <span class="yellow">{k}</span> of {n}', "f3 white"))
    return "".join(out)


# ================================================================================================ the rerun
FOUR = [("openai/gpt-4o-mini", "GPT-4o mini"), ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
        ("deepseek/deepseek-chat", "DeepSeek V3"), ("google/gemini-2.5-flash", "Gemini 2.5 Flash")]


def judge_pct():
    """Agreement of our labels with the authors' labels on their own answers, pooled over both files."""
    n = sum(v["n"] for v in JUDGE.values())
    a = sum(v["n"] * v["pipeline_vs_paper"] for v in JUDGE.values()) / n
    return round(a * 100), n


def paired(title, rows, unit_max, fmt=None, sub=None, axis=None, pid="pr"):
    """Blue (paper's run) and orange (ours) bars per model on the bench board; rows = [(label, paper, ours)].
    Row names share their ids (rn0..) across the scene, so they stay while the bars change."""
    out = [board("bench", title, sub)]
    out.append(legend(pid + "lg", BX + 385, BY + 22, [("bp", "paper"), ("bo", "ours")], "f2 white"))
    bx, bw = BX + 230, 300
    y0, step = BY + 112, 54 if len(rows) > 2 else 80
    for i, (lab, a, b) in enumerate(rows):
        y = y0 + i * step
        out.append(txt(f"rn{i}", BX + 28, y + 5, lab, "f2 white"))
        for k, (v, kind, col) in enumerate(((a, "bp", "sky"), (b, "bo", "orange"))):
            yy = y + k * 24
            out.append(hbar(f"{pid}b{i}{k}", bx, yy + 3, bw * v / unit_max, 20, kind))
            if fmt:
                out.append(txt(f"{pid}v{i}{k}", bx + blen(bw * v / unit_max) + 12, yy - 7, fmt(v), f"f2 {col}"))
    if axis:
        ay = y0 + len(rows) * step - 6
        out.append(grid(pid + "ax", bx, ay, bw, 5, "steel"))
        for t in axis:
            x = bx + r5(bw * t / unit_max)
            out.append(grid(f"{pid}tk{int(t * 100)}", x - (5 if t == unit_max else 0), ay + 5, 5, 10, "steel"))
            out.append(txt(f"{pid}tl{int(t * 100)}", x - 40, ay + 12, f"{t:g}", "f2 steel", "center", 80))
    return "".join(out)


def lean_size():
    rows = [(lab, NOISE["paired"][k]["lean_gap"]["paper"], NOISE["paired"][k]["lean_gap"]["ours"]) for k, lab in FOUR]
    return paired("size of the lean", rows, 0.2, sub="accuracy gap, lean side vs reverse", axis=(0, 0.1, 0.2), pid="ls")


def flag_count():
    """GPT-4o mini and Llama only: the two models the sentence names."""
    rows = [(lab, RUNS["paper_same_pairs"][k]["n_unf"], RUNS["base"][k]["n_unf"]) for k, lab in FOUR[:2]]
    return paired("flagged pairs", rows, 160, fmt=str, sub="same 1,014 pairs", pid="nf")


DS = "deepseek/deepseek-chat"


def deepseek(state="two"):
    """DeepSeek V3: the paper's flags, the paper's answers relabelled by our labeller, our run's flags."""
    d = NOISE["paired"][DS]
    rows = [("paper", d["paper_run_vs_ours"]["flags"], "bp", "sky"),
            ("paper's answers,<br>our labeller", d["paper_answers_our_labels_vs_ours"]["flags"], "bm", "white"),
            ("our run", RUNS["base"][DS]["n_unf"], "bo", "orange")]
    out = [board("bench", "DeepSeek V3, flagged pairs")]
    bx, bw, mx = BX + 270, 220, 20
    for i, (lab, v, kind, col) in enumerate(rows):
        if state == "two" and i == 1:
            continue
        y = BY + 90 + i * 90
        out.append(txt(f"dsn{i}", BX + 28, y + (2 if i == 1 else 20), lab, "f2 white"))
        out.append(hbar(f"dsb{i}", bx, y + 20, bw * v / mx, 45, kind))
        out.append(txt(f"dsv{i}", bx + blen(bw * v / mx) + 15, y + 2, str(v), f"f4 {col}"))
    return "".join(out)


TICK_NOISE = '<div style="width:10px;height:30px;background:var(--white);box-shadow:inset -5px 0 0 0 var(--steel)"></div>'


def excess(state="gpt"):
    """Pairs with extra asymmetry on the lean side in the paper's run (above the template-only 97.5% point): how
    much of it returns in our run (orange bar), against the high end of what noise alone gives (a white tick on
    the same row: the 97.5% point of the simulation). noise_models.json, paired.*.one_sided_lean_recurrence, the
    statistic of the report's 'lean-side excess'. state 'gpt': GPT-4o mini lit, the other bars dithered; 'all'."""
    out = [board("bench", "beyond the general lean", "same order better again in ours?")]
    out.append(legend("exlg", BX + 28, BY + 100, [("bo", "ours"), (TICK_NOISE, "noise, high end")], "f2 white"))
    bx, bw, mx = BX + 250, 300, 0.2
    for i, (k, lab) in enumerate(FOUR):
        r = NOISE["paired"][k]["one_sided_lean_recurrence"]
        on = state == "all" or i == 0
        y = BY + 160 + i * 46
        out.append(txt(f"rn{i}", BX + 28, y - 4, lab, "f2 " + ("white" if on else "steel")))
        out.append(hbar(f"exb{i}", bx, y + 3, bw * r["mean_in_other_run"] / mx, 24, "bo" if on else "bod"))
        out.append(el(f"exg{i}", bx + r5(bw * r["null_975"] / mx) - 5, y - 3, TICK_NOISE, "", "width:10px;height:36px"))
        if on:
            out.append(txt(f"exv{i}", bx + blen(bw * r["mean_in_other_run"] / mx) + 14, y - 4,
                           f"{r['mean_in_other_run']:.2f}", "f2 orange"))
    ay = BY + 345
    out.append(grid("exax", bx, ay - 8, bw, 5, "steel"))
    for t in (0, 0.1, 0.2):
        x = bx + r5(bw * t / mx)
        out.append(txt(f"ext{int(t * 100)}", x - 40, ay - 6, f"{t:g}", "f2 steel", "center", 80))
    return "".join(out)


# ================================================================================================ split by kind
KIND8 = NOISE["ranking_geography"]
LABEL = {k: lab for k, lab, _ in FIG2}
KB = dict(x=60, w=640)


def kind(state="all"):
    """Figure 2 split by kind of question on its paper board, the paper's data for the 8 models with released
    counts: geography to the left, the other questions to the right, models in the order of their geography rate.
    state: 'all', 'gpt' or 'rev' (QwQ and the Llamas): their names on a yellow highlight, values on their bars, the
    other bars pale."""
    R = NOISE["rate_by_kind_paper_full"]
    hi = {"all": None, "gpt": {"openai/gpt-4o-mini"},
          "rev": {"qwen/qwq-32b", "meta-llama/Llama-3.3-70B-Instruct", "meta-llama/Llama-3.1-70B"}}[state]
    x0 = KB["x"]
    out = [board("paper", "Figure 2 by kind, 8 models", x=x0, w=KB["w"])]
    lx, rx, px_ = x0 + 225, x0 + 475, 6
    out.append(txt("kdgeo", x0 + 20, BY + 62, "geography", "f3 ink", "right", lx - x0 - 30))
    out.append(txt("kdoth", rx + 10, BY + 62, "others", "f3 ink"))
    y0, step = BY + 135, 30
    out.append(grid("kdaxl", lx, y0 - 8, 5, 8 * step, "ink"))
    out.append(grid("kdaxr", rx - 5, y0 - 8, 5, 8 * step, "ink"))
    for i, k in enumerate(KIND8):
        y = y0 + i * step
        g, o = R[k]["geography"]["rate"] * 100, R[k]["other"]["rate"] * 100
        on = hi is None or k in hi
        kind_ = "bp" if on else "bpl"
        if hi and on:
            cxm = (lx + rx) // 2
            out.append(band(f"kdhl{i}", cxm - tw(LABEL[k]) // 2 - 8, y - 2, tw(LABEL[k]) + 16, 24))
        out.append(txt(f"kdn{i}", lx + 15, y - 11, LABEL[k], "f2 ink", "center", rx - lx - 30))
        wg, wo = blen(g * px_), blen(o * px_)
        out.append(el(f"kdg{i}", lx - wg, y, "", f"bar {kind_}", f"width:{wg}px;height:20px"))
        out.append(el(f"kdo{i}", rx, y, "", f"bar {kind_}", f"width:{wo}px;height:20px"))
        if hi is not None and k in hi:
            out.append(txt(f"kdvg{i}", lx - wg - 95, y - 11, f"{g:.1f}%", "f2 navy", "right", 85))
            out.append(txt(f"kdvo{i}", rx + wo + 10, y - 11, f"{o:.1f}%", "f2 navy"))
    return "".join(out)


# ================================================================================================ fact cards
FACT4 = [("openai/gpt-4o-mini", "GPT-4o mini"), ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
         ("deepseek/deepseek-chat", "DeepSeek V3"), ("openai/gpt-5.6-luna", "newer model")]


def facts(state="after"):
    """Flagged pairs on the questions that are not about geography, without and with the fact card: the total
    across the four models is the subject; the rows are small. A value of 0 is a 1-pixel aqua stub."""
    out = [board("bench", "flags outside geography")]
    items = [("bo", "no values")] + ([("ba", "values in the prompt")] if state == "after" else [])
    out.append(legend("fclg", BX + 28, BY + 62, items, "f2 ice"))
    bx, bw, mx = BX + 230, 260, 35
    tot = [0, 0]
    for i, (k, lab) in enumerate(FACT4):
        a, b = RUNS["by_kind"][k]["other"]["base"], RUNS["by_kind"][k]["other"]["factcard"]
        tot[0] += a; tot[1] += b
        y = BY + 112 + i * 40
        out.append(txt(f"fcn{i}", BX + 28, y - 4, lab, "f2 steel"))
        out.append(hbar(f"fcb{i}0", bx, y + 2, bw * a / mx, 14, "bo"))
        out.append(txt(f"fcv{i}0", bx + blen(bw * a / mx) + 10, y - 10, str(a), "f2 steel"))
        if state == "after":
            w = blen(bw * b / mx) or 3
            out.append(el(f"fcb{i}1", bx, y + 18, "", "bar ba", f"width:{w}px;height:12px"))
    out.append(txt("fctl", BX + 28, BY + 290, "4 models", "f3 white"))
    out.append(txt("fct0", BX + 230, BY + 272, str(tot[0]), "f5 orange"))
    if state == "after":
        out.append(el("fcarr", BX + 335, BY + 305, arrow_svg("steel", 5, 12), "", "width:60px;height:30px"))
        out.append(txt("fct1", BX + 420, BY + 272, str(tot[1]), "f5 cyan"))
    return "".join(out)


def nongeo_total():
    """(flags on non-geography questions without the card, with it) summed over the four fact-card models."""
    return (sum(RUNS["by_kind"][k]["other"]["base"] for k, _ in FACT4),
            sum(RUNS["by_kind"][k]["other"]["factcard"] for k, _ in FACT4))


def recall(state="known"):
    """Llama 3.3's flagged pairs outside geography, each value asked on its own: the spoken 'about seven in ten'
    ordered correctly as ten pips, seven lit; 'guess' adds the line where guessing lands (five in ten).
    The figure itself is checked against results/recall_probe.json in checks.claims()."""
    out = [board("bench", "Llama 3.3 70B, flagged pairs", "outside geography, each value asked alone")]
    pips = ""
    for i in range(10):
        col, hi = ("orange", "gold") if i < 7 else ("dusk", "slate")
        pips += (f'<div class="o" style="left:{i * 50}px;top:0;width:40px;height:40px;background:var(--{col});'
                 f'box-shadow:inset 0 5px 0 0 var(--{hi})"></div>')
    out.append(el("rcpips", BX + 50, BY + 140, pips, "", "width:490px;height:40px"))
    out.append(txt("rcn", BX + 50, BY + 205, "about 7 in 10", "f4 orange"))
    out.append(txt("rcl", BX + 50, BY + 280, "in the right order", "f2 white"))
    if state == "guess":
        dash = "".join(f'<div class="o" style="left:0;top:{q * 16}px;width:5px;height:9px;background:var(--ice)"></div>' for q in range(6))
        out.append(el("rcg", BX + 50 + 5 * 50 - 7, BY + 115, dash, "", "width:5px;height:90px"))
        out.append(txt("rcgl", BX + 330, BY + 280, "guessing: 5 in 10", "f2 ice"))
    return "".join(out)


# ================================================================================================ geography
def dist():
    """GPT-4o mini on geography, the paper's data: the share of pairs flagged in each quarter of the distance
    between the two places on the asked axis. On the sea-chart board."""
    q = GEO["distances"]["paper | openai/gpt-4o-mini"]["flag_rate_by_asked_quartile"]
    out = [board("map", "GPT-4o mini, geography", "share flagged, by distance apart")]
    base, px_ = BY + 300, 3.6
    out.append(grid("diax", BX + 30, base, 540, 5, "ink"))
    labs = ("closest<br>quarter", "", "", "farthest<br>quarter")
    for i, v in enumerate(q):
        x = BX + 60 + i * 130
        out.append(bar(f"dib{i}", x, base, 90, v * 100 * px_, "bp"))
        out.append(txt(f"div{i}", x - 55, base - blen(v * 100 * px_) - 45, f"{v * 100:.0f}%", "f2 navy", "center", 200))
        if labs[i]:
            out.append(el(f"dil{i}", x - 55, base + 10, labs[i], "f2 ink", "width:200px;text-align:center;line-height:31px"))
            TEXTS.add(f"dil{i}")
    out.append(el("diarr", BX + 245, base + 25, arrow_svg("slate", 5, 16), "", "width:80px;height:30px"))
    return "".join(out)


LADDER = [("base", "paper's<br>wording"), ("paraphrase", "reworded,<br>same vague"),
          ("clarified", "+ further<br>west"), ("strict", "+ only<br>due west")]


def ladder(n=2):
    """GPT-4o mini's flags on geography for four wordings, each its own condition (not stacked); exact bar heights.
    The paper's wording is grey context with its number in grey (the baseline); the others are our runs, in
    orange, each with its own value above its bar. The clarified wording's label is highlighted yellow."""
    G = GEO["conditions"]
    N = G["base"]["pairs"]
    out = [board("map", "GPT-4o mini, geography flags")]
    base, px_ = BY + 235, 120 / N
    out.append(grid("ldax", BX + 30, base, 540, 5, "ink"))
    for i, (c, lab) in enumerate(LADDER):
        if i >= n:
            continue
        x = BX + 50 + i * 140
        v = G[c]["flags"]
        st = "width:180px;text-align:center;line-height:31px"
        if c == "clarified":
            for j, line in enumerate(lab.split("<br>")):
                out.append(band(f"ldhl{j}", x + 45 - tw(line) // 2 - 6, base + 10 + j * 31 + 6, tw(line) + 12, 24))
        out.append(el(f"ldl{i}", x - 45, base + 10, lab, "f2 " + ("slate" if c == "base" else "ink"), st))
        TEXTS.add(f"ldl{i}")
        out.append(bar(f"ldb{i}", x, base, 90, v * px_, "bg" if c == "base" else "bo", exact=True))
        h = max(3, round(v * px_))
        if c == "base":
            out.append(txt(f"ldv{i}", x - 55, base - h - 45, str(v), "f2 slate", "center", 200))
            continue
        lab_v = f"{v} of {N}" if c == "strict" else str(v)
        out.append(txt(f"ldv{i}", x - 55, base - h - 45, lab_v, "f2 orange" if c != "strict" else "f2 ink", "center", 200))
    return "".join(out)


# ================================================================================================ the slides
def slides():
    return {
        "fig2_axes": fig2("axes"), "fig2_bars": fig2("bars"), "fig2_top": fig2("top"), "fig2_think": fig2("think"),
        "fig2_rec": fig2("recomputed"),
        "rec_table": recompute("table"), "rec_two": recompute("two"), "divisor": divisor(),
        "retest_cut": retest(), "rank_claim": rank("claim"), "rank_table": rank("table"),
        "lean_size": lean_size(), "flag_count": flag_count(),
        "ds_two": deepseek("two"), "ds_three": deepseek("three"),
        "excess_gpt": excess("gpt"), "excess_all": excess("all"),
        "kind_all": kind("all"), "kind_gpt": kind("gpt"), "kind_rev": kind("rev"),
        "facts_before": facts("before"), "facts_after": facts("after"),
        "recall": recall("known"), "recall_guess": recall("guess"), "dist": dist(),
        "ladder2": ladder(2), "ladder3": ladder(3), "ladder4": ladder(4),
    }


# Which board each chart stands on, and its native extent (x0, width, bottom y): the stand reaches the ground.
STYLE = {"fig2": "paper", "rec_": "term", "divisor": "term", "retest": "term", "rank": "term", "lean": "bench",
         "flag": "bench", "ds": "bench", "excess": "bench", "kind": "paper", "facts": "bench", "recall": "bench",
         "dist": "map", "ladder": "map"}


def stand_of(slide):
    style = next(v for k, v in STYLE.items() if slide.startswith(k))
    if slide.startswith("fig2"):
        x, w, y, h = F2["x"], F2["w"], F2["y"], F2["h"]
    elif slide.startswith("kind"):
        x, w, y, h = KB["x"], KB["w"], BY, BH
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
