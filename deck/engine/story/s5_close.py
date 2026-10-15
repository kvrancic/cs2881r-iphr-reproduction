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
    stage(tl, "happy", ("up", "up"), c=326)      # on the floor right of the board, as on Figure 2
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
    cue(tl, "4 reruns: about as strong")
    tl.beat("Each of the four models we reran leans about as strongly as in the paper.", fade=True)

    # GPT-4o mini steps forward, a quarter larger, with its flag count; the other three step back
    R = charts.RUNS
    for k in (1, 2, 3):
        tl.drop(f"bot{k}", f"t_bot{k}", f"sign{k}")
    key = charts.FOUR[0][0]
    a, b = R["paper_same_pairs"][key]["n_unf"], R["base"][key]["n_unf"]
    k_ = 1.25
    place(tl, "bot0", robot("grin", who="gpt"), 192, k_, z=20)
    tg = tl.objs["t_bot0"]
    tl.move("t_bot0", x=192 - tg.img.width // 2, y=round(GY - RB_H * k_ - tg.img.height) + 1)   # under the key, over the antenna
    pc = P.placard([(a * 0.5, "paper", str(a)), (b * 0.5, "ours", str(b))], 100)
    tl.put("sign0", pc, 192 - pc.width // 2, GY - RB_H * k_ + 64, z=36, screen=True)
    _key(tl, "flagged pairs")
    cue(tl, "GPT-4o mini: count repeats")
    tl.beat("GPT-4o mini's flag count repeats closely.")


def limits(tl):
    """The limits as cards dealt one per phrase: each new card slides in and the row stays centred."""
    tl.section = "limits"
    tl.clear(); put_ground(tl)
    faces = []
    mw = _mini_wall(lit=(1, 7), cols=2, rows=3)
    faces.append((mw, "1,014 pairs,\nnot all " + f"{charts.N_PAIRS:,}"))
    faces.append((robot("focus", acc=("judge",)), "a different\njudge"))
    faces.append((robot("question"), "weights\nunchanged?"))
    says = ("Our limits are a smaller sample,", "a different judge",
            "and no way to check that providers still serve the same weights.")
    gap, CW = 10, 112                         # cards wide enough that every label keeps 16 px from the edges
    for n in range(1, 4):
        x0 = 192 - (n * CW + (n - 1) * gap) // 2
        for k in range(n):
            img, lab = faces[k]
            x = x0 + k * (CW + gap)
            tl.put(f"card_{k}", P.card(CW, CARD_H), x, CARD_Y, z=10, screen=True)
            tl.put(f"lim{k}", img, x + (CW - img.width) // 2 + (3 if k else 0), CARD_Y + 12 + max(0, (84 - img.height) // 2), z=12, screen=True)
            t = T(lab, "ink", align="center")
            tl.put(f"t_lim{k}", t, x + (CW - t.width) // 2, CARD_Y + CARD_H - t.height - 12, z=40, screen=True)
        if n == 1:
            cue(tl, "limits")
        tl.beat(says[n - 1], fade=(n == 1))


def thanks(tl):
    """A curtain call: thank you and the names in pixel type, the repo link in smooth type (about four fifths the
    width of the pixel line), above the four models we reran, all on the ground line, two of them waving."""
    tl.section = "thanks"
    tl.clear(); put_ground(tl)
    b = ui.say("Thank you", "ink", 48)
    tl.put("t_thanks", b, cx(b), 12, z=40, screen=True)
    nm = T("Shlok Dholakia     Nadia Sumin", "ink")
    nm2 = T("Karlo Vrancic     Marc Walden", "ink")
    y = 12 + b.height + 4
    tl.put("t_names", nm, cx(nm), y, z=40, screen=True)
    y2 = y + nm.height + 3
    tl.put("t_names2", nm2, cx(nm2), y2, z=40, screen=True)
    smooth(tl, "t_repo", REPO, 0, y2 + nm2.height + 6, "slate", size=14, face="Demi", align="center")
    tl.put("floor", floor(340), 22, GY, z=2, screen=True)
    arms = (("down", "up"), ("down", "down"), ("down", "down"), ("up", "down"))
    for k in range(4):
        tl.put(f"bot{k}", robot("happy", arms[k], who=WHOS[k]), at(BOT_X[k]), ROBOT_Y, z=20 + k, screen=True)
    tl.beat("Thank you.", fade=True)


def act5(tl):
    close(tl)
    limits(tl)
    thanks(tl)
