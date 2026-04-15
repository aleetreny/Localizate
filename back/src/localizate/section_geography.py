from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .censo import build_censo_snapshot_manifest, load_and_normalize_censo_snapshot, load_raw_manifest
from .csv_utils import read_delimited_file
from .paths import DATA_DIR, DOCS_DATA_DIR, RAW_DATA_DIR
from .section_keys import (
    extract_renta_section_key_series,
    get_selected_source_row,
    normalize_section_key_series,
)


@dataclass(frozen=True)
class DbfField:
    name: str
    field_type: str
    length: int
    decimal_count: int


def read_dbf_table(path: str | Path, *, encoding: str = "utf-8") -> pd.DataFrame:
    file_path = Path(path)
    with file_path.open("rb") as handle:
        header = handle.read(32)
        if len(header) < 32:
            raise ValueError(f"Invalid DBF header in {file_path}")

        record_count = int.from_bytes(header[4:8], "little")
        header_length = int.from_bytes(header[8:10], "little")
        record_length = int.from_bytes(header[10:12], "little")
        field_count = max((header_length - 33) // 32, 0)

        fields: list[DbfField] = []
        for _ in range(field_count):
            descriptor = handle.read(32)
            name = descriptor[:11].split(b"\x00", 1)[0].decode("ascii", errors="ignore")
            fields.append(
                DbfField(
                    name=name,
                    field_type=chr(descriptor[11]),
                    length=descriptor[16],
                    decimal_count=descriptor[17],
                )
            )

        terminator = handle.read(1)
        if terminator not in {b"\r", b"\n"}:
            raise ValueError(f"Unexpected DBF field terminator in {file_path}")

        records: list[dict[str, object]] = []
        for _ in range(record_count):
            record = handle.read(record_length)
            if not record:
                break
            if record[:1] == b"*":
                continue

            values: dict[str, object] = {}
            offset = 1
            for field in fields:
                raw_value = record[offset : offset + field.length]
                offset += field.length
                values[field.name] = _parse_dbf_value(raw_value, field=field, encoding=encoding)
            records.append(values)

    return pd.DataFrame(records)


def _parse_dbf_value(raw_value: bytes, *, field: DbfField, encoding: str) -> object:
    text = raw_value.decode(encoding, errors="replace").strip()
    if not text:
        return pd.NA

    if field.field_type in {"N", "F"}:
        return pd.to_numeric(text.replace(",", "."), errors="coerce")

    if field.field_type == "L":
        return text.upper() in {"Y", "T"}

    return text


def load_section_metadata(raw_manifest: pd.DataFrame | None = None, *, raw_root: Path = RAW_DATA_DIR) -> pd.DataFrame:
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    selected = get_selected_source_row(manifest, "secciones_censales_shp")
    shp_path = raw_root / selected["selected_relative_path"]
    dbf_path = shp_path.with_suffix(".dbf")
    prj_path = shp_path.with_suffix(".prj")
    cpg_path = shp_path.with_suffix(".CPG")

    encoding = "utf-8"
    if cpg_path.exists():
        encoding = cpg_path.read_text(encoding="utf-8", errors="replace").strip() or "utf-8"

    table = read_dbf_table(dbf_path, encoding=encoding)
    table["section_key"] = normalize_section_key_series(table["COD_SECCIO"])
    table["district_code"] = (
        table["COD_DIS"].astype("string").str.strip().replace({"": pd.NA}).str.zfill(2)
    )
    table["district_name"] = table["NOM_DIS"].astype("string").str.strip().replace({"": pd.NA})
    table["barrio_code"] = (
        table["COD_BAR"].astype("string").str.strip().replace({"": pd.NA}).str.zfill(3)
    )
    table["barrio_name"] = table["NOM_BAR"].astype("string").str.strip().replace({"": pd.NA})
    table["section_area_m2"] = pd.to_numeric(table["Area"], errors="coerce")
    table = (
        table.groupby("section_key", dropna=False, sort=True)
        .agg(
            district_code=("district_code", "first"),
            district_name=("district_name", "first"),
            barrio_code=("barrio_code", "first"),
            barrio_name=("barrio_name", "first"),
            section_area_m2=("section_area_m2", "sum"),
            geometry_part_count=("section_key", "size"),
        )
        .reset_index()
    )
    table["geometry_available"] = True
    table["shape_relative_path"] = str(shp_path.relative_to(raw_root))
    table["dbf_relative_path"] = str(dbf_path.relative_to(raw_root))
    table["crs_wkt"] = prj_path.read_text(encoding="utf-8", errors="replace").strip() if prj_path.exists() else pd.NA
    ordered_columns = [
        "section_key",
        "district_code",
        "district_name",
        "barrio_code",
        "barrio_name",
        "section_area_m2",
        "geometry_part_count",
        "geometry_available",
        "shape_relative_path",
        "dbf_relative_path",
        "crs_wkt",
    ]
    return table[ordered_columns].sort_values("section_key").reset_index(drop=True)


def build_section_geography_coverage(
    raw_manifest: pd.DataFrame | None = None,
    *,
    censo_period: str | None = None,
    padron_period: str | None = None,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame]:
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    snapshot_manifest = build_censo_snapshot_manifest(manifest)
    censo_target_period = censo_period or snapshot_manifest["period"].iloc[-1]
    padron_row = get_selected_source_row(manifest, "padron", period=padron_period)
    renta_row = get_selected_source_row(manifest, "renta_media")

    section_metadata = load_section_metadata(manifest)
    geometry_sections = set(section_metadata["section_key"].dropna().tolist())

    locales_frame, _ = load_and_normalize_censo_snapshot(
        dataset_name="locales",
        period=censo_target_period,
        snapshot_manifest=snapshot_manifest,
    )
    censo_sections = set(
        normalize_section_key_series(locales_frame["id_seccion_censal_local"]).dropna().tolist()
    )

    padron_frame, _ = read_delimited_file(RAW_DATA_DIR / padron_row["selected_relative_path"])
    padron_sections = set(normalize_section_key_series(padron_frame["COD_DIST_SECCION"]).dropna().tolist())

    renta_frame, _ = read_delimited_file(RAW_DATA_DIR / renta_row["selected_relative_path"])
    renta_madrid = renta_frame[renta_frame["Municipios"].astype("string").str.startswith("28079 ", na=False)].copy()
    renta_sections = set(extract_renta_section_key_series(renta_madrid["Secciones"]).dropna().tolist())

    summary = pd.DataFrame(
        [
            {
                "censo_period": censo_target_period,
                "padron_period": padron_row["period"],
                "geometry_unique_sections": len(geometry_sections),
                "censo_unique_sections": len(censo_sections),
                "padron_unique_sections": len(padron_sections),
                "renta_unique_sections": len(renta_sections),
                "geometry_censo_intersection": len(geometry_sections & censo_sections),
                "geometry_padron_intersection": len(geometry_sections & padron_sections),
                "geometry_renta_intersection": len(geometry_sections & renta_sections),
                "geometry_only_sections": len(geometry_sections - censo_sections),
                "censo_only_vs_geometry": len(censo_sections - geometry_sections),
                "padron_only_vs_geometry": len(padron_sections - geometry_sections),
                "renta_only_vs_geometry": len(renta_sections - geometry_sections),
                "geometry_area_m2_min": float(section_metadata["section_area_m2"].min()),
                "geometry_area_m2_median": float(section_metadata["section_area_m2"].median()),
                "geometry_area_m2_max": float(section_metadata["section_area_m2"].max()),
            }
        ]
    )

    details = {
        "geometry_only_vs_censo": pd.DataFrame({"section_key": sorted(geometry_sections - censo_sections)}),
        "censo_only_vs_geometry": pd.DataFrame({"section_key": sorted(censo_sections - geometry_sections)}),
        "padron_only_vs_geometry": pd.DataFrame({"section_key": sorted(padron_sections - geometry_sections)}),
        "renta_only_vs_geometry": pd.DataFrame({"section_key": sorted(renta_sections - geometry_sections)}),
    }
    return summary, details, section_metadata


def render_section_geography_markdown(
    summary: pd.DataFrame,
    details: dict[str, pd.DataFrame],
    section_metadata: pd.DataFrame,
) -> str:
    row = summary.iloc[0]
    lines: list[str] = []
    lines.append("# Section Geography")
    lines.append("")
    lines.append("Metadata base y cobertura del bundle geometrico de secciones censales.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Periodo censo de referencia: `{row['censo_period']}`")
    lines.append(f"- Periodo padron de referencia: `{row['padron_period']}`")
    lines.append(f"- Secciones unicas en geometria: {int(row['geometry_unique_sections'])}")
    lines.append(f"- Interseccion geometria-censo: {int(row['geometry_censo_intersection'])}")
    lines.append(f"- Interseccion geometria-padron: {int(row['geometry_padron_intersection'])}")
    lines.append(f"- Interseccion geometria-renta: {int(row['geometry_renta_intersection'])}")
    lines.append(f"- Secciones solo en censo frente a geometria: {int(row['censo_only_vs_geometry'])}")
    lines.append(f"- Secciones solo en renta frente a geometria: {int(row['renta_only_vs_geometry'])}")
    lines.append("")
    lines.append("## CRS y area")
    lines.append("")
    lines.append(f"- CRS shapefile: `{section_metadata['crs_wkt'].dropna().iloc[0]}`")
    lines.append(f"- Area minima inferida: {row['geometry_area_m2_min']:.2f} m2")
    lines.append(f"- Area mediana inferida: {row['geometry_area_m2_median']:.2f} m2")
    lines.append(f"- Area maxima inferida: {row['geometry_area_m2_max']:.2f} m2")
    lines.append("")
    for name, frame in details.items():
        if frame.empty:
            continue
        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"- Muestra: {', '.join(frame['section_key'].head(20).tolist())}")
        lines.append("")
    return "\n".join(lines) + "\n"


