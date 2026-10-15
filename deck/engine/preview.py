"""python3 preview.py out.png  -- builds a contact sheet of whatever sheet() returns."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from px import canvas, paste, text


def sheet(items, bg="night", cols=6, cell=(76, 76), k=4, out="sheet.png", label=True):
    rows = (len(items) + cols - 1) // cols
    img = Image.new("RGBA", (cols * cell[0], rows * (cell[1] + (10 if label else 0))), (38, 43, 68, 255))
    from pal import rgba
    img = Image.new("RGBA", img.size, rgba(bg))
    for i, (name, spr) in enumerate(items):
        cx = (i % cols) * cell[0]; cy = (i // cols) * (cell[1] + (10 if label else 0))
        paste(img, spr, cx + (cell[0] - spr.width) // 2, cy + (cell[1] - spr.height) // 2)
        if label:
            t = text(name, "steel", 10)
            paste(img, t, cx + 2, cy + cell[1])
    img.resize((img.width * k, img.height * k), Image.NEAREST).save(out)
    return out
