# KU Car Club landing page

Landing page for Khalifa University's car club in Abu Dhabi. It replaces the club's earlier site at https://ihama1305-design.github.io/KU-CAR-CLUB/ (an Astro project in `ihama1305-design/KU-CAR-CLUB`, useful as a source for content and photos).

The club in one line: student-run, backed by the Abu Dhabi Motor Majlis, free to join, open to everyone, every car welcome.

## Rules for this repository

- Commit as the repository owner. Never add `Co-Authored-By` lines, "Generated with" lines or any other AI attribution to commits or pull requests. If git's `user.name` and `user.email` are not the owner's, stop and ask before committing.
- This is a plain static site. Keep it deployable from the repository root with no build step unless the owner asks for one.
- Number plates stay blank in every sketch, and people are not drawn.

## Current state

`index.html` is the full landing page, live at https://f00di.github.io/KU-car-club/ since it was published from `main` on 21 November 2026. Top to bottom: navigation bar with a phone and tablet menu, puzzle-bento hero with rotating car sketches, film collection carousel (`#club`), Explore map with the meets and events list (`#explore`), Our people (`#people`), next meet and closing call (`#meet`), footer. Styles and script are inline in the file. It was checked at 1440, 1024, 390 and 320 px wide with no errors, no broken images and no sideways scroll.

Not built: inner pages. The members' cars wall (`#cars`) was removed at the owner's request.

### How the sections are built

- Each piece has its own `<style>` block (marked `/* section: name */`), its own class prefix and, where needed, its own script: menu `mn-`, explore `xp-`, people `pp-`, meet `mt-`, footer `ft-`. The header's hover scribble is `/* section: join scribble */` (`btn-scrib`), and the hero rotation script is `/* section: hero cars */`. Shared helpers come first (`ku-sec`, `ku-wrap`, `ku-over`, `ku-h2`, `ku-lead`, `ku-hand`, `ku-paper`).
- Sections carry `data-ku-reveal`. A shared script adds `.is-in` when one scrolls into view: `.rise` blocks fade up and `.draw` outlines draw on. Without script, and with reduced motion, everything is simply visible.
- To announce a meet, set `data-date` (UAE time, for example `2026-12-05T19:30:00+04:00`) and `data-venue` on the `#meet` section. While they are empty the countdown stays hidden and the page says "Date and venue announced soon." No date or venue has been confirmed.
- Explore ("Adventures beyond campus.") lists upcoming meets and events. To add one, put a line in the `EVENTS` array at the top of the `/* section: explore */` script: `{ title, date: 'YYYY-MM-DD', time: 'HH:MM', venue, lat, lon, note }`. Only title and date are required, and the date and time are UAE time. The list sorts itself by date and shows dd/mm, or dd/mm/yy for another year. Events whose lat/lon fall inside the map get a pin.
- With no events (the case today) the card says "Nothing booked yet" and links to the meet alert. That card is plain HTML, so it shows without script.
- `isListed(ev, now)` in that script decides when a past event drops off the list. It is still a TODO and returns true, so delete past events by hand. The hero's "Next meet" tile and `#meet` don't read from this list.
- The map's coastline is public-domain Natural Earth data, taken from the earlier site. The first time the map scrolls into view it opens as a globe (`/* section: explore intro */`, outlines from `assets/world-land.json`, Natural Earth 1:110m). The globe turns to the UAE, drops the club badge on KU main campus, then pulls back to the flat map, and the badge goes. A tap on the map or the list skips the intro, and reduced motion leaves it out.
- The film carousel's arrows are `#filmPrev` and `#filmNext`. The hero's "Next meet" tile keeps `id="next"`.

## Files

- `index.html` – the page
- `assets/` – `wordmark.png` (navy logo), `wordmark-cream.png` (footer), `badge.png` (round badge, also the favicon), eleven hero car sketches `sketch-<name>.svg` (supra, mustang, r33, r8, p918, senna, p993, ferrari, p992, p930, p964; copies of the `design/sketches/` SVGs), `world-land.json` (globe outlines), nine film carousel photos (`photo-01`, `04`, `07`, `08`, `09`, `12`, `13`, `15`, `16`). `sketch-supra.png` and `sketch-mustang.png` are no longer used.
- `assets/sketches/` – `car-01.svg` … `car-08.svg`, made for the removed cars wall and no longer used
- `fonts/` – self-hosted woff files and their Open Font Licence texts
- `design/sketches/` – twelve ink sketches as transparent navy PNG and as SVG
- `design/logo/` – navy and cream wordmarks, badge
- `design/reference/` – screenshots of the approved hero and carousel (`landing-desktop.png`, `landing-phone.png`), of the full page as built on 20 November (`landing-full-desktop.png`, `landing-full-phone.png`), and the sheet of all twelve sketches. The page screenshots are older than the rotating hero, the events list and the removal of the cars wall.
- `design/tools/` – the scripts that made the hand-drawn outlines and the sketches (see its README)

## Design

Colours: navy `#14213D`, cream `#F3EBD8` (page background), ivory `#FAF6EC` (paper tiles), gold `#C6A75E` (accents). Set as `--navy`, `--cream`, `--ivory`, `--gold` on `.ku`. Gold on cream is only about 2:1, so don't use it for body text.

