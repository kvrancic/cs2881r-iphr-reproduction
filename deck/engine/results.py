"""The results slides, authored in HTML/CSS on the finer 960x540 grid (2.5 x the 384x216 art grid), rendered
by headless Chromium, snapped to Endesga 32 with no anti-aliasing, and cut into one picture per element so
every card and tile is its own Morph object.

Every figure on these slides comes from BRIEF.md or from the files it names:
  camel-hacks/RESULTS.md, camel-hacks/exports/probes/RESULTS.md,
  camel-hacks/exports/probes/results/target_list_macrophage_SPP1.{csv,json}.
"""
import csv, hashlib, io, json, os
import numpy as np
from PIL import Image
from pal import HEX, C

ENGINE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.dirname(ENGINE)
FONT = os.path.join(DECK, "art", "fonts", "Jersey10.ttf")
CACHE = os.path.join(DECK, "build", "results")
TARGETS = "/Users/karlovrancic/Documents/projects/camel-hacks/exports/probes/results/target_list_macrophage_SPP1.csv"
GW, GH = 960, 540
SCALE = 384 / GW          # native pixels per grid pixel (0.4)

# Jersey 10 is drawn on a 75-unit grid in a 1400-unit em: 56/3 px puts one font pixel on one grid pixel.
F = {1: 56 / 3, 2: 112 / 3, 3: 56, 4: 224 / 3, 5: 280 / 3}

CSS = """
@font-face { font-family: J; src: url(data:font/ttf;base64,%(font)s) format('truetype'); }
@font-face { font-family: P; src: url(data:font/ttf;base64,%(pfont)s) format('truetype'); }
:root { %(vars)s }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 960px; height: 540px; background: transparent; overflow: hidden; }
body { font-family: J; color: var(--ink); -webkit-font-smoothing: none; font-kerning: none; }
.o { position: absolute; }
.f2 { font-size: %(f2)spx; line-height: 40px; }
.f3 { font-size: %(f3)spx; line-height: 60px; }
.f4 { font-size: %(f4)spx; line-height: 80px; }
.f5 { font-size: %(f5)spx; line-height: 100px; }
.g { font-family: P; font-size: 24px; line-height: 30px; }
.g2 { font-family: P; font-size: 16px; line-height: 20px; }
/* an instrument panel in the pixel world: night face, dusk bezel, ink outline, ice drop shadow; every edge
   a multiple of 5 grid pixels, so it lands on whole pixels of the art grid */
.panel { background: var(--night);
  box-shadow: inset 0 0 0 5px var(--dusk), inset 0 5px 0 5px var(--slate), 0 0 0 5px var(--ink), 10px 10px 0 5px var(--ice); }
.white { color: var(--white); } .ice { color: var(--ice); } .steel { color: var(--steel); } .slate { color: var(--slate); }
.green { color: var(--green); } .lime { color: var(--yellow); } .gold { color: var(--gold); } .navy { color: var(--navy); }
.track { height: 20px; background: var(--dusk); }
.bar { height: 20px; background: var(--green); box-shadow: inset 0 5px 0 0 var(--yellow), inset 0 -5px 0 0 var(--leaf); }
.lamp { width: 15px; height: 15px; background: var(--green); box-shadow: inset 5px 5px 0 0 var(--yellow), 0 0 0 5px var(--ink); }
.hl { background: var(--deep); }
"""


def _css():
    import base64
    v = " ".join(f"--{k}: #{h};" for k, h in HEX.items())
    b64 = lambda f: base64.b64encode(open(os.path.join(DECK, "art", "fonts", f), "rb").read()).decode()
    return CSS % dict(font=b64("Jersey10.ttf"), pfont=b64("PressStart2P.ttf"), vars=v, f2=F[2], f3=F[3], f4=F[4], f5=F[5])


def arrow_svg(w=30, color="white", h=16):
    """A right-pointing pixel arrow drawn with whole-pixel rects."""
    c = f"#{HEX[color]}"
    cy = h // 2
    rects = [f'<rect x="0" y="{cy - 2}" width="{w - 8}" height="4" fill="{c}"/>']
    for k in range(8):
        hh = 2 * (8 - k)
        rects.append(f'<rect x="{w - 8 + k}" y="{cy - hh // 2}" width="1" height="{hh}" fill="{c}"/>')
    return f'<svg width="{w}" height="{h}" shape-rendering="crispEdges" style="display:inline-block;vertical-align:middle">{"".join(rects)}</svg>'


