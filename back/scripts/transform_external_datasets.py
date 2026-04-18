"""
Transform and profile external datasets for the Localízate opportunity enrichment.

Reads raw downloads from storage/data/external/, profiles each one, and produces
standardized CSVs ready for integration into the opportunities pipeline.

Output:  storage/data/external/processed/
"""

import os
import json
import csv
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "data", "external")
OUT_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────
# Helper: extract lat/lon from datos.madrid.es JSON
# ─────────────────────────────────────────────────
def parse_madrid_json(filepath: str) -> list[dict]:
    """Parse a datos.madrid.es JSON file and extract key fields + coordinates."""
    import re as _re
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    raw = _re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', raw)
    data = json.loads(raw, strict=False)

    # Typical structure: {"@graph": [...items...], ...}
    items = data.get("@graph", data if isinstance(data, list) else [])
    results = []
    for item in items:
        rec = {
            "id": item.get("id", item.get("@id", "")),
            "title": item.get("title", ""),
        }
        # Address fields
        addr = item.get("address", {})
        if addr:
            rec["district_name"] = addr.get("district", {}).get("@id", "").split("/")[-1] if isinstance(addr.get("district"), dict) else str(addr.get("district", ""))
            rec["neighborhood"] = addr.get("area", {}).get("@id", "").split("/")[-1] if isinstance(addr.get("area"), dict) else str(addr.get("area", ""))
            rec["street"] = addr.get("street-address", "")
            rec["postal_code"] = addr.get("postal-code", "")
            rec["locality"] = addr.get("locality", "")

        # Location
        loc = item.get("location", {})
        if loc:
            rec["lat"] = loc.get("latitude", None)
            rec["lon"] = loc.get("longitude", None)

        # Additional useful fields
        if "organization" in item:
            org = item["organization"]
            rec["organization"] = org.get("organization-name", "") if isinstance(org, dict) else str(org)

        if "relation" in item:
            rel = item["relation"]
            if isinstance(rel, str):
                rec["url"] = rel
            elif isinstance(rel, dict):
                rec["url"] = rel.get("@id", "")

        results.append(rec)
    return results


