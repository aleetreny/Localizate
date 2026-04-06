from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from .activity_taxonomy import macro_category_feature_names
from .censo import load_raw_manifest
from .csv_utils import read_delimited_file
from .paths import DATA_DIR, PROJECT_ROOT, RAW_DATA_DIR


EARTH_RADIUS_M = 6_371_000.0
DEFAULT_METRO_DISTANCE_BANDS_M = (500.0, 1000.0)
MADRID_LAT_RANGE = (40.0, 41.0)
MADRID_LON_RANGE = (-4.5, -3.0)


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    status: str
    category: str
    source: str
    description: str


MODEL_FEATURE_SPECS: tuple[FeatureSpec, ...] = (
    FeatureSpec("renta_effective_eur", "existing", "socioeconomic", "renta + policy fill", "Renta usable en entrenamiento tras fallback sección→distrito→ciudad."),
    FeatureSpec("renta_carry_forward_years", "existing", "socioeconomic", "renta + policy fill", "Años de carry-forward aplicados a la renta por falta de dato reciente."),
    FeatureSpec("share_foreign_start", "existing", "socioeconomic", "section_socioeconomic_panel", "Peso de población extranjera en la sección al alta del local."),
    FeatureSpec("share_age_00_14_start", "new", "socioeconomic", "section_socioeconomic_panel", "Peso de población infantil en la sección al alta."),
    FeatureSpec("share_age_15_29_start", "existing", "socioeconomic", "section_socioeconomic_panel", "Peso de población joven en la sección al alta."),
    FeatureSpec("share_age_30_44_start", "new", "socioeconomic", "section_socioeconomic_panel", "Peso de población adulta joven en la sección al alta."),
    FeatureSpec("share_age_45_64_start", "existing", "socioeconomic", "section_socioeconomic_panel", "Peso de población madura en la sección al alta."),
    FeatureSpec("share_age_65_plus_start", "existing", "socioeconomic", "section_socioeconomic_panel", "Peso de población sénior en la sección al alta."),
    FeatureSpec("share_male_start", "new", "socioeconomic", "section_socioeconomic_panel", "Peso masculino en la sección al alta."),
    FeatureSpec("age_mean_start", "new", "socioeconomic", "section_socioeconomic_panel", "Edad media estimada de la sección al alta."),
    FeatureSpec("total_population_start", "new", "socioeconomic", "section_socioeconomic_panel", "Población total de la sección al alta (log-transform en modelado)."),
    FeatureSpec("population_density_km2_start", "existing", "socioeconomic", "section_socioeconomic_panel", "Densidad de población por km² en la sección al alta."),
    FeatureSpec("padron_lag_months_start", "existing", "data_quality", "section_socioeconomic_panel", "Meses de retraso del padrón usado para el join PiT."),
    FeatureSpec("geometry_available_start", "existing", "data_quality", "section_geography", "Flag de disponibilidad geométrica para la sección."),
    FeatureSpec("missing_h3", "existing", "data_quality", "censo_geospatial", "Flag de H3 ausente en el punto inicial del local."),
    FeatureSpec("n_divisions_start", "new", "activity", "actividades", "Número de divisiones activas del local en su primer mes observado."),
    FeatureSpec("n_epigrafes_start", "new", "activity", "actividades", "Número de epígrafes activos del local en su primer mes observado."),
    FeatureSpec("n_activity_categories_start", "new", "activity", "actividades", "Número de macrocategorías activas del local en su primer mes observado."),
    FeatureSpec("section_local_count_start", "new", "competition", "censo locales historico", "Stock de locales observados en la sección en el mes previo al alta (`t-1`)."),
    FeatureSpec("section_unique_division_count_start", "new", "competition", "censo actividades historico", "Diversidad de divisiones presentes en la sección en `t-1`."),
    FeatureSpec("section_unique_activity_category_count_start", "new", "competition", "censo actividades historico", "Diversidad de macrocategorías presentes en la sección en `t-1`."),
    FeatureSpec("section_single_division_share_start", "new", "competition", "censo actividades historico", "Peso de locales single-division en la sección en `t-1`."),
    FeatureSpec("section_same_division_local_count_start", "new", "competition", "censo actividades historico", "Número de competidores single-division de la misma división en la sección en `t-1`."),
    FeatureSpec("section_same_division_share_start", "new", "competition", "censo actividades historico", "Cuota de competidores de la misma división dentro del stock de la sección en `t-1`."),
    FeatureSpec("section_same_activity_category_local_count_start", "new", "competition", "censo actividades historico", "Número de competidores de la misma macrocategoría en la sección en `t-1`."),
    FeatureSpec("section_same_activity_category_share_start", "new", "competition", "censo actividades historico", "Cuota de competidores de la misma macrocategoría dentro del stock de la sección en `t-1`."),
    FeatureSpec("section_entry_count_3m_start", "new", "competition_flow", "censo locales historico", "Entradas de locales observadas en la sección durante los 3 meses previos a `t-1` (log-transform en modelado)."),
    FeatureSpec("section_entry_count_6m_start", "new", "competition_flow", "censo locales historico", "Entradas de locales observadas en la sección durante los 6 meses previos a `t-1` (log-transform en modelado)."),
    FeatureSpec("section_entry_count_12m_start", "new", "competition_flow", "censo locales historico", "Entradas de locales observadas en la sección durante los 12 meses previos a `t-1` (log-transform en modelado)."),
    FeatureSpec("section_exit_count_3m_start", "new", "competition_flow", "censo locales historico", "Salidas observadas en la sección durante los 3 meses previos a `t-1` (log-transform en modelado)."),
    FeatureSpec("section_exit_count_6m_start", "new", "competition_flow", "censo locales historico", "Salidas observadas en la sección durante los 6 meses previos a `t-1` (log-transform en modelado)."),
    FeatureSpec("section_exit_count_12m_start", "new", "competition_flow", "censo locales historico", "Salidas observadas en la sección durante los 12 meses previos a `t-1` (log-transform en modelado)."),
    FeatureSpec("section_entry_rate_12m_start", "new", "competition_flow", "censo locales historico", "Tasa de entradas sobre el stock de la sección en la ventana de 12 meses previa a `t-1`."),
    FeatureSpec("section_exit_rate_12m_start", "new", "competition_flow", "censo locales historico", "Tasa de salidas sobre el stock de la sección en la ventana de 12 meses previa a `t-1`."),
    FeatureSpec("section_net_flow_12m_start", "new", "competition_flow", "censo locales historico", "Balance neto de entradas menos salidas en la ventana de 12 meses previa a `t-1`."),
    FeatureSpec("section_turnover_rate_12m_start", "new", "competition_flow", "censo locales historico", "Rotación total (entradas + salidas) sobre stock en la ventana de 12 meses previa a `t-1`."),
    FeatureSpec("section_division_hhi_start", "new", "competition_concentration", "censo actividades historico", "Concentración HHI por divisiones dentro de la sección en `t-1`."),
    FeatureSpec("section_division_top_share_start", "new", "competition_concentration", "censo actividades historico", "Cuota de la división dominante dentro de la sección en `t-1`."),
    FeatureSpec("section_activity_category_hhi_start", "new", "competition_concentration", "censo actividades historico", "Concentración HHI por macrocategorías dentro de la sección en `t-1`."),
    FeatureSpec("section_activity_category_top_share_start", "new", "competition_concentration", "censo actividades historico", "Cuota de la macrocategoría dominante dentro de la sección en `t-1`."),
    FeatureSpec("section_local_count_delta_12m_start", "new", "zone_dynamics", "censo locales historico", "Cambio de stock de locales en la sección frente a 12 meses antes."),
    FeatureSpec("total_population_delta_12m_start", "new", "zone_dynamics", "section_socioeconomic_panel", "Cambio interanual de población total en la sección."),
    FeatureSpec("share_foreign_delta_12m_start", "new", "zone_dynamics", "section_socioeconomic_panel", "Cambio interanual del peso de población extranjera."),
    FeatureSpec("share_age_15_29_delta_12m_start", "new", "zone_dynamics", "section_socioeconomic_panel", "Cambio interanual del peso de población de 15-29 años."),
    FeatureSpec("population_density_km2_delta_12m_start", "new", "zone_dynamics", "section_socioeconomic_panel", "Cambio interanual de densidad poblacional."),
    FeatureSpec("renta_best_eur_delta_12m_start", "new", "zone_dynamics", "section_socioeconomic_panel", "Cambio interanual de renta disponible en la sección."),
    FeatureSpec("avisos_district_per_1000_prev_year", "new", "avisos", "DB/avisos + section_socioeconomic_panel", "Avisos recibidos del distrito en el año anterior por cada 1.000 habitantes."),
    FeatureSpec("avisos_barrio_per_1000_prev_year", "new", "avisos", "DB/avisos + section_socioeconomic_panel", "Avisos recibidos del barrio en el año anterior por cada 1.000 habitantes."),
    FeatureSpec("avisos_barrio_share_of_district_prev_year", "new", "avisos", "DB/avisos", "Peso del barrio dentro del total de avisos del distrito en el año anterior."),
    FeatureSpec("metro_distance_m_start", "new", "metro", "DB/Metro", "Distancia al acceso de metro más cercano desde la localización inicial (log-transform en modelado)."),
    FeatureSpec("metro_access_count_500m_start", "new", "metro", "DB/Metro", "Número de accesos de metro a 500 m o menos."),
    FeatureSpec("metro_access_count_1000m_start", "new", "metro", "DB/Metro", "Número de accesos de metro a 1 km o menos."),
    FeatureSpec("missing_metro_distance_start", "new", "data_quality", "DB/Metro + censo_geospatial", "Flag de imposibilidad de calcular cercanía a metro por falta de coordenadas iniciales."),
    FeatureSpec("cohort_2015_2017", "new", "temporal", "first_seen_period", "Flag de cohorte de entrada 2015-2017."),
    FeatureSpec("cohort_2018_2019", "new", "temporal", "first_seen_period", "Flag de cohorte de entrada 2018-2019."),
    FeatureSpec("cohort_2020_2021", "new", "temporal", "first_seen_period", "Flag de cohorte de entrada 2020-2021."),
    FeatureSpec("cohort_2022_plus", "new", "temporal", "first_seen_period", "Flag de cohorte de entrada desde 2022."),
    FeatureSpec("entry_month_sin", "new", "temporal", "first_seen_period", "Codificación cíclica seno del mes de entrada del local."),
    FeatureSpec("entry_month_cos", "new", "temporal", "first_seen_period", "Codificación cíclica coseno del mes de entrada del local."),
)


