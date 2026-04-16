from __future__ import annotations

import unittest

import duckdb
import pandas as pd

from localizate.abt_survival import (
    _materialize_activity_period_tables,
    _build_activity_lookup,
    next_period,
    normalize_activity_code,
    normalize_activity_description,
    resolve_survival_target,
)


class AbtSurvivalTests(unittest.TestCase):
    def test_next_period_advances_month(self) -> None:
        self.assertEqual(next_period("2026-03"), "2026-04")

    def test_next_period_handles_year_rollover(self) -> None:
        self.assertEqual(next_period("2026-12"), "2027-01")

    def test_normalize_activity_description_repairs_common_encoding_noise(self) -> None:
        self.assertEqual(normalize_activity_description("Educaci0n"), "EDUCACION")
        self.assertEqual(
            normalize_activity_description("REPARACI\u00d3N de ordenadores"),
            "REPARACION DE ORDENADORES",
        )

    def test_normalize_activity_code_collapses_decimal_strings(self) -> None:
        self.assertEqual(normalize_activity_code("47.0", min_numeric=1, max_numeric=99), "47")
        self.assertEqual(normalize_activity_code("PT", min_numeric=1, max_numeric=99), "PT")
        self.assertIsNone(normalize_activity_code("561005", min_numeric=1, max_numeric=99))

    def test_build_activity_lookup_remaps_invalid_division_code_by_description(self) -> None:
        summary = pd.DataFrame(
            {
                "raw_code": ["56", "56.0", "561005", "PT"],
                "raw_desc": [
                    "SERVICIOS DE COMIDAS Y BEBIDAS",
                    "SERVICIOS DE COMIDAS Y BEBIDAS",
                    "SERVICIOS DE COMIDAS Y BEBIDAS",
                    "SIN ACTIVIDAD PTE. DE CODIFICAR",
                ],
                "n": [100, 50, 3, 8],
            }
        )

        lookup = _build_activity_lookup(
            summary,
            taxonomy="division",
            min_numeric=1,
            max_numeric=99,
            placeholder_codes=frozenset({"", "0", "-1", "PT"}),
        )

        remapped = lookup.loc[lookup["raw_code"] == "561005"].iloc[0]
        placeholder = lookup.loc[lookup["raw_code"] == "PT"].iloc[0]

        self.assertEqual(remapped["clean_code"], "56")
        self.assertEqual(remapped["mapping_reason"], "description_remap")
        self.assertTrue(bool(remapped["code_valid"]))
        self.assertEqual(placeholder["mapping_reason"], "placeholder")
        self.assertFalse(bool(placeholder["code_valid"]))

    def test_activity_periods_keep_macro_when_epigrafe_is_valid_but_division_is_not(self) -> None:
        activities_clean = pd.DataFrame(
            {
                "id_local": [1, 2],
                "period": ["2024-01", "2024-01"],
                "division_code": [None, "47"],
                "division_desc": [None, "COMERCIO AL POR MENOR"],
                "division_valid": [False, True],
                "epigrafe_code": ["561005", "561006"],
                "epigrafe_desc": ["BAR CON COCINA", "CAFETERIA"],
                "epigrafe_valid": [True, True],
                "macro_category_code": ["bar_cafe", "bar_cafe"],
                "macro_category_name": ["Bar y cafetería", "Bar y cafetería"],
            }
        )

        con = duckdb.connect()
        try:
            con.register("activities_clean_df", activities_clean)
            con.execute("CREATE OR REPLACE TABLE activities_clean AS SELECT * FROM activities_clean_df")
            _materialize_activity_period_tables(con)
            periods = con.execute(
                """
                SELECT id_local, period, n_divisions, n_epigrafes, n_macro_categories, macro_category_sig
                FROM activity_periods
                ORDER BY id_local
                """
            ).df()
        finally:
            con.close()

        first = periods.iloc[0]
        second = periods.iloc[1]

        self.assertEqual(first["id_local"], 1)
        self.assertEqual(first["n_divisions"], 0)
        self.assertEqual(first["n_epigrafes"], 1)
        self.assertEqual(first["n_macro_categories"], 1)
        self.assertEqual(first["macro_category_sig"], "bar_cafe")

        self.assertEqual(second["id_local"], 2)
        self.assertEqual(second["n_divisions"], 1)
        self.assertEqual(second["n_epigrafes"], 1)
        self.assertEqual(second["n_macro_categories"], 1)

    def test_local_feature_context_falls_back_to_same_period_when_tminus1_missing(self) -> None:
        local_activity_enriched = pd.DataFrame(
            {
                "id_local": [101],
                "period": ["2015-01"],
                "section_key": ["01001"],
                "division_code_start": ["56"],
                "activity_category_code_start": ["bar_cafe"],
            }
        )
        section_period_features = pd.DataFrame(
            {
                "period": ["2015-01"],
                "section_key": ["01001"],
                "section_local_count": [100],
            }
        )
        section_division_features = pd.DataFrame(
            {
                "period": ["2015-01"],
                "section_key": ["01001"],
                "division_code_start": ["56"],
                "section_same_division_local_count": [20],
            }
        )
        section_activity_category_features = pd.DataFrame(
            {
                "period": ["2015-01"],
                "section_key": ["01001"],
                "activity_category_code_start": ["bar_cafe"],
                "section_same_activity_category_local_count": [30],
            }
        )

        con = duckdb.connect()
        try:
            con.register("local_activity_enriched_df", local_activity_enriched)
            con.register("section_period_features_df", section_period_features)
            con.register("section_division_features_df", section_division_features)
            con.register("section_activity_category_features_df", section_activity_category_features)
            con.execute("CREATE OR REPLACE TABLE local_activity_enriched AS SELECT * FROM local_activity_enriched_df")
            con.execute("CREATE OR REPLACE TABLE section_period_features AS SELECT * FROM section_period_features_df")
            con.execute("CREATE OR REPLACE TABLE section_division_features AS SELECT * FROM section_division_features_df")
            con.execute(
                "CREATE OR REPLACE TABLE section_activity_category_features AS SELECT * FROM section_activity_category_features_df"
            )

            resolved = con.execute(
                """
                WITH lagged_context AS (
                    SELECT
                        *,
                        STRFTIME(CAST(period || '-01' AS DATE) - INTERVAL 1 MONTH, '%Y-%m') AS context_period
                    FROM local_activity_enriched
                ), context_enriched AS (
                    SELECT
                        l.*,
                        COALESCE(s_prev.section_local_count, s_curr.section_local_count) AS section_local_count,
                        COALESCE(d_prev.section_same_division_local_count, d_curr.section_same_division_local_count) AS section_same_division_local_count,
                        COALESCE(a_prev.section_same_activity_category_local_count, a_curr.section_same_activity_category_local_count) AS section_same_activity_category_local_count
                    FROM lagged_context l
                    LEFT JOIN section_period_features s_prev
                        ON l.context_period = s_prev.period
                       AND l.section_key = s_prev.section_key
                    LEFT JOIN section_period_features s_curr
                        ON l.period = s_curr.period
                       AND l.section_key = s_curr.section_key
                    LEFT JOIN section_division_features d_prev
                        ON l.context_period = d_prev.period
                       AND l.section_key = d_prev.section_key
                       AND l.division_code_start = d_prev.division_code_start
                    LEFT JOIN section_division_features d_curr
                        ON l.period = d_curr.period
                       AND l.section_key = d_curr.section_key
                       AND l.division_code_start = d_curr.division_code_start
                    LEFT JOIN section_activity_category_features a_prev
                        ON l.context_period = a_prev.period
                       AND l.section_key = a_prev.section_key
                       AND l.activity_category_code_start = a_prev.activity_category_code_start
                    LEFT JOIN section_activity_category_features a_curr
                        ON l.period = a_curr.period
                       AND l.section_key = a_curr.section_key
                       AND l.activity_category_code_start = a_curr.activity_category_code_start
                )
                SELECT
                    section_local_count,
                    section_same_division_local_count,
                    section_same_activity_category_local_count,
                    CASE
                        WHEN section_local_count IS NULL OR section_local_count = 0 OR section_same_division_local_count IS NULL THEN NULL
                        ELSE CAST(section_same_division_local_count AS DOUBLE) / CAST(section_local_count AS DOUBLE)
                    END AS section_same_division_share,
                    CASE
                        WHEN section_local_count IS NULL OR section_local_count = 0 OR section_same_activity_category_local_count IS NULL THEN NULL
                        ELSE CAST(section_same_activity_category_local_count AS DOUBLE) / CAST(section_local_count AS DOUBLE)
                    END AS section_same_activity_category_share
                FROM context_enriched
                """
            ).df().iloc[0]
        finally:
            con.close()

        self.assertEqual(int(resolved["section_local_count"]), 100)
        self.assertEqual(int(resolved["section_same_division_local_count"]), 20)
        self.assertEqual(int(resolved["section_same_activity_category_local_count"]), 30)
        self.assertAlmostEqual(float(resolved["section_same_division_share"]), 0.2)
        self.assertAlmostEqual(float(resolved["section_same_activity_category_share"]), 0.3)

    def test_local_feature_context_falls_back_to_same_period_when_tminus1_is_zero(self) -> None:
        local_activity_enriched = pd.DataFrame(
            {
                "id_local": [101],
                "period": ["2018-03"],
                "section_key": ["08151"],
                "division_code_start": ["56"],
                "activity_category_code_start": ["bar_cafe"],
            }
        )
        section_period_features = pd.DataFrame(
            {
                "period": ["2018-02", "2018-03"],
                "section_key": ["08151", "08151"],
                "section_local_count": [0, 12],
                "section_unique_division_count": [0, 4],
                "section_unique_activity_category_count": [0, 5],
            }
        )
        section_division_features = pd.DataFrame(
            {
                "period": ["2018-02", "2018-03"],
                "section_key": ["08151", "08151"],
                "division_code_start": ["56", "56"],
                "section_same_division_local_count": [0, 3],
            }
        )
        section_activity_category_features = pd.DataFrame(
            {
                "period": ["2018-02", "2018-03"],
                "section_key": ["08151", "08151"],
                "activity_category_code_start": ["bar_cafe", "bar_cafe"],
                "section_same_activity_category_local_count": [0, 4],
            }
        )

        con = duckdb.connect()
        try:
            con.register("local_activity_enriched_df", local_activity_enriched)
            con.register("section_period_features_df", section_period_features)
            con.register("section_division_features_df", section_division_features)
            con.register("section_activity_category_features_df", section_activity_category_features)
            con.execute("CREATE OR REPLACE TABLE local_activity_enriched AS SELECT * FROM local_activity_enriched_df")
            con.execute("CREATE OR REPLACE TABLE section_period_features AS SELECT * FROM section_period_features_df")
            con.execute("CREATE OR REPLACE TABLE section_division_features AS SELECT * FROM section_division_features_df")
            con.execute(
                "CREATE OR REPLACE TABLE section_activity_category_features AS SELECT * FROM section_activity_category_features_df"
            )

            resolved = con.execute(
                """
                WITH lagged_context AS (
                    SELECT
                        *,
                        STRFTIME(CAST(period || '-01' AS DATE) - INTERVAL 1 MONTH, '%Y-%m') AS context_period
                    FROM local_activity_enriched
                ), context_enriched AS (
                    SELECT
                        l.*,
                        CASE
                            WHEN COALESCE(s_prev.section_local_count, 0) <= 0
                                 AND COALESCE(s_curr.section_local_count, 0) > 0
                                THEN s_curr.section_local_count
                            ELSE COALESCE(s_prev.section_local_count, s_curr.section_local_count)
                        END AS section_local_count,
                        CASE
                            WHEN COALESCE(s_prev.section_unique_division_count, 0) <= 0
                                 AND COALESCE(s_curr.section_unique_division_count, 0) > 0
                                THEN s_curr.section_unique_division_count
                            ELSE COALESCE(s_prev.section_unique_division_count, s_curr.section_unique_division_count)
                        END AS section_unique_division_count,
                        CASE
                            WHEN COALESCE(s_prev.section_unique_activity_category_count, 0) <= 0
                                 AND COALESCE(s_curr.section_unique_activity_category_count, 0) > 0
                                THEN s_curr.section_unique_activity_category_count
                            ELSE COALESCE(s_prev.section_unique_activity_category_count, s_curr.section_unique_activity_category_count)
                        END AS section_unique_activity_category_count,
                        CASE
                            WHEN COALESCE(d_prev.section_same_division_local_count, 0) <= 0
                                 AND COALESCE(d_curr.section_same_division_local_count, 0) > 0
                                THEN d_curr.section_same_division_local_count
                            ELSE COALESCE(d_prev.section_same_division_local_count, d_curr.section_same_division_local_count)
                        END AS section_same_division_local_count,
                        CASE
                            WHEN COALESCE(a_prev.section_same_activity_category_local_count, 0) <= 0
                                 AND COALESCE(a_curr.section_same_activity_category_local_count, 0) > 0
                                THEN a_curr.section_same_activity_category_local_count
                            ELSE COALESCE(a_prev.section_same_activity_category_local_count, a_curr.section_same_activity_category_local_count)
                        END AS section_same_activity_category_local_count
                    FROM lagged_context l
                    LEFT JOIN section_period_features s_prev
                        ON l.context_period = s_prev.period
                       AND l.section_key = s_prev.section_key
                    LEFT JOIN section_period_features s_curr
                        ON l.period = s_curr.period
                       AND l.section_key = s_curr.section_key
                    LEFT JOIN section_division_features d_prev
                        ON l.context_period = d_prev.period
                       AND l.section_key = d_prev.section_key
                       AND l.division_code_start = d_prev.division_code_start
                    LEFT JOIN section_division_features d_curr
                        ON l.period = d_curr.period
                       AND l.section_key = d_curr.section_key
                       AND l.division_code_start = d_curr.division_code_start
                    LEFT JOIN section_activity_category_features a_prev
                        ON l.context_period = a_prev.period
                       AND l.section_key = a_prev.section_key
                       AND l.activity_category_code_start = a_prev.activity_category_code_start
                    LEFT JOIN section_activity_category_features a_curr
                        ON l.period = a_curr.period
                       AND l.section_key = a_curr.section_key
                       AND l.activity_category_code_start = a_curr.activity_category_code_start
                )
                SELECT
                    section_local_count,
                    section_unique_division_count,
                    section_unique_activity_category_count,
                    section_same_division_local_count,
                    section_same_activity_category_local_count
                FROM context_enriched
                """
            ).df().iloc[0]
        finally:
            con.close()

        self.assertEqual(int(resolved["section_local_count"]), 12)
        self.assertEqual(int(resolved["section_unique_division_count"]), 4)
        self.assertEqual(int(resolved["section_unique_activity_category_count"]), 5)
        self.assertEqual(int(resolved["section_same_division_local_count"]), 3)
        self.assertEqual(int(resolved["section_same_activity_category_local_count"]), 4)

    def test_resolve_survival_target_prioritizes_earliest_change_event(self) -> None:
        resolved = resolve_survival_target(
            first_seen_period="2020-01",
            last_observed_period="2020-06",
            max_period="2020-12",
            change_event_period="2020-03",
        )

        self.assertEqual(resolved["event_source"], "cese_de_actividad")
        self.assertEqual(resolved["event_subtype"], "cambio_actividad")
        self.assertEqual(resolved["event_period"], "2020-03")
        self.assertEqual(resolved["duration_months"], 3)

    def test_resolve_survival_target_accepts_activity_change_source(self) -> None:
        resolved = resolve_survival_target(
            first_seen_period="2020-01",
            last_observed_period="2020-06",
            max_period="2020-12",
            change_event_period="2020-04",
            change_event_source="activity_category_change_single_single",
        )

        self.assertEqual(resolved["event_source"], "cese_de_actividad")
        self.assertEqual(resolved["event_subtype"], "cambio_actividad")
        self.assertEqual(resolved["event_subtype_detail"], "activity_category_change_single_single")
        self.assertEqual(resolved["event_period"], "2020-04")

    def test_resolve_survival_target_falls_back_to_disappearance(self) -> None:
        resolved = resolve_survival_target(
            first_seen_period="2020-01",
            last_observed_period="2020-06",
            max_period="2020-12",
            change_event_period=None,
        )

        self.assertEqual(resolved["event_source"], "cese_de_actividad")
        self.assertEqual(resolved["event_subtype"], "desaparicion")
        self.assertEqual(resolved["event_period"], "2020-06")
        self.assertEqual(resolved["duration_months"], 6)

    def test_section_key_resolution_prefers_district_consistent_candidates(self) -> None:
        local_rows = pd.DataFrame(
            {
                "id_local": [1, 2, 3, 4, 5],
                "period": ["2024-10", "2024-10", "2024-10", "2024-11", "2024-11"],
                "district_digits": ["18", "20", "99", "06", ""],
                "section_digits": ["180460", "2032", "2032", "60290", "60290"],
            }
        )
        panel_rows = pd.DataFrame(
            {
                "target_period": ["2024-10", "2024-10", "2024-10", "2024-10"],
                "section_key": ["18046", "20032", "02032", "20032"],
            }
        )

        con = duckdb.connect()
        try:
            con.register("local_rows_df", local_rows)
            con.register("section_panel_df", panel_rows)
            con.execute("CREATE OR REPLACE TABLE local_base_raw AS SELECT * FROM local_rows_df")
            con.execute("CREATE OR REPLACE TABLE section_panel AS SELECT * FROM section_panel_df")
            resolved = con.execute(
                """
                WITH candidates AS (
                    SELECT
                        r.*,
                        CASE
                            WHEN district_digits IS NULL OR district_digits = '' OR section_digits IS NULL OR section_digits = '' THEN NULL
                            WHEN LENGTH(section_digits) >= 5 THEN RIGHT(section_digits, 5)
                            WHEN LENGTH(section_digits) = 4 THEN LPAD(section_digits, 5, '0')
                            ELSE LPAD(district_digits, 2, '0') || LPAD(section_digits, 3, '0')
                        END AS section_key_current,
                        CASE
                            WHEN section_digits IS NULL OR section_digits = '' THEN NULL
                            WHEN LENGTH(section_digits) >= 5 AND RIGHT(section_digits, 1) = '0'
                                THEN LPAD(RIGHT(LEFT(section_digits, LENGTH(section_digits) - 1), 5), 5, '0')
                            ELSE NULL
                        END AS section_key_drop_trailing_zero,
                        CASE
                            WHEN district_digits IS NULL OR district_digits = '' OR section_digits IS NULL OR section_digits = '' THEN NULL
                            ELSE LPAD(district_digits, 2, '0') || RIGHT('000' || section_digits, 3)
                        END AS section_key_district_tail3,
                        CASE
                            WHEN district_digits IS NULL OR district_digits = '' OR section_digits IS NULL OR section_digits = '' THEN NULL
                            WHEN LENGTH(section_digits) >= 5 AND RIGHT(section_digits, 1) = '0'
                                THEN LPAD(district_digits, 2, '0') || RIGHT('000' || LEFT(section_digits, LENGTH(section_digits) - 1), 3)
                            ELSE NULL
                        END AS section_key_district_tail3_drop
                    FROM local_base_raw r
                ), resolved AS (
                    SELECT
                        c.id_local,
                        COALESCE(
                            CASE WHEN sp_district_tail3_drop.section_key IS NOT NULL THEN c.section_key_district_tail3_drop END,
                            CASE WHEN sp_district_tail3.section_key IS NOT NULL THEN c.section_key_district_tail3 END,
                            CASE WHEN sp_drop_trailing_zero.section_key IS NOT NULL THEN c.section_key_drop_trailing_zero END,
                            CASE WHEN sp_current.section_key IS NOT NULL THEN c.section_key_current END,
                            c.section_key_district_tail3_drop,
                            c.section_key_district_tail3,
                            c.section_key_drop_trailing_zero,
                            c.section_key_current
                        ) AS section_key
                    FROM candidates c
                    LEFT JOIN section_panel sp_district_tail3_drop
                        ON c.period = sp_district_tail3_drop.target_period
                       AND c.section_key_district_tail3_drop = sp_district_tail3_drop.section_key
                    LEFT JOIN section_panel sp_district_tail3
                        ON c.period = sp_district_tail3.target_period
                       AND c.section_key_district_tail3 = sp_district_tail3.section_key
                    LEFT JOIN section_panel sp_drop_trailing_zero
                        ON c.period = sp_drop_trailing_zero.target_period
                       AND c.section_key_drop_trailing_zero = sp_drop_trailing_zero.section_key
                    LEFT JOIN section_panel sp_current
                        ON c.period = sp_current.target_period
                       AND c.section_key_current = sp_current.section_key
                )
                SELECT id_local, section_key
                FROM resolved
                ORDER BY id_local
                """
            ).df()
        finally:
            con.close()

        resolved_map = {int(row.id_local): str(row.section_key) for row in resolved.itertuples(index=False)}
        self.assertEqual(resolved_map[1], "18046")
        self.assertEqual(resolved_map[2], "20032")
        self.assertEqual(resolved_map[3], "02032")
        self.assertEqual(resolved_map[4], "06029")
        self.assertEqual(resolved_map[5], "06029")


if __name__ == "__main__":
    unittest.main()
