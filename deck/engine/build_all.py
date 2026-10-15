"""python3 build_all.py [pptx] [sheets] [qa] [frames]   regenerate the deck from the storyboard code.

pptx    deck/IPHR_Reproduction.pptx
sheets  contact sheets of every slide, composed exactly as placed, in deck/review/
qa      LibreOffice render of the .pptx into deck/review/qa/ (PDF, one PNG per slide, sheets)
frames  every slide as a 4x PNG in deck/build/frames/"""
import sys, os, time
from build_story import story
import reg, checks

DECK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(DECK, "IPHR_Reproduction.pptx")
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
    fails = 0
    ok, msg = checks.notes_match(tl.beats)
    fails += not ok
    print(("OK   " if ok else "FAIL ") + msg)
    for ok_, txt in checks.claims():
        fails += not ok_
        print(("OK   " if ok_ else "FAIL ") + "claim " + txt)
    issues = checks.check_layout(tl.beats)
    fails += bool(issues)
    print(("OK   " if not issues else "FAIL ") + f"layout: {len(issues)} text collisions or off-screen labels")
    for x in issues:
        print("  " + x)
    with open(os.path.join(BUILD, "morph.txt"), "w") as f:
        f.write("\n".join(checks.morph_report(tl.beats)) + "\n")
    if "pptx" in what:
        from build_pptx import build
        p, n = build(tl.beats, OUT)
        print(f"pptx: {n} slides, {os.path.getsize(p) / 1e6:.1f} MB -> {p}")
        errs, summary = checks.validate_pptx(p, tl.beats)
        fails += bool(errs)
        print(("OK   " if not errs else "FAIL ") + "round trip: " + summary)
        for e in errs:
            print("  " + e)
    if "sheets" in what:
        from render import contact
        per = 12
        for f in os.listdir(REVIEW):
            if f.startswith("slides-") and f.endswith(".png"):
                os.remove(os.path.join(REVIEW, f))
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
        print(f"qa: {len(pngs)} slide PNGs; sheets:", qa.sheets(pngs, os.path.join(qd, "sheet")))
    print(f"{'all checks passed' if not fails else f'{fails} check(s) failed'}; done in {time.time() - t0:.0f}s")