MODEL_FEATURE_COLUMNS = tuple(spec.name for spec in MODEL_FEATURE_SPECS)
ACTIVITY_SURVIVAL_PRUNED_EXCLUDED_CATEGORIES = frozenset({"competition", "avisos", "temporal"})

HELPER_COLUMN_SPECS: tuple[FeatureSpec, ...] = (
    FeatureSpec("district_code_start", "new", "join_helper", "section_socioeconomic_panel", "Código de distrito del local en el periodo inicial."),
    FeatureSpec("barrio_code_start", "new", "join_helper", "section_socioeconomic_panel", "Código de barrio del local en el periodo inicial."),
    FeatureSpec("division_code_start", "new", "join_helper", "actividades", "Firma/división principal single-division del local al alta."),
    FeatureSpec("event_source", "existing", "target", "abt_survival", "Etiqueta unificada del objetivo: `cese_de_actividad` o `censored`."),
    FeatureSpec("event_subtype", "new", "target", "abt_survival", "Subtipo solo de auditoría: `cambio_actividad`, `desaparicion` o `censored`."),
    FeatureSpec("event_subtype_detail", "new", "target", "abt_survival", "Detalle forense del cierre: fuente exacta del cambio robusto o subtipo final cuando no hay cambio de actividad."),
    FeatureSpec("event_period", "existing", "target", "abt_survival", "Periodo en el que ocurre el evento objetivo."),
    FeatureSpec("duration_months", "existing", "target", "abt_survival", "Duración observada en meses desde el alta hasta evento/censura."),
)


