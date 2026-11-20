#!/usr/bin/env python3
"""V7 visual acceptance tests (run: python3 test_v7.py).

Checks geometry, story accounting, the Africa/LatAm swap, the V7 fact
audit fixes, text fit (via the renderer's own wrap helpers), map pins
(colour-coded, badge spacing), and render determinism.
Exits non-zero on any failure. Does NOT call makefun check/bundle/submit.
"""
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402  (importing render.py runs no drawing)

passed = failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS {name}")
    else:
        failed += 1
        print(f"FAIL {name} {detail}")


data = json.loads((HERE / "news.json").read_text())
src = (HERE / "render.py").read_text()

# --- story accounting ---
feat, also = data["featured"], data["also"]
check("35 stories total", data["stories_total"] == 35 and len(feat) + len(also) == 35)
check("heroes 1-3", [s["n"] for s in feat[:3]] == [1, 2, 3])
check("minis 4-15", [s["n"] for s in feat[3:]] == list(range(4, 16)))
check("newswire 16-35", [s["n"] for s in also] == list(range(16, 36)))
check("3+12+20 = 35", len(feat[:3]) == 3 and len(feat[3:]) == 12 and len(also) == 20)

# --- Africa / Latin America swap ---
regions = Counter(s["region"] for s in feat + also)
check("region counts Asia 10 / Europe 11 / NAm 5 / ME 5 / Africa 2 / Oceania 1 / LatAm 1",
      regions == {"Asia": 10, "Europe": 11, "North America": 5, "Middle East": 5,
                  "Africa": 2, "Oceania": 1, "Latin America": 1}, str(regions))
feat_regions = Counter(s["region"] for s in feat)
check("illustrated set covers all 7 regions",
      set(feat_regions) == {"Asia", "Europe", "North America", "Latin America",
                            "Africa", "Middle East", "Oceania"}, str(feat_regions))
by_n = {s["n"]: s for s in feat + also}
check("#11 is Jepchirchir (Nairobi, Africa), illustrated",
      by_n[11]["headline"] == "Jepchirchir banned 3y, EPO"
      and by_n[11]["region"] == "Africa" and by_n[11] in feat)
check("#15 is Hegseth (Quito, Latin America), illustrated",
      by_n[15]["headline"] == "Hegseth in Ecuador, Honduras"
      and by_n[15]["region"] == "Latin America" and by_n[15] in feat)
check("Yunus home + Gaza tank raid demoted to newswire",
      by_n[16]["headline"].startswith("Yunus home")
      and by_n[17]["headline"].startswith("Israel ends tank raid"))

# --- V7 fact-audit fixes ---
check("#19 Han headline rewritten (overturned, retrial)",
      by_n[19]["headline"] == "Top court overturns Han's 15y term, orders retrial"
      and "partly cut" not in json.dumps(data).lower())
check("#18 Mongolia sharpened (parliament accepts president's resignation)",
      by_n[18]["headline"] == "Mongolia parliament accepts president's resignation")
check("#27 Houthis keeps CLAIM + 'over two days'",
      by_n[27]["headline"] == "CLAIM: Houthis: 10 killed in Sanaa over two days"
      and by_n[27]["confidence"] == "claim")
check("#28 Gaza reworded (no 'IDF kills five')",
      by_n[28]["headline"] == "Five more deaths recorded in Gaza in 24h"
      and "IDF kills five" not in json.dumps(data))
check("#14 asset-seizure summary tightened (fled/died/ill/unknown)",
      "fled, died, is ill or unknown" in by_n[14]["summary"])
check("stats typo fixed: 'S. Korea', no 'Sit Korea'",
      any(s["label"] == "S. Korea's Suneung exam" for s in data["stats"])
      and "Sit Korea" not in json.dumps(data))
check("#12 stays CLAIM-labelled",
      by_n[12]["headline"].startswith("CLAIM:") and by_n[12]["confidence"] == "claim")
claims = [s["n"] for s in feat + also if s["confidence"] == "claim"]
check("CLAIM items are exactly #12 and #27", claims == [12, 27])
a4 = feat[3]
check("#4 headline has no 'record'", "record" not in a4["headline"].lower())
check("#4 summary has no superlative",
      "largest" not in a4["summary"].lower() and "record" not in a4["summary"].lower())
check("#4 confidence is 'reported' (no VERIFIED chip)", a4["confidence"] == "reported")
check("no 'EVERY CLAIM VERIFIED' wording",
      "EVERY CLAIM VERIFIED" not in src and "every claim verified" not in json.dumps(data).lower())
check("footer integrity says 35 stories",
      "All 35 stories happened or were first reported Thu 19 Nov 2026" in src)

# --- masthead / trust devices ---
check("dominant date masthead in code", '"Thursday 19 November 2026"' in src
      and "SERIF_B, 52" in src)
check("region strip in code (7 colour tabs, live counts)",
      "REGION_STRIP_ORDER" in src and "REGION_COLORS" in src
      and "Counter(" in src)
check("DATE CHECK red-bordered box in code",
      '"DATE CHECK"' in src and "outline=RED, width=2" in src)
check("hero navy title bands in code",
      "APEC 2026" in src and "WORLD COURT" in src and "COP31" in src
      and "fill=NAVY" in src)
