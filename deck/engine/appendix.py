"""The appendix (A1 to A9): native, editable PowerPoint built from deck/APPENDIX.md on every build.

Real text boxes, real tables, a native chart for the use of funds and a Gantt made of editable shapes, in a
clean formal style: white background, ink text, navy headings, one gold accent, Calibri. Every word and number
comes from APPENDIX.md; the speaker notes are its Notes paragraphs, verbatim."""
import os, re
from lxml import etree
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION

DECK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(DECK, "APPENDIX.md")

INK = RGBColor(0x18, 0x14, 0x25)
NAVY = RGBColor(0x12, 0x4E, 0x89)
GOLD = RGBColor(0xFE, 0xAE, 0x34)
GREY = RGBColor(0x5A, 0x69, 0x88)
RULE = RGBColor(0xC0, 0xCB, 0xDC)
TINT = RGBColor(0xF2, 0xF5, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"

W, H = Inches(13.333), Inches(7.5)
M = Inches(0.6)                     # side margin
TOP = Inches(1.55)                  # where the body starts, under the title and its gold rule

FADE = """<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition>"""
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}


# ---------------------------------------------------------------- parsing APPENDIX.md
def _clean(s):
    return s.replace("**", "").strip()


def parse(path=SOURCE):
    """-> list of slides: {id, heading, title, subtitle, notes, tables: [[row cells]], bullets, objectives,
    steps, lines}. Bold markers are kept in table cells (a bold row is the total)."""
    text = open(path).read()
    parts = re.split(r"^## (A\d+)\. (.*)$", text, flags=re.M)
    slides = []
    for k in range(1, len(parts), 3):
        sid, heading, body = parts[k], parts[k + 1].strip(), parts[k + 2]
        s = {"id": sid, "heading": heading, "title": heading, "subtitle": None, "notes": "", "tables": [],
             "bullets": [], "objectives": [], "steps": [], "after_table": []}
        table, seen_table = [], False
        for line in body.split("\n"):
            l = line.strip()
            if l.startswith("**Title:**"):
                s["title"] = _clean(l[len("**Title:**"):])
            elif l.startswith("**Subtitle:**"):
                s["subtitle"] = _clean(l[len("**Subtitle:**"):])
            elif l.startswith("**Notes:**"):
                s["notes"] = l[len("**Notes:**"):].strip()
            elif l.startswith("|"):
                cells = [c.strip() for c in l.strip("|").split("|")]
                if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    continue
                table.append(cells)
            else:
                if table:
                    s["tables"].append(table); table = []; seen_table = True
                m = re.match(r"^\*\*Objective (\d+)\. (.*)\*\*$", l)
                if m:
                    s["objectives"].append({"title": f"Objective {m.group(1)}. {m.group(2)}", "items": []})
                    continue
                m = re.match(r"^(\d+)\. \*\*(.*?)\*\* ?(.*)$", l)
                if m:
                    s["steps"].append((_clean(m.group(2)), m.group(3).strip()))
                    continue
                if l.startswith("- "):
                    item = l[2:].strip()
                    if s["objectives"]:
                        s["objectives"][-1]["items"].append(item)
                    elif seen_table:
                        s["after_table"].append(item)
                    else:
                        s["bullets"].append(item)
        if table:
            s["tables"].append(table)
        slides.append(s)
    return slides


