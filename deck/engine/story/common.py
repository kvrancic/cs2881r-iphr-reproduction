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


def robot(face="neutral", arms=("down", "down"), acc=(), grey=False):
    """The model under test, drawn big (112x86 canvas, body centred at x 50, feet on the last row)."""
    return spr("robot.big", _w=RB_W, _h=RB_H, face=face, arms=tuple(arms), acc=tuple(acc), grey=grey)


def at(cx_):
    """x that centres the robot's body on cx_."""
    return cx_ - RB_CX


ROBOT_Y = GY - RB_H


def judge(face="focus"):
    """Our labeller: the robot with a judge's cap and a rubber stamp held out."""
    return robot(face, ("down", "out"), ("stamp", "judge"))


def scale(tilt=0, grey=False):
    return spr("props.scale", _w=86, _h=72, tilt=tilt, grey=grey)


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


def cue(tl, s, x=8, y=8, align="left"):
    """The orientation cue: a few of the speaker's keywords, white on ink with a yellow bar, in screen space."""
    c = ui.cue(s)
    if align == "right":
        x = W - x - c.width
    elif align == "center":
        x = (W - c.width) // 2
    tl.put("cue", c, x, y, z=90, screen=True)
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


def chart(tl, slide, z=20):
    """Place every element of a chart state (960 grid, scale 0.4) and drop chart elements of other states."""
    global _CH
    if _CH is None:
        _CH = charts.render()
        for items in _CH.values():
            CHART_IDS.update("ch_" + i for i in items)
    items = _CH[slide]
    for oid in [o for o in tl.objs if o in CHART_IDS]:
        if oid[3:] not in items:
            tl.drop(oid)
    for k, (i, (img, x, y)) in enumerate(items.items()):
        zz = z - 5 if i in charts.PANELS else z + k / 1000   # HTML order: later elements on top
        tl.put("ch_" + i, img, x * charts.SCALE, y * charts.SCALE, z=zz, screen=True, scale=charts.SCALE)
    return tl


def clear_charts(tl):
    for oid in [o for o in tl.objs if o in CHART_IDS]:
        tl.drop(oid)
    return tl
