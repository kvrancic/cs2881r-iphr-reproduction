# IPHR reproduction deck (five minutes)

`IPHR_Reproduction.pptx` is the deck: 73 slides at 16:9, one per spoken sentence or phrase. Every object is a picture named `!!<id>`, so PowerPoint Morph glides it from one slide to the next; a fade starts each chapter. The robot (the model under test) acts in every scene: it frames its own value with a magnifier, points with a long pointer at a board, a map or a scale, turns the knob of the cutoff gauge, holds a rank tile, a fact card or a sign with its counts, and grows to half again its size at the moments that matter (the title, the unsaid lean, "maybe another model", "unsure, answers anyway"). Where the runs compare models, the models themselves hold signs with their bars or counts. Each model keeps one look on every slide: GPT-4o mini a pink antenna and a chat-bubble badge, Llama 3.3 a brown beret, DeepSeek V3 a slate fin, Gemini 2.5 Flash a gold bow, GPT-5.6 Luna (the fourth model of the fact-card runs) a gold crescent moon, our labeller a judge's cap. The speaker notes of each slide are exactly the words said while it is up, then `NEXT:` with the words that follow.

## Presenting
- Morph needs PowerPoint 2019 or later, or Microsoft 365. Keynote and Google Slides fall back to a plain fade.
- All text is pictures, so no fonts need to be installed. The title and the repo link are smooth Avenir Next; everything else is Jersey 10.
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
- `engine/story/s1_claim.py`, `s2_did.py`, `s3_kind.py`, `s4_ext.py` and `s5_close.py` are the storyboard as code (the example and Figure 2; the recompute and rerun; the split by kind; the two variations and the readings of "west"; the close and limits); `storyboard.md` describes the same slides in words.
- `engine/sprites/robot.py` is the robot from the Seattle talk, plus a big version drawn at twice the detail with antenna colours, the model looks, a raised open hand, a held card and sweat; `props.py` holds the scale (any size, tilt and load), chat windows, question cards and card stacks, the flag, compass, the one lake map (with the two readings of "west", and B due west of A for the paper's own test), large kind icons, the aqua fact card, plinths, the printed papers of the title, the divisor page, the cutoff gauge, the held props (pointer, magnifier, rank tile, the signs the models hold: lean bars on one scale, flag counts), the wine arrow of the lean and the board stands (legs, monitor stand, lab bench); `deckui.py` holds text, chips, plates and the cue plate, which always sits at the bottom left.
- `engine/sprites/sets.py` draws one set piece per act (a lecture hall, a lab wall, a map wall, a surveyor's corner, a stage) in the ground's pale colours; `build_story.py` sets it per act with `Timeline.scenery`, and every slide of the act carries it under everything else, so Morph keeps it still.
- `engine/charts.py` authors every chart in HTML/CSS on a 960x540 grid, renders it in headless Chromium, snaps it to the palette and cuts it into one picture per element. The board says where the data come from: the white paper board on legs holds the paper's figures and data (Figure 2, its split by kind, the distance chart, the paper's own test), the dark terminal on a monitor stand the released data recomputed, the white board with an orange rim on the lab bench our own runs (DeepSeek's counts, GPT-4o mini per pair against chance, the recall probe). The three discrepancies, the fact-card counts and the wording ladder are drawn as pictures (props, signs held by the models, chat bubbles with bars). Blue is the paper's run, orange ours, yellow a highlight. All figures on screen are read at build time from `../results/paper_data_checks.json`, `runs.json`, `noise_models.json`, `geo_analysis.json` and `../data/judge_validation/summary.json` (`checks.claims()` also reads `cited_facts.json`, and `recall_probe.json` to check the spoken "about seven in ten"); the few numbers typed in code (the plotting divisor 4,892, the 1,014-pair sample in panel titles, the paper's 9% same-latitude test) are stated in the talk or equal the result files; the build checks 4,892 against every plotted bar and the 9% against the paper's table in `../scratch/paper.txt`. `checks.claims()` compares the retest cutoffs with the paper's reported 76.5%, which is not shown on screen.
