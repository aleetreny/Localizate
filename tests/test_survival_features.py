from __future__ import annotations

import unittest

import pandas as pd

from localizate.survival_features import (
    _fix_metro_mojibake,
    _normalize_metro_station_name,
    attach_avisos_features,
    attach_external_district_features,
    compute_metro_features,
    get_model_feature_columns,
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

    def test_compute_metro_features_counts_unique_stations_separately_from_accesses(self) -> None:
        abt = pd.DataFrame(
            {
                "lat_wgs84_start": [40.0],
                "lon_wgs84_start": [-3.0],
            }
        )
        metro = pd.DataFrame(
            {
                "metro_lat": [40.0, 40.0004, 40.0008],
                "metro_lon": [-3.0, -3.0, -3.0],
                "metro_display_name": ["Acceso A", "Acceso B", "Acceso C"],
                "metro_station_name": ["Sol", "Sol", "Gran Vía"],
            }
        )

        features = compute_metro_features(abt, metro_reference=metro, include_names=True)

        self.assertEqual(float(features.loc[0, "metro_access_count_500m_start"]), 3.0)
        self.assertEqual(float(features.loc[0, "metro_station_count_500m_start"]), 2.0)
        self.assertEqual(features.loc[0, "metro_station_names_500m_start"], ["Sol", "Gran Vía"])

    def test_fix_metro_mojibake_recovers_common_station_strings(self) -> None:
        cases = {
            "AlcorcÃ³n Central": "Alcorcón Central",
            "TetuÃ¡n": "Tetuán",
            "ChamartÃ­n": "Chamartín",
            "EstaciÃ³n del Arte": "Estación del Arte",
            "AntÃ³n MartÃ­n": "Antón Martín",
            "Gran VÃ­a": "Gran Vía",
            "RÃ­os Rosas": "Ríos Rosas",
            "Ã“pera": "Ópera",
            "ArgÃ¼elles": "Argüelles",
            "NÃºÃ±ez de Balboa": "Núñez de Balboa",
            "RubÃ©n DarÃ­o": "Rubén Darío",
            "Sol": "Sol",
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(_fix_metro_mojibake(raw), expected)

    def test_normalize_metro_station_name_never_raises_on_mixed_inputs(self) -> None:
        samples = [None, float("nan"), pd.NA, "", " ", "Sol", "Ã“pera", 123, "RubÃ©n DarÃ­o"]
        for sample in samples:
            with self.subTest(sample=sample):
                try:
                    normalized = _normalize_metro_station_name(sample)
                except Exception as exc:  # pragma: no cover - explicit safety guarantee
                    self.fail(f"_normalize_metro_station_name raised unexpectedly for {sample!r}: {exc}")
                should_be_na = sample is None or sample is pd.NA
                should_be_na = should_be_na or (isinstance(sample, float) and pd.isna(sample))
                should_be_na = should_be_na or (isinstance(sample, str) and not sample.strip())
                if should_be_na:
                    self.assertTrue(pd.isna(normalized))

    def test_get_model_feature_columns_only_exposes_external_features_in_candidate_profiles(self) -> None:
        self.assertNotIn("district_panel_locales_open_start", get_model_feature_columns(feature_profile="full"))
        self.assertNotIn(
            "district_panel_locales_open_start",
            get_model_feature_columns(feature_profile="activity_survival_pruned"),
        )
        self.assertIn(
            "district_panel_locales_open_start",
            get_model_feature_columns(feature_profile="full_with_external"),
        )
        self.assertIn(
            "district_panel_locales_open_start",
            get_model_feature_columns(feature_profile="activity_survival_pruned_with_external"),
        )

    def test_attach_external_district_features_uses_backward_lagged_join(self) -> None:
        abt = pd.DataFrame(
            {
                "first_seen_period": ["2022-05", "2023-01", "2015-07"],
                "district_code_start": ["01", "01", "02"],
            }
        )
        panel_yearly = pd.DataFrame(
            {
                "panel_year": [2020, 2021, 2022],
                "district_code": ["01", "01", "02"],
                "district_panel_locales_open_start": [10.0, 20.0, 30.0],
            }
        )
        iguala_yearly = pd.DataFrame(
            {
                "iguala_year": [2021, 2022],
                "district_code": ["01", "02"],
                "district_iguala_vulnerability_global_start": [4.5, 6.0],
            }
        )

        enriched = attach_external_district_features(
            abt,
            panel_yearly=panel_yearly,
            iguala_yearly=iguala_yearly,
        )

        self.assertEqual(int(enriched.loc[0, "district_panel_year_start"]), 2021)
        self.assertEqual(float(enriched.loc[0, "district_panel_locales_open_start"]), 20.0)
        self.assertEqual(float(enriched.loc[0, "district_panel_lag_years_start"]), 0.0)
        self.assertEqual(int(enriched.loc[1, "district_panel_year_start"]), 2021)
        self.assertEqual(float(enriched.loc[1, "district_panel_lag_years_start"]), 1.0)
        self.assertEqual(float(enriched.loc[0, "district_iguala_vulnerability_global_start"]), 4.5)
        self.assertTrue(pd.isna(enriched.loc[2, "district_panel_year_start"]))
        self.assertTrue(pd.isna(enriched.loc[2, "district_iguala_year_start"]))

    def test_attach_external_district_features_preserves_existing_district_code_column(self) -> None:
        abt = pd.DataFrame(
            {
                "first_seen_period": ["2022-05"],
                "district_code_start": ["01"],
                "district_code": ["01"],
            }
        )
        panel_yearly = pd.DataFrame(
            {
                "panel_year": [2021],
                "district_code": ["01"],
                "district_panel_locales_open_start": [20.0],
            }
        )

        enriched = attach_external_district_features(
            abt,
            panel_yearly=panel_yearly,
            iguala_yearly=pd.DataFrame(columns=["iguala_year", "district_code"]),
        )

        self.assertEqual(str(enriched.loc[0, "district_code"]), "01")
        self.assertEqual(int(enriched.loc[0, "district_panel_year_start"]), 2021)
        self.assertEqual(float(enriched.loc[0, "district_panel_locales_open_start"]), 20.0)


if __name__ == "__main__":
    unittest.main()
