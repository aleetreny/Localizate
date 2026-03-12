from __future__ import annotations

from bisect import bisect_right
from pathlib import Path

import pandas as pd

from .censo import build_censo_snapshot_manifest, load_raw_manifest
from .csv_utils import CsvReadMetadata, read_delimited_file
from .paths import DATA_DIR, DOCS_DIR, RAW_DATA_DIR
from .section_geography import load_section_metadata
from .section_keys import get_selected_source_row, extract_renta_section_key_series, normalize_section_key_series


PADRON_PURITY_START = "2015-01"

PADRON_BASE_COLUMNS: tuple[str, ...] = (
    "COD_DISTRITO",
    "DESC_DISTRITO",
    "COD_DIST_BARRIO",
    "DESC_BARRIO",
    "COD_BARRIO",
    "COD_DIST_SECCION",
    "COD_SECCION",
    "COD_EDAD_INT",
    "ESPANOLESHOMBRES",
    "ESPANOLESMUJERES",
    "EXTRANJEROSHOMBRES",
    "EXTRANJEROSMUJERES",
    "FX_CARGA",
    "FX_DATOS_INI",
    "FX_DATOS_FIN",
)


def normalize_padron_snapshot(
    frame: pd.DataFrame,
    *,
    period: str,
    source_relative_path: str,
    read_metadata: CsvReadMetadata,
) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [str(column).strip().upper() for column in normalized.columns]

    for column in PADRON_BASE_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = pd.NA

    normalized["district_code"] = _normalize_code_series(normalized["COD_DISTRITO"], width=2)
    normalized["district_name"] = normalized["DESC_DISTRITO"].astype("string").str.strip().replace({"": pd.NA})
    normalized["barrio_code"] = _normalize_code_series(normalized["COD_BARRIO"], width=3)
    normalized["barrio_name"] = normalized["DESC_BARRIO"].astype("string").str.strip().replace({"": pd.NA})
    normalized["section_key"] = normalize_section_key_series(normalized["COD_DIST_SECCION"])
    normalized["section_code"] = _normalize_code_series(normalized["COD_SECCION"], width=3)
    normalized["age_raw"] = normalized["COD_EDAD_INT"].astype("string").str.strip().replace({"": pd.NA})
    normalized["age_value"] = _parse_padron_age_series(normalized["COD_EDAD_INT"])
    normalized["age_is_topcoded"] = normalized["age_raw"].fillna("").str.contains(r"100", regex=True)

    for source_column, target_column in {
        "ESPANOLESHOMBRES": "spanish_male",
        "ESPANOLESMUJERES": "spanish_female",
        "EXTRANJEROSHOMBRES": "foreign_male",
        "EXTRANJEROSMUJERES": "foreign_female",
    }.items():
        normalized[target_column] = pd.to_numeric(normalized[source_column], errors="coerce").fillna(0)

    normalized["spanish_total"] = normalized["spanish_male"] + normalized["spanish_female"]
    normalized["foreign_total"] = normalized["foreign_male"] + normalized["foreign_female"]
    normalized["male_total"] = normalized["spanish_male"] + normalized["foreign_male"]
    normalized["female_total"] = normalized["spanish_female"] + normalized["foreign_female"]
    normalized["total_population"] = normalized["spanish_total"] + normalized["foreign_total"]
    normalized["age_known_population"] = normalized["total_population"].where(normalized["age_value"].notna(), 0)
    normalized["age_weighted_population"] = (
        normalized["age_value"].astype("Float64").fillna(0) * normalized["age_known_population"]
    )

    age_value = normalized["age_value"].astype("Float64")
    normalized["age_00_14_total"] = normalized["total_population"].where(age_value.between(0, 14), 0)
    normalized["age_15_29_total"] = normalized["total_population"].where(age_value.between(15, 29), 0)
    normalized["age_30_44_total"] = normalized["total_population"].where(age_value.between(30, 44), 0)
    normalized["age_45_64_total"] = normalized["total_population"].where(age_value.between(45, 64), 0)
    normalized["age_65_plus_total"] = normalized["total_population"].where(age_value.ge(65), 0)

    normalized["padron_period"] = period
    normalized["padron_year"] = int(period[:4])
    normalized["padron_month"] = int(period[5:7])
    normalized["padron_date"] = f"{period}-01"
    normalized["padron_source_relative_path"] = source_relative_path
    normalized["padron_raw_encoding"] = read_metadata.encoding
    normalized["padron_raw_delimiter"] = read_metadata.delimiter
    normalized["padron_raw_reader_mode"] = read_metadata.reader_mode
    normalized["padron_fx_carga"] = pd.to_datetime(normalized["FX_CARGA"], errors="coerce")
    normalized["padron_fx_datos_ini"] = pd.to_datetime(normalized["FX_DATOS_INI"], errors="coerce")
    normalized["padron_fx_datos_fin"] = pd.to_datetime(normalized["FX_DATOS_FIN"], errors="coerce")

    ordered_columns = [
        "padron_period",
        "padron_year",
        "padron_month",
        "padron_date",
        "section_key",
        "district_code",
        "district_name",
        "barrio_code",
        "barrio_name",
        "section_code",
        "age_raw",
        "age_value",
        "age_is_topcoded",
        "spanish_male",
        "spanish_female",
        "foreign_male",
        "foreign_female",
        "spanish_total",
        "foreign_total",
        "male_total",
        "female_total",
        "total_population",
        "age_known_population",
        "age_weighted_population",
        "age_00_14_total",
        "age_15_29_total",
        "age_30_44_total",
        "age_45_64_total",
        "age_65_plus_total",
        "padron_fx_carga",
        "padron_fx_datos_ini",
        "padron_fx_datos_fin",
        "padron_source_relative_path",
        "padron_raw_encoding",
        "padron_raw_delimiter",
        "padron_raw_reader_mode",
    ]
    return normalized[ordered_columns]


