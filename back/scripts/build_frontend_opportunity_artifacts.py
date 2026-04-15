#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.activity_survival_cox import fit_activity_survival_cox_scorer  # noqa: E402
from localizate.activity_taxonomy import classify_macro_category  # noqa: E402
from localizate.censo import load_raw_manifest  # noqa: E402
from localizate.csv_utils import read_delimited_file  # noqa: E402
from localizate.manual_available_locales import MADRID_BBOX  # noqa: E402
from localizate.section_geography import load_section_geodataframe  # noqa: E402
from localizate.section_keys import normalize_section_key_series  # noqa: E402
from localizate.survival_baseline import apply_training_policies, build_feature_frame, compute_linear_risk_score  # noqa: E402
from localizate.survival_features import build_avisos_yearly_features, compute_metro_features, normalize_admin_code  # noqa: E402
from localizate.zone_category_survival import confidence_tier  # noqa: E402


UNIFIED_EQUIPAMIENTOS_CSV = PROJECT_ROOT / "storage" / "data" / "external" / "processed" / "unified_equipamientos_geo.csv"
INSPECCIONES_CSV = PROJECT_ROOT / "storage" / "data" / "external" / "processed" / "inspecciones_consumo.csv"
IGUALA_GLOBAL_XLSX = PROJECT_ROOT / "storage" / "data" / "external" / "iguala_global_distritos.xlsx"
PANEL_INDICADORES_CSV = PROJECT_ROOT / "storage" / "data" / "external" / "panel_indicadores_2020_2025.csv"

AVAILABLE_LISTINGS_CSV = PROJECT_ROOT / "storage" / "data" / "exports" / "manual_available_locales_madrid.csv"
SELECTED_LISTINGS_CSV = PROJECT_ROOT / "storage" / "data" / "exports" / "manual_available_locales_madrid_selected.csv"
SELECTED_SUMMARY_JSON = PROJECT_ROOT / "storage" / "data" / "processed" / "manual_available_locales_madrid_selected_summary.json"
SECTION_PANEL_CSV = PROJECT_ROOT / "storage" / "data" / "processed" / "section_socioeconomic_panel.csv"
LOCAL_SURVIVAL_ABT_CSV = PROJECT_ROOT / "storage" / "data" / "features" / "local_survival_abt.csv"
ACTIVITY_SURVIVAL_ABT_CSV = PROJECT_ROOT / "storage" / "data" / "features" / "activity_survival_abt.csv"
ACTIVITY_MACRO_TAXONOMY_CSV = PROJECT_ROOT / "storage" / "data" / "processed" / "activity_macro_taxonomy.csv"
DISTRICT_CATEGORY_CSV = PROJECT_ROOT / "storage" / "data" / "exports" / "district_category_survival.csv"
BARRIO_CATEGORY_CSV = PROJECT_ROOT / "storage" / "data" / "exports" / "barrio_category_survival.csv"
WEB_DATA_DIR = PROJECT_ROOT / "front" / "public" / "data"
OPPORTUNITY_DATA_DIR = WEB_DATA_DIR / "opportunities"
OPPORTUNITY_SECTIONS_DATA_DIR = OPPORTUNITY_DATA_DIR / "sections"
FRONTEND_OUTPUT_JSON = OPPORTUNITY_DATA_DIR / "listings.json"
FRONTEND_SECTIONS_INDEX_JSON = OPPORTUNITY_SECTIONS_DATA_DIR / "index.json"
FRONTEND_SECTIONS_GEOJSON = OPPORTUNITY_SECTIONS_DATA_DIR / "geometry.geojson"

CALIBRATION_BUCKETS = 20
SECTION_SIMPLIFY_TOLERANCE_M = 8.0
RECENT_LOOKBACK_MONTHS = 36
ACTIVITY_PRIOR_STRENGTH = 25.0
UNSUPPORTED_ACTIVITY_PENALTY = 0.03
ACTIVITY_SOURCE_PENALTY_MULTIPLIER = 1.25
ACTIVITY_UNSUPPORTED_PENALTY_MULTIPLIER = 1.35
ACTIVITY_SOURCE_SCORE_PENALTIES = {
    "barrio": 0.0,
    "district": 0.015,
    "city": 0.03,
}
ACTIVITY_SUPERCATEGORY_REPEAT_PENALTY = 0.05
ACTIVITY_RECOMMENDATION_COUNT = 5
ACTIVITY_DISTRICT_MIN_LOCALES = 80
ACTIVITY_DISTRICT_MIN_EVENTS = 12
ACTIVITY_BARRIO_MIN_LOCALES = 40
ACTIVITY_BARRIO_MIN_EVENTS = 8
ACTIVITY_CITY_MIN_LOCALES = 150
AVISOS_TOP_CATEGORY_COUNT = 3

EQUIPMENT_CATEGORY_LABELS = {
    "bicimad": "BiciMAD",
    "instalaciones_deportivas": "Inst. deportivas",
    "colegios": "Colegios",
    "parques": "Parques",
    "centros_culturales": "Centros culturales",
    "centros_mayores": "Centros mayores",
    "polideportivos": "Polideportivos",
    "bibliotecas": "Bibliotecas",
    "mercados": "Mercados",
    "servicios_sociales": "Servicios sociales",
    "mercadillos": "Mercadillos",
    "aparcamientos": "Aparcamientos",
}
EQUIPMENT_RADII_M = [200, 500, 1000]
EQUIPMENT_TIER_THRESHOLDS = [(16, "Abundantes"), (6, "Medias"), (0, "Escasas")]
INSPECCIONES_TOP_COUNT = 5
IGUALA_SPHERE_COLUMNS = [
    ("Índice de Vulnerabilidad Bienestar Social e Igualdad", "bienestar", "Bienestar social"),
    ("Índice de Vulnerabilidad Medio Ambiente Urbano y Movilidad", "medio_ambiente", "Medio ambiente"),
    ("Índice de Vulnerabilidad Educación y Cultura", "educacion", "Educación y cultura"),
    ("Índice de Vulnerabilidad Economía y Empleo", "economia", "Economía y empleo"),
    ("Índice de Vulnerabilidad Salud", "salud", "Salud"),
]
PANEL_INDICATOR_PICKS = [
    ("Número de locales dados de alta abiertos", "locales_abiertos", "Locales abiertos"),
    ("Número de locales dados de alta cerrados", "locales_cerrados", "Locales cerrados"),
    ("Tasa absoluta de paro registrado (febrero)", "tasa_paro", "Tasa de paro (%)"),
    ("Número habitantes", "habitantes_distrito", "Habitantes"),
    ("Edad media de la población", "edad_media_distrito", "Edad media"),
    ("Índice de dependencia (población de 0-15 + población 65 años y más / pob. 16-64)", "indice_dependencia", "Índice de dependencia"),
    ("Proporción de personas migrantes (personas extranjeras menos UE y resto países de OCDE / población total)", "proporcion_migrantes", "Proporción migrante"),
    ("Población densidad (hab./ha.)", "densidad_distrito", "Densidad del distrito"),
    ("Superficie de zonas verdes y parques de distrito (ha.) entre número de habitantes *10.000", "zonas_verdes_por_10k", "Zonas verdes por 10.000 hab."),
    ("Mercados municipales", "mercados_municipales", "Mercados municipales"),
    ("Bibliotecas municipales", "bibliotecas_municipales", "Bibliotecas municipales"),
    ("Centros y espacios culturales", "centros_culturales_distrito", "Centros culturales"),
    ("Centros deportivos municipales", "centros_deportivos_municipales", "Centros deportivos"),
    ("Instalaciones deportivas básicas", "instalaciones_deportivas_basicas", "Instalaciones deportivas básicas"),
    ("Centros municipales de mayores", "centros_municipales_mayores", "Centros de mayores"),
    ("Apartamentos municipales para mayores", "apartamentos_municipales_mayores", "Apartamentos para mayores"),
    ("Personas socias de los centros municipales de mayores", "socios_centros_mayores", "Personas socias centros mayores"),
    ("Valor catastral medio por inmueble de uso residencial", "valor_catastral", "Valor catastral medio (€)"),
]

POINT_OUTPUT_COLUMNS = [
    "listing_id",
    "listing_url",
    "card_title",
    "address_text",
    "operation",
    "price_eur",
    "price_per_m2_eur",
    "area_m2",
    "lat_wgs84",
    "lon_wgs84",
    "section_key",
    "district_code",
    "district_name",
    "barrio_code",
    "barrio_name",
    "risk_score",
    "risk_percentile",
    "expected_survival_12m",
    "expected_survival_24m",
    "opportunity_tier",
    "city_rank",
    "city_total_sections",
    "district_rank",
    "district_total_sections",
    "barrio_rank",
    "barrio_total_sections",
    "renta_effective_eur",
    "total_population_start",
    "population_density_km2_start",
    "age_mean_start",
    "share_foreign_start",
    "share_age_15_29_start",
    "share_age_65_plus_start",
    "metro_distance_m_start",
    "metro_access_count_500m_start",
    "metro_access_count_1000m_start",
    "metro_station_count_500m_start",
    "metro_station_count_1000m_start",
    "metro_nearest_name_start",
    "metro_nearest_station_name_start",
    "metro_access_names_500m_start",
    "metro_access_names_1000m_start",
    "metro_station_names_500m_start",
    "metro_station_names_1000m_start",
    "avisos_barrio_per_1000_prev_year",
    "avisos_district_per_1000_prev_year",
    "section_local_count_start",
    "section_unique_activity_category_count_start",
    "section_turnover_rate_12m_start",
    "section_same_activity_category_share_start",
    "best_activity_label",
    "best_activity_risk",
    "best_activity_survival_24m",
]

ABT_USECOLS = [
    "first_seen_period",
    "duration_months",
    "event_observed",
    "section_key_start",
    "district_code_start",
    "barrio_code_start",
    "h3_cell_start",
    "coord_transform_status_start",
    "padron_lag_months_start",
    "total_population_start",
    "age_mean_start",
    "renta_best_eur_start",
    "share_foreign_start",
    "share_male_start",
    "share_age_00_14_start",
    "share_age_15_29_start",
    "share_age_30_44_start",
    "share_age_45_64_start",
    "share_age_65_plus_start",
    "population_density_km2_start",
    "total_population_delta_12m_start",
    "share_foreign_delta_12m_start",
    "share_age_15_29_delta_12m_start",
    "population_density_km2_delta_12m_start",
    "renta_best_eur_delta_12m_start",
    "n_divisions_start",
    "n_epigrafes_start",
    "n_activity_categories_start",
    "section_local_count_start",
    "section_unique_division_count_start",
    "section_unique_activity_category_count_start",
    "section_single_division_share_start",
    "section_same_division_local_count_start",
    "section_same_division_share_start",
    "section_same_activity_category_local_count_start",
    "section_same_activity_category_share_start",
    "section_entry_count_3m_start",
    "section_entry_count_6m_start",
    "section_entry_count_12m_start",
    "section_exit_count_3m_start",
    "section_exit_count_6m_start",
    "section_exit_count_12m_start",
    "section_entry_rate_12m_start",
    "section_exit_rate_12m_start",
    "section_net_flow_12m_start",
    "section_turnover_rate_12m_start",
    "section_division_hhi_start",
    "section_division_top_share_start",
    "section_activity_category_hhi_start",
    "section_activity_category_top_share_start",
    "section_local_count_delta_12m_start",
    "geometry_available_start",
    "avisos_district_per_1000_prev_year",
    "avisos_barrio_per_1000_prev_year",
    "avisos_barrio_share_of_district_prev_year",
    "metro_distance_m_start",
    "metro_access_count_500m_start",
    "metro_access_count_1000m_start",
    "missing_metro_distance_start",
]

ACTIVITY_COX_ABT_USECOLS = list(dict.fromkeys(ABT_USECOLS + [
    "renta_best_eur_start",
    "activity_category_code_start",
]))

ACTIVITY_SECTION_SCORING_COLUMNS = [
    "section_key",
    "district_code",
    "district_name",
    "barrio_name",
    "first_seen_period",
    "h3_cell_start",
    "renta_effective_eur",
    "renta_carry_forward_years",
    "share_foreign_start",
    "share_male_start",
    "share_age_00_14_start",
    "share_age_15_29_start",
    "share_age_30_44_start",
    "share_age_45_64_start",
    "share_age_65_plus_start",
    "age_mean_start",
    "total_population_start",
    "population_density_km2_start",
    "padron_lag_months_start",
    "geometry_available_start",
    "n_divisions_start",
    "n_epigrafes_start",
    "n_activity_categories_start",
    "section_local_count_start",
    "section_unique_division_count_start",
    "section_unique_activity_category_count_start",
    "section_single_division_share_start",
    "section_same_division_local_count_start",
    "section_same_division_share_start",
    "section_same_activity_category_local_count_start",
    "section_same_activity_category_share_start",
    "section_entry_count_3m_start",
    "section_entry_count_6m_start",
    "section_entry_count_12m_start",
    "section_exit_count_3m_start",
    "section_exit_count_6m_start",
    "section_exit_count_12m_start",
    "section_entry_rate_12m_start",
    "section_exit_rate_12m_start",
    "section_net_flow_12m_start",
    "section_turnover_rate_12m_start",
    "section_division_hhi_start",
    "section_division_top_share_start",
    "section_activity_category_hhi_start",
    "section_activity_category_top_share_start",
    "avisos_district_per_1000_prev_year",
    "avisos_barrio_per_1000_prev_year",
    "avisos_barrio_share_of_district_prev_year",
    "total_population_delta_12m_start",
    "share_foreign_delta_12m_start",
    "share_age_15_29_delta_12m_start",
    "population_density_km2_delta_12m_start",
    "renta_best_eur_delta_12m_start",
    "metro_distance_m_start",
    "metro_access_count_500m_start",
    "metro_access_count_1000m_start",
    "missing_metro_distance_start",
]

SECTION_PROFILE_MEDIAN_COLUMNS = [
    "section_local_count_start",
    "section_unique_division_count_start",
    "section_unique_activity_category_count_start",
    "section_single_division_share_start",
    "section_same_division_local_count_start",
    "section_same_division_share_start",
    "section_same_activity_category_local_count_start",
    "section_same_activity_category_share_start",
    "section_entry_count_3m_start",
    "section_entry_count_6m_start",
    "section_entry_count_12m_start",
    "section_exit_count_3m_start",
    "section_exit_count_6m_start",
    "section_exit_count_12m_start",
    "section_entry_rate_12m_start",
    "section_exit_rate_12m_start",
    "section_net_flow_12m_start",
    "section_turnover_rate_12m_start",
    "section_division_hhi_start",
    "section_division_top_share_start",
    "section_activity_category_hhi_start",
    "section_activity_category_top_share_start",
    "section_local_count_delta_12m_start",
]

SECTION_CONTEXT_OVERRIDE_COLUMNS = [
    "section_local_count_start",
    "section_unique_division_count_start",
    "section_unique_activity_category_count_start",
    "section_single_division_share_start",
    "section_same_division_local_count_start",
    "section_same_division_share_start",
    "section_same_activity_category_local_count_start",
    "section_same_activity_category_share_start",
    "section_local_count_delta_12m_start",
]

SECTION_CONTEXT_OVERRIDE_USECOLS = [
    "first_seen_period",
    "section_key_start",
    "district_code_start",
    "barrio_code_start",
    *SECTION_CONTEXT_OVERRIDE_COLUMNS,
]


