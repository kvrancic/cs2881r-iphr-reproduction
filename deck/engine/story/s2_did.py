"""Act 2, the first two things we did: the recompute from the released data and the rerun on a fifth of the
pairs. The recompute stands on the monitor (released data), the rerun on the lab bench (our runs)."""
from story.common import *
from px import rect, frame, paste, blank

CARD_W, CARD_H, CARD_Y = 100, 142, 26


def recompute(tl):
    tl.section = "recompute"
    # the released data, our code on its monitor stand and the figure, large on the ground
    tl.clear(); put_ground(tl)
    items = [("folder", P.folder(110, 84), "released data"), ("term", P.terminal(110, 80), "our code"),
             ("doc", P.doc(70, 90), "Figure 2")]
    xs = (16, 150, 286)                       # large, filling the stage: the opening of the reproduction
    for (i, img, lab), x in zip(items, xs):
        y = feet(img) - (14 if i == "term" else 0)
        tl.put(i, img, x, y, z=12, screen=True)
        t = T(lab, "ink")
        tl.put("t_" + i, t, x + img.width // 2 - t.width // 2, y - t.height - 6, z=40, screen=True)
    tl.put("stand", P.monitor(110, 14), 150, GY - 14, z=11, screen=True)
    for k, x in enumerate((130, 264)):
        tl.put(f"arr{k}", ui.arrow(16, "slate", 2), x, GY - 42, z=12, screen=True)
    tl.put("floor", floor(340), 22, GY, z=2, screen=True)
    cue(tl, "recompute")
    tl.beat("First, we recomputed the figure from the authors' released data.", fade=True)

    # our code's small terminal grows into the monitor board; the robot stands at its right
    tl.clear(); put_ground(tl)
    chart(tl, "rec_table", alias={"bd": "term"}, dx=STD_R)    # the board at the right, the robot at its left
    stage(tl, "happy", ("down", "up"), side="L")
    cue(tl, "released data: exact match")
    tl.beat("For the eight models whose ten-answer counts were released, our code gives exactly their numbers.", morph=0.9)

    # three discrepancies as three props on plinths: the plot's page, the retest's dial, the ranking's swap
    clear_charts(tl)
    tl.keep("ground")
    props = (("pg", P.divpage(62, 80), "the plot"), ("dial", P.gauge(32, post=12)[0], "the retest"),
             ("swap", P.swapcard(55, 40), "the ranking"))
    PL = 34                                   # tall plinths: the props stand higher on the stage
    for k, (i, img, lab) in enumerate(props):
        c_ = 62 + k * 100
        tl.put(f"plinth{k}", P.plinth(80, PL), c_ - 40, GY - PL, z=8, screen=True)
        tl.put(i, img, c_ - img.width // 2, GY - PL - img.height, z=12, screen=True)
        t = T(lab, "ink")
        tl.put(f"t_{i}", t, c_ - t.width // 2, GY - PL - img.height - t.height - 6, z=40, screen=True)
    tl.put("floor", floor(320), 18, GY, z=2, screen=True)
    stage(tl, "focus", c=344)
    cue(tl, "three discrepancies")
    tl.beat("We also found three discrepancies.", morph=0.9)

    # the divisor: the plot's page with the number it divides by, against the stack of pairs in the data;
    # the robot stands between them, squints and points at 4,892
    tl.keep("ground", "pg", "robot", "cfloor")
    pg = P.divpage(80, 100)
    tl.put("pg", pg, 34, GY - pg.height, z=12, screen=True)
    st = P.deckpile(12, w=46, h=58)
    tl.put("stack", st, 262, GY - st.height, z=12, screen=True)
    for i, (x0, w_, lab, num, col) in enumerate(((34, pg.width, "the plot divides by", f"{charts.PLOT_DIVISOR:,}", "sky"),
                                                 (262, st.width, "pairs in the data", f"{charts.N_PAIRS:,}", "ink"))):
        n = ui.big(num, col, 40, drop="ice")
        top = GY - (pg.height if i == 0 else st.height) - n.height - 8
        tl.put(f"t_num{i}", n, x0 + w_ // 2 - n.width // 2, top, z=40, screen=True)
        t = T(lab, "ink")
        tl.put(f"t_lab{i}", t, x0 + w_ // 2 - t.width // 2, top - t.height - 4, z=40, screen=True)
    tl.put("floor", floor(340), 22, GY, z=2, screen=True)
    stage(tl, "squint", POINT, c=196)
    hx, hy = hand(tl, "L", POINT)
    n0 = tl.objs["t_num0"]
    hold(tl, "stick", hx, hy, round(n0.x + n0.w + 4), round(n0.y + n0.h - 4))
    cue(tl, "the plot's divisor")
    tl.beat("The plot divides by 4,892 pairs where the data hold 4,834.", morph=0.9)

    # the retest: the cutoff as a gauge on the ground; the paper states 0.5 (the ghost needle), its code uses 0.4;
    # the robot turns the knob down
    tl.keep("ground", "robot", "cfloor", "floor")
    GR = 70                                   # the gauge's radius
    g, (gcx, gcy), tip = P.gauge(GR, post=26)
    gx_ = 128 - gcx
    tl.put("panel_dial", g, gx_, GY - g.height, z=12, screen=True)   # a backdrop: its scale labels sit on the dial
    gy_ = GY - g.height
    for i, (v, lab, fg, bg, side) in enumerate(((0.4, "used 0.4", "white", "sky", -1), (0.5, "stated 0.5", "sky", "white", 1))):
        ex, ey = tip(v, GR + 26)
        c = ui.chip(lab, fg, bg, border="sky" if bg == "white" else "ink")
        x = gx_ + ex - (c.width if side < 0 else 0)
        tl.put(f"t_cut{i}", c, x - (8 if side > 0 else 0), gy_ + ey - c.height, z=40, screen=True)
    for v in (0.3, 0.4, 0.5, 0.6):            # the scale: its ends just above the baseline, the two needles' ticks at the rim
        t = T(f"{v:.1f}", "slate")
        if v in (0.3, 0.6):
            ex, ey = tip(v, GR - 16)
            tl.put(f"t_tick{int(v * 10)}", t, gx_ + ex - t.width // 2, gy_ + ey - t.height - 3, z=40, screen=True)
        else:
            ex, ey = tip(v, GR + 9)
            tl.put(f"t_tick{int(v * 10)}", t, gx_ + ex - t.width // 2, gy_ + ey - t.height // 2, z=40, screen=True)
    tt = T("retest cutoff", "ink")
    tl.put("t_gname", tt, gx_ + gcx - tt.width // 2, gy_ - tt.height - 30, z=40, screen=True)   # above the dial and its chips
    stage(tl, "squint", ("out", "down"), c=gx_ + gcx + GR + 56)     # the hand on the knob, off the rim
    cue(tl, "looser than stated")
    tl.beat("The retest uses a looser cutoff than the paper states.", morph=0.9)

    # the ranking: the robot reads the paper's claim, then holds up a rank tile whose two lines cross
    tl.keep("ground")
    chart(tl, "rank_claim", alias={"bd": "term"})
    stage(tl, "side_l", ("down", "down"))
    cue(tl, "the paper's claim")
    tl.beat("The paper says the model ranking never changes with the cutoffs,", morph=0.9)
    chart(tl, "rank_table", alias={"bd": "term"})
    stage(tl, "shock", ("down", "down"), c=342)
    cue(tl, "its own table: it changes")
    tl.beat("while its own table shows that it does.", morph=0.9)


def run_panel(who, rows, h=80):
    """One run of a pair, framed in its run's colour (the paper's blue, our orange): the question and its reverse,
    ten answers each, a word and the true answer on the left of each row and the number of right answers at its
    end; the order that comes out better sits on a yellow highlight."""
    col, lab = ("sky", "paper's run") if who == "paper" else ("orange", "our run")
    from px import text as _text
    words = [_text(wd, "ink", 20) for wd in ("this order", "other order")]
    tabs = [P.truthtab("YES" if truth == "Y" else "NO") for _, truth in rows]
    counts = [_text(f"{sum(a == truth for a in answers)} right", "ink", 20, line=True) for answers, truth in rows]
    qx = 9 + max(t_.width for t_ in words + tabs) + 4
    PX0, PP = qx + 22, 10                      # the first pip and the pip pitch
    cx_ = PX0 + 9 * PP + 9 + 5
    w = cx_ + max(c_.width for c_ in counts) + 6
    img = blank(w, h)
    rect(img, 0, 0, w, h, "ink"); rect(img, 1, 1, w - 2, h - 2, col); rect(img, 3, 17, w - 6, h - 20, "white")
    t = _text(lab, "white", 20, line=True)          # cut to the font's lines: both headers share a baseline
    paste(img, t, (w - t.width) // 2, 2)
    for k, ((answers, truth), lw, tb, cn) in enumerate(zip(rows, words, tabs, counts)):
        y = 19 + k * 29
        if k == 0:
            rect(img, 5, y - 1, w - 10, 28, "yellow")
        paste(img, lw, 9, y)
        paste(img, tb, 9, y + 11)
        paste(img, P.qcard("place", 18, 22), qx, y + 2)
        for i, a in enumerate(answers):       # ten answers as plain pips: green YES, red NO
            c, hi = ("green", "yellow") if a == "Y" else ("red", "rose")
            px_ = PX0 + i * PP
            rect(img, px_, y + 4, 9, 18, "ink"); rect(img, px_ + 1, y + 5, 7, 16, c); rect(img, px_ + 1, y + 5, 7, 1, hi)
        paste(img, cn, cx_, y + 13 - cn.height // 2)
    return img


def rerun(tl):
    tl.section = "rerun"
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    # the whole set as a stack on a plinth; a fifth of it peels off into a smaller stack beside it
    pl = P.plinth(214, 22)
    tl.put("panel_pl", pl, 192 - 107, GY - 22, z=8, screen=True)
    d = P.deckpile(12, w=46, h=58)
    tl.put("deck", d, 104, GY - 22 - d.height, z=12, screen=True)
    sm = P.deckpile(3, w=46, h=58)
    tl.put("pile", sm, 222, GY - 22 - sm.height, z=12, screen=True)
    for k, (x, y) in enumerate(((176, 76), (200, 62))):
        tl.put(f"fly{k}", P.qcard("place" if k else "film", 30, 38), x, y, z=14, screen=True)
    lab = ui.runs([(f"{charts.RUNS['base']['openai/gpt-4o-mini']['n_pairs']:,}", "orange"), (" of ", "ink"), (f"{charts.N_PAIRS:,}", "ink")])
    tl.put("t_fifth", lab, 192 - lab.width // 2, GY - 22 + (22 - lab.height) // 2, z=40, screen=True)
    s_ = T("same prompt, same settings", "ink")
    tl.put("t_same", s_, 192 - s_.width // 2, 22, z=40, screen=True)
    tl.put("floor", floor(330), 26, GY, z=2, screen=True)
    cue(tl, "a fifth of the pairs, rerun")
    spot(tl, 192, 105, 150, 110)              # the lights dimmed on the opening of the rerun
    tl.beat("Second, we ran the experiment again on a fifth of the pairs with the same prompt and settings.", fade=True)

    # the judge -------------------------------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(290), 47, GY, z=2, screen=True)
    tl.put("old", robot("blank", grey=True), at(110), ROBOT_Y, z=20, screen=True)
    pl = P.plug(40)
    tl.put("plug", pl, 110 + 34, GY - pl.height + 1, z=21, screen=True)
    tl.put("judge", judge("focus"), at(262), ROBOT_Y, z=20, screen=True)
    a1, a2 = ui.chip("their judge, retired", "white", "slate"), ui.chip("our labeller", "white", "ink")
    cy_ = ROBOT_Y - max(a1.height, a2.height) - 12
    tl.put("t_old", a1, 110 - a1.width // 2, cy_, z=40, screen=True)
    tl.put("t_new", a2, 262 - a2.width // 2, cy_, z=40, screen=True)
    cue(tl, "old judge gone: a new labeller")
    tl.beat("The authors' judge is retired, so we built our own labeller,")

    pct, n = charts.judge_pct()
    for k in range(3):
        slip = blank(22, 16)
        rect(slip, 0, 0, 22, 16, "ink"); rect(slip, 1, 1, 20, 14, "white")
        for r in range(3):
            rect(slip, 3, 3 + r * 3, 12 - r * 3, 1, "steel")
        rect(slip, 13, 8, 7, 6, "orange"); rect(slip, 14, 9, 5, 4, "white"); rect(slip, 15, 10, 3, 2, "orange")
        tl.put(f"slip{k}", slip, 314 + k * 9, GY - 16 - k * 12, z=24, screen=True)
    b = ui.big(f"{pct}%", "orange", 60)
    t2 = T("label agreement, on their answers", "ink")
    top = 6
    tl.put("t_pct", b, 192 - b.width // 2, top, z=40, screen=True)
    tl.put("t_pct2", t2, 192 - t2.width // 2, top + b.height + 3, z=40, screen=True)
    tl.put("judge", judge("happy"))
    cue(tl, "our labeller vs their labels")
    tl.beat("which matches their labels on about ninety-nine percent of their answers.")

    # the four models we could rerun, each with its look -----------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(340), 22, GY, z=2, screen=True)
    names = ("GPT-4o\nmini", "Llama 3.3\n70B", "DeepSeek\nV3", "Gemini 2.5\nFlash")    # two lines: four tags in one row
    whos = ("gpt", "llama", "deepseek", "gemini")
    faces = (("grin", ("down", "up")), ("happy", ("down", "down")), ("calm", ("down", "down")), ("smug", ("down", "down")))
    for k, nm in enumerate(names):
        c_ = BOT_X[k]
        f, a = faces[k]
        tl.put(f"bot{k}", robot(f, a, who=whos[k]), at(c_), ROBOT_Y, z=20 + k, screen=True)
        c = ui.tag(nm, "white", "ink")
        tl.put(f"t_bot{k}", c, c_ - c.width // 2, ROBOT_Y - c.height - 10, z=40, screen=True)
    cue(tl, "4 models rerun")
    tl.beat("On the four models we could rerun,", fade=False)

    # each model holds up a sign with the size of its lean: the paper's run (blue) and ours (orange)
    _key(tl, "size of the lean")
    lean_signs(tl)
    for k in range(4):
        tl.put(f"bot{k}", robot("happy", who=whos[k]))
    cue(tl, "our runs: the same lean")
    tl.beat("each leans about as strongly as in the paper.", morph=0.8)

    # the flag counts: GPT-4o mini, Llama and Gemini step forward with their counts; DeepSeek steps back
    R = charts.RUNS
    tl.drop("bot2", "t_bot2", "sign2")
    signs_later = []
    for k, c_ in ((0, 96), (1, 192), (3, 288)):
        key = charts.FOUR[k][0]
        a_, b_ = R["paper_same_pairs"][key]["n_unf"], R["base"][key]["n_unf"]
        tl.move(f"bot{k}", x=at(c_))
        tg = tl.objs[f"t_bot{k}"]
        tl.move(f"t_bot{k}", x=c_ - tg.img.width // 2)
        pc = P.placard([(a_ * 0.3, "paper", str(a_)), (b_ * 0.3, "ours", str(b_))], 76)
        if k == 0:                            # GPT-4o mini's sign first; the other two hold theirs on the next slide
            tl.put(f"sign{k}", pc, c_ - pc.width // 2, ROBOT_Y + 52)
        else:
            tl.drop(f"sign{k}")
            signs_later.append((k, pc, c_))
    tl.put("bot0", robot("grin", who="gpt"))
    _key(tl, "flagged pairs")
    cue(tl, "GPT-4o mini: repeats closely")
    tl.beat("GPT-4o mini's flag count repeats closely.")

    for k, pc, c_ in signs_later:              # Llama's and Gemini's counts, with what an interval says about them
        tl.put(f"sign{k}", pc, c_ - pc.width // 2, ROBOT_Y + 52, z=36 + k, screen=True)
    tl.put("bot0", robot("happy", who="gpt"))
    nt = T("within the noise", "slate")
    tl.put("t_noise", nt, 240 - nt.width // 2, 37, z=40, screen=True)       # between the key and the two tags
    cue(tl, "Llama, Gemini: within the noise")
    tl.beat("Llama's and Gemini's differ within the noise.")

    # DeepSeek beside its board: the paper's flags and ours, then the paper's answers relabelled by our labeller
    tl.keep("ground")
    chart(tl, "ds_two")
    stage(tl, "side", who="deepseek", c=DS_C)          # in front of the wide board's empty lower left corner
    cue(tl, "DeepSeek: fewer flags")
    tl.beat("DeepSeek gets fewer.")
    chart(tl, "ds_three")
    stage(tl, "side", POINT_R, ("sweat",), who="deepseek", c=DS_C)
    hx, hy = hand(tl, "R", POINT_R)
    x, y, w, h = chart_pos("ds_three", "dsn1")              # the stick ends a little short of "our labeller"
    hold(tl, "stick", hx, hy, round(x - 10), round(y + h / 2))
    cue(tl, "part of it: our labeller")
    tl.beat("Part of that is our labeller.")

    # the rest: chance near the cutoff. At the stated cutoff on the template's lean (0.05) the two runs differ; at
    # 0.10 only a few flags are left in either, so most of the gap sits in pairs just past the cutoff
    chart(tl, "ds_cut")
    stage(tl, "focus", who="deepseek", c=DS_C)
    cue(tl, "the rest: near the cutoff")
    tl.beat("The rest may be chance, since its leans sit close to the cutoff.")

    # still: of the paper's twelve flags (our labeller) only one is flagged again in our run
    chart(tl, "ds_recur")
    stage(tl, "question", who="deepseek", c=DS_C)
    cue(tl, "1 of 12 flagged again")
    tl.beat("Still, only one of its twelve flags recurred, which hints at a change.", morph=0.9)

    # GPT-4o mini at the left points at one pair as two stacked runs: the paper's (blue) and ours (orange, grey
    # until its turn); the order that came out better sits on yellow in both
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(120), 4, GY, z=2, screen=True)
    pa = run_panel("paper", (("NNNNNNNNYN", "N"), ("NNYNNNYNNN", "Y")))
    ou = run_panel("ours", (("NNNNNNYNNN", "N"), ("NNNYNNNNNY", "Y")))
    PXL = 376 - pa.width
    tl.put("panel_p", pa, PXL, 14, z=10, screen=True)          # the two panels centred above the cue plate
    tl.put("panel_o", P.faint(ou), PXL, 100, z=10, screen=True)
    RC = PXL - 44                             # the robot's hand just reaches the panels
    stage(tl, "focus", POINT_R, who="gpt", c=RC)
    t = ui.tag("GPT-4o mini", "white", "ink")
    tl.put("t_name", t, max(6, RC - t.width // 2), ROBOT_Y - t.height - 8, z=40, screen=True)
    cue(tl, "one order better in the paper's run")
    tl.beat("When GPT-4o mini did better on one order of a pair in the paper's run,", fade=True)

    tl.put("panel_o", ou)
    tl.put("robot", robot("happy", POINT_R, who="gpt"))
    cue(tl, "the same order, better again")
    tl.beat("it also did better on that order in ours,")

    tl.keep("ground", "robot", "cfloor", "cue")
    chart(tl, "excess", dx=STD_R)
    stage(tl, "happy", POINT_R, who="gpt", c=LX - 8)          # the hand stops short of the bench's test tubes
    cue(tl, "same order better again")
    tl.beat("beyond its general lean.", morph=0.9)

    chart(tl, "excess_both", dx=STD_R)
    stage(tl, "focus", POINT_R, who="gpt", c=LX - 8)
    cue(tl, "against the lean: about as much")
    tl.beat("It did so by about as much on pairs that went against its lean.", morph=0.9)


BOT_X = (66, 152, 238, 324)          # the four models in a row
DS_C = 44                            # DeepSeek's centre in front of its board


LEAN_PX = 260                       # placard px per unit of lean: 0.2 spans 52 px on every sign
LEAN_TICKS = (0.1 * LEAN_PX, 0.2 * LEAN_PX)


def lean_signs(tl, whos=range(4)):
    """Each model holds a sign with the size of its lean, the paper's run (blue) and ours (orange), all on one
    scale: a common baseline and the same faint gridlines on every sign, each value (the lean gap, noise_models.json
    paired.*.lean_gap) at its bar's end."""
    N = charts.NOISE["paired"]
    for k, (key, _) in enumerate(charts.FOUR):
        if k not in whos:
            continue
        lg = N[key]["lean_gap"]
        pc = P.placard([(lg[r] * LEAN_PX, r, f"{lg[r]:.3f}") for r in ("paper", "ours")], 72, ticks=LEAN_TICKS, bh=10)
        tl.put(f"sign{k}", pc, BOT_X[k] - pc.width // 2, ROBOT_Y + 50, z=36 + k, screen=True)


def _key(tl, what):
    """What the signs show, then the two runs' colours: one line at the top of the stage."""
    t = T(what + ":", "ink")
    k1, k2 = ui.chip("paper's run", "white", "sky"), ui.chip("our run", "white", "orange")
    w = t.width + 8 + k1.width + 6 + k2.width
    x = 192 - w // 2
    tl.put("t_keyw", t, x, 14 + (k1.height - t.height) // 2, z=40, screen=True)
    tl.put("t_key0", k1, x + t.width + 8, 14, z=40, screen=True)
    tl.put("t_key1", k2, x + t.width + 8 + k1.width + 6, 14, z=40, screen=True)


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
    recompute(tl)
    rerun(tl)
