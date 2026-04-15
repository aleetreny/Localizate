from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .censo import load_and_normalize_censo_snapshot
from .paths import DATA_DIR


NUMERIC_PROFILE_COLUMNS: tuple[str, ...] = (
    "locales_rows",
    "locales_unique_ids",
    "locales_duplicate_id_rows",
    "locales_with_best_coords",
    "locales_without_best_coords",
    "locales_coordinate_local_valid",
    "locales_coordinate_group_valid",
    "locales_coordinate_local_noncanonical",
    "locales_coordinate_missing",
    "locales_status_abierto",
    "locales_status_cerrado",
    "locales_status_baja",
    "actividades_rows",
    "actividades_unique_local_ids",
    "actividades_unique_epigrafes",
    "avg_activities_per_local",
    "local_ids_missing_in_actividades",
    "activity_ids_not_in_locales",
)


def profile_censo_snapshots(
    snapshot_manifest: pd.DataFrame,
    *,
    periods: list[str] | None = None,
) -> pd.DataFrame:
    target_manifest = snapshot_manifest.copy()
    if periods:
        target_manifest = target_manifest[target_manifest["period"].isin(periods)].copy()

    profile_rows: list[dict[str, object]] = []

    for row in target_manifest.sort_values("period").itertuples(index=False):
        locales_frame, locales_meta = load_and_normalize_censo_snapshot(
            dataset_name="locales",
            period=row.period,
            snapshot_manifest=snapshot_manifest,
        )
        locales_ids = locales_frame["id_local"].dropna()
        locale_id_set = set(locales_ids.astype("Int64").dropna().astype(int).tolist())

        profile_row: dict[str, object] = {
            "period": row.period,
            "snapshot_date": row.snapshot_date,
            "coord_crs_status": row.coord_crs_status,
            "coord_crs_hint": row.coord_crs_hint,
            "coverage_status": row.coverage_status,
            "has_actividades": bool(row.has_actividades),
            "locales_rows": len(locales_frame),
            "locales_unique_ids": int(locales_ids.nunique(dropna=True)),
            "locales_duplicate_id_rows": int(len(locales_frame) - locales_ids.nunique(dropna=True)),
            "locales_reader_mode": locales_meta.reader_mode,
            "locales_raw_encoding": locales_meta.encoding,
            "locales_with_best_coords": int(locales_frame["x_utm_best"].notna().sum()),
            "locales_without_best_coords": int(locales_frame["x_utm_best"].isna().sum()),
            "locales_coordinate_local_valid": int((locales_frame["coordinate_source_best"] == "local_valid").sum()),
            "locales_coordinate_group_valid": int((locales_frame["coordinate_source_best"] == "group_valid").sum()),
            "locales_coordinate_local_noncanonical": int(
                (locales_frame["coordinate_source_best"] == "local_noncanonical").sum()
            ),
            "locales_coordinate_missing": int((locales_frame["coordinate_source_best"] == "missing").sum()),
            "locales_status_abierto": int(
                locales_frame["desc_situacion_local"].fillna("").astype(str).str.strip().str.lower().eq("abierto").sum()
            ),
            "locales_status_cerrado": int(
                locales_frame["desc_situacion_local"].fillna("").astype(str).str.strip().str.lower().eq("cerrado").sum()
            ),
            "locales_status_baja": int(
                locales_frame["desc_situacion_local"].fillna("").astype(str).str.strip().str.lower().eq("baja").sum()
            ),
        }

        if row.has_actividades:
            actividades_frame, actividades_meta = load_and_normalize_censo_snapshot(
                dataset_name="actividades",
                period=row.period,
                snapshot_manifest=snapshot_manifest,
            )
            activity_ids = actividades_frame["id_local"].dropna()
            activity_id_set = set(activity_ids.astype("Int64").dropna().astype(int).tolist())

            profile_row.update(
                {
                    "actividades_rows": len(actividades_frame),
                    "actividades_unique_local_ids": int(activity_ids.nunique(dropna=True)),
                    "actividades_reader_mode": actividades_meta.reader_mode,
                    "actividades_raw_encoding": actividades_meta.encoding,
                    "actividades_unique_epigrafes": int(actividades_frame["id_epigrafe"].nunique(dropna=True)),
                    "avg_activities_per_local": round(len(actividades_frame) / max(activity_ids.nunique(dropna=True), 1), 4),
                    "local_ids_missing_in_actividades": int(len(locale_id_set - activity_id_set)),
                    "activity_ids_not_in_locales": int(len(activity_id_set - locale_id_set)),
                }
            )
        else:
            profile_row.update(
                {
                    "actividades_rows": float("nan"),
                    "actividades_unique_local_ids": float("nan"),
                    "actividades_reader_mode": None,
                    "actividades_raw_encoding": None,
                    "actividades_unique_epigrafes": float("nan"),
                    "avg_activities_per_local": float("nan"),
                    "local_ids_missing_in_actividades": float("nan"),
                    "activity_ids_not_in_locales": float("nan"),
                }
            )

        profile_rows.append(profile_row)

    frame = pd.DataFrame(profile_rows)
    for column in NUMERIC_PROFILE_COLUMNS:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def materialize_normalized_censo_period(
    period: str,
    snapshot_manifest: pd.DataFrame,
    *,
    output_root: Path | None = None,
    compression: str = "gzip",
) -> list[Path]:
    resolved_root = output_root or (DATA_DIR / "intermediate" / "censo_snapshots")
    written_paths: list[Path] = []

    for dataset_name in ("locales", "actividades"):
        try:
            frame, _ = load_and_normalize_censo_snapshot(
                dataset_name=dataset_name,
                period=period,
                snapshot_manifest=snapshot_manifest,
            )
        except KeyError:
            continue

        target_dir = resolved_root / dataset_name
        target_dir.mkdir(parents=True, exist_ok=True)
        suffix = ".csv.gz" if compression == "gzip" else ".csv"
        target_path = target_dir / f"{period}{suffix}"
        frame.to_csv(target_path, index=False, compression=compression if compression == "gzip" else None)
        written_paths.append(target_path)

    return written_paths


