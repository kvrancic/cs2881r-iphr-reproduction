"""Cells: the cast of the biology crash course (slides 3 to 30).
The tumor (a grumpy lumpy blob that later wears a crown), T cells (little soldiers with helmets and spears),
macrophages (white-cell guards in a peaked cap whose uniform shows the side: sky when loyal, red with gold when
bribed), fibroblasts (spindle-shaped builders in hard hats), a germ, and a big close-up guard for the petri dish.
The guard and the builder are ported from the explainer video's pixkit.py so the deck and the video match.
Bodies are shaded procedurally (light from the top-left, hard bands, no gradients), faces are hand-placed.
Every function returns RGBA of its spec size; Endesga 32 only; 1px ink outline on the outer silhouette."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image
from px import blank, paste, ascii_sprite
from pal import rgba, C

_L = (-0.55, -0.65, 0.52)
_n = math.sqrt(sum(v * v for v in _L))
LX, LY, LZ = (v / _n for v in _L)

# ---------------------------------------------------------------- pixel helpers


def _P(img, x, y, col, a=255):
    x, y = int(x), int(y)
    if col and 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), rgba(col, a) if isinstance(col, str) else col)


def _A(img, x, y):
    x, y = int(x), int(y)
    if 0 <= x < img.width and 0 <= y < img.height:
        return img.getpixel((x, y))[3]
    return 0


def _get(img, x, y):
    x, y = int(x), int(y)
    if 0 <= x < img.width and 0 <= y < img.height:
        p = img.getpixel((x, y))
        if p[3]:
            for k, v in C.items():
                if v == p[:3]:
                    return k
    return None


def _R(img, x, y, w, h, col):
    for yy in range(int(y), int(y + h)):
        for xx in range(int(x), int(x + w)):
            _P(img, xx, yy, col)


def _ln(img, x0, y0, x1, y1, col):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        _P(img, x0, y0, col)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def _outline(img, col="ink"):
    """In-place 1px outline on transparent pixels touching opaque ones (4-neighbourhood)."""
    w, h = img.size
    src = img.copy().load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and src[xx, yy][3]:
                    img.putpixel((x, y), rgba(col))
                    break
    return img


FK = {"K": "ink", "W": "white", "I": "ice", "R": "rose", "r": "red", "w": "wine", "P": "plum", "D": "dusk",
      "N": "night", "Y": "yellow", "G": "gold", "O": "orange", "U": "rust", "C": "cyan", "S": "sky", "V": "navy",
      "B": "brown", "g": "green", "l": "leaf", "p": "pine", "s": "steel", "L": "slate", "T": "tan", "A": "sand",
      "E": "peach"}


def _stamp(img, rows, x, y, key=None, mirror=False):
    key = key or FK
    rows = [r for r in rows.strip("\n").split("\n")] if isinstance(rows, str) else rows
    wd = max(len(r) for r in rows)
    for j, r in enumerate(rows):
        r = r.ljust(wd, ".")
        if mirror:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch not in ". ":
                _P(img, x + i, y + j, key[ch])


# ---------------------------------------------------------------- shading


def _xf(px_, py_, ang=0.0, sx=1.0, sy=1.0):
    """Canvas -> shape space: inverse of (scale by sx, sy, then rotate by ang degrees) about (px_, py_)."""
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def f(x, y):
        dx, dy = x - px_, y - py_
        u, v = dx * ca + dy * sa, -dx * sa + dy * ca
        return px_ + u / sx, py_ + v / sy
    return f


def _lobes(lobes):
    """Union of ellipses (cx, cy, rx, ry); each pixel takes the highest lobe; returns shape fn."""
    def f(u, v):
        best = None
        for k, (cx, cy, rx, ry) in enumerate(lobes):
            dx, dy = (u - cx) / rx, (v - cy) / ry
            d2 = dx * dx + dy * dy
            if d2 <= 1.0:
                nz = math.sqrt(1 - d2)
                hgt = nz * min(rx, ry)
                if best is None or hgt > best[4]:
                    best = (dx, dy, nz, k, hgt)
        return best
    return f


def _shade(img, fn, ramp, cuts, xf=None, clip=None, crease=False, light=None):
    """Fill every pixel the shape covers with a ramp colour picked by its lit value. ramp: light -> dark."""
    lx, ly, lz = light or (LX, LY, LZ)
    own = {}
    for y in range(img.height):
        for x in range(img.width):
            if clip and not clip(x, y):
                continue
            u, v = xf(x + 0.5, y + 0.5) if xf else (x + 0.5, y + 0.5)
            r = fn(u, v)
            if r is None:
                continue
            nx, ny, nz, k, hgt = r
            i = nx * lx + ny * ly + nz * lz
            idx = len(cuts)
            for j, c in enumerate(cuts):
                if i > c:
                    idx = j
                    break
            own[(x, y)] = [k, idx, hgt]
    if crease:
        for (x, y), o in own.items():
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = own.get((x + dx, y + dy))
                if q and q[0] != o[0] and q[2] > o[2]:
                    o[1] = min(o[1] + 1, len(ramp) - 1)
                    break
    for (x, y), (k, idx, _) in own.items():
        _P(img, x, y, ramp[min(idx, len(ramp) - 1)])
    return own


def _drop(img, x, y, small=False):
    """A sweat drop, tip up, its own ink edge."""
    if small:
        _stamp(img, """
.K.
KCK
KSK
.K.""", x, y)
    else:
        _stamp(img, """
