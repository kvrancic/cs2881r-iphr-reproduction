"""Sprite registry. spr('module.func', _w=, _h=, _d='desc', **kw) calls sprites/module.py:func(**kw);
if it does not exist yet, returns a labeled placeholder of size _w x _h and records it in MANIFEST."""
import importlib, json, os
from functools import lru_cache
from PIL import ImageDraw
from px import blank, text, rect, frame
from pal import rgba

MANIFEST = {}
MISSING = set()


def _key(kw):
    return tuple(sorted((k, v if not isinstance(v, list) else tuple(v)) for k, v in kw.items()))


SEARCH = {}   # module aliases; every sprite module is named directly (people, cells, castle, things, deckui)
ERRORS = {}


@lru_cache(maxsize=4096)
def _call(name, kwt):
    kw = dict(kwt)
    mod, fn = name.split(".", 1)
    for m_name in SEARCH.get(mod, [mod]):
        try:
            m = importlib.import_module(f"sprites.{m_name}")
        except Exception as e:  # a half-written module must not break the others
            ERRORS[m_name] = repr(e)
            continue
        f = getattr(m, fn, None)
        if f is None:
            continue
        try:
            return f(**kw)
        except Exception as e:
            ERRORS[name] = repr(e)
            return None
    return None


def placeholder(name, w, h, kw):
    img = blank(w, h)
    rect(img, 0, 0, w, h, "dusk", 200)
    frame(img, 0, 0, w, h, "rose")
    label = name.split(".", 1)[1] + ("" if not kw else " " + ",".join(f"{v}" for _, v in sorted(kw.items()))[:30])
    t = text(label[:40], "white", 20, maxw=max(w - 4, 20))
    if t.width > w - 2 or t.height > h - 2:
        t = t.crop((0, 0, min(t.width, w - 2), min(t.height, h - 2)))
    img.alpha_composite(t, (1, 1))
    return img


def spr(name, _w=24, _h=24, _d="", **kw):
    ent = MANIFEST.setdefault(name, {"w": _w, "h": _h, "desc": _d, "variants": []})
    if _d and not ent["desc"]:
        ent["desc"] = _d
    v = {k: (list(x) if isinstance(x, tuple) else x) for k, x in kw.items()}
    if v and v not in ent["variants"]:
        ent["variants"].append(v)
    img = _call(name, _key(kw))
    if img is None:
        MISSING.add(name)
        return placeholder(name, _w, _h, kw)
    return img


def dump(path):
    with open(path, "w") as f:
        json.dump({"missing": sorted(MISSING), "manifest": MANIFEST}, f, indent=1)
