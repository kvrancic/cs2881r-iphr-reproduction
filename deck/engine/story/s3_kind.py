"""Act 3, Figure 2 split by kind of question: the ranking nearly reverses, and each kind has its own lean."""
from story.common import *


def split(tl):
    tl.section = "split by kind"
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    d = P.doc(56, 70)
    tl.put("doc", d, 20, 46, z=12, screen=True)
    t = T("Figure 2", "ink")
    tl.put("t_doc", t, 20 + d.width // 2 - t.width // 2, 46 + d.height + 4, z=40, screen=True)
    for k, y in enumerate((64, 126)):
        tl.put(f"arr{k}", ui.arrow(30, "slate", 2), 90, y, z=12, screen=True)
    g = P.kindicon("geography", 38)
    tl.put("kgeo", g, 134, 50, z=12, screen=True)
    tl.put("t_kgeo", T("geography", "ink"), 134 + g.width + 8, 62, z=40, screen=True)
    x = 134
    for name in ("dates", "sizes", "ages"):
        ic = P.kindicon(name, 32)
        tl.put(f"k{name}", ic, x, 146 - ic.height, z=12, screen=True)
        x += ic.width + 10
    tl.put("t_koth", T("dates, sizes, ages", "ink"), 134, 152, z=40, screen=True)
    tl.put("floor", floor(270), 6, GY, z=2, screen=True)
    stage(tl, "dots")
    cue(tl, "by kind")
    tl.beat("Third, we split Figure 2 by kind of question.", fade=True)

    tl.keep("ground", "robot", "cfloor")
    chart(tl, "kind_all")
    stage(tl, "shock")
    cue(tl, "ranking flips by kind")
    tl.beat("The top and bottom of the ranking swap.")
    chart(tl, "kind_gpt")
    stage(tl, "focus", POINT)
    tl.drop("cue")
    tl.beat("GPT-4o mini is flagged on a fifth of the geography pairs and on one percent of the rest.")
    chart(tl, "kind_rev")
    stage(tl, "side", POINT)
    cue(tl, "QwQ, Llama: the reverse")
    tl.beat("QwQ and Llama are the other way round.")


def leans(tl):
    """Two scales, each loaded with its kind of question in its pans, standing on plinths that carry the counts:
    geography tilts to NO, dates, sizes and ages tilt to YES (flagged pairs in the paper's data, 8 models)."""
    tl.section = "leans"
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    t = charts.CHECKS["lean_by_kind_total"]
    tl.put("floor", floor(372), 6, GY, z=2, screen=True)
    PH = 22
    for k, (c_, sc) in enumerate(((104, scale(-1, s=1.25, load=("geography", None))),
                                  (272, scale(0, grey=True, s=1.25, load=(None, "others"))))):
        pw = sc.width + 8
        tl.put(f"panel_{k}", P.plinth(pw, PH), c_ - pw // 2, GY - PH, z=7, screen=True)
        tl.put("scale2" if k == 0 else "scale", sc, c_ - sc.width // 2, GY - PH - sc.height, z=8, screen=True)
    a = ui.runs([(f"{t['geography_NO']:,} NO", "wine"), ("   ", "ink"), (f"{t['geography_YES']} YES", "leaf")])
    tl.put("t_lno", a, 104 - a.width // 2, GY - PH + (PH - a.height) // 2 - 1, z=40, screen=True)
    cue(tl, "geography: leans NO")
    tl.beat("On geography the models lean towards no.", fade=True)

    sc = scale(1, s=1.25, load=(None, "others"))
    tl.put("scale", sc, 272 - sc.width // 2, GY - PH - sc.height)
    b = ui.runs([(f"{t['other_YES']} YES", "leaf"), ("   ", "ink"), (f"{t['other_NO']} NO", "wine")])
    tl.put("t_lyes", b, 272 - b.width // 2, GY - PH + (PH - b.height) // 2 - 1, z=40, screen=True)
    cue(tl, "dates, sizes, ages: lean YES")
    tl.beat("On dates, sizes and ages they lean towards yes.")


def act3(tl):
    split(tl)
    leans(tl)
