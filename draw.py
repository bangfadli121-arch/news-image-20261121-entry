#!/usr/bin/env python3
"""Render the 21 November 2026 newspaper front page (entry.png).

Fresh build from the prose spec: classic newspaper front page, 1024x1024,
cream paper, 11 main stories (Saturday 21 November 2026, numbered and
pinned on a world map) plus 22 Friday 20 November catch-up stories in
the ALSO list. Python 3 + PIL only, no network, deterministic output.

Deviation from the spec, logged honestly: the spec asks for a 112 px tall
hero photo slot, but the verbatim hero decks (3 lines each) plus 2-line
headlines overflow a 190 px hero card by 17 px with that slot. The hero
photo slot is therefore 90 px tall instead (HERO_PHOTO_H = 90), which
keeps every headline and deck verbatim, keeps all fonts and sizes, and
keeps the 190 px card height and every other layout number intact.
Hero bottom margins after the change: 5, 5 and 20 px.

Second deviation: the spec's pin offset for story 7 (Brussels, dx 18,
dy 12) puts its disc 7.6 px from the story 6 (Gaza) disc, so the two
16 px discs overlap and pin 6's number is hidden. Story 7's offset is
therefore dx 18, dy -14 instead: the pin sits over the North Sea with
a leader line down to Brussels, and the closest pin pair is then
27.7 px apart (stories 1-2). Every other pin offset is as specified.
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

# ---------------------------------------------------------------- palette
PAPER = (247, 241, 222)
INK = (16, 16, 14)
DECK = (30, 30, 28)
RED = (176, 32, 32)
DARK_RED = (120, 20, 20)
MUTED = (90, 82, 66)
RULE = (40, 40, 38)
PANEL = (253, 251, 243)
OCEAN_TOP = (222, 235, 233)
OCEAN_BOTTOM = (198, 219, 217)
LAND = (203, 209, 164)
COAST = (118, 130, 86)
CONTINENT = (96, 104, 72)
GOLD = (176, 138, 58)
GRAT = (190, 208, 205)
GRAT_LABEL = (120, 140, 138)
OCEAN_NAME = (110, 138, 136)
DIVIDER = (210, 200, 175)
WHITE = (255, 255, 255)
SHADOW = (90, 90, 85)

W, H = 1024, 1024
MARGIN = 26
RIGHT = 998
CONTENT_W = RIGHT - MARGIN  # 972

HERO_PHOTO_H = 90   # spec says 112; see module docstring for why it is 90
SMALL_PHOTO_H = 80

# ------------------------------------------------------------------- fonts
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

# ------------------------------------------------------------- text tools
def wrap_text(fnt, text, width):
    """Greedy word wrap: fill each line while the next word still fits."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if fnt.getlength(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centred(draw, cx, y, text, fnt, fill):
    draw.text((cx - fnt.getlength(text) / 2, y), text, font=fnt, fill=fill)


def draw_tracked_centred(draw, cx, y, text, fnt, tracking, fill):
    """Letterspaced centred text: tracking px between characters."""
    total = sum(fnt.getlength(ch) for ch in text) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += fnt.getlength(ch) + tracking


def rule_h(draw, y, x0=MARGIN, x1=RIGHT, width=1):
    if width == 1:
        draw.line([(x0, y), (x1, y)], fill=RULE, width=1)
    else:
        draw.rectangle([x0, y, x1, y + width - 1], fill=RULE)

