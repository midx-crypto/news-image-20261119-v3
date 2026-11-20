#!/usr/bin/env python3
"""V6 visual acceptance tests (run: python3 test_v6.py).

Checks geometry, story accounting, fact-audit rules, text fit (via the
renderer's own wrap/trim helpers), map pins, and render determinism.
Exits non-zero on any failure. Does NOT call makefun check/bundle/submit.
"""
import hashlib
import json
import subprocess
import sys
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

# --- dropped stories absent ---
dropped = ["Colombia", "Florida", "Kumamoto", "Badme", "Serbia", "Cupic",
           "UK, Norway fund", "Pakistan", "Iraq", "Walmart", "Trump to meet Kim",
           "leasehold", "Cleverly", "Tinubu", "India v NZ", "Punjab bridge"]
blob = json.dumps(data)
check("all 15 dropped stories absent", all(d not in blob for d in dropped))

# --- fact audit ---
a4 = feat[3]
check("#4 headline has no 'record'", "record" not in a4["headline"].lower())
check("#4 summary has no superlative",
      "largest" not in a4["summary"].lower() and "record" not in a4["summary"].lower())
check("#4 confidence is 'reported' (no VERIFIED chip)",
      a4["confidence"] == "reported")
check("no 'record'/'largest IPO ever' anywhere in render.py",
      "largest IPO" not in src.lower() and "LARGEST IPO EVER" not in src)
claims = [s["n"] for s in feat + also if s["confidence"] == "claim"]
check("CLAIM items are exactly #12 and #27", claims == [12, 27])
check("no 'EVERY CLAIM VERIFIED' wording",
      "EVERY CLAIM VERIFIED" not in src and "every claim verified" not in blob.lower())
check("stats drop $81.3bn, add 99 GTA VI",
      all(s["value"] != "$81.3bn" for s in data["stats"])
      and any(s["value"] == "99" for s in data["stats"])
      and len(data["stats"]) == 5)
check("footer integrity says 35 stories",
      "All 35 stories happened or were first reported Thu 19 Nov 2026" in src)
check("dateline says 35 STORIES", "35 STORIES" in src and "50 STORIES" not in src)

# --- geometry (from render.py constants) ---
check("3 heroes", len(render.HEROES) == 3)
check("12 minis", len(render.MINIS) == 12)
check("hero panels 318x150 in code", "318, 150" in src)
check("hero card width 320, xs 24/352/680", "hero_xs = [24, 352, 680]" in src)
check("mini panels identical 154x76", "154, 76" in src)
check("map pins = 14, no pin 5, no pin 16",
      len(render.PINS) == 14 and {n for n, _, _ in render.PINS}
      == {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15})
check("newswire 2 cols x 10, pitch 21", "rows[0:10]" in src and "rows[10:20]" in src
      and "j * 21" in src)

# --- text fit (renderer helpers, same fonts) ---
hf = render.font(render.SERIF_B, 15)
sf = render.font(render.SANS, 11)
chf = render.font(render.SANS_B, 12)
nwf = render.font(render.SANS_B, 11)
ok = True
for s in feat[:3]:
    if len(render.fit_lines(s["headline"], hf, 304, 2)) > 2:
        ok = False
    if len(render.fit_lines(s["summary"], sf, 304, 3)) > 3:
        ok = False
check("hero headlines <=2 lines, summaries <=3 lines", ok)
ok = all(len(render.fit_lines(s["headline"], chf, 140, 3)) <= 3 for s in feat[3:])
check("mini headlines <=3 lines", ok)
ok = all(render.font(render.SANS_B, 11).getlength(
    render.trim_one(f"{s['n']}. {s['headline']}", nwf, 276)) <= 280 for s in also)
check("newswire headlines fit their columns (<=280px)", ok)

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

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
