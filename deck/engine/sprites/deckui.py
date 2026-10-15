"""Code-drawn UI: titles, big numbers, labels, chips, the orientation cue plate, pixel windows, ticks and
crosses. Text is Jersey 10 at multiples of size 20 only (20 = 1px strokes), so every glyph lands on whole pixels."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image
from px import blank, rect, frame, text, paste, line, poly, outline, disc, dither, font, _klen, _kdraw
from pal import rgba, C

SHADE = {"red": ("rose", "wine"), "gold": ("yellow", "orange"), "ink": ("dusk", "ink"), "navy": ("sky", "night"),
         "green": ("yellow", "leaf"), "sky": ("cyan", "navy"), "wine": ("red", "plum"), "white": ("white", "ice")}


def runs(parts, size=20, shadow=None):
    """One line of text in several colours: parts = [(string, colour), ...]."""
    from PIL import ImageDraw
    f = font("Jersey10", size)
    s = "".join(p[0] for p in parts)
    w = int(_klen(f, s)) + 4 + (size // 20 if shadow else 0)
    asc, desc = f.getmetrics()
    img = blank(w, asc + desc + 4)
    d = ImageDraw.Draw(img); d.fontmode = "1"
    passes = ([(size // 20, size // 20, shadow)] if shadow else []) + [(0, 0, None)]
    for dx, dy, sc in passes:
        x = 0
        for k, (txt, col) in enumerate(parts):
            nxt = parts[k + 1][0][:1] if k + 1 < len(parts) else ""
            _kdraw(d, f, x + dx, dy, txt, rgba(sc or col))
            x += _klen(f, txt) + (-1 if txt[-1:] == "r" and nxt.isalpha() else 0)
    bb = img.getbbox()
    return img.crop(bb) if bb else img


def say(s, color="ink", size=20, maxw=None, align="left"):
    """Plain text on the white ground."""
    return text(s, color, size, maxw=maxw, align=align)


def big(s, face="red", size=160, depth=None, drop="ice"):
    """A chunky arcade title: face colour with a lit top edge and a shaded bottom edge on every stroke,
    an ink outline and a drop shadow on the ground. Used for CANCER and the big numbers."""
    hi, lo = SHADE.get(face, ("white", "ink"))
    t = text(s, face, size)
    px_ = size // 20                      # pixels per font pixel
    w, h = t.size
    a = t.split()[3].load()
    img = blank(w, h)
    p = img.load()
    for y in range(h):
        for x in range(w):
            if not a[x, y]:
                continue
            top = y - 1 < 0 or not a[x, y - 1]
            below = [y + k < h and a[x, y + k] for k in range(1, max(2, px_ // 2) + 1)]
            if top:
                col = hi
            elif not all(below):
                col = lo
            else:
                col = face
            p[x, y] = rgba(col)
    # left edges lit as well (light from the top-left)
    for y in range(h):
        for x in range(w):
            if a[x, y] and (x == 0 or not a[x - 1, y]) and p[x, y][:3] == C[face]:
                p[x, y] = rgba(hi)
    img = outline(img, "ink")
    d = depth if depth is not None else max(1, px_ // 2)
    out = blank(img.width + d, img.height + d)
    sh = Image.new("RGBA", img.size, rgba(drop))
    out.paste(sh, (d, d), img)
    out.alpha_composite(img, (0, 0))
    return out


def chip(s, fg="ink", bg="sand", pad=3, size=20, border="ink"):
    """A small rounded label."""
    t = text(s, fg, size, line=True)
    img = blank(t.width + pad * 2 + 2, t.height + pad * 2 + 2)
    rect(img, 1, 0, img.width - 2, img.height, border); rect(img, 0, 1, img.width, img.height - 2, border)
    rect(img, 1, 1, img.width - 2, img.height - 2, bg)
    rect(img, 2, img.height - 2, img.width - 4, 1, "ink", 50)
    paste(img, t, pad + 1, pad + 1)
    return img


def tag(s, fg="ink", bg="white", point="down", size=20):
    """A pointer label: a chip with a small tail pointing at the thing it names."""
    c = chip(s, fg, bg, size=size)
    img = blank(c.width, c.height + 4)
    if point == "down":
        paste(img, c, 0, 0)
        cx = c.width // 2
        poly(img, [(cx - 3, c.height - 1), (cx + 3, c.height - 1), (cx, c.height + 3)], "ink")
        poly(img, [(cx - 2, c.height - 2), (cx + 2, c.height - 2), (cx, c.height + 1)], bg)
    else:
        paste(img, c, 0, 4)
        cx = c.width // 2
        poly(img, [(cx - 3, 4), (cx + 3, 4), (cx, 0)], "ink")
        poly(img, [(cx - 2, 5), (cx + 2, 5), (cx, 2)], bg)
    return img


def window(w, h, title="", dark=False, url=None):
    """A pixel-art window frame with a 16px title bar. The content area (x 3..w-4, y 18..h-4) is left
    transparent for a screenshot placed under it; dark=True gives a terminal with a night content area."""
    TB = 16
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, TB, "dusk" if dark else "ice")
    rect(img, 1, 1, w - 2, 1, "slate" if dark else "white")
    for i, c in enumerate(("red", "gold", "green")):
        disc(img, 7 + i * 8, 1 + TB // 2, 2, c)
    if title:
        t = text(title, "ice" if dark else "slate", 20)
        paste(img, t, 31, 1 + (TB - t.height) // 2)
    if url:
        u = text(url, "slate", 20)
        bw = min(w - 70, max(u.width + 14, 90))
        bx = max(32, (w - bw) // 2)
        rect(img, bx, 3, bw, TB - 4, "white"); frame(img, bx, 3, bw, TB - 4, "steel")
        paste(img, u, bx + 7, 3 + (TB - 4 - u.height) // 2)
    rect(img, 1, TB + 1, w - 2, 1, "ink")
    if dark:
        rect(img, 2, TB + 2, w - 4, h - TB - 4, "night")
    else:
        img.paste((0, 0, 0, 0), (3, TB + 2, w - 3, h - 3))
        rect(img, 1, TB + 2, 2, h - TB - 4, "ice"); rect(img, w - 3, TB + 2, 2, h - TB - 4, "ice")
        rect(img, 1, h - 3, w - 2, 2, "ice")
    return img


WIN_TOP = 18   # first content row of window()


def term_lines(lines, maxw=None):
    """Terminal text: lines = [[(text, colour), ...], ...] drawn one per row on a transparent image."""
    rows = [runs(l) if l else blank(1, 9) for l in lines]
    w = max(r.width for r in rows)
    img = blank(w, len(rows) * 13)
    for i, r in enumerate(rows):
        paste(img, r, 0, i * 13 + (10 - r.height if r.height < 10 else 0))
    return img


def stamp(s="MEASURED", color="green"):
    t = text(s, color, 20)
    w, h = t.width + 12, t.height + 10
    img = blank(w, h)
    frame(img, 0, 0, w, h, color); frame(img, 2, 2, w - 4, h - 4, color)
    rect(img, 1, 1, w - 2, 1, color)
    paste(img, t, 6, 5)
    # a few worn pixels, like ink on paper
    for (x, y) in ((5, 0), (w - 9, h - 1), (0, h // 2), (w - 1, 3), (w // 2, 2)):
        img.putpixel((x, y), (0, 0, 0, 0))
    return outline(img, "white")


def dashed(w, h, color="steel", q=True):
    """A dashed outline marking an empty spot, optionally with a question mark."""
    img = blank(w, h)
    for x in range(w):
        if (x // 3) % 2 == 0:
            img.putpixel((x, 0), rgba(color)); img.putpixel((x, h - 1), rgba(color))
    for y in range(h):
        if (y // 3) % 2 == 0:
            img.putpixel((0, y), rgba(color)); img.putpixel((w - 1, y), rgba(color))
    if q:
        t = text("?", color, 40)
        paste(img, t, (w - t.width) // 2, (h - t.height) // 2)
    return img


def qmark(color="gold", size=40):
    t = text("?", color, size)
    return outline(t, "ink")


def check(color="green"):
    from px import ascii_sprite
    return ascii_sprite("""