def get_model_feature_columns(*, feature_profile: str = "full") -> tuple[str, ...]:
    if feature_profile == "full":
        base_columns = list(MODEL_FEATURE_COLUMNS)
    elif feature_profile == "activity_survival_pruned":
        base_columns = [
            spec.name
            for spec in MODEL_FEATURE_SPECS
            if spec.category not in ACTIVITY_SURVIVAL_PRUNED_EXCLUDED_CATEGORIES
        ]
    else:
        raise ValueError(f"Unsupported feature_profile: {feature_profile}")

    return tuple(base_columns + macro_category_feature_names())


def _parse_integer_like_text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    numeric_candidate = text.replace(",", ".")
    if re.fullmatch(r"-?\d+(?:\.\d+)?", numeric_candidate):
        try:
            numeric_value = float(numeric_candidate)
        except ValueError:
            numeric_value = math.nan
        if math.isfinite(numeric_value):
            return str(int(numeric_value))
    digits = re.sub(r"[^0-9]", "", text)
    return digits or None


def normalize_admin_code(value: object, *, width: int) -> str | None:
    digits = _parse_integer_like_text(value)
    if digits is None:
        return None
    return digits.zfill(width)[-width:]


def normalize_section_key(value: object) -> str | None:
    digits = _parse_integer_like_text(value)
    if digits is None:
        return None
    return digits.zfill(5)[-5:]


