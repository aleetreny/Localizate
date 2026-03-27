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
    parser = argparse.ArgumentParser(description="Run walk-forward rolling backtest for activity survival canonical model.")
    parser.add_argument("--rsf-estimators", type=int, default=120)
    parser.add_argument("--gbsa-estimators", type=int, default=120)
    parser.add_argument("--rsf-chunk-size", type=int, default=20)
    parser.add_argument("--gbsa-chunk-size", type=int, default=20)
    parser.add_argument("--fit-max-rows", type=int, default=25000)
    parser.add_argument(
        "--progress-file",
        type=Path,
        default=PROJECT_ROOT / "models" / "run_progress_activity_survival_rolling_backtest.json",
    )
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
    from localizate.survival_rolling_backtest import run_activity_survival_rolling_backtest

    args = parse_args()
    tracker = ProgressTracker(args.progress_file)
    result = run_activity_survival_rolling_backtest(
        rsf_n_estimators=args.rsf_estimators,
        gbsa_n_estimators=args.gbsa_estimators,
        rsf_chunk_size=args.rsf_chunk_size,
        gbsa_chunk_size=args.gbsa_chunk_size,
        fit_max_rows=args.fit_max_rows,
        progress_callback=tracker,
    )
    print(f"Wrote rolling metrics: {result.metrics_json}")
    print(f"Wrote rolling report: {result.report_md}")
    print(f"Folds executed: {result.folds_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())