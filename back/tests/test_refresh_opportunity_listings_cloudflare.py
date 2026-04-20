from __future__ import annotations

from pathlib import Path
import sys
import unittest

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scripts.refresh_opportunity_listings_cloudflare import (  # noqa: E402
    build_snapshot_refresh_plan,
    normalize_match_text,
)


def _current_card(address_text: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source_portal": "locales.es",
                "city_slug": "madrid",
                "operation": "venta",
                "page_number": 1,
                "listing_id": "123",
                "listing_key": "venta:123",
                "listing_url": "https://www.locales.es/madrid/venta/local123",
                "contact_url": pd.NA,
                "card_title": "Local comercial en Venta en calle de alcala, Madrid",
                "detail_title": pd.NA,
                "product_name": pd.NA,
                "listing_type": "local_comercial",
                "advertiser_type": "De inmobiliaria",
                "price_eur": 150000.0,
                "price_per_m2_eur": 1500.0,
                "area_m2": 100.0,
                "bathroom_count": 1.0,
                "tag_list": pd.NA,
                "description_short": "Descripcion",
                "description_full": pd.NA,
                "breadcrumb_zone": pd.NA,
                "breadcrumb_path": pd.NA,
                "address_text": address_text,
                "geocode_query": pd.NA,
                "geocode_status": pd.NA,
                "coord_source": pd.NA,
                "coord_precision": pd.NA,
                "geocode_display_name": pd.NA,
                "lat_wgs84": pd.NA,
                "lon_wgs84": pd.NA,
                "h3_cell": pd.NA,
                "h3_resolution": pd.NA,
                "section_key": pd.NA,
                "district_code": pd.NA,
                "district_name": pd.NA,
                "barrio_code": pd.NA,
                "barrio_name": pd.NA,
                "published_at": pd.NA,
                "modified_at": pd.NA,
                "detail_fetch_status": "card_only",
            }
        ]
    )


def _previous_snapshot(address_text: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source_portal": "locales.es",
                "city_slug": "madrid",
                "operation": "venta",
                "page_number": 1,
                "listing_id": "123",
                "listing_key": "venta:123",
                "listing_url": "https://www.locales.es/madrid/venta/local123",
                "contact_url": pd.NA,
                "card_title": "Local comercial en Venta en calle de Alcala, Madrid",
                "detail_title": pd.NA,
                "product_name": pd.NA,
                "listing_type": "local_comercial",
                "advertiser_type": "De inmobiliaria",
                "price_eur": 149000.0,
                "price_per_m2_eur": 1490.0,
                "area_m2": 100.0,
                "bathroom_count": 1.0,
                "tag_list": pd.NA,
                "description_short": "Descripcion",
                "description_full": pd.NA,
                "breadcrumb_zone": pd.NA,
                "breadcrumb_path": pd.NA,
                "address_text": address_text,
                "geocode_query": "Calle de Alcala, Madrid, España",
                "geocode_status": "ok",
                "coord_source": "nominatim",
                "coord_precision": "street_approx",
                "geocode_display_name": "Calle de Alcala, Madrid, España",
                "lat_wgs84": 40.42,
                "lon_wgs84": -3.68,
                "h3_cell": "8a390ca0007ffff",
                "h3_resolution": 10.0,
                "section_key": "04055",
                "district_code": "04",
                "district_name": "Salamanca",
                "barrio_code": "055",
                "barrio_name": "Goya",
                "published_at": pd.NA,
                "modified_at": pd.NA,
                "detail_fetch_status": "ok",
            }
        ]
    )


class RefreshOpportunityListingsCloudflareTests(unittest.TestCase):
    def test_normalize_match_text_ignores_accents_and_case(self) -> None:
        self.assertEqual(
            normalize_match_text("Calle de Alcalá, Madrid"),
            normalize_match_text("  calle de alcala madrid "),
        )

    def test_build_snapshot_refresh_plan_reuses_existing_context_for_same_location(self) -> None:
        plan = build_snapshot_refresh_plan(
            _current_card("Calle de Alcalá, Madrid"),
            _previous_snapshot("calle de alcala, madrid"),
        )

        self.assertEqual(plan.reused_context_count, 1)
        self.assertEqual(plan.geocode_row_indexes, ())
        self.assertEqual(plan.frame.loc[0, "section_key"], "04055")
        self.assertEqual(plan.frame.loc[0, "geocode_status"], "ok")

    def test_build_snapshot_refresh_plan_flags_relocated_listing_for_geocode(self) -> None:
        plan = build_snapshot_refresh_plan(
            _current_card("Calle de Serrano, Madrid"),
            _previous_snapshot("Calle de Alcalá, Madrid"),
        )

        self.assertEqual(plan.reused_context_count, 0)
        self.assertEqual(plan.geocode_row_indexes, (0,))
        self.assertTrue(pd.isna(plan.frame.loc[0, "section_key"]))
        self.assertTrue(pd.isna(plan.frame.loc[0, "geocode_status"]))


if __name__ == "__main__":
    unittest.main()
