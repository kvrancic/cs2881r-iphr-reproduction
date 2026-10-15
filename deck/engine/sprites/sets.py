"""One lit set per act, drawn over the whole 384x216 screen behind everything, in Endesga colours that carry no
meaning elsewhere in the deck (night, dusk, slate, steel, grape, plum, brown, clay, sand, ice, white; no blue, orange,
red, green, aqua or yellow as large fills). Light is ordered dither between two colours, as on the ground.

  lecture  the claim: an evening study, dusk-blue wall shading to grape, wood panelling, bookshelves at the edges
  lab      the reproduction: a lab at night, dark slate walls, three ceiling lamps casting cool light, slate tiles
  mapwall  by kind: a map room, wooden walls, a large parchment map, two hanging lamps over the scales
  survey   the variations: a field station at dusk, a dithered twilight sky with stars, hills on the horizon,
           an earth ground plane
  stage    the close: a theatre stage, a deep curtain, side curtains and a valance, two spotlights

The characters stand on light pools (common.floor). Panels, chats and cards are drawn light with an ink outline,
and free labels sit on light plates (build_story), so text keeps its contrast on the darker sets."""
import math
import numpy as np
from PIL import Image
from px import W, H, blank, rect, line, disc, ellipse
from pal import rgba, C

GY = 184
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def _mix(arr, mask, a, b, share):
    """Paint the pixels in mask with colour a, and a share of them (ordered dither) with colour b."""
    h, w = arr.shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    m = mask & (BAYER4[y % 4, x % 4] < share)
    arr[mask] = C[a] + (255,)
    arr[m] = C[b] + (255,)


def _gradient(arr, y0, y1, stops):
    """A vertical gradient between y0 and y1 through colour stops [(a, b, share), ...], one band per stop."""
    h, w = arr.shape[:2]
    n = len(stops)
    for k, (a, b, share) in enumerate(stops):
        ya, yb = y0 + (y1 - y0) * k // n, y0 + (y1 - y0) * (k + 1) // n
        mask = np.zeros((h, w), bool)
        mask[ya:yb, :] = True
        _mix(arr, mask, a, b, share)


def _cone(arr, cx, top, bottom, w0, w1, col, share):
    """A cone of light from (cx, top), w0 wide, to bottom, w1 wide: a share of its pixels in col (over what is there)."""
    h, w = arr.shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    t = np.clip((y - top) / max(1, bottom - top), 0, 1)
    half = (w0 + (w1 - w0) * t) / 2
    inside = (y >= top) & (y < bottom) & (np.abs(x - cx) <= half)
    fade = 1 - np.abs(x - cx) / np.maximum(half, 1)          # brighter in the middle of the cone
    m = inside & (BAYER4[y % 4, x % 4] < share * (0.5 + 0.5 * fade))
    arr[m] = C[col] + (255,)


def _img(arr):
    return Image.fromarray(arr, "RGBA")


def _planks(arr, y0, y1, base, dark, light, step=48):
    """Wood panelling: a base colour with a few lighter grain pixels, a dark seam every step px and a rail on top."""
    h, w = arr.shape[:2]
    mask = np.zeros((h, w), bool)
    mask[y0:y1, :] = True
    _mix(arr, mask, base, light, 0.12)
    arr[y0:y0 + 2, :] = C[dark] + (255,)
    arr[y0 + 2:y0 + 3, :] = C[light] + (255,)
    for x in range(0, w, step):
        arr[y0:y1, x] = C[dark] + (255,)


def _shelf(img, x, y, w, h):
    """A bookshelf: a brown frame, three shelves of books in muted colours."""
    rect(img, x, y, w, h, "plum"); rect(img, x + 2, y + 2, w - 4, h - 4, "night")
    cols = ("clay", "steel", "grape", "sand", "slate", "brown", "ice")
    for s in range(3):
        sy = y + 2 + (s + 1) * (h - 4) // 3
        rect(img, x + 2, sy - 2, w - 4, 2, "brown")
        bx, k = x + 3, s * 3
        while bx < x + w - 5:
            bw, bh = 3 + (k % 2), (h - 4) // 3 - 5 - (k % 3)
            rect(img, bx, sy - 2 - bh, bw, bh, cols[k % len(cols)])
            bx += bw + 1
            k += 1


def lecture():
    a = np.zeros((H, W, 4), np.uint8)
    _gradient(a, 0, 140, [("night", "dusk", 0.5), ("dusk", "night", 0.25), ("dusk", "grape", 0.25), ("dusk", "grape", 0.5)])
    _planks(a, 140, GY, "brown", "plum", "clay")
    _gradient(a, GY, H, [("plum", "brown", 0.5), ("plum", "night", 0.5)])
    _cone(a, 192, 0, 140, 40, 220, "grape", 0.35)             # the warm wash of the lamps on the wall
    img = _img(a)
    _shelf(img, 0, 30, 34, 110)
    _shelf(img, W - 34, 30, 34, 110)
    return img


def lab():
    a = np.zeros((H, W, 4), np.uint8)
    _gradient(a, 0, 150, [("night", "night", 0), ("night", "dusk", 0.5), ("dusk", "night", 0.25), ("dusk", "slate", 0.12)])
    for cx in (64, 192, 320):                                  # cool light from three ceiling lamps
        _cone(a, cx, 6, 150, 14, 110, "slate", 0.45)
    h, w = a.shape[:2]
    mask = np.zeros((h, w), bool); mask[150:GY, :] = True
    _mix(a, mask, "slate", "dusk", 0.25)
    for x in range(0, W, 16):                                  # tile grout
        a[150:GY, x] = C["dusk"] + (255,)
    for y in range(150, GY, 12):
        a[y, :] = C["dusk"] + (255,)
    _gradient(a, GY, H, [("dusk", "night", 0.5), ("night", "dusk", 0.25)])
    img = _img(a)
    for cx in (64, 192, 320):                                  # the lamps: a shade and a bulb
        rect(img, cx - 9, 2, 18, 4, "slate"); rect(img, cx - 7, 6, 14, 2, "steel"); rect(img, cx - 3, 8, 6, 1, "ice")
        rect(img, cx, 0, 1, 2, "steel")
    return img