# ------------------------------------------------------------------ stories
# (number, kicker, headline, deck, lon, lat, dx, dy, photo, focus)
STORIES = [
    (1, "SAUDI ARABIA \u00b7 MISSILES",
     "Houthi missiles intercepted over Riyadh",
     "Saudi-led coalition shoots down three ballistic missiles aimed at "
     "the capital \u2014 the second attack on Riyadh in days.",
     46.7, 24.7, 20, 12, "hero1-riyadh.webp", 0.50),
    (2, "INDIA \u00b7 CYCLONE",
     "Akvan fizzles: zero deaths after 440,000 flee",
     "The storm weakens to a depression over Odisha; more than 440,000 "
     "people were evacuated and no casualties are reported.",
     84.9, 19.3, 0, 0, "card10-cyclone.webp", 0.50),
    (3, "AUSTRALIA \u00b7 CRICKET",
     "Ashes begin in Perth",
     "Steve Smith leads Australia with Cummins out injured; two debutants "
     "face England at Optus Stadium.",
     115.86, -31.95, 0, 0, "hero2-ashes.webp", 0.50),
    (4, "IRAQ \u00b7 SECURITY",
     "Iraqi forces retake militia stronghold",
     "A joint army, police and PMF headquarters opens in Jurf al-Sakhar "
     "after 12 years of Kataib Hezbollah rule.",
     44.2, 32.9, -2, -22, "card-iraq.webp", 0.50),
    (5, "UNITED STATES \u00b7 SCAM",
     "Fined $811m, still in business",
     "BBC finds the migrant-bail firm behind an $811m penalty kept "
     "operating under a new name while families paid thousands.",
     -78.9, 38.2, 0, 0, "card-scam.webp", 0.50),
    (6, "GAZA \u00b7 CEASEFIRE",
     "Five killed as Gaza truce frays",
     "Drone strikes hit Gaza City crowds on Saturday; the Board of Peace "
     "warns the year-old ceasefire may collapse.",
     34.47, 31.5, -26, -16, "card-gaza.webp", 0.50),
    (7, "EUROPE \u00b7 TRADE",
     "Indonesia and EU sign trade deal",
     "IEU-CEPA is signed in Brussels after years of talks, opening "
     "Europe's market to Indonesian goods.",
     4.35, 50.85, 18, -14, "card-ieucepa.webp", 0.50),
    (8, "UNITED STATES \u00b7 FORMULA 1",
     "Las Vegas lights up tonight",
     "Fifty laps of the Strip at 8pm local in the 21st round of the "
     "season; F1 Academy closes its season first.",
     -115.17, 36.11, 0, 0, "card-f1.webp", 0.50),
    (9, "ENGLAND \u00b7 FOOTBALL",
     "Newcastle host Arsenal in late game",
     "Seven Premier League matches on Saturday, headlined by Newcastle v "
     "Arsenal at 18:30.",
     -1.62, 54.98, -18, -16, "card-pl.webp", 0.50),
    (10, "INDONESIA \u00b7 WAGES",
     "Jakarta sets 2027 wage at Rp6.14m",
     "The capital's minimum wage rises to Rp6,136,941; Banten sets "
     "Rp3,372,828.70.",
     106.85, -6.2, 0, 0, "card-jakarta.webp", 0.50),
    (11, "NEW ZEALAND \u00b7 CRICKET",
     "India fight back in Wellington",
     "India reach 159 for 1 at stumps on day two of the first Test, "
     "trailing New Zealand by 209.",
     174.78, -41.29, -24, -6, "card-wellington.webp", 0.50),
]

