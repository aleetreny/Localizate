from __future__ import annotations

import unittest

import pandas as pd

from localizate.abt_survival import (
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

    def test_resolve_survival_target_prioritizes_earliest_change_event(self) -> None:
        resolved = resolve_survival_target(
            first_seen_period="2020-01",
            last_observed_period="2020-06",
            max_period="2020-12",
            change_event_period="2020-03",
        )

        self.assertEqual(resolved["event_source"], "division_change_single_single")
        self.assertEqual(resolved["event_period"], "2020-03")
        self.assertEqual(resolved["duration_months"], 3)

    def test_resolve_survival_target_falls_back_to_disappearance(self) -> None:
        resolved = resolve_survival_target(
            first_seen_period="2020-01",
            last_observed_period="2020-06",
            max_period="2020-12",
            change_event_period=None,
        )

        self.assertEqual(resolved["event_source"], "disappearance")
        self.assertEqual(resolved["event_period"], "2020-06")
        self.assertEqual(resolved["duration_months"], 6)


if __name__ == "__main__":
    unittest.main()
