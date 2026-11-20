#!/usr/bin/env python3
"""Render 'The World in One Day' - Thu 19 Nov 2026 - as a 1024x1024 PNG.

V7 FINAL RENDER (branch v7, from V6 commit 3d5c27c). Binding geometry:
v7-layout-spec.md. Canvas 1024x1024. Header 0-140 (dominant date
masthead + colour-coded region-count strip + stats); 3 heroes ONE row
145-390 (cards 320x245, illustration panels 318x150 with navy title
bands, shared baseline y=296); 12 minis 6x2 395-715 (cards 156x156,
illustration panels IDENTICAL 154x76, each with a black in-image label
strip and a 1-3 line summary); map + newswire 720-955 (region-colour
map pins); DATE CHECK box in the footer zone 960-1024.

V7 changes vs V6 (documented in v7-layout-spec.md): dominant date
masthead + region strip; heroes redrawn (faces + nameplates + summit
banner; Peace Palace with clock tower + Myanmar flag; COP31 landscape
with globe + thermometer + red CUT stamp); minis gain summaries and
label strips and the 3 badge collisions are fixed; Africa (Jepchirchir)
and Latin America (Hegseth) promoted to illustrated minis, Yunus home
and the Gaza tank raid demoted to the newswire (renumbered 1-35);
fact fixes: Han headline rewritten, Mongolia sharpened, Houthis
"over two days", Gaza deaths reworded, asset-seizure summary tightened,
"Sit Korea" typo fixed; map pins colour-coded by region; DATE CHECK
promoted to a bold red-bordered box.

35 stories: 3 heroes + 12 minis + 20 newswire (V5 had 50; 15 dropped,
see v6-layout-spec.md). Stats strip: 9-6 ICJ, 99 GTA VI Metacritic,
551,864 Suneung, 80,000+ Akvan, 51-48 Senate (the $81.3bn Anthropic stat
is DROPPED).

Deterministic: fixed seed, no network, no timestamps, no random text.
Reads news.json beside this file, writes entry.png beside this file.
Pillow only (render-time dependency); the shipped main.py is stdlib-only.

V6 changes vs V5 (documented in v6-layout-spec.md):
1. Heroes: 4 -> 3 equal columns (320 wide); illustration panels 318x150
   (was 236x120), all three share baseline y=296. Hero scenes redesigned
   for the wider/taller panel. Anthropic moves from hero 4 to mini 4.
2. Minis: stories 4-15 (was 5-16); Colombia strike (#16) dropped.
   New mini_anthropic: chart + ticker + "$81.3bn", NO chip, NO "record" /
   "largest IPO ever" wording anywhere.
3. Newswire: 20 items, 2 columns x 10 (was 34 in 3 cols), LARGER type
   (headline Sans-Bold 11, place-source Sans 9, 21px pitch).
4. Map: 14 geographic pins (was 15 + GLOBAL badge). Pin 16 (Bogota)
   dropped with its story. Pin 5 (GTA VI, "Worldwide") still has NO
   geographic dot; the red "5" badge sits in the map legend with the text
   "GLOBAL: GTA VI (story 5) is worldwide - no map dot."
5. VERIFIED-chip audit: chips kept for heroes 1 (White House, primary),
   2 (ICJ, primary source: the ruling itself) and 3 (Reuters reporting an
   observable draft document). NO chip on #4 Anthropic: its core figures
   rest on a single secondary report (Investopedia) with no
   primary/exchange source named in the dataset. CLAIM items (12, 27)
   stay labelled CLAIM.
"""
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

random.seed(20261119)

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
MARGIN = 24
CW = W - 2 * MARGIN  # 976 content width

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# Palette: newsprint (kept from V4).
PAPER = (248, 244, 236)
CARD = (255, 253, 247)
INK = (25, 25, 25)
MUTED = (107, 100, 85)
RULE = (190, 182, 166)
RED = (158, 27, 27)
BLUE = (29, 78, 121)
TEAL = (14, 107, 92)
GOLD = (166, 124, 0)
SKY = (178, 205, 224)
SEA = (46, 111, 148)
GREEN = (46, 125, 50)
ORANGE = (204, 102, 0)
DARK = (38, 38, 38)
# Extra scene colours.
OCEAN = (205, 224, 238)
LAND = (222, 205, 165)
LAND_LINE = (170, 150, 110)
PALE_SKY = (216, 228, 238)
NIGHT = (36, 42, 64)
NAVY = (24, 42, 70)
# Region colours (V7): shared by the header region strip and the map pins.
REGION_COLORS = {
    "Asia": (204, 102, 0),
    "Europe": (29, 78, 121),
    "North America": (110, 60, 150),
    "Latin America": (150, 110, 30),
    "Africa": (46, 125, 50),
    "Middle East": (158, 27, 27),
    "Oceania": (14, 107, 92),
}
# Region counts computed from news.json (35 stories, V7 numbering):
# Asia 10, Europe 11, North America 5, Middle East 5, Africa 2,
# Oceania 1, Latin America 1. Computed live in main(); this dict is the
# display order for the strip.
REGION_STRIP_ORDER = ["Asia", "Europe", "North America", "Middle East",
                      "Africa", "Latin America", "Oceania"]
REGION_STRIP_LABEL = {"Asia": "ASIA", "Europe": "EUROPE",
                      "North America": "N. AMERICA", "Middle East": "MIDDLE EAST",
                      "Africa": "AFRICA", "Latin America": "LATIN AM.",
                      "Oceania": "OCEANIA"}


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, width):
    """Greedy word wrap; returns list of lines that fit `width` px."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, fnt, width, max_lines):
    """Wrap text to at most max_lines; ellipsize the last line if needed."""
    lines = wrap(text, fnt, width)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and fnt.getlength(lines[-1] + " \u2026") > width:
        lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
    lines[-1] = lines[-1] + " \u2026"
    return lines


def trim_one(text, fnt, width):
    """Trim a single line to fit, with an ellipsis."""
    if fnt.getlength(text) <= width:
        return text
    while text and fnt.getlength(text + "\u2026") > width:
        text = text.rsplit(" ", 1)[0] if " " in text else text[:-1]
    return text + "\u2026"


def chip(draw, x, y, text, fnt, fg, bg):
    """Small rounded label; returns its width."""
    pad = 5
    w = int(fnt.getlength(text)) + 2 * pad
    h = 15
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    draw.text((x + pad, y + 2), text, font=fnt, fill=fg)
    return w


def num_badge(draw, x, y, n, d=18):
    draw.ellipse([x, y, x + d, y + d], fill=INK)
    f = font(SANS_B, 11)
    t = str(n)
    tw = f.getlength(t)
    draw.text((x + (d - tw) / 2, y + 2), t, font=f, fill=(255, 255, 255))


def red_pin_badge(draw, x, y, n, d=16, fill=RED):
    """Map pin badge (white number); x, y are the badge centre.
    V7: fill is the story's region colour (default red)."""
    r = d // 2
    draw.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=(255, 255, 255), width=1)
    f = font(SANS_B, 10)
    t = str(n)
    tw = f.getlength(t)
    draw.text((x - tw / 2, y - 6), t, font=f, fill=(255, 255, 255))


def label_strip(d, x, y, w, h, text):
    """Black in-image label strip along the bottom of a mini panel
    (panel origin x, y; panel w x h). Fitted width, white bold text.
    The strip occupies the bottom 13px; mini art must keep that band
    clear of essential detail (bars/lines end above y+63)."""
    f = font(SANS_B, 8)
    bw = min(w, int(f.getlength(text)) + 12)
    d.rectangle([x, y + h - 13, x + bw, y + h], fill=INK)
    d.text((x + 6, y + h - 11), text, font=f, fill=(255, 255, 255))


def star(d, cx, cy, r, fill):
    """Five-point star polygon (drawn, not a font glyph: U+2605 renders
    as a hollow rectangle in Liberation Sans)."""
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


MINI_STRIP = {4: "IPO $83 \u00b7 $81.3BN", 5: "GTA VI \u00b7 OUT NOW",
              6: "KERCH BRIDGE \u00b7 RAIL HALTED", 7: "GREENLAND \u00b7 109\u20130",
              8: "AKVAN \u00b7 90\u2013100 KM/H", 9: "SUNEUNG \u00b7 551,864",
              10: "4.9% \u00b7 43,500 JOBS LOST", 11: "NAIROBI \u00b7 3 YEARS",
              12: "CLAIM \u00b7 3 TANKERS", 13: "PIF TOWER \u00b7 RIYADH",
              14: "ASSET-SEIZURE \u00b7 18 YEARS", 15: "QUITO \u00b7 HONDURAS"}


# ---------------------------------------------------------------- map
# Recognisable coastline outlines as (lon, lat) polygons. Equirectangular
# projection matching the spec: lon -180..180 -> x 30..414, lat 90..-60 ->
# y 758..918 (1.0667 px/deg). Pin dots in the spec were computed on exactly
# this projection, so the outlines must use the same one.

MAP_X0, MAP_Y0 = 30, 758
MAP_PX_DEG = 384.0 / 360.0  # 1.0667


def project(lon, lat):
    return (MAP_X0 + (lon + 180) * MAP_PX_DEG,
            MAP_Y0 + (90 - lat) * MAP_PX_DEG)


def project_poly(poly):
    return [project(lon, lat) for lon, lat in poly]


