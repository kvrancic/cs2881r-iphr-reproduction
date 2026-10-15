"""Checks run on every build: the speaker notes are exactly the script, and Morph names line up."""
import os, re

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pitch-script.md")


def spoken():
    """The words Karlo says, from pitch-script.md: every paragraph that is not a heading, rule or video block."""
    out = []
    started = False
    for para in open(SCRIPT).read().split("\n\n"):
        p = para.strip()
        if not p or p.startswith("#") or p.startswith(">") or p == "---":
            continue
        if p.startswith("This is only what you say"):
            continue
        out.append(p)
    return " ".join(" ".join(out).split())


def notes_match(beats):
    said = " ".join(" ".join(b.say for b in beats if b.say).split())
    want = spoken()
    if said == want:
        return True, "speaker notes match pitch-script.md word for word"
    i = next((k for k, (a, b) in enumerate(zip(said, want)) if a != b), min(len(said), len(want)))
    return False, f"notes differ from the script at char {i}:\n  deck:   ...{said[max(0, i - 60):i + 60]}\n  script: ...{want[max(0, i - 60):i + 60]}"


def morph_report(beats):
    """For each Morph transition: ids that carry over, appear and disappear."""
    lines = []
    for i in range(1, len(beats)):
        a, b = beats[i - 1], beats[i]
        A, B = set(a.objs) - {"ground"}, set(b.objs) - {"ground"}
        kind = "cut" if (b.clip is not None and a.clip is not None) else "fade" if (b.fade or b.video or a.video) else "morph"
        lines.append(f"{i:2d}->{i + 1:2d} {kind:5s} keep {len(A & B):2d}  in {sorted(B - A)}  out {sorted(A - B)}")
    return lines


def validate_pptx(path, beats):
    """Round trip through python-pptx: slide count, 16:9, names, Morph and fade transitions, notes, videos."""
    from pptx import Presentation
    from lxml import etree
    import appendix
    prs = Presentation(path)
    errs = []
    apx = appendix.parse()
    if len(prs.slides) != len(beats) + len(apx):
        errs.append(f"{len(prs.slides)} slides, expected {len(beats)} + {len(apx)} appendix")
    for k, a in enumerate(apx):           # the appendix notes are APPENDIX.md's, verbatim (not the script)
        sl = prs.slides[len(beats) + k]
        got = sl.notes_slide.notes_text_frame.text if sl.has_notes_slide else ""
        if got != a["notes"]:
            errs.append(f"appendix {a['id']}: notes differ from APPENDIX.md")
        if "<p:fade" not in etree.tostring(sl._element).decode():
            errs.append(f"appendix {a['id']}: no fade")
        if any(sh.shape_type == 13 for sh in sl.shapes):
            errs.append(f"appendix {a['id']}: contains a picture")
    if abs(prs.slide_width / prs.slide_height - 16 / 9) > 1e-3:
        errs.append("not 16:9")
    n_morph = n_fade = n_vid = n_cut = n_clip = 0
    for i, (s, b) in enumerate(zip(prs.slides, beats), 1):
        prev = beats[i - 2] if i > 1 else None
        clip_cut = b.clip is not None and prev is not None and prev.clip is not None
        names = [sh.name for sh in s.shapes]
        pics = [n for n in names if not n.startswith("video_")]
        if any(not n.startswith("!!") for n in pics):
            errs.append(f"slide {i}: unnamed picture")
        if len(set(pics)) != len(pics):
            errs.append(f"slide {i}: duplicate names")
        xml = etree.tostring(s._element).decode()
        if clip_cut:
            if "<p:transition" in xml or "p159:morph" in xml:
                errs.append(f"slide {i}: a transition between two clips")
            n_cut += 1
        elif "p159:morph" in xml:
            n_morph += 1
        elif "<p:fade" in xml:
            n_fade += 1
        else:
            errs.append(f"slide {i}: no transition")
        if any(n.startswith("video_") for n in names):
            n_vid += 1
            if "playFrom" not in xml or 'nodeType="afterEffect"' not in xml:
                errs.append(f"slide {i}: video does not start automatically")
            if "clickEffect" in xml or "interactiveSeq" in xml:
                errs.append(f"slide {i}: a click on the video would trigger it")
            if b.clip is not None:
                n_clip += 1
                if "advTm" in xml:
                    errs.append(f"slide {i}: clip slide advances on its own")
            elif "advTm" not in xml:
                errs.append(f"slide {i}: intro does not advance on its own")
        notes = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
        if b.say and not notes.startswith(b.say):
            errs.append(f"slide {i}: notes do not start with the spoken words")
    return errs, (f"{len(prs.slides)} slides ({len(beats)} + {len(apx)} appendix), {n_morph} Morph, {n_fade} fade, {n_cut} instant cuts between clips, "
                  f"{n_vid} embedded videos of which {n_clip} narrated clips (autoplay, no auto-advance)")
