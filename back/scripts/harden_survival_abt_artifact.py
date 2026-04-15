#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.survival_features import (  # noqa: E402
    attach_avisos_features,
    attach_section_reference_fallbacks,
    compute_metro_features,
)


AVISOS_COLUMNS = [
    "avisos_district_prev_year",
    "avisos_district_per_1000_prev_year",
    "avisos_barrio_prev_year",
    "avisos_barrio_per_1000_prev_year",
    "avisos_barrio_share_of_district_prev_year",
]

METRO_COLUMNS = [
    "metro_distance_m_start",
    "metro_access_count_500m_start",
    "metro_access_count_1000m_start",
    "missing_metro_distance_start",
]


def main() -> int:
    abt_path = PROJECT_ROOT / "storage" / "data" / "features" / "local_survival_abt.csv"
    parquet_path = PROJECT_ROOT / "storage" / "data" / "features" / "local_survival_abt.parquet"

    abt = pd.read_csv(abt_path, low_memory=False)
    abt = attach_section_reference_fallbacks(abt)
    abt = abt.drop(columns=[column for column in AVISOS_COLUMNS + METRO_COLUMNS if column in abt.columns])
    abt = attach_avisos_features(abt)
    metro = compute_metro_features(abt)
    for column in metro.columns:
        abt[column] = metro[column]

    abt.to_csv(abt_path, index=False)
    try:
        abt.to_parquet(parquet_path, index=False)
    except Exception:
        pass

    metro_distance = pd.to_numeric(abt["metro_distance_m_start"], errors="coerce")
    summary = {
        "rows": len(abt),
        "district_missing": int(abt["district_code_start"].isna().sum()),
        "barrio_missing": int(abt["barrio_code_start"].isna().sum()),
        "geometry_missing": int(abt["geometry_available_start"].isna().sum()),
        "metro_missing": int(metro_distance.isna().sum()),
        "metro_gt_10000": int((metro_distance > 10000).sum()),
    }
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
