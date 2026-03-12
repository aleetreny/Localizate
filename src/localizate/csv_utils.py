from __future__ import annotations

import codecs
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_ENCODING_CANDIDATES: tuple[str, ...] = (
    "utf-8-sig",
    "utf-8",
    "cp1252",
    "latin-1",
)


@dataclass(frozen=True)
class CsvReadMetadata:
    path: Path
    encoding: str
    delimiter: str
    reader_mode: str


def sniff_encoding(path: str | Path, encoding_candidates: tuple[str, ...] = DEFAULT_ENCODING_CANDIDATES) -> str:
    file_path = Path(path)
    with file_path.open("rb") as handle:
        sample = handle.read(65536)

    if sample.startswith(codecs.BOM_UTF8):
        return "utf-8-sig"

    for encoding in encoding_candidates:
        try:
            sample.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue

    return "latin-1"


def sniff_delimiter(path: str | Path, encoding: str | None = None) -> str:
    file_path = Path(path)
    resolved_encoding = encoding or sniff_encoding(file_path)
    with file_path.open("rb") as handle:
        sample_bytes = handle.read(8192)
    sample = sample_bytes.decode(resolved_encoding, errors="replace")

    if not sample:
        return ","

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t,")
        return dialect.delimiter
    except csv.Error:
        counts = {delimiter: sample.count(delimiter) for delimiter in (";", ",", "\t", "|")}
        return max(counts, key=counts.get)


def read_delimited_file(
    path: str | Path,
    *,
    encoding: str | None = None,
    delimiter: str | None = None,
    encoding_candidates: tuple[str, ...] = DEFAULT_ENCODING_CANDIDATES,
    allow_last_column_overflow: bool = False,
    **pandas_kwargs: Any,
) -> tuple[pd.DataFrame, CsvReadMetadata]:
    file_path = Path(path)
    candidate_encodings = (encoding,) if encoding else encoding_candidates
    resolved_delimiter = delimiter
    last_error: Exception | None = None

    for candidate_encoding in candidate_encodings:
        try:
            current_delimiter = resolved_delimiter or sniff_delimiter(file_path, encoding=candidate_encoding)
            reader_mode = "pandas_default"
            try:
                frame = pd.read_csv(
                    file_path,
                    sep=current_delimiter,
                    encoding=candidate_encoding,
                    low_memory=False,
                    **pandas_kwargs,
                )
            except pd.errors.ParserError as exc:
                if not allow_last_column_overflow:
                    raise exc
                frame = _read_with_last_column_overflow_fix(
                    file_path,
                    encoding=candidate_encoding,
                    delimiter=current_delimiter,
                )
                reader_mode = "last_column_overflow_fix"
            return frame, CsvReadMetadata(
                path=file_path,
                encoding=candidate_encoding,
                delimiter=current_delimiter,
                reader_mode=reader_mode,
            )
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
        except pd.errors.ParserError as exc:
            last_error = exc
            continue

    raise ValueError(f"Unable to read delimited file {file_path}") from last_error


def _read_with_last_column_overflow_fix(path: Path, *, encoding: str, delimiter: str) -> pd.DataFrame:
    with path.open("r", encoding=encoding, errors="replace", newline="") as handle:
        header_line = handle.readline()
        header = next(csv.reader([header_line], delimiter=delimiter))
        expected_columns = len(header)

        rows: list[list[str]] = []
        for line in handle:
            stripped = line.rstrip("\r\n")
            parts = stripped.split(delimiter, expected_columns - 1)
            if len(parts) < expected_columns:
                parts.extend([""] * (expected_columns - len(parts)))
            rows.append([_clean_split_field(part) for part in parts])

    cleaned_header = [_clean_split_field(column) for column in header]
    return pd.DataFrame(rows, columns=cleaned_header)


def _clean_split_field(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
    return cleaned.replace('""', '"')
