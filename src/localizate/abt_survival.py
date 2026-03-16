from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .paths import DATA_DIR, DOCS_DIR


@dataclass(frozen=True)
class SurvivalAbtBuildResult:
    output_csv: Path
    output_parquet: Path
    parquet_written: bool
    report_md: Path
    rows: int
    max_period: str


def next_period(period: str) -> str:
    year = int(period[:4])
    month = int(period[5:7])
    if month == 12:
        return f"{year + 1}-01"
    return f"{year}-{month + 1:02d}"


def build_local_survival_abt(
    *,
    geospatial_manifest_csv: Path | None = None,
    section_panel_csv: Path | None = None,
    output_csv: Path | None = None,
    output_parquet: Path | None = None,
    report_md: Path | None = None,
) -> SurvivalAbtBuildResult:
    try:
        import duckdb  # type: ignore
    except ModuleNotFoundError:
        duckdb = None

    resolved_manifest = geospatial_manifest_csv or (DATA_DIR / "processed" / "censo_geospatial_manifest.csv")
    resolved_section_panel = section_panel_csv or (DATA_DIR / "processed" / "section_socioeconomic_panel.csv")
    resolved_output_csv = output_csv or (DATA_DIR / "features" / "local_survival_abt.csv")
    resolved_output_parquet = output_parquet or (DATA_DIR / "features" / "local_survival_abt.parquet")
    resolved_report_md = report_md or (DOCS_DIR / "abt_survival.md")

    manifest = pd.read_csv(resolved_manifest)
    usable = manifest[manifest["status"].isin(["materialized", "skipped_existing"])].copy()
    if usable.empty:
        raise ValueError("Geospatial manifest has no materialized/skipped_existing periods")

    max_period = str(usable["period"].max())
    max_year = int(max_period[:4])
    max_month = int(max_period[5:7])

    resolved_output_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_output_parquet.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_md.parent.mkdir(parents=True, exist_ok=True)

    if duckdb is not None:
        con = duckdb.connect(database=":memory:")
        try:
            con.execute("PRAGMA threads=4")
            con.execute("CREATE TEMP TABLE section_panel AS SELECT * FROM read_csv_auto(?, union_by_name=true)", [str(resolved_section_panel)])

            sql = """
            WITH base AS (
                SELECT
                    CAST(id_local AS BIGINT) AS id_local,
                    snapshot_period AS period,
                    CASE
                        WHEN id_distrito_local IS NULL OR id_seccion_censal_local IS NULL THEN NULL
                        WHEN LENGTH(REGEXP_REPLACE(CAST(id_seccion_censal_local AS VARCHAR), '[^0-9]', '', 'g')) >= 5
                            THEN RIGHT(REGEXP_REPLACE(CAST(id_seccion_censal_local AS VARCHAR), '[^0-9]', '', 'g'), 5)
                        WHEN LENGTH(REGEXP_REPLACE(CAST(id_seccion_censal_local AS VARCHAR), '[^0-9]', '', 'g')) = 4
                            THEN LPAD(REGEXP_REPLACE(CAST(id_seccion_censal_local AS VARCHAR), '[^0-9]', '', 'g'), 5, '0')
                        ELSE LPAD(REGEXP_REPLACE(CAST(id_distrito_local AS VARCHAR), '[^0-9]', '', 'g'), 2, '0')
                            || LPAD(REGEXP_REPLACE(CAST(id_seccion_censal_local AS VARCHAR), '[^0-9]', '', 'g'), 3, '0')
                    END AS section_key,
                    h3_cell,
                    lat_wgs84,
                    lon_wgs84,
                    coord_transform_status
                FROM read_csv_auto(?, union_by_name=true)
                WHERE id_local IS NOT NULL
            ),
            enriched AS (
                SELECT
                    b.*,
                    s.padron_lag_months,
                    s.renta_best_eur,
                    s.share_foreign,
                    s.share_age_15_29,
                    s.share_age_30_44,
                    s.share_age_45_64,
                    s.share_age_65_plus,
                    s.population_density_km2,
                    s.geometry_available
                FROM base b
                LEFT JOIN section_panel s
                    ON b.period = s.target_period
                    AND b.section_key = s.section_key
            )
            SELECT
                id_local,
                MIN(period) AS first_seen_period,
                MAX(period) AS last_seen_period,
                COUNT(DISTINCT period) AS active_months,
                ((CAST(SUBSTR(MAX(period), 1, 4) AS INTEGER) - CAST(SUBSTR(MIN(period), 1, 4) AS INTEGER)) * 12
                  + (CAST(SUBSTR(MAX(period), 6, 2) AS INTEGER) - CAST(SUBSTR(MIN(period), 6, 2) AS INTEGER)) + 1) AS duration_months,
                CASE WHEN MAX(period) < ? THEN 1 ELSE 0 END AS event_observed,
                ? AS censor_reference_period,
                ARG_MIN(section_key, period) AS section_key_start,
                ARG_MIN(h3_cell, period) AS h3_cell_start,
                ARG_MIN(lat_wgs84, period) AS lat_wgs84_start,
                ARG_MIN(lon_wgs84, period) AS lon_wgs84_start,
                ARG_MIN(coord_transform_status, period) AS coord_transform_status_start,
                ARG_MIN(padron_lag_months, period) AS padron_lag_months_start,
                ARG_MIN(renta_best_eur, period) AS renta_best_eur_start,
                ARG_MIN(share_foreign, period) AS share_foreign_start,
                ARG_MIN(share_age_15_29, period) AS share_age_15_29_start,
                ARG_MIN(share_age_30_44, period) AS share_age_30_44_start,
                ARG_MIN(share_age_45_64, period) AS share_age_45_64_start,
                ARG_MIN(share_age_65_plus, period) AS share_age_65_plus_start,
                ARG_MIN(population_density_km2, period) AS population_density_km2_start,
                ARG_MIN(geometry_available, period) AS geometry_available_start
            FROM enriched
            GROUP BY id_local
            ORDER BY first_seen_period, id_local
            """

            abt = con.execute(
                sql,
                [str(DATA_DIR / "processed" / "censo_geospatial" / "locales" / "*.csv.gz"), max_period, max_period],
            ).df()
        finally:
            con.close()
    else:
        abt = _build_local_survival_abt_with_pandas(
            usable,
            pd.read_csv(
                resolved_section_panel,
                low_memory=False,
                dtype={
                    "target_period": "string",
                    "section_key": "string",
                },
            ),
            max_period=max_period,
        )

    abt.to_csv(resolved_output_csv, index=False)
    parquet_written = True
    try:
        abt.to_parquet(resolved_output_parquet, index=False)
    except ImportError:
        parquet_written = False

    report = _render_abt_report(abt, max_period=max_period, max_year=max_year, max_month=max_month)
    resolved_report_md.write_text(report, encoding="utf-8")

    return SurvivalAbtBuildResult(
        output_csv=resolved_output_csv,
        output_parquet=resolved_output_parquet,
        parquet_written=parquet_written,
        report_md=resolved_report_md,
        rows=len(abt),
        max_period=max_period,
    )


