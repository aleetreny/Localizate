#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.censo import load_raw_manifest
from localizate.section_geography import build_section_geography_coverage, write_section_geography_outputs


def main() -> int:
    raw_manifest = load_raw_manifest()
    summary, details, section_metadata = build_section_geography_coverage(raw_manifest)
    write_section_geography_outputs(summary, details, section_metadata)

    print("Wrote section geography metadata and coverage reports.")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
