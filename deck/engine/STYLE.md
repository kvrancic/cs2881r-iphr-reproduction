# Pixel style guide (binding)

Every slide is a frame of one pixel-art world: sharp, readable from the back of a hall. `../BRIEF.md` is the source; this file is how the engine applies it.

## Canvas and scale
- Native canvas 384x216. Sprites are drawn at native resolution and upscaled 10x with nearest neighbour into the .pptx. To make something bigger, draw it bigger (the big robot in `sprites/robot.py`) or move the camera.
- The camera may zoom by 1.2, 1.6, 2.0 or 2.4 (`Timeline.focus`), which keep every native pixel a whole block at 1080p and 4K.
- Charts use a finer 960x540 grid (2.5x the art grid), authored in HTML in `charts.py` and snapped to the palette.

## Ground
- Near-white with ordered-dither bands of ice and steel towards the edges (`ground.py`). No smooth gradients.
- Characters stand with their feet on y 184 on a faint dithered floor band.

## Palette
Endesga 32 only (`pal.py`). Semantic colours, the same everywhere: NO wine/red; YES green; the paper's run blue (sky, navy); our run orange; fact cards aqua (cyan, deep); unknown or hidden grey; yellow is the only highlight; ticks and crosses for right and wrong are ink (the scale and the compass are grey until the talk names them).

## Rules
- Light from the top left; 1px ink outlines on characters and props.
- Text: Jersey 10 only, at size 20 or a multiple. Words are keywords and short labels, never the spoken sentence. The orientation cue is white on an ink plate with a yellow bar, in one spot per scene. No em dashes, no headers, footers or trackers.
- All text is Jersey 10, the title and closing slides included, except the repo link on the closing slide: smooth Avenir Next (as the brief allows), so the long link sits well inside the frame.

## Code
- Sprites are functions with keyword arguments, deterministic, returning RGBA.
- Every object is placed through `Timeline.put` with an id; the id becomes the picture name `!!id`, which Morph matches between slides. Text ids start with `t_` (or are the `cue`) so the layout check finds them.
