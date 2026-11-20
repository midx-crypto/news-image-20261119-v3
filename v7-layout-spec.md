# V7 Layout Specification — news-image-20261119

**Status:** FINAL RENDER. No submission (coordinator bundles + checks).
**Branch:** `v7` (from V6 commit `3d5c27c`). V5 (`2fd510f`) and V6 stay
untouched as rollback checkpoints.
**Render:** `entry.png` (1024×1024, SHA-256
`9fef8ced4d9d19b053d675cc2428b4794f22ab30ec046cab923030bca11eb706`,
219,919 bytes). Renderer: `render.py` (Pillow, fixed seed, no network).
**Entrypoint:** `main.py` UNTOUCHED (proven stdlib-only copy + validation;
`git diff v6 -- main.py` is empty).
**Dataset:** `news.json`, V6's 35 stories renumbered after the swap (§2).
**Acceptance tests:** `test_v7.py` (51/51 pass).
**Deadline:** entries close 21 Nov 07:00 WIB.
**Audits applied:** `v7-competitor-audit.md` (top-3: hazel-harbor-63
992344, izayoi-20 992290, push-limits 992235) and `v7-fact-audit.md`
(31 CONFIRMED / 3 ATTRIBUTED / 1 WRONG).

---

## 1. Geometry changes vs V6 (with reasons)

Canvas 1024×1024, margin 24, content width 976 (x=24–1000). Section
bands kept from V6: header 0–140, heroes 145–390, minis 395–715,
map + newswire 720–955, footer 960–1024.