.K..
KCK.
KWCK
KCSK
.KK.""", x, y)


def _star(img, x, y):
    _stamp(img, """
..K..
.KYK.
KYWYK
.KYK.
..K..""", x, y)


# ======================================================================== TUMOR

TUMOR_LOBES = [(21, 26, 15, 13), (12, 15, 8, 8), (24, 11, 9, 8), (34, 16, 7, 7), (37, 28, 6, 9),
               (7, 29, 6, 8), (30, 33, 9, 6)]
TUMOR_RAMP = ("rose", "red", "wine", "plum")
TUMOR_CUTS = (0.9, 0.55, 0.0)


def _sym(half):
    """Mirror a left half (list of rows) into a symmetric face."""
    rows = [r for r in half.strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    return [r.ljust(w, ".") + r.ljust(w, ".")[::-1] for r in rows]


def _scale_lobes(lobes, s, px_, py_, dx=0, dy=0):
    return [(px_ + (cx - px_) * s + dx, py_ + (cy - py_) * s + dy, rx * s, ry * s) for cx, cy, rx, ry in lobes]


def tumor(mood="grumpy"):
    if mood == "tiny":
        return _tumor_tiny()
    if mood not in ("grumpy", "queasy", "wobble", "panic", "hurt", "king"):
        mood = "grumpy"
    W, H = 44, 40
    img = blank(W, H)
    lobes = TUMOR_LOBES
    xf = None
    fx, fy = 8, 17          # face box origin (20 wide)
    if mood == "panic":
        lobes = _scale_lobes(lobes, 0.86, 22, 39)
        fx, fy = 10, 19
    elif mood == "hurt":
        lobes = _scale_lobes(lobes, 0.8, 22, 39)
        fx, fy = 11, 21
    elif mood == "king":
        lobes = _scale_lobes(lobes, 0.9, 22, 39, dx=3)
        fx, fy = 12, 19
    elif mood == "wobble":
        lobes = _scale_lobes(lobes, 0.9, 22, 39)
        xf = _xf(22, 39, ang=-11, sx=1.05, sy=0.84)
        fx, fy = 9, 21
    _shade(img, _lobes(lobes), TUMOR_RAMP, TUMOR_CUTS, xf=xf, clip=lambda x, y: y <= 38, crease=True)
    if mood == "queasy":
        _queasy(img, fx, fy)
    if mood == "king":
        _shade(img, _lobes([(9, 28, 6, 3.2), (4, 27, 3.2, 2.8)]), TUMOR_RAMP, TUMOR_CUTS,
               clip=lambda x, y: _A(img, x, y) == 0 or x < 12)
        _crown(img, 17, 0)
    if mood == "hurt":
        _wrap(img, 19)
    if mood == "wobble":
        _drop(img, 38, 6); _drop(img, 1, 12, small=True)
    if mood == "panic":
        _drop(img, 1, 8); _drop(img, 39, 6); _drop(img, 6, 1, small=True); _drop(img, 34, 0, small=True)
    _outline(img)
    _tumor_face(img, mood, fx, fy)
    return img


def _queasy(img, fx, fy):
    """Sick green patches: the face goes green around the mouth (dithered rim) and the cheeks puff out."""
    m = {"rose": "green", "red": "green", "wine": "leaf", "plum": "pine"}
    cx, cy = fx + 9.5, fy + 10
    for y in range(img.height):
        for x in range(img.width):
            d = math.hypot((x + 0.5 - cx) / 1.6, y + 0.5 - cy)
            c = _get(img, x, y)
            if c in m and (d < 3.2 or (d < 5 and (x + y) % 2 == 0)):
                _P(img, x, y, m[c])
    for (x0, mirror) in ((fx - 1, False), (fx + 14, True)):
        _stamp(img, """
..KKK.
.KYggK
KgYggK
KgggllK
.KllpK.
..KKK..""", x0, fy + 6, mirror=mirror)


def _crown(img, x, y):
    _stamp(img, """
.K....K....K.
KYK..KYK..KYK
KGK.KYRYK.KGK
KGGKYGGGYKGGK
KYGGGGGGGGGOK
KGRGGYWYGGROK
KOOOOOOOOOOUK
KKKKKKKKKKKKK""", x, y)


def _wrap(img, cy):
    """A head bandage wrapped across the top of the blob, knot and tails on the right."""
    for x in range(img.width):
        col = [y for y in range(img.height) if _A(img, x, y)]
        if not col:
            continue
        top = col[0]
        y0 = max(top, cy - 6 + (x * 3) // 44)
        for y in range(y0, y0 + 4):
            if _A(img, x, y):
                _P(img, x, y, "white" if y < y0 + 2 else "ice")
        _P(img, x, y0 + 4, "steel") if _A(img, x, y0 + 4) else None
    _stamp(img, """
.WW.
WWIW
.II.
.WI.
WI..""", 36, 15)


def _tumor_face(img, mood, fx, fy):
    def S(rows, dx=0, dy=0):
        _stamp(img, rows, fx + dx, fy + dy)
    if mood in ("grumpy", "queasy"):
        if mood == "grumpy":
            S(_sym("""
.KK.......
..KKK.....
...KKKKK..
..KWWWWK..
..KWWWWK..
...KKKK..."""))
            S("KK\nKK", 3, 3); S("KK\nKK", 13, 3)          # pupils looking left
            S("""
.......KKKKKK.......
.....KK.W....KK.....
....K...W......K....""", 0, 8)
        else:
            S(_sym("""
...KK.....
.KK.......
..........
..KKKK....
..KWWK....
...KK....."""))
            S("""