NORTH_AMERICA = [
    (-168, 66), (-162, 60), (-158, 58), (-152, 60), (-145, 60), (-138, 59),
    (-133, 56), (-130, 54), (-127, 50), (-124, 48), (-124, 42), (-121, 37),
    (-117, 33), (-112, 29), (-108, 25), (-105, 20), (-100, 18), (-96, 16),
    (-94, 17), (-91, 14), (-88, 13), (-85, 12), (-83, 9), (-80, 8),
    (-78, 7), (-80, 9), (-82, 10), (-84, 13), (-86, 16), (-88, 18),
    (-87, 21), (-90, 21), (-91, 19), (-93, 17), (-96, 19), (-97, 22),
    (-97, 26), (-94, 29), (-90, 29), (-86, 30), (-84, 30), (-81, 25),
    (-80, 27), (-80, 32), (-76, 35), (-75, 38), (-74, 40), (-71, 41),
    (-69, 44), (-67, 45), (-64, 44), (-60, 46), (-59, 48), (-55, 47),
    (-53, 49), (-55, 51), (-58, 52), (-60, 55), (-63, 58), (-66, 58),
    (-70, 60), (-74, 62), (-78, 62), (-82, 64), (-86, 66), (-90, 66),
    (-94, 68), (-98, 69), (-104, 68), (-110, 68), (-116, 69), (-122, 70),
    (-128, 70), (-135, 69), (-142, 70), (-150, 70), (-157, 71), (-163, 70),
    (-168, 66),
]

GREENLAND = [
    (-58, 64), (-53, 60), (-46, 60), (-42, 61), (-40, 64), (-36, 66),
    (-32, 68), (-28, 70), (-22, 70), (-20, 73), (-22, 76), (-26, 78),
    (-32, 80), (-38, 81), (-45, 81), (-52, 80), (-58, 78), (-60, 76),
    (-58, 72), (-56, 68), (-58, 64),
]

SOUTH_AMERICA = [
    (-79, 9), (-77, 5), (-79, 1), (-81, -4), (-80, -7), (-77, -11),
    (-74, -16), (-71, -19), (-70, -23), (-70, -28), (-71, -32), (-72, -37),
    (-73, -42), (-73, -47), (-74, -51), (-71, -54), (-68, -55), (-66, -53),
    (-66, -49), (-64, -44), (-62, -40), (-58, -35), (-55, -34), (-52, -32),
    (-49, -28), (-46, -24), (-42, -22), (-40, -20), (-39, -16), (-37, -13),
    (-35, -9), (-35, -6), (-37, -4), (-40, -3), (-43, -2), (-47, -1),
    (-50, 0), (-52, 2), (-54, 4), (-56, 6), (-59, 8), (-62, 9),
    (-66, 10), (-69, 11), (-72, 12), (-75, 10), (-77, 8), (-79, 9),
]

# Europe + Asia as one Eurasian landmass (the Europe/Asia boundary is not a
# coastline). Coastline runs Iberia -> Scandinavia -> Siberian Arctic coast
# -> Kamchatka -> Pacific coast -> SE Asia -> India -> Arabia -> Levant ->
# Turkey -> Greece -> Italy -> S. France -> Spain.
EURASIA = [
    (-9, 37), (-9, 39), (-9, 43), (-4, 44), (-2, 44), (-1, 46), (-4, 48),
    (-2, 49), (-1, 50), (1, 51), (3, 52), (5, 53), (7, 54), (8, 56),
    (10, 57), (8, 58), (6, 58), (5, 59), (5, 60), (6, 62), (8, 63),
    (11, 64), (13, 66), (15, 68), (18, 69), (21, 70), (25, 71), (28, 71),
    (31, 70), (33, 69), (35, 68), (38, 67), (41, 66), (44, 67), (47, 68),
    (50, 68), (53, 69), (56, 69), (60, 69), (64, 70), (68, 70), (72, 71),
    (75, 72), (79, 73), (83, 74), (87, 75), (91, 75), (95, 76), (99, 76),
    (103, 77), (107, 77), (111, 76), (114, 74), (118, 73), (122, 73),
    (126, 72), (130, 72), (134, 71), (138, 72), (142, 72), (146, 71),
    (150, 70), (154, 70), (158, 69), (160, 67), (162, 64), (162, 61),
    (160, 58), (158, 55), (157, 52), (156, 50), (154, 48), (150, 45),
    (147, 44), (143, 44), (141, 41), (140, 39), (138, 36), (135, 34),
    (132, 33), (129, 34), (127, 35), (125, 37), (122, 38), (121, 35),
    (120, 32), (119, 28), (117, 25), (114, 22), (111, 21), (109, 18),
    (107, 16), (105, 12), (104, 9), (102, 8), (100, 9), (98, 11),
    (96, 14), (94, 16), (92, 20), (90, 22), (88, 22), (86, 20), (84, 18),
    (82, 17), (80, 15), (78, 12), (76, 9), (75, 12), (73, 16), (71, 20),
    (69, 21), (67, 24), (65, 25), (62, 25), (59, 25), (57, 26), (55, 27),
    (53, 26), (51, 28), (50, 29), (49, 30), (48, 30), (50, 28), (52, 26),
    (54, 26), (56, 27), (58, 26), (59, 23), (58, 20), (56, 18), (54, 17),
    (52, 15), (50, 14), (47, 13), (44, 12), (43, 13), (42, 15), (41, 17),
    (39, 20), (38, 22), (37, 24), (36, 27), (35, 29), (34, 31), (35, 34),
    (36, 36), (33, 36), (31, 36), (29, 36), (27, 37), (26, 38), (24, 37),
    (23, 36), (22, 37), (23, 39), (21, 39), (20, 40), (19, 41), (17, 42),
    (15, 43), (13, 44), (11, 44), (9, 44), (7, 44), (5, 43), (3, 42),
    (1, 40), (0, 39), (-1, 38), (-3, 37), (-5, 36), (-7, 36), (-9, 37),
]

AFRICA = [
    (-6, 35), (-9, 32), (-11, 30), (-14, 28), (-16, 25), (-17, 21),
    (-17, 17), (-16, 13), (-14, 10), (-12, 8), (-9, 6), (-6, 5), (-3, 5),
    (0, 6), (3, 6), (6, 4), (8, 4), (10, 4), (12, 4), (11, 2), (9, 0),
    (10, -2), (12, -4), (13, -6), (12, -9), (13, -12), (12, -15),
    (13, -17), (12, -20), (13, -22), (14, -25), (15, -27), (17, -29),
    (18, -32), (19, -34), (22, -34), (25, -34), (28, -33), (30, -31),
    (32, -29), (34, -26), (36, -23), (38, -20), (40, -17), (40, -14),
    (40, -11), (41, -8), (42, -5), (44, -2), (46, 0), (48, 1), (50, 2),
    (51, 6), (51, 10), (49, 11), (46, 11), (44, 11), (42, 12), (40, 14),
    (39, 16), (38, 19), (37, 21), (36, 23), (35, 25), (34, 27), (33, 29),
    (32, 31), (30, 31), (27, 32), (24, 32), (21, 32), (18, 32), (15, 32),
    (12, 33), (10, 34), (10, 37), (8, 37), (5, 37), (2, 37), (0, 36),
    (-2, 35), (-4, 35), (-6, 35),
]

MADAGASCAR = [
    (44, -12), (46, -14), (48, -15), (50, -16), (50, -18), (49, -21),
    (47, -24), (45, -25), (44, -22), (43, -19), (43, -16), (44, -12),
]

UK = [
    (-5, 50), (-4, 52), (-3, 53), (-5, 55), (-5, 56), (-3, 58), (-2, 57),
    (-1, 56), (0, 54), (1, 53), (1, 51), (-1, 50), (-3, 50), (-5, 50),
]

IRELAND = [
    (-10, 52), (-10, 53), (-9, 54), (-8, 55), (-6, 55), (-6, 54),
    (-6, 52), (-7, 51), (-9, 51), (-10, 52),
]

ICELAND = [
    (-22, 64), (-20, 63), (-17, 63), (-14, 64), (-15, 65), (-17, 66),
    (-20, 66), (-23, 66), (-24, 65), (-22, 64),
]

JAPAN = [
    (130, 31), (131, 32), (133, 33), (135, 34), (137, 34), (138, 35),
    (140, 35), (141, 36), (141, 38), (141, 40), (142, 42), (143, 43),
    (144, 44), (145, 44), (144, 43), (142, 42), (141, 40), (140, 38),
    (139, 36), (137, 35), (135, 34), (133, 33), (131, 32), (130, 31),
]

SUMATRA = [
    (95, 5), (97, 4), (99, 2), (101, 0), (103, -2), (104, -4), (106, -6),
    (105, -5), (103, -3), (101, -1), (99, 1), (97, 3), (95, 5),
]

JAVA = [
    (105, -6), (108, -7), (111, -7), (114, -7), (114, -8), (111, -8),
    (108, -8), (105, -7), (105, -6),
]

BORNEO = [
    (109, 1), (110, 2), (112, 3), (114, 4), (116, 6), (118, 5), (119, 2),
    (118, 0), (117, -2), (115, -3), (113, -3), (111, -2), (109, 0), (109, 1),
]

NEW_GUINEA = [
    (131, -1), (133, -1), (135, -2), (137, -2), (139, -3), (141, -3),
    (143, -4), (145, -5), (147, -6), (149, -8), (150, -8), (148, -9),
    (146, -8), (144, -7), (142, -7), (140, -6), (138, -5), (136, -3),
    (134, -2), (132, -1), (131, -1),
]

SULAWESI = [
    (119, 0), (120, 1), (121, 1), (122, 0), (121, -1), (120, -2),
    (119, -3), (119, -1), (119, 0),
]

AUSTRALIA = [
    (114, -22), (113, -25), (114, -29), (115, -32), (116, -34), (118, -35),
    (121, -34), (124, -33), (127, -32), (129, -32), (131, -32), (133, -33),
    (135, -34), (137, -35), (139, -36), (140, -38), (143, -38), (145, -38),
    (147, -38), (149, -37), (150, -36), (151, -34), (153, -32), (153, -30),
    (153, -27), (152, -25), (151, -23), (150, -22), (148, -20), (146, -19),
    (144, -17), (142, -15), (142, -12), (141, -13), (141, -15), (140, -17),
    (139, -17), (137, -16), (136, -15), (135, -13), (134, -12), (132, -11),
    (130, -12), (128, -14), (126, -14), (124, -16), (122, -17), (120, -19),
    (118, -20), (116, -21), (114, -22),
]