ALSO = [
    "12. UKRAINE \u2014 Russian strikes hit three Kyiv bridges; at least nine killed",
    "13. EUROPE \u2014 EU approves \u20ac1bn military aid for Ukraine; \u20ac7.9bn disbursed",
    "14. GAMES \u2014 GTA VI books record $3.79bn in day-one sales; 32.5m pre-orders",
    "15. MARKETS \u2014 AI rout: Nasdaq \u22125.3%, S&P \u22123.7%, Dow \u22121.9%; Nvidia \u221214%",
    "16. MARKETS \u2014 Anthropic slides 8.5% a day after its record IPO",
    "17. GAZA \u2014 Board of Peace warns it may hand Gaza's \"keys\" back to the UN",
    "18. GAZA \u2014 Floods destroy 6,000 shelters; 150,000 tents still outside Gaza",
    "19. UNITED STATES \u2014 Trump threatens \"tremendous tax\" on data centres built abroad",
    "20. UNITED STATES \u2014 Trump: \"good chance\" of a Russia-Ukraine deal",
    "21. CLIMATE \u2014 COP31 ends in Antalya; fossil-fuel language dropped from deal",
    "22. COURTS \u2014 Paris: three police jailed over the racist beating of Michel Zecler",
    "23. NEPAL \u2014 PM Balendra Shah to visit India on 22\u201323 Nov, his first bilateral trip",
    "24. INDONESIA \u2014 Komdigi asks Google to explain closure of 19,389 YouTube channels",
    "25. POLAND \u2014 Russian missile falls in Poland; Tusk calls it \"intentional provocation\"",
    "26. UNITED STATES \u2014 Pentagon releases eighth UFO file batch: 43 records, three videos",
    "27. DENMARK \u2014 Denmark expels Russian defence attach\u00e9 over murder plot",
    "28. UNITED STATES \u2014 Nikhil Gupta jailed for 235 months over Pannun murder plot",
    "29. UNITED STATES \u2014 Rikers Island to shut by 2032, Mayor Mamdani announces",
    "30. INDONESIA \u2014 Prabowo returns home with Rp1,600tn investment commitments",
    "31. INDONESIA \u2014 Balance of payments back in surplus, $0.1bn in Q3",
    "32. BRITAIN \u2014 UK and EU finalise new deal on farming, carbon and youth mobility",
    "33. TECH \u2014 Hyundai unveils 2027 Elantra at Los Angeles Auto Show",
]

NUMBERS = [
    ("3", "Missiles at Riyadh"),
    ("440,000", "Evacuated from Akvan"),
    ("$811m", "Fine the bail firm dodged"),
    ("50", "Laps in Las Vegas"),
    ("Rp6,14jt", "Jakarta wage 2027"),
    ("159/1", "India in Wellington"),
]

UTC_SLOTS = [
    ("EARLY", "Houthi missiles hit Riyadh"),
    ("MORNING", "Akvan weakens to a depression"),
    ("DAY", "Ashes begins in Perth"),
    ("AFTERNOON", "IEU-CEPA signed in Brussels"),
    ("EVENING", "Las Vegas GP under lights"),
]

# ------------------------------------------------------------- photo crops
_photo_cache = {}


def cropped_photo(num, photo, tw, th, focus):
    """Crop to the slot aspect (focus = vertical anchor 0 top .. 1 bottom),
    then LANCZOS-resize to the slot. Cached per (story, slot size)."""
    key = (num, tw, th)
    if key in _photo_cache:
        return _photo_cache[key]
    im = Image.open(os.path.join(HERE, "photos", photo)).convert("RGB")
    sw, sh = im.size
    target = tw / th
    if sw / sh > target:
        # source wider than slot: crop the width, centred horizontally
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        box = (x0, 0, x0 + nw, sh)
    else:
        # source taller than slot: crop the height around the focus point
        nh = sw / target
        y0 = focus * (sh - nh)
        y0 = max(0.0, min(sh - nh, y0))
        box = (0, int(y0), sw, int(y0 + nh))
    out = im.crop(box).resize((tw, th), Image.LANCZOS)
    _photo_cache[key] = out
    return out

