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
BACKDROPS = {"ground", "floor"}
BACKDROP_PREFIX = ("win_", "slot", "frame", "map", "wall", "panel", "card_", "c_")


# --- the cast --------------------------------------------------------------------------------------
RB_W, RB_H, RB_CX = 112, 86, 50      # the big robot's canvas and the x of its body's centre in it


def robot(face="neutral", arms=("down", "down"), acc=(), grey=False, ant="red", hat=None, tint=None):
    """The model under test, drawn big (112x86 canvas, body centred at x 50, feet on the last row)."""
    return spr("robot.big", _w=RB_W, _h=RB_H, face=face, arms=tuple(arms), acc=tuple(acc), grey=grey,
               ant=ant, hat=hat, tint=tint)


def bot(face="neutral", arms=("down", "down"), acc=(), flip=False):
    """The same robot at 1x (58x50 canvas, feet on the last row): the persistent corner character of chart scenes.
    flip=True turns it to face left (pointing at the board)."""
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


# --- chart scenes: the board at the left, the big robot (the model under test) standing beside it ---------------
CHART_RX = 330                      # x of the big robot's body centre in chart scenes
CHART_ROBOT = (at(CHART_RX), ROBOT_Y)
POINT = ("out", "down")             # the left arm held out towards the board


def stage(tl, face="neutral", arms=("down", "down"), acc=(), robot_on=True):
    """The model under test at 2x, standing on the ground line beside the chart board, reacting. The scale is
    not part of chart scenes."""
    tl.drop("scale")
    if robot_on:
        tl.put("robot", robot(face, arms, acc), *CHART_ROBOT, z=30, screen=True)
        tl.put("cfloor", floor(100), CHART_RX - 50, GY, z=2, screen=True)
    else:
        tl.drop("robot", "cfloor")
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


def chart_pos(slide, i):
    """(x, y, w, h) in native pixels of chart element i on a chart state."""
    img, x, y = _charts()[slide][i]
    return x * charts.SCALE, y * charts.SCALE, img.width * charts.SCALE, img.height * charts.SCALE


def put_stand(tl, slide, z=16):
    """The stand of the board the chart is drawn on (legs, monitor stand, lab bench or map table), down to the
    ground line."""
    style, x0, w, yb = charts.stand_of(slide)
    x0, w, yb = round(x0), round(w), round(yb)
    if style == "paper":
        tl.put("stand", P.stand(w, GY - yb), x0, yb, z=z, screen=True)
    elif style == "term":
        tl.put("stand", P.monitor(w, GY - yb - 1), x0, yb + 1, z=z, screen=True)
    elif style == "bench":
        b = P.bench(w + 24, GY - yb - 2)
        tl.put("stand", b, x0 - 18, yb + 2 - 18, z=z, screen=True)
    else:
        tl.put("stand", P.table(w, GY - yb - 1), x0, yb + 1, z=z, screen=True)
    return tl


def chart(tl, slide, z=20, alias=None):
    """Place every element of a chart state (960 grid, scale 0.4) on its board and stand, and drop the chart
    elements of other states. alias maps a chart element id to a stage id, so it can Morph from or into a picture
    of another scene."""
    alias = alias or {}
    put_stand(tl, slide)
    items = _charts()[slide]
    CHART_IDS.update(alias.values())
    keep = {alias.get(i, "ch_" + i) for i in items}
    for oid in [o for o in tl.objs if o in CHART_IDS]:
        if oid not in keep:
            tl.drop(oid)
    for k, (i, (img, x, y)) in enumerate(items.items()):
        zz = (z - 5 if i in charts.PANELS else z - 4 if i in charts.GRIDS else z - 3 if i in charts.PLATES
              else z + k / 1000)   # board, gridlines, plates, then the rest in HTML order (later on top)
        tl.put(alias.get(i, "ch_" + i), img, x * charts.SCALE, y * charts.SCALE, z=zz, screen=True, scale=charts.SCALE)
    return tl


def clear_charts(tl):
    for oid in [o for o in tl.objs if o in CHART_IDS]:
        tl.drop(oid)
    tl.drop("stand")
    return tl
