from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scripts.refresh_opportunity_listings_cloudflare import (  # noqa: E402
    ListingCardsUnavailable,
    _crawl_listing_cards,
    build_snapshot_refresh_plan,
    normalize_match_text,
)
import scripts.refresh_opportunity_listings_cloudflare as refresh_script  # noqa: E402


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


    def test_crawl_listing_cards_raises_diagnostics_when_transport_returns_empty_pages(self) -> None:
        config = refresh_script.ManualAvailableLocalesConfig(max_pages=2)

        with self.assertRaises(ListingCardsUnavailable) as ctx:
            _crawl_listing_cards(
                fetch_html=lambda _url: "<html><head><title>Blocked</title></head><body>No cards</body></html>",
                config=config,
                transport="browser_run",
            )

        self.assertEqual(ctx.exception.transport, "browser_run")
        self.assertGreaterEqual(len(ctx.exception.page_samples), 2)
        self.assertEqual(ctx.exception.page_samples[0]["title"], "Blocked")
        self.assertEqual(ctx.exception.page_samples[0]["js_card_count"], 0)

    def test_main_skips_refresh_after_all_fetch_transports_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir)
            snapshot_csv = temp_root / "snapshot.csv"
            summary_json = temp_root / "summary.json"
            geocode_cache_path = temp_root / "geocode-cache.csv"
            _previous_snapshot("Calle de AlcalÃ¡, Madrid").to_csv(snapshot_csv, index=False)

            args = argparse.Namespace(
                city="madrid",
                operations=["venta", "alquiler"],
                max_pages=2,
                max_browser_requests=24,
                min_browser_interval_seconds=15.0,
                browser_timeout_seconds=90.0,
                max_browser_ms_per_run=240000,
                max_new_geocodes=40,
                geocode_delay_seconds=1.2,
                contact_email=None,
                h3_resolution=10,
                snapshot_csv=snapshot_csv,
                summary_json=summary_json,
                geocode_cache_path=geocode_cache_path,
            )

            browser_client = mock.Mock()
            browser_client.request_count = 4
            browser_client.browser_ms_used_total = 24358
            empty_browser_result = ListingCardsUnavailable(
                transport="browser_run",
                page_samples=[
                    {
                        "operation": "venta",
                        "page_number": 1,
                        "url": "https://www.locales.es/madrid/venta/locales?page=1",
                        "title": "Blocked",
                        "html_length": 64,
                        "js_card_count": 0,
                        "card_link_count": 0,
                        "challenge_detected": False,
                    }
                ],
            )

            with (
                mock.patch.object(refresh_script, "parse_args", return_value=args),
                mock.patch.object(refresh_script, "build_browser_run_client_from_env", return_value=browser_client),
                mock.patch.object(
                    refresh_script,
                    "crawl_listing_cards_with_http_session",
                    side_effect=requests.HTTPError(
                        "403 Client Error: Forbidden for url: https://www.locales.es/madrid/venta/locales?page=1"
                    ),
                ),
                mock.patch.object(
                    refresh_script,
                    "crawl_listing_cards_with_browser_run",
                    side_effect=empty_browser_result,
                ),
            ):
                exit_code = refresh_script.main()

            self.assertEqual(exit_code, 0)
            summary = json.loads(summary_json.read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "skipped")
            self.assertEqual(summary["snapshot_listing_count"], 1)
            self.assertEqual(summary["request_count"], 4)
            self.assertEqual(summary["browser_ms_used_total"], 24358)
            self.assertEqual(len(summary["attempts"]), 2)
            self.assertIn("direct_http", summary["reason"])
            self.assertIn("browser_run", summary["reason"])

    def test_main_prefers_direct_http_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir)
            snapshot_csv = temp_root / "snapshot.csv"
            summary_json = temp_root / "summary.json"
            geocode_cache_path = temp_root / "geocode-cache.csv"
            _previous_snapshot("Calle de AlcalÃ¡, Madrid").to_csv(snapshot_csv, index=False)

            args = argparse.Namespace(
                city="madrid",
                operations=["venta"],
                max_pages=1,
                max_browser_requests=24,
                min_browser_interval_seconds=15.0,
                browser_timeout_seconds=90.0,
                max_browser_ms_per_run=240000,
                max_new_geocodes=40,
                geocode_delay_seconds=1.2,
                contact_email=None,
                h3_resolution=10,
                snapshot_csv=snapshot_csv,
                summary_json=summary_json,
                geocode_cache_path=geocode_cache_path,
            )

            browser_client = mock.Mock()
            browser_client.request_count = 0
            browser_client.browser_ms_used_total = 0
            current_cards = _current_card("Calle de AlcalÃ¡, Madrid")

            with (
                mock.patch.object(refresh_script, "parse_args", return_value=args),
                mock.patch.object(refresh_script, "build_browser_run_client_from_env", return_value=browser_client),
                mock.patch.object(refresh_script, "crawl_listing_cards_with_http_session", return_value=current_cards),
                mock.patch.object(refresh_script, "crawl_listing_cards_with_browser_run") as browser_mock,
                mock.patch.object(refresh_script, "apply_geocode_refresh_plan", side_effect=lambda frame, **_: frame),
            ):
                exit_code = refresh_script.main()

            self.assertEqual(exit_code, 0)
            browser_mock.assert_not_called()
            summary = json.loads(summary_json.read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "updated")
            self.assertEqual(summary["attempts"][0]["transport"], "direct_http")
            self.assertEqual(summary["attempts"][0]["status"], "success")

if __name__ == "__main__":
    unittest.main()
