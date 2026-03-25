from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sksurv.metrics import concordance_index_ipcw, cumulative_dynamic_auc

from .paths import DATA_DIR, DOCS_DIR, PROJECT_ROOT
from .survival_baseline import apply_training_policies, assign_temporal_split_adaptive
from .survival_canonical import (
    DEFAULT_HORIZONS,
    _compute_dynamic_auc_by_split,
    _compute_uno_c_index_by_split,
    _frame_to_survival,
    _supported_eval_times,
)


@dataclass(frozen=True)
class CanonicalRobustnessResult:
    report_md: Path
    report_json: Path
    status: str


def run_canonical_robustness_check(
    *,
    abt_csv: Path | None = None,
    map_export_csv: Path | None = None,
    canonical_metrics_json: Path | None = None,
    report_md: Path | None = None,
    report_json: Path | None = None,
    bootstrap_iterations: int = 200,
    bootstrap_max_rows: int | None = 10000,
    random_seed: int = 20260325,
) -> CanonicalRobustnessResult:
    resolved_abt = abt_csv or (DATA_DIR / "features" / "local_survival_abt.csv")
    resolved_map_export = map_export_csv or (DATA_DIR / "exports" / "local_survival_map_export.csv")
    resolved_canonical_metrics = canonical_metrics_json or (PROJECT_ROOT / "models" / "survival_canonical_metrics.json")
    resolved_report_md = report_md or (DOCS_DIR / "survival_canonical_robustness.md")
    resolved_report_json = report_json or (PROJECT_ROOT / "models" / "survival_canonical_robustness.json")

    resolved_report_md.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_json.parent.mkdir(parents=True, exist_ok=True)

    abt = pd.read_csv(resolved_abt, low_memory=False)
    scores = pd.read_csv(resolved_map_export, low_memory=False)
    canonical_metrics = _load_json_if_exists(resolved_canonical_metrics)

    merged = _merge_abt_with_scores(abt, scores)
    training_payload = apply_training_policies(
        merged,
        transition_policy="exclude_transition",
        renta_max_year=2023,
    )
    dataset = training_payload["dataset"].copy()
    dataset["split"] = assign_temporal_split_adaptive(
        dataset,
        period_col="first_seen_period",
        event_col="event_observed",
        min_events_valid=120,
        min_events_test=120,
        min_rows_valid=20_000,
        min_rows_test=20_000,
    )

    split_frames = {
        split_name: dataset.loc[dataset["split"].astype("string").eq(split_name)].copy()
        for split_name in ("train", "valid", "test")
    }
    split_survival = {split_name: _frame_to_survival(frame) for split_name, frame in split_frames.items()}
    reference_survival = split_survival["train"]
    estimates_by_split = {
        split_name: pd.to_numeric(frame["risk_ensemble"], errors="coerce").fillna(0).to_numpy(dtype=float)
        for split_name, frame in split_frames.items()
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

    bootstrap_uno = _bootstrap_uno_c_index_by_split(
        reference_survival=reference_survival,
        split_frames=split_frames,
        score_col="risk_ensemble",
        iterations=bootstrap_iterations,
        max_rows=bootstrap_max_rows,
        seed=random_seed,
    )
    bootstrap_dynamic_auc = _bootstrap_dynamic_auc_by_split(
        reference_survival=reference_survival,
        split_frames=split_frames,
        score_col="risk_ensemble",
        base_dynamic_auc=dynamic_auc,
        iterations=bootstrap_iterations,
        max_rows=bootstrap_max_rows,
        seed=random_seed,
    )

    comparison = _compare_against_canonical_metrics(canonical_metrics, uno_c_index, dynamic_auc)
    warnings = _build_robustness_warnings(dynamic_auc, bootstrap_uno, bootstrap_dynamic_auc, comparison)
    status = _resolve_robustness_status(warnings, comparison)

    payload = {
        "status": status,
        "source_artifacts": {
            "abt_csv": str(resolved_abt),
            "map_export_csv": str(resolved_map_export),
            "canonical_metrics_json": str(resolved_canonical_metrics),
        },
        "dataset": {
            "rows_scored": int(len(scores)),
            "rows_merged": int(len(merged)),
            "rows_evaluated": int(len(dataset)),
            "split_counts": dataset["split"].value_counts(dropna=False).to_dict(),
            "split_event_counts": dataset.groupby("split", dropna=False)["event_observed"].sum().to_dict(),
        },
        "bootstrap_config": {
            "iterations": int(bootstrap_iterations),
            "max_rows": int(bootstrap_max_rows) if bootstrap_max_rows is not None else None,
            "random_seed": int(random_seed),
        },
        "metrics": {
            "uno_c_index": _to_jsonable(uno_c_index),
            "dynamic_auc": _to_jsonable(dynamic_auc),
        },
        "bootstrap": {
            "uno_c_index": _to_jsonable(bootstrap_uno),
            "dynamic_auc": _to_jsonable(bootstrap_dynamic_auc),
        },
        "comparison_with_training_metrics": _to_jsonable(comparison),
        "warnings": warnings,
        "recommended_primary_metrics": [
            "uno_c_index.valid",
            "uno_c_index.test",
            "dynamic_auc.valid.mean_auc",
            "dynamic_auc.test.h6",
            "dynamic_auc.test.h12",
        ],
    }

    resolved_report_json.write_text(json.dumps(_to_jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    resolved_report_md.write_text(render_canonical_robustness_markdown(payload), encoding="utf-8")

    return CanonicalRobustnessResult(
        report_md=resolved_report_md,
        report_json=resolved_report_json,
        status=status,
    )


def render_canonical_robustness_markdown(payload: dict[str, object]) -> str:
    dataset = payload.get("dataset", {})
    bootstrap_config = payload.get("bootstrap_config", {})
    warnings = payload.get("warnings", [])
    metrics = payload.get("metrics", {})
    bootstrap = payload.get("bootstrap", {})

    lines: list[str] = []
    lines.append("# Survival Canonical Robustness")
    lines.append("")
    lines.append("Chequeo post-entrenamiento sobre los scores ya exportados para añadir intervalos de confianza y alertas de soporte estadístico sin relanzar el fit.")
    lines.append("")
    lines.append(f"- Estado global: {payload.get('status')}")
    lines.append(f"- Filas evaluadas: {dataset.get('rows_evaluated')}")
    lines.append(f"- Split counts: {json.dumps(_to_jsonable(dataset.get('split_counts', {})), ensure_ascii=False)}")
    lines.append(f"- Split events: {json.dumps(_to_jsonable(dataset.get('split_event_counts', {})), ensure_ascii=False)}")
    lines.append(f"- Bootstrap config: {json.dumps(_to_jsonable(bootstrap_config), ensure_ascii=False)}")
    lines.append("")
    lines.append("## Lectura ejecutiva")
    lines.append("")
    for bullet in _build_executive_summary(metrics, bootstrap, warnings):
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## Uno / IPCW C-index")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("uno_c_index", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Bootstrap Uno / IPCW C-index")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(bootstrap.get("uno_c_index", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Dynamic AUC")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(metrics.get("dynamic_auc", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Bootstrap Dynamic AUC")
    lines.append("")
    lines.append(json.dumps(_to_jsonable(bootstrap.get("dynamic_auc", {})), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    lines.append(json.dumps(warnings, ensure_ascii=False, indent=2))
    lines.append("")
    return "\n".join(lines) + "\n"


def _merge_abt_with_scores(abt: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    merge_keys = [column for column in ("id_local", "first_seen_period") if column in abt.columns and column in scores.columns]
    if not merge_keys:
        raise ValueError("No shared merge keys between ABT and score export")

    score_columns = merge_keys + [
        column
        for column in ("risk_cox", "risk_rsf", "risk_gbsa", "risk_ensemble", "risk_percentile", "risk_decile")
        if column in scores.columns
    ]
    deduplicated_scores = scores[score_columns].drop_duplicates(subset=merge_keys)
    return abt.merge(deduplicated_scores, on=merge_keys, how="inner", validate="one_to_one")


def _bootstrap_uno_c_index_by_split(
    *,
    reference_survival: np.ndarray,
    split_frames: dict[str, pd.DataFrame],
    score_col: str,
    iterations: int,
    max_rows: int | None,
    seed: int,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    out: dict[str, object] = {}

    for split_name in ("valid", "test"):
        frame = split_frames.get(split_name, pd.DataFrame()).copy()
        estimate = pd.to_numeric(frame.get(score_col), errors="coerce").fillna(0)
        sample_rows = min(len(frame), int(max_rows)) if max_rows is not None and len(frame) else len(frame)
        values: list[float] = []
        skipped = 0

        if frame.empty:
            out[split_name] = {
                "estimate": float("nan"),
                "ci_lower": float("nan"),
                "ci_upper": float("nan"),
                "iterations_requested": int(iterations),
                "iterations_successful": 0,
                "sample_rows": 0,
                "reason": "empty_split",
            }
            continue

        for _ in range(int(iterations)):
            sampled = _bootstrap_sample_frame(frame.assign(_score_eval=estimate), rng=rng, sample_rows=sample_rows)
            survival = _frame_to_survival(sampled)
            tau = _safe_metric_tau(reference_survival, survival)
            if tau is None or int(np.sum(survival["event"])) == 0:
                skipped += 1
                continue
            try:
                metric = float(
                    concordance_index_ipcw(
                        reference_survival,
                        survival,
                        pd.to_numeric(sampled["_score_eval"], errors="coerce").fillna(0).to_numpy(dtype=float),
                        tau=tau,
                    )[0]
                )
            except ValueError:
                skipped += 1
                continue
            values.append(metric)

        out[split_name] = _bootstrap_payload(values, iterations=iterations, sample_rows=sample_rows, skipped=skipped)
    return out


def _bootstrap_dynamic_auc_by_split(
    *,
    reference_survival: np.ndarray,
    split_frames: dict[str, pd.DataFrame],
    score_col: str,
    base_dynamic_auc: dict[str, object],
    iterations: int,
    max_rows: int | None,
    seed: int,
) -> dict[str, object]:
    rng = np.random.default_rng(seed + 17)
    out: dict[str, object] = {}

    for split_name in ("valid", "test"):
        frame = split_frames.get(split_name, pd.DataFrame()).copy()
        estimate = pd.to_numeric(frame.get(score_col), errors="coerce").fillna(0)
        base_payload = base_dynamic_auc.get(split_name, {})
        horizons = base_payload.get("horizons", {}) if isinstance(base_payload, dict) else {}
        supported_times = [
            float(payload.get("time"))
            for payload in horizons.values()
            if isinstance(payload, dict) and payload.get("supported")
        ]
        sample_rows = min(len(frame), int(max_rows)) if max_rows is not None and len(frame) else len(frame)
        mean_values: list[float] = []
        horizon_values: dict[str, list[float]] = {
            str(key): []
            for key, payload in horizons.items()
            if isinstance(payload, dict) and payload.get("supported")
        }
        skipped = 0

        if frame.empty or not supported_times:
            out[split_name] = {
                "mean_auc": _bootstrap_payload([], iterations=iterations, sample_rows=sample_rows, skipped=int(iterations)),
                "horizons": {
                    str(key): _bootstrap_payload([], iterations=iterations, sample_rows=sample_rows, skipped=int(iterations))
                    for key in horizons
                },
                "reason": "empty_split_or_no_supported_horizons",
            }
            continue

        fixed_times = np.asarray(supported_times, dtype=float)
        for _ in range(int(iterations)):
            sampled = _bootstrap_sample_frame(frame.assign(_score_eval=estimate), rng=rng, sample_rows=sample_rows)
            survival = _frame_to_survival(sampled)
            if _supported_eval_times(reference_survival, survival, requested_times=tuple(supported_times)).size != len(supported_times):
                skipped += 1
                continue
            try:
                auc_values, mean_auc = cumulative_dynamic_auc(
                    reference_survival,
                    survival,
                    pd.to_numeric(sampled["_score_eval"], errors="coerce").fillna(0).to_numpy(dtype=float),
                    fixed_times,
                )
            except ValueError:
                skipped += 1
                continue

            mean_values.append(float(mean_auc))
            for horizon_key, auc_value in zip(horizon_values.keys(), np.atleast_1d(np.asarray(auc_values, dtype=float)).tolist()):
                horizon_values[horizon_key].append(float(auc_value))

        out[split_name] = {
            "mean_auc": _bootstrap_payload(mean_values, iterations=iterations, sample_rows=sample_rows, skipped=skipped),
            "horizons": {
                horizon_key: _bootstrap_payload(values, iterations=iterations, sample_rows=sample_rows, skipped=skipped)
                for horizon_key, values in horizon_values.items()
            },
        }
    return out


def _bootstrap_sample_frame(frame: pd.DataFrame, *, rng: np.random.Generator, sample_rows: int) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()

    event_mask = pd.to_numeric(frame["event_observed"], errors="coerce").fillna(0).astype(int).to_numpy() == 1
    event_idx = np.flatnonzero(event_mask)
    non_event_idx = np.flatnonzero(~event_mask)

    if sample_rows <= 0:
        sample_rows = len(frame)

    if len(event_idx) == 0 or len(non_event_idx) == 0:
        sampled_idx = rng.choice(np.arange(len(frame)), size=sample_rows, replace=True)
        return frame.iloc[np.sort(sampled_idx)].reset_index(drop=True)

    event_share = len(event_idx) / len(frame)
    target_events = min(sample_rows, max(1, int(round(sample_rows * event_share))))
    target_non_events = max(1, sample_rows - target_events)
    sampled_events = rng.choice(event_idx, size=target_events, replace=True)
    sampled_non_events = rng.choice(non_event_idx, size=target_non_events, replace=True)
    sampled_idx = np.concatenate([sampled_events, sampled_non_events])
    return frame.iloc[np.sort(sampled_idx)].reset_index(drop=True)


def _bootstrap_payload(values: list[float], *, iterations: int, sample_rows: int, skipped: int) -> dict[str, object]:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return {
            "estimate": float("nan"),
            "ci_lower": float("nan"),
            "ci_upper": float("nan"),
            "ci_width": float("nan"),
            "iterations_requested": int(iterations),
            "iterations_successful": 0,
            "success_rate": 0.0,
            "sample_rows": int(sample_rows),
            "skipped_iterations": int(skipped),
        }

    ci_lower, ci_upper = np.percentile(array, [2.5, 97.5]).tolist()
    estimate = float(np.median(array))
    return {
        "estimate": estimate,
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "ci_width": float(ci_upper - ci_lower),
        "iterations_requested": int(iterations),
        "iterations_successful": int(array.size),
        "success_rate": float(array.size / max(1, int(iterations))),
        "sample_rows": int(sample_rows),
        "skipped_iterations": int(skipped),
    }


def _compare_against_canonical_metrics(
    canonical_metrics: dict[str, object],
    uno_c_index: dict[str, object],
    dynamic_auc: dict[str, object],
) -> dict[str, object]:
    comparison: dict[str, object] = {"matches_training_metrics": True, "deltas": {}}
    if not canonical_metrics:
        comparison["matches_training_metrics"] = False
        comparison["reason"] = "missing_training_metrics"
        return comparison

    canonical_uno = canonical_metrics.get("uno_c_index", {})
    canonical_dynamic = canonical_metrics.get("dynamic_auc", {})
    tolerance = 1e-3

    for split_name in ("valid", "test"):
        delta_uno = _metric_delta(
            canonical_uno.get(split_name, {}).get("uno_c_index"),
            uno_c_index.get(split_name, {}).get("uno_c_index"),
        )
        delta_auc = _metric_delta(
            canonical_dynamic.get(split_name, {}).get("mean_auc"),
            dynamic_auc.get(split_name, {}).get("mean_auc"),
        )
        comparison["deltas"][split_name] = {
            "uno_c_index": delta_uno,
            "dynamic_auc_mean": delta_auc,
        }
        if any(abs(value) > tolerance for value in (delta_uno, delta_auc) if np.isfinite(value)):
            comparison["matches_training_metrics"] = False
    return comparison


def _metric_delta(expected: object, observed: object) -> float:
    left = pd.to_numeric(expected, errors="coerce")
    right = pd.to_numeric(observed, errors="coerce")
    if pd.isna(left) or pd.isna(right):
        return float("nan")
    return float(float(right) - float(left))


def _build_robustness_warnings(
    dynamic_auc: dict[str, object],
    bootstrap_uno: dict[str, object],
    bootstrap_dynamic_auc: dict[str, object],
    comparison: dict[str, object],
) -> list[str]:
    warnings: list[str] = []

    if not comparison.get("matches_training_metrics", False):
        warnings.append("recomputed_metrics_do_not_match_training_artifact")

    for split_name in ("valid", "test"):
        uno_success = float(pd.to_numeric(bootstrap_uno.get(split_name, {}).get("success_rate"), errors="coerce") or 0.0)
        if uno_success < 0.9:
            warnings.append(f"low_bootstrap_success_uno_{split_name}")

        dynamic_payload = bootstrap_dynamic_auc.get(split_name, {})
        mean_success = float(
            pd.to_numeric(dynamic_payload.get("mean_auc", {}).get("success_rate"), errors="coerce") or 0.0
        )
        if mean_success < 0.9:
            warnings.append(f"low_bootstrap_success_dynamic_auc_{split_name}")

        ci_width = pd.to_numeric(dynamic_payload.get("mean_auc", {}).get("ci_width"), errors="coerce")
        if pd.notna(ci_width) and float(ci_width) > 0.20:
            warnings.append(f"wide_dynamic_auc_ci_{split_name}")

        uno_width = pd.to_numeric(bootstrap_uno.get(split_name, {}).get("ci_width"), errors="coerce")
        if pd.notna(uno_width) and float(uno_width) > 0.15:
            warnings.append(f"wide_uno_ci_{split_name}")

        for horizon_key, horizon_payload in dynamic_auc.get(split_name, {}).get("horizons", {}).items():
            cases = int(horizon_payload.get("cases", 0) or 0)
            controls = int(horizon_payload.get("controls", 0) or 0)
            if horizon_payload.get("supported") and cases < 20:
                warnings.append(f"low_cases_{split_name}_{horizon_key}")
            if horizon_payload.get("supported") and controls < 200:
                warnings.append(f"low_controls_{split_name}_{horizon_key}")

    return list(dict.fromkeys(warnings))


def _resolve_robustness_status(warnings: list[str], comparison: dict[str, object]) -> str:
    if not comparison.get("matches_training_metrics", False):
        return "review_required"
    severe_prefixes = ("low_bootstrap_success_", "wide_uno_ci_", "wide_dynamic_auc_ci_")
    if any(warning.startswith(severe_prefixes) for warning in warnings):
        return "pass_with_caveats"
    return "pass"


def _build_executive_summary(metrics: dict[str, object], bootstrap: dict[str, object], warnings: list[str]) -> list[str]:
    bullets: list[str] = []
    uno = metrics.get("uno_c_index", {})
    dynamic = metrics.get("dynamic_auc", {})
    boot_uno = bootstrap.get("uno_c_index", {})
    boot_dynamic = bootstrap.get("dynamic_auc", {})

    bullets.append(
        "El chequeo robusto reutiliza los scores del último run y añade intervalos bootstrap sin relanzar el entrenamiento."
    )
    bullets.append(
        f"Uno valid={_fmt_metric(uno.get('valid', {}).get('uno_c_index'))} con CI bootstrap {_fmt_ci(boot_uno.get('valid', {}))}; test={_fmt_metric(uno.get('test', {}).get('uno_c_index'))} con CI {_fmt_ci(boot_uno.get('test', {}))}."
    )
    bullets.append(
        f"Dynamic AUC mean valid={_fmt_metric(dynamic.get('valid', {}).get('mean_auc'))} con CI {_fmt_ci(boot_dynamic.get('valid', {}).get('mean_auc', {}))}; test={_fmt_metric(dynamic.get('test', {}).get('mean_auc'))} con CI {_fmt_ci(boot_dynamic.get('test', {}).get('mean_auc', {}))}."
    )
    if any("low_controls_test_h24" == warning or "low_cases_valid_h6" == warning for warning in warnings):
        bullets.append("Los horizontes más extremos siguen siendo frágiles: el soporte de casos/controles en h6 valid y h24 test no alcanza un nivel cómodo para venderlos como KPI principal.")
    return bullets


def _fmt_metric(value: object) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "nan"
    return f"{float(numeric):.4f}"


def _fmt_ci(payload: dict[str, object]) -> str:
    lower = pd.to_numeric(payload.get("ci_lower"), errors="coerce")
    upper = pd.to_numeric(payload.get("ci_upper"), errors="coerce")
    if pd.isna(lower) or pd.isna(upper):
        return "[nan, nan]"
    return f"[{float(lower):.4f}, {float(upper):.4f}]"


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


def _load_json_if_exists(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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