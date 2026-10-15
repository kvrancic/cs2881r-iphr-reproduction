"""Things: the props of the read-versus-write metaphor, the business story (patent cliff, pharmacy shelf,
owning drugs) and the close. Every function returns RGBA of its spec size; Endesga 32 only; a 1px ink outline
on every outer silhouette (the deck ground is near-white); light from the top-left."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from px import blank, paste, line, text
from pal import rgba, C

NAME = {v: k for k, v in C.items()}


# ---------------------------------------------------------------- helpers

def _P(img, x, y, col, a=255):
    x, y = int(x), int(y)
    if col and 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), rgba(col, a) if isinstance(col, str) else col)


def _R(img, x, y, w, h, col, a=255):
    for yy in range(int(y), int(y + h)):
        for xx in range(int(x), int(x + w)):
            _P(img, xx, yy, col, a)


def _A(img, x, y):
    if 0 <= x < img.width and 0 <= y < img.height:
        return img.getpixel((int(x), int(y)))[3]
    return 0


def _G(img, x, y):
    """Palette name of an opaque pixel, else None."""
    if 0 <= x < img.width and 0 <= y < img.height:
        r, g, b, a = img.getpixel((int(x), int(y)))
        if a:
            return NAME.get((r, g, b))
    return None


def _ln(img, x0, y0, x1, y1, col):
    line(img, int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)), rgba(col))


def _outline(img, col="ink", thresh=128):
    """In place: 1px outline on transparent pixels touching opaque ones (4-neighbourhood)."""
    w, h = img.size
    src = img.copy().load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] >= thresh:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and src[xx, yy][3] >= thresh:
                    img.putpixel((x, y), rgba(col))
                    break
    return img


def _fill(img, mask, col):
    for y in range(img.height):
        for x in range(img.width):
            if mask(x + 0.5, y + 0.5):
                _P(img, x, y, col)


def _ell(cx, cy, rx, ry):
    return lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def _box(x0, y0, x1, y1):
    """Inclusive pixel box as a mask."""
    return lambda x, y: x0 <= x - 0.5 <= x1 and y0 <= y - 0.5 <= y1


def _cap(ax, ay, bx, by, r):
    def m(x, y):
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L))
        px_, py_ = ax + dx * t, ay + dy * t
        return (x - px_) ** 2 + (y - py_) ** 2 <= r * r
    return m


def _poly_cap(pts, r):
    segs = [_cap(*pts[i], *pts[i + 1], r) for i in range(len(pts) - 1)]
    return lambda x, y: any(s(x, y) for s in segs)


def _any(*ms):
    return lambda x, y: any(m(x, y) for m in ms)


def _parts(w, h, parts, outline="ink"):
    """Layered shapes, back to front. Each part: dict(m=mask, c=base, lo=shadow, hi=highlight,
    line=contact colour where a part in front touches it, lo_n=shadow depth, hi_left=bool)."""
    lab = [[-1] * w for _ in range(h)]
    for i, p in enumerate(parts):
        m = p["m"]
        for y in range(h):
            for x in range(w):
                if m(x + 0.5, y + 0.5):
                    lab[y][x] = i

    def L(x, y):
        return lab[y][x] if 0 <= x < w and 0 <= y < h else -1

    img = blank(w, h)
    for y in range(h):
        for x in range(w):
            i = lab[y][x]
            if i < 0:
                continue
            p = parts[i]
            col = p["c"]
            n = p.get("lo_n", 1)
            if p.get("hi") and (L(x, y - 1) < 0 or (p.get("hi_left") and L(x - 1, y) < 0)):
                col = p["hi"]
            if p.get("lo") and any(L(x, y + k) != i or L(x + 1, y + k) != i for k in range(1, n + 1)):
                col = p["lo"]
            if p.get("line") and any(L(x + dx, y + dy) > i for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                col = p["line"]
            _P(img, x, y, col)
    if outline:
        img = _outline(img, outline)
    return img



def _sphere(img, cx, cy, r, ramp, cut=(0.82, 0.45, 0.0, -0.45), mask=None):
    lx, ly, lz = -0.55, -0.62, 0.56
    n = math.sqrt(lx * lx + ly * ly + lz * lz); lx, ly, lz = lx / n, ly / n, lz / n
    for y in range(int(cy - r - 2), int(cy + r + 3)):
        for x in range(int(cx - r - 2), int(cx + r + 3)):
            if mask is not None and not mask(x + 0.5, y + 0.5):
                continue
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = min(dx * dx + dy * dy, 1.0)
            nz = math.sqrt(max(0.0, 1 - d2))
            i = dx * lx + dy * ly + nz * lz
            k = len(cut)
            for j, c in enumerate(cut):
                if i > c:
                    k = j; break
            _P(img, x, y, ramp[min(k, len(ramp) - 1)])
    return img


def _text_center(img, s, col, cx, y):
    t = text(s, col, 20)
    bb = t.getbbox()
    t = t.crop((bb[0], 0, bb[2], t.height))
    paste(img, t, int(round(cx - t.width / 2)), y)
    return t.width


# ---------------------------------------------------------------- file icon

def _castle_art():
    """A small grumpy castle, 38x42, outlined."""
    W_, H_ = 38, 42
    battl = lambda x0, x1, y0, step=4: (lambda x, y: y0 <= y - 0.5 <= y0 + 2 and x0 <= x - 0.5 <= x1
                                        and ((int(x - 0.5) - x0) % step) < 2)
    keep = _any(_box(13, 12, 24, 30), battl(13, 24, 9, 4), _box(23, 9, 24, 11))
    wall = _any(_box(9, 26, 28, 40), battl(10, 27, 23, 4))
    lt = _any(_box(2, 18, 11, 40), battl(2, 11, 15, 4), _box(10, 15, 11, 17))
    rt = _any(_box(26, 18, 35, 40), battl(26, 35, 15, 4), _box(34, 15, 35, 17))
    pole = _box(18, 1, 18, 9)
    flag = _any(_box(19, 1, 29, 7), _box(19, 8, 27, 8))
    img = _parts(W_, H_, [
        dict(m=pole, c="slate"),
        dict(m=flag, c="red", lo="wine", hi="rose"),
        dict(m=keep, c="wine", lo="plum", hi="red", hi_left=True, line="ink", lo_n=2),
        dict(m=wall, c="wine", lo="plum", hi="red", line="ink", lo_n=1),
        dict(m=lt, c="wine", lo="plum", hi="red", hi_left=True, line="plum", lo_n=2),
        dict(m=rt, c="wine", lo="plum", hi="red", hi_left=True, line="plum", lo_n=2),
    ])
    # outline sits one px out: art pixels are at +0 (no growth, _outline is in place)
    # brick dashes
    for (x, y, n) in ((4, 22, 3), (7, 27, 2), (4, 33, 3), (28, 23, 2), (31, 29, 3), (28, 35, 2),
                      (15, 15, 2), (20, 19, 2), (12, 30, 3), (24, 28, 2)):
        for k in range(n):
            if _G(img, x + k, y) == "wine":
                _P(img, x + k, y, "plum")
    # gate: arched, dark, portcullis
    gate = _any(_box(15, 31, 22, 40), _box(16, 30, 21, 30), _box(17, 29, 20, 29))
    for y in range(29, 41):
        for x in range(14, 24):
            if gate(x + 0.5, y + 0.5):
                _P(img, x, y, "plum")
            elif any(gate(x + 0.5 + dx, y + 0.5 + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and y <= 40:
                _P(img, x, y, "ink")
    for x in (17, 20):
        _ln(img, x, 30, x, 40, "ink")
    for y in (33, 37):
        _ln(img, 16, y, 21, y, "ink")
    # windows (arrow slits) and a lit keep window
    for (x, y) in ((6, 22), (30, 22)):
        _R(img, x, y, 2, 4, "ink")
    _R(img, 17, 15, 3, 4, "ink"); _P(img, 17, 15, None)
    _R(img, 18, 16, 1, 2, "gold")
    # grumpy flag face
    for (x, y, c) in ((21, 3, "ink"), (22, 4, "ink"), (26, 3, "ink"), (25, 4, "ink"),
                      (22, 5, "ink"), (25, 5, "ink"),
                      (23, 7, "ink"), (24, 7, "ink"), (22, 8, "ink"), (25, 8, "ink")):
        _P(img, x, y, c)
    _P(img, 18, 0, "gold")
    return img


def _cell_art():
    """A small red blob cell, 34x30, outlined."""
    W_, H_ = 34, 30
    cx, cy = 16.5, 14.5

    def m(x, y):
        a = math.atan2(y - cy, x - cx)
        r = 12.0 + 0.9 * math.sin(3 * a + 0.7) + 0.5 * math.sin(5 * a + 2.1)
        return ((x - cx) / 1.12) ** 2 + (y - cy) ** 2 <= r * r
    img = blank(W_, H_)
    _sphere(img, cx - 1.5, cy - 1, 15.5, ["rose", "red", "red", "wine", "wine"], cut=(0.78, 0.3, -0.25, -0.62), mask=m)
    # nucleus: a darker oval with a rim on its lower right and a lit upper left
    nm = _ell(19.0, 16.0, 5.6, 4.6)
    for y in range(H_):
        for x in range(W_):
            if nm(x + 0.5, y + 0.5):
                col = "wine"
                if not nm(x + 1.5, y + 0.5) or not nm(x + 0.5, y + 1.5):
                    col = "plum"
                _P(img, x, y, col)
    for (x, y) in ((16, 13), (17, 13), (15, 14), (16, 14)):
        _P(img, x, y, "red")
    # granules
    for (x, y) in ((9, 18), (10, 18), (24, 9), (25, 9), (12, 23), (13, 23), (26, 19)):
        _P(img, x, y, "wine")
    for (x, y) in ((8, 12), (13, 6), (22, 5)):
        _P(img, x, y, "rose")
    # specular glint
    for (x, y) in ((8, 6), (9, 6), (7, 7), (8, 7)):
        _P(img, x, y, "white")
    return _outline(img)


def file_icon(art="castle"):
    """64x80 document icon; art='castle' or 'cell'. Page y 1..76; rows 64..79 calm for the file name."""
    img = blank(64, 80)
    x0, y0, x1, y1, F = 6, 1, 56, 76, 14
    page = [(x0, y0), (x1 - F, y0), (x1, y0 + F), (x1, y1), (x0, y1)]
    # drop shadow, dithered steel, offset down-right
    sh = blank(64, 80)
    from PIL import ImageDraw
    ImageDraw.Draw(sh).polygon([(x + 2, y + 2) for x, y in page], fill=rgba("steel"))
    for y in range(80):
        for x in range(64):
            if sh.getpixel((x, y))[3] and (x + y) % 2 == 0:
                _P(img, x, y, "steel")
    d = ImageDraw.Draw(img)
    d.polygon(page, fill=rgba("white"), outline=rgba("ink"))
    # page shading: right and bottom edges
    for y in range(y0 + F + 1, y1):
        _P(img, x1 - 1, y, "ice")
        if y % 2 == 0:
            _P(img, x1 - 2, y, "ice")
    for x in range(x0 + 1, x1):
        _P(img, x, y1 - 1, "ice")
        if x % 2 == 0:
            _P(img, x, y1 - 2, "ice")
    # the fold
    fx = x1 - F
    for y in range(y0, y0 + F + 1):
        for x in range(fx, x1 + 1):
            if x - fx <= y - y0:
                _P(img, x, y, "ice")
    _ln(img, fx, y0, fx, y0 + F, "ink")
    _ln(img, fx, y0 + F, x1, y0 + F, "ink")
    _ln(img, fx, y0, x1, y0 + F, "ink")
    for y in range(y0 + 2, y0 + F):
        _P(img, fx + 1, y, "white")
    for x in range(fx + 2, x1):
        _P(img, x, y0 + F - 1, "steel")
    for x in range(fx + 1, x1):
        if x % 2:
            _P(img, x, y0 + F + 1, "ice")
    for y in range(y0 + 1, y0 + F):
        if y % 2:
            _P(img, fx - 1, y, "ice")
    # a few header lines, top left, quiet
    for (yy, ww) in ((6, 18), (9, 12)):
        _R(img, x0 + 5, yy, ww, 1, "ice")
    if art == "cell":
        a = _cell_art()
        # floor shadow
        for x in range(16, 47):
            _P(img, x, 56, "ice")
            if x % 2 and 18 < x < 45:
                _P(img, x, 57, "ice")
        paste(img, a, 31 - a.width // 2, 25)
    else:
        a = _castle_art()
        for x in range(13, 49):
            _P(img, x, 60, "ice")
            if x % 2 and 15 < x < 47:
                _P(img, x, 61, "ice")
        paste(img, a, 31 - a.width // 2, 19)
    return img


# ---------------------------------------------------------------- petri dish

_PD = dict(cx=85.0, top=15.0, bot=25.0, rx=84.0, ry=13.5, med=20.0)


def _in(e, x, y, dr=0.0):
    cx, cy, rx, ry = e
    return ((x - cx) / (rx + dr)) ** 2 + ((y - cy) / (ry + dr)) ** 2 <= 1.0


def petri_dish(front=False):
    """170x40. Back layer (front=False): back rim, inner glass, the medium. Front layer (front=True): front rim
    and front glass only. A 112x92 cell sits between them."""
    W_, H_ = 170, 40
    cx, top, bot, rx, ry, med = _PD["cx"], _PD["top"], _PD["bot"], _PD["rx"], _PD["ry"], _PD["med"]
    Etop = (cx, top, rx, ry)
    Ebot = (cx, bot, rx, ry)
    Ein = (cx, top + 0.6, rx - 2.2, ry - 2.0)          # inner edge of the rim
    Emed = (cx, med, rx - 3.0, ry - 2.6)                # medium surface
    Emb = (cx, bot - 0.5, rx - 2.5, ry - 2.3)           # inner bottom
    img = blank(W_, H_)

    def body(x, y):  # whole dish silhouette
        return _in(Etop, x, y) or _in(Ebot, x, y) or (abs(x - cx) <= rx and top <= y <= bot)

    for y in range(H_):
        for x in range(W_):
            X, Y = x + 0.5, y + 0.5
            if not body(X, Y):
                continue
            in_rim = _in(Etop, X, Y) and not _in(Ein, X, Y)
            upper = Y < top
            front_wall = (not _in(Etop, X, Y) or Y > top) and not upper
            if not front:
                if in_rim and Y < top:
                    # back rim: white crest, ice body
                    _P(img, x, y, "white" if not _in(Etop, X, Y - 1.2) else "ice")
                elif _in(Ein, X, Y) and not _in(Emed, X, Y) and Y < med:
                    # inner back wall of glass, seen over the medium
                    if (x + y) % 2 == 0 and y % 2 == 0:
                        _P(img, x, y, "ice")
                    if not _in(Ein, X, Y - 1.5):
                        _P(img, x, y, "ice")
                elif _in(Emed, X, Y):
                    # medium surface: rose, dithered pink towards the back, a white glint
                    far = Y < med - (ry - 2.6) * 0.35
                    col = "rose"
                    if far and (x + y) % 2 == 0:
                        col = "pink"
                    if not _in(Emed, X, Y - 1.0) and Y < med:
                        col = "pink"
                    _P(img, x, y, col)
                elif Y >= med and (_in(Emb, X, Y) or (abs(X - cx) <= rx - 3 and Y <= bot)):
                    # medium volume seen through the front glass
                    deep = not _in(Ebot, X, Y + 1.5)
                    _P(img, x, y, "pink" if deep or (x + y) % 2 else "rose")
            else:
                if in_rim and Y >= top:
                    _P(img, x, y, "white" if _in(Etop, X, Y + 1.3) and not _in(Ein, X, Y - 0.5) and Y > top + ry - 4 else "ice")
                elif front_wall and not _in(Etop, X, Y) and (_in(Ebot, X, Y) or abs(X - cx) <= rx):
                    # front glass wall: sparse ice, steel base edge, vertical glints on the left
                    if not _in(Ebot, X, Y + 1.6) and _in(Ebot, X, Y):
                        _P(img, x, y, "steel")
                    elif x % 4 == 0 and y % 2 == 0:
                        _P(img, x, y, "ice")
                    if x in (22, 23, 27) and Y > top:
                        _P(img, x, y, "white")
    # silhouette outline: back half on the back layer, front half and sides on the front layer
    sil = blank(W_, H_)
    _fill(sil, body, "white")
    o = _outline(sil.copy())
    for y in range(H_):
        for x in range(W_):
            if _G(o, x, y) == "ink" and not sil.getpixel((x, y))[3]:
                is_back = y < top
                if is_back != front:
                    _P(img, x, y, "ink")
    if front:
        # the line where the rim meets the front wall
        for x in range(W_):
            for y in range(int(top), H_):
                X = x + 0.5
                if _in(Etop, X, y + 0.5) and not _in(Etop, X, y + 1.5) and abs(X - cx) < rx - 1:
                    _P(img, x, y + 1, "steel")
                    break
        # side edges of the wall, ink
        for y in range(int(top), int(bot) + 1):
            _P(img, int(cx - rx) - 1, y, "ink"); _P(img, int(cx + rx), y, "ink")
    return img


# ---------------------------------------------------------------- finger

def finger():
    """48x30: a big cartoon hand, index pointing left and a little down, sky cuff at the right."""
    sk = dict(c="skin", lo="skin2", hi="sand", line="clay")
    palm = _ell(34.0, 15.5, 8.5, 10.5)
    f3 = _cap(24, 24.6, 32, 24.6, 2.3)
    f2 = _cap(22.5, 21.2, 32, 21.2, 2.4)
    f1 = _cap(21, 17.6, 31, 17.6, 2.5)
    thumb = _cap(32, 9.5, 24.5, 5.0, 2.7)
    index = _cap(33, 12.0, 5.2, 16.6, 3.3)
    cuff = _box(40, 4, 46, 26)
    img = _parts(48, 30, [
        dict(m=palm, lo_n=2, **sk),
        dict(m=f3, **sk), dict(m=f2, **sk), dict(m=f1, **sk),
        dict(m=thumb, **sk),
        dict(m=index, lo_n=1, **sk),
        dict(m=cuff, c="sky", lo="navy", hi="cyan", hi_left=False, line="navy"),
    ])
    # nail at the fingertip
    for (x, y, c) in ((4, 14, "sand"), (5, 14, "sand"), (6, 14, "sand"), (4, 15, "sand"), (5, 15, "white"),
                      (6, 15, "sand"), (7, 15, "skin2"), (7, 14, "skin2")):
        _P(img, x, y, c)
    # knuckle creases on the index
    for (x, y) in ((15, 15), (15, 16), (23, 14), (23, 15)):
        _P(img, x, y, "skin2")
    # cuff: opening shadow, stitch and button
    for y in range(5, 26):
        _P(img, 40, y, "navy")
    for y in range(6, 25, 2):
        _P(img, 42, y, "cyan")
    _R(img, 44, 14, 2, 2, "white"); _P(img, 45, 15, "ice")
    return img


# ---------------------------------------------------------------- pill bottle

_LABELS = {
    "keytruda": ("navy", "night", "sky", "navy"),
    "bb": ("sky", "navy", "cyan", "sky"),
    "plain": ("white", "ice", "white", "steel"),
    "a": ("rose", "red", "pink", "red"),
    "b": ("green", "leaf", "yellow", "leaf"),
    "c": ("orange", "rust", "gold", "orange"),
    "d": ("grape", "plum", "pink", "grape"),
}


def _bottle(w=20, h=28, label="plain", cap_h=5):
    """Pharmacy pill bottle, fills (w x h) with outline; base on the last row."""
    base, dark, light, capc = _LABELS.get(label, _LABELS["plain"])
    img = blank(w, h)
    bx0, bx1 = 1, w - 2
    cx0, cx1 = 3, w - 4
    cy0, cy1 = 1, cap_h
    ly = cap_h + 1
    by0, by1 = cap_h + 2, h - 2
    # cap with ridges
    capdark = {"sky": "navy", "navy": "night", "steel": "slate", "red": "wine", "leaf": "pine",
               "orange": "rust", "grape": "plum"}[capc]
    caplight = {"sky": "cyan", "navy": "sky", "steel": "ice", "red": "rose", "leaf": "green",
                "orange": "gold", "grape": "pink"}[capc]
    for y in range(cy0, cy1 + 1):
        for x in range(cx0, cx1 + 1):
            c = capc
            if (x - cx0) % 2 == 1 and y > cy0:
                c = capdark
            if y == cy0:
                c = caplight
            if x >= cx1 - 1 and y > cy0:
                c = capdark
            _P(img, x, y, c)
    # lip
    for x in range(cx0 - 1, cx1 + 2):
        _P(img, x, ly, "ice" if x < cx1 else "steel")
    # body
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            c = "white"
            if x >= bx1 - 2:
                c = "ice"
            if x == bx1:
                c = "steel"
            if y == by1:
                c = "ice" if x < bx1 else "steel"
            _P(img, x, y, c)
    # shoulder rounding
    _P(img, bx0, by0, None); _P(img, bx1, by0, None)
    # label band
    lb0, lb1 = by0 + 3, by1 - 4
    for y in range(lb0, lb1 + 1):
        for x in range(bx0, bx1 + 1):
            c = base
            if x >= bx1 - 2:
                c = dark
            if y in (lb0, lb1):
                c = dark
            _P(img, x, y, c)
    if label == "keytruda":
        m = (lb0 + lb1) // 2
        for x in range(bx0, bx1 + 1):
            _P(img, x, m, "gold" if x < bx1 - 2 else "orange")
            _P(img, x, m + 1, "gold" if x < bx1 - 2 else "orange")
            _P(img, x, m - 3, "sky" if x < bx1 - 2 else "navy")
    elif label == "bb" and w >= 20:
        t = text("3B", "white", 20)
        bb = t.getbbox(); t = t.crop((bb[0], 0, bb[2], t.height))
        paste(img, t, bx0 + (bx1 - bx0 + 1 - t.width) // 2, lb0 + 1)
    elif label == "bb":
        m = (lb0 + lb1) // 2; c = (bx0 + bx1) // 2
        for k in range(-2, 3):
            _P(img, c + k, m, "white"); _P(img, c, m + k, "white")
    elif label == "plain":
        for i, yy in enumerate(range(lb0 + 2, lb1 - 1, 2)):
            _R(img, bx0 + 2, yy, (bx1 - bx0 - 5) - (i % 2) * 3, 1, "steel")
    else:
        mid = (lb0 + lb1) // 2
        _R(img, bx0 + 2, mid - 1, bx1 - bx0 - 5, 1, "white")
        _R(img, bx0 + 2, mid + 1, (bx1 - bx0 - 5) // 2 + 1, 1, "white")
    # glass highlight on the left
    for y in range(by0 + 1, by1):
        if not (lb0 <= y <= lb1):
            _P(img, bx0 + 1, y, "white")
    return _outline(img)


def pill_bottle(label="plain"):
    """20x28, base on the last row. label: keytruda, bb, plain, a, b, c, d."""
    return _bottle(20, 28, label if label in _LABELS else "plain")


# ---------------------------------------------------------------- shelf

def _box_item(w, h, col, dark, band="white", rng=None):
    img = blank(w, h)
    _R(img, 1, 1, w - 2, h - 2, col)
    _R(img, w - 3, 1, 2, h - 2, dark)
    _R(img, 1, 1, w - 2, 1, band if band != "white" else "white")
    # white panel with a coloured mark
    if h >= 10 and w >= 8:
        py = 3 if h < 16 else h // 3
        _R(img, 2, py, w - 5, max(3, h // 4), "white")
        _R(img, w - 3, py, 1, max(3, h // 4), "ice")
        _R(img, 3, py + 1, max(1, (w - 7) // 2), 1, dark)
    return _outline(img)


def _jar(w, h, lid, glass="orange"):
    img = blank(w, h)
    _R(img, 2, 1, w - 4, 3, lid)
    _R(img, w - 4, 1, 2, 3, {"red": "wine", "sky": "navy", "white": "ice", "green": "leaf", "gold": "orange"}.get(lid, "slate"))
    _R(img, 1, 4, w - 2, h - 5, glass)
    dark = {"orange": "rust", "sky": "navy", "white": "ice", "rose": "red"}.get(glass, "brown")
    _R(img, w - 3, 4, 2, h - 5, dark)
    _R(img, 1, h - 2, w - 2, 1, dark)
    _R(img, 2, 5, 1, h - 8, "white" if glass != "white" else "ice")
    if h > 10:
        _R(img, 3, h // 2, w - 6, max(3, h // 4), "white")
        _R(img, w - 4, h // 2, 1, max(3, h // 4), "ice")
    return _outline(img)


def _blister(w, h):
    img = blank(w, h)
    _R(img, 1, 1, w - 2, h - 2, "ice")
    _R(img, w - 2, 1, 1, h - 2, "steel"); _R(img, 1, h - 2, w - 2, 1, "steel")
    for y in range(3, h - 3, 4):
        for x in range(3, w - 3, 4):
            _R(img, x, y, 2, 2, "white"); _P(img, x + 1, y + 1, "steel")
    return _outline(img)


def _syrup(w, h, label):
    img = blank(w, h)
    nk = w // 2 - 1
    _R(img, nk, 1, 3, 3, "ink")
    _R(img, nk - 1, 4, 5, 1, "slate")
    _R(img, nk, 5, 3, 2, "rust")
    _R(img, 1, 7, w - 2, h - 8, "rust")
    _R(img, 2, 6, w - 4, 1, "rust")
    _R(img, w - 3, 7, 2, h - 8, "brown")
    _R(img, 2, 8, 1, h - 10, "orange")
    _R(img, 2, h // 2, w - 4, h // 3, label)
    _R(img, w - 3, h // 2, 1, h // 3, "ice")
    return _outline(img)


def _shelf_row(img, x0, x1, ybase, maxh, rng):
    """Fill x0..x1 with groups of goods standing on row ybase."""
    cols = [("red", "wine"), ("sky", "navy"), ("green", "leaf"), ("orange", "rust"), ("grape", "plum"),
            ("rose", "red"), ("gold", "orange"), ("navy", "night"), ("pink", "grape"), ("leaf", "pine")]
    labels = ["a", "b", "c", "d", "plain", "bb"]
    x = x0
    while x < x1 - 6:
        kind = rng.choice(["bottle", "bottle", "box", "box", "jar", "blister", "syrup"])
        n = rng.choice([2, 3, 3, 4]) if kind in ("bottle", "box") else rng.choice([1, 2])
        col, dark = rng.choice(cols)
        if kind == "bottle":
            w = rng.choice([11, 12, 13]); h = min(maxh - 2, rng.choice([15, 17, 19]))
            spr = lambda: _bottle(w, h, rng_label, cap_h=3 if h < 18 else 4)
            rng_label = rng.choice(labels)
        elif kind == "box":
            w = rng.choice([10, 12, 14]); h = min(maxh - 2, rng.choice([16, 20, 24]))
            spr = lambda: _box_item(w, h, col, dark)
        elif kind == "jar":
            w = rng.choice([13, 15]); h = min(maxh - 2, rng.choice([12, 14]))
            lid = rng.choice(["red", "sky", "white", "green", "gold"])
            glass = rng.choice(["orange", "white", "orange"])
            spr = lambda: _jar(w, h, lid, glass)
        elif kind == "blister":
            w = rng.choice([14, 18]); h = min(maxh - 2, rng.choice([18, 22]))
            spr = lambda: _blister(w, h)
        else:
            w = rng.choice([9, 10]); h = min(maxh - 2, rng.choice([20, 22, 24]))
            lab = rng.choice(["white", "sand"])
            spr = lambda: _syrup(w, h, lab)
        for k in range(n):
            if x + w > x1 + 1:
                break
            s = spr()
            paste(img, s, x, ybase - s.height + 1)
            x += w - 1 if kind in ("box",) else w
        x += 1
    return img


def shelf():
    """220x110, base on the last row. Three shelves of medicine; a gap on the middle shelf at x 100..121.
    The middle shelf's top surface is row 69 (a bottle placed there has its last row at y 69)."""
    W_, H_ = 220, 110
    img = blank(W_, H_)
    # back panel
    _R(img, 6, 5, 208, 98, "ice")
    for (y0, y1) in ((5, 33), (38, 69), (74, 101)):
        for x in range(6, 214):
            _P(img, x, y0, "steel")
            if x % 2:
                _P(img, x, y0 + 1, "steel")
        for y in range(y0, y1 + 1):
            _P(img, 6, y, "steel")
            if y % 2:
                _P(img, 7, y, "steel")
    # frame: posts, cornice, boards, plinth (wood)

    def wood(x, y, w, h, top=True):
        _R(img, x, y, w, h, "tan")
        if top:
            _R(img, x, y, w, 1, "sand")
        _R(img, x, y + h - 1, w, 1, "clay")
    wood(1, 1, 218, 4)
    _R(img, 1, 5, 218, 1, "brown")
    for (yb) in (34, 70):
        wood(1, yb, 218, 4)
        _R(img, 6, yb + 4, 208, 1, "steel")
    wood(1, 102, 218, 7)
    _R(img, 3, 105, 214, 2, "clay")
    _R(img, 3, 105, 214, 1, "brown")
    for x0 in (1, 214):
        _R(img, x0, 1, 5, 108, "tan")
        _R(img, x0, 1, 1, 108, "sand")
        _R(img, x0 + 4, 1, 1, 108, "clay")
    # grain dashes
    for (x, y, n) in ((20, 2, 6), (90, 3, 5), (160, 2, 7), (40, 35, 5), (130, 36, 6), (190, 35, 4),
                      (60, 71, 6), (150, 72, 5), (30, 104, 8), (120, 103, 6), (180, 104, 7)):
        _R(img, x, y, n, 1, "clay")
    for (x, y) in ((3, 12), (3, 50), (3, 88), (216, 20), (216, 60), (216, 95)):
        _R(img, x, y, 1, 4, "clay")
    rng = random.Random(46)
    _shelf_row(img, 9, 211, 33, 28, rng)
    _shelf_row(img, 9, 98, 69, 31, rng)
    _shelf_row(img, 123, 211, 69, 31, rng)
    _shelf_row(img, 9, 211, 101, 27, rng)
    # outer outline
    sil = blank(W_, H_)
    _R(sil, 1, 1, 218, 108, "tan")
    o = _outline(sil.copy())
    for y in range(H_):
        for x in range(W_):
            if _G(o, x, y) == "ink" and not sil.getpixel((x, y))[3]:
                _P(img, x, y, "ink")
    return img


