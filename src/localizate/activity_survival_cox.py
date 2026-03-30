from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.util import Surv

from .paths import DATA_DIR
from .survival_baseline import apply_training_policies, assign_temporal_split_adaptive, build_feature_frame


DEFAULT_ACTIVITY_COX_HORIZONS = (12.0, 24.0)
ACTIVITY_CONTEXT_INTERACTION_BASES = (
    "renta_effective_eur",
    "share_foreign_start",
    "share_age_15_29_start",
    "population_density_km2_start",
    "metro_distance_m_start",
    "section_same_activity_category_share_start",
)
DEFAULT_ACTIVITY_RELATIVE_WEIGHT_MIN = 0.30
DEFAULT_ACTIVITY_RELATIVE_WEIGHT_MAX = 0.70
DEFAULT_ACTIVITY_RELATIVE_WEIGHT_EVENT_PIVOT = 120.0
DEFAULT_ACTIVITY_SPECIFICITY_BONUS = 0.30
DEFAULT_ACTIVITY_EFFECTIVE_WEIGHT_MIN = 0.35
DEFAULT_ACTIVITY_EFFECTIVE_WEIGHT_MAX = 0.92


@dataclass(frozen=True)
class ActivityRiskReference:
    sorted_scores: np.ndarray
    mean: float
    std: float
    rows: int
    events: int
    relative_weight: float


@dataclass
class ActivitySurvivalCoxScorer:
    feature_profile: str
    include_context_interactions: bool
    scaler: StandardScaler
    estimator: CoxPHSurvivalAnalysis
    feature_columns: tuple[str, ...]
    feature_fill_values: pd.Series
    sorted_reference_scores: np.ndarray
    reference_score_mean: float
    reference_score_std: float
    activity_references: dict[str, ActivityRiskReference]

    def score_frame(
        self,
        frame: pd.DataFrame,
        *,
        horizons: tuple[float, ...] = DEFAULT_ACTIVITY_COX_HORIZONS,
    ) -> pd.DataFrame:
        scoring_frame = frame.copy()
        if "renta_effective_eur" not in scoring_frame.columns:
            scoring_frame["renta_effective_eur"] = pd.to_numeric(scoring_frame.get("renta_best_eur_start"), errors="coerce")
        if "renta_carry_forward_years" not in scoring_frame.columns:
            scoring_frame["renta_carry_forward_years"] = 0.0

        features = build_activity_survival_feature_frame(
            scoring_frame,
            feature_profile=self.feature_profile,
            include_context_interactions=self.include_context_interactions,
            fill_missing=False,
        )
        features = features.reindex(columns=self.feature_columns)
        features = features.fillna(self.feature_fill_values).fillna(0.0)
        scaled = self.scaler.transform(features)

        risk_cox = pd.Series(self.estimator.predict(scaled), index=frame.index, dtype=float)
        centered_scores = (risk_cox - float(self.reference_score_mean)) / float(self.reference_score_std)
        risk_index = pd.Series(1.0 / (1.0 + np.exp(-centered_scores)), index=frame.index, dtype=float)
        percentiles = risk_cox.map(lambda value: compute_score_percentile(self.sorted_reference_scores, float(value)))
        activity_fit_percentiles, activity_fit_z, activity_relative_weight = compute_activity_context_metrics(
            activity_codes=resolve_activity_codes(scoring_frame),
            score_values=risk_cox.to_numpy(dtype=float),
            default_percentiles=percentiles.to_numpy(dtype=float),
            default_z_scores=centered_scores.to_numpy(dtype=float),
            references=self.activity_references,
        )
        activity_specificity = compute_activity_specificity(
            activity_codes=resolve_activity_codes(scoring_frame),
            references=self.activity_references,
            global_std=float(self.reference_score_std),
        )
        activity_effective_weight = np.clip(
            activity_relative_weight + DEFAULT_ACTIVITY_SPECIFICITY_BONUS * activity_specificity,
            DEFAULT_ACTIVITY_EFFECTIVE_WEIGHT_MIN,
            DEFAULT_ACTIVITY_EFFECTIVE_WEIGHT_MAX,
        )
        activity_context_index = pd.Series(
            activity_effective_weight * activity_fit_percentiles + (1.0 - activity_effective_weight) * risk_index.to_numpy(dtype=float),
            index=frame.index,
            dtype=float,
        )

        resolved_horizons = tuple(float(value) for value in horizons)
        survival_probabilities = predict_survival_probabilities(self.estimator, scaled, resolved_horizons)

        out = pd.DataFrame(
            {
                "risk_cox": risk_cox.astype(float),
                "risk_index": risk_index.astype(float),
                "risk_percentile": percentiles.astype(float),
                "activity_fit_percentile": pd.Series(activity_fit_percentiles, index=frame.index, dtype=float),
                "activity_fit_z": pd.Series(activity_fit_z, index=frame.index, dtype=float),
                "activity_relative_weight": pd.Series(activity_relative_weight, index=frame.index, dtype=float),
                "activity_specificity": pd.Series(activity_specificity, index=frame.index, dtype=float),
                "activity_effective_weight": pd.Series(activity_effective_weight, index=frame.index, dtype=float),
                "activity_context_index": activity_context_index.astype(float),
            },
            index=frame.index,
        )
        for position, horizon in enumerate(resolved_horizons):
            out[f"survival_{int(horizon)}m"] = survival_probabilities[:, position]
        return out


