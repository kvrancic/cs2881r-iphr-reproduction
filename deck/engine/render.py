"""Compose a beat into a preview frame exactly as the deck places it (same maths as build_pptx)."""
from PIL import Image
from px import W, H
from pal import rgba


def placement(o, cam):
    """(x, y, w, h) of an object on the 384x216 slide, in native pixels."""
    z = 1.0 if o.screen or len(cam) < 3 else cam[2]
    x = o.x if o.screen else (o.x - cam[0]) * z
    y = o.y if o.screen else (o.y - cam[1]) * z
    return x, y, o.w * z, o.h * z


def compose(beat, k=5):
    img = Image.new("RGBA", (W * k, H * k), rgba(beat.bg))
    for o in sorted(beat.objs.values(), key=lambda o: o.z):
        if o.alpha <= 0.001:
            continue
        x, y, w, h = placement(o, beat.cam)
        src = o.img.resize((max(1, round(w * k)), max(1, round(h * k))), Image.NEAREST)
        if o.alpha < 0.999:
            src = src.copy()
            src.putalpha(src.split()[3].point(lambda v: int(v * o.alpha)))
        _paste_clip(img, src, round(x * k), round(y * k))
    return img


def _paste_clip(dst, src, x, y):
    sx0, sy0 = max(0, -x), max(0, -y)
    if sx0 >= src.width or sy0 >= src.height or x >= dst.width or y >= dst.height:
        return
    crop = src.crop((sx0, sy0, min(src.width, dst.width - x + sx0), min(src.height, dst.height - y + sy0)))
    dst.alpha_composite(crop, (max(0, x), max(0, y)))


def contact(beats, path, cols=4, k=1, first=1):
    """Contact sheet of beats at k x native, numbered like the deck's slides."""
    from px import text
    tw, th = W * k, H * k
    pad = 16
    rows = (len(beats) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (tw + 6) + 6, rows * (th + pad + 6) + 6), (24, 20, 37, 255))
    for i, b in enumerate(beats):
        f = compose(b, k=max(1, k))
        x, y = 6 + (i % cols) * (tw + 6), 6 + (i // cols) * (th + pad + 6)
        sheet.alpha_composite(f, (x, y))
        t = text(f"{first + i}  {b.say[:60]}", "ice", 20)
        sheet.alpha_composite(t.crop((0, 0, min(t.width, tw), t.height)), (x, y + th + 3))
    sheet.save(path)
    return path
