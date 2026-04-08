#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import argparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from localizate.survival_feature_validation import validate_survival_feature_frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate activity/local survival feature frames.")
    parser.add_argument("--abt-csv", type=Path, default=PROJECT_ROOT / "data" / "features" / "activity_survival_abt.csv")
    parser.add_argument("--feature-profile", default="full")
    parser.add_argument("--output-tag", default="")
    return parser.parse_args()


def _tag_path(path: Path, tag: str) -> Path:
    clean_tag = str(tag).strip()
    if not clean_tag:
        return path
    return path.with_name(f"{path.stem}__{clean_tag}{path.suffix}")


def main() -> int:
    args = parse_args()
    result = validate_survival_feature_frame(
        abt_csv=args.abt_csv,
        feature_profile=args.feature_profile,
        metrics_json=_tag_path(PROJECT_ROOT / "models" / "survival_feature_validation.json", args.output_tag),
        report_md=_tag_path(PROJECT_ROOT / "docs" / "survival_feature_validation.md", args.output_tag),
    )
    print(f"Wrote feature validation metrics: {result.metrics_json}")
    print(f"Wrote feature validation report: {result.report_md}")
    print(f"Rows analyzed: {result.rows:,}")
    print(f"Features analyzed: {result.features}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
