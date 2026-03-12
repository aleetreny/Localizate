from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from localizate.section_geography import read_dbf_table
from localizate.socioeconomics import (
    aggregate_padron_section_snapshot,
    attach_renta_features,
    attach_section_geography_features,
    normalize_padron_snapshot,
)


def _build_minimal_dbf(path: Path) -> None:
    fields = [
        ("COD_SECCIO", "C", 5, 0),
        ("Area", "F", 12, 2),
    ]
    header_length = 32 + len(fields) * 32 + 1
    record_length = 1 + sum(length for _, _, length, _ in fields)

    header = bytearray(32)
    header[0] = 0x03
    header[1:4] = bytes([26, 3, 9])
    header[4:8] = (1).to_bytes(4, "little")
    header[8:10] = header_length.to_bytes(2, "little")
    header[10:12] = record_length.to_bytes(2, "little")

    field_descriptors = bytearray()
    for name, field_type, length, decimal_count in fields:
        descriptor = bytearray(32)
        descriptor[: len(name)] = name.encode("ascii")
        descriptor[11] = ord(field_type)
        descriptor[16] = length
        descriptor[17] = decimal_count
        field_descriptors.extend(descriptor)

    record = bytearray()
    record.extend(b" ")
    record.extend(b"01001")
    record.extend(b"     1234.56")

    path.write_bytes(bytes(header) + bytes(field_descriptors) + b"\r" + bytes(record) + b"\x1a")