def attach_section_reference_fallbacks(
    abt: pd.DataFrame,
    *,
    section_reference_csv: Path | None = None,
) -> pd.DataFrame:
    enriched = abt.copy()
    section_key = enriched.get("section_key_start", pd.Series(pd.NA, index=enriched.index)).map(normalize_section_key)
    enriched["section_key_start"] = pd.Series(section_key, index=enriched.index, dtype="string")

    resolved_reference = section_reference_csv or (DATA_DIR / "processed" / "section_geography.csv")
    reference = pd.read_csv(
        resolved_reference,
        usecols=["section_key", "district_code", "barrio_code", "geometry_available"],
        dtype={"section_key": "string", "district_code": "string", "barrio_code": "string"},
    )
    reference["section_key"] = reference["section_key"].map(normalize_section_key).astype("string")
    reference["district_code"] = reference["district_code"].map(lambda value: normalize_admin_code(value, width=2)).astype("string")
    reference["barrio_code"] = reference["barrio_code"].map(lambda value: normalize_admin_code(value, width=3)).astype("string")

    enriched = enriched.merge(reference, how="left", left_on="section_key_start", right_on="section_key")
    district_existing = enriched.get("district_code_start", pd.Series(pd.NA, index=enriched.index)).map(
        lambda value: normalize_admin_code(value, width=2)
    )
    barrio_existing = enriched.get("barrio_code_start", pd.Series(pd.NA, index=enriched.index)).map(
        lambda value: normalize_admin_code(value, width=3)
    )

    district_from_section = enriched["section_key_start"].astype("string").str[:2]
    enriched["district_code_start"] = district_existing.fillna(enriched["district_code"]).fillna(district_from_section).astype("string")
    enriched["barrio_code_start"] = barrio_existing.fillna(enriched["barrio_code"]).astype("string")

    geometry_existing = pd.to_numeric(enriched.get("geometry_available_start"), errors="coerce")
    geometry_reference = pd.to_numeric(enriched.get("geometry_available"), errors="coerce")
    enriched["geometry_available_start"] = geometry_existing.fillna(geometry_reference)

    return enriched.drop(columns=[column for column in ["section_key", "district_code", "barrio_code", "geometry_available"] if column in enriched.columns])


def is_valid_madrid_coordinate(lat: pd.Series, lon: pd.Series) -> pd.Series:
    return (
        lat.notna()
        & lon.notna()
        & lat.between(MADRID_LAT_RANGE[0], MADRID_LAT_RANGE[1], inclusive="both")
        & lon.between(MADRID_LON_RANGE[0], MADRID_LON_RANGE[1], inclusive="both")
    )


