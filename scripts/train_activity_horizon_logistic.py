#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> int:
    from localizate.activity_horizon_logistic import train_activity_horizon_logistic_models

    result = train_activity_horizon_logistic_models()
    print(f"Wrote logistic metrics: {result.metrics_json}")
    print(f"Wrote logistic report: {result.report_md}")
    print(f"Selected horizons: {result.selected_horizons}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())