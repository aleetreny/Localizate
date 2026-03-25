from __future__ import annotations

import unittest

import pandas as pd

from localizate.activity_taxonomy import build_web_taxonomy, classify_epigrafe


class ActivityTaxonomyTests(unittest.TestCase):
    def test_classify_exact_epigrafe_maps_fruteria(self) -> None:
        decision = classify_epigrafe("472102", "COMERCIO AL POR MENOR DE FRUTAS Y HORTALIZAS SIN OBRADOR")

        self.assertEqual(decision.display_label, "Fruteria")
        self.assertTrue(decision.investable)

    def test_classify_keyword_maps_butcher(self) -> None:
        decision = classify_epigrafe("472299", "COMERCIO AL POR MENOR DE CARNICERIA TRADICIONAL")

        self.assertEqual(decision.display_label, "Carniceria y charcuteria")

    def test_build_web_taxonomy_deduplicates_clean_codes(self) -> None:
        frame = pd.DataFrame(
            [
                {"taxonomy": "epigrafe", "code_valid": True, "clean_code": "472102", "clean_desc": "COMERCIO AL POR MENOR DE FRUTAS Y HORTALIZAS SIN OBRADOR", "n": 10},
                {"taxonomy": "epigrafe", "code_valid": True, "clean_code": "472102", "clean_desc": "COMERCIO AL POR MENOR DE FRUTAS Y HORTALIZAS SIN OBRADOR", "n": 8},
            ]
        )

        mapped = build_web_taxonomy(frame)

        self.assertEqual(len(mapped), 1)
        self.assertEqual(mapped.iloc[0]["display_label"], "Fruteria")


if __name__ == "__main__":
    unittest.main()