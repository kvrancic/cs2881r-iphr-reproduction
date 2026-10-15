"""People of the BB Therapeutics deck: the patient (every state of the opening arcade fight and the 1-in-5 row),
his fallen hair, the three founders (bodies and character-select portraits) and the closing camel.

Bodies share the proportions of the builder in sprites/chars.py (32x56 canvas, a 14px head at y 11..25, a 12px
torso at y 25..40, legs to the last row) but are drawn as layered parts: every part (back arm, legs, torso, head,
front arm, held prop) is filled, shaded from the top-left and gets its own 1px ink outline before it is laid over
the parts behind it, so the outer silhouette is always inked for the white ground and overlapping limbs stay
readable. Figures stand in a three-quarter view facing right."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from px import ascii_sprite, blank, paste
from pal import rgba, C

CW, CH = 32, 56
_REV = {v: k for k, v in C.items()}


# ---------------------------------------------------------------- pixel helpers

def _P(img, x, y, col):
    """Set one pixel; col None clears it."""
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((int(x), int(y)), (0, 0, 0, 0) if col is None else rgba(col) if isinstance(col, str) else col)


def _R(img, x, y, w, h, col):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            _P(img, xx, yy, col)


def _A(img, x, y):
    if 0 <= x < img.width and 0 <= y < img.height:
        return img.getpixel((x, y))[3]
    return 0


def _name(img, x, y):
    if 0 <= x < img.width and 0 <= y < img.height:
        r, g, b, a = img.getpixel((x, y))
        return _REV.get((r, g, b)) if a else None
    return None


def _ink(part, col="ink"):
    """The part plus a 1px outline (4-neighbourhood) drawn into its own transparent pixels."""
    out = part.copy()
    src = part.load()
    w, h = part.size
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and src[xx, yy][3]:
                    out.putpixel((x, y), rgba(col))
                    break
    return out


def _lay(base, part, col="ink"):
    base.alpha_composite(_ink(part, col))
    return base


def _seg(img, x0, y0, x1, y1, col, w=3):
    """Thick segment with a square brush of width w (brush anchored so odd widths centre on the line)."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    lo = -((w - 1) // 2)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n)
        y = round(y0 + (y1 - y0) * i / n)
        for dx in range(lo, lo + w):
            for dy in range(lo, lo + w):
                _P(img, x + dx, y + dy, col)


def _rim(part, base, dark, sides=("r", "b")):
    """Shade pixels of colour `base` whose right / bottom neighbour is empty (light comes from the top-left)."""
    src = part.copy()
    for y in range(part.height):
        for x in range(part.width):
            if _name(src, x, y) != base:
                continue
            if ("r" in sides and not _A(src, x + 1, y)) or ("b" in sides and not _A(src, x, y + 1)):
                _P(part, x, y, dark)
    return part


def _hi(part, base, light, sides=("l", "t")):
    src = part.copy()
    for y in range(part.height):
        for x in range(part.width):
            if _name(src, x, y) != base:
                continue
            if ("l" in sides and not _A(src, x - 1, y)) or ("t" in sides and not _A(src, x, y - 1)):
                _P(part, x, y, light)
    return part


def _stamp(img, rows, key, x, y):
    paste(img, ascii_sprite(list(rows), key), x, y)


def _recolor(img, table, default=None):
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in _REV:
                n = table.get(_REV[(r, g, b)], default)
                if n:
                    px[x, y] = C[n] + (a,)
    return out


# ---------------------------------------------------------------- heads
# 15 wide x 13 tall fills, facing right (the ink outline comes from _lay). Face features are drawn afterwards at
# fixed head-local spots: brows row 6, eyes rows 7-8 at cols 8 and 12, nose col 14 row 8, mouth row 10.
# H hair, h hair highlight, d hair shadow, S skin, s skin shade, W scalp shine, G glasses (drawn later).

HEADS = {
    "patient": [
        ".....hhhH......",
        "...hhhHHHHHd...",
        "..hhHHHHHHHHd..",
        ".hHHHHHHHHHHHd.",
        ".hHHHHHHHHHHHHd",
        "hHHHHHHHSHHHHSd",
        "HHHHHHSSSSSSSSS",
        "HHHHsSSSSSSSSS.",
        "HHHssSSSSSSSSSS",
        "dHdssSSSSSSSSS.",
        ".ddssSSSSSSSSs.",
        "..dssSSSSSSSs..",
        "....sssSSSs....",
    ],
    "bald": [
        "...............",
        "....SSSSSSs....",
        "...SWWSSSSSs...",
        "..SWWSSSSSSSs..",
        ".SSWSSSSSSSSSs.",
        ".SSSSSSSSSSSSSs",
        ".SSSSSSSSSSSSSS",
        ".SSSssSSSSSSSS.",
        ".SSssSSSSSSSSSS",
        ".sSssSSSSSSSSS.",
        "..sssSSSSSSSSs.",
        "...ssSSSSSSSs..",
        "....sssSSSs....",
    ],
    "karlo": [   # short dark brown hair, swept up a little at the front
        "..........hH...",
        "....hhhhhHHHd..",
        "..hhHHHHHHHHHd.",
        ".hHHHHHHHHHHHHd",
        ".dHHHHHHHHHHHd.",
        ".dHHHHSSSSSSSSs",
        ".dHHSSSSSSSSSSS",
        ".dHHsSSSSSSSSS.",
        ".dHssSSSSSSSSSS",
        ".sSssSSSSSSSSS.",
        "..sssSSSSSSSSs.",
        "...ssSSSSSSSs..",
        "....sssSSSs....",
    ],
    "luka": [    # dark green baseball cap, brim forward, short dark hair below it
        "....lCCCCC.......",
        "..lCCCCCCCCc.....",
        ".lCCCCCCCCCCc....",
        ".CCCCCCCCCCCCc...",
        "HccccccccccccBBBB",
        "HHHHHSSSSSSSSS...",
        "HHHHSSSSSSSSSSS..",
        "HHHHsSSSSSSSSS...",
        "dHHssSSSSSSSSSS..",
        ".dsssSSSSSSSSS...",
        "..sssSSSSSSSSs...",
        "...ssSSSSSSSs....",
        "....sssSSSs......",
    ],
    "djordje": [  # short dark brown hair
        "...............",
        "....hhhhHHd....",
        "...hhHHHHHHHd..",
        "..hHHHHHHHHHHd.",
        ".hHHHHHHHHHHHHd",
        ".HHHHHHHHSHHHSd",
        ".HHHHSSSSSSSSSS",
        ".HHHsSSSSSSSSS.",
        ".dHssSSSSSSSSSS",
        ".dsssSSSSSSSSS.",
        "..sssSSSSSSSSs.",
        "...ssSSSSSSSs..",
        "....sssSSSs....",
    ],
}
HX, HY = 8, 12    # head origin in the canvas; the head spans x 8..22, y 12..24 (fills)


