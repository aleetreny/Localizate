from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from .csv_utils import sniff_delimiter, sniff_encoding
from .paths import RAW_DATA_DIR
from .raw_sources import RAW_SOURCE_SPECS, RAW_SOURCE_SPECS_BY_NAME, RawSourceSpec


RESOURCE_ID_PATTERN = re.compile(r"(?P<resource_id>\d{6}-\d+)")
MONTHLY_PERIOD_PATTERN = re.compile(r"^(?P<year>\d{4})_(?P<month>\d{2})_")
YEARLY_PERIOD_PATTERN = re.compile(r"^(?P<year>\d{4})_")


@dataclass(frozen=True)
class RawFileRecord:
    source_name: str
    relative_path: str
    filename: str
    exists: bool
    file_size_bytes: int
    extension: str
    format_hint: str
    period_granularity: str
    period: str | None
    year: int | None
    month: int | None
    resource_id: str | None
    encoding_guess: str | None
    delimiter_guess: str | None
    is_primary_asset: bool
    sidecar_complete: bool | None
    selection_strategy: str


def _extract_period(filename: str, period_granularity: str) -> tuple[str | None, int | None, int | None]:
    if period_granularity == "monthly":
        match = MONTHLY_PERIOD_PATTERN.match(filename)
        if not match:
            return None, None, None
        year = int(match.group("year"))
        month = int(match.group("month"))
        return f"{year:04d}-{month:02d}", year, month

    if period_granularity == "yearly":
        match = YEARLY_PERIOD_PATTERN.match(filename)
        if not match:
            return None, None, None
        year = int(match.group("year"))
        return f"{year:04d}", year, None

    return None, None, None


def _sidecar_complete(path: Path, spec: RawSourceSpec) -> bool | None:
    if not spec.required_sidecar_suffixes:
        return None
    if path.suffix.lower() != spec.primary_extension:
        return None

    stem = path.stem
    parent = path.parent
    return all((parent / f"{stem}{suffix}").exists() for suffix in spec.required_sidecar_suffixes)


def _build_record(path: Path, raw_root: Path, spec: RawSourceSpec) -> RawFileRecord:
    period, year, month = _extract_period(path.name, spec.period_granularity)
    resource_match = RESOURCE_ID_PATTERN.search(path.name)
    extension = path.suffix.lower()
    format_hint = _infer_format_hint(path.name, extension)
    is_primary_asset = extension == (spec.primary_extension or extension)

    encoding_guess = None
    delimiter_guess = None
    if extension in {".csv", ".txt"}:
        encoding_guess = sniff_encoding(path)
        delimiter_guess = sniff_delimiter(path, encoding=encoding_guess)

    return RawFileRecord(
        source_name=spec.name,
        relative_path=str(path.relative_to(raw_root)),
        filename=path.name,
        exists=path.exists(),
        file_size_bytes=path.stat().st_size,
        extension=extension,
        format_hint=format_hint,
        period_granularity=spec.period_granularity,
        period=period,
        year=year,
        month=month,
        resource_id=resource_match.group("resource_id") if resource_match else None,
        encoding_guess=encoding_guess,
        delimiter_guess=delimiter_guess,
        is_primary_asset=is_primary_asset,
        sidecar_complete=_sidecar_complete(path, spec),
        selection_strategy=spec.selection_strategy,
    )


def _infer_format_hint(filename: str, extension: str) -> str:
    lowered = filename.lower()
    if re.search(r"-txt(?=\.csv$|\.txt$)", lowered):
        return ".txt"
    if re.search(r"-csv(?=\.csv$|\.txt$)", lowered):
        return ".csv"
    return extension


def build_raw_inventory(raw_root: Path = RAW_DATA_DIR, specs: tuple[RawSourceSpec, ...] = RAW_SOURCE_SPECS) -> pd.DataFrame:
    records: list[RawFileRecord] = []

    for spec in specs:
        source_dir = raw_root / spec.relative_dir
        if not source_dir.exists():
            continue

        for path in sorted(p for p in source_dir.iterdir() if p.is_file()):
            records.append(_build_record(path, raw_root, spec))

    frame = pd.DataFrame(asdict(record) for record in records)
    if frame.empty:
        return frame

    return frame.sort_values(["source_name", "year", "month", "filename"], na_position="last").reset_index(drop=True)


def build_raw_manifest(inventory: pd.DataFrame) -> pd.DataFrame:
    if inventory.empty:
        return pd.DataFrame(
            columns=[
                "source_name",
                "period",
                "status",
                "selected_relative_path",
                "selected_filename",
                "selection_reason",
                "candidate_count",
                "candidate_filenames",
            ]
        )

    manifest_rows: list[dict[str, object]] = []

    for source_name, source_group in inventory.groupby("source_name", sort=True):
        spec = RAW_SOURCE_SPECS_BY_NAME[source_name]
        if spec.period_granularity == "static":
            grouped_items = [(None, source_group)]
        else:
            grouped_items = list(source_group.groupby("period", dropna=False, sort=True))

        for period, period_group in grouped_items:
            manifest_rows.append(_resolve_group(spec, period, period_group.copy()))

    return pd.DataFrame(manifest_rows).sort_values(
        ["source_name", "period"], na_position="last"
    ).reset_index(drop=True)


