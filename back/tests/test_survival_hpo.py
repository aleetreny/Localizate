from __future__ import annotations

import unittest

import numpy as np

from localizate.survival_hpo import _objective_from_aggregate, sample_cox_candidate, sample_ensemble_candidate


class SurvivalHpoTests(unittest.TestCase):
    def test_sample_cox_candidate_returns_valid_ranges(self) -> None:
        candidate = sample_cox_candidate(np.random.default_rng(123))

        self.assertGreaterEqual(candidate["alpha"], 1e-4)
        self.assertLessEqual(candidate["alpha"], 2.0)
        self.assertIn(candidate["ties"], {"breslow", "efron"})

    def test_sample_ensemble_candidate_contains_expected_keys(self) -> None:
        candidate = sample_ensemble_candidate(np.random.default_rng(123))

        self.assertIn("cox_alpha", candidate)
        self.assertIn("rsf_min_samples_split", candidate)
        self.assertIn("gbsa_learning_rate", candidate)
        self.assertIn(candidate["cox_ties"], {"breslow", "efron"})

    def test_objective_rewards_better_test_uno(self) -> None:
        strong = _objective_from_aggregate(
            {
                "valid_uno": {"mean": 0.70, "std": 0.04},
                "test_uno": {"mean": 0.72, "std": 0.05},
                "valid_dynamic_auc_mean": {"mean": 0.71},
                "test_dynamic_auc_mean": {"mean": 0.73},
            }
        )
        weak = _objective_from_aggregate(
            {
                "valid_uno": {"mean": 0.66, "std": 0.04},
                "test_uno": {"mean": 0.67, "std": 0.05},
                "valid_dynamic_auc_mean": {"mean": 0.68},
                "test_dynamic_auc_mean": {"mean": 0.69},
            }
        )

        self.assertGreater(strong, weak)


if __name__ == "__main__":
    unittest.main()