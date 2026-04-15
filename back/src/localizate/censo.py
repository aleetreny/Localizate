from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .csv_utils import CsvReadMetadata, read_delimited_file
from .paths import DATA_DIR, RAW_DATA_DIR


CENSO_PURITY_START = "2015-01"
TRANSITION_PERIOD = "2017-09"

LOCALES_BASE_COLUMNS: tuple[str, ...] = (
    "id_local",
    "id_distrito_local",
    "desc_distrito_local",
    "id_barrio_local",
    "desc_barrio_local",
    "cod_barrio_local",
    "id_seccion_censal_local",
    "desc_seccion_censal_local",
    "coordenada_x_local",
    "coordenada_y_local",
    "id_tipo_acceso_local",
    "desc_tipo_acceso_local",
    "id_situacion_local",
    "desc_situacion_local",
    "id_vial_edificio",
    "clase_vial_edificio",
    "desc_vial_edificio",
    "id_ndp_edificio",
    "id_clase_ndp_edificio",
    "nom_edificio",
    "num_edificio",
    "cal_edificio",
    "secuencial_local_PC",
    "id_vial_acceso",
    "clase_vial_acceso",
    "desc_vial_acceso",
    "id_ndp_acceso",
    "id_clase_ndp_acceso",
    "nom_acceso",
    "num_acceso",
    "cal_acceso",
    "coordenada_x_agrupacion",
    "coordenada_y_agrupacion",
    "id_agrupacion",
    "nombre_agrupacion",
    "id_tipo_agrup",
    "desc_tipo_agrup",
    "id_planta_agrupado",
    "id_local_agrupado",
    "rotulo",
    "cod_postal",
    "hora_apertura1",
    "hora_apertura2",
    "hora_cierre1",
    "hora_cierre2",
    "fx_carga",
)

ACTIVIDADES_BASE_COLUMNS: tuple[str, ...] = (
    *LOCALES_BASE_COLUMNS[:-6],
    "id_seccion",
    "desc_seccion",
    "id_division",
    "desc_division",
    "id_epigrafe",
    "desc_epigrafe",
    "fx_carga",
)

COMMON_NUMERIC_COLUMNS: tuple[str, ...] = (
    "id_local",
    "id_distrito_local",
    "id_barrio_local",
    "cod_barrio_local",
    "id_seccion_censal_local",
    "desc_seccion_censal_local",
    "coordenada_x_local",
    "coordenada_y_local",
    "id_tipo_acceso_local",
    "id_situacion_local",
    "id_vial_edificio",
    "id_ndp_edificio",
    "id_clase_ndp_edificio",
    "secuencial_local_PC",
    "id_vial_acceso",
    "id_ndp_acceso",
    "id_clase_ndp_acceso",
    "coordenada_x_agrupacion",
    "coordenada_y_agrupacion",
    "id_agrupacion",
    "id_tipo_agrup",
    "cod_postal",
)


@dataclass(frozen=True)
class CensoSnapshotRecord:
    period: str
    snapshot_year: int
    snapshot_month: int
    snapshot_date: str
    locales_relative_path: str
    actividades_relative_path: str | None
    has_actividades: bool
    coverage_status: str
    coord_crs_status: str
    coord_crs_hint: str


def load_raw_manifest(manifest_path: Path | None = None) -> pd.DataFrame:
    resolved_path = manifest_path or (DATA_DIR / "intermediate" / "raw_manifest.csv")
    return pd.read_csv(resolved_path)


def build_censo_snapshot_manifest(raw_manifest: pd.DataFrame, purity_start: str = CENSO_PURITY_START) -> pd.DataFrame:
    selected = raw_manifest[raw_manifest["status"] == "selected"].copy()
    locales = selected[selected["source_name"] == "locales"][["period", "selected_relative_path"]].rename(
        columns={"selected_relative_path": "locales_relative_path"}
    )
    actividades = selected[selected["source_name"] == "actividades"][["period", "selected_relative_path"]].rename(
        columns={"selected_relative_path": "actividades_relative_path"}
    )

    snapshot_manifest = locales.merge(actividades, on="period", how="left")
    snapshot_manifest = snapshot_manifest[snapshot_manifest["period"] >= purity_start].copy()
    snapshot_manifest[["snapshot_year", "snapshot_month"]] = snapshot_manifest["period"].str.split("-", expand=True).astype(int)
    snapshot_manifest["snapshot_date"] = (
        snapshot_manifest["snapshot_year"].astype(str)
        + "-"
        + snapshot_manifest["snapshot_month"].astype(str).str.zfill(2)
        + "-01"
    )
    snapshot_manifest["has_actividades"] = snapshot_manifest["actividades_relative_path"].notna()
    snapshot_manifest["coverage_status"] = snapshot_manifest["has_actividades"].map(
        {True: "complete", False: "missing_actividades"}
    )
    snapshot_manifest["coord_crs_status"] = snapshot_manifest["period"].map(resolve_period_crs_status)
    snapshot_manifest["coord_crs_hint"] = snapshot_manifest["coord_crs_status"].map(
        {
            "ed50_utm30": "EPSG:23030",
            "transition_2017_09": "TRANSITION_2017_09",
            "etrs89_utm30": "EPSG:25830",
        }
    )
    return snapshot_manifest.sort_values("period").reset_index(drop=True)


def resolve_period_crs_status(period: str) -> str:
    if period < TRANSITION_PERIOD:
        return "ed50_utm30"
    if period == TRANSITION_PERIOD:
        return "transition_2017_09"
    return "etrs89_utm30"