NZ_NORTH = [
    (173, -35), (175, -36), (176, -37), (178, -38), (177, -39), (175, -40),
    (174, -41), (173, -39), (172, -37), (173, -35),
]

NZ_SOUTH = [
    (167, -45), (168, -44), (169, -43), (171, -42), (173, -41), (174, -42),
    (173, -43), (171, -44), (169, -45), (167, -46), (167, -45),
]

CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, EURASIA, AFRICA,
              MADAGASCAR, UK, IRELAND, ICELAND, JAPAN, SUMATRA, JAVA,
              BORNEO, NEW_GUINEA, SULAWESI, AUSTRALIA, NZ_NORTH, NZ_SOUTH]

# Map pins: (story n, dot (x, y), badge (x, y), region). V7 numbering
# (Africa #11 Nairobi and Latin America #15 Quito are now illustrated;
# Yunus #11 and the Gaza raid #13 of V6 are demoted to the newswire).
# Pin 5 is DELIBERATELY ABSENT: GTA VI is "Worldwide", so it gets a
# legend badge instead of a geographic dot. Pin dots use the same
# equirectangular projection as the outlines (1.0667 px/deg): Nairobi
# (36.8E, 1.3S) -> (261, 855); Quito (78.5W, 0.2S) -> (138, 854).
# Pin 4 (New York) nudged to (145, 812), on the coast. Badge offsets
# keep every pair of badges >=16px apart (checked in test_v7.py).
PINS = [
    (1, (344, 830), (344, 830), "Asia"),
    (2, (227, 798), (211, 788), "Europe"),
    (3, (255, 815), (237, 815), "Europe"),
    (4, (145, 812), (129, 801), "North America"),
    (6, (261, 806), (261, 790), "Europe"),
    (7, (235, 795), (249, 779), "Europe"),
    (8, (313, 833), (329, 841), "Asia"),
    (9, (357, 814), (357, 814), "Asia"),
    (10, (383, 890), (383, 890), "Oceania"),
    (11, (261, 855), (261, 855), "Africa"),
    (12, (282, 826), (298, 838), "Middle East"),
    (13, (272, 828), (284, 852), "Middle East"),
    (14, (336, 861), (336, 861), "Asia"),
    (15, (138, 854), (138, 854), "Latin America"),
]


def draw_map(d):
    """World map frame (24, 740, 396, 212) with recognisable continents.

    Ocean fill, tan land with darker coastline, 14 geographic pins (1-4,
    6-15) colour-coded by region (same colours as the header region
    strip), with leader lines where the badge is offset from the dot,
    and the legend including the GLOBAL badge for story 5 (no dot).
    Returns the list of plotted pin numbers (for the acceptance test).
    """
    fx, fy, fw, fh = 24, 740, 396, 212
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=OCEAN, outline=RULE, width=1)
    hf = font(SANS_B, 13)
    d.text((28, 742), "WHERE IT HAPPENED", font=hf, fill=INK)
    # faint graticule: every 30 degrees
    for lon in range(-150, 181, 30):
        gx = MAP_X0 + (lon + 180) * MAP_PX_DEG
        d.line([gx, 758, gx, 918], fill=(190, 210, 224), width=1)
    for lat in (60, 30, 0, -30):
        gy = MAP_Y0 + (90 - lat) * MAP_PX_DEG
        d.line([30, gy, 414, gy], fill=(190, 210, 224), width=1)
    for poly in CONTINENTS:
        d.polygon(project_poly(poly), fill=LAND, outline=LAND_LINE)
    # pins: leader line first, then dot, then badge (region colours)
    for n, dot, badge, region in PINS:
        col = REGION_COLORS[region]
        if badge != dot:
            d.line([dot, badge], fill=col, width=1)
    for n, dot, badge, region in PINS:
        col = REGION_COLORS[region]
        d.ellipse([dot[0] - 3, dot[1] - 3, dot[0] + 3, dot[1] + 3],
                  fill=col, outline=(255, 255, 255), width=1)
    for n, dot, badge, region in PINS:
        red_pin_badge(d, badge[0], badge[1], n, fill=REGION_COLORS[region])
    # legend (inside frame, below the plot): GLOBAL badge for story 5
    lf = font(SANS, 9)
    red_pin_badge(d, 36, 927, 5, d=13)
    d.text((47, 922), "GLOBAL: GTA VI (story 5) is worldwide \u2014 no map dot.",
           font=lf, fill=INK)
    d.text((30, 934),
           "Pins 1\u201315 match stories 1\u201315. Pin colours match the region strip above.",
           font=lf, fill=MUTED)
    return [n for n, _, _, _ in PINS]


# ---------------------------------------------------------------- heroes
# Each draws a real editorial scene into a (w x h) panel, w=318, h=150,
# with a navy title band across the bottom 16px (y+134..150).
# Foreground / midground / background depth, not flat bands.

# ---------------------------------------------------------------- heroes
# V7: THREE heroes, each 318x150. Scenes are redrawn (not stretched V6
# art): distinct faces + nameplates + summit banner; Peace Palace with
# clock tower + Myanmar flag; COP31 landscape with globe + thermometer
# + red CUT stamp. Each ends in a navy title band.

