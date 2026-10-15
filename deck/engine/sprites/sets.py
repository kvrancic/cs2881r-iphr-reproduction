"""One set per act, drawn on the full 384x216 screen behind everything: a coloured wainscot along the back wall
(a band above the ground line, inside the ground's white area, in muted palette colours that carry no meaning
elsewhere: beige and clay wood, grey lab tiles, lilac cork, slate boards, stage boards) and one set piece in steel and
slate. The band sits below the stage's text and the pieces stay clear of the places where text sits.

  lecture  the claim: wood panelling and a tall window at the right
  lab      the reproduction: a cooler wall, low grey tiles and a glass cabinet with bottles at each edge
  mapwall  by kind: a warm wall, lilac cork and a world map pinned to it
  survey   the variations: a pale slate wall and slate boards (the theodolite stands on the act's first slide)
  stage    the close: stage boards, curtains drawn back at both sides and a scalloped valance"""
from px import W, H, blank, rect, line, disc, ellipse
from pal import rgba
from ground import ground

GY = 184
TOP = 146                     # the top of the wainscot


def _inside():
    """The ground's white area: the set never covers the dithered border."""
    g = ground()
    white = rgba("white")
    return lambda x, y: g.getpixel((x, y)) == white


def _band(img, light, dark, rail, step=None, grid=None, top=TOP, dense=False):
    """The wainscot from top to the ground line: light, sprinkled with dark (1 in 16 pixels, or 1 in 4 if dense), a
    2 px rail on top; step draws vertical panel lines every step px, grid a tile grid of that size."""
    inside = _inside()
    L, D, R = rgba(light), rgba(dark), rgba(rail)
    for y in range(top, GY):
        for x in range(W):
            if not inside(x, y):
                continue
            if y < top + 2 or step and x % step == 0 or grid and (x % grid == 0 or (y - top) % grid == 0):
                c = R
            elif (x % 2 == 0 and y % 2 == 0 and (x + y) % 4 == 0) if dense else (x % 4 == 0 and y % 4 == 0):
                c = D
            else:
                c = L
            img.putpixel((x, y), c)


def _wall(img, tint, top, extra=None):
    """A light tint over the back wall, above the wainscot: 1 in 4 pixels of tint (and 1 in 16 of extra), so ink
    and slate text keep their contrast."""
    inside = _inside()
    T_, E = rgba(tint), rgba(extra) if extra else None
    for y in range(0, top):
        for x in range(W):
            if not inside(x, y):
                continue
            if E and x % 4 == 2 and y % 4 == 2:
                img.putpixel((x, y), E)
            elif x % 2 == 0 and y % 2 == 0:
                img.putpixel((x, y), T_)


def tripod():
    """A surveyor's theodolite on its tripod, feet on the ground line (a prop for the opening of the variations)."""
    img = blank(36, 52)
    tx, ty = 18, 18
    rect(img, tx - 6, ty - 10, 13, 8, "slate"); rect(img, tx - 3, ty - 14, 7, 4, "slate"); rect(img, tx + 7, ty - 8, 4, 3, "slate")
    rect(img, tx - 5, ty - 9, 11, 2, "steel")
    for fx in (tx - 16, tx, tx + 16):
        line(img, tx, ty - 2, fx, 51, "slate")
    return img