# ---------------------------------------------------------------- claw

def claw(closed=False):
    """36x70: arcade claw on a steel cable from the top edge; prongs open, or closed."""
    W_, H_ = 36, 70
    cable = _box(17, 0, 18, 22)
    top = _any(_box(13, 21, 22, 24))
    hub = _any(_ell(17.5, 30, 10.5, 7.5), _box(8, 28, 27, 34))
    collar = _box(11, 35, 24, 37)
    if closed:
        L = [(12, 37), (7, 48), (9, 58), (15, 64)]
        R = [(23, 37), (28, 48), (26, 58), (20, 64)]
        M = [(17.5, 38), (17.5, 56)]
    else:
        L = [(12, 37), (4, 47), (3, 58), (7, 65)]
        R = [(23, 37), (31, 47), (32, 58), (28, 65)]
        M = [(17.5, 38), (17.5, 59)]
    st = dict(c="steel", lo="slate", hi="white", line="dusk")
    img = _parts(W_, H_, [
        dict(m=cable, c="steel", lo="slate", hi=None),
        dict(m=_poly_cap(M, 1.8), **st),
        dict(m=top, c="slate", lo="dusk", hi="steel"),
        dict(m=hub, c="slate", lo="dusk", hi="steel", hi_left=True, line="dusk", lo_n=2),
        dict(m=collar, c="slate", lo="dusk", hi="steel"),
        dict(m=_poly_cap(L, 2.0), **st),
        dict(m=_poly_cap(R, 2.0), **st),
    ])
    # cable twist
    for y in range(0, 21, 3):
        _P(img, 17, y, "slate"); _P(img, 18, y + 1, "white")
    # hub: shine, rivets, a band
    _R(img, 11, 25, 3, 1, "white"); _P(img, 10, 26, "white"); _P(img, 10, 27, "ice")
    _R(img, 24, 28, 2, 1, "green")
    for x in range(9, 27):
        if _G(img, x, 31) in ("slate", "steel"):
            _P(img, x, 31, "gold")
        if _G(img, x, 32) in ("slate", "steel", "dusk"):
            _P(img, x, 32, "orange")
    for (x, y) in ((12, 38), (23, 38)):
        _P(img, x, y, "gold")
    return img


