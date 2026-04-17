#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_DIR = PROJECT_ROOT / "front" / "public" / "data" / "map" / "historical"
MONOLITH_PATH = HISTORICAL_DIR / "hex-composition.json"
MANIFEST_PATH = HISTORICAL_DIR / "hex-composition.manifest.json"
PARTS_DIR = HISTORICAL_DIR / "hex-composition"
PREFIX_MANIFEST_PATH = HISTORICAL_DIR / "hex-composition.by-prefix.manifest.json"
PREFIX_PARTS_DIR = HISTORICAL_DIR / "hex-composition-by-prefix"
PREFIX_LENGTH = 10


def main() -> int:
    if not MONOLITH_PATH.exists():
        raise SystemExit(f"Hex composition monolith not found: {MONOLITH_PATH}")

    payload = json.loads(MONOLITH_PATH.read_text(encoding="utf-8"))
    rows = payload.get("hexes")
    if not isinstance(rows, list):
        raise SystemExit("Invalid hex composition payload: missing 'hexes' list.")

    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    PREFIX_PARTS_DIR.mkdir(parents=True, exist_ok=True)
    for existing_part in PARTS_DIR.glob("*.json"):
        existing_part.unlink()
    for existing_part in PREFIX_PARTS_DIR.glob("*.json"):
        existing_part.unlink()

    rows_by_year: dict[int, list[dict[str, object]]] = {}
    rows_by_prefix: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        year_value = row.get("year")
        try:
            year = int(year_value)
        except (TypeError, ValueError):
            continue
        rows_by_year.setdefault(year, []).append(row)
        h3_cell = str(row.get("h3_cell") or "").strip()
        if h3_cell:
            rows_by_prefix.setdefault(h3_cell[:PREFIX_LENGTH], []).append(row)

    manifest_parts: list[dict[str, object]] = []
    for year in sorted(rows_by_year):
        year_rows = rows_by_year[year]
        part_path = PARTS_DIR / f"{year}.json"
        part_path.write_text(
            json.dumps({"hexes": year_rows}, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )
        manifest_parts.append(
            {
                "year": year,
                "path": f"/data/map/historical/hex-composition/{year}.json",
                "rows": len(year_rows),
            }
        )

    manifest = {
        "meta": payload.get("meta", {}),
        "parts": manifest_parts,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    shard_sizes: list[int] = []
    for prefix in sorted(rows_by_prefix):
        shard_rows = rows_by_prefix[prefix]
        shard_sizes.append(len(shard_rows))
        shard_path = PREFIX_PARTS_DIR / f"{prefix}.json"
        shard_path.write_text(
            json.dumps({"hexes": shard_rows}, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
            encoding="utf-8",
        )

    prefix_manifest = {
        "meta": payload.get("meta", {}),
        "prefix_length": PREFIX_LENGTH,
        "base_path": "/data/map/historical/hex-composition-by-prefix",
        "shard_count": len(rows_by_prefix),
        "min_rows_per_shard": min(shard_sizes) if shard_sizes else 0,
        "max_rows_per_shard": max(shard_sizes) if shard_sizes else 0,
    }
    PREFIX_MANIFEST_PATH.write_text(
        json.dumps(prefix_manifest, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    print(f"Wrote {len(manifest_parts)} hex composition yearly parts under {PARTS_DIR}")
    print(f"Wrote {len(rows_by_prefix)} hex composition prefix shards under {PREFIX_PARTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
