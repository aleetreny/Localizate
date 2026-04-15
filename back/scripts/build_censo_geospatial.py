#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

DATA_DIR = PROJECT_ROOT / "storage" / "data"
DOCS_DIR = PROJECT_ROOT / "docs" / "data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build geospatial (lat/lon + H3) outputs for normalized censo locales.")
    parser.add_argument("--start-period", default="2015-01")
    parser.add_argument("--end-period")
    parser.add_argument("--period", action="append", dest="periods")
    parser.add_argument("--year", type=int, action="append", dest="years")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--h3-resolution", type=int, default=10)
    parser.add_argument(
        "--transition-policy",
        choices=["skip", "assume_etrs89", "assume_ed50"],
        default="skip",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DATA_DIR / "processed" / "censo_geospatial" / "locales",
    )
    parser.add_argument(
        "--manifest-csv",
        type=Path,
        default=DATA_DIR / "processed" / "censo_geospatial_manifest.csv",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=DOCS_DATA_DIR / "censo_geospatial.md",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip periods whose geospatial output already exists.",
    )
    return parser.parse_args()


def _apply_filters(periods: list[str], args: argparse.Namespace) -> list[str]:
    filtered = [period for period in periods if period >= args.start_period]
    if args.end_period:
        filtered = [period for period in filtered if period <= args.end_period]
    if args.years:
        allowed = {int(year) for year in args.years}
        filtered = [period for period in filtered if int(period[:4]) in allowed]
    if args.periods:
        requested = set(args.periods)
        filtered = [period for period in filtered if period in requested]
    if args.limit is not None:
        filtered = filtered[: args.limit]
    return filtered