def _window(img, x, y, w, h):
    """A tall window: a steel frame, four panes, ice glass."""
    for yy in range(y + 2, y + h - 2):
        for xx in range(x + 2, x + w - 2):
            if (xx + yy) % 2 == 0:
                img.putpixel((xx, yy), rgba("ice"))
    for d in (0, 1):
        rect(img, x + d, y, 1, h, "steel"); rect(img, x + w - 1 - d, y, 1, h, "steel")
        rect(img, x, y + d, w, 1, "steel"); rect(img, x, y + h - 1 - d, w, 1, "steel")
    rect(img, x + w // 2, y, 1, h, "steel"); rect(img, x, y + h // 2, w, 1, "steel")
    rect(img, x - 3, y + h, w + 6, 2, "slate")                  # the sill


def lecture():
    img = blank(W, H)
    _band(img, "sand", "clay", "clay")
    _window(img, W - 64, 22, 34, 62)                   # its sill at y 86, above the robot's head
    return img


def _cabinet(img, x, y, w, h):
    """A tall glass-front lab cabinet: a slate frame, ice glass, two shelves of bottles."""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (xx + yy) % 2 == 0:
                img.putpixel((xx, yy), rgba("ice"))
    for d in (0, 1):
        rect(img, x + d, y, 1, h, "slate"); rect(img, x + w - 1 - d, y, 1, h, "slate")
        rect(img, x, y + d, w, 1, "slate")
    for sy in (y + h // 3, y + 2 * h // 3):
        rect(img, x, sy, w, 2, "slate")
        for k, bx in enumerate(range(x + 4, x + w - 5, 6)):
            bh = 7 + (k % 2) * 3
            rect(img, bx, sy - bh, 4, bh, "steel"); rect(img, bx + 1, sy - bh - 2, 2, 2, "steel")


def lab():
    img = blank(W, H)
    _wall(img, "ice", 172, "steel")                          # a cooler, slightly darker wall
    _band(img, "ice", "steel", "steel", grid=12, top=172)    # low tiles: clear of the gauge's scale labels
    _cabinet(img, 18, 116, 28, 56)              # low cabinets: under the labels that sit at the left
    _cabinet(img, W - 46, 116, 28, 56)
    return img


CONTINENTS = [(110, 50, 46, 26), (132, 80, 20, 30), (190, 46, 30, 20), (200, 76, 26, 32), (236, 50, 70, 30),
              (278, 92, 26, 18), (330, 60, 22, 14)]   # (centre x, centre y, w, h) on the screen


def mapwall():
    img = blank(W, H)
    _wall(img, "sand", 172)                                    # a warm map-room wall
    _band(img, "ice", "grape", "grape", top=172, dense=True)   # under the labels of the split
    x0, y0, x1, y1 = 32, 16, W - 32, 154
    for d in (0, 1):
        rect(img, x0, y0 + d, x1 - x0, 1, "steel"); rect(img, x0, y1 - d, x1 - x0, 1, "steel")
        rect(img, x0 + d, y0, 1, y1 - y0, "steel"); rect(img, x1 - d, y0, 1, y1 - y0 + 1, "steel")
    for (cx, cy, w, h) in CONTINENTS:
        m = blank(w, h)
        ellipse(m, 0, 0, w, h, "steel")
        for yy in range(h):
            for xx in range(w):
                if m.getpixel((xx, yy))[3] and (xx + yy) % 2 == 0:
                    img.putpixel((cx - w // 2 + xx, cy - h // 2 + yy), rgba("ice"))
                if m.getpixel((xx, yy))[3] and xx % 4 == 0 and yy % 4 == 0:
                    img.putpixel((cx - w // 2 + xx, cy - h // 2 + yy), rgba("steel"))
    for (px_, py_) in ((x0 + 5, y0 + 5), (x1 - 5, y0 + 5)):
        disc(img, px_, py_, 2, "slate")
    return img


def survey():
    img = blank(W, H)
    _wall(img, "ice", 162)                                       # a pale slate wall
    _band(img, "ice", "dusk", "dusk", step=32, top=162)      # lower: the wording ladder's last row sits above it
    return img


def stage():
    img = blank(W, H)
    _band(img, "sand", "brown", "brown", step=40)
    rect(img, 0, 0, W, 4, "grape")                    # a narrow valance, above the boards and cards of the close
    for k in range(0, W, 24):
        for dx in range(24):
            rect(img, k + dx, 4, 1, max(1, round(2 * (1 - ((dx - 11.5) / 12) ** 2))), "grape")
    for side in (0, 1):                                # the curtains, drawn back to the edges of the stage
        for i in range(14):
            x = i if side == 0 else W - 1 - i
            for y in range(5, GY):
                bulge = 14 - int(5 * ((y - 5) / (GY - 5)) ** 2)
                if i >= bulge:
                    continue
                fold = (i + (y // 30)) % 5
                img.putpixel((x, y), rgba("plum" if fold == 0 else "grape" if fold in (1, 3) else "pink"))
    return img
