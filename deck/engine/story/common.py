"""Shared helpers for the storyboard: the cast, text, chart placement and the orientation cue."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reg import spr
from px import W, H, blank, paste, hitext, HI
from ground import ground
from sprites import deckui as ui
from sprites import props as P
import charts

GY = 184          # ground line: feet stand on it

# Objects that other things may sit on (a label on a window, a bar on a panel). The layout check skips them.
BACKDROPS = {"ground", "floor", "held", "doc", "term"}
BACKDROP_PREFIX = ("win_", "slot", "frame", "map", "wall", "panel", "card_", "c_")


# --- the cast --------------------------------------------------------------------------------------
RB_W, RB_H, RB_CX = 112, 86, 50      # the big robot's canvas and the x of its body's centre in it

# One look per model, the same on every slide: antenna colour plus one accessory.
LOOK = {None: dict(ant="red"),
        "gpt": dict(ant="pink", acc=("badge",)),         # GPT-4o mini: pink antenna, a chat-bubble badge
        "llama": dict(ant="gold", hat="beret"),          # Llama 3.3 70B: a brown beret
        "deepseek": dict(ant="steel", hat="fin"),        # DeepSeek V3: a slate fin
        "gemini": dict(ant="plum", hat="bow"),           # Gemini 2.5 Flash: a gold bow
        "luna": dict(ant="cyan", hat="moon")}            # GPT-5.6 Luna (the fact-card runs): a gold crescent moon


def robot(face="neutral", arms=("down", "down"), acc=(), grey=False, ant=None, hat=None, tint=None, who=None):
    """The model under test, drawn big (112x86 canvas, body centred at x 50, feet on the last row). who picks the
    model's look (LOOK)."""
    lk = LOOK[who]
    acc = tuple(acc) + tuple(lk.get("acc", ()))
    return spr("robot.big", _w=RB_W, _h=RB_H, face=face, arms=tuple(arms), acc=acc, grey=grey,
               ant=ant or lk["ant"], hat=hat or lk.get("hat"), tint=tint)


def bot(face="neutral", arms=("down", "down"), acc=(), flip=False):
    """The robot at 1x without a model's look (used inside cards)."""
    img = spr("robot.robot", _w=58, _h=50, face=face, arms=tuple(arms), acc=tuple(acc))
    if flip:
        from px import flip as _flip
        img = _flip(img)
    return img


def at(cx_):
    """x that centres the robot's body on cx_."""
    return cx_ - RB_CX


ROBOT_Y = GY - RB_H


def judge(face="focus"):
    """Our labeller: the robot with a judge's cap and a rubber stamp held out."""
    return robot(face, ("down", "out"), ("stamp", "judge"))


def scale(tilt=0, grey=False, s=1.0, load=None):
    return spr("props.scale", _w=86, _h=72, tilt=tilt, grey=grey, s=s, load=load)


# --- chart scenes: the board, and the robot (the model under test) acting beside it --------------------------
RX, LX = 324, 60                    # the robot's body centre when it stands right or left of a board
POINT = ("out", "down")             # the left arm held out towards a board on its left
POINT_R = ("down", "out")           # the right arm held out towards a board on its right
FIG2_C = 38                         # shifts that centre a board when no robot stands beside it
STD_C = 48
STD_R = 88                          # the standard board shifted right, the robot at its left


def place(tl, id, img, c, k=1.0, gy=GY, z=20, screen=True):
    """Stand a big robot picture with its body centred on c and its feet on gy, drawn k times larger (1, 1.25,
    1.5 or 2: every robot pixel stays a whole block in the export)."""
    tl.put(id, img, c - RB_CX * k, gy - RB_H * k, z=z, screen=screen, scale=k)
    return tl


def stage(tl, face="neutral", arms=("down", "down"), acc=(), who=None, side="R", on=True, c=None, k=1.0):
    """The model under test at 2x on the ground line beside the board (side 'R' or 'L', or its body centre c),
    k times larger for the moments that matter; on=False removes it."""
    tl.drop("scale", "held")
    if on:
        c = c if c is not None else RX if side == "R" else LX
        place(tl, "robot", robot(face, arms, acc, who=who), c, k, z=30)
        tl.put("cfloor", floor(round(100 * k)), c - round(50 * k), GY, z=2, screen=True)
    else:
        tl.drop("robot", "cfloor")
    return tl


def hand(tl, side="L", arms=("down", "down")):
    """Native screen position of a hand of the big robot as it stands now."""
    from sprites.robot import big_hand
    o = tl.objs["robot"]
    hx, hy = big_hand(tuple(arms), side)
    return round(o.x + hx * o.scale), round(o.y + hy * o.scale)


def hold(tl, kind, hx, hy, tx, ty, r=16):
    """A long prop from a hand at (hx, hy) to a target: 'stick' a pointer, 'lens' a magnifier centred on it."""
    if kind == "lens":
        img, x, y = P.lens_on_stick(hx, hy, tx, ty, r)
    else:
        img, x, y = P.stick(hx, hy, tx, ty)
    tl.put("held", img, x, y, z=32, screen=True)
    return tl


