from __future__ import annotations

import unittest
from unittest.mock import patch

import h3
import pandas as pd

from scripts.build_frontend_map_artifacts import (
    attach_section_geography,
    build_hex_aggregates,
    build_hex_size_specs,
    build_zone_metrics,
    compute_horizon_metrics,
    detect_h3_resolution,
    roll_up_hex_frame,
)


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

    def test_detect_h3_resolution_and_size_specs_follow_base_grid(self) -> None:
        series = pd.Series(
            [
                h3.latlng_to_cell(40.4168, -3.7038, 10),
                h3.latlng_to_cell(40.4182, -3.6991, 10),
            ],
            dtype="string",
        )

        resolution = detect_h3_resolution(series)
        specs = build_hex_size_specs(resolution)

        self.assertEqual(resolution, 10)
        self.assertEqual([item["key"] for item in specs], ["small", "medium", "large"])
        self.assertEqual([item["h3_resolution"] for item in specs], [10, 9, 8])
        self.assertTrue(all(float(item["hex_area_km2"]) > 0.0 for item in specs))

    def test_roll_up_hex_frame_and_aggregate_preserve_metrics(self) -> None:
        parent = h3.latlng_to_cell(40.4168, -3.7038, 9)
        child_cells = sorted(h3.cell_to_children(parent, 10))[:2]
        frame = pd.DataFrame(
            {
                "h3_cell_start": child_cells,
                "category_code": ["A", "A"],
                "category_desc": ["Cafe", "Cafe"],
                "district_name": ["Centro", "Centro"],
                "barrio_name": ["Sol", "Sol"],
                "duration_months": [30.0, 8.0],
                "event_observed": [0, 1],
                "risk_ensemble": [0.2, 0.6],
                "risk_percentile": [0.1, 0.9],
                "quality_tier": ["medium", "medium"],
            }
        )

        rolled = roll_up_hex_frame(frame, target_resolution=9)
        rows = build_hex_aggregates(rolled, hex_cell_col="hex_h3_cell")

        self.assertEqual(rolled["hex_h3_cell"].nunique(), 1)
        self.assertEqual(rolled.loc[0, "hex_h3_cell"], parent)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["h3_cell"], parent)
        self.assertEqual(rows[0]["n_locales"], 2)
        self.assertEqual(rows[0]["support_12m"], 2)
        self.assertEqual(rows[0]["support_24m"], 2)
        self.assertAlmostEqual(rows[0]["survival_12m"] or 0.0, 0.5)
        self.assertAlmostEqual(rows[0]["survival_24m"] or 0.0, 0.5)
        self.assertAlmostEqual(rows[0]["avg_risk_ensemble"], 0.4)
        self.assertAlmostEqual(rows[0]["avg_risk_percentile"], 0.5)


if __name__ == "__main__":
    unittest.main()