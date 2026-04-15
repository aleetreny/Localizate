from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re
import unicodedata

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

try:
    from ftfy import fix_text as _ftfy_fix_text
except ImportError:  # pragma: no cover - optional defensive fallback
    _ftfy_fix_text = None

from .activity_taxonomy import macro_category_feature_names
from .censo import load_raw_manifest
from .csv_utils import read_delimited_file
from .paths import DATA_DIR, DOCS_REFERENCE_DIR, PROJECT_ROOT, RAW_DATA_DIR


EARTH_RADIUS_M = 6_371_000.0
DEFAULT_METRO_DISTANCE_BANDS_M = (500.0, 1000.0)
MADRID_LAT_RANGE = (40.0, 41.0)
MADRID_LON_RANGE = (-4.5, -3.0)
PANEL_INDICATOR_FEATURE_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
    (
        "Numero de locales dados de alta abiertos",
        "district_panel_locales_open_start",
        "Locales dados de alta abiertos en el distrito con join anual lagged <= t-1 (log-transform en modelado).",
    ),
    (
        "Numero de locales dados de alta cerrados",
        "district_panel_locales_closed_start",
        "Locales dados de alta cerrados en el distrito con join anual lagged <= t-1 (log-transform en modelado).",
    ),
    (
        "Tasa absoluta de paro registrado (febrero)",
        "district_panel_unemployment_rate_start",
        "Tasa absoluta de paro registrado del distrito con join anual lagged <= t-1.",
    ),
    (
        "Edad media de la poblacion",
        "district_panel_mean_age_start",
        "Edad media del distrito con join anual lagged <= t-1.",
    ),
    (
        "Indice de dependencia (poblacion de 0-15 + poblacion 65 anos y mas / pob. 16-64)",
        "district_panel_dependency_index_start",
        "Indice de dependencia del distrito con join anual lagged <= t-1.",
    ),
    (
        "Proporcion de personas migrantes (personas extranjeras menos UE y resto paises de OCDE / poblacion total)",
        "district_panel_migrant_share_start",
        "Proporcion de personas migrantes en el distrito con join anual lagged <= t-1.",
    ),
    (
        "Poblacion densidad (hab./ha.)",
        "district_panel_density_start",
        "Densidad de poblacion del distrito con join anual lagged <= t-1.",
    ),
)
IGUALA_FEATURE_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
    (
        "Indice de Vulnerabilidad Territorial Agregado",
        "district_iguala_vulnerability_global_start",
        "Indice IGUALA agregado del distrito con join anual lagged <= t-1.",
    ),
    (
        "Indice de Vulnerabilidad Bienestar Social e Igualdad",
        "district_iguala_bienestar_start",
        "Indice IGUALA de bienestar del distrito con join anual lagged <= t-1.",
    ),
    (
        "Indice de Vulnerabilidad Medio Ambiente Urbano y Movilidad",
        "district_iguala_medio_ambiente_start",
        "Indice IGUALA de medio ambiente y movilidad del distrito con join anual lagged <= t-1.",
    ),
    (
        "Indice de Vulnerabilidad Educacion y Cultura",
        "district_iguala_educacion_start",
        "Indice IGUALA de educacion y cultura del distrito con join anual lagged <= t-1.",
    ),
    (
        "Indice de Vulnerabilidad Economia y Empleo",
        "district_iguala_economia_start",
        "Indice IGUALA de economia y empleo del distrito con join anual lagged <= t-1.",
    ),
    (
        "Indice de Vulnerabilidad Salud",
        "district_iguala_salud_start",
        "Indice IGUALA de salud del distrito con join anual lagged <= t-1.",
    ),
)


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    status: str
    category: str
    source: str
    description: str