def _head(who, skin, shade, hair, dx=0, dy=0):
    h, h2, h3 = hair
    key = {"H": h, "h": h2, "d": h3, "S": skin, "s": shade, "W": "white",
           "C": "pine", "c": "deep", "l": "leaf", "B": "deep"}   # Luka's cap
    part = blank(CW, CH)
    _stamp(part, HEADS[who], key, HX + dx, HY + dy)
    if who == "bald":
        _P(part, HX + dx + 4, HY + dy + 2, "white")
    if who == "luka":
        _P(part, HX + dx + 9, HY + dy + 2, "ice")   # the small pale badge on the cap front
    return part


def _face(img, face, dx=0, dy=0, glasses=None, brow="brown", ear="skin2"):
    x0, y0 = HX + dx, HY + dy
    P = lambda x, y, c: _P(img, x0 + x, y0 + y, c)
    # ear: a little C of shade at the side of the head
    if face != "none":
        P(4, 7, ear); P(4, 8, ear); P(3, 8, ear) if _name(img, x0 + 3, y0 + 8) in ("skin", "sand", "skin2") else None
    if glasses == "round":
        # two round dark lenses (the far one narrower in three-quarter view), a bridge and an arm to the ear
        for (x, y) in ((8, 6), (7, 7), (8, 7), (9, 7), (7, 8), (8, 8), (9, 8), (8, 9),
                       (12, 6), (13, 6), (12, 7), (13, 7), (14, 7), (12, 8), (13, 8), (14, 8), (12, 9), (13, 9)):
            P(x, y, "ink")
        P(7, 6, "night"); P(9, 6, "night"); P(7, 9, "night"); P(9, 9, "night")
        P(10, 7, "ink"); P(11, 7, "ink"); P(5, 7, "ink"); P(6, 7, "ink")
        P(7, 7, "slate"); P(12, 7, "slate"); P(8, 7, "dusk")
        if face == "happy":
            P(9, 11, "ink"); P(10, 12, "red"); P(11, 12, "red"); P(12, 11, "ink"); P(10, 11, "white"); P(11, 11, "white")
            P(9, 10, "clay"); P(12, 10, "clay")
        else:
            P(10, 11, "clay"); P(11, 11, "clay"); P(12, 10, "clay")
        return
    if glasses == "sun":
        # dark sporty sunglasses: two lenses joined by a bridge, an arm back to the ear
        for x in (7, 8, 9, 12, 13, 14):
            P(x, 7, "ink"); P(x, 8, "ink")
        P(10, 7, "ink"); P(11, 7, "ink"); P(5, 7, "ink"); P(6, 7, "ink")
        P(7, 7, "slate"); P(12, 7, "slate"); P(8, 7, "dusk")
        if face == "happy":
            P(9, 11, "ink"); P(10, 11, "white"); P(11, 11, "white"); P(12, 11, "ink"); P(10, 12, "red"); P(11, 12, "red")
        else:
            P(10, 11, "clay"); P(11, 11, "clay"); P(12, 11, "clay"); P(9, 11, "clay")
        return
    if face in ("neutral",):
        P(8, 7, "ink"); P(8, 8, "ink"); P(12, 7, "ink"); P(12, 8, "ink")
        P(10, 10, "clay"); P(11, 10, "clay"); P(12, 9, "clay")
        P(13, 9, "rose")
    elif face == "happy":
        P(7, 8, "ink"); P(8, 7, "ink"); P(9, 8, "ink")
        P(11, 8, "ink"); P(12, 7, "ink"); P(13, 8, "ink")
        for x in range(9, 14):
            P(x, 10, "ink")
        P(10, 11, "red"); P(11, 11, "red"); P(12, 11, "red")
        P(9, 11, "ink"); P(13, 11, "ink"); P(10, 12, "ink"); P(11, 12, "ink"); P(12, 12, "ink")
        P(10, 10, "white"); P(11, 10, "white"); P(12, 10, "white")
        P(14, 9, "rose")
    elif face == "queasy":
        P(7, 8, "ink"); P(8, 8, "ink"); P(12, 8, "ink"); P(13, 8, "ink")
        P(7, 7, brow); P(8, 6, brow); P(12, 6, brow); P(13, 7, brow)
        P(9, 11, "pine"); P(10, 10, "pine"); P(11, 11, "pine"); P(12, 10, "pine")
    elif face == "sick":
        P(7, 7, "ink"); P(8, 8, "ink"); P(7, 9, "ink")
        P(13, 7, "ink"); P(12, 8, "ink"); P(13, 9, "ink")
        P(9, 11, "pine"); P(10, 10, "pine"); P(11, 10, "pine"); P(12, 11, "pine"); P(10, 11, "deep"); P(11, 11, "deep")
    elif face == "sad":
        P(8, 8, "ink"); P(8, 9, "ink"); P(12, 8, "ink"); P(12, 9, "ink")
        P(7, 6, brow); P(8, 6, brow); P(12, 6, brow); P(13, 6, brow); P(9, 5, brow); P(11, 5, brow)
        P(9, 11, "brown"); P(10, 10, "brown"); P(11, 10, "brown"); P(12, 11, "brown")
        P(8, 10, "skin2"); P(12, 10, "skin2")   # tired eye bags


