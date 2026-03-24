from __future__ import annotations

import unittest

import pandas as pd

from localizate.survival_features import (
    attach_avisos_features,
    compute_metro_features,
    normalize_admin_code,
)


class SurvivalFeaturesTests(unittest.TestCase):
    def test_normalize_admin_code_handles_decimal_strings(self) -> None:
        self.assertEqual(normalize_admin_code("7.0", width=3), "007")
        self.assertEqual(normalize_admin_code("16", width=2), "16")
        self.assertIsNone(normalize_admin_code(None, width=2))

    def test_attach_avisos_features_uses_previous_year(self) -> None:
        abt = pd.DataFrame(
            {
                "first_seen_period": ["2024-03", "2025-01"],
                "district_code_start": ["12", "12"],
                "barrio_code_start": ["007", "007"],
            }
        )
        yearly = pd.DataFrame(
            {
                "avisos_year": [2023, 2024],
                "district_code": ["12", "12"],
                "barrio_code": ["007", "007"],
                "avisos_district_prev_year": [100, 200],
                "avisos_district_per_1000_prev_year": [10.0, 20.0],
                "avisos_barrio_prev_year": [40, 80],
                "avisos_barrio_per_1000_prev_year": [4.0, 8.0],
                "avisos_barrio_share_of_district_prev_year": [0.4, 0.4],
            }
        )

        enriched = attach_avisos_features(abt, avisos_yearly=yearly)

        self.assertEqual(enriched.loc[0, "avisos_district_prev_year"], 100)
        self.assertEqual(enriched.loc[1, "avisos_district_prev_year"], 200)
        self.assertEqual(enriched.loc[0, "avisos_barrio_per_1000_prev_year"], 4.0)

    def test_compute_metro_features_returns_distance_and_counts(self) -> None:
        abt = pd.DataFrame(
            {
                "lat_wgs84_start": [40.0, None],
                "lon_wgs84_start": [-3.0, None],
            }
        )
        metro = pd.DataFrame(
            {
                "metro_lat": [40.0, 40.004],
                "metro_lon": [-3.0, -3.0],
            }
        )

        features = compute_metro_features(abt, metro_reference=metro)

        self.assertAlmostEqual(float(features.loc[0, "metro_distance_m_start"]), 0.0, places=4)
        self.assertGreaterEqual(float(features.loc[0, "metro_access_count_500m_start"]), 1.0)
        self.assertEqual(float(features.loc[1, "missing_metro_distance_start"]), 1.0)


if __name__ == "__main__":
    unittest.main()
