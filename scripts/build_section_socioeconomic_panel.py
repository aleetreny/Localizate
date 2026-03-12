#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.censo import load_raw_manifest
from localizate.paths import DATA_DIR
from localizate.socioeconomics import (
    build_padron_section_panel,
    load_and_normalize_renta_madrid,
    build_section_socioeconomic_panel,
    write_optional_parquet,
    write_section_socioeconomic_outputs,
)
from localizate.section_geography import load_section_metadata


def main() -> int:
    raw_manifest = load_raw_manifest()
    print("Building padron section panel...", flush=True)
    padron_panel = build_padron_section_panel(raw_manifest)
    print("Loading renta and section metadata...", flush=True)
    renta_madrid = load_and_normalize_renta_madrid(raw_manifest)
    section_metadata = load_section_metadata(raw_manifest)
    print("Building censo-aligned section panel...", flush=True)
    section_panel = build_section_socioeconomic_panel(
        raw_manifest,
        padron_panel=padron_panel,
        renta_madrid=renta_madrid,
        section_metadata=section_metadata,
    )
    write_section_socioeconomic_outputs(padron_panel, section_panel)

    padron_parquet = DATA_DIR / "processed" / "padron_section_panel.parquet"
    section_parquet = DATA_DIR / "processed" / "section_socioeconomic_panel.parquet"
    wrote_padron_parquet = write_optional_parquet(padron_panel, padron_parquet)
    wrote_section_parquet = write_optional_parquet(section_panel, section_parquet)

    print("Wrote section socioeconomic outputs.")
    print(f"Padron parquet written: {wrote_padron_parquet}")
    print(f"Section parquet written: {wrote_section_parquet}")
    print(section_panel[['target_period', 'padron_reference_period', 'padron_lag_months']].drop_duplicates().tail().to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
