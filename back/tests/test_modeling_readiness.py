from __future__ import annotations

import unittest

from localizate.modeling_readiness import (
    _canonical_gate_status_is_acceptable,
    _extract_bootstrap_ci_width,
    _robustness_status_is_acceptable,
    _resolve_readiness_status,
    _to_jsonable,
)


class ModelingReadinessTests(unittest.TestCase):
    def test_to_jsonable_converts_nested_structures(self) -> None:
        payload = {"a": [1, 2, {"b": True}]}
        converted = _to_jsonable(payload)
        self.assertEqual(converted["a"][2]["b"], True)

    def test_canonical_gate_status_accepts_caveats(self) -> None:
        self.assertTrue(_canonical_gate_status_is_acceptable("pass"))
        self.assertTrue(_canonical_gate_status_is_acceptable("pass_with_caveats"))
        self.assertFalse(_canonical_gate_status_is_acceptable("review_required"))

    def test_robustness_status_accepts_missing_and_caveats(self) -> None:
        self.assertTrue(_robustness_status_is_acceptable("missing"))
        self.assertTrue(_robustness_status_is_acceptable("pass_with_caveats"))
        self.assertFalse(_robustness_status_is_acceptable("review_required"))

    def test_extract_bootstrap_ci_width_reads_uno_and_dynamic_auc(self) -> None:
        payload = {
            "uno_c_index": {"valid": {"ci_width": 0.12}},
            "dynamic_auc": {"valid": {"mean_auc": {"ci_width": 0.21}}},
        }

        self.assertEqual(_extract_bootstrap_ci_width(payload, split_name="valid", metric_key="uno_c_index"), 0.12)
        self.assertEqual(_extract_bootstrap_ci_width(payload, split_name="valid", metric_key="dynamic_auc"), 0.21)

    def test_resolve_readiness_status_uses_canonical_gate(self) -> None:
        checks = {
            "abt_non_empty": True,
            "events_minimum": True,
            "event_rate_minimum": True,
            "h3_coverage_minimum": True,
            "canonical_metrics_available": True,
            "canonical_quality_gate_acceptable": True,
        }

        status = _resolve_readiness_status(checks, ["very_low_validation_events"], "pass_with_caveats")

        self.assertEqual(status, "ready_with_caveats")


if __name__ == "__main__":
    unittest.main()
