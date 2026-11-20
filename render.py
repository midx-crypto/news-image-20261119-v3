#!/usr/bin/env python3
"""Render entry.png for make.fun news-image-20261119 (fresh build, v3).

Reads news.json (dataset written in this session), draws a 1024x1024
premium-broadsheet image with PIL, deterministic: fixed seed, no network,
no timestamps. Run: python3 render.py -> writes entry.png beside this file.
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

random.seed(20261119)
HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
MARGIN = 24
CW = W - 2 * MARGIN  # 976

PAPER = (248, 244, 236)
INK = (25, 25, 25)
MUTED = (90, 86, 76)
RULE = (166, 30, 30)
NAVY = (30, 58, 95)
TEAL = (15, 107, 92)
OCHRE = (183, 121, 31)
GOLD = (201, 162, 39)
LIGHT = (255, 255, 255)
PANEL = (255, 255, 255)
MAP_BG = (220, 232, 238)
LAND = (200, 194, 180)
DOT = (166, 30, 30)

REGION_COLORS = {
    "Asia-Pacific": (15, 107, 92),
    "Europe": (30, 58, 95),
    "Middle East": (166, 30, 30),
    "North America": (183, 121, 31),
    "Latin America": (107, 79, 161),
    "Africa": (194, 87, 27),
    "Global": (85, 85, 85),
}

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(lines) * leading


def tag_chip(draw, x, y, label, fill):
    """Small confidence tag chip; returns width used."""
    f = font(SANS_B, 8)
    w = int(draw.textlength(label, font=f)) + 10
    draw.rounded_rectangle([x, y, x + w, y + 13], radius=3, fill=fill)
    draw.text((x + 5, y + 2), label, font=f, fill=LIGHT)
    return w


def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 34, 52))
    for i in range(1, 7, 2):
        d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7], fill=LIGHT)
    d.rectangle([x, y, x + w * 0.4, y + h * 4 // 7], fill=(30, 58, 95))
    for r in range(4):
        for c in range(5):
            d.ellipse([x + 4 + c * 8, y + 3 + r * 6, x + 8 + c * 8, y + 7 + r * 6], fill=LIGHT)


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    d.text((x + 6, y + 4), "*", font=font(SANS_B, 18), fill=(255, 222, 0))
    for sx, sy in [(28, 6), (34, 12), (34, 20), (28, 26)]:
        d.text((x + sx, y + sy), "*", font=font(SANS_B, 9), fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h // 3], fill=LIGHT)
    d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(213, 0, 0))


def hero_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    fw, fh = 62, 38
    flag_us(d, x + 22, y + 14, fw, fh)
    flag_cn(d, x + w // 2 - fw // 2, y + 6, fw, fh)
    flag_ru(d, x + w - 22 - fw, y + 14, fw, fh)
    d.ellipse([x + 20, y + 64, x + w - 20, y + 100], fill=(23, 44, 74))
    for cx in (x + 53, x + w // 2, x + w - 53):
        d.ellipse([cx - 10, y + 48, cx + 10, y + 68], fill=(201, 162, 39))
        d.ellipse([cx - 6, y + 52, cx + 6, y + 64], fill=(248, 244, 236))
    label = "KYLIN VILLA"
    lw = d.textlength(label, font=font(SANS_B, 11))
    d.text((x + w // 2 - lw / 2, y + 78), label, font=font(SANS_B, 11), fill=(255, 222, 0))


def hero_icj(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TEAL)
    cx, top = x + w // 2, y + 16
    d.rectangle([cx - 3, top, cx + 3, top + 52], fill=GOLD)
    d.rectangle([cx - 34, top + 52, cx + 34, top + 58], fill=GOLD)
    d.rectangle([cx - 46, top + 6, cx + 46, top + 12], fill=GOLD)
    for sgn in (-1, 1):
        px = cx + sgn * 42
        d.line([cx + sgn * 44, top + 9, px, top + 34], fill=GOLD, width=2)
        d.line([cx + sgn * 44, top + 9, px + sgn * 16, top + 34], fill=GOLD, width=2)
        d.pieslice([px - 17, top + 32, px + 17, top + 52], 0, 180, fill=GOLD)
    d.ellipse([cx - 46, y + h - 40, cx - 22, y + h - 16], fill=(255, 222, 0))
    d.text((cx - 40, y + h - 34), "9-6", font=font(SANS_B, 12), fill=INK)


def hero_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(122, 106, 44))
    d.ellipse([x + w - 66, y + 8, x + w - 18, y + 56], fill=(255, 196, 0))
    px, py, pw, ph = x + 24, y + 12, w - 110, 76
    d.rectangle([px, py, px + pw, py + ph], fill=LIGHT)
    d.rectangle([px, py, px + pw, py + 16], fill=(30, 58, 95))
    d.text((px + 8, py + 3), "DRAFT DEAL", font=font(SANS_B, 9), fill=LIGHT)
    for i in range(3):
        d.rectangle([px + 10, py + 24 + i * 9, px + pw - 10, py + 27 + i * 9], fill=(180, 180, 180))
    d.text((px + 10, py + 52), "FOSSIL FUELS", font=font(SANS_B, 11), fill=(166, 30, 30))
    d.line([px + 6, py + 56, px + 92, py + 66], fill=(166, 30, 30), width=3)
    d.line([px + 6, py + 66, px + 92, py + 56], fill=(166, 30, 30), width=3)


ICONS = {}


def icon_canvas(color):
    im = Image.new("RGB", (34, 34), color)
    return im, ImageDraw.Draw(im)


def icon_chart(color, down=False):
    im, d = icon_canvas(color)
    pts = [(6, 24), (13, 24), (13, 14), (20, 14), (20, 24), (27, 24), (27, 6), (30, 6)]
    vals = [24, 14, 18, 8] if not down else [8, 14, 18, 24]
    for i, v in enumerate(vals):
        d.rectangle([6 + i * 7, v, 11 + i * 7, 26], fill=LIGHT)
    return im


def icon_gamepad(color):
    im, d = icon_canvas(color)
    d.rounded_rectangle([4, 10, 30, 26], radius=6, fill=LIGHT)
    d.ellipse([9, 15, 13, 19], fill=color)
    d.ellipse([21, 15, 25, 19], fill=color)
    d.ellipse([15, 13, 19, 17], fill=color)
    return im


def icon_bridge(color):
    im, d = icon_canvas(color)
    d.arc([4, 8, 30, 34], 180, 360, fill=LIGHT, width=3)
    d.rectangle([4, 24, 30, 27], fill=LIGHT)
    d.rectangle([7, 18, 9, 24], fill=LIGHT)
    d.rectangle([24, 18, 26, 24], fill=LIGHT)
    return im


def icon_shield(color):
    im, d = icon_canvas(color)
    d.polygon([(17, 5), (28, 9), (28, 18), (17, 29), (6, 18), (6, 9)], fill=LIGHT)
    d.line([12, 17, 16, 21, 23, 12], fill=color, width=3)
    return im


def icon_cyclone(color):
    im, d = icon_canvas(color)
    for r, a0, a1 in [(12, 0, 300), (9, 40, 340), (6, 80, 380), (3, 120, 420)]:
        d.arc([17 - r, 17 - r, 17 + r, 17 + r], a0, a1, fill=LIGHT, width=2)
    return im


def icon_pencil(color):
    im, d = icon_canvas(color)
    d.polygon([(9, 24), (22, 11), (26, 15), (13, 28)], fill=LIGHT)
    d.polygon([(22, 11), (26, 15), (29, 12), (25, 8)], fill=(255, 196, 0))
    d.line([9, 24, 13, 28], fill=color, width=2)
    return im


def icon_flame(color):
    im, d = icon_canvas(color)
    d.polygon([(17, 5), (24, 14), (21, 18), (26, 24), (17, 29), (8, 24), (13, 18), (10, 14)],
              fill=(255, 196, 0))
    d.polygon([(17, 15), (21, 20), (17, 26), (13, 20)], fill=color)
    return im


def icon_ship(color):
    im, d = icon_canvas(color)
    d.rectangle([6, 8, 28, 20], fill=LIGHT)
    d.rectangle([9, 11, 13, 16], fill=color)
    d.rectangle([15, 11, 19, 16], fill=color)
    d.rectangle([21, 11, 25, 16], fill=color)
    d.polygon([(4, 20), (30, 20), (26, 27), (8, 27)], fill=(255, 196, 0))
    return im


def icon_tank(color):
    im, d = icon_canvas(color)
    d.rounded_rectangle([6, 18, 28, 26], radius=3, fill=LIGHT)
    d.rectangle([12, 12, 22, 18], fill=LIGHT)
    d.rectangle([22, 14, 30, 16], fill=LIGHT)
    for cx in (10, 17, 24):
        d.ellipse([cx - 2, 26, cx + 2, 30], fill=LIGHT)
    return im


def icon_tower(color):
    im, d = icon_canvas(color)
    d.polygon([(14, 4), (20, 4), (22, 28), (12, 28)], fill=LIGHT)
    for r in range(4):
        for c in range(2):
            d.rectangle([14 + c * 4, 8 + r * 5, 16 + c * 4, 10 + r * 5], fill=color)
    return im


def icon_gavel(color):
    im, d = icon_canvas(color)
    d.rectangle([8, 8, 20, 14], fill=LIGHT)
    d.rectangle([18, 13, 26, 27], fill=(255, 196, 0))
    d.rectangle([5, 26, 15, 29], fill=LIGHT)
    return im


ICON_BUILDERS = {
    4: icon_chart, 5: icon_gamepad, 6: icon_bridge, 7: icon_shield,
    8: icon_cyclone, 9: icon_pencil, 10: lambda c: icon_chart(c, down=True),
    11: icon_flame, 12: icon_ship, 13: icon_tank, 14: icon_tower, 15: icon_gavel,
}

CONTINENTS = {
    "na": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-75, 62),
           (-60, 55), (-55, 47), (-65, 45), (-75, 35), (-80, 25), (-90, 21), (-97, 16),
           (-105, 20), (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    "greenland": [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-20, 70), (-25, 76),
                  (-40, 80), (-55, 76), (-60, 70)],
    "sa": [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-50, -30),
           (-60, -38), (-70, -50), (-75, -40), (-75, -20), (-80, -5)],
    "africa": [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
               (40, 15), (48, 11), (51, 10), (40, 0), (35, -10), (30, -20), (20, -35),
               (15, -30), (12, -18), (8, 0), (-8, 5)],
    "eurasia": [(0, 36), (10, 44), (20, 40), (25, 36), (30, 36), (35, 36), (40, 38),
                (45, 40), (50, 45), (55, 50), (60, 55), (65, 68), (70, 72), (80, 73),
                (100, 77), (120, 73), (140, 72), (160, 70), (178, 66), (170, 60),
                (160, 55), (145, 45), (135, 40), (130, 35), (122, 30), (115, 22),
                (108, 12), (100, 8), (95, 15), (90, 22), (80, 15), (75, 8), (70, 20),
                (60, 25), (55, 27), (50, 29), (45, 30), (40, 32), (35, 36), (30, 36),
                (20, 38), (10, 37)],
    "australia": [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32), (140, -38),
                  (150, -37), (153, -27), (150, -22), (142, -11), (136, -12), (132, -11),
                  (126, -14), (122, -17), (114, -20)],
    "uk": [(-5, 50), (-2, 53), (0, 52), (-3, 58)],
    "japan": [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 42),
              (142, 44), (140, 40), (137, 36), (133, 34)],
}

DOT_OFFSETS = {2: (0, 0), 3: (-4, -4), 6: (6, 0), 7: (0, 0), 8: (-8, 8),
               11: (6, -6), 13: (10, 10), 14: (0, 0), 12: (0, 0)}


def render():
    data = json.loads((HERE / "news.json").read_text())
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- Masthead ----------
    y = 14
    d.text((MARGIN, y - 2), "THE WORLD", font=font(SERIF_B, 46), fill=INK)
    tw = d.textlength("THE WORLD", font=font(SERIF_B, 46))
    d.text((MARGIN + tw + 12, y + 6), "IN ONE DAY", font=font(SERIF_B, 20), fill=RULE)
    right = "THURSDAY 19 NOVEMBER 2026"
    rw = d.textlength(right, font=font(SANS_B, 19))
    d.text((W - MARGIN - rw, y + 2), right, font=font(SANS_B, 19), fill=INK)
    sub = str(data["stories_total"]) + " STORIES  ·  7 REGIONS  ·  EVERY CLAIM VERIFIED"
    sw = d.textlength(sub, font=font(SANS_B, 10))
    d.text((W - MARGIN - sw, y + 28), sub, font=font(SANS_B, 10), fill=MUTED)
    d.rectangle([MARGIN, 72, W - MARGIN, 76], fill=RULE)
    d.rectangle([MARGIN, 79, W - MARGIN, 80], fill=INK)

    # ---------- Stat strip ----------
    sy, sh = 88, 44
    stats = data["stats"]
    bw = CW // 5
    for i, s in enumerate(stats):
        x = MARGIN + i * bw
        if i:
            d.line([x - 4, sy + 4, x - 4, sy + sh - 4], fill=(210, 204, 190), width=1)
        d.text((x + 6, sy), s["value"], font=font(SANS_B, 19), fill=NAVY)
        d.text((x + 6, sy + 24), s["label"], font=font(SANS, 9), fill=MUTED)
    d.rectangle([MARGIN, sy + sh, W - MARGIN, sy + sh + 1], fill=INK)

    # ---------- Hero trio ----------
    hy, hh = 142, 242
    hw = (CW - 24) // 3
    hero_draw = [hero_summit, hero_icj, hero_cop]
    for i, item in enumerate(data["featured"][:3]):
        x = MARGIN + i * (hw + 12)
        d.rectangle([x, hy, x + hw, hy + hh], fill=PANEL, outline=(200, 194, 180), width=1)
        hero_draw[i](d, x + 1, hy + 1, hw - 2, 100)
        d.rectangle([x, hy + 101, x + hw, hy + 103], fill=RULE)
        n = str(item["n"])
        d.ellipse([x + 10, hy + 112, x + 28, hy + 130], fill=RULE)
        d.text((x + 15, hy + 114), n, font=font(SANS_B, 11), fill=LIGHT)
        d.text((x + 34, hy + 113), item["place"].upper(), font=font(SANS_B, 9), fill=MUTED)
        f_h = font(SERIF_B, 16)
        lines = wrap(d, item["headline"], f_h, hw - 20)
        yy = text_block(d, x + 10, hy + 132, lines[:3], f_h, INK, 19)
        f_s = font(SANS, 10)
        slines = wrap(d, item["summary"], f_s, hw - 20)
        text_block(d, x + 10, yy + 4, slines[:5], f_s, (60, 58, 52), 13)
        d.text((x + 10, hy + hh - 18), item["source"], font=font(SANS_B, 8), fill=MUTED)
        tag_chip(d, x + hw - 66, hy + hh - 19, item["confidence"], REGION_COLORS[item["region"]])

    # ---------- Grid of 12 ----------
    gy = 394
    gw = (CW - 16) // 3
    gh, gap = 74, 6
    for idx, item in enumerate(data["featured"][3:]):
        r, c = divmod(idx, 3)
        x = MARGIN + c * (gw + 8)
        y = gy + r * (gh + gap)
        color = REGION_COLORS[item["region"]]
        d.rectangle([x, y, x + gw, y + gh], fill=PANEL, outline=(200, 194, 180), width=1)
        d.rectangle([x, y, x + 4, y + gh], fill=color)
        icon = ICON_BUILDERS[item["n"]](color)
        img.paste(icon, (x + 10, y + 8))
        d.text((x + 10, y + 46), str(item["n"]), font=font(SANS_B, 13), fill=color)
        tx = x + 50
        f_h = font(SANS_B, 11)
        lines = wrap(d, item["headline"], f_h, gw - 60)
        yy = text_block(d, tx, y + 6, lines[:2], f_h, INK, 13)
        f_s = font(SANS, 9)
        slines = wrap(d, item["summary"], f_s, gw - 60)
        text_block(d, tx, yy + 1, slines[:2], f_s, (70, 67, 60), 11)
        d.text((tx, y + gh - 13), item["place"] + "  ·  " + item["source"],
               font=font(SANS, 8), fill=MUTED)
        tag_chip(d, x + gw - 62, y + gh - 14, item["confidence"], color)

    # ---------- World map ----------
    my, mh = 712, 100
    d.text((MARGIN, my), "WHERE IT HAPPENED", font=font(SANS_B, 11), fill=INK)
    d.text((MARGIN + 168, my), "— the day on the map  ·  5 = GTA VI, launched worldwide",
           font=font(SANS, 10), fill=MUTED)
    map_top = my + 18
    d.rectangle([MARGIN, map_top, W - MARGIN, map_top + 80], fill=MAP_BG,
                outline=(200, 194, 180), width=1)

    def to_xy(lon, lat):
        px = MARGIN + (lon + 180) / 360 * CW
        py = map_top + (85 - lat) / 145 * 80
        return px, py

    for poly in CONTINENTS.values():
        d.polygon([to_xy(lo, la) for lo, la in poly], fill=LAND)
    f_dot = font(SANS_B, 8)
    for item in data["featured"]:
        if item["lon"] is None:
            continue
        px, py = to_xy(item["lon"], item["lat"])
        ox, oy = DOT_OFFSETS.get(item["n"], (0, 0))
        px, py = px + ox, py + oy
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=DOT, outline=LIGHT, width=1)
        t = str(item["n"])
        tw = d.textlength(t, font=f_dot)
        d.text((px - tw / 2, py - 6), t, font=f_dot, fill=LIGHT)

    # ---------- Also on Thursday ----------
    ay = 820
    also = data["also"]
    d.text((MARGIN, ay), "ALSO ON THURSDAY", font=font(SANS_B, 11), fill=INK)
    d.text((MARGIN + 150, ay), "— " + str(len(also)) + " more verified stories from the day",
           font=font(SANS, 10), fill=MUTED)
    d.rectangle([MARGIN, ay + 16, W - MARGIN, ay + 17], fill=INK)
    col_w = CW // 2 - 8
    f_a = font(SANS, 8.5)
    f_ab = font(SANS_B, 8.5)
    rows = (len(also) + 1) // 2
    for i, item in enumerate(also):
        col, row = divmod(i, rows)
        x = MARGIN + col * (col_w + 16)
        y = ay + 22 + int(row * 9.5)
        n = str(item["n"]) + ". "
        d.text((x, y), n, font=f_ab, fill=RULE)
        nx = x + d.textlength(n, font=f_ab)
        head = item["headline"]
        # trim headline to fit, keep place + source
        suffix = "  (" + item["place"].split(",")[0] + "; " + item["source"] + ")"
        maxw = col_w - (nx - x)
        while d.textlength(head + suffix, font=f_a) > maxw and len(head) > 12:
            head = head[:-1]
        if head != item["headline"]:
            head = head.rstrip() + "…"
        d.text((nx, y), head, font=f_a, fill=INK)
        d.text((nx + d.textlength(head, font=f_a), y), suffix, font=f_a, fill=MUTED)

    # ---------- Footer: date check ----------
    fy = 978
    d.rectangle([MARGIN, fy, W - MARGIN, fy + 1], fill=INK)
    d.text((MARGIN, fy + 6), "DATE CHECK — LEFT OUT ON PURPOSE:",
           font=font(SANS_B, 9), fill=RULE)
    lx = MARGIN + d.textlength("DATE CHECK — LEFT OUT ON PURPOSE:  ", font=font(SANS_B, 9))
    left = "  ·  ".join(data["left_out"])
    f_f = font(SANS, 8)
    while d.textlength(left, font=f_f) > (W - MARGIN - lx):
        left = left[:left.rfind("  ·  ")]
    d.text((lx, fy + 6), left, font=f_f, fill=MUTED)
    note = ("All " + str(data["stories_total"]) + " stories happened or were first reported on Thu 19 Nov 2026. "
            "CLAIM = unverified claim, never fact. Sources: Reuters, AP, BBC, WSJ, IAEA, ICJ, IMD, ABS, Le Monde.")
    d.text((MARGIN, fy + 20), note, font=font(SANS, 8), fill=MUTED)

    img.save(HERE / "entry.png", format="PNG", optimize=True)
    print("wrote", HERE / "entry.png")


if __name__ == "__main__":
    render()