# ---------------------------------------------------------------- body parts

TORSO = [   # 12 x 15 at x 10..21, y 26..40: L light, T top, t shade, C collar, M hem, B trousers, b trouser shade
    "..LLTTCCTTt.",
    ".LLTTTTTTTtt",
    ".LTTTTTTTTtt",
    ".LTTTTTTTTtt",
    ".TTTTTTTTTtt",
    ".TTTTTTTTTtt",
    ".TTTTTTTTTtt",
    ".TTTTTTTTTtt",
    ".TTTTTTTTTtt",
    ".TTTTTTTTTtt",
    ".MMMMMMMMMMM",
    ".BBBBBBBBBBb",
    ".BBBBBBBBBBb",
]
TX, TY = 10, 26


def _torso(o, hunch=0):
    top, top2, top3 = o["top"]
    key = {"L": top3 or top, "T": top, "t": top2, "C": o.get("collar", top2), "M": o.get("hem", top2),
           "B": o["bottom"][0], "b": o["bottom"][1]}
    p = blank(CW, CH)
    rows = list(TORSO)
    if hunch:
        # slumped: shoulders drop and the back rounds out behind
        rows = ["............"] * hunch + rows[:2] + rows[2 + hunch:]
        rows[hunch] = "..LTTTCCTTt."
        for i in range(hunch, hunch + 5):
            rows[i] = "L" + rows[i][1:]
    _stamp(p, rows, key, TX, TY)
    return p


def _decor(img, o, hunch=0):
    """Chest details drawn over the inked torso."""
    y = TY + hunch
    if o.get("chest") == "heart":
        for (x, yy) in ((4, 3), (5, 3), (7, 3), (8, 3), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4),
                        (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (5, 6), (6, 6), (7, 6), (6, 7)):
            _P(img, TX + x, y + yy, "red")
        _P(img, TX + 4, y + 3, "rose"); _P(img, TX + 8, y + 5, "wine"); _P(img, TX + 7, y + 6, "wine")
    if o.get("chest") == "hoodie":
        _P(img, TX + 5, y + 1, "white"); _P(img, TX + 5, y + 2, "white"); _P(img, TX + 5, y + 3, "ice")
        _P(img, TX + 8, y + 1, "white"); _P(img, TX + 8, y + 2, "white"); _P(img, TX + 8, y + 3, "ice")
        for x in range(3, 10):
            _P(img, TX + x, y + 6, "leaf")
        _P(img, TX + 3, y + 7, "leaf"); _P(img, TX + 9, y + 7, "leaf"); _P(img, TX + 2, y + 8, "leaf"); _P(img, TX + 10, y + 8, "leaf")
    if o.get("chest") == "polo":
        # polo collar points with a thin peach trim, a short placket with two sand buttons
        for (x, yy) in ((4, 0), (5, 0), (6, 0), (5, 1)):
            _P(img, TX + x, y + yy, "skin")
        for (x, yy) in ((2, 0), (3, 0), (4, 1), (5, 2), (6, 1), (7, 0), (8, 0)):
            _P(img, TX + x, y + yy, "peach")
        _P(img, TX + 5, y + 4, "sand")
    if o.get("chest") == "sweater":
        for x in range(2, 11, 2):
            _P(img, TX + x, TY + 10, "orange")


def _coat(o, legs, hunch=0):
    """Lab coat panels over the torso and hips, open at the front over the shirt."""
    p = blank(CW, CH)
    y0 = TY + hunch
    _R(p, TX + 1, y0, 11, 21 - hunch, "white")
    _R(p, TX, y0 + 1, 1, 6, "white")
    # open front: shirt strip and the trouser gap between the flaps
    _R(p, TX + 6, y0, 2, 9 - hunch, "sky"); _P(p, TX + 7, y0 + 2, "navy"); _P(p, TX + 7, y0 + 5, "navy")
    _R(p, TX + 6, y0 + 9 - hunch, 2, 12, None)
    if legs == "walk":
        _R(p, TX + 1, y0 + 17 - hunch, 3, 4, None)
    _rim(p, "white", "ice", ("r",))
    for yy in range(y0 + 1, y0 + 20):
        _P(p, TX + 5, yy, "ice") if _name(p, TX + 5, yy) == "white" else None
    _P(p, TX + 2, y0 + 11, "ice"); _P(p, TX + 3, y0 + 11, "ice"); _P(p, TX + 4, y0 + 11, "ice")   # pocket
    _P(p, TX + 9, y0 + 3, "sky"); _P(p, TX + 9, y0 + 4, "sky"); _P(p, TX + 9, y0 + 2, "red")     # pen
    return p


LEGS = {   # (back leg points, front leg points), hip to ankle; ankles end at y 51
    "stand": (((13, 41), (13, 46), (13, 51)), ((18, 41), (18, 46), (18, 51))),
    "walk": (((14, 41), (12, 46), (9, 51)), ((17, 41), (20, 46), (22, 51))),
    "wobbly": (((13, 41), (15, 46), (13, 51)), ((18, 41), (20, 46), (18, 51))),
    "bend": (((13, 41), (14, 46), (13, 51)), ((18, 41), (19, 46), (18, 51))),
}


def _leg(pts, o):
    col, col2 = o["bottom"]
    s1, s2 = o["shoe"][:2]
    p = blank(CW, CH)
    for (a, b) in zip(pts, pts[1:]):
        _seg(p, a[0], a[1], b[0], b[1], col, 4)
    _rim(p, col, col2, ("r",))
    ax, ay = pts[-1]
    # shoe: heel at the ankle, toe forward (right); 3 rows ending at y 54
    _R(p, ax - 2, 52, 6, 2, s1); _P(p, ax + 4, 53, s1)
    _R(p, ax - 2, 54, 7, 1, s2)
    if len(o["shoe"]) > 2:
        _P(p, ax - 1, 52, o["shoe"][2])
    return p


