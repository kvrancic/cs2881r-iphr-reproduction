# IPHR reproduction deck (five minutes)

`IPHR_Reproduction.pptx` is the deck: 74 slides at 16:9, one per spoken sentence or phrase. Every object is a picture named `!!<id>`, so PowerPoint Morph glides it from one slide to the next; a fade starts each scene. In chart scenes the board stands at the left and the robot (the model under test, at 2x) stands beside it in a fixed spot, so Morph carries it from chart to chart. The speaker notes of each slide are exactly the words said while it is up, then `NEXT:` with the words that follow.

## Presenting
- Morph needs PowerPoint 2019 or later, or Microsoft 365. Keynote and Google Slides fall back to a plain fade.
- All text is pictures, so no fonts need to be installed.
- Advance with a click or the right arrow; nothing starts on its own.

## Rebuilding
Use the project venv (`../.venv`, with python-pptx, lxml, Pillow, numpy, Playwright).

```
cd engine
../../.venv/bin/python build_all.py              # .pptx and contact sheets in review/
../../.venv/bin/python build_all.py pptx sheets qa   # plus a LibreOffice render in review/qa/
```

`IPHR_Reproduction.pdf` is the LibreOffice render of the same deck (no Morph); after a `qa` build, copy it from `review/qa/`.

Every build checks that the notes equal `../talk/transcript.md` word for word, that every number the speaker says matches the result files (`checks.claims()`), that no label touches anything or leaves the screen (and no chart element leaves its grid), and that every slide has a transition. `build/morph.txt` lists what carries over at each transition.

## How it is made
- `engine/` is the CamelHacks engine (itself from the ACAP Seattle keynote): native canvas 384x216, upscaled 10x with nearest neighbour, Endesga 32 palette, Jersey 10 pixel font, the whitish dithered ground.
- `engine/story/s1_claim.py`, `s2_did.py`, `s3_kind.py`, `s4_ext.py` and `s5_close.py` are the storyboard as code (the example and Figure 2; the four things, recompute and rerun; the split by kind; the two variations; the close and limits); `storyboard.md` describes the same slides in words.
- `engine/sprites/robot.py` is the robot from the Seattle talk, plus a big version drawn at twice the detail with antenna colours, hats, a held card and sweat; `props.py` holds the scale (any size, tilt and load), chat windows, question cards, card backs, the flag, compass, the one lake map (with the two readings of "west") and its mini glyph, large kind icons, the aqua fact card, plinths and the board stands (legs, monitor stand, lab bench, map table); `deckui.py` holds text, chips, plates and the cue plate, which always sits at the bottom left.
- `engine/charts.py` authors every chart in HTML/CSS on a 960x540 grid, renders it in headless Chromium, snaps it to the palette and cuts it into one picture per element. Each act has its own board: Figure 2 and its split by kind are paper on legs, the recompute a terminal on a monitor stand, the rerun and the fact cards a board on a lab bench, geography a sea chart on a map table. All figures on screen are read at build time from `../results/paper_data_checks.json`, `runs.json`, `noise_models.json`, `geo_analysis.json` and `../data/judge_validation/summary.json` (`checks.claims()` also reads `cited_facts.json`, and `recall_probe.json` to check the spoken "about seven in ten"); the few numbers typed in code (the plotting divisor 4,892, the 1,014-pair sample in panel titles) are stated in the talk or equal the result files, and the build checks 4,892 against every plotted bar. `checks.claims()` compares the retest cutoffs with the paper's reported 76.5%, which is not shown on screen.
