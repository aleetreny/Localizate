from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sksurv.ensemble import GradientBoostingSurvivalAnalysis, RandomSurvivalForest
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.util import Surv

from .paths import DATA_DIR, DOCS_DIR, PROJECT_ROOT
from .survival_baseline import apply_training_policies, build_feature_frame
from .survival_canonical import (
    DEFAULT_HORIZONS,
    _compute_dynamic_auc_by_split,
    _compute_integrated_brier_by_split,
    _compute_uno_c_index_by_split,
    _ensemble_rank_score,
    _fit_gbsa_with_progress,
    _fit_rsf_with_progress,
    _frame_to_survival,
    _sample_training_indices,
    evaluate_canonical_quality_gate,
)


ProgressCallback = Callable[[dict[str, object]], None]

VARIANT_DEFINITIONS: dict[str, dict[str, object]] = {
    "cox_only": {"label": "Cox solo", "kind": "raw", "columns": ["risk_cox"]},
    "gbsa_only": {"label": "GBSA solo", "kind": "raw", "columns": ["risk_gbsa"]},
    "rsf_only": {"label": "RSF solo", "kind": "raw", "columns": ["risk_rsf"]},
    "cox_gbsa_rank": {"label": "Cox + GBSA", "kind": "rank", "columns": ["risk_cox", "risk_gbsa"]},
    "ensemble_all_rank": {
        "label": "Ensemble actual (rank equal)",
        "kind": "rank",
        "columns": ["risk_cox", "risk_rsf", "risk_gbsa"],
    },
    "ensemble_weighted_rank": {
        "label": "Ensemble ponderado (GBSA dominante)",
        "kind": "weighted_rank",
        "weights": {"risk_cox": 0.30, "risk_rsf": 0.10, "risk_gbsa": 0.60},
    },
}


@dataclass(frozen=True)
class RollingBacktestResult:
    metrics_json: Path
    report_md: Path
    folds_run: int


