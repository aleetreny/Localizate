from __future__ import annotations

from pathlib import Path

import pandas as pd

from .censo import build_censo_snapshot_manifest, load_and_normalize_censo_snapshot, load_raw_manifest
from .csv_utils import read_delimited_file
from .paths import DATA_DIR, DOCS_DIR, RAW_DATA_DIR


def normalize_section_key_series(series: pd.Series, *, width: int = 5) -> pd.Series:
    normalized = (
        series.astype("string")
        .str.extract(r"(\d+)", expand=False)
        .astype("string")
        .str.lstrip("0")
        .replace({"": pd.NA})
    )
    return normalized.str.zfill(width)


def extract_renta_section_key_series(series: pd.Series) -> pd.Series:
    extracted = series.astype("string").str.extract(r"(\d{5})\b", expand=False).astype("string")
    return extracted


def get_selected_source_row(raw_manifest: pd.DataFrame, source_name: str, period: str | None = None) -> pd.Series:
    selected = raw_manifest[(raw_manifest["source_name"] == source_name) & (raw_manifest["status"] == "selected")].copy()
    if selected.empty:
        raise KeyError(f"No selected rows for source {source_name}")

    if period is None:
        selected = selected.sort_values("period", na_position="last")
        return selected.iloc[-1]

    row = selected[selected["period"] == period]
    if row.empty:
        raise KeyError(f"No selected row for source {source_name} and period {period}")
    return row.iloc[0]


def build_section_key_coverage(
    raw_manifest: pd.DataFrame | None = None,
    *,
    censo_period: str | None = None,
    padron_period: str | None = None,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    manifest = raw_manifest if raw_manifest is not None else load_raw_manifest()
    snapshot_manifest = build_censo_snapshot_manifest(manifest)

    censo_target_period = censo_period or snapshot_manifest["period"].iloc[-1]
    padron_row = get_selected_source_row(manifest, "padron", period=padron_period)
    renta_row = get_selected_source_row(manifest, "renta_media")

    locales_frame, _ = load_and_normalize_censo_snapshot(
        dataset_name="locales",
        period=censo_target_period,
        snapshot_manifest=snapshot_manifest,
    )
    padron_frame, _ = read_delimited_file(RAW_DATA_DIR / padron_row["selected_relative_path"])
    renta_frame, _ = read_delimited_file(RAW_DATA_DIR / renta_row["selected_relative_path"])

    censo_sections_full = normalize_section_key_series(locales_frame["id_seccion_censal_local"])
    censo_sections = censo_sections_full.dropna()
    padron_sections = normalize_section_key_series(padron_frame["COD_DIST_SECCION"]).dropna()
    renta_madrid = renta_frame[renta_frame["Municipios"].astype("string").str.startswith("28079 ", na=False)].copy()
    renta_sections = extract_renta_section_key_series(renta_madrid["Secciones"]).dropna()

    censo_set = set(censo_sections.tolist())
    padron_set = set(padron_sections.tolist())
    renta_set = set(renta_sections.tolist())

    summary = pd.DataFrame(
        [
            {
                "censo_period": censo_target_period,
                "padron_period": padron_row["period"],
                "renta_period_min": renta_madrid["Periodo"].min(),
                "renta_period_max": renta_madrid["Periodo"].max(),
                "censo_unique_sections": len(censo_set),
                "padron_unique_sections": len(padron_set),
                "renta_unique_sections": len(renta_set),
                "censo_padron_intersection": len(censo_set & padron_set),
                "censo_renta_intersection": len(censo_set & renta_set),
                "padron_renta_intersection": len(padron_set & renta_set),
                "triple_intersection": len(censo_set & padron_set & renta_set),
                "censo_only_sections": len(censo_set - padron_set),
                "padron_only_sections": len(padron_set - censo_set),
                "renta_only_sections_vs_censo": len(renta_set - censo_set),
                "renta_only_sections_vs_padron": len(renta_set - padron_set),
                "local_rows_without_section_key": int(censo_sections_full.isna().sum()),
            }
        ]
    )

    details = {
        "censo_only_vs_padron": pd.DataFrame({"section_key": sorted(censo_set - padron_set)}),
        "padron_only_vs_censo": pd.DataFrame({"section_key": sorted(padron_set - censo_set)}),
        "censo_only_vs_renta": pd.DataFrame({"section_key": sorted(censo_set - renta_set)}),
        "renta_only_vs_censo": pd.DataFrame({"section_key": sorted(renta_set - censo_set)}),
    }
    return summary, details


def render_section_key_coverage_markdown(summary: pd.DataFrame, details: dict[str, pd.DataFrame]) -> str:
    row = summary.iloc[0]
    lines: list[str] = []
    lines.append("# Section Key Coverage")
    lines.append("")
    lines.append("Cobertura y solape de claves de seccion censal entre censo, padron y renta.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Periodo censo: `{row['censo_period']}`")
    lines.append(f"- Periodo padron: `{row['padron_period']}`")
    lines.append(f"- Renta disponible entre `{row['renta_period_min']}` y `{row['renta_period_max']}`")
    lines.append(f"- Secciones unicas censo: {int(row['censo_unique_sections'])}")
    lines.append(f"- Secciones unicas padron: {int(row['padron_unique_sections'])}")
    lines.append(f"- Secciones unicas renta Madrid capital: {int(row['renta_unique_sections'])}")
    lines.append(f"- Interseccion censo-padron: {int(row['censo_padron_intersection'])}")
    lines.append(f"- Interseccion censo-renta: {int(row['censo_renta_intersection'])}")
    lines.append(f"- Interseccion triple: {int(row['triple_intersection'])}")
    lines.append("")
    lines.append("## Desajustes")
    lines.append("")
    lines.append(f"- Solo en censo frente a padron: {int(row['censo_only_sections'])}")
    lines.append(f"- Solo en padron frente a censo: {int(row['padron_only_sections'])}")
    lines.append(f"- Solo en renta frente a censo: {int(row['renta_only_sections_vs_censo'])}")
    lines.append("")
    for name, frame in details.items():
        if frame.empty:
            continue
        lines.append(f"### {name}")
        lines.append("")
        sample = ", ".join(frame["section_key"].head(20).tolist())
        lines.append(f"- Muestra: {sample}")
        lines.append("")
    return "\n".join(lines) + "\n"


def write_section_key_coverage_outputs(
    summary: pd.DataFrame,
    details: dict[str, pd.DataFrame],
    *,
    summary_csv_path: Path | None = None,
    details_dir: Path | None = None,
    report_md_path: Path | None = None,
) -> None:
    resolved_summary_csv = summary_csv_path or (DATA_DIR / "processed" / "section_key_coverage.csv")
    resolved_details_dir = details_dir or (DATA_DIR / "processed" / "section_key_coverage")
    resolved_report_md = report_md_path or (DOCS_DIR / "section_key_coverage.md")

    resolved_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved_details_dir.mkdir(parents=True, exist_ok=True)
    resolved_report_md.parent.mkdir(parents=True, exist_ok=True)

    summary.to_csv(resolved_summary_csv, index=False)
    for name, frame in details.items():
        frame.to_csv(resolved_details_dir / f"{name}.csv", index=False)
    resolved_report_md.write_text(render_section_key_coverage_markdown(summary, details), encoding="utf-8")
