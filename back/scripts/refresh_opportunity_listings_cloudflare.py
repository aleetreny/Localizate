#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.cloudflare_browser_run import (  # noqa: E402
    BrowserRunBudgetExceeded,
    CloudflareBrowserRunClient,
    CloudflareBrowserRunConfig,
)
from localizate.manual_available_locales import (  # noqa: E402
    ManualAvailableLocalesConfig,
    NOMINATIM_USER_AGENT,
    OUTPUT_COLUMNS,
    _assign_h3_cells,
    _assign_section_geography,
    _build_http_session,
    _finalize_output_columns,
    _geocode_locales_listings,
    _load_geocode_cache,
    _normalize_operations,
    _prepare_frame_for_enrichment,
    build_locales_search_url,
    extract_listing_cards,
)
from localizate.paths import DATA_DIR  # noqa: E402


VERSIONED_OPPORTUNITY_DIR = BACKEND_ROOT / "data" / "opportunities"
SNAPSHOT_CSV = VERSIONED_OPPORTUNITY_DIR / "manual_available_locales_madrid_snapshot.csv"
SUMMARY_JSON = DATA_DIR / "processed" / "manual_available_locales_madrid_refresh_summary.json"
GEOCODE_CACHE_CSV = DATA_DIR / "intermediate" / "manual_available_locales_madrid_geocode_cache.csv"

SNAPSHOT_CONTEXT_COLUMNS = [
    "detail_title",
    "product_name",
    "description_full",
    "breadcrumb_zone",
    "breadcrumb_path",
    "geocode_query",
    "geocode_status",
    "coord_source",
    "coord_precision",
    "geocode_display_name",
    "lat_wgs84",
    "lon_wgs84",
    "h3_cell",
    "h3_resolution",
    "section_key",
    "district_code",
    "district_name",
    "barrio_code",
    "barrio_name",
    "published_at",
    "modified_at",
    "detail_fetch_status",
]


