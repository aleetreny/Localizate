#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train canonical survival model for activity survival target.")
    parser.add_argument("--rsf-estimators", type=int, default=300)
    parser.add_argument("--gbsa-estimators", type=int, default=300)
    parser.add_argument("--rsf-chunk-size", type=int, default=25)
    parser.add_argument("--gbsa-chunk-size", type=int, default=25)
    parser.add_argument(
        "--progress-file",
        type=Path,
        default=PROJECT_ROOT / "models" / "run_progress_survival_activity_canonical.json",
    )
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


class ProgressTracker:
    def __init__(self, progress_file: Path):
        self.progress_file = progress_file
        self.start_time = time.time()
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, payload: dict[str, object]) -> None:
        now = time.time()
        progress = float(payload.get("progress", 0.0) or 0.0)
        elapsed = now - self.start_time
        eta_seconds = (elapsed / progress - elapsed) if progress > 0 else None
        record = {
            "timestamp_epoch": now,
            "elapsed_seconds": elapsed,
            "eta_seconds": eta_seconds,
            **payload,
        }
        self.progress_file.write_text(__import__("json").dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        percent = int(progress * 100)
        eta_txt = f", eta~{int(eta_seconds)}s" if eta_seconds is not None else ""
        print(f"[{percent:3d}%] {payload.get('stage')}: {payload.get('message')}{eta_txt}")


def main() -> int:
    from localizate.survival_canonical import train_canonical_survival_models

    args = parse_args()
    rsf_estimators = 40 if args.quick else args.rsf_estimators
    gbsa_estimators = 5 if args.quick else args.gbsa_estimators
    fit_max_rows = 10000 if args.quick else None
    rsf_chunk_size = min(args.rsf_chunk_size, rsf_estimators) if args.quick else args.rsf_chunk_size
    gbsa_chunk_size = min(args.gbsa_chunk_size, gbsa_estimators) if args.quick else args.gbsa_chunk_size

    tracker = ProgressTracker(args.progress_file)
    result = train_canonical_survival_models(
        abt_csv=PROJECT_ROOT / "data" / "features" / "activity_survival_abt.csv",
        metrics_json=PROJECT_ROOT / "models" / "survival_activity_canonical_metrics.json",
        report_md=PROJECT_ROOT / "docs" / "survival_activity_canonical.md",
        map_export_csv=PROJECT_ROOT / "data" / "exports" / "activity_survival_map_export.csv",
        feature_profile="activity_survival_pruned",
        transition_policy_train="exclude_transition",
        renta_max_year=2023,
        rsf_n_estimators=rsf_estimators,
        gbsa_n_estimators=gbsa_estimators,
        rsf_chunk_size=rsf_chunk_size,
        gbsa_chunk_size=gbsa_chunk_size,
        fit_max_rows=fit_max_rows,
        progress_callback=tracker,
    )
    print(f"Wrote canonical metrics: {result.metrics_json}")
    print(f"Wrote canonical report: {result.report_md}")
    print(f"Wrote final map export: {result.map_export_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())