"""The videos the deck plays, configured in deck/videos.json.

Each video has `variants` (name -> file) and a `variant` that picks one, so an alternative render is swapped in
with one edit and a rebuild. A video with `cut_at` is narrated live: the build cuts it into one clip per spoken
sentence group, at those cue times, which must be sentence starts listed in the video's CUES.md. Each clip gets
its own slide that plays on entry, freezes on its last frame and waits for Karlo's click. A video without
`cut_at` (the intro) plays whole and advances on its own.

Clips are cut frame-accurately by re-encoding (never stream copy), so consecutive clips join without a seam."""
import hashlib, json, os, subprocess

DECK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(DECK, "videos.json")
CLIPS = os.path.join(DECK, "build", "clips")


def _abs(p):
    return os.path.normpath(os.path.join(DECK, p))


def cue_sentences(cues_path):
    """[(start seconds, sentence)] for every sentence start in a CUES.md: the rows of its shot table whose
    sentence column holds a sentence (rows that say '(same sentence ...)' or '(...)' continue the previous one)."""
    out = []
    for line in open(cues_path):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        nums = []
        for c in cells:
            try:
                nums.append(float(c))
            except ValueError:
                nums.append(None)
        if cells[0].isdigit() and len(cells) >= 6:   # explainer: | shot | start | end | frame | frame | sentence | ...
            t, sentence = nums[1], cells[5]
        elif nums[0] is not None and len(cells) >= 2:  # demo: | film time | sentence | ...
            t, sentence = nums[0], cells[1]
        else:
            continue
        if t is None or not sentence or not sentence[0].isalpha() or len(sentence.split()) < 3:
            continue
        out.append((t, sentence))
    return out


def load():
    with open(CONFIG) as f:
        cfg = json.load(f)
    out = {}
    for key, v in cfg.items():
        variants = v.get("variants") or {"default": v["path"]}
        name = v.get("variant", "default")
        rel = variants[name]
        path = _abs(rel)
        e = dict(v, path=rel, abspath=path, variant=name, present=os.path.isfile(path) and v.get("embed", True))
        if v.get("cut_at"):
            sents = cue_sentences(_abs(v["cues"]))
            starts = [t for t, _ in sents]
            for t in v["cut_at"]:
                if not any(abs(t - s) < 1e-6 for s in starts):
                    raise ValueError(f"{key}: cut at {t} s is not a sentence start in {v['cues']} ({starts})")
            cuts = list(v["cut_at"])
            clips = []
            for i, t0 in enumerate(cuts):
                t1 = cuts[i + 1] if i + 1 < len(cuts) else None
                say = " ".join(s for t, s in sents if t >= t0 - 1e-6 and (t1 is None or t < t1 - 1e-6))
                clips.append({"start": t0, "end": t1, "say": say})
            e["clips"] = clips
        out[key] = e
    return out


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                        "-show_entries", "stream=r_frame_rate,nb_read_packets", "-of", "json", path],
                       capture_output=True, text=True, check=True)
    s = json.loads(r.stdout)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return float(n) / float(d), int(s["nb_read_packets"])


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def poster(path, out_png, at=0.0):
    """A frame of the video (at `at` seconds), used as the poster PowerPoint shows before playback starts."""
    if not os.path.exists(out_png) or os.path.getmtime(out_png) < os.path.getmtime(path):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(at), "-i", path, "-frames:v", "1", out_png], check=True)
    return out_png


def clip(v, i):
    """Cut clip i of video v frame-accurately (re-encoded H.264, same frame rate and size, no audio).
    Returns (clip path, first-frame poster path, duration in seconds). Cached by source, variant and range."""
    os.makedirs(CLIPS, exist_ok=True)
    fps, nframes = probe(v["abspath"])
    c = v["clips"][i]
    f0 = round(c["start"] * fps)
    f1 = round(c["end"] * fps) if c["end"] is not None else nframes
    st = os.stat(v["abspath"])
    tag = hashlib.sha1(f"{v['abspath']}|{st.st_size}|{st.st_mtime}|{f0}|{f1}".encode()).hexdigest()[:10]
    base = os.path.join(CLIPS, f"{os.path.splitext(os.path.basename(v['abspath']))[0]}_{i + 1:02d}_{tag}")
    mp4, png = base + ".mp4", base + "_first.png"
    if not os.path.exists(mp4):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", v["abspath"],
                        "-vf", f"trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS",
                        "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                        "-r", f"{fps:g}", "-g", str(int(round(fps))), "-movflags", "+faststart", mp4], check=True)
    if not os.path.exists(png):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4, "-frames:v", "1", png], check=True)
    return mp4, png, (f1 - f0) / fps
