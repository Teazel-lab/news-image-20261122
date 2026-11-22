#!/usr/bin/env python3
"""Build entry.png (1024x1024) for 22 November 2026 (Sunday) from data/stories.json.

usage: python3 build.py [stories.json] [output_dir]

Writes <out>/render.html, renders it twice with headless Chrome, palette-quantises
the screenshot with Pillow, checks the two renders are byte-identical, the size
limits, and that no text on the page is smaller than 11 px.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

W = H = 1024
PAPER, INK, RULE = "#F4EFE4", "#1d1a16", "#b9b0a0"
ACCENT = "#8e1b1b"
CONFIRMED_C, CLAIM_C = "#2e7d4f", "#a8670f"
MIN_PX = 11.0
DEFAULT_DATE_LABEL = "Sunday 22 November 2026"

REGIONS = [  # key, label, colour
    ("Europe", "EUROPE", "#2f5fa8"),
    ("Americas", "AMERICAS", "#c0392b"),
    ("Asia", "ASIA", "#7b4fa0"),
    ("Africa", "AFRICA", "#2e8b4a"),
    ("Middle East", "MIDDLE EAST", "#b8862b"),
    ("Oceania", "OCEANIA", "#178a8a"),
    ("World/Space", "WORLD / SPACE", "#5e6670"),
]
RSHORT = {"World/Space": "WORLD", "Middle East": "MIDEAST", "Americas": "AMER.", "Oceania": "OCEANIA"}
LSHORT = {"Europe": "EUROPE", "Americas": "AMER.", "Africa": "AFRICA", "Middle East": "MIDEAST",
          "Oceania": "OCEANIA", "World/Space": "WORLD"}
RCOL = {k: c for k, _, c in REGIONS}
RLAB = {k: l for k, l, _ in REGIONS}
INHABITED = {"Europe", "Americas", "Asia", "Africa", "Oceania"}


def rkey(r):
    r = (r or "").strip().lower()
    if r.startswith("world") or r.startswith("space") or r.startswith("global"):
        return "World/Space"
    for k, _, _ in REGIONS:
        if k.lower() == r:
            return k
    if r in ("mideast", "middle-east", "middleeast"):
        return "Middle East"
    raise SystemExit(f"unknown region: {r!r}")


def esc(s):
    return html.escape(str(s), quote=True)


def esc_nb(s):
    """esc(), keeping number ranges such as 37-12, 20-17 or 2028-34 on one line."""
    return re.sub(r"\d+[-–]\d+", lambda m: f'<span style="white-space:nowrap">{m.group(0)}</span>', esc(s))


# ---------------------------------------------------------------- world map
# Hand-drawn, deliberately simplified outlines, (lon, lat) degrees.
LAND = {
    "north_america": [(-168, 66), (-162, 70), (-156, 71.5), (-140, 70), (-128, 70), (-115, 68.5), (-104, 68), (-95, 72),
                      (-85, 70), (-82, 66.5), (-86, 64), (-94, 62), (-93, 59), (-88, 56.5), (-82, 55), (-79, 52), (-77, 56),
                      (-78, 62), (-72, 62), (-64, 60), (-62, 56), (-56, 52), (-60, 47), (-66, 44.5), (-70, 42), (-74, 40.5),
                      (-76, 35), (-81, 31), (-80, 25.5), (-82, 27), (-84, 30), (-90, 29.5), (-94, 29.5), (-97, 26),
                      (-97, 21), (-95, 18.5), (-91, 19), (-90, 21), (-87, 21.5), (-88, 16), (-84, 15), (-83, 11),
                      (-79.5, 9), (-77.5, 8), (-80, 7.5), (-83, 8.5), (-86, 11), (-88, 13.5), (-92, 14.5), (-96, 16),
                      (-105, 20), (-106, 23), (-110, 23), (-112, 26), (-112.5, 29), (-114.5, 31), (-118, 34), (-121, 35),
                      (-124, 40), (-124, 46), (-123, 49), (-130, 54), (-135, 58), (-142, 60), (-150, 61), (-154, 58),
                      (-158, 57), (-164, 55), (-162, 58), (-166, 60), (-165, 63)],
    "baffin": [(-90, 73), (-75, 74), (-62, 67), (-66, 62), (-78, 63), (-88, 68)],
    "victoria": [(-118, 72.5), (-102, 72.5), (-104, 68.5), (-118, 69.5)],
    "ellesmere": [(-92, 76.5), (-80, 76), (-64, 80), (-75, 82), (-92, 81)],
    "greenland": [(-73, 78), (-60, 82), (-30, 83), (-18, 80), (-20, 72), (-24, 69), (-32, 68), (-42, 60), (-48, 61),
                  (-53, 66), (-55, 71), (-62, 76)],
    "iceland": [(-24, 65.5), (-22, 66.4), (-16, 66.5), (-13.6, 65.2), (-18, 63.4), (-22.5, 63.8)],
    "cuba": [(-85, 22), (-80, 23.2), (-74, 20.2), (-78, 20), (-82, 21.5)],
    "hispaniola": [(-74.3, 19.9), (-69, 19.6), (-68.4, 18.4), (-72, 18)],
    "south_america": [(-77, 8.5), (-72, 12), (-64, 10.5), (-60, 8.5), (-52, 5), (-50, 0), (-44, -2.5), (-35, -5),
                      (-35, -9), (-39, -15), (-41, -22), (-48, -26), (-53, -33.5), (-58, -38), (-62, -39), (-65, -42),
                      (-67, -46), (-66, -48), (-69, -51), (-68.5, -55), (-72, -54), (-75, -49), (-74, -42), (-73, -37),
                      (-71.5, -30), (-70.5, -18), (-76, -14), (-81, -6), (-80.5, -2), (-77, 3), (-78, 7)],
    "eurasia": [(-9, 43), (-9, 39), (-8.8, 37), (-6, 36.2), (-2, 36.8), (0, 39), (3, 42), (3.5, 43.3), (7, 43.6),
                (9, 44.3), (10.5, 43), (12, 42), (15.5, 40), (16, 38), (17, 39), (18.5, 40), (16, 41.5), (13.5, 44),
                (12.3, 45.3), (13.7, 45.6), (15, 44.5), (19, 42), (19.5, 40), (21, 38), (22.5, 36.5), (23, 38),
                (24, 40.5), (26, 41), (26.5, 40), (27, 37.5), (30, 36.3), (36, 36.8), (36, 35), (35, 33),
                (34.3, 31.3), (34.9, 29.5), (36.5, 28), (39, 22), (42.5, 16), (43.5, 12.7), (45, 13), (48, 14),
                (52, 15.5), (55, 17.5), (57.5, 19), (59.8, 22.5), (58.5, 23.6), (56.5, 24.5), (56.3, 26.3), (54, 24),
                (51.5, 24.5), (51, 26), (50, 26.5), (48, 29.5), (50, 30), (51.5, 27.8), (54, 26.7), (57, 25.8),
                (61.5, 25.2), (66.5, 25.4), (68, 23.5), (70, 21), (72.8, 21), (73, 17), (74.8, 12.5), (76.5, 8.5),
                (77.5, 8), (78.3, 9), (80.2, 13), (80, 15.5), (82.5, 17), (86, 20), (87, 21.5), (90, 22),
                (91.8, 22.4), (92.5, 20.5), (94.3, 18), (94.2, 16), (97.5, 16.5), (98.2, 13), (98.5, 9), (100.4, 7),
                (101.2, 2.8), (103.5, 1.3), (103.5, 4), (102.3, 6.2), (100.2, 13.5), (102.3, 12), (104.8, 8.6),
                (106, 9.8), (109, 11.5), (109.3, 13.5), (108.5, 15.5), (106.6, 17.5), (105.7, 19), (107, 21),
                (108.5, 21.6), (110.4, 21), (113, 22.2), (117, 23), (119.5, 25.5), (121.6, 28), (122, 30.5),
                (120.8, 32.5), (119.3, 35), (122.5, 37), (121, 37.7), (118.5, 38.5), (117.6, 39), (119.5, 40),
                (121.6, 40.9), (121.3, 39), (124.3, 39.9), (126, 37.5), (126.5, 34.5), (129.4, 35.3), (129.5, 37),
                (128.3, 38.6), (129.8, 41), (132, 43), (135.5, 43.8), (138, 46), (140.4, 48.5), (141.3, 53),
                (138.5, 54), (135.2, 54.8), (140.5, 59.5), (149, 59.5), (154.5, 59.3), (156.5, 61.5), (160, 61.7),
                (156.6, 57.5), (156, 51), (160, 53), (162.5, 56), (163, 58), (164, 60), (170, 60), (177, 62.5),
                (179.5, 64.5), (186, 65), (191, 66), (191, 67.5), (180, 68.8), (170, 70), (160, 69.8), (150, 71),
                (140, 72.5), (130, 71), (125, 73.5), (113, 73.7), (110, 76.8), (104, 77.7), (98, 76), (90, 75.5),
                (80, 73.5), (72, 72.8), (69, 73), (66, 69.5), (60, 69), (55, 68.5), (44, 68.3), (40, 66), (41, 67),
                (33, 69.5), (28, 71), (20, 70), (15, 68.5), (12.5, 65.5), (10, 63.5), (5, 62), (5.5, 58.8), (8, 58),
                (10.7, 59.5), (11.5, 58.5), (12.8, 56), (14.3, 55.6), (16, 56.5), (18.5, 59.5), (17.5, 61),
                (17.5, 62.6), (21, 64.5), (25, 65.5), (25, 64), (21.5, 62.5), (21.5, 60.5), (23, 60), (29, 60.4),
                (24, 59.4), (23.5, 58), (24.5, 57.2), (21, 56.8), (21, 55.3), (19.5, 54.4), (14.2, 53.9), (11, 54),
                (10, 54.8), (9.5, 57.1), (8.1, 56.5), (8.6, 53.9), (7, 53.5), (4.5, 52), (3, 51.2), (1.6, 50.9),
                (-1.5, 49.6), (-1.8, 48.6), (-4.7, 48.5), (-2.3, 47.2), (-1.2, 46), (-1.5, 43.5), (-8, 43.7)],
    "britain": [(-5.7, 50), (-3, 50.6), (1.4, 51.2), (1.7, 52.7), (0.2, 53.4), (-0.2, 54.5), (-1.6, 55.6), (-2.1, 57.6),
                (-3.8, 57.7), (-3.1, 58.6), (-5, 58.6), (-6.2, 57.5), (-5.6, 56.3), (-4.8, 55), (-3, 54.9),
                (-3.4, 53.4), (-4.7, 52.8), (-4.2, 51.6), (-5.3, 51.7)],
    "ireland": [(-6, 52), (-6.1, 54), (-5.6, 55.2), (-7.3, 55.4), (-8.5, 54.5), (-10, 53.6), (-9.8, 51.6), (-8, 51.6)],
    "sicily": [(12.4, 38.1), (15.6, 38.3), (15.1, 36.7)],
    "sardinia": [(8.4, 41), (9.6, 41), (9.6, 39.1), (8.4, 39)],
    "svalbard": [(11, 78.8), (17, 80), (27, 80), (22, 77.5), (16, 76.5)],
    "novaya_zemlya": [(52, 71.5), (56, 73.5), (61, 76), (68, 77), (60, 74), (56, 70.8)],
    "africa": [(-17, 21), (-16.5, 24.5), (-13, 27.6), (-9.8, 30), (-9.7, 32.5), (-6.8, 34), (-5.9, 35.8), (-2, 35.1),
               (1, 36.5), (10, 37.3), (11, 35.5), (10.2, 34), (11.5, 33.1), (15.2, 32.3), (19, 30.3), (20, 31),
               (20.1, 32.5), (23, 32.6), (25, 31.6), (29, 30.9), (32.3, 31.3), (34.2, 31.2), (32.6, 29.9), (35.5, 24),
               (37.3, 21), (38.5, 18), (39.7, 15.2), (41.7, 13.3), (43.3, 11.8), (44.5, 10.4), (51, 11.8),
               (51.1, 10.4), (49.5, 6.8), (47.5, 4.5), (43.5, 0.5), (40.9, -2.3), (39.2, -4.7), (39.3, -8),
               (40.5, -10.5), (40.6, -15), (36.5, -18.9), (35.3, -22.5), (32.9, -25.9), (32.5, -28.7), (30.5, -31),
               (27.5, -33.5), (25.6, -34), (22.5, -33.9), (20, -34.8), (18.4, -34.1), (18.2, -31.6), (15.3, -27),
               (14.4, -22.5), (11.8, -17.3), (12.2, -13.7), (13.8, -11), (12.3, -6), (11.8, -4.5), (9.6, -2),
               (9.4, 0.7), (9.7, 3.6), (8.5, 4.5), (6.8, 4.3), (5, 5.8), (3, 6.3), (1, 5.9), (-2, 4.8), (-4.6, 5.2),
               (-7.5, 4.4), (-9.3, 5.6), (-11.5, 6.9), (-13.2, 8.9), (-15, 11), (-16.7, 12.4), (-17.5, 14.7),
               (-16.2, 19.2)],
    "madagascar": [(49.3, -12), (50.5, -15.5), (49.8, -17), (47.1, -24.9), (45, -25.5), (43.3, -22), (44.3, -16.5),
                   (47, -15.5)],
    "sri_lanka": [(79.8, 9.8), (81.9, 7.5), (81.3, 6.2), (80, 6.2)],
    "taiwan": [(120.2, 23), (121.6, 25.2), (121.9, 24.3), (120.8, 21.9)],
    "hainan": [(108.7, 19), (110.2, 20.1), (111, 19.6), (109.5, 18.2)],
    "honshu": [(130.9, 34), (132.5, 35.4), (135.8, 35.7), (137, 37.2), (139.5, 38), (140, 40), (140.6, 41.3),
               (142, 39.5), (141, 36.8), (140.8, 35), (139, 34.7), (136.8, 34.4), (135, 33.6), (132, 33.8)],
    "kyushu": [(129.7, 33.6), (131.9, 33.3), (131, 31.2), (130.2, 31.4)],
    "hokkaido": [(140, 41.5), (140.3, 43.3), (141.7, 45.4), (145.5, 43.3), (143.2, 42), (141, 41.8)],
    "sakhalin": [(142, 46), (143.3, 49), (142.6, 54.3), (141.8, 52), (142, 48)],
    "luzon": [(120.2, 18.5), (122.2, 18.5), (122, 16), (124, 13), (121.5, 13.8), (120.5, 15), (120, 16.5)],
    "visayas": [(122.5, 11.8), (125.5, 12.5), (125, 10), (123, 9.2)],
    "mindanao": [(122, 7), (125.5, 9.8), (126.5, 7), (125.4, 5.6), (123.9, 7.6)],
    "sumatra": [(95.2, 5.6), (98, 4), (103.8, -1), (106, -3.2), (105.8, -5.8), (102.3, -4), (100.5, -1), (98.5, 1.8),
                (95.5, 3)],
    "java": [(105.2, -6.8), (106.5, -6), (110, -6.9), (114.4, -7.8), (114.5, -8.7), (108.8, -7.8), (105.6, -7.5)],
    "borneo": [(109, 1.8), (110, 1.8), (115, 5), (117, 7), (119, 5.2), (117.5, 1), (116, -3.8), (114.5, -3.8),
               (110.3, -2.9), (109, -0.5)],
    "sulawesi": [(119.4, -5.5), (120.5, -5.5), (121, -2.5), (123.3, -0.9), (125, 1.5), (120.8, 1.2), (119.5, 0),
                 (118.8, -3)],
    "sundas": [(115.5, -8.2), (122, -8.2), (125.5, -8.5), (125, -9.6), (119, -9.2), (115.5, -9)],
    "new_guinea": [(131, -1.3), (134, -0.9), (138, -1.6), (141, -2.6), (145, -4.5), (147.5, -6), (150.5, -10.5),
                   (147, -10), (144, -7.8), (141, -9.2), (139, -8.1), (137.8, -5.2), (133, -4), (132, -2.8)],
    "australia": [(113.5, -22), (114.2, -26), (115, -34), (117.8, -35), (123.5, -33.9), (126, -32.3), (131, -31.5),
                  (134.2, -32.8), (135.8, -34.8), (137.8, -33.2), (138, -35.5), (140.6, -38), (143.5, -38.8),
                  (146.5, -39), (150, -37.5), (151.3, -33.6), (153.6, -28.5), (153, -25), (150.7, -22.5),
                  (146.3, -19), (145.4, -14.8), (143.5, -14), (142.4, -10.7), (141.6, -12.8), (141.6, -16.5),
                  (140.6, -17.5), (139, -16.9), (136.8, -15.8), (136.8, -12.2), (132.6, -11.4), (130.3, -12.4),
                  (129.4, -14.9), (126.9, -13.8), (124.8, -16), (122.3, -17.5), (121, -19.5), (117.4, -20.7),
                  (114.6, -21.8)],
    "tasmania": [(144.7, -40.7), (148.3, -40.9), (148, -43.2), (146, -43.5)],
    "nz_north": [(172.7, -34.4), (174.8, -36.9), (178.5, -37.7), (177, -39.3), (175.2, -41.6), (174.6, -41.2),
                 (173.8, -39.2), (174.6, -37.3)],
    "nz_south": [(172.7, -40.5), (174.3, -41.7), (173, -43.8), (171.2, -44.5), (169, -46.6), (166.5, -46),
                 (168.5, -44), (171, -42.5)],
    "new_caledonia": [(164, -20.2), (167.2, -22.4), (166.4, -22.4), (164, -20.8)],
}
SEAS = {  # inland seas drawn over the land in sea colour
    "black_sea": [(27.8, 42), (28.5, 44), (30.7, 46.5), (33.5, 44.5), (36.5, 45.2), (38, 47), (39.5, 47), (41.5, 42),
                  (36, 41.5), (31, 41.1), (29, 41.2)],
    "caspian": [(47, 44.5), (49.5, 46.5), (53, 47), (53, 45), (51, 44.5), (51.3, 43), (53, 41.5), (53.8, 38),
                (52.7, 37.2), (49, 37.6), (48.7, 39), (49.5, 40.5), (47.5, 43)],
}
PACIFIC_DOTS = [(178, -17.8), (-172, -13.8), (-175, -21), (167, -15.5), (160, -9.5), (-149.5, -17.6),
                (-155.5, 19.6), (-157.8, 21.3), (158, 7), (171, 7), (173, 1.5), (-140, -9)]

LON0, LAT_TOP, LAT_BOT = -170.0, 78.0, -56.0
LAND_C, SEA_C, COAST_C, GRAT_C = "#e6dcc6", "#dbe7ee", "#a99d86", "#c3d3dd"


def make_projection(mw, mh):
    sx = mw / 360.0
    sy = mh / (LAT_TOP - LAT_BOT)

    def proj(lon, lat):
        x = ((lon - LON0) % 360.0) if lon < LON0 else (lon - LON0)
        return x * sx, (LAT_TOP - lat) * sy
    return proj, sx, sy


def world_map_svg(mw, mh, pictured):
    proj, sx, sy = make_projection(mw, mh)
    out = [f'<svg width="{mw}" height="{mh}" viewBox="0 0 {mw} {mh}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{mw}" height="{mh}" fill="{SEA_C}"/>']
    for lon in range(-150, 190, 30):
        x = (lon - LON0) * sx
        out.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{mh}" stroke="{GRAT_C}" stroke-width="0.6"/>')
    for lat in (60, 30, 0, -30):
        y = (LAT_TOP - lat) * sy
        dash = '' if lat == 0 else ' stroke-dasharray="2 2"'
        out.append(f'<line x1="0" y1="{y:.1f}" x2="{mw}" y2="{y:.1f}" stroke="{GRAT_C}" stroke-width="0.6"{dash}/>')

    def poly(pts, fill, stroke):
        d = " ".join(f"{proj(lo, la)[0]:.1f},{proj(lo, la)[1]:.1f}" for lo, la in pts)
        return f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="0.6" stroke-linejoin="round"/>'
    for pts in LAND.values():
        out.append(poly(pts, LAND_C, COAST_C))
    for pts in SEAS.values():
        out.append(poly(pts, SEA_C, COAST_C))
    for lo, la in PACIFIC_DOTS:
        x, y = proj(lo, la)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="{COAST_C}"/>')

    # pins
    R = 8.0
    pins, orbit, glob = [], [], []
    for s in pictured:
        if s.get("lat") is None or s.get("lon") is None:
            # only space stories go "in orbit"; place-less earthly stories get a GLOBAL box
            (orbit if s.get("beat", "").lower() == "space" else glob).append(s)
            continue
        x, y = proj(float(s["lon"]), float(s["lat"]))
        pins.append({"n": s["n"], "c": RCOL[rkey(s["region"])], "ox": x, "oy": y, "x": x, "y": y})
    # orbit ring over the south-east Pacific
    if orbit:
        cx, cy = proj(-135, -28)
        rx, ry = 30, 12
        out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" '
                   f'stroke-width="1.2" stroke-dasharray="3 2.5"/>')
        out.append(f'<text x="{cx:.1f}" y="{cy + ry + 13:.1f}" text-anchor="middle" font-family="Barlow Condensed" '
                   f'font-weight="700" font-size="11" letter-spacing="0.5" fill="{INK}">IN ORBIT</text>')
        k = len(orbit)
        for i, s in enumerate(orbit):
            # spread around the upper half of the ring
            import math
            a = math.radians(-60 - (i * 60 if k > 1 else 0))
            px, py = cx + rx * math.cos(a), cy + ry * math.sin(a)
            pins.append({"n": s["n"], "c": RCOL[rkey(s["region"])], "ox": px, "oy": py, "x": px, "y": py,
                         "fixed": True})
    # "GLOBAL · ONLINE" box above the orbit ring, for stories with no real place (markets, online)
    if glob:
        k = len(glob)
        bw, bh = max(78, 20 * k + 10), 30
        # sits clear above the orbit ring and the pin on its rim (ring top = cy - 12)
        bx0, by0 = 3, (proj(-135, -28)[1] - 12 - 22 - bh if orbit else mh - bh - 6)
        out.append(f'<rect x="{bx0}" y="{by0:.1f}" width="{bw}" height="{bh}" rx="3" fill="{SEA_C}" '
                   f'stroke="{INK}" stroke-width="1.1"/>')
        out.append(f'<text x="{bx0 + bw / 2:.1f}" y="{by0 + bh - 4.5:.1f}" text-anchor="middle" '
                   f'font-family="Barlow Condensed" font-weight="700" font-size="11" letter-spacing="0.3" '
                   f'fill="{INK}">GLOBAL · ONLINE</text>')
        for i, s in enumerate(glob):
            px = bx0 + bw / 2 + (i - (k - 1) / 2) * 19
            py = by0 + 10.5
            pins.append({"n": s["n"], "c": RCOL[rkey(s["region"])], "ox": px, "oy": py, "x": px, "y": py,
                         "fixed": True})
    # deterministic relaxation to separate overlapping pins
    minsep = 2 * R + 1
    for _ in range(200):
        moved = False
        for i in range(len(pins)):
            for j in range(i + 1, len(pins)):
                a, b = pins[i], pins[j]
                dx, dy = b["x"] - a["x"], b["y"] - a["y"]
                d = (dx * dx + dy * dy) ** 0.5
                if d < minsep:
                    if d < 1e-6:
                        dx, dy, d = 1.0, 0.35, 1.06
                    push = (minsep - d) / 2 + 0.05
                    ux, uy = dx / d, dy / d
                    fa, fb = (0 if a.get("fixed") else 1), (0 if b.get("fixed") else 1)
                    if fa + fb == 0:
                        continue
                    sa = push * 2 * fa / (fa + fb)
                    sb = push * 2 * fb / (fa + fb)
                    a["x"] -= ux * sa; a["y"] -= uy * sa
                    b["x"] += ux * sb; b["y"] += uy * sb
                    moved = True
        for p in pins:
            p["x"] = min(max(p["x"], R + 1), mw - R - 1)
            p["y"] = min(max(p["y"], R + 1), mh - R - 1)
        if not moved:
            break
    for p in pins:
        if abs(p["x"] - p["ox"]) + abs(p["y"] - p["oy"]) > 3:
            out.append(f'<line x1="{p["ox"]:.1f}" y1="{p["oy"]:.1f}" x2="{p["x"]:.1f}" y2="{p["y"]:.1f}" '
                       f'stroke="{INK}" stroke-width="0.9"/>')
            out.append(f'<circle cx="{p["ox"]:.1f}" cy="{p["oy"]:.1f}" r="1.8" fill="{INK}"/>')
    for p in pins:
        out.append(f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="{R}" fill="{p["c"]}" stroke="#fff" '
                   f'stroke-width="1.3"/>')
        out.append(f'<text x="{p["x"]:.1f}" y="{p["y"] + 4:.1f}" text-anchor="middle" font-family="Barlow Condensed" '
                   f'font-weight="700" font-size="11.5" fill="#fff">{p["n"]}</text>')
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------------- page
# v2 geometry (all px). Masthead + region bar end at 119.
M = 14                         # left/right margin
TL_TOP, TL_H = 121, 42         # "THE DAY IN UTC" strip
LEAD_TOP, LEAD_H, LEAD_PIC = 166, 253, 132
GUT = 10                       # horizontal gutter between cards
ROW_GAP = 6                    # vertical gap between card rows
CARD_H, CARD_PIC = 147, 66
ROW1 = LEAD_TOP + LEAD_H + ROW_GAP
ROW2 = ROW1 + CARD_H + ROW_GAP
SECT_TOP = ROW2 + CARD_H + 5   # bottom-band section heads
BAND_TOP = SECT_TOP + 20       # top of map and brief block
DC_TOP, DC_H = 975, 32         # date-check band: 1px border + 3px pad + 2 x 13.6px lines
BRIEF_GAP = 4                  # min clear space between last brief row and the date-check band
BRIEF_H = DC_TOP - BRIEF_GAP - BAND_TOP
BRIEF_MIN_PITCH = 13.0         # rows closer than this are an error
MAP_W = 340
LEGEND_H = 28                  # two 13px legend lines + gap
MAP_H = DC_TOP - 6 - LEGEND_H - BAND_TOP

CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{PAPER};color:{INK}}}
body{{position:relative;font-family:'Barlow',sans-serif;-webkit-font-smoothing:antialiased}}
.abs{{position:absolute}}
.serif{{font-family:'DM Serif Display',serif;font-weight:400}}
.cond{{font-family:'Barlow Condensed',sans-serif}}
.kick{{font-family:'Barlow Condensed';font-weight:700;font-size:12px;letter-spacing:.08em;text-transform:uppercase;
  white-space:nowrap;line-height:14px}}
.date{{left:14px;right:14px;top:13px;height:62px;text-align:center;font-size:61px;line-height:62px;white-space:nowrap;
  letter-spacing:-.005em}}
.dek{{left:14px;right:14px;top:75px;height:19px;text-align:center;font-family:'DM Serif Display';font-style:italic;
  font-size:15.5px;line-height:19px;color:{ACCENT};white-space:nowrap}}
.rule2{{left:14px;right:14px;top:94px;height:5px;border-top:2.5px solid {INK};border-bottom:1px solid {INK}}}
.bar{{left:14px;right:14px;top:102px;height:17px;display:flex;gap:2px}}
.bar div{{color:#fff;font-family:'Barlow Condensed';font-weight:700;font-size:11.5px;letter-spacing:.07em;
  line-height:17px;text-align:center;white-space:nowrap;overflow:hidden}}
.tl{{left:{M}px;right:{M}px;top:{TL_TOP}px;height:{TL_H}px;border-bottom:1px solid {RULE}}}
.tl .lab{{position:absolute;left:0;top:4px;width:62px;font-family:'Barlow Condensed';font-weight:700;font-size:13px;
  line-height:15px;letter-spacing:.08em;white-space:nowrap}}
.tl .line{{position:absolute;top:8px;height:1.5px;background:{INK}}}
.tl .stop{{position:absolute;top:0;text-align:center;line-height:16px;font-size:0}}
.tl .stop b{{display:block;width:fit-content;margin:0 auto;font-family:'Barlow Condensed';font-weight:700;font-size:14px;line-height:16px;
  color:{ACCENT};background:{PAPER};padding:0 6px;letter-spacing:.02em;line-height:15px}}
.tl .stop span{{display:block;font-family:'Barlow';font-size:12.5px;line-height:12.5px;color:{INK};margin-top:0}}
.card{{background:#fbf8f1;border:1px solid {RULE};display:flex;flex-direction:column;overflow:hidden}}
.ill{{position:relative;overflow:hidden;flex:none;background:#e9e2d3}}
.ill > svg{{display:block}}
.capband{{position:absolute;left:0;right:0;bottom:0;background:rgba(22,20,18,.86);color:#fff;
  font-family:'Barlow Condensed';font-weight:700;font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;
  white-space:nowrap;overflow:hidden;padding:0 6px}}
.kr{{display:flex;align-items:center;gap:5px;white-space:nowrap;overflow:hidden;flex:none}}
.badge{{flex:none;border-radius:50%;color:#fff;font-family:'Barlow Condensed';font-weight:700;text-align:center}}
.hl{{font-family:'DM Serif Display';font-weight:400;color:{INK};flex:none}}
.sub{{flex:none;font-family:'Barlow';color:#3a352e}}
.tag{{flex:none;align-self:flex-start;font-family:'Barlow Condensed';font-weight:700;
  letter-spacing:.03em;border:1.3px solid;border-radius:2px;white-space:nowrap;overflow:hidden;
  max-width:100%;margin-top:auto;background:#fff}}
.confirmed{{color:{CONFIRMED_C};border-color:{CONFIRMED_C}}}
.claim{{color:{CLAIM_C};border-color:{CLAIM_C}}}
.sect{{font-family:'Barlow Condensed';font-weight:700;font-size:13px;letter-spacing:.08em;line-height:15px;
  white-space:nowrap;border-bottom:1px solid {INK};padding-bottom:2px}}
.legend{{font-family:'Barlow Condensed';font-size:12px;line-height:13px;white-space:nowrap;overflow:hidden;color:#3a352e}}
.legend .dot{{display:inline-block;width:8px;height:8px;border-radius:50%;margin:0 2px 0 0;vertical-align:0}}
.legend .rg{{margin-right:5px}}
.legend b{{font-weight:700;letter-spacing:.04em;color:{INK}}}
.legend .mt{{display:inline-block;font-weight:700;font-size:11px;line-height:11px;padding:0 3px;border:1.2px solid;
  border-radius:2px;background:#fff;letter-spacing:.03em;margin:0 3px 0 4px}}
.briefs{{display:flex;gap:14px}}
.bcol{{flex:1 1 0;display:flex;flex-direction:column;min-width:0}}
.brief{{flex:none;font-family:'Barlow';white-space:nowrap;overflow:hidden}}
.brief .bn{{display:inline-block;width:19px;font-family:'Barlow Condensed';font-weight:700}}
.brief b{{font-weight:700}}
.brief i{{color:#6b645a;font-style:italic}}
.dc{{left:0;right:0;top:{DC_TOP}px;height:{DC_H}px;background:#e3ecdf;border-top:1px solid #9fb59a;
  border-bottom:1px solid #9fb59a;padding:3px 14px 0 14px;font-size:12px;line-height:13.6px;overflow:hidden}}
.dc .chip{{display:inline-block;background:#1f4d2e;color:#fff;font-family:'Barlow Condensed';font-weight:700;
  font-size:12px;letter-spacing:.08em;padding:0 6px;margin-right:6px;line-height:14px;border-radius:2px}}
.foot{{left:14px;right:14px;top:1009px;height:14px;text-align:center;font-family:'Barlow Condensed';font-size:11.5px;
  line-height:14px;color:#4a443b;white-space:nowrap;overflow:hidden}}
"""