check("mini label strips in code (all 12)",
      all(f"MINI_STRIP[{n}]" in src or f"MINI_STRIP[{n}]" in src for n in range(4, 16))
      and len(render.MINI_STRIP) == 12)
check("no tofu glyphs drawn as text (no U+2605/U+2713 text draws)",
      "\\u2605" not in src and "\\u2713" not in src
      and "\u2605" not in src and "\u2713" not in src)
check("CUT stamp in COP31 hero", '"CUT"' in src and "rotate(-18" in src)

# --- geometry (from render.py constants) ---
check("3 heroes", len(render.HEROES) == 3)
check("12 minis", len(render.MINIS) == 12 and sorted(render.MINIS) == list(range(4, 16)))
check("hero panels 318x150 in code", "318, 150" in src)
check("hero card width 320, xs 24/352/680", "hero_xs = [24, 352, 680]" in src)
check("mini panels identical 154x76", "154, 76" in src)
check("map pins = 14, no pin 5",
      len(render.PINS) == 14 and {n for n, _, _, _ in render.PINS}
      == {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15})
check("pin regions match story regions",
      all(render.REGION_COLORS[r] and by_n[n]["region"] == r
          for n, _, _, r in render.PINS))
badges = [(n, b) for n, _, b, _ in render.PINS]
ok = True
for i, (n1, b1) in enumerate(badges):
    for n2, b2 in badges[i + 1:]:
        if math.dist(b1, b2) < 16:
            ok = False
            print(f"   badge collision risk: {n1} {b1} vs {n2} {b2}")
check("all map badge pairs >=16px apart", ok)
check("newswire 2 cols x 10, pitch 20", "rows[0:10]" in src and "rows[10:20]" in src
      and "j * 20" in src)

# --- text fit (renderer helpers, same fonts) ---
hf = render.font(render.SERIF_B, 15)
sf = render.font(render.SANS, 11)
chf = render.font(render.SANS_B, 12)
csf = render.font(render.SANS, 8.5)
ok = True
for s in feat[:3]:
    if len(render.wrap(s["headline"], hf, 304)) > 2:
        ok = False
    if len(render.wrap(s["summary"], sf, 304)) > 3:
        ok = False
check("hero headlines wrap <=2 lines, summaries <=3 lines", ok)
ok = all(len(render.wrap(s["headline"], chf, 140)) <= 2 for s in feat[3:])
check("mini headlines wrap <=2 lines at 12px bold", ok)
ok = all(len(render.wrap(s["summary"], csf, 140)) <= 3 for s in feat[3:])
check("mini summaries wrap <=3 lines at 8.5px", ok)
ok = True
for s in also:
    raw = f"{s['n']}. {s['headline']}"
    colw = 276 if s["n"] <= 25 else 280
    size = 11
    while size > 9 and render.font(render.SANS_B, size).getlength(raw) > colw:
        size -= 0.5
    if render.font(render.SANS_B, size).getlength(raw) > colw:
        ok = False
check("newswire headlines fit their columns at adaptive 11-9.5px", ok)
ff = render.font(render.SANS, 9)
f1 = ("Sources: Reuters \u00b7 AP \u00b7 White House \u00b7 ICJ \u00b7 WSJ \u00b7 CNN \u00b7 GOV.UK \u00b7 national wires.  "
      "CLAIM = unverified claim, never fact. All 35 stories happened or were first reported Thu 19 Nov 2026.")
check("footer line fits 976px", ff.getlength(f1) <= 976, f"({ff.getlength(f1):.0f}px)")
mf = render.font(render.SERIF_B, 52)
check("date masthead fits 976px", mf.getlength("Thursday 19 November 2026") <= 976,
      f"({mf.getlength('Thursday 19 November 2026'):.0f}px)")

# --- main.py untouched vs v6 ---
r = subprocess.run(["git", "diff", "v6", "--", "main.py"], cwd=HERE,
                   capture_output=True, text=True)
check("main.py untouched vs v6", r.stdout.strip() == "")

# --- rendered file ---
png = HERE / "entry.png"
check("entry.png exists", png.exists())
if png.exists():
    import struct
    raw = png.read_bytes()
    check("PNG <= 1 MiB", len(raw) <= 1048576, f"({len(raw)} bytes)")
    w, h = struct.unpack(">II", raw[16:24])
    check("PNG is 1024x1024", (w, h) == (1024, 1024))

# --- determinism: render twice, compare SHA-256 ---
h1 = hashlib.sha256(png.read_bytes()).hexdigest()
subprocess.run([sys.executable, "render.py"], cwd=HERE, check=True,
               capture_output=True)
h2 = hashlib.sha256(png.read_bytes()).hexdigest()
check("render is deterministic (identical SHA-256)", h1 == h2, f"{h1} vs {h2}")

# --- main.py entrypoint still validates the render ---
r = subprocess.run([sys.executable, "main.py"], cwd=HERE, capture_output=True,
                   text=True, env={"MAKEFUN_OUTPUT_DIR": "/tmp/v7-main-out",
                                   "PATH": "/usr/bin:/bin"})
check("main.py copies + validates entry.png", r.returncode == 0, r.stderr.strip()[-200:])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
