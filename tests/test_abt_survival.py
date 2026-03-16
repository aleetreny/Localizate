from __future__ import annotations

import unittest

from localizate.abt_survival import next_period


class AbtSurvivalTests(unittest.TestCase):
    def test_next_period_advances_month(self) -> None:
        self.assertEqual(next_period("2026-03"), "2026-04")

    def test_next_period_handles_year_rollover(self) -> None:
        self.assertEqual(next_period("2026-12"), "2027-01")


if __name__ == "__main__":
    unittest.main()