def write_section_geography_outputs(
    summary: pd.DataFrame,
    details: dict[str, pd.DataFrame],
    section_metadata: pd.DataFrame,
    *,
    metadata_csv_path: Path | None = None,
    summary_csv_path: Path | None = None,
    details_dir: Path | None = None,
    report_md_path: Path | None = None,
) -> None:
    resolved_metadata_csv = metadata_csv_path or (DATA_DIR / "processed" / "section_geography.csv")
    resolved_summary_csv = summary_csv_path or (DATA_DIR / "processed" / "section_geography_coverage.csv")
    resolved_details_dir = details_dir or (DATA_DIR / "processed" / "section_geography_coverage")
    resolved_report_md = report_md_path or (DOCS_DATA_DIR / "section_geography.md")

    resolved_metadata_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_details_dir.mkdir(parents=True, exist_ok=True)
    resolved_report_md.parent.mkdir(parents=True, exist_ok=True)

    section_metadata.to_csv(resolved_metadata_csv, index=False)
    summary.to_csv(resolved_summary_csv, index=False)
    for name, frame in details.items():
        frame.to_csv(resolved_details_dir / f"{name}.csv", index=False)
    resolved_report_md.write_text(
        render_section_geography_markdown(summary, details, section_metadata),
        encoding="utf-8",
    )


def load_section_geodataframe(raw_manifest: pd.DataFrame | None = None, *, raw_root: Path = RAW_DATA_DIR) -> "pd.DataFrame":
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    selected = get_selected_source_row(manifest, "secciones_censales_shp")
    shp_path = raw_root / selected["selected_relative_path"]
    try:
        import geopandas as gpd
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "geopandas is required to read the section geometry. Install back/requirements.txt first."
        ) from exc

    return gpd.read_file(shp_path)