def process_geo_json(filename: str, category: str) -> dict:
    """Process a geographic JSON file and save as CSV."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return {"status": "SKIP", "reason": "file not found"}

    records = parse_madrid_json(filepath)
    if not records:
        return {"status": "SKIP", "reason": "no records"}

    # Add category
    for r in records:
        r["category"] = category

    # Count valid coordinates
    with_coords = sum(1 for r in records if r.get("lat") and r.get("lon"))

    # Save CSV
    out_name = f"equipamiento_{category}.csv"
    out_path = os.path.join(OUT_DIR, out_name)
    if records:
        keys = list(dict.fromkeys(k for r in records for k in r.keys()))
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)

    return {
        "status": "OK",
        "records": len(records),
        "with_coords": with_coords,
        "output": out_name,
    }


def process_bicimad():
    """Process BiciMAD stations."""
    filepath = os.path.join(DATA_DIR, "bicimad_estaciones.json")
    if not os.path.exists(filepath):
        return {"status": "SKIP"}

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    records = []
    for feat in features:
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [None, None])
        records.append({
            "station_id": props.get("numero") or props.get("gid", ""),
            "name": props.get("nombre", props.get("name", "")),
            "address": props.get("direccion", props.get("address", "")),
            "bases": props.get("num_bases", props.get("bases", "")),
            "district": props.get("distrito", ""),
            "lon": coords[0] if len(coords) >= 2 else None,
            "lat": coords[1] if len(coords) >= 2 else None,
            "category": "bicimad",
        })

    if records:
        out_path = os.path.join(OUT_DIR, "equipamiento_bicimad.csv")
        keys = list(records[0].keys())
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)

    return {"status": "OK", "records": len(records), "output": "equipamiento_bicimad.csv"}


def process_iae():
    """Process IAE (business tax) data."""
    filepath = os.path.join(DATA_DIR, "iae_2025.csv")
    if not os.path.exists(filepath):
        return {"status": "SKIP"}

    # Read and profile
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # Try different delimiters
    for delim in [";", ",", "\t"]:
        lines = content.strip().split("\n")
        if delim in lines[0]:
            reader = csv.DictReader(lines, delimiter=delim)
            records = list(reader)
            break
    else:
        records = []

    if not records:
        return {"status": "SKIP", "reason": "could not parse"}

    # Copy as-is for now, just with standard encoding
    out_path = os.path.join(OUT_DIR, "iae_empresas_2025.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    return {
        "status": "OK",
        "records": len(records),
        "columns": list(records[0].keys()),
        "output": "iae_empresas_2025.csv",
    }


def process_poblacion():
    """Process population by district and barrio data."""
    filepath = os.path.join(DATA_DIR, "poblacion_distrito_barrio.csv")
    if not os.path.exists(filepath):
        return {"status": "SKIP"}

    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    for delim in [";", ",", "\t"]:
        lines = content.strip().split("\n")
        if delim in lines[0]:
            reader = csv.DictReader(lines, delimiter=delim)
            records = list(reader)
            break
    else:
        records = []

    if not records:
        return {"status": "SKIP", "reason": "could not parse"}

    out_path = os.path.join(OUT_DIR, "poblacion_distrito_barrio.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    return {
        "status": "OK",
        "records": len(records),
        "columns": list(records[0].keys()),
        "years": len(set(r.get("Año", r.get("año", r.get("year", ""))) for r in records if any(r.get(k) for k in ["Año", "año", "year"]))),
        "output": "poblacion_distrito_barrio.csv",
    }


def process_inspecciones_consumo():
    """Process consumer inspections data."""
    filepath = os.path.join(DATA_DIR, "inspecciones_consumo.csv")
    if not os.path.exists(filepath):
        return {"status": "SKIP"}

    with open(filepath, "r", encoding="latin-1") as f:
        content = f.read()

    for delim in [";", ",", "\t"]:
        lines = content.strip().split("\n")
        if delim in lines[0]:
            reader = csv.DictReader(lines, delimiter=delim)
            records = list(reader)
            break
    else:
        records = []

    if not records:
        return {"status": "SKIP", "reason": "could not parse"}

    out_path = os.path.join(OUT_DIR, "inspecciones_consumo.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    return {
        "status": "OK",
        "records": len(records),
        "columns": list(records[0].keys())[:10],
        "output": "inspecciones_consumo.csv",
    }


def process_panel_indicadores():
    """Profile the large panel de indicadores CSV."""
    filepath = os.path.join(DATA_DIR, "panel_indicadores_2020_2025.csv")
    if not os.path.exists(filepath):
        return {"status": "SKIP"}

    size_mb = os.path.getsize(filepath) / (1024 * 1024)

    with open(filepath, "r", encoding="utf-8-sig") as f:
        # Read just the header and a few lines to profile
        reader = csv.reader(f, delimiter=";")
        header = next(reader, [])
        if not header or ";" not in header[0]:
            # Try comma
            f.seek(0)
            reader = csv.reader(f, delimiter=",")
            header = next(reader, [])

        sample_rows = []
        for i, row in enumerate(reader):
            if i < 5:
                sample_rows.append(row)
            if i >= 100:
                break
        total_approx = i + 1

    # Count total lines
    with open(filepath, "r", encoding="utf-8-sig") as f:
        total_lines = sum(1 for _ in f)

    return {
        "status": "OK",
        "size_mb": round(size_mb, 1),
        "total_lines": total_lines,
        "columns": len(header),
        "column_names_sample": header[:15] if header else [],
        "note": "Large file - kept as-is in storage/data/external/ for selective loading",
    }


def create_unified_equipamientos():
    """Create a single unified CSV of all point-of-interest equipamientos."""
    all_records = []
    processed_dir = OUT_DIR

    for fname in os.listdir(processed_dir):
        if fname.startswith("equipamiento_") and fname.endswith(".csv"):
            fpath = os.path.join(processed_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    lat = row.get("lat", "")
                    lon = row.get("lon", "")
                    if lat and lon and lat != "None" and lon != "None":
                        try:
                            all_records.append({
                                "category": row.get("category", ""),
                                "title": row.get("title", row.get("name", "")),
                                "district_name": row.get("district_name", row.get("district", "")),
                                "neighborhood": row.get("neighborhood", ""),
                                "lat": float(lat),
                                "lon": float(lon),
                                "street": row.get("street", row.get("address", "")),
                            })
                        except (ValueError, TypeError):
                            pass

    if all_records:
        out_path = os.path.join(processed_dir, "unified_equipamientos_geo.csv")
        keys = ["category", "title", "district_name", "neighborhood", "lat", "lon", "street"]
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_records)

    return {"total_points": len(all_records)}


def main():
    report = {}

    print("="*70)
    print("  Processing external datasets")
    print("="*70)

    # 1. Geographic equipment JSONs
    geo_files = [
        ("mercados_municipales.json", "mercados"),
        ("parques_jardines.json", "parques"),
        ("centros_culturales.json", "centros_culturales"),
        ("instalaciones_deportivas.json", "instalaciones_deportivas"),
        ("polideportivos.json", "polideportivos"),
        ("colegios_publicos.json", "colegios"),
        ("bibliotecas.json", "bibliotecas"),
        ("centros_mayores.json", "centros_mayores"),
        ("centros_servicios_sociales.json", "servicios_sociales"),
        ("aparcamientos_publicos.json", "aparcamientos"),
        ("mercadillos_via_publica.json", "mercadillos"),
    ]

    print("\n--- Geographic equipamientos ---")
    for fname, cat in geo_files:
        result = process_geo_json(fname, cat)
        report[f"geo_{cat}"] = result
        status = result['status']
        count = result.get('records', 0)
        coords = result.get('with_coords', 0)
        print(f"  {status:4s}  {cat:<30s}  {count:>5d} records  ({coords} geocoded)")

    # 2. BiciMAD
    print("\n--- BiciMAD ---")
    result = process_bicimad()
    report["bicimad"] = result
    print(f"  {result['status']}  {result.get('records', 0)} stations")

    # 3. IAE
    print("\n--- IAE (Impuesto Actividades Económicas) ---")
    result = process_iae()
    report["iae"] = result
    if result["status"] == "OK":
        print(f"  OK  {result['records']} records")
        print(f"  Columns: {result['columns']}")

    # 4. Población
    print("\n--- Población por distrito y barrio ---")
    result = process_poblacion()
    report["poblacion"] = result
    if result["status"] == "OK":
        print(f"  OK  {result['records']} records")
        print(f"  Columns: {result['columns'][:8]}")

    # 5. Inspecciones de consumo
    print("\n--- Inspecciones de consumo ---")
    result = process_inspecciones_consumo()
    report["inspecciones_consumo"] = result
    if result["status"] == "OK":
        print(f"  OK  {result['records']} records")
        print(f"  Columns: {result['columns']}")

    # 6. Panel de indicadores
    print("\n--- Panel de indicadores de distritos y barrios ---")
    result = process_panel_indicadores()
    report["panel_indicadores"] = result
    if result["status"] == "OK":
        print(f"  OK  {result['size_mb']}MB, {result['total_lines']} lines, {result['columns']} columns")
        print(f"  Sample columns: {result['column_names_sample']}")

    # 7. Unified equipamientos
    print("\n--- Creating unified equipamientos ---")
    uni_result = create_unified_equipamientos()
    report["unified_equipamientos"] = uni_result
    print(f"  {uni_result['total_points']} total geocoded points")

    # Save report
    report_path = os.path.join(OUT_DIR, "_processing_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*70}")
    print(f"  Processing complete. Report: {report_path}")
    print(f"{'='*70}")

    return report


if __name__ == "__main__":
    main()