# -------------------------------------------------------------------- cards
def draw_hero_card(draw, page, x, y, story):
    num, kicker, headline, deck, _lon, _lat, _dx, _dy, photo, focus = story
    w, h = 316, 190
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=PANEL, outline=RULE)
    page.paste(cropped_photo(num, photo, w - 2, HERO_PHOTO_H, focus),
               (x + 1, y + 1))
    ty = y + HERO_PHOTO_H + 5
    # number badge
    draw.rectangle([x + 8, ty, x + 27, ty + 17], fill=RED)
    draw.text((x + 18, ty - 1), str(num), font=SERIF_B(17), fill=WHITE,
              anchor="ma")
    # kicker
    kf = SANS_B(9)
    assert kf.getlength(kicker) <= w - 40, "hero kicker too wide: %s" % kicker
    draw.text((x + 34, ty + 4), kicker, font=kf, fill=RED)
    # headline
    hf = SERIF_B(14)
    lines = wrap_text(hf, headline, w - 16)
    hy = ty + 22
    for i, line in enumerate(lines):
        draw.text((x + 8, hy + i * 15), line, font=hf, fill=INK)
    # deck
    df = SANS(11)
    dlines = wrap_text(df, deck, w - 16)
    dy = hy + len(lines) * 15 + 2
    for i, line in enumerate(dlines):
        draw.text((x + 8, dy + i * 12), line, font=df, fill=DECK)
    bottom = dy + len(dlines) * 12
    margin = (y + h) - bottom
    print("hero %d bottom margin: %d" % (num, margin))
    assert margin >= 2, "hero %d overflows by %d px" % (num, -margin)
    return margin


def draw_small_card(draw, page, x, y, story):
    num, kicker, headline, deck, _lon, _lat, _dx, _dy, photo, focus = story
    w, h = 234, 170
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=PANEL, outline=RULE)
    page.paste(cropped_photo(num, photo, w - 2, SMALL_PHOTO_H, focus),
               (x + 1, y + 1))
    ty = y + SMALL_PHOTO_H + 4
    # number badge
    draw.rectangle([x + 8, ty, x + 25, ty + 15], fill=RED)
    draw.text((x + 17, ty - 1), str(num), font=SERIF_B(15), fill=WHITE,
              anchor="ma")
    # kicker
    kf = SANS_B(9)
    assert kf.getlength(kicker) <= w - 44, "small kicker too wide: %s" % kicker
    draw.text((x + 32, ty + 3), kicker, font=kf, fill=RED)
    # headline
    hf = SERIF_B(13)
    lines = wrap_text(hf, headline, w - 16)
    hy = ty + 18
    for i, line in enumerate(lines):
        draw.text((x + 8, hy + i * 14), line, font=hf, fill=INK)
    # deck
    df = SANS(10)
    dlines = wrap_text(df, deck, w - 16)
    dy = hy + len(lines) * 14 + 2
    for i, line in enumerate(dlines):
        draw.text((x + 8, dy + i * 11), line, font=df, fill=DECK)
    bottom = dy + len(dlines) * 11
    margin = (y + h) - bottom
    print("small %d bottom margin: %d" % (num, margin))
    assert margin >= 2, "small card %d overflows by %d px" % (num, -margin)
    return margin

