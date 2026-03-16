import unittest

import pandas as pd

import localizate.censo_geospatial as cgeo
from localizate.censo_geospatial import CensoGeospatialConfig, transform_locales_geospatial_frame


class CensoGeospatialTests(unittest.TestCase):
    def test_transition_policy_skip_flags_rows_for_review(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "coord_crs_status": "transition_2017_09",
                    "x_utm_best": 440000.0,
                    "y_utm_best": 4470000.0,
                }
            ]
        )

        transformed = transform_locales_geospatial_frame(
            frame,
            config=CensoGeospatialConfig(transition_policy="skip", h3_resolution=10),
        )

        self.assertEqual(transformed.iloc[0]["coord_transform_status"], "transition_requires_review")
        self.assertTrue(pd.isna(transformed.iloc[0]["lat_wgs84"]))
        self.assertTrue(pd.isna(transformed.iloc[0]["h3_cell"]))

    def test_assume_etrs89_uses_transform_and_h3_pipeline(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "coord_crs_status": "etrs89_utm30",
                    "x_utm_best": 440000.0,
                    "y_utm_best": 4470000.0,
                },
                {
                    "coord_crs_status": "transition_2017_09",
                    "x_utm_best": 441000.0,
                    "y_utm_best": 4471000.0,
                },
            ]
        )

        original_transform = cgeo._utm_to_wgs84
        original_h3 = cgeo._latlon_to_h3
        try:
            cgeo._utm_to_wgs84 = lambda x, y, source_epsg: (pd.Series([1.0] * len(x), index=x.index), pd.Series([2.0] * len(y), index=y.index))
            cgeo._latlon_to_h3 = lambda lat, lon, resolution: pd.Series([f"h3-{resolution}"] * len(lat), index=lat.index)

            transformed = transform_locales_geospatial_frame(
                frame,
                config=CensoGeospatialConfig(transition_policy="assume_etrs89", h3_resolution=9),
            )

            self.assertEqual(list(transformed["coord_transform_status"]), ["transformed", "transformed_transition_assume_etrs89"])
            self.assertEqual(list(transformed["h3_cell"]), ["h3-9", "h3-9"])
            self.assertEqual(list(transformed["h3_resolution"]), [9, 9])
        finally:
            cgeo._utm_to_wgs84 = original_transform
            cgeo._latlon_to_h3 = original_h3


if __name__ == "__main__":
    unittest.main()
