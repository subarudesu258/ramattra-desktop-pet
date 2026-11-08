"""Voice-line selection."""

from __future__ import annotations

import random
import unittest

from ramattra_pet import quotes


class QuoteTests(unittest.TestCase):
    def test_every_pool_is_usable(self) -> None:
        for form, pools in quotes.LINES.items():
            for kind, lines in pools.items():
                self.assertTrue(lines, f"{form}/{kind} is empty")
                for line in lines:
                    self.assertEqual(line, line.strip())
                    self.assertTrue(line)

    def test_pick_returns_a_line_for_each_form_and_kind(self) -> None:
        for form in quotes.FORMS:
            for kind in ("click", "idle", "transform", "wake", "sleep"):
                self.assertTrue(quotes.pick(form, kind))
                self.assertIn(quotes.pick(form, kind), quotes.LINES[form][kind])

    def test_cat_lines_only_exist_for_the_special_form(self) -> None:
        self.assertIn("cat", quotes.LINES["special"])
        self.assertTrue(quotes.pick("special", "cat"))
        self.assertNotIn("cat", quotes.LINES["omnic"])

    def test_unknown_form_or_kind_degrades_gracefully(self) -> None:
        self.assertTrue(quotes.pick("dragon", "click"))
        self.assertTrue(quotes.pick("omnic", "dance"))

    def test_seeded_pick_is_deterministic(self) -> None:
        a = quotes.pick("omnic", "idle", random.Random(7))
        b = quotes.pick("omnic", "idle", random.Random(7))
        self.assertEqual(a, b)

    def test_signature_lines(self) -> None:
        self.assertEqual(quotes.signature("nemesis"), "感受，我的痛苦！")
        self.assertEqual(quotes.signature("special"), "感受，我的痛苦！")
        self.assertIsNone(quotes.signature("omnic"))
        # the signature also sits in the normal pool, so it keeps coming back
        self.assertIn("感受，我的痛苦！", quotes.LINES["nemesis"]["click"])
        self.assertIn("感受，我的痛苦！", quotes.LINES["special"]["click"])

    def test_other_form_cycles_through_three(self) -> None:
        self.assertEqual(quotes.other_form("omnic"), "nemesis")
        self.assertEqual(quotes.other_form("nemesis"), "special")
        self.assertEqual(quotes.other_form("special"), "omnic")
        self.assertEqual(quotes.other_form("dragon"), "omnic")


if __name__ == "__main__":
    unittest.main()