def _render_abt_report(abt: pd.DataFrame, *, max_period: str, max_year: int, max_month: int) -> str:
    if abt.empty:
        return "# ABT Survival\n\nNo se genero ninguna fila en la ABT.\n"

    event_rate = float(pd.to_numeric(abt["event_observed"], errors="coerce").fillna(0).mean())
    duration_median = float(pd.to_numeric(abt["duration_months"], errors="coerce").median())
    with_h3 = int(abt["h3_cell_start"].notna().sum())
    with_renta = int(pd.to_numeric(abt["renta_best_eur_start"], errors="coerce").notna().sum())

    lines: list[str] = []
    lines.append("# ABT Survival")
    lines.append("")
    lines.append("ABT baseline por local (una fila por `id_local`) con target de supervivencia censurado.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Filas ABT: {len(abt):,}")
    lines.append(f"- Periodo de censura global: {max_period} ({max_year}-{max_month:02d})")
    lines.append(f"- Tasa de evento observada: {event_rate:.4f}")
    lines.append(f"- Mediana de duracion (meses): {duration_median:.1f}")
    lines.append(f"- Filas con H3 inicial: {with_h3:,}")
    lines.append(f"- Filas con renta inicial: {with_renta:,}")
    lines.append("")
    lines.append("## Columnas clave")
    lines.append("")
    lines.append("- `first_seen_period`, `last_seen_period`, `duration_months`, `event_observed`")
    lines.append("- Features iniciales PiT: `renta_best_eur_start`, `share_*_start`, `population_density_km2_start`")
    lines.append("- Geoespacial inicial: `h3_cell_start`, `lat_wgs84_start`, `lon_wgs84_start`")
    lines.append("")
    return "\n".join(lines) + "\n"


