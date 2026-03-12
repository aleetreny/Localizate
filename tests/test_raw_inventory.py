from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from localizate.csv_utils import _read_with_last_column_overflow_fix, read_delimited_file, sniff_delimiter, sniff_encoding
from localizate.censo import build_censo_snapshot_manifest, normalize_censo_snapshot
from localizate.censo_profile import profile_censo_snapshots
from localizate.raw_inventory import build_raw_inventory, build_raw_manifest
from localizate.raw_sources import RawSourceSpec
from localizate.section_keys import extract_renta_section_key_series, normalize_section_key_series


class CsvUtilsTests(unittest.TestCase):
    def test_sniff_latin1_semicolon_file(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sample.csv"
            path.write_bytes("col1;col2\nniño;1\n".encode("cp1252"))

            self.assertEqual(sniff_encoding(path), "cp1252")
            self.assertEqual(sniff_delimiter(path, encoding="cp1252"), ";")

            frame, metadata = read_delimited_file(path)
            self.assertEqual(list(frame.columns), ["col1", "col2"])
            self.assertEqual(frame.iloc[0]["col1"], "niño")
            self.assertEqual(metadata.delimiter, ";")
            self.assertEqual(metadata.reader_mode, "pandas_default")

    def test_last_column_overflow_fix_recovers_malformed_csv(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "broken.csv"
            path.write_text('a;b;c\n1;2;"hola "mundo; fin"\n', encoding="utf-8")

            frame = _read_with_last_column_overflow_fix(path, encoding="utf-8", delimiter=";")

            self.assertEqual(list(frame.columns), ["a", "b", "c"])
            self.assertEqual(frame.iloc[0]["c"], 'hola "mundo; fin')


class RawManifestTests(unittest.TestCase):
    def test_padron_prefers_csv_over_txt(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            raw_root = Path(tmp_dir)
            padron_dir = raw_root / "padron"
            padron_dir.mkdir(parents=True)
            content = "A;B\n1;2\n"
            (padron_dir / "2024_01_padron_padron_foo-csv.csv").write_text(content, encoding="utf-8")
            (padron_dir / "2024_01_padron_padron_bar-txt.csv").write_text(content, encoding="utf-8")

            specs = (
                RawSourceSpec(
                    name="padron",
                    relative_dir="padron",
                    period_granularity="monthly",
                    selection_strategy="prefer_suffix",
                    description="test",
                    preferred_suffixes=(".csv", ".txt"),
                    primary_extension=".csv",
                ),
            )

            inventory = build_raw_inventory(raw_root=raw_root, specs=specs)
            manifest = build_raw_manifest(inventory)

            self.assertEqual(len(manifest), 1)
            self.assertEqual(manifest.iloc[0]["status"], "selected")
            self.assertIn("-csv.csv", str(manifest.iloc[0]["selected_filename"]))

    def test_avisos_requires_manual_review_when_multiple_candidates_exist(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            raw_root = Path(tmp_dir)
            avisos_dir = raw_root / "avisos"
            avisos_dir.mkdir(parents=True)
            content = "A;B\n1;2\n"
            (avisos_dir / "2024_avisos_foo.csv").write_text(content, encoding="utf-8")
            (avisos_dir / "2024_avisos_bar.csv").write_text(content, encoding="utf-8")

            specs = (
                RawSourceSpec(
                    name="avisos",
                    relative_dir="avisos",
                    period_granularity="yearly",
                    selection_strategy="manual_review",
                    description="test",
                    preferred_suffixes=(".csv",),
                    primary_extension=".csv",
                ),
            )

            inventory = build_raw_inventory(raw_root=raw_root, specs=specs)
            manifest = build_raw_manifest(inventory)

            self.assertEqual(len(manifest), 1)
            self.assertEqual(manifest.iloc[0]["status"], "manual_review")
            self.assertIsNone(manifest.iloc[0]["selected_filename"])

    def test_avisos_is_selected_when_ckan_metadata_is_available(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            raw_root = Path(tmp_dir)
            avisos_dir = raw_root / "avisos"
            avisos_dir.mkdir(parents=True)
            content = "A;B\n1;2\n"
            (avisos_dir / "2018_avisos_avisos_212411-7-madrid-avisa-csv.csv").write_text(content, encoding="utf-8")
            (avisos_dir / "2018_avisos_avisos_212411-23-madrid-avisa-csv.csv").write_text(content, encoding="utf-8")
            (avisos_dir / "2018_avisos_avisos_212411-34-madrid-avisa-csv.csv").write_text(content, encoding="utf-8")

            specs = (
                RawSourceSpec(
                    name="avisos",
                    relative_dir="avisos",
                    period_granularity="yearly",
                    selection_strategy="manual_review",
                    description="test",
                    preferred_suffixes=(".csv",),
                    primary_extension=".csv",
                ),
            )

            inventory = build_raw_inventory(raw_root=raw_root, specs=specs)
            inventory["avisos_delivery_type"] = None
            inventory["avisos_system"] = None
            inventory.loc[inventory["resource_id"] == "212411-7", ["avisos_delivery_type", "avisos_system"]] = ["recibidos", "SIC"]
            inventory.loc[inventory["resource_id"] == "212411-23", ["avisos_delivery_type", "avisos_system"]] = ["tramitados", "SIC"]
            inventory.loc[inventory["resource_id"] == "212411-34", ["avisos_delivery_type", "avisos_system"]] = ["recibidos", "AVISA"]

            manifest = build_raw_manifest(inventory)

            self.assertEqual(len(manifest), 1)
            self.assertEqual(manifest.iloc[0]["status"], "selected")
            self.assertIn("212411-7", str(manifest.iloc[0]["selected_filename"]))


class CensoTests(unittest.TestCase):
    def test_build_censo_snapshot_manifest_flags_missing_activities(self) -> None:
        raw_manifest = pd.DataFrame(
            [
                {"source_name": "locales", "period": "2017-12", "status": "selected", "selected_relative_path": "locales/2017_12.csv"},
                {"source_name": "locales", "period": "2018-01", "status": "selected", "selected_relative_path": "locales/2018_01.csv"},
                {"source_name": "actividades", "period": "2018-01", "status": "selected", "selected_relative_path": "actividades/2018_01.csv"},
            ]
        )
        manifest = build_censo_snapshot_manifest(raw_manifest)

        self.assertEqual(list(manifest["period"]), ["2017-12", "2018-01"])
        self.assertEqual(list(manifest["coverage_status"]), ["missing_actividades", "complete"])
        self.assertEqual(list(manifest["coord_crs_status"]), ["etrs89_utm30", "etrs89_utm30"])

    def test_normalize_censo_snapshot_adds_missing_columns_and_coordinates(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "id_local": "1",
                    "desc_tipo_acceso_local": "Puerta Calle",
                    "coordenada_x_local": "440000,5",
                    "coordenada_y_local": "4470000,5",
                    "coordenada_x_agrupacion": "",
                    "coordenada_y_agrup": "",
                    "rotulo": "A",
                },
                {
                    "id_local": "2",
                    "desc_tipo_acceso_local": "Agrupado",
                    "coordenada_x_local": "0",
                    "coordenada_y_local": "0",
                    "coordenada_x_agrupacion": "441000,0",
                    "coordenada_y_agrup": "4471000,0",
                    "rotulo": "B",
                },
                {
                    "id_local": "3",
                    "desc_tipo_acceso_local": "Interior",
                    "coordenada_x_local": "442000,0",
                    "coordenada_y_local": "4472000,0",
                    "coordenada_x_agrupacion": "0",
                    "coordenada_y_agrup": "0",
                    "rotulo": "C",
                },
            ]
        )

        normalized = normalize_censo_snapshot(
            frame,
            dataset_name="locales",
            period="2017-09",
            source_relative_path="locales/test.csv",
            read_metadata=type("Meta", (), {"encoding": "cp1252", "delimiter": ";", "reader_mode": "pandas_default"})(),
        )

        self.assertIn("coordenada_y_agrupacion", normalized.columns)
        self.assertIn("fx_carga", normalized.columns)
        self.assertEqual(list(normalized["coordinate_source_best"]), ["local_valid", "group_valid", "local_noncanonical"])
        self.assertEqual(normalized.iloc[0]["coord_crs_status"], "transition_2017_09")
        self.assertEqual(normalized.iloc[0]["x_utm_best"], 440000.5)
        self.assertEqual(normalized.iloc[0]["raw_reader_mode"], "pandas_default")

    def test_profile_censo_snapshots_for_selected_periods(self) -> None:
        raw_manifest = pd.read_csv("data/intermediate/raw_manifest.csv")
        snapshot_manifest = build_censo_snapshot_manifest(raw_manifest)
        profile = profile_censo_snapshots(snapshot_manifest, periods=["2015-01"])

        self.assertEqual(len(profile), 1)
        self.assertEqual(profile.iloc[0]["period"], "2015-01")
        self.assertGreater(int(profile.iloc[0]["locales_rows"]), 0)
        self.assertEqual(profile.iloc[0]["coverage_status"], "complete")


class SectionKeyTests(unittest.TestCase):
    def test_normalize_section_key_series(self) -> None:
        series = pd.Series([1077, "13119", " 77 ", pd.NA, "00042"])
        normalized = normalize_section_key_series(series)
        self.assertEqual(normalized.iloc[0], "01077")
        self.assertEqual(normalized.iloc[1], "13119")
        self.assertEqual(normalized.iloc[2], "00077")
        self.assertTrue(pd.isna(normalized.iloc[3]))
        self.assertEqual(normalized.iloc[4], "00042")

    def test_extract_renta_section_key_series(self) -> None:
        series = pd.Series(["2807901001 Madrid sección 01001", "2807901042 Madrid sección 01042", pd.NA])
        extracted = extract_renta_section_key_series(series)
        self.assertEqual(extracted.iloc[0], "01001")
        self.assertEqual(extracted.iloc[1], "01042")
        self.assertTrue(pd.isna(extracted.iloc[2]))


if __name__ == "__main__":
    unittest.main()
