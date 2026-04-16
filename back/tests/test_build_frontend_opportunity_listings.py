from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from scripts.build_frontend_opportunity_listings import (
    attach_section_context,
    build_frontend_artifacts,
    load_section_profiles_from_index_json,
)


def _sample_section_payload() -> dict[str, object]:
    return {
        "section_key": "01001",
        "district_code": "01",
        "district_name": "Centro",
        "barrio_code": "001",
        "barrio_name": "Palacio",
        "risk_score": 0.12,
        "risk_percentile": 0.34,
        "expected_survival_12m": 0.98,
        "expected_survival_24m": 0.95,
        "opportunity_tier": "Solida",
        "city_rank": 12,
        "city_total_sections": 2461,
        "district_rank": 2,
        "district_total_sections": 110,
        "barrio_rank": 1,
        "barrio_total_sections": 18,
        "renta_effective_eur": 22000.0,
        "renta_reference_year": 2023.0,
        "renta_granularity_used": "section",
        "renta_outlier_adjusted": False,
        "total_population_start": 1000.0,
        "population_density_km2_start": 12000.0,
        "age_mean_start": 42.0,
        "share_foreign_start": 0.2,
        "share_age_15_29_start": 0.15,
        "share_age_65_plus_start": 0.18,
        "metro_distance_m_start": 120.0,
        "metro_access_count_500m_start": 4.0,
        "metro_access_count_1000m_start": 12.0,
        "metro_station_count_500m_start": 1.0,
        "metro_station_count_1000m_start": 3.0,
        "metro_nearest_name_start": "Sol",
        "metro_nearest_station_name_start": "Sol",
        "metro_access_names_500m_start": ["Sol"],
        "metro_access_names_1000m_start": ["Sol", "Callao"],
        "metro_station_names_500m_start": ["Sol"],
        "metro_station_names_1000m_start": ["Sol", "Callao"],
        "avisos_barrio_per_1000_prev_year": 100.0,
        "avisos_district_per_1000_prev_year": 200.0,
        "top_avisos_barrio_categories": [{"rank": 1, "label": "Limpieza", "count": 10, "share_of_zone": 0.5}],
        "top_avisos_district_categories": [{"rank": 1, "label": "Limpieza", "count": 20, "share_of_zone": 0.4}],
        "section_local_count_start": 6.0,
        "section_unique_activity_category_count_start": 3.0,
        "section_turnover_rate_12m_start": 0.1,
        "section_same_activity_category_share_start": 0.2,
        "best_activity_label": "Cafe",
        "best_activity_risk": 0.08,
        "best_activity_survival_24m": 0.93,
        "top_activities": [{"rank": 1, "display_label": "Cafe", "activity_risk": 0.08}],
        "facilities_tier": "Medias",
        "facilities_200m": 1,
        "facilities_500m": 5,
        "facilities_1000m": 12,
        "facilities_by_category": [{"category": "bicimad", "label": "BiciMAD", "count_200m": 1, "count_500m": 2, "count_1000m": 4}],
        "vulnerabilidad_global": 4.5,
        "vulnerabilidad_global_media_ciudad": 4.0,
        "vulnerabilidad_esferas": [{"key": "economia", "label": "Economia", "valor": 5.0, "media_ciudad": 4.2}],
        "inspecciones_distrito_total": 40.0,
        "inspecciones_ciudad_media": 20.0,
        "inspecciones_top_epigrafes": [{"label": "Retail", "count": 10, "share": 0.25}],
        "indicadores_distrito": [{"id": "tasa_paro", "label": "Tasa de paro", "valor": 5.0, "media_ciudad": 5.5}],
    }


class WeeklyOpportunityListingsTests(unittest.TestCase):
    def test_load_section_profiles_from_index_json_normalizes_codes(self) -> None:
        payload = {"meta": {"generated_at": "2026-04-15T18:41:56Z"}, "sections": [_sample_section_payload()]}

        with TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "index.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            frame = load_section_profiles_from_index_json(path)

        self.assertEqual(frame.loc[0, "section_key"], "01001")
        self.assertEqual(frame.loc[0, "district_code"], "01")
        self.assertEqual(frame.loc[0, "barrio_code"], "001")
        self.assertEqual(frame.loc[0, "top_activities"][0]["display_label"], "Cafe")

    def test_attach_section_context_raises_on_missing_section(self) -> None:
        selected = pd.DataFrame(
            [
                {
                    "listing_id": "1",
                    "listing_url": "https://example.com/local1",
                    "card_title": "Local 1",
                    "address_text": "Calle 1",
                    "operation": "alquiler",
                    "price_eur": 1000.0,
                    "price_per_m2_eur": 10.0,
                    "area_m2": 100.0,
                    "lat_wgs84": 40.4,
                    "lon_wgs84": -3.7,
                    "section_key": "99999",
                    "district_code": "01",
                    "district_name": "Centro",
                    "barrio_code": "001",
                    "barrio_name": "Palacio",
                }
            ]
        )
        sections = pd.DataFrame([_sample_section_payload()])

        with self.assertRaisesRegex(ValueError, "could not be matched"):
            attach_section_context(selected, sections)

    def test_build_frontend_artifacts_preserves_existing_section_paths(self) -> None:
        selected = pd.DataFrame(
            [
                {
                    "listing_id": "1",
                    "listing_url": "https://example.com/local1",
                    "card_title": "Local 1",
                    "address_text": "Calle 1",
                    "operation": "alquiler",
                    "price_eur": 1000.0,
                    "price_per_m2_eur": 10.0,
                    "area_m2": 100.0,
                    "lat_wgs84": 40.4,
                    "lon_wgs84": -3.7,
                    "section_key": "01001",
                    "district_code": "01",
                    "district_name": "Centro",
                    "barrio_code": "001",
                    "barrio_name": "Palacio",
                }
            ]
        )
        hydrated = attach_section_context(selected, pd.DataFrame([_sample_section_payload()]))

        payload = build_frontend_artifacts(
            hydrated,
            {"selected_listings": 1, "operations": {"alquiler": 1}},
            existing_meta={
                "title": "Madrid Opportunity Map",
                "subtitle": "Locales disponibles y recomendacion de actividad",
                "section_index_path": "/data/opportunities/sections/index.json?v=stable",
                "section_geojson_path": "/data/opportunities/sections/geometry.geojson?v=stable",
                "map_bounds": {"min_lng": -4.0, "min_lat": 40.0, "max_lng": -3.5, "max_lat": 40.7, "min_zoom": 9.5, "max_zoom": 16.0},
            },
        )

        self.assertEqual(payload["meta"]["section_index_path"], "/data/opportunities/sections/index.json?v=stable")
        self.assertEqual(payload["meta"]["section_geojson_path"], "/data/opportunities/sections/geometry.geojson?v=stable")
        self.assertEqual(len(payload["points"]), 1)
        self.assertEqual(payload["points"][0]["listing_id"], "1")


if __name__ == "__main__":
    unittest.main()