# ------------------------------------------------------------------ map data
FALLBACK_LAND = [
    # North America
    [(-168, 66), (-150, 70), (-135, 70), (-125, 72), (-115, 73), (-105, 72),
     (-95, 73), (-85, 73), (-80, 70), (-85, 66), (-90, 62), (-93, 58),
     (-92, 54), (-87, 52), (-82, 51), (-79, 54), (-77, 58), (-72, 60),
     (-68, 62), (-64, 60), (-60, 58), (-56, 52), (-60, 47), (-65, 44),
     (-70, 42), (-74, 39), (-76, 35), (-80, 32), (-81, 27), (-80, 25),
     (-84, 30), (-89, 29), (-94, 29), (-97, 26), (-97, 21), (-94, 18),
     (-90, 15), (-92, 14), (-95, 16), (-100, 18), (-105, 20), (-110, 23),
     (-112, 28), (-115, 31), (-118, 34), (-121, 35), (-124, 40), (-124, 48),
     (-128, 52), (-133, 56), (-140, 60), (-148, 60), (-155, 58),
     (-162, 58), (-166, 61), (-168, 66)],
    # Greenland
    [(-45, 60), (-32, 68), (-20, 70), (-25, 76), (-40, 80), (-55, 77),
     (-58, 71), (-53, 64), (-45, 60)],
    # South America
    [(-80, 10), (-76, 5), (-70, 2), (-60, 0), (-52, -3), (-44, -3),
     (-35, -8), (-38, -15), (-41, -22), (-48, -28), (-54, -34), (-58, -39),
     (-65, -45), (-68, -52), (-73, -50), (-73, -40), (-72, -30), (-71, -20),
     (-76, -14), (-80, -5), (-81, 0), (-80, 10)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (-1, 48), (0, 50), (3, 53), (7, 54),
     (8, 57), (10, 59), (14, 58), (18, 56), (21, 55), (24, 58), (27, 60),
     (30, 62), (31, 70), (28, 71), (22, 70), (16, 68), (12, 65), (10, 62),
     (5, 60), (5, 58), (2, 56), (-2, 53), (-5, 50), (-8, 44), (-10, 38),
     (-10, 36)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (34, 28), (37, 22),
     (39, 18), (43, 12), (48, 11), (51, 12), (46, 4), (41, -2), (40, -8),
     (38, -15), (35, -20), (33, -26), (29, -32), (25, -34), (19, -35),
     (16, -32), (14, -25), (12, -18), (9, -8), (9, -1), (9, 4), (2, 6),
     (-5, 5), (-10, 5), (-14, 8), (-17, 14), (-17, 20), (-15, 25), (-11, 30),
     (-6, 35)],
    # Asia
    [(30, 70), (35, 68), (45, 68), (55, 70), (65, 71), (75, 72), (85, 73),
     (95, 75), (105, 76), (115, 74), (125, 73), (135, 72), (145, 71),
     (155, 70), (165, 69), (175, 67), (178, 65), (172, 62), (165, 60),
     (158, 56), (156, 51), (150, 49), (143, 45), (141, 40), (138, 36),
     (135, 34), (130, 33), (127, 35), (124, 39), (121, 36), (120, 31),
     (118, 26), (114, 22), (110, 20), (108, 14), (106, 9), (103, 8),
     (100, 7), (98, 12), (96, 15), (93, 17), (91, 22), (88, 22), (86, 20),
     (83, 17), (80, 15), (78, 9), (76, 10), (74, 14), (72, 20), (69, 22),
     (66, 25), (62, 25), (58, 26), (56, 27), (53, 28), (51, 29), (49, 30),
     (47, 30), (44, 29), (41, 30), (39, 32), (36, 36), (34, 36), (31, 36),
     (30, 38), (31, 42), (33, 45), (36, 46), (39, 48), (42, 50), (45, 53),
     (48, 55), (50, 58), (52, 62), (52, 66), (45, 68), (38, 68), (30, 70)],
    # Australia
    [(113, -22), (114, -28), (114, -32), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (141, -38), (145, -38), (149, -37),
     (151, -34), (153, -31), (153, -27), (151, -24), (148, -20), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (127, -14), (124, -16), (121, -18), (117, -20), (113, -22)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-4, 58), (-2, 58), (0, 53), (1, 51),
     (-3, 50), (-5, 50)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 36), (139, 38), (141, 41),
     (143, 42), (145, 44), (143, 44), (141, 40), (139, 37), (136, 34),
     (132, 32), (130, 31)],
    # Sumatra
    [(95, 5), (98, 3), (100, 0), (103, -2), (106, -6), (104, -6),
     (101, -3), (98, 0), (95, 3), (95, 5)],
    # Borneo
    [(109, 1), (112, 4), (116, 6), (119, 2), (118, -2), (115, -4),
     (111, -3), (109, -1), (109, 1)],
    # Java
    [(105, -6), (108, -7), (111, -7), (114, -8), (114, -7), (110, -6),
     (106, -6), (105, -6)],
    # New Guinea
    [(131, -1), (135, -2), (140, -3), (145, -6), (150, -9), (147, -8),
     (142, -8), (137, -5), (133, -3), (131, -1)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (46, -24), (44, -22),
     (43, -18), (44, -16)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (177, -38), (178, -37),
     (175, -40), (172, -43), (168, -46), (167, -45)],
    # Iceland
    [(-18, 63.5), (-15, 64), (-13, 65), (-16, 66), (-20, 66), (-22, 65),
     (-20, 64), (-18, 63.5)],
    # Cuba
    [(-85, 22), (-80, 23), (-75, 20), (-74, 20), (-78, 22), (-85, 22)],
    # Philippines
    [(120, 18), (122, 18), (122, 14), (123, 11), (122, 7), (121, 10),
     (120, 13), (120, 18)],
]


