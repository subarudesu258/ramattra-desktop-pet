"""Hotspot boxes stay inside the artwork they belong to."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from ramattra_pet import hotspots

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


class HotspotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))

    def test_boxes_fit_inside_the_sprite(self) -> None:
        for form, boxes in hotspots.HOTSPOTS.items():
            entry = self.manifest[f"{form}_idle"]
            w, h = entry["size"]
            scale = entry.get("scale", 1)
            for name, (x0, y0, x1, y1) in boxes.items():
                self.assertLess(x0, x1, name)
                self.assertLess(y0, y1, name)
                self.assertGreaterEqual(x0, 0, name)
                self.assertGreaterEqual(y0, 0, name)
                self.assertLessEqual(x1, w // scale, f"{name} sticks out on the right")
                self.assertLessEqual(y1, h // scale, f"{name} sticks out at the bottom")

    def test_cats_do_not_overlap(self) -> None:
        boxes = list(hotspots.HOTSPOTS["special"].values())
        (ax0, ay0, ax1, ay1), (bx0, by0, bx1, by1) = boxes
        overlap = ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1
        self.assertFalse(overlap)

    def test_hit_and_miss(self) -> None:
        self.assertEqual(hotspots.hit("special", 20, 25), "cat_left")
        self.assertEqual(hotspots.hit("special", 70, 20), "cat_right")
        self.assertIsNone(hotspots.hit("special", 48, 60))   # the tabard
        self.assertIsNone(hotspots.hit("omnic", 20, 25))     # only the special form has cats


if __name__ == "__main__":
    unittest.main()
