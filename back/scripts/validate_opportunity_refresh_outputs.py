#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlparse

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_CSV = PROJECT_ROOT / "back" / "data" / "opportunities" / "manual_available_locales_madrid_snapshot.csv"
SUMMARY_JSON = PROJECT_ROOT / "storage" / "data" / "processed" / "manual_available_locales_madrid_refresh_summary.json"
FRONTEND_JSON = PROJECT_ROOT / "front" / "public" / "data" / "opportunities" / "listings.json"

LISTING_PATH_PATTERN = re.compile(r"^/madrid/([^/]+)/local(\d+)$")
SUPPORTED_OPERATIONS = {"venta", "alquiler"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a completed opportunity refresh before publishing it.")
    parser.add_argument("--snapshot-csv", type=Path, default=SNAPSHOT_CSV)
    parser.add_argument("--summary-json", type=Path, default=SUMMARY_JSON)
    parser.add_argument("--frontend-json", type=Path, default=FRONTEND_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_outputs(
        snapshot_csv=args.snapshot_csv,
        summary_json=args.summary_json,
        frontend_json=args.frontend_json,
    )
    print(
        "Validated opportunity refresh outputs: "
        f"{result['snapshot_listings']} active listings, "
        f"{result['frontend_points']} published points, "
        f"{result['frontend_urls']} unique published URLs."
    )
    return 0


def validate_outputs(*, snapshot_csv: Path, summary_json: Path, frontend_json: Path) -> dict[str, int]:
    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    if summary.get("status") != "updated":
        raise ValueError(f"Refresh summary is not updated: {summary.get('status')!r}")

    snapshot = pd.read_csv(snapshot_csv, dtype={"listing_id": "string", "listing_key": "string"}, low_memory=False)
    if snapshot.empty:
        raise ValueError("The refreshed snapshot is empty.")
    required_snapshot_columns = {"listing_id", "listing_key", "listing_url", "operation"}
    missing_columns = sorted(required_snapshot_columns - set(snapshot.columns))
    if missing_columns:
        raise ValueError(f"Snapshot is missing required columns: {', '.join(missing_columns)}")

    if bool(snapshot["listing_key"].isna().any()) or bool(snapshot["listing_key"].duplicated().any()):
        raise ValueError("Snapshot listing keys must be present and unique.")
    if bool(snapshot["listing_url"].isna().any()) or bool(snapshot["listing_url"].duplicated().any()):
        raise ValueError("Snapshot listing URLs must be present and unique.")

    snapshot_urls: set[str] = set()
    snapshot_url_by_identity: dict[tuple[str, str], str] = {}
    for row in snapshot.itertuples(index=False):
        operation = str(row.operation)
        listing_id = str(row.listing_id)
        listing_url = str(row.listing_url)
        validate_listing_url(listing_url, listing_id=listing_id, operation=operation)
        snapshot_urls.add(listing_url)
        snapshot_url_by_identity[(operation, listing_id)] = listing_url

    expected_count = int(summary.get("listing_count", -1))
    if expected_count != len(snapshot):
        raise ValueError(f"Refresh summary listing_count={expected_count} does not match snapshot rows={len(snapshot)}.")

    payload = json.loads(frontend_json.read_text(encoding="utf-8"))
    points = payload.get("points")
    if not isinstance(points, list) or not points:
        raise ValueError("Frontend payload contains no opportunity points.")
    stats = payload.get("stats") or {}
    if stats.get("selected_listings") != len(points):
        raise ValueError("Frontend selected_listings does not match the number of points.")

    frontend_urls: list[str] = []
    for point in points:
        if not isinstance(point, dict):
            raise ValueError("Frontend opportunity points must be objects.")
        listing_id = str(point.get("listing_id") or "")
        operation = str(point.get("operation") or "")
        listing_url = str(point.get("listing_url") or "")
        validate_listing_url(listing_url, listing_id=listing_id, operation=operation)
        expected_url = snapshot_url_by_identity.get((operation, listing_id))
        if expected_url != listing_url:
            raise ValueError(
                f"Frontend URL is not present in the freshly crawled snapshot for {operation}:{listing_id}: {listing_url}"
            )
        frontend_urls.append(listing_url)

    if len(frontend_urls) != len(set(frontend_urls)):
        raise ValueError("Frontend listing URLs must be unique.")
    if not set(frontend_urls).issubset(snapshot_urls):
        raise ValueError("Frontend payload contains URLs outside the freshly crawled snapshot.")

    return {
        "snapshot_listings": int(len(snapshot)),
        "frontend_points": int(len(points)),
        "frontend_urls": int(len(set(frontend_urls))),
    }


def validate_listing_url(url: str, *, listing_id: str, operation: str) -> None:
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError(f"Unsupported listing operation {operation!r} for {listing_id}.")

    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "www.locales.es":
        raise ValueError(f"Listing URL must use https://www.locales.es: {url}")

    match = LISTING_PATH_PATTERN.fullmatch(parsed.path)
    if match is None:
        raise ValueError(f"Unexpected Locales.es listing path: {url}")
    path_operation, path_listing_id = match.groups()
    if path_listing_id != listing_id:
        raise ValueError(f"Listing URL id {path_listing_id} does not match row id {listing_id}: {url}")
    if operation not in path_operation.split("-"):
        raise ValueError(f"Listing URL operation {path_operation!r} does not include {operation!r}: {url}")


if __name__ == "__main__":
    raise SystemExit(main())
