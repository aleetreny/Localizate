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
from sksurv.metrics import (
    concordance_index_censored,
    concordance_index_ipcw,
    cumulative_dynamic_auc,
    integrated_brier_score,
)
from sksurv.util import Surv

from .paths import DATA_DIR, DOCS_DIR, PROJECT_ROOT
from .survival_baseline import (
    apply_training_policies,
    assign_temporal_split_adaptive,
    build_feature_frame,
    compute_calibration_summary,
)


@dataclass(frozen=True)
class CanonicalSurvivalResult:
    metrics_json: Path
    report_md: Path
    map_export_csv: Path


ProgressCallback = Callable[[dict[str, object]], None]
DEFAULT_HORIZONS = (6.0, 12.0, 24.0)


def train_canonical_survival_models(
    *,
    abt_csv: Path | None = None,
    metrics_json: Path | None = None,
    report_md: Path | None = None,
    map_export_csv: Path | None = None,
    feature_profile: str = "full",
    transition_policy_train: str = "exclude_transition",
    renta_max_year: int = 2023,
    rsf_n_estimators: int = 300,
    rsf_chunk_size: int = 25,
    gbsa_n_estimators: int = 300,
    gbsa_chunk_size: int = 25,
    fit_max_rows: int | None = None,
    progress_callback: ProgressCallback | None = None,
) -> CanonicalSurvivalResult:
    _emit_progress(progress_callback, stage="start", progress=0.01, message="starting canonical survival training")

    resolved_abt = abt_csv or (DATA_DIR / "features" / "local_survival_abt.csv")
    resolved_metrics = metrics_json or (PROJECT_ROOT / "models" / "survival_canonical_metrics.json")
    resolved_report = report_md or (DOCS_DIR / "survival_canonical.md")
    resolved_map_export = map_export_csv or (DATA_DIR / "exports" / "local_survival_map_export.csv")

    resolved_metrics.parent.mkdir(parents=True, exist_ok=True)
    resolved_report.parent.mkdir(parents=True, exist_ok=True)
    resolved_map_export.parent.mkdir(parents=True, exist_ok=True)

    abt = pd.read_csv(resolved_abt, low_memory=False)
    _emit_progress(progress_callback, stage="load_data", progress=0.08, message=f"loaded ABT rows={len(abt):,}")

    training_payload = apply_training_policies(
        abt,
        transition_policy=transition_policy_train,
        renta_max_year=renta_max_year,
    )
    train_df = training_payload["dataset"].copy()
    train_df["split"] = assign_temporal_split_adaptive(
        train_df,
        period_col="first_seen_period",
        event_col="event_observed",
        min_events_valid=120,
        min_events_test=120,
        min_rows_valid=20_000,
        min_rows_test=20_000,
    )
    _emit_progress(progress_callback, stage="split", progress=0.16, message="prepared train/valid/test split")

    scoring_payload = apply_training_policies(
        abt,
        transition_policy="keep_all",
        renta_max_year=renta_max_year,
    )
    score_df = scoring_payload["dataset"].copy()

    x_train_all = build_feature_frame(train_df, feature_profile=feature_profile)
    x_score_all = build_feature_frame(score_df, feature_profile=feature_profile)
    _emit_progress(progress_callback, stage="features", progress=0.24, message="feature matrix built")

    y_struct = Surv.from_arrays(
        event=pd.to_numeric(train_df["event_observed"], errors="coerce").fillna(0).astype(bool).to_numpy(),
        time=pd.to_numeric(train_df["duration_months"], errors="coerce").fillna(0).astype(float).to_numpy(),
    )

    fit_mask = train_df["split"].astype("string").eq("train")
    x_fit = x_train_all.loc[fit_mask]
    y_fit = y_struct[fit_mask.to_numpy()]
    if fit_max_rows is not None and len(x_fit) > int(fit_max_rows):
        selected_idx = _sample_training_indices(
            train_df.loc[fit_mask].reset_index(drop=True),
            max_rows=int(fit_max_rows),
        )
        x_fit = x_fit.reset_index(drop=True).iloc[selected_idx]
        y_fit = y_fit[selected_idx]
        _emit_progress(
            progress_callback,
            stage="fit_data",
            progress=0.30,
            message=f"fit rows sampled={len(x_fit):,} from train={int(fit_mask.sum()):,}",
        )
    else:
        _emit_progress(progress_callback, stage="fit_data", progress=0.30, message=f"fit rows={len(x_fit):,}")

    scaler = StandardScaler()
    x_fit_scaled = scaler.fit_transform(x_fit)
    x_all_train_scaled = scaler.transform(x_train_all)
    x_all_score_scaled = scaler.transform(x_score_all)

    cox = CoxPHSurvivalAnalysis(alpha=0.01)
    rsf = RandomSurvivalForest(
        n_estimators=300,
        min_samples_split=20,
        min_samples_leaf=30,
        random_state=20260313,
        n_jobs=-1,
    )
    gbsa = GradientBoostingSurvivalAnalysis(
        n_estimators=max(1, int(gbsa_n_estimators)),
        learning_rate=0.03,
        random_state=20260313,
        warm_start=True,
    )

    cox.fit(x_fit_scaled, y_fit)
    _emit_progress(progress_callback, stage="fit_cox", progress=0.36, message="cox trained")

    rsf = _fit_rsf_with_progress(
        rsf,
        x_fit,
        y_fit,
        total_estimators=rsf_n_estimators,
        chunk_size=rsf_chunk_size,
        progress_callback=progress_callback,
        progress_start=0.38,
        progress_end=0.68,
    )

    gbsa = _fit_gbsa_with_progress(
        gbsa,
        x_fit_scaled,
        y_fit,
        total_estimators=gbsa_n_estimators,
        chunk_size=gbsa_chunk_size,
        progress_callback=progress_callback,
        progress_start=0.70,
        progress_end=0.78,
    )

    train_df["risk_cox"] = cox.predict(x_all_train_scaled)
    train_df["risk_rsf"] = rsf.predict(x_train_all)
    train_df["risk_gbsa"] = gbsa.predict(x_all_train_scaled)
    train_df["risk_ensemble"] = _ensemble_rank_score(train_df[["risk_cox", "risk_rsf", "risk_gbsa"]])

    split_masks = {
        split_name: train_df["split"].astype("string").eq(split_name).to_numpy()
        for split_name in ("train", "valid", "test")
    }
    split_frames = {
        split_name: train_df.loc[mask].copy()
        for split_name, mask in split_masks.items()
    }
    split_survival = {
        split_name: _frame_to_survival(frame)
        for split_name, frame in split_frames.items()
    }

    cindex_by_model = {
        "cox": _split_c_index(train_df, score_col="risk_cox"),
        "rsf": _split_c_index(train_df, score_col="risk_rsf"),
        "gbsa": _split_c_index(train_df, score_col="risk_gbsa"),
        "ensemble": _split_c_index(train_df, score_col="risk_ensemble"),
    }
    _emit_progress(progress_callback, stage="evaluate", progress=0.82, message="computed c-index by model")

    uno_c_index = _compute_uno_c_index_by_split(
        reference_survival=y_fit,
        split_survival=split_survival,
        estimates_by_split={
            split_name: split_frames[split_name]["risk_ensemble"].to_numpy(dtype=float)
            for split_name in split_frames
        },
    )
    dynamic_auc = _compute_dynamic_auc_by_split(
        reference_survival=y_fit,
        split_survival=split_survival,
        estimates_by_split={
            split_name: split_frames[split_name]["risk_ensemble"].to_numpy(dtype=float)
            for split_name in split_frames
        },
        requested_times=DEFAULT_HORIZONS,
    )
    integrated_brier = {
        "cox": _compute_integrated_brier_by_split(
            reference_survival=y_fit,
            split_survival=split_survival,
            requested_times=DEFAULT_HORIZONS,
            predictor=lambda split_name, times: _predict_survival_probabilities(
                cox,
                x_all_train_scaled[split_masks[split_name]],
                times,
            ),
        ),
        "rsf": _compute_integrated_brier_by_split(
            reference_survival=y_fit,
            split_survival=split_survival,
            requested_times=DEFAULT_HORIZONS,
            predictor=lambda split_name, times: _predict_survival_probabilities(
                rsf,
                x_train_all.loc[split_masks[split_name]],
                times,
            ),
        ),
        "gbsa": _compute_integrated_brier_by_split(
            reference_survival=y_fit,
            split_survival=split_survival,
            requested_times=DEFAULT_HORIZONS,
            predictor=lambda split_name, times: _predict_survival_probabilities(
                gbsa,
                x_all_train_scaled[split_masks[split_name]],
                times,
            ),
        ),
    }
    _emit_progress(progress_callback, stage="robust_metrics", progress=0.86, message="computed Uno C-index, dynamic AUC and IBS")

    calibration = compute_calibration_summary(
        train_df.assign(risk_decile=np.ceil(train_df["risk_ensemble"].rank(pct=True) * 10).clip(1, 10).astype(int)),
        split_col="split",
        decile_col="risk_decile",
        event_col="event_observed",
        duration_col="duration_months",
        horizon=12,
    )

    split_event_counts = train_df.groupby("split", dropna=False)["event_observed"].sum().to_dict()
    canonical_gate = evaluate_canonical_quality_gate(
        split_event_counts=split_event_counts,
        uno_c_index=uno_c_index,
        dynamic_auc=dynamic_auc,
        integrated_brier=integrated_brier,
    )

    metrics = {
        "training_run": {
            "rsf_n_estimators": int(rsf_n_estimators),
            "rsf_chunk_size": int(rsf_chunk_size),
            "gbsa_n_estimators": int(gbsa_n_estimators),
            "gbsa_chunk_size": int(gbsa_chunk_size),
            "fit_max_rows": int(fit_max_rows) if fit_max_rows is not None else None,
            "quick_mode": bool(fit_max_rows is not None),
        },
        "policy_train": training_payload["policy"],
        "policy_scoring": scoring_payload["policy"],
        "rows": int(len(train_df)),
        "split_counts": train_df["split"].value_counts(dropna=False).to_dict(),
        "split_event_counts": split_event_counts,
        "c_index": cindex_by_model,
        "uno_c_index": uno_c_index,
        "dynamic_auc": dynamic_auc,
        "integrated_brier_score": integrated_brier,
        "calibration": calibration,
        "quality_gate": canonical_gate,
    }
    _emit_progress(progress_callback, stage="quality_gate", progress=0.88, message=f"quality_gate={canonical_gate.get('status')}")

    score_df["risk_cox"] = cox.predict(x_all_score_scaled)
    score_df["risk_rsf"] = rsf.predict(x_score_all)
    score_df["risk_gbsa"] = gbsa.predict(x_all_score_scaled)
    score_df["risk_ensemble"] = _ensemble_rank_score(score_df[["risk_cox", "risk_rsf", "risk_gbsa"]])
    score_df["risk_percentile"] = score_df["risk_ensemble"].rank(method="average", pct=True)
    score_df["risk_decile"] = np.ceil(score_df["risk_percentile"] * 10).clip(1, 10).astype(int)

    score_df["quality_flag_transition"] = score_df["coord_transform_status_start"].astype("string").eq("transition_requires_review")
    score_df["quality_flag_missing_h3"] = score_df["h3_cell_start"].isna()
    score_df["quality_flag_renta_imputed"] = score_df["renta_imputation_level"].astype("string").ne("observed")
    score_df["quality_flags_count"] = (
        score_df[["quality_flag_transition", "quality_flag_missing_h3", "quality_flag_renta_imputed"]]
        .astype(int)
        .sum(axis=1)
    )
    score_df["quality_tier"] = np.select(
        [score_df["quality_flags_count"] == 0, score_df["quality_flags_count"] == 1],
        ["high", "medium"],
        default="low",
    )

    export_cols = [
        "id_local",
        "first_seen_period",
        "last_seen_period",
        "duration_months",
        "event_observed",
        "section_key_start",
        "h3_cell_start",
        "lat_wgs84_start",
        "lon_wgs84_start",
        "risk_cox",
        "risk_rsf",
        "risk_gbsa",
        "risk_ensemble",
        "risk_percentile",
        "risk_decile",
        "quality_flag_transition",
        "quality_flag_missing_h3",
        "quality_flag_renta_imputed",
        "quality_flags_count",
        "quality_tier",
    ]
    score_df[[column for column in export_cols if column in score_df.columns]].to_csv(resolved_map_export, index=False)

    resolved_metrics.write_text(json.dumps(_to_jsonable(metrics), ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report.write_text(render_canonical_report(metrics), encoding="utf-8")
    _emit_progress(progress_callback, stage="write_outputs", progress=1.0, message="canonical artifacts written")

    return CanonicalSurvivalResult(
        metrics_json=resolved_metrics,
        report_md=resolved_report,
        map_export_csv=resolved_map_export,
    )


def _split_c_index(frame: pd.DataFrame, *, score_col: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for split in ("train", "valid", "test"):
        part = frame[frame["split"].astype("string").eq(split)]
        if part.empty:
            out[split] = float("nan")
            continue
        event = pd.to_numeric(part["event_observed"], errors="coerce").fillna(0).astype(bool).to_numpy()
        time = pd.to_numeric(part["duration_months"], errors="coerce").fillna(0).astype(float).to_numpy()
        score = pd.to_numeric(part[score_col], errors="coerce").fillna(0).astype(float).to_numpy()
        if int(event.sum()) == 0:
            out[split] = float("nan")
            continue
        out[split] = float(concordance_index_censored(event, time, score)[0])
    return out


def _ensemble_rank_score(scores: pd.DataFrame) -> pd.Series:
    ranked = scores.rank(axis=0, method="average", pct=True)
    return ranked.mean(axis=1).astype(float)


def _frame_to_survival(frame: pd.DataFrame) -> np.ndarray:
    return Surv.from_arrays(
        event=pd.to_numeric(frame["event_observed"], errors="coerce").fillna(0).astype(bool).to_numpy(),
        time=pd.to_numeric(frame["duration_months"], errors="coerce").fillna(0).astype(float).to_numpy(),
    )


def _sample_training_indices(frame: pd.DataFrame, *, max_rows: int, seed: int = 20260313) -> np.ndarray:
    max_rows = max(1, int(max_rows))
    if len(frame) <= max_rows:
        return np.arange(len(frame), dtype=int)

    event_mask = pd.to_numeric(frame["event_observed"], errors="coerce").fillna(0).astype(int).to_numpy() == 1
    event_idx = np.flatnonzero(event_mask)
    non_event_idx = np.flatnonzero(~event_mask)

    if len(event_idx) >= max_rows:
        return np.sort(event_idx[:max_rows])

    rng = np.random.default_rng(seed)
    remaining = max_rows - len(event_idx)
    sampled_non_event = rng.choice(non_event_idx, size=remaining, replace=False)
    return np.sort(np.concatenate([event_idx, sampled_non_event]).astype(int))


def _safe_metric_tau(reference_survival: np.ndarray, evaluation_survival: np.ndarray) -> float | None:
    if len(reference_survival) == 0 or len(evaluation_survival) == 0:
        return None
    reference_times = np.asarray(reference_survival["time"], dtype=float)
    evaluation_times = np.asarray(evaluation_survival["time"], dtype=float)
    if reference_times.size == 0 or evaluation_times.size == 0:
        return None
    upper_bound = min(float(np.nanmax(reference_times)), float(np.nanmax(evaluation_times)))
    if not np.isfinite(upper_bound) or upper_bound <= 0:
        return None
    return float(np.nextafter(upper_bound, 0.0))


def _horizon_key(time_horizon: float) -> str:
    return f"h{int(time_horizon)}"


def _case_control_counts(survival: np.ndarray, time_horizon: float) -> tuple[int, int]:
    event = np.asarray(survival["event"], dtype=bool)
    duration = np.asarray(survival["time"], dtype=float)
    cases = int(np.sum(event & (duration <= time_horizon)))
    controls = int(np.sum(duration > time_horizon))
    return cases, controls


def _supported_eval_times(
    reference_survival: np.ndarray,
    evaluation_survival: np.ndarray,
    *,
    requested_times: tuple[float, ...],
) -> np.ndarray:
    tau = _safe_metric_tau(reference_survival, evaluation_survival)
    if tau is None:
        return np.asarray([], dtype=float)

    supported: list[float] = []
    for time_horizon in requested_times:
        time_horizon = float(time_horizon)
        cases, controls = _case_control_counts(evaluation_survival, time_horizon)
        if time_horizon <= 0 or time_horizon >= tau:
            continue
        if cases == 0 or controls == 0:
            continue
        supported.append(time_horizon)
    return np.asarray(supported, dtype=float)


def _compute_uno_c_index_by_split(
    *,
    reference_survival: np.ndarray,
    split_survival: dict[str, np.ndarray],
    estimates_by_split: dict[str, np.ndarray],
) -> dict[str, object]:
    out: dict[str, object] = {}
    for split_name in ("train", "valid", "test"):
        survival = split_survival.get(split_name)
        estimate = np.asarray(estimates_by_split.get(split_name, []), dtype=float)
        rows = int(len(survival)) if survival is not None else 0
        events = int(np.sum(survival["event"])) if survival is not None and rows else 0
        tau = _safe_metric_tau(reference_survival, survival) if survival is not None else None
        payload: dict[str, object] = {
            "rows": rows,
            "events": events,
            "tau": tau,
            "uno_c_index": float("nan"),
        }

        if survival is None or rows == 0:
            payload["reason"] = "empty_split"
            out[split_name] = payload
            continue
        if events == 0:
            payload["reason"] = "no_events"
            out[split_name] = payload
            continue
        if tau is None:
            payload["reason"] = "unsupported_time_range"
            out[split_name] = payload
            continue

        try:
            payload["uno_c_index"] = float(
                concordance_index_ipcw(reference_survival, survival, estimate, tau=tau)[0]
            )
        except ValueError as exc:
            payload["reason"] = str(exc)
        out[split_name] = payload
    return out


def _compute_dynamic_auc_by_split(
    *,
    reference_survival: np.ndarray,
    split_survival: dict[str, np.ndarray],
    estimates_by_split: dict[str, np.ndarray],
    requested_times: tuple[float, ...],
) -> dict[str, object]:
    out: dict[str, object] = {}
    for split_name in ("train", "valid", "test"):
        survival = split_survival.get(split_name)
        estimate = np.asarray(estimates_by_split.get(split_name, []), dtype=float)
        rows = int(len(survival)) if survival is not None else 0
        events = int(np.sum(survival["event"])) if survival is not None and rows else 0
        tau = _safe_metric_tau(reference_survival, survival) if survival is not None else None
        horizons = {
            _horizon_key(time_horizon): {
                "time": float(time_horizon),
                "cases": 0,
                "controls": 0,
                "auc": float("nan"),
                "supported": False,
            }
            for time_horizon in requested_times
        }
        payload: dict[str, object] = {
            "rows": rows,
            "events": events,
            "tau": tau,
            "mean_auc": float("nan"),
            "horizons": horizons,
        }

        if survival is None or rows == 0:
            payload["reason"] = "empty_split"
            out[split_name] = payload
            continue

        for time_horizon in requested_times:
            cases, controls = _case_control_counts(survival, float(time_horizon))
            payload["horizons"][_horizon_key(time_horizon)]["cases"] = cases
            payload["horizons"][_horizon_key(time_horizon)]["controls"] = controls

        supported_times = _supported_eval_times(
            reference_survival,
            survival,
            requested_times=requested_times,
        )
        if supported_times.size == 0:
            payload["reason"] = "no_supported_horizons"
            out[split_name] = payload
            continue

        try:
            auc_values, mean_auc = cumulative_dynamic_auc(reference_survival, survival, estimate, supported_times)
            auc_values = np.atleast_1d(np.asarray(auc_values, dtype=float))
            payload["mean_auc"] = float(mean_auc)
            for time_horizon, auc_value in zip(supported_times.tolist(), auc_values.tolist()):
                horizon_payload = payload["horizons"][_horizon_key(time_horizon)]
                horizon_payload["auc"] = float(auc_value)
                horizon_payload["supported"] = True
        except ValueError as exc:
            payload["reason"] = str(exc)

        out[split_name] = payload
    return out


def _predict_survival_probabilities(estimator, features, times: np.ndarray) -> np.ndarray:
    survival_functions = estimator.predict_survival_function(features, return_array=False)
    times = np.asarray(times, dtype=float)
    probabilities = np.vstack([np.clip(step_function(times), 0.0, 1.0) for step_function in survival_functions])
    return probabilities.astype(float)


def _compute_integrated_brier_by_split(
    *,
    reference_survival: np.ndarray,
    split_survival: dict[str, np.ndarray],
    requested_times: tuple[float, ...],
    predictor: Callable[[str, np.ndarray], np.ndarray],
) -> dict[str, object]:
    out: dict[str, object] = {}
    for split_name in ("train", "valid", "test"):
        survival = split_survival.get(split_name)
        rows = int(len(survival)) if survival is not None else 0
        events = int(np.sum(survival["event"])) if survival is not None and rows else 0
        supported_times = _supported_eval_times(
            reference_survival,
            survival,
            requested_times=requested_times,
        ) if survival is not None else np.asarray([], dtype=float)
        payload: dict[str, object] = {
            "rows": rows,
            "events": events,
            "times": supported_times.astype(float).tolist(),
            "ibs": float("nan"),
        }

        if survival is None or rows == 0:
            payload["reason"] = "empty_split"
            out[split_name] = payload
            continue
        if supported_times.size < 2:
            payload["reason"] = "insufficient_supported_horizons"
            out[split_name] = payload
            continue

        try:
            survival_probabilities = predictor(split_name, supported_times)
            payload["ibs"] = float(
                integrated_brier_score(reference_survival, survival, survival_probabilities, supported_times)
            )
        except ValueError as exc:
            payload["reason"] = str(exc)
        out[split_name] = payload
    return out


def evaluate_canonical_quality_gate(
    *,
    split_event_counts: dict[str, object],
    uno_c_index: dict[str, object],
    dynamic_auc: dict[str, object],
    integrated_brier: dict[str, object],
) -> dict[str, object]:
    checks: dict[str, bool] = {}
    warnings: list[str] = []

    for split_name in ("train", "valid", "test"):
        checks[f"events_{split_name}_positive"] = float(split_event_counts.get(split_name, 0)) > 0
        uno_value = pd.to_numeric(uno_c_index.get(split_name, {}).get("uno_c_index"), errors="coerce")
        checks[f"uno_c_index_{split_name}_finite"] = bool(pd.notna(uno_value) and np.isfinite(float(uno_value)))

        dynamic_mean = pd.to_numeric(dynamic_auc.get(split_name, {}).get("mean_auc"), errors="coerce")
        checks[f"dynamic_auc_{split_name}_finite"] = bool(pd.notna(dynamic_mean) and np.isfinite(float(dynamic_mean)))

        ibs_values = [
            pd.to_numeric(integrated_brier.get(model_name, {}).get(split_name, {}).get("ibs"), errors="coerce")
            for model_name in ("cox", "rsf", "gbsa")
        ]
        checks[f"ibs_{split_name}_available"] = any(pd.notna(value) and np.isfinite(float(value)) for value in ibs_values)

    if float(split_event_counts.get("valid", 0)) < 20:
        warnings.append("very_low_validation_events")
    if float(split_event_counts.get("test", 0)) < 20:
        warnings.append("very_low_test_events")

    for split_name in ("valid", "test"):
        horizons = dynamic_auc.get(split_name, {}).get("horizons", {})
        supported = sum(1 for payload in horizons.values() if payload.get("supported"))
        if supported < len(DEFAULT_HORIZONS):
            warnings.append(f"limited_dynamic_auc_horizon_support_{split_name}")

    for split_name in ("valid", "test"):
        missing_ibs_models = [
            model_name
            for model_name in ("cox", "rsf", "gbsa")
            if not np.isfinite(
                pd.to_numeric(integrated_brier.get(model_name, {}).get(split_name, {}).get("ibs"), errors="coerce")
            )
        ]
        if missing_ibs_models:
            warnings.append(f"partial_ibs_support_{split_name}:{','.join(missing_ibs_models)}")

    if not all(checks.values()):
        status = "review_required"
    elif warnings:
        status = "pass_with_caveats"
    else:
        status = "pass"

    return {
        "status": status,
        "checks": checks,
        "warnings": warnings,
    }


def _fit_rsf_with_progress(
    rsf: RandomSurvivalForest,
    x_fit: pd.DataFrame,
    y_fit,
    *,
    total_estimators: int,
    chunk_size: int,
    progress_callback: ProgressCallback | None,
    progress_start: float,
    progress_end: float,
) -> RandomSurvivalForest:
    total_estimators = max(10, int(total_estimators))
    chunk_size = max(5, int(chunk_size))

    fitted_estimators = 0
    while fitted_estimators < total_estimators:
        next_estimators = min(fitted_estimators + chunk_size, total_estimators)
        rsf.set_params(n_estimators=next_estimators, warm_start=True)
        rsf.fit(x_fit, y_fit)
        fitted_estimators = next_estimators

        share = fitted_estimators / total_estimators
        progress = progress_start + (progress_end - progress_start) * share
        _emit_progress(
            progress_callback,
            stage="fit_rsf",
            progress=progress,
            message=f"rsf fitted trees={fitted_estimators}/{total_estimators}",
        )

    return rsf


def _fit_gbsa_with_progress(
    gbsa: GradientBoostingSurvivalAnalysis,
    x_fit,
    y_fit,
    *,
    total_estimators: int,
    chunk_size: int,
    progress_callback: ProgressCallback | None,
    progress_start: float,
    progress_end: float,
) -> GradientBoostingSurvivalAnalysis:
    total_estimators = max(1, int(total_estimators))
    chunk_size = max(1, int(chunk_size))

    fitted_estimators = 0
    while fitted_estimators < total_estimators:
        next_estimators = min(fitted_estimators + chunk_size, total_estimators)
        gbsa.set_params(n_estimators=next_estimators)
        gbsa.fit(x_fit, y_fit)
        fitted_estimators = next_estimators

        share = fitted_estimators / total_estimators
        progress = progress_start + (progress_end - progress_start) * share
        _emit_progress(
            progress_callback,
            stage="fit_gbsa",
            progress=progress,
            message=f"gbsa fitted trees={fitted_estimators}/{total_estimators}",
        )

    return gbsa


def _emit_progress(callback: ProgressCallback | None, *, stage: str, progress: float, message: str) -> None:
    if callback is None:
        return
    payload = {
        "stage": stage,
        "progress": float(max(0.0, min(1.0, progress))),
        "message": message,
    }
    callback(payload)


def render_canonical_report(metrics: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# Survival Canonical Models")
    lines.append("")
    lines.append("Entrenamiento de modelos de supervivencia canónicos (Cox, RSF, GBSA) con reglas PiT y quality gate.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    split_counts = metrics.get("split_counts", {})
    split_events = metrics.get("split_event_counts", {})
    training_run = metrics.get("training_run", {})
    lines.append(f"- Filas modeladas: {metrics.get('rows')}")
    lines.append(f"- Split rows: {json.dumps(_to_jsonable(split_counts), ensure_ascii=False)}")
    lines.append(f"- Split events: {json.dumps(_to_jsonable(split_events), ensure_ascii=False)}")
    lines.append(f"- Training run: {json.dumps(_to_jsonable(training_run), ensure_ascii=False)}")
    lines.append("")
    lines.append("## Lectura ejecutiva")
    lines.append("")
    for bullet in _build_canonical_executive_summary(metrics):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## C-index por modelo")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("c_index", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Interpretacion de discriminacion")
    lines.append("")
    for bullet in _build_discrimination_summary(metrics):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## Uno / IPCW C-index (ensemble)")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("uno_c_index", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Cumulative Dynamic AUC (ensemble)")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("dynamic_auc", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Interpretacion por horizontes")
    lines.append("")
    for bullet in _build_dynamic_auc_summary(metrics):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## Integrated Brier Score (modelos base)")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("integrated_brier_score", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Interpretacion de IBS")
    lines.append("")
    for bullet in _build_ibs_summary(metrics):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("Nota: el ensemble actual es rank-based; no se reporta IBS para el ensemble hasta definir una agregacion explicita de curvas de supervivencia.")
    lines.append("")
    lines.append("## Calibration (12 meses)")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("calibration", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Quality gate")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("quality_gate", {})), ensure_ascii=False, indent=2))
    lines.append("")
    return "\n".join(lines) + "\n"


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


def _metric_grade(value: float | None, *, inverse: bool = False) -> str:
    if value is None or not np.isfinite(value):
        return "insuficiente"
    if inverse:
        if value <= 0.02:
            return "muy_bueno"
        if value <= 0.05:
            return "bueno"
        if value <= 0.10:
            return "usable"
        return "debil"
    if value >= 0.70:
        return "muy_bueno"
    if value >= 0.60:
        return "bueno"
    if value >= 0.55:
        return "usable"
    return "debil"


def _build_canonical_executive_summary(metrics: dict[str, object]) -> list[str]:
    split_events = metrics.get("split_event_counts", {})
    quality_gate = metrics.get("quality_gate", {})
    uno_valid = _coerce_float(metrics.get("uno_c_index", {}).get("valid", {}).get("uno_c_index"))
    uno_test = _coerce_float(metrics.get("uno_c_index", {}).get("test", {}).get("uno_c_index"))
    auc_valid = _coerce_float(metrics.get("dynamic_auc", {}).get("valid", {}).get("mean_auc"))
    auc_test = _coerce_float(metrics.get("dynamic_auc", {}).get("test", {}).get("mean_auc"))
    summary = [
        f"Quality gate canonico: {quality_gate.get('status')}.",
        f"Validacion: Uno={_fmt_metric(uno_valid)} ({_metric_grade(uno_valid)}), mean Dynamic AUC={_fmt_metric(auc_valid)} ({_metric_grade(auc_valid)}).",
        f"Test: Uno={_fmt_metric(uno_test)} ({_metric_grade(uno_test)}), mean Dynamic AUC={_fmt_metric(auc_test)} ({_metric_grade(auc_test)}).",
        f"Regimen de evento raro confirmado: valid={int(split_events.get('valid', 0))} eventos, test={int(split_events.get('test', 0))} eventos.",
    ]
    if str(quality_gate.get("status")) == "pass_with_caveats":
        summary.append("El modelo es util para ranking y export operativo, pero la lectura fuera de train sigue siendo fragil por muy bajo numero de eventos.")
    return summary


def _build_discrimination_summary(metrics: dict[str, object]) -> list[str]:
    summary: list[str] = []
    uno = metrics.get("uno_c_index", {})
    for split_name in ("train", "valid", "test"):
        value = _coerce_float(uno.get(split_name, {}).get("uno_c_index"))
        summary.append(
            f"En {split_name}, el ensemble marca Uno/IPCW C-index={_fmt_metric(value)} y se clasifica como {_metric_grade(value)}."
        )
    return summary


def _build_dynamic_auc_summary(metrics: dict[str, object]) -> list[str]:
    summary: list[str] = []
    dynamic_auc = metrics.get("dynamic_auc", {})
    for split_name in ("valid", "test"):
        split_payload = dynamic_auc.get(split_name, {})
        mean_auc = _coerce_float(split_payload.get("mean_auc"))
        summary.append(
            f"En {split_name}, la media de Dynamic AUC es {_fmt_metric(mean_auc)} ({_metric_grade(mean_auc)})."
        )
        for horizon_name in ("h6", "h12", "h24"):
            horizon = split_payload.get("horizons", {}).get(horizon_name, {})
            auc_value = _coerce_float(horizon.get("auc"))
            supported = bool(horizon.get("supported"))
            cases = int(horizon.get("cases", 0) or 0)
            controls = int(horizon.get("controls", 0) or 0)
            status = _metric_grade(auc_value) if supported else "sin_soporte"
            summary.append(
                f"{split_name}:{horizon_name} -> AUC={_fmt_metric(auc_value)}, cases={cases}, controls={controls}, estado={status}."
            )
    return summary


def _build_ibs_summary(metrics: dict[str, object]) -> list[str]:
    summary: list[str] = []
    integrated_brier = metrics.get("integrated_brier_score", {})
    for split_name in ("valid", "test"):
        best_model: str | None = None
        best_value: float | None = None
        for model_name in ("cox", "rsf", "gbsa"):
            value = _coerce_float(integrated_brier.get(model_name, {}).get(split_name, {}).get("ibs"))
            if value is None:
                continue
            if best_value is None or value < best_value:
                best_model = model_name
                best_value = value
        if best_model is None:
            summary.append(f"En {split_name} no hay IBS util para comparar modelos base.")
            continue
        summary.append(
            f"En {split_name}, el mejor IBS base es {best_model}={_fmt_metric(best_value)} ({_metric_grade(best_value, inverse=True)}; menor es mejor)."
        )
    return summary


def _coerce_float(value: object) -> float | None:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return None
    return float(numeric)


def _fmt_metric(value: float | None) -> str:
    if value is None or not np.isfinite(value):
        return "nan"
    return f"{value:.4f}"
