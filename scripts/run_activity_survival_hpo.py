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
    parser = argparse.ArgumentParser(description="Run overnight HPO for activity survival models.")
    parser.add_argument("--cox-screen-trials", type=int, default=16)
    parser.add_argument("--ensemble-screen-trials", type=int, default=8)
    parser.add_argument("--confirm-top-k", type=int, default=3)
    parser.add_argument("--final-top-k", type=int, default=2)
    parser.add_argument("--screen-fit-max-rows", type=int, default=12000)
    parser.add_argument("--confirm-fit-max-rows", type=int, default=25000)
    parser.add_argument("--final-fit-max-rows", type=int, default=0)
    parser.add_argument("--screen-rsf-estimators", type=int, default=80)
    parser.add_argument("--screen-gbsa-estimators", type=int, default=80)
    parser.add_argument("--confirm-rsf-estimators", type=int, default=160)
    parser.add_argument("--confirm-gbsa-estimators", type=int, default=160)
    parser.add_argument("--final-rsf-estimators", type=int, default=300)
    parser.add_argument("--final-gbsa-estimators", type=int, default=300)
    parser.add_argument("--random-seed", type=int, default=20260326)
    parser.add_argument(
        "--progress-file",
        type=Path,
        default=PROJECT_ROOT / "models" / "run_progress_activity_survival_hpo.json",
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
    from localizate.survival_hpo import run_activity_survival_hpo

    args = parse_args()
    tracker = ProgressTracker(args.progress_file)
    result = run_activity_survival_hpo(
        cox_screen_trials=args.cox_screen_trials,
        ensemble_screen_trials=args.ensemble_screen_trials,
        confirm_top_k=args.confirm_top_k,
        final_top_k=args.final_top_k,
        screen_fit_max_rows=args.screen_fit_max_rows if args.screen_fit_max_rows > 0 else None,
        confirm_fit_max_rows=args.confirm_fit_max_rows if args.confirm_fit_max_rows > 0 else None,
        final_fit_max_rows=args.final_fit_max_rows if args.final_fit_max_rows > 0 else None,
        screen_rsf_estimators=args.screen_rsf_estimators,
        screen_gbsa_estimators=args.screen_gbsa_estimators,
        confirm_rsf_estimators=args.confirm_rsf_estimators,
        confirm_gbsa_estimators=args.confirm_gbsa_estimators,
        final_rsf_estimators=args.final_rsf_estimators,
        final_gbsa_estimators=args.final_gbsa_estimators,
        random_seed=args.random_seed,
        progress_callback=tracker,
    )
    print(f"Wrote HPO metrics: {result.metrics_json}")
    print(f"Wrote HPO report: {result.report_md}")
    print(f"Wrote HPO checkpoint: {result.checkpoint_json}")
    print(f"Best family: {result.best_family}")
    print(f"Best objective: {result.best_objective}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())