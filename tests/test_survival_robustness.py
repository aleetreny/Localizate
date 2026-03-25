from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from localizate.survival_robustness import (
    _bootstrap_sample_frame,
    _build_robustness_warnings,
    _compare_against_canonical_metrics,
)


class SurvivalRobustnessTests(unittest.TestCase):
    def test_bootstrap_sample_frame_preserves_rows_and_events(self) -> None:
        frame = pd.DataFrame(
            {
                "event_observed": [1, 1, 0, 0, 0, 0],
                "duration_months": [1, 2, 3, 4, 5, 6],
            }
        )
        rng = np.random.default_rng(7)

        sampled = _bootstrap_sample_frame(frame, rng=rng, sample_rows=6)

        self.assertEqual(len(sampled), 6)
        self.assertGreaterEqual(int(sampled["event_observed"].sum()), 1)

    def test_compare_against_canonical_metrics_detects_exact_match(self) -> None:
        canonical = {
            "uno_c_index": {
                "valid": {"uno_c_index": 0.61},
                "test": {"uno_c_index": 0.59},
            },
            "dynamic_auc": {
                "valid": {"mean_auc": 0.70},
                "test": {"mean_auc": 0.68},
            },
        }
        recomputed_uno = {
            "valid": {"uno_c_index": 0.61},
            "test": {"uno_c_index": 0.59},
        }
        recomputed_auc = {
            "valid": {"mean_auc": 0.70},
            "test": {"mean_auc": 0.68},
        }

        comparison = _compare_against_canonical_metrics(canonical, recomputed_uno, recomputed_auc)

        self.assertTrue(comparison["matches_training_metrics"])

    def test_build_robustness_warnings_flags_fragile_horizon_support(self) -> None:
        warnings = _build_robustness_warnings(
            dynamic_auc={
                "valid": {"horizons": {"h6": {"supported": True, "cases": 5, "controls": 2000}}},
                "test": {"horizons": {"h24": {"supported": True, "cases": 200, "controls": 55}}},
            },
            bootstrap_uno={
                "valid": {"success_rate": 1.0, "ci_width": 0.10},
                "test": {"success_rate": 1.0, "ci_width": 0.10},
            },
            bootstrap_dynamic_auc={
                "valid": {"mean_auc": {"success_rate": 1.0, "ci_width": 0.10}},
                "test": {"mean_auc": {"success_rate": 1.0, "ci_width": 0.10}},
            },
            comparison={"matches_training_metrics": True},
        )

        self.assertIn("low_cases_valid_h6", warnings)
        self.assertIn("low_controls_test_h24", warnings)


if __name__ == "__main__":
    unittest.main()