def build_avisos_yearly_features(
    *,
    raw_manifest: pd.DataFrame | None = None,
    section_panel_csv: Path | None = None,
) -> pd.DataFrame:
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    selected = manifest[
        (manifest["source_name"] == "avisos")
        & (manifest["status"] == "selected")
        & manifest["selected_relative_path"].notna()
    ][["period", "selected_relative_path"]].copy()
    if selected.empty:
        return pd.DataFrame(
            columns=[
                "avisos_year",
                "district_code",
                "barrio_code",
                "avisos_district_prev_year",
                "avisos_district_per_1000_prev_year",
                "avisos_barrio_prev_year",
                "avisos_barrio_per_1000_prev_year",
                "avisos_barrio_share_of_district_prev_year",
            ]
        )

    yearly_frames: list[pd.DataFrame] = []
    for row in selected.sort_values("period").itertuples(index=False):
        year = int(str(row.period))
        frame, _ = read_delimited_file(RAW_DATA_DIR / str(row.selected_relative_path))
        frame.columns = [str(column).strip().upper() for column in frame.columns]
        district_series = frame.get("DISTRITO_ID", pd.Series(pd.NA, index=frame.index)).map(
            lambda value: normalize_admin_code(value, width=2)
        )
        barrio_series = frame.get("BARRIO_ID", pd.Series(pd.NA, index=frame.index)).map(
            lambda value: normalize_admin_code(value, width=3)
        )
        yearly_frames.append(
            pd.DataFrame(
                {
                    "avisos_year": year,
                    "district_code": district_series.astype("string"),
                    "barrio_code": barrio_series.astype("string"),
                }
            )
        )

    avisos = pd.concat(yearly_frames, ignore_index=True)
    district_counts = (
        avisos.dropna(subset=["district_code"])
        .groupby(["avisos_year", "district_code"], dropna=False)
        .size()
        .rename("avisos_district_prev_year")
        .reset_index()
    )
    barrio_counts = (
        avisos.dropna(subset=["district_code", "barrio_code"])
        .groupby(["avisos_year", "district_code", "barrio_code"], dropna=False)
        .size()
        .rename("avisos_barrio_prev_year")
        .reset_index()
    )

    resolved_section_panel = section_panel_csv or (PROJECT_ROOT / "data" / "processed" / "section_socioeconomic_panel.csv")
    population = pd.read_csv(
        resolved_section_panel,
        usecols=["target_period", "district_code", "barrio_code", "total_population"],
        dtype={"target_period": "string", "district_code": "string", "barrio_code": "string"},
    )
    population = population[population["target_period"].astype("string").str.endswith("-12")].copy()
    population["avisos_year"] = pd.to_numeric(population["target_period"].astype("string").str[:4], errors="coerce").astype("Int64")

    district_population = (
        population.dropna(subset=["avisos_year", "district_code"])
        .groupby(["avisos_year", "district_code"], dropna=False)["total_population"]
        .sum()
        .rename("district_population")
        .reset_index()
    )
    barrio_population = (
        population.dropna(subset=["avisos_year", "district_code", "barrio_code"])
        .groupby(["avisos_year", "district_code", "barrio_code"], dropna=False)["total_population"]
        .sum()
        .rename("barrio_population")
        .reset_index()
    )

    out = barrio_counts.merge(district_counts, how="left", on=["avisos_year", "district_code"])
    out = out.merge(district_population, how="left", on=["avisos_year", "district_code"])
    out = out.merge(barrio_population, how="left", on=["avisos_year", "district_code", "barrio_code"])
    out["avisos_district_per_1000_prev_year"] = (
        1000.0 * pd.to_numeric(out["avisos_district_prev_year"], errors="coerce") / pd.to_numeric(out["district_population"], errors="coerce")
    )
    out["avisos_barrio_per_1000_prev_year"] = (
        1000.0 * pd.to_numeric(out["avisos_barrio_prev_year"], errors="coerce") / pd.to_numeric(out["barrio_population"], errors="coerce")
    )
    out["avisos_barrio_share_of_district_prev_year"] = (
        pd.to_numeric(out["avisos_barrio_prev_year"], errors="coerce")
        / pd.to_numeric(out["avisos_district_prev_year"], errors="coerce").replace({0: pd.NA})
    )
    return out[
        [
            "avisos_year",
            "district_code",
            "barrio_code",
            "avisos_district_prev_year",
            "avisos_district_per_1000_prev_year",
            "avisos_barrio_prev_year",
            "avisos_barrio_per_1000_prev_year",
            "avisos_barrio_share_of_district_prev_year",
        ]
    ].sort_values(["avisos_year", "district_code", "barrio_code"]).reset_index(drop=True)


