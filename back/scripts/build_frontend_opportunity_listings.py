#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.section_keys import normalize_section_key_series  # noqa: E402


AVAILABLE_LISTINGS_CSV = PROJECT_ROOT / "storage" / "data" / "exports" / "manual_available_locales_madrid.csv"
SELECTED_LISTINGS_CSV = PROJECT_ROOT / "storage" / "data" / "exports" / "manual_available_locales_madrid_selected.csv"
SELECTED_SUMMARY_JSON = PROJECT_ROOT / "storage" / "data" / "processed" / "manual_available_locales_madrid_selected_summary.json"
WEB_DATA_DIR = PROJECT_ROOT / "front" / "public" / "data"
OPPORTUNITY_DATA_DIR = WEB_DATA_DIR / "opportunities"
OPPORTUNITY_SECTIONS_DATA_DIR = OPPORTUNITY_DATA_DIR / "sections"
FRONTEND_OUTPUT_JSON = OPPORTUNITY_DATA_DIR / "listings.json"
FRONTEND_SECTIONS_INDEX_JSON = OPPORTUNITY_SECTIONS_DATA_DIR / "index.json"

DEFAULT_MAP_BOUNDS = {
    "min_lng": -3.8885,
    "min_lat": 40.3121,
    "max_lng": -3.5174,
    "max_lat": 40.6437,
    "min_zoom": 9.8,
    "max_zoom": 16.2,
}
DEFAULT_SECTION_INDEX_PATH = "/data/opportunities/sections/index.json"
DEFAULT_SECTION_GEOJSON_PATH = "/data/opportunities/sections/geometry.geojson"

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
    "renta_reference_year",
    "renta_granularity_used",
    "renta_outlier_adjusted",
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
    "top_avisos_barrio_categories",
    "top_avisos_district_categories",
    "section_local_count_start",
    "section_unique_activity_category_count_start",
    "section_turnover_rate_12m_start",
    "section_same_activity_category_share_start",
    "best_activity_label",
    "best_activity_risk",
    "best_activity_survival_24m",
    "top_activities",
    "facilities_tier",
    "facilities_200m",
    "facilities_500m",
    "facilities_1000m",
    "facilities_by_category",
    "vulnerabilidad_global",
    "vulnerabilidad_global_media_ciudad",
    "vulnerabilidad_esferas",
    "inspecciones_distrito_total",
    "inspecciones_ciudad_media",
    "inspecciones_top_epigrafes",
    "indicadores_distrito",
]
LIST_FIELDS = [
    "top_activities",
    "facilities_by_category",
    "vulnerabilidad_esferas",
    "inspecciones_top_epigrafes",
    "indicadores_distrito",
    "metro_access_names_500m_start",
    "metro_access_names_1000m_start",
    "metro_station_names_500m_start",
    "metro_station_names_1000m_start",
    "top_avisos_barrio_categories",
    "top_avisos_district_categories",
]
LISTING_INPUT_COLUMNS = {
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
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Actualiza listings.json de oportunidades reutilizando el indice de secciones ya publicado.",
    )
    parser.add_argument("--input-listings-csv", type=Path, default=AVAILABLE_LISTINGS_CSV)
    parser.add_argument("--section-index-json", type=Path, default=FRONTEND_SECTIONS_INDEX_JSON)
    parser.add_argument("--existing-frontend-json", type=Path, default=FRONTEND_OUTPUT_JSON)
    parser.add_argument("--output-frontend-json", type=Path, default=FRONTEND_OUTPUT_JSON)
    parser.add_argument("--selected-output-csv", type=Path, default=SELECTED_LISTINGS_CSV)
    parser.add_argument("--summary-output-json", type=Path, default=SELECTED_SUMMARY_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    selected_listings, filter_summary = build_selected_available_listings(args.input_listings_csv)
    if selected_listings.empty:
        raise ValueError("The weekly opportunity refresh produced zero selected listings.")

    section_profiles = load_section_profiles_from_index_json(args.section_index_json)
    selected_scored = attach_section_context(selected_listings, section_profiles)

    args.selected_output_csv.parent.mkdir(parents=True, exist_ok=True)
    selected_scored[POINT_OUTPUT_COLUMNS].to_csv(args.selected_output_csv, index=False)

    summary = build_selected_summary(selected_scored, filter_summary)
    args.summary_output_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    existing_meta = load_existing_frontend_meta(args.existing_frontend_json)
    frontend_payload = build_frontend_artifacts(selected_scored, filter_summary, existing_meta=existing_meta)
    point_count = len(frontend_payload.get("points", []))
    if point_count <= 0:
        raise ValueError("The weekly opportunity refresh generated an empty frontend payload.")

    args.output_frontend_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_frontend_json.write_text(
        json.dumps(frontend_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    print(f"Selected opportunity listings: {len(selected_scored):,}")
    print(f"Wrote selected CSV: {args.selected_output_csv}")
    print(f"Wrote summary JSON: {args.summary_output_json}")
    print(f"Wrote frontend listings JSON: {args.output_frontend_json}")
    return 0


def load_section_profiles_from_index_json(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("sections", [])
    if not isinstance(rows, list):
        raise ValueError(f"Invalid section index payload in {path}")

    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=["section_key"])

    frame["section_key"] = normalize_section_key_series(frame.get("section_key", pd.Series(pd.NA, index=frame.index))).astype("string")
    frame["district_code"] = frame.get("district_code", pd.Series(pd.NA, index=frame.index)).map(
        lambda value: normalize_admin_code(value, width=2)
    ).astype("string")
    frame["barrio_code"] = frame.get("barrio_code", pd.Series(pd.NA, index=frame.index)).map(
        lambda value: normalize_admin_code(value, width=3)
    ).astype("string")
    frame["district_name"] = frame.get("district_name", pd.Series(pd.NA, index=frame.index)).map(clean_place_name).astype("string")
    frame["barrio_name"] = frame.get("barrio_name", pd.Series(pd.NA, index=frame.index)).map(clean_place_name).astype("string")

    for field in LIST_FIELDS:
        series = frame[field] if field in frame.columns else pd.Series([None] * len(frame), index=frame.index, dtype=object)
        frame[field] = [value if isinstance(value, list) else [] for value in series]

    frame = ensure_output_columns(frame, source="section_index")
    return frame.drop_duplicates(subset=["section_key"], keep="first").reset_index(drop=True)


def attach_section_context(selected_listings: pd.DataFrame, section_profiles: pd.DataFrame) -> pd.DataFrame:
    selected = selected_listings.copy()
    selected["_listing_order"] = np.arange(len(selected), dtype=int)

    merged = selected.merge(section_profiles, how="left", on="section_key", suffixes=("", "_section"))
    missing_mask = merged.get("risk_score", pd.Series(pd.NA, index=merged.index)).isna()
    if bool(missing_mask.any()):
        missing_keys = (
            merged.loc[missing_mask, "section_key"]
            .astype("string")
            .dropna()
            .drop_duplicates()
            .tolist()
        )
        preview = ", ".join(missing_keys[:8]) or "unknown"
        raise ValueError(
            f"{int(missing_mask.sum())} selected listings could not be matched against the tracked section index "
            f"({preview})."
        )

    for column in ["district_code", "district_name", "barrio_code", "barrio_name"]:
        fallback_column = f"{column}_section"
        if fallback_column in merged.columns:
            merged[column] = coalesce_strings(merged.get(column), merged.get(fallback_column))

    for field in LIST_FIELDS:
        merged[field] = [value if isinstance(value, list) else [] for value in merged[field]]

    merged = merged.sort_values("_listing_order").drop(
        columns=[column for column in merged.columns if column.endswith("_section")] + ["_listing_order"]
    )
    return ensure_output_columns(merged, source="merged")


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


def compute_outlier_flags(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    numeric_columns = ["price_eur", "price_per_m2_eur", "area_m2"]
    flag_count = pd.Series(0, index=frame.index, dtype=int)
    reasons = pd.Series("", index=frame.index, dtype="string")

    for _, index_values in frame.groupby(frame["operation"].astype("string").fillna("unknown")).groups.items():
        scoped = frame.loc[list(index_values)]
        for column in numeric_columns:
            series = pd.to_numeric(scoped[column], errors="coerce")
            valid = series.dropna()
            if len(valid) < 8:
                continue
            transformed = np.log1p(valid.clip(lower=0))
            q1 = float(transformed.quantile(0.25))
            q3 = float(transformed.quantile(0.75))
            iqr = q3 - q1
            if not math.isfinite(iqr) or iqr <= 0:
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


def ensure_output_columns(frame: pd.DataFrame, *, source: str) -> pd.DataFrame:
    prepared = frame.copy()
    for column in POINT_OUTPUT_COLUMNS:
        if column in prepared.columns:
            continue
        if column in LIST_FIELDS:
            prepared[column] = [[] for _ in range(len(prepared))]
        elif source == "section_index" and column in LISTING_INPUT_COLUMNS:
            prepared[column] = pd.NA
        else:
            prepared[column] = pd.NA
    return prepared


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


def build_frontend_artifacts(
    selected_scored: pd.DataFrame,
    filter_summary: dict[str, object],
    *,
    existing_meta: dict[str, object] | None,
) -> dict[str, object]:
    points = [build_point_payload(row) for row in selected_scored.itertuples(index=False)]
    generated_at = pd.Timestamp.utcnow().isoformat()
    stats = {
        "selected_listings": int(len(selected_scored)),
        "districts": int(selected_scored["district_code"].dropna().nunique()),
        "barrios": count_unique_barrio_scopes(selected_scored),
        "median_survival_24m": serialize_probability(pd.to_numeric(selected_scored["expected_survival_24m"], errors="coerce").median()),
        "median_price_per_m2": serialize_probability(pd.to_numeric(selected_scored["price_per_m2_eur"], errors="coerce").median()),
    }
    meta = existing_meta or {}
    map_bounds = meta.get("map_bounds") if isinstance(meta.get("map_bounds"), dict) else DEFAULT_MAP_BOUNDS
    return {
        "meta": {
            "title": str(meta.get("title") or "Madrid Opportunity Map"),
            "subtitle": str(meta.get("subtitle") or "Locales disponibles y recomendacion de actividad"),
            "generated_at": generated_at,
            "section_index_path": str(meta.get("section_index_path") or DEFAULT_SECTION_INDEX_PATH),
            "section_geojson_path": str(meta.get("section_geojson_path") or DEFAULT_SECTION_GEOJSON_PATH),
            "map_bounds": map_bounds,
        },
        "filters": _to_jsonable(filter_summary),
        "stats": _to_jsonable(stats),
        "points": _to_jsonable(points),
    }


def load_existing_frontend_meta(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    meta = payload.get("meta")
    return meta if isinstance(meta, dict) else None


def build_point_payload(row: object) -> dict[str, object]:
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
        "top_activities": getattr(row, "top_activities", []) or [],
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


def normalize_admin_code(value: object, *, width: int) -> str | None:
    digits = "".join(character for character in str(value or "") if character.isdigit())
    if not digits:
        return None
    return digits.zfill(width)[-width:]


def clean_place_name(value: object) -> object:
    if value is None or pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    return text.title()


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


def serialize_probability(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


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


def serialize_avisos_top_categories(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []

    rows: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue

        label = serialize_optional_text(item.get("label"))
        if not label:
            continue

        rank = pd.to_numeric(item.get("rank"), errors="coerce")
        count = pd.to_numeric(item.get("count"), errors="coerce")
        rows.append(
            {
                "rank": int(rank) if pd.notna(rank) else len(rows) + 1,
                "label": label,
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
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if value is None or pd.isna(value):
        return None
    return value


if __name__ == "__main__":
    raise SystemExit(main())
