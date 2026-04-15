#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> int:
    from localizate.zone_category_survival import build_zone_category_survival_analysis

    result = build_zone_category_survival_analysis()
    print(f"Wrote taxonomy csv: {result.taxonomy_csv}")
    print(f"Wrote taxonomy report: {result.taxonomy_md}")
    print(f"Wrote district category csv: {result.district_csv}")
    print(f"Wrote barrio category csv: {result.barrio_csv}")
    print(f"Wrote stats json: {result.stats_json}")
    print(f"Wrote report md: {result.report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())