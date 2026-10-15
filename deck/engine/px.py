"""Pixel helpers: ASCII sprites, primitives, text. Everything is drawn at native 384x216."""
import os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
from pal import C, rgba

W, H = 384, 216
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "art", "fonts")


def ascii_sprite(rows, key, flip=False):
    """rows: list of equal-length strings; key: char -> palette name; '.' and ' ' are transparent."""
    rows = [r for r in rows if r.strip("\n") != ""] if isinstance(rows, list) else [r for r in rows.strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    img = Image.new("RGBA", (w, len(rows)), (0, 0, 0, 0))
    p = img.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in ". ":
                continue
            name = key.get(ch)
            if name is None:
                raise KeyError(f"char {ch!r} not in key (row {y}: {r})")
            p[x, y] = rgba(name) if isinstance(name, str) else name
    return img.transpose(Image.FLIP_LEFT_RIGHT) if flip else img


def blank(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def paste(dst, src, x, y):
    dst.alpha_composite(src, (int(x), int(y)))
    return dst


def rect(img, x, y, w, h, color, a=255):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=rgba(color, a) if isinstance(color, str) else color)
    return img


def frame(img, x, y, w, h, color):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=rgba(color) if isinstance(color, str) else color)
    return img


def line(img, x0, y0, x1, y1, color):
    """Bresenham line, exact pixels."""
    p = img.load()
    col = rgba(color) if isinstance(color, str) else color
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        if 0 <= x0 < img.width and 0 <= y0 < img.height:
            p[x0, y0] = col
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy
    return img


def disc(img, cx, cy, r, color):
    p = img.load(); col = rgba(color) if isinstance(color, str) else color
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.8 and 0 <= x < img.width and 0 <= y < img.height:
                p[x, y] = col
    return img


def ellipse(img, x, y, w, h, color):
    d = ImageDraw.Draw(img)
    d.ellipse([x, y, x + w - 1, y + h - 1], fill=rgba(color) if isinstance(color, str) else color)
    return img


def poly(img, pts, color):
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=rgba(color) if isinstance(color, str) else color)
    return img


def dither(img, x, y, w, h, color, pattern=0):
    """Checkerboard dither (pattern 0) or sparse 25% (pattern 1)."""
    p = img.load(); col = rgba(color) if isinstance(color, str) else color
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if not (0 <= xx < img.width and 0 <= yy < img.height):
                continue
            if pattern == 0 and (xx + yy) % 2 == 0:
                p[xx, yy] = col
            elif pattern == 1 and xx % 2 == 0 and yy % 2 == 0:
                p[xx, yy] = col
            elif pattern == 2 and (xx % 4 == 0 and yy % 4 == 0 or xx % 4 == 2 and yy % 4 == 2):
                p[xx, yy] = col
    return img


def outline(img, color="ink"):
    """Add a 1px outline around opaque pixels (grows the image by 1px each side)."""
    w, h = img.size
    out = blank(w + 2, h + 2)
    a = img.split()[3].load()
    p = out.load(); col = rgba(color) if isinstance(color, str) else color
    for y in range(h):
        for x in range(w):
            if a[x, y] > 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    p[x + 1 + dx, y + 1 + dy] = col
    out.alpha_composite(img, (1, 1))
    return out


def recolor(img, mapping):
    """mapping: palette name -> palette name."""
    src = {C[a]: C[b] for a, b in mapping.items()}
    out = img.copy(); p = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, al = p[x, y]
            if al and (r, g, b) in src:
                p[x, y] = src[(r, g, b)] + (al,)
    return out


def flip(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def scale_int(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


@lru_cache(maxsize=64)
def font(name="Jersey10", size=20):
    """size 20 = one font pixel per canvas pixel. Jersey10 is drawn on a 75-unit grid in a 1400-unit em,
    so the exact size is 56/3 px per 20; anything else smears the glyphs."""
    if name == "Jersey10":
        return ImageFont.truetype(os.path.join(FONTS, f"{name}.ttf"), size * 56 / 60)
    return ImageFont.truetype(os.path.join(FONTS, f"{name}.ttf"), size)


HI = 10   # scale of smooth images (matches the deck's export scale)
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"


def hitext(s, color="white", size=10, face="Medium", spacing=1.3):
    """Anti-aliased Avenir Next for text that must read like print (the contact slide).
    size is in native pixels. Returns (transparent native stand-in, HI-x image)."""
    import math
    f = ImageFont.truetype(AVENIR, int(size * HI), index={"Bold": 0, "Demi": 2, "Medium": 5, "Regular": 7}[face])
    lines = s.split("\n")
    lh = int(size * HI * spacing)
    top = min(f.getbbox(l)[1] for l in lines if l)
    bot = (len(lines) - 1) * lh + max(f.getbbox(l)[3] for l in lines if l)
    w = math.ceil(max(f.getlength(l) for l in lines) / HI) + 1
    h = math.ceil((bot - top) / HI) + 1
    img = Image.new("RGBA", (w * HI, h * HI), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        d.text((0, i * lh - top), l, font=f, fill=rgba(color))
    return blank(w, h), img


def _kern(a, b):
    """Jersey10's lowercase r carries a wide right bearing that splits words ("Par is"); pull the next letter in."""
    return -1 if a == "r" and b.isalpha() else 0


def _klen(f, l, kern=True):
    return f.getlength(l) + (sum(_kern(a, b) for a, b in zip(l, l[1:])) if kern else 0)


def _kdraw(d, f, x, y, l, fill, kern=True):
    if not kern:
        d.text((x, y), l, font=f, fill=fill)
        return
    for j, ch in enumerate(l):
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + (_kern(ch, l[j + 1]) if j + 1 < len(l) else 0)


def text(s, color="white", size=20, name="Jersey10", shadow=None, maxw=None, spacing=2, align="left", line=False):
    """Render crisp pixel text to a tight RGBA image. size 20 = Jersey10 native 1px strokes."""
    f = font(name, size)
    lines = []
    for para in s.split("\n"):
        if maxw is None:
            lines.append(para); continue
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if f.getlength(t) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur); cur = word
        lines.append(cur)
    bb0 = f.getbbox("Ag")
    lh = (bb0[3] - bb0[1]) + spacing + 1
    kern = name == "Jersey10"
    tw = int(max(_klen(f, l, kern) for l in lines)) + 2
    asc, desc = f.getmetrics()
    th = lh * (len(lines) - 1) + asc + desc + 2
    img = blank(tw, th)
    d = ImageDraw.Draw(img); d.fontmode = "1"
    for i, l in enumerate(lines):
        lw = _klen(f, l, kern)
        x = 0 if align == "left" else (tw - 2 - lw) // 2 if align == "center" else tw - 2 - lw
        if shadow:
            _kdraw(d, f, x + 1, i * lh + 1, l, rgba(shadow), kern)
        _kdraw(d, f, x, i * lh, l, rgba(color), kern)
    bb = img.getbbox()
    if line and bb:
        # crop to the font's ascender and descender lines, so word chips share a baseline and a height
        rb = f.getbbox("Ag")
        return img.crop((0, min(bb[1], rb[1]), img.width, max(bb[3], (len(lines) - 1) * lh + rb[3])))
    return img.crop((0, bb[1], img.width, bb[3])) if bb else img


def canvas(bg="ink"):
    return Image.new("RGBA", (W, H), rgba(bg))
