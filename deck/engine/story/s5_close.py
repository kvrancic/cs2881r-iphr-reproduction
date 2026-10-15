"""Act 5, what Figure 2 measures: two things the reasoning never mentions; then thank you."""
from story.common import *

REPO = "github.com/kvrancic/cs2881r-iphr-reproduction"
LX, RX_, WY, WW, WH = 16, 228, 10, 140, 98


def _win(tl, k, x, q, title, seed=3):
    """A chat window: the question, a reasoning trace drawn as grey strokes, and the answer NO."""
    tl.put(f"win_c{k}", P.chat(WW, WH, title), x, WY, z=10)
    tl.put(f"qc{k}", P.bubble(q, WW - 12), x + 6, WY + 20, z=12)
    tl.put(f"trace{k}", P.trace(WW - 54, 4, seed=seed), x + 8, WY + 64, z=12)
    no = ui.plate("NO", "red", "white", 20, 2)
    tl.put(f"noc{k}", no, x + WW - no.width - 10, WY + WH - no.height - 10, z=14)


def close(tl):
    tl.section = "close"
    tl.clear(); put_ground(tl)
    chart(tl, "fig2_bars")
    st = ui.stamp("HOLDS UP", "green")
    tl.put("t_holds", st, 376 - st.width, 30, z=50, screen=True)
    tl.beat("So Figure 2 holds up as a measurement.", fade=True)

    tl.clear(); put_ground(tl)
    tl.put("floor", floor(150), 117, GY, z=2)
    tl.put("robot", robot("neutral"), at(192), ROBOT_Y, z=20)
    _win(tl, 0, LX, "Ajay River south of\nSalar de Arizaro?", "chat 1", 3)
    _win(tl, 1, RX_, "Salar de Arizaro\nsouth of Ajay River?", "chat 2, reversed", 5)
    cue(tl, "the behaviour is real", 8, 194)
    tl.beat("The behaviour is real.", fade=True)

    tl.put("scale", scale(0, grey=True), 22, 112, z=6)
    tl.put("compass", P.faint(P.compass(22)), 290, 128, z=6)
    q = ui.qmark("steel", 40)
    tl.put("qm0", q, 60, 118, z=8)
    tl.put("qm1", q, 306, 140, z=8)
    tl.put("robot", robot("side"))
    cue(tl, "two things the reasoning never mentions", 8, 194)
    tl.beat("What it measures is mostly two things the reasoning never mentions.")

    tl.drop("qm0")
    tl.put("scale", scale(-1))
    tl.put("t_lean", T("a fixed lean,\nwhen it does not know", "wine", align="center"), 0, 0, z=40)
    t = tl.objs["t_lean"].img
    tl.move("t_lean", x=max(6, 68 - t.width // 2), y=186)
    tl.drop("cue")
    tl.beat("One is a fixed lean that the model falls back on when it does not know.")

    tl.drop("qm1")
    tl.put("compass", P.compass(22))
    tl.put("t_strict", T("a strict reading,\nnever stated", "navy", align="center"), 0, 0, z=40)
    t = tl.objs["t_strict"].img
    tl.move("t_strict", x=min(378 - t.width, 314 - t.width // 2), y=186)
    tl.beat("The other is a strict reading of the question that it applies without saying so.")

    # one trace shows neither ---------------------------------------------------------------------------------
    tl.drop("win_c1", "qc1", "noc1", "trace1", "t_lean", "t_strict")
    tl.put("scale", scale(0, grey=True))
    tl.put("compass", P.faint(P.compass(22)))
    tl.put("robot", robot("neutral"))
    cue(tl, "one trace shows neither", 8, 194)
    tl.beat("No single trace shows either one.")

    _win(tl, 1, RX_, "Salar de Arizaro\nsouth of Ajay River?", "chat 2, reversed", 5)
    tl.put("link", P.link(RX_ - (LX + WW) - 8), LX + WW + 4, WY + 40, z=12)
    tl.put("scale", scale(-1))
    tl.put("compass", P.compass(22))
    tl.put("robot", robot("shock"))
    cue(tl, "ask the reversed question too", 8, 194)
    tl.beat("They only show up when you also ask the reversed question.")


def thanks(tl):
    tl.section = "thanks"
    tl.clear(); put_ground(tl)
    b = ui.big("Thank you", "ink", 60)
    tl.put("t_thanks", b, cx(b), 10, z=40, screen=True)
    tl.put("floor", floor(150), 117, 138, z=2)
    tl.put("robot", robot("happy", ("down", "up")), at(192), 138 - RB_H, z=20)
    smooth(tl, "names", "[Name 1]     [Name 2]     [Name 3]", 0, 150, "ink", 10, "Demi", align="center")
    smooth(tl, "repo", REPO, 0, 176, "navy", 9, "Medium", align="center")
    tl.beat("Thank you.", fade=True)


def act5(tl):
    close(tl)
    thanks(tl)
