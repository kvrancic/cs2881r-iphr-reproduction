"""Checks run on every build: the speaker notes are exactly the transcript, no text collides with anything,
every slide has a transition, and Morph names line up."""
import os
import numpy as np
from px import W, H

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "talk", "transcript.md")


def spoken():
    """The words said, from talk/transcript.md: every paragraph that is not a heading."""
    out = []
    for para in open(SCRIPT).read().split("\n\n"):
        p = para.strip()
        if not p or p.startswith("#"):
            continue
        out.append(p)
    return " ".join(" ".join(out).split())


def notes_match(beats):
    said = " ".join(" ".join(b.say for b in beats if b.say).split())
    want = spoken()
    empty = [i + 1 for i, b in enumerate(beats) if not b.say.strip()]
    if said == want and not empty:
        return True, f"speaker notes match talk/transcript.md word for word ({len(want.split())} words, {len(beats)} slides)"
    if empty:
        return False, f"slides without spoken words: {empty}"
    i = next((k for k, (a, b) in enumerate(zip(said, want)) if a != b), min(len(said), len(want)))
    return False, f"notes differ from the transcript at char {i}:\n  deck:       ...{said[max(0, i - 60):i + 60]}\n  transcript: ...{want[max(0, i - 60):i + 60]}"


def morph_report(beats):
    """For each transition: ids that carry over, appear and disappear."""
    lines = []
    for i in range(1, len(beats)):
        a, b = beats[i - 1], beats[i]
        A, B = set(a.objs) - {"ground"}, set(b.objs) - {"ground"}
        kind = "fade" if b.fade else "morph"
        lines.append(f"{i:2d}->{i + 1:2d} {kind:5s} keep {len(A & B):2d}  in {sorted(B - A)}  out {sorted(A - B)}")
    return lines


# ------------------------------------------------------------------------------------------------ layout
def _mask(o, cam):
    """The object's opaque pixels on the 384x216 screen, at 2x for sub-pixel chart objects."""
    from render import placement
    from PIL import Image
    k = 2
    x, y, w, h = placement(o, cam)
    a = o.img.split()[3].resize((max(1, round(w * k)), max(1, round(h * k))), Image.NEAREST)
    m = np.zeros((H * k, W * k), bool)
    X, Y = round(x * k), round(y * k)
    arr = np.asarray(a) > 0
    x0, y0 = max(0, X), max(0, Y)
    x1, y1 = min(W * k, X + arr.shape[1]), min(H * k, Y + arr.shape[0])
    if x1 > x0 and y1 > y0:
        m[y0:y1, x0:x1] = arr[y0 - Y:y1 - Y, x0 - X:x1 - X]
    off = arr.sum() - m.sum()
    return m, off


def check_layout(beats):
    """Text (the cue, every t_* label and every chart text element) must not touch any other object, except the
    backdrops it is meant to sit on, and must stay on screen. Returns a list of issues."""
    from story.common import BACKDROPS, BACKDROP_PREFIX
    import charts
    textish = lambda i: i == "cue" or i.startswith("t_") or (i.startswith("ch_") and i[3:] in charts.TEXTS)
    backdrop = lambda i: i in BACKDROPS or i.startswith(BACKDROP_PREFIX) or (i.startswith("ch_") and i[3:] in charts.PANELS)
    issues = [f"chart element runs past the 960x540 grid: {x}" for x in charts.OVERFLOW]
    for n, b in enumerate(beats, 1):
        objs = {i: o for i, o in b.objs.items() if o.alpha > 0.05}
        masks = {i: _mask(o, b.cam) for i, o in objs.items() if i != "ground"}
        for i, (m, off) in masks.items():
            if not textish(i):
                continue
            if off > 0:
                issues.append(f"slide {n}: {i} runs off screen ({off} px)")
            for j, (m2, _) in masks.items():
                if j == i or backdrop(j) or (textish(j) and j < i):
                    continue
                ov = int((m & m2).sum())
                if ov > 2:
                    issues.append(f"slide {n}: {i} touches {j} ({ov} px at 2x)")
    return issues


# ------------------------------------------------------------------------------------------------ the .pptx
def validate_pptx(path, beats):
    """Round trip through python-pptx: slide count, 16:9, names, a transition on every slide, notes."""
    from pptx import Presentation
    from lxml import etree
    from build_pptx import notes_text
    prs = Presentation(path)
    errs = []
    if len(prs.slides) != len(beats):
        errs.append(f"{len(prs.slides)} slides, expected {len(beats)}")
    if abs(prs.slide_width / prs.slide_height - 16 / 9) > 1e-3:
        errs.append("not 16:9")
    n_morph = n_fade = 0
    for i, (s, b) in enumerate(zip(prs.slides, beats), 1):
        names = [sh.name for sh in s.shapes]
        if any(not n.startswith("!!") for n in names):
            errs.append(f"slide {i}: unnamed picture")
        if len(set(names)) != len(names):
            errs.append(f"slide {i}: duplicate names")
        if any(sh.shape_type != 13 for sh in s.shapes):
            errs.append(f"slide {i}: an object that is not a picture")
        xml = etree.tostring(s._element).decode()
        if "p159:morph" in xml:
            n_morph += 1
        elif "<p:fade" in xml:
            n_fade += 1
        else:
            errs.append(f"slide {i}: no transition")
        notes = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
        nxt = next((x.say for x in beats[i:] if x.say), "(end)")
        if notes != notes_text(b, nxt):
            errs.append(f"slide {i}: notes are not the spoken words + NEXT")
    return errs, f"{len(prs.slides)} slides, {n_morph} Morph, {n_fade} fade, every slide has a transition"


# ------------------------------------------------------------------------------------------------ claims
def claims():
    """The numbers the speaker says, checked against the result files the charts read. Returns [(ok, text)]."""
    import charts as ch
    c = ch.CHECKS
    out = []
    rec = [k for k, v in c["figure2"].items() if v["source"] == "recomputed"]
    same = sum(c["figure2"][k]["paper_count"] == c["figure2"][k]["our_count"] for k in rec)
    out.append((len(rec) == 8 and same == 8, f"'eight models ... exactly their numbers': {same} of {len(rec)} recomputed counts match"))
    g = c["figure2"]["openai/gpt-4o-mini"]["paper_pct"]
    out.append((12.5 <= g < 14.5, f"'GPT-4o mini ... about thirteen percent': {g}%"))
    t = c["retest_mean_of_models"]["thr05"]
    out.append((0.55 <= t < 0.65, f"'about sixty percent of flags survive': {t:.1%}"))
    p, n = ch.judge_pct()
    out.append((p == 99, f"'ninety-nine percent of their answers': {p}% over {n} answers"))
    a, na = ch.inside("paper")
    b, nb = ch.inside("ours")
    out.append((a * 2 == na, f"'predicts their number for half of the paper's models': {a} of {na} inside the predicted range"))
    out.append((b == nb == 8, f"'and for all eight of our runs': {b} of {nb} inside the predicted range"))
    cw = ch.COORD
    out.append((cw["base"]["flags"] == 131 and cw["coordwording"]["flags"] == 24,
                f"'fell from 131 to 24': {cw['base']['flags']} -> {cw['coordwording']['flags']}"))
    return out