# Arms: points from the shoulder to the wrist, back arm first; hands sit beyond the wrist.
ARMS = {
    "down": (((11, 27), (9, 32), (9, 36)), ((20, 27), (22, 32), (22, 36))),
    "walk": (((12, 27), (11, 32), (9, 35)), ((20, 27), (22, 31), (24, 34))),
    "cheer": (((11, 27), (8, 21), (6, 16)), ((20, 27), (24, 21), (26, 16))),
    "carry": (((12, 28), (15, 33), (22, 32), (25, 31)), ((20, 28), (23, 33), (26, 33), (28, 32))),
    "fist": (((11, 27), (7, 25), (6, 20)), ((20, 27), (25, 25), (26, 20))),
    "belly": (((11, 27), (9, 32), (9, 36)), ((20, 27), (22, 32), (17, 34))),
    "clutch": (((11, 27), (9, 32), (13, 35)), ((20, 27), (22, 32), (17, 35))),
    "hold": (((11, 28), (11, 32), (13, 33), (14, 34)), ((20, 28), (23, 31), (23, 33), (21, 34))),
    "limp": (((12, 29), (11, 34), (12, 39)), ((20, 29), (21, 34), (21, 39))),
}


def _arm(pts, o, fist=False, skin="skin", shade="skin2"):
    sl, sl2 = o["top"][:2]
    short = o.get("sleeve") == "short"
    p = blank(CW, CH)
    hand = None
    if len(pts) == 4:
        pts, hand = pts[:3], pts[3]
    segs = list(zip(pts, pts[1:]))
    for i, (a, b) in enumerate(segs):
        if short and i == 1:
            col = skin
        else:
            col = o.get("sleeve_col", sl)
        _seg(p, a[0], a[1], b[0], b[1], col, 3)
    _rim(p, o.get("sleeve_col", sl), o.get("sleeve_col2", sl2))
    _rim(p, skin, shade)
    wx, wy = pts[-1]
    px_, py_ = pts[-2]
    dx = (wx > px_) - (wx < px_)
    dy = (wy > py_) - (wy < py_)
    if o.get("cuff") and not short:
        _seg(p, wx, wy, wx, wy, o["cuff"], 3)
    hx, hy = hand or (wx + dx * 2, wy + dy * 2)
    if fist:
        _R(p, hx - 1, hy - 1, 3, 3, skin); _P(p, hx + 1, hy + 1, shade); _P(p, hx, hy + 1, shade)
    else:
        _R(p, hx - 1, hy - 1, 3, 3, skin); _P(p, hx + 1, hy + 1, None); _P(p, hx + 1, hy, shade); _P(p, hx, hy + 1, shade)
    return p


OUTFITS = {
    "patient": dict(head="patient", hair=("brown", "clay", "plum"), top=("orange", "rust", "gold"), collar="rust",
                    hem="rust", cuff="rust", chest="sweater", bottom=("navy", "dusk"), shoe=("brown", "plum", "clay"),
                    brow="brown"),
    "karlo": dict(head="karlo", hair=("brown", "clay", "plum"), top=("night", "ink", "dusk"), collar="night",
                  hem="ink", sleeve="short", chest="polo", bottom=("dusk", "night"), shoe=("white", "ice")),
    "luka": dict(head="luka", hair=("plum", "brown", "ink"), top=("white", "ice", None), collar="ice", hem="white",
                 sleeve="short", bottom=("navy", "dusk"), shoe=("brown", "plum"), glasses="sun", tache=True),
    "djordje": dict(head="djordje", hair=("plum", "brown", "ink"), top=("night", "ink", "dusk"), collar="ink",
                    hem="ink", cuff="ink", bottom=("dusk", "night"), shoe=("white", "ice"), beard=True),
}


