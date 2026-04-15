from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.util import Surv

from .activity_taxonomy import macro_category_feature_names
from .paths import DATA_DIR, DOCS_MODELING_DIR, MODELS_DIR, PROJECT_ROOT
from .survival_baseline import apply_training_policies, build_feature_frame
from .survival_canonical import DEFAULT_HORIZONS, _compute_dynamic_auc_by_split, _compute_uno_c_index_by_split, _frame_to_survival, _sample_training_indices
from .survival_features import MODEL_FEATURE_SPECS
from .survival_rolling_backtest import build_walk_forward_folds, derive_event_quantile_cutoffs


ProgressCallback = Callable[[dict[str, object]], None]


@dataclass(frozen=True)
class CoxAblationResult:
    metrics_json: Path
    report_md: Path
    evaluated_blocks: int


def run_activity_survival_cox_ablation(
    *,
    abt_csv: Path | None = None,
    hpo_json: Path | None = None,
    metrics_json: Path | None = None,
    report_md: Path | None = None,
    transition_policy_train: str = "exclude_transition",
    renta_max_year: int = 2023,
    quantiles: tuple[float, ...] = (0.55, 0.65, 0.75, 0.85, 0.95),
    min_valid_events: int = 20,
    min_test_events: int = 20,
    fit_max_rows: int | None = None,
    alpha: float | None = None,
    ties: str | None = None,
    feature_profile: str = "full",
    progress_callback: ProgressCallback | None = None,
) -> CoxAblationResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "activity_survival_abt.csv")
    resolved_hpo = hpo_json or (MODELS_DIR / "activity_survival_hpo.json")
    resolved_metrics = metrics_json or (MODELS_DIR / "activity_survival_cox_ablation.json")
    resolved_report = report_md or (DOCS_MODELING_DIR / "activity_survival_cox_ablation.md")

    resolved_metrics.parent.mkdir(parents=True, exist_ok=True)
    resolved_report.parent.mkdir(parents=True, exist_ok=True)

    _emit_progress(progress_callback, stage="start", progress=0.01, message="starting Cox ablation")

    abt = pd.read_csv(resolved_abt, low_memory=False)
    payload = apply_training_policies(abt, transition_policy=transition_policy_train, renta_max_year=renta_max_year)
    dataset = payload["dataset"].copy()
    dataset["first_seen_period"] = dataset["first_seen_period"].astype("string")
    dataset["event_observed"] = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    dataset["duration_months"] = pd.to_numeric(dataset["duration_months"], errors="coerce").fillna(0).astype(float)
    feature_frame = build_feature_frame(dataset, feature_profile=feature_profile)

    cox_params = _resolve_cox_params(hpo_json=resolved_hpo, alpha=alpha, ties=ties)
    blocks = build_activity_cox_feature_blocks(feature_frame.columns)
    cutoffs = derive_event_quantile_cutoffs(dataset, quantiles=quantiles)
    folds = build_walk_forward_folds(
        dataset,
        cutoff_periods=cutoffs,
        min_valid_events=min_valid_events,
        min_test_events=min_test_events,
    )
    if not folds:
        raise ValueError("No viable folds found for Cox ablation")

    _emit_progress(progress_callback, stage="context", progress=0.08, message=f"prepared {len(folds)} folds and {len(blocks)} ablation blocks")

    baseline = _evaluate_cox_feature_subset(
        dataset=dataset,
        feature_frame=feature_frame,
        selected_columns=list(feature_frame.columns),
        folds=folds,
        alpha=float(cox_params["alpha"]),
        ties=str(cox_params["ties"]),
        fit_max_rows=fit_max_rows,
    )

    results: list[dict[str, object]] = []
    total_runs = len(blocks) + 1
    for index, block in enumerate(blocks, start=1):
        remaining_columns = [column for column in feature_frame.columns if column not in set(block["columns"])]
        progress = 0.08 + (index / total_runs) * 0.84
        _emit_progress(progress_callback, stage="ablation", progress=progress, message=f"evaluating drop block {block['name']}")
        variant = _evaluate_cox_feature_subset(
            dataset=dataset,
            feature_frame=feature_frame,
            selected_columns=remaining_columns,
            folds=folds,
            alpha=float(cox_params["alpha"]),
            ties=str(cox_params["ties"]),
            fit_max_rows=fit_max_rows,
        )
        results.append(
            {
                "block": block,
                **variant,
                "delta_vs_baseline": _compute_deltas(baseline["aggregate"], variant["aggregate"], baseline["objective"], variant["objective"]),
            }
        )

    ranked_by_test_uno = sorted(
        results,
        key=lambda item: _coerce_float(item.get("delta_vs_baseline", {}).get("test_uno_mean")) if _coerce_float(item.get("delta_vs_baseline", {}).get("test_uno_mean")) is not None else float("inf"),
    )
    ranked_by_objective = sorted(
        results,
        key=lambda item: _coerce_float(item.get("delta_vs_baseline", {}).get("objective")) if _coerce_float(item.get("delta_vs_baseline", {}).get("objective")) is not None else float("inf"),
    )

    payload_out = {
        "source_artifacts": {
            "abt_csv": str(resolved_abt),
            "hpo_json": str(resolved_hpo),
        },
        "training_context": {
            "rows": int(len(dataset)),
            "fold_count": int(len(folds)),
            "cutoffs": list(cutoffs),
            "feature_profile": feature_profile,
            "transition_policy": transition_policy_train,
            "renta_max_year": int(renta_max_year),
            "fit_max_rows": int(fit_max_rows) if fit_max_rows is not None else None,
        },
        "cox_params": cox_params,
        "baseline": baseline,
        "ablations": results,
        "ranking_by_test_uno_delta": [
            _summarize_ablation_row(item) for item in ranked_by_test_uno
        ],
        "ranking_by_objective_delta": [
            _summarize_ablation_row(item) for item in ranked_by_objective
        ],
    }

    resolved_metrics.write_text(json.dumps(_to_jsonable(payload_out), ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report.write_text(render_activity_cox_ablation_markdown(payload_out), encoding="utf-8")
    _emit_progress(progress_callback, stage="complete", progress=1.0, message="cox ablation artifacts written")

    return CoxAblationResult(
        metrics_json=resolved_metrics,
        report_md=resolved_report,
        evaluated_blocks=len(results),
    )


def build_activity_cox_feature_blocks(feature_columns: pd.Index | list[str] | tuple[str, ...]) -> list[dict[str, object]]:
    available = {str(column) for column in feature_columns}
    blocks: list[dict[str, object]] = []
    category_to_block = {
        "socioeconomic": ("socioeconomic", "Socioeconomia"),
        "data_quality": ("data_quality", "Calidad de dato"),
        "activity": ("activity_complexity", "Complejidad de actividad"),
        "competition": ("competition_stock", "Competencia stock"),
        "competition_flow": ("competition_flow", "Flujos competitivos"),
        "competition_concentration": ("competition_concentration", "Concentracion competitiva"),
        "zone_dynamics": ("zone_dynamics", "Dinamica de zona"),
        "avisos": ("avisos", "Avisos"),
        "metro": ("metro", "Accesibilidad metro"),
        "external_panel": ("external_panel", "Panel distrital externo"),
        "external_vulnerability": ("external_vulnerability", "Vulnerabilidad IGUALA"),
        "temporal": ("temporal", "Temporalidad de entrada"),
    }

    for category, (name, label) in category_to_block.items():
        columns = [spec.name for spec in MODEL_FEATURE_SPECS if spec.category == category and spec.name in available]
        if columns:
            blocks.append({"name": name, "label": label, "columns": columns})

    macro_columns = [column for column in macro_category_feature_names() if column in available]
    if macro_columns:
        blocks.append({"name": "activity_identity", "label": "Identidad de actividad", "columns": macro_columns})

    covered = {column for block in blocks for column in block["columns"]}
    remaining = sorted(available - covered)
    if remaining:
        blocks.append({"name": "misc_unassigned", "label": "Features sin clasificar", "columns": remaining})

    return blocks


def render_activity_cox_ablation_markdown(payload: dict[str, object]) -> str:
    baseline = payload.get("baseline", {})
    rows = payload.get("ranking_by_test_uno_delta", [])
    lines: list[str] = []
    lines.append("# Activity Survival Cox Ablation")
    lines.append("")
    lines.append("Ablation leave-one-block-out sobre `activity_survival` usando `cox_only` y los mismos folds rolling del benchmark temporal.")
    lines.append("")
    lines.append("## Configuracion")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(payload.get("training_context", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append(f"- Cox params: {json.dumps(_to_jsonable(payload.get('cox_params', {})), ensure_ascii=False)}")
    lines.append("")
    lines.append("## Baseline")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(baseline.get("aggregate", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Lectura ejecutiva")
    lines.append("")
    for bullet in _build_ablation_summary(payload):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## Resultados por bloque")
    lines.append("")
    lines.append("| bloque | cols | delta test Uno | delta valid Uno | delta test AUC | delta objective |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for row in rows:
        lines.append(
            "| {label} | {n_cols} | {d_test_uno} | {d_valid_uno} | {d_test_auc} | {d_objective} |".format(
                label=row.get("label", "?"),
                n_cols=row.get("n_cols", 0),
                d_test_uno=_fmt(row.get("delta_test_uno_mean")),
                d_valid_uno=_fmt(row.get("delta_valid_uno_mean")),
                d_test_auc=_fmt(row.get("delta_test_dynamic_auc_mean")),
                d_objective=_fmt(row.get("delta_objective")),
            )
        )
    lines.append("")
    lines.append("## Payload")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(payload.get("ablations", [])), ensure_ascii=False, indent=2))
    lines.append("")
    return "\n".join(lines) + "\n"


def _build_ablation_summary(payload: dict[str, object]) -> list[str]:
    baseline = payload.get("baseline", {})
    ranked = payload.get("ranking_by_test_uno_delta", [])
    bullets: list[str] = []
    baseline_test_uno = _coerce_float(baseline.get("aggregate", {}).get("test_uno", {}).get("mean"))
    baseline_valid_uno = _coerce_float(baseline.get("aggregate", {}).get("valid_uno", {}).get("mean"))
    baseline_test_auc = _coerce_float(baseline.get("aggregate", {}).get("test_dynamic_auc_mean", {}).get("mean"))
    bullets.append(
        f"Baseline Cox afinado: valid Uno={_fmt(baseline_valid_uno)}, test Uno={_fmt(baseline_test_uno)}, test mean AUC={_fmt(baseline_test_auc)}."
    )
    if ranked:
        strongest = ranked[0]
        bullets.append(
            f"El bloque cuya retirada mas dana el test Uno es `{strongest.get('name')}` ({strongest.get('label')}), con delta={_fmt(strongest.get('delta_test_uno_mean'))}."
        )
        improvements = [row for row in ranked if _coerce_float(row.get("delta_test_uno_mean")) is not None and float(row.get("delta_test_uno_mean")) > 0]
        if improvements:
            best_improvement = max(improvements, key=lambda item: float(item.get("delta_test_uno_mean", float("-inf"))))
            bullets.append(
                f"Hay al menos un bloque que parece ruidoso: quitar `{best_improvement.get('name')}` mejora el test Uno en {_fmt(best_improvement.get('delta_test_uno_mean'))}."
            )
        else:
            bullets.append("Ningun bloque mejora el test Uno al retirarlo; el dano es cero o negativo en todos los casos.")
    return bullets


def _resolve_cox_params(*, hpo_json: Path, alpha: float | None, ties: str | None) -> dict[str, object]:
    resolved_alpha = float(alpha) if alpha is not None else 0.01
    resolved_ties = str(ties) if ties is not None else "breslow"
    if hpo_json.exists():
        payload = json.loads(hpo_json.read_text(encoding="utf-8"))
        best_trial = payload.get("best_trial", {}) if isinstance(payload, dict) else {}
        if isinstance(best_trial, dict) and str(best_trial.get("family")) == "cox_only":
            params = best_trial.get("params", {}) if isinstance(best_trial.get("params"), dict) else {}
            if alpha is None and pd.notna(pd.to_numeric(params.get("alpha"), errors="coerce")):
                resolved_alpha = float(params.get("alpha"))
            if ties is None and params.get("ties"):
                resolved_ties = str(params.get("ties"))
    return {"alpha": float(resolved_alpha), "ties": str(resolved_ties)}


def _evaluate_cox_feature_subset(
    *,
    dataset: pd.DataFrame,
    feature_frame: pd.DataFrame,
    selected_columns: list[str],
    folds: list[dict[str, object]],
    alpha: float,
    ties: str,
    fit_max_rows: int | None,
) -> dict[str, object]:
    fold_results: list[dict[str, object]] = []
    for fold in folds:
        fold_results.append(
            _evaluate_cox_fold(
                dataset=dataset,
                feature_frame=feature_frame[selected_columns],
                fold=fold,
                alpha=alpha,
                ties=ties,
                fit_max_rows=fit_max_rows,
            )
        )
    aggregate = _aggregate_fold_metrics(fold_results)
    objective = _objective_from_aggregate(aggregate)
    return {
        "selected_feature_count": int(len(selected_columns)),
        "selected_columns": list(selected_columns),
        "aggregate": aggregate,
        "objective": float(objective),
        "fold_results": fold_results,
    }


def _evaluate_cox_fold(
    *,
    dataset: pd.DataFrame,
    feature_frame: pd.DataFrame,
    fold: dict[str, object],
    alpha: float,
    ties: str,
    fit_max_rows: int | None,
) -> dict[str, object]:
    train_mask = np.asarray(fold["train_mask"], dtype=bool)
    valid_mask = np.asarray(fold["valid_mask"], dtype=bool)
    test_mask = np.asarray(fold["test_mask"], dtype=bool)
    eval_mask = train_mask | valid_mask | test_mask

    fold_df = dataset.loc[eval_mask].copy()
    x_all = feature_frame.loc[eval_mask].copy()
    fold_df["split"] = np.select(
        [train_mask[eval_mask], valid_mask[eval_mask], test_mask[eval_mask]],
        ["train", "valid", "test"],
        default="holdout",
    )

    y_struct = Surv.from_arrays(
        event=fold_df["event_observed"].astype(bool).to_numpy(),
        time=fold_df["duration_months"].astype(float).to_numpy(),
    )
    fit_mask = fold_df["split"].astype("string").eq("train")
    x_fit = x_all.loc[fit_mask]
    y_fit = y_struct[fit_mask.to_numpy()]
    if fit_max_rows is not None and len(x_fit) > int(fit_max_rows):
        selected_idx = _sample_training_indices(fold_df.loc[fit_mask].reset_index(drop=True), max_rows=int(fit_max_rows))
        x_fit = x_fit.reset_index(drop=True).iloc[selected_idx]
        y_fit = y_fit[selected_idx]

    scaler = StandardScaler()
    x_fit_scaled = scaler.fit_transform(x_fit)
    x_all_scaled = scaler.transform(x_all)
    cox = CoxPHSurvivalAnalysis(alpha=float(alpha), ties=str(ties))
    cox.fit(x_fit_scaled, y_fit)

    fold_df["risk_score"] = cox.predict(x_all_scaled)
    return _evaluate_single_score_fold(fold_df=fold_df, score_col="risk_score") | {"fold_id": fold["fold_id"]}


def _evaluate_single_score_fold(*, fold_df: pd.DataFrame, score_col: str) -> dict[str, object]:
    split_frames = {
        split_name: fold_df.loc[fold_df["split"].astype("string").eq(split_name)].copy()
        for split_name in ("train", "valid", "test")
    }
    split_survival = {split_name: _frame_to_survival(frame) for split_name, frame in split_frames.items()}
    reference_survival = split_survival["train"]
    estimates_by_split = {
        split_name: pd.to_numeric(split_frames[split_name][score_col], errors="coerce").fillna(0.0).to_numpy(dtype=float)
        for split_name in split_frames
    }
    uno_c_index = _compute_uno_c_index_by_split(
        reference_survival=reference_survival,
        split_survival=split_survival,
        estimates_by_split=estimates_by_split,
    )
    dynamic_auc = _compute_dynamic_auc_by_split(
        reference_survival=reference_survival,
        split_survival=split_survival,
        estimates_by_split=estimates_by_split,
        requested_times=DEFAULT_HORIZONS,
    )
    return {
        "split_event_counts": {split_name: int(split_frames[split_name]["event_observed"].sum()) for split_name in split_frames},
        "uno_c_index": uno_c_index,
        "dynamic_auc": dynamic_auc,
    }


def _aggregate_fold_metrics(fold_results: list[dict[str, object]]) -> dict[str, object]:
    metrics = {
        "valid_uno": [_coerce_float(fold.get("uno_c_index", {}).get("valid", {}).get("uno_c_index")) for fold in fold_results],
        "test_uno": [_coerce_float(fold.get("uno_c_index", {}).get("test", {}).get("uno_c_index")) for fold in fold_results],
        "valid_dynamic_auc_mean": [_coerce_float(fold.get("dynamic_auc", {}).get("valid", {}).get("mean_auc")) for fold in fold_results],
        "test_dynamic_auc_mean": [_coerce_float(fold.get("dynamic_auc", {}).get("test", {}).get("mean_auc")) for fold in fold_results],
    }
    return {name: _summarize_metric_series(values) for name, values in metrics.items()}


def _objective_from_aggregate(aggregate: dict[str, object]) -> float:
    test_uno_mean = _coerce_float(aggregate.get("test_uno", {}).get("mean")) or float("nan")
    valid_uno_mean = _coerce_float(aggregate.get("valid_uno", {}).get("mean")) or float("nan")
    test_auc_mean = _coerce_float(aggregate.get("test_dynamic_auc_mean", {}).get("mean")) or float("nan")
    valid_auc_mean = _coerce_float(aggregate.get("valid_dynamic_auc_mean", {}).get("mean")) or float("nan")
    test_uno_std = _coerce_float(aggregate.get("test_uno", {}).get("std")) or 0.0
    valid_uno_std = _coerce_float(aggregate.get("valid_uno", {}).get("std")) or 0.0

    score = (
        0.50 * test_uno_mean
        + 0.20 * valid_uno_mean
        + 0.20 * test_auc_mean
        + 0.10 * valid_auc_mean
        - 0.10 * test_uno_std
        - 0.05 * valid_uno_std
    )
    return float(score)


def _compute_deltas(
    baseline: dict[str, object],
    variant: dict[str, object],
    baseline_objective: float,
    variant_objective: float,
) -> dict[str, object]:
    return {
        "valid_uno_mean": _delta_metric(baseline, variant, "valid_uno"),
        "test_uno_mean": _delta_metric(baseline, variant, "test_uno"),
        "valid_dynamic_auc_mean": _delta_metric(baseline, variant, "valid_dynamic_auc_mean"),
        "test_dynamic_auc_mean": _delta_metric(baseline, variant, "test_dynamic_auc_mean"),
        "objective": float(variant_objective - baseline_objective),
    }


def _delta_metric(baseline: dict[str, object], variant: dict[str, object], metric_name: str) -> float | None:
    baseline_value = _coerce_float(baseline.get(metric_name, {}).get("mean"))
    variant_value = _coerce_float(variant.get(metric_name, {}).get("mean"))
    if baseline_value is None or variant_value is None:
        return None
    return float(variant_value - baseline_value)


def _summarize_ablation_row(item: dict[str, object]) -> dict[str, object]:
    block = item.get("block", {}) if isinstance(item.get("block"), dict) else {}
    delta = item.get("delta_vs_baseline", {}) if isinstance(item.get("delta_vs_baseline"), dict) else {}
    return {
        "name": block.get("name"),
        "label": block.get("label"),
        "n_cols": len(block.get("columns", [])) if isinstance(block.get("columns"), list) else 0,
        "delta_test_uno_mean": _coerce_float(delta.get("test_uno_mean")),
        "delta_valid_uno_mean": _coerce_float(delta.get("valid_uno_mean")),
        "delta_test_dynamic_auc_mean": _coerce_float(delta.get("test_dynamic_auc_mean")),
        "delta_objective": _coerce_float(delta.get("objective")),
    }


def _summarize_metric_series(values: list[float | None]) -> dict[str, object]:
    clean = np.asarray([value for value in values if value is not None and np.isfinite(value)], dtype=float)
    if clean.size == 0:
        return {"count": 0, "mean": float("nan"), "std": float("nan"), "min": float("nan"), "max": float("nan")}
    return {
        "count": int(clean.size),
        "mean": float(clean.mean()),
        "std": float(clean.std(ddof=0)),
        "min": float(clean.min()),
        "max": float(clean.max()),
    }


def _coerce_float(value: object) -> float | None:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return None
    return float(numeric)


def _fmt(value: object) -> str:
    numeric = _coerce_float(value)
    if numeric is None or not np.isfinite(numeric):
        return "nan"
    return f"{numeric:.4f}"


def _emit_progress(callback: ProgressCallback | None, *, stage: str, progress: float, message: str) -> None:
    if callback is None:
        return
    callback({"stage": stage, "progress": float(max(0.0, min(1.0, progress))), "message": message})


def _to_jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _to_jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_to_jsonable(item) for item in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value