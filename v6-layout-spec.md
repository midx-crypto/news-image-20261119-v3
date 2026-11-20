# V6 Layout Specification — news-image-20261119

**Status:** FINAL RENDER. No submission (coordinator validates).
**Branch:** `v6` (from V5 commit `2fd510f`). V5 stays intact on branch `v5`.
**Render:** `entry.png` (1024×1024, SHA-256
`914f78146155682e243b429b7aee1b1e2d7cda9c2be81ac78fc7e2496fb4fbf9`,
187,388 bytes). Renderer: `render.py` (Pillow, fixed seed, no network).
**Entrypoint:** `main.py` UNTOUCHED (proven stdlib-only copy + validation).
**Dataset:** `news.json`, the V5 50-story dataset reduced to the exact V6
35-story selection (see §2). Acceptance tests: `test_v6.py` (29/29 pass).
**Deadline:** entries close 21 Nov 07:00 WIB.

---

## 1. Geometry changes vs V5 (with reasons)

Canvas 1024×1024, margin 24, content width 976 (x=24–1000). Section bands
unchanged from V5: header 0–140, heroes 145–390, minis 395–715,
map + newswire 720–955, footer 960–1024. Gaps 5px between sections.

| Change | V5 | V6 | Reason |
|---|---|---|---|
| Hero count | 4 columns × 238 wide | 3 columns × 320 wide (x=24, 352, 680), 8px gaps | Bram's V6 directive: 3 heroes in one row |
| Hero illustration panel | 236×120, baseline y=266 | 318×150, baseline y=296 | Wider/taller panels use the freed width for richer scenes; 150px is well above the ≥90px minimum |
| Hero text block | headline y+127, summary y+165, category y+223 | headline y+157 (2 lines, 16px leading, 304px wide), summary y+193 (3 lines, 13px leading), category y+234 | Reflowed for the taller panel; verified by fit test (headlines ≤2 lines, summaries ≤3) |
| Mini stories | 5–16 | 4–15 | Anthropic moves from hero 4 to mini 4; Colombia strike (#16) dropped |
| Mini grid | 6×2, cards 156×156, panels identical 154×76 | UNCHANGED | Approved V5 grid kept as-is |
| Newswire | 34 items, 3 cols, headline Bold 9 / meta 8, 17px pitch | 20 items, 2 cols × 10 (col 1 x=436–712, col 2 x=720–1000), headline Bold 11 / meta 9, 21px pitch, first item y=738, last meta ends ≈947 | Fewer items allow the larger type Bram asked for; two lines per item keep headline + place + source fully visible |
| Newswire heading | "ALSO ON THURSDAY 19 NOVEMBER (34 stories, 3 cols)" | "(20 stories, 2 cols)" | Count/column update |
| Map pins | 15 geographic pins (1–4, 6–16) | 14 geographic pins (1–4, 6–15); pin 16 (Bogota) dropped with its story | Story dropped; pin 5 (GTA VI, "Worldwide") still has NO geographic dot |
| Map legend | "Pins 1–16 match stories 1–16. Asia, Europe, N. Am., LatAm, Africa, M. East, Oceania." | "Pins 1–15 match stories 1–15. Asia, Europe, N. Am., Africa, M. East, Oceania." + GLOBAL badge 5: "GLOBAL: GTA VI (story 5) is worldwide — no map dot." | LatAm drops out with the Colombia story; never pin a fictional setting as a real location |
| Stat strip | 9-6 ICJ, $81.3bn Anthropic, 551,864 Suneung, 80,000+ Akvan, 51-48 Senate | 9-6 ICJ, 99 GTA VI Metacritic, 551,864 Suneung, 80,000+ Akvan, 51-48 Senate | $81.3bn Anthropic stat DROPPED per directive |
| Dateline | "50 STORIES" | "35 STORIES" | Count update |
| Footer integrity | "All 50 stories happened or were first reported Thu 19 Nov 2026." | "All 35 stories happened or were first reported Thu 19 Nov 2026." | Count update; date-check line (7 Wed-dated stories removed) kept verbatim from V5 |
| Illustration count | 16 (4 heroes + 12 minis) | 15 (3 heroes + 12 minis) | One fewer hero; the render print's hardcoded "illustrations=16" was fixed to compute `len(HEROES)+len(MINIS)` |

All pin dot/badge coordinates are the V5 spec coordinates, unchanged
(remapped to the new numbers). Map frame, projection (1.0667 px/deg),
continent polygons, fonts, palette, and helpers are reused from V5.

---

## 2. Story selection (exact, renumbered 1–35)

Heroes: 1 Summit (Shenzhen/White House), 2 ICJ (The Hague/ICJ-HRW),
3 COP31 (Antalya/Reuters). Minis: 4 Anthropic (New York/Investopedia,
confidence `reported`), 5 GTA VI (Worldwide/Metacritic), 6 Crimea Bridge
(Kerch/Reuters), 7 Greenland deal (Copenhagen/Military.com), 8 Cyclone
Akvan (Odisha/The Hindu BusinessLine), 9 Suneung (Seoul/Yonhap),
10 Australia jobs (Sydney/ABS), 11 Yunus home (Dhaka/Reuters),
12 CLAIM tankers (Hormuz/IRNA-Reuters), 13 Gaza raid (Nuseirat/Devdiscourse),
14 Riyadh tower (Riyadh/WSJ), 15 asset-seizure law (Jakarta/Reuters).
Newswire 16–35: Jepchirchir, Mongolia leader, Han term, Zelensky/Berlin,
French left, Somalia/UAE, Hegseth, Kyiv drones, S&P 500, IEA Hormuz,
Spain migrants, CLAIM Houthis/Sanaa, IDF Gaza, Trump on Iran, Kim Keon Hee,
Senate 51-48, EU cyberattack, China unis/Nvidia, Japan-India defence,
Dutch/Russian ambassador.

Dropped (15, absent from `news.json` and the render): V5 #16 Colombia
strike; V5 newswire #20 Florida floods, #21 Kumamoto quake, #24 Badme CLAIM,
#26 Serbia speaker, #28 UK-Norway boats, #32 Pakistan CLAIM, #36 Iraq CLAIM,
#38 Walmart, #44 Trump-Kim, #46 UK leasehold, #47 Cleverly, #48 APGA Tinubu,
#49 India-NZ Test, #50 Punjab bridge.

---

## 3. Illustrations (redesigned, not stretched)

- Hero 1 Summit (318×150): Shenzhen skyline with tapered Ping An-style
  tower + lit windows, hills + lake, three flags (US/CN/RU) on poles,
  "DECLARATION TOWARD PEACE" banner as focal point, three seated leaders
  behind a large round table with papers.
- Hero 2 ICJ (318×150): courthouse pediment with red serif "9–6",
  six columns, four steps, large gold scales of justice in front, two
  robed figures flanking.
- Hero 3 COP31 (318×150): large draft document ("COP31 DRAFT",
  "FOSSIL FUELS" struck through in red, "$120bn target" struck through,
  "talks run to Friday"), globe + leaf at right, sun, wind turbine.
- Minis (154×76, identical panels): 4 Anthropic — NEW: rising bars,
  soaring red line + arrow, "$81.3bn" (moved to y+24 after the number
  badge was found covering the "$" in the first render), black
  "ANT $97.17 +17%" tag; NO "record"/"largest IPO ever" wording.
  5–15 reuse the V5 miniatures (GTA night city + gold 99; bridge arch +
  flame; Greenland outline + 109–0 ballot; cyclone spiral + rain; exam
  paper + pencil; falling red chart + 4.9% + briefcase; house + roof
  flame; tanker + mine + flame; tank on road; tapered tower + impact
  burst; document + gavel + "18 YEARS").

---

## 4. Fact-audit notes

- #4 Anthropic: headline "Anthropic debuts in $81.3bn IPO" (no "record"),
  summary drops "the largest IPO ever". Confidence set to `reported` in
  `news.json` (figures as reported by Investopedia only, no primary /
  exchange source named). NO VERIFIED chip anywhere; no superlative in
  the illustration either.
- VERIFIED chips kept on heroes 1 (White House, primary), 2 (ICJ, primary:
  the ruling), 3 (Reuters, observable draft document).
- CLAIM items are exactly #12 (Iran tankers) and #27 (Houthis/Sanaa),
  labelled CLAIM in headline and (minis) category. Nowhere does the image
  say "EVERY CLAIM VERIFIED".
- All visible claims rechecked against `news.json` headlines/summaries;
  no figure was added that is not in the dataset.

---

## 5. Verification

`test_v6.py`: **29 assertions, 29 pass, 0 fail** — story accounting
(3+12+20=35), all 15 dropped stories absent, #4 audit rules, CLAIM set
exactly {12, 27}, stats/dateline/footer counts, geometry constants,
text-fit via the renderer's own helpers (hero headlines ≤2 lines,
summaries ≤3, mini headlines ≤3, newswire headlines fit columns),
PNG 1024×1024 ≤ 1 MiB, render determinism.

