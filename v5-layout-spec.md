# V5 Layout Specification — news-image-20261119

**Status:** WIREFRAME STAGE ONLY. No final render yet. No submission.
**Branch:** `v5` (from v4 commit `ec01c0efac6ce7885fd670c84aba3e91a6308e44`)
**Wireframe:** `v5-wireframe.png` (1024×1024, SHA-256 `af73b5c6ed4a8092f95478683125373c050c986380cdd19293bf5860b77b4537`)
**Generator:** `/tmp/gen_wireframe.py` (Pillow; re-run to regenerate + re-assert)
**Dataset:** the verified 50-story `news.json` from V4 (unchanged). 16 featured (1–16), 34 also (17–50).
**Canvas:** 1024×1024. Margin 24px. Content width 976px (x=24–1000).
**Deadline:** entries close 21 Nov 07:00 WIB.

---

## 1. Reference analysis — Nov 17 entry image

Source: `~/workspace/makefun/news-image-20261117-r3/entry.png` (1024×1024).
Measured programmatically (row colour profiles, `/tmp/measure_ref.py`).
Live feed check: `https://make.fun/bounty/news-image-20261117#feed` — competition ENDED,
results in; 1st place @icantcodefyi ($50), "50 sourced stories, a UTC timeline
and a date check". 47 of 50 places paid. The feed text lists no images, so the
local r3 entry image is the visual reference.

### Measured section bounding boxes (Nov 17 reference)

| Section | y-range | Notes |
|---|---|---|
| Header (dark navy) | 0–91 | "THE DAY IN WORLD NEWS" + "Tuesday 17 November 2026" + "48 STORIES" + "6 CONTINENTS - ONE DAY"; small light-blue pixel motif y≈36–67 |
| Red ticker | 92–122 | White caps: DOW -849 (-1.6%) \| NVIDIA $115.8BN \| EBOLA 11,000+ \| VOYAGER 1 ... \| KERCH BRIDGE HIT \| TRUMP-XI-PUTIN THU |
| Story cards, 3 cols × 6 rows (18 cards) | 124–790 | Each row ≈111px tall; each card ≈330px wide; illustration band ≈55px at card top, then red category line, 2-line bold headline, 2-line summary |
| Bottom heading row | ≈788 | "WHERE IT HAPPENED" (left) + "ALSO ON TUESDAY 17 NOVEMBER" (right, red "19–48") |
| Map + newswire | ≈792–983 | Map left (x≈24–500, ocean from y≈812), newswire right (2 cols × 15 items, 19–48) |
| Footer | ≈984–1024 | "Every story here happened or was first reported on Tuesday 17 November 2026..." + "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN News. Original drawings." |

### What V5 keeps from the reference (style)

- Dark navy masthead with gold kicker + huge serif date/title.
- Red ticker/timeline band under the masthead.
- Numbered story cards with an illustration band on top, red category line, bold headline, small summary.
- World map (light-blue ocean, tan continents) with numbered red pins + "WHERE IT HAPPENED" heading.
- Newswire list "ALSO ON ..." with numbered items.
- Footer with source attribution + date-check note.

### What V5 changes from the reference (structure — binding V5 geometry wins)

- Reference cards are 3×6 (18 cards). V5 is 4 heroes in ONE row + 12 minis in 6×2.
- Reference header+ticker is 0–122. V5 header+timeline is 0–140 (room for the 5-stat strip, kept from V4).
- Reference map+newswire is ≈792–983. V5 map+newswire is 720–955.
- Reference footer is ≈984–1024 (2 lines). V5 footer is 960–1024 (3 lines).
- Reference newswire is 2 cols × 15. V5 newswire is 3 cols (12/11/11) for 34 items.

---

## 2. Binding page geometry (from Bram's V5 directive — do not change without documenting)

| Section | y-range | Height |
|---|---|---|
| A — Header and timeline | 0–140 | 140 |
| B — Four hero cards, ONE row | 145–390 | 245 |
| C — Twelve mini cards, 6×2 | 395–715 | 320 |
| D — World map + newswire | 720–955 | 235 |
| E — Date check and sources | 960–1024 | 64 |