def attach_avisos_features(
    abt: pd.DataFrame,
    *,
    raw_manifest: pd.DataFrame | None = None,
    section_panel_csv: Path | None = None,
    avisos_yearly: pd.DataFrame | None = None,
) -> pd.DataFrame:
    enriched = abt.copy()
    enriched["district_code_start"] = enriched.get("district_code_start", pd.Series(pd.NA, index=enriched.index)).map(
        lambda value: normalize_admin_code(value, width=2)
    ).astype("string")
    enriched["barrio_code_start"] = enriched.get("barrio_code_start", pd.Series(pd.NA, index=enriched.index)).map(
        lambda value: normalize_admin_code(value, width=3)
    ).astype("string")
    enriched["avisos_year"] = (
        pd.to_numeric(enriched["first_seen_period"].astype("string").str[:4], errors="coerce").astype("Int64") - 1
    )

    lookup = avisos_yearly if avisos_yearly is not None else build_avisos_yearly_features(
        raw_manifest=raw_manifest,
        section_panel_csv=section_panel_csv,
    )
    if not lookup.empty:
        lookup = lookup.copy()
        lookup["district_code"] = lookup["district_code"].astype("string")
        lookup["barrio_code"] = lookup["barrio_code"].astype("string")
        lookup["avisos_year"] = pd.to_numeric(lookup["avisos_year"], errors="coerce").astype("Int64")
        enriched = enriched.merge(
            lookup,
            how="left",
            left_on=["avisos_year", "district_code_start", "barrio_code_start"],
            right_on=["avisos_year", "district_code", "barrio_code"],
        )
        enriched = enriched.drop(columns=[column for column in ["district_code", "barrio_code"] if column in enriched.columns])

    for column in (
        "avisos_district_prev_year",
        "avisos_district_per_1000_prev_year",
        "avisos_barrio_prev_year",
        "avisos_barrio_per_1000_prev_year",
        "avisos_barrio_share_of_district_prev_year",
    ):
        if column not in enriched.columns:
            enriched[column] = 0.0
        enriched[column] = pd.to_numeric(enriched[column], errors="coerce").fillna(0.0)
    return enriched


def load_metro_reference(metro_csv: Path | None = None) -> pd.DataFrame:
    resolved_path = metro_csv or (RAW_DATA_DIR / "Metro" / "Entradas_metro_todas.csv")
    frame = pd.read_csv(resolved_path)
    out = pd.DataFrame(
        {
            "metro_lat": pd.to_numeric(frame.get("@lat"), errors="coerce"),
            "metro_lon": pd.to_numeric(frame.get("@lon"), errors="coerce"),
            "metro_name": frame.get("name", pd.Series(pd.NA, index=frame.index)).astype("string"),
        }
    )
    out["metro_display_name"] = out["metro_name"].map(_normalize_metro_display_name).astype("string")
    return out.dropna(subset=["metro_lat", "metro_lon"]).reset_index(drop=True)


def compute_metro_features(
    abt: pd.DataFrame,
    *,
    metro_reference: pd.DataFrame | None = None,
    distance_bands_m: tuple[float, ...] = DEFAULT_METRO_DISTANCE_BANDS_M,
    include_names: bool = False,
    max_names_per_band: int = 6,
) -> pd.DataFrame:
    features = pd.DataFrame(index=abt.index)
    features["metro_distance_m_start"] = np.nan
    for band in distance_bands_m:
        features[f"metro_access_count_{int(band)}m_start"] = 0.0
    if include_names:
        features["metro_nearest_name_start"] = pd.Series(pd.NA, index=abt.index, dtype="string")
        for band in distance_bands_m:
            features[f"metro_access_names_{int(band)}m_start"] = pd.Series(
                [[] for _ in range(len(abt))],
                index=abt.index,
                dtype=object,
            )

    lat = pd.to_numeric(abt.get("lat_wgs84_start"), errors="coerce")
    lon = pd.to_numeric(abt.get("lon_wgs84_start"), errors="coerce")
    valid_mask = is_valid_madrid_coordinate(lat, lon)
    features["missing_metro_distance_start"] = (~valid_mask).astype(float)

    metro = metro_reference if metro_reference is not None else load_metro_reference()
    if metro.empty or not valid_mask.any():
        return features

    metro_radians = np.deg2rad(metro[["metro_lat", "metro_lon"]].to_numpy(dtype=float))
    tree = BallTree(metro_radians, metric="haversine")
    valid_indices = np.flatnonzero(valid_mask.to_numpy(dtype=bool))
    point_radians = np.deg2rad(
        np.column_stack(
            [
                lat.loc[valid_mask].to_numpy(dtype=float),
                lon.loc[valid_mask].to_numpy(dtype=float),
            ]
        )
    )
    nearest_distance, nearest_index = tree.query(point_radians, k=1)
    features.loc[valid_mask, "metro_distance_m_start"] = nearest_distance[:, 0] * EARTH_RADIUS_M
    if include_names:
        display_names = metro.get("metro_display_name", metro.get("metro_name", pd.Series(pd.NA, index=metro.index))).astype("string")
        nearest_names = display_names.iloc[nearest_index[:, 0]].reset_index(drop=True)
        features.loc[valid_mask, "metro_nearest_name_start"] = nearest_names.astype("string")

    for band in distance_bands_m:
        counts = tree.query_radius(point_radians, r=float(band) / EARTH_RADIUS_M, count_only=True)
        features.loc[valid_mask, f"metro_access_count_{int(band)}m_start"] = counts.astype(float)
        if include_names:
            indices = tree.query_radius(point_radians, r=float(band) / EARTH_RADIUS_M, return_distance=False)
            name_column = f"metro_access_names_{int(band)}m_start"
            for frame_index, metro_indices in zip(valid_indices, indices, strict=False):
                raw_names = display_names.iloc[metro_indices].tolist()
                features.at[frame_index, name_column] = _unique_metro_names(raw_names, limit=max_names_per_band)
    return features