def hero_summit(d, x, y, w, h=150):
    """V7: Shenzhen summit with DISTINCT faces + hair + nameplates.
    Skyline behind, three flags, peace banner, round table; navy band
    "APEC 2026 · SHENZHEN" across the bottom 16px of the panel."""
    d.rectangle([x, y, x + w, y + h], fill=PALE_SKY)
    # background: pale sky + clouds (kept clear of the chip corner)
    d.ellipse([x + 90, y + 6, x + 122, y + 16], fill=(255, 255, 255))
    d.ellipse([x + 108, y + 2, x + 140, y + 12], fill=(255, 255, 255))
    d.ellipse([x + 240, y + 10, x + 268, y + 20], fill=(255, 255, 255))
    # midground: Shenzhen skyline silhouettes (tapered Ping An-style tower)
    sky = (120, 145, 168)
    sky2 = (96, 122, 148)
    towers = [(8, 44, 28, 70), (36, 30, 56, 70), (62, 38, 80, 70),
              (84, 20, 102, 70), (108, 30, 124, 70), (150, 34, 168, 70),
              (172, 24, 190, 70), (196, 36, 214, 70), (218, 28, 236, 70),
              (242, 38, 260, 70), (264, 26, 284, 70), (290, 34, 308, 70)]
    for tx, ty, bx, by in towers:
        d.rectangle([x + tx, y + ty, x + bx, y + by], fill=sky)
    # tapered tower (centre, tallest)
    d.polygon([(x + 126, y + 70), (x + 130, y + 10), (x + 140, y + 10),
               (x + 144, y + 70)], fill=sky2)
    d.polygon([(x + 130, y + 10), (x + 135, y + 0), (x + 140, y + 10)], fill=sky2)
    # lit windows on the skyline
    for wx in range(x + 12, x + w - 10, 14):
        for wy in (y + 34, y + 44, y + 54, y + 62):
            d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 240, 180))
    # hills + lake
    d.polygon([(x, y + 96), (x + 80, y + 70), (x + 160, y + 96)], fill=(110, 145, 105))
    d.polygon([(x + 150, y + 96), (x + 240, y + 68), (x + w, y + 96)], fill=(96, 132, 94))
    d.rectangle([x, y + 96, x + w, y + 112], fill=(140, 175, 200))
    d.line([x + 16, y + 102, x + 90, y + 102], fill=(200, 225, 240), width=1)
    d.line([x + 200, y + 106, x + 300, y + 106], fill=(200, 225, 240), width=1)
    # three flags on poles, behind the banner
    poles = [x + 24, x + 136, x + 248]
    for px, code in zip(poles, ["US", "CN", "RU"]):
        d.line([px, y + 30, px, y + 66], fill=DARK, width=2)
        d.ellipse([px - 2, y + 28, px + 2, y + 32], fill=GOLD)
        if code == "US":
            d.rectangle([px, y + 32, px + 46, y + 48], fill=(255, 255, 255))
            for i in range(4):
                d.rectangle([px, y + 32 + i * 4, px + 46, y + 34 + i * 4], fill=(178, 34, 52))
            d.rectangle([px, y + 32, px + 18, y + 40], fill=(60, 59, 110))
            for sx in range(px + 2, px + 17, 4):
                for sy in (y + 33, y + 36):
                    d.ellipse([sx, sy, sx + 1, sy + 1], fill=(255, 255, 255))
        elif code == "CN":
            d.rectangle([px, y + 32, px + 46, y + 48], fill=(222, 41, 16))
            star(d, px + 11, y + 40, 5, (255, 215, 0))
            star(d, px + 24, y + 36, 3, (255, 215, 0))
        else:
            d.rectangle([px, y + 32, px + 46, y + 37], fill=(255, 255, 255))
            d.rectangle([px, y + 37, px + 46, y + 42], fill=(0, 57, 166))
            d.rectangle([px, y + 42, px + 46, y + 48], fill=(213, 0, 0))
    # banner ribbon: the focal point, spanning the panel
    d.rectangle([x + 16, y + 58, x + w - 16, y + 78], fill=(255, 255, 255))
    d.rectangle([x + 16, y + 58, x + w - 16, y + 78], outline=RED, width=2)
    d.polygon([(x + 16, y + 58), (x + 5, y + 68), (x + 16, y + 78)], fill=RED)
    d.polygon([(x + w - 16, y + 58), (x + w - 5, y + 68), (x + w - 16, y + 78)], fill=RED)
    bf = font(SANS_B, 13)
    t = "DECLARATION TOWARD PEACE"
    d.text((x + w // 2 - bf.getlength(t) / 2, y + 63), t, font=bf, fill=RED)
    # foreground: three seated leaders with distinct faces, hair, ties
    leaders = [(x + 70, (30, 30, 40), (232, 190, 150), (235, 205, 90),
                (178, 34, 52), "TRUMP"),
               (x + w // 2, (40, 30, 30), (240, 200, 160), (25, 25, 25),
                (120, 20, 20), "XI"),
               (x + w - 70, (30, 38, 50), (225, 185, 145), (178, 178, 178),
                (0, 57, 166), "PUTIN")]
    for cx, suit, skin, hair, tie, name in leaders:
        # hair: top half of the head
        d.pieslice([cx - 9, y + 78, cx + 9, y + 94], 180, 360, fill=hair)
        d.ellipse([cx - 9, y + 80, cx + 9, y + 98], fill=skin)
        d.pieslice([cx - 9, y + 78, cx + 9, y + 92], 180, 360, fill=hair)
        # eyes + smile
        d.ellipse([cx - 4, y + 87, cx - 2, y + 89], fill=DARK)
        d.ellipse([cx + 2, y + 87, cx + 4, y + 89], fill=DARK)
        d.arc([cx - 4, y + 89, cx + 4, y + 95], 0, 180, fill=DARK, width=1)
        # suit + shirt + tie (table covers below y+104)
        d.polygon([(cx - 15, y + 118), (cx - 12, y + 98), (cx + 12, y + 98),
                   (cx + 15, y + 118)], fill=suit)
        d.polygon([(cx - 3, y + 98), (cx, y + 104), (cx + 3, y + 98)], fill=(255, 255, 255))
        d.polygon([(cx - 2, y + 99), (cx + 2, y + 99), (cx, y + 106)], fill=tie)
    # foreground: big round table (flattened to end above the navy band)
    d.ellipse([x + 36, y + 108, x + w - 36, y + 132], fill=(122, 74, 44))
    d.ellipse([x + 36, y + 104, x + w - 36, y + 118], fill=(178, 120, 72))
    # papers on the table
    for px in (x + 66, x + w // 2 - 14, x + w - 94):
        d.rectangle([px, y + 110, px + 28, y + 118], fill=(255, 255, 255))
        d.line([px + 3, y + 113, px + 25, y + 113], fill=(150, 150, 150), width=1)
        d.line([px + 3, y + 116, px + 20, y + 116], fill=(150, 150, 150), width=1)
    # nameplates on the table front
    nf = font(SANS_B, 8)
    for cx, _, _, _, _, name in leaders:
        d.rectangle([cx - 24, y + 119, cx + 24, y + 131], fill=(255, 255, 255),
                    outline=INK, width=1)
        d.text((cx - nf.getlength(name) / 2, y + 121), name, font=nf, fill=INK)
    # navy title band
    d.rectangle([x, y + 134, x + w, y + 150], fill=NAVY)
    bf2 = font(SANS_B, 10)
    t2 = "APEC 2026 \u00b7 SHENZHEN"
    d.text((x + w // 2 - bf2.getlength(t2) / 2, y + 137), t2, font=bf2,
           fill=(255, 255, 255))



def hero_icj(d, x, y, w, h=150):
    """V7: Peace Palace, The Hague — red-brick building with pitched
    roofs, central clock tower, arched windows, Myanmar flag, small
    scales of justice in front, red 9-6 badge, navy band
    "WORLD COURT · THE HAGUE"."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 228, 205))
    # Myanmar flag, left (green / yellow / red + white star)
    d.line([x + 34, y + 18, x + 34, y + 72], fill=DARK, width=2)
    d.ellipse([x + 32, y + 16, x + 36, y + 20], fill=GOLD)
    d.rectangle([x + 34, y + 22, x + 70, y + 29], fill=(40, 130, 60))
    d.rectangle([x + 34, y + 29, x + 70, y + 36], fill=(240, 210, 60))
    d.rectangle([x + 34, y + 36, x + 70, y + 43], fill=(200, 40, 40))
    star(d, x + 52, y + 32, 5, (255, 255, 255))
    # main brick block + pitched roof
    d.rectangle([x + 30, y + 54, x + w - 30, y + 118], fill=(186, 128, 96))
    d.polygon([(x + 30, y + 54), (x + w // 2, y + 30), (x + w - 30, y + 54)],
              fill=(120, 60, 50))
    d.rectangle([x + 30, y + 54, x + w - 30, y + 58], fill=(240, 230, 210))
    # brick courses
    for by in range(y + 62, y + 116, 8):
        d.line([x + 30, by, x + w - 30, by], fill=(170, 112, 82), width=1)
    # arched windows (white frame, dark arch)
    for cx in (x + 64, x + 104, x + 214, x + 254):
        d.rectangle([cx - 11, y + 70, cx + 11, y + 102], fill=(240, 230, 210))
        d.pieslice([cx - 11, y + 60, cx + 11, y + 80], 180, 360,
                   fill=(240, 230, 210))
        d.rectangle([cx - 9, y + 72, cx + 9, y + 100], fill=(70, 55, 48))
        d.pieslice([cx - 9, y + 62, cx + 9, y + 80], 180, 360, fill=(70, 55, 48))
        d.line([cx, y + 72, cx, y + 100], fill=(120, 110, 100), width=1)
    # central clock tower (rises above the roof) + cap
    d.rectangle([x + 138, y + 8, x + 180, y + 118], fill=(168, 112, 82))
    d.polygon([(x + 136, y + 10), (x + 159, y + 0), (x + 182, y + 10)],
              fill=(120, 60, 50))
    d.ellipse([x + 145, y + 18, x + 173, y + 46], fill=(255, 255, 255),
              outline=INK, width=1)
    d.line([x + 159, y + 32, x + 159, y + 24], fill=INK, width=2)
    d.line([x + 159, y + 32, x + 165, y + 36], fill=INK, width=2)
    d.ellipse([x + 157, y + 30, x + 161, y + 34], fill=INK)
    # small tower windows
    for wy in (y + 56, y + 76):
        d.rectangle([x + 152, wy, x + 166, wy + 14], fill=(70, 55, 48))
    # door at the tower base
    d.rectangle([x + 148, y + 94, x + 170, y + 118], fill=(70, 55, 48))
    # steps
    d.rectangle([x + w // 2 - 110, y + 118, x + w // 2 + 110, y + 124],
                fill=(200, 190, 164))
    d.rectangle([x + w // 2 - 125, y + 124, x + w // 2 + 125, y + 130],
                fill=(188, 178, 152))
    # small robed figures flanking the scales
    for fx in (x + 92, x + w - 92):
        d.ellipse([fx - 7, y + 98, fx + 7, y + 112], fill=(232, 190, 150))
        d.polygon([(fx - 12, y + 132), (fx - 9, y + 112), (fx + 9, y + 112),
                   (fx + 12, y + 132)], fill=(40, 40, 48))
    # scales of justice, smaller, centre foreground
    cx = x + w // 2
    d.rectangle([cx - 16, y + 124, cx + 16, y + 129], fill=GOLD)
    d.rectangle([cx - 2, y + 86, cx + 2, y + 124], fill=GOLD)
    d.polygon([(cx - 4, y + 82), (cx, y + 76), (cx + 4, y + 82)], fill=GOLD)
    d.line([cx - 40, y + 92, cx + 40, y + 92], fill=GOLD, width=3)
    for sgn in (-1, 1):
        ex = cx + sgn * 40
        d.line([ex, y + 92, ex, y + 102], fill=GOLD, width=2)
        d.polygon([(ex - 16, y + 102), (ex + 16, y + 102), (ex, y + 118)], fill=GOLD)
        d.polygon([(ex - 12, y + 104), (ex + 12, y + 104), (ex, y + 114)],
                  fill=(190, 150, 40))
    # red 9-6 badge, top-right (clear of the VERIFIED chip above it)
    d.ellipse([x + w - 53, y + 25, x + w - 23, y + 55], fill=RED,
              outline=(255, 255, 255), width=2)
    vf = font(SERIF_B, 15)
    t = "9\u20136"
    d.text((x + w - 38 - vf.getlength(t) / 2, y + 32), t, font=vf,
           fill=(255, 255, 255))
    # navy title band
    d.rectangle([x, y + 134, x + w, y + 150], fill=NAVY)
    bf2 = font(SANS_B, 10)
    t2 = "WORLD COURT \u00b7 THE HAGUE"
    d.text((x + w // 2 - bf2.getlength(t2) / 2, y + 137), t2, font=bf2,
           fill=(255, 255, 255))



def hero_cop31(d, x, y, w, h=150):
    """V7: COP31 landscape — draft document with FOSSIL FUELS struck
    through + red CUT stamp, globe + leaf, red thermometer, wind
    turbine on the hills, navy band "COP31 · ANTALYA"."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 220))
    # sun, top-right
    d.ellipse([x + w - 44, y + 6, x + w - 16, y + 34], fill=(255, 220, 120))
    # hills along the bottom (behind document and globe)
    d.polygon([(x, y + 118), (x + 120, y + 104), (x + 200, y + 118),
               (x + w, y + 108), (x + w, y + 134), (x, y + 134)],
              fill=(150, 185, 140))
    # wind turbine on the right hill (grey-blue, not white: white on the
    # pale sky was barely visible in V6)
    tx = x + w - 26
    d.line([tx, y + 96, tx, y + 130], fill=(120, 130, 140), width=3)
    for ang in (90, 210, 330):
        a = math.radians(ang)
        d.line([tx, y + 96, tx + 14 * math.cos(a), y + 96 + 14 * math.sin(a)],
               fill=(120, 130, 140), width=3)
    d.ellipse([tx - 3, y + 93, tx + 3, y + 99], fill=(120, 130, 140))
    # draft document, left
    dx, dy, dw, dh = x + 14, y + 10, 176, 110
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(255, 255, 255),
                outline=(150, 150, 150), width=1)
    d.rectangle([dx, dy, dx + dw, dy + 24], fill=(235, 240, 235))
    tf = font(SANS_B, 14)
    d.text((dx + 10, dy + 4), "COP31 DRAFT", font=tf, fill=INK)
    for i, ln in enumerate([120, 148, 132]):
        d.rectangle([dx + 10, dy + 32 + i * 9, dx + 10 + ln, dy + 35 + i * 9],
                    fill=(205, 205, 205))
    ff = font(SANS_B, 16)
    t = "FOSSIL FUELS"
    d.text((dx + 10, dy + 62), t, font=ff, fill=(120, 120, 120))
    d.line([dx + 6, dy + 72, dx + 16 + ff.getlength(t), dy + 72], fill=RED, width=5)
    sf = font(SANS_B, 12)
    t2 = "$120bn target"
    d.text((dx + 10, dy + 84), t2, font=sf, fill=(120, 120, 120))
    d.line([dx + 6, dy + 91, dx + 14 + sf.getlength(t2), dy + 91], fill=RED, width=3)
    d.text((dx + 10, dy + 100), "talks run to Friday", font=font(SANS, 11), fill=MUTED)
    # globe, right of the document
    gx, gy, gr = x + 228, y + 64, 30
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=SEA)
    d.ellipse([gx - 24, gy - 26, gx - 2, gy - 6], fill=GREEN)
    d.ellipse([gx - 8, gy + 2, gx + 22, gy + 24], fill=GREEN)
    d.ellipse([gx + 12, gy - 26, gx + 26, gy - 10], fill=GREEN)
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], start=90, end=270,
          fill=(255, 255, 255), width=2)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(255, 255, 255), width=2)
    # leaf overlapping the globe
    d.polygon([(gx - 34, gy + 22), (gx - 16, gy - 2), (gx + 2, gy + 20)],
              fill=TEAL)
    d.line([gx - 30, gy + 18, gx - 2, gy + 10], fill=(255, 255, 255), width=2)
    # red thermometer, far right
    d.rectangle([x + 274, y + 26, x + 286, y + 108], fill=(255, 255, 255),
                outline=INK, width=1)
    d.rectangle([x + 277, y + 60, x + 283, y + 108], fill=RED)
    d.ellipse([x + 271, y + 103, x + 289, y + 121], fill=RED,
              outline=(255, 255, 255), width=1)
    for ty in (36, 48, 60, 72, 84, 96):
        d.line([x + 286, y + ty, x + 292, y + ty], fill=INK, width=1)
    # red CUT stamp, rotated, over the document corner
    stamp = Image.new("RGBA", (70, 30), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([2, 2, 67, 27], outline=RED, width=3)
    stf = font(SANS_B, 17)
    sd.text(((70 - stf.getlength("CUT")) / 2, 4), "CUT", font=stf, fill=RED)
    stamp = stamp.rotate(-18, expand=True, resample=Image.BICUBIC)
    d._image.paste(stamp, (dx + 112, dy + 82), stamp)
    # navy title band
    d.rectangle([x, y + 134, x + w, y + 150], fill=NAVY)
    bf2 = font(SANS_B, 10)
    t2 = "COP31 \u00b7 ANTALYA"
    d.text((x + w // 2 - bf2.getlength(t2) / 2, y + 137), t2, font=bf2,
           fill=(255, 255, 255))



HEROES = {1: hero_summit, 2: hero_icj, 3: hero_cop31}

# VERIFIED-chip audit (V6): 1 White House (primary), 2 ICJ (primary: the
# ruling), 3 Reuters (observable draft document). No hero carries a CLAIM.
# (Anthropic is a mini in V6, not a hero; its figures rest on Investopedia
# alone, so it carries no VERIFIED chip anywhere.)
VERIFIED_CHIP = {1: True, 2: True, 3: True}


# ------------------------------------------------------- mini illustrations
# Each draws a distinct miniature scene into a (w x h) panel, w=154, h=76.
# Real scenes with depth and details, not placeholder icons.

def mini_anthropic(d, x, y, w=154, h=76):
    """Anthropic IPO mini: rising bars, soaring line, ANT ticker tag.
    The "$81.3bn" figure now lives in the black label strip (V7), so the
    big price text is gone. NO 'record' / 'largest IPO ever' wording:
    the figures rest on Investopedia alone, so no superlative and no
    VERIFIED chip."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 226))
    # ticker tag, top-right
    tf = font(SANS_B, 9)
    tag = "ANT  $97.17  +17%"
    tw = tf.getlength(tag)
    d.rounded_rectangle([x + w - tw - 12, y + 5, x + w - 5, y + 21],
                        radius=4, fill=INK)
    d.text((x + w - tw - 8, y + 8), tag, font=tf, fill=(255, 255, 255))
    # bars, rising (end above the label strip at y+63)
    bars = [8, 12, 10, 16, 22, 30]
    bw = 14
    bx = x + 10
    for i, bh in enumerate(bars):
        d.rectangle([bx + i * (bw + 4), y + 60 - bh, bx + i * (bw + 4) + bw, y + 60],
                    fill=(120, 170, 130) if i < 4 else TEAL)
    d.line([x + 6, y + 60, x + w - 4, y + 60], fill=INK, width=1)
    # soaring line + arrow
    pts = [(x + 14, y + 48), (x + 42, y + 44), (x + 70, y + 46),
           (x + 98, y + 34), (x + 126, y + 28)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + 126, y + 28), (x + 114, y + 26), (x + 120, y + 38)],
              fill=RED)
    label_strip(d, x, y, w, h, MINI_STRIP[4])


def mini_gta(d, x, y, w=154, h=76):
    """GTA VI: neon night city, lit towers, street, controller, gold 99."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    d.ellipse([x + w - 34, y + 4, x + w - 10, y + 28], fill=(255, 240, 180))
    # skyline
    for bx, bw, bh, c in [(4, 18, 34, (58, 66, 100)), (24, 14, 46, (70, 80, 118)),
                          (40, 20, 28, (52, 60, 92)), (62, 14, 52, (76, 86, 126)),
                          (78, 18, 38, (58, 66, 100)), (98, 14, 48, (70, 80, 118)),
                          (114, 20, 30, (52, 60, 92)), (136, 16, 42, (64, 74, 110))]:
        d.rectangle([x + bx, y + 56 - bh, x + bx + bw, y + 56], fill=c)
        for wy in range(y + 60 - bh, y + 52, 9):
            for wx in range(x + bx + 3, x + bx + bw - 3, 6):
                if (wx + wy) % 13 < 6:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 210, 90))
    # street + neon strip
    d.rectangle([x, y + 56, x + w, y + h], fill=(22, 24, 38))
    d.rectangle([x, y + 56, x + w, y + 59], fill=(255, 60, 180))
    for lx in range(x + 6, x + w - 6, 16):
        d.rectangle([lx, y + 66, lx + 8, y + 69], fill=(255, 220, 90))
    # controller, foreground (raised so the label strip clears it)
    d.rounded_rectangle([x + 52, y + 42, x + 102, y + 62], radius=8, fill=(225, 225, 225))
    d.ellipse([x + 58, y + 48, x + 64, y + 54], fill=RED)
    d.ellipse([x + 90, y + 48, x + 96, y + 54], fill=BLUE)
    d.rectangle([x + 74, y + 50, x + 80, y + 52], fill=DARK)
    d.rectangle([x + 76, y + 48, x + 78, y + 54], fill=DARK)
    # gold 99 badge, top-right
    d.ellipse([x + w - 34, y + 26, x + w - 6, y + 54], fill=GOLD, outline=(255, 255, 255), width=2)
    bf = font(SANS_B, 14)
    d.text((x + w - 29, y + 32), "99", font=bf, fill=(255, 255, 255))
    label_strip(d, x, y, w, h, MINI_STRIP[5])


