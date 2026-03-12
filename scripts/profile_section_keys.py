#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.censo import load_raw_manifest
from localizate.section_keys import build_section_key_coverage, write_section_key_coverage_outputs


def main() -> int:
    raw_manifest = load_raw_manifest()
    summary, details = build_section_key_coverage(raw_manifest)
    write_section_key_coverage_outputs(summary, details)

    print("Wrote section key coverage summary and detail reports.")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
