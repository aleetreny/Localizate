from __future__ import annotations

import unittest

import pandas as pd

from localizate.zone_category_survival import apply_bh_correction, confidence_tier, estimate_km_survival


class ZoneCategorySurvivalTests(unittest.TestCase):
    def test_confidence_tier_district(self) -> None:
        self.assertEqual(confidence_tier(n_locales=200, n_events=25, zone_level="district"), "high")
        self.assertEqual(confidence_tier(n_locales=90, n_events=13, zone_level="district"), "medium")

    def test_estimate_km_survival_returns_probability(self) -> None:
        duration = pd.Series([6, 12, 18, 24], dtype=float)
        event = pd.Series([1, 0, 1, 0], dtype=int)

        value = estimate_km_survival(duration, event, time_horizon=12.0)

        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_apply_bh_correction_marks_significant(self) -> None:
        items = [{"pvalue": 0.001}, {"pvalue": 0.02}, {"pvalue": 0.2}]

        corrected = apply_bh_correction(items, alpha=0.05)

        self.assertTrue(corrected[0]["significant"])
        self.assertFalse(corrected[2]["significant"])


if __name__ == "__main__":
    unittest.main()