def fit_activity_survival_cox_scorer(
    *,
    abt: pd.DataFrame | None = None,
    abt_csv: Path | None = None,
    usecols: list[str] | None = None,
    feature_profile: str = "activity_survival_pruned",
    include_context_interactions: bool = True,
    transition_policy_train: str = "exclude_transition",
    transition_policy_score: str = "keep_all",
    renta_max_year: int = 2023,
    min_events_valid: int = 120,
    min_events_test: int = 120,
    min_rows_valid: int = 20_000,
    min_rows_test: int = 20_000,
    alpha: float = 0.1,
) -> ActivitySurvivalCoxScorer:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "activity_survival_abt.csv")
    source = abt.copy() if abt is not None else pd.read_csv(resolved_abt, usecols=usecols, low_memory=False)

    training_payload = apply_training_policies(
        source,
        transition_policy=transition_policy_train,
        renta_max_year=renta_max_year,
    )
    train_df = training_payload["dataset"].copy()
    train_df["split"] = assign_temporal_split_adaptive(
        train_df,
        period_col="first_seen_period",
        event_col="event_observed",
        min_events_valid=min_events_valid,
        min_events_test=min_events_test,
        min_rows_valid=min_rows_valid,
        min_rows_test=min_rows_test,
    )

    scoring_payload = apply_training_policies(
        source,
        transition_policy=transition_policy_score,
        renta_max_year=renta_max_year,
    )
    score_df = scoring_payload["dataset"].copy()

    x_train_all = build_activity_survival_feature_frame(
        train_df,
        feature_profile=feature_profile,
        include_context_interactions=include_context_interactions,
    )
    x_score_all = build_activity_survival_feature_frame(
        score_df,
        feature_profile=feature_profile,
        include_context_interactions=include_context_interactions,
    )
    feature_fill_values = x_train_all.median().fillna(0.0)

    fit_mask = train_df["split"].astype("string").eq("train")
    if not bool(fit_mask.any()):
        raise ValueError("No train rows available to fit activity survival Cox scorer")

    x_fit = x_train_all.loc[fit_mask]
    y_fit = Surv.from_arrays(
        event=pd.to_numeric(train_df.loc[fit_mask, "event_observed"], errors="coerce").fillna(0).astype(bool).to_numpy(),
        time=pd.to_numeric(train_df.loc[fit_mask, "duration_months"], errors="coerce").fillna(0).astype(float).to_numpy(),
    )

    scaler = StandardScaler()
    x_fit_scaled = scaler.fit_transform(x_fit)
    estimator = CoxPHSurvivalAnalysis(alpha=float(alpha))
    estimator.fit(x_fit_scaled, y_fit)

    reference_scores = estimator.predict(scaler.transform(x_score_all))
    reference_scores = np.asarray(reference_scores, dtype=float)
    sorted_reference_scores = np.sort(reference_scores)
    reference_score_mean = float(np.nanmean(reference_scores))
    reference_score_std = float(np.nanstd(reference_scores))
    if not np.isfinite(reference_score_std) or reference_score_std <= 0.0:
        reference_score_std = 1.0
    activity_references = build_activity_references(score_df, reference_scores)

    return ActivitySurvivalCoxScorer(
        feature_profile=feature_profile,
        include_context_interactions=include_context_interactions,
        scaler=scaler,
        estimator=estimator,
        feature_columns=tuple(str(column) for column in x_train_all.columns),
        feature_fill_values=feature_fill_values,
        sorted_reference_scores=sorted_reference_scores,
        reference_score_mean=reference_score_mean,
        reference_score_std=reference_score_std,
        activity_references=activity_references,
    )


def build_activity_survival_feature_frame(
    dataset: pd.DataFrame,
    *,
    feature_profile: str,
    include_context_interactions: bool,
    fill_missing: bool = True,
) -> pd.DataFrame:
    base = build_feature_frame(dataset, fill_missing=fill_missing, feature_profile=feature_profile)
    if not include_context_interactions:
        return base

    macro_columns = [column for column in base.columns if column.startswith("macro_category__")]
    if not macro_columns:
        return base

    interaction_blocks: list[pd.DataFrame] = []
    for base_column in ACTIVITY_CONTEXT_INTERACTION_BASES:
        if base_column not in base.columns:
            continue
        base_values = pd.to_numeric(base[base_column], errors="coerce").fillna(0.0)
        block = pd.DataFrame(
            {
                f"{base_column}__x__{macro_column.split('__', 1)[1]}": base_values * pd.to_numeric(base[macro_column], errors="coerce").fillna(0.0)
                for macro_column in macro_columns
            },
            index=base.index,
        )
        interaction_blocks.append(block)

    if not interaction_blocks:
        return base
    return pd.concat([base] + interaction_blocks, axis=1)


