from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
from sksurv.util import Surv

from localizate.survival_canonical import (
    _ensemble_rank_score,
    _sample_training_indices,
    _supported_eval_times,
    evaluate_canonical_quality_gate,
)
from localizate.survival_robustness import (
    _bootstrap_payload,
    _resolve_robustness_status,
)


class SurvivalCanonicalTests(unittest.TestCase):
    def test_ensemble_rank_score_range(self) -> None:
        frame = pd.DataFrame(
            {
                "risk_cox": [0.1, 0.2, 0.3],
                "risk_rsf": [0.2, 0.1, 0.4],
                "risk_gbsa": [0.05, 0.2, 0.5],
            }
        )
        score = _ensemble_rank_score(frame)
        self.assertTrue((score >= 0).all())
        self.assertTrue((score <= 1).all())

    def test_supported_eval_times_filters_unsupported_horizons(self) -> None:
        reference = Surv.from_arrays(
            event=np.array([True, True, False, True]),
            time=np.array([8.0, 14.0, 20.0, 30.0]),
        )
        evaluation = Surv.from_arrays(
            event=np.array([True, False, True, False]),
            time=np.array([4.0, 10.0, 18.0, 22.0]),
        )

        supported = _supported_eval_times(reference, evaluation, requested_times=(6.0, 12.0, 24.0))

        self.assertEqual(supported.tolist(), [6.0, 12.0])

    def test_canonical_quality_gate_returns_pass_with_caveats_for_rare_events(self) -> None:
        gate = evaluate_canonical_quality_gate(
            split_event_counts={"train": 100, "valid": 4, "test": 6},
            uno_c_index={
                "train": {"uno_c_index": 0.55},
                "valid": {"uno_c_index": 0.58},
                "test": {"uno_c_index": 0.54},
            },
            dynamic_auc={
                split_name: {
                    "mean_auc": 0.57,
                    "horizons": {
                        "h6": {"supported": True},
                        "h12": {"supported": True},
                        "h24": {"supported": True},
                    },
                }
                for split_name in ("train", "valid", "test")
            },
            integrated_brier={
                model_name: {
                    split_name: {"ibs": 0.19}
                    for split_name in ("train", "valid", "test")
                }
                for model_name in ("cox", "rsf", "gbsa")
            },
        )

        self.assertEqual(gate["status"], "pass_with_caveats")
        self.assertIn("very_low_validation_events", gate["warnings"])
        self.assertIn("very_low_test_events", gate["warnings"])

    def test_canonical_quality_gate_requires_finite_robust_metrics(self) -> None:
        gate = evaluate_canonical_quality_gate(
            split_event_counts={"train": 100, "valid": 25, "test": 25},
            uno_c_index={
                "train": {"uno_c_index": 0.55},
                "valid": {"uno_c_index": float("nan")},
                "test": {"uno_c_index": 0.54},
            },
            dynamic_auc={
                split_name: {
                    "mean_auc": 0.57,
                    "horizons": {
                        "h6": {"supported": True},
                        "h12": {"supported": True},
                        "h24": {"supported": True},
                    },
                }
                for split_name in ("train", "valid", "test")
            },
            integrated_brier={
                model_name: {
                    split_name: {"ibs": 0.19}
                    for split_name in ("train", "valid", "test")
                }
                for model_name in ("cox", "rsf", "gbsa")
            },
        )

        self.assertEqual(gate["status"], "review_required")

    def test_sample_training_indices_keeps_all_events_with_limit(self) -> None:
        frame = pd.DataFrame(
            {
                "event_observed": [1, 0, 0, 1, 0, 0, 0, 0],
            }
        )

        idx = _sample_training_indices(frame, max_rows=4, seed=7)

        self.assertEqual(len(idx), 4)
        self.assertIn(0, idx.tolist())
        self.assertIn(3, idx.tolist())

    def test_bootstrap_payload_reports_confidence_interval(self) -> None:
        payload = _bootstrap_payload([0.50, 0.55, 0.60, 0.65], iterations=4, sample_rows=100, skipped=0)

        self.assertAlmostEqual(payload["estimate"], 0.575)
        self.assertGreater(payload["ci_upper"], payload["ci_lower"])
        self.assertEqual(payload["iterations_successful"], 4)

    def test_resolve_robustness_status_returns_caveats_for_wide_intervals(self) -> None:
        status = _resolve_robustness_status(["wide_uno_ci_test"], {"matches_training_metrics": True})
        self.assertEqual(status, "pass_with_caveats")


if __name__ == "__main__":
    unittest.main()