......KKKKKKK.......
.......K..K.........""", 0, 9)
    elif mood == "king":
        S("""
..............KKK...
.KK..........K......
..KKK...............
...KKKKK....KKKKK...
..KKKKKK....KKKKKK..
..KKWWWK....KKWWWK..
...KKKK......KKKK...""")
        S("""
................K...
.......KKKKKKKKK....
........W...........""", 0, 9)
    elif mood == "wobble":
        sp = """
.KKKKK.
K.....K
K.KKK.K
K.K.K.K
K.K...K
K..KKK.
.K....."""
        S(sp, 1, 0); S(sp, 11, 0)
        S("""
......KK..KK..KK....
.....K..KK..KK..K...""", 0, 8)
    elif mood == "panic":
        S(_sym("""
.KK.......
...KK.....
..KKKK....
.KWWWWK...
KWWWWWWK..
KWWWWWWK..
KWWWWWWK..
.KWWWWK...
..KKKK...."""))
        S("K", 3, 5); S("K", 14, 5)
        S("""
.......KKKK.........
......KPPPPK........
.....KPPPPPPK.......
.....KPPRRPPK.......
......KRRRRK........
.......KKKK.........""", 0, 9)
    elif mood == "hurt":
        S(_sym("""
....KK....
..KK......
..........
..KKKK....
..KKKK....
..KWWK....
...KK....."""))
        S("KK", 4, 5); S("KK", 14, 5)
        S("""
.C..................
.CC.................
.C.......KKKK.......
........KRRRRK......
.........KKKK.......""", 0, 6)


def _tumor_tiny():
    img = blank(16, 14)
    lobes = [(8, 9, 6.2, 4.6), (5, 5.5, 3.4, 3.2), (10, 4.5, 3.6, 3.2), (13, 8, 2.6, 3)]
    _shade(img, _lobes(lobes), ("red", "red", "wine", "plum"), TUMOR_CUTS, clip=lambda x, y: y <= 12, crease=True)
    _outline(img)
    _stamp(img, """
