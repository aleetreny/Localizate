#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from localizate.abt_survival import build_local_survival_abt


def main() -> int:
    result = build_local_survival_abt(target_mode="activity_survival")
    print(f"Wrote ABT CSV: {result.output_csv}")
    print(f"Wrote ABT report: {result.report_md}")
    print(f"Wrote glossary: {result.glossary_md}")
    print(f"Wrote activity taxonomy CSV: {result.activity_taxonomy_csv}")
    print(f"Wrote change candidates audit CSV: {result.change_candidates_csv}")
    print(f"Rows in ABT: {result.rows:,}")
    print(f"Censor reference period: {result.max_period}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())