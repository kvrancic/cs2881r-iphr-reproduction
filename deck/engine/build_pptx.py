"""Beats -> .pptx. One slide per beat; every object is a picture named !!id so Morph matches it across slides.
Morph between slides, a fade into and out of the video slides. Video slides autoplay and advance when the video ends."""
import io, os, hashlib
from lxml import etree
from pptx import Presentation
from pptx.util import Emu
from pptx.dml.color import RGBColor
from PIL import Image
from pal import C
from render import placement
import videos

EMU = 31750            # one native pixel (384 across 13.333 in) is exactly 31750 EMU
K = 10                 # export scale for 384-grid art: 3840x2160 equivalent, so 1080p and 4K both get whole pixels
BUILD = os.path.join(videos.DECK, "build")

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

FADE = """<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"{adv}><p:fade/></p:transition>"""

MORPH = """<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
 xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">
 <mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">
  <p:transition spd="slow" p14:dur="{ms}"{adv}><p159:morph option="byObject"/></p:transition>
 </mc:Choice>
 <mc:Fallback><p:transition spd="fast"{adv}><p:fade/></p:transition></mc:Fallback>
</mc:AlternateContent>"""

# "Start: Automatically" for a video: the first main-sequence effect is an after-previous media call that
# begins with the slide, and the media node itself never waits for a click.
AUTOPLAY = """<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:tnLst><p:par>
<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>
 <p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>
  <p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst>
   <p:childTnLst><p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
    <p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="afterEffect">
     <p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
      <p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="{ms}" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>
     </p:childTnLst></p:cTn></p:par>
   </p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>
 </p:childTnLst></p:cTn>
 <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
 <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
 </p:seq>
 <p:video><p:cMediaNode vol="100000"><p:cTn id="7" fill="hold" display="0"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>
  <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>
</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>"""


def _png(img, f, cache={}):
    h = hashlib.sha1(img.tobytes() + bytes(f"{img.size}{f}", "ascii")).hexdigest()
    if h not in cache:
        big = img.resize((img.width * f, img.height * f), Image.NEAREST)
        b = io.BytesIO(); big.save(b, "PNG", optimize=True)
        cache[h] = b.getvalue()
    return io.BytesIO(cache[h])


def _gif(frames, fps, f, cache={}):
    """Animated GIF (palette, 1-bit transparency) for objects that loop in place."""
    key = tuple(hashlib.sha1(x.tobytes()).hexdigest() for x in frames) + (fps, f)
    if key not in cache:
        pal = []
        for fr in frames:
            q = fr.resize((fr.width * f, fr.height * f), Image.NEAREST).convert("RGBA")
            alpha = q.split()[3]
            p = q.convert("RGB").quantize(colors=63, method=Image.Quantize.MEDIANCUT)
            p.paste(63, mask=Image.eval(alpha, lambda a: 255 if a <= 128 else 0))
            pal.append(p)
        b = io.BytesIO()
        pal[0].save(b, "GIF", save_all=True, append_images=pal[1:], duration=int(1000 / fps), loop=0, transparency=63, disposal=2)
        cache[key] = b.getvalue()
    return io.BytesIO(cache[key])


def _set_alpha(pic, alpha):
    if alpha >= 0.999:
        return
    blip = pic._element.find(".//a:blip", NS)
    a = etree.SubElement(blip, "{%s}alphaModFix" % NS["a"])
    a.set("amt", str(int(alpha * 100000)))


def _notes(b, nxt):
    lines = [b.say] if b.say else []
    if b.notes:
        lines.append(b.notes)
    lines.append("NEXT: " + nxt)
    return "\n\n".join(lines)