BASE_MODEL_FEATURE_SPECS: tuple[FeatureSpec, ...] = (
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
    FeatureSpec("avisos_district_per_1000_prev_year", "new", "avisos", "storage/raw/avisos + section_socioeconomic_panel", "Avisos recibidos del distrito en el año anterior por cada 1.000 habitantes."),
    FeatureSpec("avisos_barrio_per_1000_prev_year", "new", "avisos", "storage/raw/avisos + section_socioeconomic_panel", "Avisos recibidos del barrio en el año anterior por cada 1.000 habitantes."),
    FeatureSpec("avisos_barrio_share_of_district_prev_year", "new", "avisos", "storage/raw/avisos", "Peso del barrio dentro del total de avisos del distrito en el año anterior."),
    FeatureSpec("metro_distance_m_start", "new", "metro", "storage/raw/Metro", "Distancia al acceso de metro más cercano desde la localización inicial (log-transform en modelado)."),
    FeatureSpec("metro_access_count_500m_start", "new", "metro", "storage/raw/Metro", "Número de accesos de metro a 500 m o menos."),
    FeatureSpec("metro_access_count_1000m_start", "new", "metro", "storage/raw/Metro", "Número de accesos de metro a 1 km o menos."),
    FeatureSpec("missing_metro_distance_start", "new", "data_quality", "storage/raw/Metro + censo_geospatial", "Flag de imposibilidad de calcular cercanía a metro por falta de coordenadas iniciales."),
    FeatureSpec("cohort_2015_2017", "new", "temporal", "first_seen_period", "Flag de cohorte de entrada 2015-2017."),
    FeatureSpec("cohort_2018_2019", "new", "temporal", "first_seen_period", "Flag de cohorte de entrada 2018-2019."),
    FeatureSpec("cohort_2020_2021", "new", "temporal", "first_seen_period", "Flag de cohorte de entrada 2020-2021."),
    FeatureSpec("cohort_2022_plus", "new", "temporal", "first_seen_period", "Flag de cohorte de entrada desde 2022."),
    FeatureSpec("entry_month_sin", "new", "temporal", "first_seen_period", "Codificación cíclica seno del mes de entrada del local."),
    FeatureSpec("entry_month_cos", "new", "temporal", "first_seen_period", "Codificación cíclica coseno del mes de entrada del local."),
)

EXTERNAL_MODEL_FEATURE_SPECS: tuple[FeatureSpec, ...] = (
    FeatureSpec("district_panel_locales_open_start", "candidate", "external_panel", "panel_indicadores_2020_2025", "Locales dados de alta abiertos en el distrito con join anual lagged <= t-1."),
    FeatureSpec("district_panel_locales_closed_start", "candidate", "external_panel", "panel_indicadores_2020_2025", "Locales dados de alta cerrados en el distrito con join anual lagged <= t-1."),
    FeatureSpec("district_panel_unemployment_rate_start", "candidate", "external_panel", "panel_indicadores_2020_2025", "Tasa de paro del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_panel_mean_age_start", "candidate", "external_panel", "panel_indicadores_2020_2025", "Edad media del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_panel_dependency_index_start", "candidate", "external_panel", "panel_indicadores_2020_2025", "Indice de dependencia del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_panel_migrant_share_start", "candidate", "external_panel", "panel_indicadores_2020_2025", "Proporcion migrante del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_panel_density_start", "candidate", "external_panel", "panel_indicadores_2020_2025", "Densidad de poblacion del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_iguala_vulnerability_global_start", "candidate", "external_vulnerability", "iguala_global_distritos", "Indice IGUALA agregado del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_iguala_bienestar_start", "candidate", "external_vulnerability", "iguala_global_distritos", "Indice IGUALA de bienestar del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_iguala_medio_ambiente_start", "candidate", "external_vulnerability", "iguala_global_distritos", "Indice IGUALA de medio ambiente del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_iguala_educacion_start", "candidate", "external_vulnerability", "iguala_global_distritos", "Indice IGUALA de educacion del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_iguala_economia_start", "candidate", "external_vulnerability", "iguala_global_distritos", "Indice IGUALA de economia del distrito con join anual lagged <= t-1."),
    FeatureSpec("district_iguala_salud_start", "candidate", "external_vulnerability", "iguala_global_distritos", "Indice IGUALA de salud del distrito con join anual lagged <= t-1."),
)

MODEL_FEATURE_SPECS: tuple[FeatureSpec, ...] = BASE_MODEL_FEATURE_SPECS + EXTERNAL_MODEL_FEATURE_SPECS