def mini_bridge(d, x, y, w=154, h=76):
    """Crimea Bridge: arch + deck over the strait, flame and smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(168, 198, 220))
    d.ellipse([x + 10, y + 6, x + 34, y + 24], fill=(255, 244, 200))
    d.rectangle([x, y + 50, x + w, y + h], fill=(46, 111, 148))
    for wy in (58, 66, 72):
        d.line([x, y + wy, x + w, y + wy], fill=(140, 190, 220), width=2)
    # arch + deck + pillars
    d.arc([x + 12, y + 6, x + w - 12, y + 74], start=180, end=360, fill=(80, 80, 80), width=5)
    d.line([x + 6, y + 40, x + w - 6, y + 40], fill=(80, 80, 80), width=4)
    for px in (30, 62, 92, 122):
        d.line([x + px, y + 22, x + px, y + 40], fill=(80, 80, 80), width=3)
        d.rectangle([x + px - 3, y + 40, x + px + 3, y + 52], fill=(100, 100, 100))
    # flame + smoke over the deck
    d.polygon([(x + 68, y + 6), (x + 76, y + 20), (x + 82, y + 10), (x + 88, y + 24),
               (x + 78, y + 32), (x + 66, y + 26)], fill=ORANGE)
    d.ellipse([x + 70, y + 18, x + 82, y + 30], fill=(255, 200, 0))
    d.ellipse([x + 88, y + 2, x + 100, y + 12], fill=(200, 200, 200))
    d.ellipse([x + 96, y - 2, x + 108, y + 8], fill=(220, 220, 220))
    # small boat on the water (raised above the label strip)
    d.polygon([(x + 110, y + 52), (x + 140, y + 52), (x + 134, y + 60), (x + 116, y + 60)],
              fill=(255, 255, 255))
    d.rectangle([x + 120, y + 44, x + 130, y + 52], fill=(200, 60, 60))
    label_strip(d, x, y, w, h, MINI_STRIP[6])


def mini_greenland(d, x, y, w=154, h=76):
    """V7 redraw: Greenland as a real scene, not a white map blob.
    Mountain ranges with snow caps, Danish + US flags on poles, and a
    ballot slip reading 109-0 with a red check. No stray green square."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 220, 235))
    # back range (pale) + snow caps
    d.polygon([(x, y + 52), (x + 30, y + 26), (x + 55, y + 48),
               (x + 85, y + 20), (x + 115, y + 46), (x + 140, y + 30),
               (x + w, y + 52)], fill=(165, 185, 200))
    for px, py in [(30, 26), (85, 20), (140, 30)]:
        d.polygon([(x + px - 7, y + py + 7), (x + px, y + py),
                   (x + px + 7, y + py + 7)], fill=(255, 255, 255))
    # front range (slate) + snow caps
    d.polygon([(x, y + 62), (x + 25, y + 40), (x + 60, y + 60),
               (x + 95, y + 36), (x + 125, y + 58), (x + w, y + 62)],
              fill=(110, 135, 160))
    for px, py in [(25, 40), (95, 36)]:
        d.polygon([(x + px - 6, y + py + 6), (x + px, y + py),
                   (x + px + 6, y + py + 6)], fill=(255, 255, 255))
    # Danish flag, left pole
    d.line([x + 26, y + 14, x + 26, y + 52], fill=DARK, width=2)
    d.rectangle([x + 26, y + 16, x + 54, y + 30], fill=(200, 16, 46))
    d.rectangle([x + 34, y + 16, x + 38, y + 30], fill=(255, 255, 255))
    d.rectangle([x + 26, y + 21, x + 54, y + 25], fill=(255, 255, 255))
    # US flag, right pole
    d.line([x + 118, y + 12, x + 118, y + 50], fill=DARK, width=2)
    d.rectangle([x + 118, y + 14, x + 146, y + 28], fill=(255, 255, 255))
    for i in range(4):
        d.rectangle([x + 118, y + 14 + i * 4, x + 146, y + 16 + i * 4],
                    fill=(178, 34, 52))
    d.rectangle([x + 118, y + 14, x + 128, y + 21], fill=(60, 59, 110))
    # ballot slip, bottom-left (clear of the label strip)
    d.rectangle([x + 8, y + 46, x + 68, y + 62], fill=(255, 255, 255),
                outline=INK, width=1)
    bf = font(SANS_B, 12)
    d.text((x + 12, y + 49), "109\u20130", font=bf, fill=RED)
    d.line([x + 54, y + 56, x + 58, y + 60, x + 66, y + 50], fill=RED, width=2)
    label_strip(d, x, y, w, h, MINI_STRIP[7])



