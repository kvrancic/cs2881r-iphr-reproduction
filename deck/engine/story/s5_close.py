"""Act 5, what holds up, the limits, then thank you."""
from story.common import *
from story.s2_did import CARD_Y, CARD_W, CARD_H, BOT_X, _mini_wall, _key, lean_signs

REPO = "github.com/kvrancic/cs2881r-iphr-reproduction"
WHOS = ("gpt", "llama", "deepseek", "gemini")
NAMES = ("GPT-4o\nmini", "Llama 3.3\n70B", "DeepSeek\nV3", "Gemini 2.5\nFlash")


def close(tl):
    tl.section = "close"
    tl.clear(); put_ground(tl)
    chart(tl, "fig2_rec")
    stage(tl, "happy", ("up", "up"), c=332)
    cue(tl, "8 models: counts recompute")
    tl.beat("For the eight models with released data, Figure 2's counts recompute exactly.", fade=True)

    # every model holds a sign with its lean: the paper's run (blue) and ours (orange), one scale for all four
    tl.clear(); put_ground(tl)
    tl.put("floor", floor(340), 22, GY, z=2, screen=True)
    for k, (key, _) in enumerate(charts.FOUR):
        c_ = BOT_X[k]
        tl.put(f"bot{k}", robot("happy", who=WHOS[k]), at(c_), ROBOT_Y, z=20 + k, screen=True)
        tag = ui.tag(NAMES[k], "white", "ink")
        tl.put(f"t_bot{k}", tag, c_ - tag.width // 2, ROBOT_Y - tag.height - 10, z=40, screen=True)
    lean_signs(tl)
    _key(tl, "size of the lean")
    cue(tl, "every model: the same lean")
    tl.beat("Every model's lean repeats.", fade=True)

    # the flag counts: GPT-4o mini and Llama step forward with their counts; the other two step back
    R = charts.RUNS
    for k in (2, 3):
        tl.drop(f"bot{k}", f"t_bot{k}", f"sign{k}")
    for k, c_ in ((0, 140), (1, 244)):
        key = charts.FOUR[k][0]
        a, b = R["paper_same_pairs"][key]["n_unf"], R["base"][key]["n_unf"]
        tl.move(f"bot{k}", x=at(c_))
        tg = tl.objs[f"t_bot{k}"]
        tl.move(f"t_bot{k}", x=c_ - tg.img.width // 2)
        pc = P.placard([(a * 0.3, "paper", str(a)), (b * 0.3, "ours", str(b))], 76)
        tl.put(f"sign{k}", pc, c_ - pc.width // 2, ROBOT_Y + 52)
    tl.put("bot0", robot("grin", who="gpt"))
    _key(tl, "flagged pairs")
    cue(tl, "flag counts: the same")
    tl.beat("The flag counts repeat for GPT-4o mini and Llama.")


def limits(tl):
    """The limits as cards dealt one per phrase: each new card slides in and the row stays centred."""
    tl.section = "limits"
    tl.clear(); put_ground(tl)
    faces = []
    mw = _mini_wall(lit=(1, 7), cols=2, rows=3)
    faces.append((mw, "1,014 pairs,\nnot all " + f"{charts.N_PAIRS:,}"))
    faces.append((robot("focus", acc=("judge",)), "a different\njudge"))
    faces.append((robot("question"), "same weights\nstill served?"))
    says = ("Our limits are a smaller sample,", "a different judge",
            "and no way to check that providers still serve the same weights.")
    gap = 12
    for n in range(1, 4):
        x0 = 192 - (n * CARD_W + (n - 1) * gap) // 2
        for k in range(n):
            img, lab = faces[k]
            x = x0 + k * (CARD_W + gap)
            tl.put(f"card_{k}", P.card(CARD_W, CARD_H), x, CARD_Y, z=10, screen=True)
            tl.put(f"lim{k}", img, x + (CARD_W - img.width) // 2 + (3 if k else 0), CARD_Y + 12 + max(0, (84 - img.height) // 2), z=12, screen=True)
            t = T(lab, "ink", align="center")
            tl.put(f"t_lim{k}", t, x + (CARD_W - t.width) // 2, CARD_Y + CARD_H - t.height - 12, z=40, screen=True)
        if n == 1:
            cue(tl, "limits")
        tl.beat(says[n - 1], fade=(n == 1))


def thanks(tl):
    """A curtain call: thank you and the names in pixel type, the repo link in smooth type (about four fifths the
    width of the pixel line), above the four models we reran, all on the ground line, two of them waving."""
    tl.section = "thanks"
    tl.clear(); put_ground(tl)
    b = ui.big("Thank you", "ink", 60)
    tl.put("t_thanks", b, cx(b), 18, z=40, screen=True)
    nm = T("[Name 1]     [Name 2]     [Name 3]", "ink")
    y = 18 + b.height + 5
    tl.put("t_names", nm, cx(nm), y, z=40, screen=True)
    smooth(tl, "t_repo", REPO, 0, y + nm.height + 6, "slate", size=14, face="Demi", align="center")
    tl.put("floor", floor(340), 22, GY, z=2, screen=True)
    arms = (("down", "up"), ("down", "down"), ("down", "down"), ("up", "down"))
    for k in range(4):
        tl.put(f"bot{k}", robot("happy", arms[k], who=WHOS[k]), at(BOT_X[k]), ROBOT_Y, z=20 + k, screen=True)
    tl.beat("Thank you.", fade=True)


def act5(tl):
    close(tl)
    limits(tl)
    thanks(tl)