# ---------------------------------------------------------------------------
# External data loaders
# ---------------------------------------------------------------------------


def load_equipment_points() -> pd.DataFrame:
    if not UNIFIED_EQUIPAMIENTOS_CSV.exists():
        print("  [WARN] Equipment file not found, skipping facility proximity")
        return pd.DataFrame(columns=["category", "lat", "lon"])
    df = pd.read_csv(UNIFIED_EQUIPAMIENTOS_CSV)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    return df.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def _haversine_matrix(lats: np.ndarray, lons: np.ndarray, eq_lats: np.ndarray, eq_lons: np.ndarray) -> np.ndarray:
    """Return distance matrix (n_points, n_eq) in metres using vectorised haversine."""
    R = 6_371_000.0
    lat1 = np.radians(lats[:, np.newaxis])
    lon1 = np.radians(lons[:, np.newaxis])
    lat2 = np.radians(eq_lats[np.newaxis, :])
    lon2 = np.radians(eq_lons[np.newaxis, :])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return R * 2.0 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _empty_facilities_result() -> dict:
    return {
        "facilities_tier": "Sin datos",
        "facilities_200m": 0,
        "facilities_500m": 0,
        "facilities_1000m": 0,
        "facilities_by_category": [],
    }


def compute_equipment_proximity_batch(
    lats: pd.Series,
    lons: pd.Series,
    equipment: pd.DataFrame,
) -> list[dict]:
    """For each point compute equipment counts per category at each radius."""
    if equipment.empty:
        return [_empty_facilities_result() for _ in range(len(lats))]

    lats_arr = lats.to_numpy(dtype=float, na_value=np.nan)
    lons_arr = lons.to_numpy(dtype=float, na_value=np.nan)
    valid = ~(np.isnan(lats_arr) | np.isnan(lons_arr))
    n = len(lats_arr)

    eq_lats = equipment["lat"].to_numpy(dtype=float)
    eq_lons = equipment["lon"].to_numpy(dtype=float)
    eq_cats = equipment["category"].to_numpy()
    categories = sorted(EQUIPMENT_CATEGORY_LABELS.keys())
    cat_index = {c: i for i, c in enumerate(categories)}

    results: list[dict] = [_empty_facilities_result()] * n

    valid_idx = np.where(valid)[0]
    if len(valid_idx) == 0:
        return results

    dist = _haversine_matrix(lats_arr[valid_idx], lons_arr[valid_idx], eq_lats, eq_lons)

    for pos, gi in enumerate(valid_idx):
        row_dist = dist[pos]
        breakdown = []
        totals = {}
        for radius in EQUIPMENT_RADII_M:
            mask = row_dist <= radius
            totals[radius] = int(mask.sum())
            cats_in = eq_cats[mask]
            cat_counts = {}
            for cat in categories:
                cat_counts[cat] = int((cats_in == cat).sum())
            for cat in categories:
                if pos == 0 or radius == EQUIPMENT_RADII_M[0]:
                    pass
            for cat in categories:
                existing = next((b for b in breakdown if b["category"] == cat), None)
                if existing is None:
                    entry = {"category": cat, "label": EQUIPMENT_CATEGORY_LABELS.get(cat, cat)}
                    entry[f"count_{radius}m"] = cat_counts[cat]
                    breakdown.append(entry)
                else:
                    existing[f"count_{radius}m"] = cat_counts[cat]

        breakdown.sort(key=lambda x: x.get("count_1000m", 0), reverse=True)
        total_500 = totals.get(500, 0)
        tier = "Escasas"
        for threshold, label in EQUIPMENT_TIER_THRESHOLDS:
            if total_500 >= threshold:
                tier = label
                break

        results[gi] = {
            "facilities_tier": tier,
            "facilities_200m": totals.get(200, 0),
            "facilities_500m": totals.get(500, 0),
            "facilities_1000m": totals.get(1000, 0),
            "facilities_by_category": breakdown,
        }

    return results