MODEL_FEATURE_COLUMNS = tuple(spec.name for spec in MODEL_FEATURE_SPECS)
ACTIVITY_SURVIVAL_PRUNED_EXCLUDED_CATEGORIES = frozenset({"competition", "avisos", "temporal"})
FEATURE_PROFILE_CONFIGS: dict[str, dict[str, object]] = {
    "full": {"include_external": False, "excluded_categories": frozenset()},
    "activity_survival_pruned": {
        "include_external": False,
        "excluded_categories": ACTIVITY_SURVIVAL_PRUNED_EXCLUDED_CATEGORIES,
    },
    "full_with_external": {"include_external": True, "excluded_categories": frozenset()},
    "activity_survival_pruned_with_external": {
        "include_external": True,
        "excluded_categories": ACTIVITY_SURVIVAL_PRUNED_EXCLUDED_CATEGORIES,
    },
}

HELPER_COLUMN_SPECS: tuple[FeatureSpec, ...] = (
    FeatureSpec("district_code_start", "new", "join_helper", "section_socioeconomic_panel", "Código de distrito del local en el periodo inicial."),
    FeatureSpec("barrio_code_start", "new", "join_helper", "section_socioeconomic_panel", "Código de barrio del local en el periodo inicial."),
    FeatureSpec("division_code_start", "new", "join_helper", "actividades", "Firma/división principal single-division del local al alta."),
    FeatureSpec("event_source", "existing", "target", "abt_survival", "Etiqueta unificada del objetivo: `cese_de_actividad` o `censored`."),
    FeatureSpec("event_subtype", "new", "target", "abt_survival", "Subtipo solo de auditoría: `cambio_actividad`, `desaparicion` o `censored`."),
    FeatureSpec("event_subtype_detail", "new", "target", "abt_survival", "Detalle forense del cierre: fuente exacta del cambio robusto o subtipo final cuando no hay cambio de actividad."),
    FeatureSpec("event_period", "existing", "target", "abt_survival", "Periodo en el que ocurre el evento objetivo."),
    FeatureSpec("duration_months", "existing", "target", "abt_survival", "Duración observada en meses desde el alta hasta evento/censura."),
    FeatureSpec("district_panel_year_start", "candidate", "join_helper", "panel_indicadores_2020_2025", "Ano del panel distrital finalmente unido con politica lagged <= t-1."),
    FeatureSpec("district_panel_lag_years_start", "candidate", "join_helper", "panel_indicadores_2020_2025", "Diferencia en anos entre el corte del local y el ano del panel distrital unido."),
    FeatureSpec("district_iguala_year_start", "candidate", "join_helper", "iguala_global_distritos", "Ano de IGUALA finalmente unido con politica lagged <= t-1."),
    FeatureSpec("district_iguala_lag_years_start", "candidate", "join_helper", "iguala_global_distritos", "Diferencia en anos entre el corte del local y el ano de IGUALA unido."),
)


def get_model_feature_columns(*, feature_profile: str = "full") -> tuple[str, ...]:
    config = FEATURE_PROFILE_CONFIGS.get(feature_profile)
    if config is None:
        raise ValueError(f"Unsupported feature_profile: {feature_profile}")

    base_specs = list(BASE_MODEL_FEATURE_SPECS)
    if bool(config.get("include_external")):
        base_specs.extend(EXTERNAL_MODEL_FEATURE_SPECS)

    excluded_categories = frozenset(config.get("excluded_categories", frozenset()))
    base_columns = [spec.name for spec in base_specs if spec.category not in excluded_categories]

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

    resolved_section_panel = section_panel_csv or (PROJECT_ROOT / "storage" / "data" / "processed" / "section_socioeconomic_panel.csv")
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


