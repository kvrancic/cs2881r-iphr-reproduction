"""The model under test: a toddler-sized box robot whose face is a small CRT screen (ported from the ACAP
Seattle keynote). Its face carries the mood; accessories add the judge's stamp, a weighted coin and a zipped mouth."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from px import ascii_sprite, blank, paste, flip
from pal import rgba

KEY = {"K": "ink", "W": "white", "L": "ice", "M": "steel", "D": "slate", "S": "night", "n": "dusk",
       "R": "red", "r": "wine", "Y": "yellow", "c": "cyan", "b": "sky", "P": "rose", "G": "green", "O": "orange"}

BODY = """
...........KKKK...........
..........KRWRRK..........
..........KRRRrK..........
...........KrrK...........
............KK............
............MD............
...KKKKKKKKKKKKKKKKKKKK...
..KWWWWWWWWWWWWWWWWWWWLK..
..KWKKKKKKKKKKKKKKKKKKMK..
..KWKnnSSSSSSSSSSSSSSKMK..
..KWKnSSSSSSSSSSSSSSSKMK..
..KWKSSSSSSSSSSSSSSSSKMK..
.KKWKSSSSSSSSSSSSSSSSKMKK.
KDKWKSSSSSSSSSSSSSSSSKMKDK
KDKWKSSSSSSSSSSSSSSSSKMKDK
.KKWKSSSSSSSSSSSSSSSSKMKK.
..KWKSSSSSSSSSSSSSSSSKMK..
..KWKSSSSSSSSSSSSSSSSKMK..
..KWKSSSSSSSSSSSSSSSSKMK..
..KWKKKKKKKKKKKKKKKKKKMK..
..KLLLLLLLLLLLLLLLLLLLMK..
...KKKKKKKKKKKKKKKKKKKK...
..........KDDDDK..........
......KKKKKKKKKKKKKK......
......KWWWWWWWWWWLMK......
......KWWKKKKKKKWLMK......
......KWWKcSRSSKWLMK......
......KWWKSSSYSKWLMK......
......KWWKKKKKKKWLMK......
......KLLLLLLLLLLLMK......
......KMMMMMMMMMMMDK......
......KKKKKKKKKKKKKK......
........KMK....KMK........
........KMK....KMK........
.......KDDDK..KDDDK.......
.......KKKKK..KKKKK.......
"""
SCREEN = (5, 9)        # top-left of the 16x10 screen inside BODY
SCREEN_WH = (16, 10)

ARM_DOWN = """
.KK.
KLMK
KLMK
KLMK
KDDK
KLMK
KWLK
KLMK
.KK.
"""
ARM_UP = """
.KK.
KLMK
KWLK
.KK.
KLMK
KDDK
KLMK
KLMK
KLMK
"""
ARM_OUT = """
.KKKKKKK.
KLLLDLLWK
KMMMDMMLK
.KKKKKKK.
"""

FACES = {
"neutral": """
................
................
...cc......cc...
...cc......cc...
...cc......cc...
................
................
......cccc......
................
................
""",
"happy": """
................
................
...cc......cc...
..c..c....c..c..
................
................
.....c....c.....
......cccc......
................
................
""",
"smug": """
................
................
..cccc....cccc..
....cc......cc..
................
................
..........c.....
.....ccccc......
................
................
""",
"scheme": """
................
..c..........c..
...cc......cc...
................
..cccc....cccc..
................
....cccccccc....
....c.c.c.c.c...
.....ccccccc....
................
""",
"shock": """
................
..cccc....cccc..
..c..c....c..c..
..c..c....c..c..
..cccc....cccc..
................
.......cc.......
......c..c......
.......cc.......
................
""",
"sad": """
................
................
..c..........c..
...cc......cc...
...cc......cc...
................
......cccc......
.....c....c.....
................
................
""",
"side": """
................
................
.....cc......cc.
.....cc......cc.
.....cc......cc.
................
................
.......cccc.....
................
................
""",
"closed": """
................
................
................
..cccc....cccc..
................
................
.....c....c.....
......cccc......
................
................
""",
"hearts": """
................
..PP.PP..PP.PP..
..PPPPP..PPPPP..
...PPP....PPP...
....P......P....
................
.....c....c.....
......cccc......
................
................
""",
"error": """
................
..c..c....c..c..
...cc......cc...
...cc......cc...
..c..c....c..c..
................
................
.....cccccc.....
................
................
""",
"question": """
......cccc......
.....c....c.....
..........c.....
.........c......
........c.......
........c.......
................
........c.......
................
................
""",
"dice": """
.WWWWWW..WWWWWW.
.WKWWWW..WKWWKW.
.WWWWWW..WWWWWW.
.WWWWKW..WWKWWW.
.WWWWWW..WWWWWW.
.........WKWWKW.
.........WWWWWW.
................
................
................
""",
"stars": """
................
...Y........Y...
..YYY......YYY..
...Y........Y...
................
................
.....c....c.....
......cccc......
................
................
""",
"sleep": """
................
................
................
..cccc....cccc..
................
................
.......cc.......
................
................
................
""",
"blank": """
................
................
................
................
................
................
................
................
................
................
""",
"focus": """
................
................
..cccc....cccc..
..cccc....cccc..
................
................
................
.......ccc......
................
................
""",
"globe": """
.....bbbbbb.....
...bbGGbbbbbb...
..bbGGGGbbGGbb..
..bGGGGbbbGGGb..
..bbGGbbbbbGbb..
..bbbbbbbGGbbb..
...bbbbbGGGbb...
.....bbbbbbb....
................
................
""",
"grin": """
................
................
...cc......cc...
..c..c....c..c..
................
....cccccccc....
....cWWWWWWc....
.....cccccc.....
................
................
""",
"dots": """
................
................
...cc......cc...
...cc......cc...
................
................
................
....c..c..c.....
................
................
""",
"calm": """
................
................
................
..cccc....cccc..
................
................
......cccc......
................
................
................
""",
}



BACK = """
...........KKKK...........
..........KRWRRK..........
..........KRRRrK..........
...........KrrK...........
............KK............
............MD............
...KKKKKKKKKKKKKKKKKKKK...
..KWWWWWWWWWWWWWWWWWWWLK..
..KWLLLLLLLLLLLLLLLLLLMK..
..KWLMMMMMMMMMMMMMMMMLMK..
..KWLMDDDDDDDDDDDDDDMLMK..
..KWLMMMMMMMMMMMMMMMMLMK..
.KKWLMDDDDDDDDDDDDDDMLMKK.
KDKWLMMMMMMMMMMMMMMMMLMKDK
KDKWLMDDDDDDDDDDDDDDMLMKDK
.KKWLMMMMMMMMMMMMMMMMLMKK.
..KWLLLLLLLLLLLLLLLLLLMK..
..KWLDLLLLLLLLLLLLLLDLMK..
..KWLLLLLLLLLLLLLLLLLLMK..
..KWLLLLLLLLLLLLLLLLLLMK..
..KLLLLLLLLLLLLLLLLLLLMK..
...KKKKKKKKKKKKKKKKKKKK...
..........KDDDDK..........
......KKKKKKKKKKKKKK......
......KWWWWWWWWWWLMK......
......KWLLLLLLLLLLMK......
......KWLKKKKKKKLLMK......
......KWLKYYYYGKLLMK......
......KWLKKKKKKKLLMK......
......KLLLLLLLLLLLMK......
......KMMMMMMMMMMMDK......
......KKKKKKKKKKKKKK......
........KMK....KMK........
........KMK....KMK........
.......KDDDK..KDDDK.......
.......KKKKK..KKKKK.......
"""


def face_img(name):
    return ascii_sprite(FACES[name].strip("\n").split("\n"), KEY)


CW, CH = 58, 50          # fixed canvas so accessories never change the robot's footprint
OX, OY = 16, 14          # body origin inside the canvas (feet land on the last row)


def _P(img, x, y, col, a=255):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), rgba(col, a))


def _R(img, x, y, w, h, col, a=255):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            _P(img, xx, yy, col, a)


def _box(img, x, y, w, h, fill, edge="ink"):
    _R(img, x, y, w, h, edge); _R(img, x + 1, y + 1, w - 2, h - 2, fill)


def _ln(img, x0, y0, x1, y1, col):
    from px import line
    line(img, x0, y0, x1, y1, col)


def _shapes():
    return {"down": ARM_DOWN, "up": ARM_UP, "out": ARM_OUT}


def robot(face="neutral", arms=("down", "down"), acc=(), view="front", glow=True):
    acc = set(acc or ())
    img = blank(CW, CH)
    ox, oy = OX, OY
    if "sit" in acc or "kneel" in acc:
        oy += 4
    # things behind the body
    if "swagbag" in acc:
        _box(img, ox + 18, oy + 22, 12, 12, "brown"); _R(img, ox + 21, oy + 20, 6, 3, "clay")
        _R(img, ox + 22, oy + 26, 4, 4, "yellow"); _P(img, ox + 23, oy + 27, "ink"); _P(img, ox + 24, oy + 27, "ink")
    if "halo" in acc:
        for dx in range(-6, 7):
            _P(img, ox + 13 + dx, oy - 3 if abs(dx) < 5 else oy - 2, "yellow")
            _P(img, ox + 13 + dx, oy - 1 if abs(dx) < 5 else oy - 2, "gold")
    body_src = BODY if view == "front" else BACK
    rows = body_src.strip("\n").split("\n")
    if "sit" in acc or "kneel" in acc:
        rows = rows[:32]
    body = ascii_sprite(rows, KEY)
    paste(img, body, ox, oy)
    if view == "front":
        sx, sy = ox + SCREEN[0], oy + SCREEN[1]
        p = img.load()
        if glow:
            for y in range(sy, sy + SCREEN_WH[1]):
                if (y - sy) % 2 == 1:
                    for x in range(sx, sx + SCREEN_WH[0]):
                        if p[x, y][:3] == rgba("night")[:3]:
                            p[x, y] = rgba("ink")
        if "hood_open" in acc:
            _R(img, sx, sy, 16, 10, "ink")
            for gx, gy in ((sx + 4, sy + 4), (sx + 11, sy + 5)):
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if abs(dx) + abs(dy) <= 3:
                            _P(img, gx + dx, gy + dy, "gold" if (dx + dy) % 2 else "orange")
                _P(img, gx, gy, "ink")
            _box(img, sx - 1, sy - 12, 18, 11, "night", "ink")
            _R(img, sx + 1, sy - 10, 6, 1, "dusk")
        else:
            paste(img, face_img(face), sx, sy)
        if "sunglasses" in acc:
            _R(img, sx + 1, sy + 2, 14, 1, "ink")
            _R(img, sx + 2, sy + 3, 5, 3, "ink"); _R(img, sx + 9, sy + 3, 5, 3, "ink")
            _P(img, sx + 3, sy + 3, "dusk"); _P(img, sx + 10, sy + 3, "dusk")
        if "teacher_glasses" in acc:
            for gx in (sx + 2, sx + 9):
                _R(img, gx, sy + 1, 5, 1, "gold"); _R(img, gx, sy + 5, 5, 1, "gold")
                _R(img, gx, sy + 1, 1, 5, "gold"); _R(img, gx + 4, sy + 1, 1, 5, "gold")
            _R(img, sx + 7, sy + 2, 2, 1, "gold")
        if "burglar" in acc:
            _R(img, sx, sy + 1, 16, 5, "ink")
            for gx in (sx + 3, sx + 10):
                _R(img, gx, sy + 2, 3, 3, "night"); _P(img, gx + 1, sy + 3, "cyan")
            _P(img, sx - 1, sy + 3, "ink"); _P(img, sx - 2, sy + 4, "ink"); _P(img, sx + 16, sy + 3, "ink")
        if "pacifier" in acc:
            _R(img, sx + 6, sy + 6, 4, 3, "rose"); _R(img, sx + 7, sy + 7, 2, 1, "pink"); _P(img, sx + 5, sy + 7, "rose"); _P(img, sx + 10, sy + 7, "rose")
        if "drawer_head" in acc:
            _box(img, sx - 2, sy + 2, 20, 8, "steel"); _R(img, sx + 6, sy + 5, 4, 1, "ink")
            for i in range(5):
                _R(img, sx + 0 + i * 3, sy - 1, 2, 4, ("sand", "white", "sand", "ice", "white")[i]); _P(img, sx + i * 3, sy - 1, "ink")
    # head-top accessories
    hx, hy = ox, oy + 6
    if "beret" in acc:
        _R(img, hx + 5, hy - 4, 16, 4, "ink"); _R(img, hx + 6, hy - 3, 14, 2, "red"); _R(img, hx + 8, hy - 5, 10, 2, "ink")
        _R(img, hx + 9, hy - 4, 8, 1, "red"); _P(img, hx + 13, hy - 6, "ink"); _P(img, hx + 13, hy - 7, "ink")
    if "bonnet" in acc:
        for x in range(hx + 1, hx + 25):
            _P(img, x, hy - 1, "white" if x % 2 else "rose")
        _R(img, hx + 3, hy - 4, 20, 3, "ink"); _R(img, hx + 4, hy - 3, 18, 2, "rose")
        _R(img, hx + 1, hy, 2, 10, "white"); _R(img, hx + 23, hy, 2, 10, "white")
        _P(img, hx + 1, hy + 10, "rose"); _P(img, hx + 24, hy + 10, "rose")
    if "books_on_head" in acc:
        for i, c in enumerate(("red", "sky", "green")):
            _box(img, hx + 4 + i, hy - 4 - i * 3, 17 - i * 2, 4, c)
    if "headset" in acc:
        for x in range(hx + 2, hx + 24):
            _P(img, x, hy - 2, "ink")
        _R(img, hx, hy + 5, 3, 6, "ink"); _R(img, hx + 23, hy + 5, 3, 6, "ink")
        _ln(img, hx + 1, hy + 11, hx + 7, hy + 15, "ink"); _P(img, hx + 8, hy + 15, "red")
    if "cobweb" in acc:
        for i in range(6):
            _ln(img, hx + 22, hy - 6, hx + 22 + (i % 3) * 3, hy + 2 + i, "ice")
        _ln(img, hx + 18, hy - 6, hx + 25, hy + 6, "ice"); _ln(img, hx + 20, hy - 7, hx + 26, hy, "steel")
        for i in range(10):
            _P(img, ox + 2 + i * 2, oy + 30 + (i % 2), "steel", 160)
    if "sweat" in acc:
        _P(img, hx + 26, hy + 1, "cyan"); _R(img, hx + 25, hy + 2, 3, 2, "cyan"); _P(img, hx + 26, hy + 4, "sky")
    # arms
    shapes = _shapes()
    held = None
    if "shrug" in acc:
        arms = ("out", "out")
    if any(a in acc for a in ("dumbbell", "signs")):
        arms = ("up", "up")
    for side, kind in zip(("L", "R"), arms):
        if not kind or ("sit" in acc and kind == "down" and False):
            continue
        a = ascii_sprite(shapes[kind].strip("\n").split("\n"), KEY)
        if side == "R":
            a = flip(a)
        if kind == "down":
            x = ox + (3 if side == "L" else 19); y = oy + 23
        elif kind == "up":
            x = ox + (3 if side == "L" else 19); y = oy + 15
        else:
            x = ox - 3 if side == "L" else ox + 19; y = oy + 24
        if view == "front" or True:
            paste(img, a, x, y)
    rhx, rhy = ox + 21, oy + 31        # right hand (arm down)
    if arms[1] == "out":
        rhx, rhy = ox + 27, oy + 25
    if arms[1] == "up":
        rhx, rhy = ox + 21, oy + 14
    lhx, lhy = ox + 4, oy + 31
    if arms[0] == "up":
        lhx, lhy = ox + 4, oy + 14
    # held props
    if "mic" in acc:
        _R(img, rhx, rhy - 6, 2, 7, "ink"); _R(img, rhx + 1, rhy - 6, 1, 6, "slate")
        _box(img, rhx - 2, rhy - 11, 6, 6, "steel"); _R(img, rhx - 1, rhy - 10, 2, 2, "white"); _P(img, rhx + 2, rhy - 8, "slate")
    if "signs" in acc:
        for (hx2, col, up) in ((lhx - 2, "green", True), (rhx - 2, "red", False)):
            _ln(img, hx2 + 2, rhy, hx2 + 2, rhy - 8, "brown")
            _box(img, hx2 - 3, rhy - 17, 11, 10, col)
            if up:
                for i in range(3):
                    _R(img, hx2 + 2 - i, rhy - 14 + i, 1 + 2 * i, 1, "white")
            else:
                for i in range(3):
                    _R(img, hx2 + 2 - i, rhy - 10 - i, 1 + 2 * i, 1, "white")
    if "magnifier" in acc:
        _ln(img, rhx, rhy, rhx + 4, rhy - 4, "brown")
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                d = dx * dx + dy * dy
                if 9 <= d <= 18:
                    _P(img, rhx + 7 + dx, rhy - 7 + dy, "gold")
                elif d < 9:
                    _P(img, rhx + 7 + dx, rhy - 7 + dy, "cyan", 140)
    if "pointer" in acc:
        _ln(img, rhx, rhy, rhx + 9, rhy - 12, "brown"); _P(img, rhx + 9, rhy - 12, "white")
    if "broom" in acc:
        _ln(img, lhx + 2, lhy - 12, rhx + 6, rhy + 6, "brown")
        for i in range(6):
            _ln(img, rhx + 4 + i, rhy + 5, rhx + 2 + i * 2, rhy + 12, "gold")
    if "pinch_nose" in acc:
        _R(img, ox + 11, oy + 15, 4, 3, "ice"); _box(img, ox + 10, oy + 14, 6, 5, "ice")
    if "dumbbell" in acc:
        by = oy + 12
        _R(img, lhx - 3, by, rhx - lhx + 8, 2, "steel"); _R(img, lhx - 3, by, rhx - lhx + 8, 1, "ice")
        for bx in (lhx - 7, rhx + 3):
            _box(img, bx, by - 4, 5, 10, "slate"); _R(img, bx + 1, by - 3, 1, 8, "steel")
        _R(img, ox + 9, by, 8, 2, "yellow")
    if "fan" in acc:
        for i in range(5):
            _ln(img, rhx, rhy, rhx + 6 - i * 2, rhy - 7, "rose" if i % 2 else "white")
    if "rose" in acc:
        _ln(img, rhx, rhy, rhx + 5, rhy - 6, "leaf"); _R(img, rhx + 4, rhy - 9, 4, 3, "red"); _P(img, rhx + 5, rhy - 10, "wine")
    if "flashlight" in acc:
        _R(img, rhx, rhy - 2, 5, 3, "ink")
        for i in range(10):
            _R(img, rhx + 5 + i, rhy - 2 - i // 2, 1, 3 + i, "yellow", 90)
    if "toolbelt" in acc:
        _R(img, ox + 6, oy + 29, 14, 2, "brown"); _P(img, ox + 12, oy + 29, "gold")
        _R(img, ox + 6, oy + 31, 3, 3, "slate"); _R(img, ox + 16, oy + 31, 3, 3, "green")
    if "brush" in acc:
        _ln(img, rhx, rhy, rhx + 5, rhy - 7, "brown"); _R(img, rhx + 5, rhy - 9, 2, 2, "red")
    if "mouse" in acc:
        _box(img, rhx - 1, rhy - 1, 5, 6, "white"); _P(img, rhx + 1, rhy, "ink")
    if "book" in acc:
        _box(img, ox + 5, oy + 23, 16, 9, "white"); _R(img, ox + 12, oy + 23, 1, 9, "ink")
        for y in (25, 27, 29):
            _R(img, ox + 7, oy + y, 4, 1, "steel"); _R(img, ox + 14, oy + y, 5, 1, "steel")
    if "coffee" in acc:
        _box(img, rhx - 1, rhy - 5, 5, 6, "white"); _R(img, rhx, rhy - 4, 3, 1, "brown"); _P(img, rhx + 4, rhy - 3, "white")
        _P(img, rhx + 1, rhy - 7, "ice"); _P(img, rhx + 2, rhy - 9, "ice")
    if "chained" in acc:
        cy0 = oy + (34 if "sit" not in acc else 30)
        for i in range(9):
            _box(img, ox - 8 + i * 4, cy0 + (i % 2), 5, 3, "ice" if i % 2 else "steel")
        _box(img, ox - 12, cy0 - 2, 6, 6, "slate"); _P(img, ox - 10, cy0, "ink")
        _box(img, ox + 9, oy + 21, 9, 3, "steel")
    if "kneel" in acc:
        _R(img, ox + 8, oy + 32, 10, 2, "ink"); _R(img, ox + 8, oy + 30, 3, 3, "slate")
    if "sit" in acc:
        _R(img, ox + 6, oy + 32, 14, 2, "ink"); _R(img, ox + 20, oy + 30, 4, 4, "slate"); _R(img, ox + 2, oy + 30, 4, 4, "slate")
    if "fan" in acc or "sweat" in acc:
        pass
    if "bowtie" in acc:
        bx, by = ox + 9, oy + 21
        _R(img, bx, by, 3, 3, "red"); _R(img, bx + 4, by, 3, 3, "red"); _R(img, bx + 3, by + 1, 1, 1, "wine")
        _P(img, bx, by, "wine"); _P(img, bx + 6, by + 2, "wine")
    if "stamp" in acc:          # the judge's rubber stamp, held out in the right hand (arms=("down", "out"))
        sx0, sy0 = rhx + 3, rhy - 12
        _box(img, sx0, sy0, 6, 5, "clay"); _R(img, sx0 + 1, sy0 + 1, 3, 1, "peach")
        _R(img, sx0 + 2, sy0 + 5, 2, 4, "brown"); _P(img, sx0 + 2, sy0 + 5, "ink")
        _box(img, sx0 - 2, sy0 + 9, 10, 4, "ink"); _R(img, sx0 - 1, sy0 + 10, 8, 2, "red")
    if "judge" in acc:          # a gold band and a small ink cap on the head
        _R(img, ox + 3, oy + 6, 20, 1, "gold")
        _R(img, ox + 6, oy + 2, 14, 4, "ink"); _R(img, ox + 7, oy + 3, 12, 2, "night")
        _R(img, ox + 4, oy + 5, 18, 1, "ink"); _P(img, ox + 19, oy + 4, "gold"); _P(img, ox + 20, oy + 5, "gold")
    if "coin" in acc:           # a weighted coin held up in the right hand
        cxx, cyy = rhx + 4, rhy - 7
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                d = dx * dx + dy * dy
                if d <= 30:
                    _P(img, cxx + dx, cyy + dy, "ink")
                if d <= 20:
                    _P(img, cxx + dx, cyy + dy, "gold" if dx + dy > 2 else "yellow")
        _R(img, cxx - 1, cyy - 2, 3, 5, "orange"); _P(img, cxx - 3, cyy - 3, "white")
    if "zip" in acc and view == "front":   # the mouth zipped shut: a stitched line across the lower screen
        sx, sy = ox + SCREEN[0], oy + SCREEN[1]
        _R(img, sx + 2, sy + 7, 12, 1, "steel")
        for k in range(3, 14, 2):
            _P(img, sx + k, sy + 6, "steel"); _P(img, sx + k, sy + 8, "steel")
        _R(img, sx + 13, sy + 6, 2, 3, "gold")
    img.info["robot"] = dict(face=face, arms=tuple(arms), acc=tuple(sorted(acc)), view=view)
    return img


# ================================================================================================ the big robot
BCW, BCH = 112, 86       # canvas of the big robot; the body's origin is (BOX, 2) and the feet land on the last row
BOX = 18


def big(face="neutral", arms=("down", "down"), acc=(), grey=False):
    """The same robot drawn at twice the size (not upscaled: 1px outlines, more detail), for slides where the
    robot is the subject. The face is the CRT screen, so its glyphs are drawn as 2x2 screen dots."""
    acc = set(acc or ())
    img = blank(BCW, BCH)
    ox, oy = BOX, 2
    if "shrug" in acc:
        arms = ("out", "out")
    # antenna
    _R(img, ox + 30, oy + 6, 4, 6, "ink"); _R(img, ox + 31, oy + 6, 2, 6, "steel")
    _R(img, ox + 27, oy, 10, 7, "ink"); _R(img, ox + 28, oy + 1, 8, 5, "red"); _R(img, ox + 29, oy + 1, 3, 2, "white")
    _R(img, ox + 28, oy + 4, 8, 2, "wine")
    # head: bevelled case
    hx, hy, hw, hh = ox + 6, oy + 11, 52, 38
    _R(img, hx, hy, hw, hh, "ink")
    _R(img, hx + 1, hy + 1, hw - 2, hh - 2, "ice")
    _R(img, hx + 1, hy + 1, hw - 2, 2, "white"); _R(img, hx + 1, hy + 1, 2, hh - 2, "white")
    _R(img, hx + hw - 3, hy + 2, 2, hh - 3, "steel"); _R(img, hx + 2, hy + hh - 3, hw - 3, 2, "steel")
    # ear bolts
    for ex in (hx - 4, hx + hw):
        _R(img, ex, hy + 14, 4, 10, "ink"); _R(img, ex + 1, hy + 15, 2, 8, "slate"); _P(img, ex + 1, hy + 15, "steel")
    # screen
    sx, sy, sw, sh = hx + 5, hy + 5, 42, 28
    _R(img, sx, sy, sw, sh, "ink")
    _R(img, sx + 1, sy + 1, sw - 2, sh - 2, "night")
    _R(img, sx + 2, sy + 2, 6, 1, "dusk"); _R(img, sx + 2, sy + 2, 1, 4, "dusk")
    p = img.load()
    for y in range(sy + 1, sy + sh - 1):
        if (y - sy) % 2 == 0:
            for x in range(sx + 1, sx + sw - 1):
                if p[x, y][:3] == rgba("night")[:3]:
                    p[x, y] = rgba("ink")
    if True:
        f = face_img(face)
        f2 = f.resize((f.width * 2, f.height * 2))
        paste(img, f2, sx + 5, sy + 4)
    if "zip" in acc:
        zy = sy + 20
        _R(img, sx + 4, zy, 34, 2, "steel")
        for k in range(5, 37, 3):
            _R(img, sx + k, zy - 1, 1, 4, "ice")
        _R(img, sx + 36, zy - 2, 3, 6, "gold"); _P(img, sx + 37, zy - 1, "yellow")
    # neck
    _R(img, ox + 26, oy + 49, 12, 4, "ink"); _R(img, ox + 27, oy + 49, 10, 3, "slate")
    # torso
    tx, ty, tw, th = ox + 14, oy + 52, 36, 22
    _R(img, tx, ty, tw, th, "ink")
    _R(img, tx + 1, ty + 1, tw - 2, th - 2, "ice")
    _R(img, tx + 1, ty + 1, tw - 2, 2, "white"); _R(img, tx + 1, ty + 1, 2, th - 2, "white")
    _R(img, tx + tw - 3, ty + 2, 2, th - 3, "steel"); _R(img, tx + 2, ty + th - 3, tw - 3, 2, "steel")
    _R(img, tx + 8, ty + 6, 20, 10, "ink"); _R(img, tx + 9, ty + 7, 18, 8, "night")
    for k, c in enumerate(("cyan", "red", "yellow", "green")):
        _R(img, tx + 11 + k * 4, ty + 9, 2, 2, c)
    _R(img, tx + 11, ty + 12, 10, 1, "dusk")
    # legs and feet
    for lx in (tx + 7, tx + 22):
        _R(img, lx, ty + th, 7, 6, "ink"); _R(img, lx + 1, ty + th, 5, 6, "steel"); _R(img, lx + 1, ty + th, 2, 6, "ice")
        _R(img, lx - 2, ty + th + 6, 11, 4, "ink"); _R(img, lx - 1, ty + th + 6, 9, 2, "slate")
    # arms: down hangs beside the torso, up raises the hand above the shoulder, out points sideways
    rh = None
    for side, kind in zip(("L", "R"), arms):
        if side == "L":
            ax = tx - 7
        else:
            ax = tx + tw + 1
        if kind == "down":
            _R(img, ax, ty + 1, 6, 18, "ink"); _R(img, ax + 1, ty + 2, 4, 15, "ice"); _R(img, ax + 1, ty + 2, 1, 15, "white")
            _R(img, ax + 3, ty + 2, 1, 15, "steel")
            _R(img, ax - 1, ty + 17, 8, 5, "ink"); _R(img, ax, ty + 18, 6, 3, "slate")
            hand = (ax + 3, ty + 19)
        elif kind == "up":
            _R(img, ax, ty - 16, 6, 19, "ink"); _R(img, ax + 1, ty - 15, 4, 17, "ice"); _R(img, ax + 1, ty - 15, 1, 17, "white")
            _R(img, ax - 1, ty - 21, 8, 6, "ink"); _R(img, ax, ty - 20, 6, 4, "slate")
            hand = (ax + 3, ty - 19)
        else:
            dx = 1 if side == "R" else -1
            x0 = ax if side == "R" else ax - 12
            _R(img, x0, ty + 2, 18, 6, "ink"); _R(img, x0 + 1, ty + 3, 16, 4, "ice"); _R(img, x0 + 1, ty + 3, 16, 1, "white")
            hxx = x0 + 18 if side == "R" else x0 - 6
            _R(img, hxx, ty + 1, 6, 8, "ink"); _R(img, hxx + 1, ty + 2, 4, 6, "slate")
            hand = (hxx + 3, ty + 5)
        if side == "R":
            rh = hand
    hx2, hy2 = rh
    if "coin" in acc:
        cx_, cy_ = hx2 + 8, hy2 - 9
        for dx in range(-9, 10):
            for dy in range(-9, 10):
                d = dx * dx + dy * dy
                if d <= 90:
                    _P(img, cx_ + dx, cy_ + dy, "ink")
                if d <= 72:
                    _P(img, cx_ + dx, cy_ + dy, "gold" if dx + dy > 3 else "yellow")
                if 40 <= d <= 50 and dx + dy > 0:
                    _P(img, cx_ + dx, cy_ + dy, "orange")
        _R(img, cx_ - 1, cy_ - 4, 3, 9, "orange"); _R(img, cx_ - 4, cy_ - 1, 9, 3, "orange")
        _R(img, cx_ - 5, cy_ - 6, 2, 2, "white")
    if "stamp" in acc:
        s0, t0 = hx2 + 3, hy2 - 18
        _R(img, s0, t0, 10, 7, "ink"); _R(img, s0 + 1, t0 + 1, 8, 5, "clay"); _R(img, s0 + 1, t0 + 1, 8, 1, "peach")
        _R(img, s0 + 3, t0 + 7, 4, 7, "ink"); _R(img, s0 + 4, t0 + 7, 2, 7, "brown")
        _R(img, s0 - 3, t0 + 14, 16, 6, "ink"); _R(img, s0 - 2, t0 + 15, 14, 2, "slate"); _R(img, s0 - 2, t0 + 17, 14, 2, "red")
    if "judge" in acc:
        _R(img, hx + 4, hy - 7, 44, 8, "ink"); _R(img, hx + 5, hy - 6, 42, 6, "night"); _R(img, hx + 5, hy - 6, 42, 1, "dusk")
        _R(img, hx - 2, hy - 1, 56, 3, "ink"); _R(img, hx - 1, hy, 54, 1, "gold")
        _R(img, ox + 30, oy + 2, 4, 2, "gold")
    if grey:
        from px import recolor
        img = recolor(img, {"red": "steel", "wine": "slate", "cyan": "steel", "yellow": "ice", "green": "steel",
                            "white": "ice", "ice": "ice", "night": "slate", "ink": "steel", "gold": "ice",
                            "dusk": "steel", "slate": "steel", "clay": "steel", "peach": "ice", "brown": "slate"})
    return img
