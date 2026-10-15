# Pixel style guide for the 3B Therapeutics deck (binding)

Every slide is a frame of one pixel-art world (SNES/GBA era and modern HD pixel art): sharp, readable from the back of a hall, a little mischievous in posture, expression and visual gags, never in words. `../../BRIEF.md` is the source; this file is how the engine applies it.

## Canvas and scale
- Native canvas 384x216. Sprites are drawn at native resolution and upscaled by a whole factor with nearest neighbour (10x into the .pptx). Never draw at a higher resolution and never scale a sprite by a non-integer factor to make it bigger: draw it bigger.
- The camera may zoom a scene by 1.2, 1.6, 2.0 or 2.4 (`Timeline.focus`): those factors keep every native pixel a whole block on a 1080p and a 4K screen.
- The results slides use a finer 960x540 grid (2.5x the art grid), authored in HTML in `results.py` and snapped to the palette.

## Ground
- Near-white: white in the middle, ordered-dither bands of ice and a touch of steel towards the edges (`ground.py`, the same ground as the intro video). No smooth gradients anywhere.
- Characters stand with their feet on y 184 on a faint dithered floor band (`story/common.py: floor`), with a dithered contact shadow.

## Palette
Endesga 32 only (`pal.py`). Semantic colours, the same everywhere:
- T cells, the soldiers: sky / navy. Tumor, the castle: wine / plum / red. Fibroblasts and the wall: sand / tan / brown.
- Macrophage that protects the tumor (bribed guard): red. Macrophage that lets the soldiers in: sky.
- Chemotherapy poison: green / leaf. Measured: green. Predicted: gold.

Shading ramps (hue-shift, do not just darken): warm yellow > gold > orange > rust > brown > plum; skin sand > skin > skin2 > clay > brown; cool white > ice > steel > slate > dusk > night > ink; green yellow > green > leaf > pine > deep; blue cyan > sky > navy > dusk > night; red rose > red > wine > plum.

## Rules
- Light from the top-left. Characters and props carry a 1px ink outline so they pop on the white ground.
- Clusters, not noise; dither sparingly and in patterns. Big shapes first, details second.
- Text: Jersey 10 only, at size 20 (1px strokes, caps 10px) or a multiple of 20, through `px.text` or `deckui`. Text is sparse: words, short labels and plain sentences, never slogans. No em dashes.

## Code
- Python and PIL. Sprites are functions with keyword arguments and defaults, deterministic, returning RGBA at their contract size (listed in `story/common.py`).
- Every object on a slide is placed through `Timeline.put` with an id; the id becomes the picture name `!!id`, which is what Morph matches between slides.
