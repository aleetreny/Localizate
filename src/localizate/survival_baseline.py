from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .paths import DATA_DIR, DOCS_DIR, PROJECT_ROOT


@dataclass(frozen=True)
class SurvivalBaselineResult:
    scored_csv: Path
    metrics_json: Path
    report_md: Path
    train_rows: int
    valid_rows: int
    test_rows: int


DEFAULT_MIN_EVENTS_VALID = 120
DEFAULT_MIN_EVENTS_TEST = 120
DEFAULT_MIN_ROWS_VALID = 20_000
DEFAULT_MIN_ROWS_TEST = 20_000


def train_and_score_survival_baseline(
    *,
    abt_csv: Path | None = None,
    scored_csv: Path | None = None,
    metrics_json: Path | None = None,
    report_md: Path | None = None,
    transition_policy: str = "exclude_transition",
    renta_max_year: int = 2023,
    min_events_valid: int = DEFAULT_MIN_EVENTS_VALID,
    min_events_test: int = DEFAULT_MIN_EVENTS_TEST,
    min_rows_valid: int = DEFAULT_MIN_ROWS_VALID,
    min_rows_test: int = DEFAULT_MIN_ROWS_TEST,
) -> SurvivalBaselineResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "local_survival_abt.csv")
    resolved_scored = scored_csv or (DATA_DIR / "exports" / "local_survival_scores.csv")
    resolved_metrics = metrics_json or (PROJECT_ROOT / "models" / "survival_baseline_metrics.json")
    resolved_report = report_md or (DOCS_DIR / "survival_baseline.md")

    resolved_scored.parent.mkdir(parents=True, exist_ok=True)
    resolved_metrics.parent.mkdir(parents=True, exist_ok=True)
    resolved_report.parent.mkdir(parents=True, exist_ok=True)

    abt = pd.read_csv(resolved_abt, low_memory=False)
    policy = apply_training_policies(
        abt,
        transition_policy=transition_policy,
        renta_max_year=renta_max_year,
    )
    dataset = policy["dataset"]

    dataset["split"] = assign_temporal_split_adaptive(
        dataset,
        period_col="first_seen_period",
        event_col="event_observed",
        min_events_valid=min_events_valid,
        min_events_test=min_events_test,
        min_rows_valid=min_rows_valid,
        min_rows_test=min_rows_test,
    )

    features = build_feature_frame(dataset)
    scores = compute_linear_risk_score(features)
    dataset["risk_score"] = scores
    dataset["risk_percentile"] = dataset["risk_score"].rank(method="average", pct=True)
    dataset["risk_decile"] = np.ceil(dataset["risk_percentile"] * 10).clip(1, 10).astype(int)
    dataset["risk_probability_12m"] = score_to_probability(dataset["risk_score"])

    metrics = {
        "policy": policy["policy"],
        "rows": int(len(dataset)),
        "split_counts": dataset["split"].value_counts(dropna=False).to_dict(),
        "split_event_counts": dataset.groupby("split", dropna=False)["event_observed"].sum().to_dict(),
        "split_event_rates": (
            dataset.groupby("split", dropna=False)["event_observed"].mean().fillna(0).to_dict()
        ),
        "c_index": {
            "train": sampled_concordance_index(
                dataset.loc[dataset["split"] == "train", "duration_months"],
                dataset.loc[dataset["split"] == "train", "event_observed"],
                dataset.loc[dataset["split"] == "train", "risk_score"],
            ),
            "valid": sampled_concordance_index(
                dataset.loc[dataset["split"] == "valid", "duration_months"],
                dataset.loc[dataset["split"] == "valid", "event_observed"],
                dataset.loc[dataset["split"] == "valid", "risk_score"],
            ),
            "test": sampled_concordance_index(
                dataset.loc[dataset["split"] == "test", "duration_months"],
                dataset.loc[dataset["split"] == "test", "event_observed"],
                dataset.loc[dataset["split"] == "test", "risk_score"],
            ),
        },
        "horizon_metrics": compute_horizon_metrics(
            dataset,
            split_col="split",
            duration_col="duration_months",
            event_col="event_observed",
            score_col="risk_score",
            prob_col="risk_probability_12m",
            horizons=(6, 12, 24),
        ),
        "calibration": compute_calibration_summary(
            dataset,
            split_col="split",
            decile_col="risk_decile",
            event_col="event_observed",
            duration_col="duration_months",
            horizon=12,
        ),
    }
    metrics["quality_gate"] = evaluate_quality_gate(metrics)

    keep_columns = [
        "id_local",
        "first_seen_period",
        "last_seen_period",
        "duration_months",
        "event_observed",
        "coord_transform_status_start",
        "section_key_start",
        "h3_cell_start",
        "renta_best_eur_start",
        "renta_effective_eur",
        "renta_imputation_level",
        "renta_carry_forward_years",
        "risk_score",
        "risk_probability_12m",
        "risk_percentile",
        "risk_decile",
        "split",
    ]
    dataset[[column for column in keep_columns if column in dataset.columns]].to_csv(resolved_scored, index=False)
    resolved_metrics.write_text(json.dumps(_to_jsonable(metrics), ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report.write_text(render_survival_baseline_report(metrics), encoding="utf-8")

    split_counts = metrics["split_counts"]
    return SurvivalBaselineResult(
        scored_csv=resolved_scored,
        metrics_json=resolved_metrics,
        report_md=resolved_report,
        train_rows=int(split_counts.get("train", 0)),
        valid_rows=int(split_counts.get("valid", 0)),
        test_rows=int(split_counts.get("test", 0)),
    )


def apply_training_policies(
    abt: pd.DataFrame,
    *,
    transition_policy: str,
    renta_max_year: int,
) -> dict[str, object]:
    dataset = abt.copy()
    dataset["first_seen_period"] = dataset["first_seen_period"].astype("string")
    dataset["first_seen_year"] = pd.to_numeric(dataset["first_seen_period"].str[:4], errors="coerce").astype("Int64")

    blocked = dataset["coord_transform_status_start"].astype("string").eq("transition_requires_review")
    blocked_rows = int(blocked.fillna(False).sum())

    if transition_policy == "exclude_transition":
        dataset = dataset[~blocked.fillna(False)].copy()

    renta = pd.to_numeric(dataset.get("renta_best_eur_start"), errors="coerce")
    dataset["district_code_start"] = dataset.get("section_key_start", pd.Series(pd.NA, index=dataset.index)).astype("string").str[:2]
    city_median = float(renta.median()) if renta.notna().any() else 0.0
    district_median = (
        pd.DataFrame({"district": dataset["district_code_start"], "renta": renta})
        .dropna(subset=["district", "renta"]) 
        .groupby("district")["renta"]
        .median()
        .to_dict()
    )

    first_year = pd.to_numeric(dataset["first_seen_year"], errors="coerce")
    carry_forward_years = (first_year - renta_max_year).clip(lower=0).fillna(0).astype(int)

    filled = renta.copy()
    missing = filled.isna()
    district_fill = dataset.loc[missing, "district_code_start"].map(district_median)
    filled.loc[missing] = district_fill
    missing_after_district = filled.isna()
    filled.loc[missing_after_district] = city_median

    dataset["renta_effective_eur"] = filled
    dataset["renta_carry_forward_years"] = carry_forward_years

    imputation_level = pd.Series("observed", index=dataset.index, dtype="string")
    imputation_level.loc[renta.isna() & dataset["district_code_start"].map(district_median).notna()] = "district_median"
    imputation_level.loc[renta.isna() & dataset["district_code_start"].map(district_median).isna()] = "city_median"
    dataset["renta_imputation_level"] = imputation_level

    policy = {
        "transition_policy": transition_policy,
        "transition_rows_blocked": blocked_rows,
        "renta_max_year": renta_max_year,
        "renta_city_median": city_median,
        "renta_imputation_counts": imputation_level.value_counts().to_dict(),
    }

    return {"dataset": dataset, "policy": policy}


def assign_temporal_split(periods: pd.Series) -> pd.Series:
    periods = periods.astype("string")
    split = pd.Series("train", index=periods.index, dtype="string")
    split.loc[(periods >= "2023-01") & (periods <= "2024-12")] = "valid"
    split.loc[periods >= "2025-01"] = "test"
    return split


def assign_temporal_split_adaptive(
    dataset: pd.DataFrame,
    *,
    period_col: str,
    event_col: str,
    min_events_valid: int,
    min_events_test: int,
    min_rows_valid: int,
    min_rows_test: int,
) -> pd.Series:
    frame = dataset[[period_col, event_col]].copy()
    frame[period_col] = frame[period_col].astype("string")
    frame[event_col] = pd.to_numeric(frame[event_col], errors="coerce").fillna(0)

    by_period = (
        frame.groupby(period_col, dropna=False)
        .agg(rows=(event_col, "size"), events=(event_col, "sum"))
        .reset_index()
        .sort_values(period_col)
        .reset_index(drop=True)
    )

    split_by_period: dict[str, str] = {str(period): "train" for period in by_period[period_col].tolist()}

    test_periods = _collect_tail_periods(by_period, period_col, min_events=min_events_test, min_rows=min_rows_test)
    remaining = by_period[~by_period[period_col].isin(test_periods)].copy()
    valid_periods = _collect_tail_periods(remaining, period_col, min_events=min_events_valid, min_rows=min_rows_valid)

    for period in valid_periods:
        split_by_period[str(period)] = "valid"
    for period in test_periods:
        split_by_period[str(period)] = "test"

    assigned = pd.Series(dataset[period_col].astype("string").map(split_by_period), index=dataset.index, dtype="string")
    event_series = pd.to_numeric(dataset[event_col], errors="coerce").fillna(0)
    valid_events = float(event_series[assigned == "valid"].sum())
    test_events = float(event_series[assigned == "test"].sum())

    # If event-aware allocation still leaves empty-event splits, use event-quantile temporal fallback.
    if (
        assigned.eq("train").sum() == 0
        or assigned.eq("test").sum() == 0
        or assigned.eq("valid").sum() == 0
        or valid_events <= 0
        or test_events <= 0
    ):
        assigned = assign_temporal_split_event_quantiles(
            dataset,
            period_col=period_col,
            event_col=event_col,
            q_valid=0.70,
            q_test=0.90,
        )

    # Final guardrail: if still degenerate, revert to deterministic fixed split.
    valid_events = float(event_series[assigned == "valid"].sum())
    test_events = float(event_series[assigned == "test"].sum())
    if (
        assigned.eq("train").sum() == 0
        or assigned.eq("test").sum() == 0
        or assigned.eq("valid").sum() == 0
        or valid_events <= 0
        or test_events <= 0
    ):
        return assign_temporal_split(dataset[period_col])
    return assigned


def assign_temporal_split_event_quantiles(
    dataset: pd.DataFrame,
    *,
    period_col: str,
    event_col: str,
    q_valid: float,
    q_test: float,
) -> pd.Series:
    periods = dataset[period_col].astype("string")
    events = pd.to_numeric(dataset[event_col], errors="coerce").fillna(0)
    event_periods = periods[events > 0]
    if event_periods.empty:
        return assign_temporal_split(periods)

    unique_event_periods = pd.Series(sorted(event_periods.dropna().unique()), dtype="string")
    n = len(unique_event_periods)
    valid_idx = min(max(int(np.floor((n - 1) * q_valid)), 0), n - 1)
    test_idx = min(max(int(np.floor((n - 1) * q_test)), 0), n - 1)
    valid_cut = unique_event_periods.iloc[valid_idx]
    test_cut = unique_event_periods.iloc[test_idx]

    split = pd.Series("train", index=dataset.index, dtype="string")
    split.loc[(periods >= valid_cut) & (periods <= test_cut)] = "valid"
    split.loc[periods > test_cut] = "test"

    if split.eq("valid").sum() == 0:
        split.loc[periods == valid_cut] = "valid"
    if split.eq("test").sum() == 0:
        split.loc[periods == test_cut] = "test"
    return split


def _collect_tail_periods(
    by_period: pd.DataFrame,
    period_col: str,
    *,
    min_events: int,
    min_rows: int,
) -> list[str]:
    if by_period.empty:
        return []

    selected: list[str] = []
    rows_acc = 0
    events_acc = 0.0
    for row in by_period.sort_values(period_col, ascending=False).itertuples(index=False):
        period = str(getattr(row, period_col))
        selected.append(period)
        rows_acc += int(getattr(row, "rows"))
        events_acc += float(getattr(row, "events"))
        if rows_acc >= min_rows and events_acc >= min_events:
            break
    return selected


def build_feature_frame(dataset: pd.DataFrame, *, fill_missing: bool = True) -> pd.DataFrame:
    frame = pd.DataFrame(index=dataset.index)
    frame["renta_effective_eur"] = pd.to_numeric(dataset["renta_effective_eur"], errors="coerce")
    frame["renta_carry_forward_years"] = pd.to_numeric(dataset.get("renta_carry_forward_years"), errors="coerce")
    frame["share_foreign_start"] = pd.to_numeric(dataset.get("share_foreign_start"), errors="coerce")
    frame["share_age_00_14_start"] = pd.to_numeric(dataset.get("share_age_00_14_start"), errors="coerce")
    frame["share_age_15_29_start"] = pd.to_numeric(dataset.get("share_age_15_29_start"), errors="coerce")
    frame["share_age_30_44_start"] = pd.to_numeric(dataset.get("share_age_30_44_start"), errors="coerce")
    frame["share_age_45_64_start"] = pd.to_numeric(dataset.get("share_age_45_64_start"), errors="coerce")
    frame["share_age_65_plus_start"] = pd.to_numeric(dataset.get("share_age_65_plus_start"), errors="coerce")
    frame["share_male_start"] = pd.to_numeric(dataset.get("share_male_start"), errors="coerce")
    frame["age_mean_start"] = pd.to_numeric(dataset.get("age_mean_start"), errors="coerce")
    frame["total_population_start"] = np.log1p(pd.to_numeric(dataset.get("total_population_start"), errors="coerce"))
    frame["population_density_km2_start"] = pd.to_numeric(dataset.get("population_density_km2_start"), errors="coerce")
    frame["padron_lag_months_start"] = pd.to_numeric(dataset.get("padron_lag_months_start"), errors="coerce")
    frame["geometry_available_start"] = pd.to_numeric(dataset.get("geometry_available_start"), errors="coerce")
    frame["missing_h3"] = dataset.get("h3_cell_start").isna().astype(float)
    frame["n_divisions_start"] = pd.to_numeric(dataset.get("n_divisions_start"), errors="coerce")
    frame["n_epigrafes_start"] = pd.to_numeric(dataset.get("n_epigrafes_start"), errors="coerce")
    frame["section_local_count_start"] = np.log1p(pd.to_numeric(dataset.get("section_local_count_start"), errors="coerce"))
    frame["section_unique_division_count_start"] = pd.to_numeric(dataset.get("section_unique_division_count_start"), errors="coerce")
    frame["section_single_division_share_start"] = pd.to_numeric(dataset.get("section_single_division_share_start"), errors="coerce")
    frame["section_same_division_local_count_start"] = np.log1p(pd.to_numeric(dataset.get("section_same_division_local_count_start"), errors="coerce"))
    frame["section_same_division_share_start"] = pd.to_numeric(dataset.get("section_same_division_share_start"), errors="coerce")
    frame["section_local_count_delta_12m_start"] = pd.to_numeric(dataset.get("section_local_count_delta_12m_start"), errors="coerce")
    frame["total_population_delta_12m_start"] = pd.to_numeric(dataset.get("total_population_delta_12m_start"), errors="coerce")
    frame["share_foreign_delta_12m_start"] = pd.to_numeric(dataset.get("share_foreign_delta_12m_start"), errors="coerce")
    frame["share_age_15_29_delta_12m_start"] = pd.to_numeric(dataset.get("share_age_15_29_delta_12m_start"), errors="coerce")
    frame["population_density_km2_delta_12m_start"] = pd.to_numeric(dataset.get("population_density_km2_delta_12m_start"), errors="coerce")
    frame["renta_best_eur_delta_12m_start"] = pd.to_numeric(dataset.get("renta_best_eur_delta_12m_start"), errors="coerce")
    frame["avisos_district_per_1000_prev_year"] = np.log1p(pd.to_numeric(dataset.get("avisos_district_per_1000_prev_year"), errors="coerce"))
    frame["avisos_barrio_per_1000_prev_year"] = np.log1p(pd.to_numeric(dataset.get("avisos_barrio_per_1000_prev_year"), errors="coerce"))
    frame["avisos_barrio_share_of_district_prev_year"] = pd.to_numeric(dataset.get("avisos_barrio_share_of_district_prev_year"), errors="coerce")
    frame["metro_distance_m_start"] = np.log1p(pd.to_numeric(dataset.get("metro_distance_m_start"), errors="coerce"))
    frame["metro_access_count_500m_start"] = pd.to_numeric(dataset.get("metro_access_count_500m_start"), errors="coerce")
    frame["metro_access_count_1000m_start"] = pd.to_numeric(dataset.get("metro_access_count_1000m_start"), errors="coerce")
    frame["missing_metro_distance_start"] = pd.to_numeric(dataset.get("missing_metro_distance_start"), errors="coerce")

    if fill_missing:
        for column in frame.columns:
            if frame[column].notna().any():
                frame[column] = frame[column].fillna(frame[column].median())
            else:
                frame[column] = 0.0
    return frame


def compute_linear_risk_score(features: pd.DataFrame) -> pd.Series:
    z = (features - features.mean()) / features.std(ddof=0).replace(0, 1)
    score = (
        -0.35 * z["renta_effective_eur"]
        + 0.10 * z["renta_carry_forward_years"]
        + 0.18 * z["share_foreign_start"]
        -0.08 * z["share_age_00_14_start"]
        -0.10 * z["share_age_15_29_start"]
        -0.06 * z["share_age_30_44_start"]
        + 0.15 * z["share_age_45_64_start"]
        + 0.28 * z["share_age_65_plus_start"]
        + 0.06 * z["share_male_start"]
        + 0.08 * z["age_mean_start"]
        -0.08 * z["total_population_start"]
        + 0.10 * z["population_density_km2_start"]
        + 0.10 * z["padron_lag_months_start"]
        -0.05 * z["geometry_available_start"]
        + 0.25 * z["missing_h3"]
        + 0.12 * z["n_divisions_start"]
        + 0.08 * z["n_epigrafes_start"]
        -0.05 * z["section_local_count_start"]
        -0.08 * z["section_unique_division_count_start"]
        + 0.08 * z["section_single_division_share_start"]
        + 0.12 * z["section_same_division_local_count_start"]
        + 0.16 * z["section_same_division_share_start"]
        -0.10 * z["section_local_count_delta_12m_start"]
        -0.06 * z["total_population_delta_12m_start"]
        + 0.08 * z["share_foreign_delta_12m_start"]
        + 0.06 * z["share_age_15_29_delta_12m_start"]
        -0.06 * z["population_density_km2_delta_12m_start"]
        -0.08 * z["renta_best_eur_delta_12m_start"]
        + 0.14 * z["avisos_district_per_1000_prev_year"]
        + 0.18 * z["avisos_barrio_per_1000_prev_year"]
        + 0.10 * z["avisos_barrio_share_of_district_prev_year"]
        + 0.10 * z["metro_distance_m_start"]
        -0.14 * z["metro_access_count_500m_start"]
        -0.08 * z["metro_access_count_1000m_start"]
        + 0.10 * z["missing_metro_distance_start"]
    )
    return score.astype(float)


def score_to_probability(score: pd.Series) -> pd.Series:
    std = float(pd.to_numeric(score, errors="coerce").std(ddof=0))
    denom = std if np.isfinite(std) and std > 0 else 1.0
    z = (score - score.mean()) / denom
    clipped = z.clip(lower=-6, upper=6)
    prob = 1.0 / (1.0 + np.exp(-clipped))
    return pd.Series(prob, index=score.index, dtype=float)


def sampled_concordance_index(
    duration: pd.Series,
    event_observed: pd.Series,
    risk_score: pd.Series,
    *,
    max_pairs: int = 200_000,
    seed: int = 20260313,
) -> float:
    d = pd.to_numeric(duration, errors="coerce").to_numpy(dtype=float)
    e = pd.to_numeric(event_observed, errors="coerce").fillna(0).to_numpy(dtype=int)
    s = pd.to_numeric(risk_score, errors="coerce").to_numpy(dtype=float)

    mask = np.isfinite(d) & np.isfinite(s)
    d = d[mask]
    e = e[mask]
    s = s[mask]
    n = len(d)
    if n < 2:
        return float("nan")

    rng = np.random.default_rng(seed)
    comparable = 0
    concordant = 0.0

    sample_size = min(max_pairs, n * 10)
    idx_i = rng.integers(0, n, size=sample_size)
    idx_j = rng.integers(0, n, size=sample_size)

    for i, j in zip(idx_i, idx_j):
        if i == j:
            continue
        ti, tj = d[i], d[j]
        ei, ej = e[i], e[j]

        if ti < tj and ei == 1:
            comparable += 1
            if s[i] > s[j]:
                concordant += 1
            elif s[i] == s[j]:
                concordant += 0.5
        elif tj < ti and ej == 1:
            comparable += 1
            if s[j] > s[i]:
                concordant += 1
            elif s[i] == s[j]:
                concordant += 0.5

    if comparable == 0:
        return float("nan")
    return float(concordant / comparable)


def compute_horizon_metrics(
    dataset: pd.DataFrame,
    *,
    split_col: str,
    duration_col: str,
    event_col: str,
    score_col: str,
    prob_col: str,
    horizons: tuple[int, ...],
) -> dict[str, object]:
    out: dict[str, object] = {}
    duration = pd.to_numeric(dataset[duration_col], errors="coerce")
    event = pd.to_numeric(dataset[event_col], errors="coerce").fillna(0)
    score = pd.to_numeric(dataset[score_col], errors="coerce")
    prob = pd.to_numeric(dataset[prob_col], errors="coerce")

    for split_name in ("train", "valid", "test"):
        split_mask = dataset[split_col].astype("string").eq(split_name)
        split_metrics: dict[str, object] = {}
        for horizon in horizons:
            y = ((event == 1) & (duration <= horizon)).astype(int)
            y_split = y[split_mask]
            score_split = score[split_mask]
            prob_split = prob[split_mask]
            auc = binary_auc(y_split, score_split)
            brier = binary_brier(y_split, prob_split)
            split_metrics[f"h{horizon}"] = {
                "rows": int(split_mask.sum()),
                "events": int(y_split.sum()),
                "auc": auc,
                "brier": brier,
            }
        out[split_name] = split_metrics
    return out


def binary_auc(y_true: pd.Series, score: pd.Series) -> float:
    y = pd.to_numeric(y_true, errors="coerce").fillna(0).astype(int)
    s = pd.to_numeric(score, errors="coerce")
    mask = y.notna() & s.notna()
    y = y[mask].to_numpy()
    s = s[mask].to_numpy(dtype=float)

    pos = y == 1
    neg = y == 0
    n_pos = int(pos.sum())
    n_neg = int(neg.sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")

    ranks = pd.Series(s).rank(method="average").to_numpy(dtype=float)
    sum_pos = float(ranks[pos].sum())
    auc = (sum_pos - (n_pos * (n_pos + 1) / 2.0)) / (n_pos * n_neg)
    return float(auc)


def binary_brier(y_true: pd.Series, prob: pd.Series) -> float:
    y = pd.to_numeric(y_true, errors="coerce").fillna(0).astype(float)
    p = pd.to_numeric(prob, errors="coerce")
    mask = y.notna() & p.notna()
    if int(mask.sum()) == 0:
        return float("nan")
    return float(np.mean((y[mask].to_numpy() - p[mask].to_numpy()) ** 2))


def compute_calibration_summary(
    dataset: pd.DataFrame,
    *,
    split_col: str,
    decile_col: str,
    event_col: str,
    duration_col: str,
    horizon: int,
) -> dict[str, object]:
    duration = pd.to_numeric(dataset[duration_col], errors="coerce")
    event = pd.to_numeric(dataset[event_col], errors="coerce").fillna(0)
    y_h = ((event == 1) & (duration <= horizon)).astype(int)

    out: dict[str, object] = {}
    for split_name in ("train", "valid", "test"):
        split_mask = dataset[split_col].astype("string").eq(split_name)
        frame = pd.DataFrame(
            {
                "decile": pd.to_numeric(dataset.loc[split_mask, decile_col], errors="coerce"),
                "y": y_h[split_mask],
            }
        ).dropna(subset=["decile"])
        if frame.empty:
            out[split_name] = []
            continue
        calib = (
            frame.groupby("decile", dropna=False)
            .agg(rows=("y", "size"), event_rate=("y", "mean"))
            .reset_index()
            .sort_values("decile")
        )
        out[split_name] = calib.to_dict(orient="records")
    return out


def render_survival_baseline_report(metrics: dict[str, object]) -> str:
    split_counts = metrics.get("split_counts", {})
    split_event_counts = metrics.get("split_event_counts", {})
    split_event_rates = metrics.get("split_event_rates", {})
    c_index = metrics.get("c_index", {})
    horizon_metrics = metrics.get("horizon_metrics", {})
    policy = metrics.get("policy", {})
    quality_gate = metrics.get("quality_gate", {})

    lines: list[str] = []
    lines.append("# Survival Baseline")
    lines.append("")
    lines.append("Baseline heuristico de riesgo para supervivencia, con split temporal bloqueado y politicas PiT de robustez.")
    lines.append("")
    lines.append("## Politicas aplicadas")
    lines.append("")
    lines.append(f"- `transition_policy`: {policy.get('transition_policy')}")
    lines.append(f"- Filas bloqueadas por transicion CRS: {policy.get('transition_rows_blocked')}")
    lines.append(f"- `renta_max_year`: {policy.get('renta_max_year')}")
    lines.append(f"- Mediana ciudad para imputacion de renta: {policy.get('renta_city_median')}")
    lines.append("")
    lines.append("## Split temporal")
    lines.append("")
    lines.append(f"- Train: {split_counts.get('train', 0):,}")
    lines.append(f"- Validation: {split_counts.get('valid', 0):,}")
    lines.append(f"- Test: {split_counts.get('test', 0):,}")
    lines.append(f"- Eventos train: {int(split_event_counts.get('train', 0)):,}")
    lines.append(f"- Eventos validation: {int(split_event_counts.get('valid', 0)):,}")
    lines.append(f"- Eventos test: {int(split_event_counts.get('test', 0)):,}")
    lines.append(f"- Tasa evento train: {split_event_rates.get('train')}")
    lines.append(f"- Tasa evento validation: {split_event_rates.get('valid')}")
    lines.append(f"- Tasa evento test: {split_event_rates.get('test')}")
    lines.append("")
    lines.append("## Concordance index (sampled)")
    lines.append("")
    lines.append(f"- Train C-index: {c_index.get('train')}")
    lines.append(f"- Validation C-index: {c_index.get('valid')}")
    lines.append(f"- Test C-index: {c_index.get('test')}")
    lines.append("")
    lines.append("## Horizon metrics (6/12/24 meses)")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(horizon_metrics), ensure_ascii=False, sort_keys=True))
    lines.append("")
    lines.append("## Quality gate")
    lines.append("")
    lines.append(f"- Estado: {quality_gate.get('status')}")
    lines.append(
        "- Checks: "
        + json.dumps(_to_jsonable(quality_gate.get("checks", {})), ensure_ascii=False, sort_keys=True)
    )
    lines.append(
        "- Warnings: "
        + json.dumps(_to_jsonable(quality_gate.get("warnings", [])), ensure_ascii=False)
    )
    lines.append("")
    return "\n".join(lines) + "\n"


def evaluate_quality_gate(metrics: dict[str, object]) -> dict[str, object]:
    c_index = metrics.get("c_index", {})
    split_event_counts = metrics.get("split_event_counts", {})

    checks: dict[str, bool] = {}
    warnings: list[str] = []

    checks["events_train_positive"] = float(split_event_counts.get("train", 0)) > 0
    checks["events_valid_positive"] = float(split_event_counts.get("valid", 0)) > 0
    checks["events_test_positive"] = float(split_event_counts.get("test", 0)) > 0

    for split_name in ("train", "valid", "test"):
        value = c_index.get(split_name)
        checks[f"c_index_{split_name}_finite"] = value is not None and np.isfinite(value)
        if value is not None and np.isfinite(value) and (value < 0.45 or value > 0.80):
            warnings.append(f"c_index_{split_name}_outside_expected_range")

    status = "pass" if all(checks.values()) else "review_required"
    return {
        "status": status,
        "checks": checks,
        "warnings": warnings,
    }


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