def _render_report(manifest: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Censo Geospatial")
    lines.append("")
    lines.append("Materializacion de lat/lon y H3 sobre snapshots normalizados de locales.")
    lines.append("")

    if manifest.empty:
        lines.append("No hay periodos procesados.")
        return "\n".join(lines) + "\n"

    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Periodos en manifest: {manifest['period'].nunique()}")
    lines.append(f"- Ejecuciones materializadas: {int((manifest['status'] == 'materialized').sum())}")
    lines.append(f"- Ejecuciones saltadas por cache: {int((manifest['status'] == 'skipped_existing').sum())}")
    lines.append("")

    materialized = manifest[manifest["status"] == "materialized"].copy()
    if not materialized.empty:
        rows = pd.to_numeric(materialized["rows"], errors="coerce").fillna(0).sum()
        transformed = pd.to_numeric(materialized["rows_transformed"], errors="coerce").fillna(0).sum()
        transition_blocked = pd.to_numeric(materialized["rows_transition_requires_review"], errors="coerce").fillna(0).sum()
        h3_rows = pd.to_numeric(materialized["rows_with_h3"], errors="coerce").fillna(0).sum()
        lines.append(f"- Filas materializadas: {int(rows):,}")
        lines.append(f"- Filas transformadas a WGS84: {int(transformed):,}")
        lines.append(f"- Filas bloqueadas por transicion 2017-09: {int(transition_blocked):,}")
        lines.append(f"- Filas con H3: {int(h3_rows):,}")
        lines.append("")

    lines.append("## Ultimos periodos")
    lines.append("")
    lines.append("| Periodo | Estado | Filas | Transformadas | H3 | Transition bloqueadas |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    tail = manifest.sort_values("period").tail(24)
    for row in tail.itertuples(index=False):
        lines.append(
            f"| {row.period} | {row.status} | {int(row.rows) if pd.notna(row.rows) else 0} | "
            f"{int(row.rows_transformed) if pd.notna(row.rows_transformed) else 0} | "
            f"{int(row.rows_with_h3) if pd.notna(row.rows_with_h3) else 0} | "
            f"{int(row.rows_transition_requires_review) if pd.notna(row.rows_transition_requires_review) else 0} |"
        )
    lines.append("")

    return "\n".join(lines) + "\n"


def _upsert_manifest(existing: pd.DataFrame, incoming: pd.DataFrame) -> pd.DataFrame:
    if existing.empty:
        return incoming.sort_values(["period"]).reset_index(drop=True)
    if incoming.empty:
        return existing.sort_values(["period"]).reset_index(drop=True)

    merged = existing.copy()
    existing_index = {str(period): idx for idx, period in enumerate(merged["period"].astype(str).tolist())}

    for row in incoming.itertuples(index=False):
        period = str(row.period)
        row_dict = row._asdict()
        if period in existing_index:
            idx = existing_index[period]
            existing_status = str(merged.at[idx, "status"])
            incoming_status = str(row_dict.get("status", ""))
            if existing_status == "materialized" and incoming_status == "skipped_existing":
                continue
            for column, value in row_dict.items():
                merged.at[idx, column] = value
        else:
            merged = pd.concat([merged, pd.DataFrame([row_dict])], ignore_index=True)
            existing_index[period] = len(merged) - 1

    return merged.sort_values(["period"]).reset_index(drop=True)


def main() -> int:
    from localizate.censo import build_censo_snapshot_manifest, load_raw_manifest
    from localizate.censo_geospatial import CensoGeospatialConfig, build_censo_geospatial_period

    args = parse_args()
    raw_manifest = load_raw_manifest()
    snapshot_manifest = build_censo_snapshot_manifest(raw_manifest)

    periods = _apply_filters(snapshot_manifest["period"].tolist(), args)

    rows: list[dict[str, object]] = []
    total = len(periods)

    for index, period in enumerate(periods, start=1):
        target_path = args.output_root / f"{period}.csv.gz"
        if args.skip_existing and target_path.exists():
            rows.append(
                {
                    "period": period,
                    "status": "skipped_existing",
                    "rows": pd.NA,
                    "rows_transformed": pd.NA,
                    "rows_with_h3": pd.NA,
                    "rows_transition_requires_review": pd.NA,
                    "h3_resolution": args.h3_resolution,
                    "transition_policy": args.transition_policy,
                    "output_path": str(target_path),
                }
            )
            print(f"[{index}/{total}] {period} -> skipped_existing", flush=True)
            continue

        frame, output_path = build_censo_geospatial_period(
            period,
            snapshot_manifest=snapshot_manifest,
            output_root=args.output_root,
            config=CensoGeospatialConfig(
                h3_resolution=args.h3_resolution,
                transition_policy=args.transition_policy,
            ),
        )

        transformed_rows = int(frame["lat_wgs84"].notna().sum())
        h3_rows = int(frame["h3_cell"].notna().sum())
        transition_blocked = int((frame["coord_transform_status"] == "transition_requires_review").sum())

        rows.append(
            {
                "period": period,
                "status": "materialized",
                "rows": len(frame),
                "rows_transformed": transformed_rows,
                "rows_with_h3": h3_rows,
                "rows_transition_requires_review": transition_blocked,
                "h3_resolution": args.h3_resolution,
                "transition_policy": args.transition_policy,
                "output_path": str(output_path),
            }
        )
        print(
            f"[{index}/{total}] {period} -> materialized rows={len(frame)} transformed={transformed_rows} h3={h3_rows}",
            flush=True,
        )

    args.manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    args.report_md.parent.mkdir(parents=True, exist_ok=True)
    existing_manifest = pd.DataFrame()
    if args.manifest_csv.exists():
        existing_manifest = pd.read_csv(args.manifest_csv)

    manifest = _upsert_manifest(existing_manifest, pd.DataFrame(rows))
    manifest.to_csv(args.manifest_csv, index=False)
    args.report_md.write_text(_render_report(manifest), encoding="utf-8")

    print(f"Wrote geospatial manifest: {args.manifest_csv}")
    print(f"Wrote geospatial report: {args.report_md}")
    print(f"Rows in geospatial manifest: {len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