# JS: fit headlines/subheads into their cards, fit briefs, then measure every text element.
JS = r"""
(function(){
var rep={small:[],overflow:[],warn:[],briefs:[],bbox:[],dclines:0,fonts:{}};
function bodyOver(card){var b=card.querySelector('.cbody');return b.scrollHeight>b.clientHeight+1;}
function overflowing(el){if(el.classList.contains('card')&&bodyOver(el))return true;return el.scrollHeight>el.clientHeight+1||el.scrollWidth>el.clientWidth+1;}
function lines(el){var lh=parseFloat(getComputedStyle(el).lineHeight);return Math.round(el.getBoundingClientRect().height/lh);}
document.querySelectorAll('[data-fit]').forEach(function(card){
  var h=card.querySelector('.hl'),sub=card.querySelector('.sub'),n=card.dataset.n;
  var p=card.dataset.fit.split(','),s0=parseFloat(p[0]),min=parseFloat(p[1]),maxl=parseInt(p[2]),ratio=parseFloat(p[3]);
  var subOne=card.dataset.subone==='1';
  if(sub&&subOne){  // one-line subhead: 12 -> 11.5 -> dropped
    if(sub.scrollWidth>sub.clientWidth+1){sub.style.fontSize='11.5px';}
    if(sub.scrollWidth>sub.clientWidth+1){rep.warn.push('card '+n+': subhead too wide even at 11.5px, dropped: '+sub.textContent);sub.remove();sub=null;}
  }
  if(sub&&!subOne&&lines(sub)>2)rep.warn.push('lead '+n+': subhead runs to '+lines(sub)+' lines (max 2)');
  function fit(){var s=s0;h.style.fontSize=s+'px';h.style.lineHeight=(s*ratio)+'px';
    while((bodyOver(card)||lines(h)>maxl)&&s>min){s-=0.5;h.style.fontSize=s+'px';h.style.lineHeight=(s*ratio)+'px';}}
  fit();
  if(sub&&subOne&&bodyOver(card)){  // headline needs its 3rd line: make room by dropping the subhead
    rep.warn.push('card '+n+': subhead dropped to fit a 3-line headline: '+sub.textContent);sub.remove();sub=null;fit();}
  if(lines(h)>maxl)rep.warn.push('card '+n+': headline is '+lines(h)+' lines (max '+maxl+') at '+h.style.fontSize);
  if(bodyOver(card))rep.overflow.push('card '+n+' body overflows by '+(card.querySelector('.cbody').scrollHeight-card.querySelector('.cbody').clientHeight)+'px');
});
document.querySelectorAll('[data-fitw]').forEach(function(el){
  var p=el.dataset.fitw.split(','),s=parseFloat(p[0]),min=parseFloat(p[1]);
  while(el.scrollWidth>el.clientWidth+1&&s>min){s-=0.5;el.style.fontSize=s+'px';}
});
document.querySelectorAll('.bar div[data-short]').forEach(function(el){
  if(el.scrollWidth>el.clientWidth+1)el.textContent=el.dataset.short;
});
document.querySelectorAll('.tl .stop span').forEach(function(el){
  if(lines(el)>2)rep.warn.push('timeline label over 2 lines: '+el.textContent);
  if(el.scrollWidth>el.clientWidth+1)rep.warn.push('timeline label too wide: '+el.textContent);
});
document.querySelectorAll('.brief').forEach(function(el){
  if(el.scrollWidth>el.clientWidth+1){el.style.fontSize=BRIEF_MIN+'px';}
  if(el.scrollWidth>el.clientWidth+1)rep.briefs.push(el.textContent.trim()+' ['+(el.scrollWidth-el.clientWidth)+'px over]');
});
var dcEl=document.querySelector('.dc'),dcTop=dcEl.getBoundingClientRect().top;
document.querySelectorAll('.bcol').forEach(function(col){
  var cr=col.getBoundingClientRect(),rows=col.querySelectorAll('.brief'),prev=null;
  rows.forEach(function(el){
    var r=el.getBoundingClientRect(),t=el.textContent.trim().slice(0,40);
    if(r.left<cr.left-0.5||r.right>cr.right+0.5||r.top<cr.top-0.5||r.bottom>cr.bottom+0.5)
      rep.bbox.push(t+' outside its column');
    if(r.bottom>dcTop-BRIEF_GAP+0.01)rep.bbox.push(t+' ends '+(r.bottom-(dcTop-BRIEF_GAP)).toFixed(1)+'px too low');
    if(prev!==null&&r.top-prev<BRIEF_MIN_PITCH-0.01)rep.bbox.push(t+' row pitch '+(r.top-prev).toFixed(2)+'px');
    prev=r.top;
  });
});
rep.dclines=Math.round((dcEl.scrollHeight-4)/parseFloat(getComputedStyle(dcEl).lineHeight));
document.querySelectorAll('[data-chk]').forEach(function(el){
  if(overflowing(el))rep.overflow.push(el.dataset.chk+' (+'+(el.scrollWidth-el.clientWidth)+'w,+'+(el.scrollHeight-el.clientHeight)+'h)');
});
var all=document.body.querySelectorAll('*');
for(var i=0;i<all.length;i++){
  var el=all[i];if(el.id==='report'||el.tagName==='SCRIPT'||el.tagName==='STYLE')continue;
  var has=false;for(var c=el.firstChild;c;c=c.nextSibling){if(c.nodeType===3&&c.textContent.trim()){has=true;break;}}
  if(!has)continue;
  var cs=getComputedStyle(el);if(cs.display==='none'||cs.visibility==='hidden')continue;
  var fs=parseFloat(cs.fontSize),sc=1;
  if(el instanceof SVGElement&&el.getScreenCTM){var m=el.getScreenCTM();if(m)sc=Math.sqrt(Math.abs(m.a*m.d-m.b*m.c));}
  var px=fs*sc;
  if(px<11-0.01)rep.small.push(px.toFixed(2)+'px: '+el.textContent.trim().slice(0,40));
}
['DM Serif Display','Barlow','Barlow Condensed'].forEach(function(f){rep.fonts[f]=document.fonts.check('16px "'+f+'"');});
var pre=document.getElementById('report');pre.textContent=JSON.stringify(rep);
})();
"""


