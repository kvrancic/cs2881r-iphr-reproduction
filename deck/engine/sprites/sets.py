"""One set piece per act, drawn on the full 384x216 screen in the ground's own pale colours (ice, a little steel)
so it stays in the background: a lecture hall with a window and a radiator (the claim), a lab wall with two shelves (the reproduction), a map
wall (by kind), a surveyor's corner with a tripod and a ranging pole (the variations), a stage with curtains
(the close). Each is placed once per act under every other object and stays put, so Morph keeps it still."""
import math
from px import W, H, blank, rect, line, disc, ellipse, dither
from pal import rgba

GY = 184


def _window(img, x, y, w, h):
    """A tall window: an ice frame, four panes, sparse dithered glass."""
    dither(img, x + 2, y + 2, w - 4, h - 4, "ice", 2)
    for d in (0, 1):
        rect(img, x + d, y, 1, h, "ice"); rect(img, x + w - 1 - d, y, 1, h, "ice")
        rect(img, x, y + d, w, 1, "ice"); rect(img, x, y + h - 1 - d, w, 1, "ice")
    rect(img, x + w // 2, y, 1, h, "ice"); rect(img, x, y + h // 2, w, 1, "ice")
    rect(img, x - 3, y + h, w + 6, 2, "ice")                    # the sill


def lecture():
    """Act 1: a lecture hall's back wall: a tall window near the right corner, a low radiator at the left (clear of
    the labels that sit at the left on some slides) and a wainscot rail."""
    img = blank(W, H)
    _window(img, W - 64, 30, 34, 84)
    for k in range(6):                                 # the radiator: six fins on a foot
        rect(img, 28 + k * 5, 160, 3, 20, "ice")
    rect(img, 26, 178, 32, 2, "ice")
    rect(img, 28, 150, W - 56, 1, "ice")
    dither(img, 28, 152, W - 56, 1, "ice", 0)
    return img


def _flask(img, x, y):
    rect(img, x + 3, y, 4, 6, "ice")
    for k in range(8):
        rect(img, x + 3 - k // 2, y + 6 + k, 4 + k, 1, "ice")
    dither(img, x + 1, y + 10, 8, 3, "steel", 0)


def _beaker(img, x, y, h=12):
    rect(img, x, y, 1, h, "ice"); rect(img, x + 9, y, 1, h, "ice"); rect(img, x, y + h - 1, 10, 1, "ice")
    dither(img, x + 1, y + h // 2, 8, h // 2 - 1, "ice", 0)


def _bottle(img, x, y):
    rect(img, x + 2, y, 3, 4, "ice"); rect(img, x, y + 4, 7, 12, "ice")
    dither(img, x + 1, y + 7, 5, 6, "steel", 1)


def lab():
    """Act 2: a lab wall: two shelves high up at the left and the right with glassware, their brackets below; the
    centre stays clear for the titles that sit there."""
    img = blank(W, H)
    for x0, x1 in ((26, 128), (W - 128, W - 26)):
        rect(img, x0, 36, x1 - x0, 2, "ice"); dither(img, x0, 38, x1 - x0, 1, "steel", 1)
        for bx in (x0 + 10, x1 - 16):
            line(img, bx, 39, bx + 6, 45, "ice"); rect(img, bx, 39, 1, 7, "ice")
        x = x0 + 6
        for kind in "fbtf":
            if kind == "f":
                _flask(img, x, 22); x += 16
            elif kind == "b":
                _beaker(img, x, 24); x += 18
            else:
                _bottle(img, x, 20); x += 14
            x += 10
    return img


CONTINENTS = [(110, 46, 46, 26), (132, 72, 20, 30), (190, 42, 30, 20), (200, 68, 26, 32), (236, 46, 70, 30),
              (278, 82, 26, 18), (330, 56, 22, 14)]   # (centre x, centre y, w, h) on the screen


def mapwall():
    """Act 3: a world map pinned to the wall: an ice frame, continents in sparse dithered ice, two pins."""
    img = blank(W, H)
    x0, y0, x1, y1 = 40, 18, W - 40, 112
    for d in (0, 1):
        rect(img, x0, y0 + d, x1 - x0, 1, "ice"); rect(img, x0, y1 - d, x1 - x0, 1, "ice")
        rect(img, x0 + d, y0, 1, y1 - y0, "ice"); rect(img, x1 - d, y0, 1, y1 - y0 + 1, "ice")
    for (cx, cy, w, h) in CONTINENTS:
        m = blank(w, h)
        ellipse(m, 0, 0, w, h, "ice")
        for yy in range(h):
            for xx in range(w):
                if m.getpixel((xx, yy))[3] and (xx % 2 == 0 and yy % 2 == 0 or xx % 4 == 1 and yy % 4 == 1):
                    img.putpixel((cx - w // 2 + xx, cy - h // 2 + yy), m.getpixel((xx, yy)))
    for (px_, py_) in ((x0 + 4, y0 + 4), (x1 - 4, y0 + 4)):
        disc(img, px_, py_, 2, "steel")
    return img


def survey():
    """Act 4: a surveyor's corner: a theodolite on its tripod at the left edge and a striped ranging pole at the
    right edge, both standing on the ground, and a small compass rose high on the left wall."""
    img = blank(W, H)
    cx, cy, r = 48, 40, 15
    for a in range(0, 360, 2):
        img.putpixel((round(cx + r * math.cos(math.radians(a))), round(cy + r * math.sin(math.radians(a)))), rgba("ice"))
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        line(img, cx, cy, cx + dx * (r - 2), cy + dy * (r - 2), "ice")
    disc(img, cx, cy, 1, "steel")
    tx, ty = 22, 150                                   # the theodolite: a head on three legs, feet on the ground, low
                                                       # enough to stay under the labels at the left
    rect(img, tx - 6, ty - 10, 13, 8, "ice"); rect(img, tx - 3, ty - 14, 7, 4, "ice"); rect(img, tx + 7, ty - 8, 4, 3, "ice")
    for fx in (tx - 16, tx, tx + 16):
        line(img, tx, ty - 2, fx, GY - 1, "ice")
    px_ = W - 16                                       # the ranging pole: bands of ice and steel
    for y in range(70, GY):
        rect(img, px_, y, 3, 1, "steel" if (y // 8) % 2 else "ice")
    return img


def stage():
    """The close: a stage, curtains drawn back at both sides and a valance across the top."""
    img = blank(W, H)
    rect(img, 0, 0, W, 10, "ice")
    for k in range(0, W, 24):                          # the valance's scalloped hem
        for dx in range(24):
            depth = max(1, round(4 * (1 - ((dx - 11.5) / 12) ** 2)))
            rect(img, k + dx, 10, 1, depth, "ice")
        rect(img, k + 23, 2, 1, 8, "steel")
    for side in (0, 1):
        for i in range(28):
            x = i if side == 0 else W - 1 - i
            for y in range(10, GY):
                fold = (i + (y // 30)) % 7
                bulge = 28 - int(10 * ((y - 10) / (GY - 10)) ** 2)    # the curtain gathers towards the floor
                if i < bulge and fold in (0, 1, 3):
                    img.putpixel((x, y), rgba("ice"))
                elif i < bulge and fold == 5 and y % 2 == 0:
                    img.putpixel((x, y), rgba("steel"))
    return img
