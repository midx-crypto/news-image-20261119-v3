#!/usr/bin/env python3
"""Render 'The World in One Day' - Thu 19 Nov 2026 - as a 1024x1024 PNG.

Deterministic: fixed seed, no network, no timestamps, no random text.
Reads news.json beside this file, writes entry.png beside this file.
Pillow only (render-time dependency); the shipped main.py is stdlib-only.
"""
import json
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

# Palette: newsprint.
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


# ---------------------------------------------------------------- heroes
# Each draws a real scene into a (w x 58) band at (x, y).

def hero_summit(d, x, y, w):
    """Shenzhen summit: three flags over a round table, peace banner."""
    d.rectangle([x, y, x + w, y + 58], fill=(223, 232, 238))
    # hills + lake
    d.polygon([(x, y + 58), (x + 120, y + 30), (x + 240, y + 58)], fill=(120, 150, 110))
    d.polygon([(x + 260, y + 58), (x + 380, y + 26), (x + w, y + 58)], fill=(104, 138, 98))
    d.rectangle([x, y + 46, x + w, y + 58], fill=(140, 175, 200))
    # round table
    d.ellipse([x + w // 2 - 95, y + 34, x + w // 2 + 95, y + 52], fill=(122, 74, 44))
    d.ellipse([x + w // 2 - 95, y + 30, x + w // 2 + 95, y + 44], fill=(150, 96, 58))
    # three flags on poles
    poles = [x + 52, x + w // 2 - 22, x + w - 150]
    flags = ["US", "CN", "RU"]
    cols = [((178, 34, 52), (255, 255, 255)), ((222, 41, 16), (255, 215, 0)),
            ((255, 255, 255), (0, 57, 166))]
    for px, code, (c1, c2) in zip(poles, flags, cols):
        d.line([px, y + 2, px, y + 34], fill=DARK, width=2)
        if code == "US":
            d.rectangle([px, y + 2, px + 44, y + 16], fill=(255, 255, 255))
            for i in range(4):
                d.rectangle([px, y + 2 + i * 4, px + 44, y + 4 + i * 4], fill=(178, 34, 52))
            d.rectangle([px, y + 2, px + 18, y + 9], fill=(60, 59, 110))
        elif code == "CN":
            d.rectangle([px, y + 2, px + 44, y + 16], fill=(222, 41, 16))
            d.text((px + 5, y + 3), "\u2605", font=font(SANS_B, 11), fill=(255, 215, 0))
        else:
            d.rectangle([px, y + 2, px + 44, y + 7], fill=(255, 255, 255))
            d.rectangle([px, y + 7, px + 44, y + 11], fill=(0, 57, 166))
            d.rectangle([px, y + 11, px + 44, y + 16], fill=(213, 0, 0))
    # banner ribbon
    d.rectangle([x + w // 2 - 118, y + 20, x + w // 2 + 118, y + 32], fill=(255, 255, 255))
    d.rectangle([x + w // 2 - 118, y + 20, x + w // 2 + 118, y + 32], outline=RED, width=1)
    bf = font(SANS_B, 8)
    t = "DECLARATION TOWARD PEACE"
    d.text((x + w // 2 - bf.getlength(t) / 2, y + 22), t, font=bf, fill=RED)


def hero_icj(d, x, y, w):
    """ICJ: courthouse columns, scales of justice, 9-6 verdict."""
    d.rectangle([x, y, x + w, y + 58], fill=(232, 226, 210))
    # pediment
    d.polygon([(x + 30, y + 16), (x + w // 2, y + 2), (x + w - 30, y + 16)],
              fill=(200, 188, 158))
    # columns
    for cx in range(x + 52, x + w - 40, 62):
        d.rectangle([cx, y + 16, cx + 14, y + 52], fill=(245, 240, 224))
        d.rectangle([cx - 3, y + 14, cx + 17, y + 17], fill=(220, 210, 182))
        d.rectangle([cx - 3, y + 52, cx + 17, y + 55], fill=(220, 210, 182))
    # scales of justice, centre foreground
    cx = x + w // 2
    d.line([cx, y + 18, cx, y + 46], fill=GOLD, width=3)
    d.line([cx - 26, y + 22, cx + 26, y + 22], fill=GOLD, width=3)
    d.polygon([(cx - 26, y + 22), (cx - 38, y + 36), (cx - 14, y + 36)], fill=GOLD)
    d.polygon([(cx + 26, y + 22), (cx + 38, y + 36), (cx + 14, y + 36)], fill=GOLD)
    d.ellipse([cx - 3, y + 14, cx + 3, y + 20], fill=GOLD)
    d.rectangle([cx - 14, y + 46, cx + 14, y + 50], fill=GOLD)
    # verdict numerals on the pediment
    vf = font(SERIF_B, 13)
    t = "9\u20136"
    d.text((x + w // 2 - vf.getlength(t) / 2, y + 3), t, font=vf, fill=RED)


def hero_cop31(d, x, y, w):
    """COP31: draft document with FOSSIL FUELS struck through, globe + leaf."""
    d.rectangle([x, y, x + w, y + 58], fill=(214, 232, 220))
    # draft document, left
    dx, dy = x + 14, y + 4
    d.rectangle([dx, dy, dx + 210, dy + 50], fill=(255, 255, 255), outline=(150, 150, 150))
    tf = font(SANS_B, 11)
    d.text((dx + 8, dy + 4), "COP31 DRAFT DEAL", font=tf, fill=INK)
    for i, ln in enumerate([120, 170]):
        d.rectangle([dx + 8, dy + 21 + i * 6, dx + 8 + ln, dy + 24 + i * 6], fill=(200, 200, 200))
    ff = font(SANS_B, 10)
    t = "FOSSIL FUELS"
    d.text((dx + 8, dy + 34), t, font=ff, fill=(120, 120, 120))
    d.line([dx + 6, dy + 39, dx + 10 + ff.getlength(t), dy + 39], fill=RED, width=3)
    # globe, right
    gx, gy, gr = x + w - 62, y + 29, 24
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=SEA)
    d.ellipse([gx - 12, gy - 18, gx + 2, gy - 2], fill=GREEN)
    d.ellipse([gx - 2, gy + 2, gx + 16, gy + 16], fill=GREEN)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(255, 255, 255), width=2)
    # leaf
    d.polygon([(gx - 46, gy + 18), (gx - 30, gy - 2), (gx - 16, gy + 16)], fill=TEAL)
    d.line([gx - 42, gy + 14, gx - 20, gy + 8], fill=(255, 255, 255), width=1)


def hero_anthropic(d, x, y, w):
    """Anthropic IPO: soaring stock chart, $81.3bn, ANT ticker."""
    d.rectangle([x, y, x + w, y + 58], fill=(226, 236, 226))
    # bars
    bars = [8, 12, 10, 16, 14, 22, 30, 44]
    bw = 26
    bx = x + 16
    for i, bh in enumerate(bars):
        d.rectangle([bx + i * (bw + 6), y + 54 - bh, bx + i * (bw + 6) + bw, y + 54],
                    fill=(120, 170, 130) if i < 6 else TEAL)
    # soaring line + arrow
    pts = [(x + 20, y + 44), (x + 90, y + 38), (x + 160, y + 40), (x + 230, y + 26),
           (x + 300, y + 28), (x + 350, y + 12)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + 350, y + 12), (x + 336, y + 10), (x + 344, y + 22)], fill=RED)
    # price tag
    pf = font(SANS_B, 15)
    d.text((x + w - 128, y + 4), "$81.3bn", font=pf, fill=INK)
    tf = font(SANS_B, 10)
    tag = "ANT  $97.17  +17%"
    d.rounded_rectangle([x + w - 132, y + 26, x + w - 132 + tf.getlength(tag) + 12, y + 42],
                        radius=4, fill=INK)
    d.text((x + w - 126, y + 29), tag, font=tf, fill=(255, 255, 255))


# ------------------------------------------------------- small miniatures
# Each draws a distinct miniature scene into a 56x56 box at (x, y).

def mini_gta(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(38, 44, 66))
    d.rectangle([x, y + 34, x + 56, y + 56], fill=(24, 28, 44))
    for bx, bh in [(4, 18), (14, 26), (26, 14), (38, 30)]:
        d.rectangle([x + bx, y + 34 - bh, x + bx + 8, y + 34], fill=(70, 80, 110))
    # controller
    d.rounded_rectangle([x + 10, y + 36, x + 46, y + 50], radius=6, fill=(220, 220, 220))
    d.ellipse([x + 15, y + 40, x + 19, y + 44], fill=RED)
    d.ellipse([x + 37, y + 40, x + 41, y + 44], fill=BLUE)
    # 99 badge
    d.ellipse([x + 34, y + 2, x + 54, y + 22], fill=GOLD)
    bf = font(SANS_B, 11)
    d.text((x + 37, y + 6), "99", font=bf, fill=(255, 255, 255))


def mini_bridge(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(178, 205, 224))
    d.rectangle([x, y + 38, x + 56, y + 56], fill=(46, 111, 148))
    d.arc([x + 2, y + 8, x + 54, y + 52], start=180, end=360, fill=(90, 90, 90), width=4)
    d.line([x + 2, y + 30, x + 54, y + 30], fill=(90, 90, 90), width=3)
    for px in (12, 28, 44):
        d.line([x + px, y + 18, x + px, y + 30], fill=(90, 90, 90), width=2)
    # flame
    d.polygon([(x + 24, y + 4), (x + 30, y + 14), (x + 34, y + 8), (x + 38, y + 18),
               (x + 30, y + 24), (x + 22, y + 18)], fill=ORANGE)
    d.ellipse([x + 26, y + 14, x + 34, y + 22], fill=(255, 200, 0))


def mini_greenland(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(200, 222, 235))
    # Greenland-ish landmass
    d.polygon([(x + 8, y + 10), (x + 26, y + 4), (x + 44, y + 10), (x + 48, y + 26),
               (x + 36, y + 40), (x + 18, y + 38), (x + 8, y + 26)], fill=(240, 244, 240),
              outline=TEAL)
    d.ellipse([x + 18, y + 14, x + 26, y + 22], fill=TEAL)
    # ballot slip 109-0
    d.rectangle([x + 6, y + 38, x + 50, y + 53], fill=(255, 255, 255), outline=INK)
    bf = font(SANS_B, 10)
    d.text((x + 10, y + 41), "109\u20130", font=bf, fill=RED)
    d.text((x + 40, y + 42), "\u2713", font=font(SANS_B, 10), fill=GREEN)


def mini_cyclone(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(52, 68, 92))
    cx, cy = x + 28, y + 26
    for r in (20, 15, 10, 5):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=200 + 260, fill=(255, 255, 255), width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 200, 0))
    for rx in (8, 20, 32, 44):
        d.line([x + rx, y + 46, x + rx - 3, y + 52], fill=(140, 180, 220), width=2)


def mini_exam(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(232, 226, 210))
    d.rectangle([x + 10, y + 6, x + 38, y + 48], fill=(255, 255, 255), outline=INK)
    for i in range(5):
        d.line([x + 15, y + 14 + i * 6, x + 33, y + 14 + i * 6], fill=(150, 150, 150), width=1)
    d.text((x + 15, y + 8), "A", font=font(SANS_B, 8), fill=INK)
    # pencil, diagonal
    d.polygon([(x + 34, y + 40), (x + 52, y + 22), (x + 48, y + 18), (x + 30, y + 36)],
              fill=(255, 200, 0))
    d.polygon([(x + 52, y + 22), (x + 56, y + 26), (x + 52, y + 28)], fill=(220, 180, 140))
    d.polygon([(x + 30, y + 36), (x + 34, y + 40), (x + 32, y + 44)], fill=(220, 180, 140))


def mini_jobs(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(240, 234, 222))
    pts = [(x + 6, y + 12), (x + 18, y + 18), (x + 30, y + 16), (x + 42, y + 30), (x + 50, y + 40)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + 50, y + 40), (x + 42, y + 38), (x + 48, y + 46)], fill=RED)
    # briefcase
    d.rectangle([x + 10, y + 34, x + 34, y + 50], fill=(122, 74, 44))
    d.rectangle([x + 18, y + 30, x + 26, y + 34], fill=(122, 74, 44))
    d.line([x + 10, y + 42, x + 34, y + 42], fill=(200, 160, 110), width=1)
    bf = font(SANS_B, 10)
    d.text((x + 40, y + 8), "4.9%", font=bf, fill=RED)


def mini_house(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(40, 32, 28))
    d.polygon([(x + 8, y + 30), (x + 28, y + 14), (x + 48, y + 30)], fill=(122, 40, 40))
    d.rectangle([x + 12, y + 30, x + 44, y + 50], fill=(200, 170, 120))
    d.rectangle([x + 24, y + 38, x + 32, y + 50], fill=(60, 40, 20))
    # flame on roof
    d.polygon([(x + 22, y + 2), (x + 28, y + 12), (x + 33, y + 5), (x + 37, y + 15),
               (x + 29, y + 20), (x + 21, y + 14)], fill=ORANGE)
    d.ellipse([x + 25, y + 11, x + 32, y + 18], fill=(255, 200, 0))


def mini_tanker(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(178, 205, 224))
    for wy in (40, 46, 52):
        d.line([x, y + wy, x + 56, y + wy], fill=(255, 255, 255), width=2)
    # ship
    d.polygon([(x + 6, y + 30), (x + 48, y + 30), (x + 42, y + 40), (x + 12, y + 40)], fill=(60, 60, 60))
    d.rectangle([x + 16, y + 20, x + 30, y + 30], fill=(178, 34, 52))
    d.rectangle([x + 34, y + 24, x + 40, y + 30], fill=(255, 255, 255))
    # mine + fire
    d.ellipse([x + 42, y + 12, x + 52, y + 22], fill=DARK)
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        d.line([x + 47 + 5 * math.cos(a), y + 17 + 5 * math.sin(a),
                x + 47 + 8 * math.cos(a), y + 17 + 8 * math.sin(a)], fill=DARK, width=1)
    d.polygon([(x + 18, y + 8), (x + 22, y + 15), (x + 26, y + 9), (x + 28, y + 16),
               (x + 21, y + 19), (x + 16, y + 15)], fill=ORANGE)


def mini_tank(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(222, 214, 190))
    d.line([x, y + 44, x + 56, y + 44], fill=(120, 110, 90), width=3)
    for dx in range(0, 56, 10):
        d.line([x + dx, y + 44, x + dx + 5, y + 44], fill=(255, 255, 255), width=1)
    # tank body + turret + barrel
    d.rectangle([x + 10, y + 30, x + 40, y + 40], fill=(90, 100, 60))
    d.rectangle([x + 18, y + 22, x + 32, y + 30], fill=(70, 80, 48))
    d.line([x + 32, y + 25, x + 50, y + 20], fill=(70, 80, 48), width=4)
    for tx in (14, 22, 30, 36):
        d.ellipse([x + tx, y + 40, x + tx + 5, y + 45], fill=DARK)


def mini_tower(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(30, 34, 48))
    # PIF tower, tapered
    d.polygon([(x + 20, y + 52), (x + 22, y + 6), (x + 34, y + 6), (x + 36, y + 52)],
              fill=(140, 160, 190))
    for wy in range(12, 50, 6):
        d.line([x + 22, y + wy, x + 34, y + wy], fill=(220, 230, 240), width=1)
    # impact burst
    cx, cy = x + 44, y + 16
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        d.line([cx, cy, cx + 9 * math.cos(a), cy + 9 * math.sin(a)], fill=(255, 200, 0), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=ORANGE)


def mini_gavel(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(232, 226, 210))
    # document
    d.rectangle([x + 8, y + 22, x + 34, y + 50], fill=(255, 255, 255), outline=INK)
    for i in range(4):
        d.line([x + 12, y + 28 + i * 5, x + 30, y + 28 + i * 5], fill=(150, 150, 150), width=1)
    d.ellipse([x + 26, y + 40, x + 32, y + 46], fill=RED)
    # gavel, diagonal
    d.line([x + 30, y + 10, x + 50, y + 30], fill=(122, 74, 44), width=3)
    d.rectangle([x + 34, y + 6, x + 46, y + 16], fill=(150, 96, 58))
    d.rectangle([x + 40, y + 30, x + 50, y + 34], fill=(150, 96, 58))


def mini_strike(d, x, y):
    d.rectangle([x, y, x + 56, y + 56], fill=(240, 232, 210))
    # crowd
    for cx, cy, c in [(10, 44, BLUE), (20, 40, RED), (30, 44, TEAL), (40, 40, GOLD),
                      (48, 44, (120, 60, 140))]:
        d.ellipse([x + cx - 4, y + cy - 4, x + cx + 4, y + cy + 4], fill=c)
        d.rectangle([x + cx - 5, y + cy + 4, x + cx + 5, y + 52], fill=c)
    # megaphone
    d.polygon([(x + 12, y + 14), (x + 34, y + 8), (x + 34, y + 28), (x + 12, y + 22)], fill=RED)
    d.rectangle([x + 6, y + 14, x + 12, y + 22], fill=DARK)
    d.line([x + 34, y + 8, x + 34, y + 28], fill=(255, 255, 255), width=2)


MINIS = {5: mini_gta, 6: mini_bridge, 7: mini_greenland, 8: mini_cyclone,
         9: mini_exam, 10: mini_jobs, 11: mini_house, 12: mini_tanker,
         13: mini_tank, 14: mini_tower, 15: mini_gavel, 16: mini_strike}
HEROES = {1: hero_summit, 2: hero_icj, 3: hero_cop31, 4: hero_anthropic}


# ---------------------------------------------------------------- layout

def main():
    data = json.loads((HERE / "news.json").read_text())
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Section A: masthead
    title_f = font(SERIF_B, 42)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - title_f.getlength(t)) / 2, 22), t, font=title_f, fill=INK)
    d.line([MARGIN, 72, W - MARGIN, 72], fill=INK, width=2)
    date_f = font(SANS_B, 15)
    t2 = "THURSDAY 19 NOVEMBER 2026  \u00b7  50 STORIES  \u00b7  7 REGIONS  \u00b7  CLAIMS LABELLED"
    d.text(((W - date_f.getlength(t2)) / 2, 78), t2, font=date_f, fill=RED)
    # stat strip
    stats = data["stats"]
    gap = 8
    sw = (CW - gap * (len(stats) - 1)) // len(stats)
    sy, sh = 100, 30
    for i, s in enumerate(stats):
        sx = MARGIN + i * (sw + gap)
        d.rectangle([sx, sy, sx + sw, sy + sh], fill=CARD, outline=RULE)
        vf = font(SANS_B, 15)
        lf = font(SANS, 9)
        d.text((sx + 7, sy + 2), s["value"], font=vf, fill=INK)
        lab = trim_one(s["label"], lf, sw - 14)
        d.text((sx + 7, sy + 18), lab, font=lf, fill=MUTED)

    # ---- Section B: heroes, 2x2
    heroes = data["featured"][:4]
    hw, hh, hgap = 484, 146, 8
    hy0 = 138
    hf = font(SERIF_B, 15)
    sf = font(SANS, 11)
    mf = font(SANS, 10)
    for i, s in enumerate(heroes):
        hx = MARGIN + (i % 2) * (hw + hgap)
        hy = hy0 + (i // 2) * (hh + hgap)
        d.rectangle([hx, hy, hx + hw, hy + hh], fill=CARD, outline=RULE)
        HEROES[s["n"]](d, hx + 1, hy + 1, hw - 2)
        num_badge(d, hx + 7, hy + 7, s["n"])
        if s["confidence"] == "claim":
            chip(d, hx + hw - 62, hy + 7, "CLAIM", font(SANS_B, 9), (255, 255, 255), RED)
        else:
            chip(d, hx + hw - 82, hy + 7, "VERIFIED", font(SANS_B, 9), (255, 255, 255), TEAL)
        ty = hy + 64
        for ln in fit_lines(s["headline"], hf, hw - 16, 2):
            d.text((hx + 8, ty), ln, font=hf, fill=INK)
            ty += 18
        for ln in fit_lines(s["summary"], sf, hw - 16, 2):
            d.text((hx + 8, ty), ln, font=sf, fill=(60, 60, 60))
            ty += 14
        d.text((hx + 8, hy + hh - 15),
               f"{s['place']}  \u2014  {s['source']}", font=mf, fill=MUTED)

    # ---- Section C: 12 cards, 4x3
    cards = data["featured"][4:16]
    cw_, ch, cgap = 238, 88, 8
    cy0 = 446
    chf = font(SANS_B, 12)
    cmf = font(SANS, 9)
    for i, s in enumerate(cards):
        cx = MARGIN + (i % 4) * (cw_ + cgap)
        cy = cy0 + (i // 4) * (ch + cgap)
        d.rectangle([cx, cy, cx + cw_, cy + ch], fill=CARD, outline=RULE)
        MINIS[s["n"]](d, cx + 7, cy + 16)
        num_badge(d, cx + 3, cy + 12, s["n"])
        tx = cx + 71
        ty = cy + 8
        lines = fit_lines(s["headline"], chf, cw_ - 78, 3)
        for li, ln in enumerate(lines):
            if li == 0 and s["confidence"] == "claim" and ln.startswith("CLAIM:"):
                d.text((tx, ty), "CLAIM:", font=chf, fill=RED)
                rest = ln[len("CLAIM:"):]
                d.text((tx + chf.getlength("CLAIM:"), ty), rest, font=chf, fill=INK)
            else:
                d.text((tx, ty), ln, font=chf, fill=INK)
            ty += 14
        d.text((tx, cy + ch - 16), trim_one(s["place"], cmf, cw_ - 78), font=cmf, fill=MUTED)
        d.text((tx, cy + ch - 26), trim_one(s["source"], cmf, cw_ - 78),
               font=cmf, fill=MUTED)

    # ---- Section D: newswire 17-50, 4 cols x 9 rows
    ny0 = 740
    nf = font(SANS_B, 12)
    d.text((MARGIN, 726), "MORE FROM THE DAY", font=nf, fill=INK)
    d.line([MARGIN + 150, 732, W - MARGIN, 732], fill=RULE, width=1)
    rows = data["also"]
    nwf = font(SANS_B, 10)
    nwm = font(SANS, 9)
    colw = 238
    for i, s in enumerate(rows):
        col, row = i % 4, i // 4
        nx = MARGIN + col * (colw + 8)
        ny = ny0 + row * 25
        head = trim_one(f"{s['n']}. {s['headline']}", nwf, colw)
        d.text((nx, ny), head, font=nwf, fill=INK)
        meta = trim_one(f"{s['place']} \u2014 {s['source']}", nwm, colw)
        d.text((nx, ny + 13), meta, font=nwm, fill=MUTED)

    # ---- Section E: footer
    ff = font(SANS, 9)
    f1 = ("Sources: Reuters \u00b7 AP \u00b7 White House \u00b7 ICJ \u00b7 WSJ \u00b7 CNN \u00b7 GOV.UK \u00b7 national wires.  "
          "All 50 stories happened or were first reported Thu 19 Nov 2026.  CLAIM = unverified claim, never fact.")
    f2 = ("Date-checked: 7 Wed-dated stories removed \u2014 Van Gogh sale, IAEA Yongbyon, US-Venezuela pact, "
          "EU loan proposal, Taiz water crisis, US carrier departure, Kuwait/Bahrain drones.")
    d.line([MARGIN, 972, W - MARGIN, 972], fill=RULE, width=1)
    d.text((MARGIN, 976), trim_one(f1, ff, CW), font=ff, fill=MUTED)
    d.text((MARGIN, 988), trim_one(f2, ff, CW), font=ff, fill=MUTED)

    img.save(HERE / "entry.png", format="PNG", optimize=True)
    print(f"entry.png {img.size} saved")


if __name__ == "__main__":
    main()