def run_activity_survival_rolling_backtest(
    *,
    abt_csv: Path | None = None,
    comparison_metrics_json: Path | None = None,
    metrics_json: Path | None = None,
    report_md: Path | None = None,
    transition_policy_train: str = "exclude_transition",
    renta_max_year: int = 2023,
    quantiles: tuple[float, ...] = (0.55, 0.65, 0.75, 0.85, 0.95),
    min_valid_events: int = 20,
    min_test_events: int = 20,
    rsf_n_estimators: int = 120,
    rsf_chunk_size: int = 20,
    gbsa_n_estimators: int = 120,
    gbsa_chunk_size: int = 20,
    fit_max_rows: int | None = 25_000,
    progress_callback: ProgressCallback | None = None,
) -> RollingBacktestResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "activity_survival_abt.csv")
    resolved_comparison = comparison_metrics_json or (PROJECT_ROOT / "models" / "survival_activity_canonical_metrics.json")
    resolved_metrics = metrics_json or (PROJECT_ROOT / "models" / "activity_survival_rolling_backtest.json")
    resolved_report = report_md or (DOCS_DIR / "activity_survival_rolling_backtest.md")

    resolved_metrics.parent.mkdir(parents=True, exist_ok=True)
    resolved_report.parent.mkdir(parents=True, exist_ok=True)

    _emit_progress(progress_callback, stage="start", progress=0.01, message="starting activity survival rolling backtest")

    abt = pd.read_csv(resolved_abt, low_memory=False)
    training_payload = apply_training_policies(
        abt,
        transition_policy=transition_policy_train,
        renta_max_year=renta_max_year,
    )
    dataset = training_payload["dataset"].copy()
    dataset["first_seen_period"] = dataset["first_seen_period"].astype("string")
    dataset["event_observed"] = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    dataset["duration_months"] = pd.to_numeric(dataset["duration_months"], errors="coerce").fillna(0).astype(float)
    feature_frame = build_feature_frame(dataset, feature_profile="activity_survival_pruned")
    comparison_metrics = _load_json_if_exists(resolved_comparison)

    cutoffs = derive_event_quantile_cutoffs(dataset, quantiles=quantiles)
    folds = build_walk_forward_folds(
        dataset,
        cutoff_periods=cutoffs,
        min_valid_events=min_valid_events,
        min_test_events=min_test_events,
    )
    if not folds:
        raise ValueError("No viable walk-forward folds found for the configured quantiles and event thresholds")

    _emit_progress(progress_callback, stage="folds", progress=0.06, message=f"prepared {len(folds)} folds")

    fold_payloads: list[dict[str, object]] = []
    for index, fold in enumerate(folds, start=1):
        fold_progress_start = 0.08 + (index - 1) * (0.84 / len(folds))
        fold_progress_end = 0.08 + index * (0.84 / len(folds))
        payload = _run_single_fold(
            dataset=dataset,
            feature_frame=feature_frame,
            fold=fold,
            rsf_n_estimators=rsf_n_estimators,
            rsf_chunk_size=rsf_chunk_size,
            gbsa_n_estimators=gbsa_n_estimators,
            gbsa_chunk_size=gbsa_chunk_size,
            fit_max_rows=fit_max_rows,
            progress_callback=progress_callback,
            progress_start=fold_progress_start,
            progress_end=fold_progress_end,
            fold_index=index,
            total_folds=len(folds),
        )
        fold_payloads.append(payload)

    aggregate = aggregate_backtest_metrics(fold_payloads)
    variant_aggregate = aggregate_variant_backtest_metrics(fold_payloads)
    variant_ranking = rank_variants(variant_aggregate)
    payload = {
        "source_artifacts": {
            "abt_csv": str(resolved_abt),
            "comparison_metrics_json": str(resolved_comparison),
        },
        "training_run": {
            "rsf_n_estimators": int(rsf_n_estimators),
            "rsf_chunk_size": int(rsf_chunk_size),
            "gbsa_n_estimators": int(gbsa_n_estimators),
            "gbsa_chunk_size": int(gbsa_chunk_size),
            "fit_max_rows": int(fit_max_rows) if fit_max_rows is not None else None,
            "cut_quantiles": [float(value) for value in quantiles],
            "min_valid_events": int(min_valid_events),
            "min_test_events": int(min_test_events),
        },
        "policy_train": training_payload["policy"],
        "rows": int(len(dataset)),
        "fold_count": int(len(fold_payloads)),
        "cutoffs": list(cutoffs),
        "folds": fold_payloads,
        "aggregate": aggregate,
        "variant_aggregate": variant_aggregate,
        "variant_ranking": variant_ranking,
        "single_split_comparison": _summarize_single_split_metrics(comparison_metrics),
    }

    resolved_metrics.write_text(json.dumps(_to_jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report.write_text(render_rolling_backtest_markdown(payload), encoding="utf-8")
    _emit_progress(progress_callback, stage="write_outputs", progress=1.0, message="rolling backtest artifacts written")

    return RollingBacktestResult(
        metrics_json=resolved_metrics,
        report_md=resolved_report,
        folds_run=len(fold_payloads),
    )


def derive_event_quantile_cutoffs(dataset: pd.DataFrame, *, quantiles: tuple[float, ...]) -> tuple[str, ...]:
    periods = dataset["first_seen_period"].astype("string")
    events = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    event_periods = pd.Series(sorted(periods[events > 0].dropna().unique()), dtype="string")
    if event_periods.empty:
        raise ValueError("Cannot derive temporal cutoffs without event periods")

    cutoffs: list[str] = []
    for quantile in quantiles:
        idx = min(max(int(np.floor((len(event_periods) - 1) * float(quantile))), 0), len(event_periods) - 1)
        period = str(event_periods.iloc[idx])
        if not cutoffs or cutoffs[-1] != period:
            cutoffs.append(period)

    last_period = str(periods.dropna().max())
    end_period = _next_period(last_period)
    if not cutoffs or cutoffs[-1] != end_period:
        cutoffs.append(end_period)
    if len(cutoffs) < 3:
        raise ValueError("Insufficient distinct cutoffs to build walk-forward folds")
    return tuple(cutoffs)


def build_walk_forward_folds(
    dataset: pd.DataFrame,
    *,
    cutoff_periods: tuple[str, ...],
    min_valid_events: int,
    min_test_events: int,
) -> list[dict[str, object]]:
    periods = dataset["first_seen_period"].astype("string")
    events = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    folds: list[dict[str, object]] = []

    for index in range(len(cutoff_periods) - 2):
        valid_start, test_start, test_end = cutoff_periods[index : index + 3]
        train_mask = periods < valid_start
        valid_mask = (periods >= valid_start) & (periods < test_start)
        test_mask = (periods >= test_start) & (periods < test_end)
        valid_events = int(events[valid_mask].sum())
        test_events = int(events[test_mask].sum())
        if int(train_mask.sum()) == 0 or int(valid_mask.sum()) == 0 or int(test_mask.sum()) == 0:
            continue
        if valid_events < int(min_valid_events) or test_events < int(min_test_events):
            continue
        folds.append(
            {
                "fold_id": f"fold_{len(folds) + 1}",
                "valid_start": str(valid_start),
                "test_start": str(test_start),
                "test_end": str(test_end),
                "train_rows": int(train_mask.sum()),
                "train_events": int(events[train_mask].sum()),
                "valid_rows": int(valid_mask.sum()),
                "valid_events": valid_events,
                "test_rows": int(test_mask.sum()),
                "test_events": test_events,
                "train_mask": train_mask.to_numpy(dtype=bool),
                "valid_mask": valid_mask.to_numpy(dtype=bool),
                "test_mask": test_mask.to_numpy(dtype=bool),
            }
        )
    return folds


def aggregate_backtest_metrics(folds: list[dict[str, object]]) -> dict[str, object]:
    metrics = {
        "valid_uno": [
            _coerce_float(fold.get("metrics", {}).get("uno_c_index", {}).get("valid", {}).get("uno_c_index"))
            for fold in folds
        ],
        "test_uno": [
            _coerce_float(fold.get("metrics", {}).get("uno_c_index", {}).get("test", {}).get("uno_c_index"))
            for fold in folds
        ],
        "valid_dynamic_auc_mean": [
            _coerce_float(fold.get("metrics", {}).get("dynamic_auc", {}).get("valid", {}).get("mean_auc"))
            for fold in folds
        ],
        "test_dynamic_auc_mean": [
            _coerce_float(fold.get("metrics", {}).get("dynamic_auc", {}).get("test", {}).get("mean_auc"))
            for fold in folds
        ],
    }
    return {name: _summarize_metric_series(values) for name, values in metrics.items()}


def aggregate_variant_backtest_metrics(folds: list[dict[str, object]]) -> dict[str, object]:
    aggregate: dict[str, object] = {}
    for variant_name in VARIANT_DEFINITIONS:
        metrics = {
            "valid_uno": [
                _coerce_float(
                    fold.get("variant_metrics", {}).get(variant_name, {}).get("uno_c_index", {}).get("valid", {}).get("uno_c_index")
                )
                for fold in folds
            ],
            "test_uno": [
                _coerce_float(
                    fold.get("variant_metrics", {}).get(variant_name, {}).get("uno_c_index", {}).get("test", {}).get("uno_c_index")
                )
                for fold in folds
            ],
            "valid_dynamic_auc_mean": [
                _coerce_float(
                    fold.get("variant_metrics", {}).get(variant_name, {}).get("dynamic_auc", {}).get("valid", {}).get("mean_auc")
                )
                for fold in folds
            ],
            "test_dynamic_auc_mean": [
                _coerce_float(
                    fold.get("variant_metrics", {}).get(variant_name, {}).get("dynamic_auc", {}).get("test", {}).get("mean_auc")
                )
                for fold in folds
            ],
        }
        aggregate[variant_name] = {
            "label": VARIANT_DEFINITIONS[variant_name]["label"],
            **{metric_name: _summarize_metric_series(values) for metric_name, values in metrics.items()},
        }
    return aggregate


def rank_variants(variant_aggregate: dict[str, object]) -> list[dict[str, object]]:
    ranking: list[dict[str, object]] = []
    for variant_name, payload in variant_aggregate.items():
        if not isinstance(payload, dict):
            continue
        ranking.append(
            {
                "variant": variant_name,
                "label": payload.get("label"),
                "test_uno_mean": _coerce_float(payload.get("test_uno", {}).get("mean")),
                "valid_uno_mean": _coerce_float(payload.get("valid_uno", {}).get("mean")),
                "test_dynamic_auc_mean": _coerce_float(payload.get("test_dynamic_auc_mean", {}).get("mean")),
                "valid_dynamic_auc_mean": _coerce_float(payload.get("valid_dynamic_auc_mean", {}).get("mean")),
            }
        )
    ranking.sort(
        key=lambda item: (
            -999.0 if item["test_uno_mean"] is None or not np.isfinite(item["test_uno_mean"]) else -item["test_uno_mean"],
            -999.0 if item["valid_uno_mean"] is None or not np.isfinite(item["valid_uno_mean"]) else -item["valid_uno_mean"],
        )
    )
    return ranking


def render_rolling_backtest_markdown(payload: dict[str, object]) -> str:
    aggregate = payload.get("aggregate", {})
    variant_aggregate = payload.get("variant_aggregate", {})
    variant_ranking = payload.get("variant_ranking", [])
    folds = payload.get("folds", [])
    comparison = payload.get("single_split_comparison", {})
    training_run = payload.get("training_run", {})

    lines: list[str] = []
    lines.append("# Activity Survival Rolling Backtest")
    lines.append("")
    lines.append("Walk-forward backtest temporal para medir estabilidad del ensemble survival sobre `activity_survival` usando multiples cortes contiguos en el tiempo.")
    lines.append("")
    lines.append("## Configuracion")
    lines.append("")
    lines.append(f"- Filas evaluables: {payload.get('rows')}")
    lines.append(f"- Folds ejecutados: {payload.get('fold_count')}")
    lines.append(f"- Cutoffs: {json.dumps(_to_jsonable(payload.get('cutoffs', [])), ensure_ascii=False)}")
    lines.append(f"- Training run: {json.dumps(_to_jsonable(training_run), ensure_ascii=False)}")
    lines.append("")
    lines.append("## Lectura ejecutiva")
    lines.append("")
    for bullet in _build_rolling_summary(aggregate, variant_aggregate, variant_ranking, comparison, folds):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## Resumen agregado")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(aggregate), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Benchmark de variantes")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(variant_aggregate), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Ranking de variantes")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(variant_ranking), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Comparacion con split unico")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(comparison), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Folds")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(folds), ensure_ascii=False, indent=2))
    lines.append("")
    return "\n".join(lines) + "\n"


def _run_single_fold(
    *,
    dataset: pd.DataFrame,
    feature_frame: pd.DataFrame,
    fold: dict[str, object],
    rsf_n_estimators: int,
    rsf_chunk_size: int,
    gbsa_n_estimators: int,
    gbsa_chunk_size: int,
    fit_max_rows: int | None,
    progress_callback: ProgressCallback | None,
    progress_start: float,
    progress_end: float,
    fold_index: int,
    total_folds: int,
) -> dict[str, object]:
    train_mask = np.asarray(fold["train_mask"], dtype=bool)
    valid_mask = np.asarray(fold["valid_mask"], dtype=bool)
    test_mask = np.asarray(fold["test_mask"], dtype=bool)
    eval_mask = train_mask | valid_mask | test_mask

    x_train_all = feature_frame.loc[eval_mask].copy()
    fold_df = dataset.loc[eval_mask].copy()
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

    x_fit = x_train_all.loc[fit_mask]
    y_fit = y_struct[fit_mask.to_numpy()]
    if fit_max_rows is not None and len(x_fit) > int(fit_max_rows):
        selected_idx = _sample_training_indices(fold_df.loc[fit_mask].reset_index(drop=True), max_rows=int(fit_max_rows))
        x_fit = x_fit.reset_index(drop=True).iloc[selected_idx]
        y_fit = y_fit[selected_idx]

    scaler = StandardScaler()
    x_fit_scaled = scaler.fit_transform(x_fit)
    x_all_scaled = scaler.transform(x_train_all)

    cox = CoxPHSurvivalAnalysis(alpha=0.01)
    rsf = RandomSurvivalForest(
        n_estimators=max(10, int(rsf_n_estimators)),
        min_samples_split=20,
        min_samples_leaf=30,
        random_state=20260326 + fold_index,
        n_jobs=-1,
    )
    gbsa = GradientBoostingSurvivalAnalysis(
        n_estimators=max(1, int(gbsa_n_estimators)),
        learning_rate=0.03,
        random_state=20260326 + fold_index,
        warm_start=True,
    )

    progress_span = progress_end - progress_start
    cox.fit(x_fit_scaled, y_fit)
    _emit_progress(
        progress_callback,
        stage="rolling_fold",
        progress=progress_start + progress_span * 0.15,
        message=f"fold {fold_index}/{total_folds} cox trained ({fold['fold_id']})",
    )

    rsf = _fit_rsf_with_progress(
        rsf,
        x_fit,
        y_fit,
        total_estimators=rsf_n_estimators,
        chunk_size=rsf_chunk_size,
        progress_callback=lambda payload: _emit_progress(
            progress_callback,
            stage="rolling_fold",
            progress=progress_start + progress_span * (0.15 + 0.45 * float(payload.get("progress", 0.0))),
            message=f"fold {fold_index}/{total_folds} {payload.get('message')}",
        ) if progress_callback is not None else None,
        progress_start=0.0,
        progress_end=1.0,
    )

    gbsa = _fit_gbsa_with_progress(
        gbsa,
        x_fit_scaled,
        y_fit,
        total_estimators=gbsa_n_estimators,
        chunk_size=gbsa_chunk_size,
        progress_callback=lambda payload: _emit_progress(
            progress_callback,
            stage="rolling_fold",
            progress=progress_start + progress_span * (0.60 + 0.20 * float(payload.get("progress", 0.0))),
            message=f"fold {fold_index}/{total_folds} {payload.get('message')}",
        ) if progress_callback is not None else None,
        progress_start=0.0,
        progress_end=1.0,
    )

    fold_df["risk_cox"] = cox.predict(x_all_scaled)
    fold_df["risk_rsf"] = rsf.predict(x_train_all)
    fold_df["risk_gbsa"] = gbsa.predict(x_all_scaled)
    fold_df["risk_ensemble"] = _ensemble_rank_score(fold_df[["risk_cox", "risk_rsf", "risk_gbsa"]])

    variant_scores = build_variant_scores(fold_df)

    split_frames = {
        split_name: fold_df.loc[fold_df["split"].astype("string").eq(split_name)].copy()
        for split_name in ("train", "valid", "test")
    }
    split_survival = {split_name: _frame_to_survival(frame) for split_name, frame in split_frames.items()}
    reference_survival = split_survival["train"]
    uno_c_index = _compute_uno_c_index_by_split(
        reference_survival=reference_survival,
        split_survival=split_survival,
        estimates_by_split={
            split_name: split_frames[split_name]["risk_ensemble"].to_numpy(dtype=float)
            for split_name in split_frames
        },
    )
    dynamic_auc = _compute_dynamic_auc_by_split(
        reference_survival=reference_survival,
        split_survival=split_survival,
        estimates_by_split={
            split_name: split_frames[split_name]["risk_ensemble"].to_numpy(dtype=float)
            for split_name in split_frames
        },
        requested_times=DEFAULT_HORIZONS,
    )
    variant_metrics = evaluate_variant_scores(
        split_frames=split_frames,
        split_survival=split_survival,
        reference_survival=reference_survival,
        variant_scores=variant_scores,
    )

    split_masks = {
        split_name: fold_df["split"].astype("string").eq(split_name).to_numpy()
        for split_name in ("train", "valid", "test")
    }
    integrated_brier = {
        "cox": _compute_integrated_brier_by_split(
            reference_survival=reference_survival,
            split_survival=split_survival,
            requested_times=DEFAULT_HORIZONS,
            predictor=lambda split_name, times: _predict_survival_probabilities_for_fold(
                cox,
                x_all_scaled[split_masks[split_name]],
                times,
            ),
        ),
        "rsf": _compute_integrated_brier_by_split(
            reference_survival=reference_survival,
            split_survival=split_survival,
            requested_times=DEFAULT_HORIZONS,
            predictor=lambda split_name, times: _predict_survival_probabilities_for_fold(
                rsf,
                x_train_all.loc[split_masks[split_name]],
                times,
            ),
        ),
        "gbsa": _compute_integrated_brier_by_split(
            reference_survival=reference_survival,
            split_survival=split_survival,
            requested_times=DEFAULT_HORIZONS,
            predictor=lambda split_name, times: _predict_survival_probabilities_for_fold(
                gbsa,
                x_all_scaled[split_masks[split_name]],
                times,
            ),
        ),
    }

    split_event_counts = {split_name: int(split_frames[split_name]["event_observed"].sum()) for split_name in split_frames}
    quality_gate = evaluate_canonical_quality_gate(
        split_event_counts=split_event_counts,
        uno_c_index=uno_c_index,
        dynamic_auc=dynamic_auc,
        integrated_brier=integrated_brier,
    )
    _emit_progress(
        progress_callback,
        stage="rolling_fold",
        progress=progress_end,
        message=f"fold {fold_index}/{total_folds} done ({fold['fold_id']}, status={quality_gate.get('status')})",
    )

    return {
        key: value
        for key, value in fold.items()
        if key not in {"train_mask", "valid_mask", "test_mask"}
    } | {
        "training_rows_used": int(len(x_fit)),
        "metrics": {
            "split_event_counts": split_event_counts,
            "uno_c_index": uno_c_index,
            "dynamic_auc": dynamic_auc,
            "integrated_brier_score": integrated_brier,
            "quality_gate": quality_gate,
        },
        "variant_metrics": variant_metrics,
    }


def build_variant_scores(fold_df: pd.DataFrame) -> dict[str, pd.Series]:
    scores: dict[str, pd.Series] = {}
    for variant_name, config in VARIANT_DEFINITIONS.items():
        kind = str(config.get("kind"))
        if kind == "raw":
            column = str(config.get("columns", [""])[0])
            scores[variant_name] = pd.to_numeric(fold_df[column], errors="coerce").fillna(0.0).astype(float)
        elif kind == "rank":
            columns = [str(column) for column in config.get("columns", [])]
            scores[variant_name] = _ensemble_rank_score(fold_df[columns])
        elif kind == "weighted_rank":
            weights = {str(key): float(value) for key, value in dict(config.get("weights", {})).items()}
            scores[variant_name] = _weighted_rank_score(fold_df, weights=weights)
        else:
            raise ValueError(f"Unsupported variant kind: {kind}")
    return scores


def evaluate_variant_scores(
    *,
    split_frames: dict[str, pd.DataFrame],
    split_survival: dict[str, np.ndarray],
    reference_survival: np.ndarray,
    variant_scores: dict[str, pd.Series],
) -> dict[str, object]:
    payload: dict[str, object] = {}
    for variant_name in VARIANT_DEFINITIONS:
        estimates_by_split = {
            split_name: variant_scores[variant_name].loc[split_frames[split_name].index].to_numpy(dtype=float)
            for split_name in split_frames
        }
        payload[variant_name] = {
            "label": VARIANT_DEFINITIONS[variant_name]["label"],
            "uno_c_index": _compute_uno_c_index_by_split(
                reference_survival=reference_survival,
                split_survival=split_survival,
                estimates_by_split=estimates_by_split,
            ),
            "dynamic_auc": _compute_dynamic_auc_by_split(
                reference_survival=reference_survival,
                split_survival=split_survival,
                estimates_by_split=estimates_by_split,
                requested_times=DEFAULT_HORIZONS,
            ),
        }
    return payload


def _predict_survival_probabilities_for_fold(estimator, features, times: np.ndarray) -> np.ndarray:
    survival_functions = estimator.predict_survival_function(features, return_array=False)
    eval_times = np.asarray(times, dtype=float)
    probabilities = np.vstack([np.clip(step_function(eval_times), 0.0, 1.0) for step_function in survival_functions])
    return probabilities.astype(float)


def _summarize_single_split_metrics(metrics: dict[str, object] | None) -> dict[str, object]:
    if not metrics:
        return {}
    return {
        "valid_uno": _coerce_float(metrics.get("uno_c_index", {}).get("valid", {}).get("uno_c_index")),
        "test_uno": _coerce_float(metrics.get("uno_c_index", {}).get("test", {}).get("uno_c_index")),
        "valid_dynamic_auc_mean": _coerce_float(metrics.get("dynamic_auc", {}).get("valid", {}).get("mean_auc")),
        "test_dynamic_auc_mean": _coerce_float(metrics.get("dynamic_auc", {}).get("test", {}).get("mean_auc")),
        "quality_gate": metrics.get("quality_gate", {}).get("status"),
    }


def _build_rolling_summary(
    aggregate: dict[str, object],
    variant_aggregate: dict[str, object],
    variant_ranking: list[dict[str, object]],
    comparison: dict[str, object],
    folds: object,
) -> list[str]:
    bullets: list[str] = []
    fold_count = len(folds) if isinstance(folds, list) else 0
    valid_uno_mean = _coerce_float(aggregate.get("valid_uno", {}).get("mean"))
    test_uno_mean = _coerce_float(aggregate.get("test_uno", {}).get("mean"))
    valid_auc_mean = _coerce_float(aggregate.get("valid_dynamic_auc_mean", {}).get("mean"))
    test_auc_mean = _coerce_float(aggregate.get("test_dynamic_auc_mean", {}).get("mean"))
    bullets.append(
        f"El rolling backtest ejecuta {fold_count} folds walk-forward; media valid Uno={_fmt(valid_uno_mean)}, test Uno={_fmt(test_uno_mean)}, valid mean AUC={_fmt(valid_auc_mean)}, test mean AUC={_fmt(test_auc_mean)}."
    )
    if comparison:
        bullets.append(
            f"Frente al split unico actual, valid Uno pasa de {_fmt(_coerce_float(comparison.get('valid_uno')))} a media rolling {_fmt(valid_uno_mean)}; test Uno pasa de {_fmt(_coerce_float(comparison.get('test_uno')))} a media rolling {_fmt(test_uno_mean)}."
        )
        bullets.append(
            f"Frente al split unico, valid mean AUC pasa de {_fmt(_coerce_float(comparison.get('valid_dynamic_auc_mean')))} a {_fmt(valid_auc_mean)}; test mean AUC pasa de {_fmt(_coerce_float(comparison.get('test_dynamic_auc_mean')))} a {_fmt(test_auc_mean)}."
        )
    quality_statuses = []
    if isinstance(folds, list):
        for fold in folds:
            status = fold.get("metrics", {}).get("quality_gate", {}).get("status")
            if status is not None:
                quality_statuses.append(str(status))
    if quality_statuses:
        bullets.append(f"Quality gates por fold: {', '.join(quality_statuses)}.")
    if variant_ranking:
        winner = variant_ranking[0]
        bullets.append(
            f"La mejor variante por media de Uno test es {winner.get('label')} con test Uno={_fmt(_coerce_float(winner.get('test_uno_mean')))} y valid Uno={_fmt(_coerce_float(winner.get('valid_uno_mean')))}."
        )
        current = variant_aggregate.get("ensemble_all_rank", {}) if isinstance(variant_aggregate, dict) else {}
        weighted = variant_aggregate.get("ensemble_weighted_rank", {}) if isinstance(variant_aggregate, dict) else {}
        gbsa = variant_aggregate.get("gbsa_only", {}) if isinstance(variant_aggregate, dict) else {}
        bullets.append(
            f"Comparativa clave: ensemble actual test Uno={_fmt(_coerce_float(current.get('test_uno', {}).get('mean')))}, ensemble ponderado={_fmt(_coerce_float(weighted.get('test_uno', {}).get('mean')))}, GBSA solo={_fmt(_coerce_float(gbsa.get('test_uno', {}).get('mean')))}."
        )
    return bullets


def _weighted_rank_score(frame: pd.DataFrame, *, weights: dict[str, float]) -> pd.Series:
    normalized_weights = pd.Series(weights, dtype=float)
    normalized_weights = normalized_weights / normalized_weights.sum()
    ranked = frame[list(normalized_weights.index)].rank(axis=0, method="average", pct=True)
    weighted = ranked.mul(normalized_weights, axis=1).sum(axis=1)
    return weighted.astype(float)


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


def _next_period(period: str) -> str:
    year_str, month_str = str(period).split("-", 1)
    year = int(year_str)
    month = int(month_str)
    month += 1
    if month > 12:
        year += 1
        month = 1
    return f"{year:04d}-{month:02d}"


def _load_json_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _emit_progress(callback: ProgressCallback | None, *, stage: str, progress: float, message: str) -> None:
    if callback is None:
        return
    callback(
        {
            "stage": stage,
            "progress": float(max(0.0, min(1.0, progress))),
            "message": message,
        }
    )


def _coerce_float(value: object) -> float | None:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return None
    return float(numeric)


def _fmt(value: float | None) -> str:
    if value is None or not np.isfinite(value):
        return "nan"
    return f"{value:.4f}"


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