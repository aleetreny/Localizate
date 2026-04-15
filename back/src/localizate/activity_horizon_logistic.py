from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from .paths import DATA_DIR, DOCS_MODELING_DIR, MODELS_DIR, PROJECT_ROOT
from .survival_baseline import (
    apply_training_policies,
    assign_temporal_split_adaptive,
    binary_auc,
    binary_brier,
    build_feature_frame,
)


@dataclass(frozen=True)
class ActivityHorizonLogisticResult:
    metrics_json: Path
    report_md: Path
    selected_horizons: tuple[int, ...]


DEFAULT_CANDIDATE_HORIZONS = (3, 6, 9, 12, 15, 18, 24, 30, 36)


def train_activity_horizon_logistic_models(
    *,
    abt_csv: Path | None = None,
    survival_map_export_csv: Path | None = None,
    metrics_json: Path | None = None,
    report_md: Path | None = None,
    transition_policy: str = "exclude_transition",
    renta_max_year: int = 2023,
    candidate_horizons: tuple[int, ...] = DEFAULT_CANDIDATE_HORIZONS,
    min_valid_cases: int = 15,
    min_valid_controls: int = 1000,
    min_test_cases: int = 100,
    min_test_controls: int = 200,
    max_horizons: int = 3,
    random_seed: int = 20260326,
) -> ActivityHorizonLogisticResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "activity_survival_abt.csv")
    resolved_scores = survival_map_export_csv or (DATA_DIR / "exports" / "activity_survival_map_export.csv")
    resolved_metrics = metrics_json or (MODELS_DIR / "activity_horizon_logistic_metrics.json")
    resolved_report = report_md or (DOCS_MODELING_DIR / "activity_horizon_logistic.md")

    resolved_metrics.parent.mkdir(parents=True, exist_ok=True)
    resolved_report.parent.mkdir(parents=True, exist_ok=True)

    abt = pd.read_csv(resolved_abt, low_memory=False)
    policy_payload = apply_training_policies(
        abt,
        transition_policy=transition_policy,
        renta_max_year=renta_max_year,
    )
    dataset = policy_payload["dataset"].copy()
    dataset["split"] = assign_temporal_split_adaptive(
        dataset,
        period_col="first_seen_period",
        event_col="event_observed",
        min_events_valid=120,
        min_events_test=120,
        min_rows_valid=20_000,
        min_rows_test=20_000,
    )

    support = summarize_horizon_support(dataset, candidate_horizons=candidate_horizons)
    selected_horizons = select_logistic_horizons(
        support,
        min_valid_cases=min_valid_cases,
        min_valid_controls=min_valid_controls,
        min_test_cases=min_test_cases,
        min_test_controls=min_test_controls,
        max_horizons=max_horizons,
    )
    if not selected_horizons:
        raise ValueError("No supported logistic horizons available under the configured support thresholds")

    features = build_feature_frame(dataset, feature_profile="activity_survival_pruned")
    merged = _merge_survival_scores(dataset, resolved_scores)
    feature_names = list(features.columns)

    horizon_results: dict[str, object] = {}
    for horizon in selected_horizons:
        eligible_mask = eligible_horizon_mask(dataset, horizon=horizon)
        y = horizon_binary_target(dataset, horizon=horizon)

        frame = dataset.loc[eligible_mask].copy()
        x = features.loc[eligible_mask].copy()
        merged_scores = merged.loc[eligible_mask].copy()
        y_frame = y.loc[eligible_mask].copy()

        train_mask = frame["split"].astype("string").eq("train")
        scaler = StandardScaler()
        x_train = scaler.fit_transform(x.loc[train_mask])
        model = LogisticRegression(
            C=0.5,
            class_weight="balanced",
            max_iter=1000,
            random_state=random_seed,
        )
        model.fit(x_train, y_frame.loc[train_mask].to_numpy(dtype=int))

        probability = pd.Series(
            model.predict_proba(scaler.transform(x))[:, 1],
            index=frame.index,
            dtype=float,
        )

        split_metrics: dict[str, object] = {}
        for split_name in ("train", "valid", "test"):
            split_mask = frame["split"].astype("string").eq(split_name)
            y_split = y_frame.loc[split_mask]
            p_split = probability.loc[split_mask]
            risk_split = merged_scores.loc[split_mask, "risk_ensemble"]
            split_metrics[split_name] = {
                "rows": int(split_mask.sum()),
                "events": int(y_split.sum()),
                "event_rate": float(y_split.mean()) if int(split_mask.sum()) else float("nan"),
                "logistic_auc": binary_auc(y_split, p_split),
                "survival_risk_auc": binary_auc(y_split, risk_split),
                "logistic_brier": binary_brier(y_split, p_split),
            }
            split_metrics[split_name]["auc_delta_vs_survival"] = (
                float(split_metrics[split_name]["logistic_auc"] - split_metrics[split_name]["survival_risk_auc"])
                if np.isfinite(split_metrics[split_name]["logistic_auc"])
                and np.isfinite(split_metrics[split_name]["survival_risk_auc"])
                else float("nan")
            )

        coef = pd.Series(model.coef_[0], index=feature_names, dtype=float)
        top_coef = (
            coef.reindex(coef.abs().sort_values(ascending=False).head(10).index)
            .round(6)
            .to_dict()
        )

        horizon_results[f"h{horizon}"] = {
            "horizon_months": int(horizon),
            "eligible_rows": int(len(frame)),
            "eligible_event_count": int(y_frame.sum()),
            "support": support[f"h{horizon}"],
            "metrics": split_metrics,
            "top_standardized_coefficients": top_coef,
        }

    payload = {
        "source_artifacts": {
            "abt_csv": str(resolved_abt),
            "survival_map_export_csv": str(resolved_scores),
        },
        "policy": policy_payload["policy"],
        "split_counts": dataset["split"].value_counts(dropna=False).to_dict(),
        "split_event_counts": dataset.groupby("split", dropna=False)["event_observed"].sum().to_dict(),
        "candidate_horizons": [int(value) for value in candidate_horizons],
        "support_selection_rules": {
            "min_valid_cases": int(min_valid_cases),
            "min_valid_controls": int(min_valid_controls),
            "min_test_cases": int(min_test_cases),
            "min_test_controls": int(min_test_controls),
            "max_horizons": int(max_horizons),
        },
        "support_summary": support,
        "selected_horizons": [int(value) for value in selected_horizons],
        "models": horizon_results,
    }

    resolved_metrics.write_text(json.dumps(_to_jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report.write_text(render_activity_horizon_logistic_markdown(payload), encoding="utf-8")

    return ActivityHorizonLogisticResult(
        metrics_json=resolved_metrics,
        report_md=resolved_report,
        selected_horizons=tuple(int(value) for value in selected_horizons),
    )


def summarize_horizon_support(
    dataset: pd.DataFrame,
    *,
    candidate_horizons: tuple[int, ...],
) -> dict[str, dict[str, object]]:
    duration = pd.to_numeric(dataset["duration_months"], errors="coerce").fillna(0)
    event = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    split = dataset["split"].astype("string")

    out: dict[str, dict[str, object]] = {}
    for horizon in candidate_horizons:
        support: dict[str, object] = {"horizon_months": int(horizon)}
        for split_name in ("train", "valid", "test"):
            split_mask = split.eq(split_name)
            support[split_name] = {
                "cases": int(((split_mask) & (event.eq(1)) & (duration.le(horizon))).sum()),
                "controls": int(((split_mask) & (duration.gt(horizon))).sum()),
                "eligible_rows": int((split_mask & eligible_horizon_mask(dataset, horizon=horizon)).sum()),
            }
        out[f"h{horizon}"] = support
    return out


def select_logistic_horizons(
    support_summary: dict[str, dict[str, object]],
    *,
    min_valid_cases: int,
    min_valid_controls: int,
    min_test_cases: int,
    min_test_controls: int,
    max_horizons: int,
) -> tuple[int, ...]:
    supported: list[int] = []
    for key, payload in support_summary.items():
        horizon = int(str(key).removeprefix("h"))
        valid = payload.get("valid", {}) if isinstance(payload, dict) else {}
        test = payload.get("test", {}) if isinstance(payload, dict) else {}
        if (
            int(valid.get("cases", 0) or 0) >= min_valid_cases
            and int(valid.get("controls", 0) or 0) >= min_valid_controls
            and int(test.get("cases", 0) or 0) >= min_test_cases
            and int(test.get("controls", 0) or 0) >= min_test_controls
        ):
            supported.append(horizon)

    supported = sorted(set(supported))
    if len(supported) <= max_horizons:
        return tuple(supported)

    positions = np.linspace(0, len(supported) - 1, num=max_horizons)
    selected = sorted({supported[int(round(position))] for position in positions})
    return tuple(selected)


def eligible_horizon_mask(dataset: pd.DataFrame, *, horizon: int) -> pd.Series:
    duration = pd.to_numeric(dataset["duration_months"], errors="coerce").fillna(0)
    event = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    return ((event == 1) & (duration <= horizon)) | (duration > horizon)


def horizon_binary_target(dataset: pd.DataFrame, *, horizon: int) -> pd.Series:
    duration = pd.to_numeric(dataset["duration_months"], errors="coerce").fillna(0)
    event = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    return (((event == 1) & (duration <= horizon)).astype(int)).astype(int)


def render_activity_horizon_logistic_markdown(payload: dict[str, object]) -> str:
    selected_horizons = payload.get("selected_horizons", [])
    split_counts = payload.get("split_counts", {})
    split_event_counts = payload.get("split_event_counts", {})
    support_rules = payload.get("support_selection_rules", {})
    models = payload.get("models", {})

    lines: list[str] = []
    lines.append("# Activity Horizon Logistic")
    lines.append("")
    lines.append("Comparativa horizon-based entre regresión logística y el score survival actual sobre el target `activity_survival`.")
    lines.append("")
    lines.append("## Split base")
    lines.append("")
    lines.append(f"- Split counts: {json.dumps(_to_jsonable(split_counts), ensure_ascii=False)}")
    lines.append(f"- Split event counts: {json.dumps(_to_jsonable(split_event_counts), ensure_ascii=False)}")
    lines.append(f"- Reglas de soporte: {json.dumps(_to_jsonable(support_rules), ensure_ascii=False)}")
    lines.append(f"- Horizontes elegidos: {json.dumps(_to_jsonable(selected_horizons), ensure_ascii=False)}")
    lines.append("")
    lines.append("## Lectura ejecutiva")
    lines.append("")
    for bullet in _build_executive_summary(models):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## Modelos por horizonte")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(models), ensure_ascii=False, indent=2))
    lines.append("")
    return "\n".join(lines) + "\n"


def _merge_survival_scores(dataset: pd.DataFrame, score_csv: Path) -> pd.DataFrame:
    scores = pd.read_csv(score_csv, low_memory=False)
    merge_keys = [column for column in ("id_local", "first_seen_period") if column in scores.columns]
    score_cols = merge_keys + ["risk_ensemble"]
    dedup = scores[score_cols].drop_duplicates(subset=merge_keys)
    merged = dataset[["id_local", "first_seen_period"]].merge(dedup, on=merge_keys, how="left", validate="one_to_one")
    merged.index = dataset.index
    merged["risk_ensemble"] = pd.to_numeric(merged["risk_ensemble"], errors="coerce").fillna(0.0)
    return merged


def _build_executive_summary(models: object) -> list[str]:
    if not isinstance(models, dict) or not models:
        return ["No se han generado modelos logisticos."]

    bullets: list[str] = []
    valid_wins = 0
    test_wins = 0
    for horizon_key, payload in models.items():
        if not isinstance(payload, dict):
            continue
        metrics = payload.get("metrics", {}) if isinstance(payload.get("metrics"), dict) else {}
        valid = metrics.get("valid", {}) if isinstance(metrics.get("valid"), dict) else {}
        test = metrics.get("test", {}) if isinstance(metrics.get("test"), dict) else {}
        valid_delta = valid.get("auc_delta_vs_survival")
        test_delta = test.get("auc_delta_vs_survival")
        if valid_delta is not None and np.isfinite(valid_delta) and valid_delta > 0:
            valid_wins += 1
        if test_delta is not None and np.isfinite(test_delta) and test_delta > 0:
            test_wins += 1
        bullets.append(
            f"{horizon_key}: valid AUC logit={_fmt(valid.get('logistic_auc'))} vs survival={_fmt(valid.get('survival_risk_auc'))}; test AUC logit={_fmt(test.get('logistic_auc'))} vs survival={_fmt(test.get('survival_risk_auc'))}."
        )

    bullets.insert(
        0,
        f"La logística gana en {valid_wins} de {len(models)} horizontes en valid y en {test_wins} de {len(models)} en test frente al score survival actual, usando la misma población elegible por horizonte.",
    )
    return bullets


def _fmt(value: object) -> str:
    if value is None:
        return "nan"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "nan"
    if not np.isfinite(numeric):
        return "nan"
    return f"{numeric:.4f}"


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
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value