K....K
.K..K.
WK..KW
......
.KKKK.
K....K""", 4, 5)
    return img


# ======================================================================== T CELL

TC_RAMP = ("cyan", "sky", "sky", "navy")
TC_CUTS = (0.86, 0.3, -0.3)


def _helmet(img, cx, cy, rx, ry, ang=0.0, brim=2, ramp=("white", "sky", "navy", "dusk"), rim="night", face=1,
            cuts=(0.93, 0.7, -0.15)):
    """A dome hat above the rim line through (cx, cy), tilted by ang degrees (+ = towards the face side),
    with a rim and a brim sticking out on the face side. face: 1 = faces right, -1 = faces left."""
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)       # up (in face-right space)
    fx, fy = math.cos(a), math.sin(a)        # forward
    pts = {}
    R = max(rx, ry) + brim + 3
    for y in range(int(cy - R), int(cy + R + 1)):
        for x in range(int(cx - R), int(cx + R + 1)):
            dx, dy = (x + 0.5 - cx) * face, y + 0.5 - cy
            up = dx * ux + dy * uy
            fw = dx * fx + dy * fy
            if up >= 0 and (fw / rx) ** 2 + (up / ry) ** 2 <= 1:
                nx, ny = fw / rx * face, -up / ry
                nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
                i = nx * LX + ny * LY + nz * LZ
                k = len(cuts)
                for j, c in enumerate(cuts):
                    if i > c:
                        k = j
                        break
                pts[(x, y)] = ramp[min(k, len(ramp) - 1)]
            elif -1.6 <= up < 0 and -rx - 0.6 <= fw <= rx + brim:
                pts[(x, y)] = rim
    for (x, y), c in pts.items():
        _P(img, x, y, c)
    return pts


TC_EYES = {
    "det": ("WWW\nWKK\nWKK\nWWW", "WWW\nWKK\nWKK\nWWW"),
    "fierce": ("K...\n.KK.\n.WKK\n.WKK", "..K\nKK.\nWKK\nWKK"),
    "wide": ("WWW\nWWW\nWKW\nWWW", "WWW\nWWW\nWKW\nWWW"),
    "closed": ("K..K\n.KK.", "K..K\n.KK."),
    "shut": ("...\n...\nKKK", "...\n...\nKKK"),
    "happy": (".KK.\nK..K", ".KK.\nK..K"),
    "x": ("K.K\n.K.\nK.K", "K.K\n.K.\nK.K"),
    "bored": ("KKK\nWKK\nWKK", "KKK\nWKK\nWKK"),
    "puzzled": ("...\nKKK\n...", "WWW\nWWW\nWKK\nWKK"),
}
TC_MOUTH = {"line": "KK", "smile": "K..K\n.KK.", "shout": "KKK\nKRK\n.K.", "o": ".K.\nK.K\n.K.", "flat": "KKK",
            "wavy": "K.K.\n.K.K", "grin": "KKKK\nKRRK\n.KK.", "small": "KK\nKK"}


def _spear(img, x0, y0, x1, y1):
    """Shaft from (x0, y0) to the tip at (x1, y1): brown shaft, steel leaf blade."""
    _ln(img, x0, y0, x1, y1, "brown")
    L = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    px_, py_ = -uy, ux
    for t, w in ((0, 0), (1, 1), (2, 1), (3, 0)):
        for s in range(-w, w + 1):
            _P(img, x1 - ux * t + px_ * s, y1 - uy * t + py_ * s, "steel" if s >= 0 else "ice")
    _P(img, x1, y1, "white")


TC_POSES = {
    # body (cx, cy, rx, ry); helm (cx, rim y, rx, ry, tilt); eyes/mouth (kind, x, y); boots; hands; spear (x0, y0, tip x, tip y)
    "stand":   dict(body=(10, 14.5, 7.2, 7), helm=(9.5, 8.5, 6.8, 5, 0), eyes=("det", 9, 11), mouth=("line", 14, 17),
                    boots=[(5, 21), (11, 21)], hands=[(17, 14)], spear=(19, 22, 19, 1)),
    "alert":   dict(body=(10, 12.5, 6.8, 7.4), helm=(9, 4.5, 6.6, 4.8, -14), eyes=("wide", 9, 8), mouth=("o", 13, 14),
                    boots=[(4, 19), (12, 19)], hands=[(17, 8)], spear=(15, 21, 20, 1), lines=True),
    "march":   dict(body=(10, 14, 7.2, 7), helm=(9.5, 8, 6.8, 5, 0), eyes=("det", 9, 11), mouth=("smile", 13, 16),
                    boots=[(3, 21), (13, 20)], hands=[(15, 16)], spear=(18, 19, 2, 2), spear_behind=True),
    "charge":  dict(body=(10, 15, 7.2, 6.6), helm=(11, 9, 6.8, 4.8, 12), eyes=("fierce", 9, 12), mouth=("shout", 14, 17),
                    boots=[(1, 21), (12, 21)], hands=[(8, 19)], spear=(0, 20, 21, 20)),
    "sit":     dict(body=(9, 16.5, 7.2, 6.6), helm=(8.5, 10.5, 6.8, 5, 0), eyes=("bored", 8, 13), mouth=("flat", 12, 18),
                    boots=[(13, 21), (16, 20)], hands=[(1, 18)], spear=(0, 22, 21, 22), spear_behind=True),
    "doze":    dict(body=(9, 16.5, 7.2, 6.6), helm=(10, 11.5, 6.8, 5, 24), eyes=("closed", 8, 13), mouth=("small", 13, 19),
                    boots=[(13, 21), (16, 20)], hands=[(1, 18)], spear=(0, 22, 21, 22), spear_behind=True, bubble=(16, 15)),
    "sleep":   dict(body=(11, 18, 8.6, 5.4), helm=(4.5, 13, 6.4, 4.8, -45), eyes=("closed", 10, 15), mouth=("smile", 16, 19),
                    boots=[(16, 21), (18, 19)], hands=[], spear=(0, 22, 21, 22), spear_behind=True),
    "bonk":    dict(body=(10, 15, 7.2, 7), helm=(8, 6.5, 6.8, 5, -32), eyes=("x", 9, 12), mouth=("wavy", 13, 17),
                    boots=[(4, 21), (12, 20)], hands=[(1, 12), (17, 10)], spear=(13, 22, 21, 9), spear_behind=True,
                    stars=[(15, 0), (0, 2)]),
    "puzzled": dict(body=(10, 14.5, 7.2, 7), helm=(9.5, 8.5, 6.8, 5, -8), eyes=("puzzled", 9, 11), mouth=("wavy", 12, 17),
                    boots=[(5, 21), (11, 21)], hands=[(15, 3), (1, 14)], spear=(2, 22, 2, 1), spear_behind=True),
    "cheer":   dict(body=(10, 14, 7.2, 7), helm=(9.5, 8, 6.8, 5, 0), eyes=("happy", 8, 12), mouth=("grin", 12, 15),
                    boots=[(4, 20), (12, 20)], hands=[(18, 5), (1, 7)], spear=(19, 14, 19, 0)),
}


def _tc_draw(p):
    img = blank(22, 24)
    if p.get("spear") and p.get("spear_behind"):
        _spear(img, *p["spear"])
    for (bx_, by_) in p["boots"]:
        _R(img, bx_, by_, 4, 2, "navy"); _P(img, bx_, by_, "sky")
    bx, by, rx, ry = p["body"]
    _shade(img, _lobes([(bx, by, rx, ry)]), TC_RAMP, TC_CUTS)
    # receptor bumps on the back and bottom of the cell
    for ang in (160, 205, 250):
        a = math.radians(ang)
        _P(img, round(bx + math.cos(a) * (rx + 0.5) - 0.5), round(by - math.sin(a) * (ry + 0.5) - 0.5), "sky")
    hl = blank(22, 24)
    _helmet(hl, *p["helm"], ramp=("white", "sky", "navy", "dusk"), cuts=(0.95, 0.66, -0.2))
    _outline(hl)
    img.alpha_composite(hl)
    if p.get("spear") and not p.get("spear_behind"):
        _spear(img, *p["spear"])
    for (hx, hy) in p["hands"]:
        _R(img, hx, hy, 2, 2, "sky")
    if p.get("bubble"):
        _stamp(img, ".CC.\nCWCC\nCCCC\n.CC.", *p["bubble"])
    _outline(img)
    e, ex, ey = p["eyes"]
    _stamp(img, TC_EYES[e][0], ex, ey); _stamp(img, TC_EYES[e][1], ex + 4, ey)
    m, mx, my = p["mouth"]
    _stamp(img, TC_MOUTH[m], mx, my)
    for (sx, sy) in p.get("stars", []):
        _star(img, sx, sy)
    if p.get("lines"):
        for x in (5, 9, 13):
            _P(img, x, 22, "steel"); _P(img, x, 23, "steel")
    return img


def tcell(pose="stand"):
    return _tc_draw(TC_POSES.get(pose, TC_POSES["stand"]))


# ======================================================================== GERM


def germ():
    """A small green germ with spikes and a worried face."""
    return ascii_sprite("""
