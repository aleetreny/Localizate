from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from localizate.section_geography import load_section_geodataframe


class SectionGeometryFallbackTests(unittest.TestCase):
    def test_load_section_geodataframe_uses_frontend_geojson_when_raw_is_missing(self) -> None:
        payload = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[-3.71, 40.41], [-3.70, 40.41], [-3.70, 40.42], [-3.71, 40.41]]],
                    },
                    "properties": {
                        "section_key": "01001",
                        "district_code": "01",
                        "district_name": "Centro",
                        "barrio_code": "001",
                        "barrio_name": "Palacio",
                    },
                }
            ],
        }

        with TemporaryDirectory() as tmp_dir:
            fallback_path = Path(tmp_dir) / "geometry.geojson"
            fallback_path.write_text(json.dumps(payload), encoding="utf-8")

            with patch("localizate.section_geography.FRONTEND_SECTION_GEOJSON_PATH", fallback_path), patch(
                "localizate.section_geography.load_raw_manifest",
                side_effect=FileNotFoundError("missing raw manifest"),
            ):
                gdf = load_section_geodataframe()

        self.assertIn("COD_SECCIO", gdf.columns)
        self.assertIn("COD_DIS", gdf.columns)
        self.assertEqual(str(gdf.iloc[0]["COD_SECCIO"]), "01001")
        self.assertEqual(str(gdf.iloc[0]["COD_DIS"]), "01")


if __name__ == "__main__":
    unittest.main()
