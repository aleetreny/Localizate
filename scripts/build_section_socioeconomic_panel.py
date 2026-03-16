#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.censo import load_raw_manifest
from localizate.paths import DATA_DIR
from localizate.socioeconomics import (
    build_padron_section_panel,
    load_and_normalize_renta_madrid,
    build_section_socioeconomic_panel,
    plan_padron_period_cache,
    write_optional_parquet,
    write_section_socioeconomic_outputs,
)
from localizate.section_geography import load_section_metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and materialize socioeconomic section panels.")
    parser.add_argument(
        "--start-period",
        default="2015-01",
        help="Minimum padron/censo period to process (YYYY-MM).",
    )
    parser.add_argument(
        "--target-period",
        action="append",
        dest="target_periods",
        help="Optional target period(s) for censo-aligned panel generation (repeatable).",
    )
    parser.add_argument(
        "--padron-period",
        action="append",
        dest="padron_periods",
        help="Optional padron period(s) to process (repeatable).",
    )
    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Disable cache-based incremental build for padron panel.",
    )
    parser.add_argument(
        "--rebuild-cache",
        action="store_true",
        help="Recompute cached padron monthly aggregates even if cache files already exist.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DATA_DIR / "intermediate" / "padron_section_panel",
        help="Directory where monthly padron section aggregates are cached.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_manifest = load_raw_manifest()

    if not args.no_incremental:
        cache_plan = plan_padron_period_cache(
            raw_manifest,
            periods=args.padron_periods,
            start_period=args.start_period,
            cache_dir=args.cache_dir,
            rebuild_cache=args.rebuild_cache,
        )
        print(
            "Padron cache plan: "
            f"target={len(cache_plan['target_periods'])}, "
            f"cached={len(cache_plan['cached_periods'])}, "
            f"pending={len(cache_plan['pending_periods'])}",
            flush=True,
        )

    print("Building padron section panel...", flush=True)
    padron_panel = build_padron_section_panel(
        raw_manifest,
        periods=args.padron_periods,
        start_period=args.start_period,
        incremental=not args.no_incremental,
        cache_dir=args.cache_dir,
        rebuild_cache=args.rebuild_cache,
        progress_callback=lambda period, idx, total: print(f"[padron {idx}/{total}] {period}", flush=True),
    )
    print("Loading renta and section metadata...", flush=True)
    renta_madrid = load_and_normalize_renta_madrid(raw_manifest)
    section_metadata = load_section_metadata(raw_manifest)
    print("Building censo-aligned section panel...", flush=True)
    section_panel = build_section_socioeconomic_panel(
        raw_manifest,
        target_periods=args.target_periods,
        start_period=args.start_period,
        padron_panel=padron_panel,
        renta_madrid=renta_madrid,
        section_metadata=section_metadata,
    )
    write_section_socioeconomic_outputs(padron_panel, section_panel)

    padron_parquet = DATA_DIR / "processed" / "padron_section_panel.parquet"
    section_parquet = DATA_DIR / "processed" / "section_socioeconomic_panel.parquet"
    wrote_padron_parquet = write_optional_parquet(padron_panel, padron_parquet)
    wrote_section_parquet = write_optional_parquet(section_panel, section_parquet)

    print("Wrote section socioeconomic outputs.")
    print(f"Padron parquet written: {wrote_padron_parquet}")
    print(f"Section parquet written: {wrote_section_parquet}")
    print(f"Padron rows: {len(padron_panel):,}")
    print(f"Section rows: {len(section_panel):,}")
    print(section_panel[['target_period', 'padron_reference_period', 'padron_lag_months']].drop_duplicates().tail().to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
