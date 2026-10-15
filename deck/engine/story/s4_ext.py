"""Act 4, the two variations: values in the prompt on the questions that are not about geography, then why
GPT-4o mini fails on geography and the wording ladder."""
from story.common import *
from px import rect

WX, WY, WW = 8, 24, 168                  # the chat window of both variations
RBC = 338                                 # the big robot's centre, to the right
SC = 238                                  # the big scale's centre, between the window and the robot
QF = "Was film A released\nbefore film B?"
QW = "Is lake B west\nof lake A?"


def two(tl):
    tl.section = "variations"
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    fc = P.factcard(["A: true value", "B: true value"], 112)
    tl.put("fact", fc, 22, 58, z=12, screen=True)
    t1 = T("values in the prompt", "ink")
    tl.put("t_v1", t1, 22 + (fc.width - t1.width) // 2, 58 + fc.height + 8, z=40, screen=True)
    cp = P.compass(30)
    tl.put("compass", cp, 222 - cp.width // 2, 44, z=12, screen=True)
    t2 = T("geography wording", "ink")
    tl.put("t_v2", t2, 222 - t2.width // 2, 44 + cp.height + 8, z=40, screen=True)
    tl.put("floor", floor(270), 6, GY, z=2, screen=True)
    stage(tl, "dots")
    tl.beat("Fourth, the two variations.", fade=True)


def _name(tl, nm):
    """The model's name once, as a tag above the big robot."""
    t = ui.tag(nm, "white", "ink")
    tl.put("t_name", t, RBC - t.width // 2 - 2, ROBOT_Y - t.height - 6, z=40)


def _scene(tl, bubble_text, card=None, face="neutral", acc=(), arms=("down", "down"), answer=None, **look):
    """The chat window (card above the question, an optional answer below), the big robot on the ground."""
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(220), 160, GY, z=2)
    y = WY + 20
    if card is not None:
        tl.put("fact", card, WX + 6, y, z=14)
        y += card.height + 4
    b = P.bubble(bubble_text, WW - 12)
    tl.put("q", b, WX + 6, y, z=12)
    y += b.height + 6
    if answer is not None:
        tl.put("ans", answer, WX + 8, y, z=12)
        y += answer.height + 6
    tl.put("win_q", P.chat(WW, y - WY, "chat"), WX, WY, z=10)
    tl.put("robot", robot(face, arms, acc, **look), at(RBC), ROBOT_Y, z=20)
    return y


def _big_scale(tl, tilt=0, grey=False):
    sc = scale(tilt, grey=grey, s=1.5)
    tl.put("scale", sc, SC - sc.width // 2, feet(sc), z=6)


def _numbers_trace():
    """A reasoning trace in grey strokes with two written numbers in gold: the values the model writes as it compares."""
    img = P.trace(150, 4, seed=7)
    for (x, y) in ((24, 0), (96, 12)):
        rect(img, x - 1, y - 2, 26, 6, "ink"); rect(img, x, y - 1, 24, 4, "gold"); rect(img, x, y - 1, 24, 1, "yellow")
    return img


def facts(tl):
    tl.section = "fact cards"
    card = P.factcard(["film A: release date", "film B: release date"], WW - 12)
    _scene(tl, QF, card, "focus", ("card",), ("down", "up"))
    _big_scale(tl, 0, grey=True)
    cue(tl, "both true values, above the question")
    tl.beat("In the first we printed both true values above each question.", fade=True)

    tl.clear(); put_ground(tl)
    chart(tl, "facts_before")
    stage(tl, "neutral")
    tl.beat("Outside geography", fade=True)
    chart(tl, "facts_after")
    stage(tl, "happy", POINT)
    tl.beat("the flags went from fifty-seven to zero across four models.")

    # each value asked alone: Llama mostly knows the order ------------------------------------------------------
    chart(tl, "recall")
    stage(tl, "happy")
    tl.beat("Asked for each value on its own, Llama ordered about seven in ten of its flagged pairs outside geography correctly,")
    chart(tl, "recall_guess")
    stage(tl, "focus", POINT)
    tl.beat("where guessing gives five in ten.")

    # in its wrong answers the written numbers support the wrong answer -----------------------------------------
    clear_charts(tl)
    yes = ui.plate("YES", "green", "white", 20, 2)
    tr = _numbers_trace()
    ans = blank(tr.width, tr.height + 4 + yes.height)
    paste(ans, tr, 0, 0); paste(ans, yes, 0, tr.height + 4); paste(ans, ui.cross("ink"), yes.width + 4, tr.height + 4 + (yes.height - 9) // 2)
    _scene(tl, QF, None, "focus", answer=ans, ant="gold", hat="beret")
    _name(tl, "Llama 3.3 70B")
    _big_scale(tl, 1)
    cue(tl, "wrong answer: its numbers back it")
    tl.beat("In its wrong answers, the numbers it writes support the wrong answer.", fade=True)


MAP_XY, MAP_WH = (8, 34), (204, 120)
LR = 342                                   # the robot's centre in the lake scene


def wording(tl):
    tl.section = "geography"
    y = _scene(tl, QW, None, "focus")
    cp = P.compass(30)
    tl.put("compass", cp, WX + (WW - cp.width) // 2 + 20, y + 14, z=16)
    sc = scale(-1)
    tl.put("scale", sc, SC - sc.width // 2, feet(sc), z=6)
    _name(tl, "GPT-4o mini")
    cue(tl, "why it fails on geography")
    tl.beat("In the second we asked why GPT-4o mini fails on geography.", fade=True)

    tl.clear(); put_ground(tl)
    chart(tl, "dist", alias={"dib3": "map"})
    stage(tl, "focus", POINT)
    cue(tl, "far apart: more flags")
    tl.beat("Its flags are most common for places that are far apart,", fade=True)

    # far apart: the easiest to locate; the farthest bar opens into the one map of the lakes --------------------
    clear_charts(tl)
    tl.keep("ground", "map", "robot", "cfloor")
    q = P.bubble("Is lake B west of lake A?", 172)
    tl.put("q", q, MAP_XY[0], 8, z=12, screen=True)
    tl.put("map", P.lakemap(None, *MAP_WH), *MAP_XY, z=8, screen=True, scale=1.0)
    tl.put("robot", robot("happy"), at(LR), ROBOT_Y, z=20, screen=True)
    tl.put("cfloor", floor(100), LR - 50, GY, z=2, screen=True)
    t = ui.tag("GPT-4o mini", "white", "ink")
    tl.put("t_name", t, LR - t.width // 2 - 2, ROBOT_Y - t.height - 6, z=40, screen=True)
    cue(tl, "far apart: should be easy")
    tl.beat("which should be the easiest to put in order.", morph=0.9)

    b1 = P.bubble("B is southwest\nof A.", 96, tail="side")
    tl.put("say1", b1, LR - 50 - 2 - b1.width + 6, 92, z=22, screen=True)
    tl.put("robot", robot("focus"))
    cue(tl, "its answer: southwest")
    tl.beat("A typical wrong answer says that a lake is southwest of another,")

    b2 = P.bubble("Southwest,\nnot due west.\nSo: NO.", 96, tail="side")
    tl.put("say2", b2, LR - 50 - 2 - b2.width + 6, 92 + b1.height + 4, z=22, screen=True)
    tl.put("robot", robot("smug"))
    cue(tl, "southwest does not count")
    tl.beat("so it is not directly west of it.")

    # the wording ladder ----------------------------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    chart(tl, "ladder2")
    stage(tl, "neutral")
    tl.beat("A paraphrase with the same vague direction left the flags at about 140.", fade=True)
    chart(tl, "ladder3")
    _glyph(tl, "ladder3", 2, "further")
    stage(tl, "happy")
    tl.beat("One sentence saying that anywhere further west counts cut them to 31.")
    chart(tl, "ladder4")
    _glyph(tl, "ladder4", 2, "further")
    _glyph(tl, "ladder4", 3, "due")
    stage(tl, "shock", POINT)
    tl.beat("The opposite sentence, that only directly west counts, raised them to 667 of 684.")


def _glyph(tl, slide, i, reading):
    """The mini lake map of a wording, under its bar's label."""
    x, y, w, h = chart_pos(slide, f"ldl{i}")
    g = P.minimap(reading)
    tl.put(f"glyph{i}", g, round(x + w / 2 - g.width / 2), round(y + h + 3), z=30, screen=True)


def act4(tl):
    two(tl)
    facts(tl)
    wording(tl)