.........KK
........KGK
.......KGGK
.KK...KGGK.
KGGK.KGGK..
.KGGKGGK...
..KGGGK....
...KGK.....
....K......
""", {"K": "ink", "G": color})


def shadow(w=24, h=4):
    """A soft dithered contact shadow under a character's feet."""
    img = blank(w, h)
    cx, cy = (w - 1) / 2, (h - 1) / 2
    for y in range(h):
        for x in range(w):
            d = ((x - cx) / (w / 2)) ** 2 + ((y - cy) / (h / 2)) ** 2
            if d <= 0.55 or (d <= 1.0 and (x + y) % 2 == 0):
                img.putpixel((x, y), rgba("ice"))
    return img


def arrow(length=24, color="ink", thick=2):
    """A right-pointing pixel arrow."""
    h = thick + 6
    img = blank(length, h)
    cy = h // 2
    rect(img, 0, cy - thick // 2, length - 4, thick, color)
    for k in range(4):
        hh = max(1, 2 * (3 - k) + (thick % 2 == 0) * 0)
        rect(img, length - 4 + k, cy - thick // 2 - (3 - k) + (thick // 2), 1, hh + (1 if thick % 2 == 0 and k < 3 else 0) or 1, color)
    return img


def strike(w, h, color="red"):
    """A thick diagonal strike-through, for crossing a label out."""
    img = blank(w, h)
    for x in range(w):
        y = round(h - 1 - x * (h - 1) / max(w - 1, 1))
        for dy in (-1, 0, 1):
            if 0 <= y + dy < h:
                img.putpixel((x, y + dy), rgba(color))
    return img


def caption(s, color="ink"):
    """A short descriptive line on a white plate, for the bottom of the illustrated slides."""
    t = text(s, color, 20)
    w, h = t.width + 12, t.height + 8
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "steel"); rect(img, 0, 1, w, h - 2, "steel")
    rect(img, 1, 1, w - 2, h - 2, "white")
    paste(img, t, 6, 4)
    return img



def cue(s, size=20):
    """Orientation cue: a few of the speaker's own keywords, white on an ink plate with a yellow accent bar."""
    t = text(s, "white", size, line=True)
    w, h = t.width + 14, t.height + 8
    img = blank(w, h)
    rect(img, 0, 0, w, h, "ink")
    rect(img, 0, 0, 3, h, "yellow")
    paste(img, t, 9, 4)
    return img


def cross(color="red"):
    """A pixel X the size of check()."""
    from px import ascii_sprite
    return ascii_sprite("""
KK.....KK
KRK...KRK
.KRK.KRK.
..KRKRK..
...KRK...
..KRKRK..
.KRK.KRK.
KRK...KRK
KK.....KK
""", {"K": "ink", "R": color})


def plate(s, bg="red", fg="white", size=40, pad=4):
    """A bold answer plate (YES / NO): coloured face, lit top edge, shaded bottom edge, ink outline."""
    hi, lo = SHADE.get(bg, ("white", "ink"))
    t = text(s, fg, size, line=True)
    w, h = t.width + pad * 2 + 4, t.height + pad * 2 + 2
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, h - 2, bg)
    rect(img, 1, 1, w - 2, 1, hi)
    rect(img, 1, h - 3, w - 2, 2, lo)
    paste(img, t, pad + 2, pad + 1)
    return img
