"""Act 4, the two variations: values in the prompt on the questions that are not about geography, then why
GPT-4o mini fails on geography and the wording ladder."""
from story.common import *
from px import rect, paste

WX, WY, WW = 22, 24, 150                 # the chat window of both variations
RBC = 326                                 # the big robot's centre, to the right
SC = 235                                  # the scale's centre, between the window and the robot (its YES pan clears it)
QF = "Was film A released\nbefore film B?"
QW = "Is lake B west\nof lake A?"


def two(tl):
    """The two variations as two halves, the fact card and the compass, their labels on one baseline, the robot
    standing between them."""
    tl.section = "variations"
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(300), 42, GY, z=2, screen=True)
    LBY = 118                                     # one baseline for both labels, above the robot's arms
    for k, (c_, img, lab) in enumerate(((84, P.factcard(["A: true value", "B: true value"], 128), "values in\nthe prompt"),
                                        (300, P.compass(38), "geography\nwording"))):
        tl.put(("fact", "compass")[k], img, c_ - img.width // 2, LBY - 12 - img.height, z=12, screen=True)
        t = T(lab, "ink", align="center")
        tl.put(f"t_v{k + 1}", t, c_ - t.width // 2, LBY, z=40, screen=True)
    place(tl, "robot", robot("happy", ("out", "out")), 192)
    cue(tl, "two variations")
    spot(tl, 192, 110, 185, 105)              # the lights dimmed on the opening of the variations
    tl.beat("Fourth, two variations.", fade=True)


def _name(tl, nm):
    """The model's name once, as a tag above the big robot."""
    t = ui.tag(nm, "white", "ink")
    tl.put("t_name", t, RBC - t.width // 2, ROBOT_Y - t.height - 10, z=40, screen=True)


def _scene(tl, bubble_text, card=None, face="neutral", acc=(), arms=("down", "down"), answer=None, who=None, clear=True):
    """The chat window (card above the question, an optional answer below), the big robot on the ground."""
    if clear:
        tl.clear(); put_ground(tl)
    tl.put("floor", floor(220), 160, GY, z=2, screen=True)
    y = WY + 20
    if card is not None:
        tl.put("fact", card, WX + 6, y, z=14, screen=True)
        y += card.height + 4
    b = P.bubble(bubble_text, WW - 12)
    tl.put("q", b, WX + 6, y, z=12, screen=True)
    y += b.height + 6
    if answer is not None:
        tl.put("ans", answer, WX + 8, y, z=12, screen=True)
        y += answer.height + 6
    else:
        tl.drop("ans")
    tl.put("win_q", P.chat(WW, y - WY, "chat"), WX, WY, z=10, screen=True)
    tl.put("robot", robot(face, arms, acc, who=who), at(RBC), ROBOT_Y, z=20, screen=True)
    return y


def _big_scale(tl, tilt=0, grey=False):
    sc = scale(tilt, grey=grey, s=1.25)
    tl.put("scale", sc, SC - sc.width // 2, feet(sc), z=6, screen=True)


def _numbers_trace():
    """A reasoning trace in grey strokes; on its second line the two numbers it writes, as grey blocks with an ink
    edge, compared the wrong way round (the later one written as the earlier)."""
    img = P.trace(WW - 16, 4, seed=7)
    rect(img, 0, 9, WW - 16, 10, "white")
    for x in (8, 58):
        rect(img, x - 1, 10, 28, 8, "ink"); rect(img, x, 11, 26, 6, "steel"); rect(img, x, 11, 26, 1, "ice")
    lt = T("<", "ink")
    paste(img, lt, 42, 14 - lt.height // 2)
    return img


NUMS_AT = (8, 10, 84, 18)        # where the two numbers sit in the trace: x0, y0, x1, y1 (the bracket spans x0..x1)


def _answer(named=False):
    """The wrong answer: the trace with its numbers (named=True: a bracket under the two numbers and the words
    "its numbers"), then YES and an ink cross."""
    yes = ui.plate("YES", "green", "white", 20, 2)
    tr = _numbers_trace()
    nm = T("its numbers", "ink") if named else None
    x0, _, x1, _ = NUMS_AT
    th = tr.height + (4 + nm.height + 2 if nm else 0)
    h = th + 4 + yes.height
    ans = blank(tr.width, h)
    paste(ans, tr, 0, 0)
    if nm:                                    # the bracket under the two numbers, the words centred under it
        by = tr.height + 1
        rect(ans, x0 - 1, by, x1 - x0 + 2, 1, "ink"); rect(ans, x0 - 1, by - 2, 1, 2, "ink"); rect(ans, x1, by - 2, 1, 2, "ink")
        paste(ans, nm, (x0 + x1) // 2 - nm.width // 2, by + 3)
    y = th + 4
    paste(ans, yes, 0, y); paste(ans, ui.cross("ink"), yes.width + 4, y + (yes.height - 9) // 2)
    return ans


def facts(tl):
    tl.section = "fact cards"
    card = P.factcard(["film A: release date", "film B: release date"], WW - 12)
    _scene(tl, QF, card, "focus", ("card",), ("down", "up"))
    _big_scale(tl, 0, grey=True)
    cue(tl, "both true values, above the question")
    tl.beat("In the first we printed both true values above each question.")

    # the four models of these runs (GPT-5.6 Luna takes Gemini's place), each holding up its flags outside
    # geography; then each holds the fact card and its count drops to 0
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(350), 17, GY, z=2, screen=True)
    a_, b_ = charts.nongeo_total()
    for k, (key, nm) in enumerate(FACT_NAMES):
        c_ = BOTS[k]
        place(tl, f"bot{k}", robot("focus", who=FACT_WHO[k]), c_, z=20 + k)
        tg = ui.tag(nm, "white", "ink")
        tl.put(f"t_bot{k}", tg, c_ - tg.width // 2, ROBOT_Y - tg.height - 8, z=40, screen=True)
        sg = P.flagsign(charts.RUNS["by_kind"][key]["other"]["base"], 48)
        tl.put(f"sign{k}", sg, c_ - sg.width // 2, ROBOT_Y + 52, z=36 + k, screen=True)
    _total(tl, [])                            # the total comes with the next sentence
    cue(tl, "our runs, outside geography")
    tl.beat("As expected, flags outside geography", morph=0.9)
    for k, (key, nm) in enumerate(FACT_NAMES):
        tl.put(f"bot{k}", robot("happy", ("down", "up"), ("card",), who=FACT_WHO[k]))
        sg = P.flagsign(charts.RUNS["by_kind"][key]["other"]["factcard"], 48, col="ink")
        tl.put(f"sign{k}", sg, BOTS[k] - sg.width // 2)
    _total(tl, [(str(a_), "orange"), (None, "arrow"), (str(b_), "ink")])
    cue(tl, "both values in the prompt: 0")
    tl.beat("went from fifty-seven to zero across four models.", morph=0.9)

    # each value asked alone: Llama mostly knows the order; it holds up the next lit tile ---------------------------
    tl.clear(); put_ground(tl)
    chart(tl, "recall")
    arms = ("up", "down")
    stage(tl, "happy", arms, who="llama")
    hx, hy = hand(tl, "L", arms)
    tile = blank(14, 14)
    rect(tile, 0, 0, 14, 14, "ink"); rect(tile, 1, 1, 12, 12, "orange"); rect(tile, 1, 1, 12, 2, "gold")
    tl.put("held", tile, hx - 7, hy - 20, z=34, screen=True)
    cue(tl, "Llama, each value asked alone")
    tl.beat("Asked for each value on its own, Llama ordered about seven in ten of its flagged pairs correctly,")
    chart(tl, "recall_other")
    stage(tl, "focus", who="llama")
    cue(tl, "its other pairs")
    tl.beat("against eight and a half in ten for its other pairs")
    chart(tl, "recall_guess")
    stage(tl, "side_l", POINT, who="llama")
    hx, hy = hand(tl, "L", POINT)
    x, y, w, h = chart_pos("recall_guess", "rcgl")
    hold(tl, "stick", hx, hy, round(x + w + 4), hy if y <= hy <= y + h else round(y + h / 2))   # level: one straight line
    cue(tl, "and by guessing")
    tl.beat("and five in ten by guessing.")

    # in its wrong answers the written numbers support the wrong answer -----------------------------------------
    clear_charts(tl)
    _scene(tl, QF, None, "focus", answer=_answer(named=True), who="llama")
    _name(tl, "Llama 3.3 70B")
    _big_scale(tl, 1)
    cue(tl, "wrong answer: its numbers back it")
    tl.beat("In most of its wrong answers, the numbers it writes support the wrong answer.", morph=0.9)


MAP_XY, MAP_WH = (12, 42), (160, 110)    # the lake map, over 40% of the width
LR = 228                                   # the robot's centre in the lake scene: beside the map
FACT_NAMES = (("openai/gpt-4o-mini", "GPT-4o\nmini"), ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3\n70B"),
              ("deepseek/deepseek-chat", "DeepSeek\nV3"), ("openai/gpt-5.6-luna", "GPT-5.6\nLuna"))
FACT_WHO = ("gpt", "llama", "deepseek", "luna")
BOTS = (62, 148, 236, 324)


def _total(tl, parts):
    """The total over the four models, at the top: a short label and the number(s) in large type."""
    t = T("flags outside geography", "ink")
    ims = [ui.arrow(22, "slate", 3) if s_ is None else ui.say(s_, c_, 40) for s_, c_ in parts]
    if not ims:                               # no total yet: the label alone, at the height it keeps later
        n = blank(1, ui.say("0", "ink", 40).height)
        tl.put("t_totl", t, 192 - t.width // 2, 10 + (n.height - t.height) // 2, z=40, screen=True)
        tl.drop("t_tot")
        s_ = T("the four models in this test", "slate")
        tl.put("t_four", s_, 192 - s_.width // 2, 10 + n.height + 2, z=40, screen=True)
        return
    n = blank(sum(i.width for i in ims) + 8 * (len(ims) - 1), max(i.height for i in ims))
    x_ = 0
    for i in ims:
        paste(n, i, x_, (n.height - i.height) // 2); x_ += i.width + 8
    w = t.width + 10 + n.width
    x = 192 - w // 2
    tl.put("t_totl", t, x, 10 + (n.height - t.height) // 2, z=40, screen=True)
    tl.put("t_tot", n, x + t.width + 10, 10, z=40, screen=True)
    s_ = T("the four models in this test", "slate")
    tl.put("t_four", s_, 192 - s_.width // 2, 10 + n.height + 2, z=40, screen=True)


LADDER = [("base", "paper's wording"), ("paraphrase", "reworded,\nsame vague"),
          ("coordwording", "a more western\nlongitude"), ("strict", "+ only\ndue west")]


def _hbar(L, h=20):
    """A flag-count bar lying on its side, our run's orange, lit on top and shaded at its end."""
    L = max(2, round(L))
    img = blank(L, h)
    rect(img, 0, 0, L, h, "ink"); rect(img, 0, 1, L - 1, h - 2, "orange")
    rect(img, 0, 1, L - 1, 2, "gold"); rect(img, L - 3, 3, 2, h - 4, "rust")
    return img


def _track(w, h):
    """A faint dotted outline of a bar lying on its side, for the room up to all pairs."""
    img = blank(w, h)
    for x in range(0, w, 3):
        rect(img, x, 0, 1, 1, "steel"); rect(img, x, h - 1, 1, 1, "steel")
    for y in range(0, h, 3):
        rect(img, w - 1, y, 1, 1, "steel")
    return img


def _point_b(tl):
    """GPT-4o mini, standing to the right of the lake map, points its stick at lake B."""
    from sprites.props import LAKE_B, MAP_W, MAP_H
    bx = MAP_XY[0] + round(LAKE_B[0] * MAP_WH[0] / MAP_W) + 14
    by = MAP_XY[1] + round(LAKE_B[1] * MAP_WH[1] / MAP_H) + 4
    hx, hy = hand(tl, "L", POINT)
    hold(tl, "stick", hx, hy, bx, by)


def wording(tl):
    tl.section = "geography"
    y = _scene(tl, QW, None, "focus", who="gpt")
    cp = P.compass(30)
    tl.put("compass", cp, WX + (WW - cp.width) // 2, y + 12, z=16, screen=True)
    sc = scale(-1)
    tl.put("scale", sc, SC - sc.width // 2, feet(sc), z=6, screen=True)
    _name(tl, "GPT-4o mini")
    cue(tl, "why it fails on geography")
    tl.beat("In the second we asked why GPT-4o mini fails on geography.", fade=True)

    # the paper's data by distance: GPT-4o mini, small, climbs onto its tallest bar
    tl.clear(); put_ground(tl)
    chart(tl, "dist", alias={"dib3": "map"})
    stage(tl, "side_l", POINT, who="gpt")
    hx, hy = hand(tl, "L", POINT)
    x, y, w, h = chart_pos("dist", "dib3")
    hold(tl, "stick", hx, hy, round(x + w + 3), round(y + h * 0.4))
    cue(tl, "far apart: more flags")
    tl.beat("Its flags are most common for places that are far apart,", morph=0.9)

    # far apart: the easiest to put in order; the farthest bar opens into the one map of the lakes, and GPT-4o mini
    # steps up beside it and points at lake B
    clear_charts(tl)
    tl.keep("ground", "map", "robot")
    q = P.bubble("Is lake B west of lake A?", 176, tail=None)
    tl.put("q", q, MAP_XY[0], 14, z=12, screen=True)
    tl.put("map", P.lakemap(None, *MAP_WH), *MAP_XY, z=8, screen=True, scale=1.0)
    stage(tl, "happy", POINT, who="gpt", c=LR)
    _point_b(tl)
    t = ui.tag("GPT-4o mini", "white", "ink")
    tl.put("t_name", t, LR - t.width // 2, ROBOT_Y - t.height - 10, z=40, screen=True)
    cue(tl, "far apart: should be easy")
    tl.beat("which should be the easiest to put in order.", morph=0.9)

    # its answer, in one bubble on its right that grows; the tail points at the robot's screen
    def say(s_):
        b_ = P.bubble(s_, max(T(l).width for l in s_.split("\n")) + 12, tail="lside")
        tl.put("say", b_, LR + 34, ROBOT_Y + 30 - b_.height // 2, z=22, screen=True)
    say("B is\nsouthwest\nof A.")
    tl.put("robot", robot("focus", POINT, who="gpt"))
    cue(tl, "its answer: southwest")
    tl.beat("A typical wrong answer says that a lake is southwest of another,")

    say("B is\nsouthwest\nof A, not\ndue west.\nSo: NO.")
    tl.put("map", P.lakemap("due", *MAP_WH))
    tl.put("robot", robot("smug", POINT, who="gpt"))
    cue(tl, "southwest does not count")
    tl.beat("so it is not directly west of it.")

    # the wording ladder: the same 684 pairs asked in four wordings, each a chat bubble with its flags as a bar on
    # one scale and the count at the bar's end; a faint dotted track of all 684 lies behind each row from the start,
    # "of 684" right of the top one; GPT-4o mini stands at the right, the whole robot inside the frame
    tl.clear(); put_ground(tl)
    G = charts.GEO["conditions"]
    N = G["base"]["pairs"]
    BX0, BWD = 138, 96                        # the bars start at x 138; all 684 pairs span 96 px
    LRC = 326                                 # GPT-4o mini's centre: 16 px from the right edge of the frame
    ys = (24, 62, 100, 138)
    ax = blank(2, ys[-1] + 24 - ys[0] + 8)
    rect(ax, 0, 0, 2, ax.height, "ice")      # light: the dusk sky behind it is dark
    tl.put("lad_ax", ax, BX0 - 3, ys[0] - 4, z=12, screen=True)
    for i, y_ in enumerate(ys):              # a faint dotted track behind each row: the room up to all pairs
        tl.put(f"slot_tr{i}", _track(BWD, 20), BX0, y_ + 1, z=11, screen=True)
    al = T(f"of {N}", "slate")
    tl.put("t_all", al, BX0 + BWD + 4, ys[0] + 11 - al.height // 2, z=40, screen=True)   # right of the top track
    stage(tl, "neutral", who="gpt", c=LRC)

    def rung(i, face, arms=("down", "down"), acc=()):
        c_, lab = LADDER[i]
        for j in range(i + 1):               # only the rung being spoken about is on yellow
            b_ = P.bubble(LADDER[j][1], 122, bg="yellow" if j == i and i >= 2 else "ice",
                          edge="gold" if j == i and i >= 2 else "steel", tail=None)
            tl.put(f"lad_q{j}", b_, 8, ys[j] + 10 - b_.height // 2 + 2, z=12, screen=True)
        v = G[c_]["flags"]
        L = v * BWD / N
        L = max(6, L)                         # a short bar still reads as a bar, apart from its count
        tl.put(f"slot_lb{i}", _hbar(L), BX0, ys[i] + 1, z=13, screen=True)
        t = ui.say(str(v), "orange", 40)      # every count at its bar's end, a clear gap after it
        tl.put(f"t_lv{i}", t, BX0 + round(L) + 9, ys[i] + 11 - t.height // 2, z=40, screen=True)
        stage(tl, face, arms, acc, who="gpt", c=LRC)

    rung(0, "neutral")
    cue(tl, "same 684 pairs, four wordings")
    tl.beat("With the paper's wording it has 131 flags.", fade=True)
    rung(1, "dots")
    cue(tl, "reworded: about the same")
    tl.beat("A paraphrase with the same vague direction gives 140.")
    rung(2, "happy", POINT)
    hx, hy = hand(tl, "L", POINT)
    o = tl.objs["t_lv2"]
    hold(tl, "stick", hx, hy, round(o.x + o.w + 4), round(o.y + o.h / 2))
    cue(tl, "more western longitude: 24")
    tl.beat("Asking for a more western longitude cuts them to 24.")
    rung(3, "shock", ("up", "up"), ("sweat",))
    cue(tl, "+ only due west: almost all")
    tl.beat("A sentence saying that only directly west counts raises them to 667 of 684,")

    # under the strict reading NO is right in both orders
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    tl.put("map1", P.lakemap("due", 170, 110), 22, 40, z=8, screen=True)
    t = ui.chip("due west only", "white", "ink")
    tl.put("t_read1", t, 22 + 85 - t.width // 2, 40 - t.height - 5, z=40, screen=True)   # above the map, clear of the floor
    for k, qq in enumerate(("Is B west of A?", "Is A west of B?")):
        b = P.bubble(qq, 128, tail=None)
        y = 50 + k * 58
        tl.put(f"qq{k}", b, 212, y, z=12, screen=True)
        no = ui.plate("NO", "red", "white", 20, 2)
        tl.put(f"qno{k}", no, 212 + 8, y + b.height + 2, z=14, screen=True)
        tl.put(f"qok{k}", ui.check("ink"), 212 + 8 + no.width + 5, y + b.height + 6, z=14, screen=True)
    cue(tl, "read strictly: NO is right both times")
    tl.beat("although under that reading no is right for both orders.", fade=True)


def readings(tl):
    """Geography with both coordinates printed above the question: GPT-4o mini has no flags (geo_analysis.json,
    conditions.fullcard). Then the paper's own test where only one reading works."""
    tl.section = "readings"
    G = charts.GEO["conditions"]["fullcard"]
    card = P.factcard(["lake A: coordinates", "lake B: coordinates"], WW - 12)
    _scene(tl, QW, card, "happy", ("card",), ("down", "up"), who="gpt")
    _name(tl, "GPT-4o mini")
    n = ui.say(f"{G['flags']} flags", "orange", 40)
    tl.put("t_zero", n, 236 - n.width // 2, 70, z=40, screen=True)
    s_ = T(f"YES right: {G['acc_yes_q']:.0%}", "slate")
    tl.put("t_zero2", s_, 236 - s_.width // 2, 70 + n.height + 6, z=40, screen=True)
    cue(tl, "coordinates given: 0 flags")
    tl.beat("With both coordinates printed it has no flags, so it reads \"west\" strictly mainly when it lacks them.", fade=True)

    # the paper's own test: places at the same latitude, one reading only
    tl.clear(); put_ground(tl)
    chart(tl, "ablation", dx=STD_R)            # the board at the right; GPT-4o mini in the foreground at the left, larger
    m = P.lakemap("due", 110, 70, same=True)
    tl.put("abmap", m, 36 + STD_R, 62, z=26, screen=True)
    stage(tl, "side", ("down", "down"), ("sweat",), who="gpt", c=56, k=1.25)
    cue(tl, "one reading only: still flagged")
    tl.beat("The paper's own test on pairs where only one reading works still flags GPT-4o mini on nine percent,", fade=True)
    stage(tl, "calm", ("out", "out"), who="gpt", c=56, k=1.25)
    cue(tl, "wording: only part of it")
    tl.beat("so wording explains only part of it.")


def act4(tl):
    two(tl)
    facts(tl)
    wording(tl)
    readings(tl)
