"""Act 4, the two extensions: the aqua fact card, and the geography questions asked in exact terms."""
from story.common import *
from px import rect

WX, WY, WW, WH = 30, 30, 210, 130        # the chat window of both extensions
RBC = 318                                 # the robot's centre, to the right of the window
Q = "Is the Ajay River south of Salar de Arizaro?"
QW = "Is lake A west of lake B?"
QL = "Does lake A have a more western longitude than lake B?"


def _frame_card(icon, label, w=160, h=118):
    img = P.slot(None, w, h)
    paste(img, icon, (w - icon.width) // 2, 16 + (64 - icon.height) // 2)
    t = T(label, "ink", 20, maxw=w - 16, align="center")
    paste(img, t, (w - t.width) // 2, 86)
    return img


def two(tl):
    tl.section = "extensions"
    tl.clear(); put_ground(tl)
    fc = P.factcard(["A: true value", "B: true value"], 96)
    tl.put("frame1", _frame_card(fc, "1. put the facts in front"), 24, 46, z=10)
    tl.put("frame2", _frame_card(P.compass(24), "2. ask in exact terms"), 200, 46, z=10)
    cue(tl, "two extensions")
    tl.beat("That led to our two extensions.", fade=True)


def _scene(tl, bubble_text, card=None, tilt=-1, face="neutral"):
    tl.put("floor", floor(120), RBC - 60, GY, z=2)
    tl.put("win_q", P.chat(WW, WH, "chat"), WX, WY, z=10)
    y = WY + 20
    if card is not None:
        tl.put("fact", card, WX + 6, y, z=14)
        y += card.height + 4
    else:
        tl.drop("fact")
    b = P.bubble(bubble_text, WW - 12)
    tl.put("q", b, WX + 6, y, z=12)
    tl.put("scale", scale(tilt), RBC - 46, 14, z=6)
    tl.put("robot", robot(face), at(RBC), ROBOT_Y, z=20)
    return tl


def facts(tl):
    tl.section = "fact cards"
    tl.clear(); put_ground(tl)
    card = P.factcard(["Ajay River: its latitude", "Salar de Arizaro: its latitude"], WW - 12)
    _scene(tl, Q, card, tilt=-1, face="focus")
    tl.put("t_card", T("both true values, above the question", "deep"), WX + 4, WY + WH + 6, z=40)
    cue(tl, "1. both true values printed", 8, 194)
    tl.beat("In the first, we printed both true values above each question.", fade=True)

    tl.clear(); put_ground(tl)
    chart(tl, "facts_after")
    tl.beat("The flags almost disappear for every model we tried.", fade=True)

    tl.clear(); put_ground(tl)
    _scene(tl, Q, card, tilt=0, face="calm")
    tl.put("t_card", T("with the facts: the scale stays level", "deep"), WX + 4, WY + WH + 6, z=40)
    cue(tl, "the lean acts only without the facts", 8, 194)
    tl.beat("So the lean only acts when the model does not have the facts in front of it.", fade=True)


def wording(tl):
    tl.section = "exact wording"
    tl.clear(); put_ground(tl)
    _scene(tl, QW, None, tilt=-1, face="neutral")
    tl.put("compass", P.compass(22), WX + WW - 56, WY + WH - 56, z=16)
    tl.put("t_geo", T("geography, no facts", "slate"), WX + 4, WY + WH + 6, z=40)
    cue(tl, "2. the same questions, in exact terms", 8, 194)
    tl.beat("In the second, we kept the geography questions without any facts but asked them in exact terms.", fade=True)

    m = P.lonmap(WW - 12, 54, pins=((150, 22, "red", "A"), (60, 40, "sky", "B")), lit=None)
    tl.put("q", P.bubble(QL, WW - 12), WX + 6, WY + 20)
    qh = tl.objs["q"].img.height
    tl.put("map", m, WX + 6, WY + 20 + qh + 2, z=13)
    tl.drop("compass")
    tl.put("t_geo", T("\"west of\" becomes longitude", "slate"), WX + 4, WY + WH + 6)
    cue(tl, "a more western longitude?", 8, 194)
    tl.beat("We asked whether one place has a more western longitude than another.")

    tl.clear(); put_ground(tl)
    chart(tl, "coord_drop")
    tl.beat("GPT-4o mini's geography flags fell from 131 to 24.", fade=True)
    clear_charts(tl)
    chart(tl, "coord_share")
    tl.beat("Geography is almost all of its bar.", fade=True)

    # what the answers say ---------------------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(120), RBC - 60, GY, z=2)
    m = P.lonmap(220, 130, pins=((168, 44, "red", "A"), (64, 98, "sky", "B")))
    tl.put("map", m, 20, 30, z=8)
    tl.put("robot", robot("focus"), at(RBC), ROBOT_Y, z=20)
    b1 = P.bubble("B is southwest of A.", 112, tail="right")
    tl.put("say1", b1, 262, 20, z=22)
    tl.put("ok1", ui.check(), 262 + b1.width - 12, 12, z=24)
    tl.put("t_rough", T("the rough position: right", "leaf"), 24, 166, z=40)
    cue(tl, "it knows roughly where both are", 8, 194)
    tl.beat("When we read its answers, the model often knew the rough position", fade=True)

    b2 = P.bubble("Southwest is not west, so NO.", 112, tail="right")
    tl.put("say2", b2, 262, 20 + b1.height + 2, z=22)
    tl.put("robot", robot("smug"))
    tl.put("t_rough", T("then: southwest does not count", "wine"), 24, 166)
    cue(tl, "southwest does not count as west", 8, 194)
    tl.beat("and then decided that southwest does not count as west.")

    # both orders NO under the strict reading ----------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(120), RBC - 60, GY, z=2)
    tl.put("robot", robot("smug"), at(RBC), ROBOT_Y, z=20)
    for k, (qq, y) in enumerate((("Is B west of A?", 34), ("Is A west of B?", 100))):
        tl.put(f"win_s{k}", P.chat(200, 58, "chat " + str(k + 1)), 30, y, z=10)
        tl.put(f"qs{k}", P.bubble(qq, 120), 36, y + 18, z=12)
        no = ui.plate("NO", "red", "white", 20, 2)
        tl.put(f"nos{k}", no, 168, y + 22, z=14)
        tl.put(f"oks{k}", ui.check(), 168 + no.width + 4, y + 25, z=15)
    tl.put("t_strict", T("if only due west counts,\nNO is right both times", "ink"), 30, 166, z=40)
    cue(tl, "under the strict reading: NO, NO", 8, 194)
    tl.beat("Under that strict reading no is correct in both orders.", fade=True)

    tl.put("robot", robot("neutral", acc=("zip",)))
    tl.put("t_strict", T("the strict reading\nis never stated", "wine"), 30, 166)
    cue(tl, "it never says it chose it", 8, 194)
    tl.beat("The model does not say that it chose it.")


def act4(tl):
    two(tl)
    facts(tl)
    wording(tl)
