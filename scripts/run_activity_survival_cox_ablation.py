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
    parser = argparse.ArgumentParser(description="Run Cox leave-one-block-out ablation for activity_survival.")
    parser.add_argument("--fit-max-rows", type=int, default=None)
    parser.add_argument("--alpha", type=float, default=None)
    parser.add_argument("--ties", choices=["breslow", "efron"], default=None)
    parser.add_argument("--feature-profile", default="full")
    parser.add_argument("--output-tag", default="")
    parser.add_argument("--hpo-json", type=Path, default=PROJECT_ROOT / "models" / "activity_survival_hpo.json")
    parser.add_argument(
        "--progress-file",
        type=Path,
        default=PROJECT_ROOT / "models" / "run_progress_activity_survival_cox_ablation.json",
    )
    return parser.parse_args()


def _tag_path(path: Path, tag: str) -> Path:
    clean_tag = str(tag).strip()
    if not clean_tag:
        return path
    return path.with_name(f"{path.stem}__{clean_tag}{path.suffix}")


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
    from localizate.survival_ablation import run_activity_survival_cox_ablation

    args = parse_args()
    tracker = ProgressTracker(_tag_path(args.progress_file, args.output_tag))
    result = run_activity_survival_cox_ablation(
        abt_csv=PROJECT_ROOT / "data" / "features" / "activity_survival_abt.csv",
        hpo_json=args.hpo_json,
        metrics_json=_tag_path(PROJECT_ROOT / "models" / "activity_survival_cox_ablation.json", args.output_tag),
        report_md=_tag_path(PROJECT_ROOT / "docs" / "activity_survival_cox_ablation.md", args.output_tag),
        fit_max_rows=args.fit_max_rows,
        alpha=args.alpha,
        ties=args.ties,
        feature_profile=args.feature_profile,
        progress_callback=tracker,
    )
    print(f"Wrote ablation metrics: {result.metrics_json}")
    print(f"Wrote ablation report: {result.report_md}")
    print(f"Evaluated ablation blocks: {result.evaluated_blocks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())