def mini_cyclone(d, x, y, w=154, h=76):
    """Cyclone Akvan: spiral bands over a dark sea, coast and rain below."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 68, 92))
    cx, cy = x + 62, y + 32
    for r, st in [(30, 200), (24, 160), (18, 120), (12, 80), (6, 40)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=st, end=st + 260,
              fill=(255, 255, 255), width=4)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 200, 0))
    # coast + houses at the bottom (raised above the label strip)
    d.polygon([(x, y + 58), (x + 40, y + 52), (x + 90, y + 58), (x + w, y + 54),
               (x + w, y + h), (x, y + h)], fill=(90, 120, 90))
    for hx in (14, 44, 118):
        d.rectangle([x + hx, y + 56, x + hx + 12, y + 64], fill=(240, 220, 170))
        d.polygon([(x + hx - 2, y + 56), (x + hx + 6, y + 50), (x + hx + 14, y + 56)],
                  fill=(150, 60, 60))
    # rain streaks
    for rx in range(x + 8, x + w - 4, 14):
        d.line([rx, y + 52, rx - 4, y + 60], fill=(140, 180, 220), width=2)
    label_strip(d, x, y, w, h, MINI_STRIP[8])


def mini_exam(d, x, y, w=154, h=76):
    """V7: Suneung exam. The sheet carries answer bubbles (no title text,
    so the number badge can no longer cover the "S" of SUNEUNG — that
    text now lives in the label strip). Pencil shrunk so it no longer
    dominates the panel."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    d.rectangle([x, y + 60, x + w, y + h], fill=(170, 130, 85))
    # answer sheet with bubble rows
    d.rectangle([x + 14, y + 8, x + 92, y + 64], fill=(255, 255, 255), outline=INK, width=1)
    filled = [1, 2, 0, 3, 1]
    for i in range(5):
        yy = y + 16 + i * 9
        d.text((x + 19, yy - 1), f"{i + 1}.", font=font(SANS, 8), fill=MUTED)
        for b in range(4):
            bx = x + 34 + b * 13
            d.ellipse([bx, yy, bx + 7, yy + 7], outline=(150, 150, 150), width=1)
            if b == filled[i]:
                d.ellipse([bx + 1, yy + 1, bx + 6, yy + 6], fill=RED)
    # pencil, diagonal, smaller than V6
    d.polygon([(x + 90, y + 52), (x + 126, y + 16), (x + 132, y + 22),
               (x + 96, y + 58)], fill=(255, 200, 0))
    d.polygon([(x + 126, y + 16), (x + 132, y + 22), (x + 138, y + 28),
               (x + 132, y + 32)], fill=(220, 180, 140))
    d.polygon([(x + 90, y + 52), (x + 96, y + 58), (x + 92, y + 62)], fill=(220, 180, 140))
    d.rectangle([x + 120, y + 18, x + 126, y + 26], fill=(220, 100, 100))
    label_strip(d, x, y, w, h, MINI_STRIP[9])



def mini_jobs(d, x, y, w=154, h=76):
    """Australia jobs: falling red line on a grid, briefcase, 4.9% tag."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 234, 222))
    # grid
    for gx in range(x + 10, x + w - 6, 18):
        d.line([gx, y + 8, gx, y + 58], fill=(220, 212, 196), width=1)
    for gy in range(y + 8, y + 58, 12):
        d.line([x + 10, gy, x + w - 10, gy], fill=(220, 212, 196), width=1)
    # falling line + arrow
    pts = [(x + 12, y + 12), (x + 40, y + 18), (x + 68, y + 16),
           (x + 96, y + 34), (x + 124, y + 46), (x + 142, y + 54)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + 142, y + 54), (x + 132, y + 50), (x + 138, y + 60)], fill=RED)
    # 4.9% tag
    bf = font(SANS_B, 15)
    d.rounded_rectangle([x + 100, y + 6, x + 148, y + 26], radius=4, fill=RED)
    d.text((x + 106, y + 9), "4.9%", font=bf, fill=(255, 255, 255))
    # briefcase, bottom-left (raised above the label strip; the
    # "43,500 jobs lost" note is gone — the strip carries it)
    d.rectangle([x + 12, y + 46, x + 52, y + 62], fill=(122, 74, 44))
    d.rectangle([x + 24, y + 40, x + 40, y + 46], fill=(122, 74, 44))
    d.line([x + 12, y + 54, x + 52, y + 54], fill=(200, 160, 110), width=2)
    d.rectangle([x + 30, y + 52, x + 34, y + 56], fill=GOLD)
    label_strip(d, x, y, w, h, MINI_STRIP[10])


def mini_house(d, x, y, w=154, h=76):
    """Yunus home torched: dusk sky, house, roof flame and smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(58, 44, 40))
    d.ellipse([x + 120, y + 6, x + 142, y + 28], fill=(255, 220, 140))
    # house
    d.polygon([(x + 34, y + 38), (x + 77, y + 16), (x + 120, y + 38)], fill=(122, 40, 40))
    d.rectangle([x + 40, y + 38, x + 114, y + 70], fill=(200, 170, 120))
    d.rectangle([x + 70, y + 50, x + 84, y + 70], fill=(60, 40, 20))
    for wx in (48, 94):
        d.rectangle([x + wx, y + 46, x + wx + 12, y + 58], fill=(255, 220, 120))
    # flame on the roof + smoke
    d.polygon([(x + 66, y + 2), (x + 74, y + 14), (x + 80, y + 4), (x + 88, y + 16),
               (x + 78, y + 24), (x + 64, y + 18)], fill=ORANGE)
    d.ellipse([x + 70, y + 12, x + 82, y + 24], fill=(255, 200, 0))
    d.ellipse([x + 88, y - 2, x + 102, y + 10], fill=(150, 140, 130))
    d.ellipse([x + 100, y + 2, x + 112, y + 12], fill=(170, 160, 150))
    # fence + ground
    d.rectangle([x, y + 70, x + w, y + h], fill=(40, 32, 28))
    for fx in range(x + 6, x + w - 4, 12):
        d.line([fx, y + 70, fx, y + 76], fill=(120, 100, 80), width=2)


def mini_tanker(d, x, y, w=154, h=76):
    """Tankers CLAIM: sea, tanker with containers, spiked mine, flame."""
    d.rectangle([x, y, x + w, y + h], fill=(178, 205, 224))
    for wy in (52, 57, 61):
        d.line([x, y + wy, x + w, y + wy], fill=(255, 255, 255), width=2)
    # tanker hull + containers
    d.polygon([(x + 12, y + 40), (x + 118, y + 40), (x + 108, y + 56),
               (x + 22, y + 56)], fill=(60, 60, 60))
    for cx, cc in [(28, (178, 34, 52)), (48, (40, 110, 70)), (68, (200, 140, 40))]:
        d.rectangle([x + cx, y + 26, x + cx + 18, y + 40], fill=cc)
    d.rectangle([x + 92, y + 30, x + 106, y + 40], fill=(255, 255, 255))
    d.line([x + 99, y + 22, x + 99, y + 30], fill=DARK, width=2)
    # spiked mine, upper right
    mx, my = x + 132, y + 20
    d.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=DARK)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([mx + 9 * math.cos(a), my + 9 * math.sin(a),
                mx + 13 * math.cos(a), my + 13 * math.sin(a)], fill=DARK, width=2)
    # flame + smoke on the tanker
    d.polygon([(x + 34, y + 8), (x + 40, y + 18), (x + 46, y + 10), (x + 50, y + 20),
               (x + 40, y + 26), (x + 30, y + 20)], fill=ORANGE)
    d.ellipse([x + 36, y + 16, x + 46, y + 26], fill=(255, 200, 0))
    d.ellipse([x + 50, y + 2, x + 62, y + 12], fill=(200, 200, 200))
    label_strip(d, x, y, w, h, MINI_STRIP[12])


