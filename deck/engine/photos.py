"""The founders' real photos, cropped to matching head-and-shoulders squares and lightly pixelated into the
deck's world: resampled to a 2x-finer grid than the art (each pixel half a native pixel), mapped onto Endesga 32
with a gentle ordered dither. The card around them draws the ink frame."""
import os
from functools import lru_cache
import numpy as np
from PIL import Image, ImageEnhance
from pal import C, HEX

DECK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = os.path.join(DECK, "photos")

# (file, crop box in the original pixels): head and shoulders, eyes at about 40% of the height
CROPS = {
    "luka": ("luka.png", (22, 6, 192, 176)),
    "djordje": ("djordje.png", (150, 10, 690, 550)),
    "karlo": ("karlo.jpg", (80, 260, 2280, 2460)),
}
SCALE = 0.5        # native pixels per portrait pixel
BAYER4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16.0
GREYS = ["white", "ice", "steel", "slate", "dusk", "night", "ink"]


def _map(a, names, strength):
    pal = np.array([C[k] for k in names], np.float64)
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    a = a + (BAYER4[yy % 4, xx % 4][..., None] - 0.5) * 40 * strength
    d = ((a[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
    return pal[d.argmin(-1)].astype(np.uint8)


@lru_cache(maxsize=8)
def portrait(who, lit=True, native=64):
    f, box = CROPS[who]
    im = Image.open(os.path.join(PHOTOS, f)).convert("RGB").crop(box)
    n = int(native / SCALE)
    im = im.resize((n, n), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    a = np.asarray(im, np.float64)
    if lit:
        out = _map(a, list(HEX), 0.6)
    else:
        g = a.mean(-1, keepdims=True).repeat(3, -1) * 0.8 + 50
        out = _map(g, GREYS, 0.8)
    return Image.fromarray(out, "RGB").convert("RGBA")


if __name__ == "__main__":
    sheet = Image.new("RGBA", (128 * 3 * 4, 128 * 2 * 4), (255, 255, 255, 255))
    for i, w in enumerate(CROPS):
        for j, lit in enumerate((True, False)):
            p = portrait(w, lit)
            sheet.paste(p.resize((512, 512), Image.NEAREST), (i * 512, j * 512))
    sheet.save(os.path.join(DECK, "build", "review", "photos-portraits.png"))