@dataclass(frozen=True)
class SnapshotRefreshPlan:
    frame: pd.DataFrame
    geocode_row_indexes: tuple[int, ...]
    reused_context_count: int
    removed_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Refresca el snapshot versionado de oportunidades con Cloudflare Browser Run "
            "sin hacer scrape de detalle y con limites conservadores."
        )
    )
    parser.add_argument("--city", default="madrid", help="Slug de ciudad en Locales.es.")
    parser.add_argument(
        "--operations",
        nargs="+",
        default=["venta", "alquiler"],
        help="Operaciones a rastrear en Locales.es.",
    )
    parser.add_argument("--max-pages", type=int, default=24, help="Numero maximo de paginas por operacion.")
    parser.add_argument(
        "--max-browser-requests",
        type=int,
        default=24,
        help="Tope duro de requests Browser Run por ejecucion.",
    )
    parser.add_argument(
        "--min-browser-interval-seconds",
        type=float,
        default=15.0,
        help="Espera minima entre requests Browser Run.",
    )
    parser.add_argument(
        "--browser-timeout-seconds",
        type=float,
        default=90.0,
        help="Timeout HTTP por request Browser Run.",
    )
    parser.add_argument(
        "--max-browser-ms-per-run",
        type=int,
        default=240000,
        help="Tope conservador de tiempo total de Browser Run por ejecucion en milisegundos.",
    )
    parser.add_argument(
        "--max-new-geocodes",
        type=int,
        default=40,
        help="Numero maximo de listings nuevos o reubicados a geocodificar en una ejecucion.",
    )
    parser.add_argument(
        "--geocode-delay-seconds",
        type=float,
        default=1.2,
        help="Pausa entre peticiones a Nominatim para listings nuevos.",
    )
    parser.add_argument(
        "--contact-email",
        default=None,
        help="Email opcional para identificarte ante Nominatim.",
    )
    parser.add_argument("--h3-resolution", type=int, default=10, help="Resolucion H3 para nuevos listings.")
    parser.add_argument("--snapshot-csv", type=Path, default=SNAPSHOT_CSV)
    parser.add_argument("--summary-json", type=Path, default=SUMMARY_JSON)
    parser.add_argument("--geocode-cache-path", type=Path, default=GEOCODE_CACHE_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.snapshot_csv.exists():
        raise FileNotFoundError(
            "No se encontro el snapshot versionado de oportunidades. "
            f"Bootstrap esperado en {args.snapshot_csv}"
        )

    previous_snapshot = load_snapshot_frame(args.snapshot_csv)
    browser_client = build_browser_run_client_from_env(args)
    refresh_config = ManualAvailableLocalesConfig(
        city_slug=args.city.lower().strip(),
        operations=tuple(args.operations),
        max_pages=args.max_pages,
        geocode_delay_seconds=args.geocode_delay_seconds,
        geocode_email=args.contact_email,
        h3_resolution=args.h3_resolution,
    )

    try:
        listing_cards = crawl_listing_cards_with_browser_run(browser_client, config=refresh_config)
    except BrowserRunBudgetExceeded as exc:
        print(f"Skipped Cloudflare refresh: {exc}")
        write_refresh_summary(
            args.summary_json,
            {
                "status": "skipped",
                "reason": str(exc),
                "request_count": browser_client.request_count,
                "browser_ms_used_total": browser_client.browser_ms_used_total,
                "snapshot_listing_count": int(len(previous_snapshot)),
            },
        )
        return 0

    plan = build_snapshot_refresh_plan(listing_cards, previous_snapshot)
    pending_geocodes = len(plan.geocode_row_indexes)
    print(
        "Cloudflare crawl complete: "
        f"{len(listing_cards)} active listings, "
        f"{plan.reused_context_count} reused from snapshot, "
        f"{pending_geocodes} new or relocated listings, "
        f"{plan.removed_count} removed."
    )

    if pending_geocodes > args.max_new_geocodes:
        reason = (
            "Skipped Cloudflare refresh: "
            f"{pending_geocodes} listings need fresh geocoding, over the conservative cap "
            f"of {args.max_new_geocodes}."
        )
        print(reason)
        write_refresh_summary(
            args.summary_json,
            {
                "status": "skipped",
                "reason": reason,
                "request_count": browser_client.request_count,
                "browser_ms_used_total": browser_client.browser_ms_used_total,
                "snapshot_listing_count": int(len(previous_snapshot)),
                "crawled_listing_count": int(len(listing_cards)),
                "pending_geocodes": int(pending_geocodes),
            },
        )
        return 0

    refreshed_snapshot = apply_geocode_refresh_plan(
        plan.frame,
        row_indexes=plan.geocode_row_indexes,
        geocode_cache_path=args.geocode_cache_path,
        geocode_delay_seconds=args.geocode_delay_seconds,
        geocode_email=args.contact_email,
        city_slug=refresh_config.city_slug,
        h3_resolution=args.h3_resolution,
    )

    args.snapshot_csv.parent.mkdir(parents=True, exist_ok=True)
    refreshed_snapshot.to_csv(args.snapshot_csv, index=False)

    summary = {
        "status": "updated",
        "city_slug": refresh_config.city_slug,
        "operations": list(_normalize_operations(refresh_config.operations)),
        "request_count": browser_client.request_count,
        "browser_ms_used_total": browser_client.browser_ms_used_total,
        "listing_count": int(len(refreshed_snapshot)),
        "reused_context_count": int(plan.reused_context_count),
        "new_or_relocated_count": int(pending_geocodes),
        "removed_count": int(plan.removed_count),
        "street_precision_count": int(refreshed_snapshot["coord_precision"].astype("string").eq("street_approx").sum()),
        "section_key_count": int(refreshed_snapshot["section_key"].notna().sum()),
    }
    write_refresh_summary(args.summary_json, summary)

    print(f"Updated snapshot CSV: {args.snapshot_csv}")
    print(
        "Snapshot summary: "
        f"{summary['listing_count']} listings, "
        f"{summary['street_precision_count']} with street precision, "
        f"{summary['section_key_count']} with section_key."
    )
    return 0


def build_browser_run_client_from_env(args: argparse.Namespace) -> CloudflareBrowserRunClient:
    account_id = (os.environ.get("CLOUDFLARE_ACCOUNT_ID") or "").strip()
    api_token = (os.environ.get("CLOUDFLARE_BROWSER_RUN_API_TOKEN") or "").strip()
    if not account_id:
        raise RuntimeError("Missing CLOUDFLARE_ACCOUNT_ID for Browser Run refresh.")
    if not api_token:
        raise RuntimeError("Missing CLOUDFLARE_BROWSER_RUN_API_TOKEN for Browser Run refresh.")

    config = CloudflareBrowserRunConfig(
        account_id=account_id,
        api_token=api_token,
        max_requests=args.max_browser_requests,
        min_interval_seconds=args.min_browser_interval_seconds,
        timeout_seconds=args.browser_timeout_seconds,
        max_browser_ms_per_run=args.max_browser_ms_per_run,
    )
    return CloudflareBrowserRunClient(config)


def load_snapshot_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    return _finalize_output_columns(_prepare_frame_for_enrichment(frame))


def crawl_listing_cards_with_browser_run(
    browser_client: CloudflareBrowserRunClient,
    *,
    config: ManualAvailableLocalesConfig,
) -> pd.DataFrame:
    operations = _normalize_operations(config.operations)
    if not operations:
        raise ValueError("At least one operation must be provided")

    seen_keys: set[str] = set()
    records: list[dict[str, Any]] = []

    for operation in operations:
        consecutive_empty_pages = 0
        for page_number in range(1, config.max_pages + 1):
            page_url = build_locales_search_url(config.city_slug, operation, page_number)
            html = browser_client.fetch_html(page_url)
            page_records = extract_listing_cards(
                html,
                city_slug=config.city_slug,
                operation=operation,
                page_number=page_number,
            )
            fresh_records = [record for record in page_records if record["listing_key"] not in seen_keys]
            print(
                f"Fetched {operation} page {page_number}: "
                f"{len(page_records)} cards, {len(fresh_records)} fresh, "
                f"{browser_client.request_count}/{browser_client.config.max_requests} Browser Run requests, "
                f"{browser_client.browser_ms_used_total} ms used."
            )

            if not fresh_records:
                consecutive_empty_pages += 1
            else:
                consecutive_empty_pages = 0

            for record in fresh_records:
                seen_keys.add(record["listing_key"])
                records.append(record)

            if consecutive_empty_pages >= 2:
                break

    if not records:
        raise ValueError("Cloudflare Browser Run returned zero listing cards.")

    frame = pd.DataFrame.from_records(records)
    frame = frame.sort_values(["operation", "page_number", "listing_id"]).reset_index(drop=True)
    frame = _prepare_frame_for_enrichment(frame)
    frame["detail_fetch_status"] = "card_only"
    return _finalize_output_columns(frame)


def build_snapshot_refresh_plan(
    current_cards: pd.DataFrame,
    previous_snapshot: pd.DataFrame,
) -> SnapshotRefreshPlan:
    previous = _finalize_output_columns(_prepare_frame_for_enrichment(previous_snapshot))
    previous = previous.drop_duplicates(subset=["listing_key"], keep="last")
    previous_by_key = previous.set_index("listing_key", drop=False)
    current_keys = set(current_cards["listing_key"].astype("string").dropna().tolist())

    merged_records: list[dict[str, Any]] = []
    geocode_row_indexes: list[int] = []
    reused_context_count = 0

    for row in current_cards.to_dict(orient="records"):
        record = {column: row.get(column, pd.NA) for column in OUTPUT_COLUMNS}
        listing_key = str(record.get("listing_key") or "")

        if listing_key and listing_key in previous_by_key.index:
            previous_row = previous_by_key.loc[listing_key].to_dict()
            if should_reuse_snapshot_context(record, previous_row):
                reused_context_count += 1
                apply_snapshot_context(record, previous_row)
            else:
                geocode_row_indexes.append(len(merged_records))
        else:
            geocode_row_indexes.append(len(merged_records))

        merged_records.append(record)

    removed_count = int(previous["listing_key"].astype("string").isin(current_keys).eq(False).sum())
    frame = pd.DataFrame.from_records(merged_records)
    frame = _prepare_frame_for_enrichment(frame)
    return SnapshotRefreshPlan(
        frame=_finalize_output_columns(frame),
        geocode_row_indexes=tuple(geocode_row_indexes),
        reused_context_count=reused_context_count,
        removed_count=removed_count,
    )


def should_reuse_snapshot_context(current_row: dict[str, Any], previous_row: dict[str, Any]) -> bool:
    current_fingerprint = build_location_fingerprint(current_row)
    previous_fingerprint = build_location_fingerprint(previous_row)
    if current_fingerprint and previous_fingerprint:
        return current_fingerprint == previous_fingerprint
    return True


def apply_snapshot_context(current_row: dict[str, Any], previous_row: dict[str, Any]) -> None:
    if not current_row.get("address_text") and previous_row.get("address_text"):
        current_row["address_text"] = previous_row.get("address_text")

    for column in SNAPSHOT_CONTEXT_COLUMNS:
        previous_value = previous_row.get(column, pd.NA)
        if pd.isna(previous_value):
            continue
        current_row[column] = previous_value

    detail_fetch_status = current_row.get("detail_fetch_status")
    if detail_fetch_status is None or detail_fetch_status is pd.NA or str(detail_fetch_status).strip() in {"", "card_only"}:
        current_row["detail_fetch_status"] = "reused_snapshot"


def build_location_fingerprint(row: dict[str, Any]) -> str:
    for column in ("address_text", "detail_title", "card_title", "listing_url"):
        normalized = normalize_match_text(row.get(column))
        if normalized:
            return normalized
    return ""


def normalize_match_text(value: object) -> str:
    if value is None or value is pd.NA:
        return ""
    text = str(value).strip()
    if not text or text.lower() in {"nan", "<na>"}:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = re.sub(r"[^0-9a-zA-Z]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def apply_geocode_refresh_plan(
    frame: pd.DataFrame,
    *,
    row_indexes: tuple[int, ...],
    geocode_cache_path: Path,
    geocode_delay_seconds: float,
    geocode_email: str | None,
    city_slug: str,
    h3_resolution: int,
) -> pd.DataFrame:
    if not row_indexes:
        return _finalize_output_columns(_prepare_frame_for_enrichment(frame))

    prepared = _prepare_frame_for_enrichment(frame)
    target = prepared.loc[list(row_indexes)].copy()
    geocode_session = _build_http_session(user_agent=NOMINATIM_USER_AGENT)
    geocode_cache = _load_geocode_cache(geocode_cache_path)

    _geocode_locales_listings(
        target,
        session=geocode_session,
        geocode_cache_path=geocode_cache_path,
        cache=geocode_cache,
        geocode_delay_seconds=geocode_delay_seconds,
        geocode_email=geocode_email,
        city_slug=city_slug,
    )
    _assign_h3_cells(target, resolution=h3_resolution)
    _assign_section_geography(target)

    ok_mask = target["geocode_status"].astype("string").eq("ok")
    target.loc[ok_mask, "detail_fetch_status"] = "card_only_geocoded"
    target.loc[~ok_mask, "detail_fetch_status"] = target.loc[~ok_mask, "detail_fetch_status"].fillna("card_only")

    for column in prepared.columns:
        prepared.loc[target.index, column] = target[column]

    return _finalize_output_columns(prepared)


def write_refresh_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
