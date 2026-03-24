#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from localizate.survival_feature_validation import validate_survival_feature_frame


def main() -> int:
    result = validate_survival_feature_frame()
    print(f"Wrote feature validation metrics: {result.metrics_json}")
    print(f"Wrote feature validation report: {result.report_md}")
    print(f"Rows analyzed: {result.rows:,}")
    print(f"Features analyzed: {result.features}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
