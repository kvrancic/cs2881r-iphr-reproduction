"""The whitish dithered ground every slide sits on: white in the middle, ordered-dither bands of ice and a touch
of steel towards the edges. It is the same ground as the intro video's title card (intro/build/pixel.py), so the
video hands over to the deck without a visible change. No smooth gradients anywhere."""
from functools import lru_cache
import numpy as np
from PIL import Image
from pal import C
from px import W, H

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
# (start of band as squircle distance from the centre, colour A, colour B, share of B). Distance 1 = the edge.
BANDS = [(0.00, "white", "ice", 0.0), (0.76, "white", "ice", 0.25), (0.83, "white", "ice", 0.5),
         (0.89, "white", "ice", 0.75), (0.93, "ice", "steel", 0.0), (0.975, "ice", "steel", 0.25)]


@lru_cache(maxsize=4)
def ground(w=W, h=H):
    y, x = np.mgrid[0:h, 0:w]
    nx = np.abs(x + 0.5 - w / 2) / (w / 2)
    ny = np.abs(y + 0.5 - h / 2) / (h / 2)
    d = ((0.94 * nx) ** 6 + ny ** 6) ** (1 / 6)
    idx = np.zeros((h, w), int)
    for i, (start, *_r) in enumerate(BANDS):
        idx[d >= start] = i
    b4 = BAYER4[y % 4, x % 4]
    img = np.zeros((h, w, 3), np.uint8)
    for i, (_, a, b, share) in enumerate(BANDS):
        m = idx == i
        col = np.where((b4 < share)[..., None], np.array(C[b]), np.array(C[a]))
        img[m] = col[m]
    return Image.fromarray(img, "RGB").convert("RGBA")


def on_ground(sprite, k=4, pad=8):
    """Preview helper for sprite authors: the sprite centred on a patch of the real ground, upscaled k x."""
    w, h = sprite.width + 2 * pad, sprite.height + 2 * pad
    g = ground().crop((W // 2 - w // 2, H // 2 - h // 2, W // 2 - w // 2 + w, H // 2 - h // 2 + h)).copy()
    g.alpha_composite(sprite, (pad, pad))
    return g.resize((w * k, h * k), Image.NEAREST)