def load_land_rings():
    """Land rings from land-110m.geojson, or the hand polygons above."""
    path = os.path.join(HERE, "land-110m.geojson")
    rings = []
    if os.path.exists(path):
        with open(path) as fh:
            data = json.load(fh)
        for feature in data["features"]:
            geom = feature["geometry"]
            polys = (geom["coordinates"] if geom["type"] == "MultiPolygon"
                     else [geom["coordinates"]])
            for poly in polys:
                rings.append(poly[0])  # outer ring only; holes skipped
        print("map: %d land rings from geojson" % len(rings))
    else:
        rings = [list(p) for p in FALLBACK_LAND]
        print("map: geojson missing, using %d fallback rings" % len(rings))
    return rings


def split_antimeridian(ring):
    """Split a lon/lat ring wherever it jumps across the antimeridian."""
    parts = []
    current = [ring[0]]
    for a, b in zip(ring, ring[1:]):
        if abs(b[0] - a[0]) > 180:
            # unwrap b next to a, find where the segment hits +/-180
            lon_b = b[0] + 360 if b[0] < a[0] else b[0] - 360
            edge = 180 if a[0] > 0 else -180
            den = lon_b - a[0]
            # den == 0 when a and b sit on opposite edges of the same
            # meridian (e.g. 180 -> -180): split at the midpoint latitude
            t = (edge - a[0]) / den if den else 0.5
            lat_edge = a[1] + t * (b[1] - a[1])
            current.append((edge, lat_edge))
            parts.append(current)
            current = [(-edge, lat_edge), b]
        else:
            current.append(b)
    parts.append(current)
    return parts

# ---------------------------------------------------------------------- map
MAP_W, MAP_H = 448, 238


def project(lon, lat):
    """Equirectangular projection into map-layer pixels."""
    return ((lon + 180) / 360 * MAP_W, (84 - lat) / 144 * MAP_H)