def _resolve_group(spec: RawSourceSpec, period: str | None, group: pd.DataFrame) -> dict[str, object]:
    candidate_filenames = sorted(group["filename"].tolist())
    base_row = {
        "source_name": spec.name,
        "period": period,
        "status": "unresolved",
        "selected_relative_path": None,
        "selected_filename": None,
        "selection_reason": None,
        "candidate_count": len(group),
        "candidate_filenames": " | ".join(candidate_filenames),
    }

    if len(group) == 1 and spec.selection_strategy != "manual_review":
        selected = group.iloc[0]
        base_row.update(
            {
                "status": "selected",
                "selected_relative_path": selected["relative_path"],
                "selected_filename": selected["filename"],
                "selection_reason": "single_candidate",
            }
        )
        return base_row

    if spec.selection_strategy == "unique_per_period":
        if len(group) == 1:
            return base_row
        base_row.update(
            {
                "status": "conflict",
                "selection_reason": "multiple_candidates_for_unique_period",
            }
        )
        return base_row

    if spec.selection_strategy == "prefer_suffix":
        return _resolve_by_suffix(spec, group, base_row)

    if spec.selection_strategy == "prefer_filename":
        return _resolve_by_filename(spec, group, base_row)

    if spec.selection_strategy == "manual_review":
        if spec.name == "avisos":
            resolved = _resolve_avisos_group(group, base_row)
            if resolved["status"] == "selected":
                return resolved
        base_row.update(
            {
                "status": "manual_review",
                "selection_reason": "requires_external_metadata_or_manual_rule",
            }
        )
        return base_row

    return base_row


def _resolve_by_suffix(spec: RawSourceSpec, group: pd.DataFrame, base_row: dict[str, object]) -> dict[str, object]:
    for suffix in spec.preferred_suffixes:
        matches = group[group["format_hint"] == suffix]
        if len(matches) == 1:
            selected = matches.iloc[0]
            base_row.update(
                {
                    "status": "selected",
                    "selected_relative_path": selected["relative_path"],
                    "selected_filename": selected["filename"],
                    "selection_reason": f"preferred_suffix:{suffix}",
                }
            )
            return base_row
        if len(matches) > 1:
            base_row.update(
                {
                    "status": "conflict",
                    "selection_reason": f"multiple_candidates_with_preferred_suffix:{suffix}",
                }
            )
            return base_row

    base_row.update(
        {
            "status": "unresolved",
            "selection_reason": "no_candidate_matched_preferred_suffixes",
        }
    )
    return base_row


def _resolve_by_filename(spec: RawSourceSpec, group: pd.DataFrame, base_row: dict[str, object]) -> dict[str, object]:
    for filename in spec.preferred_filenames:
        matches = group[group["filename"] == filename]
        if len(matches) == 1:
            selected = matches.iloc[0]
            base_row.update(
                {
                    "status": "selected",
                    "selected_relative_path": selected["relative_path"],
                    "selected_filename": selected["filename"],
                    "selection_reason": f"preferred_filename:{filename}",
                }
            )
            return base_row
        if len(matches) > 1:
            base_row.update(
                {
                    "status": "conflict",
                    "selection_reason": f"multiple_candidates_with_preferred_filename:{filename}",
                }
            )
            return base_row

    primary_assets = group[group["is_primary_asset"]]
    if len(primary_assets) == 1:
        selected = primary_assets.iloc[0]
        base_row.update(
            {
                "status": "selected",
                "selected_relative_path": selected["relative_path"],
                "selected_filename": selected["filename"],
                "selection_reason": "single_primary_asset",
            }
        )
        return base_row

    if len(primary_assets) > 1:
        base_row.update(
            {
                "status": "conflict",
                "selection_reason": "multiple_primary_assets",
            }
        )
        return base_row

    base_row.update(
        {
            "status": "unresolved",
            "selection_reason": "no_candidate_matched_preferred_filenames",
        }
    )
    return base_row


def _resolve_avisos_group(group: pd.DataFrame, base_row: dict[str, object]) -> dict[str, object]:
    required_columns = {"avisos_delivery_type", "avisos_system", "year"}
    if not required_columns.issubset(group.columns):
        return base_row

    year_series = group["year"].dropna()
    if year_series.empty:
        return base_row
    year = int(year_series.iloc[0])
    target_system = "SIC" if year >= 2018 else "AVISA"

    matches = group[
        (group["avisos_delivery_type"] == "recibidos")
        & (group["avisos_system"] == target_system)
    ]
    if len(matches) == 1:
        selected = matches.iloc[0]
        base_row.update(
            {
                "status": "selected",
                "selected_relative_path": selected["relative_path"],
                "selected_filename": selected["filename"],
                "selection_reason": f"avisos_rule:recibidos:{target_system}",
            }
        )
        return base_row

    return base_row


