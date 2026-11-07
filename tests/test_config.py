"""Settings round-trip and validation."""

from __future__ import annotations

import json
import unittest

from ramattra_pet import config
from tests._helpers import temp_dir


class ConfigTests(unittest.TestCase):
    def test_defaults_are_sane(self) -> None:
        cfg = config.Config()
        self.assertEqual(cfg.form, "omnic")
        self.assertTrue(cfg.topmost)
        self.assertIsNone(cfg.x)

    def test_normalised_clamps_bad_values(self) -> None:
        cfg = config.Config(form="dragon", idle_sleep_seconds=1, idle_talk_min=99, idle_talk_max=10, bubble_seconds=99)
        cfg.normalised()
        self.assertEqual(cfg.form, "omnic")
        self.assertGreaterEqual(cfg.idle_sleep_seconds, 30)
        self.assertLess(cfg.idle_talk_min, cfg.idle_talk_max)
        self.assertLessEqual(cfg.bubble_seconds, 15.0)

    def test_three_forms_are_accepted(self) -> None:
        for form in ("omnic", "nemesis", "special"):
            self.assertEqual(config.Config(form=form).normalised().form, form)

    def test_roundtrip(self) -> None:
        with temp_dir() as tmp:
            path = tmp / "config.json"
            cfg = config.Config(x=120, y=340, form="nemesis", topmost=False)
            config.save(cfg, path)
            again = config.load(path)
            self.assertEqual((again.x, again.y), (120, 340))
            self.assertEqual(again.form, "nemesis")
            self.assertFalse(again.topmost)

    def test_corrupt_file_falls_back_to_defaults(self) -> None:
        with temp_dir() as tmp:
            path = tmp / "config.json"
            path.write_text("{not json", encoding="utf-8")
            self.assertEqual(config.load(path).form, "omnic")

    def test_unknown_keys_are_ignored(self) -> None:
        with temp_dir() as tmp:
            path = tmp / "config.json"
            path.write_text(json.dumps({"form": "nemesis", "nonsense": 1}), encoding="utf-8")
            self.assertEqual(config.load(path).form, "nemesis")

    def test_save_is_atomic_and_leaves_no_temp(self) -> None:
        with temp_dir() as tmp:
            path = tmp / "config.json"
            config.save(config.Config(), path)
            self.assertTrue(path.exists())
            self.assertFalse(path.with_suffix(".tmp").exists())

    def test_candidate_dirs_prefer_appdata(self) -> None:
        dirs = config.candidate_dirs()
        self.assertTrue(dirs)
        self.assertTrue(all(isinstance(d, type(dirs[0])) for d in dirs))


if __name__ == "__main__":
    unittest.main()