def load_iguala_vulnerability() -> dict[str, dict]:
    """Return {district_code_2digit: {global, city_avg, spheres: [...]}} from latest IGUALA year."""
    if not IGUALA_GLOBAL_XLSX.exists():
        print("  [WARN] IGUALA file not found, skipping vulnerability")
        return {}
    try:
        import openpyxl
    except ModuleNotFoundError:
        print("  [WARN] openpyxl not available, skipping vulnerability")
        return {}

    wb = openpyxl.load_workbook(IGUALA_GLOBAL_XLSX, read_only=True)
    ws = wb["Vul. esferas distritos"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if len(rows) < 2:
        return {}

    header = rows[0]
    data_rows = rows[1:]
    latest_year = max(r[2] for r in data_rows if r[2] is not None)
    latest = [r for r in data_rows if r[2] == latest_year]

    lookup: dict[str, dict] = {}
    city_avg = latest[0][4] if latest else None
    for r in latest:
        code = str(int(r[0])).zfill(2)
        spheres = []
        for col_name, key, display_label in IGUALA_SPHERE_COLUMNS:
            idx = next((i for i, h in enumerate(header) if h and col_name in str(h)), None)
            if idx is not None and idx < len(r):
                val = r[idx]
                avg_idx = idx + 1
                avg = r[avg_idx] if avg_idx < len(r) else None
                spheres.append({"key": key, "label": display_label, "valor": _safe_float(val), "media_ciudad": _safe_float(avg)})
        lookup[code] = {
            "vulnerabilidad_global": _safe_float(r[3]),
            "vulnerabilidad_global_media_ciudad": _safe_float(city_avg),
            "vulnerabilidad_esferas": spheres,
        }
    return lookup


def load_inspecciones_by_district() -> dict[str, dict]:
    """Return {district_code_2digit: {total, city_avg, top_epigrafes: [...]}}."""
    if not INSPECCIONES_CSV.exists():
        print("  [WARN] Inspecciones file not found, skipping")
        return {}
    df = pd.read_csv(INSPECCIONES_CSV, low_memory=False)
    if "DISTRITO" not in df.columns:
        return {}

    df["district_code"] = df["DISTRITO"].map(lambda v: str(v).strip().split(" - ")[0].strip().zfill(2) if pd.notna(v) else None)
    total_by_dist = df.groupby("district_code").size()
    city_avg = float(total_by_dist.mean()) if not total_by_dist.empty else 0.0

    lookup: dict[str, dict] = {}
    for code, group in df.groupby("district_code"):
        total = len(group)
        epig_col = "EPIGRAFE" if "EPIGRAFE" in df.columns else None
        top_epigrafes = []
        if epig_col:
            cleaned = group[epig_col].map(_clean_epigrafe_label).dropna()
            counts = cleaned.value_counts().head(INSPECCIONES_TOP_COUNT)
            for label, count in counts.items():
                top_epigrafes.append({"label": str(label), "count": int(count), "share": round(int(count) / total, 3) if total else 0})
        lookup[str(code)] = {
            "inspecciones_distrito_total": total,
            "inspecciones_ciudad_media": round(city_avg, 1),
            "inspecciones_top_epigrafes": top_epigrafes,
        }
    return lookup


def _clean_epigrafe_label(raw: str) -> str | None:
    """Clean raw inspection epigraph labels and drop unresolved buckets."""
    parts = raw.split(" - ", 1)
    text = parts[-1].strip() if len(parts) > 1 else raw.strip()
    text = text.replace("SITUADOS:", "").strip(" :")
    if not text:
        return None
    if text.upper() == "SIN DETERMINAR":
        return None
    return text.capitalize()


def load_panel_indicators_by_district() -> dict[str, list[dict]]:
    """Return {district_code_2digit: [{id, label, valor, media_ciudad}, ...]} for picked indicators."""
    if not PANEL_INDICADORES_CSV.exists():
        print("  [WARN] Panel indicadores file not found, skipping")
        return {}
    df = pd.read_csv(PANEL_INDICADORES_CSV, sep=";", low_memory=False, encoding="utf-8")

    indicator_col = None
    for c in df.columns:
        if "indicador_completo" in c.lower() or "indicador_completo" in c:
            indicator_col = c
            break
    if indicator_col is None:
        return {}

    value_col = None
    for c in df.columns:
        if "valor_indicador" in c.lower() or "valor_indicador" in c:
            value_col = c
            break
    if value_col is None:
        return {}

    dist_col = None
    for c in df.columns:
        if "cod_distrito" in c.lower() or "cod_distrito" in c:
            dist_col = c
            break
    if dist_col is None:
        return {}

    period_col = None
    for c in df.columns:
        if "periodo panel" in c.lower() or "Periodo panel" in c:
            period_col = c
            break

    indicator_names_in_data = set(df[indicator_col].dropna().unique())

    matched_picks = []
    for raw_name, key, label in PANEL_INDICATOR_PICKS:
        matches = [n for n in indicator_names_in_data if _fuzzy_indicator_match(raw_name, n)]
        if matches:
            matched_picks.append((matches[0], key, label))

    if not matched_picks:
        return {}

    latest_period = str(df[period_col].dropna().max()) if period_col else None
    if latest_period and period_col:
        period_df = df[df[period_col].astype(str) == latest_period]
    else:
        period_df = df

    lookup: dict[str, list[dict]] = {}
    for matched_name, key, label in matched_picks:
        subset = period_df[period_df[indicator_col] == matched_name].copy()
        subset["_val"] = pd.to_numeric(subset[value_col].astype(str).str.replace(",", "."), errors="coerce")
        subset["_dc"] = pd.to_numeric(subset[dist_col], errors="coerce").fillna(0).astype(int).astype(str).str.zfill(2)
        barrio_col = next((c for c in df.columns if "cod_barrio" in c.lower()), None)
        if barrio_col is not None:
            district_level = subset[subset[barrio_col].isna() | (subset[barrio_col].astype(str).str.strip() == "")]
        else:
            district_level = subset
        if district_level.empty:
            district_level = subset.groupby("_dc")["_val"].mean().reset_index()
            district_level.columns = ["_dc", "_val"]

        district_level = district_level[district_level["_dc"] != "00"].copy()
        if district_level.empty:
            continue

        city_mean = float(district_level["_val"].mean()) if not district_level.empty else None

        for _, row_data in district_level.iterrows():
            code = str(row_data["_dc"])
            val = _safe_float(row_data["_val"])
            lookup.setdefault(code, []).append({
                "id": key,
                "label": label,
                "valor": val,
                "media_ciudad": round(city_mean, 1) if city_mean is not None else None,
            })

    return lookup


def _fuzzy_indicator_match(target: str, candidate: str) -> bool:
    t = target.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    c = candidate.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    c = c.replace("ß", "a").replace("¾", "o").replace("¬", "a").replace("·", "u").replace("Ý", "i").replace("ú", "u")
    return t[:40] in c or c[:40] in t


def _safe_float(value: object) -> float | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return None


def enrich_frame_with_external_district_data(
    frame: pd.DataFrame,
    district_code_col: str,
    vulnerability: dict[str, dict],
    inspecciones: dict[str, dict],
    panel: dict[str, list[dict]],
) -> None:
    """Add vulnerability, inspecciones, and panel columns to frame in-place by district code."""
    codes = frame[district_code_col].astype(str).str.strip().str.zfill(2)

    frame["vulnerabilidad_global"] = codes.map(lambda c: (vulnerability.get(c) or {}).get("vulnerabilidad_global"))
    frame["vulnerabilidad_global_media_ciudad"] = codes.map(lambda c: (vulnerability.get(c) or {}).get("vulnerabilidad_global_media_ciudad"))
    frame["vulnerabilidad_esferas"] = codes.map(lambda c: (vulnerability.get(c) or {}).get("vulnerabilidad_esferas", []))

    frame["inspecciones_distrito_total"] = codes.map(lambda c: (inspecciones.get(c) or {}).get("inspecciones_distrito_total"))
    frame["inspecciones_ciudad_media"] = codes.map(lambda c: (inspecciones.get(c) or {}).get("inspecciones_ciudad_media"))
    frame["inspecciones_top_epigrafes"] = codes.map(lambda c: (inspecciones.get(c) or {}).get("inspecciones_top_epigrafes", []))

    frame["indicadores_distrito"] = codes.map(lambda c: panel.get(c, []))


def enrich_frame_with_facilities(frame: pd.DataFrame, lat_col: str, lon_col: str, equipment: pd.DataFrame) -> None:
    """Add facilities proximity columns to frame in-place."""
    prox = compute_equipment_proximity_batch(frame[lat_col], frame[lon_col], equipment)
    frame["facilities_tier"] = [p["facilities_tier"] for p in prox]
    frame["facilities_200m"] = [p["facilities_200m"] for p in prox]
    frame["facilities_500m"] = [p["facilities_500m"] for p in prox]
    frame["facilities_1000m"] = [p["facilities_1000m"] for p in prox]
    frame["facilities_by_category"] = [p["facilities_by_category"] for p in prox]


def main() -> int:
    print("Loading external data sources...")
    equipment = load_equipment_points()
    vulnerability = load_iguala_vulnerability()
    inspecciones = load_inspecciones_by_district()
    panel = load_panel_indicators_by_district()
    print(f"  Equipment points: {len(equipment):,}")
    print(f"  Vulnerability districts: {len(vulnerability)}")
    print(f"  Inspecciones districts: {len(inspecciones)}")
    print(f"  Panel indicator districts: {len(panel)}")
    external = {
        "equipment": equipment,
        "vulnerability": vulnerability,
        "inspecciones": inspecciones,
        "panel": panel,
    }

    selected_listings, filter_summary = build_selected_available_listings(AVAILABLE_LISTINGS_CSV)
    reference = build_reference_inputs(LOCAL_SURVIVAL_ABT_CSV)
    section_profiles, sections_geojson = build_section_profiles(reference, external)
    selected_scored = score_selected_available_listings(selected_listings, section_profiles, reference, external)

    SELECTED_LISTINGS_CSV.parent.mkdir(parents=True, exist_ok=True)
    selected_scored[POINT_OUTPUT_COLUMNS].to_csv(SELECTED_LISTINGS_CSV, index=False)

    summary = build_selected_summary(selected_scored, filter_summary)
    SELECTED_SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SELECTED_SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    FRONTEND_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    FRONTEND_SECTIONS_INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
    FRONTEND_SECTIONS_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    FRONTEND_OUTPUT_JSON.write_text(
        json.dumps(build_frontend_artifacts(selected_scored, filter_summary), ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    FRONTEND_SECTIONS_INDEX_JSON.write_text(
        json.dumps(build_section_index_payload(section_profiles), ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    FRONTEND_SECTIONS_GEOJSON.write_text(json.dumps(sections_geojson, ensure_ascii=False, allow_nan=False), encoding="utf-8")

    print(f"Selected opportunity listings: {len(selected_scored):,}")
    print(f"Sections with opportunity profile: {len(section_profiles):,}")
    print(f"Wrote selected CSV: {SELECTED_LISTINGS_CSV}")
    print(f"Wrote summary JSON: {SELECTED_SUMMARY_JSON}")
    print(f"Wrote frontend artifacts: {FRONTEND_OUTPUT_JSON}")
    print(f"Wrote section index JSON: {FRONTEND_SECTIONS_INDEX_JSON}")
    print(f"Wrote section GeoJSON: {FRONTEND_SECTIONS_GEOJSON}")
    return 0


def build_selected_available_listings(path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    frame = pd.read_csv(path, low_memory=False)
    frame["listing_id"] = frame["listing_id"].astype("string")
    frame["section_key"] = normalize_section_key_series(frame.get("section_key", pd.Series(pd.NA, index=frame.index))).astype("string")
    frame["district_code"] = frame.get("district_code", pd.Series(pd.NA, index=frame.index)).map(
        lambda value: normalize_admin_code(value, width=2)
    ).astype("string")
    frame["barrio_code"] = frame.get("barrio_code", pd.Series(pd.NA, index=frame.index)).map(
        lambda value: normalize_admin_code(value, width=3)
    ).astype("string")

    for column in ["price_eur", "price_per_m2_eur", "area_m2", "lat_wgs84", "lon_wgs84"]:
        frame[column] = pd.to_numeric(frame.get(column), errors="coerce")

    frame["district_name"] = frame.get("district_name", pd.Series(pd.NA, index=frame.index)).map(clean_place_name).astype("string")
    frame["barrio_name"] = frame.get("barrio_name", pd.Series(pd.NA, index=frame.index)).map(clean_place_name).astype("string")
    frame["price_per_m2_eur"] = frame["price_per_m2_eur"].fillna(frame["price_eur"] / frame["area_m2"].replace({0: np.nan}))

    precise_mask = (
        frame.get("coord_precision", pd.Series(pd.NA, index=frame.index)).astype("string").eq("street_approx")
        & frame["section_key"].notna()
        & frame["lat_wgs84"].notna()
        & frame["lon_wgs84"].notna()
    )
    precise = frame.loc[precise_mask].copy()
    precise["has_commercial_fields"] = precise["price_eur"].notna() & precise["area_m2"].notna()
    precise["outlier_flag_count"], precise["outlier_reasons"] = compute_outlier_flags(precise)

    selected = precise.loc[precise["has_commercial_fields"] & precise["outlier_flag_count"].le(1)].copy()
    selected = selected.sort_values(["operation", "district_name", "barrio_name", "listing_id"], na_position="last").reset_index(drop=True)

    summary = {
        "total_listings": int(len(frame)),
        "precise_candidates": int(len(precise)),
        "selected_listings": int(len(selected)),
        "excluded_incomplete": int((~precise["has_commercial_fields"]).sum()),
        "excluded_outliers": int((precise["has_commercial_fields"] & precise["outlier_flag_count"].gt(1)).sum()),
        "operations": {
            str(key): int(value) for key, value in selected["operation"].astype("string").value_counts(dropna=False).to_dict().items()
        },
    }
    return selected, summary


def build_reference_inputs(abt_path: Path) -> dict[str, object]:
    abt = pd.read_csv(abt_path, usecols=ABT_USECOLS, low_memory=False)
    abt["section_key_start"] = normalize_section_key_series(abt.get("section_key_start", pd.Series(pd.NA, index=abt.index))).astype("string")
    abt["district_code_start"] = abt.get("district_code_start", pd.Series(pd.NA, index=abt.index)).map(
        lambda value: normalize_admin_code(value, width=2)
    ).astype("string")
    abt["barrio_code_start"] = abt.get("barrio_code_start", pd.Series(pd.NA, index=abt.index)).map(
        lambda value: normalize_admin_code(value, width=3)
    ).astype("string")

    policy = apply_training_policies(abt, transition_policy="exclude_transition", renta_max_year=2023)
    dataset = policy["dataset"].copy()
    dataset["first_seen_date"] = pd.to_datetime(dataset["first_seen_period"].astype("string") + "-01", errors="coerce")

    reference_features = build_feature_frame(dataset, fill_missing=True)
    feature_means = reference_features.mean()
    feature_stds = reference_features.std(ddof=0).replace(0, 1).fillna(1.0)
    feature_fill_values = reference_features.median().fillna(0.0)
    reference_scores = compute_linear_risk_score(reference_features, reference_means=feature_means, reference_stds=feature_stds)
    dataset["risk_score"] = reference_scores

    section_reference = build_section_feature_reference(dataset)
    section_context_override_source = pd.read_csv(ACTIVITY_SURVIVAL_ABT_CSV, usecols=SECTION_CONTEXT_OVERRIDE_USECOLS, low_memory=False)
    section_context_override = build_section_feature_reference(
        section_context_override_source,
        value_columns=SECTION_CONTEXT_OVERRIDE_COLUMNS,
    )
    section_reference = overwrite_section_reference_columns(
        section_reference,
        section_context_override,
        columns=SECTION_CONTEXT_OVERRIDE_COLUMNS,
    )

    latest_period = str(dataset["first_seen_period"].astype("string").dropna().max())
    return {
        "dataset": dataset,
        "feature_columns": list(reference_features.columns),
        "feature_means": feature_means,
        "feature_stds": feature_stds,
        "feature_fill_values": feature_fill_values,
        "sorted_scores": np.sort(reference_scores.to_numpy(dtype=float)),
        "calibration": build_calibration_lookup(
            score=reference_scores,
            duration=dataset["duration_months"],
            event=dataset["event_observed"],
            bucket_count=CALIBRATION_BUCKETS,
        ),
        # Commercial stock/diversity fields are materially healthier in the activity ABT.
        # The local ABT currently carries degenerate zeros for much of that block, which
        # leaks into the opportunity competition cards if we do not override it here.
        "section_reference": section_reference,
        "latest_period": latest_period,
    }


def build_section_profiles(reference: dict[str, object], external: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
    section_panel, latest_period = load_latest_section_panel(SECTION_PANEL_CSV)
    sections = load_section_geometry()
    section_reference = reference["section_reference"]
    activity_context = build_activity_prediction_context()
    avisos_lookup = build_latest_avisos_lookup(SECTION_PANEL_CSV)

    section_profiles = sections.merge(section_panel, how="left", on="section_key", suffixes=("", "_panel"))
    section_profiles = section_profiles.merge(section_reference, how="left", on="section_key", suffixes=("", "_median"))
    section_profiles = section_profiles.merge(avisos_lookup, how="left", on=["district_code", "barrio_code"])

    section_profiles["district_name"] = coalesce_strings(section_profiles.get("district_name_panel"), section_profiles.get("district_name"))
    section_profiles["barrio_name"] = coalesce_strings(section_profiles.get("barrio_name_panel"), section_profiles.get("barrio_name"))
    section_profiles["district_code"] = coalesce_strings(section_profiles.get("district_code_panel"), section_profiles.get("district_code"))
    section_profiles["barrio_code"] = coalesce_strings(section_profiles.get("barrio_code_panel"), section_profiles.get("barrio_code"))

    section_profiles["first_seen_period"] = latest_period or reference["latest_period"]
    section_profiles["h3_cell_start"] = latlon_to_h3(section_profiles["centroid_lat"], section_profiles["centroid_lon"], resolution=10)
    section_profiles["missing_h3"] = 0.0
    section_profiles["n_divisions_start"] = 1.0
    section_profiles["n_epigrafes_start"] = 1.0
    section_profiles["n_activity_categories_start"] = 1.0

    section_profiles["renta_effective_eur"] = section_profiles["renta_effective_eur"]
    section_profiles["renta_carry_forward_years"] = pd.to_numeric(section_profiles.get("renta_carry_forward_years"), errors="coerce").fillna(0.0)
    section_profiles["padron_lag_months_start"] = pd.to_numeric(section_profiles.get("padron_lag_months_start"), errors="coerce")
    section_profiles["geometry_available_start"] = pd.to_numeric(section_profiles.get("geometry_available_start"), errors="coerce")

    metro_input = section_profiles[["centroid_lat", "centroid_lon"]].rename(
        columns={"centroid_lat": "lat_wgs84_start", "centroid_lon": "lon_wgs84_start"}
    )
    metro_features = compute_metro_features(metro_input, include_names=True)
    section_profiles = pd.concat([section_profiles.reset_index(drop=True), metro_features.reset_index(drop=True)], axis=1)

    fill_section_reference_holes(section_profiles)
    harmonize_section_commercial_context(section_profiles)
    fill_avisos_holes(section_profiles)
    for column in ["top_avisos_district_categories", "top_avisos_barrio_categories"]:
        values = section_profiles[column] if column in section_profiles.columns else pd.Series([None] * len(section_profiles), index=section_profiles.index, dtype=object)
        section_profiles[column] = [value if isinstance(value, list) else [] for value in values]

    scores = score_entity_frame(section_profiles, reference=reference)
    section_profiles = pd.concat([section_profiles.reset_index(drop=True), scores.reset_index(drop=True)], axis=1)
    section_profiles = add_section_rankings(section_profiles)
    section_profiles["opportunity_tier"] = section_profiles["risk_percentile"].map(opportunity_tier_from_percentile).astype("string")
    section_profiles["top_activities"] = build_predictive_activity_recommendations(section_profiles, activity_context)
    section_profiles["best_activity_label"] = section_profiles["top_activities"].map(
        lambda rows: rows[0]["display_label"] if rows else None
    )
    section_profiles["best_activity_risk"] = section_profiles["top_activities"].map(
        lambda rows: rows[0]["activity_risk"] if rows else None
    )
    section_profiles["best_activity_survival_24m"] = section_profiles["top_activities"].map(
        lambda rows: rows[0]["survival_24m"] if rows else None
    )

    print("  Enriching sections with external data...")
    enrich_frame_with_external_district_data(
        section_profiles, "district_code",
        external["vulnerability"], external["inspecciones"], external["panel"],
    )
    enrich_frame_with_facilities(section_profiles, "centroid_lat", "centroid_lon", external["equipment"])
    print(f"  Sections enriched: {len(section_profiles):,}")

    geojson = build_sections_geojson(section_profiles)
    return section_profiles, geojson


def score_selected_available_listings(
    selected_listings: pd.DataFrame,
    section_profiles: pd.DataFrame,
    reference: dict[str, object],
    external: dict[str, object],
) -> pd.DataFrame:
    required_columns = [
        "section_key",
        "district_code",
        "district_name",
        "barrio_code",
        "barrio_name",
        "renta_effective_eur",
        "renta_reference_year",
        "renta_granularity_used",
        "renta_outlier_adjusted",
        "renta_carry_forward_years",
        "share_foreign_start",
        "share_age_00_14_start",
        "share_age_15_29_start",
        "share_age_30_44_start",
        "share_age_45_64_start",
        "share_age_65_plus_start",
        "share_male_start",
        "age_mean_start",
        "total_population_start",
        "population_density_km2_start",
        "padron_lag_months_start",
        "geometry_available_start",
        "metro_nearest_name_start",
        "metro_nearest_station_name_start",
        "metro_station_count_500m_start",
        "metro_station_count_1000m_start",
        "metro_access_names_500m_start",
        "metro_access_names_1000m_start",
        "metro_station_names_500m_start",
        "metro_station_names_1000m_start",
        "n_divisions_start",
        "n_epigrafes_start",
        "n_activity_categories_start",
        "section_local_count_start",
        "section_unique_division_count_start",
        "section_unique_activity_category_count_start",
        "section_single_division_share_start",
        "section_same_division_local_count_start",
        "section_same_division_share_start",
        "section_same_activity_category_local_count_start",
        "section_same_activity_category_share_start",
        "section_entry_count_3m_start",
        "section_entry_count_6m_start",
        "section_entry_count_12m_start",
        "section_exit_count_3m_start",
        "section_exit_count_6m_start",
        "section_exit_count_12m_start",
        "section_entry_rate_12m_start",
        "section_exit_rate_12m_start",
        "section_net_flow_12m_start",
        "section_turnover_rate_12m_start",
        "section_division_hhi_start",
        "section_division_top_share_start",
        "section_activity_category_hhi_start",
        "section_activity_category_top_share_start",
        "section_local_count_delta_12m_start",
        "total_population_delta_12m_start",
        "share_foreign_delta_12m_start",
        "share_age_15_29_delta_12m_start",
        "population_density_km2_delta_12m_start",
        "renta_best_eur_delta_12m_start",
        "avisos_district_per_1000_prev_year",
        "avisos_barrio_per_1000_prev_year",
        "avisos_barrio_share_of_district_prev_year",
        "top_avisos_district_categories",
        "top_avisos_barrio_categories",
        "city_rank",
        "city_total_sections",
        "district_rank",
        "district_total_sections",
        "barrio_rank",
        "barrio_total_sections",
        "top_activities",
        "best_activity_label",
        "best_activity_risk",
        "best_activity_survival_24m",
        "vulnerabilidad_global",
        "vulnerabilidad_global_media_ciudad",
        "vulnerabilidad_esferas",
        "inspecciones_distrito_total",
        "inspecciones_ciudad_media",
        "inspecciones_top_epigrafes",
        "indicadores_distrito",
        "facilities_tier",
        "facilities_200m",
        "facilities_500m",
        "facilities_1000m",
        "facilities_by_category",
    ]
    enriched = selected_listings.merge(section_profiles[required_columns], how="left", on="section_key", suffixes=("", "_section"))
    enriched["district_code"] = coalesce_strings(enriched.get("district_code_section"), enriched.get("district_code"))
    enriched["district_name"] = coalesce_strings(enriched.get("district_name_section"), enriched.get("district_name"))
    enriched["barrio_code"] = coalesce_strings(enriched.get("barrio_code_section"), enriched.get("barrio_code"))
    enriched["barrio_name"] = coalesce_strings(enriched.get("barrio_name_section"), enriched.get("barrio_name"))
    enriched["first_seen_period"] = section_profiles["first_seen_period"].iloc[0] if not section_profiles.empty else reference["latest_period"]
    enriched["h3_cell_start"] = enriched.get("h3_cell", pd.Series(pd.NA, index=enriched.index)).astype("string")

    metro_input = enriched[["lat_wgs84", "lon_wgs84"]].rename(columns={"lat_wgs84": "lat_wgs84_start", "lon_wgs84": "lon_wgs84_start"})
    metro_features = compute_metro_features(metro_input, include_names=True)
    for column in [
        "metro_distance_m_start",
        "metro_access_count_500m_start",
        "metro_access_count_1000m_start",
        "metro_station_count_500m_start",
        "metro_station_count_1000m_start",
        "missing_metro_distance_start",
    ]:
        enriched[column] = pd.to_numeric(metro_features[column], errors="coerce")
    nearest_name_values = metro_features["metro_nearest_name_start"] if "metro_nearest_name_start" in metro_features.columns else pd.Series(pd.NA, index=enriched.index)
    enriched["metro_nearest_name_start"] = nearest_name_values.astype("string")
    nearest_station_name_values = metro_features["metro_nearest_station_name_start"] if "metro_nearest_station_name_start" in metro_features.columns else pd.Series(pd.NA, index=enriched.index)
    enriched["metro_nearest_station_name_start"] = nearest_station_name_values.astype("string")
    for column in [
        "metro_access_names_500m_start",
        "metro_access_names_1000m_start",
        "metro_station_names_500m_start",
        "metro_station_names_1000m_start",
    ]:
        values = metro_features[column] if column in metro_features.columns else pd.Series([None] * len(enriched), index=enriched.index, dtype=object)
        enriched[column] = [value if isinstance(value, list) else [] for value in values]
    for column in ["top_avisos_district_categories", "top_avisos_barrio_categories"]:
        values = enriched[column] if column in enriched.columns else pd.Series([None] * len(enriched), index=enriched.index, dtype=object)
        enriched[column] = [value if isinstance(value, list) else [] for value in values]

    enrich_frame_with_facilities(enriched, "lat_wgs84", "lon_wgs84", external["equipment"])

    scores = score_entity_frame(enriched, reference=reference)
    enriched = pd.concat([enriched.reset_index(drop=True), scores.reset_index(drop=True)], axis=1)
    enriched["opportunity_tier"] = enriched["risk_percentile"].map(opportunity_tier_from_percentile).astype("string")
    return enriched.sort_values(["operation", "risk_score", "district_name", "barrio_name", "listing_id"], na_position="last").reset_index(drop=True)


def score_entity_frame(frame: pd.DataFrame, *, reference: dict[str, object]) -> pd.DataFrame:
    features = build_feature_frame(frame, fill_missing=False)
    features = features.reindex(columns=reference["feature_columns"]) 
    features = features.fillna(reference["feature_fill_values"])
    features = features.fillna(0.0)
    scores = compute_linear_risk_score(features, reference_means=reference["feature_means"], reference_stds=reference["feature_stds"])
    percentiles = scores.map(lambda value: compute_score_percentile(reference["sorted_scores"], value))
    calibration_rows = [lookup_calibration(reference["calibration"], float(score)) for score in scores]
    return pd.DataFrame(
        {
            "risk_score": scores.astype(float),
            "risk_percentile": percentiles.astype(float),
            "expected_survival_12m": [row["survival_12m"] for row in calibration_rows],
            "expected_survival_24m": [row["survival_24m"] for row in calibration_rows],
            "calibration_bucket": [row["bucket_label"] for row in calibration_rows],
        },
        index=frame.index,
    )


def build_section_feature_reference(
    dataset: pd.DataFrame,
    *,
    value_columns: list[str] | None = None,
) -> pd.DataFrame:
    normalized = dataset.copy()
    normalized["section_key_start"] = normalize_section_key_series(
        normalized.get("section_key_start", pd.Series(pd.NA, index=normalized.index))
    ).astype("string")
    normalized["district_code_start"] = normalized.get("district_code_start", pd.Series(pd.NA, index=normalized.index)).map(
        lambda value: normalize_admin_code(value, width=2)
    ).astype("string")
    normalized["barrio_code_start"] = normalized.get("barrio_code_start", pd.Series(pd.NA, index=normalized.index)).map(
        lambda value: normalize_admin_code(value, width=3)
    ).astype("string")

    value_columns = value_columns or SECTION_PROFILE_MEDIAN_COLUMNS
    available_value_columns = [column for column in value_columns if column in normalized.columns]
    scoped = normalized[["section_key_start", "district_code_start", "barrio_code_start", *available_value_columns]].copy()
    if "first_seen_date" in normalized.columns:
        scoped["first_seen_date"] = pd.to_datetime(normalized["first_seen_date"], errors="coerce")
    else:
        scoped["first_seen_date"] = pd.to_datetime(
            normalized.get("first_seen_period", pd.Series(pd.NA, index=normalized.index)).astype("string") + "-01",
            errors="coerce",
        )
    scoped = scoped[scoped["section_key_start"].notna()].copy()

    recent_cutoff = scoped["first_seen_date"].max() - pd.DateOffset(months=RECENT_LOOKBACK_MONTHS)
    recent = scoped[scoped["first_seen_date"].ge(recent_cutoff)].copy() if scoped["first_seen_date"].notna().any() else scoped.iloc[0:0].copy()

    history_medians = scoped.groupby("section_key_start", dropna=False)[available_value_columns].median(numeric_only=True)
    recent_medians = recent.groupby("section_key_start", dropna=False)[available_value_columns].median(numeric_only=True)
    combined = history_medians.copy()
    combined.update(recent_medians)

    identity = scoped.groupby("section_key_start", dropna=False).agg(
        district_code=("district_code_start", first_valid),
        barrio_code=("barrio_code_start", first_valid),
    )
    combined = identity.join(combined, how="outer").reset_index().rename(columns={"section_key_start": "section_key"})
    fill_section_reference_holes(combined, district_col="district_code", barrio_col="barrio_code", columns=value_columns)
    harmonize_section_commercial_context(combined)
    return combined


def load_latest_section_panel(path: Path) -> tuple[pd.DataFrame, str | None]:
    panel = pd.read_csv(
        path,
        usecols=[
            "target_period",
            "target_date",
            "section_key",
            "district_code",
            "district_name",
            "barrio_code",
            "barrio_name",
            "total_population",
            "age_mean",
            "renta_best_eur",
            "renta_lag_years",
            "renta_reference_year",
            "renta_granularity_used",
            "renta_outlier_adjusted",
            "share_foreign",
            "share_male",
            "share_age_00_14",
            "share_age_15_29",
            "share_age_30_44",
            "share_age_45_64",
            "share_age_65_plus",
            "padron_lag_months",
            "geometry_available",
            "population_density_km2",
        ],
        dtype={"target_period": "string", "section_key": "string", "district_code": "string", "district_name": "string", "barrio_code": "string", "barrio_name": "string"},
        low_memory=False,
    )
    panel["section_key"] = normalize_section_key_series(panel["section_key"]).astype("string")
    panel["district_code"] = panel["district_code"].map(lambda value: normalize_admin_code(value, width=2)).astype("string")
    panel["barrio_code"] = panel["barrio_code"].map(lambda value: normalize_admin_code(value, width=3)).astype("string")
    panel["district_name"] = panel["district_name"].map(clean_place_name).astype("string")
    panel["barrio_name"] = panel["barrio_name"].map(clean_place_name).astype("string")
    panel["target_date"] = pd.to_datetime(panel["target_date"], errors="coerce")
    panel["renta_reference_year"] = pd.to_numeric(panel.get("renta_reference_year"), errors="coerce")
    panel["renta_reference_year"] = panel["renta_reference_year"].fillna(
        panel["target_date"].dt.year - pd.to_numeric(panel.get("renta_lag_years"), errors="coerce")
    )
    panel["renta_granularity_used"] = panel.get("renta_granularity_used", pd.Series(pd.NA, index=panel.index)).astype("string")
    renta_outlier_raw = panel.get("renta_outlier_adjusted", pd.Series(False, index=panel.index))
    panel["renta_outlier_adjusted"] = renta_outlier_raw.map(
        lambda value: str(value).strip().lower() in {"1", "true", "yes"} if pd.notna(value) else False
    ).astype(bool)

    previous = panel[["section_key", "target_date", "total_population", "share_foreign", "share_age_15_29", "population_density_km2", "renta_best_eur"]].copy()
    previous["target_date"] = previous["target_date"] + pd.DateOffset(months=12)
    previous = previous.rename(
        columns={
            "total_population": "total_population_prev12",
            "share_foreign": "share_foreign_prev12",
            "share_age_15_29": "share_age_15_29_prev12",
            "population_density_km2": "population_density_km2_prev12",
            "renta_best_eur": "renta_best_eur_prev12",
        }
    )

    latest = panel.sort_values(["section_key", "target_date"]).groupby("section_key", dropna=False).tail(1).copy()
    latest = latest.merge(previous, how="left", on=["section_key", "target_date"])

    latest["renta_effective_eur"] = pd.to_numeric(latest["renta_best_eur"], errors="coerce")
    district_median = latest.groupby("district_code", dropna=False)["renta_effective_eur"].median(numeric_only=True)
    city_median = float(latest["renta_effective_eur"].median()) if latest["renta_effective_eur"].notna().any() else 0.0
    latest["renta_effective_eur"] = latest["renta_effective_eur"].fillna(latest["district_code"].map(district_median)).fillna(city_median)
    # For current opportunity scoring, stale public updates should not inflate model risk.
    latest["renta_carry_forward_years"] = 0.0

    latest["total_population_delta_12m_start"] = pd.to_numeric(latest["total_population"], errors="coerce") - pd.to_numeric(
        latest["total_population_prev12"], errors="coerce"
    )
    latest["share_foreign_delta_12m_start"] = pd.to_numeric(latest["share_foreign"], errors="coerce") - pd.to_numeric(
        latest["share_foreign_prev12"], errors="coerce"
    )
    latest["share_age_15_29_delta_12m_start"] = pd.to_numeric(latest["share_age_15_29"], errors="coerce") - pd.to_numeric(
        latest["share_age_15_29_prev12"], errors="coerce"
    )
    latest["population_density_km2_delta_12m_start"] = pd.to_numeric(latest["population_density_km2"], errors="coerce") - pd.to_numeric(
        latest["population_density_km2_prev12"], errors="coerce"
    )
    latest["renta_best_eur_delta_12m_start"] = pd.to_numeric(latest["renta_best_eur"], errors="coerce") - pd.to_numeric(
        latest["renta_best_eur_prev12"], errors="coerce"
    )

    latest = latest.rename(
        columns={
            "share_foreign": "share_foreign_start",
            "share_male": "share_male_start",
            "share_age_00_14": "share_age_00_14_start",
            "share_age_15_29": "share_age_15_29_start",
            "share_age_30_44": "share_age_30_44_start",
            "share_age_45_64": "share_age_45_64_start",
            "share_age_65_plus": "share_age_65_plus_start",
            "age_mean": "age_mean_start",
            "total_population": "total_population_start",
            "population_density_km2": "population_density_km2_start",
            "padron_lag_months": "padron_lag_months_start",
            "geometry_available": "geometry_available_start",
            "district_code": "district_code_panel",
            "district_name": "district_name_panel",
            "barrio_code": "barrio_code_panel",
            "barrio_name": "barrio_name_panel",
        }
    )

    latest["padron_lag_months_start"] = 0.0

    latest_period = str(latest["target_period"].astype("string").dropna().max()) if not latest.empty else None
    return latest, latest_period


def build_latest_avisos_lookup(section_panel_csv: Path) -> pd.DataFrame:
    raw_manifest = load_raw_manifest()
    avisos = build_avisos_yearly_features(raw_manifest=raw_manifest, section_panel_csv=section_panel_csv)
    if avisos.empty:
        return pd.DataFrame(columns=[
            "district_code",
            "barrio_code",
            "avisos_district_per_1000_prev_year",
            "avisos_barrio_per_1000_prev_year",
            "avisos_barrio_share_of_district_prev_year",
            "top_avisos_district_categories",
            "top_avisos_barrio_categories",
        ])

    avisos["district_code"] = avisos["district_code"].map(lambda value: normalize_admin_code(value, width=2)).astype("string")
    avisos["barrio_code"] = [
        normalize_section_barrio_code(district_code, barrio_code)
        for district_code, barrio_code in zip(avisos["district_code"], avisos["barrio_code"])
    ]
    for column in [
        "avisos_district_per_1000_prev_year",
        "avisos_barrio_per_1000_prev_year",
        "avisos_barrio_share_of_district_prev_year",
    ]:
        avisos[column] = pd.to_numeric(avisos[column], errors="coerce")

    valid_mask = avisos[[
        "avisos_district_per_1000_prev_year",
        "avisos_barrio_per_1000_prev_year",
    ]].notna().any(axis=1)
    if not bool(valid_mask.any()):
        return pd.DataFrame(columns=[
            "district_code",
            "barrio_code",
            "avisos_district_per_1000_prev_year",
            "avisos_barrio_per_1000_prev_year",
            "avisos_barrio_share_of_district_prev_year",
            "top_avisos_district_categories",
            "top_avisos_barrio_categories",
        ])

    latest_year = int(pd.to_numeric(avisos.loc[valid_mask, "avisos_year"], errors="coerce").dropna().max())
    latest = avisos[pd.to_numeric(avisos["avisos_year"], errors="coerce").eq(latest_year)].copy()
    district_categories, barrio_categories = build_latest_avisos_category_lookups(raw_manifest=raw_manifest, latest_year=latest_year)
    latest = latest.merge(district_categories, how="left", on=["district_code"])
    latest = latest.merge(barrio_categories, how="left", on=["district_code", "barrio_code"])
    for column in ["top_avisos_district_categories", "top_avisos_barrio_categories"]:
        values = latest[column] if column in latest.columns else pd.Series([None] * len(latest), index=latest.index, dtype=object)
        latest[column] = [value if isinstance(value, list) else [] for value in values]
    return latest[[
        "district_code",
        "barrio_code",
        "avisos_district_per_1000_prev_year",
        "avisos_barrio_per_1000_prev_year",
        "avisos_barrio_share_of_district_prev_year",
        "top_avisos_district_categories",
        "top_avisos_barrio_categories",
    ]]


def build_latest_avisos_category_lookups(*, raw_manifest: pd.DataFrame, latest_year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = raw_manifest[
        (raw_manifest["source_name"] == "avisos")
        & (raw_manifest["status"] == "selected")
        & raw_manifest["selected_relative_path"].notna()
    ].copy()
    selected["period_numeric"] = pd.to_numeric(selected["period"], errors="coerce")
    latest_rows = selected[selected["period_numeric"].eq(latest_year)].copy()
    if latest_rows.empty:
        return (
            pd.DataFrame(columns=["district_code", "top_avisos_district_categories"]),
            pd.DataFrame(columns=["district_code", "barrio_code", "top_avisos_barrio_categories"]),
        )

    category_frames: list[pd.DataFrame] = []
    for row in latest_rows.sort_values("selected_relative_path").itertuples(index=False):
        frame, _ = read_delimited_file(PROJECT_ROOT / "storage" / "raw" / str(row.selected_relative_path))
        normalized = normalize_avisos_category_frame(frame)
        if not normalized.empty:
            category_frames.append(normalized)

    if not category_frames:
        return (
            pd.DataFrame(columns=["district_code", "top_avisos_district_categories"]),
            pd.DataFrame(columns=["district_code", "barrio_code", "top_avisos_barrio_categories"]),
        )

    latest_categories = pd.concat(category_frames, ignore_index=True)
    district_lookup = build_avisos_top_category_lookup(
        latest_categories.dropna(subset=["district_code"]),
        zone_cols=["district_code"],
        output_col="top_avisos_district_categories",
    )
    barrio_lookup = build_avisos_top_category_lookup(
        latest_categories.dropna(subset=["district_code", "barrio_code"]),
        zone_cols=["district_code", "barrio_code"],
        output_col="top_avisos_barrio_categories",
    )
    return district_lookup, barrio_lookup


def normalize_avisos_category_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [str(column).strip().upper() for column in normalized.columns]

    district_code = normalized.get("DISTRITO_ID", pd.Series(pd.NA, index=normalized.index)).map(
        lambda value: normalize_admin_code(value, width=2)
    ).astype("string")
    barrio_source = normalized.get("BARRIO_ID", pd.Series(pd.NA, index=normalized.index))
    barrio_code = pd.Series(
        [normalize_section_barrio_code(district, barrio) for district, barrio in zip(district_code, barrio_source)],
        index=normalized.index,
        dtype="string",
    )

    if "CATEGORIA_NIVEL1" in normalized.columns:
        category_source = normalized["CATEGORIA_NIVEL1"]
    elif "SECCION" in normalized.columns:
        category_source = normalized["SECCION"]
    elif "CATEGORIA_NIVEL2" in normalized.columns:
        category_source = normalized["CATEGORIA_NIVEL2"]
    elif "ANOMALIA" in normalized.columns:
        category_source = normalized["ANOMALIA"]
    else:
        return pd.DataFrame(columns=["district_code", "barrio_code", "category_label"])

    category_label = category_source.astype("string").map(clean_avisos_category_label).astype("string")
    return pd.DataFrame(
        {
            "district_code": district_code,
            "barrio_code": barrio_code,
            "category_label": category_label,
        }
    ).dropna(subset=["district_code", "category_label"])


def build_avisos_top_category_lookup(frame: pd.DataFrame, *, zone_cols: list[str], output_col: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=[*zone_cols, output_col])

    grouped = (
        frame.dropna(subset=[*zone_cols, "category_label"])
        .groupby([*zone_cols, "category_label"], dropna=False)
        .size()
        .rename("count")
        .reset_index()
    )
    if grouped.empty:
        return pd.DataFrame(columns=[*zone_cols, output_col])

    totals = grouped.groupby(zone_cols, dropna=False)["count"].sum().rename("zone_total").reset_index()
    grouped = grouped.merge(totals, how="left", on=zone_cols)
    grouped["share_of_zone"] = grouped["count"] / grouped["zone_total"].replace({0: pd.NA})
    grouped = grouped.sort_values(
        [*zone_cols, "count", "share_of_zone", "category_label"],
        ascending=[*[True] * len(zone_cols), False, False, True],
    )

    rows: list[dict[str, object]] = []
    for zone_key, part in grouped.groupby(zone_cols, dropna=False, sort=False):
        zone_values = zone_key if isinstance(zone_key, tuple) else (zone_key,)
        payload = [
            {
                "rank": rank,
                "label": str(row.category_label),
                "count": int(row.count),
                "share_of_zone": serialize_probability(getattr(row, "share_of_zone", None)),
            }
            for rank, row in enumerate(part.head(AVISOS_TOP_CATEGORY_COUNT).itertuples(index=False), start=1)
        ]
        zone_payload = {column: value for column, value in zip(zone_cols, zone_values)}
        zone_payload[output_col] = payload
        rows.append(zone_payload)

    return pd.DataFrame(rows, columns=[*zone_cols, output_col])


def load_section_geometry() -> pd.DataFrame:
    sections = load_section_geodataframe().copy()
    sections["section_key"] = normalize_section_key_series(sections["COD_SECCIO"]).astype("string")
    sections["district_code"] = sections["COD_DIS"].astype("string").str.strip().replace({"": pd.NA}).str.zfill(2)
    sections["district_name"] = sections["NOM_DIS"].astype("string").map(clean_place_name)
    sections["barrio_code"] = sections["COD_BAR"].astype("string").str.strip().replace({"": pd.NA}).str.zfill(3)
    sections["barrio_name"] = sections["NOM_BAR"].astype("string").map(clean_place_name)
    sections = sections[["section_key", "district_code", "district_name", "barrio_code", "barrio_name", "geometry"]].dropna(subset=["section_key", "geometry"])
    sections = sections.to_crs("EPSG:25830")
    sections = sections.dissolve(
        by="section_key",
        aggfunc={
            "district_code": "first",
            "district_name": "first",
            "barrio_code": "first",
            "barrio_name": "first",
        },
    ).reset_index()
    sections["geometry"] = sections.geometry.simplify(SECTION_SIMPLIFY_TOLERANCE_M, preserve_topology=True)
    sections["centroid_geometry"] = sections.geometry.centroid
    centroids = sections.copy().set_geometry("centroid_geometry").to_crs("EPSG:4326")
    sections = sections.to_crs("EPSG:4326")
    sections["centroid_lat"] = centroids.geometry.y
    sections["centroid_lon"] = centroids.geometry.x
    return sections[["section_key", "district_code", "district_name", "barrio_code", "barrio_name", "centroid_lat", "centroid_lon", "geometry"]]


def build_activity_prediction_context() -> dict[str, object]:
    activity_abt = pd.read_csv(ACTIVITY_SURVIVAL_ABT_CSV, low_memory=False)
    macro_catalog = load_activity_macro_catalog(ACTIVITY_MACRO_TAXONOMY_CSV)
    district_rows = load_activity_evidence_rows(DISTRICT_CATEGORY_CSV, zone_level="district")
    barrio_rows = load_activity_evidence_rows(BARRIO_CATEGORY_CSV, zone_level="barrio")
    scorer = fit_activity_survival_cox_scorer(
        abt=activity_abt,
        feature_profile="full",
    )
    return {
        "macro_catalog": macro_catalog,
        "district_evidence": build_macro_zone_evidence(district_rows, zone_level="district"),
        "barrio_evidence": build_macro_zone_evidence(barrio_rows, zone_level="barrio"),
        "city_evidence": build_city_macro_evidence(district_rows),
        "section_macro_reference": build_section_macro_activity_reference(activity_abt),
        "calibration": build_activity_score_calibration(activity_abt, scorer),
        "scorer": scorer,
    }


def load_activity_macro_catalog(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    frame["investable"] = frame["investable"].fillna(False).astype(bool)
    frame["source_rows"] = pd.to_numeric(frame.get("source_rows"), errors="coerce").fillna(0.0)
    frame["macro_category_code"] = frame.get("macro_category_code", pd.Series(pd.NA, index=frame.index)).astype("string")
    frame["macro_category_name"] = frame.get("macro_category_name", pd.Series(pd.NA, index=frame.index)).astype("string")
    frame["macro_category_definition"] = frame.get("macro_category_definition", pd.Series(pd.NA, index=frame.index)).astype("string")
    frame["web_supercategory"] = frame.get("web_supercategory", pd.Series(pd.NA, index=frame.index)).astype("string")
    frame["web_category"] = frame.get("web_category", pd.Series(pd.NA, index=frame.index)).astype("string")

    investable = frame[
        frame["investable"]
        & frame["macro_category_code"].notna()
        & frame["macro_category_code"].ne("non_priorizable")
    ].copy()
    investable = investable.sort_values(["macro_category_code", "source_rows"], ascending=[True, False])
    catalog = investable.drop_duplicates(subset=["macro_category_code"], keep="first").copy()
    catalog["display_label"] = catalog["macro_category_name"].fillna(catalog["web_category"]).fillna(catalog["macro_category_code"])
    return catalog[[
        "macro_category_code",
        "display_label",
        "web_supercategory",
        "web_category",
        "macro_category_name",
        "macro_category_definition",
    ]].reset_index(drop=True)


def load_activity_evidence_rows(path: Path, *, zone_level: str) -> pd.DataFrame:
    frame = pd.read_csv(
        path,
        usecols=["zone_code", "zone_name", "web_supercategory", "web_category", "display_label", "n_locales", "n_events"],
        low_memory=False,
    )
    frame["zone_name"] = frame["zone_name"].map(clean_place_name).astype("string")
    frame["display_label"] = frame["display_label"].astype("string")
    frame["web_supercategory"] = frame["web_supercategory"].astype("string")
    frame["web_category"] = frame["web_category"].astype("string")
    frame["n_locales"] = pd.to_numeric(frame["n_locales"], errors="coerce").fillna(0.0)
    frame["n_events"] = pd.to_numeric(frame["n_events"], errors="coerce").fillna(0.0)

    if zone_level == "district":
        frame["zone_code"] = frame["zone_code"].map(lambda value: normalize_admin_code(value, width=2)).astype("string")
        frame["zone_lookup_key"] = frame["zone_code"]
    else:
        frame["zone_code"] = frame["zone_code"].astype("string")
        frame["zone_lookup_key"] = frame["zone_name"].map(normalize_zone_lookup_key).astype("string")

    decisions = [
        classify_macro_category(
            display_label=str(display_label or ""),
            web_category=str(web_category or ""),
            web_supercategory=str(web_supercategory or ""),
            investable=True,
        )
        for display_label, web_category, web_supercategory in zip(
            frame["display_label"],
            frame["web_category"],
            frame["web_supercategory"],
        )
    ]
    frame["macro_category_code"] = [decision.macro_category_code for decision in decisions]
    frame = frame[frame["macro_category_code"].astype("string").ne("non_priorizable")].copy()
    return frame[["zone_code", "zone_name", "zone_lookup_key", "macro_category_code", "n_locales", "n_events"]]


def build_macro_zone_evidence(frame: pd.DataFrame, *, zone_level: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["zone_lookup_key", "macro_category_code", "n_locales", "n_events", "event_rate", "macro_share", "confidence_tier", "supported_for_stats"])

    grouped = frame.groupby(["zone_lookup_key", "macro_category_code"], dropna=False).agg(
        zone_code=("zone_code", first_valid),
        zone_name=("zone_name", first_valid),
        n_locales=("n_locales", "sum"),
        n_events=("n_events", "sum"),
    ).reset_index()
    grouped["event_rate"] = grouped["n_events"] / grouped["n_locales"].replace({0.0: np.nan})
    grouped["macro_share"] = grouped["n_locales"] / grouped.groupby("zone_lookup_key", dropna=False)["n_locales"].transform("sum").replace({0.0: np.nan})
    grouped["confidence_tier"] = [
        confidence_tier(n_locales=int(round(n_locales)), n_events=int(round(n_events)), zone_level=zone_level)
        for n_locales, n_events in zip(grouped["n_locales"], grouped["n_events"])
    ]
    grouped["supported_for_stats"] = [
        activity_evidence_supported(n_locales=float(n_locales), n_events=float(n_events), zone_level=zone_level)
        for n_locales, n_events in zip(grouped["n_locales"], grouped["n_events"])
    ]
    return grouped


def build_city_macro_evidence(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["macro_category_code", "n_locales", "n_events", "event_rate", "macro_share", "confidence_tier", "supported_for_stats"])

    grouped = frame.groupby(["macro_category_code"], dropna=False).agg(
        n_locales=("n_locales", "sum"),
        n_events=("n_events", "sum"),
    ).reset_index()
    grouped["event_rate"] = grouped["n_events"] / grouped["n_locales"].replace({0.0: np.nan})
    grouped["macro_share"] = grouped["n_locales"] / grouped["n_locales"].sum()
    grouped["confidence_tier"] = grouped["n_locales"].map(lambda value: city_confidence_tier(float(value)))
    grouped["supported_for_stats"] = grouped["n_locales"].ge(ACTIVITY_CITY_MIN_LOCALES)
    return grouped


def build_predictive_activity_recommendations(
    section_profiles: pd.DataFrame,
    context: dict[str, object],
    *,
    max_rows: int = ACTIVITY_RECOMMENDATION_COUNT,
) -> pd.Series:
    if section_profiles.empty:
        return pd.Series([[] for _ in range(len(section_profiles))], index=section_profiles.index, dtype=object)

    macro_catalog = context["macro_catalog"]
    scorer = context["scorer"]
    candidate_base = section_profiles[ACTIVITY_SECTION_SCORING_COLUMNS].copy()
    candidate_base["barrio_lookup_key"] = candidate_base["barrio_name"].map(normalize_zone_lookup_key).astype("string")

    candidates = candidate_base.merge(macro_catalog, how="cross")
    candidates["activity_category_code_start"] = candidates["macro_category_code"].astype("string")
    candidates["n_divisions_start"] = 1.0
    candidates["n_epigrafes_start"] = 1.0
    candidates["n_activity_categories_start"] = 1.0
    candidates = candidates.merge(
        context["section_macro_reference"],
        how="left",
        on=["section_key", "macro_category_code"],
    )
    candidates = candidates.merge(
        context["barrio_evidence"][ ["zone_lookup_key", "macro_category_code", "macro_share"] ].rename(
            columns={"zone_lookup_key": "barrio_lookup_key", "macro_share": "barrio_macro_share"}
        ),
        how="left",
        on=["barrio_lookup_key", "macro_category_code"],
    )
    candidates = candidates.merge(
        context["district_evidence"][ ["zone_lookup_key", "macro_category_code", "macro_share"] ].rename(
            columns={"zone_lookup_key": "district_code", "macro_share": "district_macro_share"}
        ),
        how="left",
        on=["district_code", "macro_category_code"],
    )
    candidates = candidates.merge(
        context["city_evidence"][ ["macro_category_code", "macro_share"] ].rename(columns={"macro_share": "city_macro_share"}),
        how="left",
        on=["macro_category_code"],
    )
    zone_macro_share = (
        pd.to_numeric(candidates.get("barrio_macro_share"), errors="coerce")
        .combine_first(pd.to_numeric(candidates.get("district_macro_share"), errors="coerce"))
        .combine_first(pd.to_numeric(candidates.get("city_macro_share"), errors="coerce"))
    )
    section_local_count = pd.to_numeric(candidates.get("section_local_count_start"), errors="coerce")
    candidates["section_same_activity_category_local_count_start"] = pd.to_numeric(
        candidates.get("macro_section_same_activity_category_local_count_start"),
        errors="coerce",
    ).combine_first((section_local_count * zone_macro_share).clip(lower=0.0))
    candidates["section_same_activity_category_share_start"] = pd.to_numeric(
        candidates.get("macro_section_same_activity_category_share_start"),
        errors="coerce",
    ).combine_first(zone_macro_share)

    scored = scorer.score_frame(candidates, horizons=(12.0, 24.0))
    candidates = pd.concat([candidates.reset_index(drop=True), scored.reset_index(drop=True)], axis=1)
    calibration_rows = [lookup_calibration(context["calibration"], float(score)) for score in candidates["risk_cox"]]
    candidates["survival_12m"] = [row["survival_12m"] for row in calibration_rows]
    candidates["survival_24m"] = [row["survival_24m"] for row in calibration_rows]
    candidates = attach_activity_evidence(candidates, context=context)
    source_penalty = candidates["source_zone"].map(ACTIVITY_SOURCE_SCORE_PENALTIES).fillna(ACTIVITY_SOURCE_SCORE_PENALTIES["city"])
    unsupported_penalty = (~candidates["supported_for_stats"].fillna(False)).astype(float) * UNSUPPORTED_ACTIVITY_PENALTY
    candidates["activity_rank_score"] = (
        pd.to_numeric(candidates["activity_context_index"], errors="coerce")
        + ACTIVITY_SOURCE_PENALTY_MULTIPLIER * pd.to_numeric(source_penalty, errors="coerce")
        + ACTIVITY_UNSUPPORTED_PENALTY_MULTIPLIER * unsupported_penalty
    )
    candidates["activity_risk"] = pd.to_numeric(candidates["activity_rank_score"], errors="coerce")
    candidates["supported_rank"] = (~candidates["supported_for_stats"].fillna(False)).astype(int)
    candidates["source_priority"] = candidates["source_zone"].map({"barrio": 0, "district": 1, "city": 2}).fillna(3).astype(int)

    top = select_diversified_activity_rows(candidates, max_rows=max_rows)
    top["rank"] = top.groupby("section_key", dropna=False).cumcount() + 1

    payload_by_section: dict[str, list[dict[str, object]]] = {}
    for section_key, part in top.groupby("section_key", dropna=False):
        rows: list[dict[str, object]] = []
        for row in part.itertuples(index=False):
            rows.append(
                {
                    "rank": int(row.rank),
                    "source_zone": str(getattr(row, "source_zone", "city") or "city"),
                    "display_label": str(getattr(row, "display_label", "") or ""),
                    "web_supercategory": str(getattr(row, "web_supercategory", "") or ""),
                    "web_category": str(getattr(row, "web_category", "") or ""),
                    "event_rate": serialize_probability(getattr(row, "event_rate", None)),
                    "activity_risk": serialize_probability(getattr(row, "activity_risk", None)),
                    "survival_12m": serialize_probability(getattr(row, "survival_12m", None)),
                    "survival_24m": serialize_probability(getattr(row, "survival_24m", None)),
                    "n_locales": int(round(float(getattr(row, "n_locales", 0) or 0))),
                    "confidence_tier": str(getattr(row, "confidence_tier", "") or ""),
                    "supported_for_stats": bool(getattr(row, "supported_for_stats", False)),
                }
            )
        payload_by_section[str(section_key)] = rows

    return pd.Series(
        [payload_by_section.get(str(section_key), []) for section_key in section_profiles["section_key"]],
        index=section_profiles.index,
        dtype=object,
    )


def select_diversified_activity_rows(candidates: pd.DataFrame, *, max_rows: int) -> pd.DataFrame:
    selected_parts: list[pd.DataFrame] = []
    for _, part in candidates.groupby("section_key", dropna=False):
        remaining = part.sort_values(
            ["activity_risk", "risk_percentile", "supported_rank", "source_priority", "n_locales", "display_label"],
            ascending=[True, True, True, True, False, True],
            na_position="last",
        ).copy()
        picked: list[pd.Series] = []
        used_supercategories: dict[str, int] = {}
        while len(picked) < max_rows and not remaining.empty:
            penalties = remaining["web_supercategory"].astype("string").map(
                lambda value: used_supercategories.get(str(value), 0) * ACTIVITY_SUPERCATEGORY_REPEAT_PENALTY
            ).astype(float)
            adjusted_score = pd.to_numeric(remaining["activity_risk"], errors="coerce") + penalties
            chosen_index = adjusted_score.idxmin()
            chosen = remaining.loc[chosen_index]
            picked.append(chosen)
            used_supercategories[str(chosen.get("web_supercategory", ""))] = used_supercategories.get(str(chosen.get("web_supercategory", "")), 0) + 1
            remaining = remaining.drop(index=chosen_index)
        if picked:
            selected_parts.append(pd.DataFrame(picked))

    if not selected_parts:
        return candidates.iloc[0:0].copy()
    return pd.concat(selected_parts, axis=0, ignore_index=True)


def attach_activity_evidence(candidates: pd.DataFrame, *, context: dict[str, object]) -> pd.DataFrame:
    out = candidates.copy()

    barrio_evidence = context["barrio_evidence"].add_prefix("barrio_")
    district_evidence = context["district_evidence"].add_prefix("district_")
    city_evidence = context["city_evidence"].add_prefix("city_")

    out = out.merge(
        barrio_evidence,
        how="left",
        left_on=["barrio_lookup_key", "macro_category_code"],
        right_on=["barrio_zone_lookup_key", "barrio_macro_category_code"],
    )
    out = out.merge(
        district_evidence,
        how="left",
        left_on=["district_code", "macro_category_code"],
        right_on=["district_zone_lookup_key", "district_macro_category_code"],
    )
    out = out.merge(
        city_evidence,
        how="left",
        left_on=["macro_category_code"],
        right_on=["city_macro_category_code"],
    )

    barrio_available = out.get("barrio_n_locales", pd.Series(np.nan, index=out.index)).notna()
    district_available = out.get("district_n_locales", pd.Series(np.nan, index=out.index)).notna()
    out["source_zone"] = np.select(
        [barrio_available, district_available],
        ["barrio", "district"],
        default="city",
    )

    out["n_locales"] = (
        pd.to_numeric(out.get("barrio_n_locales"), errors="coerce")
        .combine_first(pd.to_numeric(out.get("district_n_locales"), errors="coerce"))
        .combine_first(pd.to_numeric(out.get("city_n_locales"), errors="coerce"))
        .fillna(0.0)
    )
    out["n_events"] = (
        pd.to_numeric(out.get("barrio_n_events"), errors="coerce")
        .combine_first(pd.to_numeric(out.get("district_n_events"), errors="coerce"))
        .combine_first(pd.to_numeric(out.get("city_n_events"), errors="coerce"))
        .fillna(0.0)
    )
    out["event_rate"] = (
        pd.to_numeric(out.get("barrio_event_rate"), errors="coerce")
        .combine_first(pd.to_numeric(out.get("district_event_rate"), errors="coerce"))
        .combine_first(pd.to_numeric(out.get("city_event_rate"), errors="coerce"))
    )
    out["confidence_tier"] = (
        out.get("barrio_confidence_tier", pd.Series(pd.NA, index=out.index)).astype("string")
        .combine_first(out.get("district_confidence_tier", pd.Series(pd.NA, index=out.index)).astype("string"))
        .combine_first(out.get("city_confidence_tier", pd.Series(pd.NA, index=out.index)).astype("string"))
        .fillna("very_low")
    )
    out["supported_for_stats"] = (
        out.get("barrio_supported_for_stats", pd.Series(pd.NA, index=out.index, dtype="boolean")).astype("boolean")
        .combine_first(out.get("district_supported_for_stats", pd.Series(pd.NA, index=out.index, dtype="boolean")).astype("boolean"))
        .combine_first(out.get("city_supported_for_stats", pd.Series(pd.NA, index=out.index, dtype="boolean")).astype("boolean"))
        .fillna(False)
        .astype(bool)
    )
    return out


def build_section_macro_activity_reference(activity_abt: pd.DataFrame) -> pd.DataFrame:
    frame = activity_abt[[
        "first_seen_period",
        "section_key_start",
        "activity_category_code_start",
        "section_same_activity_category_local_count_start",
        "section_same_activity_category_share_start",
    ]].copy()
    frame["section_key_start"] = normalize_section_key_series(frame.get("section_key_start", pd.Series(pd.NA, index=frame.index))).astype("string")
    frame["activity_category_code_start"] = frame.get("activity_category_code_start", pd.Series(pd.NA, index=frame.index)).astype("string")
    frame["first_seen_date"] = pd.to_datetime(frame["first_seen_period"].astype("string") + "-01", errors="coerce")

    valid = frame[frame["section_key_start"].notna() & frame["activity_category_code_start"].notna()].copy()
    if valid.empty:
        return pd.DataFrame(columns=[
            "section_key",
            "macro_category_code",
            "macro_section_same_activity_category_local_count_start",
            "macro_section_same_activity_category_share_start",
        ])

    recent_cutoff = valid["first_seen_date"].max() - pd.DateOffset(months=RECENT_LOOKBACK_MONTHS)
    recent = valid[valid["first_seen_date"].ge(recent_cutoff)].copy() if valid["first_seen_date"].notna().any() else valid.iloc[0:0].copy()

    history = valid.groupby(["section_key_start", "activity_category_code_start"], dropna=False)[[
        "section_same_activity_category_local_count_start",
        "section_same_activity_category_share_start",
    ]].median(numeric_only=True)
    recent_grouped = recent.groupby(["section_key_start", "activity_category_code_start"], dropna=False)[[
        "section_same_activity_category_local_count_start",
        "section_same_activity_category_share_start",
    ]].median(numeric_only=True)
    combined = history.copy()
    combined.update(recent_grouped)
    return combined.reset_index().rename(columns={
        "section_key_start": "section_key",
        "activity_category_code_start": "macro_category_code",
        "section_same_activity_category_local_count_start": "macro_section_same_activity_category_local_count_start",
        "section_same_activity_category_share_start": "macro_section_same_activity_category_share_start",
    })


def build_activity_score_calibration(
    activity_abt: pd.DataFrame,
    scorer,
) -> list[dict[str, object]]:
    score_payload = apply_training_policies(
        activity_abt,
        transition_policy="keep_all",
        renta_max_year=2023,
    )
    dataset = score_payload["dataset"].copy()
    scored = scorer.score_frame(dataset, horizons=(12.0, 24.0))
    return build_calibration_lookup(
        score=scored["risk_cox"],
        duration=dataset["duration_months"],
        event=dataset["event_observed"],
        bucket_count=CALIBRATION_BUCKETS,
    )


def activity_evidence_supported(*, n_locales: float, n_events: float, zone_level: str) -> bool:
    if zone_level == "district":
        return n_locales >= ACTIVITY_DISTRICT_MIN_LOCALES and n_events >= ACTIVITY_DISTRICT_MIN_EVENTS
    return n_locales >= ACTIVITY_BARRIO_MIN_LOCALES and n_events >= ACTIVITY_BARRIO_MIN_EVENTS


def build_activity_recommendation_lookup() -> dict[str, dict[str, list[dict[str, object]]]]:
    return {
        "district_by_code": load_zone_recommendations(DISTRICT_CATEGORY_CSV, zone_level="district", key_mode="code"),
        "district_by_name": load_zone_recommendations(DISTRICT_CATEGORY_CSV, zone_level="district", key_mode="name"),
        "barrio_by_name": load_zone_recommendations(BARRIO_CATEGORY_CSV, zone_level="barrio", key_mode="name"),
        "citywide": load_city_recommendations(DISTRICT_CATEGORY_CSV),
    }


def load_zone_recommendations(path: Path, *, zone_level: str, key_mode: str) -> dict[str, list[dict[str, object]]]:
    frame = pd.read_csv(path, low_memory=False)
    width = 2 if zone_level == "district" else 3
    frame["zone_code"] = frame["zone_code"].map(lambda value: normalize_admin_code(value, width=width)).astype("string")
    frame["zone_name"] = frame["zone_name"].astype("string")
    frame["zone_lookup_key"] = frame["zone_code"] if key_mode == "code" else frame["zone_name"].map(normalize_zone_lookup_key).astype("string")
    frame["display_label"] = frame["display_label"].astype("string")
    frame["event_rate"] = pd.to_numeric(frame["event_rate"], errors="coerce")
    frame["survival_12m"] = pd.to_numeric(frame["survival_12m"], errors="coerce")
    frame["survival_24m"] = pd.to_numeric(frame["survival_24m"], errors="coerce")
    frame["n_locales"] = pd.to_numeric(frame["n_locales"], errors="coerce")
    frame["supported_for_stats"] = frame["supported_for_stats"].fillna(False).astype(bool)

    out: dict[str, list[dict[str, object]]] = {}
    for zone_key, part in frame.groupby("zone_lookup_key", dropna=False):
        if pd.isna(zone_key) or not str(zone_key).strip():
            continue
        scoped = part[part["supported_for_stats"]].copy()
        if scoped.empty:
            scoped = part.copy()

        prior_event_rate = float(pd.to_numeric(scoped["event_rate"], errors="coerce").median()) if scoped["event_rate"].notna().any() else 0.15
        scoped["activity_risk"] = [
            compute_activity_risk(
                event_rate=event_rate,
                n_locales=n_locales,
                supported_for_stats=supported_for_stats,
                prior_event_rate=prior_event_rate,
            )
            for event_rate, n_locales, supported_for_stats in zip(
                scoped["event_rate"],
                scoped["n_locales"],
                scoped["supported_for_stats"],
            )
        ]
        scoped = scoped.sort_values(
            ["activity_risk", "event_rate", "survival_24m", "n_locales", "display_label"],
            ascending=[True, True, False, False, True],
        )
        scoped = scoped.drop_duplicates(subset=["display_label"], keep="first")

        rows: list[dict[str, object]] = []
        for index, row in enumerate(scoped.head(5).itertuples(index=False), start=1):
            rows.append(
                {
                    "rank": index,
                    "source_zone": zone_level,
                    "display_label": str(row.display_label),
                    "web_supercategory": str(getattr(row, "web_supercategory", "") or ""),
                    "web_category": str(getattr(row, "web_category", "") or ""),
                    "event_rate": serialize_probability(getattr(row, "event_rate", None)),
                    "activity_risk": serialize_probability(getattr(row, "activity_risk", None)),
                    "survival_12m": serialize_probability(getattr(row, "survival_12m", None)),
                    "survival_24m": serialize_probability(getattr(row, "survival_24m", None)),
                    "n_locales": int(float(getattr(row, "n_locales", 0) or 0)),
                    "confidence_tier": str(getattr(row, "confidence_tier", "") or ""),
                    "supported_for_stats": bool(getattr(row, "supported_for_stats", False)),
                }
            )
        out[str(zone_key)] = rows
    return out


def lookup_zone_recommendations(
    lookup: dict[str, dict[str, list[dict[str, object]]]],
    *,
    zone_level: str,
    zone_code: object | None = None,
    zone_name: object | None = None,
) -> list[dict[str, object]]:
    if zone_level == "district":
        zone_code_key = normalize_admin_code(zone_code, width=2)
        zone_name_key = normalize_zone_lookup_key(zone_name)
        if zone_code_key and zone_code_key in lookup["district_by_code"]:
            return lookup["district_by_code"][zone_code_key]
        if zone_name_key and zone_name_key in lookup["district_by_name"]:
            return lookup["district_by_name"][zone_name_key]
        return []

    zone_name_key = normalize_zone_lookup_key(zone_name)
    if zone_name_key and zone_name_key in lookup["barrio_by_name"]:
        return lookup["barrio_by_name"][zone_name_key]
    return []


def load_city_recommendations(path: Path) -> list[dict[str, object]]:
    frame = pd.read_csv(path, low_memory=False)
    frame["display_label"] = frame["display_label"].astype("string")
    frame["web_supercategory"] = frame["web_supercategory"].astype("string")
    frame["web_category"] = frame["web_category"].astype("string")
    frame["n_locales"] = pd.to_numeric(frame["n_locales"], errors="coerce").fillna(0.0)
    frame["n_events"] = pd.to_numeric(frame.get("n_events"), errors="coerce").fillna(0.0)
    frame["survival_12m"] = pd.to_numeric(frame["survival_12m"], errors="coerce")
    frame["survival_24m"] = pd.to_numeric(frame["survival_24m"], errors="coerce")
    frame["supported_for_stats"] = frame["supported_for_stats"].fillna(False).astype(bool)

    grouped = frame.groupby(["display_label", "web_supercategory", "web_category"], dropna=False).apply(
        lambda part: pd.Series(
            {
                "n_locales": float(part["n_locales"].sum()),
                "n_events": float(part["n_events"].sum()),
                "survival_12m": weighted_mean(part["survival_12m"], part["n_locales"]),
                "survival_24m": weighted_mean(part["survival_24m"], part["n_locales"]),
                "supported_for_stats": bool(part["supported_for_stats"].any()),
            }
        ),
        include_groups=False,
    ).reset_index()
    grouped = grouped[grouped["display_label"].notna()].copy()
    grouped["event_rate"] = grouped["n_events"] / grouped["n_locales"].replace({0.0: np.nan})

    prior_event_rate = float(grouped["event_rate"].median()) if grouped["event_rate"].notna().any() else 0.15
    grouped["activity_risk"] = [
        compute_activity_risk(
            event_rate=event_rate,
            n_locales=n_locales,
            supported_for_stats=supported_for_stats,
            prior_event_rate=prior_event_rate,
        )
        for event_rate, n_locales, supported_for_stats in zip(
            grouped["event_rate"],
            grouped["n_locales"],
            grouped["supported_for_stats"],
        )
    ]
    grouped["confidence_tier"] = grouped["n_locales"].map(city_confidence_tier)
    grouped = grouped.sort_values(
        ["activity_risk", "event_rate", "survival_24m", "n_locales", "display_label"],
        ascending=[True, True, False, False, True],
    )

    rows: list[dict[str, object]] = []
    for index, row in enumerate(grouped.head(50).itertuples(index=False), start=1):
        rows.append(
            {
                "rank": index,
                "source_zone": "city",
                "display_label": str(row.display_label),
                "web_supercategory": str(getattr(row, "web_supercategory", "") or ""),
                "web_category": str(getattr(row, "web_category", "") or ""),
                "event_rate": serialize_probability(getattr(row, "event_rate", None)),
                "activity_risk": serialize_probability(getattr(row, "activity_risk", None)),
                "survival_12m": serialize_probability(getattr(row, "survival_12m", None)),
                "survival_24m": serialize_probability(getattr(row, "survival_24m", None)),
                "n_locales": int(round(float(getattr(row, "n_locales", 0) or 0))),
                "confidence_tier": str(getattr(row, "confidence_tier", "") or ""),
                "supported_for_stats": bool(getattr(row, "supported_for_stats", False)),
            }
        )
    return rows


def combine_activity_recommendations(
    barrio_rows: list[dict[str, object]],
    district_rows: list[dict[str, object]],
    city_rows: list[dict[str, object]],
    *,
    max_rows: int = 5,
) -> list[dict[str, object]]:
    best_by_label: dict[str, dict[str, object]] = {}

    for rows in [barrio_rows, district_rows, city_rows]:
        for row in rows:
            key = str(row.get("display_label") or "")
            if not key:
                continue

            item = dict(row)
            existing = best_by_label.get(key)
            if existing is None or activity_recommendation_sort_key(item) < activity_recommendation_sort_key(existing):
                best_by_label[key] = item

    merged = sorted(best_by_label.values(), key=activity_recommendation_sort_key)[:max_rows]
    for index, item in enumerate(merged, start=1):
        item["rank"] = index
    return merged


def build_calibration_lookup(
    *,
    score: pd.Series,
    duration: pd.Series,
    event: pd.Series,
    bucket_count: int,
) -> list[dict[str, object]]:
    frame = pd.DataFrame(
        {
            "score": pd.to_numeric(score, errors="coerce"),
            "duration": pd.to_numeric(duration, errors="coerce"),
            "event": pd.to_numeric(event, errors="coerce").fillna(0),
        }
    ).dropna(subset=["score", "duration"])
    if frame.empty:
        return [{"score_max": float("inf"), "survival_12m": None, "survival_24m": None, "bucket_label": "P00-P100"}]

    rank = frame["score"].rank(method="first", pct=True)
    frame["bucket_index"] = np.minimum(bucket_count - 1, np.floor(rank * bucket_count).astype(int))
    rows: list[dict[str, object]] = []
    for bucket_index, part in frame.groupby("bucket_index", dropna=False):
        support_12m, survival_12m = compute_horizon_metrics(part["duration"], part["event"], horizon=12.0)
        support_24m, survival_24m = compute_horizon_metrics(part["duration"], part["event"], horizon=24.0)
        bucket_low = int(bucket_index) / bucket_count
        bucket_high = (int(bucket_index) + 1) / bucket_count
        rows.append(
            {
                "bucket_index": int(bucket_index),
                "bucket_label": f"P{int(bucket_low * 100):02d}-P{int(bucket_high * 100):02d}",
                "score_max": float(part["score"].max()),
                "survival_12m": serialize_probability(survival_12m),
                "survival_24m": serialize_probability(survival_24m),
                "support_12m": int(support_12m),
                "support_24m": int(support_24m),
            }
        )
    return sorted(rows, key=lambda item: item["score_max"])


def lookup_calibration(rows: list[dict[str, object]], score: float) -> dict[str, object]:
    for row in rows:
        if score <= float(row["score_max"]):
            return row
    return rows[-1]


def compute_score_percentile(sorted_scores: np.ndarray, value: float) -> float:
    if len(sorted_scores) == 0 or not np.isfinite(value):
        return float("nan")
    position = np.searchsorted(sorted_scores, value, side="right")
    return float(position / len(sorted_scores))


def add_section_rankings(frame: pd.DataFrame) -> pd.DataFrame:
    ranked = frame.copy()
    ranked["city_total_sections"] = int(len(ranked))
    ranked["city_rank"] = ranked["risk_score"].rank(method="min", ascending=True).astype(int)
    ranked["district_total_sections"] = ranked.groupby("district_code", dropna=False)["section_key"].transform("size").astype(int)
    ranked["district_rank"] = ranked.groupby("district_code", dropna=False)["risk_score"].rank(method="min", ascending=True).astype(int)
    barrio_scope = ["district_code", "barrio_code"]
    ranked["barrio_total_sections"] = ranked.groupby(barrio_scope, dropna=False)["section_key"].transform("size").astype(int)
    ranked["barrio_rank"] = ranked.groupby(barrio_scope, dropna=False)["risk_score"].rank(method="min", ascending=True).astype(int)
    return ranked


def compute_outlier_flags(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    numeric_columns = ["price_eur", "price_per_m2_eur", "area_m2"]
    flag_count = pd.Series(0, index=frame.index, dtype=int)
    reasons = pd.Series("", index=frame.index, dtype="string")

    for _, index_values in frame.groupby(frame["operation"].astype("string").fillna("unknown")).groups.items():
        index_list = list(index_values)
        scoped = frame.loc[index_list]
        for column in numeric_columns:
            series = pd.to_numeric(scoped[column], errors="coerce")
            valid = series.dropna()
            if len(valid) < 8:
                continue
            transformed = np.log1p(valid.clip(lower=0))
            q1 = float(transformed.quantile(0.25))
            q3 = float(transformed.quantile(0.75))
            iqr = q3 - q1
            if not np.isfinite(iqr) or iqr <= 0:
                continue

            lower = max(0.0, float(np.expm1(q1 - 1.5 * iqr)))
            upper = float(np.expm1(q3 + 1.5 * iqr))
            flagged = series.notna() & ((series < lower) | (series > upper))
            if not bool(flagged.any()):
                continue

            flagged_index = flagged[flagged].index
            flag_count.loc[flagged_index] = flag_count.loc[flagged_index] + 1
            reasons.loc[flagged_index] = reasons.loc[flagged_index].fillna("") + f"{column};"

    return flag_count, reasons.fillna("")


def fill_section_reference_holes(
    frame: pd.DataFrame,
    *,
    district_col: str = "district_code",
    barrio_col: str = "barrio_code",
    columns: list[str] | None = None,
) -> None:
    columns = columns or SECTION_PROFILE_MEDIAN_COLUMNS
    for column in columns:
        if column not in frame.columns:
            frame[column] = np.nan
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        barrio_fill = frame.groupby(barrio_col, dropna=False)[column].transform("median") if barrio_col in frame.columns else np.nan
        district_fill = frame.groupby(district_col, dropna=False)[column].transform("median") if district_col in frame.columns else np.nan
        city_fill = float(frame[column].median()) if frame[column].notna().any() else 0.0
        frame[column] = frame[column].fillna(barrio_fill).fillna(district_fill).fillna(city_fill).fillna(0.0)


def overwrite_section_reference_columns(
    base: pd.DataFrame,
    override: pd.DataFrame,
    *,
    columns: list[str],
) -> pd.DataFrame:
    if base.empty or override.empty:
        return base

    available_columns = [column for column in columns if column in base.columns and column in override.columns]
    if not available_columns:
        return base

    out = base.merge(
        override[["section_key", *available_columns]],
        how="left",
        on="section_key",
        suffixes=("", "_override"),
    )
    for column in available_columns:
        override_column = f"{column}_override"
        out[column] = pd.to_numeric(out.get(override_column), errors="coerce").combine_first(pd.to_numeric(out.get(column), errors="coerce"))
        out = out.drop(columns=[override_column])
    return out


def harmonize_section_commercial_context(frame: pd.DataFrame) -> None:
    if "section_local_count_start" not in frame.columns:
        return

    local_count = pd.to_numeric(frame.get("section_local_count_start"), errors="coerce")
    frame["section_local_count_start"] = local_count.clip(lower=0.0)

    if "section_unique_activity_category_count_start" in frame.columns:
        unique_categories = pd.to_numeric(frame.get("section_unique_activity_category_count_start"), errors="coerce").clip(lower=0.0)
        needs_minimum_category = frame["section_local_count_start"].gt(0) & unique_categories.fillna(0.0).le(0.0)
        unique_categories = unique_categories.mask(needs_minimum_category, 1.0)
        frame["section_unique_activity_category_count_start"] = unique_categories


def fill_avisos_holes(frame: pd.DataFrame) -> None:
    for column in [
        "avisos_district_per_1000_prev_year",
        "avisos_barrio_per_1000_prev_year",
        "avisos_barrio_share_of_district_prev_year",
    ]:
        frame[column] = pd.to_numeric(frame.get(column), errors="coerce")
        city_fill = float(frame[column].median()) if frame[column].notna().any() else 0.0
        frame[column] = frame[column].fillna(city_fill).fillna(0.0)


def build_section_index_payload(section_profiles: pd.DataFrame) -> dict[str, object]:
    sections = [build_section_payload(row) for row in section_profiles.itertuples(index=False)]
    return {
        "meta": {
            "generated_at": pd.Timestamp.utcnow().isoformat(),
        },
        "sections": _to_jsonable(sections),
    }


def build_sections_geojson(section_profiles: pd.DataFrame) -> dict[str, object]:
    features: list[dict[str, object]] = []
    for row in section_profiles.itertuples(index=False):
        features.append(
            {
                "type": "Feature",
                "geometry": row.geometry.__geo_interface__,
                "properties": _to_jsonable(build_section_geometry_properties(row)),
            }
        )
    return {"type": "FeatureCollection", "features": features}


def build_section_geometry_properties(row: object) -> dict[str, object]:
    return {
        "section_key": str(getattr(row, "section_key", "") or ""),
        "district_code": str(getattr(row, "district_code", "") or ""),
        "district_name": str(getattr(row, "district_name", "") or ""),
        "barrio_code": str(getattr(row, "barrio_code", "") or ""),
        "barrio_name": str(getattr(row, "barrio_name", "") or ""),
        "centroid_lat": serialize_probability(getattr(row, "centroid_lat", None)),
        "centroid_lon": serialize_probability(getattr(row, "centroid_lon", None)),
    }


def build_section_payload(row: object) -> dict[str, object]:
    return {
        **build_section_geometry_properties(row),
        "risk_score": float(getattr(row, "risk_score")),
        "risk_percentile": float(getattr(row, "risk_percentile")),
        "expected_survival_12m": serialize_probability(getattr(row, "expected_survival_12m", None)),
        "expected_survival_24m": serialize_probability(getattr(row, "expected_survival_24m", None)),
        "opportunity_tier": str(getattr(row, "opportunity_tier", "") or ""),
        "city_rank": int(getattr(row, "city_rank")),
        "city_total_sections": int(getattr(row, "city_total_sections")),
        "district_rank": int(getattr(row, "district_rank")),
        "district_total_sections": int(getattr(row, "district_total_sections")),
        "barrio_rank": int(getattr(row, "barrio_rank")),
        "barrio_total_sections": int(getattr(row, "barrio_total_sections")),
        "renta_effective_eur": serialize_probability(getattr(row, "renta_effective_eur", None)),
        "renta_reference_year": serialize_probability(getattr(row, "renta_reference_year", None)),
        "renta_granularity_used": str(getattr(row, "renta_granularity_used", "") or ""),
        "renta_outlier_adjusted": bool(getattr(row, "renta_outlier_adjusted", False)),
        "total_population_start": serialize_probability(getattr(row, "total_population_start", None)),
        "population_density_km2_start": serialize_probability(getattr(row, "population_density_km2_start", None)),
        "age_mean_start": serialize_probability(getattr(row, "age_mean_start", None)),
        "share_foreign_start": serialize_probability(getattr(row, "share_foreign_start", None)),
        "share_age_15_29_start": serialize_probability(getattr(row, "share_age_15_29_start", None)),
        "share_age_65_plus_start": serialize_probability(getattr(row, "share_age_65_plus_start", None)),
        "metro_distance_m_start": serialize_probability(getattr(row, "metro_distance_m_start", None)),
        "metro_access_count_500m_start": serialize_probability(getattr(row, "metro_access_count_500m_start", None)),
        "metro_access_count_1000m_start": serialize_probability(getattr(row, "metro_access_count_1000m_start", None)),
        "metro_station_count_500m_start": serialize_probability(getattr(row, "metro_station_count_500m_start", None)),
        "metro_station_count_1000m_start": serialize_probability(getattr(row, "metro_station_count_1000m_start", None)),
        "metro_nearest_name_start": serialize_optional_text(getattr(row, "metro_nearest_name_start", None)),
        "metro_nearest_station_name_start": serialize_optional_text(getattr(row, "metro_nearest_station_name_start", None)),
        "metro_access_names_500m_start": serialize_optional_text_list(getattr(row, "metro_access_names_500m_start", [])),
        "metro_access_names_1000m_start": serialize_optional_text_list(getattr(row, "metro_access_names_1000m_start", [])),
        "metro_station_names_500m_start": serialize_optional_text_list(getattr(row, "metro_station_names_500m_start", [])),
        "metro_station_names_1000m_start": serialize_optional_text_list(getattr(row, "metro_station_names_1000m_start", [])),
        "avisos_barrio_per_1000_prev_year": serialize_probability(getattr(row, "avisos_barrio_per_1000_prev_year", None)),
        "avisos_district_per_1000_prev_year": serialize_probability(getattr(row, "avisos_district_per_1000_prev_year", None)),
        "top_avisos_barrio_categories": serialize_avisos_top_categories(getattr(row, "top_avisos_barrio_categories", [])),
        "top_avisos_district_categories": serialize_avisos_top_categories(getattr(row, "top_avisos_district_categories", [])),
        "section_local_count_start": serialize_probability(getattr(row, "section_local_count_start", None)),
        "section_unique_activity_category_count_start": serialize_probability(
            getattr(row, "section_unique_activity_category_count_start", None)
        ),
        "section_turnover_rate_12m_start": serialize_probability(getattr(row, "section_turnover_rate_12m_start", None)),
        "section_same_activity_category_share_start": serialize_probability(
            getattr(row, "section_same_activity_category_share_start", None)
        ),
        "best_activity_label": str(getattr(row, "best_activity_label", "") or ""),
        "best_activity_risk": serialize_probability(getattr(row, "best_activity_risk", None)),
        "best_activity_survival_24m": serialize_probability(getattr(row, "best_activity_survival_24m", None)),
        "top_activities": getattr(row, "top_activities", []),
        "facilities_tier": str(getattr(row, "facilities_tier", "Sin datos") or "Sin datos"),
        "facilities_200m": int(getattr(row, "facilities_200m", 0) or 0),
        "facilities_500m": int(getattr(row, "facilities_500m", 0) or 0),
        "facilities_1000m": int(getattr(row, "facilities_1000m", 0) or 0),
        "facilities_by_category": getattr(row, "facilities_by_category", []) or [],
        "vulnerabilidad_global": serialize_probability(getattr(row, "vulnerabilidad_global", None)),
        "vulnerabilidad_global_media_ciudad": serialize_probability(getattr(row, "vulnerabilidad_global_media_ciudad", None)),
        "vulnerabilidad_esferas": getattr(row, "vulnerabilidad_esferas", []) or [],
        "inspecciones_distrito_total": serialize_probability(getattr(row, "inspecciones_distrito_total", None)),
        "inspecciones_ciudad_media": serialize_probability(getattr(row, "inspecciones_ciudad_media", None)),
        "inspecciones_top_epigrafes": getattr(row, "inspecciones_top_epigrafes", []) or [],
        "indicadores_distrito": getattr(row, "indicadores_distrito", []) or [],
    }


def build_selected_summary(selected_scored: pd.DataFrame, filter_summary: dict[str, object]) -> dict[str, object]:
    return {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "filter_summary": filter_summary,
        "selected_listings": int(len(selected_scored)),
        "districts": int(selected_scored["district_code"].dropna().nunique()),
        "barrios": count_unique_barrio_scopes(selected_scored),
        "operations": {
            str(key): int(value) for key, value in selected_scored["operation"].astype("string").value_counts(dropna=False).to_dict().items()
        },
        "median_risk_percentile": float(pd.to_numeric(selected_scored["risk_percentile"], errors="coerce").median()),
        "median_survival_24m": serialize_probability(pd.to_numeric(selected_scored["expected_survival_24m"], errors="coerce").median()),
    }


def build_frontend_artifacts(selected_scored: pd.DataFrame, filter_summary: dict[str, object]) -> dict[str, object]:
    points = [build_point_payload(row) for row in selected_scored.itertuples(index=False)]
    generated_at = pd.Timestamp.utcnow().isoformat()
    generated_version = pd.Timestamp.utcnow().strftime('%Y%m%dT%H%M%S')
    stats = {
        "selected_listings": int(len(selected_scored)),
        "districts": int(selected_scored["district_code"].dropna().nunique()),
        "barrios": count_unique_barrio_scopes(selected_scored),
        "median_survival_24m": serialize_probability(pd.to_numeric(selected_scored["expected_survival_24m"], errors="coerce").median()),
        "median_price_per_m2": serialize_probability(pd.to_numeric(selected_scored["price_per_m2_eur"], errors="coerce").median()),
    }
    return {
        "meta": {
            "title": "Madrid Opportunity Map",
            "subtitle": "Locales disponibles y recomendación de actividad",
            "generated_at": generated_at,
            "section_index_path": f"/data/opportunities/sections/index.json?v={generated_version}",
            "section_geojson_path": f"/data/opportunities/sections/geometry.geojson?v={generated_version}",
            "map_bounds": {
                "min_lng": MADRID_BBOX["min_lon"],
                "min_lat": MADRID_BBOX["min_lat"],
                "max_lng": MADRID_BBOX["max_lon"],
                "max_lat": MADRID_BBOX["max_lat"],
                "min_zoom": 9.8,
                "max_zoom": 16.2,
            },
        },
        "filters": _to_jsonable(filter_summary),
        "stats": _to_jsonable(stats),
        "points": _to_jsonable(points),
    }


def build_point_payload(row: object) -> dict[str, object]:
    top_activities = getattr(row, "top_activities", []) or []
    return {
        "listing_id": str(getattr(row, "listing_id")),
        "listing_url": str(getattr(row, "listing_url", "") or ""),
        "card_title": str(getattr(row, "card_title", "") or ""),
        "address_text": str(getattr(row, "address_text", "") or ""),
        "operation": str(getattr(row, "operation", "") or ""),
        "price_eur": serialize_probability(getattr(row, "price_eur", None)),
        "price_per_m2_eur": serialize_probability(getattr(row, "price_per_m2_eur", None)),
        "area_m2": serialize_probability(getattr(row, "area_m2", None)),
        "lat_wgs84": serialize_probability(getattr(row, "lat_wgs84", None)),
        "lon_wgs84": serialize_probability(getattr(row, "lon_wgs84", None)),
        "section_key": str(getattr(row, "section_key", "") or ""),
        "district_code": str(getattr(row, "district_code", "") or ""),
        "district_name": str(getattr(row, "district_name", "") or ""),
        "barrio_code": str(getattr(row, "barrio_code", "") or ""),
        "barrio_name": str(getattr(row, "barrio_name", "") or ""),
        "risk_score": float(getattr(row, "risk_score")),
        "risk_percentile": float(getattr(row, "risk_percentile")),
        "expected_survival_12m": serialize_probability(getattr(row, "expected_survival_12m", None)),
        "expected_survival_24m": serialize_probability(getattr(row, "expected_survival_24m", None)),
        "opportunity_tier": str(getattr(row, "opportunity_tier", "") or ""),
        "city_rank": int(getattr(row, "city_rank")),
        "city_total_sections": int(getattr(row, "city_total_sections")),
        "district_rank": int(getattr(row, "district_rank")),
        "district_total_sections": int(getattr(row, "district_total_sections")),
        "barrio_rank": int(getattr(row, "barrio_rank")),
        "barrio_total_sections": int(getattr(row, "barrio_total_sections")),
        "renta_effective_eur": serialize_probability(getattr(row, "renta_effective_eur", None)),
        "renta_reference_year": serialize_probability(getattr(row, "renta_reference_year", None)),
        "renta_granularity_used": str(getattr(row, "renta_granularity_used", "") or ""),
        "renta_outlier_adjusted": bool(getattr(row, "renta_outlier_adjusted", False)),
        "total_population_start": serialize_probability(getattr(row, "total_population_start", None)),
        "population_density_km2_start": serialize_probability(getattr(row, "population_density_km2_start", None)),
        "age_mean_start": serialize_probability(getattr(row, "age_mean_start", None)),
        "share_foreign_start": serialize_probability(getattr(row, "share_foreign_start", None)),
        "share_age_15_29_start": serialize_probability(getattr(row, "share_age_15_29_start", None)),
        "share_age_65_plus_start": serialize_probability(getattr(row, "share_age_65_plus_start", None)),
        "metro_distance_m_start": serialize_probability(getattr(row, "metro_distance_m_start", None)),
        "metro_access_count_500m_start": serialize_probability(getattr(row, "metro_access_count_500m_start", None)),
        "metro_access_count_1000m_start": serialize_probability(getattr(row, "metro_access_count_1000m_start", None)),
        "metro_station_count_500m_start": serialize_probability(getattr(row, "metro_station_count_500m_start", None)),
        "metro_station_count_1000m_start": serialize_probability(getattr(row, "metro_station_count_1000m_start", None)),
        "metro_nearest_name_start": serialize_optional_text(getattr(row, "metro_nearest_name_start", None)),
        "metro_nearest_station_name_start": serialize_optional_text(getattr(row, "metro_nearest_station_name_start", None)),
        "metro_access_names_500m_start": serialize_optional_text_list(getattr(row, "metro_access_names_500m_start", [])),
        "metro_access_names_1000m_start": serialize_optional_text_list(getattr(row, "metro_access_names_1000m_start", [])),
        "metro_station_names_500m_start": serialize_optional_text_list(getattr(row, "metro_station_names_500m_start", [])),
        "metro_station_names_1000m_start": serialize_optional_text_list(getattr(row, "metro_station_names_1000m_start", [])),
        "avisos_barrio_per_1000_prev_year": serialize_probability(getattr(row, "avisos_barrio_per_1000_prev_year", None)),
        "avisos_district_per_1000_prev_year": serialize_probability(getattr(row, "avisos_district_per_1000_prev_year", None)),
        "top_avisos_barrio_categories": serialize_avisos_top_categories(getattr(row, "top_avisos_barrio_categories", [])),
        "top_avisos_district_categories": serialize_avisos_top_categories(getattr(row, "top_avisos_district_categories", [])),
        "section_local_count_start": serialize_probability(getattr(row, "section_local_count_start", None)),
        "section_unique_activity_category_count_start": serialize_probability(getattr(row, "section_unique_activity_category_count_start", None)),
        "section_turnover_rate_12m_start": serialize_probability(getattr(row, "section_turnover_rate_12m_start", None)),
        "section_same_activity_category_share_start": serialize_probability(getattr(row, "section_same_activity_category_share_start", None)),
        "best_activity_label": str(getattr(row, "best_activity_label", "") or ""),
        "best_activity_risk": serialize_probability(getattr(row, "best_activity_risk", None)),
        "best_activity_survival_24m": serialize_probability(getattr(row, "best_activity_survival_24m", None)),
        "top_activities": top_activities,
        "facilities_tier": str(getattr(row, "facilities_tier", "Sin datos") or "Sin datos"),
        "facilities_200m": int(getattr(row, "facilities_200m", 0) or 0),
        "facilities_500m": int(getattr(row, "facilities_500m", 0) or 0),
        "facilities_1000m": int(getattr(row, "facilities_1000m", 0) or 0),
        "facilities_by_category": getattr(row, "facilities_by_category", []) or [],
        "vulnerabilidad_global": serialize_probability(getattr(row, "vulnerabilidad_global", None)),
        "vulnerabilidad_global_media_ciudad": serialize_probability(getattr(row, "vulnerabilidad_global_media_ciudad", None)),
        "vulnerabilidad_esferas": getattr(row, "vulnerabilidad_esferas", []) or [],
        "inspecciones_distrito_total": serialize_probability(getattr(row, "inspecciones_distrito_total", None)),
        "inspecciones_ciudad_media": serialize_probability(getattr(row, "inspecciones_ciudad_media", None)),
        "inspecciones_top_epigrafes": getattr(row, "inspecciones_top_epigrafes", []) or [],
        "indicadores_distrito": getattr(row, "indicadores_distrito", []) or [],
    }


def compute_horizon_metrics(duration: pd.Series, event: pd.Series, *, horizon: float) -> tuple[int, float | None]:
    support = int(((duration >= float(horizon)) | ((event == 1) & (duration <= float(horizon)))).sum())
    if support <= 0:
        return 0, None
    survivors = int((duration >= float(horizon)).sum())
    return support, float(survivors / support)


def latlon_to_h3(lat: pd.Series, lon: pd.Series, *, resolution: int) -> pd.Series:
    try:
        import h3
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("h3 is required to compute the opportunity H3 cells") from exc

    valid = lat.notna() & lon.notna()
    out = pd.Series(pd.NA, index=lat.index, dtype="string")
    if not bool(valid.any()):
        return out

    if hasattr(h3, "latlng_to_cell"):
        out.loc[valid] = [
            h3.latlng_to_cell(float(lat_value), float(lon_value), resolution)
            for lat_value, lon_value in zip(lat.loc[valid], lon.loc[valid])
        ]
        return out

    out.loc[valid] = [
        h3.geo_to_h3(float(lat_value), float(lon_value), resolution)
        for lat_value, lon_value in zip(lat.loc[valid], lon.loc[valid])
    ]
    return out


def clean_place_name(value: object) -> object:
    if value is None or pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    return text.title()


def clean_avisos_category_label(value: object) -> object:
    if value is None or pd.isna(value):
        return pd.NA
    text = " ".join(str(value).strip().split())
    if not text or text.lower() == "nan":
        return pd.NA
    return text


def normalize_zone_lookup_key(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().lower()
    return text or None


def serialize_optional_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if not text or text == "<NA>" or text.lower() == "nan":
        return ""
    return text


def serialize_optional_text_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned = [serialize_optional_text(item) for item in value]
    return [item for item in cleaned if item]


def count_unique_barrio_scopes(frame: pd.DataFrame) -> int:
    if frame.empty or "district_code" not in frame.columns or "barrio_code" not in frame.columns:
        return 0

    scoped_keys = pd.Series(
        [
            f"{district}:{barrio}"
            if pd.notna(district) and pd.notna(barrio) and str(district).strip() and str(barrio).strip()
            else pd.NA
            for district, barrio in zip(frame["district_code"], frame["barrio_code"])
        ],
        index=frame.index,
        dtype="string",
    )
    return int(scoped_keys.dropna().nunique())


def normalize_section_barrio_code(district_code: object, barrio_code: object) -> str | None:
    district = normalize_admin_code(district_code, width=2)
    barrio_local = normalize_admin_code(barrio_code, width=3)
    if district is None or barrio_local is None:
        return None

    district_value = int(district)
    barrio_value = int(barrio_local)
    citywide_value = (district_value * 10) + barrio_value
    return str(citywide_value).zfill(3)


def coalesce_strings(primary: pd.Series | None, secondary: pd.Series | None) -> pd.Series:
    if primary is None and secondary is None:
        return pd.Series(dtype="string")
    if primary is None:
        return secondary.astype("string")
    if secondary is None:
        return primary.astype("string")
    left = primary.astype("string")
    right = secondary.astype("string")
    return left.fillna(right).astype("string")


def first_valid(series: pd.Series) -> object:
    non_null = series.dropna()
    if non_null.empty:
        return pd.NA
    return non_null.iloc[0]


def opportunity_tier_from_percentile(value: float) -> str:
    if not np.isfinite(value):
        return "Sin lectura"
    if value <= 0.2:
        return "Alta"
    if value <= 0.45:
        return "Solida"
    if value <= 0.7:
        return "Intermedia"
    return "Fragil"


def activity_recommendation_sort_key(row: dict[str, object]) -> tuple[float, float, float, float, int, str]:
    risk = coerce_sort_float(row.get("activity_risk"), default=float("inf"))
    event_rate = coerce_sort_float(row.get("event_rate"), default=float("inf"))
    survival_24m = coerce_sort_float(row.get("survival_24m"), default=float("-inf"))
    n_locales = coerce_sort_float(row.get("n_locales"), default=0.0)
    source_zone = str(row.get("source_zone") or "")
    if source_zone == "barrio":
        source_priority = 0
    elif source_zone == "district":
        source_priority = 1
    else:
        source_priority = 2
    label = str(row.get("display_label") or "")
    return (risk, event_rate, -survival_24m, -n_locales, source_priority, label)


def coerce_sort_float(value: object, *, default: float) -> float:
    if value is None or pd.isna(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def weighted_mean(values: pd.Series, weights: pd.Series) -> float | None:
    valid = values.notna() & weights.notna() & weights.gt(0)
    if not bool(valid.any()):
        return None
    return float(np.average(values.loc[valid], weights=weights.loc[valid]))


def city_confidence_tier(n_locales: float) -> str:
    if not np.isfinite(n_locales):
        return "city"
    if n_locales >= 1500:
        return "high"
    if n_locales >= 500:
        return "medium"
    if n_locales >= 150:
        return "low"
    return "very_low"


def compute_activity_risk(
    *,
    event_rate: object,
    n_locales: object,
    supported_for_stats: object,
    prior_event_rate: float,
) -> float:
    resolved_event_rate = float(event_rate) if event_rate is not None and pd.notna(event_rate) else float(prior_event_rate)
    resolved_event_rate = min(max(resolved_event_rate, 0.0), 1.0)
    resolved_support = float(n_locales) if n_locales is not None and pd.notna(n_locales) else 0.0
    shrunk = ((resolved_event_rate * resolved_support) + (prior_event_rate * ACTIVITY_PRIOR_STRENGTH)) / (resolved_support + ACTIVITY_PRIOR_STRENGTH)
    if not bool(supported_for_stats):
        shrunk += UNSUPPORTED_ACTIVITY_PENALTY
    return float(min(max(shrunk, 0.0), 1.0))


def serialize_probability(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def serialize_avisos_top_categories(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []

    rows: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue

        label = clean_avisos_category_label(item.get("label"))
        if label is None or pd.isna(label):
            continue

        rank = pd.to_numeric(item.get("rank"), errors="coerce")
        count = pd.to_numeric(item.get("count"), errors="coerce")
        rows.append(
            {
                "rank": int(rank) if pd.notna(rank) else len(rows) + 1,
                "label": str(label),
                "count": int(count) if pd.notna(count) else 0,
                "share_of_zone": serialize_probability(item.get("share_of_zone")),
            }
        )
    return rows


def _to_jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, pd.Series):
        return {str(key): _to_jsonable(item) for key, item in value.to_dict().items()}
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.floating, float)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if value is None or pd.isna(value):
        return None
    return value


if __name__ == "__main__":
    raise SystemExit(main())
