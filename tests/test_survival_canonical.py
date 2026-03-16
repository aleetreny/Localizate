from __future__ import annotations

import unittest

import pandas as pd

from localizate.survival_canonical import _ensemble_rank_score


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


if __name__ == "__main__":
    unittest.main()