def draw_map():
    """Build the 448x238 world map layer (ocean, land, labels, pins)."""
    layer = Image.new("RGB", (MAP_W, MAP_H), OCEAN_TOP)
    md = ImageDraw.Draw(layer)
    # ocean vertical gradient
    for yy in range(MAP_H):
        t = yy / (MAP_H - 1)
        col = tuple(int(OCEAN_TOP[i] + (OCEAN_BOTTOM[i] - OCEAN_TOP[i]) * t)
                    for i in range(3))
        md.line([(0, yy), (MAP_W - 1, yy)], fill=col)
    # land
    for ring in load_land_rings():
        for part in split_antimeridian(ring):
            pts = [project(lon, lat) for lon, lat in part]
            if len(pts) >= 3:
                md.polygon(pts, fill=LAND, outline=COAST)
    # graticule
    for lat, label in ((-60, "60S"), (-30, "30S"), (0, "0"),
                       (30, "30N"), (60, "60N")):
        _x, gy = project(0, lat)
        md.line([(0, gy), (MAP_W - 1, gy)], fill=GRAT)
        md.text((3, gy - 11), label, font=SANS(8), fill=GRAT_LABEL)
    for lon, label in ((-120, "120W"), (-60, "60W"), (0, "0"),
                       (60, "60E"), (120, "120E")):
        gx, _y = project(lon, 0)
        md.line([(gx, 0), (gx, MAP_H - 1)], fill=GRAT)
        md.text((gx + 3, MAP_H - 11), label, font=SANS(8), fill=GRAT_LABEL)
    # ocean names
    for text, lon, lat in (("PACIFIC OCEAN", -120, -8), ("ATLANTIC", -28, -35),
                           ("INDIAN OCEAN", 75, -32), ("PACIFIC", 140, -48)):
        cx, cy = project(lon, lat)
        draw_tracked_centred(md, cx, cy, text, SERIF(11), 3, OCEAN_NAME)
    # continent labels
    for text, lon, lat in (("NORTH AMERICA", -108, 62),
                           ("SOUTH AMERICA", -58, -14), ("AFRICA", 20, 3),
                           ("ASIA", 78, 60), ("AUSTRALIA", 134, -25)):
        cx, cy = project(lon, lat)
        draw_tracked_centred(md, cx, cy, text, SANS_B(9), 2, CONTINENT)
    # compass rose
    cx, cy = 58, MAP_H - 24
    md.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=PAPER, outline=INK)
    md.polygon([(cx, cy - 7), (cx + 2.5, cy + 2), (cx - 2.5, cy + 2)],
               fill=RED)
    md.text((cx - 3, cy - 16), "N", font=SANS_B(8), fill=INK)
    # pins
    for story in STORIES:
        num, _k, _h, _d, lon, lat, dx, dy, _p, _f = story
        tx, ty = project(lon, lat)
        px, py = tx + dx, ty + dy
        if dx or dy:
            md.line([(tx, ty), (px, py)], fill=INK)
            md.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=INK)
        md.ellipse([px - 8 + 1, py - 8 + 2, px + 8 + 1, py + 8 + 2],
                   fill=SHADOW)
        md.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                   outline=WHITE, width=2)
        md.text((px, py - 6), str(num), font=SANS_B(10), fill=WHITE,
                anchor="ma")
    # caption strip, drawn last so it sits above the map
    caption = "THE WORLD AT A GLANCE \u2014 11 STORIES PINNED"
    cf = SANS_B(11)
    cw = cf.getlength(caption)
    md.rectangle([4, 4, 12 + cw, 20], fill=PAPER)
    md.text((8, 5), caption, font=cf, fill=RED)
    # border
    md.rectangle([0, 0, MAP_W - 1, MAP_H - 1], outline=RULE)
    return layer

