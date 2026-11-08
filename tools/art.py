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
    "c": (52, 40, 32),        # leather, shadow (combat forms)
    "C": (80, 62, 46),        # leather, mid
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
# Shared parts of the two combat forms
# ---------------------------------------------------------------------------

MASK_H = 16


def draw_mask(d: ImageDraw.ImageDraw, C: int, top: int, eye_off: bool = False) -> None:
    """The white kitsune faceplate: nine red marks above a violet jaw."""
    p = PALETTE
    d.polygon(
        [(C - 7, top + 2), (C - 5, top), (C + 5, top), (C + 7, top + 2),
         (C + 7, top + 10), (C + 3, top + MASK_H), (C - 3, top + MASK_H), (C - 7, top + 10)],
        fill=p["W"], outline=p["k"],
    )
    d.line((C - 4, top + 1, C + 3, top + 1), fill=(255, 253, 248))
    d.line((C - 6, top + 3, C - 6, top + 9), fill=p["i"])
    # violet jaw
    d.polygon([(C - 4, top + 11), (C + 4, top + 11), (C + 2, top + MASK_H), (C - 2, top + MASK_H)],
              fill=p["q"])
    d.line((C - 3, top + 12, C + 3, top + 12), fill=p["Q"])
    # nine red marks, 3 x 3, with air between them
    for gy in (top + 3, top + 6, top + 9):
        for gx in (C - 4, C, C + 4):
            if eye_off:
                d.point((gx, gy + 1), fill=(104, 80, 86))
            else:
                d.rectangle((gx - 1, gy, gx, gy + 1), fill=p["O"])
                d.point((gx - 1, gy), fill=p["F"])