def fallback_illus(place, w, h):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="3" y="3" width="{w - 6}" height="{h - 6}" fill="#e2dccd" stroke="{RULE}" stroke-width="2"/>'
            f'<text x="{w / 2}" y="{h / 2 + 5}" text-anchor="middle" font-family="Barlow Condensed" font-size="14" '
            f'fill="#7a7266">{esc(place)}</text></svg>')


def illus_for(s, w, h, ILLUS):
    fn = ILLUS.get(s["id"])
    if fn is None:
        print(f"note: no illustration for id {s['id']!r}; using placeholder", file=sys.stderr)
        return fallback_illus(s.get("place", s["id"]), w, h)
    return fn(w, h)


def status_of(s):
    st = s["status"].strip().lower()
    if st not in ("confirmed", "claim"):
        raise SystemExit(f"story {s['n']}: status must be confirmed|claim")
    return st


def card_html(s, x, y, w, h, ih, lead, ILLUS):
    rk = rkey(s["region"])
    col = RCOL[rk]
    st = status_of(s)
    beat = esc(s.get("beat", "")).upper()
    if lead:  # headline 23px, 2 lines, shrinking to >= 20px; subhead 13px up to 2 lines
        hs, hmin, ratio, maxl = 23, 20, 1.04, 2
        pad, bsz, ksz, band, csz, tsz, tlh = 8, 17, 12, 16, 11.5, 12, 14
        sub = (f'<div class="sub" style="font-size:13px;line-height:14px;margin-top:2px">{esc_nb(s["subhead"])}</div>'
               if s.get("subhead") else "")
    else:     # headline 16px up to 3 lines (>= 14.5px); one-line subhead 12px
        hs, hmin, ratio, maxl = 16, 14.5, 1.03, 3
        pad, bsz, ksz, band, csz, tsz, tlh = 6, 14, 11, 15, 11, 11, 11
        sub = (f'<div class="sub" style="font-size:12px;line-height:13px;margin-top:1px;white-space:nowrap;'
               f'overflow:hidden">{esc_nb(s["subhead"])}</div>' if s.get("subhead") else "")
    tag = (f'<div class="tag {st}" data-chk="tag {s["n"]}" style="font-size:{tsz}px;line-height:{tlh}px;'
           f'padding:0 {5 if lead else 4}px">{"CONFIRMED" if st == "confirmed" else "CLAIM"} · {esc(s["tag"])}</div>')
    kick = (f'<div class="kr" style="margin-top:{5 if lead else 3}px;height:{bsz}px">'
            f'<div class="badge" style="width:{bsz}px;height:{bsz}px;line-height:{bsz}px;font-size:{ksz}px;'
            f'background:{col}">{s["n"]}</div>'
            f'<div class="kick" style="color:{col};font-size:{ksz}px">{RLAB[rk]} · {beat}</div></div>')
    head = (f'<div class="hl" style="font-size:{hs}px;line-height:{hs * ratio:.2f}px;margin-top:{3 if lead else 1}px">'
            f'{esc_nb(s["headline"])}</div>')
    cap = (f'<div class="capband" style="height:{band}px;line-height:{band}px;font-size:{csz}px">'
           f'{esc(s["caption"])}</div>')
    body = (f'<div class="cbody" style="flex:1;display:flex;flex-direction:column;padding:0 {pad}px {3 if lead else 3}px {pad}px;'
            f'min-height:0;overflow:hidden">'
            f'{kick}{head}{sub}<div style="height:{3 if lead else 2}px;flex:none"></div>{tag}</div>')
    return (f'<div class="abs card" data-chk="card {s["n"]}" data-n="{s["n"]}" data-fit="{hs},{hmin},{maxl},{ratio}" '
            f'data-subone="{0 if lead else 1}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="ill" style="width:{w - 2}px;height:{ih}px">{illus_for(s, w - 2, ih, ILLUS)}{cap}</div>'
            f'{body}</div>')


