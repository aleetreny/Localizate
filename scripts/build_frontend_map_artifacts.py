#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


DEFAULT_OUTPUT = PROJECT_ROOT / "apps" / "web" / "public" / "data" / "frontend-map-artifacts.json"


def main() -> int:
    output_path = DEFAULT_OUTPUT
    output_path.parent.mkdir(parents=True, exist_ok=True)

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

    all_rows = merged.copy()
    all_rows["category_code"] = "__all__"
    all_rows["category_desc"] = "Todos los locales"
    merged = pd.concat([all_rows, merged], ignore_index=True)

    hexes = build_hex_aggregates(merged)
    categories = build_category_options(hexes)
    zones = build_zone_payloads()

    payload = {
        "meta": {
            "title": "Madrid Survival Grid",
            "subtitle": "Mapa H3 minimalista listo para plasmar regiones de prediccion y filtrar por tipo de local.",
            "generated_at": pd.Timestamp.utcnow().isoformat(),
            "defaultCategoryCode": "__all__",
            "map_bounds": {
                "min_lng": -3.888,
                "min_lat": 40.312,
                "max_lng": -3.517,
                "max_lat": 40.643,
                "min_zoom": 9.8,
                "max_zoom": 15.4,
            },
        },
        "categories": categories,
        "hexes": hexes,
        "zones": zones,
    }

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote frontend map artifacts: {output_path}")
    print(f"Hex rows: {len(hexes):,}")
    print(f"Categories: {len(categories):,}")
    return 0


def build_hex_aggregates(frame: pd.DataFrame) -> list[dict[str, object]]:
    grouped = frame.groupby(["h3_cell_start", "category_code", "category_desc"], dropna=False)
    rows: list[dict[str, object]] = []
    for (h3_cell, category_code, category_desc), part in grouped:
        duration = part["duration_months"]
        event = part["event_observed"]
        support_12m = ((duration >= 12.0) | ((event == 1) & (duration <= 12.0))).sum()
        support_24m = ((duration >= 24.0) | ((event == 1) & (duration <= 24.0))).sum()
        survival_12m = float((duration >= 12.0).sum() / support_12m) if int(support_12m) > 0 else 0.0
        survival_24m = float((duration >= 24.0).sum() / support_24m) if int(support_24m) > 0 else 0.0
        quality_tier = quality_mode(part["quality_tier"].astype("string"))
        rows.append(
            {
                "h3_cell": str(h3_cell),
                "category_code": str(category_code),
                "category_desc": str(category_desc),
                "n_locales": int(len(part)),
                "n_events": int(event.sum()),
                "avg_risk_ensemble": float(part["risk_ensemble"].mean()),
                "avg_risk_percentile": float(part["risk_percentile"].mean()),
                "survival_12m": survival_12m,
                "survival_24m": survival_24m,
                "support_12m": int(support_12m),
                "support_24m": int(support_24m),
                "quality_tier": quality_tier,
            }
        )
    rows.sort(key=lambda item: (item["category_desc"], -int(item["n_locales"]), item["h3_cell"]))
    return rows


def build_category_options(hexes: list[dict[str, object]]) -> list[dict[str, object]]:
    frame = pd.DataFrame(hexes)
    grouped = (
        frame.groupby(["category_code", "category_desc"], dropna=False)
        .agg(n_locales=("n_locales", "sum"), n_hexes=("h3_cell", "nunique"))
        .reset_index()
        .sort_values(["category_code", "n_locales"], ascending=[True, False])
    )
    rows = grouped.to_dict(orient="records")
    rows.sort(key=lambda item: (item["category_code"] != "__all__", -int(item["n_locales"]), item["category_desc"]))
    return rows


def build_zone_payloads() -> dict[str, list[dict[str, object]]]:
    district = pd.read_csv(PROJECT_ROOT / "data" / "exports" / "district_category_survival.csv", low_memory=False)
    barrio = pd.read_csv(PROJECT_ROOT / "data" / "exports" / "barrio_category_survival.csv", low_memory=False)

    keep_cols = [
        "zone_level",
        "zone_code",
        "zone_name",
        "web_supercategory",
        "web_category",
        "display_label",
        "n_locales",
        "n_events",
        "survival_12m",
        "survival_24m",
        "confidence_tier",
    ]

    return {
        "district": normalize_zone_frame(district[keep_cols]),
        "barrio": normalize_zone_frame(barrio[keep_cols]),
    }


def normalize_zone_frame(frame: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for row in frame.itertuples(index=False):
        rows.append(
            {
                "zone_level": str(row.zone_level),
                "zone_code": str(row.zone_code),
                "zone_name": str(row.zone_name),
                "web_supercategory": str(row.web_supercategory),
                "web_category": str(row.web_category),
                "category_desc": str(row.display_label),
                "n_locales": int(row.n_locales),
                "n_events": int(row.n_events),
                "survival_12m": float(row.survival_12m) if pd.notna(row.survival_12m) else 0.0,
                "survival_24m": float(row.survival_24m) if pd.notna(row.survival_24m) else 0.0,
                "confidence_tier": str(row.confidence_tier),
            }
        )
    return rows


def quality_mode(series: pd.Series) -> str:
    priority = {"high": 3, "medium": 2, "low": 1}
    counts = series.value_counts(dropna=True)
    if counts.empty:
      return "low"
    ranked = sorted(counts.index.tolist(), key=lambda value: (-int(counts[value]), -priority.get(str(value), 0), str(value)))
    return str(ranked[0])


if __name__ == "__main__":
    raise SystemExit(main())