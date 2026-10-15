"""Act 2, what we did: three slots, the recompute from the released data, the rerun on a fifth of the pairs."""
from story.common import *

SLOT_X, SLOT_Y = (24, 140, 256), 50


def slots(tl, lit=None):
    for k, x in enumerate(SLOT_X, 1):
        tl.put(f"slot{k}", P.slot(k, lit=lit == k, dim=lit is not None and lit != k), x, SLOT_Y, z=10)


def three(tl):
    tl.section = "three things"
    tl.clear()
    put_ground(tl)
    slots(tl)
    cue(tl, "we did three things")
    tl.beat("We did three things.", fade=True)


def recompute(tl):
    tl.section = "recompute"
    # slot 1 opens into the recompute: released data -> our code -> the figure
    tl.drop("slot2", "slot3")
    tl.put("slot1", P.slot(1, 336, 150, lit=True), 24, 34, z=10)
    items = [("folder", P.folder(), "released data"), ("term", P.terminal(), "our code"), ("doc", P.doc(), "Figure 2")]
    xs = (62, 165, 276)
    for (i, img, lab), x in zip(items, xs):
        tl.put(i, img, x, 128 - img.height, z=12)
        t = T(lab, "ink")
        tl.put("t_" + i, t, x + img.width // 2 - t.width // 2, 134, z=40)
    for k, x in enumerate((126, 230)):
        tl.put(f"arr{k}", ui.arrow(28, "slate", 2), x, 104, z=12)
    cue(tl, "1. recompute Figure 2 ourselves")
    tl.beat("First, we recomputed the figure from the authors' released data with our own code.")

    tl.clear(); put_ground(tl)
    chart(tl, "rec_table")
    tl.beat("For the eight models whose raw counts were released we get exactly their numbers.", fade=True)
    chart(tl, "rec_two")
    tl.beat("We also found two small discrepancies.")
    clear_charts(tl)
    chart(tl, "divisor")
    tl.beat("The plotting script divides by the wrong number of pairs.", fade=True)
    clear_charts(tl)
    chart(tl, "retest_cut")
    tl.beat("The paper's retest also uses a looser cutoff than it states.", fade=True)
    chart(tl, "retest_keep")
    tl.beat("At the stated cutoff about sixty percent of flags survive, where the paper reports seventy-six.")


def _mini_wall(lit=(2, 7, 12)):
    """The 15 pairs of the wall, small, with a fifth of them lit."""
    img = blank(178, 70)
    from sprites.props import qcard, faint
    kinds = ("book", "film", "person", "place")
    for p in range(15):
        r, c = divmod(p, 5)
        k = kinds[(p * 3 + r) % 4]
        for s in (0, 1):
            cd = qcard(k, 15, 20, lit=False)
            if p not in lit:
                cd = faint(cd)
            paste(img, cd, c * 36 + s * 16, r * 24)
    return img


def rerun(tl):
    tl.section = "rerun"
    tl.clear(); put_ground(tl)
    tl.put("slot2", P.slot(2, 336, 150, lit=True), 24, 34, z=10)
    mw = _mini_wall()
    tl.put("minwall", mw, 44, 74, z=12)
    n = ui.big("1,014 pairs", "orange", 40, drop="ice")
    tl.put("t_fifth", n, 226, 76, z=40)
    tl.put("t_fifth2", T("a fifth of them", "ink"), 228, 104, z=40)
    tl.put("t_same", T("same prompt\nsame settings", "slate"), 228, 124, z=40)
    cue(tl, "2. run it again")
    tl.beat("Second, we ran the experiment again on a fifth of the pairs with the same prompt and settings.", fade=True)

    # the judge -------------------------------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(300), 42, GY, z=2)
    tl.put("old", robot("sleep", grey=True), at(110), ROBOT_Y, z=20)
    tl.put("sign", P.sign("retired"), 26, GY - 27, z=22)
    tl.put("judge", judge("focus"), at(270), ROBOT_Y, z=20)
    a1, a2 = ui.chip("their judge", "slate", "white"), ui.chip("our labeller", "ink", "white")
    tl.put("t_old", a1, 110 - a1.width // 2, GY + 4, z=40)
    tl.put("t_new", a2, 270 - a2.width // 2, GY + 4, z=40)
    cue(tl, "their judge is retired: we built our own")
    tl.beat("The authors' judge model is retired, so we built our own labeller,", fade=True)

    pct, n = charts.judge_pct()
    from px import rect
    for k in range(3):
        slip = blank(22, 16)
        rect(slip, 0, 0, 22, 16, "ink"); rect(slip, 1, 1, 20, 14, "white")
        for r in range(3):
            rect(slip, 3, 3 + r * 3, 12 - r * 3, 1, "steel")
        rect(slip, 13, 8, 7, 6, "green"); rect(slip, 14, 9, 5, 4, "white"); rect(slip, 15, 10, 3, 2, "green")
        tl.put(f"slip{k}", slip, 330 + k * 8, GY - 16 - k * 12, z=24)
    b = ui.big(f"{pct}%", "green", 60)
    tl.put("t_pct", b, 376 - b.width, 34, z=40, screen=True)
    t2 = T("same labels as theirs,\non their own answers", "ink", align="right")
    tl.put("t_pct2", t2, 376 - t2.width, 34 + b.height + 4, z=40, screen=True)
    tl.put("judge", judge("happy"))
    cue(tl, "our labeller agrees with theirs")
    tl.beat("which matches their labels on ninety-nine percent of their answers.")

    # the four original models -----------------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(356), 14, GY, z=2)
    names = ("GPT-4o\nmini", "Llama 3.3\n70B", "DeepSeek\nV3", "Gemini 2.5\nFlash")
    for k, nm in enumerate(names):
        c_ = 52 + k * 92
        tl.put(f"bot{k}", robot(("neutral", "happy", "focus", "smug")[k]), at(c_), ROBOT_Y, z=20 + k)
        c = ui.chip(nm, "white", "sky")
        tl.put(f"t_bot{k}", c, c_ - c.width // 2, ROBOT_Y - c.height - 2, z=40)
    cue(tl, "the four original models still online")
    tl.beat("On the four original models that are still online,", fade=True)

    tl.clear(); put_ground(tl)
    chart(tl, "lean_size")
    tl.beat("the size of each model's lean comes back almost exactly.", fade=True)
    clear_charts(tl)
    chart(tl, "flag_rate")
    tl.beat("The flag rate comes back for GPT-4o mini and Llama.", fade=True)
    clear_charts(tl)
    chart(tl, "deepseek")
    tl.beat("For DeepSeek it depends on where the cutoff falls.", fade=True)
    clear_charts(tl)
    chart(tl, "recur_flags")
    tl.beat("For GPT-4o mini and Llama, single flags repeat", fade=True)
    clear_charts(tl)
    chart(tl, "recur_bars")
    tl.beat("about as often as ten answers per question allow.", fade=True)


def act2(tl):
    three(tl)
    recompute(tl)
    rerun(tl)