| Change | V6 | V7 | Reason |
|---|---|---|---|
| Masthead | "THE WORLD IN ONE DAY" 42px serif title; date as small red caps subline | Eyebrow "THE WORLD IN ONE DAY" 12px red caps (y=8); date "Thursday 19 November 2026" 52px serif bold, largest type on the page (y=26, 872px wide) | Audit weakness 1: leaders make the date the masthead; V6 read as a generic infographic |
| Region strip | None (only tiny grey footer text) | Colour-coded tabs y=86–106: ASIA 10, EUROPE 11, N. AMERICA 5, MIDDLE EAST 5, AFRICA 2, LATIN AM. 1, OCEANIA 1; counts computed live from news.json (`Counter`); colours shared with map pins | Audit weakness 1: leaders prove coverage at a glance |
| Stat strip | 5 boxes y=98–134, value 15px / label 9px | 5 boxes y=110–138, value 13px / label 8px; typo fixed ("Sit Korea" → "S. Korea") | Room for the region strip above it |
| Hero panels | 318×150 scenes, no band | Same 318×150, plus a navy band across the bottom 16px (y+134–150): "APEC 2026 · SHENZHEN", "WORLD COURT · THE HAGUE", "COP31 · ANTALYA" | Audit weakness 2: leaders anchor heroes with navy title bands |
| Hero 1 Summit | Faceless beige heads, round table | Distinct faces: blond Trump (red tie), black-haired Xi, grey-haired Putin (blue tie); eyes + smiles; nameplates TRUMP / XI / PUTIN on the table front; same skyline/flags/banner | Audit weakness 2: leaders draw distinct faces + nameplates + summit banner |
| Hero 2 ICJ | Bare courthouse, oversized scales, faceless robed blobs | Red-brick Peace Palace: pitched roofs, central clock tower with working clock face, 4 arched windows, Myanmar flag (drawn white star), smaller scales in front, red 9–6 badge top-right, 2 small robed figures | Audit weakness 2: building itself must say where you are |
| Hero 3 COP31 | White document with struck-through words; flat globe | Landscape: hills + grey-blue wind turbine (white was invisible on pale sky in V6), globe + leaf, tall red thermometer, document with struck-through "FOSSIL FUELS" / "$120bn target", rotated red CUT stamp (−18°) | Audit weakness 2: same idea executed as a scene, not a form |
| Mini cards | Headline only (3 lines max), place + source on two lines | Category y+79; headline max 2 lines (12px bold, y+90); summary 1–3 lines (8.5px, y+116, 10px leading); one combined "place — source" line (8px, y+147) | Audit weakness 3: summaries existed in news.json but the render dropped them; headlines shortened where needed (see §2) |
| Mini panels | Generic icons, no in-image text except stray numbers | Black label strip along the bottom 13px of every panel (white 8px bold): IPO $83 · $81.3BN, GTA VI · OUT NOW, KERCH BRIDGE · RAIL HALTED, GREENLAND · 109–0, AKVAN · 90–100 KM/H, SUNEUNG · 551,864, 4.9% · 43,500 JOBS LOST, NAIROBI · 3 YEARS, CLAIM · 3 TANKERS, PIF TOWER · RIYADH, ASSET-SEIZURE · 18 YEARS, QUITO · HONDURAS; art raised clear of the strip | Audit weakness 4: leaders carry bold in-image wordmarks on every card |
| Mini 7 Greenland | White map blob + stray green square | Redrawn as a scene: two mountain ranges with snow caps, Danish + US flags, ballot slip "109–0" with a drawn red check | Audit weakness 4: weakest V6 illustration |
| Mini 9 Suneung | "9" badge covered the "S" of SUNEUNG; giant pencil dominated | Sheet carries answer bubbles only (no title text; the words live in the strip); pencil shrunk | Audit weakness 4: badge collision |
| Mini 15→14 gavel | "15" badge covered the "A" of ASSET-SEIZURE; thin gavel; "18 YEARS" tag crowded the corner | Document carries lines + Rp1bn+ + red seal only (title lives in the strip); gavel raised; separate "18 YEARS" tag removed (strip carries it) | Audit weakness 4: badge collision |
| Map pins | 14 identical red circles | 14 pins colour-coded by region (same colours as the strip: Asia orange, Europe blue, N. America purple, Middle East red, Africa green, Latin Am. gold, Oceania teal); leader lines + dots + badges all in the region colour | Audit weakness 5: leaders colour-code pins by region |
| Map pin 4 (New York) | (143, 811), sat inland over the Great Lakes area | (145, 812), on the coast | Audit weakness 5 |
| New pins | 11 Dhaka, 13 Nuseirat, 14 Riyadh, 15 Jakarta | 11 Nairobi (261, 855, Africa green), 15 Quito (138, 854, LatAm gold); 13 Riyadh badge moved to (284, 852) to keep ≥16px from the Nairobi badge | The swap (§2); all badge pairs verified ≥16px apart in test_v7.py |
| Newswire | 2 cols × 10, 21px pitch | 2 cols × 10, 20px pitch; headlines use an adaptive font (11px, shrinking to 9.5px) so the two longest headlines fit whole instead of truncating | #18 (293px at 11px) and #19 (277px) truncated with "…" in the first V7 render; shrinking 1–1.5px keeps the audit-required wording intact |
| Footer / date check | 3 lines of small grey text | Bold red-bordered DATE CHECK box (y=960–1008, CARD fill, 2px red border): "DATE CHECK ✓" (check drawn with lines — the ✓ glyph is tofu in Liberation Sans) + 2 lines naming the 7 excluded Wed-dated stories; one combined sources + CLAIM + integrity line below (y=1013) | Audit weakness 5: leaders show their verification in a bold box; V6 whispered it |
| Glyph policy | ★ (U+2605) and ✓ (U+2713) drawn as font text | Both replaced by drawn geometry: `star()` 5-point polygon helper (China + Myanmar flags); checks drawn as polylines (ballot slip, DATE CHECK title) | Both glyphs render as hollow rectangles (tofu) in Liberation Sans; caught on 2x zoom inspection |

---

## 2. Story selection (exact, renumbered 1–35)

