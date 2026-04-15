from __future__ import annotations

import unittest
from unittest.mock import patch

import h3
import pandas as pd

from scripts.build_frontend_map_artifacts import (
    attach_section_geography,
    build_hex_aggregates,
    build_hex_composition_history_records,
    build_map_hex_payload,
    build_map_shared_payload,
    build_zone_history_records,
    build_category_options,
    build_hex_size_specs,
    build_zone_metrics,
    compute_horizon_metrics,
    detect_h3_resolution,
    finalize_historical_metric_records,
    infer_unknown_activity_category,
    roll_up_hex_frame,
    select_latest_periods_by_year,
    summarize_snapshot_activity_categories,
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

    def test_build_map_shared_payload_excludes_hex_rows(self) -> None:
        payload = build_map_shared_payload(
            generated_at="2026-04-15T00:00:00Z",
            categories=[{"category_code": "__all__", "category_desc": "Todos", "n_locales": 10, "n_hexes": 2}],
            zones={"district": [{"zone_code": "01"}], "barrio": [{"zone_code": "001"}]},
        )

        self.assertIn("meta", payload)
        self.assertIn("categories", payload)
        self.assertIn("zones", payload)
        self.assertNotIn("hexes", payload)

    def test_build_map_hex_payload_contains_only_meta_and_hexes(self) -> None:
        payload = build_map_hex_payload(
            generated_at="2026-04-15T00:00:00Z",
            spec={"key": "small", "h3_resolution": 10, "hex_area_km2": 0.1234},
            hexes=[{"h3_cell": "abc"}],
        )

        self.assertEqual(sorted(payload.keys()), ["hexes", "meta"])
        self.assertEqual(payload["meta"]["hex_size"], "small")
        self.assertEqual(payload["meta"]["h3_resolution"], 10)
        self.assertEqual(payload["hexes"], [{"h3_cell": "abc"}])

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
        self.assertAlmostEqual(rows[0]["avg_risk_primary"], 0.25)

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
        self.assertAlmostEqual(rows[0]["avg_risk_primary"], 0.4)
        self.assertAlmostEqual(rows[0]["avg_risk_ensemble"], 0.4)
        self.assertAlmostEqual(rows[0]["avg_risk_percentile"], 0.5)

    def test_infer_unknown_activity_category_recovers_single_macro(self) -> None:
        category_code, category_desc = infer_unknown_activity_category(
            {
                "raw_rows": 1,
                "macro_count": 1,
                "valid_epigrafe_rows": 1,
                "single_macro_code": "bar_cafe",
                "single_macro_desc": "Bar y cafetería",
            }
        )

        self.assertEqual(category_code, "bar_cafe")
        self.assertEqual(category_desc, "Bar y cafetería")

    def test_infer_unknown_activity_category_marks_multi_activity_before_placeholders(self) -> None:
        category_code, category_desc = infer_unknown_activity_category(
            {
                "raw_rows": 2,
                "macro_count": 2,
                "valid_epigrafe_rows": 2,
                "has_no_activity_marker": 1,
            }
        )

        self.assertEqual(category_code, "__status_multi_activity__")
        self.assertEqual(category_desc, "Multiactividad")

    def test_build_category_options_hides_residual_statuses_from_selector(self) -> None:
        categories = build_category_options(
            [
                {"h3_cell": "a", "category_code": "__status_uncoded_activity__", "category_desc": "Actividad no informada", "n_locales": 100},
                {"h3_cell": "a", "category_code": "__status_multi_activity__", "category_desc": "Multiactividad", "n_locales": 60},
                {"h3_cell": "a", "category_code": "__status_no_activity__", "category_desc": "Sin actividad declarada", "n_locales": 20},
                {"h3_cell": "a", "category_code": "__status_missing_snapshot__", "category_desc": "Mes sin fichero de actividad", "n_locales": 10},
                {"h3_cell": "a", "category_code": "__status_pending_coding__", "category_desc": "Actividad pendiente de codificar", "n_locales": 5},
                {"h3_cell": "b", "category_code": "bar_cafe", "category_desc": "Bar y cafetería", "n_locales": 10},
                {"h3_cell": "c", "category_code": "__all__", "category_desc": "Todos los locales", "n_locales": 110},
            ],
            glossary_profiles={},
        )

        self.assertEqual(
            [item["category_code"] for item in categories],
            ["__all__", "bar_cafe", "__status_uncoded_activity__", "__status_multi_activity__"],
        )

    def test_select_latest_periods_by_year_uses_last_available_cut(self) -> None:
        periods = ["2015-01", "2015-11", "2015-12", "2016-03", "2016-09", "2016-12", "2026-01", "2026-03"]

        selected = select_latest_periods_by_year(periods)

        self.assertEqual(selected, ["2015-12", "2016-12", "2026-03"])

    def test_summarize_snapshot_activity_categories_collapses_snapshot_rows(self) -> None:
        activity_frame = pd.DataFrame(
            {
                "id_local": pd.Series([1, 1, 2, 3, 4, 4], dtype="Int64"),
                "snapshot_period": pd.Series(["2024-12"] * 6, dtype="string"),
                "raw_epigrafe_code": pd.Series(["561006.0", "563004.0", "0.0", "", "561001.0", "472401.0"], dtype="string"),
                "raw_epigrafe_desc": pd.Series(
                    [
                        "CAFETERIA",
                        "TABERNA",
                        "LOCAL SIN ACTIVIDAD",
                        "",
                        "RESTAURANTE",
                        "PANADERIA",
                    ],
                    dtype="string",
                ),
            }
        )
        epigrafe_lookup = pd.DataFrame(
            {
                "raw_code": ["561006.0", "563004.0", "561001.0", "472401.0"],
                "clean_code": ["561006", "563004", "561001", "472401"],
                "code_valid": [True, True, True, True],
            }
        )
        macro_lookup = pd.DataFrame(
            {
                "epigrafe_code": ["561006", "563004", "561001", "472401"],
                "macro_category_code": ["bar_cafe", "bar_cafe", "restaurant", "bakery_pastry"],
                "macro_category_name": ["Bar y cafeteria", "Bar y cafeteria", "Restaurante", "Panaderia y pasteleria"],
            }
        )

        summary = summarize_snapshot_activity_categories(
            activity_frame,
            epigrafe_lookup=epigrafe_lookup,
            macro_lookup=macro_lookup,
        )

        resolved = summary.sort_values("id_local").reset_index(drop=True)
        self.assertEqual(
            resolved[["category_code", "category_desc"]].to_dict(orient="records"),
            [
                {"category_code": "bar_cafe", "category_desc": "Bar y cafeteria"},
                {"category_code": "__status_no_activity__", "category_desc": "Sin actividad declarada"},
                {"category_code": "__status_uncoded_activity__", "category_desc": "Actividad no informada"},
                {"category_code": "__status_multi_activity__", "category_desc": "Multiactividad"},
            ],
        )

    def test_build_zone_history_records_ranks_each_category_within_year(self) -> None:
        frame = pd.DataFrame(
            {
                "id_local": pd.Series([1, 2, 3, 4, 5, 6], dtype="Int64"),
                "snapshot_period": pd.Series(["2024-12"] * 6, dtype="string"),
                "district_code": pd.Series(["01", "01", "01", "02", "02", "02"], dtype="string"),
                "district_name": pd.Series(["Centro", "Centro", "Centro", "Salamanca", "Salamanca", "Salamanca"], dtype="string"),
                "barrio_code": pd.Series(["01001", "01001", "01001", "02001", "02001", "02001"], dtype="string"),
                "barrio_name": pd.Series(["Sol", "Sol", "Sol", "Recoletos", "Recoletos", "Recoletos"], dtype="string"),
                "barrio_context_name": pd.Series(["Centro", "Centro", "Centro", "Salamanca", "Salamanca", "Salamanca"], dtype="string"),
                "barrio_key": pd.Series(["01001", "01001", "01001", "02001", "02001", "02001"], dtype="string"),
                "category_code": pd.Series(["__all__", "bar_cafe", "bar_cafe", "__all__", "bar_cafe", "restaurant"], dtype="string"),
                "category_desc": pd.Series(["Todos los locales", "Bar", "Bar", "Todos los locales", "Bar", "Restaurante"], dtype="string"),
            }
        )

        rows = build_zone_history_records(frame, zone_level="district", year=2024, period="2024-12")
        bar_rows = [row for row in rows if row["category_code"] == "bar_cafe"]

        self.assertEqual([row["zone_name"] for row in bar_rows], ["Centro", "Salamanca"])
        self.assertEqual([row["rank"] for row in bar_rows], [1, 2])
        self.assertEqual([row["n_locales"] for row in bar_rows], [2, 1])

    def test_build_zone_history_records_ranks_by_specialization_not_raw_stock(self) -> None:
        rows: list[dict[str, object]] = []

        for local_id in range(1, 101):
            rows.append(
                {
                    "id_local": local_id,
                    "snapshot_period": "2024-12",
                    "district_code": "01",
                    "district_name": "Centro",
                    "barrio_code": "01001",
                    "barrio_name": "Sol",
                    "barrio_context_name": "Centro",
                    "barrio_key": "01001",
                    "category_code": "__all__",
                    "category_desc": "Todos los locales",
                }
            )
        for local_id in range(1, 21):
            rows.append(
                {
                    "id_local": local_id,
                    "snapshot_period": "2024-12",
                    "district_code": "01",
                    "district_name": "Centro",
                    "barrio_code": "01001",
                    "barrio_name": "Sol",
                    "barrio_context_name": "Centro",
                    "barrio_key": "01001",
                    "category_code": "pet_retail",
                    "category_desc": "Mascotas",
                }
            )

        for local_id in range(101, 121):
            rows.append(
                {
                    "id_local": local_id,
                    "snapshot_period": "2024-12",
                    "district_code": "02",
                    "district_name": "Arganzuela",
                    "barrio_code": "02001",
                    "barrio_name": "Palos de la Frontera",
                    "barrio_context_name": "Arganzuela",
                    "barrio_key": "02001",
                    "category_code": "__all__",
                    "category_desc": "Todos los locales",
                }
            )
        for local_id in range(101, 111):
            rows.append(
                {
                    "id_local": local_id,
                    "snapshot_period": "2024-12",
                    "district_code": "02",
                    "district_name": "Arganzuela",
                    "barrio_code": "02001",
                    "barrio_name": "Palos de la Frontera",
                    "barrio_context_name": "Arganzuela",
                    "barrio_key": "02001",
                    "category_code": "pet_retail",
                    "category_desc": "Mascotas",
                }
            )

        frame = pd.DataFrame(rows)

        records = build_zone_history_records(frame, zone_level="district", year=2024, period="2024-12")
        pet_rows = [row for row in records if row["category_code"] == "pet_retail"]

        self.assertEqual([row["zone_name"] for row in pet_rows], ["Arganzuela", "Centro"])
        self.assertGreater(pet_rows[0]["metric_value"], pet_rows[1]["metric_value"])
        self.assertEqual([row["n_locales"] for row in pet_rows], [10, 20])

    def test_build_hex_composition_history_records_builds_per_hex_shares(self) -> None:
        frame = pd.DataFrame(
            {
                "id_local": pd.Series([1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 5, 6], dtype="Int64"),
                "snapshot_period": pd.Series(["2024-12"] * 12, dtype="string"),
                "h3_cell": pd.Series(["8a1", "8a1", "8a1", "8a1", "8a2", "8a2", "8a2", "8a1", "8a1", "8a1", "8a2", "8a2"], dtype="string"),
                "district_code": pd.Series(["01"] * 12, dtype="string"),
                "district_name": pd.Series(["Centro"] * 12, dtype="string"),
                "barrio_code": pd.Series(["01001"] * 12, dtype="string"),
                "barrio_name": pd.Series(["Sol"] * 12, dtype="string"),
                "barrio_context_name": pd.Series(["Centro"] * 12, dtype="string"),
                "barrio_key": pd.Series(["01001"] * 12, dtype="string"),
                "category_code": pd.Series([
                    "__all__",
                    "__all__",
                    "__all__",
                    "__all__",
                    "__all__",
                    "__all__",
                    "__all__",
                    "bar_cafe",
                    "bar_cafe",
                    "restaurant",
                    "restaurant",
                    "restaurant",
                ], dtype="string"),
                "category_desc": pd.Series([
                    "Todos los locales",
                    "Todos los locales",
                    "Todos los locales",
                    "Todos los locales",
                    "Todos los locales",
                    "Todos los locales",
                    "Todos los locales",
                    "Bar",
                    "Bar",
                    "Restaurante",
                    "Restaurante",
                    "Restaurante",
                ], dtype="string"),
            }
        )

        records = build_hex_composition_history_records(frame, year=2024, period="2024-12")
        hex_8a1 = [row for row in records if row["h3_cell"] == "8a1" and row["category_code"] != "__all__"]
        hex_8a2_restaurant = [
            row for row in records if row["h3_cell"] == "8a2" and row["category_code"] == "restaurant"
        ]

        self.assertEqual(len(hex_8a1), 2)
        self.assertEqual([row["category_code"] for row in hex_8a1], ["bar_cafe", "restaurant"])
        self.assertEqual([row["n_locales"] for row in hex_8a1], [2, 1])
        self.assertEqual([row["hex_total_locales"] for row in hex_8a1], [4, 4])
        self.assertAlmostEqual(hex_8a1[0]["share_in_hex"] or 0.0, 0.5)
        self.assertAlmostEqual(hex_8a1[1]["share_in_hex"] or 0.0, 0.25)
        self.assertEqual(len(hex_8a2_restaurant), 1)
        self.assertEqual(hex_8a2_restaurant[0]["n_locales"], 2)
        self.assertEqual(hex_8a2_restaurant[0]["hex_total_locales"], 3)
        self.assertAlmostEqual(hex_8a2_restaurant[0]["share_in_hex"] or 0.0, 2.0 / 3.0)

    def test_finalize_historical_metric_records_ranks_all_locales_by_share_change(self) -> None:
        rows_2020: list[dict[str, object]] = []
        rows_2024: list[dict[str, object]] = []

        zone_specs = [
            ("01", "Centro", 100, 120),
            ("02", "Salamanca", 60, 100),
            ("03", "Chamberi", 40, 80),
        ]

        next_local_id = 1
        for district_code, district_name, count_2020, count_2024 in zone_specs:
            for _ in range(count_2020):
                rows_2020.append(
                    {
                        "id_local": next_local_id,
                        "snapshot_period": "2020-12",
                        "district_code": district_code,
                        "district_name": district_name,
                        "barrio_code": f"{district_code}001",
                        "barrio_name": f"Barrio {district_name}",
                        "barrio_context_name": district_name,
                        "barrio_key": f"{district_code}001",
                        "category_code": "__all__",
                        "category_desc": "Todos los locales",
                    }
                )
                next_local_id += 1

            for _ in range(count_2024):
                rows_2024.append(
                    {
                        "id_local": next_local_id,
                        "snapshot_period": "2024-12",
                        "district_code": district_code,
                        "district_name": district_name,
                        "barrio_code": f"{district_code}001",
                        "barrio_name": f"Barrio {district_name}",
                        "barrio_context_name": district_name,
                        "barrio_key": f"{district_code}001",
                        "category_code": "__all__",
                        "category_desc": "Todos los locales",
                    }
                )
                next_local_id += 1

        records = build_zone_history_records(pd.DataFrame(rows_2020), zone_level="district", year=2020, period="2020-12")
        records.extend(build_zone_history_records(pd.DataFrame(rows_2024), zone_level="district", year=2024, period="2024-12"))

        finalized = finalize_historical_metric_records(records)
        latest_rows = [row for row in finalized if row["category_code"] == "__all__" and row["year"] == 2024]

        self.assertEqual([row["zone_name"] for row in latest_rows], ["Chamberi", "Salamanca", "Centro"])
        self.assertGreater(latest_rows[0]["metric_value"], latest_rows[1]["metric_value"])
        self.assertGreater(latest_rows[1]["metric_value"], latest_rows[2]["metric_value"])


if __name__ == "__main__":
    unittest.main()
