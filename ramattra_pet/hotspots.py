"""Clickable regions inside the sprite, in 1:1 sprite pixels.

The pet window is exactly the size of the scaled sprite, so a click at window
coordinate ``(x, y)`` maps onto the artwork at ``(x // scale, y // scale)``.
Keeping the boxes here (plain data, no Pillow) lets the app hit-test without
importing the art toolchain.

Keep in sync with ``tools/art.py`` (``CAT_POS`` + ``CAT_W``/``CAT_H``); the test
suite checks that every box stays inside the sprite canvas.
"""

from __future__ import annotations

# form -> name -> (x0, y0, x1, y1) in 1:1 sprite pixels, x1/y1 exclusive
HOTSPOTS: dict[str, dict[str, tuple[int, int, int, int]]] = {
    "special": {
        "cat_left": (16, 20, 35, 37),
        "cat_right": (62, 18, 81, 35),
    },
}


def hit(form: str, x: int, y: int) -> str | None:
    """Return the hotspot name at sprite coordinates, or None."""
    for name, (x0, y0, x1, y1) in HOTSPOTS.get(form, {}).items():
        if x0 <= x < x1 and y0 <= y < y1:
            return name
    return None
