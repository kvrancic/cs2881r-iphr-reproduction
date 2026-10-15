"""The whole deck as one Timeline, act by act. ../storyboard.md describes the same slides in words."""
import numpy as np
from timeline import Timeline, Obj
from story.s1_claim import act1
from story.s2_did import act2
from story.s3_kind import act3
from story.s4_ext import act4
from story.s5_close import act5
from sprites import sets


def story():
    tl = Timeline()
    tl.scenery("wall_hall", sets.lecture())
    act1(tl)      # title, the Figure 1 example, the pairs, Figure 2
    tl.scenery("wall_lab", sets.lab())
    act2(tl)      # four things; 1 the recompute, 2 the rerun
    tl.scenery("wall_map", sets.mapwall())
    act3(tl)      # 3 Figure 2 split by kind of question
    tl.scenery("wall_survey", sets.survey())
    act4(tl)      # 4 the two variations: fact cards, then the wording of geography questions
    tl.scenery("wall_stage", sets.stage())
    act5(tl)      # what Figure 2 measures, thank you
    for b in tl.beats:
        plate_labels(b)
    return tl


SOLID = ("card_", "panel_", "win_", "ch_bd", "map", "doc", "term", "q", "fact", "lad_q", "sign", "slot_")


def _free(img):
    """True for plain text (mostly transparent around the glyphs), False for chips, tags and plates."""
    key = id(img)
    if key not in _FREE:
        a = np.asarray(img.split()[3]) > 0
        _FREE[key] = a.mean() < 0.9            # chips, tags and plates are opaque almost everywhere
    return _FREE[key]


_FREE = {}


def _opaque_at(o, x, y):
    """True if the picture o is opaque at screen point (x, y)."""
    px_, py_ = int((x - o.x) / o.scale), int((y - o.y) / o.scale)
    if not (0 <= px_ < o.img.width and 0 <= py_ < o.img.height):
        return False
    return o.img.getpixel((px_, py_))[3] > 0


def plate_labels(beat):
    """Every free label (t_*: plain text, not already inside a light panel, card, chat or board) gets a light plate
    with a 1 px ink outline behind it, so it reads on the darker sets. The plate keeps the label's id (panel_pl_*), so
    Morph moves it with the label."""
    from px import blank
    from sprites.props import _rbox
    objs = beat.objs
    solids = [o for i, o in objs.items() if i.startswith(SOLID) and o.alpha > 0.05]
    for i, o in list(objs.items()):
        if not i.startswith("t_") or o.alpha <= 0.05 or not _free(o.img):
            continue
        x0, y0, x1, y1 = o.x, o.y, o.x + o.w, o.y + o.h
        if any(s.x <= x0 and s.y <= y0 and s.x + s.w >= x1 and s.y + s.h >= y1 and s.z < o.z and _opaque_at(s, (x0 + x1) / 2, (y0 + y1) / 2)
               for s in solids):
            continue
        pw, ph = int(round(o.w)) + 8, int(round(o.h)) + 6
        img = blank(pw, ph)
        _rbox(img, 0, 0, pw, ph, "white", "ink")
        objs["panel_pl_" + i[2:]] = Obj("panel_pl_" + i[2:], img, round(x0) - 4, round(y0) - 3, z=o.z - 0.5,
                                        alpha=o.alpha, screen=o.screen)