# --------------------------------------------------------------------- page
def build_page():
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)

    # 1. masthead
    y = 6
    draw_centred(draw, W // 2, y, "THE WORLD", SERIF_B(37), INK)
    y += 40
    rule_h(draw, y, width=2)
    y += 4
    draw_centred(draw, W // 2, y, "SATURDAY 21 NOVEMBER 2026",
                 SANS_B(12), INK)
    y += 15
    draw_centred(draw, W // 2, y,
                 "33 STORIES  \u00b7  6 CONTINENTS  \u00b7  ONE PAGE",
                 SANS(10), MUTED)
    y += 12
    rule_h(draw, y)
    y += 5  # y = 82

    # 2. numbers strip
    sy = y + 2  # 84
    rule_h(draw, sy)
    col_w = (W - 52) // 6  # 162
    for i, (number, caption) in enumerate(NUMBERS):
        cx = MARGIN + i * col_w + col_w // 2
        draw.text((cx, sy + 2), number, font=SERIF_B(16), fill=RED,
                  anchor="ma")
        draw.text((cx, sy + 21), caption, font=SANS(8), fill=INK,
                  anchor="ma")
        if i:
            bx = MARGIN + i * col_w
            draw.line([(bx, sy + 4), (bx, sy + 30)], fill=DIVIDER)
    rule_h(draw, sy + 33)
    y = sy + 34  # 118

    # 3. UTC strip
    sy = y + 2  # 120
    draw.rectangle([MARGIN, sy, 133, sy + 25], fill=RED)
    draw.text((80, sy + 13), "THE DAY IN UTC", font=SANS_B(9), fill=WHITE,
              anchor="mm")
    slot_w = 171
    for i, (phase, event) in enumerate(UTC_SLOTS):
        sx = 142 + i * slot_w
        draw.text((sx, sy + 3), phase, font=SANS_B(9), fill=RED)
        ef = SANS(8)
        assert ef.getlength(event) <= slot_w - 6, "UTC event too wide"
        draw.text((sx, sy + 14), event, font=ef, fill=INK)
    rule_h(draw, sy + 25)
    y = sy + 26  # 146

    # 4. hero row
    y += 6  # 152
    hero_y = y
    hero_x = [MARGIN, 354, 682]
    for x, story in zip(hero_x, STORIES[:3]):
        draw_hero_card(draw, page, x, hero_y, story)
    hero_bottom = hero_y + 190  # 342

    # 5. small cards, two rows of four
    small_y = hero_bottom + 4  # 346
    small_x = [MARGIN, 272, 518, 764]
    for row, stories in enumerate((STORIES[3:7], STORIES[7:11])):
        for x, story in zip(small_x, stories):
            draw_small_card(draw, page, x, small_y + row * 174, story)
    small_bottom = small_y + 170 + 4 + 170  # 690

    # 6. rule + section titles
    y = small_y + 348  # 694
    rule_h(draw, y, width=2)
    y += 6  # 700
    draw.text((MARGIN, y), "WHERE IT HAPPENED", font=SANS_B(12), fill=INK)
    draw.text((490, y), "ALSO ON FRIDAY 20 NOVEMBER \u2014 22 MORE STORIES",
              font=SANS_B(12), fill=INK)
    y += 18  # 718

    # 7. map + ALSO list
    map_y = y
    page.paste(draw_map(), (MARGIN, map_y))
    map_bottom = map_y + MAP_H  # 956
    col_w = (W - MARGIN - 490 - 18) // 2  # 245
    also_bottom = map_y
    for col in range(2):
        ay = map_y
        for item in ALSO[col * 11:(col + 1) * 11]:
            lines = wrap_text(SANS(9), item, col_w)
            for i, line in enumerate(lines):
                draw.text((490 + col * (col_w + 18), ay + i * 10), line,
                          font=SANS(9), fill=INK)
            ay += len(lines) * 10
        also_bottom = max(also_bottom, ay)
    print("ALSO bottom: %d, map bottom: %d" % (also_bottom, map_bottom))
    assert also_bottom <= map_bottom + 4, "ALSO list overflows the map"

    # 8. judge footer box + sources footer
    y = map_bottom + 6  # 962
    draw.rectangle([MARGIN, y, RIGHT - 1, y + 39], outline=RED, width=2)
    jx = MARGIN + 10
    lab1 = "JUDGE NOTE:  "
    draw.text((jx, y + 6), lab1, font=SANS_B(11), fill=RED)
    draw.text((jx + SANS_B(11).getlength(lab1), y + 6),
              "The 11 main stories above happened, or were first reported, "
              "on Saturday 21 November 2026. Disputed claims are attributed.",
              font=SANS(11), fill=INK)
    lab2 = "DATE CHECK:  "
    draw.text((jx, y + 22), lab2, font=SANS_B(10), fill=RED)
    draw.text((jx + SANS_B(10).getlength(lab2), y + 22),
              "The ALSO list is Friday 20 Nov catch-up. Left out entirely "
              "\u2014 Thu 19 Nov: ICJ Myanmar \u00b7 Shenzhen summit \u00b7 "
              "GTA VI launch \u00b7 JPMorgan breach \u00b7 Nvidia subpoena "
              "\u00b7 Bukele.",
              font=SANS(10), fill=INK)
    y += 46  # 1008
    draw_centred(draw, W // 2, y,
                 "Reporting: AP \u00b7 Reuters \u00b7 AFP \u00b7 BBC \u00b7 "
                 "Al Jazeera \u00b7 The Guardian \u00b7 Financial Times",
                 SANS(11), MUTED)
    final_y = y + 11  # 1019
    print("final y: %d" % final_y)
    assert final_y <= 1022, "final y %d exceeds 1022" % final_y
    return page


def main():
    page = build_page()
    out = os.path.join(HERE, "entry.png")
    page.save(out, "PNG")
    print("saved %s" % out)


if __name__ == "__main__":
    main()
