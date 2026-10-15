"""Act 5, what Figure 2 measures, the limits, then thank you."""
from story.common import *
from px import rect
from story.s2_did import CARD_X, CARD_Y, CARD_W, CARD_H

REPO = "github.com/kvrancic/cs2881r-iphr-reproduction"
Q1 = "Ajay River south\nof Arizaro?"            # the same two questions as the Figure 1 example
Q2 = "Arizaro south of\nAjay River?"


def _win(tl, k, x, q, title, seed=3, y=10, ww=140, wh=98):
    """A chat window: the question, a reasoning trace drawn as grey strokes, and the answer NO."""
    tl.put(f"win_c{k}", P.chat(ww, wh, title), x, y, z=10)
    tl.put(f"qc{k}", P.bubble(q, ww - 12), x + 6, y + 20, z=12)
    tl.put(f"trace{k}", P.trace(ww - 54, 4, seed=seed), x + 8, y + 58, z=12)
    no = ui.plate("NO", "red", "white", 20, 2)
    tl.put(f"noc{k}", no, x + ww - no.width - 10, y + wh - no.height - 10, z=14)


def readings(tl):
    """Geography: many flags depend on how the model reads "west", and no answer says it can be read two ways.
    The two readings in the order the talk gives them: anywhere further west (31), then due west only (667)."""
    tl.section = "readings"
    tl.clear(); put_ground(tl)
    q = P.bubble("Is lake B west of lake A?", 172)
    tl.put("q", q, (W - q.width) // 2, 6, z=12)
    for k, (reading, lab, fg, bg) in enumerate((("further", "anywhere further west", "ink", "yellow"),
                                                 ("due", "due west only", "white", "ink"))):
        x = 14 + k * 186
        tl.put(f"map{k}", P.lakemap(reading), x, 40, z=8)
        t = ui.chip(lab, fg, bg)
        tl.put(f"t_read{k}", t, x + 85 - t.width // 2, 146, z=40)
    cue(tl, "how it reads \"west\"")
    tl.beat("So many of these flags depend on how the model reads \"west\".", fade=True)

    # no answer says so: close on the zipped robot (GPT-4o mini on geography) -------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(150), 126, GY, z=2)
    _win(tl, 0, 68, "Is lake B west\nof lake A?", "chat", 3, y=62, ww=106, wh=86)
    tl.put("robot", robot("neutral", acc=("zip",)), at(218), ROBOT_Y, z=20)
    nm = ui.tag("GPT-4o mini", "white", "ink")
    tl.put("t_name", nm, 218 - nm.width // 2, ROBOT_Y - nm.height - 4, z=40)
    lab = T("two readings?", "slate")
    box = ui.dashed(lab.width + 12, lab.height + 10, "steel", q=False)
    paste(box, lab, 6, 5)
    x_ = ui.cross("ink")
    img = blank(box.width + 4 + x_.width, box.height)
    paste(img, box, 0, 0); paste(img, x_, box.width + 4, (box.height - x_.height) // 2)
    tl.put("t_unsaid0", img, 248, 122, z=40)
    tl.focus(212, 121, 1.2)
    cue(tl, "not in any answer we read")
    tl.beat("None of the answers we read says that the question can be read two ways.", fade=True)


def _tiles():
    """The four findings of the close, each a picture and a few keywords, sized like the four cards of act 2.
    The first: a pair of questions in the paper's run (blue) and the same pair in ours (orange), a year apart."""
    t1 = blank(72, 70)
    paste(t1, P.calendar(30), 21, 0)
    for k, col in enumerate(("sky", "orange")):
        x0 = k * 40
        rect(t1, x0, 40, 32, 28, col); rect(t1, x0 + 1, 41, 30, 26, "white")
        paste(t1, P.qcard("place", 14, 20), x0 + 2, 44); paste(t1, P.qcard("place", 14, 20), x0 + 16, 44)
    t2 = P.compass(30)
    t3 = blank(72, 66)
    paste(t3, P.chat(72, 46, ""), 0, 0)
    for (x, y) in ((8, 22), (40, 22)):
        rect(t3, x - 1, y - 2, 22, 6, "ink"); rect(t3, x, y - 1, 20, 4, "gold"); rect(t3, x, y - 1, 20, 1, "yellow")
    yes = ui.plate("YES", "green", "white", 20, 2)
    paste(t3, yes, 8, 66 - yes.height); paste(t3, ui.cross("ink"), 8 + yes.width + 3, 66 - yes.height + 3)
    t4 = blank(72, 66)
    paste(t4, bot("question"), 0, 14)
    paste(t4, yes, 44, 36)
    return [(t1, "GPT-4o mini\nrepeats a\nyear later"), (t2, "geography:\nreading\nof \"west\""),
            (t3, "others:\nnumbers\nback errors"), (t4, "Llama:\nunsure, still\nanswers")]


def close(tl):
    tl.section = "close"
    tl.clear(); put_ground(tl)
    chart(tl, "fig2_rec")
    stage(tl, "happy", POINT)
    cue(tl, "the counts reproduce")
    tl.beat("So Figure 2's numbers hold up.", fade=True)

    # the four cards of act 2 come back, now with what we found
    clear_charts(tl)
    tl.clear(); put_ground(tl)
    for k, x in enumerate(CARD_X):
        tl.put(f"card_{k}", P.cardback(CARD_W, CARD_H), x, CARD_Y, z=10, screen=True)
    says = ("For GPT-4o mini the pair-level effect repeats a year later.",
            "On geography much of it depends on how the model reads the direction word.",
            "On the other questions the wrong answers write numbers that support the wrong answer.",
            "Llama often says it is unsure and answers anyway.")
    for k, ((img, lab), say) in enumerate(zip(_tiles(), says)):
        x = CARD_X[k]
        tl.put(f"card_{k}", P.card(CARD_W, CARD_H))
        tl.put(f"tile{k}", img, x + (CARD_W - img.width) // 2, CARD_Y + 10 + (88 - img.height) // 2, z=12, screen=True)
        t = T(lab, "ink", align="center")
        tl.put(f"t_tile{k}", t, x + (CARD_W - t.width) // 2, CARD_Y + CARD_H - t.height - 10, z=40, screen=True)
        tl.beat(say, fade=(k == 0))


def limits(tl):
    """Three slots, laid out from the start as dashed outlines, filled one per phrase."""
    tl.section = "limits"
    tl.clear(); put_ground(tl)
    FX, FY, FW, FH = (16, 136, 256), 22, 112, 150
    from story.s2_did import _mini_wall
    for k in range(3):
        tl.put(f"frame{k}", ui.dashed(FW, FH, "steel", q=False), FX[k], FY, z=10)
    tl.put("frame0", P.slot(None, FW, FH))
    mw = _mini_wall(lit=(1, 7), cols=2, rows=3)
    tl.put("lim0", mw, FX[0] + (FW - mw.width) // 2, FY + 18, z=12)
    t0 = T("1,014 pairs,\nnot all " + f"{charts.N_PAIRS:,}", "ink", align="center")
    tl.put("t_lim0", t0, FX[0] + (FW - t0.width) // 2, FY + 104, z=40)
    cue(tl, "limits")
    tl.beat("Our limits are a smaller sample,", fade=True)

    tl.put("frame1", P.slot(None, FW, FH))
    tl.put("lim1", judge("focus"), FX[1] + 3, FY + 8, z=12)
    t1 = T("our labeller,\nnot their judge", "ink", align="center")
    tl.put("t_lim1", t1, FX[1] + (FW - t1.width) // 2, FY + 104, z=40)
    tl.beat("a different judge")

    tl.put("frame2", P.slot(None, FW, FH))
    tl.put("lim2", robot("question"), FX[2] + 3, FY + 8, z=12)
    t2 = T("same weights\nstill served?", "ink", align="center")
    tl.put("t_lim2", t2, FX[2] + (FW - t2.width) // 2, FY + 104, z=40)
    tl.beat("and no way to check that providers still serve the same weights.")


def thanks(tl):
    """The cast once more: both chats of the example, the robot with the fact card, the coloured scale and our
    labeller. Pixel type for the words, Avenir only for the names and the repo."""
    tl.section = "thanks"
    tl.clear(); put_ground(tl)
    b = T("Thank you", "ink", 60)
    tl.put("t_thanks", b, cx(b), 16, z=40, screen=True)
    smooth(tl, "names", "[Name 1]     [Name 2]     [Name 3]", 0, 16 + b.height + 6, "ink", 10, "Demi", align="center")
    smooth(tl, "repo", REPO, 0, 16 + b.height + 22, "ink", 12, "Demi", align="center")
    tl.put("floor", floor(360), 12, GY, z=2)
    for k, (x, y, q, t) in enumerate(((16, 84, Q1, "chat 1"), (28, 135, Q2, "chat 2"))):
        tl.put(f"win_t{k}", P.chat(124, 48, t), x, y, z=10 + k)
        tl.put(f"q_t{k}", P.bubble(q, 112), x + 6, y + 17, z=12 + k)
    sc = scale(-1, s=0.85)
    tl.put("scale", sc, 274 - sc.width // 2, feet(sc), z=6)
    tl.put("robot", robot("happy", ("down", "up"), ("card",)), at(184), ROBOT_Y, z=20)
    tl.put("judge", robot("happy", acc=("judge",)), at(350), ROBOT_Y, z=18)
    tl.beat("Thank you.", fade=True)


def act5(tl):
    readings(tl)
    close(tl)
    limits(tl)
    thanks(tl)