def draw_mane(d: ImageDraw.ImageDraw, C: int, top: int, spread: int, bottom: int) -> None:
    """Black hair fanning out behind the head, with loose strands at the tips."""
    p = PALETTE
    d.polygon(
        [(C - spread + 3, top + 10), (C - spread + 8, top + 2), (C + spread - 8, top + 2),
         (C + spread - 3, top + 10), (C + spread + 3, bottom), (C + spread - 6, bottom - 7),
         (C + 4, bottom - 3), (C - 4, bottom - 3), (C - spread + 6, bottom - 7),
         (C - spread - 3, bottom)],
        fill=p["h"], outline=p["k"],
    )
    d.polygon([(C - spread + 9, top + 4), (C + spread - 9, top + 4),
               (C + spread - 14, top + 14), (C - spread + 14, top + 14)], fill=p["H"])
    for i, sx in enumerate((C - spread + 7, C - spread // 2, C, C + spread // 2, C + spread - 7)):
        drop = 5 + (i % 3) * 3
        d.polygon([(sx - 1, bottom - 10), (sx + 1, bottom - 10), (sx, bottom - 10 + drop)],
                  fill=p["h"], outline=p["k"])


def draw_glow_line(d: ImageDraw.ImageDraw, pts, glow: float) -> None:
    p = PALETTE
    P = lambda k: _shade(p[k], glow)  # noqa: E731
    d.line(pts, fill=p["k"], width=3)
    d.line(pts, fill=P("Q"), width=1)


# ---------------------------------------------------------------------------
# Form 1 — the monk: staff, cowl, scarf, tabard
# ---------------------------------------------------------------------------

OMNIC_W, OMNIC_H = 60, 80


def draw_omnic(glow: float = 1.0, bob: int = 0, eye_off: bool = False, cast: int = 0) -> Image.Image:
    img, d = new_canvas(OMNIC_W, OMNIC_H)
    p = PALETTE
    P = lambda k: _shade(p[k], glow)  # noqa: E731
    y = bob
    C = 30

    # ---- torso + robe ----------------------------------------------------
    d.polygon([(C - 9, 36 + y), (C + 9, 36 + y), (C + 8, 58 + y), (C - 8, 58 + y)],
              fill=p["c"], outline=p["k"])
    d.polygon([(C - 8, 37 + y), (C - 1, 37 + y), (C - 1, 57 + y), (C - 7, 57 + y)], fill=p["C"])
    d.polygon([(C + 5, 37 + y), (C + 8, 37 + y), (C + 8, 57 + y), (C + 5, 57 + y)], fill=p["r"])
    d.line((C - 7, 40 + y, C + 7, 40 + y), fill=p["B"])
    d.line((C - 7, 47 + y, C + 7, 47 + y), fill=p["b"])

    d.polygon([(C - 11, 54 + y), (C + 11, 54 + y), (C + 14, 80), (C - 14, 80)], fill=p["r"], outline=p["k"])
    d.polygon([(C - 6, 55 + y), (C + 6, 55 + y), (C + 8, 80), (C - 8, 80)], fill=p["T"], outline=p["k"])
    d.line((C - 4, 57 + y, C - 5, 79), fill=p["U"])
    d.line((C + 4, 57 + y, C + 5, 79), fill=p["t"])
    d.line((C - 6, 56 + y, C + 6, 56 + y), fill=p["B"])
    d.polygon([(C, 59 + y), (C + 3, 62 + y), (C, 65 + y), (C - 3, 62 + y)], fill=p["k"])
    d.polygon([(C, 60 + y), (C + 2, 62 + y), (C, 64 + y), (C - 2, 62 + y)], fill=P("Q"))

    # ---- hair behind the cowl -------------------------------------------
    draw_mane(d, C, 6 + y, 18, 38 + y)

    # ---- staff -----------------------------------------------------------
    sx = 9
    d.rectangle((sx - 1, 16 + y, sx + 2, 79), fill=p["k"])
    d.rectangle((sx, 16 + y, sx + 1, 78), fill=p["b"])
    d.line((sx, 18 + y, sx, 77), fill=p["B"])
    ox, oy = sx + 3, 12 + y
    d.ellipse((ox - 7, oy - 7, ox + 7, oy + 7), outline=p["k"])
    d.ellipse((ox - 6, oy - 6, ox + 6, oy + 6), outline=p["B"])
    d.line((sx, 16 + y, ox - 4, oy + 5), fill=p["B"])
    d.line((sx + 1, 16 + y, ox + 4, oy + 5), fill=p["b"])
    d.ellipse((ox - 4, oy - 4, ox + 4, oy + 4), fill=p["k"])
    d.ellipse((ox - 3, oy - 3, ox + 3, oy + 3), fill=P("q"))
    d.ellipse((ox - 2, oy - 2, ox + 2, oy + 2), fill=P("Q"))
    d.ellipse((ox - 1, oy - 1, ox + 1, oy + 1), fill=P("w"))
    if cast:
        rad = min(13, 8 + cast * 2)
        d.ellipse((ox - rad, oy - rad, ox + rad, oy + rad), outline=P("q"))
        d.ellipse((ox - rad + 1, oy - rad + 1, ox + rad - 1, oy + rad - 1), outline=P("Q"))
        for dx, dy in ((rad + 1, 0), (-rad - 1, 0), (0, rad + 1), (0, -rad - 1)):
            d.point((ox + dx, oy + dy), fill=P("w"))

    # ---- arms ------------------------------------------------------------
    # screen-left arm reaches the staff
    d.polygon([(C - 9, 37 + y), (C - 15, 41 + y), (C - 18, 49 + y), (C - 12, 50 + y)],
              fill=p["c"], outline=p["k"])
    d.line((C - 13, 42 + y, C - 15, 48 + y), fill=p["C"])
    d.rounded_rectangle((C - 23, 46 + y, C - 12, 53 + y), radius=2, fill=p["T"], outline=p["k"])
    d.line((C - 22, 49 + y, C - 13, 49 + y), fill=p["U"])
    # screen-right arm hangs, violet claw
    d.polygon([(C + 9, 37 + y), (C + 15, 42 + y), (C + 16, 52 + y), (C + 9, 51 + y)],
              fill=p["c"], outline=p["k"])
    d.line((C + 12, 38 + y, C + 12, 50 + y), fill=p["C"])
    d.rounded_rectangle((C + 9, 51 + y, C + 17, 58 + y), radius=2, fill=p["q"], outline=p["k"])
    for kx in (C + 10, C + 12, C + 14):
        d.line((kx, 54 + y, kx, 57 + y), fill=P("Q"))
    d.point((C + 12, 52 + y), fill=P("w"))

    # ---- scarf -----------------------------------------------------------
    d.polygon([(C - 10, 36 + y), (C + 10, 36 + y), (C + 8, 44 + y), (C - 8, 44 + y)],
              fill=p["I"], outline=p["k"])
    d.polygon([(C - 9, 37 + y), (C + 9, 37 + y), (C + 8, 40 + y), (C - 8, 40 + y)], fill=p["W"])
    d.polygon([(C + 6, 42 + y), (C + 11, 43 + y), (C + 13, 66 + y), (C + 8, 64 + y)],
              fill=p["i"], outline=p["k"])
    d.polygon([(C + 8, 44 + y), (C + 11, 45 + y), (C + 12, 62 + y), (C + 9, 61 + y)], fill=p["W"])

    # ---- cowl ------------------------------------------------------------
    d.polygon([(C - 10, 22 + y), (C - 8, 13 + y), (C - 4, 9 + y), (C + 4, 9 + y),
               (C + 8, 13 + y), (C + 10, 22 + y), (C + 11, 32 + y), (C + 6, 36 + y),
               (C - 6, 36 + y), (C - 11, 32 + y)], fill=p["I"], outline=p["k"])
    d.polygon([(C - 7, 14 + y), (C - 3, 11 + y), (C + 3, 11 + y), (C + 7, 14 + y),
               (C + 7, 24 + y), (C - 7, 24 + y)], fill=p["i"])
    d.line((C - 10, 24 + y, C - 5, 34 + y), fill=p["W"])
    d.line((C + 10, 24 + y, C + 5, 34 + y), fill=p["t"])

    draw_mask(d, C, 12 + y, eye_off=eye_off)

    return img


# ---------------------------------------------------------------------------
# Form 2 — the bulwark: bronze pauldrons, gem, fists
# ---------------------------------------------------------------------------

NEMESIS_W, NEMESIS_H = 84, 78


def draw_nemesis(glow: float = 1.0, bob: int = 0, eye_off: bool = False, roar: int = 0) -> Image.Image:
    img, d = new_canvas(NEMESIS_W, NEMESIS_H)
    p = PALETTE
    P = lambda k: _shade(p[k], glow)  # noqa: E731
    y = bob
    C = 42

    # ---- legs ------------------------------------------------------------
    for lx in (C - 12, C + 4):
        d.polygon([(lx, 54), (lx + 9, 54), (lx + 9, 77), (lx, 77)], fill=p["c"], outline=p["k"])
        d.line((lx + 2, 56, lx + 2, 76), fill=p["C"])
        d.rectangle((lx - 1, 74, lx + 10, 77), fill=p["k"])
        d.line((lx, 74, lx + 9, 74), fill=p["B"])

    draw_mane(d, C, 6 + y, 15, 34 + y)

    # ---- torso -----------------------------------------------------------
    d.polygon([(C - 12, 30 + y), (C + 12, 30 + y), (C + 12, 56 + y), (C - 12, 56 + y)],
              fill=p["c"], outline=p["k"])
    d.polygon([(C - 11, 31 + y), (C - 1, 31 + y), (C - 1, 55 + y), (C - 11, 55 + y)], fill=p["C"])
    d.polygon([(C + 5, 31 + y), (C + 11, 31 + y), (C + 11, 55 + y), (C + 6, 55 + y)], fill=p["r"])
    d.rectangle((C - 6, 33 + y, C + 6, 49 + y), fill=p["k"])
    d.rectangle((C - 5, 34 + y, C + 5, 48 + y), fill=p["T"])
    d.polygon([(C, 36 + y), (C + 4, 40 + y), (C + 4, 43 + y), (C, 47 + y),
               (C - 4, 43 + y), (C - 4, 40 + y)], fill=p["k"])
    d.polygon([(C, 37 + y), (C + 3, 40 + y), (C + 3, 42 + y), (C, 46 + y),
               (C - 3, 42 + y), (C - 3, 40 + y)], fill=P("q"))
    d.polygon([(C, 39 + y), (C + 1, 41 + y), (C, 43 + y), (C - 1, 41 + y)], fill=P("Q"))

    # ---- pauldrons (top above the chin so the head sits in them) --------
    for side in (-1, 1):
        inner, outer = C + side * 10, C + side * 32
        d.polygon([(inner, 24 + y), (outer - side * 2, 28 + y), (outer, 34 + y),
                   (outer, 44 + y), (inner, 42 + y)], fill=p["T"], outline=p["k"])
        d.polygon([(inner + side * 3, 26 + y), (outer - side * 5, 30 + y),
                   (outer - side * 4, 33 + y), (inner + side * 4, 31 + y)], fill=p["U"])
        d.line((inner, 24 + y, outer - side * 2, 28 + y), fill=p["B"])
        d.line((inner, 42 + y, outer, 44 + y), fill=p["t"])
        draw_glow_line(d, [(C + side * 24, 33 + y), (C + side * 24, 40 + y),
                           (C + side * 16, 40 + y)], glow)

    # ---- arms + fists (one continuous limb under each pauldron) ---------
    for side in (-1, 1):
        ax = C + side * 23
        d.polygon([(ax, 38 + y), (ax + side * 13, 38 + y), (ax + side * 13, 58 + y), (ax, 58 + y)],
                  fill=p["T"], outline=p["k"])
        d.line((ax + side * 3, 40 + y, ax + side * 3, 56 + y), fill=p["U"])
        d.line((ax + side * 9, 40 + y, ax + side * 9, 56 + y), fill=p["t"])
        fx0, fx1 = sorted((ax - side * 1, ax + side * 14))
        d.rounded_rectangle((fx0, 54 + y, fx1, 74 + y), radius=3, fill=p["c"], outline=p["k"])
        d.line((fx0 + 3, 56 + y, fx0 + 3, 72 + y), fill=p["C"])
        d.line((fx0 + 1, 55 + y, fx1 - 1, 55 + y), fill=p["B"])
        d.line((fx0 + 2, 60 + y, fx1 - 2, 60 + y), fill=p["t"])
        d.line((fx0 + 2, 66 + y, fx1 - 2, 66 + y), fill=p["t"])
        # thumb
        d.polygon([(fx0 + 1, 58 + y), (fx0 + 4, 60 + y), (fx0 + 1, 63 + y)], fill=p["C"])

    # ---- neck joining head and chest ------------------------------------
    d.polygon([(C - 11, 23 + y), (C + 11, 23 + y), (C + 13, 31 + y), (C - 13, 31 + y)],
              fill=p["h"], outline=p["k"])

    # ---- hair falls over the shoulders, then the mask --------------------
    for side in (-1, 1):
        d.polygon([(C + side * 12, 22 + y), (C + side * 4, 28 + y), (C + side * 11, 34 + y)],
                  fill=p["h"], outline=p["k"])
        d.polygon([(C + side * 9, 24 + y), (C + side * 5, 28 + y), (C + side * 8, 32 + y)],
                  fill=p["H"])
    draw_mask(d, C, 11 + y, eye_off=eye_off)
    for side in (-1, 1):
        bx = C + side * 7
        d.polygon([(bx, 18 + y), (bx + side * 7, 9 + y), (bx + side * 2, 22 + y)],
                  fill=p["T"], outline=p["k"])
        d.polygon([(bx + side * 2, 17 + y), (bx + side * 5, 12 + y), (bx + side * 3, 19 + y)],
                  fill=p["U"])

    if roar:
        rad = 18 + roar * 5
        d.ellipse((C - rad, 40 + y - rad, C + rad, 40 + y + rad), outline=P("q"))
        d.ellipse((C - rad + 1, 40 + y - rad + 1, C + rad - 1, 40 + y + rad - 1), outline=P("Q"))
        for dx, dy in ((rad + 1, 0), (-rad - 1, 0), (0, rad + 1), (0, -rad - 1)):
            d.point((C + dx, 40 + y + dy), fill=P("w"))

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