# ---------------------------------------------------------------- drawing helpers
def _text(slide, x, y, w, h, paras, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
          bullets=False, space_after=6):
    """A text box. paras: list of strings or of [(run text, {bold, color, size})]."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        para.space_after = Pt(space_after)
        runs = p if isinstance(p, list) else [(("•  " if bullets else "") + p, {})]
        if bullets and isinstance(p, list):
            runs = [("•  ", {})] + runs
        for t, st in runs:
            r = para.add_run()
            r.text = t
            f = r.font
            f.name = FONT
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.color.rgb = st.get("color", color)
    return tb


def _base(prs, s, layout):
    slide = prs.slides.add_slide(layout)
    bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = WHITE
    # the small appendix marker, top right, and the slide id
    _text(slide, W - M - Inches(2.4), Inches(0.28), Inches(2.4), Inches(0.35),
          [[("Appendix  ", {"color": GREY, "size": 12}), (s["id"], {"color": GOLD, "size": 12, "bold": True})]],
          align=PP_ALIGN.RIGHT)
    if s["id"] != "A1":
        size = 28 if len(s["title"]) <= 52 else 24      # long titles stay on one line
        _text(slide, M, Inches(0.55), W - 2 * M, Inches(0.75), [s["title"]], size=size, color=NAVY, bold=True,
              anchor=MSO_ANCHOR.BOTTOM)
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, M + Inches(0.05), Inches(1.33), Inches(0.9), Inches(0.06))
        _solid(bar, GOLD)
    slide.notes_slide.notes_text_frame.text = s["notes"]
    # a fade into every appendix slide
    el = slide._element
    t = etree.fromstring(FADE)
    clr = el.find("p:clrMapOvr", NS)
    (clr.addnext(t) if clr is not None else el.find("p:cSld", NS).addnext(t))
    return slide


def _solid(shape, rgb, line=None):
    shape.fill.solid(); shape.fill.fore_color.rgb = rgb
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
    shape.shadow.inherit = False


def _table(slide, rows, x, y, w, col_w, size=14, row_h=0.45, header=True, highlight=None):
    """A native table: navy header, thin rules, the bold row (a total) in gold tint."""
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, x, y, w, Inches(row_h * nr))
    tbl = gt.table
    tbl.first_row = header
    tbl.horz_banding = False
    tot = sum(col_w)
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Emu(int(w * cw / tot))
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(row_h)
        bold_row = any("**" in c for c in row)
        for j, raw in enumerate(row):
            cell = tbl.cell(i, j)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            tf.text = _clean(raw)
            for p in tf.paragraphs:
                for r in p.runs:
                    r.font.name = FONT
                    r.font.size = Pt(size)
                    r.font.bold = (i == 0 and header) or bold_row or (j == 0 and not header)
                    r.font.color.rgb = WHITE if (i == 0 and header) else INK
            cell.fill.solid()
            if i == 0 and header:
                cell.fill.fore_color.rgb = NAVY
            elif bold_row or (highlight and highlight(i, row)):
                cell.fill.fore_color.rgb = RGBColor(0xFF, 0xF3, 0xD6)
            else:
                cell.fill.fore_color.rgb = WHITE if i % 2 else TINT
    return gt


# ---------------------------------------------------------------- the nine slides
def a1(prs, s, layout):
    sl = _base(prs, s, layout)
    _text(sl, M, Inches(2.55), Inches(10), Inches(1.2), [s["title"]], size=54, color=NAVY, bold=True,
          anchor=MSO_ANCHOR.BOTTOM)
    bar = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, M + Inches(0.05), Inches(3.85), Inches(1.2), Inches(0.08))
    _solid(bar, GOLD)
    _text(sl, M, Inches(4.1), Inches(11), Inches(0.8), [s["subtitle"]], size=24, color=INK)
    _text(sl, M, Inches(6.6), Inches(8), Inches(0.4), ["3B Therapeutics"], size=14, color=GREY)


def a2(prs, s, layout):
    sl = _base(prs, s, layout)
    _table(sl, s["tables"][0], M, TOP + Inches(0.15), W - 2 * M, [3.6, 8.5], size=15, row_h=0.6)


def a3(prs, s, layout):
    sl = _base(prs, s, layout)
    gap = Inches(0.35)
    bw = int((W - 2 * M - gap) / 2)
    bh = Inches(2.65)
    for k, ob in enumerate(s["objectives"]):
        x = M + (bw + gap) * (k % 2)
        y = TOP + Inches(0.1) + (bh + Inches(0.15)) * (k // 2)
        mark = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y + Inches(0.06), Inches(0.07), Inches(0.36))
        _solid(mark, GOLD)
        _text(sl, x + Inches(0.18), y, bw - Inches(0.2), Inches(0.62), [ob["title"]], size=17, color=NAVY, bold=True,
              space_after=0)
        _text(sl, x + Inches(0.18), y + Inches(0.66), bw - Inches(0.2), bh - Inches(0.66), ob["items"], size=16,
              bullets=True, space_after=4)


def a4(prs, s, layout):
    sl = _base(prs, s, layout)
    rows = s["tables"][0]
    _table(sl, rows, M, TOP + Inches(0.1), W - 2 * M, [4.4, 1.6, 1.6, 2.6, 1.9], size=13, row_h=0.47)


def a5(prs, s, layout):
    """The Gantt: one row per phase, a navy bar over its months and a gold diamond with the milestone at its end."""
    sl = _base(prs, s, layout)
    rows = s["tables"][0][1:]
    lx, lw = M, Inches(4.9)                      # phase text column
    gx = M + Inches(5.15)                        # chart area
    gw = W - M - gx
    gy = TOP + Inches(0.55)
    rh = Inches(0.98)
    months = 36

    def X(mo):
        return int(gx + gw * mo / months)
    # axis: month ticks every 6, light vertical rules
    for mo in range(0, months + 1, 6):
        ln = sl.shapes.add_connector(1, X(mo), gy - Inches(0.05), X(mo), gy + rh * len(rows))
        ln.line.color.rgb = RULE; ln.line.width = Pt(0.75)
        _text(sl, X(mo) - Inches(0.4), gy - Inches(0.45), Inches(0.8), Inches(0.35), [f"{mo}"], size=13, color=GREY,
              align=PP_ALIGN.CENTER)
    _text(sl, gx, gy - Inches(0.8), Inches(3), Inches(0.35), ["Month"], size=13, color=GREY)
    _text(sl, lx, gy - Inches(0.45), lw, Inches(0.35), [[("Months", {"bold": True, "color": GREY, "size": 13}),
                                                          ("   Phase", {"bold": True, "color": GREY, "size": 13})]])
    for i, (span, phase, milestone) in enumerate(rows):
        a, b = [int(v) for v in re.findall(r"\d+", span)[:2]]
        y = gy + rh * i
        if i:
            ln = sl.shapes.add_connector(1, lx, y, W - M, y)
            ln.line.color.rgb = RULE; ln.line.width = Pt(0.75)
        _text(sl, lx, y + Inches(0.06), lw, rh - Inches(0.1),
              [[(span + "   ", {"bold": True, "color": NAVY, "size": 12}), (phase, {"size": 12})]], space_after=0)
        bar = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, X(a), y + Inches(0.14), X(b) - X(a), Inches(0.3))
        _solid(bar, NAVY)
        d = Inches(0.3)
        dia = sl.shapes.add_shape(MSO_SHAPE.DIAMOND, X(b) - d // 2, y + Inches(0.14), d, d)
        _solid(dia, GOLD, line=INK)
        mw = Inches(3.3)
        mx = min(max(X(b) - mw, gx), W - M - mw)
        _text(sl, mx, y + Inches(0.48), mw, Inches(0.48), [milestone], size=12, color=INK,
              align=PP_ALIGN.RIGHT, space_after=0)


def a6(prs, s, layout):
    sl = _base(prs, s, layout)
    rows = s["tables"][0]
    body = [r for r in rows[1:] if "**" not in r[0]]
    cd = CategoryChartData()
    cd.categories = [_clean(r[0]) for r in body]
    cd.add_series("$M", [float(re.sub(r"[^\d.]", "", r[1])) for r in body])
    cw = Inches(4.6)
    gf = sl.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, M, TOP + Inches(0.1), cw, Inches(5.2), cd)
    ch = gf.chart
    ch.has_legend = False
    ch.has_title = False
    ch.font.name = FONT; ch.font.size = Pt(13); ch.font.color.rgb = INK
    pl = ch.plots[0]
    pl.gap_width = 60
    pl.has_data_labels = True
    pl.data_labels.number_format = '"$"0.0"M"'
    pl.data_labels.number_format_is_linked = False
    pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    pl.data_labels.font.size = Pt(13); pl.data_labels.font.name = FONT
    ser = pl.series[0]
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = NAVY
    pt = ser.points[0]
    pt.format.fill.solid(); pt.format.fill.fore_color.rgb = GOLD      # the largest use, in the one accent colour
    ca = ch.category_axis
    ca.reverse_order = True
    ca.tick_labels.font.size = Pt(13)
    ca.format.line.color.rgb = RULE
    va = ch.value_axis
    va.visible = False
    va.has_major_gridlines = False
    va.maximum_scale = 3.8
    va.minimum_scale = 0
    tx = M + cw + Inches(0.3)
    _table(sl, rows, tx, TOP + Inches(0.1), W - M - tx, [2.0, 1.1, 4.7], size=13, row_h=0.62)


def a7(prs, s, layout):
    sl = _base(prs, s, layout)
    n = len(s["steps"])
    gap = Inches(0.55)
    bw = int((W - 2 * M - gap * (n - 1)) / n)
    by, bh = TOP + Inches(0.45), Inches(3.4)
    for k, (head, rest) in enumerate(s["steps"]):
        x = M + (bw + gap) * k
        box = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, by, bw, bh)
        _solid(box, TINT, line=RULE)
        top = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, by, bw, Inches(0.09))
        _solid(top, GOLD if k == 0 else NAVY)
        _text(sl, x + Inches(0.2), by + Inches(0.25), bw - Inches(0.4), Inches(0.9), [head], size=20, color=NAVY, bold=True)
        paras = []
        for sent in re.split(r"(?<=\.) (?=[A-Z])", rest):
            if sent.startswith("Trigger:"):
                paras.append([("Trigger: ", {"bold": True}), (sent[len("Trigger:"):].strip(), {})])
            else:
                paras.append(sent)
        _text(sl, x + Inches(0.2), by + Inches(1.15), bw - Inches(0.4), bh - Inches(1.3), paras, size=16, space_after=10)
        if k < n - 1:
            ar = sl.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + bw + Inches(0.1), by + bh / 2 - Inches(0.2),
                                     gap - Inches(0.2), Inches(0.4))
            _solid(ar, GOLD)


def a8(prs, s, layout):
    sl = _base(prs, s, layout)
    rows = s["tables"][0]
    _table(sl, rows, M, TOP + Inches(0.1), W - 2 * M, [3.3, 5.2, 3.6], size=15, row_h=0.55)
    y = TOP + Inches(0.1) + Inches(0.55 * len(rows)) + Inches(0.35)
    _text(sl, M, y, W - 2 * M, Inches(1.2), s["after_table"], size=16, bullets=True, space_after=6)


def a9(prs, s, layout):
    sl = _base(prs, s, layout)
    _text(sl, M, TOP + Inches(0.1), W - 2 * M, H - TOP - Inches(0.6), s["bullets"], size=16, bullets=True, space_after=4)


BUILDERS = {"A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5, "A6": a6, "A7": a7, "A8": a8, "A9": a9}


def add(prs, layout):
    """Append the appendix to an open Presentation. Returns the parsed slides (for the notes check)."""
    slides = parse()
    for s in slides:
        BUILDERS[s["id"]](prs, s, layout)
    return slides