.l..K...l.
..K.K..K..
...KKKKK..
.KKYgggKK.
lKgWggWgKl
.KgKggKgK.
.KggggglK.
lKgKKKllKl
..KKllKK..
.K..K..K..""".strip("\n").split("\n"), {"K": "ink", "g": "green", "Y": "yellow", "W": "white", "l": "leaf"})


# ======================================================================== GUARD (macrophage)
# Ported from the explainer video's guard() (explainer/src/pixkit.py) so the deck and the video are one world:
# a smooth ruffled blob, clean cel shading, a peaked guard cap, nub arms, dot eyes. The body is a neutral pale
# cell (never the tumor's wine lobes, never the T cells' blue). The uniform shows whose side it is on: a belt and
# shoulder strap, sky for the loyal guard, red plus gold coins for the bribed one.

GUARD_RAMP = ("white", "white", "ice", "steel")
UNIFORM = {"sky": ("cyan", "sky", "navy"), "red": ("rose", "red", "wine")}
WOBBLE = ((0.045, 7, 0.3), (0.03, 11, 1.7))
GUARD_MOODS = ("idle", "chomp", "grin", "stop", "bribe")


def _emask(w, h, cx, cy, rx, ry, wobble=None):
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx + 0.5 - cx) / rx
    v = (yy + 0.5 - cy) / ry
    r = np.sqrt(u * u + v * v)
    if wobble:
        th = np.arctan2(v, u)
        return r <= 1 + sum(a * np.sin(k * th + p) for a, k, p in wobble)
    return r <= 1.0


def _cel(mask, ramp, cx, cy, rx, ry, spec=True, rim=2, deep=1):
    """The explainer's cel shading: base colour, a shadow rim bottom-right (rim px), a deeper edge (deep px),
    a highlight blob top-left and a 3px specular glint. Close-ups pass a wider rim."""
    h, w = mask.shape
    out = np.zeros((h, w, 4), np.uint8)
    out[mask] = rgba(ramp[1])
    sh = np.zeros_like(mask)
    sh[:-rim, :-rim] = mask[rim:, rim:]
    out[mask & ~sh] = rgba(ramp[2])
    sh1 = np.zeros_like(mask)
    sh1[:-deep, :-deep] = mask[deep:, deep:]
    yy, xx = np.mgrid[0:h, 0:w]
    out[mask & ~sh1 & ((xx - cx) / rx + (yy - cy) / ry > 0.45)] = rgba(ramp[3])
    hl = _emask(w, h, cx - rx * 0.38, cy - ry * 0.42, rx * 0.42, ry * 0.30) & mask
    hl2 = np.zeros_like(mask)
    hl2[2:, 2:] = mask[:-2, :-2]
    out[hl & hl2] = rgba(ramp[0])
    if spec:
        sx, sy = int(cx - rx * 0.55), int(cy - ry * 0.55)
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            if 0 <= sy + dy < h and 0 <= sx + dx < w and mask[sy + dy, sx + dx]:
                out[sy + dy, sx + dx] = rgba("white")
    return Image.fromarray(out, "RGBA")


def _volume(mask, cx, cy, rx, ry):
    """Close-up shading for the white guard: sphere-lit bands white, white/ice checker, ice, steel, slate."""
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    u, v = (xx + 0.5 - cx) / rx, (yy + 0.5 - cy) / ry
    z = np.sqrt(np.clip(1 - u * u - v * v, 0.04, 1))
    n = np.stack([u, v, z], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    I = n @ np.array([LX, LY, LZ])
    chk = (xx + yy) % 2 == 0
    out = np.zeros((h, w, 4), np.uint8)
    out[mask] = rgba("slate")
    out[mask & (I > -0.62)] = rgba("steel")
    out[mask & (I > -0.25)] = rgba("ice")
    out[mask & (I > 0.12) & chk] = rgba("white")
    out[mask & (I > 0.4)] = rgba("white")
    return Image.fromarray(out, "RGBA")


def _uniform(img, mask, color, y0, hgt, strap, sw):
    """Belt across the body (rows y0..y0+hgt-1, body pixels only) and a shoulder strap from strap[0] to strap[1]."""
    hi, mid, lo = UNIFORM[color]
    xs = [x for x in range(img.width) if mask[y0, x]]
    x0, x1 = xs[0], xs[-1]
    (ax, ay), (bx, by) = strap
    n = max(abs(bx - ax), abs(by - ay))
    for i in range(n + 1):
        x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
        for d in range(sw):
            xx, yy = int(round(x)) + d, int(round(y))
            if mask[yy, xx]:
                _P(img, xx, yy, lo if d == sw - 1 else mid)
    for y in range(y0, y0 + hgt):
        for x in range(x0, x1 + 1):
            if mask[y, x]:
                c = lo if (y == y0 + hgt - 1 or x > x1 - (x1 - x0) // 6) else (hi if (y == y0 and x < x0 + (x1 - x0) // 3) else mid)
                _P(img, x, y, c)


def _coin_pile(img, pts):
    for (x, y) in pts:
        _stamp(img, ".KKK.\nKYGGK\nKGGOK\n.KKK.", x, y)


def _sack(img, x, y):
    """A small gold money sack: cloth ears tied with a brown string, a $ mark."""
    _stamp(img, """
