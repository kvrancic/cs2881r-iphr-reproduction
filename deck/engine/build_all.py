"""python3 build_all.py [pptx] [sheets] [qa]   regenerate the deck from the storyboard code.

pptx    deck/3B_Therapeutics.pptx
sheets  contact sheets of every slide, composed exactly as placed, in deck/review/
qa      LibreOffice render of the .pptx into deck/review/qa/ (PDF and sheets)"""
import sys, os, time, json
from build_story import story
import reg, checks

DECK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(DECK, "3B_Therapeutics.pptx")
BUILD = os.path.join(DECK, "build")
REVIEW = os.path.join(DECK, "review")

if __name__ == "__main__":
    what = set(sys.argv[1:]) or {"pptx", "sheets"}
    t0 = time.time()
    os.makedirs(BUILD, exist_ok=True); os.makedirs(REVIEW, exist_ok=True)
    tl = story()
    reg.dump(os.path.join(BUILD, "manifest.json"))
    print(f"story: {len(tl.beats)} slides, missing sprites: {len(reg.MISSING)} {sorted(reg.MISSING)}, errors: {len(reg.ERRORS)}")
    for k, v in list(reg.ERRORS.items())[:20]:
        print("  ERR", k, v[:200])
    ok, msg = checks.notes_match(tl.beats)
    print(("OK  " if ok else "FAIL ") + msg)
    with open(os.path.join(BUILD, "morph.txt"), "w") as f:
        f.write("\n".join(checks.morph_report(tl.beats)) + "\n")
    if "pptx" in what:
        from build_pptx import build
        p, n, rep = build(tl.beats, OUT)
        print(f"pptx: {n} slides, {os.path.getsize(p) / 1e6:.1f} MB -> {p}")
        for r in rep:
            print("  " + r)
        errs, summary = checks.validate_pptx(p, tl.beats)
        print(("OK  " if not errs else "FAIL ") + "round trip: " + summary)
        for e in errs:
            print("  " + e)
    if "sheets" in what:
        from render import contact
        per = 12
        for k in range(0, len(tl.beats), per):
            path = os.path.join(REVIEW, f"slides-{k // per + 1:02d}.png")
            contact(tl.beats[k:k + per], path, cols=3, k=2, first=k + 1)
            print("sheet:", path)
    if "frames" in what:
        from render import compose
        d = os.path.join(BUILD, "frames"); os.makedirs(d, exist_ok=True)
        for i, b in enumerate(tl.beats):
            compose(b, k=4).save(os.path.join(d, f"s{i + 1:02d}.png"))
        print("frames:", d)
    if "qa" in what:
        import qa
        qd = os.path.join(REVIEW, "qa")
        pngs = qa.pptx_to_pngs(OUT, qd)
        print("qa sheets:", qa.sheets(pngs, os.path.join(qd, "sheet")))
    print(f"done in {time.time() - t0:.0f}s")
