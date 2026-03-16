from __future__ import annotations

import unittest

from localizate.modeling_readiness import _to_jsonable


class ModelingReadinessTests(unittest.TestCase):
    def test_to_jsonable_converts_nested_structures(self) -> None:
        payload = {"a": [1, 2, {"b": True}]}
        converted = _to_jsonable(payload)
        self.assertEqual(converted["a"][2]["b"], True)


if __name__ == "__main__":
    unittest.main()