..KK..KK....
..KYKKGK....
...KYGK.....
...KBBK.....
..KGYGGK....
.KGYGGGGK...
KGYGGUGGOK..
KGYGUUUGOK..
KGGGUGGGOK..
KGGGUUUGOK..
KGGGGGUGOK..
.KGGUUUOK...
..KKKUKKK...""", x, y)


CAP = """
....KKKKKKKKKKKK..
...KLLLLDDDDDDDDK.
...KDNNNNNNNNNNNDK
..KKDDDDGDDDDDDDKK
.KNNNNNNNNNNNNNNNK
KKKKKKKKKKKKKKKKK."""


def macrophage(mood="idle", color="sky"):
    mood = mood if mood in GUARD_MOODS else "idle"
    color = color if color in UNIFORM else "sky"
    W, H = 40, 44
    cx, cy, rx, ry, ar = 22.0, 28.5, 13.5, 13.0, 3.6
    m = _emask(W, H, cx, cy, rx, ry, WOBBLE)
    m |= _emask(W, H, cx + rx, cy + 2, ar * 0.95, ar * 0.85)                          # back arm on the hip
    front = {"idle": (cx - rx - ar * 0.2, cy + 2), "grin": (cx - rx - ar * 0.2, cy + 2),
             "chomp": (cx - rx - ar * 0.1, cy - 2), "bribe": (cx - rx + 0.5, cy + 5)}.get(mood)
    if front:
        m |= _emask(W, H, front[0], front[1], ar, ar * 0.85)
    m[H - 1:, :] = False
    img = blank(W, H)
    img.alpha_composite(_cel(m, GUARD_RAMP, cx, cy, rx, ry))
    _uniform(img, m, color, 34, 4, ((27, 34), (31, 17)), 3)
    _outline(img)
    if mood == "stop":
        # arm held straight out at the soldiers, hand up, palm towards them: halt. Own outline, in front.
        arm = blank(W, H)
        _R(arm, 4, 26, 10, 3, "white"); _R(arm, 4, 28, 10, 1, "ice")
        _stamp(arm, """
.WWW.
WWWWW
WWWWW
WWWWWI
WWWWWI
WWWWI.
WWWWI.
WWWWI.
.WWI..
.WWI..
.WII..""", 1, 18, key={"I": "ice", "W": "white"})
        _outline(arm)
        _stamp(arm, "K\nK\nK", 3, 18); _stamp(arm, "K\nK", 5, 18)     # fingers held together, flat
        img.alpha_composite(arm)
    _stamp(img, CAP, int(cx) - 10, 11)
    _guard_face(img, mood, int(cx) - 2, 22, color)
    if mood == "chomp":
        paste(img, germ(), 3, 26)
    if mood == "bribe":
        _sack(img, 0, 30)
    if color == "red" and mood != "bribe":
        _coin_pile(img, ((28, 37), (31, 39), (34, 38)))
    return _sit(img, m)


def _sit(img, mask):
    """Drop the drawing so the body's base outline lands on the last row."""
    dy = img.height - 2 - int(np.where(mask.any(1))[0][-1])
    out = blank(*img.size)
    out.alpha_composite(img, (0, dy))
    return out


def _guard_face(img, mood, fx, ey, color):
    """Explainer-style dot eyes (2x4 ink with a white glint), brows, and a mouth per mood. fx = face centre."""
    L, R = fx - 4, fx + 2

    def eye(x0, lid=0, gx=0, gy=0):
        for yy in range(4):
            for xx in range(2):
                _P(img, x0 + xx, ey + yy, "steel" if yy < lid else "ink")
        _P(img, x0 + gx, ey + lid + gy, "white")

    S = lambda rows, x, y: _stamp(img, rows, x, y)
    if mood == "idle":
        eye(L); eye(R)
        S("KK.\n..K", L - 1, ey - 3); S(".KK\nK..", R, ey - 3)
        S("KKKKK", fx - 3, ey + 7)
    elif mood in ("grin", "bribe"):
        if mood == "grin":
            eye(L, 1, 1); eye(R, 1, 1)                        # eyes slid to the side
            S("KKK", L - 1, ey - 1); S("..K\nKK.", R, ey - 3)
        else:
            eye(L, 1, 0, 2); eye(R, 1, 0, 2)                  # eyes on the sack
            S("KKK", L - 1, ey - 1); S("KKK", R, ey - 1)
        S("""
K........K
.KKKKKKKK.
.KWWIWWIK.
..KKKKKK..""", fx - 5, ey + 5)
    elif mood == "stop":
        eye(L, 2, 1); eye(R, 2, 1)
        S("KKK", L - 1, ey + 1); S("..K\nKK.", R, ey - 3)
        S(".....K\nKKKKK.", fx - 3, ey + 6)
    elif mood == "chomp":
        S("K..\n.K.\nK..", L - 1, ey); S("..K\n.K.\n..K", R, ey)
        S("""
.KKKKKKKKKK.
KWIWWIWWIWWK
KNNNNNNNNNNK
KNNNNNNNNNNK
KNNNNNRRRNNK
KWIWWIWWIWWK
.KKKKKKKKKKK""", fx - 7, ey + 4)
    if color == "red":
        S("RR", L - 2, ey + 5); S("RR", R + 2, ey + 5)


# ======================================================================== FIBROBLAST (wall builder)
# Ported from the explainer's builder(): an upright spindle cell on a pointed foot, cel shaded in sand/peach/
# tan/clay, a yellow hard hat, dot eyes with a focused brow, a trowel.