# ---------------------------------------------------------------- cliff

def cliff():
    """200x96: rocky plateau on the left, top surface ~ row 20, sheer drop near x 150; right of it transparent."""
    W_, H_ = 200, 96
    rng = random.Random(7)

    def ytop(x):
        return 20 + round(1.0 * math.sin(x * 0.09) + 0.7 * math.sin(x * 0.27 + 1.0))
    # the face: rocky ledges, an overhanging lip at the top
    E = []
    off, y = 0, 0
    while len(E) < H_:
        seg = rng.randint(4, 9)
        off = max(-5, min(2, off + rng.choice([-3, -2, -1, 1, 2])))
        E += [150 + off] * seg
    for y in range(0, 26):
        E[y] = 152
    for y in range(26, 29):
        E[y] = 150
    edge = lambda y: E[y]

    strata = ["sand", "peach", "tan", "clay", "brown", "brown"]
    shade = {"sand": "peach", "peach": "tan", "tan": "clay", "clay": "brown", "brown": "plum"}
    light = {"sand": "sand", "peach": "sand", "tan": "peach", "clay": "tan", "brown": "clay"}
    bands = [0, 5, 13, 26, 42, 60, 999]

    def band(x, y):
        wv = y - ytop(x) + round(1.5 * math.sin(x * 0.06 + 0.4) + 0.8 * math.sin(x * 0.17))
        for i in range(len(bands) - 1):
            if bands[i] <= wv < bands[i + 1]:
                return i, wv
        return 0, wv

    def inside(x, y):
        return 0 <= y < H_ and y >= ytop(x) and x <= edge(y)
    img = blank(W_, H_)
    for y in range(H_):
        for x in range(W_):
            if not inside(x, y):
                continue
            k, wv = band(x, y)
            base = strata[k]
            col = base
            if k == 5 and (x + y) % 2 == 0:
                col = "plum"
            if wv in bands[1:]:
                col = shade[base]
            dist = edge(y) - x
            if dist < 7:
                if dist < 1:
                    col = shade[shade[base]] if base != "brown" else "plum"
                elif dist < 4 or (x + y) % 2 == 0:
                    col = shade[base]
            # ledge tops catch the light
            if not inside(x, y - 1) and y > ytop(x) + 2:
                col = light[base]
            _P(img, x, y, col)
    # rock clusters: a dark dash with a lit dash above-left
    for _ in range(70):
        x = rng.randint(2, 138); y = rng.randint(26, 93)
        if not inside(x, y):
            continue
        k, _w = band(x, y)
        base = strata[k]
        n = rng.randint(3, 6)
        for i in range(n):
            if inside(x + i, y) and edge(y) - (x + i) > 6:
                _P(img, x + i, y, shade[base])
        for i in range(max(2, n - 2)):
            if inside(x + i - 1, y - 1) and edge(y - 1) - (x + i) > 6:
                _P(img, x + i - 1, y - 1, light[base])
    # grey boulders bedded in the strata
    for (bx, by, r) in ((28, 52, 4), (96, 78, 5), (64, 37, 3), (122, 62, 4), (10, 86, 4), (140, 88, 3)):
        for y in range(by - r, by + r + 1):
            for x in range(bx - r - 2, bx + r + 3):
                d = ((x - bx) / (r + 1.5)) ** 2 + ((y - by) / r) ** 2
                if d <= 1 and inside(x, y):
                    t = (x - bx) / (r + 1.5) + (y - by) / r
                    col = "ice" if t < -0.9 else "steel" if t < 0.2 else "slate"
                    if d > 0.72:
                        col = "dusk"
                    _P(img, x, y, col)
    # cracks running down the face
    for (x0, y0, n) in ((147, 32, 9), (145, 50, 12), (148, 70, 8), (144, 82, 10)):
        x = x0
        for k in range(n):
            if inside(x, y0 + k):
                _P(img, x, y0 + k, "plum")
            if k % 3 == 2:
                x -= 1
    # grass cap
    for x in range(0, W_):
        t = ytop(x)
        if not inside(x, t):
            continue
        _P(img, x, t, "green"); _P(img, x, t + 1, "green" if x % 3 else "leaf"); _P(img, x, t + 2, "leaf")
        if x % 2 == 0:
            _P(img, x, t + 3, "leaf")
    for x in (6, 19, 33, 47, 58, 74, 88, 101, 117, 131, 143):
        t = ytop(x)
        _P(img, x, t - 1, "green"); _P(img, x + 1, t - 1, "green"); _P(img, x + 1, t - 2, "green")
        if x % 2:
            _P(img, x - 1, t - 1, "green"); _P(img, x + 2, t - 2, "yellow")
    # grass hanging over the lip
    t = ytop(152)
    for (x, n) in ((152, 3), (151, 5), (149, 2)):
        for k in range(n):
            _P(img, x + 1, t + 3 + k, "leaf" if k else "green")
    o = _outline(img.copy())
    for y in range(H_):
        for x in range(W_):
            if _G(o, x, y) == "ink" and not img.getpixel((x, y))[3]:
                _P(img, x, y, "ink")
    return img


