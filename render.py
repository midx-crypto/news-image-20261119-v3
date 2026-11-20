#!/usr/bin/env python3
"""Render 'The World in One Day' - Thu 19 Nov 2026 - as a 1024x1024 PNG.

V5 FINAL RENDER (branch v5). Binding geometry: v5-layout-spec.md.
Canvas 1024x1024. Header 0-140; 4 heroes ONE row 145-390 (cards 238x245,
illustration panels 236x120, shared baseline y=266); 12 minis 6x2 395-715
(cards 156x156, illustration panels IDENTICAL 154x76); map + newswire
720-955; footer 960-1024.

Deterministic: fixed seed, no network, no timestamps, no random text.
Reads news.json beside this file, writes entry.png beside this file.
Pillow only (render-time dependency); the shipped main.py is stdlib-only.

V5 changes vs V4 (documented deviations from the spec, all readability fixes):
1. PIN 5 (GTA VI, place "Worldwide") has NO geographic dot and NO leader
   line. A dot at Miami/Vice City would present the game's setting as the
   verified real-world location of a worldwide launch, which it is not.
   Instead the number-5 badge sits in the map LEGEND with the text
   "GLOBAL: GTA VI (story 5) is worldwide - no map dot." The other 15 pins
   keep their spec coordinates and leader offsets exactly.
2. NEWSWIRE items are TWO lines (headline bold 9 / "place - source" regular
   8) at the same 17px item pitch and the same 3 columns. Measured: even the
   most concise full-form single line ("N. headline - place - source") runs
   200-290px at the spec's own Sans-Bold 10, against 183px columns, so
   single-line items could only fit by cutting sources off most stories.
   Two lines keep headline, place AND source fully visible for all 34 items.
   Also-list headlines were still rewritten concisely in news.json.
3. The map uses recognisable coastline polygons (lon/lat outlines projected
   equirectangular, 1.0667 px/deg) instead of schematic blobs, and the
   Greenland miniature draws a recognisable Greenland outline.
4. VERIFIED-chip audit (heroes): chips kept for 1 (White House, primary
   source), 2 (ICJ, primary source: the ruling itself) and 3 (Reuters
   reporting an observable draft document). NO chip on hero 4 (Anthropic
   IPO): its core figures and the "largest IPO ever" superlative rest on a
   single secondary report (Investopedia) with no primary/exchange source
   named in the dataset, so it is shown without a VERIFIED chip rather than
   over-claiming. CLAIM items (12, 24, 32, 34, 36) stay labelled CLAIM.
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


def red_pin_badge(draw, x, y, n, d=16):
    """Red map pin badge (white number); x, y are the badge centre."""
    r = d // 2
    draw.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=(255, 255, 255), width=1)
    f = font(SANS_B, 10)
    t = str(n)
    tw = f.getlength(t)
    draw.text((x - tw / 2, y - 6), t, font=f, fill=(255, 255, 255))


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

# Map pins: (story n, dot (x, y), badge (x, y)). Spec section 6 coordinates,
# kept exactly. Pin 5 is DELIBERATELY ABSENT: GTA VI is "Worldwide", so it
# gets a legend badge instead of a geographic dot (see module docstring).
PINS = [
    (1, (344, 830), (344, 830)),
    (2, (227, 798), (211, 788)),
    (3, (255, 815), (237, 815)),
    (4, (143, 811), (129, 801)),
    (6, (261, 806), (261, 790)),
    (7, (235, 795), (249, 779)),
    (8, (313, 833), (329, 841)),
    (9, (357, 814), (357, 814)),
    (10, (383, 890), (383, 890)),
    (11, (318, 829), (300, 815)),
    (12, (282, 826), (298, 838)),
    (13, (259, 820), (245, 834)),
    (14, (272, 828), (272, 844)),
    (15, (336, 861), (336, 861)),
    (16, (143, 849), (143, 849)),
]


def draw_map(d):
    """World map frame (24, 740, 396, 212) with recognisable continents.

    Ocean fill, tan land with darker coastline, 15 geographic pins (1-4,
    6-16) with leader lines where the badge is offset from the dot, and the
    legend including the GLOBAL badge for story 5 (no dot on the map).
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
    # pins: leader line first, then dot, then badge
    for n, dot, badge in PINS:
        if badge != dot:
            d.line([dot, badge], fill=RED, width=1)
    for n, dot, badge in PINS:
        d.ellipse([dot[0] - 3, dot[1] - 3, dot[0] + 3, dot[1] + 3],
                  fill=RED, outline=(255, 255, 255), width=1)
    for n, dot, badge in PINS:
        red_pin_badge(d, badge[0], badge[1], n)
    # legend (inside frame, below the plot): GLOBAL badge for story 5
    lf = font(SANS, 9)
    red_pin_badge(d, 36, 927, 5, d=13)
    d.text((47, 922), "GLOBAL: GTA VI (story 5) is worldwide \u2014 no map dot.",
           font=lf, fill=INK)
    d.text((30, 934),
           "Pins 1\u201316 match stories 1\u201316. Asia, Europe, N. Am., LatAm, Africa, M. East, Oceania.",
           font=lf, fill=MUTED)
    return [n for n, _, _ in PINS]