def materialize_and_profile_censo_period(
    period: str,
    snapshot_manifest: pd.DataFrame,
    *,
    output_root: Path | None = None,
    compression: str = "gzip",
    skip_existing: bool = True,
) -> list[dict[str, Any]]:
    resolved_root = output_root or (DATA_DIR / "intermediate" / "censo_snapshots")
    manifest_row = snapshot_manifest[snapshot_manifest["period"] == period]
    if manifest_row.empty:
        raise KeyError(f"Unknown period: {period}")

    row = manifest_row.iloc[0]
    period_results: list[dict[str, Any]] = []

    for dataset_name in ("locales", "actividades"):
        dataset_available = dataset_name == "locales" or bool(row["has_actividades"])
        target_dir = resolved_root / dataset_name
        target_dir.mkdir(parents=True, exist_ok=True)
        suffix = ".csv.gz" if compression == "gzip" else ".csv"
        target_path = target_dir / f"{period}{suffix}"

        base_result: dict[str, Any] = {
            "period": period,
            "dataset": dataset_name,
            "dataset_available": dataset_available,
            "coverage_status": row["coverage_status"],
            "coord_crs_status": row["coord_crs_status"],
            "output_path": str(target_path),
            "status": "pending",
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

        if not dataset_available:
            base_result["status"] = "missing_in_manifest"
            period_results.append(base_result)
            continue

        if skip_existing and target_path.exists():
            base_result["status"] = "skipped_existing"
            period_results.append(base_result)
            continue

        frame, read_metadata = load_and_normalize_censo_snapshot(
            dataset_name=dataset_name,
            period=period,
            snapshot_manifest=snapshot_manifest,
        )
        frame.to_csv(target_path, index=False, compression=compression if compression == "gzip" else None)

        base_result.update(
            {
                "status": "materialized",
                "rows": len(frame),
                "raw_encoding": read_metadata.encoding,
                "raw_delimiter": read_metadata.delimiter,
                "raw_reader_mode": read_metadata.reader_mode,
            }
        )

        if dataset_name == "locales":
            base_result.update(
                {
                    "locales_with_best_coords": int(frame["x_utm_best"].notna().sum()),
                    "locales_without_best_coords": int(frame["x_utm_best"].isna().sum()),
                    "locales_coordinate_missing": int((frame["coordinate_source_best"] == "missing").sum()),
                }
            )
        else:
            base_result.update(
                {
                    "actividades_unique_local_ids": int(frame["id_local"].nunique(dropna=True)),
                    "actividades_unique_epigrafes": int(frame["id_epigrafe"].nunique(dropna=True)),
                }
            )

        period_results.append(base_result)

    return period_results


def render_censo_profile_markdown(profile: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Censo Snapshot Profile")
    lines.append("")
    lines.append("Perfil operativo y de calidad de los snapshots canonicos del censo historico.")
    lines.append("")

    if profile.empty:
        lines.append("No hay periodos perfilados.")
        return "\n".join(lines) + "\n"

    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Periodos perfilados: {len(profile)}")
    lines.append(f"- Periodos con actividades: {int(profile['has_actividades'].sum())}")
    lines.append(
        f"- Periodos que necesitaron reparacion de parser en locales: "
        f"{int(profile['locales_reader_mode'].astype(str).eq('last_column_overflow_fix').sum())}"
    )
    lines.append(
        f"- Periodos que necesitaron reparacion de parser en actividades: "
        f"{int(profile['actividades_reader_mode'].astype(str).eq('last_column_overflow_fix').sum())}"
    )
    lines.append("")

    lines.append("## Periodos con incidencias relevantes")
    lines.append("")
    missing_activity_ids = pd.to_numeric(profile["local_ids_missing_in_actividades"], errors="coerce").fillna(0)
    extra_activity_ids = pd.to_numeric(profile["activity_ids_not_in_locales"], errors="coerce").fillna(0)
    issue_profile = profile[
        (profile["coverage_status"] != "complete")
        | (profile["locales_reader_mode"] != "pandas_default")
        | (missing_activity_ids > 0)
        | (extra_activity_ids > 0)
    ].copy()
    if issue_profile.empty:
        lines.append("No se detectan incidencias operativas en los periodos perfilados.")
        lines.append("")
    else:
        lines.append("| Periodo | Cobertura | Reader locales | Reader actividades | IDs sin actividad | IDs fuera de locales |")
        lines.append("| --- | --- | --- | --- | ---: | ---: |")
        for row in issue_profile.itertuples(index=False):
            lines.append(
                f"| {row.period} | {row.coverage_status} | {row.locales_reader_mode} | "
                f"{row.actividades_reader_mode if pd.notna(row.actividades_reader_mode) else '-'} | "
                f"{int(row.local_ids_missing_in_actividades) if pd.notna(row.local_ids_missing_in_actividades) else 0} | "
                f"{int(row.activity_ids_not_in_locales) if pd.notna(row.activity_ids_not_in_locales) else 0} |"
            )
        lines.append("")

    lines.append("## Muestra del perfil")
    lines.append("")
    lines.append("| Periodo | Locales | Coord OK | Coord missing | Actividades | Avg acts/local | CRS |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for row in profile.head(15).itertuples(index=False):
        avg_acts = f"{row.avg_activities_per_local:.3f}" if pd.notna(row.avg_activities_per_local) else "-"
        acts_rows = int(row.actividades_rows) if pd.notna(row.actividades_rows) else 0
        lines.append(
            f"| {row.period} | {int(row.locales_rows)} | {int(row.locales_with_best_coords)} | "
            f"{int(row.locales_coordinate_missing)} | {acts_rows} | {avg_acts} | {row.coord_crs_status} |"
        )
    lines.append("")

    return "\n".join(lines) + "\n"