def normalize_text_key(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("ß", "a").replace("¾", "o").replace("¬", "a").replace("·", "u").replace("Ý", "i")
    text = re.sub(r"[^0-9a-zA-Z]+", " ", text).strip().lower()
    return re.sub(r"\s+", " ", text)


def _find_column_by_candidates(columns: pd.Index | list[str], *candidates: str) -> str | None:
    normalized_candidates = [normalize_text_key(candidate) for candidate in candidates if candidate]
    for column in columns:
        normalized_column = normalize_text_key(column)
        if any(
            normalized_candidate == normalized_column
            or normalized_candidate in normalized_column
            or normalized_column in normalized_candidate
            for normalized_candidate in normalized_candidates
        ):
            return str(column)
    return None


def _parse_localized_numeric_series(values: pd.Series) -> pd.Series:
    text = values.astype("string")
    has_dot = text.str.contains(".", regex=False, na=False)
    has_comma = text.str.contains(",", regex=False, na=False)
    localized = has_dot & has_comma
    cleaned = text.copy()
    cleaned.loc[localized] = cleaned.loc[localized].str.replace(".", "", regex=False)
    cleaned = cleaned.str.replace(",", ".", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def _indicator_matches(target: str, candidate: object) -> bool:
    normalized_target = normalize_text_key(target)
    normalized_candidate = normalize_text_key(candidate)
    if not normalized_target or not normalized_candidate:
        return False
    return normalized_target == normalized_candidate or normalized_target in normalized_candidate or normalized_candidate in normalized_target


def build_panel_indicator_yearly_features(
    *,
    panel_csv: Path | None = None,
    panel_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    resolved_panel = panel_csv or (PROJECT_ROOT / "storage" / "data" / "external" / "panel_indicadores_2020_2025.csv")
    if panel_frame is None:
        if not resolved_panel.exists():
            return pd.DataFrame(columns=["panel_year", "district_code", *[feature_name for _, feature_name, _ in PANEL_INDICATOR_FEATURE_DEFINITIONS]])
        panel = pd.read_csv(resolved_panel, sep=";", low_memory=False, encoding="utf-8-sig")
    else:
        panel = panel_frame.copy()

    indicator_col = _find_column_by_candidates(panel.columns, "indicador_completo")
    value_col = _find_column_by_candidates(panel.columns, "valor_indicador")
    district_col = _find_column_by_candidates(panel.columns, "cod_distrito")
    barrio_col = _find_column_by_candidates(panel.columns, "cod_barrio")
    year_col = _find_column_by_candidates(panel.columns, "ano", "año")
    period_col = _find_column_by_candidates(panel.columns, "Periodo panel", "periodo panel")
    if indicator_col is None or value_col is None or district_col is None:
        return pd.DataFrame(columns=["panel_year", "district_code", *[feature_name for _, feature_name, _ in PANEL_INDICATOR_FEATURE_DEFINITIONS]])

    normalized = panel.copy()
    normalized["district_code"] = normalized[district_col].map(lambda value: normalize_admin_code(value, width=2)).astype("string")
    if year_col is not None:
        normalized["panel_year"] = pd.to_numeric(normalized[year_col], errors="coerce").astype("Int64")
    elif period_col is not None:
        normalized["panel_year"] = pd.to_numeric(normalized[period_col], errors="coerce").astype("Int64") - 1
    else:
        normalized["panel_year"] = pd.Series(pd.NA, index=normalized.index, dtype="Int64")
    normalized["indicator_name"] = normalized[indicator_col].astype("string")
    normalized["indicator_value"] = _parse_localized_numeric_series(normalized[value_col])

    district_level_mask = normalized["district_code"].notna() & normalized["district_code"].ne("00")
    if barrio_col is not None:
        barrio_values = normalized[barrio_col].astype("string").str.strip()
        district_level_mask &= barrio_values.isna() | barrio_values.eq("")
    normalized = normalized[district_level_mask].copy()
    normalized = normalized.dropna(subset=["panel_year", "district_code", "indicator_value"])
    if normalized.empty:
        return pd.DataFrame(columns=["panel_year", "district_code", *[feature_name for _, feature_name, _ in PANEL_INDICATOR_FEATURE_DEFINITIONS]])

    key_frame = normalized[["panel_year", "district_code"]].drop_duplicates().reset_index(drop=True)
    wide = key_frame.copy()
    for raw_name, feature_name, _ in PANEL_INDICATOR_FEATURE_DEFINITIONS:
        matched = normalized[normalized["indicator_name"].map(lambda value: _indicator_matches(raw_name, value))].copy()
        if matched.empty:
            wide[feature_name] = np.nan
            continue
        grouped = matched.groupby(["panel_year", "district_code"], dropna=False)["indicator_value"].mean().rename(feature_name).reset_index()
        wide = wide.merge(grouped, how="left", on=["panel_year", "district_code"])
    return wide.sort_values(["district_code", "panel_year"]).reset_index(drop=True)


def build_iguala_yearly_features(
    *,
    iguala_xlsx: Path | None = None,
    district_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    resolved_iguala = iguala_xlsx or (PROJECT_ROOT / "storage" / "data" / "external" / "iguala_global_distritos.xlsx")
    if district_frame is None:
        if not resolved_iguala.exists():
            return pd.DataFrame(columns=["iguala_year", "district_code", *[feature_name for _, feature_name, _ in IGUALA_FEATURE_DEFINITIONS]])
        try:
            iguala = pd.read_excel(resolved_iguala, sheet_name="Vul. esferas distritos")
        except (ImportError, ModuleNotFoundError, ValueError):
            return pd.DataFrame(columns=["iguala_year", "district_code", *[feature_name for _, feature_name, _ in IGUALA_FEATURE_DEFINITIONS]])
    else:
        iguala = district_frame.copy()

    district_col = _find_column_by_candidates(iguala.columns, "Codigo distrito")
    year_col = _find_column_by_candidates(iguala.columns, "Fecha datos")
    if district_col is None or year_col is None:
        return pd.DataFrame(columns=["iguala_year", "district_code", *[feature_name for _, feature_name, _ in IGUALA_FEATURE_DEFINITIONS]])

    normalized = pd.DataFrame(
        {
            "district_code": iguala[district_col].map(lambda value: normalize_admin_code(value, width=2)).astype("string"),
            "iguala_year": pd.to_numeric(iguala[year_col], errors="coerce").astype("Int64"),
        }
    )
    for raw_name, feature_name, _ in IGUALA_FEATURE_DEFINITIONS:
        source_col = _find_column_by_candidates(iguala.columns, raw_name)
        normalized[feature_name] = _parse_localized_numeric_series(iguala[source_col]) if source_col is not None else np.nan

    normalized = normalized.dropna(subset=["district_code", "iguala_year"])
    normalized = normalized[normalized["district_code"].ne("00")].copy()
    return normalized.sort_values(["district_code", "iguala_year"]).reset_index(drop=True)


def _merge_district_yearly_lookup(
    abt: pd.DataFrame,
    *,
    reference_year: pd.Series,
    lookup: pd.DataFrame,
    lookup_year_col: str,
    lookup_feature_columns: tuple[str, ...],
    output_year_col: str,
    output_lag_col: str,
) -> pd.DataFrame:
    enriched = abt.copy()
    enriched["district_code_start"] = enriched.get("district_code_start", pd.Series(pd.NA, index=enriched.index)).map(
        lambda value: normalize_admin_code(value, width=2)
    ).astype("string")
    enriched["__join_reference_year"] = pd.to_numeric(reference_year, errors="coerce").astype("Int64")
    enriched["__row_id"] = np.arange(len(enriched))

    if lookup.empty:
        for column in lookup_feature_columns:
            if column not in enriched.columns:
                enriched[column] = np.nan
        enriched[output_year_col] = pd.Series(pd.NA, index=enriched.index, dtype="Int64")
        enriched[output_lag_col] = pd.Series(pd.NA, index=enriched.index, dtype="Float64")
        return enriched.drop(columns=["__join_reference_year", "__row_id"])

    prepared_lookup = lookup.copy().rename(columns={"district_code": "__lookup_district_code"})
    prepared_lookup["__lookup_district_code"] = prepared_lookup["__lookup_district_code"].astype("string")
    prepared_lookup[lookup_year_col] = pd.to_numeric(prepared_lookup[lookup_year_col], errors="coerce").astype("Int64")
    for column in lookup_feature_columns:
        if column not in prepared_lookup.columns:
            prepared_lookup[column] = np.nan
    prepared_lookup = prepared_lookup.dropna(subset=["__lookup_district_code", lookup_year_col]).sort_values(["__lookup_district_code", lookup_year_col])

    merged_parts: list[pd.DataFrame] = []
    for district_code, part in enriched.groupby("district_code_start", dropna=False, sort=False):
        local = part.sort_values(["__join_reference_year", "__row_id"]).copy()
        if pd.isna(district_code):
            for column in lookup_feature_columns:
                if column not in local.columns:
                    local[column] = np.nan
            local[output_year_col] = pd.Series(pd.NA, index=local.index, dtype="Int64")
            local[output_lag_col] = pd.Series(pd.NA, index=local.index, dtype="Float64")
            merged_parts.append(local)
            continue

        district_lookup = prepared_lookup[prepared_lookup["__lookup_district_code"].eq(str(district_code))].copy()
        if district_lookup.empty:
            for column in lookup_feature_columns:
                if column not in local.columns:
                    local[column] = np.nan
            local[output_year_col] = pd.Series(pd.NA, index=local.index, dtype="Int64")
            local[output_lag_col] = pd.Series(pd.NA, index=local.index, dtype="Float64")
            merged_parts.append(local)
            continue

        joinable = local[local["__join_reference_year"].notna()].copy()
        non_joinable = local[local["__join_reference_year"].isna()].copy()
        if joinable.empty:
            merged = local.copy()
            for column in lookup_feature_columns:
                if column not in merged.columns:
                    merged[column] = np.nan
            merged[output_year_col] = pd.Series(pd.NA, index=merged.index, dtype="Int64")
            merged[output_lag_col] = pd.Series(pd.NA, index=merged.index, dtype="Float64")
            merged_parts.append(merged)
            continue

        merged = pd.merge_asof(
            joinable,
            district_lookup,
            left_on="__join_reference_year",
            right_on=lookup_year_col,
            direction="backward",
        )
        merged[output_year_col] = pd.to_numeric(merged[lookup_year_col], errors="coerce").astype("Int64")
        merged[output_lag_col] = (
            pd.to_numeric(merged["__join_reference_year"], errors="coerce")
            - pd.to_numeric(merged[lookup_year_col], errors="coerce")
        ).astype("Float64")
        if not non_joinable.empty:
            for column in lookup_feature_columns:
                if column not in non_joinable.columns:
                    non_joinable[column] = np.nan
            non_joinable[output_year_col] = pd.Series(pd.NA, index=non_joinable.index, dtype="Int64")
            non_joinable[output_lag_col] = pd.Series(pd.NA, index=non_joinable.index, dtype="Float64")
            merged = pd.concat([merged, non_joinable], ignore_index=True)
        merged_parts.append(merged)

    merged = pd.concat(merged_parts, ignore_index=True)
    merged = merged.sort_values("__row_id").drop(columns=["__row_id", "__join_reference_year", "__lookup_district_code", lookup_year_col], errors="ignore")
    return merged.reset_index(drop=True)


def attach_external_district_features(
    abt: pd.DataFrame,
    *,
    panel_csv: Path | None = None,
    iguala_xlsx: Path | None = None,
    panel_yearly: pd.DataFrame | None = None,
    iguala_yearly: pd.DataFrame | None = None,
) -> pd.DataFrame:
    enriched = abt.copy()
    reference_year = pd.to_numeric(enriched["first_seen_period"].astype("string").str[:4], errors="coerce").astype("Int64") - 1

    panel_lookup = panel_yearly if panel_yearly is not None else build_panel_indicator_yearly_features(panel_csv=panel_csv)
    enriched = _merge_district_yearly_lookup(
        enriched,
        reference_year=reference_year,
        lookup=panel_lookup,
        lookup_year_col="panel_year",
        lookup_feature_columns=tuple(feature_name for _, feature_name, _ in PANEL_INDICATOR_FEATURE_DEFINITIONS),
        output_year_col="district_panel_year_start",
        output_lag_col="district_panel_lag_years_start",
    )

    iguala_lookup = iguala_yearly if iguala_yearly is not None else build_iguala_yearly_features(iguala_xlsx=iguala_xlsx)
    enriched = _merge_district_yearly_lookup(
        enriched,
        reference_year=reference_year,
        lookup=iguala_lookup,
        lookup_year_col="iguala_year",
        lookup_feature_columns=tuple(feature_name for _, feature_name, _ in IGUALA_FEATURE_DEFINITIONS),
        output_year_col="district_iguala_year_start",
        output_lag_col="district_iguala_lag_years_start",
    )
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
    station_reference = load_metro_station_reference()
    if station_reference.empty:
        out["metro_station_name"] = out["metro_display_name"].astype("string")
    else:
        out = _attach_metro_station_names(out, station_reference)
    return out.dropna(subset=["metro_lat", "metro_lon"]).reset_index(drop=True)


def load_metro_station_reference(metro_csv: Path | None = None) -> pd.DataFrame:
    resolved_path = metro_csv or (RAW_DATA_DIR / "Metro" / "Entradas_metro_principales.csv")
    frame = pd.read_csv(resolved_path)
    out = pd.DataFrame(
        {
            "metro_station_lat": pd.to_numeric(frame.get("@lat"), errors="coerce"),
            "metro_station_lon": pd.to_numeric(frame.get("@lon"), errors="coerce"),
            "metro_station_name": frame.get("name", pd.Series(pd.NA, index=frame.index)).map(_normalize_metro_station_name).astype("string"),
        }
    )
    return out.dropna(subset=["metro_station_lat", "metro_station_lon", "metro_station_name"]).drop_duplicates().reset_index(drop=True)


def _attach_metro_station_names(access_reference: pd.DataFrame, station_reference: pd.DataFrame) -> pd.DataFrame:
    if access_reference.empty or station_reference.empty:
        out = access_reference.copy()
        out["metro_station_name"] = out.get("metro_display_name", pd.Series(pd.NA, index=out.index)).astype("string")
        return out

    station_radians = np.deg2rad(station_reference[["metro_station_lat", "metro_station_lon"]].to_numpy(dtype=float))
    access_radians = np.deg2rad(access_reference[["metro_lat", "metro_lon"]].to_numpy(dtype=float))
    station_tree = BallTree(station_radians, metric="haversine")
    _, nearest_index = station_tree.query(access_radians, k=1)

    out = access_reference.copy()
    nearest_station_names = station_reference["metro_station_name"].iloc[nearest_index[:, 0]].reset_index(drop=True)
    out["metro_station_name"] = nearest_station_names.astype("string")
    return out


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
        features[f"metro_station_count_{int(band)}m_start"] = 0.0
    if include_names:
        features["metro_nearest_name_start"] = pd.Series(pd.NA, index=abt.index, dtype="string")
        features["metro_nearest_station_name_start"] = pd.Series(pd.NA, index=abt.index, dtype="string")
        for band in distance_bands_m:
            features[f"metro_access_names_{int(band)}m_start"] = pd.Series(
                [[] for _ in range(len(abt))],
                index=abt.index,
                dtype=object,
            )
            features[f"metro_station_names_{int(band)}m_start"] = pd.Series(
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
    display_names = metro.get("metro_display_name", metro.get("metro_name", pd.Series(pd.NA, index=metro.index))).astype("string")
    station_names = metro.get("metro_station_name", pd.Series(pd.NA, index=metro.index)).astype("string")
    station_names = station_names.mask(station_names.isna() | station_names.str.len().fillna(0).eq(0), display_names)
    if include_names:
        nearest_names = display_names.iloc[nearest_index[:, 0]].reset_index(drop=True)
        nearest_station_names = station_names.iloc[nearest_index[:, 0]].reset_index(drop=True)
        features.loc[valid_mask, "metro_nearest_name_start"] = nearest_names.astype("string")
        features.loc[valid_mask, "metro_nearest_station_name_start"] = nearest_station_names.astype("string")

    for band in distance_bands_m:
        counts = tree.query_radius(point_radians, r=float(band) / EARTH_RADIUS_M, count_only=True)
        features.loc[valid_mask, f"metro_access_count_{int(band)}m_start"] = counts.astype(float)
        indices = tree.query_radius(point_radians, r=float(band) / EARTH_RADIUS_M, return_distance=False)
        station_count_column = f"metro_station_count_{int(band)}m_start"
        for frame_index, metro_indices in zip(valid_indices, indices, strict=False):
            raw_station_names = station_names.iloc[metro_indices].tolist()
            features.at[frame_index, station_count_column] = float(len(_unique_metro_station_names(raw_station_names, limit=max(len(raw_station_names), 1))))
        if include_names:
            name_column = f"metro_access_names_{int(band)}m_start"
            station_name_column = f"metro_station_names_{int(band)}m_start"
            for frame_index, metro_indices in zip(valid_indices, indices, strict=False):
                raw_names = display_names.iloc[metro_indices].tolist()
                raw_station_names = station_names.iloc[metro_indices].tolist()
                features.at[frame_index, name_column] = _unique_metro_names(raw_names, limit=max_names_per_band)
                features.at[frame_index, station_name_column] = _unique_metro_station_names(raw_station_names, limit=max_names_per_band)
    return features


def _normalize_metro_station_name(value: object) -> str | pd.NA:
    try:
        if value is None or pd.isna(value):
            return pd.NA
    except TypeError:
        pass

    text = str(value).strip()
    if not text:
        return pd.NA

    text = _fix_metro_mojibake(text)
    text = re.sub(r"\s+", " ", text).strip(" -,")
    return text or pd.NA


def _normalize_metro_display_name(value: object) -> str | pd.NA:
    try:
        if value is None or pd.isna(value):
            return pd.NA
    except TypeError:
        pass

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
    if not text:
        return text

    candidate = str(text)
    if _ftfy_fix_text is not None:
        try:
            candidate = _ftfy_fix_text(candidate, normalization="NFC")
        except Exception:
            candidate = str(text)

    best = candidate
    best_score = _metro_mojibake_score(best)
    if best_score == 0:
        return best

    for _ in range(3):
        improved = _try_fix_metro_mojibake(best)
        improved_score = _metro_mojibake_score(improved)
        if improved_score >= best_score:
            break
        best = improved
        best_score = improved_score
        if best_score == 0:
            break
    return best


def _try_fix_metro_mojibake(text: str) -> str:
    candidates = [text]
    for source_encoding, target_encoding in (("latin1", "utf-8"), ("cp1252", "utf-8"), ("latin1", "cp1252")):
        try:
            candidates.append(text.encode(source_encoding).decode(target_encoding))
        except (LookupError, UnicodeEncodeError, UnicodeDecodeError):
            continue

    best = text
    best_score = _metro_mojibake_score(text)
    for candidate in candidates[1:]:
        score = _metro_mojibake_score(candidate)
        if score < best_score:
            best = candidate
            best_score = score
    return best


def _metro_mojibake_score(text: str) -> int:
    suspicious_markers = ("Ã", "Â", "Ð", "€", "™", "�", "¤", "¦", "œ", "Ÿ", "�")
    score = sum(text.count(marker) for marker in suspicious_markers)
    score += text.count("\u201c")
    score += text.count("\u201d")
    score += text.count("\u2018")
    score += text.count("\u2019")
    return score


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


def _unique_metro_station_names(names: list[object], *, limit: int) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw_name in names:
        normalized = _normalize_metro_station_name(raw_name)
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
    lines.append("- Los bloques `district_panel_*` y `district_iguala_*` quedan disponibles solo en perfiles candidate con join anual lagged `<= t-1` a nivel distrito.")
    lines.append("- Las variables con sufijo `_delta_12m_start` miden cambio frente a 12 meses antes en la misma sección.")
    return "\n".join(lines) + "\n"


def write_survival_feature_inventory(output_path: Path | None = None) -> Path:
    resolved_path = output_path or (DOCS_REFERENCE_DIR / "VARIABLES.md")
    resolved_path.write_text(render_survival_feature_inventory_markdown(), encoding="utf-8")
    return resolved_path