Section gaps: 5px (140–145, 390–395, 715–720, 955–960). All sections span the
full content width x=24–1000 unless noted. No section exceeds the canvas.

---

## 3. Section A — Header and timeline (y=0–140)

| Element | Bounding box (x, y, w, h) | Notes |
|---|---|---|
| Masthead title | x=24, y=20–64, w=976 | "THE WORLD IN ONE DAY", DejaVuSerif-Bold 42, ink, centred |
| Rule | y=70, x=24–1000, 2px | Ink |
| Dateline | y=76–92 | "THURSDAY 19 NOVEMBER 2026 · 50 STORIES · 7 REGIONS · CLAIMS LABELLED", LiberationSans-Bold 15, red, centred |
| Stat strip | y=98–136 | 5 boxes, each (976−4×8)/5 = 188px wide, 8px gaps; value (Sans-Bold 15) + label (Sans 9, trimmed). Values from news.json `stats` (9-6 ICJ, $81.3bn Anthropic, 551,864 Suneung, 80,000+ Akvan, 51-48 Senate) |

---

## 4. Section B — Four hero cards, ONE horizontal row (y=145–390)

Four equal columns, 8px gaps. Each card 238×245.

| Hero | Card (x, y, w, h) | Story |
|---|---|---|
| 1 | (24, 145, 238, 245) | Trump, Xi and Putin hold first three-way summit — Shenzhen, China — White House |
| 2 | (270, 145, 238, 245) | World court: Myanmar committed genocide — The Hague — ICJ / HRW |
| 3 | (516, 145, 238, 245) | COP31 draft drops fossil fuels — Antalya, Turkiye — Reuters |
| 4 | (762, 145, 238, 245) | Anthropic debuts in record $81.3bn IPO — New York — Investopedia |

### Per-hero internal layout (relative to card top y=145)

| Element | y (absolute) | Height | Notes |
|---|---|---|---|
| Illustration panel | 146–266 | 120px | x=card_x+1 to card_x+237 (236px wide). **≥90px required — 120px chosen** to fix V4's "too shallow" failure. All four panels share baseline y=266. |
| Number badge | (card_x+7, 152), d=18 | — | Black circle, white number |
| VERIFIED / CLAIM chip | top-right of illustration, y=152 | 15px | Teal VERIFIED / red CLAIM |
| Headline | 272–306 | 2 lines, 17px leading | DejaVuSerif-Bold 15, max 2 lines, ellipsize |
| Summary | 310–352 | 3 lines, 14px leading | LiberationSans 11, max 3 lines |
| Category + source | 368–382 | 1 line | LiberationSans 10, muted, e.g. "Shenzhen, China — White House" |
| Card bottom padding | 382–390 | 8px | — |

Hero illustration subjects (redesign the V4 scenes at 236×120, not 58px bands):
1. Summit — three flags (US/CN/RU) over a round table, hills + lake, "DECLARATION TOWARD PEACE" banner.
2. ICJ — courthouse pediment + columns, scales of justice, red "9–6".
3. COP31 — draft document with "FOSSIL FUELS" struck through in red, globe + leaf.
4. Anthropic — soaring stock chart + bars, "$81.3bn", "ANT $97.17 +17%" tag.

---

## 5. Section C — Twelve mini cards, 6 columns × 2 rows (y=395–715)

Six columns, 8px gaps; two rows, 8px gap. Each card 156×156.

### Card positions

| Row | y | Cards (x) |
|---|---|---|
| 1 | 395–551 | #5 x=24, #6 x=188, #7 x=352, #8 x=516, #9 x=680, #10 x=844 |
| 2 | 559–715 | #11 x=24, #12 x=188, #13 x=352, #14 x=516, #15 x=680, #16 x=844 |

Each card is 156 wide; illustration panels are **identical 154×76** for all 12
(x=card_x+1 to card_x+155, y=card_y+1 to card_y+77).

### Per-mini internal layout (relative to card top)

| Element | y (relative) | Notes |
|---|---|---|
| Illustration panel | +1 to +77 | 154×76, identical for all 12 |
| Number badge | (card_x+3, card_y+12), d=18 | Black circle, white number |
| Category | +82 to +94 | LiberationSans-Bold 9, red, e.g. "US - TECH" |
| Headline | +96 to +138 | LiberationSans-Bold 12, max 3 lines, 14px leading; CLAIM prefix in red |
| Source | +142 to +152 | LiberationSans 9, muted, place + source (two lines: place, then source — V4 pattern) |