def gene(s, cls="g", color="white"):
    """Gene symbols in Press Start 2P: a serifed I and a footed 1, so SPI1 never reads SPII."""
    return f'<span class="{cls} {color}">{s}</span>'


# ---------------------------------------------------------------- data
def targets():
    rows = list(csv.DictReader(open(TARGETS)))
    meta = json.load(open(TARGETS.replace(".csv", ".json")))
    order = meta["gene_order"]
    rows.sort(key=lambda r: order.index(r["gene"]))
    return rows, meta


PARTNERS = [  # BRIEF.md and camel-hacks/RESULTS.md item 6d (hand-picked examples, not a rate); descriptions are ours
    ("TGFBR2", "SMAD2", "receptor and messenger"),
    ("TRADD", "TNFRSF1A", "adapter and receptor"),
    ("AHR", "ARNT", "two halves of one factor"),
    ("ADAM17", "RHBDF2", "enzyme and its escort"),
    ("FARSA", "FARSB", "two parts of one enzyme"),
]


def lamp(x, y, label="measured"):
    return (f'<div class="o lamp" style="left:{x}px;top:{y + 10}px"></div>'
            f'<div class="o f2 green" style="left:{x + 25}px;top:{y}px">{label}</div>')


def panel(id_, x, y, w, h, body):
    return f'<div class="o panel" data-id="{id_}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{body}</div>'


def note(id_, x, y, w, lines):
    """Explanatory lines in ink on the white ground, outside the instrument."""
    body = "".join(f'<div class="f2">{l}</div>' for l in lines)
    return f'<div class="o" data-id="{id_}" style="left:{x}px;top:{y}px;width:{w}px">{body}</div>'


