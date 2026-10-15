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
def scale(tilt=0, grey=False, plates=True, s=1.0, load=None):
    """A brass balance on a post, drawn natively at size s (0.75 corner, 1 normal, 1.5 when it is the subject).
    tilt -1: the NO pan (left, red) sinks; +1: the YES pan (right, green) sinks; 0: level. The beam end moves by
    14 px per unit of tilt at s=1. load=(left, right): images resting on the pans (the weight); the NO / YES plates
    then hang under the pans. grey=True draws it faint (the lean before the talk names it).
    The canvas does not depend on tilt, so Morph keeps it in place."""
    from sprites.deckui import plate
    pp = 2 if s >= 1 else 1
    pl = [plate("NO", "red", "white", 20, pp), plate("YES", "green", "white", 20, pp)]
    load = tuple(_cargo(c) for c in (load or (None, None)))
    has_load = any(c is not None for c in load)
    sit_h = max([c.height for c in load if c is not None] + ([pl[1].height] if plates and not has_load else [0]))
    sit_w = max([c.width for c in load if c is not None] + [pl[1].width])
    pw = round(11 * s) if not has_load else max(round(11 * s), sit_w // 2 + 3)
    L = round(31 * s) if not has_load else max(round(31 * s), pw + round(8 * s))
    maxdy = round(14 * s)
    dy = round(14 * s * tilt)                       # positive: the right end goes down
    hang = round(18 * s) if not has_load else max(round(18 * s), sit_h + 8)
    top = max(round(12 * s), maxdy + sit_h - hang + 3)
    half = L + max(pw + 1, sit_w // 2 + 1)
    W = 2 * half + 2
    under = (pl[1].height + 6) if (has_load and plates) else 0
    H = max(top + round(60 * s), top + 2 + maxdy + hang + round(5 * s) + under + 2)
    img = blank(W, H)
    cx = W // 2
    bw, bh = round(28 * s), max(4, round(5 * s))
    rect(img, cx - bw // 2, H - bh - 1, bw, bh, "ink"); rect(img, cx - bw // 2 + 1, H - bh, bw - 2, bh - 2, "gold")
    rect(img, cx - bw // 2 + 1, H - bh, bw - 2, 1, "yellow")
    nw = round(18 * s)
    rect(img, cx - nw // 2, H - bh - 4, nw, 4, "ink"); rect(img, cx - nw // 2 + 1, H - bh - 3, nw - 2, 2, "orange")
    pw2 = max(4, round(4 * s))
    rect(img, cx - pw2 // 2, top, pw2, H - bh - 4 - top, "ink")
    rect(img, cx - pw2 // 2 + 1, top, pw2 - 2, H - bh - 4 - top, "gold"); rect(img, cx - pw2 // 2 + 1, top, 1, H - bh - 4 - top, "yellow")
    ends = [(cx - L, top + 2 - dy), (cx + L, top + 2 + dy)]
    th = 1 if s < 1.2 else 2
    for off in range(-th, th + 1):
        line(img, ends[0][0], ends[0][1] + off, ends[1][0], ends[1][1] + off, "ink" if abs(off) == th else "gold")
    r = max(3, round(3 * s))
    disc(img, cx, top + 2, r, "ink"); disc(img, cx, top + 2, r - 1, "orange"); _P(img, cx - 1, top + 1, "yellow")
    for k, (ex, ey) in enumerate(ends):
        py = ey + hang
        sw = round(8 * s) if not has_load else pw - 2
        line(img, ex, ey, ex - sw, py, "slate"); line(img, ex, ey, ex + sw, py, "slate")
        rect(img, ex - pw, py, 2 * pw + 1, 2, "ink"); rect(img, ex - pw + 2, py + 2, 2 * pw - 3, 2, "ink")
        rect(img, ex - pw + 5, py + 4, max(3, 2 * pw - 9), 1, "ink")
        rect(img, ex - pw + 1, py, 2 * pw - 1, 1, "yellow"); rect(img, ex - pw + 3, py + 2, 2 * pw - 5, 1, "gold")
        rect(img, ex - pw + 2, py + 1, 2 * pw - 3, 1, "gold")
        disc(img, ex, ey, 1, "ink")
        c = load[k]
        if c is not None:
            paste(img, c, ex - c.width // 2, py - c.height)
        if plates and has_load:
            p = pl[k]
            rect(img, ex, py + 5, 1, 4, "slate")
            paste(img, p, ex - p.width // 2, py + 9)
        elif plates:
            p = pl[k]
            paste(img, p, ex - p.width // 2, py - p.height)
    return faint(img) if grey else img


def _cargo(name):
    """What rests on a pan, by name: 'geography' a globe; 'others' a calendar and a cake with a ruler on top."""
    if name is None or not isinstance(name, str):
        return name
    if name == "geography":
        return kindicon("geography", 34)
    if name == "others":
        from PIL import Image
        c, k = calendar(24), cake(24)
        r = ruler(30, 10).transpose(Image.ROTATE_90)
        img = blank(c.width + r.width + k.width + 4, max(c.height, k.height, r.height))
        paste(img, c, 0, img.height - c.height); paste(img, r, c.width + 2, img.height - r.height)
        paste(img, k, c.width + r.width + 4, img.height - k.height)
        return img
    return kindicon(name, 32)


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
    """A speech bubble of wrapped pixel text, width w, with a small tail: 'left' or 'right' at the bottom,
    'side' on the right edge pointing right (at the speaker), None for no tail."""
    t = text(s, fg, 20, maxw=None if "\n" in s else w - 10)   # explicit line breaks are kept as written
    h = t.height + 9
    if tail == "lside":                # on the left edge, pointing left (at a speaker standing to its left)
        img = blank(w + 6, h)
        _rbox(img, 6, 0, w, h, bg, edge)
        paste(img, t, 11, 4)
        cy = h // 2
        poly(img, [(6, cy - 4), (6, cy + 3), (0, cy)], edge)
        poly(img, [(7, cy - 3), (7, cy + 2), (3, cy)], bg)
        return img
    if tail == "side":
        img = blank(w + 6, h)
        _rbox(img, 0, 0, w, h, bg, edge)
        paste(img, t, 5, 4)
        cy = h // 2
        poly(img, [(w - 1, cy - 4), (w - 1, cy + 3), (w + 5, cy)], edge)
        poly(img, [(w - 2, cy - 3), (w - 2, cy + 2), (w + 2, cy)], bg)
        return img
    img = blank(w, h + 4)
    _rbox(img, 0, 0, w, h, bg, edge)
    paste(img, t, 5, 4)
    if tail is None:
        return img
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
...KBBBBK...
..KBcWBBBK..
..KBWWBBBK..
..KBBBBBBK..
...KBBBBK...
....KBBK....
....KBBK....
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
    stripe = {"book": "sand", "film": "night", "person": "clay", "place": "brown"}[kind]
    rect(img, 1, 1, w - 2, 4, stripe)
    ic = kind_icon(kind)
    if w >= 30 and h >= 38:          # a large card: the glyph at 2x fills half the face
        from px import scale_int
        ic = scale_int(ic, 2)
        paste(img, ic, (w - ic.width) // 2 + 1, 7)
        rect(img, 4, h - 6, w - 9, 1, "steel")
    else:
        paste(img, ic, (w - ic.width) // 2, 8)
        rect(img, 4, h - 9, w - 8, 1, "steel"); rect(img, 4, h - 6, w - 12, 1, "steel")
    rect(img, w - 2, 2, 1, h - 3, "ice"); rect(img, 2, h - 2, w - 3, 1, "ice")
    if lit:
        img = outline(img, "gold")
    return img


def pip(ans="N", right=True, w=11, h=14):
    """One sampled answer: a small plate with Y or N, green for YES and red for NO, lit top edge; a wrong answer
    gets an ink underline, so right and wrong also read in greyscale."""
    bg, hi = ("green", "yellow") if ans == "Y" else ("red", "rose")
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, bg)
    rect(img, 2, 1, w - 4, 1, hi)
    t = text(ans, "white", 20)
    paste(img, t, (w - t.width) // 2 + 1, (h - t.height) // 2)
    if not right:
        rect(img, 1, h - 2, w - 2, 1, "ink")
    return img


def answer_row(answers, truth, w=11, h=14, gap=1):
    """Ten pips in a row; truth is 'Y' or 'N'."""
    ps = [pip(a, a == truth, w, h) for a in answers]
    img = blank(len(ps) * (w + gap) - gap, h)
    for i, p in enumerate(ps):
        paste(img, p, i * (w + gap), 0)
    return img


def flag(col="gold", h=26):
    """A pennant on a pole: a flagged pair. h: the pole's height (26 small, 44 when it is the subject)."""
    k = h / 26
    w = round(16 * k)
    img = blank(w, h)
    pw = max(3, round(3 * k))
    rect(img, 1, 1, pw, h - 1, "ink"); rect(img, 2, 2, pw - 2, h - 3, "white")
    fx = 1 + pw
    poly(img, [(fx, 1), (w - 1, round(6 * k)), (fx, round(12 * k))], "ink")
    poly(img, [(fx, 3), (w - 4, round(6 * k)), (fx, round(12 * k) - 2)], col)
    line(img, fx, 3, fx + round(6 * k), round(5 * k), "yellow" if col == "gold" else "white")
    rect(img, 0, h - 2, pw + 3, 2, "ink")
    return img


# ------------------------------------------------------------------------------------------------ data and code
def folder(w=58, h=44):
    """The released-data folder: a beige folder with a tab and a few sheets sticking out (no orange: orange is
    our run)."""
    img = blank(w, h)
    _rbox(img, 2, 0, 20, 8, "brown")
    for k, c in enumerate(("white", "ice", "white")):
        _box(img, 6 + k * 6, 3 + k * 2, w - 18, 20, c, "slate")
        for r in range(3):
            rect(img, 9 + k * 6, 7 + k * 2 + r * 4, w - 26, 1, "steel")
    _rbox(img, 0, 12, w, h - 12, "sand")
    rect(img, 1, 13, w - 2, 1, "white"); rect(img, 1, h - 3, w - 2, 2, "clay")
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
    k = w / 58
    rows = [(18, "green"), (30, "ice"), (24, "green"), (34, "ice"), (12, "green"), (28, "ice"), (20, "green"), (32, "ice")]
    n = max(5, (h - 16) // 7)
    for r in range(n):
        L, c = rows[r % len(rows)]
        y = 13 + r * (6 if n == 5 else 7)
        if y + 2 > h - 4:
            break
        rect(img, 8, y, min(round(L * k), w - 14), 2, c)
        rect(img, 4, y, 2, 2, "gold")
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
    """A compass rose: a ring and four points; the point named by lit is dark (ink), the others are steel."""
    d = 2 * r + 3
    img = blank(d, d)
    c = d // 2
    disc(img, c, c, r, "white")                # a light face, so it reads on dark sets
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
        col, sh = ("dusk", "ink") if k == lit else ("steel", "slate")
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


LAKE_A, LAKE_B = (126, 30), (46, 72)       # the two lakes of the 170x100 map, B to the southwest of A
MAP_W, MAP_H = 170, 100


def pin(letter, big=False):
    """A large ink map pin with a white letter (at twice the type size when big); its point is the bottom-centre
    pixel."""
    t = text(letter, "white", 40 if big else 20)
    w, h = (21, 21) if big else (13, 13)
    img = blank(w, h + 5)
    _rbox(img, 0, 0, w, h, "ink", "ink")
    rect(img, 1, 1, w - 2, 1, "slate")
    paste(img, t, (w - t.width) // 2 + 1, (h - t.height) // 2)
    poly(img, [(3, h - 1), (w - 4, h - 1), (w // 2, h + 4)], "ink")
    return img


def _lake(img, cx, cy, rx, ry, seed, water="sky", shade="navy"):
    """An irregular lake: water blue with a 1px cyan glint on its upper left, a darker shade on its lower right,
    an ink waterline and a sand shoreline around it."""
    import random
    r = random.Random(seed)
    wob = [r.uniform(-0.18, 0.18) for _ in range(8)]
    def inside(x, y, pad=0):
        ang = math.atan2(y - cy, x - cx)
        k = 1 + wob[int((ang + math.pi) / (2 * math.pi) * 8) % 8]
        return ((x - cx) / (rx * k + pad)) ** 2 + ((y - cy) / (ry * k + pad)) ** 2 <= 1
    box = [(x, y) for y in range(cy - ry - 6, cy + ry + 7) for x in range(cx - rx - 6, cx + rx + 7)]
    for x, y in box:
        if inside(x, y, 2):
            _P(img, x, y, "sand")
        if inside(x, y, 1):
            _P(img, x, y, "ink")
        if inside(x, y):
            _P(img, x, y, water)
    for x, y in box:
        if inside(x, y) and not inside(x - 1, y - 1):
            _P(img, x, y, "cyan")
        elif inside(x, y) and not inside(x + 1, y + 1):
            _P(img, x, y, shade)
    rect(img, cx - rx // 3, cy - 1, max(3, rx // 3), 1, "cyan")


def lakemap(reading=None, w=MAP_W, h=MAP_H, same=False):
    """The one map of the lake question, reused wherever it appears: pale land, dashed meridians, five lakes,
    lake A and lake B (to A's southwest) under large ink pins. reading: 'due' adds a dashed ink line due west
    from A; 'further' dithers in yellow everything further west than A. Drawn natively at any size."""
    sx, sy = w / MAP_W, h / MAP_H
    A = (round(LAKE_A[0] * sx), round(LAKE_A[1] * sy))
    B = (round(LAKE_B[0] * sx), round((LAKE_A[1] if same else LAKE_B[1]) * sy))   # same: B due west of A
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "white", "ink")
    dither(img, 1, 1, w - 2, h - 2, "ice", 2)
    for k in range(1, 6):
        x = round(k * w / 6)
        for y in range(2, h - 2):
            if y % 4 < 2:
                _P(img, x, y, "ice")
    if reading == "further":
        for yy in range(2, h - 2):
            for xx in range(2, A[0]):
                if (xx + yy) % 2 == 0:
                    _P(img, xx, yy, "yellow")
    lakes = ((A[0], A[1] + round(6 * sy), 15, 7, 1, "sky", "navy"), (B[0], B[1] + round(6 * sy), 17, 8, 2, "sky", "deep"),
             (round(92 * sx), round(66 * sy), 9, 5, 3, "sky", "navy"), (round(150 * sx), round(78 * sy), 8, 6, 4, "sky", "navy"),
             (round(24 * sx), round((78 if same else 24) * sy), 9, 6, 5, "sky", "navy"))
    for (cx, cy, rx, ry, sd, wat, sh) in lakes:
        _lake(img, cx, cy, round(rx * sx), round(ry * sy), sd, wat, sh)
    if reading == "further":
        rect(img, A[0], 2, 2, h - 4, "gold"); rect(img, A[0] + 2, 2, 1, h - 4, "ink")
    elif reading == "due":
        for x in range(4, A[0] - 4):
            if x % 6 < 4:
                rect(img, x, A[1] + 2, 1, 2, "ink")
    for (x, y), lab in ((A, "A"), (B, "B")):
        p = pin(lab, big=w >= 160)
        paste(img, p, x - p.width // 2, y - p.height + 4)
    return img


# ------------------------------------------------------------------------------------------------ board stands
def monitor(w, h=16):
    """The stand of the terminal board: a neck under its middle and a foot on the ground."""
    img = blank(w, h)
    cx = w // 2
    rect(img, cx - 8, 0, 16, h - 4, "ink"); rect(img, cx - 7, 0, 14, h - 4, "dusk"); rect(img, cx - 7, 0, 3, h - 4, "slate")
    rect(img, cx - 30, h - 4, 60, 4, "ink"); rect(img, cx - 29, h - 4, 58, 2, "slate"); rect(img, cx - 29, h - 4, 58, 1, "steel")
    return img


def bench(w, h=16):
    """A wooden lab bench the board stands on, with a flask and a test-tube rack at its left end."""
    img = blank(w, h + 18)
    top = 18
    rect(img, 0, top, w, 5, "ink"); rect(img, 1, top + 1, w - 2, 3, "clay"); rect(img, 1, top + 1, w - 2, 1, "peach")
    for x in (6, w - 12):
        rect(img, x, top + 5, 6, h - 5, "ink"); rect(img, x + 1, top + 5, 4, h - 5, "brown"); rect(img, x + 1, top + 5, 1, h - 5, "clay")
    rect(img, 6, top + h - 6, w - 12, 2, "ink"); rect(img, 7, top + h - 6, w - 14, 1, "brown")
    # flask
    fl = ascii_sprite("""
...KKK...
...KWK...
...KLK...
..KLLLK..
.KLLLLLK.
KGGGGGGGK
KGYGGGGGK
KGGGGGGGK
.KKKKKKK.
""", {"K": "ink", "W": "white", "L": "ice", "G": "green", "Y": "yellow"})
    paste(img, fl, 2, top - fl.height)
    for k, c in enumerate(("cyan", "rose")):
        x = 13 + k * 4
        rect(img, x, top - 12, 3, 12, "ink"); rect(img, x + 1, top - 11, 1, 4, "white"); rect(img, x + 1, top - 7, 1, 6, c)
    return img


def table(w, h=16):
    """The legs of the map table: two wooden legs with a stretcher."""
    img = blank(w, h)
    for x in (10, w - 16):
        rect(img, x, 0, 6, h, "ink"); rect(img, x + 1, 0, 4, h, "brown"); rect(img, x + 1, 0, 1, h, "clay")
    rect(img, 16, h // 2, w - 32, 3, "ink"); rect(img, 16, h // 2 + 1, w - 32, 1, "brown")
    return img


def plinth(w, h=20):
    """A stone block a prop stands on, with room on its face for a label."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "white", "ink")
    rect(img, 1, 1, w - 2, 1, "white"); rect(img, 1, h - 3, w - 2, 2, "ice"); rect(img, w - 3, 2, 2, h - 4, "ice")
    return img


def ribbon(s, fg="ink", bg="yellow"):
    """A small ribbon label with notched ends."""
    t = text(s, fg, 20, line=True)
    w, h = t.width + 14, t.height + 4
    img = blank(w, h)
    rect(img, 0, 0, w, h, "ink"); rect(img, 1, 1, w - 2, h - 2, bg)
    for y in range(h):
        d = 3 - abs(y - h // 2) if abs(y - h // 2) < 3 else 0
        for x in range(d):
            img.putpixel((x, y), (0, 0, 0, 0)); img.putpixel((w - 1 - x, y), (0, 0, 0, 0))
    paste(img, t, 7, 2)
    return img


# ------------------------------------------------------------------------------------------------ big icons
def calendar(w=30):
    """A wall calendar drawn at size w (at least 30 px): clay header with rings, a grid of days, one day marked."""
    h = w + 2
    img = blank(w, h)
    _rbox(img, 0, 3, w, h - 3, "white")
    rect(img, 1, 4, w - 2, max(6, w // 4), "clay"); rect(img, 1, 4, w - 2, 1, "peach")
    rect(img, 1, 4 + max(6, w // 4), w - 2, 1, "ink")
    for rx in (w // 4, 3 * w // 4 - 1):
        rect(img, rx, 0, 2, 7, "ink"); rect(img, rx, 1, 1, 5, "steel")
    gy = 7 + max(6, w // 4)
    cw = (w - 6) // 5
    for r in range(4):
        for c in range(5):
            x, y = 3 + c * cw, gy + r * ((h - gy - 4) // 4)
            if y + 2 < h - 2:
                rect(img, x, y, cw - 2, 2, "steel")
    rect(img, 3 + 3 * cw - 1, gy + (h - gy - 4) // 4 - 1, cw, 4, "red")
    rect(img, 2, h - 2, w - 4, 1, "ice")
    return img


def ruler(w=40, h=14):
    """A yellow ruler with ticks."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "yellow")
    rect(img, 1, h - 3, w - 2, 2, "gold"); rect(img, 1, 1, w - 2, 1, "white")
    for k, x in enumerate(range(3, w - 2, 3)):
        rect(img, x, 1, 1, 6 if k % 5 == 0 else 3, "ink")
    return img


def cake(w=30):
    """A birthday cake with candles (ages)."""
    h = w
    img = blank(w, h)
    bx, by = 2, h // 2
    _box(img, bx, by, w - 4, h - by - 2, "sand")
    rect(img, bx + 1, by + 1, w - 6, 4, "pink"); rect(img, bx + 1, by + 1, w - 6, 1, "rose")
    for x in range(bx + 2, w - 4, 4):
        rect(img, x, by + 5, 2, 2, "pink")
    rect(img, bx + 1, by + (h - by) // 2 + 2, w - 6, 1, "peach")
    rect(img, 0, h - 2, w, 2, "ink"); rect(img, 1, h - 2, w - 2, 1, "steel")
    for k in range(3):
        x = bx + 5 + k * ((w - 14) // 2)
        rect(img, x, by - 7, 3, 7, "ink"); rect(img, x + 1, by - 6, 1, 6, "white")
        _P(img, x + 1, by - 9, "gold"); _P(img, x + 1, by - 10, "yellow"); _P(img, x + 1, by - 8, "orange")
    return img


def kindicon(name, size=32):
    """The kinds of question as large icons (at least 30 px): geography a globe, dates a calendar, sizes a ruler,
    ages a cake."""
    if name == "geography":
        return globe(size // 2 - 1)
    if name == "dates":
        return calendar(size - 2)
    if name == "sizes":
        return ruler(size + 8, max(12, size // 3))
    return cake(size)


def cardback(w=66, h=96):
    """A face-down card: ink border, navy-free dusk back with a gold diamond lattice."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "dusk")
    rect(img, 3, 3, w - 6, h - 6, "night")
    for y in range(5, h - 5):
        for x in range(5, w - 5):
            if (x + y) % 8 == 0 or (x - y) % 8 == 0:
                _P(img, x, y, "slate")
    frame(img, 3, 3, w - 6, h - 6, "steel")
    rect(img, 1, 1, w - 2, 1, "slate")
    return img


def card(w=66, h=110):
    """A face-up card for one of the four things: white face, gold rim."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "white", "ink")
    frame(img, 2, 2, w - 4, h - 4, "sand")
    rect(img, 3, h - 5, w - 6, 2, "ice")
    return img


def deckpile(n=7, kind="place", w=30, h=38):
    """A stack of question cards seen from the front, n cards deep (the whole set, or a part of it)."""
    c = qcard(kind, w, h)
    img = blank(c.width + 2 * n, c.height + 2 * n)
    for k in range(n):
        paste(img, qcard(kind, w, h) if k == n - 1 else faint(c), 2 * (n - 1 - k), 2 * (n - 1 - k))
    return img


def plug(w=40):
    """An unplugged power cord lying on the ground."""
    img = blank(w, 10)
    for x in range(w - 8):
        y = 6 + round(1.5 * math.sin(x / 4))
        rect(img, x, y, 1, 2, "ink")
    _box(img, w - 9, 3, 7, 7, "slate"); rect(img, w - 2, 4, 2, 1, "steel"); rect(img, w - 2, 7, 2, 1, "steel")
    return img


def stand(w, h=10):
    """The two legs of a board standing on the ground line (w: the board's width)."""
    img = blank(w, h)
    for x in (w // 8, w - w // 8 - 4):
        rect(img, x, 0, 4, h - 2, "ink"); rect(img, x + 1, 0, 2, h - 2, "slate"); rect(img, x + 1, 0, 1, h - 2, "steel")
        rect(img, x - 3, h - 2, 10, 2, "ink")
    return img


def truthtab(ans):
    """A small tab with the true answer, for a chat window's title bar."""
    from sprites.deckui import runs
    t = runs([("true: ", "slate"), (ans, "wine" if ans == "NO" else "leaf")])
    img = blank(t.width + 8, t.height + 5)
    _rbox(img, 0, 0, img.width, img.height, "white", "steel")
    paste(img, t, 4, 3)
    return img


# ------------------------------------------------------------------------------------------------ held props
def stick(x0, y0, x1, y1, tip="red"):
    """A long pointer from a hand at (x0, y0) to its tip at (x1, y1), in native pixels. Returns (img, x, y): the
    picture and where its top-left corner goes."""
    pad = 3
    X, Y = min(x0, x1) - pad, min(y0, y1) - pad
    img = blank(abs(x1 - x0) + 2 * pad + 1, abs(y1 - y0) + 2 * pad + 1)
    a, b = (x0 - X, y0 - Y), (x1 - X, y1 - Y)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1)):
        line(img, a[0] + dx, a[1] + dy, b[0] + dx, b[1] + dy, "ink")
    line(img, a[0], a[1], b[0], b[1], "clay")
    rect(img, b[0] - 2, b[1] - 2, 5, 5, "ink"); rect(img, b[0] - 1, b[1] - 1, 3, 3, tip)
    return img, X, Y


def lens_on_stick(hx, hy, cx, cy, r=16):
    """A big magnifying glass: a gold ring of radius r centred on (cx, cy), its handle running to the hand at
    (hx, hy). The glass is a faint tint, so what it looks at stays readable. Returns (img, x, y)."""
    ang = math.atan2(hy - cy, hx - cx)
    ex, ey = round(cx + (r + 1) * math.cos(ang)), round(cy + (r + 1) * math.sin(ang))
    st, sx, sy = stick(hx, hy, ex, ey, tip="clay")
    X, Y = min(sx, cx - r - 3), min(sy, cy - r - 3)
    img = blank(max(sx + st.width, cx + r + 4) - X, max(sy + st.height, cy + r + 4) - Y)
    paste(img, st, sx - X, sy - Y)
    c = (cx - X, cy - Y)
    for y in range(-r - 2, r + 3):
        for x in range(-r - 2, r + 3):
            d = math.hypot(x, y)
            if d <= r - 2.5:
                if (x + y) % 2 == 0 and d > r - 6:
                    img.putpixel((c[0] + x, c[1] + y), rgba("cyan", 70))
            elif d <= r - 1.5:
                _P(img, c[0] + x, c[1] + y, "ink")
            elif d <= r + 0.5:
                _P(img, c[0] + x, c[1] + y, "gold" if x + y > 0 else "yellow")
            elif d <= r + 1.5:
                _P(img, c[0] + x, c[1] + y, "ink")
    return img, X, Y


def swaptile(w=20, h=14):
    """A rank tile as on the ranking board: two models' places as yellow lines that cross, white dots at the ends."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "dusk", "slate")
    a0, a1 = 4, h - 5
    line(img, 3, a0, w - 4, a1, "yellow"); line(img, 3, a1, w - 4, a0, "yellow")
    for (x, y) in ((2, a0 - 1), (2, a1 - 1), (w - 4, a0 - 1), (w - 4, a1 - 1)):
        rect(img, x, y, 2, 3, "white")
    return img


def placard(rows, w=56, scale=None, ticks=(), bh=None):
    """A white sign held in front of the body: rows = [(length in px, 'paper' | 'ours', label or None)].
    Paper's run blue, ours orange, the bars lit on top and shaded on the right, each label at its bar's end. With
    ticks (lengths in px), every sign drawn on the same scale carries the same faint gridlines, so the signs of
    different models compare. bh sets the bar height."""
    from sprites.deckui import say
    hs = bh or (6 if not ticks else 8)
    labs = [say(r[2], "ink") if r[2] else None for r in rows]
    rh = [max(hs, l.height if l is not None else 0) for l in labs]
    h = sum(rh) + 3 * (len(rows) - 1) + 10
    w = max([w] + [4 + max(2, round(r[0])) + 3 + (l.width if l is not None else 0) + 5 for r, l in zip(rows, labs)])
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "white", "ink")
    rect(img, w - 3, 2, 2, h - 4, "ice"); rect(img, 2, h - 3, w - 4, 2, "ice")
    for t in ticks:
        for yy in range(3, h - 3):
            if yy % 3 != 2:
                _P(img, 4 + round(t), yy, "ice")
    if ticks:
        rect(img, 3, 3, 1, h - 6, "ink")          # the common baseline
    y = 5
    for (L, who, _), lab, hh in zip(rows, labs, rh):
        body, hi, lo = ("sky", "cyan", "navy") if who == "paper" else ("orange", "gold", "rust")
        by = y + (hh - hs) // 2
        L = max(2, round(L))
        rect(img, 4, by, L, hs, body); rect(img, 4, by, L, 1, hi); rect(img, 4 + L - 1, by + 1, 1, hs - 1, lo)
        if lab is not None:
            paste(img, lab, 4 + L + 3, y + (hh - lab.height) // 2)
        y += hh + 3
    return img


def flagsign(n, w=50, col="orange"):
    """A sign held in front of the body: a gold flag (flagged pairs) and the count, in our run's orange."""
    from sprites.deckui import say
    f = flag(h=20)
    t = say(str(n), col, 40)
    h = max(f.height, t.height) + 10
    w = max(w, f.width + 6 + t.width + 12)
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "white", "ink")
    rect(img, w - 3, 2, 2, h - 4, "ice"); rect(img, 2, h - 3, w - 4, 2, "ice")
    x = (w - f.width - 6 - t.width) // 2
    paste(img, f, x, (h - f.height) // 2)
    paste(img, t, x + f.width + 6, (h - t.height) // 2)
    return img


def paper(w=56, h=70, col="sky", hi="cyan"):
    """A printed page held up: a coloured title band, text lines and a small bar chart in the same colour."""
    img = blank(w, h)
    _box(img, 0, 0, w, h, "white")
    poly(img, [(w - 9, 0), (w - 1, 8), (w - 9, 8)], "ice")
    line(img, w - 9, 0, w - 9, 8, "ink"); line(img, w - 9, 8, w - 1, 8, "ink")
    rect(img, 4, 4, w - 16, 5, col); rect(img, 4, 4, w - 16, 1, hi)
    for r in range(4):
        rect(img, 4, 14 + r * 4, w - 9 if r % 2 == 0 else w - 16, 1, "steel")
    hs = (16, 6, 10, 3, 13, 5, 8)
    for i, hh in enumerate(hs):
        if 5 + i * 6 + 4 > w - 5:
            break
        rect(img, 5 + i * 6, h - 5 - hh, 4, hh, col); rect(img, 5 + i * 6, h - 5 - hh, 4, 1, hi)
    rect(img, 4, h - 5, w - 8, 1, "ink")
    return img


def divpage(w=50, h=64):
    """The plot's page with a division sign on it: the divisor."""
    img = doc(w, h)
    cx, cy = w // 2, h // 2 - 2
    _box(img, cx - 13, cy - 13, 26, 26, "white")
    rect(img, cx - 9, cy - 1, 18, 3, "navy")
    for dy in (-7, 5):
        rect(img, cx - 2, cy + dy, 4, 4, "navy"); rect(img, cx - 2, cy + dy, 2, 1, "sky")
    return img


def gauge(r=50, used=0.4, stated=0.5, lo=0.3, hi=0.6, post=30, small=False):
    """A cutoff gauge on a post: a half dial from lo (left) to hi (right), a solid blue needle at the value used and
    an outlined (ghost) needle at the value stated, a knob at the right of its base. Returns (img, (cx, cy), tip)
    where tip(v) gives the end of a needle at value v in the picture."""
    import math as _m
    pad = 6
    W_, H_ = 2 * r + 2 * pad + 10, r + pad + post + 6
    img = blank(W_, H_)
    cx, cy = pad + r, pad + r
    ang = lambda v: _m.pi * (1 - (v - lo) / (hi - lo))
    for y in range(-r - 1, 1):
        for x in range(-r - 1, r + 2):
            d = _m.hypot(x, y)
            if d <= r + 1:
                _P(img, cx + x, cy + y, "ink" if d > r - 1 or y == 0 else ("white" if d < r - 7 else "ice"))
    rect(img, cx - r - 1, cy, 2 * r + 3, 3, "ink"); rect(img, cx - r, cy + 1, 2 * r + 1, 1, "slate")
    for k in range(7):
        v = lo + k * (hi - lo) / 6
        a = ang(v)
        r0 = r - (9 if k % 2 == 0 else 5)
        for t in range(r0, r - 1):
            _P(img, cx + round(t * _m.cos(a)), cy - round(t * _m.sin(a)), "ink")
    tip = lambda v, rr=r - 10: (cx + round(rr * _m.cos(ang(v))), cy - round(rr * _m.sin(ang(v))))
    if stated is not None:                 # the ghost needle: an outline only
        ex, ey = tip(stated)
        for off in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            line(img, cx + off[0], cy + off[1], ex + off[0], ey + off[1], "sky")
        line(img, cx, cy, ex, ey, "white")
    if used is not None:
        ex, ey = tip(used)
        for off in ((-1, 0), (0, -1), (-1, -1), (0, 0)):
            line(img, cx + off[0], cy + off[1], ex + off[0], ey + off[1], "navy")
        line(img, cx, cy - 1, ex, ey - 1, "sky")
    disc(img, cx, cy, 4, "ink"); disc(img, cx, cy, 3, "slate"); _P(img, cx - 1, cy - 1, "steel")
    # post, foot and the knob at the right of the base
    rect(img, cx - 3, cy + 3, 7, post, "ink"); rect(img, cx - 2, cy + 3, 5, post, "steel"); rect(img, cx - 2, cy + 3, 1, post, "ice")
    rect(img, cx - 16, H_ - 5, 33, 5, "ink"); rect(img, cx - 15, H_ - 4, 31, 2, "slate"); rect(img, cx - 15, H_ - 4, 31, 1, "steel")
    kx, ky = cx + r + 4, cy - 3
    rect(img, kx - 2, ky, 12, 10, "ink"); rect(img, kx - 1, ky + 1, 10, 8, "steel"); rect(img, kx - 1, ky + 1, 10, 2, "ice")
    for k in range(3):
        rect(img, kx + 1 + k * 3, ky + 3, 1, 6, "slate")
    return img, (cx, cy), tip


def swapcard(w=40, h=30):
    """A rank tile held up: two models' places as yellow lines that cross."""
    img = blank(w, h)
    _rbox(img, 0, 0, w, h, "dusk", "ink")
    rect(img, 2, 2, w - 4, 1, "slate")
    a0, a1 = 6, h - 7
    for off in (0, 1):
        line(img, 5, a0 + off, w - 6, a1 + off, "yellow"); line(img, 5, a1 + off, w - 6, a0 + off, "yellow")
    for (x, y) in ((3, a0 - 1), (3, a1 - 1), (w - 6, a0 - 1), (w - 6, a1 - 1)):
        rect(img, x, y, 3, 4, "white")
    return img


def elbow(pts, col="wine", head=True):
    """A thick arrow along a path of right-angled segments [(x, y), ...] in picture coordinates; the head points
    along the last segment. Returns (img, x, y) placed so the path keeps its coordinates."""
    xs, ys = [p_[0] for p_ in pts], [p_[1] for p_ in pts]
    X, Y = min(xs) - 6, min(ys) - 6
    img = blank(max(xs) - X + 7, max(ys) - Y + 7)
    q = [(x - X, y - Y) for x, y in pts]
    for (x0, y0), (x1, y1) in zip(q, q[1:]):
        rect(img, min(x0, x1) - 2, min(y0, y1) - 2, abs(x1 - x0) + 5, abs(y1 - y0) + 5, "ink")
    for (x0, y0), (x1, y1) in zip(q, q[1:]):
        rect(img, min(x0, x1) - 1, min(y0, y1) - 1, abs(x1 - x0) + 3, abs(y1 - y0) + 3, col)
    if head:
        (x0, y0), (x1, y1) = q[-2], q[-1]
        dx, dy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
        for k in range(6):
            ww = 6 - k
            if dy:
                rect(img, x1 - ww - 1, y1 + dy * k - (1 if dy < 0 else 0), 2 * ww + 3, 1, "ink")
                rect(img, x1 - ww, y1 + dy * k, 2 * ww + 1, 1, col)
            else:
                rect(img, x1 + dx * k, y1 - ww - 1, 1, 2 * ww + 3, "ink")
                rect(img, x1 + dx * k, y1 - ww, 1, 2 * ww + 1, col)
    return img, X, Y
