from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .paths import DATA_DIR, DOCS_DIR, PROJECT_ROOT


@dataclass(frozen=True)
class ModelingReadinessResult:
    report_md: Path
    report_json: Path
    status: str


def run_modeling_readiness_check(
    *,
    abt_csv: Path | None = None,
    baseline_metrics_json: Path | None = None,
    geospatial_manifest_csv: Path | None = None,
    report_md: Path | None = None,
    report_json: Path | None = None,
) -> ModelingReadinessResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "local_survival_abt.csv")
    resolved_baseline_metrics = baseline_metrics_json or (PROJECT_ROOT / "models" / "survival_baseline_metrics.json")
    resolved_geospatial_manifest = geospatial_manifest_csv or (DATA_DIR / "processed" / "censo_geospatial_manifest.csv")
    resolved_report_md = report_md or (DOCS_DIR / "modeling_readiness.md")
    resolved_report_json = report_json or (PROJECT_ROOT / "models" / "modeling_readiness.json")

    resolved_report_md.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_json.parent.mkdir(parents=True, exist_ok=True)

    abt = pd.read_csv(resolved_abt, low_memory=False)
    geo = pd.read_csv(resolved_geospatial_manifest)

    baseline_metrics = {}
    if resolved_baseline_metrics.exists():
        baseline_metrics = json.loads(resolved_baseline_metrics.read_text(encoding="utf-8"))

    events = pd.to_numeric(abt["event_observed"], errors="coerce").fillna(0)
    duration = pd.to_numeric(abt["duration_months"], errors="coerce")
    renta = pd.to_numeric(abt.get("renta_best_eur_start"), errors="coerce")

    summary = {
        "rows_abt": int(len(abt)),
        "events_total": int(events.sum()),
        "event_rate": float(events.mean()) if len(events) else float("nan"),
        "duration_median_months": float(duration.median()) if duration.notna().any() else float("nan"),
        "h3_coverage": float(abt["h3_cell_start"].notna().mean()) if "h3_cell_start" in abt.columns else float("nan"),
        "renta_coverage": float(renta.notna().mean()) if renta.notna().any() else 0.0,
        "geo_transition_rows": int(pd.to_numeric(geo.get("rows_transition_requires_review"), errors="coerce").fillna(0).sum()),
    }

    checks = {
        "abt_non_empty": summary["rows_abt"] > 0,
        "events_minimum": summary["events_total"] >= 300,
        "event_rate_minimum": summary["event_rate"] >= 0.001,
        "h3_coverage_minimum": summary["h3_coverage"] >= 0.70,
        "renta_coverage_minimum": summary["renta_coverage"] >= 0.20,
        "transition_rows_flagged": summary["geo_transition_rows"] >= 0,
        "baseline_quality_gate_pass": bool(baseline_metrics.get("quality_gate", {}).get("status") == "pass") if baseline_metrics else False,
    }

    warnings: list[str] = []
    if summary["renta_coverage"] < 0.4:
        warnings.append("low_observed_renta_coverage_expected_due_to_post_2023_carry_forward")
    if summary["event_rate"] < 0.002:
        warnings.append("rare_event_regime_use_time_blocked_validation_and_calibration")
    split_event_counts = baseline_metrics.get("split_event_counts", {}) if baseline_metrics else {}
    if split_event_counts:
        if int(split_event_counts.get("valid", 0)) < 20:
            warnings.append("very_low_validation_events")
        if int(split_event_counts.get("test", 0)) < 20:
            warnings.append("very_low_test_events")

    status = "ready_with_caveats" if checks["abt_non_empty"] and checks["events_minimum"] and checks["baseline_quality_gate_pass"] else "review_required"

    payload = {
        "status": status,
        "summary": _to_jsonable(summary),
        "checks": _to_jsonable(checks),
        "warnings": warnings,
        "next_actions": [
            "enable canonical survival stack (scikit-learn/scikit-survival/scipy)",
            "train Cox/GBSA/RSF with the same policy gate",
            "stabilize validation/test horizons to increase observed events",
        ],
    }

    resolved_report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report_md.write_text(render_modeling_readiness_markdown(payload), encoding="utf-8")

    return ModelingReadinessResult(
        report_md=resolved_report_md,
        report_json=resolved_report_json,
        status=status,
    )


def render_modeling_readiness_markdown(payload: dict[str, object]) -> str:
    summary = payload.get("summary", {})
    checks = payload.get("checks", {})
    warnings = payload.get("warnings", [])
    actions = payload.get("next_actions", [])

    lines: list[str] = []
    lines.append("# Modeling Readiness")
    lines.append("")
    lines.append("Chequeo continuo de calidad para asegurar que el paso a modelos de supervivencia avanzados sea estable y trazable.")
    lines.append("")
    lines.append(f"- Estado global: {payload.get('status')}")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Filas ABT: {summary.get('rows_abt'):,}")
    lines.append(f"- Eventos totales: {summary.get('events_total'):,}")
    lines.append(f"- Tasa de evento: {summary.get('event_rate')}")
    lines.append(f"- Mediana duracion (meses): {summary.get('duration_median_months')}")
    lines.append(f"- Cobertura H3: {summary.get('h3_coverage')}")
    lines.append(f"- Cobertura renta observada: {summary.get('renta_coverage')}")
    lines.append(f"- Filas marcadas por transicion CRS: {summary.get('geo_transition_rows')}")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append(json.dumps(checks, ensure_ascii=False, sort_keys=True))
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    lines.append(json.dumps(warnings, ensure_ascii=False))
    lines.append("")
    lines.append("## Siguientes acciones")
    lines.append("")
    for action in actions:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines) + "\n"


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
