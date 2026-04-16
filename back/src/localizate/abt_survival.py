from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import unicodedata

import pandas as pd

from .activity_taxonomy import build_macro_activity_taxonomy, render_macro_glossary
from .censo import load_raw_manifest
from .paths import DATA_DIR, DOCS_MODELING_DIR, DOCS_REFERENCE_DIR, PROJECT_ROOT
from .survival_features import (
    attach_avisos_features,
    attach_external_district_features,
    attach_metro_features,
    attach_section_reference_fallbacks,
)


PLACEHOLDER_ACTIVITY_CODES = frozenset({"", "0", "-1", "PT", "NA", "N/A", "NULL"})
PLACEHOLDER_ACTIVITY_DESC_KEYS = frozenset(
    {
        "SIN ACTIVIDAD",
        "SIN ACTIVIDAD PTE DE CODIFICAR",
        "SIN ACTIVIDAD PENDIENTE DE CODIFICAR",
        "PENDIENTE DE CODIFICAR",
        "SIN CODIFICAR",
        "SIN INFORMACION",
        "SIN INFORMACIÓN",
    }
)

UNIFIED_EVENT_SOURCE = "cese_de_actividad"
EVENT_SUBTYPE_ACTIVITY_CHANGE = "cambio_actividad"
EVENT_SUBTYPE_DISAPPEARANCE = "desaparicion"
EVENT_SUBTYPE_CENSORED = "censored"


@dataclass(frozen=True)
class SurvivalAbtBuildResult:
    output_csv: Path
    output_parquet: Path
    parquet_written: bool
    report_md: Path
    glossary_md: Path
    activity_taxonomy_csv: Path
    rows: int
    max_period: str
    change_candidates_csv: Path
    normalization_audit_csv: Path


def next_period(period: str) -> str:
    year = int(period[:4])
    month = int(period[5:7])
    if month == 12:
        return f"{year + 1}-01"
    return f"{year}-{month + 1:02d}"


def months_between_inclusive(start_period: str, end_period: str) -> int:
    start_year = int(start_period[:4])
    start_month = int(start_period[5:7])
    end_year = int(end_period[:4])
    end_month = int(end_period[5:7])
    return (end_year - start_year) * 12 + (end_month - start_month) + 1


def normalize_activity_description(value: object) -> str | None:
    text = _clean_display_text(value)
    if not text:
        return None
    text = text.upper().replace("0", "O")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_activity_code(
    value: object,
    *,
    min_numeric: int | None = None,
    max_numeric: int | None = None,
    placeholders: frozenset[str] = PLACEHOLDER_ACTIVITY_CODES,
) -> str | None:
    raw = _clean_raw_code(value)
    if raw is None:
        return None
    if raw in placeholders:
        return raw
    numeric_value = _parse_integer_like(raw)
    if numeric_value is None:
        return raw
    if min_numeric is not None and numeric_value < min_numeric:
        return None
    if max_numeric is not None and numeric_value > max_numeric:
        return None
    return str(numeric_value)


def resolve_survival_target(
    *,
    first_seen_period: str,
    last_observed_period: str,
    max_period: str,
    change_event_period: str | None,
    change_event_source: str = "division_change_single_single",
) -> dict[str, object]:
    disappearance_event_period = last_observed_period if last_observed_period < max_period else None
    if change_event_period is not None and (
        disappearance_event_period is None or change_event_period <= disappearance_event_period
    ):
        event_period = change_event_period
        event_source = UNIFIED_EVENT_SOURCE
        event_subtype = EVENT_SUBTYPE_ACTIVITY_CHANGE
    elif disappearance_event_period is not None:
        event_period = disappearance_event_period
        event_source = UNIFIED_EVENT_SOURCE
        event_subtype = EVENT_SUBTYPE_DISAPPEARANCE
    else:
        event_period = None
        event_source = "censored"
        event_subtype = EVENT_SUBTYPE_CENSORED

    duration_end_period = event_period or last_observed_period
    return {
        "event_period": event_period,
        "disappearance_event_period": disappearance_event_period,
        "event_source": event_source,
        "event_subtype": event_subtype,
        "event_subtype_detail": change_event_source if event_subtype == EVENT_SUBTYPE_ACTIVITY_CHANGE else event_subtype,
        "event_observed": int(event_period is not None),
        "target_end_period": duration_end_period,
        "duration_months": months_between_inclusive(first_seen_period, duration_end_period),
    }


