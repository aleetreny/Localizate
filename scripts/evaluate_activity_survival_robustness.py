#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run post-training robustness evaluation for activity survival scores.")
    parser.add_argument("--bootstrap-iterations", type=int, default=200)
    parser.add_argument("--bootstrap-max-rows", type=int, default=10000)
    return parser.parse_args()


def main() -> int:
    from localizate.survival_robustness import run_canonical_robustness_check

    args = parse_args()
    result = run_canonical_robustness_check(
        abt_csv=PROJECT_ROOT / "data" / "features" / "activity_survival_abt.csv",
        map_export_csv=PROJECT_ROOT / "data" / "exports" / "activity_survival_map_export.csv",
        canonical_metrics_json=PROJECT_ROOT / "models" / "survival_activity_canonical_metrics.json",
        report_md=PROJECT_ROOT / "docs" / "survival_activity_canonical_robustness.md",
        report_json=PROJECT_ROOT / "models" / "survival_activity_canonical_robustness.json",
        bootstrap_iterations=args.bootstrap_iterations,
        bootstrap_max_rows=args.bootstrap_max_rows,
    )
    print(f"Wrote robustness report: {result.report_md}")
    print(f"Wrote robustness json: {result.report_json}")
    print(f"Robustness status: {result.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())