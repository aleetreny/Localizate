from __future__ import annotations

import unittest

import pandas as pd

from localizate.activity_horizon_logistic import (
    eligible_horizon_mask,
    horizon_binary_target,
    select_logistic_horizons,
)


class ActivityHorizonLogisticTests(unittest.TestCase):
    def test_eligible_horizon_mask_excludes_early_censored_rows(self) -> None:
        frame = pd.DataFrame(
            {
                "duration_months": [6, 6, 18, 24],
                "event_observed": [0, 1, 0, 1],
            }
        )

        mask = eligible_horizon_mask(frame, horizon=12)

        self.assertEqual(mask.tolist(), [False, True, True, True])

    def test_horizon_binary_target_flags_events_up_to_horizon(self) -> None:
        frame = pd.DataFrame(
            {
                "duration_months": [6, 12, 18, 24],
                "event_observed": [1, 1, 0, 1],
            }
        )

        target = horizon_binary_target(frame, horizon=12)

        self.assertEqual(target.tolist(), [1, 1, 0, 0])

    def test_select_logistic_horizons_keeps_supported_candidates(self) -> None:
        support_summary = {
            "h9": {"valid": {"cases": 13, "controls": 2600}, "test": {"cases": 96, "controls": 50000}},
            "h12": {"valid": {"cases": 18, "controls": 2600}, "test": {"cases": 159, "controls": 50000}},
            "h15": {"valid": {"cases": 19, "controls": 2600}, "test": {"cases": 214, "controls": 49000}},
            "h18": {"valid": {"cases": 23, "controls": 2600}, "test": {"cases": 235, "controls": 302}},
            "h24": {"valid": {"cases": 35, "controls": 2600}, "test": {"cases": 238, "controls": 81}},
        }

        selected = select_logistic_horizons(
            support_summary,
            min_valid_cases=15,
            min_valid_controls=1000,
            min_test_cases=100,
            min_test_controls=200,
            max_horizons=3,
        )

        self.assertEqual(selected, (12, 15, 18))


if __name__ == "__main__":
    unittest.main()