# --- text ------------------------------------------------------------------------------------------
def T(s, color="ink", size=20, maxw=None, align="left"):
    return ui.say(s, color, size, maxw=maxw, align=align)


def cx(img, x0=0, x1=W):
    """x that centres img between x0 and x1."""
    return (x0 + x1 - img.width) // 2


def feet(img, gy=GY):
    """y that stands img on the ground line."""
    return gy - img.height


def floor(w=344):
    """The ground band characters stand on: a dithered ice line that fades out at both ends."""
    from pal import rgba
    img = blank(w, 6)
    for x in range(w):
        edge = min(x, w - 1 - x)
        for y in range(6):
            keep = (y == 0 and edge > 6) or (y == 0 and (x % 2 == 0)) or (y > 0 and (x + y) % 2 == 0 and edge > 12 + 6 * y)
            if y == 1 and edge > 10 and (x + y) % 2 == 0:
                keep = True
            if keep:
                img.putpixel((x, y), rgba("ice"))
    return img


def spot(tl, cx, cy, rx, ry):
    """Dim the lights for a section's opening, an ellipse of light left on the subject (removed on the next slide)."""
    from sprites.sets import spotlight
    tl.put("wall_spot", spotlight(cx, cy, rx, ry), 0, 0, z=1.5, screen=True)
    return tl


def put_ground(tl):
    tl.put("ground", ground(), 0, 0, z=0, screen=True)
    return tl


CUE_XY = (8, 194)


def cue(tl, s):
    """The orientation cue: a few of the speaker's keywords, white on ink with a yellow bar, always bottom left."""
    tl.put("cue", ui.cue(s), *CUE_XY, z=90, screen=True)
    return tl


def smooth(tl, id, s, x, y, color="ink", size=10, face="Medium", align="left", z=60, screen=True, spacing=1.3):
    """Smooth anti-aliased Avenir Next text (title and closing slides only), placed as a HI-x picture."""
    lo, hi = hitext(s, color, size, face, spacing, align)
    if align == "center":
        x = (W - lo.width) / 2
    tl.put(id, hi, x, y, z=z, screen=screen, scale=1 / HI)
    return lo


# --- charts ----------------------------------------------------------------------------------------
_CH = None
CHART_IDS = set()


def _charts():
    global _CH
    if _CH is None:
        _CH = charts.render()
        for items in _CH.values():
            CHART_IDS.update("ch_" + i for i in items)
    return _CH


def chart_pos(slide, i, dx=0):
    """(x, y, w, h) in native pixels of chart element i on a chart state, its board shifted by dx."""
    img, x, y = _charts()[slide][i]
    return x * charts.SCALE + dx, y * charts.SCALE, img.width * charts.SCALE, img.height * charts.SCALE


def chart_mid(slide, i, dx=0):
    x, y, w, h = chart_pos(slide, i, dx)
    return round(x + w / 2), round(y + h / 2)


def put_stand(tl, slide, z=16, dx=0, bench_extra=0):
    """The stand of the board the chart is drawn on (legs, monitor stand or lab bench), down to the ground line.
    bench_extra lengthens the lab bench to the right, for things standing on it."""
    style, x0, w, yb = charts.stand_of(slide)
    x0, w, yb = round(x0 + dx), round(w), round(yb)
    if yb >= GY - 2:                    # a board that reaches the ground stands on it
        tl.drop("stand")
        return tl
    if style == "paper":
        tl.put("stand", P.stand(w, GY - yb), x0, yb, z=z, screen=True)
    elif style == "term":
        tl.put("stand", P.monitor(w, GY - yb - 1), x0, yb + 1, z=z, screen=True)
    elif style == "bench":
        b = P.bench(w + 24 + bench_extra, GY - yb - 2)
        tl.put("stand", b, x0 - 18, yb + 2 - 18, z=z, screen=True)
    else:
        tl.put("stand", P.table(w, GY - yb - 1), x0, yb + 1, z=z, screen=True)
    return tl


def chart(tl, slide, z=20, alias=None, dx=0, bench_extra=0):
    """Place every element of a chart state (960 grid, scale 0.4) on its board and stand, and drop the chart
    elements of other states. alias maps a chart element id to a stage id, so it can Morph from or into a picture
    of another scene."""
    alias = alias or {}
    put_stand(tl, slide, dx=dx, bench_extra=bench_extra)
    items = _charts()[slide]
    CHART_IDS.update(alias.values())
    keep = {alias.get(i, "ch_" + i) for i in items}
    for oid in [o for o in tl.objs if o in CHART_IDS]:
        if oid not in keep:
            tl.drop(oid)
    for k, (i, (img, x, y)) in enumerate(items.items()):
        zz = (z - 5 if i in charts.PANELS else z - 4 if i in charts.GRIDS else z - 3 if i in charts.PLATES
              else z + k / 1000)   # board, gridlines, plates, then the rest in HTML order (later on top)
        tl.put(alias.get(i, "ch_" + i), img, x * charts.SCALE + dx, y * charts.SCALE, z=zz, screen=True, scale=charts.SCALE)
    return tl


def clear_charts(tl):
    for oid in [o for o in tl.objs if o in CHART_IDS]:
        tl.drop(oid)
    tl.drop("stand")
    return tl
