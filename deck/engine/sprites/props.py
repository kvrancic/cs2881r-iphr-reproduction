"""Props of this talk, all drawn in code at native resolution: the weighing scale of the hidden lean, chat windows,
question cards and answer pips, the flag, the released-data folder, numbered slots, the compass and longitude map,
the aqua fact card and small icons for the kinds of question. Light from the top left, 1px ink outlines."""
import math
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from px import blank, rect, frame, text, paste, line, poly, outline, disc, dither, recolor, ascii_sprite, ellipse
from pal import rgba, C


def _P(img, x, y, col):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((int(x), int(y)), rgba(col))


def _box(img, x, y, w, h, fill, edge="ink"):
    rect(img, x, y, w, h, edge)
    rect(img, x + 1, y + 1, w - 2, h - 2, fill)


def _rbox(img, x, y, w, h, fill, edge="ink"):
    """A box with clipped corners (the pixel-art rounded rectangle)."""
    rect(img, x + 1, y, w - 2, h, edge); rect(img, x, y + 1, w, h - 2, edge)
    rect(img, x + 1, y + 1, w - 2, h - 2, fill)


GREY = {"gold": "ice", "yellow": "white", "orange": "steel", "brown": "slate", "red": "steel", "wine": "slate",
        "rose": "ice", "green": "steel", "leaf": "slate", "slate": "steel", "dusk": "steel", "steel": "ice",
        "clay": "steel", "peach": "ice", "ink": "steel", "plum": "slate"}


def faint(img):
    """The hidden-cause look: every colour pushed to pale grey, ink lines to steel."""
    return recolor(img, GREY)