def load_and_normalize_censo_snapshot(
    *,
    dataset_name: str,
    period: str,
    snapshot_manifest: pd.DataFrame,
    raw_root: Path = RAW_DATA_DIR,
) -> tuple[pd.DataFrame, CsvReadMetadata]:
    row = snapshot_manifest[snapshot_manifest["period"] == period]
    if row.empty:
        raise KeyError(f"Unknown period: {period}")
    snapshot_row = row.iloc[0]

    if dataset_name == "locales":
        relative_path = snapshot_row["locales_relative_path"]
    elif dataset_name == "actividades":
        relative_path = snapshot_row["actividades_relative_path"]
        if pd.isna(relative_path):
            raise KeyError(f"No actividades file for period {period}")
    else:
        raise ValueError(f"Unsupported dataset_name: {dataset_name}")

    frame, read_metadata = read_delimited_file(
        raw_root / relative_path,
        allow_last_column_overflow=True,
    )
    normalized = normalize_censo_snapshot(
        frame,
        dataset_name=dataset_name,
        period=period,
        source_relative_path=str(relative_path),
        read_metadata=read_metadata,
    )
    return normalized, read_metadata


def normalize_censo_snapshot(
    frame: pd.DataFrame,
    *,
    dataset_name: str,
    period: str,
    source_relative_path: str,
    read_metadata: CsvReadMetadata,
) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [str(column).strip().strip('"') for column in normalized.columns]

    if "coordenada_y_agrup" in normalized.columns and "coordenada_y_agrupacion" not in normalized.columns:
        normalized = normalized.rename(columns={"coordenada_y_agrup": "coordenada_y_agrupacion"})

    expected_columns = LOCALES_BASE_COLUMNS if dataset_name == "locales" else ACTIVIDADES_BASE_COLUMNS
    for column in expected_columns:
        if column not in normalized.columns:
            normalized[column] = pd.NA

    for column in COMMON_NUMERIC_COLUMNS:
        if column in normalized.columns:
            normalized[column] = coerce_spanish_numeric(normalized[column])

    normalized["snapshot_period"] = period
    normalized["snapshot_year"] = int(period[:4])
    normalized["snapshot_month"] = int(period[5:7])
    normalized["snapshot_date"] = f"{period}-01"
    normalized["source_dataset"] = dataset_name
    normalized["source_relative_path"] = source_relative_path
    normalized["raw_encoding"] = read_metadata.encoding
    normalized["raw_delimiter"] = read_metadata.delimiter
    normalized["raw_reader_mode"] = read_metadata.reader_mode
    normalized["coord_crs_status"] = resolve_period_crs_status(period)
    normalized["coord_crs_hint"] = {
        "ed50_utm30": "EPSG:23030",
        "transition_2017_09": "TRANSITION_2017_09",
        "etrs89_utm30": "EPSG:25830",
    }[normalized["coord_crs_status"].iloc[0]]

    normalized = add_best_coordinate_columns(normalized)

    ordered_columns = list(expected_columns) + [
        "snapshot_period",
        "snapshot_year",
        "snapshot_month",
        "snapshot_date",
        "source_dataset",
        "source_relative_path",
        "raw_encoding",
        "raw_delimiter",
        "raw_reader_mode",
        "coord_crs_status",
        "coord_crs_hint",
        "coordinate_source_best",
        "x_utm_best",
        "y_utm_best",
    ]
    return normalized[ordered_columns]


def coerce_spanish_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.strip().replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}).str.replace(",", ".", regex=False),
        errors="coerce",
    )


def add_best_coordinate_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    access_type = normalized["desc_tipo_acceso_local"].fillna("").astype(str).str.strip().str.upper()

    local_x = normalized["coordenada_x_local"]
    local_y = normalized["coordenada_y_local"]
    group_x = normalized["coordenada_x_agrupacion"]
    group_y = normalized["coordenada_y_agrupacion"]

    has_local = local_x.notna() & local_y.notna() & (local_x != 0) & (local_y != 0)
    has_group = group_x.notna() & group_y.notna() & (group_x != 0) & (group_y != 0)

    use_local_valid = access_type.eq("PUERTA CALLE") & has_local
    use_group_valid = ~use_local_valid & has_group
    use_local_noncanonical = ~use_local_valid & ~use_group_valid & has_local

    normalized["coordinate_source_best"] = "missing"
    normalized.loc[use_local_valid, "coordinate_source_best"] = "local_valid"
    normalized.loc[use_group_valid, "coordinate_source_best"] = "group_valid"
    normalized.loc[use_local_noncanonical, "coordinate_source_best"] = "local_noncanonical"

    normalized["x_utm_best"] = pd.NA
    normalized["y_utm_best"] = pd.NA
    normalized.loc[use_local_valid, ["x_utm_best", "y_utm_best"]] = normalized.loc[
        use_local_valid, ["coordenada_x_local", "coordenada_y_local"]
    ].to_numpy()
    normalized.loc[use_group_valid, ["x_utm_best", "y_utm_best"]] = normalized.loc[
        use_group_valid, ["coordenada_x_agrupacion", "coordenada_y_agrupacion"]
    ].to_numpy()
    normalized.loc[use_local_noncanonical, ["x_utm_best", "y_utm_best"]] = normalized.loc[
        use_local_noncanonical, ["coordenada_x_local", "coordenada_y_local"]
    ].to_numpy()
    return normalized
