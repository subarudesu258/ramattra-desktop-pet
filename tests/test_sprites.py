"""The committed sprites must stay consistent with the manifest and the app."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from PIL import Image

from ramattra_pet import app
from ramattra_pet.sprites import COLOUR_KEY, SpriteLibrary

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def key_rgb() -> tuple[int, int, int]:
    value = COLOUR_KEY.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))

    def test_every_frame_file_exists(self) -> None:
        for clip, entry in self.manifest.items():
            folder = ASSETS / entry["dir"]
            self.assertTrue(folder.is_dir(), f"{clip}: missing folder {folder}")
            for name in entry["frames"]:
                self.assertTrue((folder / name).is_file(), f"{clip}: missing {name}")

    def test_frames_are_colour_keyed_and_the_right_size(self) -> None:
        expected = key_rgb()
        for clip, entry in self.manifest.items():
            folder = ASSETS / entry["dir"]
            width, height = entry["size"]
            for name in entry["frames"]:
                with Image.open(folder / name) as img:
                    self.assertEqual(img.mode, "RGB", f"{clip}/{name} must not have alpha")
                    self.assertEqual(img.size, (width, height))
                    self.assertEqual(img.getpixel((0, 0)), expected, f"{clip}/{name} corner is not the key colour")
                    # packed RGB bytes; avoids Pillow's deprecated getdata()
                    raw = img.tobytes()
                    key = bytes(expected)
                    keyed = sum(1 for i in range(0, len(raw), 3) if raw[i : i + 3] == key)
                    self.assertGreater(keyed * 3 / len(raw), 0.05, f"{clip}/{name} has almost no transparent area")


class ClipTableTests(unittest.TestCase):
    """Catches typos where app.CLIPS points at a clip that was never baked."""

    def test_clip_references(self) -> None:
        baked = set(SpriteLibrary().clip_names())
        required = {"idle", "blink", "action", "sleep"}
        for form, clips in app.CLIPS.items():
            self.assertLessEqual(required, set(clips), form)
            for key, clip in clips.items():
                self.assertIn(clip.name, baked, f"{form}.{key} -> {clip.name} is not baked")
                self.assertGreater(clip.fps, 0)


class TkFrameTests(unittest.TestCase):
    """Needs a display; skipped automatically where Tk cannot start."""

    @classmethod
    def setUpClass(cls) -> None:
        import tkinter as tk

        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except Exception as exc:  # pragma: no cover - headless CI
            raise unittest.SkipTest(f"no Tk display: {exc}")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.root.destroy()

    def test_frames_load(self) -> None:
        lib = SpriteLibrary(master=self.root)
        for form in ("omnic", "nemesis", "special"):
            self.assertEqual(len(lib.frames(f"{form}_idle")), 8)
            self.assertEqual(len(lib.frames(f"{form}_sleep")), 4)
            self.assertEqual(lib.scale(f"{form}_idle"), 3)

    def test_unknown_clip_raises(self) -> None:
        with self.assertRaises(KeyError):
            SpriteLibrary(master=self.root).frames("nope")

    def test_zoom_scales_frames_and_reported_size(self) -> None:
        lib = SpriteLibrary(master=self.root)
        base = lib.frames("omnic_idle", 1)[0]
        doubled = lib.frames("omnic_idle", 2)[0]
        self.assertEqual((doubled.width(), doubled.height()), (base.width() * 2, base.height() * 2))
        self.assertEqual(lib.size("omnic_idle", 2), (base.width() * 2, base.height() * 2))


if __name__ == "__main__":
    unittest.main()