def mini_tank(d, x, y, w=154, h=76):
    """Gaza tank raid: desert road, tank with barrel, dust."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 214, 190))
    d.ellipse([x + 118, y + 6, x + 142, y + 28], fill=(255, 240, 180))
    # distant dunes
    d.polygon([(x, y + 34), (x + 50, y + 24), (x + 100, y + 34), (x + w, y + 26),
               (x + w, y + 40), (x, y + 40)], fill=(205, 190, 150))
    # road
    d.rectangle([x, y + 52, x + w, y + h], fill=(120, 110, 90))
    for dx in range(x + 4, x + w - 4, 18):
        d.line([dx, y + 64, dx + 9, y + 64], fill=(255, 255, 255), width=2)
    # tank
    d.rectangle([x + 34, y + 38, x + 96, y + 52], fill=(90, 100, 60))
    d.rectangle([x + 52, y + 28, x + 80, y + 38], fill=(70, 80, 48))
    d.line([x + 80, y + 31, x + 118, y + 24], fill=(70, 80, 48), width=5)
    for tx in (40, 52, 64, 76, 86):
        d.ellipse([x + tx, y + 52, x + tx + 8, y + 60], fill=DARK)
    d.rectangle([x + 34, y + 52, x + 96, y + 56], fill=(60, 68, 40))
    # dust cloud behind
    d.ellipse([x + 6, y + 40, x + 26, y + 52], fill=(215, 200, 160))
    d.ellipse([x + 16, y + 34, x + 36, y + 46], fill=(225, 212, 175))


def mini_tower(d, x, y, w=154, h=76):
    """Riyadh tower: night sky, tapered PIF Tower, impact burst, city."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 34, 48))
    for sx in range(x + 8, x + w - 6, 18):
        d.ellipse([sx, y + 6 + (sx % 7), sx + 2, y + 8 + (sx % 7)], fill=(255, 255, 255))
    # tapered tower, centre-left (base raised above the label strip)
    d.polygon([(x + 56, y + 64), (x + 62, y + 8), (x + 78, y + 8), (x + 84, y + 64)],
              fill=(140, 160, 190))
    for wy in range(14, 62, 7):
        d.line([x + 62, y + wy, x + 78, y + wy], fill=(220, 230, 240), width=1)
    # crown
    d.polygon([(x + 62, y + 8), (x + 70, y + 0), (x + 78, y + 8)], fill=(180, 195, 215))
    # impact burst ON the upper tower (was floating detached in the sky)
    cx, cy = x + 86, y + 24
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line([cx, cy, cx + 14 * math.cos(a), cy + 14 * math.sin(a)],
               fill=(255, 200, 0), width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=ORANGE)
    d.ellipse([cx + 12, cy - 12, cx + 24, cy - 2], fill=(120, 120, 130))
    # city lights at the base (raised above the label strip)
    for bx, bh in [(8, 12), (26, 18), (100, 14), (118, 20), (136, 12)]:
        d.rectangle([x + bx, y + 64 - bh, x + bx + 12, y + 64], fill=(60, 68, 92))
        d.rectangle([x + bx + 3, y + 64 - bh + 3, x + bx + 6, y + 64 - bh + 6],
                    fill=(255, 210, 90))
    d.rectangle([x, y + 64, x + w, y + h], fill=(20, 22, 34))
    label_strip(d, x, y, w, h, MINI_STRIP[13])


