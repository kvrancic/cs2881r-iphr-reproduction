"""Render a .pptx through LibreOffice into per-slide PNGs and contact sheets for review."""
import os, sys, subprocess, glob
from PIL import Image

def pptx_to_pngs(pptx, outdir, dpi=40):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run([sys.executable, os.path.expanduser("~/.claude/skills/pptx/scripts/office/soffice.py"), "--headless",
                    "--convert-to", "pdf", "--outdir", outdir, pptx], check=True, capture_output=True)
    pdf = os.path.join(outdir, os.path.basename(pptx).replace(".pptx", ".pdf"))
    for f in glob.glob(os.path.join(outdir, "p-*.png")):
        os.remove(f)
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf, os.path.join(outdir, "p")], check=True)
    return sorted(glob.glob(os.path.join(outdir, "p-*.png")))


def sheets(pngs, outprefix, cols=6, per=36):
    out = []
    for k in range(0, len(pngs), per):
        ims = [Image.open(p) for p in pngs[k:k + per]]
        w, h = ims[0].size
        rows = (len(ims) + cols - 1) // cols
        s = Image.new("RGB", (cols * (w + 4), rows * (h + 4)), (255, 255, 255))
        for i, im in enumerate(ims):
            s.paste(im, ((i % cols) * (w + 4), (i // cols) * (h + 4)))
        path = f"{outprefix}-{k // per + 1:02d}.png"
        s.save(path); out.append(path)
    return out

if __name__ == "__main__":
    pngs = pptx_to_pngs(sys.argv[1], sys.argv[2])
    print(len(pngs), sheets(pngs, os.path.join(sys.argv[2], "sheet")))
