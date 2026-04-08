from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy import stats

from .paths import DATA_DIR, DOCS_DIR, PROJECT_ROOT
from .survival_baseline import apply_training_policies, build_feature_frame


@dataclass(frozen=True)
class SurvivalFeatureValidationResult:
    metrics_json: Path
    report_md: Path
    rows: int
    features: int


def validate_survival_feature_frame(
    *,
    abt_csv: Path | None = None,
    metrics_json: Path | None = None,
    report_md: Path | None = None,
    transition_policy: str = "exclude_transition",
    renta_max_year: int = 2023,
    feature_profile: str = "full",
) -> SurvivalFeatureValidationResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "local_survival_abt.csv")
    resolved_metrics = metrics_json or (PROJECT_ROOT / "models" / "survival_feature_validation.json")
    resolved_report = report_md or (DOCS_DIR / "survival_feature_validation.md")

    resolved_metrics.parent.mkdir(parents=True, exist_ok=True)
    resolved_report.parent.mkdir(parents=True, exist_ok=True)

    abt = pd.read_csv(resolved_abt, low_memory=False)
    policy = apply_training_policies(abt, transition_policy=transition_policy, renta_max_year=renta_max_year)
    dataset = policy["dataset"].copy()
    raw_features = build_feature_frame(dataset, fill_missing=False, feature_profile=feature_profile)
    features = build_feature_frame(dataset, fill_missing=True, feature_profile=feature_profile)

    event = pd.to_numeric(dataset["event_observed"], errors="coerce").fillna(0).astype(int)
    event_mask = event.eq(1)
    summaries: list[dict[str, object]] = []

    for column in features.columns:
        raw = pd.to_numeric(raw_features[column], errors="coerce")
        filled = pd.to_numeric(features[column], errors="coerce")
        event_values = filled.loc[event_mask]
        non_event_values = filled.loc[~event_mask]

        mean_event = float(event_values.mean()) if not event_values.empty else float("nan")
        mean_non_event = float(non_event_values.mean()) if not non_event_values.empty else float("nan")
        std_event = float(event_values.std(ddof=0)) if len(event_values) > 1 else 0.0
        std_non_event = float(non_event_values.std(ddof=0)) if len(non_event_values) > 1 else 0.0
        pooled_std = float(np.sqrt((std_event**2 + std_non_event**2) / 2.0)) if (std_event or std_non_event) else 0.0
        standardized_mean_diff = (
            (mean_event - mean_non_event) / pooled_std if pooled_std and np.isfinite(pooled_std) else float("nan")
        )

        mann_whitney_p = float("nan")
        if len(event_values) >= 5 and len(non_event_values) >= 5 and filled.nunique(dropna=True) > 1:
            try:
                mann_whitney_p = float(
                    stats.mannwhitneyu(event_values, non_event_values, alternative="two-sided").pvalue
                )
            except ValueError:
                mann_whitney_p = float("nan")

        point_biserial = float("nan")
        if filled.nunique(dropna=True) > 1:
            try:
                point_biserial = float(stats.pointbiserialr(event.astype(float), filled.astype(float)).statistic)
            except ValueError:
                point_biserial = float("nan")

        summaries.append(
            {
                "feature": column,
                "missing_rate": float(raw.isna().mean()),
                "mean_event": mean_event,
                "mean_non_event": mean_non_event,
                "standardized_mean_diff": standardized_mean_diff,
                "mann_whitney_p": mann_whitney_p,
                "point_biserial": point_biserial,
            }
        )

    summary_df = pd.DataFrame(summaries).sort_values(
        ["mann_whitney_p", "standardized_mean_diff"],
        ascending=[True, False],
        na_position="last",
    )
    significant = int((pd.to_numeric(summary_df["mann_whitney_p"], errors="coerce") < 0.05).fillna(False).sum())
    low_missing = int((pd.to_numeric(summary_df["missing_rate"], errors="coerce") <= 0.2).fillna(False).sum())

    payload = {
        "policy": policy["policy"],
        "feature_profile": feature_profile,
        "rows": int(len(dataset)),
        "event_rate": float(event.mean()) if len(event) else 0.0,
        "feature_count": int(len(summary_df)),
        "features_with_p_lt_0_05": significant,
        "features_with_missing_rate_le_0_20": low_missing,
        "top_features_by_signal": summary_df.head(15).to_dict(orient="records"),
        "all_features": summary_df.to_dict(orient="records"),
    }
    resolved_metrics.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report.write_text(render_survival_feature_validation_report(payload), encoding="utf-8")

    return SurvivalFeatureValidationResult(
        metrics_json=resolved_metrics,
        report_md=resolved_report,
        rows=int(len(dataset)),
        features=int(len(summary_df)),
    )


def render_survival_feature_validation_report(payload: dict[str, object]) -> str:
    def _as_float(value: object, default: float = 0.0) -> float:
        numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        return float(numeric) if pd.notna(numeric) else default

    lines: list[str] = []
    lines.append("# Survival Feature Validation")
    lines.append("")
    lines.append("Chequeo estadístico ligero de la matriz de variables antes de relanzar el entrenamiento canónico.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Perfil de features: `{payload.get('feature_profile', 'full')}`")
    lines.append(f"- Filas analizadas: {int(payload.get('rows', 0)):,}")
    lines.append(f"- Event rate: {float(payload.get('event_rate', 0.0)):.4f}")
    lines.append(f"- Variables analizadas: {int(payload.get('feature_count', 0))}")
    lines.append(f"- Variables con `p < 0.05`: {int(payload.get('features_with_p_lt_0_05', 0))}")
    lines.append(f"- Variables con missing <= 20% antes de imputación: {int(payload.get('features_with_missing_rate_le_0_20', 0))}")
    lines.append("")
    lines.append("## Top variables por señal univariante")
    lines.append("")
    lines.append("| Variable | Missing | Media evento | Media no evento | SMD | p-value | Correlación biserial |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload.get("top_features_by_signal", []):
        lines.append(
            "| {feature} | {missing:.2%} | {mean_event:.4f} | {mean_non_event:.4f} | {smd:.4f} | {pvalue:.4g} | {pb:.4f} |".format(
                feature=row.get("feature", ""),
                missing=_as_float(row.get("missing_rate", 0.0)),
                mean_event=_as_float(row.get("mean_event", 0.0)),
                mean_non_event=_as_float(row.get("mean_non_event", 0.0)),
                smd=_as_float(row.get("standardized_mean_diff", 0.0)),
                pvalue=_as_float(row.get("mann_whitney_p", 1.0), default=1.0),
                pb=_as_float(row.get("point_biserial", 0.0)),
            )
        )
    lines.append("")
    lines.append("## Interpretación")
    lines.append("")
    lines.append("- Este reporte no sustituye al entrenamiento survival final; solo verifica cobertura y señal univariante razonable.")
    lines.append("- Un `p-value` bajo o una `SMD` alta indican separación útil entre eventos y no eventos, pero no prueban causalidad ni robustez multivariante.")
    lines.append("- Las variables externas de `avisos` y `metro` quedan integradas y listas para el siguiente entrenamiento canónico.")
    return "\n".join(lines) + "\n"