def build_inventory_markdown(inventory: pd.DataFrame, manifest: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Raw Data Inventory")
    lines.append("")
    lines.append("Inventario generado automaticamente a partir del contenido actual de `storage/raw/`.")
    lines.append("")

    if inventory.empty:
        lines.append("No se encontraron archivos.")
        return "\n".join(lines) + "\n"

    inventory_summary = (
        inventory.groupby("source_name")
        .agg(
            files=("filename", "count"),
            periods=("period", lambda values: values.dropna().nunique()),
            primary_assets=("is_primary_asset", "sum"),
        )
        .reset_index()
    )
    manifest_summary = (
        manifest.groupby("source_name")
        .agg(
            manifest_rows=("status", "count"),
            selected_rows=("status", lambda values: int((values == "selected").sum())),
            issue_rows=("status", lambda values: int((values != "selected").sum())),
        )
        .reset_index()
    )
    summary = inventory_summary.merge(manifest_summary, on="source_name", how="left").fillna(0)

    lines.append("## Resumen por fuente")
    lines.append("")
    lines.append("| Fuente | Archivos | Periodos | Assets primarios | Seleccionados | Incidencias |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for row in summary.itertuples(index=False):
        lines.append(
            f"| {row.source_name} | {int(row.files)} | {int(row.periods)} | {int(row.primary_assets)} | "
            f"{int(row.selected_rows)} | {int(row.issue_rows)} |"
        )
    lines.append("")

    lines.append("## Hallazgos operativos")
    lines.append("")
    missing_activity_months = _find_missing_periods(manifest, "locales", "actividades")
    if missing_activity_months:
        lines.append(
            f"- `actividades` no cubre todos los periodos de `locales`. Faltan: {', '.join(missing_activity_months)}."
        )

    padron_issue_count = int(
        manifest[(manifest["source_name"] == "padron") & (manifest["selection_reason"].astype(str).str.startswith("preferred_suffix"))].shape[0]
    )
    if padron_issue_count:
        lines.append(
            f"- `padron` tiene {padron_issue_count} periodos resueltos por preferencia de formato; se escoge la variante `csv` y se deja `txt` como respaldo."
        )

    avisos_issue_count = int(manifest[(manifest["source_name"] == "avisos") & (manifest["status"] == "manual_review")].shape[0])
    if avisos_issue_count:
        lines.append(
            f"- `avisos` queda pendiente de clasificacion fina en {avisos_issue_count} periodos anuales porque el nombre del fichero no distingue de forma fiable entre recibidos y resueltos."
        )
    elif "avisos" in set(manifest["source_name"]):
        lines.append(
            "- `avisos` ya se resuelve automaticamente con metadata oficial CKAN: `recibidos + AVISA` para 2014-2017 y `recibidos + SIC` para 2018+."
        )

    shapefile_entry = inventory[
        (inventory["source_name"] == "secciones_censales_shp") & (inventory["is_primary_asset"])
    ]
    if not shapefile_entry.empty:
        sidecar_complete = shapefile_entry.iloc[0]["sidecar_complete"]
        lines.append(
            f"- El shapefile principal de secciones censales tiene sidecars minimos "
            f"{'completos' if sidecar_complete else 'incompletos'}."
        )
    lines.append("")

    lines.append("## Incidencias y periodos pendientes")
    lines.append("")
    issue_rows = manifest[manifest["status"] != "selected"]
    if issue_rows.empty:
        lines.append("No quedan incidencias abiertas en el manifiesto canonico actual.")
    else:
        lines.append("| Fuente | Periodo | Estado | Motivo | Candidatos |")
        lines.append("| --- | --- | --- | --- | --- |")
        for row in issue_rows.itertuples(index=False):
            period = row.period if pd.notna(row.period) else "-"
            candidates = str(row.candidate_filenames).replace(" | ", "<br>")
            lines.append(f"| {row.source_name} | {period} | {row.status} | {row.selection_reason} | {candidates} |")
    lines.append("")

    return "\n".join(lines) + "\n"


def _find_missing_periods(manifest: pd.DataFrame, reference_source: str, comparison_source: str) -> list[str]:
    reference_periods = set(
        manifest[(manifest["source_name"] == reference_source) & (manifest["status"] == "selected")]["period"].dropna()
    )
    comparison_periods = set(
        manifest[(manifest["source_name"] == comparison_source) & (manifest["status"] == "selected")]["period"].dropna()
    )
    return sorted(reference_periods - comparison_periods)
