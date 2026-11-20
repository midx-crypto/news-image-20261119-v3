#!/usr/bin/env python3
"""V8 PRODUCTION — Geographic Intelligence Atlas (V8.2 baseline, production port).
Refinement of B2 (b2-prototype.png, SHA-256 93f426ca...). Fixes the five
coordinator inspection findings (heroes, map drama, Europe inset window,
Brussels mislabel, number-led minis) plus hero-summary truncation. Design
exploration only: no submission, no quota, no production file touched.
Data: news.json beside this file (v7.1 dataset, 35 stories); land from
land110.geojson beside this file (Natural Earth 110m, 127 features).
Deterministic PIL render, 1024x1024. Fixed seed; no randomness, no wall clock.
"""
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

random.seed(20261119)
HERE = Path(__file__).resolve().parent
DATA = json.load(open(HERE / "news.json"))
LAND = HERE / "land110.geojson"
OUT  = HERE / "entry.png"

F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SANS    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(p, s): return ImageFont.truetype(p, s)

PAPER   = (247, 243, 234)
INK     = (24, 28, 34)
MUTED   = (96, 100, 108)
RULE    = (180, 172, 156)
OCEAN   = (168, 196, 214)
OCEAN_T = (160, 192, 212)   # V8-final (A): teal-to-navy ocean gradient, top
OCEAN_B = (104, 146, 178)   # V8-final (A): teal-to-navy ocean gradient, bottom
RIDGE   = (96, 74, 52)      # V8-final (A): mountain ridge marks
LANDC   = (231, 221, 197)   # V8-final (A): parchment, slightly warmer than V8.2
LANDOUT = (138, 123, 92)
CARD    = (255, 255, 255)
NAVY    = (22, 42, 66)
GOLD    = (176, 141, 44)
CLAIM_BG= (253, 238, 205)
CLAIM_TX= (146, 90, 8)

REGION = {
    "Asia":          (198, 62, 52),
    "Europe":        (46, 111, 183),
    "North America": (31, 138, 91),
    "Latin America": (214, 110, 34),
    "Africa":        (128, 68, 164),
    "Middle East":   (176, 141, 44),
    "Oceania":       (22, 160, 133),
}

data = DATA
featured = data["featured"]
also     = data["also"]
assert len(featured) == 15 and len(also) == 20, (len(featured), len(also))
heroes, secondary = featured[:3], featured[3:]
stats = data["stats"]