# ------------------------------------------------------------------------------------------------ the scale
def scale(tilt=0, grey=False, plates=True):
    """A brass balance on a post. tilt -1: the NO pan (left, red) sinks; +1: the YES pan (right, green) sinks;
    0: level. grey=True draws it faint, the way it hangs behind the robot before the talk names it."""
    W, H = 86, 72
    img = blank(W, H)
    cx, top = W // 2, 12
    # base and post
    rect(img, cx - 14, H - 6, 28, 5, "ink"); rect(img, cx - 13, H - 5, 26, 3, "gold"); rect(img, cx - 13, H - 5, 26, 1, "yellow")
    rect(img, cx - 9, H - 9, 18, 4, "ink"); rect(img, cx - 8, H - 8, 16, 2, "orange")
    rect(img, cx - 2, top, 4, H - 9 - top, "ink"); rect(img, cx - 1, top, 2, H - 9 - top, "gold"); rect(img, cx - 1, top, 1, H - 9 - top, "yellow")
    # beam
    L = 31
    dy = round(7 * tilt)          # positive: the right end goes down
    ends = [(cx - L, top + 2 - dy), (cx + L, top + 2 + dy)]
    for off, col in ((-1, "ink"), (1, "ink"), (0, "gold")):
        line(img, ends[0][0], ends[0][1] + off, ends[1][0], ends[1][1] + off, col)
    line(img, ends[0][0], ends[0][1] - 0, ends[1][0], ends[1][1] - 0, "gold")
    # pivot cap
    disc(img, cx, top + 2, 3, "ink"); disc(img, cx, top + 2, 2, "orange"); _P(img, cx - 1, top + 1, "yellow")
    # strings and pans
    for k, (ex, ey) in enumerate(ends):
        py = ey + 18
        line(img, ex, ey, ex - 8, py, "slate"); line(img, ex, ey, ex + 8, py, "slate")
        rect(img, ex - 11, py, 23, 2, "ink"); rect(img, ex - 9, py + 2, 19, 2, "ink"); rect(img, ex - 6, py + 4, 13, 1, "ink")
        rect(img, ex - 10, py, 21, 1, "yellow"); rect(img, ex - 8, py + 2, 17, 1, "gold"); rect(img, ex - 9, py + 1, 19, 1, "gold")
        disc(img, ex, ey, 1, "ink")
        if plates:
            lab, bg = (("NO", "red") if k == 0 else ("YES", "green"))
            from sprites.deckui import plate
            p = plate(lab, bg, "white", 20, 2)
            paste(img, p, ex - p.width // 2, py - p.height)
    return faint(img) if grey else img


# ------------------------------------------------------------------------------------------------ chat windows
def chat(w=150, h=120, title="chat"):
    """A chat window: ice title bar with three lamps and a title, white content area, ink frame."""
    TB = 14
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, TB, "ice"); rect(img, 1, 1, w - 2, 1, "white")
    for i, c in enumerate(("red", "gold", "green")):
        disc(img, 6 + i * 7, 1 + TB // 2, 2, c)
    if title:
        t = text(title, "slate", 20)
        paste(img, t, 26, 1 + (TB - t.height) // 2)
    rect(img, 1, TB + 1, w - 2, 1, "ink")
    rect(img, 1, TB + 2, w - 2, h - TB - 3, "white")
    rect(img, w - 3, TB + 2, 2, h - TB - 3, "ice"); rect(img, 1, h - 3, w - 2, 2, "ice")
    return img


def bubble(s, w, fg="ink", bg="ice", edge="steel", tail="left"):
    """A speech bubble of wrapped pixel text, width w, with a small tail at the bottom."""
    t = text(s, fg, 20, maxw=None if "\n" in s else w - 10)   # explicit line breaks are kept as written
    h = t.height + 9
    img = blank(w, h + 4)
    _rbox(img, 0, 0, w, h, bg, edge)
    paste(img, t, 5, 4)
    tx = 8 if tail == "left" else w - 12
    poly(img, [(tx, h - 1), (tx + 5, h - 1), (tx + (0 if tail == "left" else 5), h + 3)], edge)
    poly(img, [(tx + 1, h - 2), (tx + 4, h - 2), (tx + (1 if tail == "left" else 4), h + 1)], bg)
    return img


def trace(w=120, rows=6, seed=1, col="steel"):
    """Lines of reasoning text drawn as grey strokes (a trace you cannot read from the back of a hall)."""
    import random
    r = random.Random(seed)
    img = blank(w, rows * 6)
    for i in range(rows):
        x = 0
        end = w - (r.randint(10, 40) if i == rows - 1 else r.randint(0, 8))
        while x < end:
            L = r.randint(5, 16)
            rect(img, x, i * 6, min(L, end - x), 2, col)
            x += L + 3
    return img


# ------------------------------------------------------------------------------------------------ cards and pips
def kind_icon(kind):
    """12x12 icon for a kind of question card: book, film, person, place."""
    K = {"K": "ink", "P": "plum", "p": "grape", "W": "white", "S": "sand", "s": "skin", "c": "clay", "B": "brown",
         "G": "slate", "g": "steel", "R": "pink", "r": "rose", "L": "ice"}
    art = {
        "book": """
..KKKKKKKK..
.KppppppPK..
.KpWWWWpPK..
.KppppppPK..
.KpWWWppPK..
.KppppppPK..
.KppppppPK..
.KppppppPK..
.KWWWWWWWK..
.KLLLLLLLK..
..KKKKKKKK..
""",
        "film": """
..KKKKKKKK..
.KGGGGGGGGK.
KGgKgggKgGGK
KGKKKgKKKgGK
KGgKgggKgGGK
KGgggKgggGGK
KGgKgggKgGGK
KGKKKgKKKgGK
KGgKgggKgGGK
.KGGGGGGGGK.
..KKKKKKKK..
""",
        "person": """
....KKKK....
...KBBBBK...
..KBssssBK..
..KsKssKsK..
..KssssssK..
...KssssK...
....KssK....
..KKcccKKK..
.KcccccccK..
.KcccccccK..
.KKKKKKKKK..
""",
        "place": """
....KKKK....
...KRRRRK...
..KRrWRRRK..
..KRWWRRRK..
..KRRRRRRK..
...KRRRRK...
....KRRK....
....KRRK....
.....KK.....
...KKKKKK...
............
""",
    }
    return ascii_sprite(art[kind].strip("\n").split("\n"), K)


def qcard(kind="book", w=26, h=32, lit=False):
    """A question card: white card, a coloured header stripe by kind, the kind's icon and two lines of text."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "white")
    stripe = {"book": "grape", "film": "slate", "person": "clay", "place": "pink"}[kind]
    rect(img, 1, 1, w - 2, 4, stripe)
    ic = kind_icon(kind)
    paste(img, ic, (w - ic.width) // 2, 8)
    rect(img, 4, h - 9, w - 8, 1, "steel"); rect(img, 4, h - 6, w - 12, 1, "steel")
    rect(img, w - 2, 2, 1, h - 3, "ice"); rect(img, 2, h - 2, w - 3, 1, "ice")
    if lit:
        img = outline(img, "gold")
    return img


def pip(ans="N", right=True):
    """One sampled answer: a small plate with Y or N, green for YES and red for NO; a wrong answer gets a darker
    rim and a dithered face, so right and wrong also read in greyscale."""
    bg = "green" if ans == "Y" else "red"
    img = blank(11, 14)
    _rbox(img, 0, 0, 11, 14, bg)
    t = text(ans, "white", 20)
    paste(img, t, (11 - t.width) // 2 + 1, (14 - t.height) // 2)
    if not right:
        rect(img, 1, 12, 9, 1, "ink")
    return img


def answer_row(answers, truth):
    """Ten pips in a row; truth is 'Y' or 'N'."""
    ps = [pip(a, a == truth) for a in answers]
    img = blank(len(ps) * 12 - 1, 14)
    for i, p in enumerate(ps):
        paste(img, p, i * 12, 0)
    return img


def flag(col="gold"):
    """A small pennant on a pole: a flagged pair."""
    img = blank(16, 26)
    rect(img, 1, 1, 3, 25, "ink"); rect(img, 2, 2, 1, 23, "white")
    poly(img, [(4, 1), (15, 6), (4, 12)], "ink")
    poly(img, [(4, 3), (12, 6), (4, 10)], col)
    line(img, 4, 3, 10, 5, "yellow" if col == "gold" else "white")
    rect(img, 0, 24, 5, 2, "ink")
    return img


# ------------------------------------------------------------------------------------------------ data and code
def folder(w=58, h=44):
    """The released-data folder: a tan folder with a tab and a few sheets sticking out."""
    img = blank(w, h)
    _rbox(img, 2, 0, 20, 8, "clay")
    for k, c in enumerate(("white", "ice", "white")):
        _box(img, 6 + k * 6, 3 + k * 2, w - 18, 20, c, "slate")
        for r in range(3):
            rect(img, 9 + k * 6, 7 + k * 2 + r * 4, w - 26, 1, "steel")
    _rbox(img, 0, 12, w, h - 12, "tan")
    rect(img, 1, 13, w - 2, 1, "peach"); rect(img, 1, h - 3, w - 2, 2, "rust")
    return img


def doc(w=34, h=42, chart=True):
    """A paper page: folded corner, text lines and a small blue bar chart (the published figure)."""
    img = blank(w, h)
    _box(img, 0, 0, w, h, "white")
    poly(img, [(w - 9, 0), (w - 1, 8), (w - 9, 8)], "ice")
    line(img, w - 9, 0, w - 9, 8, "ink"); line(img, w - 9, 8, w - 1, 8, "ink")
    for r in range(3):
        rect(img, 4, 5 + r * 4, w - 16 if r == 0 else w - 9, 1, "steel")
    if chart:
        hs = (14, 4, 7, 2, 10, 3)
        for i, hh in enumerate(hs):
            rect(img, 5 + i * 4, h - 5 - hh, 3, hh, "sky"); rect(img, 5 + i * 4, h - 5 - hh, 3, 1, "cyan")
        rect(img, 4, h - 5, w - 8, 1, "ink")
    return img


def terminal(w=58, h=44):
    """Our code: a small dark terminal with a prompt and green lines."""
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, 7, "dusk")
    for i, c in enumerate(("red", "gold", "green")):
        rect(img, 3 + i * 4, 3, 2, 2, c)
    rect(img, 2, 9, w - 4, h - 11, "night")
    rows = [(4, 18, "green"), (4, 30, "ice"), (4, 24, "green"), (4, 34, "ice"), (4, 12, "green")]
    for r, (x, L, c) in enumerate(rows):
        rect(img, x + 4, 13 + r * 6, L, 2, c)
        rect(img, x, 13 + r * 6, 2, 2, "gold")
    return img


# ------------------------------------------------------------------------------------------------ the slots
def slot(n, w=104, h=96, lit=False, dim=False):
    """A numbered slot for 'what we did': a framed card with a big number in its top-left corner."""
    img = blank(w, h)
    border = "gold" if lit else ("ice" if dim else "steel")
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, h - 2, border)
    rect(img, 3, 3, w - 6, h - 6, "ink")
    rect(img, 4, 4, w - 8, h - 8, "white")
    dither(img, 4, h - 14, w - 8, 10, "ice", 0)
    if n is not None:
        from sprites.deckui import big
        b = big(str(n), "gold" if lit else "ink", 60)
        if dim:
            b = faint(b)
        paste(img, b, 8, 7)
    return img


# ------------------------------------------------------------------------------------------------ geography
def globe(r=20, pins=(), equator=True):
    """A small globe: sky ocean, sand land, an equator line, and pins given as (lon, lat) in -1..1."""
    d = 2 * r + 1
    img = blank(d + 2, d + 2)
    cx = cy = r + 1
    lands = [(-0.45, -0.35, 0.35, 0.3), (0.3, -0.45, 0.32, 0.35), (-0.25, 0.45, 0.22, 0.4), (0.45, 0.3, 0.2, 0.2)]
    for y in range(d + 2):
        for x in range(d + 2):
            q = (x - cx) ** 2 + (y - cy) ** 2
            if q <= (r + 1) ** 2:
                img.putpixel((x, y), rgba("ink"))
            if q <= r * r:
                nx, ny = (x - cx) / r, (y - cy) / r
                land = any(((nx - a) / ra) ** 2 + ((ny - b) / rb) ** 2 <= 1 for a, b, ra, rb in lands)
                col = ("sand" if land else "sky")
                if nx + ny > 0.9:
                    col = "tan" if land else "navy"
                if nx + ny < -1.0:
                    col = "white" if land else "cyan"
                img.putpixel((x, y), rgba(col))
    if equator:
        for x in range(2, d):
            if ((x - cx) ** 2) <= r * r and x % 2 == 0:
                img.putpixel((x, cy), rgba("gold"))
    for (lx, ly, col) in pins:
        px_, py_ = round(cx + lx * r), round(cy + ly * r)
        pin = mappin(col)
        paste(img, pin, px_ - pin.width // 2, py_ - pin.height + 1)
    return img


def mappin(col="red"):
    hi = {"red": "rose", "green": "yellow", "pink": "rose", "orange": "gold", "sky": "cyan", "grape": "pink"}.get(col, "white")
    return ascii_sprite("""
.KKK.
KCHCK
KCCCK
.KCK.
..K..
""", {"K": "ink", "C": col, "H": hi})


def continents(w=60, h=34):
    """Two land masses with open sea between them, as in 'places on different continents'."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "sky", "navy")
    dither(img, 1, 1, w - 2, h - 2, "cyan", 2)
    sx, sy = w / 60, h / 34
    a = [(4, 6), (20, 3), (24, 12), (18, 20), (8, 18)]
    b = [(36, 14), (52, 12), (56, 24), (46, 30), (38, 26)]
    for pts in (a, b):
        pts = [(round(x * sx), round(y * sy)) for x, y in pts]
        poly(img, [(x + 1, y + 1) for x, y in pts], "ink")
        poly(img, pts, "sand")
    paste(img, mappin("red"), round(13 * sx), round(6 * sy))
    paste(img, mappin("red"), round(45 * sx), round(17 * sy))
    return img


def compass(r=22, lit="W"):
    """A compass rose: a ring and four points; the point named by lit glows gold, the others are steel."""
    d = 2 * r + 3
    img = blank(d, d)
    c = d // 2
    for y in range(d):
        for x in range(d):
            q = math.hypot(x - c, y - c)
            if r - 2 <= q <= r + 1:
                img.putpixel((x, y), rgba("ink"))
            if r - 1 <= q <= r and (x + y) % 2 == 0:
                img.putpixel((x, y), rgba("ice"))
            elif r - 1 <= q <= r:
                img.putpixel((x, y), rgba("white"))
    dirs = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    for k, (dx, dy) in dirs.items():
        col, sh = ("gold", "orange") if k == lit else ("steel", "slate")
        tip = (c + dx * (r - 3), c + dy * (r - 3))
        side = (-dy, dx)
        pts = [tip, (c + side[0] * 4, c + side[1] * 4), (c - side[0] * 4, c - side[1] * 4)]
        poly(img, pts, "ink")
        poly(img, [tip, (c + side[0] * 3, c + side[1] * 3), (c, c)], col)
        poly(img, [tip, (c - side[0] * 3, c - side[1] * 3), (c, c)], sh)
    disc(img, c, c, 2, "ink"); _P(img, c, c, "white")
    return img


def lonmap(w=150, h=96, pins=(), lit=None):
    """A sea chart with longitude lines: vertical dashed meridians on a pale map, land in sand.
    pins = [(x, y, colour, label)]; lit = index of a meridian to draw in gold (a line of longitude to compare)."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "white", "slate")
    blobs = [(18, 20, 34, 22), (70, 50, 46, 26), (110, 18, 26, 16), (30, 70, 22, 12)]
    for (x, y, a, b) in blobs:
        ellipse(img, x - a // 2 + 1, y - b // 2 + 1, a, b, "steel")
        ellipse(img, x - a // 2, y - b // 2, a, b, "sand")
    n = 6
    for k in range(1, n):
        x = round(k * w / n)
        col = "gold" if lit == k else "ice"
        for y in range(2, h - 2):
            if lit == k or y % 4 < 2:
                img.putpixel((x, y), rgba(col if lit != k else "gold"))
                if lit == k:
                    img.putpixel((x + 1, y), rgba("orange"))
    for (x, y, col, lab) in pins:
        p = mappin(col)
        paste(img, p, x - p.width // 2, y - p.height + 1)
        if lab:
            t = text(lab, "ink", 20)
            paste(img, t, x + 4, y - t.height - 2)
    return img


# ------------------------------------------------------------------------------------------------ fact card
def factcard(lines, w=150):
    """The aqua fact card: both true values printed above the question."""
    ts = [text(l, "deep", 20, maxw=w - 12) for l in lines]
    h = sum(t.height for t in ts) + 4 * (len(ts) - 1) + 12
    img = blank(w, h + 1)
    _rbox(img, 0, 0, w, h, "cyan", "deep")
    rect(img, 1, 1, w - 2, 1, "white")
    rect(img, 1, h - 2, w - 2, 1, "sky")
    y = 6
    for t in ts:
        paste(img, t, 6, y)
        y += t.height + 4
    rect(img, 2, h, w - 3, 1, "ice")
    return img


# ------------------------------------------------------------------------------------------------ kind icons
def icon(name):
    """16x16 icons for the kinds of question: calendar (dates), ruler (sizes), cake (ages), globe (geography)."""
    K = {"K": "ink", "R": "red", "r": "wine", "W": "white", "L": "ice", "G": "gold", "Y": "yellow", "O": "orange",
         "S": "sand", "s": "peach", "P": "pink", "p": "rose", "B": "sky", "b": "navy", "g": "leaf", "D": "steel", "c": "clay"}
    art = {
        "dates": """
...K......K.....
.KKKKKKKKKKKKK..
.KccccccccccccK.
.KccccccccccccK.
.KKKKKKKKKKKKKK.
.KWWWWWWWWWWWWK.
.KWKKWKKWKKWLWK.
.KWWWWWWWWWWWWK.
.KWKKWKKWKKWLWK.
.KWWWWWWWWWWWWK.
.KWKKWKKWLLWLWK.
.KWWWWWWWWWWWWK.
.KLLLLLLLLLLLLK.
..KKKKKKKKKKKK..
""",
        "sizes": """
................
................
................
KKKKKKKKKKKKKKKK
KYYYYYYYYYYYYYYK
KYKYKYKYKYKYKYYK
KYKYYYKYYYKYYYYK
KYKYYYKYYYKYYYYK
KYYYYYYYYYYYYYYK
KGGGGGGGGGGGGGGK
KKKKKKKKKKKKKKKK
................
""",
        "ages": """
......K.........
.....KYK........
.....KOK........
......K.........
.....KWK........
.KKKKKWKKKKKKK..
.KpPpPpPpPpPpK..
.KPPPPPPPPPPPK..
.KSSSSSSSSSSSK..
.KsssssssssssK..
.KSSSSSSSSSSSK..
.KsssssssssssK..
KKKKKKKKKKKKKKK.
""",
        "geography": """
.....KKKKK......
...KKBBBBBKK....
..KBBSSBBBBBK...
.KBBSSSSBBSSBK..
.KBSSSSBBBSSBK..
KBBBSSBBBBBSBBK.
KBBBBBBBBSSBBBK.
KBBBBBBBSSSSBBK.
KBBBBBBBBSSBBbK.
.KBBSBBBBBBBbK..
.KBBBSSBBBBbbK..
..KBBBBBBbbbK...
...KKbbbbbKK....
.....KKKKK......
""",
    }
    return ascii_sprite(art[name].strip("\n").split("\n"), K)


def kindbox(name, label):
    """An icon with its label under it, for the kinds-of-question row."""
    ic = icon(name)
    t = text(label, "ink", 20)
    w = max(ic.width, t.width)
    img = blank(w, ic.height + 3 + t.height)
    paste(img, ic, (w - ic.width) // 2, 0)
    paste(img, t, (w - t.width) // 2, ic.height + 3)
    return img


def sign(s, col="steel"):
    """A small wooden sign on a post, for 'retired'."""
    t = text(s, "white", 20, line=True)
    w, h = t.width + 10, t.height + 6
    img = blank(w, h + 10)
    rect(img, w // 2 - 1, h - 1, 3, 11, "ink"); rect(img, w // 2, h - 1, 1, 10, "clay")
    _rbox(img, 0, 0, w, h, col)
    rect(img, 1, 1, w - 2, 1, "ice")
    paste(img, t, 5, 3)
    return img


def link(w=40, broken=True):
    """A red link line with a cross in the middle: two answers that cannot both be right."""
    img = blank(w, 11)
    for x in range(w):
        if (x // 3) % 2 == 0:
            rect(img, x, 4, 1, 3, "ink"); img.putpixel((x, 5), rgba("red"))
    return img
