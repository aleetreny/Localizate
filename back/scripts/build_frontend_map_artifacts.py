#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import duckdb
import h3
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


import localizate.abt_survival as activity_abt_survival


WEB_DATA_DIR = PROJECT_ROOT / "front" / "public" / "data"
MAP_DATA_DIR = WEB_DATA_DIR / "map"
MAP_HEX_DATA_DIR = MAP_DATA_DIR / "hex"
MAP_HISTORICAL_DATA_DIR = MAP_DATA_DIR / "historical"
MAP_ZONES_DATA_DIR = MAP_DATA_DIR / "zones"
MAP_SHARED_OUTPUT = MAP_DATA_DIR / "shared.json"
DEFAULT_OUTPUT = MAP_HEX_DATA_DIR / "small.json"
MEDIUM_OUTPUT = MAP_HEX_DATA_DIR / "medium.json"
LARGE_OUTPUT = MAP_HEX_DATA_DIR / "large.json"
HISTORICAL_RANKING_OUTPUT = MAP_HISTORICAL_DATA_DIR / "rankings.json"
HEX_COMPOSITION_HISTORY_OUTPUT = MAP_HISTORICAL_DATA_DIR / "hex-composition.json"
HEX_COMPOSITION_HISTORY_PARTS_DIR = MAP_HISTORICAL_DATA_DIR / "hex-composition"
HEX_COMPOSITION_HISTORY_MANIFEST_OUTPUT = MAP_HISTORICAL_DATA_DIR / "hex-composition.manifest.json"
HEX_COMPOSITION_HISTORY_PREFIX_PARTS_DIR = MAP_HISTORICAL_DATA_DIR / "hex-composition-by-prefix"
HEX_COMPOSITION_HISTORY_PREFIX_MANIFEST_OUTPUT = MAP_HISTORICAL_DATA_DIR / "hex-composition.by-prefix.manifest.json"
HEX_COMPOSITION_HISTORY_PREFIX_LENGTH = 10
ZONE_BOUNDARY_OUTPUT = MAP_ZONES_DATA_DIR / "boundaries.json"
ACTIVITY_GLOSSARY = PROJECT_ROOT / "docs" / "reference" / "ACTIVITY_GLOSSARY.md"
ACTIVITY_NORMALIZATION_AUDIT = PROJECT_ROOT / "storage" / "data" / "processed" / "activity_code_normalization_audit.csv"
ACTIVITY_MACRO_TAXONOMY = PROJECT_ROOT / "storage" / "data" / "processed" / "activity_macro_taxonomy.csv"
HISTORICAL_LOCALES_DIR = PROJECT_ROOT / "storage" / "data" / "processed" / "censo_geospatial" / "locales"
HISTORICAL_ACTIVITIES_DIR = PROJECT_ROOT / "storage" / "data" / "intermediate" / "censo_snapshots" / "actividades"
SPATIAL_FALLBACK_CRS = "EPSG:25830"
SPATIAL_NEAREST_MAX_DISTANCE_M = 75.0
ZONE_BOUNDARY_SIMPLIFY_TOLERANCE_M = 8.0
GEOGRAPHY_COLUMNS = ("district_code", "district_name", "barrio_code", "barrio_name")
HEX_SIZE_SPECS = (
    {"key": "small", "label": "Pequeño", "resolution_offset": 0, "output_path": DEFAULT_OUTPUT},
    {"key": "medium", "label": "Mediano", "resolution_offset": 1, "output_path": MEDIUM_OUTPUT},
    {"key": "large", "label": "Grande", "resolution_offset": 2, "output_path": LARGE_OUTPUT},
)
MAP_BOUNDS = {
    "min_lng": -3.888,
    "min_lat": 40.312,
    "max_lng": -3.517,
    "max_lat": 40.643,
    "min_zoom": 9.8,
    "max_zoom": 15.4,
}
PRIMARY_RISK_COLUMN = "risk_cox"
PRIMARY_RISK_MODEL_KEY = "cox"
PRIMARY_RISK_MODEL_LABEL = "Cox"
HISTORICAL_METRIC_KEY = "specialization_index"
HISTORICAL_METRIC_LABEL = "Indice de especializacion"
HISTORICAL_METRIC_SHORT_LABEL = "Especializacion vs Madrid"
HISTORICAL_METRIC_DEFINITION = (
    "Cuota suavizada de la categoria en cada zona comparada con la cuota de esa misma categoria en Madrid para el mismo ano. "
    "Valores por encima de 1 indican que la categoria pesa mas en esa zona que en el conjunto de la ciudad."
)
HISTORICAL_METRIC_DIRECTION = "higher_better"
HISTORICAL_SMOOTHING_WEIGHT = 12.0
HISTORICAL_CURRENT_SERIES_LIMIT = 4
HISTORICAL_SERIES_LIMIT = 12
HISTORICAL_RANK_FOCUS_LIMIT = 12
HEX_COMPOSITION_HISTORY_YEAR_MIN = 2015
HEX_COMPOSITION_HISTORY_YEAR_MAX = 2026
HIDDEN_SELECTOR_STATUS_CATEGORY_CODES = frozenset(
    {
        "__status_no_activity__",
        "__status_missing_snapshot__",
        "__status_pending_coding__",
    }
)
UNKNOWN_ACTIVITY_CATEGORY_METADATA = {
    "__status_multi_activity__": {
        "desc": "Multiactividad",
        "definition": "El local arranca con varias macrocategorias simultaneas en el mismo periodo. No se fuerza una unica categoria porque distorsionaria la lectura historica.",
    },
    "__status_no_activity__": {
        "desc": "Sin actividad declarada",
        "definition": "La fuente historica marca el local como sin actividad en su periodo inicial, asi que no existe una categoria comercial activa que mostrar.",
    },
    "__status_uncoded_activity__": {
        "desc": "Actividad no informada",
        "definition": "Existe fila de actividad en origen, pero sin un epigrafe utilizable o con valor nulo. No se puede asignar una macrocategoria fiable con los datos actuales.",
    },
    "__status_pending_coding__": {
        "desc": "Actividad pendiente de codificar",
        "definition": "La fuente conserva el local, pero deja su actividad pendiente de codificar. Se mantiene aparte hasta disponer de un epigrafe valido.",
    },
    "__status_missing_snapshot__": {
        "desc": "Mes sin fichero de actividad",
        "definition": "Falta el fichero mensual de actividad para el periodo inicial del local. Es un hueco puntual de fuente, no una categoria comercial.",
    },
    "__status_unmapped_activity__": {
        "desc": "Actividad fuera de taxonomia",
        "definition": "La actividad tiene un epigrafe valido, pero todavia no cae en una macrocategoria del glosario historico. Es una señal de cobertura pendiente, no de cierre.",
    },
}


