#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "back"
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.manual_available_locales import ManualAvailableLocalesConfig, build_manual_available_locales_dataset
from localizate.paths import DATA_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrae un CSV manual de locales disponibles en Madrid desde Locales.es y lo enriquece con WGS84/H3.",
    )
    parser.add_argument("--city", default="madrid", help="Slug de ciudad en Locales.es.")
    parser.add_argument(
        "--operations",
        nargs="+",
        default=["venta", "alquiler"],
        help="Operaciones a rastrear en Locales.es.",
    )
    parser.add_argument("--max-pages", type=int, default=250, help="Numero maximo de paginas por operacion.")
    parser.add_argument("--max-listings", type=int, default=None, help="Limita el numero final de listings procesados.")
    parser.add_argument(
        "--resume-from-raw",
        action="store_true",
        help="Reutiliza el CSV bruto ya existente y reanuda desde ahi sin volver a rastrear paginas.",
    )
    parser.add_argument(
        "--request-delay-seconds",
        type=float,
        default=0.25,
        help="Pausa entre peticiones al portal de listados.",
    )
    parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=30.0,
        help="Timeout HTTP por peticion de listados/detalle.",
    )
    parser.add_argument(
        "--skip-geocode",
        action="store_true",
        help="Desactiva el geocoding y deja solo el scrape bruto.",
    )
    parser.add_argument(
        "--geocode-delay-seconds",
        type=float,
        default=1.1,
        help="Pausa entre peticiones a Nominatim.",
    )
    parser.add_argument(
        "--contact-email",
        default=None,
        help="Email opcional para identificarte ante Nominatim.",
    )
    parser.add_argument("--h3-resolution", type=int, default=10, help="Resolucion H3 para los puntos geocodificados.")
    parser.add_argument("--output-path", type=Path, default=None, help="CSV final enriquecido.")
    parser.add_argument("--raw-output-path", type=Path, default=None, help="CSV bruto tras el crawl y antes del geocoding.")
    parser.add_argument("--summary-path", type=Path, default=None, help="JSON resumen de la extraccion.")
    parser.add_argument("--geocode-cache-path", type=Path, default=None, help="Cache CSV de geocoding.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    city_slug = args.city.lower().strip()
    sample_suffix = "_sample" if args.max_listings is not None else ""

    output_path = args.output_path or (DATA_DIR / "exports" / f"manual_available_locales_{city_slug}{sample_suffix}.csv")
    raw_output_path = args.raw_output_path or (DATA_DIR / "exports" / f"manual_available_locales_{city_slug}_raw{sample_suffix}.csv")
    summary_path = args.summary_path or (DATA_DIR / "processed" / f"manual_available_locales_{city_slug}_summary{sample_suffix}.json")
    geocode_cache_path = args.geocode_cache_path or (
        DATA_DIR / "intermediate" / f"manual_available_locales_{city_slug}_geocode_cache.csv"
    )

    config = ManualAvailableLocalesConfig(
        city_slug=city_slug,
        operations=tuple(args.operations),
        max_pages=args.max_pages,
        max_listings=args.max_listings,
        resume_from_raw=args.resume_from_raw,
        request_delay_seconds=args.request_delay_seconds,
        request_timeout_seconds=args.request_timeout_seconds,
        geocode_enabled=not args.skip_geocode,
        geocode_delay_seconds=args.geocode_delay_seconds,
        geocode_email=args.contact_email,
        h3_resolution=args.h3_resolution,
    )
    frame, summary = build_manual_available_locales_dataset(
        config,
        output_path=output_path,
        raw_output_path=raw_output_path,
        summary_path=summary_path,
        geocode_cache_path=geocode_cache_path,
    )

    print(f"Wrote raw listing export: {raw_output_path}")
    print(f"Wrote enriched listing export: {output_path}")
    print(f"Wrote extraction summary: {summary_path}")
    print(
        "Summary: "
        f"{summary['listing_count']} listings, "
        f"{summary['geocoded_count']} geocoded, "
        f"{summary['h3_count']} with H3, "
        f"{summary['section_key_count']} with section_key."
    )
    if not frame.empty:
        preview_columns = [
            "operation",
            "listing_id",
            "card_title",
            "price_eur",
            "lat_wgs84",
            "lon_wgs84",
            "h3_cell",
            "section_key",
        ]
        print(frame[preview_columns].head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())