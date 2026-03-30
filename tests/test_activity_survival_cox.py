from __future__ import annotations

import unittest

import pandas as pd

from localizate.activity_survival_cox import fit_activity_survival_cox_scorer


def make_abt_row(
    *,
    first_seen_period: str,
    activity_category_code_start: str,
    duration_months: float,
    event_observed: int,
    renta_best_eur_start: float,
    share_foreign_start: float,
) -> dict[str, object]:
    return {
        "first_seen_period": first_seen_period,
        "duration_months": duration_months,
        "event_observed": event_observed,
        "section_key_start": "28079",
        "h3_cell_start": "abc123",
        "coord_transform_status_start": "ok",
        "padron_lag_months_start": 0.0,
        "total_population_start": 1200.0,
        "age_mean_start": 42.0,
        "renta_best_eur_start": renta_best_eur_start,
        "share_foreign_start": share_foreign_start,
        "share_male_start": 0.48,
        "share_age_00_14_start": 0.12,
        "share_age_15_29_start": 0.16,
        "share_age_30_44_start": 0.24,
        "share_age_45_64_start": 0.28,
        "share_age_65_plus_start": 0.20,
        "population_density_km2_start": 14000.0,
        "total_population_delta_12m_start": 10.0,
        "share_foreign_delta_12m_start": 0.01,
        "share_age_15_29_delta_12m_start": 0.00,
        "population_density_km2_delta_12m_start": 50.0,
        "renta_best_eur_delta_12m_start": 120.0,
        "n_divisions_start": 1.0,
        "n_epigrafes_start": 1.0,
        "n_activity_categories_start": 1.0,
        "activity_category_code_start": activity_category_code_start,
        "geometry_available_start": 1.0,
        "metro_distance_m_start": 180.0,
        "metro_access_count_500m_start": 2.0,
        "metro_access_count_1000m_start": 4.0,
        "missing_metro_distance_start": 0.0,
    }


class ActivitySurvivalCoxTests(unittest.TestCase):
    def test_scorer_returns_activity_sensitive_survival_outputs(self) -> None:
        periods = pd.date_range("2018-01-01", periods=18, freq="4MS").strftime("%Y-%m").tolist()
        rows: list[dict[str, object]] = []

        for period, duration, event in zip(periods[:6], [8, 10, 12, 14, 16, 18], [1, 1, 1, 1, 0, 1]):
            rows.append(
                make_abt_row(
                    first_seen_period=period,
                    activity_category_code_start="bar_cafe",
                    duration_months=duration,
                    event_observed=event,
                    renta_best_eur_start=12000.0,
                    share_foreign_start=0.18,
                )
            )

        for period, duration, event in zip(periods[6:12], [28, 32, 36, 40, 44, 48], [0, 0, 0, 0, 0, 1]):
            rows.append(
                make_abt_row(
                    first_seen_period=period,
                    activity_category_code_start="pharmacy_optics",
                    duration_months=duration,
                    event_observed=event,
                    renta_best_eur_start=18000.0,
                    share_foreign_start=0.10,
                )
            )

        for period, duration, event in zip(periods[12:], [18, 20, 24, 26, 30, 34], [1, 0, 1, 0, 0, 0]):
            rows.append(
                make_abt_row(
                    first_seen_period=period,
                    activity_category_code_start="restaurant",
                    duration_months=duration,
                    event_observed=event,
                    renta_best_eur_start=15000.0,
                    share_foreign_start=0.14,
                )
            )

        abt = pd.DataFrame(rows)
        scorer = fit_activity_survival_cox_scorer(
            abt=abt,
            min_events_valid=1,
            min_events_test=1,
            min_rows_valid=2,
            min_rows_test=2,
        )

        candidates = pd.DataFrame(
            [
                make_abt_row(
                    first_seen_period="2024-01",
                    activity_category_code_start="bar_cafe",
                    duration_months=24.0,
                    event_observed=0,
                    renta_best_eur_start=16000.0,
                    share_foreign_start=0.12,
                ),
                make_abt_row(
                    first_seen_period="2024-01",
                    activity_category_code_start="pharmacy_optics",
                    duration_months=24.0,
                    event_observed=0,
                    renta_best_eur_start=16000.0,
                    share_foreign_start=0.12,
                ),
            ]
        )

        scored = scorer.score_frame(candidates)

        self.assertIn("risk_index", scored.columns)
        self.assertIn("activity_fit_percentile", scored.columns)
        self.assertIn("activity_relative_weight", scored.columns)
        self.assertIn("activity_specificity", scored.columns)
        self.assertIn("activity_effective_weight", scored.columns)
        self.assertIn("activity_context_index", scored.columns)
        self.assertIn("survival_12m", scored.columns)
        self.assertIn("survival_24m", scored.columns)
        self.assertTrue(((scored["risk_index"] >= 0.0) & (scored["risk_index"] <= 1.0)).all())
        self.assertTrue(((scored["activity_fit_percentile"] >= 0.0) & (scored["activity_fit_percentile"] <= 1.0)).all())
        self.assertTrue(((scored["activity_relative_weight"] >= 0.3) & (scored["activity_relative_weight"] <= 0.7)).all())
        self.assertTrue(((scored["activity_specificity"] >= 0.0) & (scored["activity_specificity"] <= 1.0)).all())
        self.assertTrue(((scored["activity_effective_weight"] >= 0.35) & (scored["activity_effective_weight"] <= 0.92)).all())
        self.assertTrue(((scored["activity_context_index"] >= 0.0) & (scored["activity_context_index"] <= 1.0)).all())
        self.assertTrue(((scored["survival_12m"] >= 0.0) & (scored["survival_12m"] <= 1.0)).all())
        self.assertTrue(((scored["survival_24m"] >= 0.0) & (scored["survival_24m"] <= 1.0)).all())
        self.assertTrue(((scored["risk_percentile"] >= 0.0) & (scored["risk_percentile"] <= 1.0)).all())
        self.assertGreater(scored.iloc[0]["activity_relative_weight"], scored.iloc[1]["activity_relative_weight"])
        self.assertGreater(scored.iloc[0]["risk_cox"], scored.iloc[1]["risk_cox"])
        self.assertGreater(scored.iloc[0]["risk_index"], scored.iloc[1]["risk_index"])
        self.assertLess(scored.iloc[0]["survival_24m"], scored.iloc[1]["survival_24m"])


if __name__ == "__main__":
    unittest.main()