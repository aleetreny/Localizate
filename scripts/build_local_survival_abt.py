#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from localizate.abt_survival import build_local_survival_abt


def main() -> int:
    result = build_local_survival_abt()
    print(f"Wrote ABT CSV: {result.output_csv}")
    if result.parquet_written:
        print(f"Wrote ABT Parquet: {result.output_parquet}")
    else:
        print(f"Skipped ABT Parquet (pyarrow/fastparquet unavailable): {result.output_parquet}")
    print(f"Wrote change candidates audit CSV: {result.change_candidates_csv}")
    print(f"Wrote normalization audit CSV: {result.normalization_audit_csv}")
    print(f"Wrote ABT report: {result.report_md}")
    print(f"Rows in ABT: {result.rows:,}")
    print(f"Censor reference period: {result.max_period}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
