from __future__ import annotations

import math
import unittest

import pandas as pd

from scripts.build_frontend_opportunity_artifacts import (
    build_avisos_top_category_lookup,
    build_section_index_payload,
    build_sections_geojson,
    normalize_avisos_category_frame,
    serialize_avisos_top_categories,
)


class DummyGeometry:
    @property
    def __geo_interface__(self) -> dict[str, object]:
        return {
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [0.5, 0.0], [0.5, 0.5], [0.0, 0.0]]],
        }


class FrontendOpportunityArtifactsTests(unittest.TestCase):
    def test_normalize_avisos_category_frame_uses_modern_category_level(self) -> None:
        frame = pd.DataFrame(
            {
                "DISTRITO_ID": [1, 1],
                "BARRIO_ID": [1, 1],
                "CATEGORIA_NIVEL1": ["Retirada de elementos", "Limpieza y pintadas"],
            }
        )

        normalized = normalize_avisos_category_frame(frame)

        self.assertEqual(normalized["district_code"].tolist(), ["01", "01"])
        self.assertEqual(normalized["barrio_code"].tolist(), ["011", "011"])
        self.assertEqual(normalized["category_label"].tolist(), ["Retirada de elementos", "Limpieza y pintadas"])

    def test_normalize_avisos_category_frame_falls_back_to_legacy_schema(self) -> None:
        frame = pd.DataFrame(
            {
                "DISTRITO_ID": [2],
                "BARRIO_ID": [4],
                "SECCION": ["Incidencias y peticiones"],
            }
        )

        normalized = normalize_avisos_category_frame(frame)

        self.assertEqual(normalized.loc[0, "district_code"], "02")
        self.assertEqual(normalized.loc[0, "barrio_code"], "024")
        self.assertEqual(normalized.loc[0, "category_label"], "Incidencias y peticiones")

    def test_build_avisos_top_category_lookup_returns_top_three_with_share(self) -> None:
        frame = pd.DataFrame(
            {
                "district_code": ["01"] * 6,
                "category_label": [
                    "Retirada de elementos",
                    "Retirada de elementos",
                    "Retirada de elementos",
                    "Cubos y contenedores",
                    "Cubos y contenedores",
                    "Limpieza y pintadas",
                ],
            }
        )

        lookup = build_avisos_top_category_lookup(frame, zone_cols=["district_code"], output_col="top_categories")
        categories = lookup.loc[0, "top_categories"]

        self.assertEqual(len(categories), 3)
        self.assertEqual([item["rank"] for item in categories], [1, 2, 3])
        self.assertEqual([item["label"] for item in categories], [
            "Retirada de elementos",
            "Cubos y contenedores",
            "Limpieza y pintadas",
        ])
        self.assertEqual([item["count"] for item in categories], [3, 2, 1])
        self.assertTrue(math.isclose(categories[0]["share_of_zone"] or 0.0, 0.5))
        self.assertTrue(math.isclose(categories[1]["share_of_zone"] or 0.0, 2.0 / 6.0))

    def test_serialize_avisos_top_categories_skips_invalid_rows(self) -> None:
        serialized = serialize_avisos_top_categories(
            [
                {"rank": 1, "label": "Retirada de elementos", "count": 42, "share_of_zone": 0.42},
                {"rank": 2, "label": " ", "count": 10, "share_of_zone": 0.1},
                "invalid",
            ]
        )

        self.assertEqual(serialized, [
            {"rank": 1, "label": "Retirada de elementos", "count": 42, "share_of_zone": 0.42}
        ])

    def test_section_index_keeps_full_payload_while_geojson_stays_minimal(self) -> None:
        section_profiles = pd.DataFrame(
            [
                {
                    "section_key": "00001",
                    "district_code": "01",
                    "district_name": "Centro",
                    "barrio_code": "001",
                    "barrio_name": "Sol",
                    "centroid_lat": 40.4168,
                    "centroid_lon": -3.7038,
                    "risk_score": 0.21,
                    "risk_percentile": 0.62,
                    "expected_survival_12m": 0.81,
                    "expected_survival_24m": 0.66,
                    "opportunity_tier": "Alta",
                    "city_rank": 12,
                    "city_total_sections": 2400,
                    "district_rank": 4,
                    "district_total_sections": 180,
                    "barrio_rank": 2,
                    "barrio_total_sections": 24,
                    "geometry": DummyGeometry(),
                }
            ]
        )

        section_index = build_section_index_payload(section_profiles)
        geojson = build_sections_geojson(section_profiles)

        self.assertEqual(section_index["sections"][0]["section_key"], "00001")
        self.assertIn("risk_score", section_index["sections"][0])
        self.assertEqual(geojson["features"][0]["properties"]["section_key"], "00001")
        self.assertNotIn("risk_score", geojson["features"][0]["properties"])


if __name__ == "__main__":
    unittest.main()
