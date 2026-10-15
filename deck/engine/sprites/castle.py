"""Castle props: the tumor castle and its hill, the fibroblast wall, the chemo IV stand and drops, the alarm clock,
the immunotherapy syringe, ball and chain, the magnifier and stopwatch of the crash course, and the gold (sack,
coins, money bag). Every function returns RGBA of exactly its spec size; Endesga 32 only, 1px ink outline on every
outer silhouette, light from the top-left."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image, ImageDraw
from px import ascii_sprite, blank, line
from pal import rgba, C


# ----------------------------------------------------------------------------------------------- helpers
def _P(img, x, y, col, a=255):
    if col and 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((int(x), int(y)), rgba(col, a) if isinstance(col, str) else col)


def _R(img, x, y, w, h, col):
    if w > 0 and h > 0:
        ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=rgba(col))


def _ln(img, x0, y0, x1, y1, col):
    line(img, int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)), col)


def _spr(rows, key):
    return ascii_sprite([r for r in rows.strip("\n").split("\n")], key)


def _over(img, src, x=0, y=0):
    img.alpha_composite(src, (int(x), int(y)))
    return img


def _nb(m, dx, dy):
    """m sampled at (x+dx, y+dy), False outside."""
    h, w = m.shape
    out = np.zeros_like(m)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    if ys1 > ys0 and xs1 > xs0:
        out[ys0:ys1, xs0:xs1] = m[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
    return out


def _grid(w, h):
    return np.mgrid[0:h, 0:w]


def _mpoly(w, h, *polys):
    m = Image.new("1", (w, h), 0)
    d = ImageDraw.Draw(m)
    for pts in polys:
        d.polygon([tuple(p) for p in pts], fill=1)
    return np.array(m, dtype=bool)


def _mell(w, h, *ells):
    """ells: (cx, cy, rx, ry), pixel-centred."""
    m = np.zeros((h, w), bool)
    yy, xx = _grid(w, h)
    for (cx, cy, rx, ry) in ells:
        m |= ((xx - cx) / (rx + 0.5)) ** 2 + ((yy - cy) / (ry + 0.5)) ** 2 <= 1.0
    return m


def _mrect(w, h, *rects):
    m = np.zeros((h, w), bool)
    for (x, y, rw, rh) in rects:
        m[max(0, y):max(0, y + rh), max(0, x):max(0, x + rw)] = True
    return m


def _paint(img, m, col):
    arr = np.array(img)
    arr[m] = rgba(col) if isinstance(col, str) else col
    img.paste(Image.fromarray(arr), (0, 0))
    return img


def _edge_br(m, k=1):
    """Pixels of m within k px of its bottom/right border."""
    band = np.zeros_like(m)
    for i in range(1, k + 1):
        band |= ~_nb(m, i, 0) | ~_nb(m, 0, i) | ~_nb(m, i, i)
    return m & band


def _edge_tl(m, k=1):
    band = np.zeros_like(m)
    for i in range(1, k + 1):
        band |= ~_nb(m, -i, 0) | ~_nb(m, 0, -i)
    return m & band


def _inner(m):
    return m & _nb(m, 1, 0) & _nb(m, -1, 0) & _nb(m, 0, 1) & _nb(m, 0, -1)


def _ring(m):
    """4-neighbour ring just outside m."""
    return ~m & (_nb(m, 1, 0) | _nb(m, -1, 0) | _nb(m, 0, 1) | _nb(m, 0, -1))


def _alpha(img):
    return np.array(img)[:, :, 3] > 0


def _ol(img, col="ink"):
    """In-place 1px outline around opaque pixels, only on transparent pixels."""
    return _paint(img, _ring(_alpha(img)), col)


def _checker(w, h, phase=0):
    yy, xx = _grid(w, h)
    return (xx + yy + phase) % 2 == 0


def _sphere(img, m, cx, cy, r, ramp, cuts, light=(-0.6, -0.65, 0.48)):
    """Fill mask m with a lit-sphere ramp (light -> dark). cuts: descending thresholds, len(ramp) - 1."""
    lx, ly, lz = light
    n = math.sqrt(lx * lx + ly * ly + lz * lz); lx, ly, lz = lx / n, ly / n, lz / n
    arr = np.array(img)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
        dz = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
        v = dx * lx + dy * ly + dz * lz
        i = 0
        while i < len(cuts) and v < cuts[i]:
            i += 1
        arr[y, x] = rgba(ramp[i])
    img.paste(Image.fromarray(arr), (0, 0))
    return img


def _star4(img, x, y, col="yellow", core="white", big=False):
    _P(img, x, y, core)
    for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        _P(img, x + d[0], y + d[1], col)
    if big:
        for d in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            _P(img, x + d[0], y + d[1], col)


# ----------------------------------------------------------------------------------------------- castle
TUMOR_FACE = """
......KKK...KKKK......
....KKRRRKKKRRRRKK....
...KRRrrRRRRRRRRRRK...
..KRrrRRRRRRRRRRRRRK..
.KRrRKKRRRRRRRRRKKRRK.
.KRRRRKKKRRRRKKKRRRRK.
KRRRRWWWKKRRKKWWWRRRPK
KRRRRWWKKKRRKKKWWRRRPK
KRRRRWWKKKRRKKKWWRRPPK
.KRRRRWWWRRRRRWWWRRRPK
.KRRRRRRRRRRRRRRRRRPPK
KRRRRRRKKKKKKKKRRRRPPK
KRRRRRKRRRRRRRRKRRPPK.
.KPRRRRRRRRRRRRRRPPPK.
..KKPPPPKKPPPPPPPPKK..
....KKKK..KKKKKKKK....
"""


def _tumor_face():
    """The tumor's grumpy lumpy blob face, 22x16, for the castle flag."""
    return _spr(TUMOR_FACE, {"K": "ink", "R": "wine", "r": "red", "W": "white", "P": "plum"})


def _hash(v, seed=0):
    return (v * 2654435761 + seed * 40503) % 1000


