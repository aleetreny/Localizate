#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.censo import build_censo_snapshot_manifest, load_raw_manifest
from localizate.paths import DATA_DIR, DOCS_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical snapshot manifest for the historical census.")
    parser.add_argument(
        "--raw-manifest",
        type=Path,
        default=DATA_DIR / "intermediate" / "raw_manifest.csv",
    )
    parser.add_argument(
        "--output-parquet",
        type=Path,
        default=DATA_DIR / "processed" / "censo_snapshot_manifest.parquet",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=DATA_DIR / "processed" / "censo_snapshot_manifest.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=DOCS_DIR / "censo_snapshot_manifest.md",
    )
    return parser.parse_args()


def render_markdown(snapshot_manifest) -> str:
    lines: list[str] = []
    lines.append("# Censo Snapshot Manifest")
    lines.append("")
    lines.append("Manifest canonico de snapshots del censo historico desde el corte de pureza 2015-01.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Periodos de locales: {len(snapshot_manifest)}")
    lines.append(f"- Periodos con actividades disponibles: {int(snapshot_manifest['has_actividades'].sum())}")
    missing = snapshot_manifest[~snapshot_manifest["has_actividades"]]["period"].tolist()
    lines.append(f"- Periodos sin actividades: {', '.join(missing) if missing else 'ninguno'}")
    lines.append("")
    lines.append("## CRS por periodo")
    lines.append("")
    lines.append("| Periodo | CRS status | CRS hint | Cobertura |")
    lines.append("| --- | --- | --- | --- |")
    for row in snapshot_manifest.itertuples(index=False):
        lines.append(
            f"| {row.period} | {row.coord_crs_status} | {row.coord_crs_hint} | {row.coverage_status} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    raw_manifest = load_raw_manifest(args.raw_manifest)
    snapshot_manifest = build_censo_snapshot_manifest(raw_manifest)

    args.output_parquet.parent.mkdir(parents=True, exist_ok=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)

    snapshot_manifest.to_csv(args.output_csv, index=False)
    parquet_written = False
    try:
        snapshot_manifest.to_parquet(args.output_parquet, index=False)
        parquet_written = True
    except Exception as exc:
        print(f"Warning: unable to write parquet output: {exc}")
    args.output_md.write_text(render_markdown(snapshot_manifest), encoding="utf-8")

    print(f"Snapshot periods: {len(snapshot_manifest)}")
    print(f"Wrote snapshot manifest CSV: {args.output_csv}")
    if parquet_written:
        print(f"Wrote snapshot manifest parquet: {args.output_parquet}")
    print(f"Wrote report: {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