def load_and_normalize_padron_snapshot(
    *,
    period: str,
    raw_manifest: pd.DataFrame | None = None,
    raw_root: Path = RAW_DATA_DIR,
) -> tuple[pd.DataFrame, CsvReadMetadata]:
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    row = get_selected_source_row(manifest, "padron", period=period)
    frame, read_metadata = read_delimited_file(raw_root / row["selected_relative_path"])
    normalized = normalize_padron_snapshot(
        frame,
        period=period,
        source_relative_path=str(row["selected_relative_path"]),
        read_metadata=read_metadata,
    )
    return normalized, read_metadata


def aggregate_padron_section_snapshot(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        frame.groupby(["padron_period", "section_key"], dropna=False, sort=True)
        .agg(
            padron_year=("padron_year", "first"),
            padron_month=("padron_month", "first"),
            padron_date=("padron_date", "first"),
            district_code=("district_code", "first"),
            district_name=("district_name", "first"),
            barrio_code=("barrio_code", "first"),
            barrio_name=("barrio_name", "first"),
            section_code=("section_code", "first"),
            total_population=("total_population", "sum"),
            spanish_total=("spanish_total", "sum"),
            foreign_total=("foreign_total", "sum"),
            male_total=("male_total", "sum"),
            female_total=("female_total", "sum"),
            spanish_male=("spanish_male", "sum"),
            spanish_female=("spanish_female", "sum"),
            foreign_male=("foreign_male", "sum"),
            foreign_female=("foreign_female", "sum"),
            age_known_population=("age_known_population", "sum"),
            age_weighted_population=("age_weighted_population", "sum"),
            age_00_14_total=("age_00_14_total", "sum"),
            age_15_29_total=("age_15_29_total", "sum"),
            age_30_44_total=("age_30_44_total", "sum"),
            age_45_64_total=("age_45_64_total", "sum"),
            age_65_plus_total=("age_65_plus_total", "sum"),
            padron_rows=("section_key", "size"),
            topcoded_age_rows=("age_is_topcoded", "sum"),
            padron_source_relative_path=("padron_source_relative_path", "first"),
            padron_raw_encoding=("padron_raw_encoding", "first"),
            padron_raw_delimiter=("padron_raw_delimiter", "first"),
            padron_raw_reader_mode=("padron_raw_reader_mode", "first"),
            padron_fx_carga=("padron_fx_carga", "first"),
            padron_fx_datos_ini=("padron_fx_datos_ini", "first"),
            padron_fx_datos_fin=("padron_fx_datos_fin", "first"),
        )
        .reset_index()
    )

    grouped["age_mean"] = grouped["age_weighted_population"] / grouped["age_known_population"].replace({0: pd.NA})
    for numerator, suffix in {
        "foreign_total": "foreign",
        "male_total": "male",
        "female_total": "female",
        "age_00_14_total": "age_00_14",
        "age_15_29_total": "age_15_29",
        "age_30_44_total": "age_30_44",
        "age_45_64_total": "age_45_64",
        "age_65_plus_total": "age_65_plus",
    }.items():
        grouped[f"share_{suffix}"] = grouped[numerator] / grouped["total_population"].replace({0: pd.NA})

    ordered_columns = [
        "padron_period",
        "padron_year",
        "padron_month",
        "padron_date",
        "section_key",
        "district_code",
        "district_name",
        "barrio_code",
        "barrio_name",
        "section_code",
        "total_population",
        "spanish_total",
        "foreign_total",
        "male_total",
        "female_total",
        "spanish_male",
        "spanish_female",
        "foreign_male",
        "foreign_female",
        "age_mean",
        "age_00_14_total",
        "age_15_29_total",
        "age_30_44_total",
        "age_45_64_total",
        "age_65_plus_total",
        "share_foreign",
        "share_male",
        "share_female",
        "share_age_00_14",
        "share_age_15_29",
        "share_age_30_44",
        "share_age_45_64",
        "share_age_65_plus",
        "padron_rows",
        "topcoded_age_rows",
        "age_known_population",
        "age_weighted_population",
        "padron_source_relative_path",
        "padron_raw_encoding",
        "padron_raw_delimiter",
        "padron_raw_reader_mode",
        "padron_fx_carga",
        "padron_fx_datos_ini",
        "padron_fx_datos_fin",
    ]
    return grouped[ordered_columns].sort_values(["padron_period", "section_key"]).reset_index(drop=True)