def _build_local_survival_abt_with_pandas(
    usable_manifest: pd.DataFrame,
    section_panel: pd.DataFrame,
    *,
    max_period: str,
) -> pd.DataFrame:
    section_cols = [
        "section_key",
        "padron_lag_months",
        "renta_best_eur",
        "share_foreign",
        "share_age_15_29",
        "share_age_30_44",
        "share_age_45_64",
        "share_age_65_plus",
        "population_density_km2",
        "geometry_available",
    ]

    panel_by_period: dict[str, pd.DataFrame] = {}
    for period, frame in section_panel.groupby("target_period"):
        available_cols = [column for column in section_cols if column in frame.columns]
        period_frame = frame[available_cols].copy()
        if "section_key" in period_frame.columns:
            period_frame["section_key"] = (
                period_frame["section_key"].astype("string").str.extract(r"(\d+)", expand=False).astype("string").str.zfill(5)
            )
        panel_by_period[str(period)] = period_frame

    abt = pd.DataFrame()
    usable_sorted = usable_manifest.sort_values("period").reset_index(drop=True)
    for period, output_path in usable_sorted[["period", "output_path"]].itertuples(index=False):
        path = Path(str(output_path))
        if not path.exists():
            continue

        frame = pd.read_csv(
            path,
            usecols=[
                "id_local",
                "id_distrito_local",
                "id_seccion_censal_local",
                "h3_cell",
                "lat_wgs84",
                "lon_wgs84",
                "coord_transform_status",
            ],
            low_memory=False,
        )
        frame["id_local"] = pd.to_numeric(frame["id_local"], errors="coerce").astype("Int64")
        frame = frame.dropna(subset=["id_local"]).copy()
        frame["id_local"] = frame["id_local"].astype("int64")

        district = pd.to_numeric(frame["id_distrito_local"], errors="coerce").astype("Int64").astype("string").str.zfill(2)
        section_raw = pd.to_numeric(frame["id_seccion_censal_local"], errors="coerce").astype("Int64").astype("string")

        section_key = pd.Series(pd.NA, index=frame.index, dtype="string")
        section_len = section_raw.str.len()
        mask_len_ge_5 = section_len >= 5
        mask_len_4 = section_len == 4
        mask_other = ~(mask_len_ge_5 | mask_len_4)

        section_key.loc[mask_len_ge_5] = section_raw.loc[mask_len_ge_5].str[-5:]
        section_key.loc[mask_len_4] = section_raw.loc[mask_len_4].str.zfill(5)
        section_key.loc[mask_other] = district.loc[mask_other] + section_raw.loc[mask_other].str.zfill(3)
        frame["section_key"] = section_key

        period_panel = panel_by_period.get(str(period))
        if period_panel is not None and not period_panel.empty:
            frame = frame.merge(period_panel, on="section_key", how="left")

        frame["first_seen_period"] = str(period)
        frame["last_seen_period"] = str(period)
        frame["active_months"] = 1

        rename_map = {
            "section_key": "section_key_start",
            "h3_cell": "h3_cell_start",
            "lat_wgs84": "lat_wgs84_start",
            "lon_wgs84": "lon_wgs84_start",
            "coord_transform_status": "coord_transform_status_start",
            "padron_lag_months": "padron_lag_months_start",
            "renta_best_eur": "renta_best_eur_start",
            "share_foreign": "share_foreign_start",
            "share_age_15_29": "share_age_15_29_start",
            "share_age_30_44": "share_age_30_44_start",
            "share_age_45_64": "share_age_45_64_start",
            "share_age_65_plus": "share_age_65_plus_start",
            "population_density_km2": "population_density_km2_start",
            "geometry_available": "geometry_available_start",
        }
        frame = frame.rename(columns=rename_map)
        frame = frame.drop_duplicates(subset=["id_local"], keep="first")

        selected_columns = [
            "id_local",
            "first_seen_period",
            "last_seen_period",
            "active_months",
            "section_key_start",
            "h3_cell_start",
            "lat_wgs84_start",
            "lon_wgs84_start",
            "coord_transform_status_start",
            "padron_lag_months_start",
            "renta_best_eur_start",
            "share_foreign_start",
            "share_age_15_29_start",
            "share_age_30_44_start",
            "share_age_45_64_start",
            "share_age_65_plus_start",
            "population_density_km2_start",
            "geometry_available_start",
        ]
        frame = frame[[column for column in selected_columns if column in frame.columns]].set_index("id_local")

        if abt.empty:
            abt = frame.copy()
            continue

        existing_mask = frame.index.isin(abt.index)
        updates = frame[existing_mask]
        additions = frame[~existing_mask]

        if not updates.empty:
            abt.loc[updates.index, "last_seen_period"] = str(period)
            abt.loc[updates.index, "active_months"] = pd.to_numeric(abt.loc[updates.index, "active_months"], errors="coerce").fillna(0) + 1

        if not additions.empty:
            abt = pd.concat([abt, additions], axis=0)

    if abt.empty:
        return pd.DataFrame()

    abt = abt.reset_index().rename(columns={"index": "id_local"})
    first_year = pd.to_numeric(abt["first_seen_period"].astype(str).str[:4], errors="coerce")
    first_month = pd.to_numeric(abt["first_seen_period"].astype(str).str[5:7], errors="coerce")
    last_year = pd.to_numeric(abt["last_seen_period"].astype(str).str[:4], errors="coerce")
    last_month = pd.to_numeric(abt["last_seen_period"].astype(str).str[5:7], errors="coerce")

    abt["duration_months"] = ((last_year - first_year) * 12 + (last_month - first_month) + 1).astype("Int64")
    abt["event_observed"] = (abt["last_seen_period"].astype(str) < str(max_period)).astype(int)
    abt["censor_reference_period"] = str(max_period)

    ordered = [
        "id_local",
        "first_seen_period",
        "last_seen_period",
        "active_months",
        "duration_months",
        "event_observed",
        "censor_reference_period",
        "section_key_start",
        "h3_cell_start",
        "lat_wgs84_start",
        "lon_wgs84_start",
        "coord_transform_status_start",
        "padron_lag_months_start",
        "renta_best_eur_start",
        "share_foreign_start",
        "share_age_15_29_start",
        "share_age_30_44_start",
        "share_age_45_64_start",
        "share_age_65_plus_start",
        "population_density_km2_start",
        "geometry_available_start",
    ]
    return abt[[column for column in ordered if column in abt.columns]].sort_values(["first_seen_period", "id_local"]).reset_index(drop=True)
