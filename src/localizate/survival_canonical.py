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
from sksurv.metrics import concordance_index_censored
from sksurv.util import Surv

from .paths import DATA_DIR, DOCS_DIR, PROJECT_ROOT
from .survival_baseline import (
    apply_training_policies,
    assign_temporal_split_adaptive,
    build_feature_frame,
    compute_calibration_summary,
    compute_horizon_metrics,
    evaluate_quality_gate,
)


@dataclass(frozen=True)
class CanonicalSurvivalResult:
    metrics_json: Path
    report_md: Path
    map_export_csv: Path


ProgressCallback = Callable[[dict[str, object]], None]


def train_canonical_survival_models(
    *,
    abt_csv: Path | None = None,
    metrics_json: Path | None = None,
    report_md: Path | None = None,
    map_export_csv: Path | None = None,
    transition_policy_train: str = "exclude_transition",
    renta_max_year: int = 2023,
    rsf_n_estimators: int = 300,
    rsf_chunk_size: int = 25,
    gbsa_n_estimators: int = 300,
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

    x_train_all = build_feature_frame(train_df)
    x_score_all = build_feature_frame(score_df)
    _emit_progress(progress_callback, stage="features", progress=0.24, message="feature matrix built")

    y_struct = Surv.from_arrays(
        event=pd.to_numeric(train_df["event_observed"], errors="coerce").fillna(0).astype(bool).to_numpy(),
        time=pd.to_numeric(train_df["duration_months"], errors="coerce").fillna(0).astype(float).to_numpy(),
    )

    fit_mask = train_df["split"].astype("string").eq("train")
    x_fit = x_train_all.loc[fit_mask]
    y_fit = y_struct[fit_mask.to_numpy()]
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
        n_estimators=gbsa_n_estimators,
        learning_rate=0.03,
        random_state=20260313,
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

    gbsa.fit(x_fit_scaled, y_fit)
    _emit_progress(progress_callback, stage="fit_gbsa", progress=0.74, message="gbsa trained")

    train_df["risk_cox"] = cox.predict(x_all_train_scaled)
    train_df["risk_rsf"] = rsf.predict(x_train_all)
    train_df["risk_gbsa"] = gbsa.predict(x_all_train_scaled)
    train_df["risk_ensemble"] = _ensemble_rank_score(train_df[["risk_cox", "risk_rsf", "risk_gbsa"]])

    cindex_by_model = {
        "cox": _split_c_index(train_df, score_col="risk_cox"),
        "rsf": _split_c_index(train_df, score_col="risk_rsf"),
        "gbsa": _split_c_index(train_df, score_col="risk_gbsa"),
        "ensemble": _split_c_index(train_df, score_col="risk_ensemble"),
    }
    _emit_progress(progress_callback, stage="evaluate", progress=0.82, message="computed c-index by model")

    horizon = compute_horizon_metrics(
        train_df,
        split_col="split",
        duration_col="duration_months",
        event_col="event_observed",
        score_col="risk_ensemble",
        prob_col="risk_ensemble",
        horizons=(6, 12, 24),
    )
    calibration = compute_calibration_summary(
        train_df.assign(risk_decile=np.ceil(train_df["risk_ensemble"].rank(pct=True) * 10).clip(1, 10).astype(int)),
        split_col="split",
        decile_col="risk_decile",
        event_col="event_observed",
        duration_col="duration_months",
        horizon=12,
    )

    canonical_gate = evaluate_quality_gate(
        {
            "c_index": cindex_by_model["ensemble"],
            "split_event_counts": train_df.groupby("split", dropna=False)["event_observed"].sum().to_dict(),
        }
    )

    metrics = {
        "policy_train": training_payload["policy"],
        "policy_scoring": scoring_payload["policy"],
        "rows": int(len(train_df)),
        "split_counts": train_df["split"].value_counts(dropna=False).to_dict(),
        "split_event_counts": train_df.groupby("split", dropna=False)["event_observed"].sum().to_dict(),
        "c_index": cindex_by_model,
        "horizon_metrics": horizon,
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
    lines.append(f"- Filas modeladas: {metrics.get('rows')}")
    lines.append(f"- Split rows: {json.dumps(_to_jsonable(split_counts), ensure_ascii=False)}")
    lines.append(f"- Split events: {json.dumps(_to_jsonable(split_events), ensure_ascii=False)}")
    lines.append("")
    lines.append("## C-index por modelo")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("c_index", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Horizon metrics (ensemble)")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("horizon_metrics", {})), ensure_ascii=False))
    lines.append("")
    lines.append("## Quality gate")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("quality_gate", {})), ensure_ascii=False))
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