def _stone(img, m, lit, shadow, bw=8, bh=5, x0=0, y0=0, seed=0):
    """Wine stone blocks in mask m (running bond), plum joints, red glints on some blocks, a red rim-lit band
    `lit` and a plum shadow band `shadow`."""
    h, w = m.shape
    yy, xx = _grid(w, h)
    r = (yy - y0) % bh
    row = (yy - y0) // bh
    cpos = (xx - x0 + (row % 2) * (bw // 2)) % bw
    bid = row * 97 + (xx - x0 + (row % 2) * (bw // 2)) // bw
    mortar = (r == bh - 1) | (cpos == bw - 1)
    hv = np.vectorize(lambda v: _hash(int(v), seed))(bid)
    _paint(img, m, "wine")
    _paint(img, m & mortar, "plum")
    _paint(img, m & (r == 0) & (cpos <= 2) & (hv < 160) & ~mortar, "red")
    _paint(img, m & (r == bh - 2) & (cpos >= bw - 4) & (hv > 760) & ~mortar, "plum")
    _paint(img, m & lit & ~mortar, "red")
    _paint(img, m & lit & mortar, "wine")
    _paint(img, m & shadow, "plum")
    return img


def _merlons(W, H, x0, x1, y0, mh, mw, gw):
    """Crenellation mask spanning x0..x1 inclusive: merlons mw wide, gaps gw, outer merlons absorb the slack."""
    span = x1 - x0 + 1
    n = max(2, (span + gw) // (mw + gw))
    inner = span - 2 * mw - (n - 1) * gw - (n - 2) * mw
    lo = inner // 2
    out = np.zeros((H, W), bool)
    xs = [x0]
    x = x0 + mw + lo + gw
    for i in range(n - 2):
        xs.append(x); x += mw + gw
    widths = [mw + lo] + [mw] * (n - 2) + [x1 + 1 - x]
    xs.append(x)
    for xa, ww in zip(xs, widths):
        out |= _mrect(W, H, (xa, y0, ww, mh))
    return out


def castle():
    """120x100, last row on the ground: the tumor as a castle. Crenellated side towers, a central keep with
    scowling lit windows, a curtain wall with an arched gate (x 50..69, 24 tall) and a half-raised portcullis,
    and a flag with the tumor's grumpy face."""
    W, H = 120, 100
    yy, xx = _grid(W, H)
    chk = _checker(W, H)
    img = blank(W, H)

    # ---------------- keep
    keep_l = blank(W, H)
    kx0, kx1, ktop = 40, 79, 30
    kbody = _mrect(W, H, (kx0, ktop + 9, kx1 - kx0 + 1, H - ktop - 9))
    kpara = _mrect(W, H, (kx0 - 2, ktop + 5, kx1 - kx0 + 5, 4)) | _merlons(W, H, kx0 - 2, kx1 + 2, ktop, 5, 5, 3)
    keep = kbody | kpara
    klit = (kbody & (xx <= kx0 + 1)) | (kpara & (xx <= kx0 - 1))
    ksh = keep & ((xx >= kx1 - 3) | ((xx >= kx1 - 5) & chk))
    ksh |= kbody & (yy <= ktop + 10)
    _stone(keep_l, keep, klit, ksh, bw=8, bh=5, x0=kx0, y0=ktop, seed=1)
    _paint(keep_l, kpara & (yy == ktop + 5) & ~ksh, "red")
    _paint(keep_l, kpara & (yy == ktop) & ~ksh, "red")
    # scowling windows: lit eyes under heavy brows
    for (wx, fl) in ((47, False), (64, True)):
        rows = ["KKKK.....",
                "KGGKKK...",
                "KYGGGKKK.",
                "KYYGGGOKK",
                "KYYYGGOK.",
                "KKKKKKKK."]
        if fl:
            rows = [r[::-1] for r in rows]
        _over(keep_l, _spr("\n".join(rows), {"K": "ink", "G": "gold", "Y": "yellow", "O": "orange"}), wx, 44)
    _ol(keep_l)

    # ---------------- flag (pole planted in the keep's middle merlon)
    flag_l = blank(W, H)
    px_ = 59
    _R(flag_l, px_, 2, 2, ktop - 1, "brown")
    _R(flag_l, px_, 2, 1, ktop - 1, "tan")
    _R(flag_l, px_ - 1, 0, 4, 2, "gold"); _P(flag_l, px_ - 1, 0, "yellow")
    fw, fh = 28, 21
    fx0, fy0 = px_ + 2, 3
    flag = np.zeros((H, W), bool)
    offs = []
    for x in range(fw):
        t = x / (fw - 1)
        off = round(1.6 * math.sin(t * math.pi * 1.5))
        offs.append(off)
        top, bot = fy0 + off, fy0 + fh - 1 + off
        flag[top:bot + 1, fx0 + x] = True
        if x >= fw - 6:   # swallowtail notch
            n = x - (fw - 7)
            mid = (top + bot) // 2
            flag[mid - n + 1:mid + n, fx0 + x] = False
    _paint(flag_l, flag, "sand")
    fold = np.zeros_like(flag)
    for x in range(fw):
        if math.cos(x / (fw - 1) * math.pi * 1.5) < -0.3:
            fold[:, fx0 + x] = True
    _paint(flag_l, flag & fold & ~_nb(fold, 3, 0) & chk, "tan")
    _paint(flag_l, flag & fold & _nb(fold, 3, 0) & ~_nb(fold, -2, 0), "tan")
    _paint(flag_l, flag & _edge_br(flag, 1), "tan")
    _paint(flag_l, flag & (xx <= fx0 + 1), "tan")
    _paint(flag_l, flag & ~_nb(flag, 0, -1) & ~fold, "white")
    _over(flag_l, _tumor_face(), fx0 + 2, fy0 + 3)
    _ol(flag_l)

    # ---------------- curtain wall with the gate
    curt_l = blank(W, H)
    cx0, cx1, ctop = 22, 97, 60
    cbody = _mrect(W, H, (cx0, ctop + 5, cx1 - cx0 + 1, H - ctop - 5))
    curt = cbody | _merlons(W, H, cx0, cx1, ctop, 5, 5, 3)
    csh = cbody & (yy <= ctop + 6)                                   # under the battlement lip
    csh |= cbody & (xx >= 27) & (xx <= 28)                            # left tower's cast shadow
    csh |= cbody & (xx >= 29) & (xx <= 31) & chk
    csh |= curt & (xx >= cx1 - 2)
    _stone(curt_l, curt, np.zeros_like(curt), csh, bw=9, bh=5, x0=cx0, y0=ctop, seed=2)
    _paint(curt_l, curt & (yy == ctop) & ~csh, "red")
    _paint(curt_l, cbody & (yy == ctop + 5) & ~(xx >= cx1 - 2), "red")
    # gate
    gx0, gw, gh = 50, 20, 24
    gy0 = H - gh
    r = gw / 2
    gcx, gcy = gx0 + r, gy0 + r
    d = np.sqrt((xx + 0.5 - gcx) ** 2 + (yy + 0.5 - gcy) ** 2)
    gate = (_mrect(W, H, (gx0, int(gcy), gw, H - int(gcy)))) | ((d <= r) & (yy < gcy))
    # voussoirs: a 3px ring of alternating stones, jambs below the spring line
    vous = (d > r) & (d <= r + 3.2) & (yy < gcy)
    jamb = (((xx >= gx0 - 3) & (xx < gx0)) | ((xx > gx0 + gw - 1) & (xx <= gx0 + gw + 2))) & (yy >= gcy)
    ang = np.degrees(np.arctan2(gcy - (yy + 0.5), xx + 0.5 - gcx))
    seg = np.floor(ang / 20).astype(int)
    _paint(curt_l, vous, "wine")
    _paint(curt_l, vous & (seg % 2 == 0), "red")
    _paint(curt_l, vous & (xx >= gcx + 2) & (seg % 2 == 0), "wine")
    _paint(curt_l, vous & (xx >= gcx + 2) & (seg % 2 == 1), "plum")
    _paint(curt_l, vous & (np.abs(ang - 90) < 9) & (d > r + 0.5), "red")   # keystone
    _paint(curt_l, vous & (d > r + 2.4), "plum")
    _paint(curt_l, jamb & (xx < gcx), "red")
    _paint(curt_l, jamb & (xx > gcx), "plum")
    _paint(curt_l, jamb & ((yy - int(gcy)) % 5 == 4), "wine")
    _paint(curt_l, gate, "plum")
    _paint(curt_l, gate & (yy <= gy0 + 4), "ink")
    _paint(curt_l, gate & _nb(~gate, 0, 0) & (_ring(~gate & ~_nb(gate, 0, 0)) | _ring(~gate)), "ink")
    _paint(curt_l, gate & (_nb(~gate, -1, 0) | _nb(~gate, 0, -1)), "ink")
    # portcullis, half raised, its spikes like teeth
    pc_bot = gy0 + 11
    grid = gate & (yy <= pc_bot) & (yy >= gy0 + 1) & (((xx - gx0) % 4 == 2) | ((yy - gy0) % 4 == 3))
    grid &= ~(_nb(~gate, -1, 0) | _nb(~gate, 1, 0))
    _paint(curt_l, grid, "slate")
    _paint(curt_l, grid & ((yy - gy0) % 4 == 3) & ((xx - gx0) % 4 == 2), "ice")
    _paint(curt_l, grid & ((xx - gx0) % 4 == 2) & ((yy - gy0) % 4 != 3) & (xx > gcx + 3), "dusk")
    for bx in range(gx0 + 2, gx0 + gw - 1, 4):
        _P(curt_l, bx, pc_bot + 1, "steel"); _P(curt_l, bx, pc_bot + 2, "slate"); _P(curt_l, bx, pc_bot + 3, "dusk")
    _paint(curt_l, gate & (yy >= H - 3) & chk & (yy > pc_bot + 4), "ink")
    _ol(curt_l)

    # ---------------- towers
    def tower(bx0, seed):
        L = blank(W, H)
        bw, ptop = 22, 12
        body = _mrect(W, H, (bx0, ptop + 14, bw, H - ptop - 14)) | _mrect(W, H, (bx0 - 1, H - 9, bw + 2, 9))
        para = _mrect(W, H, (bx0 - 2, ptop + 6, bw + 4, 8)) | _merlons(W, H, bx0 - 2, bx0 + bw + 1, ptop, 6, 5, 2)
        corb = np.zeros_like(body)
        for i in range(0, bw + 4, 4):
            corb |= _mrect(W, H, (bx0 - 2 + i, ptop + 14, 2, 1))
            corb |= _mrect(W, H, (bx0 - 1 + i, ptop + 15, 1, 1)) & ~body
        t = body | para | corb
        lit = (body & (xx <= bx0 + 1)) | (para & (xx <= bx0 - 1))
        sh = t & ((xx >= bx0 + bw - 5) | ((xx >= bx0 + bw - 7) & chk))
        sh |= body & (yy <= ptop + 15)
        sh |= corb
        _stone(L, t, lit, sh, bw=7, bh=5, x0=bx0, y0=ptop, seed=seed)
        _paint(L, para & (yy == ptop + 6) & _nb(para, 0, 1) & ~sh, "red")
        _paint(L, para & (yy == ptop) & ~sh, "red")
        _paint(L, para & (yy == ptop + 13), "plum")
        # arrow slits with a hot glow
        for sy in (36, 68):
            sx = bx0 + 9
            _R(L, sx - 1, sy - 1, 4, 9, "plum")
            _R(L, sx, sy, 2, 7, "ink")
            _P(L, sx, sy + 2, "orange"); _P(L, sx, sy + 3, "gold"); _P(L, sx + 1, sy + 3, "orange"); _P(L, sx, sy + 4, "orange")
            _R(L, sx - 1, sy + 8, 4, 1, "red")   # sill
        _ol(L)
        return L

    for L in (keep_l, flag_l, curt_l, tower(4, 3), tower(94, 4)):
        img.alpha_composite(L)
    # ground line
    a = _alpha(img)
    _paint(img, a & (yy == H - 1), "ink")
    return img


# ----------------------------------------------------------------------------------------------- hill
def hill():
    """220x30: a gentle grassy mound the castle stands on: flat plateau (x ~50..170 at y 4), green top with leaf and
    pine shading and tufts, a tan soil band below, flat last row, tapering to nothing at both ends."""
    W, H = 220, 30
    img = blank(W, H)
    yy, xx = _grid(W, H)
    chk = _checker(W, H)
    top = np.zeros(W, int)
    for x in range(W):
        u = abs(x + 0.5 - W / 2) / (W / 2)
        v = min(1.0, max(0.0, (u - 0.55) / 0.45))
        s = v * v * (3 - 2 * v)
        top[x] = int(round(4 + 26 * s))         # 4 on the plateau, 30 (nothing) at the ends
    T = top[None, :]
    m = yy >= T
    depth = yy - T                                # rows below the surface
    # slope of the surface per column: >0 descending to the right (away from the light)
    slope = np.array([top[min(x + 2, W - 1)] - top[max(x - 2, 0)] for x in range(W)])
    stop = np.maximum(np.round(17 + 0.55 * (top - 4)), top + 6)     # soil lens: thins and tapers to the ends
    gdx = (stop - top).astype(int)[None, :]
    grass = m & (depth < gdx)
    soil = m & ~grass
    # soil: tan, a sand stratum, clay bottom, pebbles and roots
    _paint(img, soil, "tan")
    _paint(img, soil & (yy >= H - 3), "clay")
    _paint(img, soil & (yy == H - 4) & chk, "clay")
    _paint(img, soil & (xx > W * 0.76) & chk, "clay")
    _paint(img, soil & (xx > W * 0.84), "clay")
    rng = random.Random(11)
    for _ in range(16):   # sand strata dashes
        x = rng.randrange(44, 172); y = rng.randrange(19, H - 4)
        n = rng.choice((3, 4, 5))
        if all(soil[y, min(x + i, W - 1)] for i in range(n)):
            _R(img, x, y, n, 1, "sand"); _R(img, x + 1, y + 1, n - 1, 1, "clay")
    for _ in range(14):   # pebbles
        x = rng.randrange(44, 172); y = rng.randrange(19, H - 1)
        if soil[y, x] and soil[y, min(x + 2, W - 1)] and soil[y - 1, x]:
            _P(img, x, y, "brown"); _P(img, x + 1, y, "brown"); _P(img, x, y - 1, "peach")
    # grass body in bands, one dithered row between each
    _paint(img, grass, "green")
    _paint(img, grass & (depth == 6) & chk, "leaf")
    _paint(img, grass & (depth >= 7), "leaf")
    _paint(img, grass & (depth == 10) & chk, "pine")
    _paint(img, grass & (depth >= 11), "pine")
    # the right shoulder turns away from the light; its shade deepens with the slope
    S = slope[None, :]
    _paint(img, grass & (S >= 1) & (depth >= 1) & (depth <= 2) & chk, "leaf")
    _paint(img, grass & (S >= 1) & (depth >= 3), "leaf")
    _paint(img, grass & (S >= 2) & (depth >= 4) & chk, "pine")
    _paint(img, grass & (S >= 2) & (depth >= 6), "pine")
    _paint(img, grass & (depth == gdx - 1), "pine")
    # light rim along the surface, brightest on the left
    rim = m & (depth == 0)
    _paint(img, rim, "green")
    _paint(img, rim & (slope[None, :] <= 0) & chk, "yellow")
    _paint(img, m & (depth == 1) & (xx < W * 0.3) & (xx % 4 == 0), "yellow")
    # grass fringe hanging into the soil
    for x in range(W):
        y = top[x] + int(gdx[0, x])
        if y < H and soil[y, x] and (x * 7) % 6 < 3:
            _P(img, x, y, "pine")
            if (x * 5) % 9 == 0 and y + 1 < H:
                _P(img, x, y + 1, "pine")
    # tufts on the surface: little three-blade clumps sticking up
    for x in range(6, W - 6, 11):
        x2 = x + (x * 7) % 5
        y = top[x2]
        if y <= H - 4:
            _P(img, x2, y - 1, "green"); _P(img, x2 + 2, y - 1, "green"); _P(img, x2 + 1, y - 2, "green")
            _P(img, x2 + 1, y - 1, "leaf")
    # clumps inside the grass: small chevrons of a darker green
    for i, x in enumerate(range(12, W - 12, 15)):
        y = top[x] + 4 + (i % 3) * 2
        if y < H and grass[y, x] and grass[y, x + 2] and grass[y - 1, x + 1]:
            c = "leaf" if slope[x] < 1 else "pine"
            _P(img, x, y - 1, c); _P(img, x + 1, y, c); _P(img, x + 2, y - 1, c)
    _ol(img)
    return img


# ----------------------------------------------------------------------------------------------- wall
WALL_GATE = (74, 97)


def wall(stage=3):
    """172x44, last row on the ground: the fibroblasts' thick brick wall with a crenellated top and an open archway
    at x 74..97 (dark brown inside). stage 1: bottom 10 rows built, 2: 22 rows, 3: full; the rest transparent."""
    W, H = 172, 44
    stage = stage if stage in (1, 2, 3) else 3
    img = blank(W, H)
    yy, xx = _grid(W, H)
    chk = _checker(W, H)
    g0, g1 = WALL_GATE
    gw = g1 - g0 + 1
    r = gw / 2
    gcx, gcy = g0 + r, 26
    d = np.sqrt((xx + 0.5 - gcx) ** 2 + (yy + 0.5 - gcy) ** 2)
    gate = (_mrect(W, H, (g0, gcy, gw, H - gcy))) | ((d <= r) & (yy < gcy))

    # silhouette: merlons (rows 1..7), a ledge (rows 8..9) one px proud, body below
    body = _mrect(W, H, (2, 10, W - 4, H - 10))
    ledge = _mrect(W, H, (1, 8, W - 2, 2))
    mer = np.zeros_like(body)
    for i in range(12):
        x = round(2 + i * (W - 4 - 10) / 11)
        mer |= _mrect(W, H, (x, 1, 10, 7))
    full = body | ledge | mer

    built = {1: 10, 2: 22, 3: H}[stage]
    ytop = H - built
    bw, bh = 10, 5
    row = (yy - 10) // bh
    shift = np.where(row % 2 == 0, 0, bw // 2)
    cpos = (xx - 2 + shift) % bw
    col = (xx - 2 + shift) // bw
    bid = row * 61 + col
    hv = np.vectorize(lambda v: _hash(int(v), 5))(bid)
    m = full & (yy >= ytop)
    if stage < 3:
        # an unfinished course on top: some bricks already laid
        course = body & (yy >= ytop - bh) & (yy < ytop) & (hv % 5 < 2)
        m |= course
    m &= ~(gate if stage == 3 else _mrect(W, H, (g0, 0, gw, H)))
    mortar = ((yy - 10) % bh == bh - 1) | (cpos == bw - 1)
    # bricks
    _paint(img, m, "sand")
    _paint(img, m & (hv < 260), "peach")
    _paint(img, m & ((yy - 10) % bh == bh - 2) & ~mortar, "tan")
    _paint(img, m & (cpos == bw - 2) & ~mortar & (hv < 260), "tan")
    _paint(img, m & ((yy - 10) % bh == 0) & (cpos <= 1) & (hv > 820), "white")
    _paint(img, m & mortar & body, "brown")
    # merlons and ledge: dressed stone, lit tops, shaded right faces
    mm = m & mer
    _paint(img, mm, "sand")
    _paint(img, mm & (yy == 1), "white")
    _paint(img, mm & _edge_br(mer, 2) & (yy > 1), "tan")
    _paint(img, mm & (yy == 7), "tan")
    lm = m & ledge
    _paint(img, lm, "sand")
    _paint(img, lm & (yy == 8), "white")
    _paint(img, lm & (yy == 9), "tan")
    _paint(img, m & body & (yy == 10), "brown")     # shadow under the ledge
    _paint(img, m & body & (yy == 11) & chk, "tan")
    # foot of the wall: darker courses
    _paint(img, m & body & (yy >= H - 4) & ~mortar & chk, "clay")
    _paint(img, m & body & (yy >= H - 2) & ~mortar, "clay")
    # right end in shade
    _paint(img, m & (xx >= W - 4) & ~mortar, "tan")
    _paint(img, m & (xx >= W - 3) & mortar, "brown")

    # archway (only once the wall is tall enough to frame it; lower stages keep a clean gap)
    vous = (d > r) & (d <= r + 3.4) & (yy < gcy) & m & (stage == 3)
    ang = np.degrees(np.arctan2(gcy - (yy + 0.5), xx + 0.5 - gcx))
    seg = np.floor((ang + 10) / 20).astype(int)
    _paint(img, vous, "sand")
    _paint(img, vous & (seg % 2 == 1), "peach")
    _paint(img, vous & (np.abs(ang - 90) < 10), "white")                  # keystone
    _paint(img, vous & (np.abs(((ang + 10) % 20)) < 1.6) & (d > r + 0.6), "brown")
    _paint(img, vous & (d > r + 2.6), "brown")
    jamb = m & (yy >= gcy) & (((xx >= g0 - 3) & (xx < g0)) | ((xx > g1) & (xx <= g1 + 3)))
    _paint(img, jamb, "sand")
    _paint(img, jamb & (xx > g1), "tan")
    _paint(img, jamb & ((yy - gcy) % 6 == 5), "brown")
    _paint(img, jamb & ((xx == g0 - 3) | (xx == g1 + 3)), "brown")
    if stage == 3:
        gin = gate.copy()
        _paint(img, gin, "brown")
        _paint(img, gin & (yy <= 17), "plum")                              # shadow under the vault
        _paint(img, gin & (yy == 18) & chk, "plum")
        _paint(img, gin & (xx <= g0 + 2), "plum")                          # the left reveal faces away from the light
        rev = gin & (xx >= g1 - 3) & (yy > 16)                            # the right reveal shows the wall's thickness
        _paint(img, rev, "clay")
        _paint(img, rev & (xx == g1 - 3), "brown")
        _paint(img, rev & ((yy - gcy) % 5 == 4), "brown")
        _paint(img, gin & (yy >= H - 3) & (xx < g1 - 3) & chk, "plum")
        _paint(img, gin & (yy == H - 1) & (xx < g1 - 3), "plum")

    # loose bricks lying on the unfinished top
    if stage < 3:
        a = _alpha(img)
        spots = [14, 44, 60, 112, 133, 156]
        for i, lx in enumerate(spots):
            if gate[H - 1, lx] or gate[H - 1, lx + 7]:
                continue
            yb = 0
            while yb + 4 < H and not (a[yb + 4, lx + 1] or a[yb + 4, lx + 6]):
                yb += 1
            _R(img, lx, yb, 8, 4, "peach" if i % 2 else "sand")
            _R(img, lx, yb + 3, 8, 1, "tan"); _R(img, lx + 7, yb, 1, 4, "tan")
            _P(img, lx, yb, "white"); _P(img, lx + 1, yb, "white")
    _ol(img)
    a = _alpha(img)
    _paint(img, a & (yy == H - 1) & ~(gate & (stage == 3)), "ink")
    return img


# ----------------------------------------------------------------------------------------------- chemo
SKULL = """
...WWWWW...
..WWWWWWW..
..WKKWKKW..
..WKKWKKW..
..WWWKWWW..
...WWWWW...
W..W.W.W..W
WW.......WW
..WW...WW..
....WWW....
..WW...WW..
WW.......WW
W.........W
"""


def iv_stand():
    """34x100, last row on the ground: an IV drip stand on wheels with a green poison bag (skull and crossbones)
    and a drip chamber; the tube outlet is at (17, 46)."""
    W, H = 34, 100
    img = blank(W, H)
    yy, xx = _grid(W, H)
    # pole
    _R(img, 16, 2, 2, 92, "steel"); _R(img, 16, 2, 1, 92, "ice")
    _R(img, 15, 60, 4, 3, "slate"); _R(img, 15, 60, 1, 3, "steel")      # height clamp
    _P(img, 19, 61, "slate"); _P(img, 20, 61, "slate")                      # clamp knob
    # crossbar with two up-curled hooks and a centre ring the bag hangs from
    _R(img, 9, 5, 16, 2, "steel"); _R(img, 9, 5, 16, 1, "ice")
    for (hx, sg) in ((9, -1), (24, 1)):
        _P(img, hx, 4, "steel"); _P(img, hx, 3, "steel"); _P(img, hx - sg, 2, "steel")
    _R(img, 16, 0, 2, 3, "steel"); _P(img, 16, 0, "ice")
    _P(img, 16, 7, "slate"); _P(img, 17, 7, "slate"); _P(img, 16, 8, "slate"); _P(img, 17, 8, "slate")
    # base: a spoked foot on four wheels
    _R(img, 3, 92, 28, 2, "slate"); _R(img, 3, 92, 28, 1, "steel")
    _R(img, 14, 89, 6, 3, "slate"); _R(img, 14, 89, 6, 1, "steel")
    _R(img, 9, 94, 16, 1, "dusk")
    for wx in (4, 12, 22, 29):
        m = _mell(W, H, (wx, 97, 1.6, 1.6))
        _paint(img, m, "night"); _P(img, wx, 97, "steel")
        _P(img, wx, 94, "slate"); _P(img, wx, 95, "slate")
    # bag: clear plastic top, green poison below the fill line
    bag = _mpoly(W, H, [(7, 12), (27, 12), (29, 15), (29, 35), (25, 40), (9, 40), (5, 35), (5, 15)])
    bag |= _mrect(W, H, (13, 9, 9, 4))
    _paint(img, bag, "ice")
    liquid = bag & (yy >= 16)
    _paint(img, liquid, "green")
    _paint(img, liquid & (yy == 16), "yellow")
    _paint(img, liquid & _edge_br(liquid, 2), "leaf")
    _paint(img, liquid & _edge_br(liquid, 1), "pine")
    _paint(img, liquid & (xx == 6) & (yy > 17) & (yy < 33), "yellow")
    _paint(img, bag & ~liquid & (yy <= 13), "white")
    _paint(img, bag & ~liquid & (xx >= 25), "steel")
    _paint(img, _mrect(W, H, (15, 10, 5, 2)), (0, 0, 0, 0))   # hanger hole
    _paint(img, _mrect(W, H, (15, 10, 5, 1)) | _mrect(W, H, (15, 11, 1, 1)), "ink")
    # bag seam and port
    _R(img, 6, 15, 23, 1, "steel")
    _R(img, 15, 40, 5, 2, "ice"); _R(img, 19, 40, 1, 2, "steel")
    # skull and crossbones
    sk = _spr(SKULL, {"W": "white", "K": "pine"})
    _over(img, sk, 12, 20)
    # drip chamber with a drop inside, outlet nozzle at (17, 46)
    _R(img, 14, 42, 7, 4, "ice"); _R(img, 14, 42, 1, 4, "white"); _R(img, 19, 42, 2, 4, "steel")
    _P(img, 17, 43, "green"); _P(img, 17, 44, "leaf"); _R(img, 15, 45, 5, 1, "green")
    _R(img, 16, 46, 3, 1, "slate")
    _ol(img)
    # the pole hides behind the bag: no outline needed there; wheels sit on the last row
    _paint(img, _alpha(img) & (yy == H - 1), "ink")
    return img


def drip(n=1):
    """6x12: one green drop (n=1) or two stacked (n=2)."""
    W, H = 6, 12
    img = blank(W, H)
    big = """
..KK..
.KGGK.
.KGGK.
KGYGGK
KGGGLK
KGGLLK
.KLLK.
..KK..
"""
    small = """
..KK..
.KGGK.
KGYGLK
KGGGLK
.KLLK.
..KK..
"""
    key = {"K": "ink", "G": "green", "Y": "white", "L": "leaf"}
    if n == 2:
        _over(img, _spr(small, key), 0, 0)
        _over(img, _spr(small, key), 0, 6)
    else:
        _over(img, _spr(big, key), 0, 2)
    return img


# ----------------------------------------------------------------------------------------------- alarm clock
def alarm_clock(ring=True):
    """26x26, last row on the ground: a twin-bell alarm clock, red body, white face. ring=True tilts it, lifts a
    foot and adds shake lines."""
    S = 26
    W = H = S * 2
    big = blank(W, H)
    ox, oy = S, S + 2
    a = math.radians(-13 if ring else 0)
    ca, sa = math.cos(a), math.sin(a)

    def T(lx, ly):
        return ox + lx * ca - ly * sa, oy + lx * sa + ly * ca

    # legs: short stubby feet
    for sgn in (-1, 1):
        fx, fy = T(sgn * 6, 9.5)
        _paint(big, _mell(W, H, (fx, fy, 1.4, 1.4)), "night")
        _P(big, round(fx) - 1, round(fy) - 1, "dusk")
    # bells, each its own outlined dome
    for sgn in (-1, 1):
        L = blank(W, H)
        cx, cy = T(sgn * 6.5, -8.2)
        m = _mell(W, H, (cx, cy, 3.6, 3.6))
        _sphere(L, m, cx + 0.5, cy + 0.5, 4.1, ["white", "ice", "steel", "slate"], [0.85, 0.55, 0.15])
        kx, ky = T(sgn * 7.2, -12.6)                    # knob on top of each bell
        _P(L, round(kx), round(ky), "steel")
        _ol(L)
        _over(big, L)
    # hammer and the bracket between the bells
    hx, hy = T(0, -12)
    _ln(big, *T(0, -8.5), hx, hy, "slate")
    _paint(big, _mell(W, H, (hx, hy - 0.5, 1.1, 1.1)), "steel")
    _ol(big)
    # body over the bells' feet
    B = blank(W, H)
    body = _mell(W, H, (ox, oy, 8.5, 8.5))
    _sphere(B, body, ox + 0.5, oy + 0.5, 9, ["rose", "red", "wine", "plum"], [0.88, 0.42, 0.0])
    face = _mell(W, H, (ox, oy, 5.6, 5.6))
    _paint(B, _ring(face) & body, "wine")
    _paint(B, face, "white")
    _paint(B, face & _edge_br(face, 1), "ice")
    for k in range(4):
        tx, ty = T(5 * math.sin(k * math.pi / 2), -5 * math.cos(k * math.pi / 2))
        _P(B, round(tx), round(ty), "steel")
    _ln(B, ox, oy, *T(-3, -2), "ink")          # hour hand
    _ln(B, ox, oy, *T(1.5, -4.5), "ink")       # minute hand
    _P(B, ox, oy, "red")
    gx, gy = T(-5.5, -4.5)
    _P(B, round(gx), round(gy), "white"); _P(B, round(gx) + 1, round(gy) - 1, "white")
    _ol(B)
    _over(big, B)
    # crop to 26x26: centred on the body, lowest pixel on the last row
    al = np.array(big)[:, :, 3] > 0
    bottom = np.nonzero(al)[0].max()
    left = ox - S // 2
    img = big.crop((left, bottom - S + 1, left + S, bottom + 1))
    if ring:
        # shake lines: two short strokes on each side, a ping above
        for (x0, y0, x1, y1) in ((1, 9, 2, 7), (0, 13, 2, 12), (24, 8, 23, 6), (25, 12, 23, 11),
                                 (3, 3, 4, 5), (21, 2, 20, 4)):
            _ln(img, x0, y0, x1, y1, "ink")
    return img


# ----------------------------------------------------------------------------------------------- syringe
def syringe():
    """70x22: a big friendly syringe lying horizontally, plunger left, needle pointing right."""
    W, H = 70, 22
    img = blank(W, H)
    yy, xx = _grid(W, H)
    # plunger thumb rest and rod
    _R(img, 1, 3, 4, 16, "ice"); _R(img, 1, 3, 1, 16, "white"); _R(img, 4, 3, 1, 16, "steel")
    _P(img, 1, 3, (0, 0, 0, 0)); _P(img, 1, 18, (0, 0, 0, 0))
    _R(img, 5, 9, 14, 4, "ice"); _R(img, 5, 9, 14, 1, "white"); _R(img, 5, 12, 14, 1, "steel")
    # finger flange
    _R(img, 18, 1, 3, 20, "ice"); _R(img, 18, 1, 1, 20, "white"); _R(img, 20, 1, 1, 20, "steel")
    # barrel
    barrel = _mrect(W, H, (21, 4, 35, 14))
    _paint(img, barrel, "white")
    _paint(img, barrel & (yy >= 15), "ice")
    # stopper
    _R(img, 27, 5, 3, 12, "night"); _R(img, 27, 5, 1, 12, "dusk")
    _P(img, 28, 8, "slate"); _P(img, 28, 13, "slate")
    _R(img, 21, 9, 6, 4, "ice"); _R(img, 21, 9, 6, 1, "white")              # rod inside the glass
    # liquid
    liq = _mrect(W, H, (30, 5, 25, 12))
    _paint(img, liq, "sky")
    _paint(img, liq & (yy == 5), "cyan")
    _paint(img, liq & (yy >= 15), "navy")
    _paint(img, liq & (yy == 14) & _checker(W, H), "navy")
    # glass glint and graduation marks
    _R(img, 23, 6, 3, 1, "white")
    _R(img, 32, 7, 18, 1, "white"); _R(img, 34, 8, 6, 1, "cyan")
    for gx in range(31, 55, 4):
        _P(img, gx, 4, "slate")
        if (gx - 31) % 8 == 0:
            _P(img, gx, 5, "navy")
    # nozzle and hub
    _R(img, 56, 6, 3, 10, "ice"); _R(img, 56, 6, 3, 1, "white"); _R(img, 56, 15, 3, 1, "steel")
    _R(img, 59, 8, 3, 6, "steel"); _R(img, 59, 8, 3, 1, "ice"); _R(img, 59, 13, 3, 1, "slate")
    # needle
    _R(img, 62, 10, 6, 2, "ice"); _R(img, 62, 11, 6, 1, "steel")
    _P(img, 68, 10, "steel")
    _ol(img)
    # a sparkle at the tip, friendly not scary
    return img


# ----------------------------------------------------------------------------------------------- chain
LINK_FLAT = """
.KKKKKK.
KIIISSDK
KSK..KDK
KSDDDDNK
.KKKKKK.
"""
LINK_EDGE = """
KKKKKK
KISSDK
KKKKKK
"""
LINK_OPEN = """
.KKKKK..
KIISSDK.
KSK.....
KSDDDNK.
.KKKKK..
"""
SHACKLE = """
.KKKKK.
KIISSDK
KSKKKDK
.K..KDK
.K..KDK
KSKKKNK
KSDDDNK
.KKKKK.
"""
CHAIN_KEY = {"K": "ink", "I": "ice", "S": "steel", "D": "slate", "N": "dusk"}


def _ball(img, cx, cy, r):
    W, H = img.size
    m = _mell(W, H, (cx, cy, r, r))
    _sphere(img, m, cx + 0.5, cy + 0.5, r + 0.5, ["steel", "slate", "dusk", "night"], [0.8, 0.45, 0.05])
    _P(img, int(cx - r / 2), int(cy - r / 2), "ice")
    _P(img, int(cx - r / 2) + 1, int(cy - r / 2), "steel")


def ball_chain(broken=False):
    """30x12: an iron ball with a short chain ending in an open shackle at the left edge (~(0, 9)).
    broken=True: the chain snapped in the middle, loose links and a small spark."""
    W, H = 30, 12
    img = blank(W, H)
    flat = _spr(LINK_FLAT, CHAIN_KEY); edge = _spr(LINK_EDGE, CHAIN_KEY)
    sh = _spr(SHACKLE, CHAIN_KEY); op = _spr(LINK_OPEN, CHAIN_KEY)
    if not broken:
        _over(img, edge, 15, 7)
        _over(img, flat, 9, 6)
        _over(img, edge, 4, 7)
        _over(img, sh, 0, 4)
    else:
        _over(img, edge, 15, 7)
        _over(img, op, 9, 7)
        _over(img, edge, 4, 7)
        _over(img, sh, 0, 4)
    ball = blank(W, H)
    _ball(ball, 23.5, 6, 4.5)
    _ol(ball)
    _over(img, ball)
    if broken:
        # remove the middle edge-on link's right half and throw a loose link up, with a spark at the break
        _paint(img, _mrect(W, H, (13, 7, 2, 3)), (0, 0, 0, 0))
        loose = _spr(LINK_EDGE, CHAIN_KEY).rotate(-45, expand=True, resample=Image.NEAREST)
        _over(img, loose.crop(loose.getbbox()), 12, 1)
        _star4(img, 16, 3, "yellow", "white")
        _P(img, 14, 6, "gold")
    return img


def chain_bits():
    """18x10: a few broken chain links flying, with motion ticks."""
    W, H = 18, 10
    img = blank(W, H)
    flat = _spr(LINK_FLAT, CHAIN_KEY)
    _over(img, flat, 0, 5)
    _over(img, flat.rotate(90, expand=True, resample=Image.NEAREST), 13, 0)
    _over(img, _spr(LINK_EDGE, CHAIN_KEY), 7, 2)
    # motion ticks trailing down-left of each piece
    for (x, y) in ((9, 7), (5, 2), (12, 9)):
        _P(img, x, y, "steel"); _P(img, x + 1, y - 1, "steel")
    return img


# ----------------------------------------------------------------------------------------------- crash course
def _capsule(W, H, x0, y0, x1, y1, r):
    yy, xx = _grid(W, H)
    px_, py_ = xx + 0.5, yy + 0.5
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.clip(((px_ - x0) * dx + (py_ - y0) * dy) / L2, 0, 1)
    qx, qy = x0 + t * dx, y0 + t * dy
    side = ((px_ - x0) * dy - (py_ - y0) * dx) / math.sqrt(L2)   # >0 right of the direction of travel
    return (px_ - qx) ** 2 + (py_ - qy) ** 2 <= r * r, side, t


def magnifier():
    """72x86: a giant magnifying glass, gold rim ~60 across centred at (32, 32), a transparent lens with a white
    glint at its top-left, and a wooden handle going down-right."""
    W, H = 72, 86
    img = blank(W, H)
    yy, xx = _grid(W, H)
    cx, cy = 32.5, 32.5
    d = np.sqrt((xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2)
    ang = np.arctan2(yy + 0.5 - cy, xx + 0.5 - cx)
    # handle first (the rim sits on top of it)
    dirx, diry = math.cos(math.radians(56)), math.sin(math.radians(56))
    sx, sy = cx + 27 * dirx, cy + 27 * diry
    ex, ey = cx + 58 * dirx, cy + 58 * diry
    hm, side, t = _capsule(W, H, sx + 7 * dirx, sy + 7 * diry, ex, ey, 4.2)
    _paint(img, hm, "brown")
    _paint(img, hm & (side > 1.2), "tan")     # the lit side faces up-left
    _paint(img, hm & (side > 2.6), "sand")
    _paint(img, hm & (side < -2.0), "plum")
    for tt in (0.55, 0.62):
        _paint(img, hm & (np.abs(t - tt) < 0.025), "clay")
    _paint(img, hm & (np.abs(t - 0.58) < 0.03) & (side > 1.2), "sand")
    # collar
    cm, cside, ct = _capsule(W, H, sx, sy, sx + 8 * dirx, sy + 8 * diry, 5.2)
    _paint(img, cm, "orange")
    _paint(img, cm & (cside > 1.5), "gold")
    _paint(img, cm & (cside > 3.2), "yellow")
    _paint(img, cm & (cside < -2.6), "rust")
    _paint(img, cm & (np.abs(ct - 0.55) < 0.08), "rust")
    # rim
    rim = (d <= 30.5) & (d > 25.5)
    lit = np.cos(ang - math.radians(-135))     # 1 at the top-left
    _paint(img, rim, "orange")
    _paint(img, rim & (lit > -0.35), "gold")
    _paint(img, rim & (lit > 0.55) & (d > 26.5) & (d <= 29.5), "yellow")
    _paint(img, rim & (lit < -0.55), "rust")
    _paint(img, rim & (d > 29.5) & (lit < 0.2), "rust")
    _paint(img, rim & (d <= 26.5) & (lit > 0.3), "orange")    # inner bevel in shadow on the lit side
    _paint(img, rim & (d <= 26.5) & (lit < -0.3), "gold")     # and catching light on the far side
    _ol(img)
    # lens: transparent, ink inner edge already drawn by the outline; a glint at its top-left
    gl = (d > 20.5) & (d <= 22.5) & (ang > math.radians(-160)) & (ang < math.radians(-115))
    _paint(img, gl, "white")
    _paint(img, _mell(W, H, (16, 20, 1, 1)), "white")
    return img


def stopwatch():
    """22x26: a silver stopwatch, white face with two hands (the long one at twenty seconds), crown button."""
    W, H = 22, 26
    img = blank(W, H)
    # crown: button and stem, side pusher
    _R(img, 8, 1, 6, 3, "ice"); _R(img, 8, 1, 6, 1, "white"); _R(img, 12, 1, 2, 3, "steel")
    _R(img, 10, 4, 2, 2, "steel"); _R(img, 10, 4, 1, 2, "ice")
    p = _mpoly(W, H, [(16, 6), (18, 4), (20, 6), (18, 8)])
    _paint(img, p, "steel")
    _P(img, 18, 5, "ice")
    _ol(img)
    body_l = blank(W, H)
    body = _mell(W, H, (11, 15, 9, 9))
    _sphere(body_l, body, 11.5, 15.5, 9.5, ["white", "ice", "steel", "slate"], [0.88, 0.6, 0.15])
    face = _mell(W, H, (11, 15, 6.5, 6.5))
    _paint(body_l, _ring(face) & body, "slate")
    _paint(body_l, face, "white")
    _paint(body_l, face & _edge_br(face, 1), "ice")
    for (tx, ty) in ((11, 10), (16, 15), (11, 20), (6, 15)):
        _P(body_l, tx, ty, "steel")
    _ln(body_l, 11, 15, 11, 11, "ink")                 # short hand up
    _ln(body_l, 11, 15, 16, 18, "red")                 # long hand at twenty seconds
    _P(body_l, 11, 15, "ink")
    _ol(body_l)
    _over(img, body_l)
    return img


# ----------------------------------------------------------------------------------------------- gold
SACK = """
........KKK.......
...KK..KYYGK.KK...
..KYGK.KYWGKKYGK..
..KYGOKKGGOKYGOK..
.KHHKKKKKKKKKKHK..
.KHTTHTTHTTHTTCK..
..KKTTTTTTTTCKK...
....KBBBBBBRK.....
.....KRBBBRK......
....KHHTTTTCK.....
...KHHTTTTTTCK....
..KHHTTTTTTTCCK...
..KHTTTTTTTTCCK...
.KHTTTTTTTTTCCCK..
.KHTTTTTTTTTCCCK..
.KTTTTTTTTTCCCBK..
..KTTTTTTCCCCBK...
...KKKKKKKKKKK....
"""


def gold_sack():
    """18x18: a small tan sack tied at the top, gold coins peeking out."""
    return _spr(SACK, {"K": "ink", "Y": "yellow", "G": "gold", "O": "orange", "W": "white", "H": "sand",
                       "T": "tan", "C": "clay", "B": "brown", "R": "rust"})


def stars():
    """16x10: three dizzy stars in a small arc."""
    W, H = 16, 10
    img = blank(W, H)
    big = """
...K...
..KYK..
KKKYKKK
KYYWYGK
.KYYGK.
.KYKGK.
.KK.KK.
"""
    plus = """
..K..
.KYK.
KYWGK
.KGK.
..K..
"""
    key = {"K": "ink", "Y": "yellow", "G": "gold", "W": "white"}
    _over(img, _spr(plus, key), 0, 5)
    _over(img, _spr(big, key), 5, 0)
    _over(img, _spr(plus, key), 11, 4)
    _P(img, 4, 3, "gold"); _P(img, 12, 1, "gold")
    return img


def zzz():
    """16x16: three Zs of growing size in navy, floating up to the right."""
    W, H = 16, 16
    img = blank(W, H)
    z1 = """
NNN
..N
.N.
N..
NNN
"""
    z2 = """
NNNN
NNNN
..N.
.N..
NNNN
NNNN
"""
    z3 = """
NNNNNN
NNNNNN
...NN.
..NN..
.NN...
NNNNNN
NNNNNN
"""
    key = {"N": "navy", "S": "sky"}
    _over(img, _spr(z1, key), 0, 11)
    _over(img, _spr(z2, key), 4, 7)
    _over(img, _spr(z3, key), 10, 0)
    return img


# coins: thick discs. Inside a pile their keylines are rust; the pile gets one ink outline.
COIN = """
.GGGGGG.
GYYWYYYG
GYYYYYGG
ROGGGGOR
.ROOOOR.
..RRRR..
"""
COIN_FACE = """
.RRRR.
RYYWGR
RYGGOR
RYGYOR
RGOOOR
.RRRR.
"""
COIN_EDGE = """
RR
YO
YO
YO
GO
RR
"""
COIN_KEY = {"R": "rust", "Y": "yellow", "G": "gold", "O": "orange", "W": "white"}
COIN_SIZES = {1: (26, 12), 2: (44, 24), 3: (70, 42), 4: (120, 64)}


def _coin_layer(W, H, seed, heap, stacks, loose):
    img = blank(W, H)
    flat, face, edge = (_spr(c, COIN_KEY) for c in (COIN, COIN_FACE, COIN_EDGE))
    rng = random.Random(seed)
    cx, hw, hh = heap
    items = []
    if hh > 0:
        n = int(hw * hh * 0.22) + 3
        tries = 0
        while len(items) < n and tries < n * 40:
            tries += 1
            x = rng.uniform(cx - hw, cx + hw)
            y = rng.uniform(H - 1 - hh, H - 1)
            u = (x - cx) / hw
            prof = H - 1 - hh * max(0.0, 1 - u * u) ** 0.8
            if y < prof + 1:
                continue
            r = rng.random()
            kind = face if r < 0.12 else edge if r < 0.18 else flat
            items.append((y, x, kind))
        # pin the summit so the silhouette is a clean mound
        items.append((H - 1 - hh + 1, cx, flat))
    if hh > 0:
        # a solid core behind the coins so the pile has no holes
        yy, xx = _grid(W, H)
        u = (xx + 0.5 - cx) / (hw - 3)
        prof = H - 1 - (hh - 3) * np.clip(1 - u * u, 0, 1) ** 0.8
        core = (yy >= prof + 1) & (np.abs(u) < 1)
        _paint(img, core, "orange")
        _paint(img, core & _checker(W, H), "gold")
        _paint(img, core & (yy > H - 1 - (hh - 3) * 0.35) & _checker(W, H), "rust")
    items.sort(key=lambda t: t[0])
    for (y, x, k) in items:
        _over(img, k, round(x - k.width / 2), round(y - k.height / 2))
    for (sx, n) in stacks:
        for i in range(n):
            j = (1 if i % 3 == 1 else 0) - (1 if i % 4 == 3 else 0)
            _over(img, flat, sx + j, H - 6 - 2 * i)
    for (lx, ly, kind) in loose:
        k = {"f": flat, "c": face, "e": edge}[kind]
        _over(img, k, lx, H - k.height if ly is None else ly)
    # shade the side away from the light: one step down the warm ramp on the lower right
    if hh > 0:
        yy, xx = _grid(W, H)
        f = (xx - cx) / hw * 0.8 + (yy - (H - 1 - hh)) / hh * 0.45
        dark = (f > 0.78) | ((f > 0.6) & _checker(W, H))
        a = np.array(img)
        out = a.copy()
        for src, dst in (("yellow", "gold"), ("gold", "orange"), ("orange", "rust"), ("white", "yellow")):
            hit = np.all(a[:, :, :3] == C[src], axis=2) & (a[:, :, 3] > 0) & dark
            out[hit, :3] = C[dst]
        img = Image.fromarray(out)
    # extra glints on a few coin tops
    a = np.array(img)
    yel = np.all(a[:, :, :3] == C["yellow"], axis=2) & (a[:, :, 3] > 0)
    ys, xs = np.nonzero(yel & _nb(yel, 1, 0) & _nb(yel, -1, 0))
    idx = list(range(len(ys)))
    rng.shuffle(idx)
    for i in idx[:len(idx) // 30]:
        _star4(img, xs[i], ys[i], "yellow", "white") if rng.random() < 0.15 else _P(img, xs[i], ys[i], "white")
    return img


def coins(size=1):
    """Piles of gold coins, last row on the ground: size 1 = 26x12, 2 = 44x24, 3 = 70x42, 4 = 120x64 (a mountain)."""
    size = size if size in COIN_SIZES else 1
    W, H = COIN_SIZES[size]
    if size == 1:
        lay = _coin_layer(W, H, 1, (13, 0, 0), [(1, 4), (15, 2)], [(9, None, "f"), (21, H - 7, "c"), (11, H - 8, "e")])
    elif size == 2:
        lay = _coin_layer(W, H, 2, (22, 17, 14), [(1, 7), (35, 4)], [(10, None, "f"), (27, None, "c")])
    elif size == 3:
        lay = _coin_layer(W, H, 3, (36, 30, 31), [(1, 11), (61, 6), (54, 3)], [(14, None, "f"), (44, None, "c")])
    else:
        lay = _coin_layer(W, H, 4, (61, 55, 56), [(1, 15), (9, 8), (111, 12), (102, 6)],
                          [(24, None, "f"), (72, None, "c"), (90, None, "f")])
    a = np.array(lay)
    a[:, 0, 3] = 0; a[:, W - 1, 3] = 0; a[0, :, 3] = 0
    img = Image.fromarray(a)
    _ol(img)
    yy, xx = _grid(W, H)
    _paint(img, _alpha(img) & (yy == H - 1), "ink")
    return img


def money_bag():
    """34x36, last row on the ground: a big tan money bag tied at the top, a gold $ on it."""
    W, H = 34, 36
    img = blank(W, H)
    yy, xx = _grid(W, H)
    body = _mell(W, H, (17, 24, 14.5, 11)) & (yy <= H - 2)
    body |= _mpoly(W, H, [(12, 11), (22, 11), (27, 16), (7, 16)])
    neck = _mrect(W, H, (13, 8, 8, 4))
    ruff = _mpoly(W, H, [(9, 2), (12, 4), (14, 1), (17, 3), (20, 1), (22, 4), (25, 2), (24, 7), (20, 9), (14, 9), (10, 7)])
    _sphere(img, body, 15, 23, 15, ["sand", "peach", "tan", "clay", "brown"], [0.9, 0.7, 0.35, 0.0])
    _paint(img, body & (yy >= H - 3) & (xx > 8), "clay")
    _sphere(img, ruff, 16, 6, 7, ["sand", "peach", "tan", "clay"], [0.85, 0.5, 0.1])
    _paint(img, neck, "tan"); _paint(img, neck & (xx >= 18), "clay")
    # fabric folds from the neck
    for (x0, y0, x1, y1) in ((14, 13, 12, 18), (19, 13, 21, 18), (16, 13, 16, 16)):
        _ln(img, x0, y0, x1, y1, "clay")
    _ln(img, 11, 3, 12, 6, "tan"); _ln(img, 22, 3, 21, 6, "clay")
    # rope tie
    _R(img, 12, 10, 10, 2, "brown"); _R(img, 12, 10, 10, 1, "clay")
    _ln(img, 21, 11, 24, 15, "brown"); _ln(img, 22, 11, 25, 14, "clay")
    _P(img, 25, 16, "brown")
    # the $: a 2px-stroke S with a bar through it, gold shading, brown keyline
    sgl = """
...Y...
.YYYYYY
YYYYYYY
YY.Y...
YYYYYY.
.YYYYYY
...Y.YY
YYYYYYY
YYYYYY.
...Y...
"""
    D = blank(W, H)
    dm = _alpha(_spr(sgl, {"Y": "yellow"}))
    dmask = np.zeros((H, W), bool)
    dmask[19:19 + dm.shape[0], 13:13 + dm.shape[1]] = dm
    _paint(D, dmask, "yellow")
    _paint(D, dmask & _edge_br(dmask, 1), "gold")
    _paint(D, dmask & ~_nb(dmask, 0, 1) & ~_nb(dmask, 1, 0), "orange")
    _ol(D, "brown")
    _over(img, D)
    _ol(img)
    _paint(img, _alpha(img) & (yy == H - 1), "ink")
    return img