CONTINENTS = [(110, 50, 46, 26), (132, 80, 20, 30), (190, 46, 30, 20), (200, 76, 26, 32), (236, 50, 70, 30),
              (278, 92, 26, 18), (330, 60, 22, 14)]   # (centre x, centre y, w, h) on the screen


def mapwall():
    a = np.zeros((H, W, 4), np.uint8)
    _planks(a, 0, GY, "brown", "plum", "clay", step=24)
    _gradient(a, GY, H, [("plum", "brown", 0.25), ("plum", "night", 0.5)])
    img = _img(a)
    x0, y0, x1, y1 = 30, 14, W - 30, 156                       # the parchment map in a dark frame
    rect(img, x0 - 3, y0 - 3, x1 - x0 + 6, y1 - y0 + 6, "plum")
    rect(img, x0, y0, x1 - x0, y1 - y0, "white")
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            if (xx + yy) % 2 == 0 and (xx % 4 == 0 or yy % 4 == 1):
                img.putpixel((xx, yy), rgba("sand"))
    for (cx, cy, w, h) in CONTINENTS:
        m = blank(w, h)
        ellipse(m, 0, 0, w, h, "sand")
        for yy in range(h):
            for xx in range(w):
                if m.getpixel((xx, yy))[3] and (xx + yy) % 2 == 0:
                    img.putpixel((cx - w // 2 + xx, cy - h // 2 + yy), rgba("sand"))
    for (px_, py_) in ((x0 + 5, y0 + 5), (x1 - 6, y0 + 5)):
        disc(img, px_, py_, 2, "plum")
    for cx in (82, 294):                                       # two hanging lamps over the scales
        rect(img, cx, 0, 1, 6, "plum"); rect(img, cx - 6, 6, 13, 4, "brown"); rect(img, cx - 4, 10, 9, 1, "sand")
    return img


def survey():
    a = np.zeros((H, W, 4), np.uint8)
    _gradient(a, 0, 150, [("night", "night", 0), ("night", "dusk", 0.5), ("dusk", "night", 0.25), ("dusk", "grape", 0.25),
                          ("grape", "dusk", 0.5), ("slate", "grape", 0.25), ("slate", "steel", 0.25)])
    h, w = a.shape[:2]
    rng = np.random.default_rng(7)
    for _ in range(40):                                        # stars in the darker sky
        sx, sy = rng.integers(0, W), rng.integers(0, 50)
        a[sy, sx] = C["white"] + (255,) if rng.random() < 0.5 else C["ice"] + (255,)
    xs = np.arange(W)
    hill = 138 + (6 * np.sin(xs / 37.0) + 4 * np.sin(xs / 13.0 + 1)).astype(int)   # hills on the horizon
    for x in range(W):
        a[hill[x]:150, x] = C["dusk"] + (255,)
    mask = np.zeros((h, w), bool); mask[150:H, :] = True
    _mix(a, mask, "brown", "clay", 0.12)
    a[150, :] = C["plum"] + (255,)
    _gradient(a, 196, H, [("plum", "brown", 0.5)])
    return _img(a)


def stage():
    a = np.zeros((H, W, 4), np.uint8)
    y, x = np.mgrid[0:H, 0:W]
    back = y < 160                                             # the back curtain: folds of grape and plum
    fold = ((x // 8) % 3)
    a[back & (fold == 0)] = C["plum"] + (255,)
    a[back & (fold == 1)] = C["grape"] + (255,)
    a[back & (fold == 2)] = C["grape"] + (255,)
    m = back & (fold == 2) & (BAYER4[y % 4, x % 4] < 0.25)
    a[m] = C["pink"] + (255,)
    _planks(a, 160, H, "brown", "plum", "clay", step=40)
    for cx in (120, 264):                                      # two spotlights onto the stage
        _cone(a, cx, 0, 200, 10, 150, "white", 0.22)
    img = _img(a)
    rect(img, 0, 0, W, 6, "plum")                              # the valance, with a scalloped hem
    for k in range(0, W, 24):
        for dx in range(24):
            rect(img, k + dx, 6, 1, max(1, round(3 * (1 - ((dx - 11.5) / 12) ** 2))), "plum")
    for side in (0, 1):                                        # the side curtains, gathered at the edges
        for i in range(16):
            xx = i if side == 0 else W - 1 - i
            for yy in range(6, GY + 10):
                if i >= 16 - int(6 * ((yy - 6) / (GY + 4)) ** 2):
                    continue
                img.putpixel((xx, yy), rgba("night" if (i + yy // 24) % 4 == 0 else "plum"))
    return img


def spotlight(cx, cy, rx, ry):
    """The lights dimmed for a section's opening: a night dither over the whole stage except an ellipse of light
    around the subject (cx, cy, radii rx, ry), with a dithered edge."""
    img = blank(W, H)
    N = rgba("night")
    for y in range(H):
        for x in range(W):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d < 1:
                continue
            if d < 1.25:
                if x % 2 == 0 and y % 2 == 0:
                    img.putpixel((x, y), N)
            elif (x + y) % 2 == 0:
                img.putpixel((x, y), N)
    return img
