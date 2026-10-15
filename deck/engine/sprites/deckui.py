"""Code-drawn UI for the 3B Therapeutics deck: titles, big numbers, labels, health bars, permission badges,
pixel windows, the instrument readout, the gene-switch panel, tubes and light. Text is Jersey 10 at multiples
of size 20 only (20 = 1px strokes), so every glyph lands on whole pixels."""
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


def hpbar(frac=1.0, w=64, h=7):
    """Arcade health bar: ink frame, dark trough, yellow fill with a gold underside, red when nearly empty."""
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, h - 2, "night")
    fw = int(round((w - 2) * max(0.0, min(1.0, frac))))
    if fw > 0:
        col, sh = ("yellow", "gold") if frac > 0.2 else ("red", "wine")
        rect(img, 1, 1, fw, h - 2, col)
        rect(img, 1, h - 3, fw, 1, sh)
        rect(img, 1, 1, fw, 1, "white" if col == "yellow" else "rose")
    # notches every 25%
    for k in (1, 2, 3):
        x = 1 + round((w - 2) * k / 4)
        rect(img, x, h - 3, 1, 1, "ink", 120)
    return img


def badge(perm="r--"):
    """A permission badge: an eye for read, a pencil for write, and the unix permission string."""
    t = text(perm, "ink", 40)
    eye = _eye()
    pencil = _pencil(on="w" in perm)
    w = 6 + eye.width + 4 + pencil.width + 6 + t.width + 8
    h = max(t.height, eye.height, pencil.height) + 12
    img = blank(w, h)
    bg = "sand" if "w" not in perm else "yellow"
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 2, 2, w - 4, h - 4, bg)
    rect(img, 2, h - 4, w - 4, 2, "gold" if "w" in perm else "peach")
    x = 6
    paste(img, eye, x, (h - eye.height) // 2); x += eye.width + 4
    paste(img, pencil, x, (h - pencil.height) // 2); x += pencil.width + 6
    paste(img, t, x, (h - t.height) // 2)
    return img


def _eye():
    from px import ascii_sprite
    return ascii_sprite("""
...KKKKKKK...
.KKWWWWWWWKK.
KWWWWKKKWWWWK
KWWWKKSKKWWWK
KWWWKKKKKWWWK
.KKWWKKKWWKK.
...KKKKKKK...
""", {"K": "ink", "W": "white", "S": "white"})


def _pencil(on=True):
    from px import ascii_sprite
    img = ascii_sprite("""
.........KK.
........KRRK
.......KOOKK
......KOOOK.
.....KOOOK..
....KOOOK...
...KOOOK....
..KSSOK.....
..KSSK......
.KKKK.......
.K..........
""", {"K": "ink", "R": "rose", "O": "orange", "S": "sand"})
    if not on:
        from px import recolor
        img = recolor(img, {"rose": "ice", "orange": "steel", "sand": "ice"})
        img.putalpha(img.split()[3].point(lambda v: v * 0.35))
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


def readout(frac=1.0, gene="SPP1", label=None, w=120):
    """An instrument panel: the gene's level as a bar, with a numeric delta when it has fallen."""
    h = 52
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, h - 2, "dusk")
    rect(img, 1, 1, w - 2, 1, "slate")
    rect(img, 4, 4, w - 8, h - 8, "night")
    t = text(gene, "white", 8, name="PressStart2P")
    paste(img, t, 8, 10)
    lv = text("level", "steel", 20)
    paste(img, lv, w - 8 - lv.width, 8)
    bx, by, bw, bh = 8, 22, w - 16, 10
    rect(img, bx, by, bw, bh, "ink")
    fw = int(round((bw - 2) * frac))
    rect(img, bx + 1, by + 1, bw - 2, bh - 2, "dusk")
    # the original level as a dithered ghost when it has fallen
    if frac < 1:
        dither(img, bx + 1, by + 1, bw - 2, bh - 2, "slate", 0)
    col = "red" if frac >= 0.999 else "green"
    rect(img, bx + 1, by + 1, max(fw, 1), bh - 2, col)
    rect(img, bx + 1, by + 1, max(fw, 1), 1, "rose" if col == "red" else "yellow")
    for k in range(1, 4):
        rect(img, bx + 1 + round((bw - 2) * k / 4), by + bh, 1, 2, "slate")
    if label:
        col = "green" if frac < 1 else "white"
        if isinstance(label, tuple):          # (gene symbol, rest): the gene in its own legible face
            g = text(label[0], col, 8, name="PressStart2P")
            r = text(label[1], col, 20)
            paste(img, g, 8, 38)
            paste(img, r, 8 + g.width + 4, 36)
        else:
            paste(img, text(label, col, 20), 8, 36)
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


def switch(on=True, label=None):
    """A toggle switch with a gene label under it."""
    sw = blank(12, 18)
    rect(sw, 1, 0, 10, 18, "ink"); rect(sw, 0, 1, 12, 16, "ink")
    rect(sw, 2, 2, 8, 14, "white" if on else "ice")
    rect(sw, 3, 3, 6, 12, "ice" if on else "steel")
    if on:
        rect(sw, 3, 3, 6, 6, "green"); rect(sw, 3, 3, 6, 1, "yellow"); rect(sw, 3, 8, 6, 1, "leaf")
    else:
        rect(sw, 3, 9, 6, 6, "slate"); rect(sw, 3, 9, 6, 1, "steel"); rect(sw, 3, 14, 6, 1, "dusk")
    if not label:
        return sw
    t = text(label, "ink", 20)
    w = max(sw.width, t.width)
    img = blank(w, sw.height + 2 + t.height)
    paste(img, sw, (w - sw.width) // 2, 0)
    paste(img, t, (w - t.width) // 2, sw.height + 2)
    return img


GENES = ("MTOR", "CEBPA", "SPI1", "ETS1", "FLCN", "MEF2D")


def switch_panel(off=()):
    """The gene switch panel that sits on the macrophage: six measured regulators, three by two."""
    cells = [switch(g not in off, g) for g in GENES]
    cw = max(c.width for c in cells) + 4
    ch = max(c.height for c in cells) + 3
    w, h = 3 * cw + 8, 2 * ch + 8
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, h - 2, "steel")
    rect(img, 2, 2, w - 4, h - 4, "ice")
    rect(img, 2, 2, w - 4, 1, "white")
    for i, c in enumerate(cells):
        x = 4 + (i % 3) * cw + (cw - c.width) // 2
        y = 5 + (i // 3) * ch
        paste(img, c, x, y)
    for (x, y) in ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)):
        img.putpixel((x, y), rgba("slate"))
    return img


def tube(points, w=None, h=None, color="green", drops=()):
    """A drip tube through the given points (a polyline in the image's own coordinates), 2px wide with an
    ink edge. drops: list of point indices fractions (t in 0..1 along the tube) where a poison drop sits."""
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    W_ = w or max(xs) + 4
    H_ = h or max(ys) + 4
    img = blank(W_, H_)
    segs = list(zip(points, points[1:]))

    def thick(col, r):
        for (x0, y0), (x1, y1) in segs:
            n = max(abs(x1 - x0), abs(y1 - y0), 1)
            for i in range(n + 1):
                x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        if 0 <= x + dx < W_ and 0 <= y + dy < H_:
                            img.putpixel((x + dx, y + dy), rgba(col))
    thick("ink", 2)
    thick("ice", 1)
    for (x0, y0), (x1, y1) in segs:
        line(img, x0, y0, x1, y1, color)
    # drops along the tube
    lens = [max(abs(b[0] - a[0]), abs(b[1] - a[1])) for a, b in segs]
    tot = sum(lens)
    for t in drops:
        d = t * tot
        for (a, b), L in zip(segs, lens):
            if d <= L:
                x = round(a[0] + (b[0] - a[0]) * d / max(L, 1)); y = round(a[1] + (b[1] - a[1]) * d / max(L, 1))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        img.putpixel((min(max(x + dx, 0), W_ - 1), min(max(y + dy, 0), H_ - 1)), rgba("leaf"))
                img.putpixel((x, y), rgba("green")); img.putpixel((max(x - 1, 0), max(y - 1, 0)), rgba("yellow"))
                break
            d -= L
    return img


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


def beam(w=60, h=80, color="yellow"):
    """A cone of light falling from the top centre, dithered (no smooth alpha)."""
    img = blank(w, h)
    for y in range(h):
        half = 2 + (w / 2 - 2) * y / max(h - 1, 1)
        x0, x1 = int(w / 2 - half), int(w / 2 + half)
        for x in range(max(0, x0), min(w, x1 + 1)):
            edge = x - x0 < 2 or x1 - x < 2
            if edge:
                img.putpixel((x, y), rgba("gold"))
            elif (x + y) % 2 == 0:
                img.putpixel((x, y), rgba(color))
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


def card(w=120, h=196, lit=False, name=None, facts=(), well=72):
    """A character-select card: frame, a portrait well (the stylised photo is placed on top of it by the story),
    a name plate and the credentials, one fact per block with a small gap between facts."""
    img = blank(w, h)
    border = "gold" if lit else "steel"
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, h - 2, border)
    rect(img, 3, 3, w - 6, h - 6, "ink")
    rect(img, 4, 4, w - 8, h - 8, "white" if lit else "ice")
    wx = (w - (well + 2)) // 2
    rect(img, wx, 7, well + 2, well + 2, "ink")
    y = 7 + well + 5
    if name:
        t = text(name, "ink" if lit else "slate", 20)
        rect(img, 4, y, w - 8, 14, "gold" if lit else "steel")
        paste(img, t, (w - t.width) // 2, y + 2)
        y += 19
    for k, f in enumerate(facts):
        t = text(f, "ink" if lit else "slate", 20, maxw=w - 14)
        paste(img, t, 7, y)
        y += t.height + 2
        if k < len(facts) - 1:          # a dotted rule between facts, so two facts never read as one
            for x in range(7, w - 7, 2):
                img.putpixel((x, y), rgba("steel" if lit else "slate"))
            y += 3
    return img


def card_well(w=120, well=72):
    """Where the portrait goes inside card(): (dx, dy) from the card's top-left."""
    return (w - (well + 2)) // 2 + 1, 8


def timer(s="36:00:00", color="green", size=40):
    """A segment-style clock readout on a dark plate."""
    t = text(s, color, size)
    w, h = t.width + 16, t.height + 14
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, h - 2, "night")
    rect(img, 1, 1, w - 2, 1, "dusk")
    paste(img, t, 8, 7)
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


def lens(d=54, see_through=False):
    """What the magnifying glass shows: a bright disc with a dithered rim, drawn behind the magnified thing.
    see_through=True dithers the disc so the body under the lens still shows."""
    img = blank(d, d)
    r = d / 2
    for y in range(d):
        for x in range(d):
            q = ((x + 0.5 - r) ** 2 + (y + 0.5 - r) ** 2) ** 0.5
            if see_through and q <= r:
                if (x + y) % 2 == 0:
                    img.putpixel((x, y), rgba("white"))
            elif q <= r - 4:
                img.putpixel((x, y), rgba("white"))
            elif q <= r:
                img.putpixel((x, y), rgba("ice" if (x + y) % 2 else "white"))
    return img


def coin():
    """One gold coin, seen a little from the side."""
    from px import ascii_sprite
    return ascii_sprite("""
..KKKK..
.KYYYYK.
KYWYYGOK
KYYGGGOK
KYYYGOOK
.KOOOOK.
..KKKK..
""", {"K": "ink", "Y": "yellow", "W": "white", "G": "gold", "O": "orange"})


def strike(w, h, color="red"):
    """A thick diagonal strike-through, for crossing a label out."""
    img = blank(w, h)
    for x in range(w):
        y = round(h - 1 - x * (h - 1) / max(w - 1, 1))
        for dy in (-1, 0, 1):
            if 0 <= y + dy < h:
                img.putpixel((x, y + dy), rgba(color))
    return img


def cable(h, color="steel"):
    img = blank(3, h)
    rect(img, 0, 0, 3, h, "ink")
    rect(img, 1, 0, 1, h, color)
    return img


def wordmark(size=60):
    """3B Therapeutics, as the intro video's title card sets it: "3B" in navy, "Therapeutics" in ink."""
    return runs([("3B ", "navy"), ("Therapeutics", "ink")], size, shadow="ice")


def ray(w, h, color="yellow"):
    """A slanted cone of light from a point at the top-left corner (x 3) down to a 24px pool at the bottom-right,
    dithered. Flip it for a ray that leans the other way."""
    img = blank(w, h)
    for y in range(h):
        t = y / max(h - 1, 1)
        c = 3 + (w - 15 - 3) * t
        half = 2 + 10 * t
        x0, x1 = int(round(c - half)), int(round(c + half))
        for x in range(max(0, x0), min(w, x1 + 1)):
            if x - x0 < 1 or x1 - x < 1:
                img.putpixel((x, y), rgba("gold"))
            elif (x + y) % 2 == 0:
                img.putpixel((x, y), rgba(color))
    return img


def mini_switch(on=True):
    """A small toggle (8x12) for the panel on the cell's belly."""
    sw = blank(8, 12)
    rect(sw, 1, 0, 6, 12, "ink"); rect(sw, 0, 1, 8, 10, "ink")
    rect(sw, 1, 1, 6, 10, "white")
    if on:
        rect(sw, 2, 2, 4, 4, "green"); rect(sw, 2, 2, 4, 1, "yellow")
        rect(sw, 2, 6, 4, 4, "ice")
    else:
        rect(sw, 2, 2, 4, 4, "ice")
        rect(sw, 2, 6, 4, 4, "slate"); rect(sw, 2, 9, 4, 1, "dusk")
    return sw


def belly_panel(off=()):
    """Six gene switches, three by two, small enough to sit on the macrophage's belly patch (52x30).
    The switch order is GENES; the flipped one is labelled with a tag by the story."""
    w, h = 46, 34
    img = blank(w, h)
    rect(img, 1, 0, w - 2, h, "ink"); rect(img, 0, 1, w, h - 2, "ink")
    rect(img, 1, 1, w - 2, h - 2, "steel"); rect(img, 2, 2, w - 4, h - 4, "ice"); rect(img, 2, 2, w - 4, 1, "white")
    for i, g in enumerate(GENES):
        x = 5 + (i % 3) * 13
        y = 4 + (i // 3) * 15
        paste(img, mini_switch(g not in off), x, y)
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


def gene(s, color="ink", size=8, shadow=None):
    """Gene symbols in Press Start 2P (8px grid, so size 8 is one canvas pixel per font pixel): its I has
    serifs and its 1 a foot, so SPI1 never reads SPII."""
    return text(s, color, size, name="PressStart2P")


def planks(w=26, h=30):
    """Boards nailed across an opening: two crossed planks in brown with ink edges."""
    img = blank(w, h)
    for y0 in (h // 3, 2 * h // 3):
        rect(img, 0, y0 - 2, w, 5, "ink"); rect(img, 1, y0 - 1, w - 2, 3, "clay"); rect(img, 1, y0 - 1, w - 2, 1, "peach")
        for nx in (2, w - 4):
            img.putpixel((nx, y0), rgba("ink"))
    return img


def callout(x0, y0, r0, x1, y1, r1, color="gold"):
    """A magnifier callout in its own canvas: a small ring at (x0, y0) radius r0 and two dotted lines to the
    top and bottom of a big lens centred at (x1, y1) radius r1. Returns (image, left, top) in world pixels."""
    L, T = min(x0 - r0, x1 - r1) - 2, min(y0 - r0, y1 - r1) - 2
    Rt, B = max(x0 + r0, x1 + r1) + 2, max(y0 + r0, y1 + r1) + 2
    img = blank(Rt - L, B - T)
    def P(x, y, c):
        if 0 <= x - L < img.width and 0 <= y - T < img.height:
            img.putpixel((x - L, y - T), rgba(c))
    import math
    for rr, c in ((r0 + 1, "ink"), (r0, "yellow"), (r0 - 1, "ink")):
        for a in range(0, 360, 2):
            P(round(x0 + rr * math.cos(math.radians(a))), round(y0 + rr * math.sin(math.radians(a))), c)
    for (ya, yb) in ((y0 - r0, y1 - r1 + 3), (y0 + r0, y1 + r1 - 3)):
        n = max(abs(x1 - x0), abs(yb - ya))
        for i in range(0, n + 1):
            if (i // 2) % 2:
                continue
            P(round(x0 + (x1 - x0) * i / n), round(ya + (yb - ya) * i / n), color)
    return img, L, T
