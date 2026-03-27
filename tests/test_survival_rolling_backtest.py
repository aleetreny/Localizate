from __future__ import annotations

import unittest

import pandas as pd

from localizate.survival_rolling_backtest import (
    _next_period,
    _weighted_rank_score,
    build_walk_forward_folds,
    build_variant_scores,
    derive_event_quantile_cutoffs,
)


class SurvivalRollingBacktestTests(unittest.TestCase):
    def test_next_period_rolls_year_boundary(self) -> None:
        self.assertEqual(_next_period("2024-12"), "2025-01")

    def test_derive_event_quantile_cutoffs_appends_end_period(self) -> None:
        frame = pd.DataFrame(
            {
                "first_seen_period": ["2020-01", "2020-02", "2020-03", "2020-04"],
                "event_observed": [1, 0, 1, 0],
            }
        )

        cutoffs = derive_event_quantile_cutoffs(frame, quantiles=(0.0, 0.5, 1.0))

        self.assertEqual(cutoffs, ("2020-01", "2020-03", "2020-05"))

    def test_build_walk_forward_folds_filters_low_event_windows(self) -> None:
        frame = pd.DataFrame(
            {
                "first_seen_period": [
                    "2020-01", "2020-02", "2020-03", "2020-04", "2020-05", "2020-06", "2020-07", "2020-08",
                ],
                "event_observed": [1, 1, 1, 1, 1, 1, 0, 0],
            }
        )

        folds = build_walk_forward_folds(
            frame,
            cutoff_periods=("2020-03", "2020-05", "2020-07", "2020-09"),
            min_valid_events=2,
            min_test_events=2,
        )

        self.assertEqual(len(folds), 1)
        self.assertEqual(folds[0]["fold_id"], "fold_1")
        self.assertEqual(folds[0]["valid_events"], 2)
        self.assertEqual(folds[0]["test_events"], 2)

    def test_weighted_rank_score_respects_weighted_average_of_ranks(self) -> None:
        frame = pd.DataFrame(
            {
                "risk_cox": [0.1, 0.2, 0.3],
                "risk_rsf": [0.3, 0.2, 0.1],
                "risk_gbsa": [0.2, 0.1, 0.3],
            }
        )

        score = _weighted_rank_score(frame, weights={"risk_cox": 0.3, "risk_rsf": 0.1, "risk_gbsa": 0.6})

        self.assertEqual(score.round(6).tolist(), [0.6, 0.466667, 0.933333])

    def test_build_variant_scores_includes_expected_variants(self) -> None:
        frame = pd.DataFrame(
            {
                "risk_cox": [0.1, 0.2],
                "risk_rsf": [0.2, 0.1],
                "risk_gbsa": [0.3, 0.4],
            }
        )

        scores = build_variant_scores(frame)

        self.assertIn("gbsa_only", scores)
        self.assertIn("ensemble_all_rank", scores)
        self.assertIn("ensemble_weighted_rank", scores)
        self.assertEqual(len(scores["gbsa_only"]), 2)


if __name__ == "__main__":
    unittest.main()