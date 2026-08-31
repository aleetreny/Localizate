from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

import pandas as pd


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from scripts.validate_opportunity_refresh_outputs import validate_outputs  # noqa: E402


class ValidateOpportunityRefreshOutputsTests(unittest.TestCase):
    def test_validate_outputs_accepts_frontend_subset_of_fresh_snapshot(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            snapshot_csv = root / "snapshot.csv"
            summary_json = root / "summary.json"
            frontend_json = root / "frontend.json"

            pd.DataFrame(
                [
                    {
                        "listing_id": "1",
                        "listing_key": "venta:1",
                        "listing_url": "https://www.locales.es/madrid/venta/local1#offerType=1",
                        "operation": "venta",
                    },
                    {
                        "listing_id": "2",
                        "listing_key": "alquiler:2",
                        "listing_url": "https://www.locales.es/madrid/alquiler-traspaso/local2#offerType=2",
                        "operation": "alquiler",
                    },
                ]
            ).to_csv(snapshot_csv, index=False)
            summary_json.write_text(json.dumps({"status": "updated", "listing_count": 2}), encoding="utf-8")
            frontend_json.write_text(
                json.dumps(
                    {
                        "stats": {"selected_listings": 1},
                        "points": [
                            {
                                "listing_id": "2",
                                "listing_url": "https://www.locales.es/madrid/alquiler-traspaso/local2#offerType=2",
                                "operation": "alquiler",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = validate_outputs(
                snapshot_csv=snapshot_csv,
                summary_json=summary_json,
                frontend_json=frontend_json,
            )

        self.assertEqual(result["snapshot_listings"], 2)
        self.assertEqual(result["frontend_points"], 1)

    def test_validate_outputs_rejects_stale_frontend_url(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            snapshot_csv = root / "snapshot.csv"
            summary_json = root / "summary.json"
            frontend_json = root / "frontend.json"

            pd.DataFrame(
                [
                    {
                        "listing_id": "1",
                        "listing_key": "venta:1",
                        "listing_url": "https://www.locales.es/madrid/venta/local1",
                        "operation": "venta",
                    }
                ]
            ).to_csv(snapshot_csv, index=False)
            summary_json.write_text(json.dumps({"status": "updated", "listing_count": 1}), encoding="utf-8")
            frontend_json.write_text(
                json.dumps(
                    {
                        "stats": {"selected_listings": 1},
                        "points": [
                            {
                                "listing_id": "9",
                                "listing_url": "https://www.locales.es/madrid/venta/local9",
                                "operation": "venta",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "not present in the freshly crawled snapshot"):
                validate_outputs(
                    snapshot_csv=snapshot_csv,
                    summary_json=summary_json,
                    frontend_json=frontend_json,
                )

    def test_validate_outputs_rejects_skipped_refresh(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            snapshot_csv = root / "snapshot.csv"
            summary_json = root / "summary.json"
            frontend_json = root / "frontend.json"
            summary_json.write_text(json.dumps({"status": "skipped"}), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "not updated"):
                validate_outputs(
                    snapshot_csv=snapshot_csv,
                    summary_json=summary_json,
                    frontend_json=frontend_json,
                )


if __name__ == "__main__":
    unittest.main()
