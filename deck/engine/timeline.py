"""A Timeline holds a mutable stage; beat() snapshots it as one slide."""
import copy
from dataclasses import dataclass, replace
from typing import Optional


@dataclass
class Obj:
    id: str
    img: object            # PIL RGBA
    x: float               # position in native 384x216 pixels (fractional allowed for fine-grid objects)
    y: float
    z: int = 5
    alpha: float = 1.0
    screen: bool = False   # True: ignores the camera
    scale: float = 1.0     # native pixels per image pixel: 1 for 384-grid art, 0.4 for 960-grid (HTML) art
    anim: tuple = ()       # (("frames", sprite, n, fps),) -> animated GIF in the deck

    @property
    def w(self):
        return self.img.width * self.scale

    @property
    def h(self):
        return self.img.height * self.scale


@dataclass
class Beat:
    say: str                 # the exact spoken words: the slide's speaker notes
    objs: dict
    cam: tuple
    bg: str
    morph: float = 0.6       # seconds for the transition into this slide
    section: str = ""
    notes: str = ""          # extra presenter notes
    video: Optional[str] = None   # key into videos.VIDEOS: this slide plays that video full screen
    fade: bool = False       # force a fade (instead of Morph) into this slide
    clip: Optional[int] = None   # with video: which clip of a narrated video this slide plays


class Timeline:
    def __init__(self):
        self.objs = {}
        self.camxy = (0, 0, 1.0)
        self.bgc = "white"
        self.beats = []
        self.section = ""

    # stage edits -------------------------------------------------------
    def put(self, id, img=None, x=None, y=None, z=None, **kw):
        o = self.objs.get(id)
        if o is None:
            o = Obj(id, img, x or 0, y or 0, z if z is not None else 5, **kw)
        else:
            o = replace(o, img=img if img is not None else o.img,
                        x=o.x if x is None else x, y=o.y if y is None else y,
                        z=o.z if z is None else z, **kw)
        self.objs[id] = o
        return self

    def move(self, id, x=None, y=None, dx=0, dy=0, **kw):
        o = self.objs[id]
        self.objs[id] = replace(o, x=(o.x if x is None else x) + dx, y=(o.y if y is None else y) + dy, **kw)
        return self

    def drop(self, *ids):
        for i in ids:
            self.objs.pop(i, None)
        return self

    def keep(self, *ids):
        for i in list(self.objs):
            if i not in ids:
                self.objs.pop(i)
        return self

    def clear(self):
        self.objs = {}
        self.camxy = (0, 0, 1.0)
        return self

    def cam(self, x=0, y=0, zoom=1.0):
        """Camera window top-left (x, y) in world pixels; zoom 2 shows a 192x108 window filling the screen."""
        self.camxy = (x, y, zoom)
        return self

    ZOOMS = (1.2, 1.6, 2.0, 2.4)   # 1920/z and 5*z are whole numbers: every native pixel stays a uniform block

    def focus(self, cx, cy, zoom=2.0):
        """Zoom so that world point (cx, cy) sits at the centre of the screen."""
        from px import W, H
        zoom = min(self.ZOOMS, key=lambda z: abs(z - zoom))
        x = min(max(cx - W / zoom / 2, 0), W - W / zoom)
        y = min(max(cy - H / zoom / 2, 0), H - H / zoom)
        self.camxy = (round(x * 5) / 5, round(y * 5) / 5, zoom)
        return self

    def bg(self, color):
        self.bgc = color
        return self

    # snapshot ------------------------------------------------------------
    def beat(self, say="", morph=0.6, notes="", video=None, fade=False, clip=None):
        objs = {k: copy.copy(v) for k, v in self.objs.items()}
        self.beats.append(Beat(say=say, objs=objs, cam=self.camxy, bg=self.bgc, morph=morph,
                               section=self.section, notes=notes, video=video, fade=fade, clip=clip))
        return self