Heroes: 1 Summit, 2 ICJ, 3 COP31 (unchanged).
Minis: 4 Anthropic, 5 GTA VI, 6 Crimea Bridge, 7 Greenland, 8 Akvan,
9 Suneung, 10 Australia jobs, **11 Jepchirchir (promoted from #16)**,
12 CLAIM tankers, 13 Riyadh tower, **14 asset-seizure law**,
**15 Hegseth (promoted from #22)**.
Newswire 16–35: 16 Yunus home (demoted), 17 Gaza tank raid (demoted),
18 Mongolia, 19 Han, 20 Zelensky/Berlin, 21 French left, 22 Somalia/UAE,
23 Kyiv drones, 24 S&P 500, 25 IEA Hormuz, 26 Spain migrants,
27 CLAIM Houthis/Sanaa, 28 Gaza deaths, 29 Trump on Iran, 30 Kim Keon Hee,
31 Senate 51-48, 32 EU cyberattack, 33 China unis/Nvidia,
34 Japan-India defence, 35 Dutch/Russian ambassador.

Swap rationale (audit weakness 5): V6 illustrated zero Africa and zero
Latin America. Promoting the two strongest available stories from those
regions (a sport story and a diplomacy story — the leaders also
illustrate sport) and demoting two Asia/Middle-East minis leaves the
illustrated set covering all 7 regions: Asia 4, Europe 4, N. America 2,
Middle East 2, Africa 1, Latin America 1, Oceania 1. Total stays 35
(3+12+20); region totals: Asia 10, Europe 11, N. America 5,
Middle East 5, Africa 2, Oceania 1, Latin America 1.

Headline shortenings (minis only, facts preserved; summaries carry the
dropped detail): #6 "Third strike in a week hits Crimea Bridge" →
"Third strike hits Crimea Bridge" (summary: "Third attack in a week…");
#8 "Cyclone Akvan nears India; 80,000+ moved" → "Cyclone Akvan nears
India" (summary carries 80,000+); #10 "…a 5-year high" → "Australia
jobless rate hits 4.9%" (summary carries "5-year high; 43,500 jobs
lost"); #13 "…Riyadh's tallest tower" → "Houthi strike hits Riyadh
tower" (summary: "80-storey PIF Tower"); #14 "…law after 18 years" →
"Indonesia passes asset-seizure law" ("18 years" lives in the label
strip and the summary). All mini headlines wrap ≤2 lines at 12px bold
and all mini summaries wrap ≤3 lines at 8.5px (asserted in test_v7.py).

---

## 3. Fact-audit fixes (v7-fact-audit.md)

- **#19 Han (MUST-FIX):** "Han 15y term partly cut" → "Top court
  overturns Han's 15y term, orders retrial" (Supreme Court overturned
  the 15-year sentence entirely on 19 Nov; the 23y→15y cut was 7 May).
- **#18 Mongolia:** "Mongolia leader resigns" → "Mongolia parliament
  accepts president's resignation" (19 Nov hook is the parliamentary
  acceptance of President Khurelsukh's resignation).
- **#27 Houthis:** "CLAIM: Houthis: 10 killed in Sanaa over two days"
  (added "over two days"; CLAIM label kept).
- **#28 Gaza:** "IDF kills five across Gaza" → "Five more deaths
  recorded in Gaza in 24h" (only 2 newly killed; Gaza Health Ministry
  attribution kept).
- **#14 asset-seizure summary:** "…seizable without conviction only
  if suspect fled, died, is ill or unknown" (no-conviction route is
  limited to those circumstances).
- **Stats typo:** "Sit Korea's Suneung exam" → "S. Korea's Suneung exam".
- Kept as-is: #12 and #27 CLAIM-labelled; #5 "151 critic reviews";
  #7 109–0; all other verified figures.

---

## 4. Illustrations (new / redesigned in V7)

- Hero 1: faces/hair/nameplates/ties per leader; table flattened to
  end at panel y+132 (band below); papers + nameplates on the table.
- Hero 2: brick courses, arched windows with white frames, clock tower
  with clock face + hands, door behind the (smaller) scales, steps,
  Myanmar flag, red 9–6 badge clear of the VERIFIED chip.