def _hood(o, hdx, hdy):
    p = blank(CW, CH)
    top, top2, top3 = o["top"]
    _stamp(p, ["..TTT.", ".TTTTt", "TTTTtt", "TTTtt.", ".tt..."], {"T": top, "t": top2}, 8 + hdx // 2, 22 + hdy // 2)
    return p


def _body(o, arms="down", legs="stand", hunch=0, face="neutral", hold=None, fist=False):
    img = blank(CW, CH)
    hdx, hdy = (0, 0) if hunch == 0 else (hunch, hunch)
    back, front = ARMS[arms]
    if hunch:
        back = tuple((x + (i > 0), y + hunch) for i, (x, y) in enumerate(back))
        if arms in ("limp", "down"):
            front = tuple((x + (i > 0), y + hunch) for i, (x, y) in enumerate(front))
    front_back = arms in ("hold",)   # both hands in front of the chest: the far arm crosses the torso
    if not front_back:
        _lay(img, _arm(back, o, fist=fist))
    lb, lf = LEGS[legs]
    _lay(img, _leg(lb, o))
    _lay(img, _leg(lf, o))
    if o.get("hood"):
        _lay(img, _hood(o, hdx, hdy))
    _lay(img, _torso(o, hunch))
    _decor(img, o, hunch)
    if o.get("coat"):
        _lay(img, _coat(o, legs, hunch))
    _lay(img, _head(o["head"] if face != "bald" else "bald", "skin", "skin2", o["hair"], hdx, hdy))
    if front_back:
        _lay(img, _arm(back, o, fist=fist))
    return img, hdx, hdy, front


def _bottle(x, y, drug=False):
    """Small white pill bottle, 5x8 fills, top-left at x,y: grey cap, navy label band with a gold stripe
    (Keytruda's colours), or with drug=True the rose label of the new drug (things.pill_bottle label "a")."""
    p = blank(CW, CH)
    _R(p, x, y, 5, 2, "steel"); _R(p, x, y, 4, 1, "ice")
    _R(p, x, y + 2, 5, 6, "white"); _R(p, x + 4, y + 2, 1, 6, "ice")
    band, stripe, edge = ("rose", "white", "red") if drug else ("navy", "gold", "dusk")
    _R(p, x, y + 4, 5, 2, band); _R(p, x + 1, y + 4, 2, 1, stripe); _P(p, x + 4, y + 4, edge); _P(p, x + 4, y + 5, edge)
    return p


# ---------------------------------------------------------------- the patient

PATIENT_STATES = ("normal", "queasy", "sick", "bald", "happy", "grey", "glow")


def patient(state="normal", hold=None):
    st = state if state in PATIENT_STATES else "normal"
    base = "normal" if st in ("grey", "glow") else st
    o = OUTFITS["patient"]
    hunch = {"normal": 0, "queasy": 1, "sick": 2, "bald": 2, "happy": 0}[base]
    arms = {"normal": "down", "queasy": "belly", "sick": "belly", "bald": "limp", "happy": "fist"}[base]
    if hold in ("pill", "drug") and base == "normal":
        arms = "hold"
    legs = {"normal": "stand", "queasy": "stand", "sick": "wobbly", "bald": "bend", "happy": "stand"}[base]
    face = {"normal": "neutral", "queasy": "queasy", "sick": "sick", "bald": "sad", "happy": "happy"}[base]
    img, hdx, hdy, front = _body(o, arms, legs, hunch, "bald" if base == "bald" else face, fist=arms == "fist")
    _face(img, face, hdx, hdy, brow="brown")
    if base in ("queasy", "sick"):
        _green(img, hdx, hdy, base == "sick")
    arm = _ink(_arm(front, o, fist=arms in ("fist", "clutch")))
    if st == "grey":   # the patient fades, the medicine he is sold keeps its colours
        img, arm = _recolor(img, GREY, "steel"), _recolor(arm, GREY, "steel")
    if arms == "hold":
        _lay(img, _bottle(15, 28, drug=hold == "drug"))
        back = _ink(_arm(ARMS["hold"][0], o))
        img.alpha_composite(_recolor(back, GREY, "steel") if st == "grey" else back)
    img.alpha_composite(arm)
    if base == "sick":
        for (x, y) in ((27, 13), (5, 15), (28, 21)):
            _drop(img, x, y)
        for (x, y) in ((9, 44), (23, 44)):   # shaking ticks beside the knees
            _P(img, x, y, "steel"); _P(img, x, y + 2, "steel"); _P(img, x + (1 if x > 16 else -1), y + 1, "steel")
    if st == "glow":
        _sparkle(img, 26, 6)
    return img


def _green(img, hdx, hdy, strong):
    """Queasy: a dithered green tinge over the face. Sick: the whole face is green, leaf in the shade."""
    x0, y0 = HX + hdx, HY + hdy
    if strong:
        for y in range(5, 13):
            for x in range(4, 15):
                n = _name(img, x0 + x, y0 + y)
                if n in ("skin", "skin2"):
                    _P(img, x0 + x, y0 + y, "green" if n == "skin" else "leaf")
        return
    for y in range(5, 13):   # queasy: a checker of green over the face, solid along the jaw
        for x in range(4, 15):
            n = _name(img, x0 + x, y0 + y)
            if n in ("skin", "skin2") and ((x + y) % 2 == 0 or y >= 11):
                _P(img, x0 + x, y0 + y, "green" if n == "skin" else "leaf")


def _drop(img, x, y):
    p = blank(img.width, img.height)
    _P(p, x, y, "sky"); _R(p, x - 1, y + 1, 2, 2, "sky"); _P(p, x - 1, y + 1, "cyan")
    _lay(img, p)


GREY = {"white": "ice", "ice": "ice", "sand": "ice", "skin": "ice", "peach": "ice", "yellow": "ice", "cyan": "ice",
        "gold": "steel", "orange": "steel", "tan": "steel", "skin2": "steel", "clay": "steel", "rose": "steel",
        "sky": "steel", "green": "steel", "steel": "steel", "red": "slate", "rust": "slate", "brown": "slate",
        "navy": "slate", "leaf": "slate", "wine": "slate", "pink": "slate", "slate": "slate", "hot": "slate",
        "plum": "dusk", "dusk": "dusk", "night": "dusk", "pine": "dusk", "deep": "dusk", "grape": "dusk",
        "ink": "ink"}


def _sparkle(img, x, y):
    p = blank(img.width, img.height)
    for d in range(-3, 4):
        _P(p, x + d, y, "gold"); _P(p, x, y + d, "gold")
    for (dx, dy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        _P(p, x + dx, y + dy, "gold")
    _P(p, x, y, "white"); _P(p, x - 1, y, "yellow"); _P(p, x, y - 1, "yellow"); _P(p, x - 2, y, "yellow"); _P(p, x, y - 2, "yellow")
    _P(p, x + 3, y, "orange"); _P(p, x, y + 3, "orange"); _P(p, x + 1, y + 1, "orange")
    _lay(img, p)
    q = blank(img.width, img.height)
    _P(q, x - 4, y + 4, "gold"); _P(q, x + 4, y - 3, "yellow")
    img.alpha_composite(q)


# ---------------------------------------------------------------- hair tufts

TUFTS = [
    "...................hH...",
    "......hH..........H..d..",
    ".....H..d..........d....",
    "......d.................",
    "..........hhHH..........",
    "..hhHHd..hH...Hd....hH..",
    ".hH...Hd.H..hHd.d.hhH.Hd",
    "hH.....d.dHHd...dhd....d",
]


def hair_tufts():
    """Locks of the patient's hair: three curled locks lying on the floor, two still falling. Thin strands with a
    plum dark edge instead of an ink outline, so they read as hair and not as clods. Last row is the floor."""
    rows = [r.ljust(24, ".")[:24] for r in TUFTS]
    return ascii_sprite(rows, {"H": "brown", "h": "clay", "d": "plum"})


# ---------------------------------------------------------------- founders

FOUNDER_POSES = {"stand": ("down", "stand"), "walk": ("walk", "walk"), "cheer": ("cheer", "stand"),
                 "carry": ("carry", "stand")}


def founder(who="karlo", pose="stand"):
    o = OUTFITS.get(who, OUTFITS["karlo"]) if who in ("karlo", "luka", "djordje") else OUTFITS["karlo"]
    arms, legs = FOUNDER_POSES.get(pose, FOUNDER_POSES["stand"])
    face = "happy" if pose == "cheer" else "neutral"
    img, hdx, hdy, front = _body(o, arms, legs, 0, face)
    _face(img, face, hdx, hdy, glasses=o.get("glasses"))
    x0, y0 = HX + hdx, HY + hdy
    P = lambda x, y, c: _P(img, x0 + x, y0 + y, c)
    if o.get("tache"):   # a light moustache and a little stubble on the chin
        for x in (9, 10, 11, 12):
            P(x, 10, "brown")
        P(10, 12, "skin2"); P(12, 12, "skin2")
    if o.get("beard"):   # a short dark beard from the ears round the jaw, the mouth showing through
        for y in range(8, 13):
            for x in range(3, 15):
                n = _name(img, x0 + x, y0 + y)
                if n in ("skin", "skin2", "rose", "clay") and (y >= 10 or x <= 5 or (y == 9 and x >= 9)):
                    _P(img, x0 + x, y0 + y, "plum" if n != "skin2" and (x + y) % 3 else "brown")
        if face == "neutral":   # his easy grin
            for x in (10, 11, 12):
                P(x, 10, "white")
            P(9, 10, "ink"); P(13, 9, "ink")
    _lay(img, _arm(front, o, fist=pose == "cheer"))
    return img


# ---------------------------------------------------------------- portraits (56x56 character-select busts)

def _ell(img, cx, cy, rx, ry, col):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                _P(img, x, y, col)


DIM = {"white": "steel", "ice": "steel", "sand": "steel", "skin": "steel", "peach": "steel", "yellow": "steel",
       "cyan": "steel", "gold": "slate", "orange": "slate", "tan": "slate", "skin2": "slate", "clay": "slate",
       "rose": "slate", "sky": "slate", "green": "slate", "steel": "slate", "red": "slate", "rust": "dusk",
       "brown": "dusk", "navy": "dusk", "leaf": "dusk", "wine": "dusk", "pink": "dusk", "slate": "dusk",
       "hot": "dusk", "plum": "night", "dusk": "night", "night": "night", "pine": "night", "deep": "night",
       "grape": "night", "ink": "ink"}


def portrait(who="karlo", lit=True):
    who = who if who in ("karlo", "luka", "djordje") else "karlo"
    img = blank(56, 56)
    skin, shade = "skin", "skin2"
    # ---- shoulders: the bust is cut flat by the bottom edge (the deck's card frames it)
    base, sh = {"karlo": ("white", "ice"), "luka": ("white", "ice"), "djordje": ("green", "leaf")}[who]
    body = blank(56, 56)
    _ell(body, 28, 61, 26, 20, base)
    _rim_wide(body, base, sh, 3)
    _lay(img, body)
    if who == "djordje":   # the hood bunched round the back of the neck
        hood = blank(56, 56)
        _ell(hood, 28, 43, 14, 5, "green")
        _rim_wide(hood, "green", "leaf", 2)
        _lay(img, hood)
    # ---- neck
    neck = blank(56, 56)
    _R(neck, 22, 32, 12, 13, skin)
    _R(neck, 22, 32, 12, 3, shade)
    _R(neck, 31, 35, 3, 10, shade)
    _lay(img, neck)
    if who == "karlo":   # crew neck and the heart
        c = blank(56, 56)
        _ell(c, 28, 44, 8, 3, "ice")
        _ell(c, 28, 43, 6, 2.5, skin)
        _R(c, 22, 41, 12, 1, None)
        img.alpha_composite(c)
        _heart(img, 34, 48)
    elif who == "luka":   # sky shirt with collar points under an open lab coat
        sh_ = blank(56, 56)
        _poly_fill(sh_, [(20, 42), (36, 42), (31, 56), (25, 56)], "sky")
        _lay(img, sh_)
        col = blank(56, 56)
        _poly_fill(col, [(21, 41), (28, 44), (24, 48)], "sky"); _poly_fill(col, [(35, 41), (28, 44), (32, 48)], "sky")
        _lay(img, col, "navy")
        _P(img, 28, 50, "navy"); _P(img, 28, 54, "navy")
        lap = blank(56, 56)
        _poly_fill(lap, [(14, 42), (21, 42), (27, 56), (12, 56)], "white")
        _poly_fill(lap, [(35, 42), (42, 42), (44, 56), (29, 56)], "white")
        _rim(lap, "white", "ice", ("r",))
        _lay(img, lap)
        _R(img, 35, 51, 5, 1, "ice")                                     # breast pocket
        _R(img, 37, 48, 1, 3, "sky"); _P(img, 37, 47, "navy")            # pen
    else:   # drawstrings
        for x in (25, 31):
            _R(img, x, 45, 1, 6, "white"); _P(img, x, 51, "ice"); _P(img, x, 52, "ice")
    # ---- hair behind the head
    _hair(img, who, back=True)
    # ---- head and ears
    head = blank(56, 56)
    _ell(head, 14, 25, 2.5, 3.5, skin); _ell(head, 42, 25, 2.5, 3.5, skin)
    _ell(head, 28, 21, 13.5, 14, skin)
    _poly_fill(head, [(15, 22), (41, 22), (39, 30), (33, 36), (23, 36), (17, 30)], skin)
    _rim_wide(head, skin, shade, 2)
    for (x, y) in ((13, 24), (13, 25), (13, 26), (42, 24), (42, 25), (42, 26)):
        _P(head, x, y, shade)
    _lay(img, head)
    _hair(img, who, back=False)
    _pface(img, who)
    if not lit:
        img = _recolor(img, DIM, "slate")
    return img


def _poly_fill(img, pts, col):
    from PIL import ImageDraw
    m = blank(img.width, img.height)
    ImageDraw.Draw(m).polygon(pts, fill=rgba(col))
    img.alpha_composite(m)


def _rim_wide(part, base, dark, n=2):
    """Shade a band n px wide on the right / bottom edge of colour `base`."""
    src = part.copy()
    for y in range(part.height):
        for x in range(part.width):
            if _name(src, x, y) != base:
                continue
            if any(not _A(src, x + d, y) for d in range(1, n + 1)) or any(not _A(src, x + d, y + d) for d in range(1, n)):
                _P(part, x, y, dark)


def _heart(img, x, y):
    for (dx, dy) in ((1, 0), (2, 0), (4, 0), (5, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
                     (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
                     (2, 4), (3, 4), (4, 4), (3, 5)):
        _P(img, x + dx, y + dy, "red")
    _P(img, x + 1, y + 1, "rose"); _P(img, x + 5, y + 2, "wine"); _P(img, x + 4, y + 3, "wine"); _P(img, x + 3, y + 4, "wine")


def _hair(img, who, back=False):
    h = blank(56, 56)
    if who == "karlo":   # buzz cut: a short cap hugging the skull, the hairline high on the forehead
        if back:
            return
        _ell(h, 28, 20, 14.5, 14.5, "clay")
        for y in range(56):
            for x in range(56):
                if not _A(h, x, y):
                    continue
                hairline = 12 + max(0, abs(x - 28) - 8)   # recedes towards the temples
                if y > hairline or (y > 20):
                    _P(h, x, y, None)
        src = h.copy()
        for y in range(56):
            for x in range(56):
                if not _A(src, x, y):
                    continue
                if not _A(src, x, y + 1) or not _A(src, x + 1, y) and x > 28:
                    _P(h, x, y, "brown")
                elif y < 10 and x < 28 and (x + y) % 2 == 0 and x + y < 32 and x + y > 26:
                    _P(h, x, y, "peach")
                elif (x % 4 == 1 and y % 4 == 3) or (x % 4 == 3 and y % 4 == 1):
                    _P(h, x, y, "brown")
        _lay(img, h)
    elif who == "luka":   # short dark brown hair, side part on the left, swept to the right
        if back:
            return
        _ell(h, 28, 18, 15.5, 14, "plum")
        for y in range(56):
            for x in range(56):
                if not _A(h, x, y):
                    continue
                fringe = 15 - (x - 15) * 4 // 26          # sweeps up towards the right
                side = 21 if (x <= 16 or x >= 40) else 0
                if y > max(fringe, side):
                    _P(h, x, y, None)
        for (x0, y0, x1, y1) in ((16, 9, 22, 6), (23, 5, 33, 5), (24, 9, 36, 7), (19, 13, 30, 10), (32, 11, 39, 10),
                                 (36, 7, 40, 10)):
            _seg(h, x0, y0, x1, y1, "brown", 1)
        _P(h, 18, 8, "clay"); _P(h, 25, 5, "clay"); _P(h, 26, 8, "clay")
        _seg(h, 21, 5, 19, 10, "ink", 1)         # the parting
        _lay(img, h)
    else:   # black, longer curly hair: curls down to the jaw, a curly fringe
        if back:
            for (cx, cy, r) in ((13, 22, 5), (43, 22, 5), (13, 30, 4.5), (43, 30, 4.5), (15, 36, 3.5), (41, 36, 3.5)):
                _ell(h, cx, cy, r, r, "night")
            _curls(h, ((12, 21), (11, 29), (14, 35), (42, 22), (42, 30), (40, 36)))
            _lay(img, h)
            return
        for (cx, cy, r) in ((28, 9, 7.5), (19, 10, 7), (37, 10, 7), (14, 16, 5), (42, 16, 5), (23, 6.5, 5),
                            (33, 6.5, 5), (16, 12, 5), (40, 12, 5)):
            _ell(h, cx, cy, r, r, "night")
        for (cx, cy, r) in ((20, 14, 3), (25, 14, 3), (30, 14, 3), (35, 14, 3)):   # fringe curls
            _ell(h, cx, cy, r, r, "night")
        _curls(h, ((22, 4), (30, 4), (17, 7), (26, 8), (35, 7), (40, 11), (13, 14), (20, 13), (29, 13), (35, 13),
                   (43, 15), (24, 15)))
        _lay(img, h)


def _curls(h, spots):
    """Each curl: a small dusk C opening to the bottom-right, a slate glint on curls in the top-left light."""
    src = h.copy()
    for (cx, cy) in spots:
        for (dx, dy) in ((0, 0), (1, 0), (2, 0), (-1, 1), (-1, 2), (0, 3)):
            if _A(src, cx + dx, cy + dy):
                _P(h, cx + dx, cy + dy, "dusk")
        if cx + cy < 40 and _A(src, cx, cy):
            _P(h, cx, cy, "slate")
        if _A(src, cx + 1, cy + 2):
            _P(h, cx + 1, cy + 2, "ink")


def _pface(img, who):
    P = lambda x, y, c: _P(img, x, y, c)
    if who == "karlo":
        lens = ["..KKKKK..", ".KnnnnnK.", "KnnnnnnnK", "KnnnnnnnK", "KnnnnnnnK", "KnnnnnnnK", ".KnnnnnK.",
                "..KKKKK.."]
        for x0 in (17, 31):
            _stamp(img, lens, {"K": "ink", "n": "night"}, x0, 19)
            P(x0 + 2, 21, "slate"); P(x0 + 3, 21, "slate"); P(x0 + 2, 22, "steel"); P(x0 + 4, 21, "dusk")
            P(x0 + 6, 24, "dusk"); P(x0 + 5, 25, "dusk")
        _R(img, 26, 21, 5, 1, "ink")
        _R(img, 14, 21, 3, 1, "ink"); _R(img, 40, 21, 3, 1, "ink")
        _R(img, 24, 31, 7, 1, "clay"); P(31, 30, "clay"); P(23, 30, "clay")
    else:
        for cx in (21, 35):
            _R(img, cx - 1, 21, 3, 4, "ink")
            P(cx - 1, 21, "white")
            P(cx + 1, 24, "night")
        brow = "plum" if who == "luka" else "night"
        _R(img, 19, 18, 4, 1, brow); _R(img, 34, 18, 4, 1, brow); P(18, 19, brow); P(38, 19, brow)
        if who == "luka":
            _R(img, 25, 31, 6, 1, "clay"); P(24, 30, "clay"); P(31, 30, "clay")
        else:   # open grin
            _R(img, 24, 30, 9, 1, "ink")
            P(24, 31, "ink"); _R(img, 25, 31, 7, 1, "white"); P(32, 31, "ink")
            P(25, 32, "ink"); _R(img, 26, 32, 5, 1, "red"); P(31, 32, "ink")
            _R(img, 26, 33, 5, 1, "ink")
    # nose and cheeks
    P(29, 24, "skin2"); P(29, 25, "skin2"); P(29, 26, "skin2"); P(28, 27, "clay"); P(29, 27, "skin2")
    for (x, y) in ((17, 28), (18, 28), (38, 28), (39, 28)):
        P(x, y, "rose")


# ---------------------------------------------------------------- the camel

CAMEL_HEAD = [   # fills of the head and ear; inked with the body
    "..B.............",
    ".BBB.BBBBB......",
    ".BBBBBBBBBBB....",
    "..BBBBBBBBBBBB..",
    "..BBBBBBBBBBBBB.",
    ".BBBBBBBBBBBBBB.",
    ".BBBBBBBBBBBBBBB",
    ".BBBBBBBBBBBBBBB",
    ".BBBBBBBBBBBBBBB",
    ".BBBBBBBBBBBBBB.",
    ".BBBBBBBBBBBBB..",
    ".BBBBBBBBBBBB...",
    ".BBBBB..........",
]
HEAD_X, HEAD_Y = 47, 2


def camel(frame=0):
    """A cheerful two-humped camel walking right; frames 0..3 make a walk cycle (contact, passing, contact,
    passing). Peach coat with sand light and clay shade, tan fur on the humps, brown pads, a sky scarf."""
    f = int(frame) % 4
    img = blank(64, 48)
    bob = (0, -1, 0, -1)[f]
    sw = (3, 0, -3, 0)[f]           # stride of the near pair; the far pair swings the other way
    base, light, dark = "peach", "sand", "clay"
    # far legs, behind the body, a shade darker
    for (hx, s_) in ((15, -sw), (36, sw)):
        _lay(img, _camel_leg(hx, 30 + bob, s_, dark, "brown", "brown"))
    # tail
    t = blank(64, 48)
    tw = (0, 1, 0, -1)[f]
    _seg(t, 11, 22 + bob, 9 - tw, 28 + bob, base, 2)
    _R(t, 7 - tw, 28 + bob, 3, 4, "brown"); _P(t, 8 - tw, 32 + bob, "brown")
    _lay(img, t)
    # body, humps, neck, head as one shape
    b = blank(64, 48)
    _ell(b, 26, 26 + bob, 17, 8, base)
    _ell(b, 19, 18.5 + bob, 7.5, 8.5, base)
    _ell(b, 33, 18.5 + bob, 7.5, 8.5, base)
    _seg(b, 39, 25 + bob, 45, 26 + bob, base, 7)
    _seg(b, 46, 25 + bob, 49, 18 + bob, base, 6)
    _seg(b, 49, 18 + bob, 50, 14 + bob, base, 5)
    _stamp(b, CAMEL_HEAD, {"B": base}, HEAD_X, HEAD_Y + bob)
    _rim_wide(b, base, dark, 2)
    _hi(b, base, light, ("t",))
    for (x, y) in ((15, 13), (16, 12), (17, 12), (16, 13), (29, 13), (30, 12), (31, 12), (30, 13), (14, 15), (28, 15)):
        _P(b, x, y + bob, light)
    for (x, y) in ((19, 11), (20, 11), (21, 12), (33, 11), (34, 11), (35, 12), (18, 11), (32, 11)):   # fur on the humps
        _P(b, x, y + bob, "tan")
    _lay(img, b)
    # near legs
    for (hx, s_) in ((19, sw), (40, -sw)):
        _lay(img, _camel_leg(hx, 30 + bob, s_, base, "brown", dark))
    # face: a happy closed eye with a lash, nostril, a smile, a blush
    P = lambda x, y, c: _P(img, HEAD_X + x, HEAD_Y + bob + y, c)
    for (x, y) in ((6, 6), (7, 5), (8, 5), (9, 6)):
        P(x, y, "ink")
    P(10, 5, "ink")
    P(14, 6, "brown")
    for (x, y) in ((10, 8), (11, 9), (12, 9), (13, 9), (14, 8)):
        P(x, y, "brown")
    P(7, 8, "rose"); P(8, 8, "rose")
    # scarf: a band round the neck, the loose end streaming back as it walks
    sc = blank(64, 48)
    y0 = 20 + bob
    _R(sc, 46, y0, 5, 1, "sky"); _R(sc, 45, y0 + 1, 7, 1, "sky"); _R(sc, 45, y0 + 2, 7, 1, "navy")
    _P(sc, 47, y0, "cyan"); _P(sc, 48, y0, "cyan")
    _R(sc, 43, y0 + 1, 3, 3, "sky")                                               # the knot
    sway = (0, 1, 0, -1)[f]
    _seg(sc, 43, y0 + 3, 41 - sway, y0 + 8, "sky", 2)                              # two loose ends
    _seg(sc, 45, y0 + 3, 45 - sway, y0 + 7, "sky", 2)
    _P(sc, 41 - sway, y0 + 9, "cyan"); _P(sc, 42 - sway, y0 + 9, "cyan")
    _P(sc, 45 - sway, y0 + 8, "cyan"); _P(sc, 46 - sway, y0 + 8, "cyan")
    _rim(sc, "sky", "navy", ("r",))
    _lay(img, sc)
    return img


def _camel_leg(hx, hy, s, col, pad, knee):
    p = blank(64, 48)
    kx, ky = hx + (s + (1 if s > 0 else -1 if s < 0 else 0)) // 2, 38
    fx = hx + s
    _seg(p, hx, hy, kx, ky, col, 4)
    _seg(p, kx, ky, fx, 44, col, 3)
    _R(p, kx - 2, ky - 1, 4, 3, col)                 # knobbly knee
    _P(p, kx - 1, ky, knee); _P(p, kx, ky, knee)
    _R(p, fx - 2, 45, 5, 2, pad)                     # wide padded foot
    _P(p, fx + 3, 46, pad)
    return p
