#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from localizate.survival_baseline import train_and_score_survival_baseline


def main() -> int:
    result = train_and_score_survival_baseline(
        transition_policy="exclude_transition",
        renta_max_year=2023,
    )
    print(f"Wrote scored export: {result.scored_csv}")
    print(f"Wrote metrics json: {result.metrics_json}")
    print(f"Wrote report: {result.report_md}")
    print(f"Split rows -> train={result.train_rows:,}, valid={result.valid_rows:,}, test={result.test_rows:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