def _normalize_metro_display_name(value: object) -> str | pd.NA:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return pd.NA

    text = str(value).strip()
    if not text:
        return pd.NA

    text = _fix_metro_mojibake(text)
    text = re.sub(r"\s+", " ", text).strip(" -,")
    lower_text = text.lower()

    if lower_text.startswith("acceso "):
        text = text[7:].strip()
        lower_text = text.lower()

    if "-" in text and (" pares" in lower_text or " impares" in lower_text):
        text = text.split("-")[-1].strip()
    elif "," in text and any(token in lower_text for token in [" pabellones", " pares", " impares"]):
        text = text.split(",")[0].strip()

    text = re.sub(r"\s+", " ", text).strip(" -,")
    return text or pd.NA


def _fix_metro_mojibake(text: str) -> str:
    if not any(marker in text for marker in ("Ã", "Â", "Ð", "€", "™")):
        return text
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _unique_metro_names(names: list[object], *, limit: int) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw_name in names:
        normalized = _normalize_metro_display_name(raw_name)
        if pd.isna(normalized):
            continue
        name = str(normalized)
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
        if len(out) >= limit:
            break
    return out


def attach_metro_features(
    abt: pd.DataFrame,
    *,
    metro_reference: pd.DataFrame | None = None,
) -> pd.DataFrame:
    features = compute_metro_features(abt, metro_reference=metro_reference)
    return pd.concat([abt.reset_index(drop=True), features.reset_index(drop=True)], axis=1)


def render_survival_feature_inventory_markdown() -> str:
    lines: list[str] = []
    lines.append("# Variables")
    lines.append("")
    lines.append("Inventario de variables del pipeline de supervivencia justo antes del siguiente reentrenamiento canónico.")
    lines.append("")
    lines.append("## Variables de modelado activas")
    lines.append("")
    lines.append("| Variable | Estado | Categoría | Fuente | Descripción |")
    lines.append("| --- | --- | --- | --- | --- |")
    for spec in MODEL_FEATURE_SPECS:
        lines.append(
            f"| {spec.name} | {spec.status} | {spec.category} | {spec.source} | {spec.description} |"
        )
    lines.append("")
    lines.append("## Variables auxiliares y de target")
    lines.append("")
    lines.append("| Variable | Estado | Categoría | Fuente | Descripción |")
    lines.append("| --- | --- | --- | --- | --- |")
    for spec in HELPER_COLUMN_SPECS:
        lines.append(
            f"| {spec.name} | {spec.status} | {spec.category} | {spec.source} | {spec.description} |"
        )
    lines.append("")
    lines.append("## Criterio de uso")
    lines.append("")
    lines.append("- Todas las variables de modelado son point-in-time y se congelan en `first_seen_period` o en información histórica estrictamente anterior.")
    lines.append("- `avisos_*_prev_year` usa el año natural anterior al alta del local para evitar leakage intraanual.")
    lines.append("- `metro_*` usa la posición inicial del local y la malla estática de accesos de metro.")
    lines.append("- Las variables con sufijo `_delta_12m_start` miden cambio frente a 12 meses antes en la misma sección.")
    return "\n".join(lines) + "\n"


def write_survival_feature_inventory(output_path: Path | None = None) -> Path:
    resolved_path = output_path or (PROJECT_ROOT / "VARIABLES.md")
    resolved_path.write_text(render_survival_feature_inventory_markdown(), encoding="utf-8")
    return resolved_path