def main() -> int:
    MAP_SHARED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    HISTORICAL_RANKING_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    HEX_COMPOSITION_HISTORY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    HEX_COMPOSITION_HISTORY_PARTS_DIR.mkdir(parents=True, exist_ok=True)
    HEX_COMPOSITION_HISTORY_PREFIX_PARTS_DIR.mkdir(parents=True, exist_ok=True)
    ZONE_BOUNDARY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    section_geography = pd.read_csv(
        PROJECT_ROOT / "storage" / "data" / "processed" / "section_geography.csv",
        usecols=["section_key", "district_code", "district_name", "barrio_code", "barrio_name"],
        dtype={
            "section_key": "string",
            "district_code": "string",
            "district_name": "string",
            "barrio_code": "string",
            "barrio_name": "string",
        },
        low_memory=False,
    )
    section_geography["section_key"] = section_geography["section_key"].astype("string").str.zfill(5)
    section_geography = normalize_geography_columns(section_geography)

    abt = pd.read_csv(
        PROJECT_ROOT / "storage" / "data" / "features" / "activity_survival_abt.csv",
        usecols=[
            "id_local",
            "first_seen_period",
            "h3_cell_start",
            "duration_months",
            "event_observed",
            "activity_category_code_start",
            "activity_category_desc_start",
        ],
        low_memory=False,
    )
    scores = pd.read_csv(
        PROJECT_ROOT / "storage" / "data" / "exports" / "activity_survival_map_export.csv",
        usecols=[
            "id_local",
            "h3_cell_start",
            "section_key_start",
            "lat_wgs84_start",
            "lon_wgs84_start",
            PRIMARY_RISK_COLUMN,
            "quality_tier",
        ],
        low_memory=False,
    )

    merged = abt.merge(scores, on=["id_local", "h3_cell_start"], how="inner", validate="one_to_one")
    merged = merged[merged["h3_cell_start"].notna()].copy()
    merged = apply_frontend_activity_categories(merged)
    merged["duration_months"] = pd.to_numeric(merged["duration_months"], errors="coerce").fillna(0.0)
    merged["event_observed"] = pd.to_numeric(merged["event_observed"], errors="coerce").fillna(0).astype(int)
    merged["risk_primary"] = pd.to_numeric(merged[PRIMARY_RISK_COLUMN], errors="coerce").fillna(0.0)
    merged["risk_percentile"] = merged["risk_primary"].rank(method="average", pct=True)
    merged["lat_wgs84_start"] = pd.to_numeric(merged["lat_wgs84_start"], errors="coerce")
    merged["lon_wgs84_start"] = pd.to_numeric(merged["lon_wgs84_start"], errors="coerce")
    merged, geography_stats = attach_section_geography(merged, section_geography=section_geography)

    all_rows = merged.copy()
    all_rows["category_code"] = "__all__"
    all_rows["category_desc"] = "Todos los locales"
    merged = pd.concat([all_rows, merged], ignore_index=True)

    glossary_profiles = parse_activity_glossary(ACTIVITY_GLOSSARY)
    zones = build_zone_payloads(merged)
    generated_at = pd.Timestamp.utcnow().isoformat()
    base_h3_resolution = detect_h3_resolution(merged["h3_cell_start"])
    historical_payload = build_historical_ranking_artifacts(generated_at=generated_at)
    zone_boundary_payload = build_zone_boundary_artifacts(generated_at=generated_at)

    HISTORICAL_RANKING_OUTPUT.write_text(
        json.dumps(historical_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    print(
        f"Wrote historical ranking artifacts: {HISTORICAL_RANKING_OUTPUT} "
        f"(district_rows={len(historical_payload['zones']['district']):,}, barrio_rows={len(historical_payload['zones']['barrio']):,})"
    )

    ZONE_BOUNDARY_OUTPUT.write_text(
        json.dumps(zone_boundary_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    print(
        f"Wrote zone boundary artifacts: {ZONE_BOUNDARY_OUTPUT} "
        f"(district_features={len(zone_boundary_payload['zones']['district']['features']):,}, "
        f"barrio_features={len(zone_boundary_payload['zones']['barrio']['features']):,})"
    )

    hex_composition_payload = build_hex_composition_history_artifacts(generated_at=generated_at)
    HEX_COMPOSITION_HISTORY_OUTPUT.write_text(
        json.dumps(hex_composition_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    print(
        f"Wrote hex composition history artifacts: {HEX_COMPOSITION_HISTORY_OUTPUT} "
        f"(rows={len(hex_composition_payload['hexes']):,}, years={len(hex_composition_payload['meta']['years']):,})"
    )
    hex_composition_manifest = write_hex_composition_history_manifest(hex_composition_payload)
    print(
        f"Wrote hex composition manifest: {HEX_COMPOSITION_HISTORY_MANIFEST_OUTPUT} "
        f"(parts={len(hex_composition_manifest['parts']):,})"
    )
    hex_composition_prefix_manifest = write_hex_composition_history_prefix_manifest(hex_composition_payload)
    print(
        f"Wrote hex composition prefix manifest: {HEX_COMPOSITION_HISTORY_PREFIX_MANIFEST_OUTPUT} "
        f"(shards={hex_composition_prefix_manifest['shard_count']:,}, "
        f"prefix_length={hex_composition_prefix_manifest['prefix_length']})"
    )

    hex_specs = build_hex_size_specs(base_h3_resolution)
    shared_payload = None

    for spec in hex_specs:
        sized_frame = roll_up_hex_frame(merged, target_resolution=int(spec["h3_resolution"]))
        hexes = build_hex_aggregates(sized_frame, hex_cell_col="hex_h3_cell")
        categories = build_category_options(hexes, glossary_profiles)
        if shared_payload is None:
            shared_payload = build_map_shared_payload(
                generated_at=generated_at,
                categories=categories,
                zones=zones,
            )
        payload = build_map_hex_payload(
            generated_at=generated_at,
            spec=spec,
            hexes=hexes,
        )
        output_path = Path(spec["output_path"])
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        print(
            f"Wrote {spec['label'].lower()} frontend hex artifacts: {output_path} "
            f"(res={spec['h3_resolution']}, area_km2~{float(spec['hex_area_km2']):.4f}, hex_rows={len(hexes):,})"
        )

    if shared_payload is None:
        raise RuntimeError("No se pudo construir el payload compartido del mapa.")

    MAP_SHARED_OUTPUT.write_text(
        json.dumps(shared_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    print(
        f"Wrote shared frontend map artifacts: {MAP_SHARED_OUTPUT} "
        f"(categories={len(shared_payload['categories']):,}, "
        f"district_rows={len(shared_payload['zones']['district']):,}, "
        f"barrio_rows={len(shared_payload['zones']['barrio']):,})"
    )

    print(f"Direct section geography matches: {geography_stats['matched_from_section_key']:,}")
    print(f"Coordinate geography backfills: {geography_stats['backfilled_from_coordinates']:,}")
    print(f"Rows still missing geography: {geography_stats['remaining_missing_geography']:,}")
    return 0


def build_map_shared_payload(
    *,
    generated_at: str,
    categories: list[dict[str, object]],
    zones: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    return {
        "meta": {
            "title": "Madrid Survival Grid",
            "subtitle": "Mapa H3 minimalista listo para plasmar regiones de prediccion y filtrar por tipo de local.",
            "generated_at": generated_at,
            "defaultCategoryCode": "__all__",
            "risk_model_key": PRIMARY_RISK_MODEL_KEY,
            "risk_model_label": PRIMARY_RISK_MODEL_LABEL,
            "map_bounds": MAP_BOUNDS,
        },
        "categories": categories,
        "zones": zones,
    }


def build_map_hex_payload(
    *,
    generated_at: str,
    spec: dict[str, object],
    hexes: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "meta": {
            "generated_at": generated_at,
            "hex_size": str(spec["key"]),
            "h3_resolution": int(spec["h3_resolution"]),
            "hex_area_km2": float(spec["hex_area_km2"]),
        },
        "hexes": hexes,
    }


def apply_frontend_activity_categories(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["category_code"] = result["activity_category_code_start"].astype("string")
    result["category_desc"] = result["activity_category_desc_start"].astype("string")

    unknown_mask = result["category_code"].isna() | result["category_desc"].isna()
    if unknown_mask.any():
        unknown_targets = result.loc[unknown_mask, ["id_local", "first_seen_period"]].drop_duplicates().copy()
        derived = classify_unknown_activity_categories(unknown_targets)
        if not derived.empty:
            result = result.merge(derived, on=["id_local", "first_seen_period"], how="left")
            result["category_code"] = result["category_code"].fillna(result["derived_category_code"])
            result["category_desc"] = result["category_desc"].fillna(result["derived_category_desc"])
            result = result.drop(columns=["derived_category_code", "derived_category_desc"], errors="ignore")

    fallback = UNKNOWN_ACTIVITY_CATEGORY_METADATA["__status_uncoded_activity__"]
    result["category_code"] = result["category_code"].fillna("__status_uncoded_activity__").astype("string")
    result["category_desc"] = result["category_desc"].fillna(str(fallback["desc"])).astype("string")
    return result


def classify_unknown_activity_categories(targets: pd.DataFrame) -> pd.DataFrame:
    if targets.empty:
        return pd.DataFrame(columns=["id_local", "first_seen_period", "derived_category_code", "derived_category_desc"])

    audit = pd.read_csv(PROJECT_ROOT / "storage" / "data" / "processed" / "activity_code_normalization_audit.csv", low_memory=False)
    epigrafe_lookup = activity_abt_survival._collapse_activity_lookup_by_raw_code(
        audit[audit["taxonomy"] == "epigrafe"].copy()
    )
    for column in ["raw_code", "clean_code"]:
        epigrafe_lookup[column] = epigrafe_lookup[column].fillna("").astype(str).str.upper().str.strip()

    macro_lookup = pd.read_csv(
        PROJECT_ROOT / "storage" / "data" / "processed" / "activity_macro_taxonomy.csv",
        usecols=["epigrafe_code", "macro_category_code", "macro_category_name"],
        dtype="string",
        low_memory=False,
    ).dropna(subset=["epigrafe_code", "macro_category_code", "macro_category_name"])
    macro_lookup["epigrafe_code"] = macro_lookup["epigrafe_code"].astype("string").str.upper().str.strip()
    macro_lookup["macro_category_code"] = macro_lookup["macro_category_code"].astype("string").str.strip()
    macro_lookup["macro_category_name"] = macro_lookup["macro_category_name"].astype("string").str.strip()
    macro_lookup = macro_lookup.drop_duplicates()

    prepared_targets = targets.copy()
    prepared_targets["id_local"] = pd.to_numeric(prepared_targets["id_local"], errors="coerce").astype("Int64")
    prepared_targets["first_seen_period"] = prepared_targets["first_seen_period"].astype("string")
    prepared_targets = prepared_targets.dropna(subset=["id_local", "first_seen_period"])
    if prepared_targets.empty:
        return pd.DataFrame(columns=["id_local", "first_seen_period", "derived_category_code", "derived_category_desc"])

    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    con.register("targets_df", prepared_targets[["id_local", "first_seen_period"]])
    con.register("epigrafe_lookup_df", epigrafe_lookup[["raw_code", "clean_code", "code_valid"]])
    con.register("macro_lookup_df", macro_lookup)

    activities_glob = str(PROJECT_ROOT / "storage" / "data" / "intermediate" / "censo_snapshots" / "actividades" / "*.csv.gz")
    summary = con.execute(
        """
        WITH raw_activity AS (
            SELECT
                t.id_local,
                t.first_seen_period,
                CASE WHEN a.id_local IS NULL THEN 0 ELSE 1 END AS matched_row,
                COALESCE(TRIM(UPPER(CAST(a.id_epigrafe AS VARCHAR))), '') AS epigrafe_raw_code,
                COALESCE(TRIM(UPPER(CAST(a.desc_epigrafe AS VARCHAR))), '') AS epigrafe_raw_desc
            FROM targets_df t
            LEFT JOIN read_csv_auto(?, union_by_name=true) a
              ON CAST(a.id_local AS BIGINT) = t.id_local
             AND CAST(a.snapshot_period AS VARCHAR) = t.first_seen_period
        ),
        enriched AS (
            SELECT
                r.*,
                CAST(COALESCE(e.code_valid, FALSE) AS BOOLEAN) AS epigrafe_valid,
                COALESCE(m.macro_category_code, '') AS macro_category_code,
                COALESCE(m.macro_category_name, '') AS macro_category_desc
            FROM raw_activity r
            LEFT JOIN epigrafe_lookup_df e
              ON r.epigrafe_raw_code = e.raw_code
            LEFT JOIN macro_lookup_df m
              ON e.clean_code = m.epigrafe_code
        )
        SELECT
            id_local,
            first_seen_period,
            SUM(matched_row) AS raw_rows,
            SUM(CASE WHEN epigrafe_valid THEN 1 ELSE 0 END) AS valid_epigrafe_rows,
            COUNT(DISTINCT CASE WHEN macro_category_code <> '' THEN macro_category_code END) AS macro_count,
            MIN(CASE WHEN macro_category_code <> '' THEN macro_category_code END) AS single_macro_code,
            MIN(CASE WHEN macro_category_desc <> '' THEN macro_category_desc END) AS single_macro_desc,
            MAX(CASE WHEN matched_row = 1 AND (epigrafe_raw_code IN ('000000', '0', '0.0') OR epigrafe_raw_desc = 'LOCAL SIN ACTIVIDAD') THEN 1 ELSE 0 END) AS has_no_activity_marker,
            MAX(CASE WHEN matched_row = 1 AND (epigrafe_raw_code LIKE 'PTE%' OR epigrafe_raw_desc LIKE 'PTE.%') THEN 1 ELSE 0 END) AS has_pending_coding_marker,
            MAX(CASE WHEN matched_row = 1 AND epigrafe_raw_code = '' AND epigrafe_raw_desc = '' THEN 1 ELSE 0 END) AS has_blank_marker,
            MAX(CASE WHEN matched_row = 1 AND (epigrafe_raw_code = '-1' OR epigrafe_raw_desc = 'VALOR NULO EN ORIGEN') THEN 1 ELSE 0 END) AS has_null_origin_marker
        FROM enriched
        GROUP BY 1, 2
        """,
        [activities_glob],
    ).df()
    con.close()

    if summary.empty:
        return pd.DataFrame(columns=["id_local", "first_seen_period", "derived_category_code", "derived_category_desc"])

    derived = summary.apply(
        lambda row: pd.Series(infer_unknown_activity_category(row.to_dict())),
        axis=1,
    )
    derived.columns = ["derived_category_code", "derived_category_desc"]
    return pd.concat([summary[["id_local", "first_seen_period"]], derived], axis=1)


def infer_unknown_activity_category(record: dict[str, object]) -> tuple[str, str]:
    raw_rows = int(record.get("raw_rows") or 0)
    macro_count = int(record.get("macro_count") or 0)
    valid_epigrafe_rows = int(record.get("valid_epigrafe_rows") or 0)
    single_macro_code = str(record.get("single_macro_code") or "").strip()
    single_macro_desc = str(record.get("single_macro_desc") or "").strip()

    if raw_rows == 0:
        return status_category_payload("__status_missing_snapshot__")
    if macro_count == 1 and single_macro_code and single_macro_desc:
        return single_macro_code, single_macro_desc
    if macro_count >= 2:
        return status_category_payload("__status_multi_activity__")
    if bool(record.get("has_no_activity_marker")):
        return status_category_payload("__status_no_activity__")
    if bool(record.get("has_pending_coding_marker")):
        return status_category_payload("__status_pending_coding__")
    if valid_epigrafe_rows > 0:
        return status_category_payload("__status_unmapped_activity__")
    if bool(record.get("has_blank_marker")) or bool(record.get("has_null_origin_marker")):
        return status_category_payload("__status_uncoded_activity__")
    return status_category_payload("__status_uncoded_activity__")


def status_category_payload(category_code: str) -> tuple[str, str]:
    metadata = UNKNOWN_ACTIVITY_CATEGORY_METADATA[category_code]
    return category_code, str(metadata["desc"])


def is_status_category_code(category_code: str) -> bool:
    return category_code in UNKNOWN_ACTIVITY_CATEGORY_METADATA


def should_include_in_category_selector(category_code: str) -> bool:
    return category_code not in HIDDEN_SELECTOR_STATUS_CATEGORY_CODES


def resolve_primary_risk_column(frame: pd.DataFrame) -> str:
    if "risk_primary" in frame.columns:
        return "risk_primary"
    return "risk_ensemble"


def build_hex_aggregates(frame: pd.DataFrame, *, hex_cell_col: str = "h3_cell_start") -> list[dict[str, object]]:
    primary_risk_col = resolve_primary_risk_column(frame)
    grouped = frame.groupby([hex_cell_col, "category_code", "category_desc"], dropna=False)
    rows: list[dict[str, object]] = []
    for (h3_cell, category_code, category_desc), part in grouped:
        duration = part["duration_months"]
        event = part["event_observed"]
        district_name = dominant_place_name(part["district_name"])
        barrio_name = dominant_place_name(part["barrio_name"])
        support_12m, survival_12m = compute_horizon_metrics(duration, event, horizon=12.0)
        support_24m, survival_24m = compute_horizon_metrics(duration, event, horizon=24.0)
        quality_tier = quality_mode(part["quality_tier"].astype("string"))
        avg_risk_primary = float(part[primary_risk_col].mean())
        rows.append(
            {
                "h3_cell": str(h3_cell),
                "category_code": str(category_code),
                "category_desc": str(category_desc),
                "district_name": district_name,
                "barrio_name": barrio_name,
                "location_label": build_location_label(barrio_name, district_name),
                "n_locales": int(len(part)),
                "n_events": int(event.sum()),
                "avg_risk_primary": avg_risk_primary,
                "avg_risk_ensemble": avg_risk_primary,
                "avg_risk_percentile": float(part["risk_percentile"].mean()),
                "survival_12m": serialize_probability(survival_12m),
                "survival_24m": serialize_probability(survival_24m),
                "support_12m": int(support_12m),
                "support_24m": int(support_24m),
                "quality_tier": quality_tier,
            }
        )
    rows.sort(key=lambda item: (item["category_desc"], -int(item["n_locales"]), item["h3_cell"]))
    return rows


def build_category_options(hexes: list[dict[str, object]], glossary_profiles: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    frame = pd.DataFrame(hexes)
    grouped = (
        frame.groupby(["category_code", "category_desc"], dropna=False)
        .agg(n_locales=("n_locales", "sum"), n_hexes=("h3_cell", "nunique"))
        .reset_index()
        .sort_values(["category_code", "n_locales"], ascending=[True, False])
    )
    rows = grouped.to_dict(orient="records")
    glossary_total_epigraphs = sum(int(profile.get("mapped_epigraphs") or 0) for profile in glossary_profiles.values())
    glossary_total_rows = sum(int(profile.get("historical_coverage_rows") or 0) for profile in glossary_profiles.values())
    common_examples = [
        str(item["category_desc"])
        for item in sorted(rows, key=lambda item: (-int(item["n_locales"]), str(item["category_desc"])))
        if str(item["category_code"]) not in {"__all__", "__unknown__"} and not is_status_category_code(str(item["category_code"]))
    ][:5]

    for item in rows:
        item["n_locales"] = int(item["n_locales"])
        item["n_hexes"] = int(item["n_hexes"])
        item.update(
            build_category_profile(
                category_code=str(item["category_code"]),
                category_desc=str(item["category_desc"]),
                glossary_profiles=glossary_profiles,
                glossary_total_epigraphs=glossary_total_epigraphs,
                glossary_total_rows=glossary_total_rows,
                common_examples=common_examples,
            )
        )

    rows = [item for item in rows if should_include_in_category_selector(str(item["category_code"]))]

    rows.sort(
        key=lambda item: (
            0 if str(item["category_code"]) == "__all__" else 2 if is_status_category_code(str(item["category_code"])) else 1,
            -int(item["n_locales"]),
            item["category_desc"],
        )
    )
    return rows


def build_zone_payloads(frame: pd.DataFrame) -> dict[str, list[dict[str, object]]]:
    return {
        "district": build_zone_metrics(
            frame,
            zone_level="district",
            zone_code_col="district_code",
            zone_name_col="district_name",
        ),
        "barrio": build_zone_metrics(
            frame,
            zone_level="barrio",
            zone_code_col="barrio_code",
            zone_name_col="barrio_name",
            zone_context_col="district_name",
        ),
    }


def build_zone_metrics(
    frame: pd.DataFrame,
    *,
    zone_level: str,
    zone_code_col: str,
    zone_name_col: str,
    zone_context_col: str | None = None,
) -> list[dict[str, object]]:
    primary_risk_col = resolve_primary_risk_column(frame)
    scoped = frame.copy()
    scoped[zone_name_col] = scoped[zone_name_col].fillna("").astype("string").map(clean_place_name)
    scoped[zone_code_col] = scoped[zone_code_col].fillna("").astype("string")
    if zone_context_col:
        scoped[zone_context_col] = scoped[zone_context_col].fillna("").astype("string").map(clean_place_name)
    scoped = scoped[scoped[zone_name_col].ne("")].copy()

    min_locales = 80 if zone_level == "district" else 40
    min_events = 12 if zone_level == "district" else 8

    rows: list[dict[str, object]] = []
    grouped = scoped.groupby([zone_code_col, zone_name_col, "category_code", "category_desc"], dropna=False)
    for (zone_code, zone_name, category_code, category_desc), part in grouped:
        duration = part["duration_months"]
        event = part["event_observed"]
        zone_context_name = dominant_place_name(part[zone_context_col]) if zone_context_col else ""
        support_12m, survival_12m = compute_horizon_metrics(duration, event, horizon=12.0)
        support_24m, survival_24m = compute_horizon_metrics(duration, event, horizon=24.0)
        n_locales = int(len(part))
        n_events = int(event.sum())
        avg_risk_primary = float(part[primary_risk_col].mean())
        rows.append(
            {
                "zone_level": zone_level,
                "zone_code": str(zone_code),
                "zone_name": str(zone_name),
                "zone_context_name": str(zone_context_name) if zone_context_name else None,
                "category_code": str(category_code),
                "category_desc": str(category_desc),
                "n_locales": n_locales,
                "n_events": n_events,
            "avg_risk_primary": avg_risk_primary,
            "avg_risk_ensemble": avg_risk_primary,
                "avg_risk_percentile": float(part["risk_percentile"].mean()),
                "event_rate": float(n_events / n_locales) if n_locales > 0 else 0.0,
                "duration_median_months": float(duration.median()) if duration.notna().any() else 0.0,
                "survival_12m": survival_12m,
                "survival_24m": survival_24m,
                "support_12m": int(support_12m),
                "support_24m": int(support_24m),
                "supported_for_stats": bool(n_locales >= min_locales and n_events >= min_events),
                "confidence_tier": zone_confidence_tier(n_locales=n_locales, n_events=n_events, zone_level=zone_level),
            }
        )

    if not rows:
        return []

    out = pd.DataFrame(rows)
    out["rank_within_zone_risk"] = (
        out.sort_values(["zone_code", "avg_risk_primary", "avg_risk_percentile", "n_locales"], ascending=[True, True, True, False])
        .groupby("zone_code")
        .cumcount()
        + 1
    )
    out["rank_within_zone_12m"] = (
        out.sort_values(["zone_code", "survival_12m", "survival_24m", "n_locales"], ascending=[True, False, False, False])
        .groupby("zone_code")
        .cumcount()
        + 1
    )
    out["rank_within_zone_24m"] = (
        out.sort_values(["zone_code", "survival_24m", "survival_12m", "n_locales"], ascending=[True, False, False, False])
        .groupby("zone_code")
        .cumcount()
        + 1
    )
    out = out.sort_values(["zone_level", "zone_name", "rank_within_zone_risk", "category_desc"]).reset_index(drop=True)

    records: list[dict[str, object]] = []
    for row in out.itertuples(index=False):
        records.append(
            {
                "zone_level": str(row.zone_level),
                "zone_code": str(row.zone_code),
                "zone_name": str(row.zone_name),
                "zone_context_name": str(row.zone_context_name) if pd.notna(row.zone_context_name) and str(row.zone_context_name).strip() else None,
                "category_code": str(row.category_code),
                "category_desc": str(row.category_desc),
                "n_locales": int(row.n_locales),
                "n_events": int(row.n_events),
                "avg_risk_primary": float(row.avg_risk_primary),
                "avg_risk_ensemble": float(row.avg_risk_ensemble),
                "avg_risk_percentile": float(row.avg_risk_percentile),
                "event_rate": float(row.event_rate),
                "duration_median_months": float(row.duration_median_months),
                "survival_12m": serialize_probability(row.survival_12m),
                "survival_24m": serialize_probability(row.survival_24m),
                "support_12m": int(row.support_12m),
                "support_24m": int(row.support_24m),
                "supported_for_stats": bool(row.supported_for_stats),
                "confidence_tier": str(row.confidence_tier),
                "rank_within_zone_risk": int(row.rank_within_zone_risk),
                "rank_within_zone_12m": int(row.rank_within_zone_12m),
                "rank_within_zone_24m": int(row.rank_within_zone_24m),
            }
        )
    return records


def build_category_profile(
    *,
    category_code: str,
    category_desc: str,
    glossary_profiles: dict[str, dict[str, object]],
    glossary_total_epigraphs: int,
    glossary_total_rows: int,
    common_examples: list[str],
) -> dict[str, object]:
    if category_code == "__all__":
        return {
            "definition": "Vista agregada de todos los locales con H3 visible, sin filtrar por macrocategoría.",
            "mapped_epigraphs": glossary_total_epigraphs,
            "historical_coverage_rows": glossary_total_rows,
            "example_labels": common_examples,
        }

    if category_code == "__unknown__":
        return {
            "definition": "Locales sin macrocategoría normalizada en el ABT actual o sin clasificación suficiente para entrar en el glosario.",
            "mapped_epigraphs": None,
            "historical_coverage_rows": None,
            "example_labels": [],
        }

    if is_status_category_code(category_code):
        metadata = UNKNOWN_ACTIVITY_CATEGORY_METADATA[category_code]
        return {
            "definition": str(metadata["definition"]),
            "mapped_epigraphs": None,
            "historical_coverage_rows": None,
            "example_labels": [],
        }

    profile = glossary_profiles.get(category_code)
    if profile:
        return profile

    return {
        "definition": f"Macrocategoría comercial agregada en el ABT histórico para {category_desc.lower()}.",
        "mapped_epigraphs": None,
        "historical_coverage_rows": None,
        "example_labels": [],
    }


def parse_activity_glossary(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}

    profiles: dict[str, dict[str, object]] = {}
    current_title: str | None = None
    current: dict[str, object] = {}

    def flush_current() -> None:
        if current_title and current.get("category_code"):
            profiles[str(current["category_code"])] = {
                "definition": str(current.get("definition") or ""),
                "mapped_epigraphs": current.get("mapped_epigraphs"),
                "historical_coverage_rows": current.get("historical_coverage_rows"),
                "example_labels": list(current.get("example_labels") or []),
            }

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            flush_current()
            current_title = line[3:].strip()
            current = {"title": current_title, "example_labels": []}
            continue
        if not current_title or not line.startswith("- "):
            continue
        if line.startswith("- Código:"):
            current["category_code"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Definición:"):
            current["definition"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Epígrafes mapeados:"):
            current["mapped_epigraphs"] = parse_integer_token(line)
        elif line.startswith("- Cobertura histórica bruta:"):
            current["historical_coverage_rows"] = parse_integer_token(line)
        elif line.startswith("- Ejemplos de etiquetas finas:"):
            examples = line.split(":", 1)[1].strip()
            current["example_labels"] = [item.strip() for item in examples.split(",") if item.strip()]

    flush_current()
    return profiles


def parse_integer_token(text: str) -> int | None:
    match = re.search(r"([\d,]+)", text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def build_historical_ranking_artifacts(*, generated_at: str) -> dict[str, object]:
    common_periods = select_latest_periods_by_year(
        sorted(set(list_snapshot_periods(HISTORICAL_LOCALES_DIR)).intersection(list_snapshot_periods(HISTORICAL_ACTIVITIES_DIR)))
    )

    if not common_periods:
        return {
            "meta": {
                "title": "Madrid Historical Category Ranking",
                "subtitle": "Ranking anual por especializacion relativa de cada categoria usando el ultimo mes disponible de cada ano.",
                "generated_at": generated_at,
                "metric_key": HISTORICAL_METRIC_KEY,
                "metric_label": HISTORICAL_METRIC_LABEL,
                "metric_short_label": HISTORICAL_METRIC_SHORT_LABEL,
                "metric_definition": HISTORICAL_METRIC_DEFINITION,
                "metric_direction": HISTORICAL_METRIC_DIRECTION,
                "smoothing_weight": int(HISTORICAL_SMOOTHING_WEIGHT),
                "years": [],
                "latest_period_by_year": {},
                "latest_year": 0,
                "latest_period": "",
                "latest_year_is_partial": False,
                "current_series_limit": HISTORICAL_CURRENT_SERIES_LIMIT,
                "series_limit": HISTORICAL_SERIES_LIMIT,
                "rank_focus_limit": HISTORICAL_RANK_FOCUS_LIMIT,
                "zone_totals": {"district": 0, "barrio": 0},
            },
            "zones": {"district": [], "barrio": []},
        }

    epigrafe_lookup, macro_lookup = load_snapshot_activity_lookups()
    district_rows: list[dict[str, object]] = []
    barrio_rows: list[dict[str, object]] = []

    for period in common_periods:
        year = int(period.split("-", 1)[0])
        locales_frame = load_locales_snapshot_frame(period)
        if locales_frame.empty:
            continue

        activity_frame = load_activity_snapshot_frame(period)
        activity_categories = summarize_snapshot_activity_categories(
            activity_frame,
            epigrafe_lookup=epigrafe_lookup,
            macro_lookup=macro_lookup,
        )
        merged = locales_frame.merge(
            activity_categories,
            on=["id_local", "snapshot_period"],
            how="left",
            validate="one_to_one",
        )
        missing_code, missing_desc = status_category_payload("__status_missing_snapshot__")
        merged["category_code"] = merged["category_code"].fillna(missing_code).astype("string")
        merged["category_desc"] = merged["category_desc"].fillna(missing_desc).astype("string")

        combined = build_snapshot_category_frame(merged)
        district_rows.extend(build_zone_history_records(combined, zone_level="district", year=year, period=period))
        barrio_rows.extend(build_zone_history_records(combined, zone_level="barrio", year=year, period=period))

    district_rows = finalize_historical_metric_records(district_rows)
    barrio_rows = finalize_historical_metric_records(barrio_rows)

    latest_period = common_periods[-1]
    latest_year = int(latest_period.split("-", 1)[0])
    years = [int(period.split("-", 1)[0]) for period in common_periods]

    return {
        "meta": {
            "title": "Madrid Historical Category Ranking",
            "subtitle": "Ranking anual por especializacion relativa de cada categoria usando el ultimo mes disponible de cada ano.",
            "generated_at": generated_at,
            "metric_key": HISTORICAL_METRIC_KEY,
            "metric_label": HISTORICAL_METRIC_LABEL,
            "metric_short_label": HISTORICAL_METRIC_SHORT_LABEL,
            "metric_definition": HISTORICAL_METRIC_DEFINITION,
            "metric_direction": HISTORICAL_METRIC_DIRECTION,
            "smoothing_weight": int(HISTORICAL_SMOOTHING_WEIGHT),
            "years": years,
            "latest_period_by_year": {str(int(period.split("-", 1)[0])): period for period in common_periods},
            "latest_year": latest_year,
            "latest_period": latest_period,
            "latest_year_is_partial": not latest_period.endswith("-12"),
            "current_series_limit": HISTORICAL_CURRENT_SERIES_LIMIT,
            "series_limit": HISTORICAL_SERIES_LIMIT,
            "rank_focus_limit": HISTORICAL_RANK_FOCUS_LIMIT,
            "zone_totals": {
                "district": len({row["zone_key"] for row in district_rows if row["category_code"] == "__all__"}),
                "barrio": len({row["zone_key"] for row in barrio_rows if row["category_code"] == "__all__"}),
            },
        },
        "zones": {
            "district": district_rows,
            "barrio": barrio_rows,
        },
    }


def build_hex_composition_history_artifacts(*, generated_at: str) -> dict[str, object]:
    common_periods = select_latest_periods_by_year(
        sorted(set(list_snapshot_periods(HISTORICAL_LOCALES_DIR)).intersection(list_snapshot_periods(HISTORICAL_ACTIVITIES_DIR)))
    )
    common_periods = [
        period
        for period in common_periods
        if HEX_COMPOSITION_HISTORY_YEAR_MIN <= int(period.split("-", 1)[0]) <= HEX_COMPOSITION_HISTORY_YEAR_MAX
    ]

    if not common_periods:
        return {
            "meta": {
                "title": "Madrid Historical Hex Composition",
                "subtitle": "Mezcla anual por categoria dentro de cada hexagono usando el ultimo mes disponible de cada ano.",
                "generated_at": generated_at,
                "years": [],
                "latest_period_by_year": {},
                "latest_year": 0,
                "latest_period": "",
                "latest_year_is_partial": False,
            },
            "hexes": [],
        }

    epigrafe_lookup, macro_lookup = load_snapshot_activity_lookups()
    rows: list[dict[str, object]] = []

    for period in common_periods:
        year = int(period.split("-", 1)[0])
        locales_frame = load_locales_snapshot_frame(period)
        if locales_frame.empty:
            continue

        activity_frame = load_activity_snapshot_frame(period)
        activity_categories = summarize_snapshot_activity_categories(
            activity_frame,
            epigrafe_lookup=epigrafe_lookup,
            macro_lookup=macro_lookup,
        )
        merged = locales_frame.merge(
            activity_categories,
            on=["id_local", "snapshot_period"],
            how="left",
            validate="one_to_one",
        )
        missing_code, missing_desc = status_category_payload("__status_missing_snapshot__")
        merged["category_code"] = merged["category_code"].fillna(missing_code).astype("string")
        merged["category_desc"] = merged["category_desc"].fillna(missing_desc).astype("string")

        combined = build_snapshot_category_frame(merged)
        rows.extend(build_hex_composition_history_records(combined, year=year, period=period))

    rows.sort(
        key=lambda item: (
            str(item.get("h3_cell") or ""),
            int(item.get("year") or 0),
            str(item.get("category_code") or ""),
        )
    )

    latest_period = common_periods[-1]
    latest_year = int(latest_period.split("-", 1)[0])
    years = [int(period.split("-", 1)[0]) for period in common_periods]

    return {
        "meta": {
            "title": "Madrid Historical Hex Composition",
            "subtitle": "Mezcla anual por categoria dentro de cada hexagono usando el ultimo mes disponible de cada ano.",
            "generated_at": generated_at,
            "years": years,
            "latest_period_by_year": {str(int(period.split("-", 1)[0])): period for period in common_periods},
            "latest_year": latest_year,
            "latest_period": latest_period,
            "latest_year_is_partial": not latest_period.endswith("-12"),
        },
        "hexes": rows,
    }


def write_hex_composition_history_manifest(payload: dict[str, object]) -> dict[str, object]:
    for existing_part in HEX_COMPOSITION_HISTORY_PARTS_DIR.glob("*.json"):
        existing_part.unlink()

    rows = payload.get("hexes")
    if not isinstance(rows, list):
        rows = []

    rows_by_year: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        year_value = row.get("year")
        try:
            year = int(year_value)
        except (TypeError, ValueError):
            continue
        rows_by_year.setdefault(year, []).append(row)

    parts: list[dict[str, object]] = []
    for year in sorted(rows_by_year):
        year_rows = rows_by_year[year]
        part_path = HEX_COMPOSITION_HISTORY_PARTS_DIR / f"{year}.json"
        part_path.write_text(
            json.dumps({"hexes": year_rows}, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )
        parts.append(
            {
                "year": year,
                "path": f"/data/map/historical/hex-composition/{year}.json",
                "rows": len(year_rows),
            }
        )

    manifest = {
        "meta": payload.get("meta", {}),
        "parts": parts,
    }
    HEX_COMPOSITION_HISTORY_MANIFEST_OUTPUT.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    return manifest


def write_hex_composition_history_prefix_manifest(payload: dict[str, object]) -> dict[str, object]:
    for existing_part in HEX_COMPOSITION_HISTORY_PREFIX_PARTS_DIR.glob("*.json"):
        existing_part.unlink()

    rows = payload.get("hexes")
    if not isinstance(rows, list):
        rows = []

    rows_by_prefix: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        h3_cell = str(row.get("h3_cell") or "").strip()
        if not h3_cell:
            continue
        prefix = h3_cell[:HEX_COMPOSITION_HISTORY_PREFIX_LENGTH]
        rows_by_prefix.setdefault(prefix, []).append(row)

    shard_sizes: list[int] = []
    for prefix in sorted(rows_by_prefix):
        shard_rows = rows_by_prefix[prefix]
        shard_sizes.append(len(shard_rows))
        shard_path = HEX_COMPOSITION_HISTORY_PREFIX_PARTS_DIR / f"{prefix}.json"
        shard_path.write_text(
            json.dumps({"hexes": shard_rows}, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
            encoding="utf-8",
        )

    manifest = {
        "meta": payload.get("meta", {}),
        "prefix_length": HEX_COMPOSITION_HISTORY_PREFIX_LENGTH,
        "base_path": "/data/map/historical/hex-composition-by-prefix",
        "shard_count": len(rows_by_prefix),
        "min_rows_per_shard": min(shard_sizes) if shard_sizes else 0,
        "max_rows_per_shard": max(shard_sizes) if shard_sizes else 0,
    }
    HEX_COMPOSITION_HISTORY_PREFIX_MANIFEST_OUTPUT.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    return manifest


def list_snapshot_periods(directory: Path) -> list[str]:
    if not directory.exists():
        return []

    periods: list[str] = []
    for path in directory.glob("*.csv.gz"):
        period = path.name.removesuffix(".csv.gz")
        if re.fullmatch(r"\d{4}-\d{2}", period):
            periods.append(period)
    return sorted(set(periods))


def select_latest_periods_by_year(periods: list[str]) -> list[str]:
    latest_by_year: dict[int, str] = {}
    for period in sorted(periods):
        if not re.fullmatch(r"\d{4}-\d{2}", period):
            continue
        latest_by_year[int(period[:4])] = period
    return [latest_by_year[year] for year in sorted(latest_by_year)]


def load_snapshot_activity_lookups() -> tuple[pd.DataFrame, pd.DataFrame]:
    audit = pd.read_csv(ACTIVITY_NORMALIZATION_AUDIT, low_memory=False)
    epigrafe_lookup = activity_abt_survival._collapse_activity_lookup_by_raw_code(
        audit[audit["taxonomy"] == "epigrafe"].copy()
    )
    epigrafe_lookup["raw_code"] = epigrafe_lookup["raw_code"].fillna("").astype(str).str.upper().str.strip()
    epigrafe_lookup["clean_code"] = epigrafe_lookup["clean_code"].fillna("").astype(str).str.upper().str.strip()
    epigrafe_lookup["code_valid"] = epigrafe_lookup["code_valid"].astype("boolean").fillna(False).astype(bool)
    epigrafe_lookup = epigrafe_lookup[["raw_code", "clean_code", "code_valid"]].drop_duplicates(subset=["raw_code"])

    macro_lookup = pd.read_csv(
        ACTIVITY_MACRO_TAXONOMY,
        usecols=["epigrafe_code", "macro_category_code", "macro_category_name"],
        dtype="string",
        low_memory=False,
    )
    macro_lookup["epigrafe_code"] = macro_lookup["epigrafe_code"].fillna("").astype("string").str.upper().str.strip()
    macro_lookup["macro_category_code"] = macro_lookup["macro_category_code"].fillna("").astype("string").str.strip()
    macro_lookup["macro_category_name"] = macro_lookup["macro_category_name"].fillna("").astype("string").str.strip()
    macro_lookup = macro_lookup[macro_lookup["epigrafe_code"].ne("")].drop_duplicates(subset=["epigrafe_code"])
    return epigrafe_lookup, macro_lookup


def load_activity_snapshot_frame(period: str) -> pd.DataFrame:
    frame = pd.read_csv(
        HISTORICAL_ACTIVITIES_DIR / f"{period}.csv.gz",
        usecols=["id_local", "snapshot_period", "id_epigrafe", "desc_epigrafe"],
        low_memory=False,
    )
    frame["id_local"] = pd.to_numeric(frame["id_local"], errors="coerce").astype("Int64")
    frame["snapshot_period"] = frame["snapshot_period"].fillna(period).astype("string")
    frame["raw_epigrafe_code"] = frame["id_epigrafe"].fillna("").astype(str).str.upper().str.strip()
    frame["raw_epigrafe_desc"] = frame["desc_epigrafe"].fillna("").astype(str).str.upper().str.strip()
    return frame[["id_local", "snapshot_period", "raw_epigrafe_code", "raw_epigrafe_desc"]]


def load_locales_snapshot_frame(period: str) -> pd.DataFrame:
    frame = pd.read_csv(
        HISTORICAL_LOCALES_DIR / f"{period}.csv.gz",
        usecols=lambda column: column
        in {
            "id_local",
            "snapshot_period",
            "id_distrito_local",
            "desc_distrito_local",
            "id_barrio_local",
            "desc_barrio_local",
            "h3_cell",
        },
        low_memory=False,
    )
    frame["id_local"] = pd.to_numeric(frame["id_local"], errors="coerce").astype("Int64")
    frame["snapshot_period"] = frame["snapshot_period"].fillna(period).astype("string")
    frame["h3_cell"] = frame.get("h3_cell", pd.Series(pd.NA, index=frame.index)).astype("string").str.lower().str.strip()
    frame["district_code"] = frame["id_distrito_local"].map(lambda value: normalize_admin_code_value(value, width=2)).astype("string")
    frame["district_name"] = frame["desc_distrito_local"].map(clean_place_name).astype("string")
    frame["barrio_code"] = [
        normalize_snapshot_barrio_code(district_value, barrio_value)
        for district_value, barrio_value in zip(frame["id_distrito_local"], frame["id_barrio_local"])
    ]
    frame["barrio_code"] = pd.Series(frame["barrio_code"], index=frame.index, dtype="string")
    frame["barrio_name"] = frame["desc_barrio_local"].map(clean_place_name).astype("string")
    frame["barrio_context_name"] = frame["district_name"]
    frame["barrio_key"] = [
        build_barrio_zone_key(district_code, barrio_code, barrio_name)
        for district_code, barrio_code, barrio_name in zip(
            frame["district_code"],
            frame["barrio_code"],
            frame["barrio_name"],
        )
    ]
    frame["barrio_key"] = pd.Series(frame["barrio_key"], index=frame.index, dtype="string")
    frame = frame.dropna(subset=["id_local"]).drop_duplicates(subset=["id_local", "snapshot_period"], keep="first")
    return frame[
        [
            "id_local",
            "snapshot_period",
            "h3_cell",
            "district_code",
            "district_name",
            "barrio_code",
            "barrio_name",
            "barrio_context_name",
            "barrio_key",
        ]
    ]


def normalize_snapshot_barrio_code(district_value: object, barrio_value: object) -> str:
    district_code = normalize_admin_code_value(district_value, width=2)
    if pd.isna(barrio_value):
        return ""
    text = str(barrio_value).strip()
    if not text or text.casefold() in {"nan", "<na>"}:
        return ""
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(char for char in text if char.isdigit())
    if not digits:
        return ""
    if len(digits) <= 3 and district_code:
        return f"{district_code}{digits.zfill(3)}"
    if len(digits) <= 4:
        return digits.zfill(4)
    return digits


def build_barrio_zone_key(district_code: object, barrio_code: object, barrio_name: object) -> str:
    barrio_code_text = str(barrio_code or "").strip()
    if barrio_code_text:
        return barrio_code_text
    clean_name = clean_place_name(barrio_name)
    if not clean_name:
        return ""
    slug = re.sub(r"[^a-z0-9]+", "-", clean_name.casefold()).strip("-")
    district_code_text = str(district_code or "").strip()
    if district_code_text and slug:
        return f"{district_code_text}:{slug}"
    return slug


def summarize_snapshot_activity_categories(
    activity_frame: pd.DataFrame,
    *,
    epigrafe_lookup: pd.DataFrame,
    macro_lookup: pd.DataFrame,
) -> pd.DataFrame:
    empty = pd.DataFrame(columns=["id_local", "snapshot_period", "category_code", "category_desc"])
    if activity_frame.empty:
        return empty

    working = activity_frame.dropna(subset=["id_local"]).copy()
    if working.empty:
        return empty

    working = working.merge(
        epigrafe_lookup.rename(columns={"raw_code": "raw_epigrafe_code"}),
        on="raw_epigrafe_code",
        how="left",
        validate="many_to_one",
    )
    working = working.merge(
        macro_lookup.rename(columns={"epigrafe_code": "clean_code"}),
        on="clean_code",
        how="left",
        validate="many_to_one",
    )
    working["code_valid"] = working["code_valid"].astype("boolean").fillna(False).astype(bool)
    working["macro_category_code"] = working["macro_category_code"].fillna("").astype("string")
    working["macro_category_name"] = working["macro_category_name"].fillna("").astype("string")
    working["has_no_activity_marker"] = (
        working["raw_epigrafe_code"].isin({"000000", "0", "0.0"})
        | working["raw_epigrafe_desc"].eq("LOCAL SIN ACTIVIDAD")
    )
    working["has_pending_coding_marker"] = (
        working["raw_epigrafe_code"].str.startswith("PTE")
        | working["raw_epigrafe_desc"].str.startswith("PTE.")
    )
    working["has_blank_marker"] = working["raw_epigrafe_code"].eq("") & working["raw_epigrafe_desc"].eq("")
    working["has_null_origin_marker"] = (
        working["raw_epigrafe_code"].eq("-1")
        | working["raw_epigrafe_desc"].eq("VALOR NULO EN ORIGEN")
    )

    summary = (
        working.groupby(["id_local", "snapshot_period"], dropna=False)
        .agg(
            raw_rows=("id_local", "size"),
            valid_epigrafe_rows=("code_valid", "sum"),
            macro_count=("macro_category_code", count_non_empty_unique),
            single_macro_code=("macro_category_code", first_non_empty_text),
            single_macro_desc=("macro_category_name", first_non_empty_text),
            has_no_activity_marker=("has_no_activity_marker", "max"),
            has_pending_coding_marker=("has_pending_coding_marker", "max"),
            has_blank_marker=("has_blank_marker", "max"),
            has_null_origin_marker=("has_null_origin_marker", "max"),
        )
        .reset_index()
    )
    summary["category_code"] = pd.Series(pd.NA, index=summary.index, dtype="string")
    summary["category_desc"] = pd.Series(pd.NA, index=summary.index, dtype="string")

    single_macro_mask = (
        summary["macro_count"].eq(1)
        & summary["single_macro_code"].astype("string").ne("")
        & summary["single_macro_desc"].astype("string").ne("")
    )
    summary.loc[single_macro_mask, "category_code"] = summary.loc[single_macro_mask, "single_macro_code"].astype("string")
    summary.loc[single_macro_mask, "category_desc"] = summary.loc[single_macro_mask, "single_macro_desc"].astype("string")

    apply_status_category(summary, summary["macro_count"].ge(2), "__status_multi_activity__")
    apply_status_category(summary, summary["has_no_activity_marker"].astype(bool), "__status_no_activity__")
    apply_status_category(summary, summary["has_pending_coding_marker"].astype(bool), "__status_pending_coding__")
    apply_status_category(summary, summary["valid_epigrafe_rows"].gt(0), "__status_unmapped_activity__")
    apply_status_category(
        summary,
        summary["has_blank_marker"].astype(bool) | summary["has_null_origin_marker"].astype(bool),
        "__status_uncoded_activity__",
    )

    fallback = UNKNOWN_ACTIVITY_CATEGORY_METADATA["__status_uncoded_activity__"]
    summary["category_code"] = summary["category_code"].fillna("__status_uncoded_activity__").astype("string")
    summary["category_desc"] = summary["category_desc"].fillna(str(fallback["desc"])).astype("string")
    return summary[["id_local", "snapshot_period", "category_code", "category_desc"]]


def apply_status_category(frame: pd.DataFrame, mask: pd.Series, category_code: str) -> None:
    pending_mask = mask & frame["category_code"].isna()
    if not bool(pending_mask.any()):
        return
    frame.loc[pending_mask, "category_code"] = category_code
    frame.loc[pending_mask, "category_desc"] = str(UNKNOWN_ACTIVITY_CATEGORY_METADATA[category_code]["desc"])


def count_non_empty_unique(series: pd.Series) -> int:
    cleaned = series.fillna("").astype("string").str.strip()
    return int(cleaned[cleaned.ne("")].nunique())


def first_non_empty_text(series: pd.Series) -> str:
    cleaned = series.fillna("").astype("string").str.strip()
    values = cleaned[cleaned.ne("")].drop_duplicates().sort_values()
    if values.empty:
        return ""
    return str(values.iloc[0])


def build_snapshot_category_frame(frame: pd.DataFrame) -> pd.DataFrame:
    scoped = frame[
        [
            "id_local",
            "snapshot_period",
            "h3_cell",
            "district_code",
            "district_name",
            "barrio_code",
            "barrio_name",
            "barrio_context_name",
            "barrio_key",
            "category_code",
            "category_desc",
        ]
    ].copy()
    all_rows = scoped[
        [
            "id_local",
            "snapshot_period",
            "h3_cell",
            "district_code",
            "district_name",
            "barrio_code",
            "barrio_name",
            "barrio_context_name",
            "barrio_key",
        ]
    ].copy()
    all_rows["category_code"] = "__all__"
    all_rows["category_desc"] = "Todos los locales"
    return pd.concat([all_rows, scoped], ignore_index=True)


def build_hex_composition_history_records(frame: pd.DataFrame, *, year: int, period: str) -> list[dict[str, object]]:
    if frame.empty:
        return []

    scoped = frame.copy()
    scoped["h3_cell"] = scoped["h3_cell"].fillna("").astype("string").str.lower().str.strip()
    scoped["category_code"] = scoped["category_code"].fillna("").astype("string").str.strip()
    scoped["category_desc"] = scoped["category_desc"].fillna("").astype("string").str.strip()
    scoped = scoped[scoped["id_local"].notna() & scoped["h3_cell"].ne("") & scoped["category_code"].ne("")].copy()
    if scoped.empty:
        return []

    hex_totals = (
        scoped[scoped["category_code"].eq("__all__")]
        .groupby("h3_cell", dropna=False)
        .agg(hex_total_locales=("id_local", "nunique"))
        .reset_index()
    )
    if hex_totals.empty:
        return []

    counts = (
        scoped.groupby(["h3_cell", "category_code", "category_desc"], dropna=False)
        .agg(n_locales=("id_local", "nunique"))
        .reset_index()
    )
    counts = counts.merge(hex_totals, on="h3_cell", how="left", validate="many_to_one")
    counts = counts[counts["hex_total_locales"].fillna(0).astype(float) > 0].copy()
    if counts.empty:
        return []

    counts["share_in_hex"] = counts["n_locales"] / counts["hex_total_locales"]
    counts = counts.sort_values(
        ["h3_cell", "n_locales", "category_desc"],
        ascending=[True, False, True],
    ).reset_index(drop=True)

    records: list[dict[str, object]] = []
    for row in counts.itertuples(index=False):
        records.append(
            {
                "year": int(year),
                "period": str(period),
                "h3_cell": str(row.h3_cell),
                "category_code": str(row.category_code),
                "category_desc": str(row.category_desc),
                "n_locales": int(row.n_locales),
                "hex_total_locales": int(row.hex_total_locales),
                "share_in_hex": serialize_probability(row.share_in_hex),
            }
        )
    return records


def build_zone_history_records(frame: pd.DataFrame, *, zone_level: str, year: int, period: str) -> list[dict[str, object]]:
    if frame.empty:
        return []

    if zone_level == "district":
        scoped = frame.assign(
            zone_key=frame["district_code"],
            zone_code=frame["district_code"],
            zone_name=frame["district_name"],
            zone_context_name=pd.Series("", index=frame.index, dtype="string"),
        ).copy()
    else:
        scoped = frame.assign(
            zone_key=frame["barrio_key"],
            zone_code=frame["barrio_code"],
            zone_name=frame["barrio_name"],
            zone_context_name=frame["barrio_context_name"],
        ).copy()

    scoped["zone_key"] = scoped["zone_key"].fillna("").astype("string").str.strip()
    scoped["zone_code"] = scoped["zone_code"].fillna("").astype("string").str.strip()
    scoped["zone_name"] = scoped["zone_name"].fillna("").astype("string").map(clean_place_name)
    scoped["zone_context_name"] = scoped["zone_context_name"].fillna("").astype("string").map(clean_place_name)
    scoped = scoped[scoped["id_local"].notna() & scoped["zone_key"].ne("") & scoped["zone_name"].ne("")].copy()
    if scoped.empty:
        return []

    zone_keys = ["zone_key", "zone_code", "zone_name", "zone_context_name"]
    zone_totals = (
        scoped[scoped["category_code"].eq("__all__")]
        .groupby(zone_keys, dropna=False)
        .agg(zone_total_locales=("id_local", "nunique"))
        .reset_index()
    )
    counts = (
        scoped.groupby(["category_code", "category_desc", *zone_keys], dropna=False)
        .agg(n_locales=("id_local", "nunique"))
        .reset_index()
    )
    counts = counts.merge(zone_totals, on=zone_keys, how="left", validate="many_to_one")
    counts["share_of_zone"] = counts["n_locales"] / counts["zone_total_locales"]
    city_total_locales = float(zone_totals["zone_total_locales"].sum())
    counts["city_category_locales"] = counts.groupby("category_code")["n_locales"].transform("sum")
    counts["city_total_locales"] = city_total_locales
    counts["city_share"] = counts["city_category_locales"] / city_total_locales if city_total_locales > 0 else pd.NA
    counts["smoothed_share_of_zone"] = (
        counts["n_locales"] + HISTORICAL_SMOOTHING_WEIGHT * counts["city_share"]
    ) / (counts["zone_total_locales"] + HISTORICAL_SMOOTHING_WEIGHT)
    counts["metric_value"] = counts["smoothed_share_of_zone"] / counts["city_share"]
    counts = counts.sort_values(
        ["category_code", "metric_value", "share_of_zone", "n_locales", "zone_name", "zone_context_name"],
        ascending=[True, False, False, False, True, True],
    ).reset_index(drop=True)
    counts["rank"] = counts.groupby("category_code").cumcount() + 1

    records: list[dict[str, object]] = []
    for row in counts.itertuples(index=False):
        records.append(
            {
                "zone_level": zone_level,
                "category_code": str(row.category_code),
                "category_desc": str(row.category_desc),
                "year": int(year),
                "period": str(period),
                "zone_key": str(row.zone_key),
                "zone_code": str(row.zone_code),
                "zone_name": str(row.zone_name),
                "zone_context_name": str(row.zone_context_name) if str(row.zone_context_name).strip() else None,
                "n_locales": int(row.n_locales),
                "zone_total_locales": int(row.zone_total_locales),
                "share_of_zone": serialize_probability(row.share_of_zone),
                "smoothed_share_of_zone": serialize_probability(row.smoothed_share_of_zone),
                "city_share": serialize_probability(row.city_share),
                "city_category_locales": int(row.city_category_locales),
                "city_total_locales": int(row.city_total_locales),
                "metric_value": serialize_probability(row.metric_value),
                "rank": int(row.rank),
            }
        )
    return records


def finalize_historical_metric_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    if not records:
        return []

    finalized = [dict(record) for record in records]
    base_year = min(int(record["year"]) for record in finalized)
    base_share_by_zone: dict[str, float] = {}

    for record in finalized:
        if str(record["category_code"]) != "__all__" or int(record["year"]) != base_year:
            continue
        city_total = float(record.get("city_total_locales") or 0)
        if city_total <= 0:
            continue
        base_share_by_zone[str(record["zone_key"])] = float(record.get("n_locales") or 0) / city_total

    for record in finalized:
        if str(record["category_code"]) != "__all__":
            continue
        city_total = float(record.get("city_total_locales") or 0)
        if city_total <= 0:
            record["metric_value"] = None
            continue
        current_share_of_city = float(record.get("n_locales") or 0) / city_total
        base_share_of_city = base_share_by_zone.get(str(record["zone_key"]), 0.0)
        record["metric_value"] = current_share_of_city - base_share_of_city

    grouped: dict[tuple[int, str], list[dict[str, object]]] = {}
    for record in finalized:
        key = (int(record["year"]), str(record["category_code"]))
        grouped.setdefault(key, []).append(record)

    for key, group in grouped.items():
        group.sort(
            key=lambda item: (
                -float(item["metric_value"]) if item.get("metric_value") is not None else float("inf"),
                -(float(item.get("share_of_zone") or 0.0)),
                -(int(item.get("n_locales") or 0)),
                str(item.get("zone_name") or ""),
                str(item.get("zone_context_name") or ""),
            )
        )
        for rank, item in enumerate(group, start=1):
            item["rank"] = rank

    finalized.sort(key=lambda item: (str(item["zone_level"]), str(item["category_code"]), int(item["year"]), int(item["rank"]), str(item["zone_name"])))
    return finalized


def build_hex_size_specs(base_h3_resolution: int) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    for spec in HEX_SIZE_SPECS:
        resolution = max(0, int(base_h3_resolution) - int(spec["resolution_offset"]))
        specs.append(
            {
                **spec,
                "h3_resolution": resolution,
                "hex_area_km2": average_hex_area_km2(resolution),
            }
        )
    return specs


def detect_h3_resolution(series: pd.Series) -> int:
    sample = series.dropna().astype("string").drop_duplicates().head(1024)
    if sample.empty:
        raise ValueError("Unable to detect H3 resolution from empty series")
    resolutions = sample.map(lambda value: int(h3.get_resolution(str(value))))
    return int(pd.Series(resolutions).mode().iloc[0])


def roll_up_hex_frame(frame: pd.DataFrame, *, target_resolution: int) -> pd.DataFrame:
    rolled = frame.copy()
    rolled["hex_h3_cell"] = rolled["h3_cell_start"].map(lambda value: roll_up_h3_cell(value, target_resolution=target_resolution))
    return rolled


def roll_up_h3_cell(value: object, *, target_resolution: int) -> str:
    cell = str(value).strip()
    if not cell or cell.casefold() in {"nan", "<na>"}:
        raise ValueError("Cannot roll up an empty H3 cell")

    current_resolution = int(h3.get_resolution(cell))
    if current_resolution < target_resolution:
        raise ValueError(f"Cannot expand H3 cell from resolution {current_resolution} to {target_resolution}")
    if current_resolution == target_resolution:
        return cell
    return str(h3.cell_to_parent(cell, target_resolution))


def average_hex_area_km2(resolution: int) -> float:
    try:
        return float(h3.average_hexagon_area(resolution, unit="km^2"))
    except TypeError:
        return float(h3.average_hexagon_area(resolution, "km^2"))


def normalize_section_key(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.casefold() in {"nan", "<na>"}:
        return None
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(char for char in text if char.isdigit())
    if not digits:
        return None
    return digits.zfill(5)


def dominant_place_name(series: pd.Series) -> str:
    cleaned = series.fillna("").astype("string").map(clean_place_name)
    cleaned = cleaned[cleaned.ne("")]
    if cleaned.empty:
        return ""
    counts = cleaned.value_counts(dropna=True)
    return str(counts.index[0])


def clean_place_name(value: object) -> str:
    text = str(value).strip()
    if not text:
        return ""
    if text.casefold() in {"nan", "<na>", "barrios en edif. bdc", "dto. fict.sec.desap."}:
        return ""
    return text


def normalize_admin_code_value(value: object, *, width: int) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if not text or text.casefold() in {"nan", "<na>"}:
        return ""
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(char for char in text if char.isdigit())
    if not digits:
        return ""
    return digits.zfill(width)[-width:]


def normalize_geography_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    for column, width in (("district_code", 2), ("barrio_code", 3)):
        if column in normalized.columns:
            normalized[column] = normalized[column].map(lambda value: normalize_admin_code_value(value, width=width)).astype("string")
        else:
            normalized[column] = pd.Series("", index=normalized.index, dtype="string")
    for column in ("district_name", "barrio_name"):
        if column in normalized.columns:
            normalized[column] = normalized[column].fillna("").astype("string").map(clean_place_name)
        else:
            normalized[column] = pd.Series("", index=normalized.index, dtype="string")
    return normalized


def geography_missing_mask(frame: pd.DataFrame) -> pd.Series:
    district_missing = frame["district_name"].fillna("").astype("string").map(clean_place_name).eq("")
    barrio_missing = frame["barrio_name"].fillna("").astype("string").map(clean_place_name).eq("")
    return district_missing | barrio_missing


def attach_section_geography(
    frame: pd.DataFrame,
    *,
    section_geography: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    enriched = frame.copy()
    enriched["section_key_join"] = enriched["section_key_start"].map(normalize_section_key).astype("string")
    enriched = enriched.merge(
        section_geography.rename(columns={"section_key": "section_key_join"}),
        on="section_key_join",
        how="left",
        validate="many_to_one",
    )
    enriched = normalize_geography_columns(enriched)

    missing_after_key_join = geography_missing_mask(enriched)
    if bool(missing_after_key_join.any()):
        resolved = resolve_section_geography_from_coordinates(
            enriched.loc[missing_after_key_join],
            section_geography=section_geography,
        )
        if not resolved.empty:
            enriched = apply_section_geography_fallback(enriched, resolved)
            enriched = normalize_geography_columns(enriched)

    missing_after_fallback = geography_missing_mask(enriched)
    return enriched, {
        "matched_from_section_key": int((~missing_after_key_join).sum()),
        "backfilled_from_coordinates": int((missing_after_key_join & ~missing_after_fallback).sum()),
        "remaining_missing_geography": int(missing_after_fallback.sum()),
    }


def resolve_section_geography_from_coordinates(
    frame: pd.DataFrame,
    *,
    section_geography: pd.DataFrame,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["section_key_spatial", *GEOGRAPHY_COLUMNS])

    from localizate.survival_features import is_valid_madrid_coordinate

    valid_coordinates = is_valid_madrid_coordinate(frame["lat_wgs84_start"], frame["lon_wgs84_start"])
    candidates = frame.loc[valid_coordinates, ["lat_wgs84_start", "lon_wgs84_start"]].copy()
    if candidates.empty:
        return pd.DataFrame(columns=["section_key_spatial", *GEOGRAPHY_COLUMNS])

    spatial_keys = match_section_keys_by_coordinates(candidates)
    if spatial_keys.empty:
        return pd.DataFrame(columns=["section_key_spatial", *GEOGRAPHY_COLUMNS])

    reference = normalize_geography_columns(section_geography.drop_duplicates("section_key").set_index("section_key"))
    resolved = pd.DataFrame({"section_key_spatial": spatial_keys.astype("string")}, index=spatial_keys.index)
    resolved = resolved.join(reference[list(GEOGRAPHY_COLUMNS)], on="section_key_spatial")
    return normalize_geography_columns(resolved)


def match_section_keys_by_coordinates(candidates: pd.DataFrame) -> pd.Series:
    if candidates.empty:
        return pd.Series(dtype="string")

    try:
        import geopandas as gpd
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "geopandas is required to backfill missing section geography by coordinates. Install back/requirements.txt first."
        ) from exc

    from localizate.section_geography import load_section_geodataframe

    sections = load_section_geodataframe()
    sections["section_key_spatial"] = sections["COD_SECCIO"].map(normalize_section_key).astype("string")
    sections = sections.loc[sections["section_key_spatial"].notna() & sections.geometry.notna(), ["section_key_spatial", "geometry"]].copy()
    if sections.empty:
        return pd.Series(dtype="string")

    sections = sections.dissolve(by="section_key_spatial", as_index=False)
    if sections.crs is None:
        raise ValueError("Section geometry shapefile has no CRS; cannot apply coordinate fallback safely.")
    sections = sections.to_crs("EPSG:4326")

    points = gpd.GeoDataFrame(
        candidates.copy(),
        geometry=gpd.points_from_xy(candidates["lon_wgs84_start"], candidates["lat_wgs84_start"]),
        crs="EPSG:4326",
    )
    matches = collapse_spatial_join_matches(
        gpd.sjoin(points, sections[["section_key_spatial", "geometry"]], how="left", predicate="within"),
        key_column="section_key_spatial",
    )

    unresolved_index = matches[matches.isna()].index
    if len(unresolved_index) > 0:
        boundary_matches = collapse_spatial_join_matches(
            gpd.sjoin(points.loc[unresolved_index], sections[["section_key_spatial", "geometry"]], how="left", predicate="intersects"),
            key_column="section_key_spatial",
        )
        matches.loc[boundary_matches.index] = matches.loc[boundary_matches.index].fillna(boundary_matches)

    unresolved_index = matches[matches.isna()].index
    if len(unresolved_index) > 0 and hasattr(gpd, "sjoin_nearest"):
        nearest_matches = collapse_spatial_join_matches(
            gpd.sjoin_nearest(
                points.loc[unresolved_index].to_crs(SPATIAL_FALLBACK_CRS),
                sections[["section_key_spatial", "geometry"]].to_crs(SPATIAL_FALLBACK_CRS),
                how="left",
                max_distance=SPATIAL_NEAREST_MAX_DISTANCE_M,
                distance_col="distance_m",
            ),
            key_column="section_key_spatial",
            distance_column="distance_m",
        )
        matches.loc[nearest_matches.index] = matches.loc[nearest_matches.index].fillna(nearest_matches)

    return matches.dropna().astype("string")


def collapse_spatial_join_matches(
    joined: pd.DataFrame,
    *,
    key_column: str,
    distance_column: str | None = None,
) -> pd.Series:
    if joined.empty or key_column not in joined.columns:
        return pd.Series(dtype="string")

    collapsed = joined.reset_index().rename(columns={"index": "row_index"})
    sort_columns = ["row_index"]
    ascending = [True]
    if distance_column and distance_column in collapsed.columns:
        sort_columns.append(distance_column)
        ascending.append(True)
    sort_columns.append(key_column)
    ascending.append(True)
    collapsed = (
        collapsed.sort_values(sort_columns, ascending=ascending, na_position="last")
        .drop_duplicates("row_index", keep="first")
        .set_index("row_index")
    )
    return collapsed[key_column].astype("string")


def apply_section_geography_fallback(frame: pd.DataFrame, resolved: pd.DataFrame) -> pd.DataFrame:
    if resolved.empty:
        return frame

    updated = frame.copy()
    if "section_key_join" in updated.columns and "section_key_spatial" in resolved.columns:
        updated.loc[resolved.index, "section_key_join"] = resolved.loc[resolved.index, "section_key_spatial"].astype("string")

    for column in GEOGRAPHY_COLUMNS:
        existing = updated.loc[resolved.index, column].fillna("").astype("string")
        if column.endswith("_name"):
            missing_values = existing.map(clean_place_name).eq("")
        else:
            missing_values = existing.str.strip().eq("")
        if bool(missing_values.any()):
            fill_index = missing_values[missing_values].index
            updated.loc[fill_index, column] = resolved.loc[fill_index, column].fillna("").astype("string")
    return updated


def build_location_label(barrio_name: str, district_name: str) -> str:
    if barrio_name and district_name and barrio_name.casefold() != district_name.casefold():
        return f"{barrio_name}, {district_name}"
    if barrio_name:
        return barrio_name
    if district_name:
        return district_name
    return "Madrid"


def build_zone_boundary_artifacts(*, generated_at: str) -> dict[str, object]:
    try:
        import geopandas as gpd
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "geopandas is required to build frontend administrative boundaries. Install back/requirements.txt first."
        ) from exc

    from localizate.section_geography import load_section_geodataframe

    sections = load_section_geodataframe()
    sections["district_code"] = sections["COD_DIS"].map(lambda value: normalize_admin_code_value(value, width=2)).astype("string")
    sections["district_name"] = sections["NOM_DIS"].map(clean_place_name).astype("string")
    sections["barrio_code"] = sections["COD_BAR"].map(lambda value: normalize_admin_code_value(value, width=3)).astype("string")
    sections["barrio_name"] = sections["NOM_BAR"].map(clean_place_name).astype("string")
    sections = sections.loc[sections.geometry.notna()].copy()

    district_sections = sections.loc[
        sections["district_code"].ne("") & sections["district_name"].ne(""),
        ["district_code", "district_name", "geometry"],
    ].copy()
    barrio_sections = sections.loc[
        sections["barrio_code"].ne("") & sections["barrio_name"].ne("") & sections["district_name"].ne(""),
        ["barrio_code", "barrio_name", "district_name", "geometry"],
    ].copy()

    district_boundaries = district_sections.dissolve(by=["district_code", "district_name"], as_index=False)
    barrio_boundaries = barrio_sections.dissolve(by=["barrio_code", "barrio_name", "district_name"], as_index=False)

    district_boundaries = simplify_zone_geometries(
        district_boundaries,
        tolerance_m=ZONE_BOUNDARY_SIMPLIFY_TOLERANCE_M * 1.75,
    )
    barrio_boundaries = simplify_zone_geometries(
        barrio_boundaries,
        tolerance_m=ZONE_BOUNDARY_SIMPLIFY_TOLERANCE_M,
    )

    return {
        "meta": {
            "title": "Madrid Zone Boundaries",
            "subtitle": "Limites administrativos simplificados para la vista historica por distritos y barrios.",
            "generated_at": generated_at,
        },
        "zones": {
            "district": serialize_zone_boundary_collection(
                district_boundaries.sort_values(["district_code", "district_name"]).reset_index(drop=True),
                zone_level="district",
                zone_code_col="district_code",
                zone_name_col="district_name",
            ),
            "barrio": serialize_zone_boundary_collection(
                barrio_boundaries.sort_values(["barrio_code", "district_name", "barrio_name"]).reset_index(drop=True),
                zone_level="barrio",
                zone_code_col="barrio_code",
                zone_name_col="barrio_name",
                zone_context_col="district_name",
            ),
        },
    }


def simplify_zone_geometries(frame: "pd.DataFrame", *, tolerance_m: float):
    if frame.empty:
        return frame

    working = frame.copy()
    if getattr(working, "crs", None) is None:
        raise ValueError("Section geometry has no CRS; cannot build administrative boundary artifacts safely.")

    working = working.to_crs(SPATIAL_FALLBACK_CRS)
    working["geometry"] = working.geometry.simplify(float(tolerance_m), preserve_topology=True)
    working = working.loc[working.geometry.notna() & ~working.geometry.is_empty].copy()
    return working.to_crs("EPSG:4326")


def serialize_zone_boundary_collection(
    frame: "pd.DataFrame",
    *,
    zone_level: str,
    zone_code_col: str,
    zone_name_col: str,
    zone_context_col: str | None = None,
) -> dict[str, object]:
    export = frame.copy()
    export["zone_level"] = zone_level
    export["zone_code"] = export[zone_code_col].fillna("").astype("string").str.strip()
    export["zone_name"] = export[zone_name_col].fillna("").astype("string").map(clean_place_name)
    if zone_context_col:
        export["zone_context_name"] = export[zone_context_col].fillna("").astype("string").map(clean_place_name)
    else:
        export["zone_context_name"] = pd.Series("", index=export.index, dtype="string")

    export = export.loc[export["zone_code"].ne("") & export["zone_name"].ne(""), [
        "zone_level",
        "zone_code",
        "zone_name",
        "zone_context_name",
        "geometry",
    ]].copy()

    payload = json.loads(export.to_json(drop_id=True))
    for feature in payload.get("features", []):
        properties = feature.get("properties", {})
        properties["zone_context_name"] = properties.get("zone_context_name") or None
    return payload


def compute_horizon_metrics(duration: pd.Series, event: pd.Series, *, horizon: float) -> tuple[int, float | None]:
    support = int(((duration >= float(horizon)) | ((event == 1) & (duration <= float(horizon)))).sum())
    if support <= 0:
        return 0, None

    survivors = int((duration >= float(horizon)).sum())
    return support, float(survivors / support)


def serialize_probability(value: object) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def quality_mode(series: pd.Series) -> str:
    priority = {"high": 3, "medium": 2, "low": 1}
    counts = series.value_counts(dropna=True)
    if counts.empty:
        return "low"
    ranked = sorted(counts.index.tolist(), key=lambda value: (-int(counts[value]), -priority.get(str(value), 0), str(value)))
    return str(ranked[0])


def zone_confidence_tier(*, n_locales: int, n_events: int, zone_level: str) -> str:
    if zone_level == "district":
        if n_locales >= 150 and n_events >= 20:
            return "high"
        if n_locales >= 80 and n_events >= 12:
            return "medium"
        return "low"
    if n_locales >= 80 and n_events >= 12:
        return "medium"
    if n_locales >= 40 and n_events >= 8:
        return "low"
    return "very_low"


if __name__ == "__main__":
    raise SystemExit(main())
