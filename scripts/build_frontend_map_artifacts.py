#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import h3
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


DEFAULT_OUTPUT = PROJECT_ROOT / "apps" / "web" / "public" / "data" / "frontend-map-artifacts.json"
MEDIUM_OUTPUT = PROJECT_ROOT / "apps" / "web" / "public" / "data" / "frontend-map-artifacts-medium.json"
LARGE_OUTPUT = PROJECT_ROOT / "apps" / "web" / "public" / "data" / "frontend-map-artifacts-large.json"
ACTIVITY_GLOSSARY = PROJECT_ROOT / "ACTIVITY_GLOSSARY.md"
SPATIAL_FALLBACK_CRS = "EPSG:25830"
SPATIAL_NEAREST_MAX_DISTANCE_M = 75.0
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


def main() -> int:
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    section_geography = pd.read_csv(
        PROJECT_ROOT / "data" / "processed" / "section_geography.csv",
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
        PROJECT_ROOT / "data" / "features" / "activity_survival_abt.csv",
        usecols=[
            "id_local",
            "h3_cell_start",
            "duration_months",
            "event_observed",
            "activity_category_code_start",
            "activity_category_desc_start",
        ],
        low_memory=False,
    )
    scores = pd.read_csv(
        PROJECT_ROOT / "data" / "exports" / "activity_survival_map_export.csv",
        usecols=[
            "id_local",
            "h3_cell_start",
            "section_key_start",
            "lat_wgs84_start",
            "lon_wgs84_start",
            "risk_ensemble",
            "risk_percentile",
            "quality_tier",
        ],
        low_memory=False,
    )

    merged = abt.merge(scores, on=["id_local", "h3_cell_start"], how="inner", validate="one_to_one")
    merged = merged[merged["h3_cell_start"].notna()].copy()
    merged["category_code"] = merged["activity_category_code_start"].fillna("__unknown__").astype("string")
    merged["category_desc"] = merged["activity_category_desc_start"].fillna("Sin categoria").astype("string")
    merged["duration_months"] = pd.to_numeric(merged["duration_months"], errors="coerce").fillna(0.0)
    merged["event_observed"] = pd.to_numeric(merged["event_observed"], errors="coerce").fillna(0).astype(int)
    merged["risk_ensemble"] = pd.to_numeric(merged["risk_ensemble"], errors="coerce").fillna(0.0)
    merged["risk_percentile"] = pd.to_numeric(merged["risk_percentile"], errors="coerce").fillna(0.0)
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

    for spec in build_hex_size_specs(base_h3_resolution):
        sized_frame = roll_up_hex_frame(merged, target_resolution=int(spec["h3_resolution"]))
        hexes = build_hex_aggregates(sized_frame, hex_cell_col="hex_h3_cell")
        categories = build_category_options(hexes, glossary_profiles)
        payload = {
            "meta": {
                "title": "Madrid Survival Grid",
                "subtitle": "Mapa H3 minimalista listo para plasmar regiones de prediccion y filtrar por tipo de local.",
                "generated_at": generated_at,
                "defaultCategoryCode": "__all__",
                "map_bounds": MAP_BOUNDS,
            },
            "categories": categories,
            "hexes": hexes,
            "zones": zones,
        }
        output_path = Path(spec["output_path"])
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        print(
            f"Wrote {spec['label'].lower()} frontend map artifacts: {output_path} "
            f"(res={spec['h3_resolution']}, area_km2~{float(spec['hex_area_km2']):.4f}, hex_rows={len(hexes):,}, categories={len(categories):,})"
        )

    print(f"Direct section geography matches: {geography_stats['matched_from_section_key']:,}")
    print(f"Coordinate geography backfills: {geography_stats['backfilled_from_coordinates']:,}")
    print(f"Rows still missing geography: {geography_stats['remaining_missing_geography']:,}")
    return 0


def build_hex_aggregates(frame: pd.DataFrame, *, hex_cell_col: str = "h3_cell_start") -> list[dict[str, object]]:
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
                "avg_risk_ensemble": float(part["risk_ensemble"].mean()),
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
        if str(item["category_code"]) not in {"__all__", "__unknown__"}
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

    rows.sort(key=lambda item: (item["category_code"] != "__all__", -int(item["n_locales"]), item["category_desc"]))
    return rows


def build_zone_payloads(frame: pd.DataFrame) -> dict[str, list[dict[str, object]]]:
    return {
        "district": build_zone_metrics(frame, zone_level="district", zone_code_col="district_code", zone_name_col="district_name"),
        "barrio": build_zone_metrics(frame, zone_level="barrio", zone_code_col="barrio_code", zone_name_col="barrio_name"),
    }


def build_zone_metrics(frame: pd.DataFrame, *, zone_level: str, zone_code_col: str, zone_name_col: str) -> list[dict[str, object]]:
    scoped = frame.copy()
    scoped[zone_name_col] = scoped[zone_name_col].fillna("").astype("string").map(clean_place_name)
    scoped[zone_code_col] = scoped[zone_code_col].fillna("").astype("string")
    scoped = scoped[scoped[zone_name_col].ne("")].copy()

    min_locales = 80 if zone_level == "district" else 40
    min_events = 12 if zone_level == "district" else 8

    rows: list[dict[str, object]] = []
    grouped = scoped.groupby([zone_code_col, zone_name_col, "category_code", "category_desc"], dropna=False)
    for (zone_code, zone_name, category_code, category_desc), part in grouped:
        duration = part["duration_months"]
        event = part["event_observed"]
        support_12m, survival_12m = compute_horizon_metrics(duration, event, horizon=12.0)
        support_24m, survival_24m = compute_horizon_metrics(duration, event, horizon=24.0)
        n_locales = int(len(part))
        n_events = int(event.sum())
        rows.append(
            {
                "zone_level": zone_level,
                "zone_code": str(zone_code),
                "zone_name": str(zone_name),
                "category_code": str(category_code),
                "category_desc": str(category_desc),
                "n_locales": n_locales,
                "n_events": n_events,
                "avg_risk_ensemble": float(part["risk_ensemble"].mean()),
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
        out.sort_values(["zone_code", "avg_risk_ensemble", "avg_risk_percentile", "n_locales"], ascending=[True, True, True, False])
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
                "category_code": str(row.category_code),
                "category_desc": str(row.category_desc),
                "n_locales": int(row.n_locales),
                "n_events": int(row.n_events),
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
            "definition": "Vista agregada de todos los locales con H3 visible, sin filtrar por macrocategoria.",
            "mapped_epigraphs": glossary_total_epigraphs,
            "historical_coverage_rows": glossary_total_rows,
            "example_labels": common_examples,
        }

    if category_code == "__unknown__":
        return {
            "definition": "Locales sin macrocategoria normalizada en el ABT actual o sin clasificacion suficiente para entrar en el glosario.",
            "mapped_epigraphs": None,
            "historical_coverage_rows": None,
            "example_labels": [],
        }

    profile = glossary_profiles.get(category_code)
    if profile:
        return profile

    return {
        "definition": f"Macrocategoria comercial agregada en el ABT historico para {category_desc.lower()}.",
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
        if line.startswith("- Codigo:"):
            current["category_code"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Definicion:"):
            current["definition"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Epigrafes mapeados:"):
            current["mapped_epigraphs"] = parse_integer_token(line)
        elif line.startswith("- Cobertura historica bruta:"):
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
            "geopandas is required to backfill missing section geography by coordinates. Install requirements.txt first."
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
