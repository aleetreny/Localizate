from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


CKAN_PACKAGE_SHOW_URL = "https://datos.madrid.es/api/3/action/package_show"
AVISOS_DATASET_ID = "212411-0-madrid-avisa"
AVISOS_CODE_PATTERN = re.compile(r"^(?P<resource_code>212411-\d+)")
AVISOS_YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")


def fetch_dataset_resources(dataset_id: str, timeout: int = 60) -> list[dict[str, Any]]:
    query = urlencode({"id": dataset_id})
    with urlopen(f"{CKAN_PACKAGE_SHOW_URL}?{query}", timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["result"]["resources"]


def fetch_avisos_resource_metadata(timeout: int = 60) -> pd.DataFrame:
    rows = fetch_dataset_resources(AVISOS_DATASET_ID, timeout=timeout)
    normalized_rows: list[dict[str, Any]] = []

    for row in rows:
        name = row.get("name", "")
        match = AVISOS_CODE_PATTERN.match(name)
        if not match:
            continue

        description = row.get("description") or ""
        description_lower = description.lower()
        year_match = AVISOS_YEAR_PATTERN.search(description)

        if "recibidos" in description_lower:
            delivery_type = "recibidos"
        elif "tramitados" in description_lower:
            delivery_type = "tramitados"
        else:
            delivery_type = None

        if "(sic)" in description_lower:
            system = "SIC"
        elif "(avisa)" in description_lower:
            system = "AVISA"
        else:
            system = None

        normalized_rows.append(
            {
                "resource_id": match.group("resource_code"),
                "ckan_name": name,
                "ckan_description": description,
                "avisos_year_from_ckan": int(year_match.group(1)) if year_match else None,
                "avisos_delivery_type": delivery_type,
                "avisos_system": system,
            }
        )

    return pd.DataFrame(normalized_rows)


def enrich_inventory_with_avisos_metadata(inventory: pd.DataFrame, timeout: int = 60) -> pd.DataFrame:
    if inventory.empty or "source_name" not in inventory.columns:
        return inventory

    avisos_inventory = inventory[inventory["source_name"] == "avisos"]
    if avisos_inventory.empty:
        return inventory

    avisos_metadata = fetch_avisos_resource_metadata(timeout=timeout)
    if avisos_metadata.empty:
        return inventory

    return inventory.merge(avisos_metadata, how="left", on="resource_id")