def mini_gavel(d, x, y, w=154, h=76):
    """V7: asset-seizure law. The document carries lines + Rp1bn+ + red
    seal only (no "ASSET-SEIZURE" title text, so the number badge can no
    longer cover its "A" — that text now lives in the label strip).
    The separate "18 YEARS" tag is gone; the strip carries it."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    # bill document
    d.rectangle([x + 12, y + 8, x + 92, y + 64], fill=(255, 255, 255), outline=INK, width=1)
    for i in range(4):
        d.line([x + 20, y + 20 + i * 7, x + 86, y + 20 + i * 7], fill=(170, 170, 170), width=1)
    d.text((x + 20, y + 48), "Rp1bn+", font=font(SANS, 9), fill=MUTED)
    # red seal
    d.ellipse([x + 70, y + 46, x + 86, y + 62], fill=RED)
    d.ellipse([x + 74, y + 50, x + 82, y + 58], outline=(255, 255, 255), width=1)
    # gavel, diagonal at right (raised clear of the label strip)
    d.line([x + 96, y + 14, x + 136, y + 52], fill=(122, 74, 44), width=4)
    d.rectangle([x + 100, y + 6, x + 120, y + 22], fill=(150, 96, 58))
    d.rectangle([x + 126, y + 50, x + 146, y + 60], fill=(150, 96, 58))
    label_strip(d, x, y, w, h, MINI_STRIP[14])



def mini_runner(d, x, y, w=154, h=76):
    """V7 NEW (#11, Nairobi): marathon runner on a red track, Kenyan
    flag on a pole, red BANNED stamp. Africa joins the illustrated set."""
    d.rectangle([x, y, x + w, y + h], fill=(220, 230, 240))
    # red BANNED stamp, top-centre
    sf = font(SANS_B, 9)
    d.rectangle([x + 56, y + 6, x + 108, y + 21], outline=RED, width=2)
    d.text((x + 82 - sf.getlength("BANNED") / 2, y + 8), "BANNED", font=sf, fill=RED)
    # Kenyan flag on a pole, right
    d.line([x + 132, y + 10, x + 132, y + 48], fill=DARK, width=2)
    d.rectangle([x + 132, y + 12, x + 150, y + 17], fill=(20, 20, 20))
    d.rectangle([x + 132, y + 17, x + 150, y + 18], fill=(255, 255, 255))
    d.rectangle([x + 132, y + 18, x + 150, y + 22], fill=(178, 34, 52))
    d.rectangle([x + 132, y + 22, x + 150, y + 23], fill=(255, 255, 255))
    d.rectangle([x + 132, y + 23, x + 150, y + 27], fill=(40, 130, 60))
    # runner silhouette, mid-stride (dark, leaning forward)
    d.ellipse([x + 71, y + 23, x + 83, y + 35], fill=(40, 40, 48))
    d.rectangle([x + 71, y + 29, x + 83, y + 31], fill=(255, 255, 255))
    d.line([x + 77, y + 35, x + 73, y + 49], fill=(40, 40, 48), width=4)
    d.line([x + 73, y + 49, x + 86, y + 59], fill=(40, 40, 48), width=3)
    d.line([x + 73, y + 49, x + 60, y + 57], fill=(40, 40, 48), width=3)
    d.line([x + 76, y + 39, x + 89, y + 33], fill=(40, 40, 48), width=3)
    d.line([x + 76, y + 39, x + 64, y + 43], fill=(40, 40, 48), width=3)
    # motion lines behind the runner
    for my in (31, 39, 47):
        d.line([x + 8, y + my, x + 30, y + my], fill=(160, 170, 185), width=2)
    # red running track + lane lines (above the label strip)
    d.rectangle([x, y + 56, x + w, y + 63], fill=(178, 60, 50))
    d.line([x, y + 59, x + w, y + 59], fill=(255, 255, 255), width=1)
    label_strip(d, x, y, w, h, MINI_STRIP[11])


def mini_hegseth(d, x, y, w=154, h=76):
    """V7 NEW (#15, Quito): LatAm tour — jet over a runway, US +
    Ecuador flags. Latin America joins the illustrated set."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
    d.ellipse([x + 10, y + 6, x + 34, y + 14], fill=(255, 255, 255))
    d.ellipse([x + 44, y + 10, x + 66, y + 17], fill=(255, 255, 255))
    # jet, left, flying right (side view: thin fuselage, tail fin,
    # swept main wing below, nose cone, windows)
    d.rounded_rectangle([x + 14, y + 32, x + 64, y + 38], radius=3, fill=(60, 66, 80))
    d.polygon([(x + 64, y + 32), (x + 72, y + 35), (x + 64, y + 38)], fill=(60, 66, 80))
    d.polygon([(x + 18, y + 32), (x + 24, y + 22), (x + 29, y + 32)], fill=(60, 66, 80))
    d.polygon([(x + 34, y + 38), (x + 44, y + 50), (x + 50, y + 38)], fill=(60, 66, 80))
    d.rectangle([x + 54, y + 33, x + 62, y + 36], fill=(140, 190, 230))
    # motion lines trailing the jet
    d.line([x + 2, y + 32, x + 10, y + 32], fill=(160, 170, 185), width=2)
    d.line([x + 4, y + 38, x + 12, y + 38], fill=(160, 170, 185), width=2)
    # US flag, right
    d.line([x + 102, y + 14, x + 102, y + 52], fill=DARK, width=2)
    d.rectangle([x + 102, y + 16, x + 124, y + 30], fill=(255, 255, 255))
    for i in range(4):
        d.rectangle([x + 102, y + 16 + i * 4, x + 124, y + 18 + i * 4],
                    fill=(178, 34, 52))
    d.rectangle([x + 102, y + 16, x + 111, y + 23], fill=(60, 59, 110))
    # Ecuador flag (yellow / blue / red), far right
    d.line([x + 128, y + 14, x + 128, y + 52], fill=DARK, width=2)
    d.rectangle([x + 128, y + 16, x + 150, y + 23], fill=(240, 210, 60))
    d.rectangle([x + 128, y + 23, x + 150, y + 27], fill=(40, 90, 180))
    d.rectangle([x + 128, y + 27, x + 150, y + 30], fill=(200, 40, 40))
    # runway (above the label strip)
    d.rectangle([x, y + 52, x + w, y + 63], fill=(120, 120, 120))
    for rx in range(x + 8, x + w - 8, 18):
        d.line([rx, y + 57, rx + 9, y + 57], fill=(255, 255, 255), width=2)
    label_strip(d, x, y, w, h, MINI_STRIP[15])


MINIS = {4: mini_anthropic, 5: mini_gta, 6: mini_bridge, 7: mini_greenland,
         8: mini_cyclone, 9: mini_exam, 10: mini_jobs, 11: mini_runner,
         12: mini_tanker, 13: mini_tower, 14: mini_gavel, 15: mini_hegseth}
# V7: mini_house (Yunus) and mini_tank (Gaza raid) are demoted to the
# newswire and no longer in MINIS; their functions stay defined above.

# Short red category labels for the mini cards (fit 140px at Sans-Bold 9).
MINI_CAT = {4: "US \u00b7 TECH", 5: "GLOBAL \u00b7 GAMES",
            6: "EUROPE \u00b7 WAR", 7: "EUROPE \u00b7 POLITICS",
            8: "ASIA \u00b7 WEATHER", 9: "ASIA \u00b7 EDUCATION",
            10: "OCEANIA \u00b7 ECONOMY", 11: "AFRICA \u00b7 SPORT",
            12: "M. EAST \u00b7 CLAIM", 13: "M. EAST \u00b7 ATTACK",
            14: "ASIA \u00b7 LAW", 15: "LATAM \u00b7 DEFENCE"}


# ---------------------------------------------------------------- layout

def draw_claim_headline(d, x, y, text, fnt, width):
    """Draw a newswire headline; a leading 'CLAIM:' is drawn in red."""
    if text.startswith("CLAIM:"):
        d.text((x, y), "CLAIM:", font=fnt, fill=RED)
        rest = text[len("CLAIM:"):]
        d.text((x + fnt.getlength("CLAIM:"), y), rest, font=fnt, fill=INK)
    else:
        d.text((x, y), text, font=fnt, fill=INK)


def main():
    data = json.loads((HERE / "news.json").read_text())
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Section A: masthead (0-140). V7: the DATE is the masthead
    # (largest type on the page); "THE WORLD IN ONE DAY" is the eyebrow.
    eb_f = font(SANS_B, 12)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - eb_f.getlength(t)) / 2, 8), t, font=eb_f, fill=RED)
    date_f = font(SERIF_B, 52)
    t2 = "Thursday 19 November 2026"
    d.text(((W - date_f.getlength(t2)) / 2, 26), t2, font=date_f, fill=INK)
    d.line([MARGIN, 82, W - MARGIN, 82], fill=INK, width=2)
    # region-count strip: colour-coded tabs, counts computed from news.json
    from collections import Counter
    counts = Counter(s["region"] for s in data["featured"] + data["also"])
    strip_f = font(SANS_B, 11)
    tabs = []
    for region in REGION_STRIP_ORDER:
        label = f"{REGION_STRIP_LABEL[region]} {counts[region]}"
        tabs.append((label, REGION_COLORS[region],
                     int(strip_f.getlength(label)) + 16))
    total_w = sum(w for _, _, w in tabs) + 6 * (len(tabs) - 1)
    tx = (W - total_w) // 2
    ty = 86
    for label, col, w in tabs:
        d.rectangle([tx, ty, tx + w, ty + 20], fill=col)
        d.text((tx + 8, ty + 4), label, font=strip_f, fill=(255, 255, 255))
        tx += w + 6
    # stat strip: 5 boxes, y=110-138
    stats = data["stats"]
    gap = 8
    sw = (CW - gap * (len(stats) - 1)) // len(stats)
    sy, sh = 110, 28
    for i, s in enumerate(stats):
        sx = MARGIN + i * (sw + gap)
        d.rectangle([sx, sy, sx + sw, sy + sh], fill=CARD, outline=RULE)
        vf = font(SANS_B, 13)
        lf = font(SANS, 8)
        d.text((sx + 7, sy + 2), s["value"], font=vf, fill=INK)
        lab = trim_one(s["label"], lf, sw - 14)
        d.text((sx + 7, sy + 16), lab, font=lf, fill=MUTED)
    d.line([MARGIN, 141, W - MARGIN, 141], fill=RULE, width=1)

    # ---- Section B: three hero cards, ONE row (145-390)
    heroes = data["featured"][:3]
    hero_xs = [24, 352, 680]
    hf = font(SERIF_B, 15)
    sf = font(SANS, 11)
    mf = font(SANS, 10)
    for hx, s in zip(hero_xs, heroes):
        hy = 145
        d.rectangle([hx, hy, hx + 320, hy + 245], fill=CARD, outline=RULE)
        HEROES[s["n"]](d, hx + 1, hy + 1, 318, 150)
        num_badge(d, hx + 7, hy + 7, s["n"])
        if s["confidence"] == "claim":
            chip(d, hx + 320 - 62, hy + 7, "CLAIM", font(SANS_B, 9),
                 (255, 255, 255), RED)
        elif VERIFIED_CHIP.get(s["n"], True):
            chip(d, hx + 320 - 82, hy + 7, "VERIFIED", font(SANS_B, 9),
                 (255, 255, 255), TEAL)
        ty = hy + 157
        for ln in fit_lines(s["headline"], hf, 304, 2):
            d.text((hx + 8, ty), ln, font=hf, fill=INK)
            ty += 16
        ty = hy + 193
        for ln in fit_lines(s["summary"], sf, 304, 3):
            d.text((hx + 8, ty), ln, font=sf, fill=(60, 60, 60))
            ty += 13
        d.text((hx + 8, hy + 234),
               f"{s['place']}  \u2014  {s['source']}", font=mf, fill=MUTED)

    # ---- Section C: twelve mini cards, 6x2 (395-715)
    cards = data["featured"][3:15]
    mini_xs = [24, 188, 352, 516, 680, 844]
    mini_ys = [395, 559]
    cf = font(SANS_B, 9)
    chf = font(SANS_B, 12)
    csf = font(SANS, 8.5)
    cmf = font(SANS, 8)
    for i, s in enumerate(cards):
        cx = mini_xs[i % 6]
        cy = mini_ys[i // 6]
        d.rectangle([cx, cy, cx + 156, cy + 156], fill=CARD, outline=RULE)
        MINIS[s["n"]](d, cx + 1, cy + 1, 154, 76)
        num_badge(d, cx + 3, cy + 12, s["n"])
        d.text((cx + 8, cy + 79), MINI_CAT[s["n"]], font=cf, fill=RED)
        # V7: headline max 2 lines, then the news.json summary (1-3 lines),
        # then one combined place — source line.
        ty = cy + 90
        lines = fit_lines(s["headline"], chf, 140, 2)
        for li, ln in enumerate(lines):
            if li == 0 and s["confidence"] == "claim" and ln.startswith("CLAIM:"):
                d.text((cx + 8, ty), "CLAIM:", font=chf, fill=RED)
                rest = ln[len("CLAIM:"):]
                d.text((cx + 8 + chf.getlength("CLAIM:"), ty), rest, font=chf, fill=INK)
            else:
                d.text((cx + 8, ty), ln, font=chf, fill=INK)
            ty += 13
        ty = cy + 116
        for ln in fit_lines(s["summary"], csf, 140, 3):
            d.text((cx + 8, ty), ln, font=csf, fill=(60, 60, 60))
            ty += 10
        meta = trim_one(f"{s['place']} \u2014 {s['source']}", cmf, 140)
        d.text((cx + 8, cy + 147), meta, font=cmf, fill=MUTED)

    # ---- Section D: world map + newswire (720-955)
    pins = draw_map(d)
    nf = font(SANS_B, 13)
    d.text((440, 722), "ALSO ON THURSDAY 19 NOVEMBER (20 stories, 2 cols)",
           font=nf, fill=INK)
    # Newswire: 20 items, 2 columns x 10, 20px item pitch. Two lines per
    # item (headline bold 11 / place-source regular 9).
    rows = data["also"]
    nwf = font(SANS_B, 11)
    nwm = font(SANS, 9)
    cols = [(436, 276, rows[0:10]), (720, 280, rows[10:20])]
    for nx, colw, items in cols:
        for j, s in enumerate(items):
            ny = 738 + j * 20
            raw = f"{s['n']}. {s['headline']}"
            size = 11
            while size > 9 and font(SANS_B, size).getlength(raw) > colw:
                size -= 0.5
            wf = font(SANS_B, size)
            head = trim_one(raw, wf, colw)
            draw_claim_headline(d, nx, ny, head, wf, colw)
            meta = trim_one(f"{s['place']} \u2014 {s['source']}", nwm, colw)
            d.text((nx, ny + 11), meta, font=nwm, fill=MUTED)

    # ---- Section E: footer (960-1024). V7: the date check is a bold
    # red-bordered box, not small grey footer text.
    d.rectangle([MARGIN, 960, W - MARGIN, 1008], fill=CARD, outline=RED, width=2)
    tf = font(SANS_B, 11)
    d.text((MARGIN + 10, 964), "DATE CHECK", font=tf, fill=RED)
    _cx = MARGIN + 10 + int(tf.getlength("DATE CHECK")) + 6
    d.line([_cx, 970, _cx + 4, 975, _cx + 10, 966], fill=RED, width=2)
    ff = font(SANS, 9)
    d.text((MARGIN + 10, 978),
           "Every story here happened or was first reported Thu 19 Nov 2026. Left out as other days' news:",
           font=ff, fill=INK)
    d.text((MARGIN + 10, 990),
           "Van Gogh sale \u00b7 IAEA Yongbyon \u00b7 US\u2013Venezuela pact \u00b7 EU loan plan \u00b7 Taiz crisis \u00b7 "
           "US carrier departure \u00b7 Kuwait/Bahrain drones (all Wed 18 Nov).",
           font=ff, fill=INK)
    f1 = ("Sources: Reuters \u00b7 AP \u00b7 White House \u00b7 ICJ \u00b7 WSJ \u00b7 CNN \u00b7 GOV.UK \u00b7 national wires.  "
          "CLAIM = unverified claim, never fact. All 35 stories happened or were first reported Thu 19 Nov 2026.")
    d.text((MARGIN, 1013), trim_one(f1, ff, CW), font=ff, fill=MUTED)

    img.save(HERE / "entry.png", format="PNG", optimize=True)
    n_stories = len(data["featured"]) + len(data["also"])
    print(f"entry.png {img.size} saved; stories={n_stories} "
          f"(featured {len(data['featured'])}, also {len(data['also'])}), "
          f"illustrations={len(HEROES) + len(MINIS)}, map pins={len(pins)} {sorted(pins)} "
          f"(5 = GLOBAL legend, no dot)")


if __name__ == "__main__":
    main()