class SectionPanelTests(unittest.TestCase):
    def test_read_dbf_table_parses_char_and_float_fields(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sample.dbf"
            _build_minimal_dbf(path)

            frame = read_dbf_table(path)

            self.assertEqual(list(frame.columns), ["COD_SECCIO", "Area"])
            self.assertEqual(frame.iloc[0]["COD_SECCIO"], "01001")
            self.assertAlmostEqual(float(frame.iloc[0]["Area"]), 1234.56, places=2)

    def test_normalize_padron_snapshot_handles_old_columns_and_topcoded_age(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "COD_DISTRITO": "1",
                    "DESC_DISTRITO": "CENTRO",
                    "COD_BARRIO": "2",
                    "DESC_BARRIO": "EMBAJADORES",
                    "COD_DIST_SECCION": "1042",
                    "COD_SECCION": "42",
                    "COD_EDAD_INT": "100 o +",
                    "EspanolesHombres": 3,
                    "EspanolesMujeres": 4,
                    "ExtranjerosHombres": 1,
                    "ExtranjerosMujeres": 2,
                }
            ]
        )

        normalized = normalize_padron_snapshot(
            frame,
            period="2023-01",
            source_relative_path="padron/test.csv",
            read_metadata=type("Meta", (), {"encoding": "utf-8-sig", "delimiter": ";", "reader_mode": "pandas_default"})(),
        )

        self.assertEqual(normalized.iloc[0]["section_key"], "01042")
        self.assertEqual(int(normalized.iloc[0]["age_value"]), 100)
        self.assertTrue(bool(normalized.iloc[0]["age_is_topcoded"]))
        self.assertEqual(int(normalized.iloc[0]["total_population"]), 10)
        self.assertTrue(pd.isna(normalized.iloc[0]["padron_fx_carga"]))

    def test_aggregate_padron_section_snapshot_builds_demographic_features(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "padron_period": "2023-01",
                    "padron_year": 2023,
                    "padron_month": 1,
                    "padron_date": "2023-01-01",
                    "section_key": "01042",
                    "district_code": "01",
                    "district_name": "CENTRO",
                    "barrio_code": "002",
                    "barrio_name": "EMBAJADORES",
                    "section_code": "042",
                    "age_is_topcoded": False,
                    "spanish_male": 2,
                    "spanish_female": 2,
                    "foreign_male": 1,
                    "foreign_female": 1,
                    "spanish_total": 4,
                    "foreign_total": 2,
                    "male_total": 3,
                    "female_total": 3,
                    "total_population": 6,
                    "age_known_population": 6,
                    "age_weighted_population": 60,
                    "age_00_14_total": 6,
                    "age_15_29_total": 0,
                    "age_30_44_total": 0,
                    "age_45_64_total": 0,
                    "age_65_plus_total": 0,
                    "padron_source_relative_path": "padron/test.csv",
                    "padron_raw_encoding": "utf-8-sig",
                    "padron_raw_delimiter": ";",
                    "padron_raw_reader_mode": "pandas_default",
                    "padron_fx_carga": pd.NaT,
                    "padron_fx_datos_ini": pd.NaT,
                    "padron_fx_datos_fin": pd.NaT,
                },
                {
                    "padron_period": "2023-01",
                    "padron_year": 2023,
                    "padron_month": 1,
                    "padron_date": "2023-01-01",
                    "section_key": "01042",
                    "district_code": "01",
                    "district_name": "CENTRO",
                    "barrio_code": "002",
                    "barrio_name": "EMBAJADORES",
                    "section_code": "042",
                    "age_is_topcoded": True,
                    "spanish_male": 1,
                    "spanish_female": 0,
                    "foreign_male": 0,
                    "foreign_female": 1,
                    "spanish_total": 1,
                    "foreign_total": 1,
                    "male_total": 1,
                    "female_total": 1,
                    "total_population": 2,
                    "age_known_population": 2,
                    "age_weighted_population": 200,
                    "age_00_14_total": 0,
                    "age_15_29_total": 0,
                    "age_30_44_total": 0,
                    "age_45_64_total": 0,
                    "age_65_plus_total": 2,
                    "padron_source_relative_path": "padron/test.csv",
                    "padron_raw_encoding": "utf-8-sig",
                    "padron_raw_delimiter": ";",
                    "padron_raw_reader_mode": "pandas_default",
                    "padron_fx_carga": pd.NaT,
                    "padron_fx_datos_ini": pd.NaT,
                    "padron_fx_datos_fin": pd.NaT,
                },
            ]
        )

        aggregated = aggregate_padron_section_snapshot(frame)

        self.assertEqual(len(aggregated), 1)
        self.assertEqual(int(aggregated.iloc[0]["total_population"]), 8)
        self.assertAlmostEqual(float(aggregated.iloc[0]["age_mean"]), 32.5, places=2)
        self.assertAlmostEqual(float(aggregated.iloc[0]["share_foreign"]), 0.375, places=3)
        self.assertEqual(int(aggregated.iloc[0]["topcoded_age_rows"]), 1)
        self.assertEqual(int(aggregated.iloc[0]["share_age_65_plus"] * 1000), 250)

    def test_attach_renta_features_uses_section_district_and_city_fallbacks(self) -> None:
        panel = pd.DataFrame(
            [
                {"target_year": 2026, "section_key": "01001", "district_code": "01"},
                {"target_year": 2026, "section_key": "01002", "district_code": "01"},
                {"target_year": 2026, "section_key": "02001", "district_code": "02"},
            ]
        )
        renta = pd.DataFrame(
            [
                {"reference_year": 2023, "granularity": "city", "district_code": pd.NA, "section_key": pd.NA, "renta_value_eur": 19000},
                {"reference_year": 2023, "granularity": "district", "district_code": "01", "section_key": pd.NA, "renta_value_eur": 22000},
                {"reference_year": 2023, "granularity": "section", "district_code": "01", "section_key": "01001", "renta_value_eur": 27000},
            ]
        )

        enriched = attach_renta_features(panel, renta)

        self.assertEqual(list(enriched["renta_granularity_used"]), ["section", "district", "city"])
        self.assertEqual(list(enriched["renta_best_eur"]), [27000, 22000, 19000])
        self.assertEqual(list(enriched["renta_reference_year"].astype(int)), [2023, 2023, 2023])
        self.assertEqual(list(enriched["renta_lag_years"].astype(int)), [3, 3, 3])

    def test_attach_section_geography_features_adds_density_and_missing_flag(self) -> None:
        panel = pd.DataFrame(
            [
                {"section_key": "01001", "total_population": 100},
                {"section_key": "01002", "total_population": 50},
            ]
        )
        metadata = pd.DataFrame(
            [
                {"section_key": "01001", "section_area_m2": 20_000.0, "geometry_available": True},
                {"section_key": "01001", "section_area_m2": 30_000.0, "geometry_available": True},
            ]
        )

        enriched = attach_section_geography_features(panel, metadata)

        self.assertTrue(bool(enriched.iloc[0]["geometry_available"]))
        self.assertAlmostEqual(float(enriched.iloc[0]["population_density_km2"]), 2000.0, places=2)
        self.assertEqual(len(enriched), 2)
        self.assertFalse(bool(enriched.iloc[1]["geometry_available"]))
        self.assertTrue(pd.isna(enriched.iloc[1]["population_density_km2"]))


if __name__ == "__main__":
    unittest.main()