def wrap(text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= width: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_lines(d, x, y, lines, f, fill, leading=None):
    lh = leading or int(f.size * 1.22)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y

def sky(d, box, top, bot):
    x0, y0, x1, y1 = box
    for i in range(y1 - y0):
        t = i / max(1, y1 - y0 - 1)
        c = tuple(int(top[j] + (bot[j] - top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)

W = H = 1024
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img, "RGBA")

# ================= MASTHEAD (light — B fix: navy bookends were heavy) y 0..58
d.rectangle([0, 0, W, 58], fill=(250, 247, 238))
d.text((16, 8), "THE WORLD IN ONE DAY", font=font(F_SERIF_B, 30), fill=NAVY)
d.text((16, 42), "WORLD INTELLIGENCE ATLAS  ·  A GEOGRAPHIC FRONT PAGE",
       font=font(F_SANS_B, 10), fill=GOLD)
d.text((W-16, 10), "THURSDAY 19 NOVEMBER 2026", font=font(F_SANS_B, 13),
       fill=NAVY, anchor="ra")
d.text((W-16, 32), "35 STORIES  ·  7 REGIONS  ·  ONE DAY",
       font=font(F_SANS, 10), fill=MUTED, anchor="ra")
d.rectangle([0, 56, W, 59], fill=GOLD)
d.rectangle([0, 59, W, 60], fill=NAVY)

# ================= HEROES y 60..248 (h 188, scenes 104 px tall) =================
# REFINED: HY 62 -> 60 (masthead-to-heroes gap 2 px -> 0 px, cards sit on the
# gold rule) as part of the +14 px map-height reclaim, see MAP ZONE below.
HY, HH = 60, 188
HW, HGAP = 328, 8

def hero_summit(box):
    x0, y0, x1, y1 = box
    sky(d, box, (252, 200, 122), (216, 132, 72))
    d.ellipse([x1-72, y0+6, x1-28, y0+50], fill=(255, 238, 172))
    # midground skyline
    for bx, bw, bh, c in [(x0+6, 44, 46, (52,58,74)), (x0+56, 32, 62, (40,46,62)),
                          (x0+94, 50, 40, (66,72,88)), (x0+150, 30, 70, (34,40,54)),
                          (x0+186, 42, 48, (52,58,74)), (x0+234, 34, 58, (44,50,66)),
                          (x0+274, 40, 44, (58,64,80))]:
        d.rectangle([bx, y1-52-bh+22, bx+bw, y1-30], fill=c)
        for wy in range(y1-52-bh+28, y1-34, 11):
            for wx in range(bx+5, bx+bw-4, 9):
                d.rectangle([wx, wy, wx+4, wy+5], fill=(255, 214, 110))
    # three flags in the gaps BETWEEN the figures (poles moved off the
    # figures' heads: larger heads now reach y1-66, where the old poles stood)
    for fx, fc in [(x0+24, (178,34,34)), (x0+118, (198,62,52)), (x0+218, (240,240,240))]:
        d.line([(fx, y1-64), (fx, y1-30)], fill=(30,30,30), width=2)
        d.polygon([(fx, y1-64), (fx+22, y1-58), (fx, y1-52)], fill=fc)
    # foreground: conference table + three distinguishable figures.
    # REFINED: larger heads (r 14, was 11), distinct hair (Trump blond sweep,
    # Xi black side-part, Putin grey receding), brows / eyes / nose / smile,
    # wider suits with shirt V + tie. Nameplates kept.
    # (No ribbon: it collided with the figures' heads in the first render;
    #  the declaration quote is carried in the summary below the scene)
    d.rectangle([x0+14, y1-30, x1-14, y1-2], fill=(96, 66, 40))
    d.rectangle([x0+14, y1-30, x1-14, y1-24], fill=(122, 86, 52))
    figs = [(x0+70, (232,196,150), (240,205,110), "TRUMP", (30,44,66), (178,34,34),
             (200,170,100), "blond"),
            ((x0+x1)//2, (240,210,170), (35,35,35), "XI", (178,34,34), (22,42,66),
             (30,30,30), "sidepart"),
            (x1-70, (232,200,160), (190,190,190), "PUTIN", (70,70,70), (46,111,183),
             (150,150,150), "receding")]
    for cx, skin, hair, name, suit, tie, brow, style in figs:
        # wider suit: shoulders above the table, white shirt V, tie
        d.polygon([(cx-20, y1-30), (cx-20, y1-38), (cx+20, y1-38), (cx+20, y1-30)], fill=suit)
        d.polygon([(cx-6, y1-38), (cx+6, y1-38), (cx, y1-30)], fill=(255,255,255))
        d.polygon([(cx-2, y1-38), (cx+2, y1-38), (cx+3, y1-31), (cx, y1-29), (cx-3, y1-31)], fill=tie)
        # larger head
        d.ellipse([cx-14, y1-66, cx+14, y1-38], fill=skin)
        # hair: cap hairline at y1-56 (10 px down the 28 px head)
        if style == "receding":
            # grey only at the sides + a thin crescent at the very top: bare forehead
            d.arc([cx-14, y1-66, cx+14, y1-38], 180, 360, fill=hair, width=3)
            d.ellipse([cx-15, y1-60, cx-9, y1-48], fill=hair)
            d.ellipse([cx+9, y1-60, cx+15, y1-48], fill=hair)
        else:
            d.pieslice([cx-14, y1-66, cx+14, y1-46], 180, 360, fill=hair)
            if style == "blond":
                # swept fringe: a blond wedge dipping across the forehead
                d.polygon([(cx-13, y1-58), (cx-2, y1-61), (cx+12, y1-57),
                           (cx+13, y1-52), (cx+2, y1-55), (cx-10, y1-54)], fill=hair)
            else:  # sidepart: a skin part-line on the left side
                d.line([(cx-7, y1-65), (cx-4, y1-56)], fill=skin, width=2)
        # face: brows, eyes, nose, smile
        d.line([(cx-9, y1-55), (cx-4, y1-56)], fill=brow, width=2)
        d.line([(cx+4, y1-56), (cx+9, y1-55)], fill=brow, width=2)
        d.ellipse([cx-7, y1-52, cx-5, y1-50], fill=(40,30,25))
        d.ellipse([cx+5, y1-52, cx+7, y1-50], fill=(40,30,25))
        d.line([(cx, y1-50), (cx, y1-46)], fill=(180,140,110), width=1)
        d.arc([cx-5, y1-46, cx+5, y1-40], 0, 180, fill=(150,80,60), width=1)
        d.rectangle([cx-16, y1-18, cx+16, y1-6], fill=(250,246,236), outline=(120,110,90))
        d.text((cx, y1-12), name, font=font(F_SANS_B, 7), fill=INK, anchor="mm")

def hero_icj(box):
    x0, y0, x1, y1 = box
    sky(d, box, (200, 216, 230), (158, 182, 202))
    d.ellipse([x0+16, y0+8, x0+54, y0+46], fill=(255, 244, 200))
    # REFINED layering: clouds in the sky, a tree + a flagpole flanking the
    # palace, plaza paving + a soft shadow under the scales. Composition kept:
    # palace centre, tower left, scales bottom-left, vote chip bottom-right.
    d.ellipse([x0+96, y0+6, x0+132, y0+16], fill=(238, 242, 246))
    d.ellipse([x0+118, y0+2, x0+150, y0+12], fill=(238, 242, 246))
    d.ellipse([x1-108, y0+12, x1-78, y0+20], fill=(238, 242, 246))
    # Peace Palace: brick hall + clock tower
    d.rectangle([x0+58, y1-72, x1-58, y1-30], fill=(176, 120, 84))
    d.polygon([(x0+48, y1-72), ((x0+x1)//2, y1-88), (x1-48, y1-72)], fill=(150, 56, 48))
    d.rectangle([x0+58, y1-76, x0+82, y1-30], fill=(160, 104, 72))   # tower
    d.polygon([(x0+54, y1-76), (x0+70, y1-90), (x0+86, y1-76)], fill=(120, 40, 36))
    d.ellipse([x0+63, y1-72, x0+77, y1-58], fill=(250,246,236), outline=(60,50,40))
    d.line([(x0+70, y1-65), (x0+70, y1-70)], fill=(40,40,40), width=1)
    d.line([(x0+70, y1-65), (x0+74, y1-63)], fill=(40,40,40), width=1)
    for i in range(4):
        cx = x0 + 100 + i * 40
        d.rectangle([cx, y1-66, cx+11, y1-36], fill=(250, 246, 236))
        d.rectangle([cx-3, y1-70, cx+14, y1-66], fill=(250, 246, 236))
    d.rectangle([(x0+x1)//2-11, y1-52, (x0+x1)//2+11, y1-30], fill=(70, 58, 44))
    d.rectangle([x0+40, y1-30, x1-40, y1-24], fill=(120, 110, 92))
    # tree left of the palace, flagpole right (pole stops where the vote chip
    # starts, so the chip covers its foot)
    d.line([(x0+38, y1-30), (x0+38, y1-48)], fill=(90, 70, 40), width=2)
    d.ellipse([x0+26, y1-58, x0+50, y1-40], fill=(70, 110, 70))
    d.ellipse([x0+30, y1-62, x0+46, y1-48], fill=(90, 130, 80))
    d.line([(x1-34, y1-30), (x1-34, y1-84)], fill=(60, 60, 60), width=2)
    d.polygon([(x1-34, y1-84), (x1-14, y1-78), (x1-34, y1-72)], fill=(140, 180, 220))
    # plaza paving lines in the foreground
    d.line([(x0+20, y1-16), (x1-20, y1-16)], fill=(200, 190, 170), width=1)
    d.line([(x0+20, y1-8), (x1-20, y1-8)], fill=(200, 190, 170), width=1)
    # foreground: scales of justice + 9-6 vote bar
    cx = x0 + 52
    d.ellipse([cx-26, y1-10, cx+26, y1-2], fill=(0, 0, 0, 40))  # soft shadow
    d.line([(cx, y1-24), (cx, y1-6)], fill=(176,141,44), width=3)
    d.line([(cx-18, y1-22), (cx+18, y1-22)], fill=(176,141,44), width=2)
    d.polygon([(cx-24, y1-8), (cx-12, y1-8), (cx-18, y1-16)], fill=(176,141,44))
    d.polygon([(cx+12, y1-8), (cx+24, y1-8), (cx+18, y1-16)], fill=(176,141,44))
    d.ellipse([cx-3, y1-26, cx+3, y1-20], fill=(176,141,44))
    # vote device, right foreground: dark chip so the white label and the
    # 9 gold / 6 grey segments read against the pale palace
    bx0, by0 = x1-132, y1-32
    d.rectangle([bx0, by0, x1-6, y1-4], fill=(22, 42, 66))
    d.text((bx0+6, by0+3), "ICJ VOTE  9-6", font=font(F_SANS_B, 8), fill=(255,255,255))
    for i in range(15):
        col = GOLD if i < 9 else (200, 200, 200)
        d.rectangle([bx0+6+i*7, by0+15, bx0+6+i*7+5, by0+24], fill=col)

def hero_cop(box):
    x0, y0, x1, y1 = box
    sky(d, box, (238, 226, 170), (168, 200, 216))
    d.ellipse([x0+18, y0+8, x0+60, y0+50], fill=(255, 240, 170))
    # REFINED layering: clouds, distant hills behind the turbines, a second
    # document page peeking behind the draft, wave lines on the sea band.
    # Composition kept: turbines left/right, globe top-right, doc centre.
    d.ellipse([x0+96, y0+6, x0+128, y0+15], fill=(244, 240, 224))
    d.ellipse([x0+118, y0+2, x0+148, y0+11], fill=(244, 240, 224))
    d.polygon([(x0, y1-34), (x0+60, y1-52), (x0+130, y1-40), (x0+200, y1-54),
               (x0+260, y1-42), (x1, y1-34)], fill=(140, 160, 140))
    # background: turbines, solar, globe, sea
    for tx in (x0+36, x0+286):
        d.line([(tx, y1-30), (tx, y1-58)], fill=(40,60,80), width=3)
        cx, cy = tx, y1-60
        for ang in (90, 210, 330):
            ex = cx + 15*math.cos(math.radians(ang)); ey = cy - 15*math.sin(math.radians(ang))
            d.line([(cx, cy), (ex, ey)], fill=(40,60,80), width=3)
        d.ellipse([cx-3, cy-3, cx+3, cy+3], fill=(40,60,80))
    d.polygon([(x0+210, y1-30), (x0+238, y1-30), (x0+244, y1-48), (x0+216, y1-48)], fill=(36,64,120))
    d.ellipse([x0+250, y0+10, x0+292, y0+52], fill=(70,130,170), outline=(40,80,120))
    d.ellipse([x0+258, y0+18, x0+284, y0+44], fill=(120,190,120))
    d.rectangle([x0, y1-30, x1, y1], fill=(64, 130, 170))
    d.rectangle([x0, y1-34, x1, y1-30], fill=(232, 220, 180))
    # wave lines on the sea band
    for wx, wy in [(x0+16, y1-18), (x0+120, y1-12), (x0+230, y1-20), (x0+280, y1-10)]:
        d.arc([wx, wy, wx+22, wy+8], 180, 360, fill=(220, 235, 240), width=1)
    # foreground: draft document, fossil-fuel language struck out
    # (doc starts below the badge band so its header is never covered)
    # second page peeking behind the draft, offset down-right
    px0, py0, px1, py1 = x0+72, y0+26, x1-84, y1-8
    d.rectangle([px0+6, py0+6, px1+6, py1+6], fill=(228, 224, 210), outline=(150, 140, 120), width=1)
    d.polygon([(px0+8, py1+4), (px1-4, py1+4), (px1, py1), (px0+4, py1)], fill=(210,200,180))
    d.rectangle([px0, py0, px1, py1], fill=(255, 255, 255), outline=(120,110,90), width=1)
    d.text((px0+10, py0+6), "COP31  ·  DRAFT DEAL TEXT", font=font(F_SANS_B, 8), fill=MUTED)
    for i in range(2):
        d.rectangle([px0+10, py0+20+i*7, px1-10, py0+23+i*7], fill=(200,200,200))
    d.text((px0+10, py0+36), "FOSSIL FUELS", font=font(F_SANS_B, 12), fill=(150,40,30))
    d.line([(px0+8, py0+43), (px0+108, py0+41)], fill=(198,40,30), width=3)
    d.rectangle([px0+10, py0+52, px1-10, py0+55], fill=(200,200,200))
    d.text((px0+10, py0+58), "$120bn adaptation target — removed", font=font(F_SANS, 8), fill=MUTED)
    d.line([(px0+8, py0+65), (px1-10, py0+63)], fill=(198,40,30), width=2)
    # CUT stamp, rotated via small polygon frame
    sx, sy = px1-52, py0+34
    d.rectangle([sx, sy, sx+46, sy+18], outline=(198,40,30), width=2)
    d.text((sx+23, sy+9), "CUT", font=font(F_SANS_B, 12), fill=(198,40,30), anchor="mm")

# ---- V8.2 hero rework (overrides the V8.1 definitions above; same card
# geometry, new artwork inside). Rank-1 reference: big half-figure portraits
# against full flag panels, nameplates on the table front. Scene box is
# 326x104; the caller darkens the top 22 px as a banner, so art lives below
# y0+22.
def hero_summit(box):
    x0, y0, x1, y1 = box
    cxm = (x0 + x1) // 2
    # deep navy wall with a warm centre glow
    sky(d, box, (26, 42, 72), (44, 66, 104))
    # (no glow ellipse: an earlier glow bled past the scene box into the
    # masthead and the headline area; the flags + navy wall carry the depth)
    # three full flag panels behind the figures (rank-1 device)
    fxs = [x0+8, cxm-49, x1-104]
    # US flag: stripes + canton
    d.rectangle([fxs[0], y0+6, fxs[0]+96, y1-28], fill=(255, 255, 255))
    for i in range(7):
        d.rectangle([fxs[0], y0+6+i*11, fxs[0]+96, y0+6+i*11+5], fill=(178, 34, 34))
    d.rectangle([fxs[0], y0+6, fxs[0]+40, y0+40], fill=(30, 50, 110))
    for r in range(3):
        for c in range(4):
            d.ellipse([fxs[0]+4+c*9, y0+10+r*10, fxs[0]+8+c*9, y0+14+r*10], fill=(255,255,255))
    # China flag: red field, one large + four small gold stars
    d.rectangle([fxs[1], y0+6, fxs[1]+96, y1-28], fill=(222, 41, 16))
    d.polygon([(fxs[1]+16, y0+12), (fxs[1]+19, y0+19), (fxs[1]+26, y0+19), (fxs[1]+20, y0+24),
               (fxs[1]+22, y0+31), (fxs[1]+16, y0+27), (fxs[1]+10, y0+31), (fxs[1]+12, y0+24),
               (fxs[1]+6, y0+19), (fxs[1]+13, y0+19)], fill=(255, 215, 0))
    for sx, sy in [(fxs[1]+36, y0+12), (fxs[1]+42, y0+18), (fxs[1]+40, y0+26), (fxs[1]+33, y0+28)]:
        d.ellipse([sx-3, sy-3, sx+3, sy+3], fill=(255, 215, 0))
    # Russia flag: white / blue / red horizontal thirds
    d.rectangle([fxs[2], y0+6, fxs[2]+96, y1-28], fill=(255, 255, 255))
    d.rectangle([fxs[2], y0+6+22, fxs[2]+96, y0+6+44], fill=(0, 60, 160))
    d.rectangle([fxs[2], y0+6+44, fxs[2]+96, y1-28], fill=(200, 30, 30))
    # thin gold frame line under the flags
    d.line([(x0, y1-28), (x1, y1-28)], fill=(176, 141, 44), width=2)
    # table: polished dark wood top + front panel
    d.rectangle([x0+6, y1-28, x1-6, y1-22], fill=(140, 100, 60))
    d.rectangle([x0+6, y1-22, x1-6, y1-2], fill=(96, 66, 40))
    d.line([(x0+6, y1-22), (x1-6, y1-22)], fill=(176, 141, 44), width=1)
    # three large half-figure portraits
    figs = [(x0+56, (236, 198, 152), (240, 205, 110), "TRUMP", (26, 40, 64), (178, 34, 34), "blond"),
            (cxm, (242, 212, 172), (32, 32, 32), "XI", (24, 24, 28), (22, 42, 66), "sidepart"),
            (x1-56, (234, 202, 162), (185, 185, 185), "PUTIN", (68, 70, 76), (46, 111, 183), "receding")]
    for cx, skin, hair, name, suit, tie, style in figs:
        # shoulders: broad suit with lapels + shirt V + tie
        d.polygon([(cx-30, y1-28), (cx-28, y1-52), (cx-12, y1-56), (cx+12, y1-56),
                   (cx+28, y1-52), (cx+30, y1-28)], fill=suit)
        d.polygon([(cx-9, y1-56), (cx+9, y1-56), (cx, y1-34)], fill=(255, 255, 255))
        d.polygon([(cx-12, y1-56), (cx-9, y1-56), (cx, y1-40), (cx-4, y1-52)], fill=(suit[0]+18, suit[1]+18, suit[2]+18))
        d.polygon([(cx+12, y1-56), (cx+9, y1-56), (cx, y1-40), (cx+4, y1-52)], fill=(suit[0]+18, suit[1]+18, suit[2]+18))
        d.polygon([(cx-3, y1-56), (cx+3, y1-56), (cx+4, y1-36), (cx, y1-32), (cx-4, y1-36)], fill=tie)
        # head r15, with soft side shading
        d.ellipse([cx-15, y1-80, cx+15, y1-50], fill=skin)
        d.arc([cx-15, y1-80, cx+15, y1-50], 300, 90, fill=(200, 160, 120), width=2)
        if style == "receding":
            d.arc([cx-15, y1-80, cx+15, y1-50], 180, 360, fill=hair, width=4)
            d.ellipse([cx-16, y1-72, cx-10, y1-58], fill=hair)
            d.ellipse([cx+10, y1-72, cx+16, y1-58], fill=hair)
        else:
            d.pieslice([cx-15, y1-80, cx+15, y1-58], 180, 360, fill=hair)
            if style == "blond":
                d.polygon([(cx-14, y1-72), (cx-2, y1-75), (cx+13, y1-71),
                           (cx+14, y1-65), (cx+2, y1-69), (cx-11, y1-68)], fill=hair)
            else:
                d.line([(cx-8, y1-79), (cx-4, y1-68)], fill=skin, width=2)
        # face: heavier brows, eyes, nose, smile
        d.line([(cx-10, y1-68), (cx-4, y1-69)], fill=(60, 45, 30), width=2)
        d.line([(cx+4, y1-69), (cx+10, y1-68)], fill=(60, 45, 30), width=2)
        d.ellipse([cx-8, y1-65, cx-5, y1-62], fill=(35, 25, 20))
        d.ellipse([cx+5, y1-65, cx+8, y1-62], fill=(35, 25, 20))
        d.line([(cx, y1-62), (cx-1, y1-57)], fill=(180, 140, 110), width=2)
        d.arc([cx-6, y1-58, cx+6, y1-51], 0, 180, fill=(150, 80, 60), width=2)
        # gooseneck microphone on the table in front of each figure
        d.line([(cx+24, y1-28), (cx+24, y1-44)], fill=(30, 30, 30), width=2)
        d.ellipse([cx+21, y1-48, cx+27, y1-42], fill=(30, 30, 30))
        # nameplate on the table front
        d.rectangle([cx-18, y1-20, cx+18, y1-6], fill=(250, 246, 236), outline=(120, 110, 90))
        d.text((cx, y1-13), name, font=font(F_SANS_B, 7), fill=INK, anchor="mm")

def hero_icj(box):
    x0, y0, x1, y1 = box
    cxm = (x0 + x1) // 2
    sky(d, box, (196, 214, 230), (150, 176, 200))
    # sun top-right, clear of the tree (left) this time
    d.ellipse([x1-56, y0+4, x1-22, y0+38], fill=(255, 242, 190))
    d.ellipse([x0+92, y0+4, x0+128, y0+14], fill=(238, 242, 246))
    d.ellipse([x0+112, y0+1, x0+146, y0+10], fill=(238, 242, 246))
    # soft distant rooftops behind the palace (low, muted, clear of the roofline)
    d.rectangle([x0+8, y1-44, x0+56, y1-30], fill=(158, 172, 186))
    d.rectangle([x1-56, y1-44, x1-8, y1-30], fill=(158, 172, 186))
    # flag poles flanking the palace: UN blue left, Dutch right
    d.line([(x0+22, y1-30), (x0+22, y1-86)], fill=(60, 60, 60), width=2)
    d.polygon([(x0+22, y1-86), (x0+44, y1-80), (x0+22, y1-74)], fill=(60, 120, 200))
    d.line([(x1-22, y1-30), (x1-22, y1-86)], fill=(60, 60, 60), width=2)
    d.polygon([(x1-22, y1-86), (x1-44, y1-82), (x1-22, y1-78)], fill=(200, 40, 40))
    d.polygon([(x1-22, y1-78), (x1-44, y1-74), (x1-22, y1-70)], fill=(255, 255, 255))
    # Peace Palace: two-tier roof, brick hall, arched windows, lit doorway
    d.rectangle([x0+62, y1-70, x1-62, y1-30], fill=(176, 120, 84))
    d.rectangle([x0+56, y1-76, x1-56, y1-70], fill=(150, 56, 48))
    d.polygon([(x0+66, y1-76), (cxm, y1-92), (x1-66, y1-76)], fill=(120, 40, 36))
    d.rectangle([x0+62, y1-74, x0+84, y1-30], fill=(160, 104, 72))   # tower
    d.polygon([(x0+58, y1-74), (x0+73, y1-90), (x0+88, y1-74)], fill=(120, 40, 36))
    d.ellipse([x0+66, y1-70, x0+80, y1-56], fill=(250, 246, 236), outline=(60, 50, 40))
    d.line([(x0+73, y1-63), (x0+73, y1-68)], fill=(40, 40, 40), width=1)
    d.line([(x0+73, y1-63), (x0+77, y1-61)], fill=(40, 40, 40), width=1)
    for i in range(5):
        wx = x0+96+i*30
        d.rectangle([wx, y1-64, wx+14, y1-38], fill=(255, 226, 150))
        d.ellipse([wx, y1-70, wx+14, y1-58], fill=(255, 226, 150))
        d.line([(wx+7, y1-64), (wx+7, y1-38)], fill=(150, 100, 60), width=1)
    # lit arched doorway + steps
    d.rectangle([cxm-12, y1-52, cxm+12, y1-30], fill=(255, 214, 120))
    d.ellipse([cxm-12, y1-60, cxm+12, y1-46], fill=(255, 214, 120))
    d.rectangle([cxm-16, y1-30, cxm+16, y1-26], fill=(120, 110, 92))
    d.rectangle([x0+44, y1-30, x1-44, y1-24], fill=(150, 138, 118))
    d.rectangle([x0+36, y1-24, x1-36, y1-18], fill=(170, 158, 138))
    # trees flanking the steps (kept low, clear of the sun)
    for tx in (x0+46, x1-46):
        d.line([(tx, y1-18), (tx, y1-36)], fill=(90, 70, 40), width=2)
        d.ellipse([tx-10, y1-46, tx+10, y1-32], fill=(70, 110, 70))
        d.ellipse([tx-7, y1-50, tx+7, y1-38], fill=(92, 132, 82))
    # plaza paving
    d.line([(x0+16, y1-10), (x1-16, y1-10)], fill=(200, 190, 170), width=1)
    d.line([(x0+16, y1-4), (x1-16, y1-4)], fill=(200, 190, 170), width=1)
    # foreground: LARGE scales of justice, left
    cx = x0 + 58
    d.ellipse([cx-30, y1-8, cx+30, y1-1], fill=(0, 0, 0, 45))
    d.line([(cx, y1-22), (cx, y1-4)], fill=(176, 141, 44), width=4)
    d.line([(cx-22, y1-20), (cx+22, y1-20)], fill=(176, 141, 44), width=3)
    d.polygon([(cx-29, y1-6), (cx-15, y1-6), (cx-22, y1-15)], fill=(176, 141, 44))
    d.polygon([(cx+15, y1-6), (cx+29, y1-6), (cx+22, y1-15)], fill=(176, 141, 44))
    d.ellipse([cx-4, y1-26, cx+4, y1-18], fill=(176, 141, 44))
    # vote device, bottom-right: red badge + 9 gold / 6 grey segments
    bx0, by0 = x1-138, y1-32
    d.rectangle([bx0, by0, x1-6, y1-4], fill=(150, 40, 36))
    d.text((bx0+6, by0+3), "ICJ VOTE  9-6", font=font(F_SANS_B, 8), fill=(255, 255, 255))
    for i in range(15):
        col = GOLD if i < 9 else (215, 215, 215)
        d.rectangle([bx0+6+i*7, by0+15, bx0+6+i*7+5, by0+24], fill=col)

def hero_cop(box):
    x0, y0, x1, y1 = box
    sky(d, box, (226, 236, 210), (150, 196, 190))
    d.ellipse([x0+14, y0+6, x0+52, y0+44], fill=(255, 240, 170))
    d.ellipse([x0+92, y0+6, x0+126, y0+15], fill=(244, 242, 230))
    d.ellipse([x0+114, y0+2, x0+146, y0+11], fill=(244, 242, 230))
    # distant hills + turbine field (turbines kept left/centre, clear of globe)
    d.polygon([(x0, y1-36), (x0+70, y1-56), (x0+150, y1-42), (x0+220, y1-56),
               (x0+280, y1-44), (x1, y1-36)], fill=(120, 150, 120))
    for tx, th in [(x0+34, 34), (x0+96, 28), (x0+196, 32)]:
        d.line([(tx, y1-32), (tx, y1-32-th)], fill=(40, 60, 80), width=3)
        cx, cy = tx, y1-32-th
        for ang in (90, 210, 330):
            ex = cx + 16*math.cos(math.radians(ang)); ey = cy - 16*math.sin(math.radians(ang))
            d.line([(cx, cy), (ex, ey)], fill=(40, 60, 80), width=3)
        d.ellipse([cx-3, cy-3, cx+3, cy+3], fill=(40, 60, 80))
    # solar panel row, bottom-left
    for i in range(3):
        px = x0+8+i*22
        d.polygon([(px, y1-30), (px+18, y1-30), (px+22, y1-18), (px+4, y1-18)], fill=(36, 64, 120))
        d.line([(px+9, y1-30), (px+13, y1-18)], fill=(120, 160, 200), width=1)
    # globe, top-right, clear of every turbine blade
    gx, gy, gr = x1-34, y0+26, 20
    d.ellipse([gx-gr, gy-gr, gx+gr, gy+gr], fill=(70, 130, 170), outline=(40, 80, 120), width=2)
    d.ellipse([gx-12, gy-10, gx+2, gy+2], fill=(120, 190, 120))
    d.ellipse([gx-2, gy+6, gx+12, gy+16], fill=(120, 190, 120))
    d.arc([gx-gr, gy-gr, gx+gr, gy+gr], 20, 160, fill=(200, 230, 240), width=1)
    # sea band
    d.rectangle([x0, y1-30, x1, y1], fill=(64, 130, 170))
    d.rectangle([x0, y1-34, x1, y1-30], fill=(232, 220, 180))
    for wx, wy in [(x0+14, y1-18), (x0+130, y1-12), (x0+240, y1-20), (x0+286, y1-10)]:
        d.arc([wx, wy, wx+22, wy+8], 180, 360, fill=(220, 235, 240), width=1)
    # foreground: draft document (second page peeking behind), struck text
    px0, py0, px1, py1 = x0+108, y0+26, x1-58, y1-8
    d.rectangle([px0+6, py0+6, px1+6, py1+6], fill=(228, 224, 210), outline=(150, 140, 120), width=1)
    d.rectangle([px0, py0, px1, py1], fill=(255, 255, 255), outline=(120, 110, 90), width=1)
    d.text((px0+10, py0+6), "COP31  ·  DRAFT DEAL TEXT", font=font(F_SANS_B, 8), fill=MUTED)
    for i in range(2):
        d.rectangle([px0+10, py0+20+i*7, px1-10, py0+23+i*7], fill=(200, 200, 200))
    d.text((px0+10, py0+36), "FOSSIL FUELS", font=font(F_SANS_B, 12), fill=(150, 40, 30))
    d.line([(px0+8, py0+43), (px0+108, py0+41)], fill=(198, 40, 30), width=3)
    d.rectangle([px0+10, py0+52, px1-10, py0+55], fill=(200, 200, 200))
    d.text((px0+10, py0+58), "$120bn adaptation target — removed", font=font(F_SANS, 8), fill=MUTED)
    d.line([(px0+8, py0+65), (px1-10, py0+63)], fill=(198, 40, 30), width=2)
    # CUT stamp: tilted red frame
    sx, sy = px1-52, py0+34
    d.polygon([(sx, sy+3), (sx+46, sy), (sx+46, sy+15), (sx, sy+18)], outline=(198, 40, 30), width=2)
    d.text((sx+23, sy+9), "CUT", font=font(F_SANS_B, 12), fill=(198, 40, 30), anchor="mm")

HERO_SCENES = [hero_summit, hero_icj, hero_cop]
for i, s in enumerate(heroes):
    x = 8 + i * (HW + HGAP)
    rc = REGION[s["region"]]
    d.rectangle([x, HY, x+HW, HY+HH], fill=CARD, outline=RULE, width=1)
    d.rectangle([x, HY, x+HW, HY+4], fill=rc)
    HERO_SCENES[i]((x+1, HY+5, x+HW-1, HY+109))
    d.rectangle([x+1, HY+5, x+HW-1, HY+27], fill=(0, 0, 0, 110))
    d.ellipse([x+8, HY+10, x+28, HY+30], fill=rc, outline=(255,255,255), width=1)
    d.text((x+18, HY+20), str(s["n"]), font=font(F_SANS_B, 11), fill=(255,255,255), anchor="mm")
    d.text((x+34, HY+20), s["region"].upper() + "  ·  " + s["place"].upper(),
           font=font(F_SANS_B, 9), fill=(255,255,255), anchor="lm")
    y = HY + 112
    hl = wrap(s["headline"], font(F_SERIF_B, 15), HW-16)[:2]
    y = draw_lines(d, x+8, y, hl, font(F_SERIF_B, 15), INK, leading=17)
    budget = (HY+HH-16) - y - 2
    nlines = max(0, budget // 12)
    sm_all = wrap(s["summary"], font(F_SANS, 10), HW-16)
    sm = sm_all[:nlines]
    if len(sm_all) > nlines and sm:
        sm[-1] = sm[-1].rstrip() + " …"
    draw_lines(d, x+8, y+2, sm, font(F_SANS, 10), MUTED, leading=12)
    d.text((x+8, HY+HH-13), "Source: " + s["source"], font=font(F_SANS, 8), fill=MUTED)

# ================= MAP ZONE y 250..560 — REFINED: map 272 -> 286 px tall (+14) ====
# Reclaim, all from ABOVE the map (nothing below it moves):
#  - heroes HY 62 -> 60: +2 px (masthead-to-heroes gap 2 -> 0)
#  - map header two lines (title y 254 + descriptor y 271) -> ONE line:
#    title left + shortened descriptor right-aligned on the same line at y 250: +12 px
# Map panel top 288 -> 274, bottom stays 560; right rail top moves with it
# (274..560, h 286; the region key simply gets 14 px taller, 80 -> 94).
# Secondary header (566), grid, regional panels, footer: all unchanged, so no
# story is cut and no wire type shrinks. Descriptor shortened (own copy, not
# data): "Europe detail inset, lower left" kept.
d.text((8, 250), "THE MAP OF THE DAY", font=font(F_SERIF_B, 13), fill=INK)
d.text((W-8, 252), "Every numbered pin is a real place.  #5 GTA VI is worldwide — see GLOBAL box.  Europe inset, lower left.",
       font=font(F_SANS, 9), fill=MUTED, anchor="ra")

MAP = (8, 274, 776, 560)          # 768 x 286 draw area (was 768 x 272)
# V8-final (A: Cinematic Editorial Atlas): teal-to-navy ocean depth gradient.
for _yy in range(MAP[1], MAP[3]):
    _t = (_yy - MAP[1]) / max(1, MAP[3] - MAP[1] - 1)
    _c = tuple(int(OCEAN_T[j] + (OCEAN_B[j] - OCEAN_T[j]) * _t) for j in range(3))
    d.line([(MAP[0], _yy), (MAP[2], _yy)], fill=_c)
d.rectangle(MAP, outline=RULE, width=1)
land = json.load(open(LAND))
LAT_TOP, LAT_BOT = 84, -58
def project(lon, lat, box=MAP):
    x0, y0, x1, y1 = box
    return (x0 + (lon + 180) / 360 * (x1 - x0),
            y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * (y1 - y0))

for lon in range(-150, 181, 30):
    x = project(lon, 0)[0]
    d.line([(x, MAP[1]), (x, MAP[3])], fill=(255,255,255,90), width=1)
for lat in range(-30, 91, 30):
    y = project(0, lat)[1]
    d.line([(MAP[0], y), (MAP[2], y)], fill=(255,255,255,90), width=1)
for feat in land["features"]:
    geom = feat["geometry"]
    polys = geom["coordinates"] if geom["type"] == "Polygon" else \
            [p for mp in geom["coordinates"] for p in mp]
    for poly in polys:
        pts = []
        for lon, lat in poly:
            lat = max(LAT_BOT, min(LAT_TOP, lat))
            pts.append(project(lon, lat))
        if len(pts) > 2:
            d.polygon(pts, fill=LANDC, outline=LANDOUT)
# V8-final (A): mountain ridge marks — fine dark strokes on REAL ranges only.
# (Prototype-A coords + (8, 250) to production page coords.)
def ridge(x, y):
    d.line([(x, y), (x + 3, y - 4), (x + 6, y)], fill=RIDGE, width=1)
for x, y in [(553, 386), (561, 382), (569, 386), (577, 383), (585, 387)]:  # Himalayas
    ridge(x, y)
for x, y in [(241, 448), (245, 458), (242, 468)]:  # Andes (above #15 callout)
    ridge(x, y)
for x, y in [(150, 372), (158, 366), (166, 372)]:  # Rockies
    ridge(x, y)
for x, y in [(410, 360), (418, 357), (425, 360)]:  # Alps
    ridge(x, y)
for x, y in [(378, 390), (386, 387)]:  # Atlas
    ridge(x, y)
# V8-final (A): ocean labels nudged out from under the callout cards.
for txt, lon, lat in [("ATLANTIC", -30, -8), ("PACIFIC", -150, 8), ("PACIFIC", 150, -18),
                      ("INDIAN OCEAN", 20, -38), ("SOUTHERN OCEAN", -40, -52)]:
    x, y = project(lon, lat)
    d.text((x, y), txt, font=font(F_SANS_B, 10), fill=(52, 88, 118), anchor="mm")
# V8-final (A): coordinate labels on frame edges, 7px muted.
for lon in range(-150, 181, 30):
    x = project(lon, 0)[0]
    if x >= MAP[2] - 4:
        continue
    lab = f"{abs(lon)}°{'W' if lon < 0 else 'E' if lon > 0 else ''}"
    d.text((x, 277), lab, font=font(F_SANS, 7), fill=(90, 110, 128), anchor="ma")
for lat, lab in [(60, "60°N"), (30, "30°N")]:
    y = project(0, lat)[1]
    d.text((11, y), lab, font=font(F_SANS, 7), fill=(90, 110, 128), anchor="lm")
# 0° / 30°S sit right of the Europe inset; x=198 keeps clear of both the
# inset edge (196) and pin 15's badge (left edge ~215). FIX: prototype A had
# the 0° label ~2px from pin 15's dot; moved left for clearance.
for lat, lab in [(0, "0°"), (-30, "30°S")]:
    y = project(0, lat)[1]
    d.text((198, y), lab, font=font(F_SANS, 7), fill=(90, 110, 128), anchor="lm")

# ---- Europe detail inset (relieves the dense pin cluster): lon -12..38, lat 37.5..61,
# ---- placed over the empty South Atlantic, bottom-left of the map.
# ---- REFINED: lat floor 37.5 (was 35). 36.5 was tried first on paper and
# ---- REJECTED: Natural Earth 110 m still has North African coast vertices at
# ---- lat 36.6-37.35 (Tunisia/Algeria), so a 36.5 window keeps a coastal sliver.
# ---- Africa's northernmost point is ~37.35 N, so 37.5 excludes the whole
# ---- African coastline. Cost: the Turkish/Greek south coasts (36.1-36.9) are
# ---- also cut; pin 3 (Antalya, 36.90) sits clamped at the frame's bottom edge,
# ---- on Turkey's landmass, which the clipping fills down to the edge.
# ---- Clipping is now TRUE rectangular clipping (Sutherland-Hodgman) instead
# ---- of B2's vertex filter, which left straight chord artifacts across the sea.
INSET = (20, 440, 196, 552)
d.rectangle(INSET, fill=(232, 240, 246), outline=NAVY, width=2)
d.text((INSET[0]+6, INSET[1]+4), "EUROPE — DETAIL", font=font(F_SANS_B, 8), fill=NAVY)
IX0, IY0, IX1, IY1 = INSET[0], INSET[1]+16, INSET[2], INSET[3]-4
IN_LAT_TOP, IN_LAT_BOT = 61, 37.5
def iproject(lon, lat):
    return (IX0 + (lon + 12) / 50 * (IX1 - IX0),
            IY0 + (IN_LAT_TOP - lat) / (IN_LAT_TOP - IN_LAT_BOT) * (IY1 - IY0))
def clip_rect(pts, x0, y0, x1, y1):
    """Sutherland-Hodgman clip of a polygon ring to an axis-aligned rect."""
    def clip(pts, inside, intersect):
        if not pts: return []
        out = []
        for i, p in enumerate(pts):
            q = pts[i-1]
            pin, qin = inside(p), inside(q)
            if pin:
                if not qin: out.append(intersect(q, p))
                out.append(p)
            elif qin:
                out.append(intersect(q, p))
        return out
    pts = clip(pts, lambda p: p[0] >= x0,
               lambda a, b: (x0, a[1] + (b[1]-a[1]) * (x0-a[0]) / (b[0]-a[0] or 1)))
    pts = clip(pts, lambda p: p[0] <= x1,
               lambda a, b: (x1, a[1] + (b[1]-a[1]) * (x1-a[0]) / (b[0]-a[0] or 1)))
    pts = clip(pts, lambda p: p[1] >= y0,
               lambda a, b: (a[0] + (b[0]-a[0]) * (y0-a[1]) / (b[1]-a[1] or 1), y0))
    pts = clip(pts, lambda p: p[1] <= y1,
               lambda a, b: (a[0] + (b[0]-a[0]) * (y1-a[1]) / (b[1]-a[1] or 1), y1))
    return pts
for feat in land["features"]:
    geom = feat["geometry"]
    polys = geom["coordinates"] if geom["type"] == "Polygon" else \
            [p for mp in geom["coordinates"] for p in mp]
    for poly in polys:
        pts = [iproject(lon, lat) for lon, lat in poly]
        pts = clip_rect(pts, IX0, IY0, IX1, IY1)
        if len(pts) > 2:
            d.polygon(pts, fill=LANDC, outline=LANDOUT)
for n, (lon, lat) in {2: (4.30, 52.08), 7: (12.57, 55.68), 6: (36.50, 45.30),
                      3: (30.71, 36.90)}.items():
    x, y = iproject(lon, lat)
    x = min(max(x, IX0+9), IX1-10); y = min(max(y, IY0+9), IY1-10)
    rc = REGION["Europe"]
    d.ellipse([x-8, y-8, x+8, y+8], fill=rc, outline=(255,255,255), width=1)
    d.text((x, y), str(n), font=font(F_SANS_B, 8), fill=(255,255,255), anchor="mm")

# ================= V8-final (A: Cinematic Editorial Atlas) — ILLUSTRATED CALLOUTS =========
# Each: paper card, region-colour top strip, gold outline, one miniature
# editorial scene + short factual label, thin connector to the true pin dot.
# Cards sit in EMPTY ocean only; connectors are drawn before the pins so
# the pin dot covers the line end. (Prototype-A coords + (8, 250).)
# NOTE on refinement 2 (Middle East inset): no clean ocean slot exists in
# A's layout — every candidate 140x85 slot either covers land (Australia's
# Bight, New Zealand, Brazil's bulge, Siberia/Japan) or collides with a
# callout/pin (the South Atlantic slot B uses is occupied by A's #15 Quito
# callout). Per Bram's "where useful without overcrowding" qualifier and
# refinement 5 (no obscured geography), the inset is NOT forced in; B's
# geographic precision is borrowed instead via the frame coordinate labels,
# honest equator scale bar, and nudged ocean labels above.

def scene_summit(box):
    x0, y0, x1, y1 = box
    sky(d, box, (252, 200, 122), (216, 132, 72))
    d.ellipse([x1 - 22, y0 + 2, x1 - 6, y0 + 18], fill=(255, 238, 172))
    cx = (x0 + x1) // 2
    for fx, fc in [(x0 + 14, (178, 34, 34)), (cx - 2, (30, 60, 140)), (x1 - 30, (240, 240, 240))]:
        d.line([(fx, y0 + 4), (fx, y1 - 12)], fill=(30, 30, 30), width=1)
        d.polygon([(fx, y0 + 4), (fx + 12, y0 + 7), (fx, y0 + 10)], fill=fc)
    d.rectangle([x0 + 4, y1 - 12, x1 - 4, y1 - 2], fill=(96, 66, 40))
    # FIX (refinement 3): prototype busts were black silhouettes at 200%;
    # lightened to warm tan so the three figures stay recognizable.
    for hx in (x0 + 16, cx, x1 - 16):
        d.ellipse([hx - 4, y1 - 20, hx + 4, y1 - 12], fill=(186, 160, 128))

def scene_ipo(box):
    x0, y0, x1, y1 = box
    sky(d, box, (30, 60, 90), (70, 120, 150))
    d.rectangle([x0 + 4, y1 - 22, x1 - 4, y1 - 2], fill=(220, 220, 210))
    d.polygon([(x0 + 2, y1 - 22), ((x0 + x1) // 2, y1 - 32), (x1 - 2, y1 - 22)], fill=(220, 220, 210))
    for i, h in enumerate((8, 12, 10, 15)):
        bx = x0 + 7 + i * 9
        d.rectangle([bx, y1 - 4 - h, bx + 6, y1 - 4], fill=(255, 255, 255))
    d.line([(x0 + 5, y1 - 26), (x1 - 5, y1 - 10)], fill=(255, 214, 110), width=2)

def scene_cyclone(box):
    x0, y0, x1, y1 = box
    sky(d, box, (60, 80, 100), (120, 150, 170))
    cx = (x0 + x1) // 2
    cy = y0 + (y1 - y0) // 2 - 2
    for r in (13, 9, 5):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 255, 255))
    d.rectangle([x0, y1 - 6, x1, y1], fill=(90, 140, 120))

def scene_quito(box):
    x0, y0, x1, y1 = box
    sky(d, box, (140, 180, 215), (205, 225, 240))
    d.ellipse([x1 - 20, y0 + 3, x1 - 8, y0 + 15], fill=(255, 240, 180))
    d.polygon([(x0 + 2, y1 - 2), (x0 + 18, y0 + 14), (x0 + 34, y1 - 2)], fill=(90, 120, 90))
    d.polygon([(x0 + 22, y1 - 2), (x0 + 40, y0 + 8), (x1 - 2, y1 - 2)], fill=(70, 100, 75))
    d.polygon([(x0 + 15, y0 + 11), (x0 + 21, y0 + 14), (x0 + 15, y0 + 17)], fill=(255, 255, 255))
    d.polygon([(x0 + 37, y0 + 5), (x0 + 43, y0 + 8), (x0 + 37, y0 + 11)], fill=(255, 255, 255))
    px, py = (x0 + x1) // 2 - 2, y0 + 8
    d.ellipse([px - 9, py - 2, px + 9, py + 2], fill=(255, 255, 255))
    d.line([(px - 2, py - 6), (px + 2, py + 6)], fill=(255, 255, 255), width=2)

def callout(box, n, region, scene_fn, title, body_lines, source, scene_box, text_xy):
    x0, y0, x1, y1 = box
    rc = REGION[region]
    d.rectangle(box, fill=CARD, outline=GOLD, width=1)
    d.rectangle([x0, y0, x1, y0 + 3], fill=rc)
    scene_fn(scene_box)
    d.rectangle(scene_box, outline=RULE, width=1)
    cx0, cy0 = scene_box[0] + 8, scene_box[1] + 8
    d.ellipse([cx0 - 8, cy0 - 8, cx0 + 8, cy0 + 8], fill=rc, outline=(255, 255, 255), width=1)
    d.text((cx0, cy0), str(n), font=font(F_SANS_B, 8), fill=(255, 255, 255), anchor="mm")
    tx, ty, tw = text_xy
    lines = wrap(title, font(F_SANS_B, 8), tw)
    ty = draw_lines(d, tx, ty, lines, font(F_SANS_B, 8), INK, leading=10)
    ty = draw_lines(d, tx, ty, body_lines, font(F_SANS, 8), MUTED, leading=10)
    d.text((tx, ty), source, font=font(F_SANS, 7), fill=MUTED)

def connector(n, from_xy):
    x, y = project(*PINS[n])
    d.line([from_xy, (x, y)], fill=(60, 60, 60), width=1)

# PINS moved up from the pins block below: the callout connectors above need
# them at draw time. Values identical to V8.2 (verified: same coordinates).
PINS = {
 1: (114.06, 22.55), 2: (4.30, 52.08), 3: (30.71, 36.90), 4: (-74.00, 40.71),
 6: (36.50, 45.30), 7: (12.57, 55.68), 8: (85.80, 20.30), 9: (126.98, 37.57),
 10: (151.21, -33.87), 11: (36.82, -1.29), 12: (56.30, 26.60), 13: (46.68, 24.71),
 14: (106.85, -6.21), 15: (-78.51, -0.18),
}

# #4 IPO — Atlantic box; scene left, text right.
connector(4, (252, 408))
callout((252, 376, 404, 440), 4, "North America", scene_ipo,
        "ANTHROPIC IPO", ["$81.3bn debut,", "closes $97.17, +17%"],
        "New York · Investopedia",
        (256, 380, 308, 436), (312, 382, 88))
# #1 Summit — Pacific east of Japan, vertical card. Card bottom +4px vs
# prototype so the source line clears the border (was <2px margin at 200%).
connector(1, (676, 394))
callout((676, 390, 776, 472), 1, "Asia", scene_summit,
        "US-RUSSIA-CHINA SUMMIT", ["Peace declaration"],
        "Shenzhen · White House",
        (680, 394, 772, 424), (680, 428, 92))
# #8 Cyclone — open Indian Ocean south of India. Card bottom +4px vs
# prototype so the source line clears the border (was <2px margin at 200%).
connector(8, (558, 450))
callout((500, 450, 604, 532), 8, "Asia", scene_cyclone,
        "CYCLONE AKVAN", ["80,000+ evacuated,", "Odisha landfall Fri"],
        "The Hindu BusinessLine",
        (504, 454, 600, 484), (504, 488, 92))
# #15 Hegseth — South Atlantic east of the inset.
connector(15, (258, 466))
callout((222, 466, 374, 530), 15, "Latin America", scene_quito,
        "HEGSETH IN QUITO", ["Defence chief's", "LatAm tour"],
        "Quito + Honduras · dpa",
        (226, 470, 282, 526), (286, 472, 84))

# V8-final (A): gold compass rose — empty North Pacific, away from pins/cards.
ccx, ccy = 98, 380
d.ellipse([ccx - 14, ccy - 14, ccx + 14, ccy + 14], outline=NAVY, width=1)
d.line([(ccx, ccy - 14), (ccx, ccy + 14)], fill=NAVY, width=1)
d.line([(ccx - 14, ccy), (ccx + 14, ccy)], fill=NAVY, width=1)
d.polygon([(ccx, ccy - 13), (ccx + 3, ccy), (ccx, ccy + 13), (ccx - 3, ccy)],
          fill=GOLD, outline=NAVY)
d.text((ccx, ccy - 20), "N", font=font(F_SANS_B, 8), fill=NAVY, anchor="mm")

# V8-final (A): scale bar — honest only at the equator (equirectangular
# stretches with latitude). 768 px = 360 deg -> 2.1333 px/deg; 111.32 km/deg
# -> 2000 km = 38.3 px.
sb_x, sb_y = 478, 547
d.text((sb_x - 4, sb_y - 2), "SCALE AT EQUATOR", font=font(F_SANS_B, 7),
       fill=(90, 110, 128), anchor="rm")
d.rectangle([sb_x, sb_y - 4, sb_x + 19, sb_y], fill=NAVY)
d.rectangle([sb_x + 19, sb_y - 4, sb_x + 38, sb_y], fill=(255, 255, 255),
            outline=NAVY, width=1)
d.text((sb_x, sb_y - 12), "0", font=font(F_SANS, 7), fill=(90, 110, 128), anchor="ma")
d.text((sb_x + 19, sb_y - 12), "1000", font=font(F_SANS, 7), fill=(90, 110, 128), anchor="ma")
d.text((sb_x + 38, sb_y - 12), "2000 km", font=font(F_SANS, 7), fill=(90, 110, 128), anchor="ma")

# ---- pins (featured 1-4, 6-15; #5 GLOBAL, no pin) ----
# (PINS defined above, before the V8-final callouts, which connect to them.)
LEADER = {2: (-40, -22), 7: (36, -24), 6: (38, -14), 3: (-42, 18), 12: (32, 20), 13: (-38, 18)}
for s in featured:
    n = s["n"]
    if n not in PINS: continue
    x, y = project(*PINS[n])
    rc = REGION[s["region"]]
    dx, dy = LEADER.get(n, (0, 0))
    if (dx, dy) != (0, 0):
        d.ellipse([x-3, y-3, x+3, y+3], fill=rc, outline=(255,255,255), width=1)
        bx, by = x + dx, y + dy
        d.line([(x, y), (bx, by)], fill=(60, 60, 60), width=1)
        x, y = bx, by
    d.ellipse([x-9, y-9, x+9, y+9], fill=rc, outline=(255,255,255), width=2)
    d.text((x, y), str(n), font=font(F_SANS_B, 9), fill=(255,255,255), anchor="mm")
# region colour dots for wire-only places stay off the map by design (see spec):
# their geography is carried by the regional panels + place tags.

# ================= RIGHT RAIL x 784..1016, y 274..560 (top moved with the map) =================
RX0, RX1 = 784, 1016
ry = 274
d.rectangle([RX0, ry, RX1, ry+112], fill=NAVY)
d.text((RX0+10, ry+8), "ATLAS BRIEFING", font=font(F_SANS_B, 11), fill=(214, 190, 130))
d.text((RX0+10, ry+24), "BY THE NUMBERS — VERIFIED", font=font(F_SANS_B, 9), fill=(190,205,220))
sy = ry + 40
# Display labels are shortened forms of the data labels (values unchanged);
# full labels are listed in b2-spec.md. (First render: full labels ran off the
# panel edge.) The 51-48 vote bar was dropped: it duplicated stat row 5.
SHORT_LABEL = {"ICJ: Myanmar committed genocide": "ICJ: Myanmar genocide",
               "GTA VI Metacritic score": "GTA VI Metacritic score",
               "S. Korea's Suneung exam": "S. Korea's Suneung exam",
               "Evacuated ahead of Cyclone Akvan": "Cyclone Akvan evacuees",
               "Senate rejects Iran war-powers": "Senate Iran war-powers"}
for st in stats:
    d.text((RX0+10, sy), st["value"], font=font(F_SERIF_B, 13), fill=(255,255,255))
    d.text((RX0+86, sy+2), SHORT_LABEL.get(st["label"], st["label"]),
           font=font(F_SANS, 9), fill=(210, 218, 228))
    sy += 12
ry = ry + 120
d.rectangle([RX0, ry, RX1, ry+64], fill=(232, 240, 246), outline=(46,111,183), width=2)
d.text((RX0+10, ry+7), "◉  GLOBAL — NO SINGLE PIN", font=font(F_SANS_B, 10), fill=(46,111,183))
d.text((RX0+10, ry+23), "#5  GTA VI launches after 13 years", font=font(F_SERIF_B, 11), fill=INK)
d.text((RX0+10, ry+39), "Metascore 99 from 151 reviews · $79.99", font=font(F_SANS, 9), fill=MUTED)
d.text((RX0+10, ry+51), "Worldwide midnight launch · Metacritic", font=font(F_SANS, 8), fill=MUTED)
ry = ry + 72
d.rectangle([RX0, ry, RX1, 560], fill=CARD, outline=RULE, width=1)
d.text((RX0+10, ry+5), "REGIONS — COLOUR KEY", font=font(F_SANS_B, 10), fill=INK)
# two-column key (rail is shorter than B's; 7 rows in one column would not fit)
ly = ry + 22
for i, (name, c) in enumerate(REGION.items()):
    cx0 = RX0 + 10 + (112 if i >= 4 else 0)
    cy = ly + (i % 4) * 13
    d.rectangle([cx0, cy, cx0+11, cy+10], fill=c)
    cnt = sum(1 for s in featured + also if s["region"] == name)
    d.text((cx0+15, cy), f"{name} · {cnt}", font=font(F_SANS, 9), fill=INK)

# ================= SECONDARY y 566..774 — 12 location-scene cards =================
SY0 = 566
d.text((8, SY0), "AROUND THE WORLD — 12 MORE STORIES", font=font(F_SERIF_B, 13), fill=INK)
d.text((W-8, SY0+2), "each card carries its place — scene + location strip",
       font=font(F_SANS, 9), fill=MUTED, anchor="ra")

def mini(n, box):
    """Miniature editorial scene with a geographic cue; one dominant subject."""
    x0, y0, x1, y1 = box
    cx = (x0+x1)//2
    if n == 4:   # NYSE / IPO — exchange facade + rising chart
        sky(d, box, (30,60,90), (70,120,150))
        d.rectangle([x0+6, y1-26, x1-6, y1-4], fill=(220,220,210))
        d.polygon([(x0+4, y1-26), (cx, y1-40), (x1-4, y1-26)], fill=(220,220,210))
        for i, h in enumerate((10, 16, 13, 22)):
            bx = x0+10+i*11
            d.rectangle([bx, y1-6-h, bx+8, y1-6], fill=(255,255,255))
        d.line([(x0+8, y1-32), (x1-8, y1-12)], fill=(255,214,110), width=2)
    elif n == 5:  # GTA VI — night city skyline, star, globe arc
        sky(d, box, (24,28,48), (70,60,120))
        for bx, bh in [(x0+6, 22), (x0+20, 30), (x0+34, 18), (x0+46, 26)]:
            d.rectangle([bx, y1-4-bh, bx+10, y1-4], fill=(16,18,32))
        d.polygon([(cx, y0+4), (cx+4, y0+13), (cx+13, y0+13), (cx+6, y0+19),
                   (cx+9, y0+28), (cx, y0+23), (cx-9, y0+28), (cx-6, y0+19),
                   (cx-13, y0+13), (cx-4, y0+13)], fill=(255,214,110))
        d.text((cx, y1-16), "99", font=font(F_SANS_B, 12), fill=(255,214,110), anchor="mm")
    elif n == 6:  # Crimea Bridge — strait, suspension bridge, blast
        sky(d, box, (70,110,150), (150,180,200))
        d.rectangle([x0, y1-14, x1, y1], fill=(60,110,150))
        d.line([(x0+4, y1-18), (x1-4, y1-18)], fill=(255,255,255), width=3)
        d.line([(x0+14, y0+10), (x0+14, y1-18)], fill=(255,255,255), width=2)
        d.line([(x1-14, y0+10), (x1-14, y1-18)], fill=(255,255,255), width=2)
        d.ellipse([cx-9, y1-34, cx+9, y1-16], fill=(255,150,60))
        d.ellipse([cx-5, y1-30, cx+5, y1-20], fill=(255,220,120))
    elif n == 7:  # Denmark / Greenland — REFINED: Greenland outline + parliament
        # chamber (seat rows + speaker's desk) + ballot box carry the meaning;
        # "109-0" is now a small chip top-left, not the scene itself.
        sky(d, box, (110, 145, 180), (190, 205, 220))
        d.polygon([(x0+34, y0+2), (x0+54, y0+2), (x0+57, y0+9), (x0+51, y0+16),
                   (x0+55, y0+22), (x0+46, y0+22), (x0+40, y0+17), (x0+33, y0+20),
                   (x0+31, y0+12)], fill=(255,255,255), outline=(150,160,170))
        d.rectangle([x0+2, y0+3, x0+30, y0+13], fill=(178,34,34))
        d.text((x0+16, y0+8), "109-0", font=font(F_SANS_B, 7), fill=(255,255,255), anchor="mm")
        # speaker's desk + curved seat rows (chamber floor)
        d.rectangle([x0+6, y1-20, x0+26, y1-15], fill=(96, 66, 40))
        d.rectangle([x0+10, y1-23, x0+22, y1-20], fill=(250, 246, 236))
        d.rectangle([x0+2, y1-15, x1-2, y1], fill=(146, 124, 96))
        for yy in (y1-12, y1-6):
            for xx in range(x0+5, x0+27, 5):
                d.rectangle([xx, yy, xx+3, yy+3], fill=(120, 50, 45))
        # ballot box + slip, bottom-right
        d.rectangle([x0+36, y1-19, x0+42, y1-11], fill=(255,255,255), outline=(120,110,90))
        d.rectangle([x0+32, y1-12, x0+50, y1-1], fill=(250,246,236), outline=(120,110,90))
        d.line([(x0+36, y1-11), (x0+46, y1-11)], fill=(60,50,40), width=1)
    elif n == 8:  # Cyclone Akvan — spiral over Odisha coast
        sky(d, box, (60,80,100), (120,150,170))
        d.rectangle([x0, y1-12, x1, y1], fill=(90,140,120))
        d.ellipse([cx-16, y0+4, cx+16, y0+36], fill=(255,255,255))
        d.ellipse([cx-9, y0+11, cx+9, y0+29], fill=(120,150,170))
        d.ellipse([cx-3, y0+17, cx+3, y0+23], fill=(255,255,255))
        for xx in (x0+10, x0+22, x0+34, x0+46):
            d.line([(xx, y0+38), (xx-3, y0+46)], fill=(255,214,110), width=2)
    elif n == 9:  # Suneung — exam hall, desks, answer sheet
        sky(d, box, (190,160,110), (240,220,170))
        d.rectangle([x0+8, y1-14, x1-8, y1-4], fill=(120,84,50))
        d.rectangle([x0+14, y1-34, x1-14, y1-14], fill=(255,255,255))
        for i in range(4):
            d.line([(x0+18, y1-30+i*4), (x1-18, y1-30+i*4)], fill=(150,150,150), width=1)
        d.ellipse([cx-5, y0+4, cx+5, y0+14], fill=(255,214,110))
        d.polygon([(x1-14, y0+6), (x1-4, y0+10), (x1-14, y0+14)], fill=(255,180,60))
    elif n == 10:  # Australia — harbour sails + falling chart
        sky(d, box, (40,90,110), (90,150,160))
        d.rectangle([x0, y1-10, x1, y1], fill=(50,110,140))
        d.polygon([(x0+10, y1-10), (x0+22, y1-34), (x0+22, y1-10)], fill=(255,255,255))
        d.polygon([(x0+26, y1-10), (x0+38, y1-30), (x0+38, y1-10)], fill=(240,240,240))
        d.line([(x0+8, y0+8), (x1-8, y0+26)], fill=(255,120,90), width=3)
        d.text((x1-8, y0+8), "4.9%", font=font(F_SANS_B, 9), fill=(255,120,90), anchor="ra")
    elif n == 11:  # Jepchirchir — REFINED: stadium stands + floodlight, running
        # track with lane lines, a mid-stride runner in a dark singlet, a red
        # BANNED stamp top-right; "3y BAN" is now a small chip in the stands,
        # not the scene itself.
        sky(d, box, (40, 90, 120), (90, 150, 170))
        d.rectangle([x0, y0, x1, y0+14], fill=(90, 100, 120))
        for xx in range(x0+3, x1-2, 5):
            for yy in (y0+4, y0+9):
                d.rectangle([xx, yy, xx+2, yy+2], fill=(220, 220, 220))
        d.line([(x0+34, y0+2), (x0+34, y0+14)], fill=(255,255,255), width=1)
        d.ellipse([x0+31, y0, x0+37, y0+5], fill=(255,240,180))
        # "3y BAN" as a small chip in the stands, top-left
        d.rectangle([x0+2, y0+2, x0+30, y0+12], fill=(20,20,20))
        d.text((x0+16, y0+7), "3y BAN", font=font(F_SANS_B, 7), fill=(255,255,255), anchor="mm")
        d.rectangle([x0, y0+14, x1, y1-12], fill=(60, 140, 80))
        d.rectangle([x0, y1-12, x1, y1], fill=(178,34,34))
        d.line([(x0, y1-8), (x1, y1-8)], fill=(255,255,255), width=1)
        d.line([(x0, y1-4), (x1, y1-4)], fill=(255,255,255), width=1)
        # runner, mid-stride
        top = y0+16
        d.ellipse([cx-4, top, cx+4, top+8], fill=(232,196,150))
        d.rectangle([cx-3, top+8, cx+3, top+18], fill=(20,20,20))
        d.line([(cx-3, top+11), (cx+3, top+11)], fill=(198,34,34), width=1)
        d.line([(cx, top+10), (cx-8, top+15)], fill=(232,196,150), width=2)
        d.line([(cx, top+10), (cx+6, top+12)], fill=(232,196,150), width=2)
        d.line([(cx, top+18), (cx-8, y1-5)], fill=(40,40,40), width=3)
        d.line([(cx, top+18), (cx+9, y1-6)], fill=(40,40,40), width=3)
        # red BANNED stamp, top-right
        d.polygon([(x1-24, y0+15), (x1-4, y0+17), (x1-4, y0+25), (x1-24, y0+23)],
                  outline=(198,40,30), width=2)
        d.text((x1-14, y0+20), "BAN", font=font(F_SANS_B, 7), fill=(198,40,30), anchor="mm")
    elif n == 12:  # CLAIM tankers — tanker + mine warning (amber)
        sky(d, box, (150,120,60), (220,180,100))
        d.rectangle([x0, y1-14, x1, y1], fill=(90,130,150))
        d.rectangle([x0+8, y1-26, x1-8, y1-14], fill=(60,50,40))
        d.rectangle([x0+14, y1-34, x0+26, y1-26], fill=(200,200,200))
        d.ellipse([cx-8, y0+6, cx+8, y0+22], fill=(60,60,60))
        for ang in range(0, 360, 45):
            ex = cx + 11*math.cos(math.radians(ang)); ey = y0+14 + 11*math.sin(math.radians(ang))
            d.line([(cx, y0+14), (ex, ey)], fill=(60,60,60), width=1)
        d.text((x1-6, y0+6), "?", font=font(F_SANS_B, 12), fill=(146,90,8), anchor="ra")
    elif n == 13:  # Riyadh PIF Tower — tower + strike flash
        sky(d, box, (90,60,80), (160,110,130))
        d.rectangle([cx-9, y0+10, cx+9, y1-4], fill=(220,220,230))
        d.rectangle([cx-13, y0+6, cx+13, y0+12], fill=(220,220,230))
        for wy in range(y0+16, y1-8, 8):
            d.rectangle([cx-5, wy, cx+5, wy+3], fill=(120,140,170))
        d.polygon([(cx-14, y0+8), (cx, y0-2), (cx+14, y0+8)], fill=(255,180,60))
        d.line([(cx+14, y0+2), (cx+22, y0+10)], fill=(255,220,120), width=2)
    elif n == 14:  # Jakarta — parliament dome + scales
        sky(d, box, (100,90,70), (170,150,110))
        d.ellipse([cx-14, y1-30, cx+14, y1-14], fill=(200,190,170))
        d.rectangle([x0+8, y1-16, x1-8, y1-4], fill=(160,140,110))
        d.line([(cx, y1-30), (cx, y1-8)], fill=(60,50,30), width=2)
        d.line([(cx-12, y1-26), (cx+12, y1-26)], fill=(60,50,30), width=2)
        d.polygon([(cx-16, y1-10), (cx-8, y1-10), (cx-12, y1-16)], fill=(176,141,44))
        d.polygon([(cx+8, y1-10), (cx+16, y1-10), (cx+12, y1-16)], fill=(176,141,44))
    else:  # 15 Hegseth LatAm — plane + two flags over Andes
        sky(d, box, (60,100,70), (120,160,120))
        d.polygon([(x0, y1-4), (x0+20, y1-24), (x0+40, y1-4)], fill=(120,140,120))
        d.polygon([(x0+24, y1-4), (x0+44, y1-30), (x1-4, y1-4)], fill=(140,160,140))
        d.polygon([(cx-14, y0+10), (cx+16, y0+14), (cx-14, y0+18)], fill=(220,220,220))
        d.rectangle([cx+14, y0+12, cx+20, y0+16], fill=(220,220,220))
        for fx, fc in [(x0+8, (214,110,34)), (x1-28, (46,111,183))]:
            d.line([(fx, y0+22), (fx, y1-12)], fill=(255,255,255), width=2)
            d.polygon([(fx, y0+22), (fx+18, y0+27), (fx, y0+32)], fill=fc)

# ---- V8.2 mini rework (overrides the V8.1 mini above; same card geometry,
# same location strips). Each scene now carries a second layer: an environment
# behind the subject plus one event-specific detail. Scene area ~58x41.
def mini(n, box):
    """Miniature editorial scene with a geographic cue; one dominant subject."""
    x0, y0, x1, y1 = box
    cx = (x0+x1)//2
    if n == 4:   # NYSE / IPO — exchange facade + rising bars + arrow
        sky(d, box, (30, 60, 90), (70, 120, 150))
        d.rectangle([x0+4, y1-24, x1-4, y1-4], fill=(226, 226, 214))
        d.polygon([(x0+2, y1-24), (cx, y1-36), (x1-2, y1-24)], fill=(226, 226, 214))
        d.ellipse([cx-4, y1-34, cx+4, y1-26], fill=(176, 141, 44))
        for i in range(5):
            bx = x0+7+i*9
            d.rectangle([bx, y1-22, bx+5, y1-6], fill=(255, 255, 255))
        d.rectangle([x0+2, y1-6, x1-2, y1-4], fill=(180, 174, 160))
        for i, h in enumerate((6, 10, 8, 14)):
            bx = x0+10+i*11
            d.rectangle([bx, y1-6-h, bx+7, y1-6], fill=(90, 200, 120))
        d.line([(x0+8, y1-20), (x1-10, y1-34)], fill=(255, 214, 110), width=2)
        d.polygon([(x1-12, y1-34), (x1-4, y1-33), (x1-9, y1-28)], fill=(255, 214, 110))
    elif n == 5:  # GTA VI — neon night city, big VI, star, 99
        sky(d, box, (24, 28, 48), (70, 60, 120))
        d.ellipse([x1-12, y0+2, x1-4, y0+10], fill=(240, 240, 220))
        for bx, bh in [(x0+4, 20), (x0+16, 30), (x0+28, 16), (x0+40, 24)]:
            d.rectangle([bx, y1-4-bh, bx+10, y1-4], fill=(16, 18, 32))
            for wy in range(y1-bh+3, y1-6, 6):
                d.rectangle([bx+2, wy, bx+4, wy+2], fill=(255, 214, 110))
                d.rectangle([bx+6, wy+3, bx+8, wy+5], fill=(255, 214, 110))
        d.text((cx, y0+12), "VI", font=font(F_SANS_B, 16), fill=(255, 80, 200), anchor="mm")
        d.text((cx, y0+12), "VI", font=font(F_SANS_B, 16), fill=(255, 214, 110), anchor="mm")
        d.polygon([(cx-14, y0+24), (cx-12, y0+29), (cx-17, y0+29), (cx-13, y0+32),
                   (cx-14, y0+37), (cx-10, y0+34), (cx-6, y0+37), (cx-7, y0+32),
                   (cx-3, y0+29), (cx-8, y0+29)], fill=(255, 214, 110))
        d.text((cx+14, y1-14), "99", font=font(F_SANS_B, 11), fill=(255, 214, 110), anchor="mm")
    elif n == 6:  # Crimea Bridge — strait, suspension bridge, train, blast
        sky(d, box, (70, 110, 150), (150, 180, 200))
        d.rectangle([x0, y1-14, x1, y1], fill=(60, 110, 150))
        for wx in (x0+4, x0+22, x0+40):
            d.arc([wx, y1-10, wx+12, y1-5], 180, 360, fill=(200, 225, 240), width=1)
        # deck + two towers + suspension cables
        d.line([(x0+4, y1-20), (x1-4, y1-20)], fill=(255, 255, 255), width=3)
        for tx in (x0+14, x1-14):
            d.line([(tx, y0+8), (tx, y1-20)], fill=(255, 255, 255), width=2)
        d.line([(x0+14, y0+8), (cx, y1-20)], fill=(220, 220, 220), width=1)
        d.line([(x1-14, y0+8), (cx, y1-20)], fill=(220, 220, 220), width=1)
        # small rail car on the deck, left of the blast
        d.rectangle([x0+6, y1-27, x0+18, y1-21], fill=(120, 40, 40))
        d.rectangle([x0+8, y1-26, x0+11, y1-23], fill=(255, 240, 180))
        d.rectangle([x0+13, y1-26, x0+16, y1-23], fill=(255, 240, 180))
        # blast + smoke
        d.ellipse([cx-10, y1-36, cx+10, y1-16], fill=(255, 150, 60))
        d.ellipse([cx-5, y1-31, cx+5, y1-21], fill=(255, 220, 120))
        d.ellipse([cx-3, y1-44, cx+5, y1-36], fill=(120, 120, 120))
        d.ellipse([cx+4, y1-42, cx+11, y1-35], fill=(150, 150, 150))
    elif n == 7:  # Denmark / Greenland — chamber + Greenland + ballot + flag
        sky(d, box, (110, 145, 180), (190, 205, 220))
        d.polygon([(x0+34, y0+2), (x0+54, y0+2), (x0+57, y0+9), (x0+51, y0+16),
                   (x0+55, y0+22), (x0+46, y0+22), (x0+40, y0+17), (x0+33, y0+20),
                   (x0+31, y0+12)], fill=(255, 255, 255), outline=(150, 160, 170))
        d.rectangle([x0+2, y0+3, x0+30, y0+13], fill=(178, 34, 34))
        d.text((x0+16, y0+8), "109-0", font=font(F_SANS_B, 7), fill=(255, 255, 255), anchor="mm")
        # small Danish flag on the speaker's desk
        d.line([(x0+12, y1-26), (x0+12, y1-16)], fill=(60, 60, 60), width=1)
        d.polygon([(x0+12, y1-26), (x0+24, y1-23), (x0+12, y1-20)], fill=(198, 12, 48))
        d.rectangle([x0+6, y1-20, x0+26, y1-15], fill=(96, 66, 40))
        d.rectangle([x0+10, y1-23, x0+22, y1-20], fill=(250, 246, 236))
        d.rectangle([x0+2, y1-15, x1-2, y1], fill=(146, 124, 96))
        for yy in (y1-12, y1-6):
            for xx in range(x0+5, x0+27, 5):
                d.rectangle([xx, yy, xx+3, yy+3], fill=(120, 50, 45))
        d.rectangle([x0+36, y1-19, x0+42, y1-11], fill=(255, 255, 255), outline=(120, 110, 90))
        d.rectangle([x0+32, y1-12, x0+50, y1-1], fill=(250, 246, 236), outline=(120, 110, 90))
        d.line([(x0+36, y1-11), (x0+46, y1-11)], fill=(60, 50, 40), width=1)
    elif n == 8:  # Cyclone Akvan — spiral + rain + coast houses
        sky(d, box, (60, 80, 100), (120, 150, 170))
        d.rectangle([x0, y1-12, x1, y1], fill=(90, 140, 120))
        # three houses on the coast
        for hx in (x0+4, x0+18, x0+32):
            d.rectangle([hx, y1-20, hx+10, y1-12], fill=(230, 210, 180))
            d.polygon([(hx-1, y1-20), (hx+5, y1-25), (hx+11, y1-20)], fill=(178, 60, 40))
        d.rectangle([x0+44, y1-22, x1-2, y1-12], fill=(70, 110, 70))
        # spiral: concentric arcs + eye
        d.ellipse([cx-17, y0+2, cx+17, y0+36], fill=(255, 255, 255))
        d.arc([cx-13, y0+6, cx+13, y0+32], 20, 300, fill=(120, 150, 170), width=2)
        d.arc([cx-8, y0+11, cx+8, y0+27], 200, 120, fill=(120, 150, 170), width=2)
        d.ellipse([cx-4, y0+15, cx+4, y0+23], fill=(255, 255, 255))
        for xx in (x0+8, x0+20, x0+46):
            d.line([(xx, y0+38), (xx-3, y0+46)], fill=(255, 214, 110), width=2)
    elif n == 9:  # Suneung — exam hall: clock, two desk rows, students
        sky(d, box, (190, 160, 110), (240, 220, 170))
        d.ellipse([cx-6, y0+3, cx+6, y0+15], fill=(255, 255, 255), outline=(60, 50, 40))
        d.line([(cx, y0+9), (cx, y0+5)], fill=(40, 40, 40), width=1)
        d.line([(cx, y0+9), (cx+3, y0+10)], fill=(40, 40, 40), width=1)
        # back row of students (heads + shoulders)
        for sx in (x0+12, x0+28, x0+44):
            d.ellipse([sx-4, y0+16, sx+4, y0+24], fill=(232, 196, 150))
            d.rectangle([sx-6, y0+24, sx+6, y0+30], fill=(90, 110, 150))
        d.rectangle([x0+6, y1-16, x1-6, y1-12], fill=(120, 84, 50))
        # front desks + answer sheets
        for dx in (x0+8, x0+30):
            d.rectangle([dx, y1-12, dx+18, y1-4], fill=(120, 84, 50))
            d.rectangle([dx+3, y1-20, dx+15, y1-12], fill=(255, 255, 255))
            for i in range(3):
                d.line([(dx+5, y1-18+i*3), (dx+13, y1-18+i*3)], fill=(150, 150, 150), width=1)
        d.line([(x1-12, y1-22), (x1-4, y1-10)], fill=(255, 180, 60), width=2)
    elif n == 10:  # Australia — Opera House sails + bridge + falling chart
        sky(d, box, (40, 90, 110), (90, 150, 160))
        d.rectangle([x0, y1-10, x1, y1], fill=(50, 110, 140))
        # opera sails
        d.polygon([(x0+8, y1-10), (x0+18, y1-34), (x0+18, y1-10)], fill=(255, 255, 255))
        d.polygon([(x0+20, y1-10), (x0+32, y1-30), (x0+32, y1-10)], fill=(240, 240, 240))
        d.polygon([(x0+34, y1-10), (x0+44, y1-26), (x0+44, y1-10)], fill=(225, 225, 225))
        # rate chip, top-right + small descending bars at the far right edge
        d.rectangle([x1-26, y0+3, x1-3, y0+14], fill=(198, 40, 30))
        d.text((x1-14, y0+8), "4.9%", font=font(F_SANS_B, 8), fill=(255, 255, 255), anchor="mm")
        d.rectangle([x0+48, y1-22, x0+52, y1-12], fill=(255, 120, 90))
        d.rectangle([x0+54, y1-18, x1-2, y1-12], fill=(255, 120, 90))
    elif n == 11:  # Jepchirchir — stadium, floodlight, track, runner, BAN stamp
        sky(d, box, (40, 90, 120), (90, 150, 170))
        d.rectangle([x0, y0, x1, y0+14], fill=(90, 100, 120))
        for xx in range(x0+3, x1-2, 5):
            for yy in (y0+4, y0+9):
                d.rectangle([xx, yy, xx+2, yy+2], fill=(220, 220, 220))
        d.line([(x0+36, y0+2), (x0+36, y0+14)], fill=(255, 255, 255), width=1)
        d.ellipse([x0+33, y0, x0+39, y0+5], fill=(255, 240, 180))
        d.rectangle([x0+2, y0+2, x0+30, y0+12], fill=(20, 20, 20))
        d.text((x0+16, y0+7), "3y BAN", font=font(F_SANS_B, 7), fill=(255, 255, 255), anchor="mm")
        d.rectangle([x0, y0+14, x1, y1-12], fill=(60, 140, 80))
        d.rectangle([x0, y1-12, x1, y1], fill=(178, 34, 34))
        d.line([(x0, y1-9), (x1, y1-9)], fill=(255, 255, 255), width=1)
        d.line([(x0, y1-5), (x1, y1-5)], fill=(255, 255, 255), width=1)
        # runner, mid-stride, with motion lines
        top = y0+16
        d.line([(cx-12, top+6), (cx-8, top+6)], fill=(255, 255, 255), width=1)
        d.line([(cx-12, top+12), (cx-8, top+12)], fill=(255, 255, 255), width=1)
        d.ellipse([cx-4, top, cx+4, top+8], fill=(232, 196, 150))
        d.rectangle([cx-3, top+8, cx+3, top+18], fill=(20, 20, 20))
        d.line([(cx-3, top+11), (cx+3, top+11)], fill=(198, 34, 34), width=1)
        d.line([(cx, top+10), (cx-8, top+15)], fill=(232, 196, 150), width=2)
        d.line([(cx, top+10), (cx+6, top+12)], fill=(232, 196, 150), width=2)
        d.line([(cx, top+18), (cx-8, y1-5)], fill=(40, 40, 40), width=3)
        d.line([(cx, top+18), (cx+9, y1-6)], fill=(40, 40, 40), width=3)
        d.polygon([(x1-24, y0+15), (x1-4, y0+17), (x1-4, y0+25), (x1-24, y0+23)],
                  outline=(198, 40, 30), width=2)
        d.text((x1-14, y0+20), "BAN", font=font(F_SANS_B, 7), fill=(198, 40, 30), anchor="mm")
    elif n == 12:  # CLAIM tankers — tanker + second hull + mine + warning
        sky(d, box, (150, 120, 60), (220, 180, 100))
        d.rectangle([x0, y1-14, x1, y1], fill=(90, 130, 150))
        for wx in (x0+4, x0+24, x0+42):
            d.arc([wx, y1-10, wx+12, y1-5], 180, 360, fill=(200, 225, 240), width=1)
        # distant second tanker silhouette
        d.rectangle([x0+30, y1-24, x1-4, y1-16], fill=(90, 80, 70))
        d.rectangle([x0+36, y1-29, x0+42, y1-24], fill=(90, 80, 70))
        # main tanker: hull, containers, bridge tower
        d.rectangle([x0+6, y1-26, x1-10, y1-14], fill=(60, 50, 40))
        d.rectangle([x0+8, y1-32, x0+22, y1-26], fill=(178, 34, 34))
        d.rectangle([x0+24, y1-32, x0+38, y1-26], fill=(46, 111, 183))
        d.rectangle([x1-16, y1-36, x1-10, y1-26], fill=(200, 200, 200))
        d.rectangle([x1-16, y1-34, x1-10, y1-32], fill=(60, 60, 60))
        # spiked mine + amber warning triangle + ?
        d.ellipse([cx-7, y0+6, cx+7, y0+20], fill=(60, 60, 60))
        for ang in range(0, 360, 45):
            ex = cx + 10*math.cos(math.radians(ang)); ey = y0+13 + 10*math.sin(math.radians(ang))
            d.line([(cx, y0+13), (ex, ey)], fill=(60, 60, 60), width=1)
        d.polygon([(x1-14, y0+4), (x1-4, y0+4), (x1-9, y0+14)], fill=(146, 90, 8))
        d.text((x1-9, y0+9), "!", font=font(F_SANS_B, 7), fill=(255, 255, 255), anchor="mm")
    elif n == 13:  # Riyadh PIF Tower — skyline + tall tower + strike flash
        sky(d, box, (90, 60, 80), (160, 110, 130))
        for bx, bh in [(x0+4, 16), (x0+16, 22), (x1-26, 18), (x1-14, 12)]:
            d.rectangle([bx, y1-4-bh, bx+10, y1-4], fill=(120, 90, 100))
        # main tower: tall glass shaft, stepped crown, window bands
        d.rectangle([cx-9, y0+12, cx+9, y1-4], fill=(220, 220, 230))
        d.rectangle([cx-12, y0+8, cx+12, y0+13], fill=(220, 220, 230))
        d.polygon([(cx-9, y0+8), (cx, y0+2), (cx+9, y0+8)], fill=(255, 180, 60))
        for wy in range(y0+16, y1-8, 7):
            d.rectangle([cx-5, wy, cx+5, wy+3], fill=(120, 140, 170))
        # strike flash + smoke plume at the crown
        d.polygon([(cx+12, y0+2), (cx+20, y0+10), (cx+14, y0+10), (cx+20, y0+18),
                   (cx+10, y0+10), (cx+16, y0+10)], fill=(255, 220, 120))
        d.ellipse([cx-14, y0+2, cx-6, y0+10], fill=(200, 200, 200))
        d.ellipse([cx-11, y0-1, cx-4, y0+6], fill=(220, 220, 220))
    elif n == 14:  # Jakarta — parliament dome + columns + scales + gavel/doc
        sky(d, box, (100, 90, 70), (170, 150, 110))
        # parliament building: dome + colonnade behind the scales
        d.ellipse([cx-14, y1-38, cx+14, y1-24], fill=(200, 190, 170))
        d.rectangle([cx-2, y1-42, cx+2, y1-38], fill=(200, 190, 170))
        d.rectangle([x0+6, y1-26, x1-6, y1-16], fill=(160, 140, 110))
        for i in range(5):
            bx = x0+9+i*9
            d.rectangle([bx, y1-26, bx+4, y1-16], fill=(220, 205, 175))
        d.rectangle([x0+6, y1-16, x1-6, y1-12], fill=(140, 120, 92))
        # scales of justice, foreground centre
        d.line([(cx, y1-24), (cx, y1-6)], fill=(60, 50, 30), width=2)
        d.line([(cx-11, y1-21), (cx+11, y1-21)], fill=(60, 50, 30), width=2)
        d.polygon([(cx-15, y1-8), (cx-7, y1-8), (cx-11, y1-14)], fill=(176, 141, 44))
        d.polygon([(cx+7, y1-8), (cx+15, y1-8), (cx+11, y1-14)], fill=(176, 141, 44))
        # seizure document, bottom-left, with verified Rp1bn+ figure
        d.rectangle([x0+3, y1-11, x0+21, y1-2], fill=(255, 255, 255), outline=(120, 110, 90))
        d.text((x0+12, y1-7), "Rp1bn+", font=font(F_SANS_B, 6), fill=(150, 40, 30), anchor="mm")
        # gavel, bottom-right
        d.line([(x1-16, y1-12), (x1-6, y1-4)], fill=(96, 66, 40), width=2)
        d.rectangle([x1-18, y1-14, x1-10, y1-10], fill=(96, 66, 40))
    else:  # 15 Hegseth LatAm — Andes + plane + contrail + two flags
        sky(d, box, (60, 100, 70), (120, 160, 120))
        d.polygon([(x0, y1-4), (x0+18, y1-22), (x0+36, y1-4)], fill=(110, 130, 110))
        d.polygon([(x0+22, y1-4), (x0+42, y1-30), (x1-4, y1-4)], fill=(140, 160, 140))
        d.polygon([(x0+30, y1-22), (x0+42, y1-30), (x0+52, y1-22)], fill=(255, 255, 255))
        # runway strip
        d.rectangle([x0, y1-6, x1, y1-4], fill=(90, 90, 90))
        # plane with contrail
        d.line([(x0+4, y0+12), (cx-12, y0+10)], fill=(255, 255, 255), width=1)
        d.polygon([(cx-16, y0+10), (cx+14, y0+14), (cx-16, y0+18)], fill=(230, 230, 230))
        d.rectangle([cx+12, y0+12, cx+20, y0+16], fill=(230, 230, 230))
        d.polygon([(cx-2, y0+8), (cx+2, y0+8), (cx+4, y0+14)], fill=(200, 200, 200))
        for fx, fc in [(x0+6, (214, 110, 34)), (x1-26, (46, 111, 183))]:
            d.line([(fx, y0+22), (fx, y1-12)], fill=(255, 255, 255), width=2)
            d.polygon([(fx, y0+22), (fx+16, y0+27), (fx, y0+32)], fill=fc)

CW, CH, CG = 246, 60, 8
for i, s in enumerate(secondary):
    r, c = divmod(i, 4)
    x = 8 + c * (CW + CG)
    y = SY0 + 22 + r * (CH + 5)
    rc = REGION[s["region"]]
    claim = s["confidence"] == "claim"
    fill = CLAIM_BG if claim else CARD
    d.rectangle([x, y, x+CW, y+CH], fill=fill, outline=(CLAIM_TX if claim else RULE), width=1)
    d.rectangle([x, y, x+3, y+CH], fill=rc)
    tx0, ty0, tx1, ty1 = x+8, y+4, x+66, y+CH-4
    mini(s["n"], (tx0, ty0, tx1, ty1-11))
    # location strip at the foot of the thumb (geographic tie-in)
    # short place names: the full place name would overflow the 58 px thumb
    # ("STRAIT OF HORMUZ" rendered as "TRAIT OF HORM" in the first render)
    PLACE_SHORT = {4: "NEW YORK", 5: "WORLDWIDE", 6: "KERCH", 7: "COPENHAGEN",
                   8: "ODISHA", 9: "SEOUL", 10: "SYDNEY", 11: "NAIROBI",
                   12: "HORMUZ", 13: "RIYADH", 14: "JAKARTA", 15: "QUITO"}
    d.rectangle([tx0, ty1-11, tx1, ty1], fill=rc)
    place = PLACE_SHORT[s["n"]]
    d.text(((tx0+tx1)//2, ty1-6), place, font=font(F_SANS_B, 7), fill=(255,255,255), anchor="mm")
    tx = x + 74
    hl = wrap(s["headline"], font(F_SANS_B, 10), CW-82)
    draw_lines(d, tx, y+4, hl[:2], font(F_SANS_B, 10), INK, leading=12)
    tag = ("CLAIM · " if claim else "") + s["source"]
    d.text((tx, y+CH-12), tag, font=font(F_SANS_B, 7), fill=(CLAIM_TX if claim else MUTED))

# ================= REGIONAL PANELS y 796..988 (h 192) — rebalanced: 4 panels =================
# B's problem: Europe 7 vs Africa 1. B2: Europe split into 2 sub-columns (4+3),
# Africa merged with Middle East (contiguous geography), N. America gets a
# verified S&P callout so its 3 items do not leave a hole. REFINED: the two
# Europe sub-columns are UNLABELLED (B2's "WESTERN EUROPE" / "NORTH & EAST"
# labels misplaced Brussels); the split itself is unchanged.
PY0, PY1 = 796, 988
d.text((8, PY0-18), "THE WIRES BY REGION — 20 MORE STORIES", font=font(F_SERIF_B, 13), fill=INK)
d.text((W-8, PY0-16), "numbered 16–35 · place + source for every item",
       font=font(F_SANS, 9), fill=MUTED, anchor="ra")
by_region = {}
for s in also:
    by_region.setdefault(s["region"], []).append(s)

def wire_item(d, x, y, w, s):
    claim = s["confidence"] == "claim"
    rc = REGION[s["region"]]
    d.ellipse([x, y+1, x+11, y+12], fill=(CLAIM_TX if claim else rc))
    d.text((x+5, y+6), str(s["n"]), font=font(F_SANS_B, 7), fill=(255,255,255), anchor="mm")
    hl = wrap(s["headline"], font(F_SANS, 9), w-16)
    y = draw_lines(d, x+16, y, hl[:2], font(F_SANS, 9), INK, leading=10)
    tag = ("CLAIM · " if claim else "") + s["place"] + " · " + s["source"]
    tf = font(F_SANS, 7)
    while tf.getlength(tag) > w-16 and len(tag) > 10:
        tag = tag[:-1]
    d.text((x+16, y), tag, font=tf, fill=(CLAIM_TX if claim else MUTED))
    return y + 10

def panel_frame(x, w, title, rc):
    d.rectangle([x, PY0, x+w, PY1], fill=CARD, outline=RULE, width=1)
    d.rectangle([x, PY0, x+w, PY0+20], fill=rc)
    d.text((x+8, PY0+4), title, font=font(F_SANS_B, 10), fill=(255,255,255))
    return PY0 + 26

# --- Europe 296 wide, two UNLABELLED sub-columns (REFINED fix 4).
# B2's labels ("WESTERN EUROPE" / "NORTH & EAST") misplaced Brussels (western)
# in "North & East". The labels are removed entirely rather than regrouped:
# any thematic regrouping would still force an editorial judgement on
# borderline stories, while the two columns are just a space split of one
# region. The column split itself is unchanged (20, 21, 25, 26 | 23, 32, 35);
# the thin divider stays as a neutral column separator.
px = 8; w = 296
y = panel_frame(px, w, "EUROPE  ·  7", REGION["Europe"])
yy1 = y; yy2 = y
for s in [by_region["Europe"][i] for i in (0, 1, 3, 4)]:   # 20,21,25,26
    yy1 = wire_item(d, px+8, yy1, 136, s) + 4
for s in [by_region["Europe"][i] for i in (2, 5, 6)]:      # 23,32,35
    yy2 = wire_item(d, px+152, yy2, 136, s) + 4
d.line([(px+144, y), (px+144, PY1-8)], fill=(225,218,205), width=1)
px += w + 8
# --- Asia 264 wide, 6 items
w = 264
y = panel_frame(px, w, "ASIA  ·  6", REGION["Asia"])
yy = y
for s in by_region["Asia"]:
    yy = wire_item(d, px+8, yy, w-16, s) + 4
px += w + 8
# --- Middle East + Africa 232 wide, 4 items + Africa inset
w = 232
y = panel_frame(px, w, "MIDDLE EAST + AFRICA  ·  4", REGION["Middle East"])
yy = y
for s in by_region["Middle East"] + by_region["Africa"]:
    yy = wire_item(d, px+8, yy, w-16, s) + 3
inset = (px+8, yy+2, px+w-8, PY1-6)
d.rectangle(inset, fill=OCEAN, outline=RULE, width=1)
d.text((inset[0]+5, inset[1]+3), "AFRICA — MOGADISHU (#22)", font=font(F_SANS_B, 7), fill=(60,90,110))
for feat in land["features"]:
    geom = feat["geometry"]
    polys = geom["coordinates"] if geom["type"] == "Polygon" else \
            [p for mp in geom["coordinates"] for p in mp]
    for poly in polys:
        pts = []
        for lon, lat in poly:
            if -20 < lon < 55 and -38 < lat < 38:
                pts.append((inset[0] + (lon + 20) / 75 * (inset[2]-inset[0]),
                            inset[1]+14 + (38 - lat) / 76 * (inset[3]-inset[1]-14)))
        if len(pts) > 2:
            d.polygon(pts, fill=LANDC, outline=LANDOUT)
mx = inset[0] + (45.3 + 20) / 75 * (inset[2]-inset[0])
my = inset[1]+14 + (38 - 2.0) / 76 * (inset[3]-inset[1]-14)
d.ellipse([mx-4, my-4, mx+4, my+4], fill=REGION["Africa"], outline=(255,255,255), width=1)
d.text((mx, my-8), "22", font=font(F_SANS_B, 7), fill=INK, anchor="mb")
px += w + 8
# --- North America 192 wide, 3 items + verified S&P callout
w = 192
y = panel_frame(px, w, "NORTH AMERICA  ·  3", REGION["North America"])
yy = y
for s in by_region["North America"]:
    yy = wire_item(d, px+8, yy, w-16, s) + 4
d.rectangle([px+8, yy+4, px+w-8, PY1-6], fill=(238,232,219), outline=RULE, width=1)
d.text((px+16, yy+10), "S&P 500  −2.02%", font=font(F_SERIF_B, 13), fill=INK)
d.text((px+16, yy+28), "6th straight fall — #24", font=font(F_SANS, 8), fill=MUTED)
d.text((px+16, yy+40), "New York · Morningstar", font=font(F_SANS, 7), fill=MUTED)

# ================= FOOTER (light — B fix: navy footer was heavy) y 994..1024 =================
d.rectangle([0, 992, W, 994], fill=GOLD)
d.text((8, 998), "Sources: Reuters, AP, White House, ICJ, WSJ, CNN, GOV.UK and national wires.  "
                 "CLAIM = unverified claim as reported, never a fact.",
       font=font(F_SANS, 8), fill=INK)
d.text((8, 1010), "All 35 stories happened or were first reported on Thursday 19 November 2026.  "
                  "Seven Wed 18 Nov stories removed in a date check.",
       font=font(F_SANS, 8), fill=MUTED)
d.text((W-8, 1004), "35 / 35", font=font(F_SANS_B, 10), fill=GOLD, anchor="ra")

img.save(OUT)
print("saved", OUT, img.size)
