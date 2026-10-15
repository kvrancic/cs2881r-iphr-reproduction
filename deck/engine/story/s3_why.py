"""Act 3, what produces the flags: a model that either knows or guesses with one fixed lean per kind of question."""
from story.common import *
from px import rect


def _answer(ans, ok):
    """A small answer plate (YES green, NO red) with a tick or a cross after it."""
    p = ui.plate(ans, "green" if ans == "YES" else "red", "white", 20, 2)
    m = ui.check() if ok else ui.cross()
    img = blank(p.width + 3 + m.width, max(p.height, m.height))
    paste(img, p, 0, 0); paste(img, m, p.width + 3, (img.height - m.height) // 2)
    return img


def why(tl):
    tl.section = "why"
    tl.clear(); put_ground(tl)
    tl.put("slot3", P.slot(3, 336, 150, lit=True), 24, 34, z=10)
    tl.put("scale", scale(0, grey=True), 52, 92, z=11)
    tl.put("robot", robot("question"), at(192), 178 - RB_H, z=20)
    f = P.flag()
    tl.put("flag", f, 270, 178 - f.height, z=20)
    cue(tl, "3. what produces the flags?")
    tl.beat("Then we asked what produces the flags.", fade=True)

    # a simple model and its prediction ---------------------------------------------------------------------
    tl.drop("scale", "flag")
    tl.put("robot", robot("dice", ("down", "out"), ("coin",)), at(84), 178 - RB_H, z=20)
    tl.put("t_simple", T("a simple model", "ink"), 48, 76, z=40)
    tl.put("arr0", ui.arrow(24, "slate", 2), 152, 128, z=12)
    pr = ui.chip("predicted number of flags", "white", "slate")
    tl.put("t_pred", pr, 182, 112, z=40)
    ob = ui.chip("observed number of flags", "white", "ink")
    tl.put("t_obs", ob, 182, 138, z=40)
    cue(tl, "a simple model predicts the count")
    tl.beat("A very simple model predicts their number")

    tl.clear(); put_ground(tl)
    chart(tl, "predict")
    tl.beat("for half of the paper's models and for all eight of our runs.", fade=True)

    # knows, or guesses with a lean ---------------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(344), 20, GY, z=2)
    div = blank(1, 176)
    for y in range(0, 176, 4):
        rect(div, 0, y, 1, 2, "steel")
    tl.put("div", div, 192, 8, z=3)
    tl.put("t_knows", T("knows the answer", "ink"), 20, 12, z=40)
    tl.put("t_both", T("right in both orders", "leaf"), 20, 26, z=40)
    tl.put("robot", robot("happy"), at(70), ROBOT_Y, z=20)
    tl.put("ansk0", _answer("YES", True), 120, 112, z=22)
    tl.put("ansk1", _answer("NO", True), 120, 140, z=22)
    cue(tl, "either it knows", 8, 194)
    tl.beat("Either the model knows the answer,", fade=True)

    tl.put("t_guess", T("does not know: guesses", "ink"), 204, 12, z=40)
    tl.put("t_fixed", T("one fixed lean per kind", "wine"), 204, 26, z=40)
    tl.put("scale", scale(-1), 254, 40, z=8)
    tl.put("guesser", robot("dice", ("down", "out"), ("coin",)), at(244), ROBOT_Y, z=20)
    tl.put("ansg0", _answer("NO", True), 316, 140, z=22)
    tl.put("ansg1", _answer("NO", False), 316, 164, z=22)
    cue(tl, "or it guesses with a fixed lean", 8, 194)
    tl.beat("or it guesses with one fixed lean for each kind of question.")

    # the leans split ------------------------------------------------------------------------------------------
    tl.clear(); put_ground(tl)
    tl.put("scale", scale(0, grey=True), 46, 34, z=8)
    tl.put("scale2", scale(0, grey=True), 246, 34, z=8)
    kinds = [P.kindbox("dates", "dates"), P.kindbox("sizes", "sizes"), P.kindbox("ages", "ages")]
    x = 92 - (sum(k.width for k in kinds) + 24) // 2
    for i, k in enumerate(kinds):
        tl.put(f"kind{i}", k, x, 116, z=20)
        x += k.width + 12
    g = P.kindbox("geography", "geography")
    tl.put("kind3", g, 292 - g.width // 2, 116, z=20)
    cue(tl, "one lean for each kind of question")
    tl.beat("The leans split cleanly.", fade=True)

    t = charts.CHECKS["lean_by_kind_total"]
    tl.put("scale", scale(1))
    a = ui.runs([(f"{t['other_YES']}", "leaf"), (" flags lean YES", "ink")])
    b = ui.runs([(f"{t['other_NO']}", "wine"), (" lean NO", "slate")])
    tl.put("t_lyes", a, 92 - a.width // 2, 152, z=40)
    tl.put("t_lyes2", b, 92 - b.width // 2, 166, z=40)
    src = T("flagged pairs in the paper's released answers", "slate")
    tl.put("t_src", src, cx(src), 194, z=40, screen=True)
    cue(tl, "dates, sizes, ages: towards YES")
    tl.beat("On dates, sizes and ages the models lean towards yes.")

    tl.put("scale2", scale(-1))
    a = ui.runs([(f"{t['geography_NO']:,}", "wine"), (" flags lean NO", "ink")])
    b = ui.runs([(f"{t['geography_YES']}", "leaf"), (" lean YES", "slate")])
    tl.put("t_lno", a, 292 - a.width // 2, 152, z=40)
    tl.put("t_lno2", b, 292 - b.width // 2, 166, z=40)
    cue(tl, "geography: towards NO")
    tl.beat("On geography they lean towards no.")


def act3(tl):
    why(tl)
