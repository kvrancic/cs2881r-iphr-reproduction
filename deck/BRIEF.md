# Deck brief (binding)

A 5-minute class talk reproducing Figure 2 of "Chain-of-Thought Reasoning in the Wild Is Not Always Faithful". The deck is a 2D pixel-art story told in PowerPoint with Morph transitions, in the same art language as Karlo's ACAP Seattle keynote and CamelHacks pitch. It must not look like a slide template. It must be informative.

## Sources
- Spoken script, one slide per sentence: `../talk/transcript.md`. The speaker notes of each slide are exactly the words said while it is up, then `NEXT: <the following words>`. A build check compares the notes with the transcript word for word.
- Scene ideas: `../talk/storyboard.md` (a starting point; improve on it, keep the meaning).
- Every number: `../results/runs.json`, `../results/paper_data_checks.json`, `../results/cited_facts.json`, `../data/judge_validation/summary.json`. Never type a number that is not in those files or the transcript.
- Engine: `engine/` is a copy of the CamelHacks engine (itself the ACAP engine). Read `engine/STYLE.md`, `../../../camel-hacks-pitch/deck/README.md` path is `~/Documents/projects/camel-hacks-pitch/deck/` for how the previous deck was built, `~/Documents/projects/camel-hacks-pitch/deck/engine/story/act*.py` for the storyboard-as-code idiom, and `~/Documents/projects/ACAP/seattle/engine/sprites/robot.py` for the AI robot character (boxy robot, CRT screen face). Reuse and adapt; do not start from zero.

## Look
- Native canvas 384x216, nearest-neighbour upscale, Endesga 32 palette, Jersey 10 pixel font at whole-pixel sizes, 1px ink outlines, light from the top left, no smooth gradients.
- Ground: the whitish dithered ground of the CamelHacks deck.
- Cast: the robot (the model under test) whose screen face carries the mood; a weighing scale or tilted signpost behind it for the hidden lean (faint grey until the talk names it, then coloured, tilting to NO or YES); chat windows for the two reversed questions; a judge robot with a stamp; an aqua fact card.
- Semantic colours, the same everywhere: NO = wine/red; YES = green; the paper's run = blue; our run = orange; fact cards = aqua/teal; unknown = grey.
- Charts and number panels (Figure 2 bars, the paper-vs-ours bars, the fact-card collapse, the overlap of flags, the template scatter) are authored as HTML/CSS on the 960x540 grid in the style of `results.py` (pixel instrument panels or pixel bar charts), rendered with headless Chromium, snapped to the palette, cut into one picture per element so bars can grow by Morph. Values exact, labels readable from the back of a hall.

## On-screen text (Karlo's rules from the earlier decks)
- One slide per spoken sentence or phrase. The main subject of each slide is large and obvious, so the speaker can tell from the picture which sentence comes next.
- Text is minimal: a few of the speaker's own keywords as a label or one short orientation cue per slide (white on a dark plate with a yellow left bar, in a consistent spot per scene), or a slightly reworded key point. Never the spoken sentence verbatim. Never added facts, sources, section title plates, progress trackers, headers or footers.
- Not images only either: every slide needs enough words that the audience understands it without the narration.
- Plain words. No slogans, no punchy lines, no em dashes.
- Explainer animations follow logical order (show the question before the answer, the input before the result).
- The title slide and the closing slide may use smooth hi-res text (Avenir Next rendered as an image) for the paper title, names and the repo link. Team names, alphabetical by surname: Shlok Dholakia, Nadia Sumin, Karlo Vrancic, Marc Walden.

## Output
- `deck/IPHR_Reproduction.pptx` (16:9), every object a picture named `!!id` so Morph glides it; a fade between scenes; no fonts needed on the presenting machine.
- Contact sheets of every slide in `deck/review/`, a LibreOffice render to PDF and PNGs in `deck/review/qa/`.
- `deck/README.md` (how to present and rebuild) and `deck/storyboard.md` (the slides in words), both short and plain.
- Build checks: notes match the transcript word for word; no overlapping text (check_layout); every slide has a transition; slide count printed.