def predict_survival_probabilities(
    estimator: CoxPHSurvivalAnalysis,
    features: np.ndarray,
    horizons: tuple[float, ...],
) -> np.ndarray:
    resolved_horizons = np.asarray(horizons, dtype=float)
    survival_functions = estimator.predict_survival_function(features, return_array=False)
    probabilities = np.vstack([np.clip(step_function(resolved_horizons), 0.0, 1.0) for step_function in survival_functions])
    return probabilities.astype(float)


def compute_score_percentile(sorted_scores: np.ndarray, value: float) -> float:
    if len(sorted_scores) == 0 or not np.isfinite(value):
        return float("nan")
    position = int(np.searchsorted(sorted_scores, value, side="right"))
    return float(position / len(sorted_scores))


def resolve_activity_codes(frame: pd.DataFrame) -> pd.Series:
    if "activity_category_code_start" in frame.columns:
        return frame["activity_category_code_start"].astype("string")
    if "macro_category_code" in frame.columns:
        return frame["macro_category_code"].astype("string")
    return pd.Series(pd.NA, index=frame.index, dtype="string")


def compute_activity_context_metrics(
    *,
    activity_codes: pd.Series,
    score_values: np.ndarray,
    default_percentiles: np.ndarray,
    default_z_scores: np.ndarray,
    references: dict[str, ActivityRiskReference],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fit_percentiles = np.asarray(default_percentiles, dtype=float).copy()
    fit_z_scores = np.asarray(default_z_scores, dtype=float).copy()
    relative_weight = np.full(len(score_values), DEFAULT_ACTIVITY_RELATIVE_WEIGHT_MIN, dtype=float)

    for position, (activity_code, score_value) in enumerate(zip(activity_codes.astype("string"), score_values)):
        if pd.isna(activity_code):
            continue
        reference = references.get(str(activity_code))
        if reference is None:
            continue
        fit_percentiles[position] = compute_score_percentile(reference.sorted_scores, float(score_value))
        fit_z_scores[position] = (float(score_value) - reference.mean) / reference.std
        relative_weight[position] = reference.relative_weight

    return fit_percentiles, fit_z_scores, relative_weight


def build_activity_references(dataset: pd.DataFrame, score_values: np.ndarray) -> dict[str, ActivityRiskReference]:
    activity_codes = resolve_activity_codes(dataset)
    frame = pd.DataFrame(
        {
            "activity_code": activity_codes,
            "risk_cox": np.asarray(score_values, dtype=float),
            "event_observed": pd.to_numeric(dataset.get("event_observed"), errors="coerce").fillna(0).astype(int),
        }
    )
    frame = frame[frame["activity_code"].notna()].copy()
    if frame.empty:
        return {}

    references: dict[str, ActivityRiskReference] = {}
    for activity_code, part in frame.groupby("activity_code", dropna=False):
        sorted_scores = np.sort(part["risk_cox"].to_numpy(dtype=float))
        mean_score = float(np.nanmean(sorted_scores))
        std_score = float(np.nanstd(sorted_scores))
        if not np.isfinite(std_score) or std_score <= 0.0:
            std_score = 1.0
        n_events = int(pd.to_numeric(part["event_observed"], errors="coerce").fillna(0).sum())
        support_ratio = float(n_events / (n_events + DEFAULT_ACTIVITY_RELATIVE_WEIGHT_EVENT_PIVOT)) if n_events >= 0 else 0.0
        relative_weight = DEFAULT_ACTIVITY_RELATIVE_WEIGHT_MIN + (DEFAULT_ACTIVITY_RELATIVE_WEIGHT_MAX - DEFAULT_ACTIVITY_RELATIVE_WEIGHT_MIN) * support_ratio
        references[str(activity_code)] = ActivityRiskReference(
            sorted_scores=sorted_scores,
            mean=mean_score,
            std=std_score,
            rows=int(len(part)),
            events=n_events,
            relative_weight=float(relative_weight),
        )
    return references


def compute_activity_specificity(
    *,
    activity_codes: pd.Series,
    references: dict[str, ActivityRiskReference],
    global_std: float,
) -> np.ndarray:
    resolved_global_std = float(global_std) if np.isfinite(global_std) and global_std > 0.0 else 1.0
    specificity = np.zeros(len(activity_codes), dtype=float)
    for position, activity_code in enumerate(activity_codes.astype("string")):
        if pd.isna(activity_code):
            continue
        reference = references.get(str(activity_code))
        if reference is None:
            continue
        specificity[position] = 1.0 - float(np.clip(reference.std / resolved_global_std, 0.0, 1.0))
    return specificity