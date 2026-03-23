from __future__ import annotations

import unittest

import pandas as pd

from localizate.survival_baseline import (
    apply_training_policies,
    assign_temporal_split,
    assign_temporal_split_adaptive,
    assign_temporal_split_event_quantiles,
    binary_auc,
    binary_brier,
    compute_horizon_metrics,
    evaluate_quality_gate,
    sampled_concordance_index,
    score_to_probability,
)


class SurvivalBaselineTests(unittest.TestCase):
    def test_assign_temporal_split(self) -> None:
        periods = pd.Series(["2022-12", "2023-01", "2024-11", "2025-01"], dtype="string")
        split = assign_temporal_split(periods)
        self.assertEqual(split.tolist(), ["train", "valid", "valid", "test"])

    def test_apply_training_policies_excludes_transition_and_imputes_renta(self) -> None:
        abt = pd.DataFrame(
            {
                "id_local": [1, 2, 3],
                "first_seen_period": ["2026-01", "2023-04", "2024-02"],
                "coord_transform_status_start": ["transition_requires_review", "transformed", "transformed"],
                "section_key_start": ["01001", "01002", "02001"],
                "renta_best_eur_start": [None, 1200.0, None],
            }
        )
        result = apply_training_policies(abt, transition_policy="exclude_transition", renta_max_year=2023)
        dataset = result["dataset"]

        self.assertEqual(len(dataset), 2)
        self.assertTrue((dataset["coord_transform_status_start"] != "transition_requires_review").all())
        self.assertTrue(dataset["renta_effective_eur"].notna().all())

    def test_sampled_concordance_index_returns_valid_range(self) -> None:
        duration = pd.Series([2, 4, 6, 8])
        event = pd.Series([1, 1, 1, 0])
        risk = pd.Series([0.9, 0.7, 0.3, 0.1])
        c_index = sampled_concordance_index(duration, event, risk, max_pairs=5000, seed=1)
        self.assertGreaterEqual(c_index, 0.0)
        self.assertLessEqual(c_index, 1.0)

    def test_assign_temporal_split_adaptive_creates_all_splits(self) -> None:
        df = pd.DataFrame(
            {
                "first_seen_period": ["2022-01", "2022-02", "2023-01", "2023-02", "2024-01", "2024-02"],
                "event_observed": [0, 1, 0, 1, 0, 1],
            }
        )
        split = assign_temporal_split_adaptive(
            df,
            period_col="first_seen_period",
            event_col="event_observed",
            min_events_valid=1,
            min_events_test=1,
            min_rows_valid=1,
            min_rows_test=1,
        )
        self.assertTrue((split == "train").any())
        self.assertTrue((split == "valid").any())
        self.assertTrue((split == "test").any())

    def test_assign_temporal_split_adaptive_never_leaves_train_empty(self) -> None:
        df = pd.DataFrame(
            {
                "first_seen_period": [
                    "2015-01",
                    "2016-01",
                    "2017-01",
                    "2018-01",
                    "2019-01",
                    "2020-01",
                    "2021-01",
                    "2022-01",
                    "2023-01",
                    "2024-01",
                    "2025-01",
                ],
                "event_observed": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            }
        )
        split = assign_temporal_split_adaptive(
            df,
            period_col="first_seen_period",
            event_col="event_observed",
            min_events_valid=3,
            min_events_test=3,
            min_rows_valid=3,
            min_rows_test=3,
        )
        self.assertTrue((split == "train").any())
        self.assertTrue((split == "valid").any())
        self.assertTrue((split == "test").any())

    def test_quality_gate_detects_missing_events_or_nan_metrics(self) -> None:
        metrics = {
            "split_event_counts": {"train": 10, "valid": 2, "test": 0},
            "c_index": {"train": 0.6, "valid": 0.55, "test": float("nan")},
        }
        gate = evaluate_quality_gate(metrics)
        self.assertEqual(gate["status"], "review_required")

    def test_assign_temporal_split_event_quantiles_uses_event_periods(self) -> None:
        df = pd.DataFrame(
            {
                "first_seen_period": ["2022-01", "2022-02", "2023-01", "2023-02", "2024-01", "2025-01"],
                "event_observed": [0, 1, 0, 1, 1, 0],
            }
        )
        split = assign_temporal_split_event_quantiles(
            df,
            period_col="first_seen_period",
            event_col="event_observed",
            q_valid=0.5,
            q_test=0.8,
        )
        self.assertTrue((split == "valid").any())
        self.assertTrue((split == "test").any())

    def test_binary_auc_and_brier_return_finite(self) -> None:
        y = pd.Series([0, 0, 1, 1])
        score = pd.Series([0.1, 0.3, 0.7, 0.9])
        prob = score_to_probability(score)
        auc = binary_auc(y, score)
        brier = binary_brier(y, prob)
        self.assertGreaterEqual(auc, 0.0)
        self.assertLessEqual(auc, 1.0)
        self.assertGreaterEqual(brier, 0.0)

    def test_compute_horizon_metrics_structure(self) -> None:
        df = pd.DataFrame(
            {
                "split": ["train", "train", "valid", "test"],
                "duration_months": [3, 20, 8, 12],
                "event_observed": [1, 0, 1, 1],
                "risk_score": [0.8, 0.1, 0.6, 0.7],
                "risk_probability_12m": [0.7, 0.2, 0.6, 0.65],
            }
        )
        metrics = compute_horizon_metrics(
            df,
            split_col="split",
            duration_col="duration_months",
            event_col="event_observed",
            score_col="risk_score",
            prob_col="risk_probability_12m",
            horizons=(6, 12),
        )
        self.assertIn("train", metrics)
        self.assertIn("h6", metrics["train"])


if __name__ == "__main__":
    unittest.main()