FIB_RAMP = ("sand", "peach", "tan", "clay")
HAT = """
...KKKKKKK...
..KYYWGGGGK..
.KYYYGGGGOOK.
KKKKKKKKKKKKK
KYGGGGGGGGOOK
.KKKKKKKKKKK."""
TROWEL_UP = """
.KKKK.
KWWssK
KWsssK
.KsLK.
..KK..
..KBK.
..KBK.
...KK."""
TROWEL_DOWN = "\n".join(TROWEL_UP.strip("\n").split("\n")[::-1])


def _brick(img, x, y, w=13):
    rows = ["K" * w,
            "K" + "A" * (w - 3) + "EK",
            "K" + "A" + "E" * (w - 4) + "TK",
            "K" + "T" * (w - 2) + "K",
            "K" + "T" * (w - 3) + "BK",
            "K" * w]
    _stamp(img, rows, x, y)


FIB_POSES = {
    #        body cx, cy, rx, ry, lean; front nub; back nub (cx, cy, rx, ry)
    "idle":  dict(body=(20, 12, 5.6, 8, 0.0), front=(13.5, 10, 2.2, 1.9), back=(26.3, 14, 2.2, 1.9),
                  trowel=(7, 3, TROWEL_UP), hat_y=2),
    "carry": dict(body=(18, 13.5, 5.8, 7, 0.0), front=(10.5, 7.5, 1.9, 2.8), back=(25.5, 7.5, 1.9, 2.8),
                  brick=(9, 0, 19), hat_y=5),
    "lay":   dict(body=(23, 12, 5.6, 8, 0.45), front=(11, 16, 2.2, 1.9), back=(29, 15, 2.2, 1.9),
                  trowel=(5, 13, TROWEL_DOWN), hat_y=2, set_brick=(0, 18)),
}


def fibroblast(pose="idle"):
    p = FIB_POSES.get(pose, FIB_POSES["idle"])
    W, H = 36, 24
    cx, cy, rx, ry, lean = p["body"]
    base = cy + ry
    yy, xx = np.mgrid[0:H, 0:W]
    xs = xx + 0.5 - cx - lean * (yy + 0.5 - base)
    v = (yy + 0.5 - cy) / ry
    half = rx * np.clip(1 - np.abs(v) ** 1.7, 0, 1) ** 0.7
    m = (np.abs(xs) <= half) & (np.abs(v) <= 1)
    m |= (np.abs(xs - (yy - cy - ry) * 0.25) <= 0.8) & (yy >= cy + ry - 2) & (yy < cy + ry + 3)
    for key in ("front", "back"):
        m |= _emask(W, H, *p[key])
    m[H - 1:, :] = False
    shift = lambda y: int(round(lean * (y + 0.5 - base)))     # sheared x offset at row y
    img = blank(W, H)
    if p.get("set_brick"):
        bx, by = p["set_brick"]
        _R(img, bx + 1, by + 1, 9, 4, "sand")
    img.alpha_composite(_cel(m, FIB_RAMP, cx + shift(cy - 3), cy - 3, rx, ry * 0.8))
    _outline(img)
    if p.get("set_brick"):
        bx, by = p["set_brick"]
        _brick(img, bx, by, 11)
        _R(img, bx + 2, by - 1, 6, 1, "ice"); _P(img, bx + 3, by - 2, "white"); _P(img, bx + 4, by - 2, "ice")
    if p.get("brick"):
        _brick(img, *p["brick"])
    hy = p["hat_y"]
    _stamp(img, HAT, int(cx) - 6 + shift(hy + 3), hy)
    ey = int(cy - ry * 0.45) + 1
    fx = int(cx) - 1 + shift(ey + 1)
    for x0 in (fx - 3, fx + 1):
        _R(img, x0, ey, 2, 3, "ink"); _P(img, x0, ey, "white")
        _R(img, x0 - (1 if x0 < fx else 0), ey - 1, 3, 1, "ink")
    _R(img, fx - 2 + shift(ey + 5) - shift(ey + 1), ey + 5, 3, 1, "ink")
    if p.get("trowel"):
        tx, ty, rows = p["trowel"]
        _stamp(img, rows, tx, ty)
    return img


# ======================================================================== BIG GUARD (close-up for the petri dish)

BELLY = (30, 46, 52, 30)


def _big_cap(w=40):
    """The guard cap at close-up scale, same parts as CAP: slate shine, dusk edges, night crown, dusk band with a
    gold badge towards the front, night visor sticking out to the left."""
    rows = []
    rows.append("." * 5 + "K" * (w - 10) + "." * 5)
    rows.append("." * 4 + "K" + "L" * 10 + "D" * (w - 20) + "K" + "." * 4)
    rows.append("." * 3 + "K" + "L" * 6 + "N" * (w - 16) + "D" * 2 + "K" + "." * 3)
    for _ in range(3):
        rows.append("." * 2 + "K" + "D" + "N" * (w - 8) + "D" * 2 + "K" + "." * 2)
    for i in range(3):
        band = "D" * 9 + ("YYGG" if i < 2 else "GGOO") + "D" * (w - 23)
        rows.append("." * 2 + "K" + "D" + band + "D" + "K" + "." * 2)
    rows.append("K" * (w - 1) + ".")
    rows.append("K" + "N" * (w - 3) + "K" + ".")
    rows.append("K" + "N" * 4 + "D" * (w - 7) + "K" + ".")
    rows.append("K" * (w - 1) + ".")
    return "\n".join(rows)