def svg_line(x0, y0, x1, y1, col, w=5, head=0, dash=0):
    """A pixel line of w x w squares, with an optional arrow head of the given length."""
    import math
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    out = []
    for s_ in range(0, int(L) + 1, 2):
        if dash and (s_ // dash) % 2:
            continue
        out.append(f'<rect x="{round(x0 + ux * s_ - w / 2)}" y="{round(y0 + uy * s_ - w / 2)}" width="{w}" height="{w}" fill="#{HEX[col]}"/>')
    for k in range(0, head, 2):
        for side in (-1, 1):
            px_ = x1 - ux * k + side * (-uy) * k * 0.6
            py_ = y1 - uy * k + side * ux * k * 0.6
            out.append(f'<rect x="{round(px_ - w / 2)}" y="{round(py_ - w / 2)}" width="{w}" height="{w}" fill="#{HEX[col]}"/>')
    return "".join(out)


# ---------------------------------------------------------------- pieces
def header():
    return ('<div class="o" data-id="rhead" style="left:40px;top:25px;width:700px;height:45px">'
            '<div class="f2">Results on real human data</div></div>')


ATLAS_ICON = {"atlas_m": (65, 120), "atlas_f": (525, 140)}   # where the deck puts the cell sprites (960 grid)


def atlas_panels():
    def one(id_, x, label, num, lines):
        body = (f'<div class="o f2 ice" style="left:25px;top:20px">{label}</div>'
                f'<div class="o f5 green" style="left:160px;top:60px">{num}</div>'
                + "".join(f'<div class="o f2 white" style="left:25px;top:{175 + 40 * k}px">{l}</div>' for k, l in enumerate(lines)))
        return panel(id_, x, 90, 420, 320, body)
    return (one("atlas_m", 40, "Macrophages, the guards", "4,378", ["knockdowns that passed", "quality checks"]) +
            one("atlas_f", 500, "Fibroblasts, the wall builders", "8,693", ["knockdowns that passed", "quality checks, measured", "at two timepoints"]) +
            note("n0", 40, 435, 880, ["Each knockdown switches off one gene; every cell is read out."]))


def card1():
    import math
    ox, oy, L = 60, 270, 210
    def tip(deg, l=L):
        r = math.radians(deg)
        return ox + l * math.cos(r), oy - l * math.sin(r)
    a0 = 6
    ax, ay = tip(a0); bx_, by_ = tip(a0 + math.degrees(math.acos(0.89))); rx_, ry_ = tip(a0 + math.degrees(math.acos(0.02)), 150)
    svg = (f'<svg class="o" style="left:0px;top:0px" width="440" height="320" shape-rendering="crispEdges">'
           + svg_line(ox, oy, rx_, ry_, "steel", 5, 18, dash=10)
           + svg_line(ox, oy, bx_, by_, "green", 5, 20) + svg_line(ox, oy, ax, ay, "green", 5, 20)
           + f'<rect x="{ox - 8}" y="{oy - 8}" width="15" height="15" fill="#{HEX["white"]}"/></svg>')
    labels = (f'<div class="o f2 green" style="left:{round(ax) + 10}px;top:{round(ay) - 25}px">A</div>'
              f'<div class="o f2 green" style="left:{round(bx_) + 10}px;top:{round(by_) - 30}px">B</div>'
              f'<div class="o f2 steel" style="left:{round(rx_) + 20}px;top:{round(ry_) - 15}px">random gene</div>')
    right = ('<div class="o" style="left:470px;top:55px;width:380px">'
             '<div class="f5 green">0.89</div><div class="f2 white">same gene, A and B</div>'
             '<div class="f3 steel" style="margin-top:10px">0.02</div><div class="f2 steel">random pairs of genes</div></div>')
    body = ('<div class="o f2 ice" style="left:25px;top:20px">Same gene, two separate experiments</div>' + lamp(690, 20)
            + svg + labels + right)
    return (panel("r1", 40, 90, 880, 320, body) +
            note("n1", 40, 430, 880, ["Median cosine over knockdown pairs measured in two libraries,",
                                      "with a real effect in both. 1 = the same direction."]))


def card2():
    rows = [("transcription factor", 28.6), ("surface protein", 28.9), ("signaling protein", 14.9), ("by chance", 0.02)]
    bx, bw = 345, 400
    out = []
    for i, (lbl, v) in enumerate(rows):
        y = 110 + i * 42
        w = max(5, round(bw * v / 100 / 5) * 5) if v >= 1 else 3
        grey = lbl == "by chance"
        out.append(f'<div class="o f2 {"steel" if grey else "white"}" style="left:25px;top:{y - 10}px">{lbl}</div>'
                   f'<div class="o track" style="left:{bx}px;top:{y}px;width:{bw}px"></div>'
                   f'<div class="o bar" style="left:{bx}px;top:{y}px;width:{w}px;{"background:var(--steel);box-shadow:none" if grey else ""}"></div>'
                   f'<div class="o f2 {"steel" if grey else "green"}" style="left:{bx + w + 15}px;top:{y - 10}px">{v:g}%</div>')
    ticks = (f'<div class="o" style="left:{bx}px;top:275px;width:{bw}px;height:5px;background:var(--steel)"></div>'
             + "".join(f'<div class="o" style="left:{bx + round(bw * t) - (0 if t < 1 else 5)}px;top:270px;width:5px;height:10px;background:var(--steel)"></div>' for t in (0, 0.25, 0.5, 0.75, 1))
             + f'<div class="o f2 steel" style="left:{bx - 5}px;top:275px">0</div>'
             + f'<div class="o f2 steel" style="left:{bx + bw // 2 - 20}px;top:275px">50%</div>'
             + f'<div class="o f2 steel" style="left:{bx + bw - 55}px;top:275px">100%</div>')
    body = ('<div class="o f2 ice" style="left:25px;top:20px">Can it name a gene from its effect alone?</div>' + lamp(690, 20)
            + '<div class="o f2 white" style="left:25px;top:55px">ranked first, by library:</div>' + "".join(out) + ticks)
    return (panel("r2", 40, 90, 880, 320, body) +
            note("n2", 40, 430, 880, ["Out of 4,377 candidates, among knockdowns with a real effect.",
                                      "Picking at random, the right gene comes first 0.02% of the time."]))


def card3():
    rows = []
    for i, (a, b, d) in enumerate(PARTNERS):
        y = 75 + i * 45
        rows.append(f'<div class="o" style="left:25px;top:{y + 5}px;width:195px;text-align:right">{gene(a)}</div>'
                    f'<div class="o" style="left:235px;top:{y + 12}px">{arrow_svg(30, "white")}</div>'
                    f'<div class="o" style="left:280px;top:{y + 5}px">{gene(b, color="green")}</div>'
                    f'<div class="o f2 steel" style="left:495px;top:{y}px;width:380px">{d}</div>')
    body = ('<div class="o f2 ice" style="left:25px;top:20px">Examples where the first pick was the known partner</div>'
            + "".join(rows))
    return (panel("r3", 40, 90, 880, 320, body) +
            note("n3", 40, 430, 880, ["The gene itself removed from about 4,363 options; the compiler",
                                      "is given no biology, only measured effects."]))


def card4():
    cols, rows_ = 99, 45
    rng = np.random.default_rng(7)
    lit = set(rng.choice(4378, 84, replace=False).tolist())
    rects = []
    for k in range(4378):
        if k in lit:
            continue
        x, y = (k % cols) * 4, (k // cols) * 4
        rects.append(f'<rect x="{x}" y="{y}" width="2" height="2" fill="#{HEX["slate"]}"/>')
    for k in lit:   # the 84 drawn on top, large, with an ink rim so they stand out
        x, y = (k % cols) * 4, (k // cols) * 4
        rects.append(f'<rect x="{x - 3}" y="{y - 3}" width="9" height="9" fill="#{HEX["ink"]}"/>'
                     f'<rect x="{x - 2}" y="{y - 2}" width="7" height="7" fill="#{HEX["green"]}"/>'
                     f'<rect x="{x - 2}" y="{y - 2}" width="3" height="3" fill="#{HEX["yellow"]}"/>')
    svg = f'<svg class="o" style="left:25px;top:105px" width="{cols * 4 + 4}" height="{rows_ * 4 + 4}" shape-rendering="crispEdges">{"".join(rects)}</svg>'
    body = ('<div class="o f2 ice" style="left:25px;top:20px">Goal: lower SPP1 in macrophages</div>' + lamp(690, 20)
            + '<div class="o f2 steel" style="left:25px;top:55px">each dot is one measured edit</div>' + svg
            + '<div class="o" style="left:460px;top:70px;width:400px">'
              '<div class="f5 green">84</div><div class="f2 white">of 4,378 edits cut SPP1</div>'
              '<div class="f2 white">by 40% or more</div>'
              f'<div class="f2 white" style="margin-top:20px">strongest: {gene("SPI1", color="green")}, 84%</div></div>')
    return (panel("r4", 40, 90, 880, 320, body) +
            note("n4", 40, 430, 880, ["SPP1 marks the macrophages that protect tumors.",
                                      "40% or more in each half of the cells; THP-1 derived."]))


DRUG_ROWS = [  # from annotated_agent and annotated_clinical_status in target_list_macrophage_SPP1.csv
    ("ATP1A1", ["approved: digoxin"], True),
    ("MTOR", ["approved: sirolimus,", "everolimus, temsirolimus"], True),
    ("KDM1A", ["clinical stage: bomedemstat"], False),
]


def table():
    rows, meta = targets()
    frac = {r["gene"]: float(r["measured_fraction_of_SPP1_removed"]) for r in rows}
    out, y = [], 70
    for g, drug, approved in DRUG_ROWS:
        h = 40 * len(drug) + 5
        bw = round(150 * frac[g] / 5) * 5
        out.append((f'<div class="o hl" style="left:15px;top:{y - 5}px;width:850px;height:{h}px"></div>' if approved else "")
                   + f'<div class="o" style="left:30px;top:{y + 5}px">{gene(g)}</div>'
                   f'<div class="o track" style="left:220px;top:{y + 10}px;width:150px"></div>'
                   f'<div class="o bar" style="left:220px;top:{y + 10}px;width:{bw}px"></div>'
                   f'<div class="o f2 white" style="left:385px;top:{y}px">{round(frac[g] * 100)}%</div>'
                   + "".join(f'<div class="o f2 {"green" if approved else "gold"}" style="left:480px;top:{y + 40 * k}px">{l}</div>'
                             for k, l in enumerate(drug)))
        y += h + 5
    rest = [r["gene"] for r in rows if r["gene"] not in {d[0] for d in DRUG_ROWS}]
    assert len(rest) == 14
    strip = (f'<div class="o" style="left:30px;top:{y + 2}px;width:830px;line-height:30px">'
             f'<span class="steel" style="font-size:{F[2]}px;line-height:30px">14 more, no drug yet: </span>'
             + " ".join(f'<span style="margin-right:6px">{gene(g, "g2", "ice")}</span>' for g in rest) + '</div>')
    body = ('<div class="o f2 ice" style="left:25px;top:20px">17 targets for lowering SPP1, approved drugs first</div>'
            + "".join(out) + strip)
    return (panel("r4", 40, 85, 880, 365, body) +
            note("n5", 40, 470, 880, ["Ordered by drug status, then by effect. All 17 measured."]))


def summary():
    def tile(i, x, y, title, fig, sub):
        return panel(f"r{i}", x, y, 430, 205,
                     f'<div class="o f2 ice" style="left:20px;top:15px;width:400px">{title}</div>'
                     f'<div class="o" style="left:20px;top:45px;width:400px">{fig}</div>'
                     + "".join(f'<div class="o f2 white" style="left:20px;top:{122 + 35 * k}px;width:400px">{l}</div>' for k, l in enumerate(sub)))
    return (tile(1, 40, 85, "Same gene, two experiments", '<div class="f4 green">0.89</div>',
                 ["median cosine;", "random pairs: 0.02"]) +
            tile(2, 490, 85, "Named from its effect alone", '<div class="f4 green">28.9%</div>',
                 ["real-effect knockdowns;", "by chance: 0.02%"]) +
            tile(3, 40, 305, "Examples: partner first",
                 f'<div style="margin-top:22px">{gene("TGFBR2")} {arrow_svg(30)} {gene("SMAD2", color="green")}</div>',
                 ["and four more examples"]) +
            tile(4, 490, 305, "Lower SPP1 in macrophages", '<div class="f4 green">17 targets</div>',
                 ["2 with approved drugs:", f'{gene("ATP1A1", "g2")} and {gene("MTOR", "g2")}']))


# ---------------------------------------------------------------- slides
def slides():
    """Each results slide as one HTML body; every element with a data-id becomes one Morph object."""
    return {"atlas": header() + atlas_panels(), "r1": header() + card1(), "r2": header() + card2(),
            "r3": header() + card3(), "r4": header() + card4(), "table": header() + table(),
            "summary": header() + summary()}


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


def render(force=False):
    """-> {slide: [(id, PIL image on the 960 grid, x, y), ...]} with x, y on the 960 grid. Cached by content."""
    html_all = slides()
    key = hashlib.sha1((_css() + json.dumps(html_all, sort_keys=True)).encode()).hexdigest()[:12]
    os.makedirs(CACHE, exist_ok=True)
    idx = os.path.join(CACHE, f"index_{key}.json")
    if os.path.exists(idx) and not force:
        meta = json.load(open(idx))
        return {sl: [(i, Image.open(os.path.join(CACHE, f)), x, y) for i, f, x, y in items] for sl, items in meta.items()}
    from playwright.sync_api import sync_playwright
    out, meta = {}, {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": GW, "height": GH}, device_scale_factor=1)
        for sl, body in html_all.items():
            page.set_content(f"<!doctype html><html><head><meta charset='utf-8'><style>{_css()}</style></head><body>{body}</body></html>")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(50)
            items, mitems = [], []
            for el in page.query_selector_all("[data-id]"):
                i = el.get_attribute("data-id")
                bb = el.bounding_box()
                # include the pixel border and drop shadow drawn by box-shadow
                clip = {"x": bb["x"] - 8, "y": bb["y"] - 8, "width": bb["width"] + 26, "height": bb["height"] + 26}
                page.evaluate("(id) => { for (const e of document.querySelectorAll('[data-id]')) e.style.visibility = e.dataset.id === id ? 'visible' : 'hidden'; }", i)
                png = page.screenshot(clip=clip, omit_background=True)
                page.evaluate("() => { for (const e of document.querySelectorAll('[data-id]')) e.style.visibility = 'visible'; }")
                img = _snap(Image.open(io.BytesIO(png)))
                bbox = img.getbbox() or (0, 0, 1, 1)
                img = img.crop(bbox)
                x, y = round(clip["x"]) + bbox[0], round(clip["y"]) + bbox[1]
                f = f"{key}_{sl}_{i}.png"
                img.save(os.path.join(CACHE, f))
                items.append((i, img, x, y)); mitems.append((i, f, x, y))
            out[sl] = items; meta[sl] = mitems
            page.screenshot(path=os.path.join(CACHE, f"page_{sl}.png"))
        b.close()
    json.dump(meta, open(idx, "w"))
    return out


if __name__ == "__main__":
    import sys
    r = render(force=True)
    for sl, items in r.items():
        print(sl, [(i, im.size, x, y) for i, im, x, y in items])
