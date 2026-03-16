#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> int:
    from localizate.modeling_readiness import run_modeling_readiness_check

    result = run_modeling_readiness_check()
    print(f"Wrote readiness report: {result.report_md}")
    print(f"Wrote readiness json: {result.report_json}")
    print(f"Readiness status: {result.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