def build_local_survival_abt(
    *,
    geospatial_manifest_csv: Path | None = None,
    section_panel_csv: Path | None = None,
    output_csv: Path | None = None,
    output_parquet: Path | None = None,
    report_md: Path | None = None,
    change_candidates_csv: Path | None = None,
    normalization_audit_csv: Path | None = None,
    activity_taxonomy_csv: Path | None = None,
    glossary_md: Path | None = None,
    target_mode: str = "local_survival",
) -> SurvivalAbtBuildResult:
    try:
        import duckdb  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError("duckdb is required to build the survival ABT") from exc

    resolved_manifest = geospatial_manifest_csv or (DATA_DIR / "processed" / "censo_geospatial_manifest.csv")
    resolved_section_panel = section_panel_csv or (DATA_DIR / "processed" / "section_socioeconomic_panel.csv")
    if target_mode not in {"local_survival", "activity_survival", "cese_activity"}:
        raise ValueError(f"Unsupported target_mode: {target_mode}")

    activity_closure_mode = target_mode in {"activity_survival", "cese_activity"}

    if activity_closure_mode:
        default_output_csv = DATA_DIR / "features" / "activity_survival_abt.csv"
        default_output_parquet = DATA_DIR / "features" / "activity_survival_abt.parquet"
        default_report_md = DOCS_MODELING_DIR / "abt_activity_survival.md"
        default_change_candidates_csv = DATA_DIR / "processed" / "activity_category_change_candidates.csv"
    else:
        default_output_csv = DATA_DIR / "features" / "local_survival_abt.csv"
        default_output_parquet = DATA_DIR / "features" / "local_survival_abt.parquet"
        default_report_md = DOCS_MODELING_DIR / "abt_survival.md"
        default_change_candidates_csv = DATA_DIR / "processed" / "local_activity_change_candidates.csv"

    resolved_output_csv = output_csv or default_output_csv
    resolved_output_parquet = output_parquet or default_output_parquet
    resolved_report_md = report_md or default_report_md
    resolved_change_candidates_csv = change_candidates_csv or default_change_candidates_csv
    resolved_normalization_audit_csv = normalization_audit_csv or (
        DATA_DIR / "processed" / "activity_code_normalization_audit.csv"
    )
    resolved_activity_taxonomy_csv = activity_taxonomy_csv or (DATA_DIR / "processed" / "activity_macro_taxonomy.csv")
    resolved_glossary_md = glossary_md or (DOCS_REFERENCE_DIR / "ACTIVITY_GLOSSARY.md")

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
    resolved_change_candidates_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_normalization_audit_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_activity_taxonomy_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_glossary_md.parent.mkdir(parents=True, exist_ok=True)

    temp_duckdb_dir = DATA_DIR / "intermediate" / "duckdb_tmp"
    temp_duckdb_dir.mkdir(parents=True, exist_ok=True)
    duckdb_db_path = temp_duckdb_dir / "build_local_survival_abt.duckdb"
    for stale_path in (duckdb_db_path, duckdb_db_path.with_suffix(".duckdb.wal")):
        if stale_path.exists():
            stale_path.unlink()

    duckdb_threads = max(1, int(os.environ.get("LOCALIZATE_DUCKDB_THREADS", "2")))
    duckdb_memory_limit = os.environ.get("LOCALIZATE_DUCKDB_MEMORY_LIMIT", "24GB")

    con = duckdb.connect(database=str(duckdb_db_path))
    try:
        con.execute(f"PRAGMA threads={duckdb_threads}")
        con.execute("SET preserve_insertion_order=false")
        con.execute(f"PRAGMA temp_directory='{temp_duckdb_dir.as_posix()}'")
        con.execute(f"PRAGMA memory_limit='{duckdb_memory_limit}'")
        con.execute(
            "CREATE OR REPLACE TABLE section_panel_base AS SELECT * FROM read_csv_auto(?, union_by_name=true)",
            [str(resolved_section_panel)],
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE section_panel AS
            WITH normalized AS (
                SELECT
                    *,
                    CAST(target_period AS VARCHAR) AS target_period_norm,
                    CASE
                        WHEN section_key IS NULL THEN NULL
                        WHEN LENGTH(REGEXP_REPLACE(CAST(section_key AS VARCHAR), '[^0-9]', '', 'g')) >= 5
                            THEN RIGHT(REGEXP_REPLACE(CAST(section_key AS VARCHAR), '[^0-9]', '', 'g'), 5)
                        ELSE LPAD(REGEXP_REPLACE(CAST(section_key AS VARCHAR), '[^0-9]', '', 'g'), 5, '0')
                    END AS section_key_norm
                FROM section_panel_base
            ), ordered AS (
                SELECT
                    * EXCLUDE (target_period, section_key, target_period_norm, section_key_norm),
                    target_period_norm AS target_period,
                    section_key_norm AS section_key,
                    LAG(total_population, 12) OVER (PARTITION BY section_key_norm ORDER BY target_period_norm) AS total_population_lag12,
                    LAG(share_foreign, 12) OVER (PARTITION BY section_key_norm ORDER BY target_period_norm) AS share_foreign_lag12,
                    LAG(share_age_15_29, 12) OVER (PARTITION BY section_key_norm ORDER BY target_period_norm) AS share_age_15_29_lag12,
                    LAG(population_density_km2, 12) OVER (PARTITION BY section_key_norm ORDER BY target_period_norm) AS population_density_km2_lag12,
                    LAG(renta_best_eur, 12) OVER (PARTITION BY section_key_norm ORDER BY target_period_norm) AS renta_best_eur_lag12
                FROM normalized
            )
            SELECT
                *,
                total_population - total_population_lag12 AS total_population_delta_12m,
                share_foreign - share_foreign_lag12 AS share_foreign_delta_12m,
                share_age_15_29 - share_age_15_29_lag12 AS share_age_15_29_delta_12m,
                population_density_km2 - population_density_km2_lag12 AS population_density_km2_delta_12m,
                renta_best_eur - renta_best_eur_lag12 AS renta_best_eur_delta_12m
            FROM ordered
            """
        )

        activities_glob = str(DATA_DIR / "intermediate" / "censo_snapshots" / "actividades" / "*.csv.gz")
        division_summary = con.execute(
            """
            SELECT
                COALESCE(TRIM(CAST(id_division AS VARCHAR)), '') AS raw_code,
                COALESCE(TRIM(CAST(desc_division AS VARCHAR)), '') AS raw_desc,
                COUNT(*) AS n
            FROM read_csv_auto(?, union_by_name=true)
            WHERE id_division IS NOT NULL
            GROUP BY 1, 2
            """,
            [activities_glob],
        ).df()
        epigrafe_summary = con.execute(
            """
            SELECT
                COALESCE(TRIM(CAST(id_epigrafe AS VARCHAR)), '') AS raw_code,
                COALESCE(TRIM(CAST(desc_epigrafe AS VARCHAR)), '') AS raw_desc,
                COUNT(*) AS n
            FROM read_csv_auto(?, union_by_name=true)
            WHERE id_epigrafe IS NOT NULL
            GROUP BY 1, 2
            """,
            [activities_glob],
        ).df()

        division_lookup = _build_activity_lookup(
            division_summary,
            taxonomy="division",
            min_numeric=1,
            max_numeric=99,
            placeholder_codes=PLACEHOLDER_ACTIVITY_CODES,
        )
        epigrafe_lookup = _build_activity_lookup(
            epigrafe_summary,
            taxonomy="epigrafe",
            min_numeric=1,
            max_numeric=None,
            placeholder_codes=PLACEHOLDER_ACTIVITY_CODES,
        )

        normalization_audit = pd.concat([division_lookup, epigrafe_lookup], ignore_index=True)
        normalization_audit.to_csv(resolved_normalization_audit_csv, index=False)
        macro_taxonomy = build_macro_activity_taxonomy(normalization_audit)
        macro_taxonomy.to_csv(resolved_activity_taxonomy_csv, index=False)
        resolved_glossary_md.write_text(render_macro_glossary(macro_taxonomy), encoding="utf-8")

        division_lookup_by_raw_code = _collapse_activity_lookup_by_raw_code(division_lookup)
        epigrafe_lookup_by_raw_code = _collapse_activity_lookup_by_raw_code(epigrafe_lookup)

        con.register("division_lookup_df", division_lookup_by_raw_code)
        con.register("epigrafe_lookup_df", epigrafe_lookup_by_raw_code)
        con.register(
            "macro_lookup_df",
            macro_taxonomy[["epigrafe_code", "macro_category_code", "macro_category_name", "macro_category_definition"]].drop_duplicates(),
        )

        locales_glob = str(DATA_DIR / "processed" / "censo_geospatial" / "locales" / "*.csv.gz")
        con.execute(
            """
            CREATE OR REPLACE TABLE local_base_raw AS
            SELECT
                CAST(id_local AS BIGINT) AS id_local,
                CAST(snapshot_period AS VARCHAR) AS period,
                REGEXP_REPLACE(CAST(id_distrito_local AS VARCHAR), '[^0-9]', '', 'g') AS district_digits,
                REGEXP_REPLACE(CAST(id_seccion_censal_local AS VARCHAR), '[^0-9]', '', 'g') AS section_digits,
                h3_cell,
                lat_wgs84,
                lon_wgs84,
                coord_transform_status
            FROM read_csv_auto(?, union_by_name=true)
            WHERE id_local IS NOT NULL AND snapshot_period IS NOT NULL
            """,
            [locales_glob],
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE local_base AS
            WITH candidates AS (
                SELECT
                    r.*,
                    CASE
                        WHEN district_digits IS NULL OR district_digits = '' OR section_digits IS NULL OR section_digits = '' THEN NULL
                        WHEN LENGTH(section_digits) >= 5 THEN RIGHT(section_digits, 5)
                        WHEN LENGTH(section_digits) = 4 THEN LPAD(section_digits, 5, '0')
                        ELSE LPAD(district_digits, 2, '0') || LPAD(section_digits, 3, '0')
                    END AS section_key_current,
                    CASE
                        WHEN section_digits IS NULL OR section_digits = '' THEN NULL
                        WHEN LENGTH(section_digits) >= 5 AND RIGHT(section_digits, 1) = '0'
                            THEN LPAD(RIGHT(LEFT(section_digits, LENGTH(section_digits) - 1), 5), 5, '0')
                        ELSE NULL
                    END AS section_key_drop_trailing_zero,
                    CASE
                        WHEN district_digits IS NULL OR district_digits = '' OR section_digits IS NULL OR section_digits = '' THEN NULL
                        ELSE LPAD(district_digits, 2, '0') || RIGHT('000' || section_digits, 3)
                    END AS section_key_district_tail3,
                    CASE
                        WHEN district_digits IS NULL OR district_digits = '' OR section_digits IS NULL OR section_digits = '' THEN NULL
                        WHEN LENGTH(section_digits) >= 5 AND RIGHT(section_digits, 1) = '0'
                            THEN LPAD(district_digits, 2, '0') || RIGHT('000' || LEFT(section_digits, LENGTH(section_digits) - 1), 3)
                        ELSE NULL
                    END AS section_key_district_tail3_drop
                FROM local_base_raw r
            ), resolved AS (
                SELECT
                    c.id_local,
                    c.period,
                    COALESCE(
                        CASE WHEN sp_district_tail3_drop.section_key IS NOT NULL THEN c.section_key_district_tail3_drop END,
                        CASE WHEN sp_district_tail3.section_key IS NOT NULL THEN c.section_key_district_tail3 END,
                        CASE WHEN sp_drop_trailing_zero.section_key IS NOT NULL THEN c.section_key_drop_trailing_zero END,
                        CASE WHEN sp_current.section_key IS NOT NULL THEN c.section_key_current END,
                        c.section_key_district_tail3_drop,
                        c.section_key_district_tail3,
                        c.section_key_drop_trailing_zero,
                        c.section_key_current
                    ) AS section_key,
                    c.h3_cell,
                    c.lat_wgs84,
                    c.lon_wgs84,
                    c.coord_transform_status
                FROM candidates c
                LEFT JOIN section_panel sp_district_tail3_drop
                    ON c.period = sp_district_tail3_drop.target_period
                   AND c.section_key_district_tail3_drop = sp_district_tail3_drop.section_key
                LEFT JOIN section_panel sp_district_tail3
                    ON c.period = sp_district_tail3.target_period
                   AND c.section_key_district_tail3 = sp_district_tail3.section_key
                LEFT JOIN section_panel sp_drop_trailing_zero
                    ON c.period = sp_drop_trailing_zero.target_period
                   AND c.section_key_drop_trailing_zero = sp_drop_trailing_zero.section_key
                LEFT JOIN section_panel sp_current
                    ON c.period = sp_current.target_period
                   AND c.section_key_current = sp_current.section_key
            )
            SELECT
                id_local,
                period,
                section_key,
                h3_cell,
                lat_wgs84,
                lon_wgs84,
                coord_transform_status
            FROM resolved
            """
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE local_enriched AS
            SELECT
                b.*,
                s.district_code,
                s.barrio_code,
                s.padron_lag_months,
                s.total_population,
                s.age_mean,
                s.renta_best_eur,
                s.share_foreign,
                s.share_male,
                s.share_age_00_14,
                s.share_age_15_29,
                s.share_age_30_44,
                s.share_age_45_64,
                s.share_age_65_plus,
                s.population_density_km2,
                s.total_population_delta_12m,
                s.share_foreign_delta_12m,
                s.share_age_15_29_delta_12m,
                s.population_density_km2_delta_12m,
                s.renta_best_eur_delta_12m,
                s.geometry_available
            FROM local_base b
            LEFT JOIN section_panel s
                ON b.period = s.target_period
               AND b.section_key = s.section_key
            """
        )

        con.execute(
            """
            CREATE OR REPLACE TABLE activity_rows AS
            SELECT
                CAST(id_local AS BIGINT) AS id_local,
                CAST(snapshot_period AS VARCHAR) AS period,
                COALESCE(TRIM(UPPER(CAST(id_division AS VARCHAR))), '') AS division_raw_code,
                COALESCE(TRIM(CAST(desc_division AS VARCHAR)), '') AS division_raw_desc,
                COALESCE(TRIM(UPPER(CAST(id_epigrafe AS VARCHAR))), '') AS epigrafe_raw_code,
                COALESCE(TRIM(CAST(desc_epigrafe AS VARCHAR)), '') AS epigrafe_raw_desc
            FROM read_csv_auto(?, union_by_name=true)
            WHERE id_local IS NOT NULL AND snapshot_period IS NOT NULL
            """,
            [activities_glob],
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE activities_clean AS
            SELECT
                r.id_local,
                r.period,
                d.clean_code AS division_code,
                d.clean_desc AS division_desc,
                CAST(COALESCE(d.code_valid, FALSE) AS BOOLEAN) AS division_valid,
                CAST(COALESCE(d.is_placeholder, FALSE) AS BOOLEAN) AS division_is_placeholder,
                COALESCE(d.mapping_reason, 'invalid') AS division_mapping_reason,
                e.clean_code AS epigrafe_code,
                e.clean_desc AS epigrafe_desc,
                CAST(COALESCE(e.code_valid, FALSE) AS BOOLEAN) AS epigrafe_valid,
                COALESCE(e.mapping_reason, 'invalid') AS epigrafe_mapping_reason
                ,m.macro_category_code,
                m.macro_category_name,
                m.macro_category_definition
            FROM activity_rows r
            LEFT JOIN division_lookup_df d
                ON r.division_raw_code = d.raw_code
            LEFT JOIN epigrafe_lookup_df e
                ON r.epigrafe_raw_code = e.raw_code
            LEFT JOIN macro_lookup_df m
                ON e.clean_code = m.epigrafe_code
            """
        )
        _materialize_activity_period_tables(con)
        con.execute(
            """
            CREATE OR REPLACE TABLE local_activity_enriched AS
            SELECT
                l.*,
                a.division_sig,
                a.division_desc_sig,
                a.n_divisions,
                a.epigrafe_sig,
                a.epigrafe_desc_sig,
                a.n_epigrafes,
                a.macro_category_sig,
                a.macro_category_desc_sig,
                a.n_macro_categories,
                CASE WHEN a.n_divisions = 1 THEN a.division_sig ELSE NULL END AS division_code_start,
                CASE WHEN a.n_divisions = 1 THEN a.division_desc_sig ELSE NULL END AS division_desc_start,
                CASE WHEN a.n_epigrafes = 1 THEN a.epigrafe_sig ELSE NULL END AS epigrafe_code_start,
                CASE WHEN a.n_epigrafes = 1 THEN a.epigrafe_desc_sig ELSE NULL END AS epigrafe_desc_start,
                CASE WHEN a.n_macro_categories = 1 THEN a.macro_category_sig ELSE NULL END AS activity_category_code_start,
                CASE WHEN a.n_macro_categories = 1 THEN a.macro_category_desc_sig ELSE NULL END AS activity_category_desc_start
            FROM local_enriched l
            LEFT JOIN activity_periods a
                ON l.id_local = a.id_local
               AND l.period = a.period
            """
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE section_period_features AS
            WITH section_grid AS (
                SELECT DISTINCT
                    CAST(target_period AS VARCHAR) AS period,
                    section_key
                FROM section_panel
                WHERE section_key IS NOT NULL
            ), stock AS (
                SELECT
                    period,
                    section_key,
                    COUNT(DISTINCT id_local) AS section_local_count,
                    COUNT(DISTINCT CASE WHEN division_code_start IS NOT NULL THEN division_code_start END) AS section_unique_division_count,
                    COUNT(DISTINCT CASE WHEN activity_category_code_start IS NOT NULL THEN activity_category_code_start END) AS section_unique_activity_category_count,
                    AVG(CASE WHEN COALESCE(n_divisions, 0) = 1 THEN 1.0 ELSE 0.0 END) AS section_single_division_share
                FROM local_activity_enriched
                WHERE section_key IS NOT NULL
                GROUP BY 1, 2
            ), section_entry_events AS (
                WITH first_seen AS (
                    SELECT
                        id_local,
                        MIN(period) AS period
                    FROM local_activity_enriched
                    GROUP BY 1
                )
                SELECT
                    f.period,
                    l.section_key,
                    COUNT(DISTINCT l.id_local) AS section_entry_count
                FROM first_seen f
                INNER JOIN local_activity_enriched l
                    ON f.id_local = l.id_local
                   AND f.period = l.period
                WHERE l.section_key IS NOT NULL
                GROUP BY 1, 2
            ), section_exit_events AS (
                WITH last_seen AS (
                    SELECT
                        id_local,
                        MAX(period) AS period
                    FROM local_activity_enriched
                    GROUP BY 1
                )
                SELECT
                    f.period,
                    l.section_key,
                    COUNT(DISTINCT l.id_local) AS section_exit_count
                FROM last_seen f
                INNER JOIN local_activity_enriched l
                    ON f.id_local = l.id_local
                   AND f.period = l.period
                WHERE l.section_key IS NOT NULL
                  AND f.period < ?
                GROUP BY 1, 2
            ), section_division_distribution AS (
                SELECT
                    period,
                    section_key,
                    division_code_start,
                    COUNT(DISTINCT id_local) AS division_local_count
                FROM local_activity_enriched
                WHERE section_key IS NOT NULL AND division_code_start IS NOT NULL
                GROUP BY 1, 2, 3
            ), section_division_concentration AS (
                SELECT
                    d.period,
                    d.section_key,
                    SUM(POW(CAST(d.division_local_count AS DOUBLE) / CAST(s.section_local_count AS DOUBLE), 2)) AS section_division_hhi,
                    MAX(CAST(d.division_local_count AS DOUBLE) / CAST(s.section_local_count AS DOUBLE)) AS section_division_top_share
                FROM section_division_distribution d
                INNER JOIN stock s
                    ON d.period = s.period
                   AND d.section_key = s.section_key
                WHERE s.section_local_count > 0
                GROUP BY 1, 2
            ), section_activity_category_distribution AS (
                SELECT
                    period,
                    section_key,
                    activity_category_code_start,
                    COUNT(DISTINCT id_local) AS activity_category_local_count
                FROM local_activity_enriched
                WHERE section_key IS NOT NULL AND activity_category_code_start IS NOT NULL
                GROUP BY 1, 2, 3
            ), section_activity_category_concentration AS (
                SELECT
                    d.period,
                    d.section_key,
                    SUM(POW(CAST(d.activity_category_local_count AS DOUBLE) / CAST(s.section_local_count AS DOUBLE), 2)) AS section_activity_category_hhi,
                    MAX(CAST(d.activity_category_local_count AS DOUBLE) / CAST(s.section_local_count AS DOUBLE)) AS section_activity_category_top_share
                FROM section_activity_category_distribution d
                INNER JOIN stock s
                    ON d.period = s.period
                   AND d.section_key = s.section_key
                WHERE s.section_local_count > 0
                GROUP BY 1, 2
            ), base AS (
                SELECT
                    g.period,
                    g.section_key,
                    COALESCE(s.section_local_count, 0) AS section_local_count,
                    COALESCE(s.section_unique_division_count, 0) AS section_unique_division_count,
                    COALESCE(s.section_unique_activity_category_count, 0) AS section_unique_activity_category_count,
                    s.section_single_division_share,
                    COALESCE(e.section_entry_count, 0) AS section_entry_count,
                    COALESCE(x.section_exit_count, 0) AS section_exit_count,
                    dc.section_division_hhi,
                    dc.section_division_top_share,
                    ac.section_activity_category_hhi,
                    ac.section_activity_category_top_share
                FROM section_grid g
                LEFT JOIN stock s
                    ON g.period = s.period
                   AND g.section_key = s.section_key
                LEFT JOIN section_entry_events e
                    ON g.period = e.period
                   AND g.section_key = e.section_key
                LEFT JOIN section_exit_events x
                    ON g.period = x.period
                   AND g.section_key = x.section_key
                LEFT JOIN section_division_concentration dc
                    ON g.period = dc.period
                   AND g.section_key = dc.section_key
                LEFT JOIN section_activity_category_concentration ac
                    ON g.period = ac.period
                   AND g.section_key = ac.section_key
            )
            SELECT
                *,
                section_local_count - LAG(section_local_count, 12) OVER (PARTITION BY section_key ORDER BY period) AS section_local_count_delta_12m,
                SUM(section_entry_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS section_entry_count_3m,
                SUM(section_entry_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS section_entry_count_6m,
                SUM(section_entry_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS section_entry_count_12m,
                SUM(section_exit_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS section_exit_count_3m,
                SUM(section_exit_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS section_exit_count_6m,
                SUM(section_exit_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS section_exit_count_12m,
                CASE
                    WHEN section_local_count <= 0 THEN NULL
                    ELSE CAST(SUM(section_entry_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS DOUBLE)
                        / CAST(section_local_count AS DOUBLE)
                END AS section_entry_rate_12m,
                CASE
                    WHEN section_local_count <= 0 THEN NULL
                    ELSE CAST(SUM(section_exit_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS DOUBLE)
                        / CAST(section_local_count AS DOUBLE)
                END AS section_exit_rate_12m,
                SUM(section_entry_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
                    - SUM(section_exit_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS section_net_flow_12m,
                CASE
                    WHEN section_local_count <= 0 THEN NULL
                    ELSE CAST(
                        SUM(section_entry_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
                        + SUM(section_exit_count) OVER (PARTITION BY section_key ORDER BY period ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
                        AS DOUBLE
                    ) / CAST(section_local_count AS DOUBLE)
                END AS section_turnover_rate_12m
            FROM base
            """,
            [max_period],
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE section_division_features AS
            SELECT
                period,
                section_key,
                division_code_start,
                COUNT(DISTINCT id_local) AS section_same_division_local_count
            FROM local_activity_enriched
            WHERE section_key IS NOT NULL AND division_code_start IS NOT NULL
            GROUP BY 1, 2, 3
            """
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE section_activity_category_features AS
            SELECT
                period,
                section_key,
                activity_category_code_start,
                COUNT(DISTINCT id_local) AS section_same_activity_category_local_count
            FROM local_activity_enriched
            WHERE section_key IS NOT NULL AND activity_category_code_start IS NOT NULL
            GROUP BY 1, 2, 3
            """
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE local_feature_base AS
            WITH lagged_context AS (
                SELECT
                    *,
                    STRFTIME(CAST(period || '-01' AS DATE) - INTERVAL 1 MONTH, '%Y-%m') AS context_period
                FROM local_activity_enriched
            ), context_enriched AS (
                SELECT
                    l.*,
                    CASE
                        WHEN COALESCE(s_prev.section_local_count, 0) <= 0
                             AND COALESCE(s_curr.section_local_count, 0) > 0
                            THEN s_curr.section_local_count
                        ELSE COALESCE(s_prev.section_local_count, s_curr.section_local_count)
                    END AS section_local_count,
                    CASE
                        WHEN COALESCE(s_prev.section_unique_division_count, 0) <= 0
                             AND COALESCE(s_curr.section_unique_division_count, 0) > 0
                            THEN s_curr.section_unique_division_count
                        ELSE COALESCE(s_prev.section_unique_division_count, s_curr.section_unique_division_count)
                    END AS section_unique_division_count,
                    CASE
                        WHEN COALESCE(s_prev.section_unique_activity_category_count, 0) <= 0
                             AND COALESCE(s_curr.section_unique_activity_category_count, 0) > 0
                            THEN s_curr.section_unique_activity_category_count
                        ELSE COALESCE(s_prev.section_unique_activity_category_count, s_curr.section_unique_activity_category_count)
                    END AS section_unique_activity_category_count,
                    COALESCE(s_prev.section_single_division_share, s_curr.section_single_division_share) AS section_single_division_share,
                    COALESCE(s_prev.section_local_count_delta_12m, s_curr.section_local_count_delta_12m) AS section_local_count_delta_12m,
                    CASE
                        WHEN COALESCE(d_prev.section_same_division_local_count, 0) <= 0
                             AND COALESCE(d_curr.section_same_division_local_count, 0) > 0
                            THEN d_curr.section_same_division_local_count
                        ELSE COALESCE(d_prev.section_same_division_local_count, d_curr.section_same_division_local_count)
                    END AS section_same_division_local_count,
                    CASE
                        WHEN COALESCE(a_prev.section_same_activity_category_local_count, 0) <= 0
                             AND COALESCE(a_curr.section_same_activity_category_local_count, 0) > 0
                            THEN a_curr.section_same_activity_category_local_count
                        ELSE COALESCE(a_prev.section_same_activity_category_local_count, a_curr.section_same_activity_category_local_count)
                    END AS section_same_activity_category_local_count,
                    COALESCE(s_prev.section_entry_count_3m, s_curr.section_entry_count_3m) AS section_entry_count_3m,
                    COALESCE(s_prev.section_entry_count_6m, s_curr.section_entry_count_6m) AS section_entry_count_6m,
                    COALESCE(s_prev.section_entry_count_12m, s_curr.section_entry_count_12m) AS section_entry_count_12m,
                    COALESCE(s_prev.section_exit_count_3m, s_curr.section_exit_count_3m) AS section_exit_count_3m,
                    COALESCE(s_prev.section_exit_count_6m, s_curr.section_exit_count_6m) AS section_exit_count_6m,
                    COALESCE(s_prev.section_exit_count_12m, s_curr.section_exit_count_12m) AS section_exit_count_12m,
                    COALESCE(s_prev.section_entry_rate_12m, s_curr.section_entry_rate_12m) AS section_entry_rate_12m,
                    COALESCE(s_prev.section_exit_rate_12m, s_curr.section_exit_rate_12m) AS section_exit_rate_12m,
                    COALESCE(s_prev.section_net_flow_12m, s_curr.section_net_flow_12m) AS section_net_flow_12m,
                    COALESCE(s_prev.section_turnover_rate_12m, s_curr.section_turnover_rate_12m) AS section_turnover_rate_12m,
                    COALESCE(s_prev.section_division_hhi, s_curr.section_division_hhi) AS section_division_hhi,
                    COALESCE(s_prev.section_division_top_share, s_curr.section_division_top_share) AS section_division_top_share,
                    COALESCE(s_prev.section_activity_category_hhi, s_curr.section_activity_category_hhi) AS section_activity_category_hhi,
                    COALESCE(s_prev.section_activity_category_top_share, s_curr.section_activity_category_top_share) AS section_activity_category_top_share
                FROM lagged_context l
                LEFT JOIN section_period_features s_prev
                    ON l.context_period = s_prev.period
                   AND l.section_key = s_prev.section_key
                LEFT JOIN section_period_features s_curr
                    ON l.period = s_curr.period
                   AND l.section_key = s_curr.section_key
                LEFT JOIN section_division_features d_prev
                    ON l.context_period = d_prev.period
                   AND l.section_key = d_prev.section_key
                   AND l.division_code_start = d_prev.division_code_start
                LEFT JOIN section_division_features d_curr
                    ON l.period = d_curr.period
                   AND l.section_key = d_curr.section_key
                   AND l.division_code_start = d_curr.division_code_start
                LEFT JOIN section_activity_category_features a_prev
                    ON l.context_period = a_prev.period
                   AND l.section_key = a_prev.section_key
                   AND l.activity_category_code_start = a_prev.activity_category_code_start
                LEFT JOIN section_activity_category_features a_curr
                    ON l.period = a_curr.period
                   AND l.section_key = a_curr.section_key
                   AND l.activity_category_code_start = a_curr.activity_category_code_start
            )
            SELECT
                c.*,
                CASE
                    WHEN c.section_local_count IS NULL OR c.section_local_count = 0 OR c.section_same_division_local_count IS NULL THEN NULL
                    ELSE CAST(c.section_same_division_local_count AS DOUBLE) / CAST(c.section_local_count AS DOUBLE)
                END AS section_same_division_share,
                CASE
                    WHEN c.section_local_count IS NULL OR c.section_local_count = 0 OR c.section_same_activity_category_local_count IS NULL THEN NULL
                    ELSE CAST(c.section_same_activity_category_local_count AS DOUBLE) / CAST(c.section_local_count AS DOUBLE)
                END AS section_same_activity_category_share
            FROM context_enriched c
            """
        )
        con.execute(
            f"""
            CREATE OR REPLACE TABLE change_candidates AS
            WITH ordered AS (
                SELECT
                    id_local,
                    period AS successor_period,
                    division_sig AS successor_division_code,
                    division_desc_sig AS successor_division_desc,
                    epigrafe_sig AS successor_epigrafe_code,
                    epigrafe_desc_sig AS successor_epigrafe_desc,
                    n_divisions AS successor_n_divisions,
                    n_epigrafes AS successor_n_epigrafes,
                    LAG(period) OVER (PARTITION BY id_local ORDER BY period) AS previous_period,
                    LAG(division_sig) OVER (PARTITION BY id_local ORDER BY period) AS previous_division_code,
                    LAG(division_desc_sig) OVER (PARTITION BY id_local ORDER BY period) AS previous_division_desc,
                    LAG(epigrafe_sig) OVER (PARTITION BY id_local ORDER BY period) AS previous_epigrafe_code,
                    LAG(epigrafe_desc_sig) OVER (PARTITION BY id_local ORDER BY period) AS previous_epigrafe_desc,
                    LAG(n_divisions) OVER (PARTITION BY id_local ORDER BY period) AS previous_n_divisions,
                    LAG(n_epigrafes) OVER (PARTITION BY id_local ORDER BY period) AS previous_n_epigrafes,
                    macro_category_sig AS successor_macro_category_code,
                    macro_category_desc_sig AS successor_macro_category_desc,
                    n_macro_categories AS successor_n_macro_categories,
                    LAG(macro_category_sig) OVER (PARTITION BY id_local ORDER BY period) AS previous_macro_category_code,
                    LAG(macro_category_desc_sig) OVER (PARTITION BY id_local ORDER BY period) AS previous_macro_category_desc,
                    LAG(n_macro_categories) OVER (PARTITION BY id_local ORDER BY period) AS previous_n_macro_categories,
                    (
                        (CAST(SUBSTR(period, 1, 4) AS INTEGER) * 12 + CAST(SUBSTR(period, 6, 2) AS INTEGER))
                        - (
                            CAST(SUBSTR(LAG(period) OVER (PARTITION BY id_local ORDER BY period), 1, 4) AS INTEGER) * 12
                            + CAST(SUBSTR(LAG(period) OVER (PARTITION BY id_local ORDER BY period), 6, 2) AS INTEGER)
                        )
                    ) AS month_gap
                FROM activity_periods
            )
            SELECT
                id_local,
                previous_period AS event_period,
                successor_period,
                '{"activity_category_change_single_single" if activity_closure_mode else "division_change_single_single"}' AS event_source,
                previous_division_code,
                previous_division_desc,
                successor_division_code,
                successor_division_desc,
                previous_epigrafe_code,
                previous_epigrafe_desc,
                successor_epigrafe_code,
                successor_epigrafe_desc,
                previous_n_divisions,
                successor_n_divisions,
                previous_n_epigrafes,
                successor_n_epigrafes,
                                previous_macro_category_code,
                                previous_macro_category_desc,
                                successor_macro_category_code,
                                successor_macro_category_desc,
                                previous_n_macro_categories,
                                successor_n_macro_categories,
                month_gap
            FROM ordered
            WHERE previous_period IS NOT NULL
              AND month_gap = 1
                            AND {'previous_n_macro_categories = 1' if activity_closure_mode else 'previous_n_divisions = 1'}
                            AND {'successor_n_macro_categories = 1' if activity_closure_mode else 'successor_n_divisions = 1'}
                            AND {'previous_macro_category_code <> successor_macro_category_code' if activity_closure_mode else 'previous_division_code <> successor_division_code'}
                        """
        )

        change_candidates = con.execute(
            "SELECT * FROM change_candidates ORDER BY event_period, successor_period, id_local"
        ).df()
        change_candidates.to_csv(resolved_change_candidates_csv, index=False)

        abt = con.execute(
            f"""
            WITH local_summary AS (
                SELECT
                    id_local,
                    MIN(period) AS first_seen_period,
                    MAX(period) AS last_seen_period,
                    COUNT(DISTINCT period) AS active_months,
                    ARG_MIN(section_key, period) AS section_key_start,
                    ARG_MIN(district_code, period) AS district_code_start,
                    ARG_MIN(barrio_code, period) AS barrio_code_start,
                    ARG_MIN(h3_cell, period) AS h3_cell_start,
                    ARG_MIN(lat_wgs84, period) AS lat_wgs84_start,
                    ARG_MIN(lon_wgs84, period) AS lon_wgs84_start,
                    ARG_MIN(coord_transform_status, period) AS coord_transform_status_start,
                    ARG_MIN(padron_lag_months, period) AS padron_lag_months_start,
                    ARG_MIN(total_population, period) AS total_population_start,
                    ARG_MIN(age_mean, period) AS age_mean_start,
                    ARG_MIN(renta_best_eur, period) AS renta_best_eur_start,
                    ARG_MIN(share_foreign, period) AS share_foreign_start,
                    ARG_MIN(share_male, period) AS share_male_start,
                    ARG_MIN(share_age_00_14, period) AS share_age_00_14_start,
                    ARG_MIN(share_age_15_29, period) AS share_age_15_29_start,
                    ARG_MIN(share_age_30_44, period) AS share_age_30_44_start,
                    ARG_MIN(share_age_45_64, period) AS share_age_45_64_start,
                    ARG_MIN(share_age_65_plus, period) AS share_age_65_plus_start,
                    ARG_MIN(population_density_km2, period) AS population_density_km2_start,
                    ARG_MIN(total_population_delta_12m, period) AS total_population_delta_12m_start,
                    ARG_MIN(share_foreign_delta_12m, period) AS share_foreign_delta_12m_start,
                    ARG_MIN(share_age_15_29_delta_12m, period) AS share_age_15_29_delta_12m_start,
                    ARG_MIN(population_density_km2_delta_12m, period) AS population_density_km2_delta_12m_start,
                    ARG_MIN(renta_best_eur_delta_12m, period) AS renta_best_eur_delta_12m_start,
                    ARG_MIN(n_divisions, period) AS n_divisions_start,
                    ARG_MIN(n_epigrafes, period) AS n_epigrafes_start,
                    ARG_MIN(n_macro_categories, period) AS n_activity_categories_start,
                    ARG_MIN(division_code_start, period) AS division_code_start,
                    ARG_MIN(division_desc_start, period) AS division_desc_start,
                    ARG_MIN(epigrafe_code_start, period) AS epigrafe_code_start,
                    ARG_MIN(epigrafe_desc_start, period) AS epigrafe_desc_start,
                    ARG_MIN(activity_category_code_start, period) AS activity_category_code_start,
                    ARG_MIN(activity_category_desc_start, period) AS activity_category_desc_start,
                    ARG_MIN(section_local_count, period) AS section_local_count_start,
                    ARG_MIN(section_unique_division_count, period) AS section_unique_division_count_start,
                    ARG_MIN(section_unique_activity_category_count, period) AS section_unique_activity_category_count_start,
                    ARG_MIN(section_single_division_share, period) AS section_single_division_share_start,
                    ARG_MIN(section_same_division_local_count, period) AS section_same_division_local_count_start,
                    ARG_MIN(section_same_division_share, period) AS section_same_division_share_start,
                    ARG_MIN(section_same_activity_category_local_count, period) AS section_same_activity_category_local_count_start,
                    ARG_MIN(section_same_activity_category_share, period) AS section_same_activity_category_share_start,
                    ARG_MIN(section_entry_count_3m, period) AS section_entry_count_3m_start,
                    ARG_MIN(section_entry_count_6m, period) AS section_entry_count_6m_start,
                    ARG_MIN(section_entry_count_12m, period) AS section_entry_count_12m_start,
                    ARG_MIN(section_exit_count_3m, period) AS section_exit_count_3m_start,
                    ARG_MIN(section_exit_count_6m, period) AS section_exit_count_6m_start,
                    ARG_MIN(section_exit_count_12m, period) AS section_exit_count_12m_start,
                    ARG_MIN(section_entry_rate_12m, period) AS section_entry_rate_12m_start,
                    ARG_MIN(section_exit_rate_12m, period) AS section_exit_rate_12m_start,
                    ARG_MIN(section_net_flow_12m, period) AS section_net_flow_12m_start,
                    ARG_MIN(section_turnover_rate_12m, period) AS section_turnover_rate_12m_start,
                    ARG_MIN(section_division_hhi, period) AS section_division_hhi_start,
                    ARG_MIN(section_division_top_share, period) AS section_division_top_share_start,
                    ARG_MIN(section_activity_category_hhi, period) AS section_activity_category_hhi_start,
                    ARG_MIN(section_activity_category_top_share, period) AS section_activity_category_top_share_start,
                    ARG_MIN(section_local_count_delta_12m, period) AS section_local_count_delta_12m_start,
                    ARG_MIN(geometry_available, period) AS geometry_available_start
                FROM local_feature_base
                GROUP BY id_local
            ), first_change AS (
                SELECT *
                FROM (
                    SELECT
                        *,
                        ROW_NUMBER() OVER (PARTITION BY id_local ORDER BY event_period, successor_period) AS rn
                    FROM change_candidates
                ) ranked
                WHERE rn = 1
            ), event_base AS (
                SELECT
                    l.*,
                    CASE WHEN l.last_seen_period < ? THEN l.last_seen_period ELSE NULL END AS disappearance_event_period,
                    c.event_period AS change_event_period,
                    c.successor_period AS change_successor_period,
                    c.event_source AS change_event_source,
                    c.previous_division_code,
                    c.previous_division_desc,
                    c.successor_division_code,
                    c.successor_division_desc,
                    c.previous_epigrafe_code,
                    c.previous_epigrafe_desc,
                    c.successor_epigrafe_code,
                    c.successor_epigrafe_desc,
                    c.previous_macro_category_code,
                    c.previous_macro_category_desc,
                    c.successor_macro_category_code,
                    c.successor_macro_category_desc
                FROM local_summary l
                LEFT JOIN first_change c USING (id_local)
            ), resolved AS (
                SELECT
                    *,
                    CASE
                        WHEN change_event_period IS NOT NULL
                             AND (disappearance_event_period IS NULL OR change_event_period <= disappearance_event_period)
                            THEN change_event_period
                        WHEN disappearance_event_period IS NOT NULL
                            THEN disappearance_event_period
                        ELSE NULL
                    END AS event_period,
                    CASE
                        WHEN change_event_period IS NOT NULL
                             AND (disappearance_event_period IS NULL OR change_event_period <= disappearance_event_period)
                            THEN '{UNIFIED_EVENT_SOURCE}'
                        WHEN disappearance_event_period IS NOT NULL
                            THEN '{UNIFIED_EVENT_SOURCE}'
                        ELSE 'censored'
                    END AS event_source
                    ,CASE
                        WHEN change_event_period IS NOT NULL
                             AND (disappearance_event_period IS NULL OR change_event_period <= disappearance_event_period)
                            THEN '{EVENT_SUBTYPE_ACTIVITY_CHANGE}'
                        WHEN disappearance_event_period IS NOT NULL
                            THEN '{EVENT_SUBTYPE_DISAPPEARANCE}'
                        ELSE '{EVENT_SUBTYPE_CENSORED}'
                    END AS event_subtype,
                    CASE
                        WHEN change_event_period IS NOT NULL
                             AND (disappearance_event_period IS NULL OR change_event_period <= disappearance_event_period)
                            THEN change_event_source
                        WHEN disappearance_event_period IS NOT NULL
                            THEN '{EVENT_SUBTYPE_DISAPPEARANCE}'
                        ELSE '{EVENT_SUBTYPE_CENSORED}'
                    END AS event_subtype_detail
                FROM event_base
            )
            SELECT
                id_local,
                first_seen_period,
                last_seen_period,
                active_months,
                event_period,
                event_source,
                event_subtype,
                                event_subtype_detail,
                CASE WHEN event_period IS NOT NULL THEN 1 ELSE 0 END AS event_observed,
                COALESCE(event_period, last_seen_period) AS target_end_period,
                ((CAST(SUBSTR(COALESCE(event_period, last_seen_period), 1, 4) AS INTEGER) - CAST(SUBSTR(first_seen_period, 1, 4) AS INTEGER)) * 12
                  + (CAST(SUBSTR(COALESCE(event_period, last_seen_period), 6, 2) AS INTEGER) - CAST(SUBSTR(first_seen_period, 6, 2) AS INTEGER)) + 1) AS duration_months,
                ? AS censor_reference_period,
                disappearance_event_period,
                change_event_period,
                change_successor_period,
                CASE WHEN change_event_period IS NOT NULL THEN 1 ELSE 0 END AS division_change_candidate_observed,
                previous_division_code,
                previous_division_desc,
                successor_division_code,
                successor_division_desc,
                previous_epigrafe_code,
                previous_epigrafe_desc,
                successor_epigrafe_code,
                successor_epigrafe_desc,
                section_key_start,
                district_code_start,
                barrio_code_start,
                h3_cell_start,
                lat_wgs84_start,
                lon_wgs84_start,
                coord_transform_status_start,
                padron_lag_months_start,
                total_population_start,
                age_mean_start,
                renta_best_eur_start,
                share_foreign_start,
                share_male_start,
                share_age_00_14_start,
                share_age_15_29_start,
                share_age_30_44_start,
                share_age_45_64_start,
                share_age_65_plus_start,
                population_density_km2_start,
                total_population_delta_12m_start,
                share_foreign_delta_12m_start,
                share_age_15_29_delta_12m_start,
                population_density_km2_delta_12m_start,
                renta_best_eur_delta_12m_start,
                n_divisions_start,
                n_epigrafes_start,
                n_activity_categories_start,
                division_code_start,
                division_desc_start,
                epigrafe_code_start,
                epigrafe_desc_start,
                activity_category_code_start,
                activity_category_desc_start,
                section_local_count_start,
                section_unique_division_count_start,
                section_unique_activity_category_count_start,
                section_single_division_share_start,
                section_same_division_local_count_start,
                section_same_division_share_start,
                section_same_activity_category_local_count_start,
                section_same_activity_category_share_start,
                section_entry_count_3m_start,
                section_entry_count_6m_start,
                section_entry_count_12m_start,
                section_exit_count_3m_start,
                section_exit_count_6m_start,
                section_exit_count_12m_start,
                section_entry_rate_12m_start,
                section_exit_rate_12m_start,
                section_net_flow_12m_start,
                section_turnover_rate_12m_start,
                section_division_hhi_start,
                section_division_top_share_start,
                section_activity_category_hhi_start,
                section_activity_category_top_share_start,
                section_local_count_delta_12m_start,
                geometry_available_start
            FROM resolved
            ORDER BY first_seen_period, id_local
            """,
            [max_period, max_period],
        ).df()
    finally:
        con.close()

    raw_manifest = load_raw_manifest()
    abt = attach_section_reference_fallbacks(abt)
    abt = attach_avisos_features(abt, raw_manifest=raw_manifest, section_panel_csv=resolved_section_panel)
    abt = attach_metro_features(abt)
    abt = attach_external_district_features(abt)

    abt.to_csv(resolved_output_csv, index=False)
    parquet_written = True
    try:
        abt.to_parquet(resolved_output_parquet, index=False)
    except ImportError:  # pragma: no cover
        parquet_written = False

    report = _render_abt_report(
        abt,
        max_period=max_period,
        max_year=max_year,
        max_month=max_month,
        normalization_audit=normalization_audit,
        change_candidates=change_candidates,
        target_mode=target_mode,
    )
    resolved_report_md.write_text(report, encoding="utf-8")

    return SurvivalAbtBuildResult(
        output_csv=resolved_output_csv,
        output_parquet=resolved_output_parquet,
        parquet_written=parquet_written,
        report_md=resolved_report_md,
        glossary_md=resolved_glossary_md,
        activity_taxonomy_csv=resolved_activity_taxonomy_csv,
        rows=len(abt),
        max_period=max_period,
        change_candidates_csv=resolved_change_candidates_csv,
        normalization_audit_csv=resolved_normalization_audit_csv,
    )


def _render_abt_report(
    abt: pd.DataFrame,
    *,
    max_period: str,
    max_year: int,
    max_month: int,
    normalization_audit: pd.DataFrame,
    change_candidates: pd.DataFrame,
    target_mode: str,
) -> str:
    if abt.empty:
        return "# ABT Survival\n\nNo se genero ninguna fila en la ABT.\n"

    event_rate = float(pd.to_numeric(abt["event_observed"], errors="coerce").fillna(0).mean())
    duration_median = float(pd.to_numeric(abt["duration_months"], errors="coerce").median())
    with_h3 = int(abt["h3_cell_start"].notna().sum())
    with_renta = int(pd.to_numeric(abt["renta_best_eur_start"], errors="coerce").notna().sum())
    with_metro = int(pd.to_numeric(abt.get("metro_distance_m_start"), errors="coerce").notna().sum())
    with_avisos = int(pd.to_numeric(abt.get("avisos_barrio_prev_year"), errors="coerce").fillna(0).gt(0).sum())
    event_source_counts = abt["event_source"].astype("string").value_counts(dropna=False).to_dict()
    event_subtype_counts = abt.get("event_subtype", abt["event_source"]).astype("string").value_counts(dropna=False).to_dict()

    division_audit = normalization_audit[normalization_audit["taxonomy"] == "division"].copy()
    epigrafe_audit = normalization_audit[normalization_audit["taxonomy"] == "epigrafe"].copy()

    def _sum_rows(frame: pd.DataFrame, mask: pd.Series) -> int:
        if frame.empty:
            return 0
        return int(pd.to_numeric(frame.loc[mask, "n"], errors="coerce").fillna(0).sum())

    division_raw_codes = int(division_audit["raw_code"].nunique(dropna=True))
    division_clean_codes = int(division_audit.loc[division_audit["code_valid"], "clean_code"].nunique(dropna=True))
    division_numeric_normalized = _sum_rows(division_audit, division_audit["mapping_reason"].eq("numeric_normalized"))
    division_description_remapped = _sum_rows(division_audit, division_audit["mapping_reason"].eq("description_remap"))
    division_placeholders = _sum_rows(division_audit, division_audit["is_placeholder"].fillna(False))
    division_invalid = _sum_rows(division_audit, division_audit["mapping_reason"].eq("invalid"))

    epigrafe_raw_codes = int(epigrafe_audit["raw_code"].nunique(dropna=True))
    epigrafe_clean_codes = int(epigrafe_audit.loc[epigrafe_audit["code_valid"], "clean_code"].nunique(dropna=True))

    top_changes = pd.DataFrame()
    if not change_candidates.empty:
        previous_desc_col = "previous_macro_category_desc" if target_mode in {"activity_survival", "cese_activity"} else "previous_division_desc"
        successor_desc_col = "successor_macro_category_desc" if target_mode in {"activity_survival", "cese_activity"} else "successor_division_desc"
        top_changes = (
            change_candidates.groupby([previous_desc_col, successor_desc_col], dropna=False)
            .size()
            .reset_index(name="transitions")
            .sort_values(["transitions", previous_desc_col, successor_desc_col], ascending=[False, True, True])
            .head(10)
        )

    activity_closure_mode = target_mode in {"activity_survival", "cese_activity"}
    change_label = "macrocategoria de actividad" if activity_closure_mode else "division"
    context_label = "section_same_activity_category_*_start (lagged t-1)" if activity_closure_mode else "section_same_division_*_start (lagged t-1)"
    title = "# ABT Cese de Actividad" if activity_closure_mode else "# ABT Survival"
    intro = (
        "ABT por local con target unico de `cese de actividad`: evento por desaparicion del `id_local` o por primer cambio robusto `single-single` entre macrocategorias de actividad. El subtipo del evento se conserva solo para auditoria."
        if activity_closure_mode
        else "ABT por local con cierre observado tanto por desaparicion del `id_local` como por primer cambio robusto `single-single` de division, tratado como cierre estructural."
    )

    lines: list[str] = []
    lines.append(title)
    lines.append("")
    lines.append(intro)
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Filas ABT: {len(abt):,}")
    lines.append(f"- Periodo de censura global: {max_period} ({max_year}-{max_month:02d})")
    lines.append(f"- Tasa de evento observada: {event_rate:.4f}")
    lines.append(f"- Mediana de duracion (meses): {duration_median:.1f}")
    lines.append(f"- Filas con H3 inicial: {with_h3:,}")
    lines.append(f"- Filas con renta inicial: {with_renta:,}")
    lines.append(f"- Filas con distancia a metro calculable: {with_metro:,}")
    lines.append(f"- Filas con avisos positivos en barrio/año previo: {with_avisos:,}")
    lines.append("")
    lines.append("## Desglose de eventos")
    lines.append("")
    if activity_closure_mode:
        lines.append(f"- Evento unificado `cese_de_actividad`: {int(event_source_counts.get(UNIFIED_EVENT_SOURCE, 0)):,}")
        lines.append(f"- Subtipo auditoria `cambio_actividad`: {int(event_subtype_counts.get(EVENT_SUBTYPE_ACTIVITY_CHANGE, 0)):,}")
        lines.append(f"- Subtipo auditoria `desaparicion`: {int(event_subtype_counts.get(EVENT_SUBTYPE_DISAPPEARANCE, 0)):,}")
    else:
        lines.append(f"- Cierre por cambio `single-single` de {change_label}: {int(event_source_counts.get('division_change_single_single', 0)):,}")
        lines.append(f"- Cierre por desaparicion del local: {int(event_source_counts.get('disappearance', 0)):,}")
    lines.append(f"- Censurados: {int(event_source_counts.get('censored', 0)):,}")
    lines.append(f"- Candidatos de cambio `single-single` auditados: {len(change_candidates):,}")
    lines.append("")
    lines.append("## Limpieza masiva de actividad")
    lines.append("")
    lines.append(f"- Codigos raw de division detectados: {division_raw_codes:,}")
    lines.append(f"- Codigos limpios y validos de division: {division_clean_codes:,}")
    lines.append(f"- Filas de division corregidas por formato numerico (`47.0 -> 47`): {division_numeric_normalized:,}")
    lines.append(f"- Filas de division remapeadas por descripcion canonica: {division_description_remapped:,}")
    lines.append(f"- Filas de division marcadas como placeholder/no codificadas: {division_placeholders:,}")
    lines.append(f"- Filas de division descartadas por codigo no valido: {division_invalid:,}")
    lines.append(f"- Codigos raw de epigrafe detectados: {epigrafe_raw_codes:,}")
    lines.append(f"- Codigos limpios y validos de epigrafe: {epigrafe_clean_codes:,}")
    lines.append("")
    lines.append("## Columnas clave")
    lines.append("")
    lines.append("- `first_seen_period`, `last_seen_period`, `target_end_period`, `duration_months`, `event_observed`")
    lines.append("- `event_source`, `event_subtype`, `event_subtype_detail`, `event_period`, `change_event_period`, `change_successor_period`")
    lines.append("- Auditoria de cambio: `previous_division_*`, `successor_division_*`, `previous_epigrafe_*`, `successor_epigrafe_*`, `previous_macro_category_*`, `successor_macro_category_*`")
    lines.append("- Features iniciales PiT: `renta_best_eur_start`, `share_*_start`, `total_population_start`, `age_mean_start`, `population_density_km2_start`")
    lines.append(f"- Contexto comercial: `n_divisions_start`, `n_epigrafes_start`, `n_activity_categories_start`, `activity_category_code_start`, `section_local_count_*_start (lagged t-1)`, `{context_label}`, `section_*_hhi_start`, `section_*_entry_count_*_start`, `section_*_exit_count_*_start`")
    lines.append("- Dinamica interanual: `*_delta_12m_start`")
    lines.append("- Externas: `avisos_*_prev_year`, `metro_distance_m_start`, `metro_access_count_500m_start`, `metro_access_count_1000m_start`")
    lines.append("- Geoespacial inicial: `h3_cell_start`, `lat_wgs84_start`, `lon_wgs84_start`")

    if not top_changes.empty:
        lines.append("")
        lines.append(f"## Cambios de {change_label} mas frecuentes tratados como cierre")
        lines.append("")
        for row in top_changes.itertuples(index=False):
            prev_desc = getattr(row, previous_desc_col) or "(sin descripcion)"
            next_desc = getattr(row, successor_desc_col) or "(sin descripcion)"
            lines.append(f"- {prev_desc} -> {next_desc}: {int(getattr(row, 'transitions')):,}")

    return "\n".join(lines) + "\n"


def _build_activity_lookup(
    summary: pd.DataFrame,
    *,
    taxonomy: str,
    min_numeric: int | None,
    max_numeric: int | None,
    placeholder_codes: frozenset[str],
) -> pd.DataFrame:
    if summary.empty:
        return pd.DataFrame(
            columns=[
                "taxonomy",
                "raw_code",
                "raw_desc",
                "desc_key",
                "n",
                "clean_code",
                "clean_desc",
                "code_valid",
                "is_placeholder",
                "mapping_reason",
            ]
        )

    frame = summary.copy()
    frame["taxonomy"] = taxonomy
    frame["raw_code"] = frame["raw_code"].map(_clean_raw_code).fillna("")
    frame["raw_desc"] = frame["raw_desc"].map(_clean_display_text).fillna("")
    frame["desc_key"] = frame["raw_desc"].map(normalize_activity_description)
    frame["n"] = pd.to_numeric(frame["n"], errors="coerce").fillna(0).astype(int)
    frame["numeric_code"] = frame["raw_code"].map(_parse_integer_like)
    frame["candidate_code"] = frame["numeric_code"].map(
        lambda value: _candidate_code_from_numeric(value, min_numeric=min_numeric, max_numeric=max_numeric)
    )

    valid_rows = frame[frame["candidate_code"].notna()].copy()
    canonical_desc_by_code: dict[str, str] = {}
    if not valid_rows.empty:
        canonical_desc_rows = (
            valid_rows.groupby(["candidate_code", "raw_desc"], dropna=False)["n"].sum().reset_index()
            .sort_values(["candidate_code", "n", "raw_desc"], ascending=[True, False, True])
            .drop_duplicates(subset=["candidate_code"], keep="first")
        )
        canonical_desc_by_code = {
            str(
                normalize_activity_code(
                    row.candidate_code,
                    min_numeric=min_numeric,
                    max_numeric=max_numeric,
                    placeholders=placeholder_codes,
                )
            ): row.raw_desc or str(row.candidate_code)
            for row in canonical_desc_rows.itertuples(index=False)
        }

    desc_to_code: dict[str, str] = {}
    if not valid_rows.empty:
        desc_code = (
            valid_rows.dropna(subset=["desc_key"])
            .groupby(["desc_key", "candidate_code"], dropna=False)["n"]
            .sum()
            .reset_index()
        )
        if not desc_code.empty:
            desc_unique = desc_code.groupby("desc_key")["candidate_code"].nunique().reset_index(name="n_codes")
            desc_code = desc_code.merge(desc_unique, on="desc_key", how="left")
            unique_desc_code = desc_code[desc_code["n_codes"] == 1].copy()
            desc_to_code = {
                str(row.desc_key): str(
                    normalize_activity_code(
                        row.candidate_code,
                        min_numeric=min_numeric,
                        max_numeric=max_numeric,
                        placeholders=placeholder_codes,
                    )
                )
                for row in unique_desc_code.itertuples(index=False)
                if pd.notna(row.desc_key) and pd.notna(row.candidate_code)
            }

    clean_code: list[str | None] = []
    clean_desc: list[str | None] = []
    code_valid: list[bool] = []
    is_placeholder: list[bool] = []
    mapping_reason: list[str] = []

    for row in frame.itertuples(index=False):
        raw_code = str(row.raw_code)
        raw_desc = str(row.raw_desc)
        desc_key = row.desc_key if pd.notna(row.desc_key) else None
        raw_numeric_code = _parse_integer_like(raw_code)
        candidate_code_raw = row.candidate_code
        candidate_code = None
        if not pd.isna(candidate_code_raw) and str(candidate_code_raw).strip().lower() != "nan":
            candidate_code = normalize_activity_code(
                candidate_code_raw,
                min_numeric=min_numeric,
                max_numeric=max_numeric,
                placeholders=placeholder_codes,
            )

        placeholder = (
            raw_code in placeholder_codes
            or (raw_numeric_code is not None and str(raw_numeric_code) in placeholder_codes)
            or desc_key in PLACEHOLDER_ACTIVITY_DESC_KEYS
        )
        if placeholder:
            reason = "placeholder"
            final_code = normalize_activity_code(raw_code, placeholders=placeholder_codes) or raw_code or None
        elif candidate_code is not None:
            reason = "exact_valid" if raw_code == str(candidate_code) else "numeric_normalized"
            final_code = str(candidate_code)
        elif desc_key is not None and desc_key in desc_to_code:
            reason = "description_remap"
            final_code = desc_to_code[desc_key]
        else:
            reason = "invalid"
            final_code = None

        canonical_final_code = None if final_code is None else normalize_activity_code(
            final_code,
            min_numeric=min_numeric,
            max_numeric=max_numeric,
            placeholders=placeholder_codes,
        )
        if canonical_final_code is not None and canonical_final_code not in placeholder_codes:
            final_code = canonical_final_code
        final_valid = (
            canonical_final_code is not None
            and canonical_final_code not in placeholder_codes
            and _parse_integer_like(canonical_final_code) is not None
        )
        final_desc = canonical_desc_by_code.get(str(final_code), raw_desc or final_code) if final_code is not None else raw_desc or None

        clean_code.append(final_code)
        clean_desc.append(final_desc)
        code_valid.append(bool(final_valid))
        is_placeholder.append(bool(placeholder))
        mapping_reason.append(reason)

    frame["clean_code"] = clean_code
    frame["clean_desc"] = clean_desc
    frame["code_valid"] = code_valid
    frame["is_placeholder"] = is_placeholder
    frame["mapping_reason"] = mapping_reason

    return frame[
        [
            "taxonomy",
            "raw_code",
            "raw_desc",
            "desc_key",
            "n",
            "clean_code",
            "clean_desc",
            "code_valid",
            "is_placeholder",
            "mapping_reason",
        ]
    ].copy()


def _collapse_activity_lookup_by_raw_code(lookup: pd.DataFrame) -> pd.DataFrame:
    if lookup.empty:
        return lookup.copy()

    frame = lookup.copy()
    frame["raw_code"] = frame["raw_code"].fillna("").astype("string")
    frame = frame[frame["raw_code"].str.strip().ne("")].copy()
    if frame.empty:
        return lookup.head(0).copy()

    frame["n"] = pd.to_numeric(frame.get("n"), errors="coerce").fillna(0)
    frame["code_valid_sort"] = frame["code_valid"].fillna(False).astype(int)
    frame = frame.sort_values(["raw_code", "code_valid_sort", "n", "mapping_reason"], ascending=[True, False, False, True])
    frame = frame.drop_duplicates(subset=["raw_code"], keep="first")
    return frame.drop(columns=["code_valid_sort"])


def _materialize_activity_period_tables(con) -> None:
    con.execute(
        """
        CREATE OR REPLACE TABLE activity_period_divisions AS
        WITH distinct_divisions AS (
            SELECT DISTINCT
                id_local,
                period,
                division_code,
                division_desc
            FROM activities_clean
            WHERE division_valid
        )
        SELECT
            id_local,
            period,
            string_agg(division_code, '|' ORDER BY division_code) AS division_sig,
            string_agg(division_desc, ' | ' ORDER BY division_desc) AS division_desc_sig,
            COUNT(*) AS n_divisions
        FROM distinct_divisions
        GROUP BY 1, 2
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE activity_period_epigrafes AS
        WITH distinct_epigrafes AS (
            SELECT DISTINCT
                id_local,
                period,
                epigrafe_code,
                epigrafe_desc
            FROM activities_clean
            WHERE epigrafe_valid
        )
        SELECT
            id_local,
            period,
            string_agg(epigrafe_code, '|' ORDER BY epigrafe_code) AS epigrafe_sig,
            string_agg(epigrafe_desc, ' | ' ORDER BY epigrafe_desc) AS epigrafe_desc_sig,
            COUNT(*) AS n_epigrafes
        FROM distinct_epigrafes
        GROUP BY 1, 2
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE activity_period_macro_categories AS
        WITH distinct_macro_categories AS (
            SELECT DISTINCT
                id_local,
                period,
                macro_category_code,
                macro_category_name
            FROM activities_clean
            WHERE epigrafe_valid AND macro_category_code IS NOT NULL
        )
        SELECT
            id_local,
            period,
            string_agg(macro_category_code, '|' ORDER BY macro_category_code) AS macro_category_sig,
            string_agg(macro_category_name, ' | ' ORDER BY macro_category_name) AS macro_category_desc_sig,
            COUNT(*) AS n_macro_categories
        FROM distinct_macro_categories
        GROUP BY 1, 2
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE activity_period_keys AS
        SELECT id_local, period FROM activity_period_divisions
        UNION
        SELECT id_local, period FROM activity_period_epigrafes
        UNION
        SELECT id_local, period FROM activity_period_macro_categories
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE activity_periods AS
        SELECT
            k.id_local,
            k.period,
            d.division_sig,
            d.division_desc_sig,
            COALESCE(d.n_divisions, 0) AS n_divisions,
            e.epigrafe_sig,
            e.epigrafe_desc_sig,
            COALESCE(e.n_epigrafes, 0) AS n_epigrafes,
            m.macro_category_sig,
            m.macro_category_desc_sig,
            COALESCE(m.n_macro_categories, 0) AS n_macro_categories
        FROM activity_period_keys k
        LEFT JOIN activity_period_divisions d
            ON k.id_local = d.id_local
           AND k.period = d.period
        LEFT JOIN activity_period_epigrafes e
            ON k.id_local = e.id_local
           AND k.period = e.period
        LEFT JOIN activity_period_macro_categories m
            ON k.id_local = m.id_local
           AND k.period = m.period
        """
    )


def _candidate_code_from_numeric(
    value: int | None,
    *,
    min_numeric: int | None,
    max_numeric: int | None,
) -> str | None:
    if value is None:
        return None
    if min_numeric is not None and value < min_numeric:
        return None
    if max_numeric is not None and value > max_numeric:
        return None
    return str(value)


def _clean_raw_code(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().upper()
    if not text:
        return None
    return text


def _clean_display_text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if "Ã" in text or "Â" in text:
        try:
            repaired = text.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
            if repaired:
                text = repaired
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    text = re.sub(r"(?<=[A-Za-zÁÉÍÓÚÜÑáéíóúüñ])0(?=[A-Za-zÁÉÍÓÚÜÑáéíóúüñ])", "O", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _parse_integer_like(value: object) -> int | None:
    raw = _clean_raw_code(value)
    if raw is None:
        return None
    if not re.fullmatch(r"[+-]?\d+(?:[\.,]0+)?", raw):
        return None
    normalized = raw.replace(",", ".")
    try:
        return int(float(normalized))
    except ValueError:
        return None
