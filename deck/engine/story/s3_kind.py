"""Act 3, Figure 2 split by kind of question: the ranking nearly reverses, and each kind has its own lean."""
from story.common import *


def split(tl):
    tl.section = "split by kind"
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    d = P.doc(62, 80)
    tl.put("doc", d, 50, 50, z=12, screen=True)
    t = T("Figure 2", "ink")
    tl.put("t_doc", t, 50 + d.width // 2 - t.width // 2, 50 + d.height + 4, z=40, screen=True)
    for k, y in enumerate((68, 130)):
        tl.put(f"arr{k}", ui.arrow(30, "slate", 2), 128, y, z=12, screen=True)
    g = P.kindicon("geography", 38)
    tl.put("kgeo", g, 176, 54, z=12, screen=True)
    tl.put("t_kgeo", T("geography", "ink"), 176 + g.width + 8, 66, z=40, screen=True)
    x = 176
    for name in ("dates", "sizes", "ages"):
        ic = P.kindicon(name, 32)
        tl.put(f"k{name}", ic, x, 150 - ic.height, z=12, screen=True)
        x += ic.width + 10
    tl.put("t_koth", T("dates, sizes, ages", "ink"), 176, 156, z=40, screen=True)
    tl.put("floor", floor(300), 30, GY, z=2, screen=True)
    cue(tl, "by kind")
    tl.beat("Third, we split Figure 2 by kind of question.", fade=True)

    # the page of Figure 2 opens into the split board; it fills the stage, no robot
    tl.keep("ground")
    chart(tl, "kind_all", alias={"bd": "doc"})
    cue(tl, "rankings run opposite")
    tl.beat("The two rankings tend to run opposite.", morph=0.9)
    chart(tl, "kind_gpt", alias={"bd": "doc"})
    cue(tl, "GPT-4o mini: geography")
    tl.beat("GPT-4o mini is flagged on a fifth of the geography pairs and on one percent of the rest.")
    chart(tl, "kind_rev", alias={"bd": "doc"})
    cue(tl, "QwQ, Llama: the reverse")
    tl.beat("QwQ and Llama are the other way round.")


def leans(tl):
    """Two scales, each loaded with its kind of question in its pans, standing on plinths that carry the counts:
    geography tilts to NO, dates, sizes and ages tilt to YES (flagged pairs in the paper's data, 8 models). The
    robot stands between them and points at the one being named."""
    tl.section = "leans"
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    t = charts.CHECKS["lean_by_kind_total"]
    tl.put("floor", floor(372), 6, GY, z=2, screen=True)
    PH = 22
    S = 1.1
    w0 = scale(-1, s=S, load=("geography", None)).width + 8
    w1 = scale(0, s=S, load=(None, "others")).width + 8
    C0, C1 = 10 + w0 // 2, 374 - w1 // 2
    for k, (c_, sc) in enumerate(((C0, scale(-1, s=S, load=("geography", None))),
                                  (C1, scale(0, grey=True, s=S, load=(None, "others"))))):
        pw = sc.width + 8
        if k == 0:                      # the right plinth appears with its counts, on the next slide
            tl.put(f"panel_{k}", P.plinth(pw, PH), c_ - pw // 2, GY - PH, z=7, screen=True)
        tl.put("scale2" if k == 0 else "scale", sc, c_ - sc.width // 2, GY - (PH if k == 0 else 0) - sc.height, z=8, screen=True)
    a = ui.runs([(f"{t['geography_NO']:,} NO", "wine"), ("  ", "ink"), (f"{t['geography_YES']} YES", "leaf")])
    tl.put("t_lno", a, C0 - a.width // 2, GY - PH + (PH - a.height) // 2 - 1, z=40, screen=True)
    place(tl, "robot", robot("side_l", POINT), (C0 + w0 // 2 + C1 - w1 // 2) // 2, z=20)
    u = T("flagged pairs, by the template's lean", "ink")    # what the counts count
    tl.put("t_unit", u, 192 - u.width // 2, 26, z=40, screen=True)
    cue(tl, "geography: leans NO")
    tl.beat("On geography the models lean towards no.")

    sc = scale(1, s=S, load=(None, "others"))
    tl.put("panel_1", P.plinth(w1, PH), C1 - w1 // 2, GY - PH, z=7, screen=True)
    tl.put("scale", sc, C1 - sc.width // 2, GY - PH - sc.height)
    b = ui.runs([(f"{t['other_NO']} NO", "wine"), ("  ", "ink"), (f"{t['other_YES']} YES", "leaf")])
    tl.put("t_lyes", b, C1 - b.width // 2, GY - PH + (PH - b.height) // 2 - 1, z=40, screen=True)
    place(tl, "robot", robot("side", POINT_R), (C0 + w0 // 2 + C1 - w1 // 2) // 2 - 8, z=20)   # the arm clear of the right box
    cue(tl, "dates, sizes, ages: lean YES")
    tl.beat("On dates, sizes and ages they lean towards yes.")


def act3(tl):
    split(tl)
    leans(tl)