# ---------------------------------------------------------------- calendar

def _cal_page(img, year, grid=True):
    _R(img, 3, 12, 34, 26, "white")
    _R(img, 35, 12, 2, 26, "ice")
    _R(img, 3, 36, 34, 1, "ice")
    _R(img, 3, 37, 34, 1, "steel")
    if grid:
        for r in range(3):
            for c in range(7):
                x, y = 6 + c * 4, 14 + r * 3
                if (r, c) not in ((0, 0), (0, 1), (2, 6)):
                    _R(img, x, y, 2, 1, "steel" if c < 6 else "red")
    _text_center(img, year, "ink", 20, 24)


def calendar(page="2027"):
    """40x44 desk flip calendar, base on the last row. page: '2027', '2028' or 'tear' (the 2027 sheet half torn
    and curling up, 2028 showing beneath)."""
    img = blank(40, 44)
    # stand
    for y in range(39, 43):
        inset = 42 - y
        _R(img, 1 + inset // 2, y, 38 - inset, 1, "slate")
    _R(img, 2, 39, 36, 1, "steel")
    _R(img, 30, 40, 8, 3, "dusk")
    yr = "2028" if page in ("2028", "tear") else "2027"
    _cal_page(img, yr, grid=True)
    _R(img, 3, 4, 34, 8, "red")
    _R(img, 3, 4, 34, 1, "rose")
    _R(img, 35, 5, 2, 7, "wine")
    _R(img, 3, 11, 34, 1, "wine")
    for x in range(2, 38):
        _P(img, x, 3, "ink"); _P(img, x, 38, "ink")
    for y in range(3, 39):
        _P(img, 2, y, "ink"); _P(img, 37, y, "ink")
    o = _outline(img.copy())
    for y in range(44):
        for x in range(40):
            if _G(o, x, y) == "ink" and not img.getpixel((x, y))[3]:
                _P(img, x, y, "ink")
    if page == "tear":
        # where the year's glyphs leave a gap between "20" and "28"
        t = text("2028", "ink", 20); bb = t.getbbox(); t = t.crop((bb[0], 0, bb[2], t.height))
        tx0 = int(round(20 - t.width / 2))
        gaps = [x for x in range(t.width) if all(t.getpixel((x, yy))[3] == 0 for yy in range(t.height))]
        gx = tx0 + min(gaps, key=lambda g: abs(g - t.width / 2)) if gaps else 20
        zig = [0, 1, 1, 0, -1, -1]

        def tear(y):
            return gx if 23 <= y <= 34 else gx + zig[y % 6]
        # right half of the 2027 sheet is ripped away and rolled up under the header
        for y in range(12, 38):
            tx = tear(y)
            _P(img, tx, y, "ink")
            if y > 18 and y % 2 == 0:
                _P(img, tx + 1, y, "steel")
        rx0 = tear(12)
        for x in range(rx0, 39):
            for (y, c) in ((12, "ice"), (13, "white"), (14, "white"), (15, "ice"), (16, "steel"), (17, "ink")):
                _P(img, x, y, c)
            if x % 2 and x > rx0:
                _P(img, x, 18, "steel")
        for (y, c) in ((12, "ink"), (13, "ink"), (14, "ink"), (15, "ink"), (16, "ink")):
            _P(img, 39, y, c)
        _P(img, 38, 13, "ice"); _P(img, 38, 14, "steel"); _P(img, 38, 15, "ice"); _P(img, 38, 12, "ink")
        _P(img, 38, 16, "ink"); _P(img, 37, 16, "ink")
        for (y, dx) in ((12, 0), (13, -1), (14, 0), (15, -1), (16, 0), (17, 0)):
            _P(img, rx0 + dx, y, "ink")
        # a scrap of paper fluttering off
        for (x, y, c) in ((37, 20, "ink"), (38, 20, "ink"), (36, 21, "ink"), (37, 21, "white"), (38, 21, "white"), (39, 21, "ink"),
                          (37, 22, "ink"), (38, 22, "ice"), (39, 22, "ink"), (38, 23, "ink")):
            _P(img, x, y, c)
    # rings
    for rx in (9, 28):
        for (x, y, c) in ((rx, 0, "ink"), (rx + 1, 0, "ink"), (rx + 2, 0, "ink"),
                          (rx - 1, 1, "ink"), (rx, 1, "steel"), (rx + 1, 1, "white"), (rx + 2, 1, "steel"), (rx + 3, 1, "ink"),
                          (rx - 1, 2, "ink"), (rx, 2, "slate"), (rx + 3, 2, "ink"), (rx + 2, 2, "slate"),
                          (rx - 1, 3, "ink"), (rx, 3, "slate"), (rx + 2, 3, "slate"), (rx + 3, 3, "ink"),
                          (rx, 4, "slate"), (rx + 2, 4, "slate"), (rx, 5, "dusk"), (rx + 2, 5, "dusk"),
                          (rx + 1, 4, "wine"), (rx + 1, 5, "wine")):
            _P(img, x, y, c)
    return img


# ---------------------------------------------------------------- cash register

def cash_register():
    """60x50, base on the last row: chunky retro register, drawer popped open with coins, a little bell."""
    W_, H_ = 60, 50
    body = _any(_box(5, 13, 52, 37), _ell(9, 15, 4, 3), _ell(48, 15, 4, 3))
    sign = _box(12, 2, 32, 11)
    crank = _poly_cap([(53, 20), (57, 20), (57, 27)], 1.3)
    knob = _ell(57.5, 28.5, 1.8, 1.8)
    bell = _any(_ell(46.5, 8.5, 5.5, 4.5))
    bellbase = _box(40, 10, 53, 12)
    img = _parts(W_, H_, [
        dict(m=crank, c="steel", lo="slate", hi="white"),
        dict(m=knob, c="gold", lo="orange", hi="yellow"),
        dict(m=sign, c="slate", lo="dusk", hi="steel", hi_left=True),
        dict(m=_any(bell, _box(46, 2, 47, 4)), c="gold", lo="orange", hi="yellow", hi_left=True, line="orange"),
        dict(m=bellbase, c="slate", lo="dusk", hi="steel"),
        dict(m=body, c="steel", lo="slate", hi="ice", hi_left=True, line="dusk", lo_n=2),
    ])
    _R(img, 14, 4, 17, 6, "night")
    for x in (16, 20, 24, 28):
        _R(img, x, 5, 2, 4, "gold")
        _P(img, x + 1, 8, "orange")
    _P(img, 44, 6, "white"); _P(img, 43, 7, "white"); _P(img, 45, 5, "yellow")
    # key deck
    _R(img, 9, 15, 40, 12, "dusk")
    _R(img, 9, 15, 40, 1, "night")
    for r in range(3):
        for c in range(8):
            x, y = 11 + c * 5, 17 + r * 3
            col = "white"
            if (r, c) in ((0, 7), (1, 7)):
                col = "red"
            if (r, c) == (2, 7):
                col = "green"
            dark = {"white": "steel", "red": "wine", "green": "leaf"}[col]
            _P(img, x, y, col); _P(img, x + 1, y, col if col != "white" else "ice")
            _P(img, x, y + 1, dark); _P(img, x + 1, y + 1, dark)
    # gold trim and front plate
    _R(img, 6, 28, 46, 1, "gold"); _R(img, 6, 29, 46, 1, "orange")
    _R(img, 6, 36, 46, 1, "gold")
    _R(img, 22, 31, 14, 3, "gold"); _R(img, 22, 33, 14, 1, "orange"); _R(img, 23, 31, 4, 1, "yellow")
    for x in (10, 47):
        _R(img, x, 31, 2, 2, "gold"); _P(img, x + 1, 32, "orange")
    # drawer, popped open: dark tray with four compartments of coins, steel front with a gold pull
    dr = blank(W_, H_)
    _R(dr, 3, 37, 54, 6, "night")
    for x in (16, 29, 42):
        _R(dr, x, 37, 1, 6, "dusk")
    _R(dr, 2, 43, 56, 5, "steel")
    _R(dr, 2, 43, 56, 1, "ice")
    _R(dr, 2, 47, 56, 1, "slate")
    _R(dr, 54, 44, 4, 3, "slate")
    _R(dr, 26, 45, 8, 1, "gold"); _R(dr, 26, 46, 8, 1, "orange")
    for (x, y) in ((4, 40), (9, 40), (6, 38), (11, 37),
                   (17, 40), (22, 40), (19, 38), (24, 37),
                   (30, 40), (35, 40), (32, 38), (37, 38),
                   (43, 40), (48, 40), (45, 38), (50, 37)):
        _coin(dr, x, y)
    dr = _outline(dr)
    # a coin flipping out
    for (x, y, c) in ((54, 31, "ink"), (55, 31, "ink"), (53, 32, "ink"), (54, 32, "yellow"), (55, 32, "gold"), (56, 32, "ink"),
                      (53, 33, "ink"), (54, 33, "gold"), (55, 33, "orange"), (56, 33, "ink"), (54, 34, "ink"), (55, 34, "ink")):
        _P(dr, x, y, c)
    paste(img, dr, 0, 0)
    out = blank(W_, H_)
    paste(out, img, 0, 1)       # base on the last row
    return out


# ---------------------------------------------------------------- switch emblem

def switch_emblem(on=True):
    """16x16 gene switch, the same toggle as the panel on the macrophage's belly: a white switch body with the
    lever block at the top and green when on, at the bottom and slate when off."""
    img = blank(16, 16)
    _R(img, 4, 0, 8, 16, "ink"); _R(img, 3, 1, 10, 14, "ink")
    _R(img, 4, 1, 8, 14, "white"); _R(img, 11, 2, 1, 12, "ice")
    if on:
        _R(img, 5, 2, 6, 6, "green"); _R(img, 5, 2, 6, 1, "yellow"); _R(img, 5, 7, 6, 1, "leaf")
        _R(img, 5, 9, 6, 5, "ice")
    else:
        _R(img, 5, 2, 6, 5, "ice")
        _R(img, 5, 8, 6, 6, "slate"); _R(img, 5, 8, 6, 1, "steel"); _R(img, 5, 13, 6, 1, "dusk")
    return img


# ---------------------------------------------------------------- door

def _door_frame():
    """Stone frame for the 54x86 door. Returns (img, opening mask)."""
    W_, H_ = 54, 86
    acx, acy = 26.5, 28.0
    outer = lambda x, y: (1 <= x - 0.5 <= 52 and y - 0.5 >= acy and y - 0.5 <= 84) or ((x - acx) ** 2 + (y - acy) ** 2 <= 26.2 ** 2 and y - 0.5 <= acy)
    opening = lambda x, y: (10 <= x - 0.5 <= 43 and acy <= y - 0.5 <= 84) or ((x - acx) ** 2 + (y - acy) ** 2 <= 17.2 ** 2 and y - 0.5 < acy)
    img = blank(W_, H_)
    for y in range(H_):
        for x in range(W_):
            X, Y = x + 0.5, y + 0.5
            if not outer(X, Y) or opening(X, Y):
                continue
            # stone blocks: voussoirs on the arch, courses on the jambs
            if Y < acy:
                ang = math.degrees(math.atan2(Y - acy, X - acx)) % 360
                r = math.hypot(X - acx, Y - acy)
                seam = abs((ang - 180) % 22.5) < 1.6 or abs(r - 21.8) < 0.5
                pos = (ang % 22.5) / 22.5
                col = "steel"
                if seam:
                    col = "slate"
                elif pos < 0.18 or r > 25:
                    col = "ice"
                elif pos > 0.82:
                    col = "slate" if (x + y) % 2 else "steel"
            else:
                left = X < acx
                course = int((Y - acy) // 8)
                off = 4 if course % 2 else 0
                yy = (Y - acy) % 8
                jx = (X - 1) if left else (X - 44)
                seam = yy < 1 or (abs(jx - (4 + off)) < 0.6 and 0 < jx < 9)
                col = "steel"
                if seam:
                    col = "slate"
                elif yy < 2:
                    col = "ice"
                elif yy > 6.5:
                    col = "slate" if (x + y) % 2 else "steel"
            _P(img, x, y, col)
    # threshold step
    _R(img, 4, 83, 46, 2, "slate"); _R(img, 4, 83, 46, 1, "steel")
    return img, outer, opening


def _door_leaf(img, opening, glow=False):
    for y in range(86):
        for x in range(54):
            X, Y = x + 0.5, y + 0.5
            if not opening(X, Y) or y > 82:
                continue
            p = (x - 10) % 6
            col = "clay"
            if p == 0:
                col = "brown"
            elif p == 1:
                col = "tan"
            elif p == 5:
                col = "brown" if (y % 3) else "clay"
            elif p == 3 and ((x // 6) * 5 + y // 7) % 3 == 0 and y % 7 < 4:
                col = "brown"
            _P(img, x, y, col)
    for y in range(9, 83):
        for x in range(10, 44):
            if opening(x + 0.5, y + 0.5) and not opening(x + 0.5, y - 1.5):
                _P(img, x, y, "brown")
    for x in range(10, 44):
        if opening(x + 0.5, 0.5 + 33):
            _P(img, x, 32, "slate"); _P(img, x, 33, "dusk"); _P(img, x, 31, "steel")
        _P(img, x, 64, "steel"); _P(img, x, 65, "slate"); _P(img, x, 66, "dusk")
    for x in range(12, 43, 6):
        _P(img, x, 32, "ice"); _P(img, x, 65, "ice")
    for (dx, dy, c) in ((0, -2, "gold"), (1, -2, "gold"), (-1, -1, "gold"), (2, -1, "orange"), (-1, 0, "gold"),
                        (2, 0, "orange"), (-1, 1, "orange"), (2, 1, "rust"), (0, 2, "orange"), (1, 2, "rust"),
                        (0, -3, "slate"), (1, -3, "slate")):
        _P(img, 37 + dx, 50 + dy, c)
    _P(img, 36, 47, "yellow")
    for y in range(86):
        for x in range(54):
            X, Y = x + 0.5, y + 0.5
            if opening(X, Y) and y <= 82:
                if any(not opening(X + dx, Y + dy) for dx, dy in ((1, 0), (-1, 0), (0, -1))):
                    _P(img, x, y, "yellow" if glow else "ink")
    return img


def door(state="closed", inside="none"):
    """54x86, last row is the floor. state: closed, open, lit. inside='castle' puts a tiny castle in the open doorway."""
    img, outer, opening = _door_frame()
    if state == "open":
        for y in range(86):
            for x in range(54):
                X, Y = x + 0.5, y + 0.5
                if not opening(X, Y) or y > 82:
                    continue
                col = "white"
                if y >= 64:
                    col = "ice" if ((x + y) % 2 == 0 and y < 72) or y >= 72 and (x + y) % 4 else "white"
                if y == 64:
                    col = "ice"
                if min(x - 10, 43 - x) < 1 or not opening(X, Y - 2):
                    col = "ice"
                _P(img, x, y, col)
        if inside == "castle":
            c = _small_castle()
            paste(img, c, 28 - c.width // 2, 66 - c.height)
            for x in range(18, 39):
                if x % 2:
                    _P(img, x, 66, "steel")
        from PIL import ImageDraw
        lf = blank(54, 86)
        ImageDraw.Draw(lf).polygon([(10, 18), (17, 25), (17, 79), (10, 82)], fill=rgba("clay"))
        for y in range(86):
            for x in range(54):
                if lf.getpixel((x, y))[3]:
                    col = "clay" if (x - 10) % 3 else "brown"
                    if x >= 16:
                        col = "brown"
                    if y in (36, 37, 66, 67):
                        col = "dusk"
                    _P(lf, x, y, col)
        _outline(lf)
        paste(img, lf, 0, 0)
        for x in range(12, 43):
            if x % 2:
                _P(img, x, 83, "ice")
    else:
        _door_leaf(img, opening, glow=(state == "lit"))
        if state == "lit":
            # warm light spilling from the door's edges onto the stone
            for y in range(86):
                for x in range(54):
                    X, Y = x + 0.5, y + 0.5
                    if opening(X, Y) or not outer(X, Y) or y > 82:
                        continue
                    d1 = any(opening(X + dx, Y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    d2 = any(opening(X + dx, Y + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))
                    d3 = any(opening(X + dx, Y + dy) for dx in (-3, 0, 3) for dy in (-3, 0, 3))
                    if d1:
                        _P(img, x, y, "yellow")
                    elif d2 and (x + y) % 2 == 0:
                        _P(img, x, y, "gold")
                    elif d3 and x % 2 == 0 and y % 2 == 0:
                        _P(img, x, y, "gold")
            # the glowing switch emblem
            ecx, ecy = 27, 45
            for y in range(ecy - 13, ecy + 14):
                for x in range(ecx - 13, ecx + 14):
                    r = math.hypot(x + 0.5 - ecx, y + 0.5 - ecy)
                    if 9.5 < r <= 11 and (x + y) % 2 == 0:
                        _P(img, x, y, "yellow")
                    elif 11 < r <= 12.5 and x % 2 == 0 and y % 2 == 0:
                        _P(img, x, y, "gold")
            sq = blank(18, 18); _R(sq, 0, 0, 18, 18, "yellow")
            for (x, y) in ((0, 0), (17, 0), (0, 17), (17, 17)):
                _P(sq, x, y, None)
            paste(img, sq, 18, 36)
            paste(img, switch_emblem(on=True), 19, 37)
            for x in range(10, 44):
                _P(img, x, 82, "yellow")
            for x in range(4, 50):
                _P(img, x, 83, "yellow" if 10 <= x <= 43 else ("gold" if x % 2 else "steel"))
                if 6 <= x <= 47 and x % 2 == 0:
                    _P(img, x, 84, "gold")
    sil = blank(54, 86)
    _fill(sil, outer, "steel")
    o = _outline(sil.copy())
    for y in range(86):
        for x in range(54):
            if _G(o, x, y) == "ink" and not sil.getpixel((x, y))[3]:
                _P(img, x, y, "ink")
    _R(img, 0, 85, 54, 1, "ink")
    return img


def _small_castle():
    """A tiny wine castle, 26x22, for the doorway."""
    battl = lambda x0, x1, y0: (lambda x, y: y0 <= y - 0.5 <= y0 + 1 and x0 <= x - 0.5 <= x1 and ((int(x - 0.5) - x0) % 3) < 2)
    keep = _any(_box(9, 6, 16, 20), battl(9, 16, 4))
    wall = _any(_box(5, 12, 20, 20), battl(5, 20, 10))
    lt = _any(_box(1, 8, 6, 20), battl(1, 6, 6))
    rt = _any(_box(19, 8, 24, 20), battl(19, 24, 6))
    pole = _box(12, 0, 12, 3)
    flag = _box(13, 0, 17, 2)
    img = _parts(26, 22, [
        dict(m=pole, c="slate"),
        dict(m=flag, c="red", lo="wine"),
        dict(m=keep, c="wine", lo="plum", hi="red", hi_left=True, line="ink"),
        dict(m=wall, c="wine", lo="plum", hi="red", line="ink"),
        dict(m=lt, c="wine", lo="plum", hi="red", hi_left=True, line="ink"),
        dict(m=rt, c="wine", lo="plum", hi="red", hi_left=True, line="ink"),
    ])
    _R(img, 11, 15, 4, 6, "plum"); _R(img, 12, 14, 2, 1, "plum")
    _P(img, 12, 16, "ink"); _P(img, 13, 16, "ink")
    _R(img, 3, 12, 1, 2, "ink"); _R(img, 22, 12, 1, 2, "ink")
    _P(img, 14, 1, "ink"); _P(img, 16, 1, "ink")
    return img


# ---------------------------------------------------------------- crate

def _floppy(col, dark):
    img = blank(10, 10)
    _R(img, 1, 1, 8, 8, col)
    _R(img, 7, 1, 2, 8, dark); _R(img, 1, 8, 8, 1, dark)
    _R(img, 3, 1, 4, 3, "steel"); _P(img, 5, 2, "dusk"); _R(img, 3, 1, 4, 1, "ice")
    _R(img, 2, 5, 6, 3, "white"); _R(img, 7, 5, 1, 3, "ice")
    _P(img, 1, 1, None)
    return _outline(img)


def _drive():
    img = blank(13, 12)
    _R(img, 1, 1, 11, 10, "slate")
    _R(img, 1, 1, 11, 1, "steel"); _R(img, 10, 2, 2, 9, "dusk"); _R(img, 1, 10, 11, 1, "dusk")
    _R(img, 3, 3, 6, 5, "ice"); _R(img, 3, 3, 6, 1, "white"); _R(img, 8, 4, 1, 4, "steel")
    _R(img, 4, 5, 3, 1, "steel")
    for (x, y) in ((2, 2), (10, 2), (2, 9), (10, 9)):
        _P(img, x, y, "ink" if (x, y) != (2, 2) else "steel")
    _P(img, 10, 8, "green")
    return _outline(img)


def _tube(cap, liq, h=15):
    img = blank(6, h)
    _R(img, 1, 1, 4, 3, cap); _R(img, 4, 1, 1, 3, {"red": "wine", "sky": "navy", "green": "leaf", "gold": "orange", "grape": "plum"}[cap])
    _R(img, 1, 1, 4, 1, {"red": "rose", "sky": "cyan", "green": "yellow", "gold": "yellow", "grape": "pink"}[cap])
    _R(img, 1, 4, 4, h - 5, "white"); _R(img, 4, 4, 1, h - 5, "ice")
    _R(img, 1, h // 2 + 1, 4, h - 2 - (h // 2 + 1), liq)
    _P(img, 2, h - 2, None); _P(img, 1, h - 2, None)
    _R(img, 2, h - 2, 2, 1, liq)
    return _outline(img)


def crate():
    """44x34, base on the last row: a wooden crate packed with data (drives, floppies, sample tubes), a sticker."""
    img = blank(44, 34)
    paste(img, _tube("sky", "cyan", 17), 37, 2)
    paste(img, _tube("red", "rose", 19), 33, 0)
    paste(img, _tube("green", "green", 16), 29, 4)
    paste(img, _floppy("navy", "night"), 19, 7)
    paste(img, _floppy("red", "wine"), 12, 5)
    paste(img, _drive(), 1, 9)
    cr = blank(44, 34)
    _R(cr, 1, 17, 42, 16, "tan")
    for (y0, h) in ((17, 5), (22, 5), (27, 6)):
        _R(cr, 1, y0, 42, 1, "sand")
        _R(cr, 1, y0 + h - 1, 42, 1, "brown")
        _R(cr, 40, y0, 2, h, "clay")
    for x0 in (1, 37):
        _R(cr, x0, 17, 5, 16, "clay")
        _R(cr, x0, 17, 1, 16, "tan")
        _R(cr, x0 + 4, 17, 1, 16, "brown")
        for y in (19, 30):
            _P(cr, x0 + 2, y, "slate")
    for (x, y, n) in ((9, 19, 4), (28, 19, 3), (12, 29, 3)):
        _R(cr, x, y, n, 1, "clay")
    _R(cr, 1, 32, 42, 1, "brown")
    _R(cr, 21, 22, 14, 9, "white")
    _R(cr, 33, 23, 2, 8, "ice"); _R(cr, 21, 30, 14, 1, "ice")
    _R(cr, 21, 22, 14, 2, "sky")
    for x, w in ((23, 1), (25, 2), (28, 1), (30, 1), (32, 1)):
        _R(cr, x, 25, w, 4, "ink")
    paste(img, cr, 0, 0)
    _outline(img)
    _R(img, 1, 16, 42, 1, "ink")
    return img


# ---------------------------------------------------------------- big question mark

_QM = [
    "......XXXXXXXXX......",
    "....XXXXXXXXXXXXX....",
    "...XXXXXXXXXXXXXXX...",
    "..XXXXXXXXXXXXXXXXX..",
    ".XXXXXXX.....XXXXXXX.",
    ".XXXXXX.......XXXXXX.",
    ".XXXXXX.......XXXXXXX",
    ".XXXXXX.......XXXXXXX",
    "..XXXX........XXXXXXX",
    "..............XXXXXXX",
    ".............XXXXXXXX",
    "............XXXXXXXX.",
    "...........XXXXXXXX..",
    "..........XXXXXXXX...",
    ".........XXXXXXX.....",
    "........XXXXXXX......",
    "........XXXXXX.......",
    "........XXXXXX.......",
    "........XXXXXX.......",
    "........XXXXXX.......",
    "........XXXXXX.......",
    "........XXXXXX.......",
    ".....................",
    ".....................",
    ".....................",
    ".....................",
    ".........XXXX........",
    "........XXXXXX.......",
    "........XXXXXX.......",
    "........XXXXXX.......",
    "........XXXXXX.......",
    "........XXXXXX.......",
    ".........XXXX........",
]


def big_question():
    """26x38 chunky 3D question mark, gold/yellow/orange, ink outline."""
    W_, H_ = 26, 38

    def on(x, y):
        return 0 <= y < len(_QM) and 0 <= x < len(_QM[0]) and _QM[y][x] == "X"
    img = blank(W_, H_)
    # extrusion, down-right
    for k in (3, 2, 1):
        for y in range(len(_QM)):
            for x in range(len(_QM[0])):
                if on(x, y):
                    _P(img, x + 1 + k, y + 1 + k, "rust" if k == 3 else "orange")
    for y in range(len(_QM)):
        for x in range(len(_QM[0])):
            if not on(x, y):
                continue
            col = "yellow"
            if not on(x + 1, y) or not on(x, y + 1):
                col = "gold"
            if not on(x, y - 1) or not on(x - 1, y):
                col = "white" if (not on(x, y - 1) and not on(x - 1, y)) else "yellow"
            _P(img, x + 1, y + 1, col)
    # a shine streak on the hook, gold shading inside the curve
    for (x, y) in ((4, 3), (5, 2), (6, 2), (3, 4), (3, 5)):
        _P(img, x + 1, y + 1, "white")
    for (x, y) in ((8, 4), (9, 4), (10, 4), (11, 4), (12, 4), (7, 5), (7, 6), (7, 7)):
        if on(x, y):
            _P(img, x + 1, y + 1, "gold")
    _P(img, 10, 28, "white"); _P(img, 10, 29, "white")
    return _outline(img)


# ---------------------------------------------------------------- for rent tag

def for_rent_tag():
    """46x26 hanging price tag: string at the top-left, sand paper, FOR RENT in ink."""
    from PIL import ImageDraw
    img = blank(46, 26)
    pts = [(9, 1), (45, 1), (45, 25), (9, 25), (1, 18), (1, 8)]
    ImageDraw.Draw(img).polygon(pts, fill=rgba("sand"), outline=rgba("ink"))
    for y in range(2, 25):
        _P(img, 44, y, "tan")
    for x in range(9, 45):
        _P(img, x, 24, "tan")
    # lower chamfer shadow
    for i in range(7):
        _P(img, 2 + i, 18 + i, "tan")
    # hole with a reinforcement ring
    for (x, y, c) in ((5, 11, "tan"), (6, 11, "tan"), (4, 12, "tan"), (7, 12, "tan"), (4, 13, "tan"), (7, 13, "tan"),
                      (5, 14, "tan"), (6, 14, "tan"), (5, 12, "ink"), (6, 12, "ink"), (5, 13, "ink"), (6, 13, "ink")):
        _P(img, x, y, c)
    _text_center(img, "FOR", "ink", 27, 3)
    _text_center(img, "RENT", "ink", 27, 14)
    # string: from the hole up to the top-left corner
    _ln(img, 5, 12, 2, 0, "brown")
    _ln(img, 6, 12, 3, 0, "clay")
    return img


# ---------------------------------------------------------------- terminal (the compiler)

def terminal(arms="down"):
    """90x70: a chunky retro CRT terminal as a character, on a stand with stubby feet and two stubby arms.
    Screen x 8..81, y 8..51 is plain night. arms: down, hold (hands at about (45, 62)), reach (right arm up-right)."""
    W_, H_ = 90, 70
    img = blank(W_, H_)
    legs = _parts(W_, H_, [
        dict(m=_box(39, 57, 50, 61), c="dusk", lo="night", hi="slate"),
        dict(m=_box(31, 61, 58, 63), c="slate", lo="dusk", hi="steel", hi_left=True),
        dict(m=_any(_ell(34.0, 66.0, 6.5, 2.8), _box(31, 63, 39, 66)), c="slate", lo="dusk", hi="steel", line="dusk"),
        dict(m=_any(_ell(56.0, 66.0, 6.5, 2.8), _box(51, 63, 59, 66)), c="slate", lo="dusk", hi="steel", line="dusk"),
    ])
    for x in range(26, 64):
        if _G(legs, x, 68) in ("slate", "dusk", "steel"):
            _P(legs, x, 68, "white")
    paste(img, legs, 0, 0)
    case = blank(W_, H_)
    # box in oblique view: top face and right side recede up-right by 3px
    D = 3
    for k in range(D):              # top face rows y 1..3
        y = 1 + k
        for x in range(4 + D - k, 86 + D - k):
            _P(case, x, y, "ice" if k == 0 else "steel")
    for k in range(D):              # right side columns x 86..88
        x = 86 + k
        for y in range(4 - k, 57 - k):
            _P(case, x, y, "dusk" if k < 2 else "night")
    for y in range(4, 58):          # front face
        for x in range(3, 86):
            if (x, y) in ((3, 4), (3, 57), (85, 57)):
                continue
            col = "slate"
            if y == 4 or x == 3:
                col = "steel"
            if y >= 56 or x >= 84:
                col = "dusk"
            _P(case, x, y, col)
    # vents on the top face
    for x in range(34, 62, 3):
        _P(case, x, 2, "slate"); _P(case, x + 1, 2, "slate")
    # bevel around the screen: dark lip, lit lower-right inner edge
    _R(case, 6, 6, 78, 48, "dusk")
    _R(case, 7, 7, 76, 46, "ink")
    _R(case, 6, 53, 78, 1, "steel")
    _R(case, 83, 6, 1, 48, "steel")
    _R(case, 8, 8, 74, 44, "night")
    # chin: floppy slot, knobs, power light
    _R(case, 10, 55, 18, 1, "ink"); _R(case, 10, 56, 18, 1, "steel")
    for kx in (64, 70):
        _R(case, kx, 54, 3, 3, "steel"); _P(case, kx, 54, "ice"); _P(case, kx + 2, 56, "dusk")
    _R(case, 76, 55, 3, 1, "green"); _P(case, 76, 55, "yellow")
    _outline(case)
    paste(img, case, 0, 0)

    def arm(pts, hand, th=1):
        sx, sy = pts[0]
        lay = blank(W_, H_)
        for y in range(H_):
            for x in range(W_):
                if (x + 0.5 - sx) ** 2 + (y + 0.5 - sy) ** 2 <= 6.5:
                    _P(lay, x, y, "ink" if (x + 0.5 - sx) ** 2 + (y + 0.5 - sy) ** 2 > 3 else "night")
        a = _parts(W_, H_, [dict(m=_poly_cap(pts, 1.6), c="steel", lo="slate", hi="ice")])
        lay.alpha_composite(a)
        hx, hy = hand
        hm = _parts(W_, H_, [dict(m=_any(_ell(hx, hy, 3.8, 3.5), _ell(hx + th * 2.6, hy - 2.5, 1.5, 1.5)),
                                  c="white", lo="ice", hi=None, line="ice")])
        lay.alpha_composite(hm)
        return lay
    if arms == "hold":
        L = arm([(5.5, 40), (3.5, 51), (10, 59), (31, 62)], (34.0, 61.5), -1)
        R = arm([(83.5, 40), (86.5, 51), (80, 59), (59, 62)], (56.0, 61.5), 1)
    elif arms == "reach":
        L = arm([(5.5, 40), (3.0, 50), (4.5, 57)], (5.5, 61.0), 1)
        R = arm([(83.5, 40), (87.0, 30), (86.0, 14)], (85.0, 7.5), -1)
    else:
        L = arm([(5.5, 40), (3.0, 50), (4.5, 57)], (5.5, 61.0), 1)
        R = arm([(83.5, 40), (87.0, 50), (85.5, 57)], (84.5, 61.0), -1)
    paste(img, L, 0, 0)
    paste(img, R, 0, 0)
    return img


def _coin(img, x, y):
    for (dx, dy, c) in ((1, 0, "gold"), (2, 0, "yellow"), (3, 0, "gold"),
                        (0, 1, "orange"), (1, 1, "gold"), (2, 1, "gold"), (3, 1, "gold"), (4, 1, "orange"),
                        (1, 2, "orange"), (2, 2, "rust"), (3, 2, "rust")):
        _P(img, x + dx, y + dy, c)
