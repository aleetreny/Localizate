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
    canonical_metrics_json: Path | None = None,
    geospatial_manifest_csv: Path | None = None,
    report_md: Path | None = None,
    report_json: Path | None = None,
) -> ModelingReadinessResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "local_survival_abt.csv")
    resolved_baseline_metrics = baseline_metrics_json or (PROJECT_ROOT / "models" / "survival_baseline_metrics.json")
    resolved_canonical_metrics = canonical_metrics_json or (PROJECT_ROOT / "models" / "survival_canonical_metrics.json")
    resolved_geospatial_manifest = geospatial_manifest_csv or (DATA_DIR / "processed" / "censo_geospatial_manifest.csv")
    resolved_report_md = report_md or (DOCS_DIR / "modeling_readiness.md")
    resolved_report_json = report_json or (PROJECT_ROOT / "models" / "modeling_readiness.json")

    resolved_report_md.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_json.parent.mkdir(parents=True, exist_ok=True)

    abt = pd.read_csv(resolved_abt, low_memory=False)
    geo = pd.read_csv(resolved_geospatial_manifest)

    baseline_metrics = _load_json_if_exists(resolved_baseline_metrics)
    canonical_metrics = _load_json_if_exists(resolved_canonical_metrics)
    canonical_gate = canonical_metrics.get("quality_gate", {}) if canonical_metrics else {}
    canonical_gate_status = str(canonical_gate.get("status") or "missing")

    uno_c_index = canonical_metrics.get("uno_c_index", {}) if canonical_metrics else {}
    dynamic_auc = canonical_metrics.get("dynamic_auc", {}) if canonical_metrics else {}
    integrated_brier = canonical_metrics.get("integrated_brier_score", {}) if canonical_metrics else {}

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
        "canonical_quality_gate_status": canonical_gate_status,
        "canonical_uno_valid": _extract_metric_value(uno_c_index, split_name="valid", metric_key="uno_c_index"),
        "canonical_uno_test": _extract_metric_value(uno_c_index, split_name="test", metric_key="uno_c_index"),
        "canonical_dynamic_auc_valid": _extract_metric_value(dynamic_auc, split_name="valid", metric_key="mean_auc"),
        "canonical_dynamic_auc_test": _extract_metric_value(dynamic_auc, split_name="test", metric_key="mean_auc"),
        "canonical_ibs_valid_available": _split_has_any_finite_ibs(integrated_brier, split_name="valid"),
        "canonical_ibs_test_available": _split_has_any_finite_ibs(integrated_brier, split_name="test"),
    }

    checks = {
        "abt_non_empty": summary["rows_abt"] > 0,
        "events_minimum": summary["events_total"] >= 300,
        "event_rate_minimum": summary["event_rate"] >= 0.001,
        "h3_coverage_minimum": summary["h3_coverage"] >= 0.70,
        "renta_coverage_minimum": summary["renta_coverage"] >= 0.20,
        "transition_rows_flagged": summary["geo_transition_rows"] >= 0,
        "canonical_metrics_available": bool(canonical_metrics),
        "canonical_quality_gate_acceptable": _canonical_gate_status_is_acceptable(canonical_gate_status),
    }

    warnings: list[str] = []
    if summary["renta_coverage"] < 0.4:
        warnings.append("low_observed_renta_coverage_expected_due_to_post_2023_carry_forward")
    if summary["event_rate"] < 0.002:
        warnings.append("rare_event_regime_use_time_blocked_validation_and_calibration")
    split_event_counts = canonical_metrics.get("split_event_counts", {}) if canonical_metrics else {}
    if not split_event_counts and baseline_metrics:
        split_event_counts = baseline_metrics.get("split_event_counts", {})
    if split_event_counts:
        if int(split_event_counts.get("valid", 0)) < 20:
            warnings.append("very_low_validation_events")
        if int(split_event_counts.get("test", 0)) < 20:
            warnings.append("very_low_test_events")
    for warning in canonical_gate.get("warnings", []):
        warnings.append(str(warning))
    warnings = list(dict.fromkeys(warnings))

    status = _resolve_readiness_status(checks, warnings, canonical_gate_status)

    payload = {
        "status": status,
        "summary": _to_jsonable(summary),
        "checks": _to_jsonable(checks),
        "warnings": warnings,
        "next_actions": [
            "stabilize valid/test evaluation under rare-event regime",
            "monitor robust survival metrics (Uno, dynamic AUC, IBS) in each iteration",
            "prepare frontend validation on top of local_survival_map_export.csv",
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
    lines.append("## Lectura ejecutiva")
    lines.append("")
    for bullet in _build_readiness_executive_summary(payload):
        lines.append(f"- {bullet}")
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
    lines.append(f"- Quality gate canonico: {summary.get('canonical_quality_gate_status')}")
    lines.append(f"- Uno C-index valid: {summary.get('canonical_uno_valid')}")
    lines.append(f"- Uno C-index test: {summary.get('canonical_uno_test')}")
    lines.append(f"- Dynamic AUC valid: {summary.get('canonical_dynamic_auc_valid')}")
    lines.append(f"- Dynamic AUC test: {summary.get('canonical_dynamic_auc_test')}")
    lines.append(f"- IBS valido disponible: {summary.get('canonical_ibs_valid_available')}")
    lines.append(f"- IBS test disponible: {summary.get('canonical_ibs_test_available')}")
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


def _load_json_if_exists(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_gate_status_is_acceptable(status: str) -> bool:
    return status in {"pass", "pass_with_caveats"}


def _extract_metric_value(metrics: dict[str, object], *, split_name: str, metric_key: str) -> float | None:
    value = pd.to_numeric(metrics.get(split_name, {}).get(metric_key), errors="coerce")
    if pd.isna(value):
        return None
    return float(value)


def _split_has_any_finite_ibs(integrated_brier: dict[str, object], *, split_name: str) -> bool:
    for model_name in ("cox", "rsf", "gbsa"):
        value = pd.to_numeric(integrated_brier.get(model_name, {}).get(split_name, {}).get("ibs"), errors="coerce")
        if pd.notna(value) and np.isfinite(float(value)):
            return True
    return False


def _resolve_readiness_status(checks: dict[str, bool], warnings: list[str], canonical_gate_status: str) -> str:
    hard_checks = [
        checks.get("abt_non_empty", False),
        checks.get("events_minimum", False),
        checks.get("event_rate_minimum", False),
        checks.get("h3_coverage_minimum", False),
        checks.get("canonical_metrics_available", False),
        checks.get("canonical_quality_gate_acceptable", False),
    ]
    if not all(hard_checks):
        return "review_required"
    if canonical_gate_status == "pass" and not warnings:
        return "ready"
    return "ready_with_caveats"


def _build_readiness_executive_summary(payload: dict[str, object]) -> list[str]:
    summary = payload.get("summary", {})
    warnings = payload.get("warnings", [])
    status = str(payload.get("status") or "unknown")
    quality_gate = summary.get("canonical_quality_gate_status")
    uno_valid = summary.get("canonical_uno_valid")
    uno_test = summary.get("canonical_uno_test")
    auc_valid = summary.get("canonical_dynamic_auc_valid")
    auc_test = summary.get("canonical_dynamic_auc_test")

    bullets = [
        f"Estado final: {status}; gate canonico: {quality_gate}.",
        f"Discriminacion ensemble: valid Uno={_fmt_summary_metric(uno_valid)}, test Uno={_fmt_summary_metric(uno_test)}.",
        f"Horizontes dinamicos: valid mean AUC={_fmt_summary_metric(auc_valid)}, test mean AUC={_fmt_summary_metric(auc_test)}.",
    ]
    if "very_low_validation_events" in warnings or "very_low_test_events" in warnings:
        bullets.append("La principal limitacion sigue siendo estadistica: muy pocos eventos en valid/test para declarar estabilidad fuerte.")
    if status == "ready_with_caveats":
        bullets.append("La pipeline sirve para export operativo y comparacion iterativa, pero todavia no para afirmar excelencia robusta fuera de muestra.")
    return bullets


def _fmt_summary_metric(value: object) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "nan"
    return f"{float(numeric):.4f}"