### Mini stories 5–16

| # | Headline | Place / source | Miniature subject (redesign V4's 56×56 at 154×76) |
|---|---|---|---|
| 5 | GTA VI launches after 13 years | Worldwide / Metacritic | Night city + controller + gold "99" badge |
| 6 | Third strike in a week hits Crimea Bridge | Kerch Strait / Reuters | Bridge arch + flame over water |
| 7 | Denmark backs Greenland deal 109-0 | Copenhagen / Military.com | Greenland landmass + "109–0" ballot slip |
| 8 | Cyclone Akvan nears India; 80,000+ moved | Odisha, India / The Hindu BusinessLine | Spiral cyclone + rain over coast |
| 9 | 551,864 sit Korea's Suneung exam | Seoul / Yonhap | Exam paper + pencil |
| 10 | Australia jobless rate hits 4.9%, a 5-year high | Sydney / ABS | Falling red line chart + briefcase + "4.9%" |
| 11 | Yunus home torched as Bangladesh burns | Dhaka / Reuters | House + roof flame |
| 12 | CLAIM: Iran says three tankers hit mines | Strait of Hormuz / IRNA / Reuters | Tanker + mine + flame on sea |
| 13 | Israel ends tank raid beyond Yellow Line | Nuseirat, Gaza / Devdiscourse | Tank on road |
| 14 | Houthi strike hits Riyadh's tallest tower | Riyadh / WSJ | Tapered tower + impact burst |
| 15 | Indonesia passes asset-seizure law after 18 years | Jakarta / Reuters | Document + gavel |
| 16 | Unions hold national strike against tax bill | Bogota, Colombia / Travelers Today | Crowd + megaphone |

---

## 6. Section D — World map + newswire (y=720–955)

### Headings

| Element | Position |
|---|---|
| Section tab | y=720–740, x=24–~330 (small tab, NOT full-width — full banner would collide with the headings) |
| "WHERE IT HAPPENED" | (28, 742), Sans-Bold 13, ink — inside the map frame, above the plot |
| "ALSO ON THURSDAY 19 NOVEMBER (34 stories, 3 cols)" | (440, 722), Sans-Bold 13, ink |

### World map — (24, 740, 396, 212)

- Map frame: x=24–420, y=740–952. Ocean fill light blue (210,228,240).
- Map plot (continents + pins): x=30–414, y=758–918.
- Projection: equirectangular, 1.0667 px/deg. Longitude −180..180 → x 30..414.
  Latitude 90..−60 → y 758..918.
- Continents: tan fill (222,205,165), thin darker outline. Schematic outlines are
  in the wireframe generator; the final render must use recognisable coastline
  shapes (refine the polygons — do not ship the wireframe's rough blobs as-is
  if they read as blobs; Greenland in V4 read as a stylised blob and was called out).
- Legend (inside map frame, below the plot): y=922 "Pins 1-16 match illustrated
  stories 1-16. Regions: Asia, Europe," / y=934 "N. America, LatAm, Africa,
  M. East, Oceania. Equirect. 1.07 px/deg." (Sans 10 / muted).

### Map pins — numbered 1–16 (red badge, white number, 16px diameter)

The DOT sits at the true projected coordinate. In dense clusters the number
BADGE is offset by a leader line (thin red 1px line from dot to badge).
Badge spacing verified ≥14px (badge-to-badge and badge-to-other-dot).

