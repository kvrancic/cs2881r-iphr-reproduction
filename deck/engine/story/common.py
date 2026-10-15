"""Shared helpers for the storyboard: sprite shortcuts with their contract sizes, text, and placement."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reg import spr
from px import W, H, blank, paste
from ground import ground
from sprites import deckui as ui

GY = 184          # ground line: feet stand on it

# --- sprites (sizes are the contract each sprite module draws to) ---------------------------------
def patient(state="normal", hold=None):
    return spr("people.patient", _w=32, _h=56, state=state, hold=hold)


def founder(who, pose="stand"):
    return spr("people.founder", _w=32, _h=56, who=who, pose=pose)


def portrait(who, lit=True):
    return spr("people.portrait", _w=56, _h=56, who=who, lit=lit)


def tumor(mood="grumpy"):
    return spr("cells.tumor", _w=16 if mood == "tiny" else 44, _h=14 if mood == "tiny" else 40, mood=mood)


def tcell(pose="stand"):
    return spr("cells.tcell", _w=22, _h=24, pose=pose)


def mac(mood="idle", color="sky"):
    return spr("cells.macrophage", _w=40, _h=44, mood=mood, color=color)


def fib(pose="idle"):
    return spr("cells.fibroblast", _w=36, _h=24, pose=pose)


def castle(name, **kw):
    sizes = {"castle": (120, 100), "hill": (220, 30), "wall": (172, 44), "iv_stand": (34, 100), "drip": (6, 12),
             "alarm_clock": (26, 26), "syringe": (70, 22), "ball_chain": (30, 12), "chain_bits": (18, 10),
             "magnifier": (72, 86), "stopwatch": (22, 26), "gold_sack": (18, 18), "stars": (16, 10), "zzz": (16, 16),
             "money_bag": (34, 36)}
    if name == "coins":
        w, h = {1: (26, 12), 2: (44, 24), 3: (70, 42), 4: (120, 64)}[kw.get("size", 1)]
    else:
        w, h = sizes[name]
    return spr("castle." + name, _w=w, _h=h, **kw)


def thing(name, **kw):
    sizes = {"file_icon": (64, 80), "petri_dish": (170, 40), "finger": (48, 30), "pill_bottle": (20, 28),
             "shelf": (220, 110), "claw": (36, 70), "cliff": (200, 96), "calendar": (40, 44), "cash_register": (60, 50),
             "door": (54, 86), "switch_emblem": (16, 16), "crate": (44, 34), "big_question": (26, 38),
             "for_rent_tag": (46, 26), "terminal": (90, 70)}
    w, h = sizes[name]
    return spr("things." + name, _w=w, _h=h, **kw)


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
    img = blank(w, 6)
    from pal import rgba
    for x in range(w):
        edge = min(x, w - 1 - x)
        for y in range(6):
            keep = (y == 0 and edge > 6) or (y == 0 and (x % 2 == 0)) or (y > 0 and (x + y) % 2 == 0 and edge > 12 + 6 * y)
            if y == 1 and edge > 10 and (x + y) % 2 == 0:
                keep = True
            if keep:
                img.putpixel((x, y), rgba("ice" if y < 2 else "ice"))
    return img


def put_ground(tl):
    tl.put("ground", ground(), 0, 0, z=0, screen=True)
    return tl