def columns(n, gut):
    """Integer x positions and widths for n equal columns between the margins."""
    cw = (W - 2 * M - (n - 1) * gut) / n
    out = []
    for i in range(n):
        x0 = round(M + i * (cw + gut))
        x1 = round(M + i * (cw + gut) + cw)
        out.append((x0, x1 - x0))
    return out


def build_html(d):
    try:
        from illus import ILLUS
    except ImportError:
        ILLUS = {}
    date_label = (d.get("date_label") or DEFAULT_DATE_LABEL).strip()
    short_date = re.sub(r"\s+\d{4}$", "", date_label)  # e.g. "Sunday 22 November"
    pictured = sorted(d["pictured"], key=lambda s: s["n"])
    briefs = sorted(d["briefs"], key=lambda s: s["n"])
    leads = [s for s in pictured if s.get("lead")]
    rest = [s for s in pictured if not s.get("lead")]
    if len(leads) != 3 or len(rest) != 10:
        raise SystemExit(f"need exactly 3 lead + 10 non-lead pictured stories, got {len(leads)} + {len(rest)}")
    if [s["n"] for s in pictured] != list(range(1, 14)):
        raise SystemExit("pictured stories must be numbered 1..13")
    if [s["n"] for s in leads] != [1, 2, 3]:
        raise SystemExit(f"the 3 lead stories must be numbered 1..3, got {[s['n'] for s in leads]}")
    if not 26 <= len(briefs) <= 36:
        print(f"WARNING: {len(briefs)} briefs; the layout is sized for 26-36", file=sys.stderr)
    if briefs and [b["n"] for b in briefs] != list(range(14, 14 + len(briefs))):
        raise SystemExit("briefs must be numbered consecutively from 14")
    tl = d["timeline"]
    if not 6 <= len(tl) <= 8:
        raise SystemExit(f"timeline needs 6-8 stops, got {len(tl)}")
    for s in pictured + briefs:
        status_of(s)

    counts = {k: 0 for k, _, _ in REGIONS}
    for s in pictured + briefs:
        counts[rkey(s["region"])] += 1
    total = len(pictured) + len(briefs)
    present = {k for k, v in counts.items() if v}
    right = f"{total} STORIES · "
    if INHABITED <= present:
        right += "EVERY INHABITED CONTINENT · "
    right += "ALL FROM THIS ONE DAY"

    P = []
    P.append(f'<div class="abs kick" style="left:14px;top:5px;font-size:12px">THE WORLD IN ONE DAY</div>')
    P.append(f'<div class="abs kick" data-chk="masthead right" style="right:14px;top:5px;font-size:12px">{esc(right)}</div>')
    P.append(f'<div class="abs serif date" data-fitw="61,48">{esc(date_label)}</div>')
    P.append(f'<div class="abs dek" data-chk="dek" data-fitw="15.5,12">{esc(d["dek"])}</div>')
    P.append('<div class="abs rule2"></div>')

    # region bar
    segs = [(k, l, c, counts[k]) for k, l, c in REGIONS if counts[k]]
    avail = W - 28 - 2 * (len(segs) - 1)
    minw = 74
    widths = [max(minw, avail * n / total) for *_, n in segs]
    extra = sum(widths) - avail
    flex_tot = sum(w - minw for w in widths) or 1
    widths = [w - extra * (w - minw) / flex_tot for w in widths]
    bar = "".join(f'<div data-chk="bar {l}" data-short="{RSHORT.get(k, l)} {n}" '
                  f'style="background:{c};width:{w:.1f}px">{l} {n}</div>'
                  for (k, l, c, n), w in zip(segs, widths))
    P.append(f'<div class="abs bar">{bar}</div>')

    # the day in UTC: stops evenly spaced on one rule
    x0, x1 = 66, W - 2 * M        # stop slots span x0..x1 inside the strip
    slot = (x1 - x0) / len(tl)
    stops = []
    for i, t in enumerate(tl):
        sx = x0 + i * slot
        stops.append(f'<div class="stop" style="left:{sx:.1f}px;width:{slot:.1f}px"><b>{esc(t["t"])}</b>'
                     f'<span style="padding:0 4px">{esc(t["label"])}</span></div>')
    P.append(f'<div class="abs tl" data-chk="timeline"><div class="lab">THE DAY<br>IN UTC</div>'
             f'<div class="line" style="left:{x0 + slot / 2 - 16:.1f}px;width:{(len(tl) - 1) * slot + 32:.1f}px"></div>'
             f'{"".join(stops)}</div>')

    # lead row: 3 wide cards
    for (x, w), s in zip(columns(3, GUT), leads):
        P.append(card_html(s, x, LEAD_TOP, w, LEAD_H, LEAD_PIC, True, ILLUS))
    # two rows of 5 cards
    cols5 = columns(5, GUT)
    for i, s in enumerate(rest):
        r, c = divmod(i, 5)
        x, w = cols5[c]
        P.append(card_html(s, x, ROW1 + r * (CARD_H + ROW_GAP), w, CARD_H, CARD_PIC, False, ILLUS))

    # bottom band: map + legend
    P.append(f'<div class="abs sect" style="left:{M}px;top:{SECT_TOP}px;width:{MAP_W}px">WHERE IT HAPPENED</div>')
    P.append(f'<div class="abs" style="left:{M}px;top:{BAND_TOP}px;width:{MAP_W}px;height:{MAP_H}px;border:1px solid {RULE}">'
             f'{world_map_svg(MAP_W - 2, MAP_H - 2, pictured)}</div>')
    regs = "".join(f'<span class="rg"><span class="dot" style="background:{c}"></span>{esc(LSHORT.get(k, l))} {counts[k]}</span>'
                   for k, l, c in REGIONS if counts[k])
    sure = (f'<b>HOW SURE</b><span class="mt confirmed">CONFIRMED</span>2+ outlets or official record'
            f'<span class="mt claim" style="margin-left:8px">CLAIM</span>one side says')
    ly = BAND_TOP + MAP_H + 3
    P.append(f'<div class="abs legend" data-chk="legend regions" data-fitw="12,11" style="left:{M}px;top:{ly}px;'
             f'width:{MAP_W}px;height:13px">{regs}</div>')
    P.append(f'<div class="abs legend" data-chk="legend sure" data-fitw="12,11" style="left:{M}px;top:{ly + 14}px;'
             f'width:{MAP_W}px;height:14px">{sure}</div>')

    # briefs, two columns, rows spread evenly over the band
    bx = M + MAP_W + 18
    bw = W - M - bx
    P.append(f'<div class="abs sect" style="left:{bx}px;top:{SECT_TOP}px;width:{bw}px">ALSO ON {esc(short_date.upper())}</div>')
    half = (len(briefs) + 1) // 2
    cols = [briefs[:half], briefs[half:]]
    pitch = BRIEF_H / max(1, half)
    if pitch < BRIEF_MIN_PITCH:
        print(f"WARNING: {len(briefs)} briefs need {half} rows; row pitch {pitch:.1f}px is under "
              f"{BRIEF_MIN_PITCH}px (fits {2 * int(BRIEF_H // BRIEF_MIN_PITCH)})", file=sys.stderr)
    bfs = 13 if pitch >= 14 else 12.5
    rowh = min(pitch, 17)
    gaps = (BRIEF_H - rowh * half) / max(1, half - 1) if half > 1 else 0

    def brief(b, last):
        return (f'<div class="brief" style="font-size:{bfs}px;line-height:{rowh:.2f}px;height:{rowh:.2f}px;'
                f'margin-bottom:{0 if last else gaps:.2f}px">'
                f'<span class="bn" style="color:{RCOL[rkey(b["region"])]}">{b["n"]}</span>'
                f'<b>{esc(b["place"])}</b> {esc_nb(b["fact"])} <i>{esc(b["source"])}</i></div>')
    bc = "".join(f'<div class="bcol">{"".join(brief(b, j == len(col) - 1) for j, b in enumerate(col))}</div>'
                 for col in cols)
    P.append(f'<div class="abs briefs" style="left:{bx}px;top:{BAND_TOP}px;width:{bw}px;height:{BRIEF_H}px">{bc}</div>')

    # date check
    dc = d["date_check"]
    def keep(x):  # never break inside a trailing "(<date>)"
        return re.sub(r" (\([^)]*\))$", lambda m: " " + m.group(1).replace(" ", " "), esc(x))
    before = "; ".join(keep(x) for x in dc.get("before", []))
    later = "; ".join(keep(x) for x in dc.get("later", []))
    txt = (f'<span class="chip">DATE CHECK ✓</span>Every story on this page happened on '
           f'<b>{esc(date_label)}</b>, or is that day’s new development in a running story.')
    if before:
        txt += f' <b>Left out as other days’ news:</b> {before}'
    if later:
        txt += f' · <b>Later:</b> {later}'
    P.append(f'<div class="abs dc" data-chk="date check">{txt}</div>')

    src = ", ".join(esc(s) for s in d.get("sources", []))
    P.append(f'<div class="abs foot" data-chk="footer" data-fitw="11.5,11">Claims by parties are attributed, not stated '
             f'as fact · Pictures and map drawn in code · Sources: {src}</div>')

    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{esc(date_label)}</title>'
            f'<style>{CSS}</style></head><body>{"".join(P)}'
            f'<pre id="report" style="display:none"></pre><script>var BRIEF_GAP={BRIEF_GAP},'
            f'BRIEF_MIN_PITCH={BRIEF_MIN_PITCH},BRIEF_MIN=12.5;{JS}</script></body></html>')



