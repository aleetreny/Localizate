#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.censo import build_censo_snapshot_manifest, load_raw_manifest
from localizate.censo_profile import (
    materialize_normalized_censo_period,
    profile_censo_snapshots,
    render_censo_profile_markdown,
)
from localizate.paths import DATA_DIR, DOCS_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile canonical census snapshots and optionally materialize selected periods.")
    parser.add_argument(
        "--raw-manifest",
        type=Path,
        default=DATA_DIR / "intermediate" / "raw_manifest.csv",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=DATA_DIR / "processed" / "censo_snapshot_profile.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=DOCS_DIR / "censo_snapshot_profile.md",
    )
    parser.add_argument(
        "--period",
        action="append",
        dest="periods",
        help="Profile only the specified period(s), e.g. 2026-03.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Process only the first N periodos after filters.",
    )
    parser.add_argument(
        "--materialize-period",
        action="append",
        dest="materialize_periods",
        help="Write normalized CSV.gz snapshot(s) for the specified period(s).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_manifest = load_raw_manifest(args.raw_manifest)
    snapshot_manifest = build_censo_snapshot_manifest(raw_manifest)
    target_periods = args.periods or snapshot_manifest["period"].tolist()
    if args.limit is not None:
        target_periods = target_periods[: args.limit]

    profile_parts = []
    total_periods = len(target_periods)
    for index, period in enumerate(target_periods, start=1):
        partial = profile_censo_snapshots(snapshot_manifest, periods=[period])
        profile_parts.append(partial)
        print(f"[{index}/{total_periods}] Profiled {period}", flush=True)
        current_profile = pd.concat(profile_parts, ignore_index=True)
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        current_profile.to_csv(args.output_csv, index=False)

    profile = pd.concat(profile_parts, ignore_index=True) if profile_parts else profile_censo_snapshots(snapshot_manifest, periods=[])

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    profile.to_csv(args.output_csv, index=False)
    args.output_md.write_text(render_censo_profile_markdown(profile), encoding="utf-8")

    print(f"Profile rows: {len(profile)}")
    print(f"Wrote profile CSV: {args.output_csv}")
    print(f"Wrote report: {args.output_md}")

    if args.materialize_periods:
        for period in args.materialize_periods:
            written_paths = materialize_normalized_censo_period(period, snapshot_manifest)
            if written_paths:
                for path in written_paths:
                    print(f"Materialized: {path}")
            else:
                print(f"No snapshots materialized for period {period}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