| Pin | Story (place) | lat, lon | Dot (x, y) | Badge (x, y) | Leader offset |
|---|---|---|---|---|---|
| 1 | Summit (Shenzhen) | 22.54, 114.06 | (344, 830) | (344, 830) | — |
| 2 | ICJ (The Hague) | 52.07, 4.32 | (227, 798) | (211, 788) | (−16, −10) |
| 3 | COP31 (Antalya) | 36.91, 30.71 | (255, 815) | (237, 815) | (−18, 0) |
| 4 | Anthropic (New York) | 40.71, −74.01 | (143, 811) | (129, 801) | (−14, −10) |
| 5 | GTA VI (Miami / Vice City) | 25.76, −80.19 | (136, 827) | (122, 837) | (−14, +10) |
| 6 | Crimea Bridge (Kerch Strait) | 45.35, 36.47 | (261, 806) | (261, 790) | (0, −16) |
| 7 | Greenland deal (Copenhagen) | 55.68, 12.57 | (235, 795) | (249, 779) | (+14, −16) |
| 8 | Cyclone Akvan (Gopalpur, Odisha) | 19.27, 84.92 | (313, 833) | (329, 841) | (+16, +8) |
| 9 | Suneung (Seoul) | 37.57, 126.98 | (357, 814) | (357, 814) | — |
| 10 | Australia jobs (Sydney) | −33.87, 151.21 | (383, 890) | (383, 890) | — |
| 11 | Yunus home (Dhaka) | 23.81, 90.41 | (318, 829) | (300, 815) | (−18, −14) |
| 12 | Tankers (Strait of Hormuz) | 26.57, 56.25 | (282, 826) | (298, 838) | (+16, +12) |
| 13 | Gaza raid (Nuseirat) | 31.45, 34.39 | (259, 820) | (245, 834) | (−14, +14) |
| 14 | Riyadh tower (Riyadh) | 24.71, 46.68 | (272, 828) | (272, 844) | (0, +16) |
| 15 | Asset-seizure law (Jakarta) | −6.21, 106.85 | (336, 861) | (336, 861) | — |
| 16 | Colombia strike (Bogota) | 4.71, −74.07 | (143, 849) | (143, 849) | — |

