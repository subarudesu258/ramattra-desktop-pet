"""Pixel-art definitions for the Ramattra desktop pet.

Everything is authored at 1:1 with integer-only primitives (Pillow's draw calls
are aliased, so edges stay perfectly crisp) and scaled NEAREST at build time.
The palette is deliberately dark: near-black violet cloth, gunmetal plating,
brass trim and violet energy — with the Nemesis form swapping in a hot red core.

Frames are baked into PNGs by ``tools/gen_sprites.py``, so the shipped app
needs nothing but the standard library.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# palette
# ---------------------------------------------------------------------------

TRANSPARENT = (255, 0, 254)  # colour-key magenta; never used by the art

PALETTE = {
    "k": (6, 5, 10),          # outline
    "r": (20, 16, 29),        # cloth, shadow
    "R": (33, 27, 45),        # cloth, mid
    "L": (48, 39, 65),        # cloth, lit
    "m": (48, 45, 60),        # steel, shadow
    "M": (78, 74, 96),        # steel, mid
    "N": (112, 108, 134),     # steel, light
    "b": (122, 92, 56),       # brass, shadow
    "B": (178, 140, 84),      # brass, light
    "v": (84, 42, 160),       # violet, deep
    "V": (132, 80, 232),      # violet, mid
    "w": (180, 140, 255),     # violet, glow
    "e": (230, 212, 255),     # violet, core
    "o": (104, 16, 28),       # red, deep
    "O": (192, 40, 46),       # red, mid
    "F": (255, 106, 82),      # red, glow
    "y": (255, 214, 138),     # red, core
    "x": (21, 18, 30),        # face recess
    # -- special form: ivory / tan / deep violet --------------------------
    "i": (196, 184, 160),     # ivory, shadow
    "I": (232, 222, 200),     # ivory, mid
    "W": (250, 246, 236),     # ivory, light
    "t": (108, 82, 46),       # tan, shadow
    "T": (168, 132, 82),      # tan, mid
    "U": (208, 172, 116),     # tan, light
    "h": (20, 18, 26),        # mane, deep
    "H": (40, 36, 50),        # mane, mid
    "q": (68, 28, 132),       # violet, deep (special)
    "Q": (138, 82, 236),      # violet, glow (special)
}


def _shade(rgb: tuple[int, int, int], glow: float) -> tuple[int, int, int]:
    if glow >= 0.999:
        return rgb
    f = 0.45 + 0.55 * max(0.0, min(1.0, glow))
    return tuple(int(c * f) for c in rgb)


def new_canvas(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (w, h), TRANSPARENT)
    return img, ImageDraw.Draw(img)


def poly(d: ImageDraw.ImageDraw, pts, fill, outline=(6, 5, 10)) -> None:
    d.polygon(pts, fill=fill, outline=outline)


# ---------------------------------------------------------------------------
# Omnic form — staff, robe, violet visor
# ---------------------------------------------------------------------------

OMNIC_W, OMNIC_H = 58, 76


def draw_omnic(glow: float = 1.0, bob: int = 0, eye_off: bool = False, cast: int = 0) -> Image.Image:
    img, d = new_canvas(OMNIC_W, OMNIC_H)
    p = PALETTE
    P = lambda k: _shade(p[k], glow)  # noqa: E731
    y = bob
    C = 30

    # ---- staff -----------------------------------------------------------
    sx = 12
    d.rectangle((sx - 1, 14 + y, sx + 2, 73), fill=p["k"])
    d.rectangle((sx, 14 + y, sx + 1, 72), fill=p["b"])
    d.line((sx, 16 + y, sx, 71), fill=p["B"])
    # prongs
    d.line((sx, 14 + y, sx - 3, 10 + y), fill=p["k"])
    d.line((sx + 1, 14 + y, sx + 4, 10 + y), fill=p["k"])
    d.line((sx, 14 + y, sx - 2, 11 + y), fill=p["B"])
    d.line((sx + 1, 14 + y, sx + 3, 11 + y), fill=p["B"])
    # orb
    ox, oy, orad = sx, 10 + y, 5
    d.ellipse((ox - orad, oy - orad, ox + orad, oy + orad), fill=p["k"])
    d.ellipse((ox - orad + 1, oy - orad + 1, ox + orad - 1, oy + orad - 1), fill=P("v"))
    d.ellipse((ox - orad + 2, oy - orad + 2, ox + orad - 2, oy + orad - 2), fill=P("V"))
    d.ellipse((ox - 2, oy - 2, ox + 2, oy + 2), fill=P("w"))
    if glow > 0.9:
        d.point((ox - 1, oy - 1), fill=P("e"))
    if cast:
        rad = orad + 2 + cast * 2
        d.ellipse((ox - rad, oy - rad, ox + rad, oy + rad), outline=P("V"))
        d.ellipse((ox - rad + 1, oy - rad + 1, ox + rad - 1, oy + rad - 1), outline=P("v"))
        for dx, dy in ((rad + 1, 0), (-rad - 1, 0), (0, rad + 1), (0, -rad - 1)):
            d.point((ox + dx, oy + dy), fill=P("w"))

    # ---- robe ------------------------------------------------------------
    robe = [(C - 8, 44 + y), (C + 8, 44 + y), (C + 12, 57 + y), (C + 15, 73),
            (C - 15, 73), (C - 12, 57 + y)]
    poly(d, robe, p["R"])
    d.polygon([(C - 8, 45 + y), (C - 2, 45 + y), (C - 4, 72), (C - 14, 72)], fill=p["L"])
    d.polygon([(C + 4, 45 + y), (C + 8, 45 + y), (C + 11, 57 + y), (C + 13, 72), (C + 4, 72)], fill=p["r"])
    for fx in (C - 11, C - 6, C + 6, C + 11):
        d.line((fx, 52 + y, fx + (-1 if fx < C else 1), 71), fill=p["r"])
    # sash
    d.rectangle((C - 3, 44 + y, C + 3, 73), fill=p["k"])
    d.rectangle((C - 2, 45 + y, C + 2, 72), fill=P("v"))
    d.rectangle((C - 1, 45 + y, C + 1, 72), fill=P("V"))
    d.line((C, 45 + y, C, 72), fill=P("w"))
    # hem
    d.rectangle((C - 15, 71, C + 15, 73), fill=p["k"])
    d.line((C - 14, 71, C + 14, 71), fill=p["B"])
    for hx in range(C - 12, C + 13, 4):
        d.point((hx, 70), fill=P("v"))

    # ---- shoulders (drawn before the torso so they tuck in) --------------
    for side in (-1, 1):
        x = C + side * 8
        poly(d, [(x, 27 + y), (x + side * 10, 29 + y), (x + side * 12, 38 + y), (x + side * 1, 37 + y)], p["M"])
        d.polygon(
            [(x + side * 2, 28 + y), (x + side * 9, 30 + y), (x + side * 9, 33 + y), (x + side * 2, 32 + y)],
            fill=p["N"] if side < 0 else p["m"],
        )

    # ---- torso -----------------------------------------------------------
    poly(d, [(C - 9, 28 + y), (C + 9, 28 + y), (C + 8, 46 + y), (C - 8, 46 + y)], p["M"])
    d.polygon([(C - 7, 30 + y), (C - 1, 30 + y), (C - 2, 45 + y), (C - 6, 45 + y)], fill=p["N"])
    d.polygon([(C + 4, 30 + y), (C + 7, 30 + y), (C + 6, 45 + y), (C + 3, 45 + y)], fill=p["m"])
    d.rectangle((C - 8, 42 + y, C + 8, 45 + y), fill=p["k"])
    d.rectangle((C - 6, 43 + y, C + 6, 44 + y), fill=p["b"])
    d.polygon([(C, 31 + y), (C + 4, 35 + y), (C, 39 + y), (C - 4, 35 + y)], fill=p["k"])
    d.polygon([(C, 32 + y), (C + 3, 35 + y), (C, 38 + y), (C - 3, 35 + y)], fill=P("v"))
    d.polygon([(C, 34 + y), (C + 1, 35 + y), (C, 36 + y), (C - 1, 35 + y)], fill=P("e"))

    # ---- arms ------------------------------------------------------------
    # screen-left arm reaches down to grip the staff
    poly(d, [(C - 19, 33 + y), (C - 11, 32 + y), (C - 11, 43 + y), (C - 19, 44 + y)], p["M"])
    d.line((C - 18, 34 + y, C - 18, 42 + y), fill=p["N"])
    poly(d, [(C - 20, 42 + y), (C - 10, 41 + y), (C - 10, 47 + y), (C - 20, 48 + y)], p["m"])
    d.line((C - 19, 45 + y, C - 11, 45 + y), fill=P("v"))
    # screen-right arm hangs
    poly(d, [(C + 11, 32 + y), (C + 19, 33 + y), (C + 19, 46 + y), (C + 11, 45 + y)], p["m"])
    d.line((C + 15, 34 + y, C + 15, 44 + y), fill=p["M"])
    poly(d, [(C + 11, 45 + y), (C + 20, 46 + y), (C + 20, 52 + y), (C + 11, 51 + y)], p["m"])
    d.line((C + 12, 47 + y, C + 19, 48 + y), fill=P("v"))
    # gripping hand wraps the shaft so the staff reads as held, not floating
    poly(d, [(sx - 4, 43 + y), (sx + 6, 43 + y), (sx + 6, 49 + y), (sx - 4, 49 + y)], p["M"])
    d.line((sx - 3, 44 + y, sx - 3, 48 + y), fill=p["N"])
    d.line((sx - 3, 46 + y, sx + 5, 46 + y), fill=p["m"])

    # ---- collar ----------------------------------------------------------
    poly(d, [(C - 12, 23 + y), (C + 12, 23 + y), (C + 9, 29 + y), (C - 9, 29 + y)], p["b"])
    d.polygon([(C - 10, 24 + y), (C + 10, 24 + y), (C + 9, 26 + y), (C - 9, 26 + y)], fill=p["B"])
    for tip in (-1, 1):
        d.polygon([(C + tip * 12, 23 + y), (C + tip * 15, 21 + y), (C + tip * 11, 26 + y)], fill=p["b"], outline=p["k"])

    # ---- head ------------------------------------------------------------
    head = [(C - 8, 6 + y), (C + 8, 6 + y), (C + 9, 10 + y), (C + 9, 21 + y),
            (C + 6, 24 + y), (C - 6, 24 + y), (C - 9, 21 + y), (C - 9, 10 + y)]
    poly(d, head, p["M"])
    d.polygon([(C - 7, 7 + y), (C + 7, 7 + y), (C + 8, 9 + y), (C + 1, 10 + y), (C - 8, 9 + y)], fill=p["N"])
    # crest fin
    poly(d, [(C - 3, 6 + y), (C + 3, 6 + y), (C + 2, 1 + y), (C - 2, 1 + y)], p["M"])
    d.line((C, 2 + y, C, 6 + y), fill=p["N"])
    # face recess
    d.rounded_rectangle((C - 7, 10 + y, C + 7, 22 + y), radius=3, fill=p["x"])
    d.line((C - 7, 11 + y, C + 7, 11 + y), fill=p["m"])

    # visor: one narrow band, brighter cores in the middle
    if eye_off:
        d.rectangle((C - 6, 14 + y, C + 6, 15 + y), fill=(17, 14, 23))
        d.line((C - 6, 16 + y, C + 6, 16 + y), fill=p["k"])
    else:
        d.rectangle((C - 6, 13 + y, C + 6, 15 + y), fill=p["k"])
        d.rectangle((C - 5, 14 + y, C + 5, 14 + y), fill=P("V"))
        d.line((C - 4, 14 + y, C + 4, 14 + y), fill=P("w"))
        d.point((C - 2, 14 + y), fill=P("e"))
        d.point((C + 2, 14 + y), fill=P("e"))
        d.line((C - 4, 16 + y, C + 4, 16 + y), fill=P("v"))
    # mouth vent: a single dark slot, not a row of teeth
    d.rectangle((C - 5, 18 + y, C + 5, 20 + y), fill=(14, 12, 19))
    d.line((C - 4, 19 + y, C + 4, 19 + y), fill=p["m"])
    # side vents
    for side in (-1, 1):
        d.line((C + side * 8, 12 + y, C + side * 7, 22 + y), fill=p["N"])

    return img


# ---------------------------------------------------------------------------
# Nemesis form — bulk, spikes, red core
# ---------------------------------------------------------------------------

NEMESIS_W, NEMESIS_H = 76, 78


def draw_nemesis(glow: float = 1.0, bob: int = 0, eye_off: bool = False, roar: int = 0) -> Image.Image:
    img, d = new_canvas(NEMESIS_W, NEMESIS_H)
    p = PALETTE
    P = lambda k: _shade(p[k], glow)  # noqa: E731
    y = bob
    C = 38

    # ---- legs ------------------------------------------------------------
    for lx in (C - 9, C + 1):
        poly(d, [(lx, 56), (lx + 8, 56), (lx + 9, 74), (lx - 1, 74)], p["r"])
        d.line((lx + 2, 58, lx + 2, 73), fill=p["L"])
        d.rectangle((lx - 2, 72, lx + 10, 74), fill=p["k"])
        d.line((lx - 1, 72, lx + 9, 72), fill=p["b"])

    # ---- torso -----------------------------------------------------------
    poly(d, [(C - 13, 30 + y), (C + 13, 30 + y), (C + 14, 58 + y), (C - 14, 58 + y)], p["R"])
    d.polygon([(C - 11, 31 + y), (C + 1, 31 + y), (C + 1, 57 + y), (C - 12, 57 + y)], fill=p["L"])
    d.polygon([(C + 6, 31 + y), (C + 11, 31 + y), (C + 12, 57 + y), (C + 7, 57 + y)], fill=p["r"])
    # chest plate
    poly(d, [(C - 7, 32 + y), (C + 7, 32 + y), (C + 5, 46 + y), (C - 5, 46 + y)], p["m"])
    # core
    d.ellipse((C - 4, 35 + y, C + 4, 43 + y), fill=p["k"])
    d.ellipse((C - 3, 36 + y, C + 3, 42 + y), fill=P("o"))
    d.ellipse((C - 2, 37 + y, C + 2, 41 + y), fill=P("F"))
    if glow > 0.9:
        d.point((C, 39 + y), fill=P("y"))
    # glowing cracks
    for pts in (
        [(C - 11, 37), (C - 9, 42), (C - 12, 47), (C - 8, 53)],
        [(C + 10, 34), (C + 12, 39), (C + 10, 44)],
        [(C - 4, 48), (C - 6, 53), (C - 3, 57)],
    ):
        pts = [(px, py + y) for px, py in pts]
        d.line(pts, fill=p["k"], width=3)
        d.line(pts, fill=P("o"), width=1)

    # ---- shoulders -------------------------------------------------------
    for side in (-1, 1):
        inner = C + side * 12
        outer = C + side * 27
        poly(d, [(inner, 27 + y), (outer, 31 + y), (outer - side * 1, 46 + y), (inner, 43 + y)], p["m"])
        d.polygon(
            [(inner + side * 3, 29 + y), (outer - side * 3, 32 + y),
             (outer - side * 4, 36 + y), (inner + side * 3, 34 + y)],
            fill=p["N"] if side < 0 else p["M"],
        )
        # chunky armour spikes
        for bx, by, h in ((side * 17, 28, 8), (side * 22, 29, 10), (side * 26, 31, 7)):
            px = C + bx
            tipx = px + side * 2
            poly(d, [(px - 4, by + y), (tipx, by - h + y), (px + 4, by + y)], p["M"])
            d.line((px, by + y, tipx, by - h + 1 + y), fill=p["N"])

    # ---- arms & fists (one continuous silhouette, no elbow gap) ----------
    for side in (-1, 1):
        ax = C + side * 20
        poly(d, [(ax - side * 3, 36 + y), (ax + side * 8, 38 + y),
                 (ax + side * 9, 56 + y), (ax - side * 3, 55 + y)], p["m"])
        d.line((ax + side * 3, 39 + y, ax + side * 3, 54 + y), fill=p["N"])
        # forearm brace
        poly(d, [(ax - side * 3, 48 + y), (ax + side * 9, 49 + y),
                 (ax + side * 9, 57 + y), (ax - side * 3, 56 + y)], p["L"])
        # fist
        fx0, fx1 = sorted((ax - side * 5, ax + side * 11))
        d.rounded_rectangle((fx0, 52 + y, fx1, 71 + y), radius=3, fill=p["M"], outline=p["k"])
        d.line((fx0 + 3, 54 + y, fx0 + 3, 69 + y), fill=p["N"])
        d.rectangle((fx0 + 2, 60 + y, fx1 - 2, 63 + y), fill=p["k"])
        d.rectangle((fx0 + 3, 61 + y, fx1 - 3, 62 + y), fill=P("O"))
        d.line((fx0 + 4, 61 + y, fx1 - 4, 61 + y), fill=P("F"))

    # ---- head ------------------------------------------------------------
    poly(d, [(C - 7, 15 + y), (C + 7, 15 + y), (C + 8, 31 + y), (C - 8, 31 + y)], p["m"])
    d.polygon([(C - 5, 16 + y), (C + 2, 16 + y), (C + 2, 30 + y), (C - 6, 30 + y)], fill=p["N"])
    poly(d, [(C - 6, 20 + y), (C + 6, 20 + y), (C + 5, 26 + y), (C - 5, 26 + y)], p["x"])
    if eye_off:
        d.rectangle((C - 5, 22 + y, C + 5, 24 + y), fill=(20, 17, 24))
    else:
        d.rectangle((C - 5, 22 + y, C + 5, 24 + y), fill=p["k"])
        d.line((C - 4, 23 + y, C + 4, 23 + y), fill=P("F"))
        d.line((C - 3, 24 + y, C + 3, 24 + y), fill=P("O"))
        d.point((C - 2, 23 + y), fill=P("y"))
        d.point((C + 2, 23 + y), fill=P("y"))
    # jaw
    d.rectangle((C - 4, 27 + y, C + 4, 30 + y), fill=p["r"])
    d.line((C - 3, 28 + y, C + 3, 28 + y), fill=p["M"])
    # swept horns
    for side in (-1, 1):
        bx = C + side * 7
        poly(d, [(bx, 18 + y), (bx + side * 5, 14 + y), (bx + side * 1, 22 + y)], p["M"])

    if roar:
        rad = 13 + roar * 4
        d.ellipse((C - rad, 39 + y - rad, C + rad, 39 + y + rad), outline=P("o"))
        d.ellipse((C - rad + 1, 39 + y - rad + 1, C + rad - 1, 39 + y + rad - 1), outline=P("O"))
        for dx, dy in ((rad + 1, 0), (-rad - 1, 0), (0, rad + 1), (0, -rad - 1)):
            d.point((C + dx, 39 + y + dy), fill=P("F"))
    return img


# ---------------------------------------------------------------------------
# Special form — ivory mask with nine red marks, tan armour, two cats
# ---------------------------------------------------------------------------

SPECIAL_W, SPECIAL_H = 96, 88
CAT_W, CAT_H = 17, 15

# Where the cats sit.  ``ramattra_pet/hotspots.py`` mirrors these boxes so the
# app can tell a poke at the cat from a poke at the armour.
CAT_POS = {"left": (17, 21), "right": (63, 19)}


def blit(dst: Image.Image, src: Image.Image, x: int, y: int) -> None:
    sp, dp = src.load(), dst.load()
    for yy in range(src.height):
        for xx in range(src.width):
            pixel = sp[xx, yy]
            if pixel == TRANSPARENT:
                continue
            X, Y = x + xx, y + yy
            if 0 <= X < dst.width and 0 <= Y < dst.height:
                dp[X, Y] = pixel


def draw_cat(kind: str = "left", blink: bool = False) -> Image.Image:
    """Tiny 17x15 shoulder cats.

    left  — hooded one-eyed cat (dark hood, one big eye, eyepatch)
    right — white fox-cat (pointed ears, red forehead marks, two eyes)
    """
    img, d = new_canvas(CAT_W, CAT_H)
    k = PALETTE["k"]

    if kind == "left":
        # hood
        d.polygon([(2, 6), (5, 2), (11, 2), (14, 6), (14, 13), (3, 13)], fill=(56, 48, 80), outline=k)
        d.polygon([(4, 5), (6, 3), (7, 5)], fill=(74, 64, 102), outline=k)
        d.polygon([(12, 5), (10, 3), (9, 5)], fill=(74, 64, 102), outline=k)
        # face
        d.rectangle((5, 7, 12, 13), fill=(232, 220, 196), outline=k)
        # eyepatch strap
        d.polygon([(5, 6), (12, 8), (12, 10), (5, 8)], fill=(32, 28, 44))
        if blink:
            d.rectangle((8, 9, 11, 10), fill=(40, 34, 52))
        else:
            d.ellipse((8, 8, 11, 12), fill=(250, 246, 236), outline=k)
            d.ellipse((9, 9, 11, 11), fill=(30, 26, 40))
            d.point((9, 9), fill=(255, 255, 255))
        d.point((7, 12), fill=(214, 150, 160))
    else:
        # body
        d.polygon([(3, 6), (6, 2), (11, 2), (14, 6), (14, 13), (3, 13)], fill=(248, 244, 232), outline=k)
        # ears with red tips
        d.polygon([(4, 5), (5, 1), (8, 4)], fill=(248, 244, 232), outline=k)
        d.polygon([(13, 5), (12, 1), (9, 4)], fill=(248, 244, 232), outline=k)
        d.point((5, 2), fill=(206, 62, 58))
        d.point((12, 2), fill=(206, 62, 58))
        # red forehead marks
        for mx in (6, 8, 10):
            d.point((mx, 5), fill=(206, 62, 58))
        # eyes
        if blink:
            d.line((5, 9, 7, 9), fill=(40, 34, 52))
            d.line((10, 9, 12, 9), fill=(40, 34, 52))
        else:
            for ex in (5, 10):
                d.ellipse((ex, 7, ex + 2, 10), fill=(60, 70, 110), outline=k)
                d.point((ex + 1, 8), fill=(250, 250, 255))
        d.point((8, 11), fill=(214, 130, 130))
        d.line((7, 12, 9, 12), fill=(150, 120, 110))
    return img


def draw_special(
    glow: float = 1.0,
    bob: int = 0,
    eye_off: bool = False,
    aura: int = 0,
    cat_blink: bool = False,
) -> Image.Image:
    img, d = new_canvas(SPECIAL_W, SPECIAL_H)
    p = PALETTE
    P = lambda k: _shade(p[k], glow)  # noqa: E731
    y = bob
    C = 48

    # ---- mane: black tendrils behind everything --------------------------
    d.polygon(
        [(C - 19, 26), (C - 15, 11), (C + 15, 11), (C + 19, 26),
         (C + 27, 52), (C + 17, 43), (C - 17, 43), (C - 27, 52)],
        fill=p["h"], outline=p["k"],
    )
    for i, sx in enumerate((C - 22, C - 16, C - 9, C + 9, C + 16, C + 22)):
        drop = 8 + (i % 3) * 4
        d.polygon([(sx - 2, 40), (sx + 2, 40), (sx + 1, 44 + drop)], fill=p["h"], outline=p["k"])
    d.polygon([(C - 13, 12), (C + 13, 12), (C + 10, 22), (C - 10, 22)], fill=p["H"])

    # ---- shoulders -------------------------------------------------------
    for side in (-1, 1):
        inner, outer = C + side * 13, C + side * 37
        poly(d, [(inner, 28 + y), (outer, 32 + y), (outer - side * 1, 48 + y), (inner, 46 + y)], p["h"])
        d.polygon(
            [(inner + side * 3, 30 + y), (outer - side * 3, 33 + y),
             (outer - side * 5, 37 + y), (inner + side * 3, 35 + y)],
            fill=p["H"],
        )
        # rim so the black slabs still read on a dark wallpaper
        d.line((inner, 28 + y, outer, 32 + y), fill=(74, 70, 92))
        d.line((outer, 32 + y, outer - side * 1, 48 + y), fill=(58, 54, 74))
        # glowing circuit traces
        d.line((C + side * 24, 33 + y, C + side * 24, 44 + y), fill=P("q"))
        d.line((C + side * 24, 39 + y, C + side * 33, 39 + y), fill=P("q"))
        d.rectangle((C + side * 30 - 1, 38 + y, C + side * 30 + 1, 40 + y), fill=P("Q"))
        d.point((C + side * 24, 38 + y), fill=P("Q"))

    # ---- arms (tan) ------------------------------------------------------
    for side in (-1, 1):
        x0, x1 = C + side * 38, C + side * 24
        poly(d, [(x0, 46 + y), (x1, 44 + y), (x1, 66 + y), (x0, 68 + y)], p["T"])
        d.line((C + side * 35, 47 + y, C + side * 35, 65 + y), fill=p["U"])
        d.line((C + side * 26, 46 + y, C + side * 26, 64 + y), fill=p["t"])
        # violet glyph panel
        gx0, gx1 = sorted((C + side * 28, C + side * 35))
        d.rectangle((gx0, 50 + y, gx1, 61 + y), fill=p["q"], outline=P("Q"))
        d.line((gx0 + 2, 53 + y, gx1 - 2, 58 + y), fill=P("Q"))
        d.point(((gx0 + gx1) // 2, 55 + y), fill=P("w"))
        # fists
        fx0, fx1 = sorted((C + side * 40, C + side * 23))
        d.rounded_rectangle((fx0, 62 + y, fx1, 80 + y), radius=3, fill=p["T"], outline=p["k"])
        d.rectangle((fx0 + 2, 64 + y, fx1 - 2, 68 + y), fill=p["U"])
        for kx in range(fx0 + 4, fx1 - 2, 4):
            d.line((kx, 70 + y, kx, 78 + y), fill=p["t"])

    # ---- torso + tabard --------------------------------------------------
    poly(d, [(C - 12, 32 + y), (C + 12, 32 + y), (C + 11, 74 + y), (C - 11, 74 + y)], p["h"])
    d.polygon([(C - 9, 34 + y), (C - 1, 34 + y), (C - 1, 72 + y), (C - 10, 72 + y)], fill=p["H"])

    tab = [(C - 5, 46 + y), (C + 5, 46 + y), (C + 7, 80 + y), (C, 86 + y), (C - 7, 80 + y)]
    poly(d, tab, p["T"])
    d.line((C - 3, 48 + y, C - 4, 79 + y), fill=p["U"])
    d.line((C + 3, 48 + y, C + 4, 79 + y), fill=p["t"])
    d.line((C - 5, 47 + y, C + 5, 47 + y), fill=p["B"])
    d.line((C - 6, 79 + y, C + 6, 79 + y), fill=p["b"])
    # gem
    d.polygon([(C, 50 + y), (C + 4, 55 + y), (C, 60 + y), (C - 4, 55 + y)], fill=p["k"])
    d.polygon([(C, 51 + y), (C + 3, 55 + y), (C, 59 + y), (C - 3, 55 + y)], fill=P("q"))
    d.polygon([(C, 53 + y), (C + 1, 55 + y), (C, 57 + y), (C - 1, 55 + y)], fill=P("Q"))

    # ---- legs ------------------------------------------------------------
    for lx in (C - 10, C + 2):
        d.rectangle((lx, 74 + y, lx + 8, 87), fill=p["h"], outline=p["k"])
        d.rectangle((lx - 1, 84, lx + 9, 87), fill=p["k"])

    # ---- scarf: ivory, draped to one side --------------------------------
    d.polygon([(C - 13, 31 + y), (C + 13, 31 + y), (C + 11, 41 + y), (C - 11, 41 + y)], fill=p["I"], outline=p["k"])
    d.polygon([(C - 13, 34 + y), (C + 13, 34 + y), (C + 12, 37 + y), (C - 12, 37 + y)], fill=p["W"])
    d.polygon([(C - 13, 38 + y), (C - 20, 43 + y), (C - 24, 66 + y), (C - 16, 64 + y), (C - 12, 44 + y)],
              fill=p["I"], outline=p["k"])
    d.polygon([(C - 15, 43 + y), (C - 19, 47 + y), (C - 22, 63 + y), (C - 17, 61 + y)], fill=p["W"])

    # ---- head ------------------------------------------------------------
    d.rounded_rectangle((C - 9, 12 + y, C + 9, 36 + y), radius=6, fill=p["I"], outline=p["k"])
    d.rounded_rectangle((C - 7, 13 + y, C + 7, 19 + y), radius=4, fill=p["W"])
    # fox-white face plate
    d.rounded_rectangle((C - 6, 19 + y, C + 6, 33 + y), radius=3, fill=p["W"], outline=p["k"])
    d.line((C - 6, 20 + y, C + 6, 20 + y), fill=p["t"])
    # nine red marks: 3 x 3, tiny
    if not eye_off:
        for gy in (21, 25, 29):
            for gx in (C - 6, C, C + 6):
                d.rectangle((gx - 1, gy + y, gx, gy + 1 + y), fill=P("O"))
                d.point((gx - 1, gy + y), fill=P("F"))
    else:
        for gy in (21, 25, 29):
            for gx in (C - 6, C, C + 6):
                d.point((gx, gy + y), fill=(66, 44, 48))
    # brow shadow
    d.line((C - 5, 21 + y, C + 5, 21 + y), fill=p["k"])

    # short swept fins on the side of the helm
    for side in (-1, 1):
        poly(d, [(C + side * 8, 16 + y), (C + side * 12, 9 + y),
                 (C + side * 13, 13 + y), (C + side * 7, 20 + y)], p["I"])
        d.line((C + side * 11, 11 + y, C + side * 9, 16 + y), fill=p["W"])

    # violet kabuki mask resting on the brow
    d.rounded_rectangle((C - 6, 4 + y, C + 6, 13 + y), radius=3, fill=p["q"], outline=p["k"])
    d.rounded_rectangle((C - 4, 6 + y, C + 4, 11 + y), radius=2, fill=P("Q"))
    d.line((C - 3, 8 + y, C + 3, 8 + y), fill=p["k"])
    d.rectangle((C - 2, 10 + y, C - 1, 11 + y), fill=p["W"])
    d.rectangle((C + 1, 10 + y, C + 2, 11 + y), fill=p["W"])

    # ---- shoulder cats ---------------------------------------------------
    blit(img, draw_cat("left", blink=cat_blink), CAT_POS["left"][0], CAT_POS["left"][1] + y)
    blit(img, draw_cat("right", blink=cat_blink), CAT_POS["right"][0], CAT_POS["right"][1] + y)

    # ---- aura ------------------------------------------------------------
    if aura:
        rad = 20 + aura * 5
        d.ellipse((C - rad, 46 + y - rad, C + rad, 46 + y + rad), outline=P("q"))
        d.ellipse((C - rad + 1, 46 + y - rad + 1, C + rad - 1, 46 + y + rad - 1), outline=P("Q"))
        for dx, dy in ((rad + 1, 0), (-rad - 1, 0), (0, rad + 1), (0, -rad - 1)):
            d.point((C + dx, 46 + y + dy), fill=P("w"))

    return img