# ---------------------------------------------------------------- render
# Headless Chrome driven over the DevTools protocol (stdlib websocket client).
# On this machine the policy-managed Chrome hangs in --screenshot/--dump-dom mode,
# but its DevTools endpoint works, so the page is loaded, measured and captured there.
CHROME_FLAGS = ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                "--window-size=1024,1024", "--no-sandbox", "--no-first-run", "--no-default-browser-check",
                "--disable-dev-shm-usage", "--remote-debugging-port=0", "--remote-allow-origins=*"]


class WS:
    def __init__(self, url):
        import base64
        import socket
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)", url)
        self.s = socket.create_connection((m.group(1), int(m.group(2))), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET {m.group(3)} HTTP/1.1\r\nHost: {m.group(1)}:{m.group(2)}\r\nUpgrade: websocket\r\n"
                        f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise RuntimeError("websocket handshake failed")
            buf += chunk
        head, self.buf = buf.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise RuntimeError("websocket handshake refused: " + head.decode(errors="replace"))
        self.next_id = 0

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(1 << 20)
            if not chunk:
                raise RuntimeError("websocket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, method, params=None):
        import struct
        self.next_id += 1
        data = json.dumps({"id": self.next_id, "method": method, "params": params or {}}).encode()
        n = len(data)
        hdr = bytes([0x81])
        if n < 126:
            hdr += bytes([0x80 | n])
        elif n < 65536:
            hdr += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            hdr += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        self.s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))
        return self.next_id

    def recv(self):
        import struct
        msg = b""
        while True:
            b0, b1 = self._read(2)
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            payload = self._read(n)
            op = b0 & 0x0F
            if op in (0, 1, 2):
                msg += payload
                if b0 & 0x80:
                    return json.loads(msg)
            elif op == 8:
                raise RuntimeError("websocket closed by chrome")

    def call(self, method, params=None):
        i = self.send(method, params)
        while True:
            m = self.recv()
            if m.get("id") == i:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})

    def wait_event(self, name):
        while True:
            m = self.recv()
            if m.get("method") == name:
                return m


