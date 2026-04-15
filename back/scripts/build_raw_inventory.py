#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.paths import DATA_DIR, DOCS_DATA_DIR, RAW_DATA_DIR
from localizate.ckan import enrich_inventory_with_avisos_metadata
from localizate.raw_inventory import build_inventory_markdown, build_raw_inventory, build_raw_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a canonical inventory of the raw data lake.")
    parser.add_argument("--raw-root", type=Path, default=RAW_DATA_DIR)
    parser.add_argument(
        "--skip-remote-metadata",
        action="store_true",
        help="Do not enrich the inventory with CKAN metadata.",
    )
    parser.add_argument(
        "--inventory-csv",
        type=Path,
        default=DATA_DIR / "intermediate" / "raw_inventory.csv",
    )
    parser.add_argument(
        "--manifest-csv",
        type=Path,
        default=DATA_DIR / "intermediate" / "raw_manifest.csv",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=DOCS_DATA_DIR / "raw_data_inventory.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory = build_raw_inventory(raw_root=args.raw_root)
    if not args.skip_remote_metadata:
        try:
            inventory = enrich_inventory_with_avisos_metadata(inventory)
        except Exception as exc:
            print(f"Warning: unable to enrich avisos metadata from CKAN: {exc}")
    manifest = build_raw_manifest(inventory)
    report = build_inventory_markdown(inventory, manifest)

    args.inventory_csv.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    args.report_md.parent.mkdir(parents=True, exist_ok=True)

    inventory.to_csv(args.inventory_csv, index=False)
    manifest.to_csv(args.manifest_csv, index=False)
    args.report_md.write_text(report, encoding="utf-8")

    print(f"Inventory rows: {len(inventory)}")
    print(f"Manifest rows: {len(manifest)}")
    print(f"Wrote inventory CSV: {args.inventory_csv}")
    print(f"Wrote manifest CSV: {args.manifest_csv}")
    print(f"Wrote report: {args.report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
