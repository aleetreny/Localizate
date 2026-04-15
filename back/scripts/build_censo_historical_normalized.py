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
    parser = argparse.ArgumentParser(
        description="Materialize and audit full historical normalized censo snapshots (locales + actividades)."
    )
    parser.add_argument(
        "--raw-manifest",
        type=Path,
        default=DATA_DIR / "intermediate" / "raw_manifest.csv",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DATA_DIR / "intermediate" / "censo_snapshots",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=DATA_DIR / "processed" / "censo_historical_materialization_manifest.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=DOCS_DATA_DIR / "censo_historical_materialization.md",
    )
    parser.add_argument(
        "--period",
        action="append",
        dest="periods",
        help="Optional period(s) to process, e.g. --period 2026-03",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Process only first N periods after filters.",
    )
    parser.add_argument(
        "--start-period",
        default="2015-01",
        help="Minimum period to process (default 2015-01).",
    )
    parser.add_argument(
        "--end-period",
        help="Maximum period to process (YYYY-MM).",
    )
    parser.add_argument(
        "--year",
        type=int,
        action="append",
        dest="years",
        help="Restrict processing to one or more years (repeatable).",
    )
    parser.add_argument(
        "--rebuild-existing",
        action="store_true",
        help="Re-materialize files even if they already exist.",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Generate the full execution plan (exists/missing) without reading or materializing source files.",
    )
    return parser.parse_args()


