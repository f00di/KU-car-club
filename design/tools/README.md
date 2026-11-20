# Design tools

These are the working scripts behind the page, kept for reference. They were written for one machine and use absolute paths (`/home/claude/...`), so adjust the paths before running them. They need Python 3 with `opencv-contrib-python`, `numpy`, `scipy` and `Pillow`.

- `geom.py` – the puzzle-bento tile shapes, their clip paths and the hand-drawn outline helper `rough()`
- `sketch.py` – the hand-drawn icons and button outlines
- `build_page.py`, `build_ink_variant.py`, `build_static.py` – how the page was assembled from those parts
- `refine.py` – traces a car photo into a clean ink sketch (PNG and SVG). It uses `ink.py` and `ink5.py` for the cut-out step, `hulls.json` and `crops5.json` for the per-photo guides, and `model.yml.gz`, OpenCV's structured edge detection model
- The source photographs are not included. Each entry in `crops5.json` and each `CARS` entry names the photo it expects.