Buttons are outline-only with no fill. The header's "Join free" (`.btn-navy`) is navy. "Join the club" (`.btn-cream`, in the hero and the meet section) is gold. The class names no longer describe the fill. On mouse hover, "Join free" scribbles a gold zigzag behind its label.

Type: Barlow Condensed 600/700 for headings and buttons, Barlow 400/500/600 for body, Caveat for handwritten notes, Instrument Serif for the italic accent words in section headings and for the large numbers (film counter, Explore dates, people and meet figures).

Sketch style: outlines of tiles, buttons and icons are hand-drawn SVG paths (doubled, slightly jittered strokes). They draw on at load with `pathLength="1"` and a `stroke-dasharray` animation (`kuDraw`). Paper tiles carry a faint dot grid.

### Hero (puzzle bento)

- One stage with a fixed aspect ratio of 1360 / 740. Four interlocking tiles are absolutely placed in percentages and cut with `clip-path: url(#kuClip…)` using `clipPathUnits="objectBoundingBox"`.
- Tile boxes on the 1360 × 740 stage, as x, y, width, height: title 7, 7, 683, 353; top car tile (`.t-carA`) 576, 7, 777, 478; bottom car tile (`.t-carB`) 7, 374, 1195, 359; next meet 1039, 431, 314, 302.
- Text inside tiles is sized in `cqw`. The page root is a container named `ku`. At 1100 px and below the tiles stack as rounded cards; 640 px and below is the phone layout.
- Title tile: h1 "Khalifa University's car club", a Caveat line "every car welcome" with a drawn underline, the badge, one paragraph, and the buttons "Join the club" and "See the next meet".
- Car tiles: each shows one whole sketch (`object-fit: contain`), sitting on the tile floor. Above 1100 px the boxes are `.ink-a` 2%, 3%, 96% × 93% and `.ink-b` 3%, 4.5%, 82% × 91%. When stacked, the tiles keep aspect ratios of 2.14 and 2.55. There are no labels on the cars, and alt text never names a make or model.
- Rotation (`/* section: hero cars */`): the tiles start on the Supra and the Mustang. Every 5 s one tile wipes its car away and scribbles another in, so each tile changes every 10 s.
  - Top tile pool: supra, r33, r8, p918, mustang, senna, p993.
  - Bottom tile pool: ferrari, p992, p930, p993, senna, p964, p918, mustang.
  - The same car never shows in both tiles at once. Each sketch is fetched just before its turn.
  - It stops while the tab is hidden or the hero is off screen, and doesn't run with reduced motion.
  - The pause button (`.ink-pause`) is hidden unless it has keyboard focus, at the owner's request. It stays for WCAG 2.2.2.
- Next-meet tile: "Next meet", "Date and venue announced soon. Free entry, open to everyone.", link "Get the meet alert".

### Film collection (3D barrel carousel)

- Navy section with no heading (the owner removed "The club, in motion."). It has the overline "KU Car Club / The film collection" and the line "The places. The people. The nights worth showing up for." `aria-label="The film collection"` names the section for screen readers.
- Pure CSS 3D. Each card: `rotateY(calc(var(--step) * -i)) translateZ(calc(-1 * var(--R)))`. The drum: `translateZ(var(--R)) rotateY(calc(var(--step) * pos))`.
- Desktop: `--R: 700px`, `--step: 15.3deg`, cards 186 × 308, perspective 860 px. Phone: 430 px, 17.7 deg, 132 × 222, perspective 540 px.
- Nine cards. Drag with pointer events, arrow buttons, dots and a counter.
- Keep the active card's frame inside the card box: Chrome clips anything that overflows a 3D-transformed layer.

### Motion

- Hover effects are gated with `@media (hover: hover) and (pointer: fine)`.
- `prefers-reduced-motion: reduce` turns off the draw-on and reveal animations, the hero rotation and the globe intro. The "Join free" scribble then shows at once instead of drawing in.

## Links

- Join buttons: `https://chat.whatsapp.com/JkFbOO5HqYm7sCNGOz8GKF`
- "Get the meet alert" and the footer: `https://www.instagram.com/ku.car.club/`
- Footer: TikTok `https://www.tiktok.com/@ku.car.club`

The owner confirmed on 20 November 2026 that the WhatsApp and Instagram links are current.

## Sketches

All twelve were traced from the club's own photographs: GR Supra, Mustang, 992 Carrera, 930 Turbo, 918 Spyder, Ferrari, bare-metal 964, R33 Skyline, 993 Turbo, R8, Senna, AMG GT. The model names are best guesses from the photos. The hero rotates eleven of them. The AMG GT is left out because it's nearly square. One line weight, closed outline, fitted wheel ellipses; use them on cream or ivory, or recolour the SVG stroke.

## Publishing

GitHub Pages: Settings, Pages, "Deploy from a branch", `main`, `/ (root)`. Pushing `main` publishes the site at https://f00di.github.io/KU-car-club/ about a minute later. GitHub Pages is case-sensitive, so check that every file name the page uses matches a committed file exactly, including the `assets/sketch-<name>.svg` paths the hero script builds.