def _render_markdown(results: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Censo Historical Materialization")
    lines.append("")
    lines.append("Materializacion historica incremental de snapshots normalizados del censo (locales + actividades).")
    lines.append("")

    if results.empty:
        lines.append("No se procesaron periodos.")
        return "\n".join(lines) + "\n"

    locales = results[results["dataset"] == "locales"].copy()
    actividades = results[results["dataset"] == "actividades"].copy()

    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Filas de manifest: {len(results)}")
    lines.append(f"- Periodos procesados: {results['period'].nunique()}")
    lines.append(f"- Materializados: {int((results['status'] == 'materialized').sum())}")
    lines.append(f"- Saltados por cache: {int((results['status'] == 'skipped_existing').sum())}")
    lines.append(f"- Sin dataset en manifest (actividades faltantes): {int((results['status'] == 'missing_in_manifest').sum())}")
    lines.append("")

    if not locales.empty:
        coord_total = pd.to_numeric(locales["locales_with_best_coords"], errors="coerce").fillna(0).sum()
        coord_missing = pd.to_numeric(locales["locales_coordinate_missing"], errors="coerce").fillna(0).sum()
        total_rows = pd.to_numeric(locales["rows"], errors="coerce").fillna(0).sum()
        coord_coverage = (coord_total / total_rows) if total_rows else 0
        lines.append("## Calidad coordenadas (locales)")
        lines.append("")
        lines.append(f"- Filas locales (materializadas en esta ejecucion): {int(total_rows):,}")
        lines.append(f"- Filas con coordenada best disponible: {int(coord_total):,}")
        lines.append(f"- Filas con coordenada missing: {int(coord_missing):,}")
        lines.append(f"- Cobertura coordenada best: {coord_coverage:.2%}")
        lines.append("")

    missing_acts_periods = (
        actividades[actividades["status"] == "missing_in_manifest"]["period"].drop_duplicates().sort_values().tolist()
    )
    lines.append("## Cobertura actividades")
    lines.append("")
    lines.append(
        f"- Periodos sin actividades en manifest: {', '.join(missing_acts_periods) if missing_acts_periods else 'ninguno'}"
    )
    lines.append("")

    lines.append("## Ultimos periodos")
    lines.append("")
    lines.append("| Periodo | Dataset | Estado | Filas | Reader mode |")
    lines.append("| --- | --- | --- | ---: | --- |")
    tail = results.sort_values(["period", "dataset"]).tail(20)
    for row in tail.itertuples(index=False):
        row_count = int(row.rows) if pd.notna(row.rows) else 0
        reader_mode = row.raw_reader_mode if pd.notna(row.raw_reader_mode) else "-"
        lines.append(f"| {row.period} | {row.dataset} | {row.status} | {row_count} | {reader_mode} |")
    lines.append("")

    return "\n".join(lines) + "\n"


def _build_plan_rows(
    snapshot_manifest: pd.DataFrame,
    target_periods: list[str],
    *,
    output_root: Path,
    rebuild_existing: bool,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    target = snapshot_manifest[snapshot_manifest["period"].isin(target_periods)].copy()

    for row in target.itertuples(index=False):
        for dataset_name in ("locales", "actividades"):
            dataset_available = dataset_name == "locales" or bool(row.has_actividades)
            target_path = output_root / dataset_name / f"{row.period}.csv.gz"
            exists = target_path.exists()
            if not dataset_available:
                status = "missing_in_manifest"
            elif exists and not rebuild_existing:
                status = "skipped_existing"
            else:
                status = "planned_materialize"

            rows.append(
                {
                    "period": row.period,
                    "dataset": dataset_name,
                    "dataset_available": dataset_available,
                    "coverage_status": row.coverage_status,
                    "coord_crs_status": row.coord_crs_status,
                    "output_path": str(target_path),
                    "status": status,
                    "rows": pd.NA,
                    "raw_encoding": pd.NA,
                    "raw_delimiter": pd.NA,
                    "raw_reader_mode": pd.NA,
                    "locales_with_best_coords": pd.NA,
                    "locales_without_best_coords": pd.NA,
                    "locales_coordinate_missing": pd.NA,
                    "actividades_unique_local_ids": pd.NA,
                    "actividades_unique_epigrafes": pd.NA,
                }
            )

    return rows


def _apply_period_filters(snapshot_manifest: pd.DataFrame, args: argparse.Namespace) -> list[str]:
    target_periods = snapshot_manifest[snapshot_manifest["period"] >= args.start_period]["period"].tolist()
    if args.end_period:
        target_periods = [period for period in target_periods if period <= args.end_period]
    if args.years:
        allowed = {int(year) for year in args.years}
        target_periods = [period for period in target_periods if int(period[:4]) in allowed]
    if args.periods:
        requested = set(args.periods)
        target_periods = [period for period in target_periods if period in requested]
    if args.limit is not None:
        target_periods = target_periods[: args.limit]
    return target_periods


def _upsert_manifest(existing: pd.DataFrame, incoming: pd.DataFrame) -> pd.DataFrame:
    if existing.empty:
        return incoming.sort_values(["period", "dataset"]).reset_index(drop=True)
    if incoming.empty:
        return existing.sort_values(["period", "dataset"]).reset_index(drop=True)

    key_cols = ["period", "dataset"]
    existing_keyed = existing.set_index(key_cols)
    incoming_keyed = incoming.set_index(key_cols)
    merged = existing_keyed.combine_first(incoming_keyed)
    merged.update(incoming_keyed)
    return merged.reset_index().sort_values(key_cols).reset_index(drop=True)


def main() -> int:
    from localizate.censo import build_censo_snapshot_manifest, load_raw_manifest
    from localizate.censo_profile import materialize_and_profile_censo_period

    args = parse_args()
    raw_manifest = load_raw_manifest(args.raw_manifest)
    snapshot_manifest = build_censo_snapshot_manifest(raw_manifest)
    target_periods = _apply_period_filters(snapshot_manifest, args)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)

    existing_manifest = pd.DataFrame()
    if args.output_csv.exists():
        existing_manifest = pd.read_csv(args.output_csv)

    if args.plan_only:
        plan_rows = _build_plan_rows(
            snapshot_manifest,
            target_periods,
            output_root=args.output_root,
            rebuild_existing=args.rebuild_existing,
        )
        result = _upsert_manifest(existing_manifest, pd.DataFrame(plan_rows))
        result.to_csv(args.output_csv, index=False)
        args.output_md.write_text(_render_markdown(result), encoding="utf-8")
        print("Plan-only mode completed.")
        print(f"Wrote materialization manifest: {args.output_csv}")
        print(f"Wrote report: {args.output_md}")
        print(f"Rows in manifest: {len(result)}")
        return 0

    all_rows: list[dict[str, object]] = []
    total = len(target_periods)

    for index, period in enumerate(target_periods, start=1):
        period_rows = materialize_and_profile_censo_period(
            period,
            snapshot_manifest,
            output_root=args.output_root,
            skip_existing=not args.rebuild_existing,
        )
        all_rows.extend(period_rows)

        period_df = pd.DataFrame(period_rows)
        statuses = ", ".join(
            f"{dataset}:{status}"
            for dataset, status in period_df[["dataset", "status"]].itertuples(index=False)
        )
        print(f"[{index}/{total}] {period} -> {statuses}", flush=True)

    result = pd.DataFrame(all_rows)
    result = _upsert_manifest(existing_manifest, result)
    result.to_csv(args.output_csv, index=False)
    args.output_md.write_text(_render_markdown(result), encoding="utf-8")

    print(f"Wrote materialization manifest: {args.output_csv}")
    print(f"Wrote report: {args.output_md}")
    print(f"Rows in manifest: {len(result)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