Determinism: `render.py` run twice → identical SHA-256
`914f7814…bf9`. `main.py` run twice to two output dirs → identical bytes
(187,388 bytes, 1024×1024).

Visual inspection (full image at native size + crops of hero 1, mini 4,
map, newswire col 2): exactly 3 hero columns in one row; hero
illustrations 150px tall; minis exactly 6×2 with identical panels; map
present with recognisable outlines and 14 pins + GLOBAL legend badge;
exactly 35 stories; no overlap/clipping (one fix applied: mini 4 price
moved below the badge); no empty illustration panel; no section exceeds
the canvas.

---

## 6. Remaining weaknesses (for the coordinator)

- COP31 wind turbine is pale white on pale green and barely visible; the
  globe + leaf + document carry the scene, but the turbine adds little.
- Map: South America reads small and the Central America isthmus looks
  gapped at this scale (V5 polygons, unchanged); the Europe/Middle East
  pin cluster (2, 3, 6, 7, 12, 13, 14) is dense but all badges stay
  readable with their leader offsets.
- `main.py` docstring/error text still says "V5 final render / 50
  stories" — left untouched per the brief (do not rewrite it); the
  coordinator may update its wording. It validates only size/dimensions/
  PNG well-formedness, so V6 passes as-is.
- Mini 15's number badge touches the "A" of "ASSET-SEIZURE" on the
  document (cosmetic, same pattern as V5 minis).