Notes:
- Pin 5 (GTA VI) is "Worldwide" in the dataset; pinned at Miami (Vice City,
  the game's setting) — document this choice in the render; do not claim the
  pin is Rockstar HQ.
- Dense clusters needing leaders: NW Europe (2, 7), E. Med / Black Sea (3, 6, 13),
  Gulf (12, 14), S. Asia (8, 11), US East (4, 5). True dots never move.

### Newswire — (436, 740, 564, 212)

- 34 stories (17–50), 3 columns, 17px pitch, single-line items:
  "`N. headline — place — source`" (Sans-Bold 10), trimmed to column width.
- Columns: col 1 x=436–619 (w=183, items 17–28, 12 items); col 2 x=627–810
  (w=183, items 29–39, 11 items); col 3 x=818–1000 (w=182, items 40–50, 11 items).
- First item y=742; last item ends y≈939–941 (within the 952 bottom edge).
- Column labels at the bottom ("col 1: 12 items" etc.) are wireframe-only;
  do NOT render them in the final image.
- Items 17–50 are exactly the `also` list in news.json (in order).

---

## 7. Section E — Date check and sources (y=960–1024)

| Element | y |
|---|---|
| Rule | 960, x=24–1000, 1px |
| L1 — Sources | 988: "Sources: Reuters · AP · White House · ICJ · WSJ · CNN · GOV.UK · national wires." |
| L2 — Date check | 1000: "Date-checked: 7 Wed-dated stories removed — Van Gogh sale, IAEA Yongbyon, US-Venezuela pact, ..." (full list from news.json `left_out`) |
| L3 — Integrity | 1012: "CLAIM = unverified claim, never fact. All 50 stories happened or were first reported Thu 19 Nov 2026." |

All Sans 9, muted, trimmed to content width 976. Lines end ≈1006–1021, inside the band.

---

## 8. Deviations from Bram's V5 binding numbers

NONE in geometry. Every section band, card count, grid shape, and the
≥90px hero-illustration minimum is met exactly as specified. Documented
interpretations (not deviations):

1. Hero illustration height is 120px, not 90px — the directive sets 90px as a
   MINIMUM; 120px is chosen to fix V4's "too shallow and visually weak" failure.
2. The section-D label is a small tab, not a full-width banner — the full banner
   collided with the "WHERE IT HAPPENED" / "ALSO ON..." headings at y=722.
   (Fixed after visual inspection of wireframe v1; the tab is a wireframe
   annotation, not part of the final image.)
3. Newswire items are single-line ("N. headline — place — source", 17px pitch).
   The directive says "compact newspaper columns" without a line count; two-line
   items do not fit 34 stories in 212px at readable sizes (12 items × 22px =
   264px > 212px). Single-line items at 17px pitch fit with room (last ends y≈941).
4. Pin 5 (GTA VI, "Worldwide") is placed at Miami (Vice City setting) — see §6.
5. The map plot is y=758–918 (not 740–952): the heading occupies y=742–755 and
   the legend y=922–946 inside the frame. The plot keeps the 1.0667 px/deg scale.

## 9. Deviations from the Nov 17 reference (structure)

See §1. The reference is used for STYLE (masthead, ticker, card style, map
style, footer), not structure. The V5 binding geometry overrides the
reference's 3×6 card grid and its ≈792–983 map band.

---

## 10. Verification (wireframe stage)

Generator: `/tmp/gen_wireframe.py`. **37 assertions, 37 pass, 0 fail.**

- Sections within canvas, in order, no overlap.
- Exactly 4 hero columns, equal width (238), spanning full content width;
  hero illustration height 120px (≥90); all four share baseline y=266;
  hero card height 245 = band height.
- Mini grid exactly 6×2 = 12 cards, 156×156, spanning full content width;
  all 12 illustration panels identical 154×76.
- Stories accounted: 4 + 12 + 34 = 50.
- Map present: 396×212 at (24, 740); all 16 pins inside the plot.
- Badge spacing ≥14px (badge-to-badge and badge-to-other-dot) — 5 close dot
  pairs resolved with leader offsets (see §6). True dots unmoved.
- Newswire: 3 columns, 12/11/11 = 34, last item ends y≈939 ≤ 952.
- Footer: 3 lines end y≈1006 ≤ 1024.
- Visual inspection of the wireframe PNG (two passes): no overlapping labels
  after fixes (section-D heading collision and hero/mini dimension-note
  collisions found in v1 and fixed in v2; final SHA-256 below).

Wireframe file: `~/workspace/makefun/ni19-v3/v5-wireframe.png`
(1024×1024, SHA-256 `af73b5c6ed4a8092f95478683125373c050c986380cdd19293bf5860b77b4537`).

---

## 11. Notes for the render stage (final V5 image — NOT this stage)

- Reuse V4's `render.py` helpers (wrap/fit_lines/trim_one/chip/num_badge), fonts
  (DejaVuSerif-Bold, LiberationSans), and palette (PAPER/CARD/INK/MUTED/RULE/
  RED/BLUE/TEAL/GOLD/SKY/SEA/GREEN/ORANGE/DARK). Keep `main.py` as the simple
  stdlib-only copy + SHA-256/size/dimension/PNG validation (the pattern that
  passes the server grade; do NOT rewrite it into a complex renderer).
- Redesign the 4 hero scenes at 236×120 and the 12 miniatures at 154×76 from
  the V4 scene functions (`hero_summit`, `hero_icj`, `hero_cop31`,
  `hero_anthropic`, `mini_*` in render.py) — scale the compositions up, do not
  merely stretch the 58px/56px art. Fix the known weak spots: summit scene
  (flat hills/lake, small table) and Greenland miniature (reads as a blob).
- Refine the continent polygons for the map (the wireframe's are schematic);
  keep the pin coordinates and leader offsets from §6 exactly.
- Headline discipline: hero headlines max 2 lines in 222px; mini headlines max
  3 lines in 140px; newswire single line in 182px — trim with ellipsis, never
  overflow or clip (mandatory acceptance test).
- Determinism: fixed seed, no network, no timestamps; render twice and compare
  SHA-256; run `makefun check` and the bundle validation before reporting.
- Provenance: keep the authentic agent history (V3 → V4 → V5 branch); do not
  fabricate transcripts. The V4 bundle fix (parent session via
  `--parent-session`) applies again if the run record complains.
- DO NOT SUBMIT. Report the V5 image preview + validation + weaknesses to the
  parent first; Bram decides after reviewing the final preview.
- If any visual acceptance test fails (hero columns ≠ 4 across; hero
  illustration < 90px; mini grid ≠ 6×2; mini illustration dimensions differ;
  map missing; < 50 stories; headline overlap/clip; empty illustration panel;
  section exceeds canvas), the build FAILS — fix it, do not declare GO.
