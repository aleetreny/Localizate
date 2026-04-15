from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sksurv.compare import compare_survival
from sksurv.nonparametric import kaplan_meier_estimator
from sksurv.util import Surv

from .activity_taxonomy import build_web_taxonomy, render_taxonomy_report
from .paths import DATA_DIR, DOCS_FRONTEND_DIR, DOCS_MODELING_DIR, MODELS_DIR, PROJECT_ROOT, RAW_DATA_DIR


@dataclass(frozen=True)
class ZoneCategoryAnalysisResult:
    taxonomy_csv: Path
    taxonomy_md: Path
    district_csv: Path
    barrio_csv: Path
    stats_json: Path
    report_md: Path


def build_zone_category_survival_analysis(
    *,
    abt_csv: Path | None = None,
    section_geography_csv: Path | None = None,
    activity_audit_csv: Path | None = None,
    raw_manifest_csv: Path | None = None,
    taxonomy_csv: Path | None = None,
    taxonomy_md: Path | None = None,
    district_csv: Path | None = None,
    barrio_csv: Path | None = None,
    stats_json: Path | None = None,
    report_md: Path | None = None,
    min_locales_district: int = 80,
    min_events_district: int = 12,
    min_locales_barrio: int = 40,
    min_events_barrio: int = 8,
    alpha: float = 0.05,
) -> ZoneCategoryAnalysisResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "local_survival_abt.csv")
    resolved_section_geo = section_geography_csv or (DATA_DIR / "processed" / "section_geography.csv")
    resolved_activity_audit = activity_audit_csv or (DATA_DIR / "processed" / "activity_code_normalization_audit.csv")
    resolved_raw_manifest = raw_manifest_csv or (DATA_DIR / "intermediate" / "raw_manifest.csv")
    resolved_taxonomy_csv = taxonomy_csv or (DATA_DIR / "processed" / "web_activity_taxonomy.csv")
    resolved_taxonomy_md = taxonomy_md or (DOCS_FRONTEND_DIR / "activity_taxonomy_web.md")
    resolved_district_csv = district_csv or (DATA_DIR / "exports" / "district_category_survival.csv")
    resolved_barrio_csv = barrio_csv or (DATA_DIR / "exports" / "barrio_category_survival.csv")
    resolved_stats_json = stats_json or (MODELS_DIR / "zone_category_survival_stats.json")
    resolved_report_md = report_md or (DOCS_MODELING_DIR / "zone_category_survival.md")

    for path in (resolved_taxonomy_csv, resolved_taxonomy_md, resolved_district_csv, resolved_barrio_csv, resolved_stats_json, resolved_report_md):
        path.parent.mkdir(parents=True, exist_ok=True)

    abt = pd.read_csv(resolved_abt, low_memory=False)
    section_geo = pd.read_csv(resolved_section_geo, low_memory=False)
    activity_audit = pd.read_csv(resolved_activity_audit, low_memory=False)
    raw_manifest = pd.read_csv(resolved_raw_manifest, low_memory=False)

    taxonomy = build_web_taxonomy(activity_audit)
    resolved_taxonomy_csv.write_text(taxonomy.to_csv(index=False), encoding="utf-8")
    resolved_taxonomy_md.write_text(render_taxonomy_report(taxonomy), encoding="utf-8")

    start_epigrafes = derive_start_epigrafes(abt, raw_manifest=raw_manifest, activity_audit=activity_audit)
    enriched = abt.merge(start_epigrafes, on=["id_local", "first_seen_period"], how="left")
    enriched = enriched.merge(
        taxonomy,
        left_on="epigrafe_code_start",
        right_on="epigrafe_code",
        how="left",
    )
    section_geo = section_geo[["section_key", "district_code", "district_name", "barrio_code", "barrio_name"]].drop_duplicates()
    enriched = enriched.merge(section_geo, left_on="section_key_start", right_on="section_key", how="left", suffixes=("", "_geo"))
    enriched["district_code_effective"] = enriched["district_code_start"].astype("string").fillna(enriched["district_code"].astype("string"))
    enriched["barrio_code_effective"] = enriched["barrio_code_start"].astype("string").fillna(enriched["barrio_code"].astype("string"))
    enriched["district_name"] = enriched["district_name"].astype("string").fillna("Distrito desconocido")
    enriched["barrio_name"] = enriched["barrio_name"].astype("string").fillna("Barrio desconocido")

    investable_mask = enriched["investable"].astype("boolean").fillna(False)
    investable = enriched[investable_mask].copy()
    investable = investable[investable["display_label"].notna()].copy()
    district_dataset = investable[investable["district_code_effective"].notna() & investable["district_name"].ne("Distrito desconocido")].copy()
    barrio_dataset = investable[investable["barrio_code_effective"].notna() & investable["barrio_name"].ne("Barrio desconocido")].copy()

    district_metrics = build_zone_category_metrics(
        district_dataset,
        zone_level="district",
        zone_code_col="district_code_effective",
        zone_name_col="district_name",
        min_locales=min_locales_district,
        min_events=min_events_district,
    )
    barrio_metrics = build_zone_category_metrics(
        barrio_dataset,
        zone_level="barrio",
        zone_code_col="barrio_code_effective",
        zone_name_col="barrio_name",
        min_locales=min_locales_barrio,
        min_events=min_events_barrio,
    )

    district_tests = run_zone_level_logrank_tests(
        district_dataset,
        district_metrics,
        zone_level="district",
        zone_code_col="district_code_effective",
        zone_name_col="district_name",
        min_locales=min_locales_district,
        min_events=min_events_district,
        alpha=alpha,
    )
    category_zone_tests = run_category_zone_logrank_tests(
        district_dataset,
        district_metrics,
        zone_code_col="district_code_effective",
        zone_name_col="district_name",
        min_locales=min_locales_district,
        min_events=min_events_district,
        alpha=alpha,
    )

    district_metrics.to_csv(resolved_district_csv, index=False)
    barrio_metrics.to_csv(resolved_barrio_csv, index=False)

    payload = {
        "taxonomy_summary": {
            "epigrafes_validos_unicos": int(len(taxonomy)),
            "categorias_web": int(taxonomy["display_label"].nunique(dropna=True)),
            "investable_epigrafes": int(taxonomy["investable"].sum()),
            "needs_manual_review": int(taxonomy["needs_manual_review"].sum()),
        },
        "dataset_summary": {
            "abt_rows": int(len(abt)),
            "start_epigrafes_matched": int(start_epigrafes["epigrafe_code_start"].notna().sum()),
            "investable_rows": int(len(investable)),
            "investable_rows_with_district": int(len(district_dataset)),
            "investable_rows_with_barrio": int(len(barrio_dataset)),
            "investable_categories": int(investable["display_label"].nunique(dropna=True)),
            "district_rows": int(len(district_metrics)),
            "barrio_rows": int(len(barrio_metrics)),
        },
        "district_level_tests": district_tests,
        "category_across_districts_tests": category_zone_tests,
    }

    resolved_stats_json.write_text(json.dumps(_to_jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report_md.write_text(render_zone_category_report(payload, district_metrics), encoding="utf-8")

    return ZoneCategoryAnalysisResult(
        taxonomy_csv=resolved_taxonomy_csv,
        taxonomy_md=resolved_taxonomy_md,
        district_csv=resolved_district_csv,
        barrio_csv=resolved_barrio_csv,
        stats_json=resolved_stats_json,
        report_md=resolved_report_md,
    )


def derive_start_epigrafes(abt: pd.DataFrame, *, raw_manifest: pd.DataFrame, activity_audit: pd.DataFrame) -> pd.DataFrame:
    manifest = raw_manifest.copy()
    manifest = manifest[(manifest["source_name"] == "actividades") & (manifest["status"] == "selected")].copy()
    file_list = [(RAW_DATA_DIR / relative).resolve() for relative in manifest["selected_relative_path"].tolist()]
    if not file_list:
        raise ValueError("No selected activity files found in raw manifest")

    epigrafe_lookup = activity_audit[(activity_audit["taxonomy"] == "epigrafe")].copy()
    epigrafe_lookup = epigrafe_lookup[["raw_code", "raw_desc", "clean_code", "clean_desc", "code_valid"]].copy()
    epigrafe_lookup["code_valid"] = epigrafe_lookup["code_valid"].astype(str).str.lower().eq("true")
    frames: list[pd.DataFrame] = []
    for file_path in file_list:
        frame = _read_activity_extract(file_path)
        frame["snapshot_period"] = _period_from_activity_filename(file_path)
        frames.append(frame)

    activities = pd.concat(frames, ignore_index=True)
    activities["id_local"] = pd.to_numeric(activities["id_local"], errors="coerce")
    activities = activities[activities["id_local"].notna()].copy()
    activities["id_local"] = activities["id_local"].astype("int64")
    activities["snapshot_period"] = activities["snapshot_period"].astype("string")
    activities["raw_code"] = activities["id_epigrafe"].fillna("").astype(str).str.strip()
    activities["raw_desc"] = activities["desc_epigrafe"].fillna("").astype(str).str.strip()

    clean = activities.merge(epigrafe_lookup, on=["raw_code", "raw_desc"], how="left")
    clean["epigrafe_valid"] = clean["code_valid"].astype("boolean").fillna(False)
    clean = clean.merge(abt[["id_local", "first_seen_period"]], left_on=["id_local", "snapshot_period"], right_on=["id_local", "first_seen_period"], how="inner")

    def _join_unique(values: pd.Series, separator: str) -> str | None:
        unique_values = sorted({str(value).strip() for value in values if pd.notna(value) and str(value).strip()})
        return separator.join(unique_values) if unique_values else None

    period_agg = (
        clean.groupby(["id_local", "first_seen_period"], dropna=False)
        .agg(
            epigrafe_sig=("clean_code", lambda s: _join_unique(s[clean.loc[s.index, "epigrafe_valid"]], "|")),
            epigrafe_desc_sig=("clean_desc", lambda s: _join_unique(s[clean.loc[s.index, "epigrafe_valid"]], " | ")),
            n_epigrafes=("clean_code", lambda s: int(pd.Series([value for value in s[clean.loc[s.index, "epigrafe_valid"]] if pd.notna(value) and str(value).strip()]).nunique())),
        )
        .reset_index()
    )

    result = abt[["id_local", "first_seen_period"]].merge(period_agg, on=["id_local", "first_seen_period"], how="left")
    result["epigrafe_code_start"] = result["epigrafe_sig"].where(result["n_epigrafes"] == 1)
    result["epigrafe_desc_start"] = result["epigrafe_desc_sig"].where(result["n_epigrafes"] == 1)
    result["n_epigrafes_start_observed"] = result["n_epigrafes"]
    result["epigrafe_assignment_status"] = np.where(
        result["n_epigrafes"].eq(1),
        "single_epigrafe",
        np.where(result["n_epigrafes"].gt(1), "multi_epigrafe", "missing_epigrafe"),
    )
    return result[[
        "id_local",
        "first_seen_period",
        "epigrafe_code_start",
        "epigrafe_desc_start",
        "n_epigrafes_start_observed",
        "epigrafe_assignment_status",
    ]]


def build_zone_category_metrics(
    dataset: pd.DataFrame,
    *,
    zone_level: str,
    zone_code_col: str,
    zone_name_col: str,
    min_locales: int,
    min_events: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    keys = [zone_code_col, zone_name_col, "display_label"]
    grouped = dataset.groupby(keys, dropna=False)
    for key, frame in grouped:
        zone_code, zone_name, display_label = key
        duration = pd.to_numeric(frame["duration_months"], errors="coerce")
        event = pd.to_numeric(frame["event_observed"], errors="coerce").fillna(0).astype(int)
        km12 = estimate_km_survival(duration, event, time_horizon=12.0)
        km24 = estimate_km_survival(duration, event, time_horizon=24.0)
        web_supercategory = _first_non_null(frame["web_supercategory"])
        web_category = _first_non_null(frame["web_category"])
        rows.append(
            {
                "zone_level": zone_level,
                "zone_code": zone_code,
                "zone_name": zone_name,
                "web_supercategory": web_supercategory,
                "web_category": web_category,
                "display_label": display_label,
                "n_locales": int(len(frame)),
                "n_events": int(event.sum()),
                "event_rate": float(event.mean()) if len(frame) else float("nan"),
                "duration_median_months": float(duration.median()) if duration.notna().any() else float("nan"),
                "survival_12m": km12,
                "survival_24m": km24,
                "supported_for_stats": bool(len(frame) >= min_locales and int(event.sum()) >= min_events),
                "confidence_tier": confidence_tier(n_locales=int(len(frame)), n_events=int(event.sum()), zone_level=zone_level),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["rank_within_zone_24m"] = (
        out.sort_values(["zone_code", "survival_24m", "survival_12m", "n_locales"], ascending=[True, False, False, False])
        .groupby("zone_code")
        .cumcount()
        + 1
    )
    return out.sort_values(["zone_code", "rank_within_zone_24m", "display_label"]).reset_index(drop=True)


def run_zone_level_logrank_tests(
    dataset: pd.DataFrame,
    metrics: pd.DataFrame,
    *,
    zone_level: str,
    zone_code_col: str,
    zone_name_col: str,
    min_locales: int,
    min_events: int,
    alpha: float,
) -> dict[str, object]:
    results: dict[str, object] = {}
    if metrics.empty or dataset.empty:
        return results
    supported_groups = compute_supported_groups(
        dataset,
        zone_code_col=zone_code_col,
        zone_name_col=zone_name_col,
        group_col="display_label",
        min_locales=min_locales,
        min_events=min_events,
    )
    for zone_code, supported in supported_groups.groupby("zone_code", dropna=False):
        if len(supported) < 2 or pd.isna(zone_code):
            continue
        subset = dataset[dataset[zone_code_col].astype("string") == str(zone_code)].copy()
        subset = subset[subset["display_label"].isin(supported["display_label"])].copy()
        subset = subset[pd.to_numeric(subset["duration_months"], errors="coerce").notna()].copy()
        if subset["display_label"].nunique(dropna=True) < 2:
            continue
        y = _frame_to_surv(subset)
        group_indicator = subset["display_label"].astype("string").to_numpy()
        try:
            chisq, pvalue = compare_survival(y, group_indicator)
        except ValueError:
            continue
        supported_metrics = metrics[(metrics["zone_code"].astype("string") == str(zone_code)) & (metrics["display_label"].isin(supported["display_label"]))].copy()
        base = supported_metrics[["display_label", "n_locales", "n_events", "survival_24m"]].copy()
        leader = supported_metrics.sort_values(["survival_24m", "survival_12m", "n_locales"], ascending=[False, False, False]).iloc[0]
        pairwise = []
        for row in supported_metrics.itertuples(index=False):
            if row.display_label == leader.display_label:
                continue
            subset_pair = subset[subset["display_label"].isin([leader.display_label, row.display_label])].copy()
            y_pair = _frame_to_surv(subset_pair)
            groups_pair = subset_pair["display_label"].astype("string").to_numpy()
            try:
                pair_chisq, pair_pvalue = compare_survival(y_pair, groups_pair)
            except ValueError:
                continue
            pairwise.append(
                {
                    "leader": leader.display_label,
                    "other": row.display_label,
                    "leader_survival_24m": float(leader.survival_24m),
                    "other_survival_24m": float(row.survival_24m),
                    "chisq": float(pair_chisq),
                    "pvalue": float(pair_pvalue),
                }
            )
        pairwise = apply_bh_correction(pairwise, alpha=alpha)
        leader_significant = bool(pairwise) and all(
            item["leader_survival_24m"] > item["other_survival_24m"] and item["significant"] for item in pairwise
        )
        results[str(zone_code)] = {
            "zone_level": zone_level,
            "zone_name": str(supported["zone_name"].iloc[0]),
            "supported_categories": int(len(supported)),
            "n_locales_supported": int(supported["n_locales"].sum()),
            "n_events_supported": int(supported["n_events"].sum()),
            "chisq": float(chisq),
            "pvalue": float(pvalue),
            "significant": bool(float(pvalue) < alpha),
            "leader_category": str(leader.display_label),
            "leader_survival_24m": float(leader.survival_24m),
            "leader_significantly_better_all": leader_significant,
            "pairwise_leader_vs_rest": pairwise,
            "categories": base.sort_values("survival_24m", ascending=False).to_dict(orient="records"),
        }
    return results


def run_category_zone_logrank_tests(
    dataset: pd.DataFrame,
    metrics: pd.DataFrame,
    *,
    zone_code_col: str,
    zone_name_col: str,
    min_locales: int,
    min_events: int,
    alpha: float,
) -> dict[str, object]:
    results: dict[str, object] = {}
    if metrics.empty or dataset.empty:
        return results
    supported_groups = compute_supported_groups(
        dataset,
        zone_code_col=zone_code_col,
        zone_name_col=zone_name_col,
        group_col="display_label",
        min_locales=min_locales,
        min_events=min_events,
    )
    for category, supported in supported_groups.groupby("display_label", dropna=False):
        if len(supported) < 2 or pd.isna(category):
            continue
        supported_zone_codes = supported["zone_code"].astype("string").tolist()
        subset = dataset[(dataset["display_label"] == category) & (dataset[zone_code_col].astype("string").isin(supported_zone_codes))].copy()
        subset = subset[pd.to_numeric(subset["duration_months"], errors="coerce").notna()].copy()
        if subset[zone_code_col].nunique(dropna=True) < 2:
            continue
        y = _frame_to_surv(subset)
        groups = subset[zone_name_col].astype("string").to_numpy()
        try:
            chisq, pvalue = compare_survival(y, groups)
        except ValueError:
            continue
        supported_metrics = metrics[(metrics["display_label"] == category) & (metrics["zone_code"].astype("string").isin(supported_zone_codes))].copy()
        results[str(category)] = {
            "districts_supported": int(len(supported)),
            "n_locales_supported": int(supported["n_locales"].sum()),
            "n_events_supported": int(supported["n_events"].sum()),
            "chisq": float(chisq),
            "pvalue": float(pvalue),
            "significant": bool(float(pvalue) < alpha),
            "districts": supported_metrics[["zone_code", "zone_name", "survival_24m", "n_locales", "n_events"]].sort_values("survival_24m", ascending=False).to_dict(orient="records"),
        }
    return results


def compute_supported_groups(
    dataset: pd.DataFrame,
    *,
    zone_code_col: str,
    zone_name_col: str,
    group_col: str,
    min_locales: int,
    min_events: int,
) -> pd.DataFrame:
    summary = (
        dataset.groupby([zone_code_col, zone_name_col, group_col], dropna=False)
        .agg(
            n_locales=("id_local", "size"),
            n_events=("event_observed", lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).astype(int).sum())),
        )
        .reset_index()
        .rename(columns={zone_code_col: "zone_code", zone_name_col: "zone_name", group_col: "display_label"})
    )
    return summary[(summary["n_locales"] >= min_locales) & (summary["n_events"] >= min_events)].copy()


def estimate_km_survival(duration: pd.Series, event: pd.Series, *, time_horizon: float) -> float:
    mask = duration.notna()
    duration_values = duration[mask].astype(float).to_numpy()
    event_values = event[mask].astype(bool).to_numpy()
    if duration_values.size == 0:
        return float("nan")
    times, survival = kaplan_meier_estimator(event_values, duration_values)
    if times.size == 0:
        return 1.0
    idx = np.searchsorted(times, float(time_horizon), side="right") - 1
    if idx < 0:
        return 1.0
    return float(survival[idx])


def confidence_tier(*, n_locales: int, n_events: int, zone_level: str) -> str:
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


def apply_bh_correction(items: list[dict[str, object]], *, alpha: float) -> list[dict[str, object]]:
    if not items:
        return items
    ordered = sorted(enumerate(items), key=lambda pair: float(pair[1]["pvalue"]))
    n = len(ordered)
    adjusted = [0.0] * n
    previous = 1.0
    for rank, (original_index, item) in enumerate(reversed(ordered), start=1):
        pvalue = float(item["pvalue"])
        adjusted_value = min(previous, pvalue * n / (n - rank + 1))
        adjusted[n - rank] = adjusted_value
        previous = adjusted_value
    for (position, (original_index, item)), adj in zip(enumerate(ordered), adjusted):
        items[original_index]["pvalue_adj"] = float(min(1.0, adj))
        items[original_index]["significant"] = bool(float(min(1.0, adj)) < alpha)
    return items


def render_zone_category_report(payload: dict[str, object], district_metrics: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Zone Category Survival")
    lines.append("")
    lines.append("Comparacion de supervivencia por categoria comercial amigable y por zona para soportar la web de recomendacion de apertura.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    taxonomy_summary = payload.get("taxonomy_summary", {})
    dataset_summary = payload.get("dataset_summary", {})
    lines.append(f"- Epigrafes validos unicos: {taxonomy_summary.get('epigrafes_validos_unicos')}")
    lines.append(f"- Categorias web: {taxonomy_summary.get('categorias_web')}")
    lines.append(f"- Filas investables: {dataset_summary.get('investable_rows')}")
    lines.append(f"- Filas investables con distrito conocido: {dataset_summary.get('investable_rows_with_district')}")
    lines.append(f"- Categorias investables observadas: {dataset_summary.get('investable_categories')}")
    lines.append("")
    lines.append("## Lectura ejecutiva")
    lines.append("")
    district_tests = payload.get("district_level_tests", {})
    category_zone_tests = payload.get("category_across_districts_tests", {})
    significant_districts = sum(1 for item in district_tests.values() if item.get("significant"))
    significant_categories = sum(1 for item in category_zone_tests.values() if item.get("significant"))
    lines.append(f"- Distritos con diferencias significativas entre categorias: {significant_districts}")
    lines.append(f"- Categorias con diferencias significativas entre distritos: {significant_categories}")
    lines.append("- La recomendacion web debe mostrarse como supervivencia esperada con evidencia suficiente, no como certeza determinista.")
    lines.append("")
    lines.append("## Mejores categorias por distrito")
    lines.append("")
    if not district_metrics.empty:
        top = district_metrics[district_metrics["rank_within_zone_24m"] == 1].sort_values(["confidence_tier", "survival_24m"], ascending=[False, False])
        for row in top.itertuples(index=False):
            lines.append(
                f"- {row.zone_name} -> {row.display_label}: surv12={row.survival_12m:.4f}, surv24={row.survival_24m:.4f}, locales={row.n_locales}, eventos={row.n_events}, confianza={row.confidence_tier}"
            )
    lines.append("")
    lines.append("## Distritos con evidencia estadistica")
    lines.append("")
    for zone_code, item in district_tests.items():
        if not item.get("significant"):
            continue
        lines.append(
            f"- {item.get('zone_name')} ({zone_code}) -> p={float(item.get('pvalue')):.6f}, categorias soportadas={item.get('supported_categories')}, lider={item.get('leader_category')}, lider_mejor_que_todas={item.get('leader_significantly_better_all')}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def _frame_to_surv(frame: pd.DataFrame) -> np.ndarray:
    duration = pd.to_numeric(frame["duration_months"], errors="coerce")
    event = pd.to_numeric(frame["event_observed"], errors="coerce").fillna(0).astype(int)
    mask = duration.notna()
    return Surv.from_arrays(event=event[mask].to_numpy(dtype=bool), time=duration[mask].to_numpy(dtype=float))


def _to_jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _to_jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _period_from_activity_filename(file_path: Path) -> str:
    name = file_path.stem
    parts = name.split("_")
    if len(parts) < 2:
        raise ValueError(f"Could not infer snapshot period from file name: {file_path.name}")
    year = parts[0]
    month = parts[1]
    return f"{year}-{month}"


def _read_activity_extract(file_path: Path) -> pd.DataFrame:
    first_line = file_path.open("r", encoding="latin1").readline().strip().lstrip("\ufeff")
    has_header = first_line.startswith("id_local;") or first_line.startswith('"id_local";')
    if has_header:
        frame = pd.read_csv(
            file_path,
            sep=";",
            encoding="latin1",
            dtype=str,
            low_memory=False,
        )
        columns = {column.strip().strip('"'): column for column in frame.columns}
        return frame[[columns["id_local"], columns["id_epigrafe"], columns["desc_epigrafe"]]].rename(
            columns={columns["id_local"]: "id_local", columns["id_epigrafe"]: "id_epigrafe", columns["desc_epigrafe"]: "desc_epigrafe"}
        )

    raw = pd.read_csv(
        file_path,
        sep=";",
        encoding="latin1",
        dtype=str,
        header=None,
        low_memory=False,
    )
    subset = raw.iloc[:, [0, -2, -1]].copy()
    subset.columns = ["id_local", "id_epigrafe", "desc_epigrafe"]
    return subset


def _first_non_null(series: pd.Series) -> str | None:
    values = series.dropna()
    if values.empty:
        return None
    return str(values.iloc[0])