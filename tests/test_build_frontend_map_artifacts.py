from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from scripts.build_frontend_map_artifacts import attach_section_geography, build_zone_metrics, compute_horizon_metrics


class FrontendMapArtifactsTests(unittest.TestCase):
    def test_compute_horizon_metrics_returns_none_without_support(self) -> None:
        duration = pd.Series([3.0, 5.0], dtype=float)
        event = pd.Series([0, 0], dtype=int)

        support, survival = compute_horizon_metrics(duration, event, horizon=12.0)

        self.assertEqual(support, 0)
        self.assertIsNone(survival)

    def test_compute_horizon_metrics_keeps_true_zero_survival(self) -> None:
        duration = pd.Series([4.0, 8.0], dtype=float)
        event = pd.Series([1, 1], dtype=int)

        support, survival = compute_horizon_metrics(duration, event, horizon=12.0)

        self.assertEqual(support, 2)
        self.assertEqual(survival, 0.0)

    def test_compute_horizon_metrics_counts_survivors_over_support(self) -> None:
        duration = pd.Series([30.0, 6.0, 18.0], dtype=float)
        event = pd.Series([0, 1, 0], dtype=int)

        support, survival = compute_horizon_metrics(duration, event, horizon=12.0)

        self.assertEqual(support, 3)
        self.assertAlmostEqual(survival or 0.0, 2.0 / 3.0)

    def test_build_zone_metrics_preserves_null_survival_without_support(self) -> None:
        frame = pd.DataFrame(
            {
                "district_code": ["01", "01"],
                "district_name": ["Centro", "Centro"],
                "barrio_code": ["001", "001"],
                "barrio_name": ["Sol", "Sol"],
                "category_code": ["A", "A"],
                "category_desc": ["Cafe", "Cafe"],
                "duration_months": [6.0, 8.0],
                "event_observed": [0, 0],
                "risk_ensemble": [0.2, 0.3],
                "risk_percentile": [0.4, 0.6],
            }
        )

        rows = build_zone_metrics(
            frame,
            zone_level="district",
            zone_code_col="district_code",
            zone_name_col="district_name",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["support_24m"], 0)
        self.assertIsNone(rows[0]["survival_24m"])

    def test_attach_section_geography_backfills_from_coordinates(self) -> None:
        frame = pd.DataFrame(
            {
                "section_key_start": ["99999"],
                "lat_wgs84_start": [40.4168],
                "lon_wgs84_start": [-3.7038],
            }
        )
        section_geography = pd.DataFrame(
            {
                "section_key": ["00001"],
                "district_code": ["01"],
                "district_name": ["Centro"],
                "barrio_code": ["001"],
                "barrio_name": ["Sol"],
            }
        )
        resolved = pd.DataFrame(
            {
                "section_key_spatial": ["00001"],
                "district_code": ["01"],
                "district_name": ["Centro"],
                "barrio_code": ["001"],
                "barrio_name": ["Sol"],
            },
            index=frame.index,
        )

        with patch("scripts.build_frontend_map_artifacts.resolve_section_geography_from_coordinates", return_value=resolved):
            enriched, stats = attach_section_geography(frame, section_geography=section_geography)

        self.assertEqual(enriched.loc[0, "section_key_join"], "00001")
        self.assertEqual(enriched.loc[0, "district_name"], "Centro")
        self.assertEqual(enriched.loc[0, "barrio_name"], "Sol")
        self.assertEqual(stats["matched_from_section_key"], 0)
        self.assertEqual(stats["backfilled_from_coordinates"], 1)
        self.assertEqual(stats["remaining_missing_geography"], 0)


if __name__ == "__main__":
    unittest.main()