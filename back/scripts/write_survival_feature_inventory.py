#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from localizate.survival_features import write_survival_feature_inventory


def main() -> int:
    path = write_survival_feature_inventory()
    print(f"Wrote feature inventory: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