def build(beats, out, title="3B Therapeutics"):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(384 * EMU), Emu(216 * EMU)
    layout = prs.slide_layouts[6]
    vids = videos.load()
    os.makedirs(BUILD, exist_ok=True)
    report = []
    for i, b in enumerate(beats):
        s = prs.slides.add_slide(layout)
        fill = s.background.fill; fill.solid(); fill.fore_color.rgb = RGBColor(*C[b.bg])
        v = vids.get(b.video) if b.video else None
        playing = v is not None and v["present"]
        for o in sorted(b.objs.values(), key=lambda o: o.z):
            if o.alpha <= 0 or (playing and o.id.startswith("vph")):
                continue
            x, y, w, h = placement(o, b.cam)
            f = max(1, round(K * o.scale))
            src = _png(o.img, f)
            for an in o.anim:
                if an[0] == "frames":
                    from reg import spr
                    _, name, n, fps, kw = an
                    src = _gif([spr(name, frame=j, **kw) for j in range(n)], fps, f)
            pic = s.shapes.add_picture(src, Emu(round(x * EMU)), Emu(round(y * EMU)), Emu(round(w * EMU)), Emu(round(h * EMU)))
            pic.name = "!!" + o.id
            _set_alpha(pic, o.alpha)
        adv = ""
        spid = None
        is_clip = b.video is not None and b.clip is not None
        if playing:
            if is_clip:
                src, post, dur = videos.clip(v, b.clip)
                tag = f"{b.video}_{b.clip + 1:02d}"
            else:
                src, dur = v["abspath"], videos.duration(v["abspath"])
                post = videos.poster(src, os.path.join(BUILD, f"poster_{b.video}.png"), v.get("poster_at", 0.0))
                tag = b.video
            mov = s.shapes.add_movie(src, 0, 0, prs.slide_width, prs.slide_height,
                                     poster_frame_image=post, mime_type="video/mp4")
            mov.name = "video_" + tag
            spid = mov.shape_id
            if is_clip:   # plays on entry, freezes on its last frame, waits for the click
                report.append(f"slide {i + 1}: {tag} clip {b.clip + 1} of {len(v['clips'])} from {v['path']} "
                              f"[{v['variant']}] ({dur:.2f} s, autoplay, waits for a click)")
            else:
                adv = f' advTm="{int(dur * 1000) + 1000}"'
                report.append(f"slide {i + 1}: {b.video} embedded from {v['path']} ({dur:.1f} s, autoplay, advances 1 s after it ends)")
        elif v is not None:
            why = "held by videos.json" if os.path.isfile(v["abspath"]) else "no file"
            report.append(f"slide {i + 1}: {b.video} PLACEHOLDER ({why}: {v['path']})")
        nxt = next((x.say for x in beats[i + 1:] if x.say), "(end)")
        s.notes_slide.notes_text_frame.text = _notes(b, nxt)
        el = s._element
        for t in el.findall("p:timing", NS):
            el.remove(t)
        prev = beats[i - 1] if i else None
        cut = is_clip and prev is not None and prev.video is not None and prev.clip is not None
        if not cut:                # between two clips there is no transition at all: an instant cut
            fade = i == 0 or b.fade or b.video or (prev is not None and prev.video)
            t = etree.fromstring(FADE.format(adv=adv) if fade else MORPH.format(ms=int(b.morph * 1000), adv=adv))
            clr = el.find("p:clrMapOvr", NS)
            (clr.addnext(t) if clr is not None else el.find("p:cSld", NS).addnext(t))
        else:
            t = el.find("p:clrMapOvr", NS)
            if t is None:
                t = el.find("p:cSld", NS)
        if spid is not None:
            t.addnext(etree.fromstring(AUTOPLAY.format(ms=int(dur * 1000), spid=spid)))
    import appendix
    extra = appendix.add(prs, layout)          # A1 to A9: native, editable slides after the close
    report.append(f"appendix: {len(extra)} native slides ({', '.join(x['id'] for x in extra)}) from APPENDIX.md")
    sz = prs.part._element.find("p:sldSz", NS)
    if sz is not None and "type" in sz.attrib:
        del sz.attrib["type"]            # the slide size is custom 16:9, not "On-screen Show (4:3)"
    prs.core_properties.title = title
    prs.core_properties.author = "3B Therapeutics"
    prs.save(out)
    return out, len(beats) + len(extra), report