def build_padron_section_panel(
    raw_manifest: pd.DataFrame | None = None,
    *,
    periods: list[str] | None = None,
    start_period: str = PADRON_PURITY_START,
) -> pd.DataFrame:
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    selected = manifest[(manifest["source_name"] == "padron") & (manifest["status"] == "selected")].copy()
    selected = selected[selected["period"] >= start_period].sort_values("period")
    if periods is not None:
        selected = selected[selected["period"].isin(periods)]

    frames: list[pd.DataFrame] = []
    for _, row in selected.iterrows():
        normalized, _ = load_and_normalize_padron_snapshot(period=row["period"], raw_manifest=manifest)
        frames.append(aggregate_padron_section_snapshot(normalized))

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True).sort_values(["padron_period", "section_key"]).reset_index(drop=True)


def load_and_normalize_renta_madrid(
    raw_manifest: pd.DataFrame | None = None,
    *,
    raw_root: Path = RAW_DATA_DIR,
) -> pd.DataFrame:
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    row = get_selected_source_row(manifest, "renta_media")
    frame, _ = read_delimited_file(raw_root / row["selected_relative_path"])

    normalized = frame.copy()
    normalized.columns = [str(column).strip() for column in normalized.columns]
    normalized["municipality_code"] = _extract_code_series(normalized["Municipios"], width=5)
    normalized = normalized[normalized["municipality_code"] == "28079"].copy()
    normalized["district_code"] = normalized["Distritos"].astype("string").str.extract(r"28079(\d{2})", expand=False)
    normalized["section_key"] = extract_renta_section_key_series(normalized["Secciones"])
    normalized["reference_year"] = pd.to_numeric(normalized["Periodo"], errors="coerce").astype("Int64")
    normalized["renta_value_eur"] = _parse_renta_amount_series(normalized["Total"])
    normalized["granularity"] = "city"
    normalized.loc[normalized["Distritos"].notna() & normalized["Secciones"].isna(), "granularity"] = "district"
    normalized.loc[normalized["Secciones"].notna(), "granularity"] = "section"
    normalized["district_label"] = normalized["Distritos"].astype("string").str.strip().replace({"": pd.NA})
    normalized["section_label"] = normalized["Secciones"].astype("string").str.strip().replace({"": pd.NA})
    return normalized[
        [
            "reference_year",
            "granularity",
            "municipality_code",
            "district_code",
            "section_key",
            "district_label",
            "section_label",
            "renta_value_eur",
        ]
    ].sort_values(["reference_year", "granularity", "district_code", "section_key"]).reset_index(drop=True)