def chrome_render(html_path):
    """Load the page once; return (layout report dict, raw screenshot PNG bytes)."""
    import base64
    import http.client
    import time
    prof = tempfile.mkdtemp(prefix="chr-", dir="/tmp")
    proc = subprocess.Popen(["google-chrome"] + CHROME_FLAGS + [f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        port_file = os.path.join(prof, "DevToolsActivePort")
        t0 = time.time()
        while not (os.path.exists(port_file) and open(port_file).read().strip()):
            if time.time() - t0 > 30 or proc.poll() is not None:
                raise SystemExit("chrome did not start its DevTools endpoint")
            time.sleep(0.1)
        port = int(open(port_file).read().split()[0])
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
        conn.request("PUT", "/json/new?about:blank")
        target = json.loads(conn.getresponse().read())
        ws = WS(target["webSocketDebuggerUrl"])
        ws.call("Emulation.setDeviceMetricsOverride",
                {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False})
        ws.call("Emulation.setScrollbarsHidden", {"hidden": True})
        ws.call("Page.enable")
        ws.send("Page.navigate", {"url": "file://" + html_path})
        ws.wait_event("Page.loadEventFired")
        r = ws.call("Runtime.evaluate", {
            "expression": "document.fonts.ready.then(function(){return new Promise(function(res){"
                          "requestAnimationFrame(function(){requestAnimationFrame(function(){"
                          "res(document.getElementById('report').textContent);});});});})",
            "awaitPromise": True, "returnByValue": True})
        report = json.loads(r["result"]["value"])
        shot = ws.call("Page.captureScreenshot", {
            "format": "png", "captureBeyondViewport": False,
            "clip": {"x": 0, "y": 0, "width": W, "height": H, "scale": 1}})
        return report, base64.b64decode(shot["data"])
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        shutil.rmtree(prof, ignore_errors=True)


def render_png(html_path, png_path):
    import io
    report, raw = chrome_render(html_path)
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if im.size != (W, H):
        raise SystemExit(f"screenshot is {im.size}, expected {W}x{H}")
    q = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q.save(png_path, format="PNG", optimize=True)
    return report


def main():
    data_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data", "stories.json"))
    out_dir = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else HERE)
    os.makedirs(out_dir, exist_ok=True)
    with open(data_path, encoding="utf-8") as f:
        d = json.load(f)
    page = build_html(d)
    html_path = os.path.join(out_dir, "render.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)

    final = os.path.join(out_dir, "entry.png")
    a, b = final + ".a.png", final + ".b.png"
    rep = render_png(html_path, a)
    render_png(html_path, b)
    ok = True
    for f_, loaded in rep["fonts"].items():
        if not loaded:
            print(f"ERROR: font not available: {f_}")
            ok = False
    for s in rep["small"]:
        print("ERROR: text under 11px:", s)
        ok = False
    for s in rep["overflow"]:
        print("WARNING: content overflows its box:", s)
    for s in rep["briefs"]:
        print("ERROR: brief text overflows its column:", s)
        ok = False
    for s in rep["bbox"]:
        print("ERROR: brief box not inside its column:", s)
        ok = False
    for s in rep["warn"]:
        print("WARNING:", s)
    if rep["dclines"] != 2:
        print(f"ERROR: date-check band is {rep['dclines']} lines, expected 2")
        ok = False
    with open(a, "rb") as fa, open(b, "rb") as fb:
        ba, bb = fa.read(), fb.read()
    os.remove(b)
    if ba != bb:
        os.remove(a)
        raise SystemExit("ERROR: two renders differ; output is not deterministic")
    os.replace(a, final)
    with Image.open(final) as im:
        size = im.size
    nbytes = os.path.getsize(final)
    if size != (W, H) or nbytes > 1048576:
        raise SystemExit(f"ERROR: entry.png is {size} / {nbytes} bytes")
    print(f"wrote {final}: {size[0]}x{size[1]}, {nbytes} bytes, renders identical")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
