# KU Car Club landing page

Landing page for Khalifa University's car club in Abu Dhabi. It replaces the club's earlier site at https://ihama1305-design.github.io/KU-CAR-CLUB/ (an Astro project in `ihama1305-design/KU-CAR-CLUB`, useful as a source for content and photos).

The club in one line: student-run, backed by the Abu Dhabi Motor Majlis, free to join, open to everyone, every car welcome.

## Rules for this repository

- Commit as the repository owner. Never add `Co-Authored-By` lines, "Generated with" lines or any other AI attribution to commits or pull requests. If git's `user.name` and `user.email` are not the owner's, stop and ask before committing.
- This is a plain static site. Keep it deployable from the repository root with no build step unless the owner asks for one.
- Number plates stay blank in every sketch, and people are not drawn.

## Current state

`index.html` is the full landing page (built 20 November 2026, not yet committed or published). Top to bottom: navigation bar with a phone and tablet menu, puzzle-bento hero, members' cars wall (`#cars`), film collection carousel (`#club`), Explore UAE map (`#explore`), Our people (`#people`), next meet and closing call (`#meet`), footer. Styles and script are inline in the file. It was checked at 1440, 1024, 390 and 320 px wide with no errors, no broken images and no sideways scroll.

Not built: inner pages. The owner has not yet reviewed or approved the sections added on 20 November.

### Sections added on 20 November

- Each added piece has its own `<style>` block (marked `/* section: name */`), its own class prefix and, where needed, its own script: menu `mn-`, cars `cr-`, explore `xp-`, people `pp-`, meet `mt-`, footer `ft-`. Shared helpers come first (`ku-sec`, `ku-wrap`, `ku-over`, `ku-h2`, `ku-lead`, `ku-hand`, `ku-paper`).
- Sections carry `data-ku-reveal`. A shared script adds `.is-in` when one scrolls into view: `.rise` blocks fade up and `.draw` outlines draw on. Without script, and with reduced motion, everything is simply visible.
- To announce a meet, set `data-date` (UAE time, for example `2026-12-05T19:30:00+04:00`) and `data-venue` on the `#meet` section. While they are empty the countdown stays hidden and the page says "Date and venue announced soon." No date or venue has been confirmed.
- The Explore UAE places are ideas, labelled "not confirmed meet venues". The coastline is public-domain Natural Earth data, taken from the earlier site.
- The cars wall shows eight sketches with no makes or models, because the model names are guesses.
- The film carousel's arrows are `#filmPrev` and `#filmNext`. The hero's "Next meet" tile keeps `id="next"`.

## Files

- `index.html` – the page
- `assets/` – `wordmark.png` (navy logo), `wordmark-cream.png` (footer), `badge.png` (round badge, also the favicon), `sketch-supra.png`, `sketch-mustang.png`, nine film carousel photos (`photo-01`, `04`, `07`, `08`, `09`, `12`, `13`, `15`, `16`)
- `assets/sketches/` – `car-01.svg` … `car-08.svg` for the cars wall: copies of eight `design/sketches/` drawings with heavier lines for small sizes
- `fonts/` – self-hosted woff files and their Open Font Licence texts
- `design/sketches/` – twelve ink sketches as transparent navy PNG and as SVG
- `design/logo/` – navy and cream wordmarks, badge
- `design/reference/` – screenshots of the approved hero and carousel (`landing-desktop.png`, `landing-phone.png`), of the full page as built on 20 November (`landing-full-desktop.png`, `landing-full-phone.png`), and the sheet of all twelve sketches
- `design/tools/` – the scripts that made the hand-drawn outlines and the sketches (see its README)

## Design

Colours: navy `#14213D`, cream `#F3EBD8` (page background), ivory `#FAF6EC` (paper tiles). Set as `--navy`, `--cream`, `--ivory` on `.ku`.

Type: Barlow Condensed 600/700 for headings and buttons, Barlow 400/500/600 for body, Caveat for handwritten notes, Instrument Serif italic for the accent words in the film heading.

Sketch style: outlines of tiles, buttons and icons are hand-drawn SVG paths (doubled, slightly jittered strokes). They draw on at load with `pathLength="1"` and a `stroke-dasharray` animation (`kuDraw`). Paper tiles carry a faint dot grid.

### Hero (puzzle bento)

- One stage with a fixed aspect ratio of 1360 / 740. Four interlocking tiles are absolutely placed in percentages and cut with `clip-path: url(#kuClip…)` using `clipPathUnits="objectBoundingBox"`.
- Tile boxes on the 1360 × 740 stage, as x, y, width, height: title 7, 7, 683, 353; Supra 576, 7, 777, 478; Mustang 7, 374, 1195, 359; next meet 1039, 431, 314, 302.
- Text inside tiles is sized in `cqw`. The page root is a container named `ku`. At 1100 px and below the tiles stack as rounded cards; 640 px and below is the phone layout.
- Title tile: h1 "Khalifa University's car club", a Caveat line "every car welcome" with a drawn underline, the badge, one paragraph, and the buttons "Join the club" and "See the next meet".
- Car tiles: the Supra and Mustang sketches fill their tiles and are cropped by the tile shape (Supra `left:-11%; top:2%; width:111%`, Mustang `left:3%; top:4.5%; width:82%`). When stacked, each car tile takes its drawing's aspect ratio so the car runs edge to edge. There are no labels on the cars.
- Next-meet tile: "Next meet", "Date and venue announced soon. Free entry, open to everyone.", link "Get the meet alert".

### Film collection (3D barrel carousel)

- Navy section. Overline "KU Car Club / The film collection", heading "The club, in motion."
- Pure CSS 3D. Each card: `rotateY(calc(var(--step) * -i)) translateZ(calc(-1 * var(--R)))`. The drum: `translateZ(var(--R)) rotateY(calc(var(--step) * pos))`.
- Desktop: `--R: 700px`, `--step: 15.3deg`, cards 186 × 308, perspective 860 px. Phone: 430 px, 17.7 deg, 132 × 222, perspective 540 px.
- Nine cards. Drag with pointer events, arrow buttons, dots and a counter.
- Keep the active card's frame inside the card box: Chrome clips anything that overflows a 3D-transformed layer.

### Motion

- Hover effects are gated with `@media (hover: hover) and (pointer: fine)`.
- `prefers-reduced-motion: reduce` turns off the draw-on and reveal animations.

## Links

- Join buttons: `https://chat.whatsapp.com/JkFbOO5HqYm7sCNGOz8GKF`
- "Get the meet alert": `https://www.instagram.com/ku.car.club/`

Both come from the earlier site. Confirm with the owner that they are still current.

## Sketches

All twelve were traced from the club's own photographs: GR Supra, Mustang, 992 Carrera, 930 Turbo, 918 Spyder, Ferrari, bare-metal 964, R33 Skyline, 993 Turbo, R8, Senna, AMG GT. The model names are best guesses from the photos. The page uses only the Supra and Mustang so far. One line weight, closed outline, fitted wheel ellipses; use them on cream or ivory, or recolour the SVG stroke.

## Publishing

GitHub Pages: Settings, Pages, "Deploy from a branch", `main`, `/ (root)`.