def attach_renta_features(
    panel: pd.DataFrame,
    renta_madrid: pd.DataFrame,
    *,
    target_year_column: str = "target_year",
) -> pd.DataFrame:
    enriched = panel.copy()
    available_years = sorted(int(value) for value in renta_madrid["reference_year"].dropna().unique())
    year_lookup = {year: _resolve_reference_year(year, available_years) for year in enriched[target_year_column].dropna().unique()}
    enriched["renta_reference_year"] = enriched[target_year_column].map(year_lookup).astype("Int64")
    enriched["renta_lag_years"] = (
        enriched[target_year_column].astype("Int64") - enriched["renta_reference_year"]
    ).astype("Int64")

    city = (
        renta_madrid[renta_madrid["granularity"] == "city"][["reference_year", "renta_value_eur"]]
        .drop_duplicates()
        .rename(columns={"reference_year": "renta_reference_year", "renta_value_eur": "renta_city_eur"})
    )
    district = (
        renta_madrid[renta_madrid["granularity"] == "district"][["reference_year", "district_code", "renta_value_eur"]]
        .drop_duplicates()
        .rename(columns={"reference_year": "renta_reference_year", "renta_value_eur": "renta_district_eur"})
    )
    section = (
        renta_madrid[renta_madrid["granularity"] == "section"][["reference_year", "section_key", "renta_value_eur"]]
        .drop_duplicates()
        .rename(columns={"reference_year": "renta_reference_year", "renta_value_eur": "renta_section_eur"})
    )

    enriched = enriched.merge(city, on="renta_reference_year", how="left")
    enriched = enriched.merge(district, on=["renta_reference_year", "district_code"], how="left")
    enriched = enriched.merge(section, on=["renta_reference_year", "section_key"], how="left")

    enriched["renta_best_eur"] = (
        enriched["renta_section_eur"].fillna(enriched["renta_district_eur"]).fillna(enriched["renta_city_eur"])
    )
    enriched["renta_granularity_used"] = "missing"
    enriched.loc[enriched["renta_city_eur"].notna(), "renta_granularity_used"] = "city"
    enriched.loc[enriched["renta_district_eur"].notna(), "renta_granularity_used"] = "district"
    enriched.loc[enriched["renta_section_eur"].notna(), "renta_granularity_used"] = "section"
    return enriched


def attach_section_geography_features(panel: pd.DataFrame, section_metadata: pd.DataFrame | None = None) -> pd.DataFrame:
    enriched = panel.copy()
    metadata = section_metadata if section_metadata is not None else load_section_metadata()
    geography = (
        metadata[["section_key", "section_area_m2", "geometry_available"]]
        .groupby("section_key", dropna=False, sort=True)
        .agg(
            section_area_m2=("section_area_m2", "sum"),
            geometry_available=("geometry_available", "max"),
        )
        .reset_index()
    )
    enriched = enriched.merge(geography, on="section_key", how="left")
    enriched["geometry_available"] = enriched["geometry_available"].fillna(False)
    enriched["population_density_km2"] = (
        enriched["total_population"] / (enriched["section_area_m2"] / 1_000_000)
    ).where(enriched["section_area_m2"].fillna(0) > 0)
    return enriched


def build_section_socioeconomic_panel(
    raw_manifest: pd.DataFrame | None = None,
    *,
    target_periods: list[str] | None = None,
    start_period: str = PADRON_PURITY_START,
    padron_panel: pd.DataFrame | None = None,
    renta_madrid: pd.DataFrame | None = None,
    section_metadata: pd.DataFrame | None = None,
) -> pd.DataFrame:
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    snapshot_manifest = build_censo_snapshot_manifest(manifest)
    censo_periods = snapshot_manifest[snapshot_manifest["period"] >= start_period]["period"].tolist()
    resolved_target_periods = target_periods or censo_periods

    resolved_padron_panel = padron_panel if padron_panel is not None else build_padron_section_panel(manifest, start_period=start_period)
    if resolved_padron_panel.empty:
        return resolved_padron_panel

    padron_periods = sorted(resolved_padron_panel["padron_period"].dropna().unique().tolist())
    target_frame = pd.DataFrame({"target_period": resolved_target_periods})
    target_frame["target_year"] = target_frame["target_period"].str[:4].astype(int)
    target_frame["target_month"] = target_frame["target_period"].str[5:7].astype(int)
    target_frame["target_date"] = target_frame["target_period"] + "-01"
    target_frame["padron_reference_period"] = target_frame["target_period"].map(
        lambda value: _resolve_reference_period(value, padron_periods)
    )
    target_frame["padron_lag_months"] = target_frame.apply(
        lambda row: _month_difference(row["target_period"], row["padron_reference_period"]),
        axis=1,
    )

    panel = target_frame.merge(
        resolved_padron_panel,
        left_on="padron_reference_period",
        right_on="padron_period",
        how="left",
    )
    panel["padron_reference_year"] = panel["padron_year"]
    panel["padron_reference_month"] = panel["padron_month"]
    resolved_renta_madrid = renta_madrid if renta_madrid is not None else load_and_normalize_renta_madrid(manifest)
    resolved_section_metadata = section_metadata if section_metadata is not None else load_section_metadata(manifest)
    panel = attach_renta_features(panel, resolved_renta_madrid, target_year_column="target_year")
    panel = attach_section_geography_features(panel, resolved_section_metadata)
    return panel.sort_values(["target_period", "section_key"]).reset_index(drop=True)