# ---------------------------------------------------------------- heroes
# Each draws a real editorial scene into a (w x h) panel, w=236, h=120.
# Foreground / midground / background depth, not flat bands.

def hero_summit(d, x, y, w, h=120):
    """Shenzhen summit: skyline behind, three flags, peace banner as focal
    point, round table with three seated leaders in the foreground."""
    d.rectangle([x, y, x + w, y + h], fill=PALE_SKY)
    # background: pale sky + small clouds (kept clear of the chip corner)
    d.ellipse([x + 66, y + 8, x + 96, y + 18], fill=(255, 255, 255))
    d.ellipse([x + 82, y + 4, x + 112, y + 14], fill=(255, 255, 255))
    # midground: Shenzhen skyline silhouettes (tapered Ping An-style tower)
    sky = (120, 145, 168)
    sky2 = (96, 122, 148)
    towers = [(6, 34, 22, 52), (30, 22, 46, 52), (50, 30, 62, 52),
              (66, 18, 84, 52), (88, 28, 100, 52), (104, 36, 118, 52),
              (150, 30, 164, 52), (168, 20, 186, 52), (190, 32, 202, 52),
              (206, 26, 222, 52)]
    for tx, ty, bx, by in towers:
        d.rectangle([x + tx, y + ty, x + bx, y + by], fill=sky)
    # tapered tower (centre-right, tallest)
    d.polygon([(x + 120, y + 52), (x + 124, y + 8), (x + 132, y + 8),
               (x + 136, y + 52)], fill=sky2)
    d.polygon([(x + 124, y + 8), (x + 128, y + 0), (x + 132, y + 8)], fill=sky2)
    # lit windows on the skyline
    for wx in range(x + 10, x + w - 8, 12):
        for wy in (y + 30, y + 38, y + 46):
            d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 240, 180))
    # hills + lake
    d.polygon([(x, y + 78), (x + 60, y + 56), (x + 120, y + 78)], fill=(110, 145, 105))
    d.polygon([(x + 110, y + 78), (x + 180, y + 54), (x + w, y + 78)], fill=(96, 132, 94))
    d.rectangle([x, y + 78, x + w, y + 96], fill=(140, 175, 200))
    d.line([x + 12, y + 84, x + 70, y + 84], fill=(200, 225, 240), width=1)
    d.line([x + 150, y + 88, x + 220, y + 88], fill=(200, 225, 240), width=1)
    # three flags on poles below the chip line, behind the banner
    poles = [x + 18, x + w // 2 - 6, x + w - 62]
    for px, code in zip(poles, ["US", "CN", "RU"]):
        d.line([px, y + 24, px, y + 52], fill=DARK, width=2)
        d.ellipse([px - 2, y + 22, px + 2, y + 26], fill=GOLD)
        if code == "US":
            d.rectangle([px, y + 26, px + 42, y + 40], fill=(255, 255, 255))
            for i in range(4):
                d.rectangle([px, y + 26 + i * 4, px + 42, y + 28 + i * 4], fill=(178, 34, 52))
            d.rectangle([px, y + 26, px + 17, y + 33], fill=(60, 59, 110))
            for sx in range(px + 2, px + 16, 4):
                for sy in (y + 27, y + 30):
                    d.ellipse([sx, sy, sx + 1, sy + 1], fill=(255, 255, 255))
        elif code == "CN":
            d.rectangle([px, y + 26, px + 42, y + 40], fill=(222, 41, 16))
            d.text((px + 4, y + 27), "\u2605", font=font(SANS_B, 11), fill=(255, 215, 0))
            d.text((px + 18, y + 27), "\u2605", font=font(SANS_B, 6), fill=(255, 215, 0))
        else:
            d.rectangle([px, y + 26, px + 42, y + 31], fill=(255, 255, 255))
            d.rectangle([px, y + 31, px + 42, y + 35], fill=(0, 57, 166))
            d.rectangle([px, y + 35, px + 42, y + 40], fill=(213, 0, 0))
    # banner ribbon: the focal point, spanning the panel
    d.rectangle([x + 14, y + 44, x + w - 14, y + 60], fill=(255, 255, 255))
    d.rectangle([x + 14, y + 44, x + w - 14, y + 60], outline=RED, width=2)
    d.polygon([(x + 14, y + 44), (x + 4, y + 52), (x + 14, y + 60)], fill=RED)
    d.polygon([(x + w - 14, y + 44), (x + w - 4, y + 52), (x + w - 14, y + 60)], fill=RED)
    bf = font(SANS_B, 11)
    t = "DECLARATION TOWARD PEACE"
    d.text((x + w // 2 - bf.getlength(t) / 2, y + 48), t, font=bf, fill=RED)
    # foreground: three seated leaders (dark suits, three skin-tone heads)
    for cx, suit, skin in [(x + 52, (30, 30, 40), (232, 190, 150)),
                           (x + w // 2, (40, 30, 30), (240, 200, 160)),
                           (x + w - 52, (30, 38, 50), (225, 185, 145))]:
        d.ellipse([cx - 8, y + 62, cx + 8, y + 78], fill=skin)
        d.polygon([(cx - 13, y + 96), (cx - 11, y + 78), (cx + 11, y + 78),
                   (cx + 13, y + 96)], fill=suit)
        d.polygon([(cx - 3, y + 78), (cx, y + 86), (cx + 3, y + 78)], fill=(255, 255, 255))
    # foreground: big round table
    d.ellipse([x + 28, y + 88, x + w - 28, y + 118], fill=(122, 74, 44))
    d.ellipse([x + 28, y + 84, x + w - 28, y + 108], fill=(150, 96, 58))
    d.ellipse([x + 28, y + 84, x + w - 28, y + 94], fill=(178, 120, 72))
    # papers + pens on the table
    for px in (x + 52, x + w // 2 - 12, x + w - 76):
        d.rectangle([px, y + 88, px + 24, y + 96], fill=(255, 255, 255))
        d.line([px + 3, y + 91, px + 21, y + 91], fill=(150, 150, 150), width=1)
        d.line([px + 3, y + 94, px + 17, y + 94], fill=(150, 150, 150), width=1)
    d.ellipse([x + w // 2 - 4, y + 97, x + w // 2 + 4, y + 105], fill=GOLD)


def hero_icj(d, x, y, w, h=120):
    """ICJ: courthouse pediment + columns, big scales of justice in front,
    red 9-6 verdict on the pediment, steps at the base."""
    d.rectangle([x, y, x + w, y + h], fill=(233, 227, 211))
    # pediment with 9-6 verdict
    d.polygon([(x + 18, y + 26), (x + w // 2, y + 4), (x + w - 18, y + 26)],
              fill=(200, 188, 158))
    d.polygon([(x + 26, y + 24), (x + w // 2, y + 8), (x + w - 26, y + 24)],
              fill=(214, 202, 172))
    vf = font(SERIF_B, 20)
    t = "9\u20136"
    d.text((x + w // 2 - vf.getlength(t) / 2, y + 8), t, font=vf, fill=RED)
    # entablature + columns
    d.rectangle([x + 12, y + 26, x + w - 12, y + 32], fill=(220, 210, 182))
    for cx in range(x + 22, x + w - 30, 42):
        d.rectangle([cx - 3, y + 32, cx + 17, y + 36], fill=(220, 210, 182))
        d.rectangle([cx, y + 36, cx + 14, y + 92], fill=(245, 240, 224))
        d.line([cx + 4, y + 36, cx + 4, y + 92], fill=(215, 205, 175), width=1)
        d.line([cx + 10, y + 36, cx + 10, y + 92], fill=(215, 205, 175), width=1)
        d.rectangle([cx - 3, y + 92, cx + 17, y + 96], fill=(220, 210, 182))
    # steps
    for i, sw in enumerate((196, 208, 220)):
        d.rectangle([x + w // 2 - sw // 2, y + 96 + i * 6,
                     x + w // 2 + sw // 2, y + 101 + i * 6], fill=(200, 190, 164))
    # scales of justice, large, centre foreground
    cx = x + w // 2
    d.rectangle([cx - 16, y + 104, cx + 16, y + 110], fill=GOLD)
    d.rectangle([cx - 2, y + 44, cx + 2, y + 104], fill=GOLD)
    d.polygon([(cx - 3, y + 40), (cx, y + 34), (cx + 3, y + 40)], fill=GOLD)
    d.line([cx - 44, y + 50, cx + 44, y + 50], fill=GOLD, width=4)
    for sgn in (-1, 1):
        ex = cx + sgn * 44
        d.line([ex, y + 50, ex, y + 62], fill=GOLD, width=2)
        d.polygon([(ex - 18, y + 62), (ex + 18, y + 62), (ex, y + 80)], fill=GOLD)
        d.polygon([(ex - 14, y + 64), (ex + 14, y + 64), (ex, y + 76)],
                  fill=(190, 150, 40))
    # small robed figures flanking the scales
    for fx in (x + 34, x + w - 34):
        d.ellipse([fx - 6, y + 78, fx + 6, y + 90], fill=(232, 190, 150))
        d.polygon([(fx - 10, y + 110), (fx - 8, y + 90), (fx + 8, y + 90),
                   (fx + 10, y + 110)], fill=(40, 40, 48))


def hero_cop31(d, x, y, w, h=120):
    """COP31: big draft document with FOSSIL FUELS struck through in red,
    globe + leaf at right, small wind turbine and sun."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 220))
    # small cloud, top-right below the chip line
    d.ellipse([x + 176, y + 28, x + 208, y + 38], fill=(255, 255, 255))
    d.ellipse([x + 192, y + 24, x + 224, y + 34], fill=(255, 255, 255))
    # draft document, left two-thirds
    dx, dy, dw, dh = x + 10, y + 8, 128, 104
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(255, 255, 255),
                outline=(150, 150, 150), width=1)
    d.rectangle([dx, dy, dx + dw, dy + 20], fill=(235, 240, 235))
    tf = font(SANS_B, 12)
    d.text((dx + 8, dy + 4), "COP31 DRAFT", font=tf, fill=INK)
    for i, ln in enumerate([86, 110, 96]):
        d.rectangle([dx + 8, dy + 28 + i * 9, dx + 8 + ln, dy + 31 + i * 9],
                    fill=(205, 205, 205))
    ff = font(SANS_B, 14)
    t = "FOSSIL FUELS"
    d.text((dx + 8, dy + 58), t, font=ff, fill=(120, 120, 120))
    d.line([dx + 5, dy + 66, dx + 12 + ff.getlength(t), dy + 66], fill=RED, width=4)
    # crossed-out $120bn target line
    sf = font(SANS_B, 11)
    t2 = "$120bn target"
    d.text((dx + 8, dy + 76), t2, font=sf, fill=(120, 120, 120))
    d.line([dx + 5, dy + 82, dx + 12 + sf.getlength(t2), dy + 82], fill=RED, width=3)
    d.text((dx + 8, dy + 90), "talks run to Friday", font=font(SANS, 10), fill=MUTED)
    # globe, right (kept clear of the document edge)
    gx, gy, gr = x + w - 42, y + 70, 30
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=SEA)
    d.ellipse([gx - 24, gy - 28, gx - 2, gy - 6], fill=GREEN)
    d.ellipse([gx - 8, gy + 2, gx + 22, gy + 24], fill=GREEN)
    d.ellipse([gx + 12, gy - 26, gx + 28, gy - 10], fill=GREEN)
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], start=90, end=270,
          fill=(255, 255, 255), width=2)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(255, 255, 255), width=2)
    # leaf overlapping the globe
    d.polygon([(gx - 52, gy + 22), (gx - 34, gy - 2), (gx - 16, gy + 20)],
              fill=TEAL)
    d.line([gx - 48, gy + 18, gx - 20, gy + 10], fill=(255, 255, 255), width=2)


def hero_anthropic(d, x, y, w, h=120):
    """Anthropic IPO: rising bars, soaring red line with arrow, big $81.3bn,
    black ANT ticker tag, small exchange building at left."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 226))
    # exchange building, left background
    d.polygon([(x + 8, y + 34), (x + 34, y + 20), (x + 60, y + 34)], fill=(180, 190, 180))
    for cx in range(x + 12, x + 58, 12):
        d.rectangle([cx, y + 36, cx + 6, y + 62], fill=(210, 218, 210))
    d.rectangle([x + 8, y + 62, x + 60, y + 68], fill=(180, 190, 180))
    # bars, rising (sized to end inside the panel)
    bars = [10, 14, 12, 20, 18, 28, 38, 56]
    bw = 16
    bx = x + 66
    for i, bh in enumerate(bars):
        d.rectangle([bx + i * (bw + 5), y + 112 - bh, bx + i * (bw + 5) + bw, y + 112],
                    fill=(120, 170, 130) if i < 5 else TEAL)
    # baseline
    d.line([x + 62, y + 112, x + w - 6, y + 112], fill=INK, width=1)
    # soaring line + arrow (ends clear of the ticker tag)
    pts = [(x + 70, y + 92), (x + 105, y + 86), (x + 140, y + 88),
           (x + 175, y + 70), (x + 200, y + 62)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + 200, y + 62), (x + 186, y + 60), (x + 194, y + 74)],
              fill=RED)
    # big price, top-left
    pf = font(SANS_B, 22)
    d.text((x + 8, y + 6), "$81.3bn", font=pf, fill=INK)
    sf = font(SANS_B, 10)
    d.text((x + 8, y + 32), "LARGEST IPO EVER", font=sf, fill=TEAL)
    # ticker tag, top-right
    tf = font(SANS_B, 11)
    tag = "ANT  $97.17  +17%"
    tw = tf.getlength(tag)
    d.rounded_rectangle([x + w - tw - 18, y + 34, x + w - 6, y + 52],
                        radius=4, fill=INK)
    d.text((x + w - tw - 12, y + 38), tag, font=tf, fill=(255, 255, 255))


HEROES = {1: hero_summit, 2: hero_icj, 3: hero_cop31, 4: hero_anthropic}

# VERIFIED-chip audit (see module docstring): 1 White House (primary),
# 2 ICJ (primary: the ruling), 3 Reuters (observable draft document).
# 4 Anthropic: NO chip - single secondary report, superlative unconfirmed.
VERIFIED_CHIP = {1: True, 2: True, 3: True, 4: False}


# ------------------------------------------------------- mini illustrations
# Each draws a distinct miniature scene into a (w x h) panel, w=154, h=76.
# Real scenes with depth and details, not placeholder icons.

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
    # controller, foreground
    d.rounded_rectangle([x + 52, y + 52, x + 102, y + 72], radius=8, fill=(225, 225, 225))
    d.ellipse([x + 58, y + 58, x + 64, y + 64], fill=RED)
    d.ellipse([x + 90, y + 58, x + 96, y + 64], fill=BLUE)
    d.rectangle([x + 74, y + 60, x + 80, y + 62], fill=DARK)
    d.rectangle([x + 76, y + 58, x + 78, y + 64], fill=DARK)
    # gold 99 badge, top-right
    d.ellipse([x + w - 34, y + 26, x + w - 6, y + 54], fill=GOLD, outline=(255, 255, 255), width=2)
    bf = font(SANS_B, 14)
    d.text((x + w - 29, y + 32), "99", font=bf, fill=(255, 255, 255))


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
    # small boat on the water
    d.polygon([(x + 110, y + 58), (x + 140, y + 58), (x + 134, y + 66), (x + 116, y + 66)],
              fill=(255, 255, 255))
    d.rectangle([x + 120, y + 50, x + 130, y + 58], fill=(200, 60, 60))


def mini_greenland(d, x, y, w=154, h=76):
    """Greenland deal: RECOGNISABLE Greenland outline (wide north coast,
    tapering south tip, fjord-notched east coast) on pale sea, plus the
    109-0 ballot slip."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 220, 235))
    # sea + ice floes
    d.ellipse([x + 8, y + 58, x + 26, y + 66], fill=(255, 255, 255))
    d.ellipse([x + 128, y + 60, x + 146, y + 68], fill=(255, 255, 255))
    # Greenland outline, drawn large: north coast across the top, east coast
    # with fjord notches, tapering to the southern tip at bottom centre.
    gl = [(22, 6), (44, 4), (66, 6), (84, 10), (96, 16), (100, 24),
          (94, 30), (98, 36), (90, 40), (92, 46), (82, 48), (78, 54),
          (66, 56), (56, 60), (48, 54), (38, 52), (28, 46), (18, 38),
          (12, 28), (12, 16), (22, 6)]
    pts = [(x + px, y + py) for px, py in gl]
    d.polygon(pts, fill=(244, 248, 244), outline=TEAL)
    # ice-sheet shading + coastline towns
    d.polygon([(x + 30, y + 12), (x + 58, y + 10), (x + 80, y + 18),
               (x + 70, y + 34), (x + 44, y + 40), (x + 28, y + 28)],
              fill=(220, 235, 240))
    for tx, ty in [(34, 44), (58, 50), (84, 28)]:
        d.ellipse([x + tx - 2, y + ty - 2, x + tx + 2, y + ty + 2], fill=RED)
    # ballot slip, bottom-left overlapping the sea
    d.rectangle([x + 6, y + 56, x + 86, y + 73], fill=(255, 255, 255), outline=INK, width=1)
    bf = font(SANS_B, 13)
    d.text((x + 10, y + 58), "109\u20130", font=bf, fill=RED)
    d.text((x + 62, y + 59), "\u2713", font=font(SANS_B, 13), fill=GREEN)
    d.text((x + 76, y + 60), "", font=bf, fill=INK)


def mini_cyclone(d, x, y, w=154, h=76):
    """Cyclone Akvan: spiral bands over a dark sea, coast and rain below."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 68, 92))
    cx, cy = x + 62, y + 32
    for r, st in [(30, 200), (24, 160), (18, 120), (12, 80), (6, 40)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=st, end=st + 260,
              fill=(255, 255, 255), width=4)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 200, 0))
    # coast + houses at the bottom
    d.polygon([(x, y + 58), (x + 40, y + 52), (x + 90, y + 58), (x + w, y + 54),
               (x + w, y + h), (x, y + h)], fill=(90, 120, 90))
    for hx in (14, 44, 118):
        d.rectangle([x + hx, y + 60, x + hx + 12, y + 70], fill=(240, 220, 170))
        d.polygon([(x + hx - 2, y + 60), (x + hx + 6, y + 54), (x + hx + 14, y + 60)],
                  fill=(150, 60, 60))
    # rain streaks
    for rx in range(x + 8, x + w - 4, 14):
        d.line([rx, y + 62, rx - 4, y + 72], fill=(140, 180, 220), width=2)


def mini_exam(d, x, y, w=154, h=76):
    """Suneung exam: desk, answer sheet, pencil, wall clock."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    d.rectangle([x, y + 60, x + w, y + h], fill=(170, 130, 85))
    # wall clock, top-right
    d.ellipse([x + w - 36, y + 6, x + w - 8, y + 34], fill=(255, 255, 255), outline=INK, width=1)
    d.line([x + w - 22, y + 20, x + w - 22, y + 10], fill=INK, width=2)
    d.line([x + w - 22, y + 20, x + w - 14, y + 24], fill=INK, width=2)
    # answer sheet
    d.rectangle([x + 14, y + 8, x + 92, y + 68], fill=(255, 255, 255), outline=INK, width=1)
    tf = font(SANS_B, 10)
    d.text((x + 20, y + 12), "SUNEUNG  \u00b7  551,864", font=tf, fill=INK)
    for i in range(5):
        yy = y + 28 + i * 7
        d.text((x + 20, yy - 2), f"{i + 1}.", font=font(SANS, 8), fill=MUTED)
        d.line([x + 32, yy + 3, x + 84, yy + 3], fill=(170, 170, 170), width=1)
        if i == 1:
            d.ellipse([x + 52, yy - 1, x + 60, yy + 7], fill=RED)
            d.text((x + 53, yy - 1), "\u2713", font=font(SANS_B, 7), fill=(255, 255, 255))
    # pencil, diagonal across the sheet
    d.polygon([(x + 96, y + 62), (x + 138, y + 20), (x + 132, y + 14),
               (x + 90, y + 56)], fill=(255, 200, 0))
    d.polygon([(x + 138, y + 20), (x + 146, y + 28), (x + 140, y + 32)], fill=(220, 180, 140))
    d.polygon([(x + 90, y + 56), (x + 96, y + 62), (x + 92, y + 68)], fill=(220, 180, 140))
    d.rectangle([x + 128, y + 18, x + 134, y + 26], fill=(220, 100, 100))


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
    # briefcase, bottom-left
    d.rectangle([x + 12, y + 52, x + 52, y + 72], fill=(122, 74, 44))
    d.rectangle([x + 24, y + 46, x + 40, y + 52], fill=(122, 74, 44))
    d.line([x + 12, y + 62, x + 52, y + 62], fill=(200, 160, 110), width=2)
    d.rectangle([x + 30, y + 60, x + 34, y + 64], fill=GOLD)
    # "43,500 jobs lost" note
    nf = font(SANS, 9)
    d.text((x + 58, y + 62), "43,500 jobs lost", font=nf, fill=MUTED)


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
    for wy in (56, 64, 71):
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
    # tapered tower, centre-left
    d.polygon([(x + 56, y + 70), (x + 62, y + 8), (x + 78, y + 8), (x + 84, y + 70)],
              fill=(140, 160, 190))
    for wy in range(14, 68, 7):
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
    # city lights at the base
    for bx, bh in [(8, 12), (26, 18), (100, 14), (118, 20), (136, 12)]:
        d.rectangle([x + bx, y + 70 - bh, x + bx + 12, y + 70], fill=(60, 68, 92))
        d.rectangle([x + bx + 3, y + 70 - bh + 3, x + bx + 6, y + 70 - bh + 6],
                    fill=(255, 210, 90))
    d.rectangle([x, y + 70, x + w, y + h], fill=(20, 22, 34))


def mini_gavel(d, x, y, w=154, h=76):
    """Asset-seizure law: bill document with red seal, gavel, 18 years tag."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    # bill document
    d.rectangle([x + 12, y + 8, x + 92, y + 68], fill=(255, 255, 255), outline=INK, width=1)
    tf = font(SANS_B, 9)
    d.text((x + 20, y + 12), "ASSET-SEIZURE", font=tf, fill=INK)
    for i in range(4):
        d.line([x + 20, y + 28 + i * 7, x + 86, y + 28 + i * 7], fill=(170, 170, 170), width=1)
    d.text((x + 20, y + 56), "Rp1bn+", font=font(SANS, 9), fill=MUTED)
    # red seal
    d.ellipse([x + 72, y + 50, x + 88, y + 66], fill=RED)
    d.ellipse([x + 76, y + 54, x + 84, y + 62], outline=(255, 255, 255), width=1)
    # gavel, diagonal at right
    d.line([x + 96, y + 18, x + 138, y + 60], fill=(122, 74, 44), width=4)
    d.rectangle([x + 100, y + 8, x + 122, y + 26], fill=(150, 96, 58))
    d.rectangle([x + 128, y + 58, x + 148, y + 68], fill=(150, 96, 58))
    # "18 YEARS" tag (shortened: the full "AFTER 18 YEARS" overflowed the panel)
    bf = font(SANS_B, 9)
    d.rounded_rectangle([x + 96, y + 62, x + 150, y + 76], radius=4, fill=INK)
    d.text((x + 101, y + 65), "18 YEARS", font=bf, fill=(255, 255, 255))


def mini_strike(d, x, y, w=154, h=76):
    """Colombia strike: crowd with placards, megaphone foreground."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 210))
    # placards held high
    for px, pt in [(20, "NO"), (66, "TAX"), (112, "NO")]:
        d.line([x + px + 12, y + 22, x + px + 12, y + 40], fill=(120, 100, 70), width=2)
        d.rectangle([x + px, y + 8, x + px + 26, y + 22], fill=(255, 255, 255),
                    outline=INK, width=1)
        pf = font(SANS_B, 9)
        d.text((x + px + 13 - pf.getlength(pt) / 2, y + 11), pt, font=pf, fill=RED)
    # crowd: heads + shoulders
    for cx, cy, c in [(16, 56, BLUE), (34, 50, RED), (52, 56, TEAL), (70, 50, GOLD),
                      (88, 56, (120, 60, 140)), (106, 50, GREEN), (124, 56, BLUE),
                      (140, 50, RED)]:
        d.ellipse([x + cx - 6, y + cy - 6, x + cx + 6, y + cy + 6], fill=c)
        d.rectangle([x + cx - 8, y + cy + 6, x + cx + 8, y + 74], fill=c)
    # megaphone, foreground right
    d.polygon([(x + 104, y + 30), (x + 138, y + 20), (x + 138, y + 46), (x + 104, y + 40)],
              fill=RED)
    d.rectangle([x + 96, y + 30, x + 104, y + 40], fill=DARK)
    d.line([x + 138, y + 20, x + 138, y + 46], fill=(255, 255, 255), width=2)


MINIS = {5: mini_gta, 6: mini_bridge, 7: mini_greenland, 8: mini_cyclone,
         9: mini_exam, 10: mini_jobs, 11: mini_house, 12: mini_tanker,
         13: mini_tank, 14: mini_tower, 15: mini_gavel, 16: mini_strike}

# Short red category labels for the mini cards (fit 140px at Sans-Bold 9).
MINI_CAT = {5: "GLOBAL \u00b7 GAMES", 6: "EUROPE \u00b7 WAR",
            7: "EUROPE \u00b7 POLITICS", 8: "ASIA \u00b7 WEATHER",
            9: "ASIA \u00b7 EDUCATION", 10: "OCEANIA \u00b7 ECONOMY",
            11: "ASIA \u00b7 UNREST", 12: "M. EAST \u00b7 CLAIM",
            13: "M. EAST \u00b7 CONFLICT", 14: "M. EAST \u00b7 ATTACK",
            15: "ASIA \u00b7 LAW", 16: "LATAM \u00b7 STRIKE"}


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

    # ---- Section A: masthead (0-140)
    title_f = font(SERIF_B, 42)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - title_f.getlength(t)) / 2, 20), t, font=title_f, fill=INK)
    d.line([MARGIN, 70, W - MARGIN, 70], fill=INK, width=2)
    date_f = font(SANS_B, 15)
    t2 = "THURSDAY 19 NOVEMBER 2026  \u00b7  50 STORIES  \u00b7  7 REGIONS  \u00b7  CLAIMS LABELLED"
    d.text(((W - date_f.getlength(t2)) / 2, 76), t2, font=date_f, fill=RED)
    # stat strip: 5 boxes, y=98-134
    stats = data["stats"]
    gap = 8
    sw = (CW - gap * (len(stats) - 1)) // len(stats)
    sy, sh = 98, 36
    for i, s in enumerate(stats):
        sx = MARGIN + i * (sw + gap)
        d.rectangle([sx, sy, sx + sw, sy + sh], fill=CARD, outline=RULE)
        vf = font(SANS_B, 15)
        lf = font(SANS, 9)
        d.text((sx + 7, sy + 3), s["value"], font=vf, fill=INK)
        lab = trim_one(s["label"], lf, sw - 14)
        d.text((sx + 7, sy + 21), lab, font=lf, fill=MUTED)

    # ---- Section B: four hero cards, ONE row (145-390)
    heroes = data["featured"][:4]
    hero_xs = [24, 270, 516, 762]
    hf = font(SERIF_B, 15)
    sf = font(SANS, 11)
    mf = font(SANS, 10)
    for hx, s in zip(hero_xs, heroes):
        hy = 145
        d.rectangle([hx, hy, hx + 238, hy + 245], fill=CARD, outline=RULE)
        HEROES[s["n"]](d, hx + 1, hy + 1, 236, 120)
        num_badge(d, hx + 7, hy + 7, s["n"])
        if s["confidence"] == "claim":
            chip(d, hx + 238 - 62, hy + 7, "CLAIM", font(SANS_B, 9),
                 (255, 255, 255), RED)
        elif VERIFIED_CHIP.get(s["n"], True):
            chip(d, hx + 238 - 82, hy + 7, "VERIFIED", font(SANS_B, 9),
                 (255, 255, 255), TEAL)
        # hero 4 carries NO chip (see VERIFIED_CHIP audit note above)
        ty = hy + 127
        for ln in fit_lines(s["headline"], hf, 222, 2):
            d.text((hx + 8, ty), ln, font=hf, fill=INK)
            ty += 17
        ty = hy + 165
        for ln in fit_lines(s["summary"], sf, 222, 3):
            d.text((hx + 8, ty), ln, font=sf, fill=(60, 60, 60))
            ty += 14
        d.text((hx + 8, hy + 223),
               f"{s['place']}  \u2014  {s['source']}", font=mf, fill=MUTED)

    # ---- Section C: twelve mini cards, 6x2 (395-715)
    cards = data["featured"][4:16]
    mini_xs = [24, 188, 352, 516, 680, 844]
    mini_ys = [395, 559]
    cf = font(SANS_B, 9)
    chf = font(SANS_B, 12)
    cmf = font(SANS, 9)
    for i, s in enumerate(cards):
        cx = mini_xs[i % 6]
        cy = mini_ys[i // 6]
        d.rectangle([cx, cy, cx + 156, cy + 156], fill=CARD, outline=RULE)
        MINIS[s["n"]](d, cx + 1, cy + 1, 154, 76)
        num_badge(d, cx + 3, cy + 12, s["n"])
        d.text((cx + 8, cy + 80), MINI_CAT[s["n"]], font=cf, fill=RED)
        ty = cy + 93
        lines = fit_lines(s["headline"], chf, 140, 3)
        for li, ln in enumerate(lines):
            if li == 0 and s["confidence"] == "claim" and ln.startswith("CLAIM:"):
                d.text((cx + 8, ty), "CLAIM:", font=chf, fill=RED)
                rest = ln[len("CLAIM:"):]
                d.text((cx + 8 + chf.getlength("CLAIM:"), ty), rest, font=chf, fill=INK)
            else:
                d.text((cx + 8, ty), ln, font=chf, fill=INK)
            ty += 13
        d.text((cx + 8, cy + 136), trim_one(s["place"], cmf, 140), font=cmf, fill=MUTED)
        d.text((cx + 8, cy + 146), trim_one(s["source"], cmf, 140), font=cmf, fill=MUTED)

    # ---- Section D: world map + newswire (720-955)
    pins = draw_map(d)
    nf = font(SANS_B, 13)
    d.text((440, 722), "ALSO ON THURSDAY 19 NOVEMBER (34 stories, 3 cols)",
           font=nf, fill=INK)
    # Newswire: 34 items, 3 columns, 17px item pitch. Two lines per item
    # (headline bold 9 / place-source regular 8) so headline, place and
    # source all stay visible - see module docstring note 2.
    rows = data["also"]
    nwf = font(SANS_B, 9)
    nwm = font(SANS, 8)
    cols = [(436, 183, rows[0:12]), (627, 183, rows[12:23]), (818, 182, rows[23:34])]
    for nx, colw, items in cols:
        for j, s in enumerate(items):
            ny = 742 + j * 17
            head = trim_one(f"{s['n']}. {s['headline']}", nwf, colw)
            draw_claim_headline(d, nx, ny, head, nwf, colw)
            meta = trim_one(f"{s['place']} \u2014 {s['source']}", nwm, colw)
            d.text((nx, ny + 9), meta, font=nwm, fill=MUTED)

    # ---- Section E: footer (960-1024)
    ff = font(SANS, 9)
    f1 = ("Sources: Reuters \u00b7 AP \u00b7 White House \u00b7 ICJ \u00b7 WSJ \u00b7 CNN \u00b7 GOV.UK \u00b7 national wires.")
    f2 = ("Date-checked: 7 Wed-dated stories removed \u2014 Van Gogh sale, IAEA Yongbyon, US-Venezuela pact, "
          "EU loan proposal, Taiz water crisis, US carrier departure, Kuwait/Bahrain drones.")
    f3 = ("CLAIM = unverified claim, never fact. All 50 stories happened or were first reported Thu 19 Nov 2026.")
    d.line([MARGIN, 960, W - MARGIN, 960], fill=RULE, width=1)
    d.text((MARGIN, 988), trim_one(f1, ff, CW), font=ff, fill=MUTED)
    d.text((MARGIN, 1000), trim_one(f2, ff, CW), font=ff, fill=MUTED)
    d.text((MARGIN, 1012), trim_one(f3, ff, CW), font=ff, fill=MUTED)

    img.save(HERE / "entry.png", format="PNG", optimize=True)
    n_stories = len(data["featured"]) + len(data["also"])
    print(f"entry.png {img.size} saved; stories={n_stories} "
          f"(featured {len(data['featured'])}, also {len(data['also'])}), "
          f"illustrations=16, map pins={len(pins)} {sorted(pins)} "
          f"(5 = GLOBAL legend, no dot)")


if __name__ == "__main__":
    main()
