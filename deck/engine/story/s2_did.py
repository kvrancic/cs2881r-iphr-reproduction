"""Act 2, what we did: four cards, then the first two: the recompute from the released data and the rerun on a
fifth of the pairs."""
from story.common import *
from px import rect

CARD_W, CARD_H, CARD_Y = 88, 142, 28
CARD_X = tuple(10 + k * (CARD_W + 4) for k in range(4))    # four cards centred in the frame


def card_icons():
    """The four things, each a large picture: the paper's figure, two chats, the kinds of question, the two
    variations (the aqua fact card and the compass)."""
    two = blank(72, 64)
    paste(two, P.chat(54, 40, ""), 0, 0); paste(two, P.chat(54, 40, ""), 18, 24)
    kinds = blank(72, 92)
    g = P.kindicon("geography", 50)
    paste(kinds, g, (72 - g.width) // 2, 0)
    paste(kinds, P.calendar(32), 0, 58); paste(kinds, P.ruler(36, 14), 36, 76)
    var = blank(72, 94)
    fc = blank(70, 40)
    rect(fc, 0, 0, 70, 40, "deep"); rect(fc, 1, 1, 68, 38, "cyan"); rect(fc, 1, 1, 68, 1, "white")
    rect(fc, 6, 10, 46, 3, "deep"); rect(fc, 6, 23, 34, 3, "deep")
    paste(var, fc, 1, 0); cp = P.compass(24); paste(var, cp, (72 - cp.width) // 2, fc.height + 2)
    return [P.doc(60, 78), two, kinds, var]


CARD_LABELS = ("check\nFigure 2", "rerun", "split by\nkind", "2\nvariations")


def four(tl):
    tl.section = "four things"
    tl.clear()
    put_ground(tl)
    for k, x in enumerate(CARD_X):
        tl.put(f"card_{k}", P.cardback(CARD_W, CARD_H), x, CARD_Y, z=10, screen=True)
    cue(tl, "four things")
    tl.beat("We did four things.", fade=True)
    says = ("We checked the figure,", "ran it again,", "split it by kind of question", "and tried two variations.")
    for k, (img, lab, say) in enumerate(zip(card_icons(), CARD_LABELS, says)):
        x = CARD_X[k]
        tl.put(f"card_{k}", P.card(CARD_W, CARD_H))
        tl.put(f"sl_ic{k}", img, x + (CARD_W - img.width) // 2, CARD_Y + 8 + (100 - img.height) // 2, z=12, screen=True)
        t = T(lab, "ink", align="center")
        tl.put(f"t_sl{k}", t, x + (CARD_W - t.width) // 2, CARD_Y + CARD_H - t.height - 10, z=40, screen=True)
        if k == 0:
            tl.drop("cue")
        tl.beat(say)


def recompute(tl):
    tl.section = "recompute"
    # the released data, our code and the figure, large on the ground; the 'check Figure 2' card's page opens
    # into the figure (same id), the other cards fall away
    tl.keep("ground", "sl_ic0")
    items = [("folder", P.folder(100, 78), "released data"), ("term", P.terminal(100, 78), "our code"),
             ("sl_ic0", P.doc(64, 82), "Figure 2")]
    xs = (30, 166, 302)
    for (i, img, lab), x in zip(items, xs):
        tl.put(i, img, x, feet(img), z=12, screen=True)
        t = T(lab, "ink")
        tl.put("t_" + i, t, x + img.width // 2 - t.width // 2, feet(img) - t.height - 6, z=40, screen=True)
    for k, x in enumerate((136, 272)):
        tl.put(f"arr{k}", ui.arrow(24, "slate", 2), x, GY - 42, z=12, screen=True)
    tl.put("floor", floor(372), 6, GY, z=2, screen=True)
    cue(tl, "recompute")
    tl.beat("First, we recomputed the figure from the authors' released data.", morph=0.8)

    tl.clear(); put_ground(tl)
    chart(tl, "rec_table")
    stage(tl, "happy")
    cue(tl, "exact match")
    tl.beat("For the eight models whose ten-answer counts were released, our code gives exactly their numbers.", fade=True)
    chart(tl, "rec_two")
    stage(tl, "side")
    tl.drop("cue")
    tl.beat("We also found three small discrepancies.")
    chart(tl, "divisor")
    stage(tl, "focus", POINT)
    tl.beat("The plot divides by 4,892 pairs where the data hold 4,834.")
    chart(tl, "retest_cut")
    stage(tl, "focus")
    tl.beat("The retest uses a looser cutoff than the paper states.")
    chart(tl, "rank_claim")
    stage(tl, "neutral")
    tl.beat("The paper says the model ranking never changes with the cutoffs,")
    chart(tl, "rank_table")
    stage(tl, "shock", POINT)
    tl.beat("while its own table shows that it does.")


def rerun(tl):
    tl.section = "rerun"
    clear_charts(tl)
    tl.keep("ground", "robot", "cfloor")
    # the whole set as a tall deck; a fifth of the cards fly out into our pile
    d = P.deckpile(9)
    tl.put("deck", d, 22, GY - d.height, z=12, screen=True)
    nb = T(f"{charts.N_PAIRS:,}", "ink", 40)
    tl.put("t_all", nb, 22 + (d.width - nb.width) // 2, GY - d.height - nb.height - 6, z=40, screen=True)
    path = [(84, 104), (112, 76), (144, 62), (176, 66), (204, 84)]
    for k, (x, y) in enumerate(path):
        tl.put(f"fly{k}", P.qcard("place" if k % 3 else "film", 22, 28), x, y, z=14, screen=True)
    pile = blank(48, 56)
    for k in range(4):
        paste(pile, P.qcard("place" if k % 2 else "book", 30, 38), 4 + k * 3 - 4, 18 - k * 6)
    tl.put("pile", pile, 214, GY - pile.height, z=12, screen=True)
    n = ui.big("1,014 pairs", "orange", 40, drop="ice")
    tl.put("t_fifth", n, 176, 22, z=40, screen=True)
    tl.put("t_same", T("same setup", "ink"), 178, 22 + n.height + 2, z=40, screen=True)
    tl.put("floor", floor(290), 6, GY, z=2, screen=True)
    stage(tl, "happy")
    cue(tl, "a fifth, again")
    tl.beat("Second, we ran the experiment again on a fifth of the pairs with the same prompt and settings.", fade=True)

    # the judge -------------------------------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(300), 42, GY, z=2)
    tl.put("old", robot("blank", grey=True), at(100), ROBOT_Y, z=20)
    pl = P.plug(40)
    tl.put("plug", pl, 100 + 34, GY - pl.height + 1, z=21)
    tl.put("judge", judge("focus"), at(262), ROBOT_Y, z=20)
    a1, a2 = ui.chip("their judge, retired", "white", "slate"), ui.chip("our labeller", "white", "ink")
    tl.put("t_old", a1, 100 - a1.width // 2, ROBOT_Y - a1.height - 6, z=40)
    tl.put("t_new", a2, 262 - a2.width // 2, ROBOT_Y - a2.height - 12, z=40)
    cue(tl, "old judge gone: a new labeller")
    tl.beat("The authors' judge is retired, so we built our own labeller,", fade=True)

    pct, n = charts.judge_pct()
    for k in range(3):
        slip = blank(22, 16)
        rect(slip, 0, 0, 22, 16, "ink"); rect(slip, 1, 1, 20, 14, "white")
        for r in range(3):
            rect(slip, 3, 3 + r * 3, 12 - r * 3, 1, "steel")
        rect(slip, 13, 8, 7, 6, "orange"); rect(slip, 14, 9, 5, 4, "white"); rect(slip, 15, 10, 3, 2, "orange")
        tl.put(f"slip{k}", slip, 318 + k * 9, GY - 16 - k * 12, z=24)
    b = ui.big(f"{pct}%", "orange", 60)
    tl.put("t_pct", b, 160 - b.width // 2, 6, z=40, screen=True)
    t2 = T("label agreement,\non their answers", "ink", align="center")
    tl.put("t_pct2", t2, 160 - t2.width // 2, 6 + b.height + 3, z=40, screen=True)
    tl.put("judge", judge("happy"))
    cue(tl, "our labeller vs their labels")
    tl.beat("which matches their labels on about ninety-nine percent of their answers.")

    # the three original models still online and the newer release of Gemini 2.5 Flash, each with one trait ------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(356), 14, GY, z=2)
    names = ("GPT-4o\nmini", "Llama 3.3\n70B", "DeepSeek\nV3", "Gemini 2.5\nFlash")    # two lines: four tags in one row
    looks = (dict(face="grin", arms=("down", "up"), ant="pink"), dict(face="happy", ant="gold", hat="beret"),
             dict(face="calm", ant="cyan"), dict(face="smug", ant="rose", hat="bow"))
    for k, nm in enumerate(names):
        c_ = 48 + k * 92
        lk = dict(looks[k])
        tl.put(f"bot{k}", robot(lk.pop("face"), lk.pop("arms", ("down", "down")), **lk), at(c_), ROBOT_Y, z=20 + k)
        c = ui.tag(nm, "white", "ink")
        tl.put(f"t_bot{k}", c, c_ - c.width // 2, ROBOT_Y - c.height - 6, z=40)
    nw = P.ribbon("newer release")
    tag3 = tl.objs["t_bot3"]
    tl.put("t_newer", nw, tag3.x + (tag3.img.width - nw.width) // 2, tag3.y - nw.height - 2, z=41)
    cue(tl, "still online: 3 originals + 1 newer")
    tl.beat("On the three original models still online and the newer release of Gemini 2.5 Flash,", fade=True)

    # the charts of the rerun: the name tags become the chart's row labels -----------------------------------
    tl.keep("ground", "t_bot0", "t_bot1", "t_bot2", "t_bot3")
    tags = {f"rn{k}": f"t_bot{k}" for k in range(4)}
    chart(tl, "lean_size", alias=tags)
    stage(tl, "focus")
    tl.beat("each model leans about as strongly as in the paper.", morph=0.8)
    chart(tl, "flag_count", alias={k: v for k, v in tags.items() if k in ("rn0", "rn1")})
    stage(tl, "happy")
    tl.beat("GPT-4o mini and Llama get about the same number of flags.")
    chart(tl, "ds_two")
    stage(tl, "side")
    tl.beat("DeepSeek gets fewer.")
    chart(tl, "ds_three")
    stage(tl, "dots", POINT)
    tl.beat("Part of that is our labeller.")

    # the rest: maybe a different model behind the same name: the paper's run in blue, ours in orange --------------
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(300), 42, GY, z=2)
    tl.put("ds_old", robot("calm", ant="sky", tint="sky"), at(120), ROBOT_Y, z=20)
    tl.put("ds_new", robot("question", ant="orange", tint="orange"), at(264), ROBOT_Y, z=20)
    nm = ui.chip("DeepSeek V3", "white", "ink")
    tl.put("t_dsname", nm, 192 - nm.width // 2, 20, z=40)
    for k, x in enumerate((120, 264)):
        t = ui.chip(("paper's run", "our run")[k], "white", ("sky", "orange")[k])
        tl.put(f"t_dsrun{k}", t, x - t.width // 2, ROBOT_Y - t.height - 8, z=40)
    from px import line as _line
    br = blank(150, 14)
    _line(br, 0, 13, 6, 2, "ink"); _line(br, 6, 2, 143, 2, "ink"); _line(br, 143, 2, 149, 13, "ink")
    _line(br, 75, 0, 75, 2, "ink")
    tl.put("bracket", br, 117, 44, z=30)
    cue(tl, "same name, maybe another model")
    tl.beat("The rest may be a different model behind the same name.", fade=True)

    # pair-level asymmetry beyond the lean: clear for GPT-4o mini, small for the others -----------------------------
    tl.clear(); put_ground(tl)
    chart(tl, "excess_gpt")
    stage(tl, "happy", POINT)
    tl.beat("For GPT-4o mini, when it did better on one order of a pair in the paper's run, it tends to do better on the same order in ours, beyond its general lean.", fade=True)
    chart(tl, "excess_all")
    stage(tl, "neutral")
    tl.beat("For the other models this effect is small.")


def _mini_wall(lit=(2, 7, 12), cols=5, rows=3):
    """The pairs of the wall, small, with some of them lit (two thirds are places, as in the data)."""
    from sprites.props import qcard, faint
    img = blank(cols * 36 - 2, rows * 24 - 2)
    kinds = ("place", "place", "film", "place", "person", "place", "book", "place", "place")
    for p in range(cols * rows):
        r, c = divmod(p, cols)
        k = kinds[p % len(kinds)]
        for s in (0, 1):
            cd = qcard(k, 15, 20, lit=False)
            if p not in lit:
                cd = faint(cd)
            paste(img, cd, c * 36 + s * 16, r * 24)
    return img


def act2(tl):
    four(tl)
    recompute(tl)
    rerun(tl)