def render_section_socioeconomic_markdown(
    padron_panel: pd.DataFrame,
    section_panel: pd.DataFrame,
) -> str:
    padron_periods = padron_panel["padron_period"].nunique() if not padron_panel.empty else 0
    target_periods = section_panel["target_period"].nunique() if not section_panel.empty else 0
    lag_distribution = (
        section_panel[["target_period", "padron_lag_months"]]
        .drop_duplicates()
        .sort_values("target_period")
        ["padron_lag_months"]
        .value_counts()
        .sort_index()
    )
    renta_distribution = section_panel["renta_granularity_used"].value_counts(dropna=False).to_dict()
    geometry_coverage = float(section_panel["geometry_available"].mean()) if not section_panel.empty else 0.0

    lines: list[str] = []
    lines.append("# Section Socioeconomic Panel")
    lines.append("")
    lines.append("Panel canonico por seccion para enriquecer el censo con demografia, renta y metadata geografica.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Periodos mensuales agregados de padron: {padron_periods}")
    lines.append(f"- Periodos objetivo alineados al censo: {target_periods}")
    lines.append(f"- Filas panel padron: {len(padron_panel):,}")
    lines.append(f"- Filas panel seccion-alineado: {len(section_panel):,}")
    lines.append(f"- Cobertura geometrica del panel: {geometry_coverage:.2%}")
    lines.append("")
    lines.append("## Lag padron")
    lines.append("")
    for lag_value, count in lag_distribution.items():
        lines.append(f"- {int(lag_value)} meses de lag: {int(count)} periodos objetivo")
    lines.append("")
    lines.append("## Renta")
    lines.append("")
    for granularity, count in renta_distribution.items():
        lines.append(f"- Fallback `{granularity}`: {int(count):,} filas")
    lines.append("")
    return "\n".join(lines) + "\n"


def write_section_socioeconomic_outputs(
    padron_panel: pd.DataFrame,
    section_panel: pd.DataFrame,
    *,
    padron_csv_path: Path | None = None,
    section_csv_path: Path | None = None,
    report_md_path: Path | None = None,
) -> None:
    resolved_padron_csv = padron_csv_path or (DATA_DIR / "processed" / "padron_section_panel.csv")
    resolved_section_csv = section_csv_path or (DATA_DIR / "processed" / "section_socioeconomic_panel.csv")
    resolved_report_md = report_md_path or (DOCS_DIR / "section_socioeconomic_panel.md")

    resolved_padron_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_section_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_md.parent.mkdir(parents=True, exist_ok=True)

    padron_panel.to_csv(resolved_padron_csv, index=False)
    section_panel.to_csv(resolved_section_csv, index=False)
    resolved_report_md.write_text(
        render_section_socioeconomic_markdown(padron_panel, section_panel),
        encoding="utf-8",
    )


def write_optional_parquet(frame: pd.DataFrame, path: Path) -> bool:
    try:
        frame.to_parquet(path, index=False)
    except (ImportError, ModuleNotFoundError, ValueError):
        return False
    return True


def _normalize_code_series(series: pd.Series, *, width: int) -> pd.Series:
    return _extract_code_series(series, width=width)


def _extract_code_series(series: pd.Series, *, width: int | None = None) -> pd.Series:
    extracted = (
        series.astype("string")
        .str.extract(r"(\d+)", expand=False)
        .astype("string")
        .str.lstrip("0")
        .replace({"": pd.NA})
    )
    if width is not None:
        return extracted.str.zfill(width)
    return extracted


def _parse_padron_age_series(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.strip().str.extract(r"(\d{1,3})", expand=False)
    return pd.to_numeric(cleaned, errors="coerce").astype("Int64")


def _parse_renta_amount_series(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA})
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _resolve_reference_period(target_period: str, available_periods: list[str]) -> str | pd.NA:
    index = bisect_right(available_periods, target_period) - 1
    if index < 0:
        return pd.NA
    return available_periods[index]


def _resolve_reference_year(target_year: int, available_years: list[int]) -> int | pd.NA:
    index = bisect_right(available_years, int(target_year)) - 1
    if index < 0:
        return pd.NA
    return available_years[index]


def _month_difference(left_period: str, right_period: str | pd.NA) -> int | pd.NA:
    if pd.isna(right_period):
        return pd.NA
    left_year, left_month = [int(part) for part in left_period.split("-")]
    right_year, right_month = [int(part) for part in str(right_period).split("-")]
    return (left_year - right_year) * 12 + (left_month - right_month)