- Hero 3: hills, grey-blue turbine, globe + leaf, red thermometer with
  bulb + ticks, CUT stamp (rotated −18°, pasted via `d._image`).
- Mini 11 runner (NEW): red track + lane line, stick-figure runner
  mid-stride, red BANNED stamp, Kenyan flag (black/white/red/white/
  green stripes).
- Mini 15 jet (NEW): side-view jet (thin fuselage, tail fin, swept wing
  below, nose cone, windows), US + Ecuador flags, runway with dashes.
- `mini_house` (Yunus) and `mini_tank` (Gaza raid) stay defined in
  render.py but are no longer in `MINIS` (demoted to the newswire).
- Label strips: `label_strip()` draws a fitted black rect along the
  bottom 13px of each mini panel; all mini art was raised clear of
  that band (bars end y+60, controller y+42–62, boat y+44–60, houses
  y+50–64, briefcase y+40–62, tanker water lines ≤y+61, tower base
  y+64, gavel base y+60, runner track y+56–63, runway y+52–63).

---

## 5. Verification

`test_v7.py`: **51 assertions, 51 pass, 0 fail** — story accounting
(3+12+20=35), the swap (all 7 regions illustrated, region counts),
all six fact fixes, CLAIM set exactly {12, 27}, #4 audit rules,
masthead/region-strip/DATE CHECK/bands/strips present in code, no tofu
glyphs, geometry constants, map pins (14, regions match stories, all
badge pairs ≥16px), text fit via the renderer's own helpers (hero
headlines ≤2 lines, summaries ≤3; mini headlines ≤2, summaries ≤3;
newswire headlines fit at adaptive 11–9.5px; footer line ≤976px; date
masthead ≈840px ≤976px), `main.py` untouched vs v6, PNG 1024×1024 ≤
1 MiB, render determinism, `main.py` copy + validate.

Determinism: `render.py` run twice → identical SHA-256
`9fef8ced…eb706`. `main.py` run to a test output dir → identical bytes
(219,919 bytes, 1024×1024).

Visual inspection (full image at native size + 2x crops of all 3 heroes,
both mini rows, map, newswire, DATE CHECK box): exactly 3 hero columns
in one row; hero panels 150px with navy bands; minis exactly 6×2 with
identical panels, every card carrying a summary + label strip; the 3
badge collisions (cards 7, 9, 15 in V6) are gone; map present with
region-colour pins + GLOBAL legend; exactly 35 stories; no
overlap/clipping (two fixes applied after the first V7 render: newswire
headlines #18/#19 truncated → adaptive font shrink; ✓/★ tofu glyphs →
drawn geometry); no empty illustration panel; no section exceeds the
canvas.

---

## 6. Deliberately not done (for the coordinator)

- **"Day by hours" timeline** (audit action 5d): no free space without
  cutting stories or shrinking the map/newswire; the DATE CHECK box +
  region strip + colour pins are the V7 ownable devices instead.
- **One-line newswire** (audit action 5e): rejected — the two longest
  audit-required headlines (#18, #19) do not fit one line with
  place/source at any readable size; the two-line list is kept and the
  DATE CHECK box lives in the footer zone instead of above it.
- **Mini 8 meta truncation:** "Odisha, India — The Hindu…" still trims
  ("The Hindu BusinessLine" is too long for 140px at 8px); honest
  ellipsis, left as-is.
- **`main.py` docstring** still says "V5 final render / 50 stories" —
  left untouched per the brief (do not rewrite it); it validates only
  size/dimensions/PNG well-formedness, so V7 passes as-is.
- **Top-3 leader images** were not available locally (the audit worker
  downloaded them to its own session); V7 was built from the audit's
  written descriptions + V6, not from a side-by-side pixel comparison
  with the leaders. The coordinator may still do a final eyeball
  against the live leaderboard artifacts before submitting.
