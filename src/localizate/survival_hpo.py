from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import time
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
    _compute_uno_c_index_by_split,
    _fit_gbsa_with_progress,
    _fit_rsf_with_progress,
    _frame_to_survival,
    _sample_training_indices,
)
from .survival_rolling_backtest import build_walk_forward_folds, derive_event_quantile_cutoffs


ProgressCallback = Callable[[dict[str, object]], None]


@dataclass(frozen=True)
class SurvivalHpoResult:
    metrics_json: Path
    report_md: Path
    checkpoint_json: Path
    best_family: str
    best_objective: float


@dataclass(frozen=True)
class HpoContext:
    dataset: pd.DataFrame
    feature_frame: pd.DataFrame
    folds: list[dict[str, object]]


def run_activity_survival_hpo(
    *,
    abt_csv: Path | None = None,
    rolling_baseline_json: Path | None = None,
    metrics_json: Path | None = None,
    report_md: Path | None = None,
    checkpoint_json: Path | None = None,
    transition_policy_train: str = "exclude_transition",
    renta_max_year: int = 2023,
    quantiles: tuple[float, ...] = (0.55, 0.65, 0.75, 0.85, 0.95),
    min_valid_events: int = 20,
    min_test_events: int = 20,
    cox_screen_trials: int = 16,
    ensemble_screen_trials: int = 8,
    confirm_top_k: int = 3,
    final_top_k: int = 2,
    screen_fit_max_rows: int | None = 12_000,
    confirm_fit_max_rows: int | None = 25_000,
    final_fit_max_rows: int | None = None,
    screen_rsf_estimators: int = 80,
    screen_gbsa_estimators: int = 80,
    confirm_rsf_estimators: int = 160,
    confirm_gbsa_estimators: int = 160,
    final_rsf_estimators: int = 300,
    final_gbsa_estimators: int = 300,
    random_seed: int = 20260326,
    feature_profile: str = "activity_survival_pruned",
    progress_callback: ProgressCallback | None = None,
) -> SurvivalHpoResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "activity_survival_abt.csv")
    resolved_baseline = rolling_baseline_json or (PROJECT_ROOT / "models" / "activity_survival_rolling_backtest.json")
    resolved_metrics = metrics_json or (PROJECT_ROOT / "models" / "activity_survival_hpo.json")
    resolved_report = report_md or (DOCS_DIR / "activity_survival_hpo.md")
    resolved_checkpoint = checkpoint_json or (PROJECT_ROOT / "models" / "activity_survival_hpo_checkpoint.json")

    resolved_metrics.parent.mkdir(parents=True, exist_ok=True)
    resolved_report.parent.mkdir(parents=True, exist_ok=True)
    resolved_checkpoint.parent.mkdir(parents=True, exist_ok=True)

    _emit_progress(progress_callback, stage="start", progress=0.01, message="starting overnight HPO for activity survival")

    context = _build_context(
        abt_csv=resolved_abt,
        transition_policy_train=transition_policy_train,
        renta_max_year=renta_max_year,
        quantiles=quantiles,
        min_valid_events=min_valid_events,
        min_test_events=min_test_events,
        feature_profile=feature_profile,
    )
    baseline_payload = _load_json_if_exists(resolved_baseline)
    rng = np.random.default_rng(random_seed)

    trial_log: list[dict[str, object]] = []
    checkpoints: dict[str, object] = {
        "started_at_epoch": time.time(),
        "trial_log": trial_log,
        "best_by_stage": {},
    }

    def save_checkpoint() -> None:
        resolved_checkpoint.write_text(json.dumps(_to_jsonable(checkpoints), ensure_ascii=False, indent=2), encoding="utf-8")

    total_trials = max(1, cox_screen_trials + ensemble_screen_trials + (confirm_top_k * 2) + final_top_k)
    completed_trials = 0

    screening_candidates = []
    for _ in range(int(cox_screen_trials)):
        screening_candidates.append(("screen", "cox_only", sample_cox_candidate(rng)))
    for _ in range(int(ensemble_screen_trials)):
        screening_candidates.append(("screen", "ensemble_all_rank", sample_ensemble_candidate(rng)))

    screening_results: list[dict[str, object]] = []
    for stage_name, family, params in screening_candidates:
        completed_trials += 1
        result = evaluate_candidate(
            context=context,
            family=family,
            params=params,
            fit_max_rows=screen_fit_max_rows,
            rsf_n_estimators=screen_rsf_estimators,
            gbsa_n_estimators=screen_gbsa_estimators,
            progress_callback=progress_callback,
            progress=0.05 + 0.55 * (completed_trials / total_trials),
            progress_message=f"{stage_name}:{family} trial {completed_trials}/{total_trials}",
        )
        record = {
            "stage": stage_name,
            "family": family,
            "params": params,
            **result,
        }
        screening_results.append(record)
        trial_log.append(record)
        checkpoints["best_by_stage"][f"{stage_name}_{family}"] = _best_trial([r for r in screening_results if r["family"] == family])
        save_checkpoint()

    confirm_candidates: list[tuple[str, str, dict[str, object]]] = []
    for family in ("cox_only", "ensemble_all_rank"):
        family_trials = [trial for trial in screening_results if trial["family"] == family]
        top_trials = sorted(family_trials, key=lambda item: item["objective"], reverse=True)[: max(1, int(confirm_top_k))]
        for trial in top_trials:
            confirm_candidates.append(("confirm", family, dict(trial["params"])))

    confirm_results: list[dict[str, object]] = []
    for stage_name, family, params in confirm_candidates:
        completed_trials += 1
        result = evaluate_candidate(
            context=context,
            family=family,
            params=params,
            fit_max_rows=confirm_fit_max_rows,
            rsf_n_estimators=confirm_rsf_estimators,
            gbsa_n_estimators=confirm_gbsa_estimators,
            progress_callback=progress_callback,
            progress=0.60 + 0.25 * (completed_trials / total_trials),
            progress_message=f"{stage_name}:{family} trial {completed_trials}/{total_trials}",
        )
        record = {
            "stage": stage_name,
            "family": family,
            "params": params,
            **result,
        }
        confirm_results.append(record)
        trial_log.append(record)
        checkpoints["best_by_stage"][f"{stage_name}_{family}"] = _best_trial([r for r in confirm_results if r["family"] == family])
        save_checkpoint()

    finalist_pool = sorted(confirm_results or screening_results, key=lambda item: item["objective"], reverse=True)[: max(1, int(final_top_k))]
    final_results: list[dict[str, object]] = []
    for trial in finalist_pool:
        completed_trials += 1
        family = str(trial["family"])
        params = dict(trial["params"])
        result = evaluate_candidate(
            context=context,
            family=family,
            params=params,
            fit_max_rows=final_fit_max_rows,
            rsf_n_estimators=final_rsf_estimators,
            gbsa_n_estimators=final_gbsa_estimators,
            progress_callback=progress_callback,
            progress=0.86 + 0.13 * (completed_trials / total_trials),
            progress_message=f"final:{family} trial {completed_trials}/{total_trials}",
        )
        record = {
            "stage": "final",
            "family": family,
            "params": params,
            **result,
        }
        final_results.append(record)
        trial_log.append(record)
        checkpoints["best_by_stage"]["final"] = _best_trial(final_results)
        save_checkpoint()

    all_trials = screening_results + confirm_results + final_results
    best_trial = _best_trial(final_results or confirm_results or screening_results)
    payload = {
        "source_artifacts": {
            "abt_csv": str(resolved_abt),
            "rolling_baseline_json": str(resolved_baseline),
            "checkpoint_json": str(resolved_checkpoint),
        },
        "search_config": {
            "feature_profile": feature_profile,
            "transition_policy_train": transition_policy_train,
            "renta_max_year": int(renta_max_year),
            "quantiles": [float(value) for value in quantiles],
            "min_valid_events": int(min_valid_events),
            "min_test_events": int(min_test_events),
            "cox_screen_trials": int(cox_screen_trials),
            "ensemble_screen_trials": int(ensemble_screen_trials),
            "confirm_top_k": int(confirm_top_k),
            "final_top_k": int(final_top_k),
            "screen_fit_max_rows": _none_or_int(screen_fit_max_rows),
            "confirm_fit_max_rows": _none_or_int(confirm_fit_max_rows),
            "final_fit_max_rows": _none_or_int(final_fit_max_rows),
            "screen_rsf_estimators": int(screen_rsf_estimators),
            "screen_gbsa_estimators": int(screen_gbsa_estimators),
            "confirm_rsf_estimators": int(confirm_rsf_estimators),
            "confirm_gbsa_estimators": int(confirm_gbsa_estimators),
            "final_rsf_estimators": int(final_rsf_estimators),
            "final_gbsa_estimators": int(final_gbsa_estimators),
            "random_seed": int(random_seed),
        },
        "context": {
            "rows": int(len(context.dataset)),
            "fold_count": int(len(context.folds)),
            "folds": [
                {
                    key: value
                    for key, value in fold.items()
                    if key not in {"train_mask", "valid_mask", "test_mask"}
                }
                for fold in context.folds
            ],
        },
        "baseline_summary": _extract_baseline_summary(baseline_payload),
        "trial_count": int(len(all_trials)),
        "screening_results": screening_results,
        "confirmation_results": confirm_results,
        "final_results": final_results,
        "best_trial": best_trial,
    }

    resolved_metrics.write_text(json.dumps(_to_jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report.write_text(render_hpo_markdown(payload), encoding="utf-8")
    save_checkpoint()
    _emit_progress(progress_callback, stage="complete", progress=1.0, message="overnight HPO finished")

    return SurvivalHpoResult(
        metrics_json=resolved_metrics,
        report_md=resolved_report,
        checkpoint_json=resolved_checkpoint,
        best_family=str(best_trial.get("family", "unknown")),
        best_objective=float(best_trial.get("objective", float("nan"))),
    )


def _build_context(
    *,
    abt_csv: Path,
    transition_policy_train: str,
    renta_max_year: int,
    quantiles: tuple[float, ...],
    min_valid_events: int,
    min_test_events: int,
    feature_profile: str,
) -> HpoContext:
    abt = pd.read_csv(abt_csv, low_memory=False)
    payload = apply_training_policies(abt, transition_policy=transition_policy_train, renta_max_year=renta_max_year)
    dataset = payload["dataset"].copy()
    dataset["first_seen_period"] = dataset["first_seen_period"].astype("string")
    dataset["event_observed"] = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    dataset["duration_months"] = pd.to_numeric(dataset["duration_months"], errors="coerce").fillna(0).astype(float)
    feature_frame = build_feature_frame(dataset, feature_profile=feature_profile)
    cutoffs = derive_event_quantile_cutoffs(dataset, quantiles=quantiles)
    folds = build_walk_forward_folds(
        dataset,
        cutoff_periods=cutoffs,
        min_valid_events=min_valid_events,
        min_test_events=min_test_events,
    )
    if not folds:
        raise ValueError("No folds available for HPO")
    return HpoContext(dataset=dataset, feature_frame=feature_frame, folds=folds)


def sample_cox_candidate(rng: np.random.Generator) -> dict[str, object]:
    alpha = float(np.exp(rng.uniform(np.log(1e-4), np.log(2.0))))
    ties = str(rng.choice(np.asarray(["breslow", "efron"], dtype=object)))
    return {"alpha": alpha, "ties": ties}


def sample_ensemble_candidate(rng: np.random.Generator) -> dict[str, object]:
    return {
        "cox_alpha": float(np.exp(rng.uniform(np.log(1e-4), np.log(0.5)))),
        "cox_ties": str(rng.choice(np.asarray(["breslow", "efron"], dtype=object))),
        "rsf_min_samples_split": int(rng.choice(np.asarray([8, 12, 16, 24, 32]))),
        "rsf_min_samples_leaf": int(rng.choice(np.asarray([5, 10, 20, 30, 40]))),
        "rsf_max_features": _choice_object(rng, ["sqrt", 0.5, 0.75]),
        "rsf_max_depth": _choice_object(rng, [None, 8, 12, 16]),
        "gbsa_learning_rate": float(rng.choice(np.asarray([0.015, 0.02, 0.03, 0.05, 0.08]))),
        "gbsa_subsample": float(rng.choice(np.asarray([0.6, 0.8, 1.0]))),
        "gbsa_max_depth": int(rng.choice(np.asarray([1, 2, 3]))),
        "gbsa_min_samples_split": int(rng.choice(np.asarray([8, 12, 20, 30]))),
        "gbsa_min_samples_leaf": int(rng.choice(np.asarray([5, 10, 20, 30]))),
        "gbsa_dropout_rate": float(rng.choice(np.asarray([0.0, 0.05, 0.1]))),
    }


def evaluate_candidate(
    *,
    context: HpoContext,
    family: str,
    params: dict[str, object],
    fit_max_rows: int | None,
    rsf_n_estimators: int,
    gbsa_n_estimators: int,
    progress_callback: ProgressCallback | None,
    progress: float,
    progress_message: str,
) -> dict[str, object]:
    _emit_progress(progress_callback, stage="hpo_trial", progress=progress, message=f"{progress_message} start")
    fold_results: list[dict[str, object]] = []
    for fold in context.folds:
        if family == "cox_only":
            fold_result = _evaluate_cox_fold(context=context, fold=fold, params=params, fit_max_rows=fit_max_rows)
        elif family == "ensemble_all_rank":
            fold_result = _evaluate_ensemble_fold(
                context=context,
                fold=fold,
                params=params,
                fit_max_rows=fit_max_rows,
                rsf_n_estimators=rsf_n_estimators,
                gbsa_n_estimators=gbsa_n_estimators,
            )
        else:
            raise ValueError(f"Unsupported HPO family: {family}")
        fold_results.append(fold_result)

    aggregate = _aggregate_fold_metrics(fold_results)
    objective = _objective_from_aggregate(aggregate)
    _emit_progress(progress_callback, stage="hpo_trial", progress=progress, message=f"{progress_message} done objective={objective:.6f}")
    return {
        "objective": float(objective),
        "aggregate": aggregate,
        "fold_results": fold_results,
        "fit_max_rows": _none_or_int(fit_max_rows),
        "rsf_n_estimators": int(rsf_n_estimators),
        "gbsa_n_estimators": int(gbsa_n_estimators),
    }


def _evaluate_cox_fold(
    *,
    context: HpoContext,
    fold: dict[str, object],
    params: dict[str, object],
    fit_max_rows: int | None,
) -> dict[str, object]:
    train_mask = np.asarray(fold["train_mask"], dtype=bool)
    valid_mask = np.asarray(fold["valid_mask"], dtype=bool)
    test_mask = np.asarray(fold["test_mask"], dtype=bool)
    eval_mask = train_mask | valid_mask | test_mask

    fold_df = context.dataset.loc[eval_mask].copy()
    x_all = context.feature_frame.loc[eval_mask].copy()
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
    cox = CoxPHSurvivalAnalysis(alpha=float(params["alpha"]), ties=str(params["ties"]))
    cox.fit(x_fit_scaled, y_fit)

    fold_df["risk_score"] = cox.predict(x_all_scaled)
    return _evaluate_single_score_fold(fold_df=fold_df, score_col="risk_score") | {"fold_id": fold["fold_id"]}


def _evaluate_ensemble_fold(
    *,
    context: HpoContext,
    fold: dict[str, object],
    params: dict[str, object],
    fit_max_rows: int | None,
    rsf_n_estimators: int,
    gbsa_n_estimators: int,
) -> dict[str, object]:
    train_mask = np.asarray(fold["train_mask"], dtype=bool)
    valid_mask = np.asarray(fold["valid_mask"], dtype=bool)
    test_mask = np.asarray(fold["test_mask"], dtype=bool)
    eval_mask = train_mask | valid_mask | test_mask

    fold_df = context.dataset.loc[eval_mask].copy()
    x_all = context.feature_frame.loc[eval_mask].copy()
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

    cox = CoxPHSurvivalAnalysis(alpha=float(params["cox_alpha"]), ties=str(params["cox_ties"]))
    cox.fit(x_fit_scaled, y_fit)

    rsf = RandomSurvivalForest(
        n_estimators=max(10, int(rsf_n_estimators)),
        min_samples_split=int(params["rsf_min_samples_split"]),
        min_samples_leaf=int(params["rsf_min_samples_leaf"]),
        max_features=params["rsf_max_features"],
        max_depth=params["rsf_max_depth"],
        random_state=20260326,
        n_jobs=-1,
        warm_start=True,
    )
    rsf = _fit_rsf_with_progress(rsf, x_fit, y_fit, total_estimators=rsf_n_estimators, chunk_size=max(10, rsf_n_estimators // 4), progress_callback=None, progress_start=0.0, progress_end=1.0)

    gbsa = GradientBoostingSurvivalAnalysis(
        n_estimators=max(1, int(gbsa_n_estimators)),
        learning_rate=float(params["gbsa_learning_rate"]),
        subsample=float(params["gbsa_subsample"]),
        max_depth=int(params["gbsa_max_depth"]),
        min_samples_split=int(params["gbsa_min_samples_split"]),
        min_samples_leaf=int(params["gbsa_min_samples_leaf"]),
        dropout_rate=float(params["gbsa_dropout_rate"]),
        random_state=20260326,
        warm_start=True,
    )
    gbsa = _fit_gbsa_with_progress(gbsa, x_fit_scaled, y_fit, total_estimators=gbsa_n_estimators, chunk_size=max(5, gbsa_n_estimators // 4), progress_callback=None, progress_start=0.0, progress_end=1.0)

    fold_df["risk_cox"] = cox.predict(x_all_scaled)
    fold_df["risk_rsf"] = rsf.predict(x_all)
    fold_df["risk_gbsa"] = gbsa.predict(x_all_scaled)
    fold_df["risk_score"] = fold_df[["risk_cox", "risk_rsf", "risk_gbsa"]].rank(axis=0, method="average", pct=True).mean(axis=1)
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


def render_hpo_markdown(payload: dict[str, object]) -> str:
    best_trial = payload.get("best_trial", {})
    baseline = payload.get("baseline_summary", {})
    lines: list[str] = []
    lines.append("# Activity Survival HPO")
    lines.append("")
    lines.append("Busqueda competitiva de hiperparametros sobre rolling backtest walk-forward para comparar `cox_only` y `ensemble_all_rank`.")
    lines.append("")
    lines.append("## Configuracion")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(payload.get("search_config", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Lectura ejecutiva")
    lines.append("")
    for bullet in _build_hpo_summary(best_trial, baseline, payload):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## Baseline rolling")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(baseline), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Best trial")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(best_trial), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Final results")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(payload.get("final_results", [])), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Confirmation results")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(payload.get("confirmation_results", [])), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Screening results")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(payload.get("screening_results", [])), ensure_ascii=False, indent=2))
    lines.append("")
    return "\n".join(lines) + "\n"


def _build_hpo_summary(best_trial: dict[str, object], baseline: dict[str, object], payload: dict[str, object]) -> list[str]:
    bullets: list[str] = []
    best_family = best_trial.get("family")
    best_obj = _coerce_float(best_trial.get("objective"))
    best_test_uno = _coerce_float(best_trial.get("aggregate", {}).get("test_uno", {}).get("mean"))
    best_valid_uno = _coerce_float(best_trial.get("aggregate", {}).get("valid_uno", {}).get("mean"))
    base_test_uno = _coerce_float(baseline.get("best_known_test_uno"))
    base_valid_uno = _coerce_float(baseline.get("best_known_valid_uno"))
    bullets.append(
        f"La mejor configuracion encontrada pertenece a `{best_family}` con objective={_fmt(best_obj)}, test Uno mean={_fmt(best_test_uno)} y valid Uno mean={_fmt(best_valid_uno)}."
    )
    if base_test_uno is not None:
        bullets.append(
            f"Frente al mejor benchmark rolling previo, test Uno pasa de {_fmt(base_test_uno)} a {_fmt(best_test_uno)} y valid Uno de {_fmt(base_valid_uno)} a {_fmt(best_valid_uno)}."
        )
    bullets.append(
        f"Se evaluaron {payload.get('trial_count')} trials en tres fases: cribado, confirmacion y finalistas full-fidelity."
    )
    return bullets


def _extract_baseline_summary(payload: dict[str, object] | None) -> dict[str, object]:
    if not payload:
        return {}
    variant_ranking = payload.get("variant_ranking", []) if isinstance(payload, dict) else []
    best = variant_ranking[0] if isinstance(variant_ranking, list) and variant_ranking else {}
    return {
        "best_known_variant": best.get("variant"),
        "best_known_label": best.get("label"),
        "best_known_test_uno": best.get("test_uno_mean"),
        "best_known_valid_uno": best.get("valid_uno_mean"),
        "best_known_test_dynamic_auc_mean": best.get("test_dynamic_auc_mean"),
        "best_known_valid_dynamic_auc_mean": best.get("valid_dynamic_auc_mean"),
    }


def _best_trial(trials: list[dict[str, object]]) -> dict[str, object]:
    if not trials:
        return {}
    return max(trials, key=lambda item: float(item.get("objective", float("-inf"))))


def _load_json_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _emit_progress(callback: ProgressCallback | None, *, stage: str, progress: float, message: str) -> None:
    if callback is None:
        return
    callback({"stage": stage, "progress": float(max(0.0, min(1.0, progress))), "message": message})


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


def _fmt(value: float | None) -> str:
    if value is None or not np.isfinite(value):
        return "nan"
    return f"{value:.4f}"


def _none_or_int(value: int | None) -> int | None:
    if value is None:
        return None
    return int(value)


def _choice_object(rng: np.random.Generator, options: list[object]) -> object:
    values = np.asarray(options, dtype=object)
    return values[int(rng.integers(0, len(values)))]


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