def big_macrophage(mood="grin", color="red"):
    mood = mood if mood in ("grin", "surprised") else "grin"
    color = color if color in UNIFORM else "red"
    W, H = 112, 92
    cx, cy, rx, ry = 56, 56, 47, 35
    m = _emask(W, H, cx, cy, rx, ry, WOBBLE)
    m[H - 1:, :] = False
    img = blank(W, H)
    img.alpha_composite(_volume(m, cx, cy, rx, ry))
    _uniform(img, m, color, 82, 6, ((84, 82), (93, 39)), 4)
    _outline(img)
    # nub arms resting at the sides, each with its own outline so they sit in front of the body
    for (ax, ay) in ((cx - rx + 4, cy + 15), (cx + rx - 4, cy + 15)):
        am = _emask(W, H, ax, ay, 8.5, 7.0)
        am[H - 1:, :] = False
        lay = _volume(am, ax, ay, 8.5, 7.0)
        _outline(lay)
        img.alpha_composite(lay)
    # buckle
    _stamp(img, """
KKKKKKKK
KYYYYGGK
KYKKKKGK
KGK..KOK
KGKKKKOK
KGGGOOOK
KKKKKKKK""", 48, 81)
    _stamp(img, _big_cap(), int(cx) - 22, 10)
    # belly patch: calm, flat, a step lighter, with a dithered rim so it sits in the body
    bx0, by0, bw, bh = BELLY
    for y in range(by0, by0 + bh):
        for x in range(bx0, bx0 + bw):
            ex_, ey_ = min(x - bx0, bx0 + bw - 1 - x), min(y - by0, by0 + bh - 1 - y)
            if ex_ + ey_ < 2:
                continue
            if ex_ == 0 or ey_ == 0 or ex_ + ey_ == 2:
                _P(img, x, y, "ice" if (x + y) % 2 == 0 else "white")
            else:
                _P(img, x, y, "white")
    _big_face(img, mood, color)
    if color == "red":
        _coin_pile(img, ((90, 83), (94, 86), (91, 88), (97, 88), (102, 88)))
    return img


def _big_eye(img, cx, cy, w, h, pupil, pw=4, ph=4, lid=0, glint=True):
    """Oval white eye with an ink rim; pupil = top-left of the pupil relative to the eye's top-left."""
    x0, y0 = cx - w // 2, cy - h // 2
    for y in range(y0 - 1, y0 + h + 1):
        for x in range(x0 - 1, x0 + w + 1):
            u, v = (x + 0.5 - cx) / (w / 2 + 0.5), (y + 0.5 - cy) / (h / 2 + 0.5)
            if u * u + v * v <= 1.0:
                inner = ((x + 0.5 - cx) / (w / 2 - 0.5)) ** 2 + ((y + 0.5 - cy) / (h / 2 - 0.5)) ** 2 <= 1.0
                _P(img, x, y, "white" if inner and y >= y0 + lid else "ink")
    px_, py_ = pupil
    for y in range(y0 + py_, y0 + py_ + ph):
        for x in range(x0 + px_, x0 + px_ + pw):
            if _get(img, x, y) == "white":
                _P(img, x, y, "ink")
    if glint and _get(img, x0 + px_, y0 + py_) == "ink":
        _P(img, x0 + px_, y0 + py_, "white")


def _big_face(img, mood, color):
    fx, ey = 52, 27
    L, R = fx - 11, fx + 7
    if mood == "grin":
        # explainer dot eyes at close-up scale: heavy lids, glints slid to the side, one brow cocked
        for x0 in (L, R):
            _R(img, x0, ey, 4, 9, "ink")
            _R(img, x0, ey, 4, 3, "steel"); _R(img, x0 - 1, ey + 3, 6, 1, "ink")
            _R(img, x0 + 2, ey + 4, 2, 2, "white")
        _ln(img, L - 3, ey - 2, L + 5, ey - 1, "ink"); _ln(img, L - 3, ey - 3, L + 5, ey - 2, "ink")
        _ln(img, R - 2, ey - 2, R + 6, ey - 4, "ink"); _ln(img, R - 2, ey - 3, R + 6, ey - 5, "ink")
        _stamp(img, """
KK.....................KK
.KK...................KK.
..KKKKKKKKKKKKKKKKKKKKK..
..KWWWIWWWIWWWIWWWIWWWK..
...KWWIWWWIWWWIWWWIWWK...
....KKKKKKKKKKKKKKKKK....
.....KNNNNNRRRRRNNNNK....
......KKKKKKKKKKKKKK.....""", fx - 12, ey + 10)
    else:
        _big_eye(img, L + 2, ey + 4, 9, 11, pupil=(3, 4), pw=3, ph=3)
        _big_eye(img, R + 2, ey + 4, 9, 11, pupil=(3, 4), pw=3, ph=3)
        _ln(img, L - 3, ey - 2, L + 6, ey - 4, "ink"); _ln(img, L - 3, ey - 3, L + 6, ey - 5, "ink")
        _ln(img, R - 2, ey - 4, R + 7, ey - 2, "ink"); _ln(img, R - 2, ey - 5, R + 7, ey - 3, "ink")
        _stamp(img, """
...KKKKK...
..KNNNNNK..
.KNNNNNNNK.
.KNNNNNNNK.
.KNNNRRNNK.
..KNRRRNK..
...KKKKK...""", fx - 4, ey + 11)
    if color == "red":
        _R(img, L - 4, ey + 11, 5, 2, "rose"); _R(img, R + 3, ey + 11, 5, 2, "rose")
