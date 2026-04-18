"""
Download external datasets from datos.madrid.es for opportunity enrichment.

Selected datasets:
1. IAE - Empresas por epígrafe de actividad económica (business tax base by activity)
2. Panel de indicadores de distritos y barrios (comprehensive socioeconomic panel)
3. IGUALA - Índice de vulnerabilidad territorial (urban vulnerability index)
4. Ranking de vulnerabilidad de distritos y barrios
5. Mercados municipales (GEO) - anchor commerce infrastructure
6. Principales parques y jardines (GEO) - green spaces
7. Centros Culturales Municipales (GEO) - cultural centers
8. Instalaciones Deportivas Básicas (GEO) - sports facilities
9. Colegios Públicos (GEO) - public schools
10. Estaciones BiciMAD (GEO) - bike sharing stations
11. Alojamientos turísticos (esmadrid.com)
12. Restaurantes con perfil turístico (esmadrid.com)
13. Puntos de interés turístico (esmadrid.com)
14. Población por distrito y barrio
15. Inspecciones de consumo
16. Terrazas y locales de ocio nocturno turístico
"""

import os
import json
import time
import urllib.request
import urllib.error
import ssl

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "external")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# datos.madrid.es catalog CSV -> we use known resource URLs
# Format: (filename, url, description)
DATASETS = [
    # --- ECONOMÍA Y COMERCIO ---
    (
        "iae_empresas_actividad_economica.csv",
        "https://datos.madrid.es/egob/catalogo/204307-0-iae-2013.csv",
        "IAE: Empresas por epígrafe actividad económica por distrito/barrio",
    ),
    (
        "mercados_municipales.json",
        "https://datos.madrid.es/egob/catalogo/200967-0-mercados.json",
        "Mercados municipales con coordenadas",
    ),
    (
        "inspecciones_consumo.csv",
        "https://datos.madrid.es/egob/catalogo/300079-0-inspecciones-consumo.csv",
        "Inspecciones de consumo en establecimientos",
    ),
    (
        "comercios_centenarios.csv",
        "https://datos.madrid.es/egob/catalogo/300290-0-comercios-centenarios.csv",
        "Comercios centenarios de Madrid",
    ),

    # --- SOCIODEMOGRÁFICO ---
    (
        "panel_indicadores_distritos_barrios.csv",
        "https://datos.madrid.es/egob/catalogo/300087-0-indicadores-distritos.csv",
        "Panel indicadores socioeconómicos distritos y barrios",
    ),
    (
        "iguala_vulnerabilidad.xlsx",
        "https://datos.madrid.es/egob/catalogo/300577-0-iguala-vulnerabilidad.xlsx",
        "IGUALA: Índice de vulnerabilidad territorial agregado",
    ),
    (
        "ranking_vulnerabilidad.csv",
        "https://datos.madrid.es/egob/catalogo/300301-0-ranking-vulnerabilidad.csv",
        "Ranking vulnerabilidad distritos y barrios",
    ),
    (
        "poblacion_distrito_barrio.csv",
        "https://datos.madrid.es/egob/catalogo/300557-0-poblacion-distrito-barrio.csv",
        "Población por distrito y barrio a 1 de enero",
    ),

    # --- EQUIPAMIENTOS (GEO) ---
    (
        "parques_jardines.json",
        "https://datos.madrid.es/egob/catalogo/200761-0-parques-jardines.json",
        "Principales parques y jardines municipales con coordenadas",
    ),
    (
        "centros_culturales.json",
        "https://datos.madrid.es/egob/catalogo/200304-0-centros-culturales.json",
        "Centros culturales municipales con coordenadas",
    ),
    (
        "instalaciones_deportivas.json",
        "https://datos.madrid.es/egob/catalogo/200215-0-instalaciones-deportivas.json",
        "Instalaciones deportivas básicas municipales con coordenadas",
    ),
    (
        "polideportivos.json",
        "https://datos.madrid.es/egob/catalogo/200186-0-polideportivos.json",
        "Centros deportivos municipales (polideportivos) con coordenadas",
    ),
    (
        "colegios_publicos.json",
        "https://datos.madrid.es/egob/catalogo/202311-0-colegios-publicos.json",
        "Colegios públicos de Madrid con coordenadas",
    ),
    (
        "bibliotecas.json",
        "https://datos.madrid.es/egob/catalogo/201747-0-bibliobuses-bibliotecas.json",
        "Bibliotecas de Madrid con coordenadas",
    ),
    (
        "centros_mayores.json",
        "https://datos.madrid.es/egob/catalogo/200337-0-centros-mayores.json",
        "Centros municipales de mayores con coordenadas",
    ),
    (
        "centros_servicios_sociales.json",
        "https://datos.madrid.es/egob/catalogo/209094-0-centros-servicios-sociales.json",
        "Centros de servicios sociales municipales con coordenadas",
    ),

    # --- TRANSPORTE Y MOVILIDAD ---
    (
        "bicimad_estaciones.json",
        "https://datos.madrid.es/egob/catalogo/208327-0-transporte-bicicletas-bicimad.json",
        "Estaciones BiciMAD con coordenadas",
    ),
    (
        "aparcamientos_publicos.json",
        "https://datos.madrid.es/egob/catalogo/300531-0-aparcamientos-publicos.json",
        "Aparcamientos públicos municipales disuasorios con coordenadas",
    ),
    (
        "paradas_taxi.csv",
        "https://datos.madrid.es/egob/catalogo/208094-0-reserva-paradas-taxis.csv",
        "Reservas de paradas de taxi con coordenadas",
    ),

    # --- TURISMO ---
    (
        "alojamientos_turisticos.xml",
        "https://datos.madrid.es/egob/catalogo/300032-0-turismo-alojamientos.xml",
        "Alojamientos turísticos (esmadrid.com) con coordenadas",
    ),
    (
        "restaurantes_turisticos.xml",
        "https://datos.madrid.es/egob/catalogo/300033-0-turismo-restauracion.xml",
        "Restaurantes con perfil turístico con coordenadas",
    ),
    (
        "puntos_interes_turistico.xml",
        "https://datos.madrid.es/egob/catalogo/300030-0-puntos-interes-turistico.xml",
        "Puntos de interés turístico de Madrid con coordenadas",
    ),
    (
        "ocio_nocturno_turistico.xml",
        "https://datos.madrid.es/egob/catalogo/300035-0-turismo-nocturno.xml",
        "Locales de ocio nocturno con perfil turístico con coordenadas",
    ),

    # --- MEDIO AMBIENTE ---
    (
        "superficie_parques_zonas_verdes.csv",
        "https://datos.madrid.es/egob/catalogo/300266-0-arbolado-superficie.csv",
        "Superficie de parques y zonas verdes por distrito",
    ),
    (
        "inventario_zonas_verdes.csv",
        "https://datos.madrid.es/egob/catalogo/300153-0-zonas-verdes-inventario.csv",
        "Inventario de zonas verdes",
    ),

    # --- URBANISMO ---
    (
        "barrios_madrid.csv",
        "https://datos.madrid.es/egob/catalogo/300496-0-barrios-madrid.csv",
        "Barrios municipales de Madrid (delimitación + códigos)",
    ),
    (
        "mercadillos_via_publica.json",
        "https://datos.madrid.es/egob/catalogo/202105-0-mercadillos.json",
        "Mercadillos en vía pública con coordenadas",
    ),

    # --- SEGURIDAD E INSPECCIONES ---
    (
        "inspecciones_urbanisticas.csv",
        "https://datos.madrid.es/egob/catalogo/300373-0-inspecciones-urbanisticas.csv",
        "Inspecciones urbanísticas",
    ),
    (
        "inspecciones_lepar.csv",
        "https://datos.madrid.es/egob/catalogo/300160-0-inspecciones-industrias-lepar.csv",
        "Inspecciones de locales sujetos a Ley de espectáculos",
    ),
]

# Create SSL context that doesn't verify (datos.madrid.es sometimes has cert issues)
ctx = ssl.create_default_context()
ctx.check_hostname = True
ctx.verify_mode = ssl.CERT_REQUIRED


def download_file(url: str, filepath: str, description: str) -> bool:
    """Download a file from URL. Returns True on success."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; Localízate/1.0; research)",
                "Accept": "*/*",
            },
        )
        with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
            data = response.read()
            with open(filepath, "wb") as f:
                f.write(data)
            size_kb = len(data) / 1024
            print(f"  OK  {size_kb:>8.1f} KB  {os.path.basename(filepath)}")
            return True
    except urllib.error.HTTPError as e:
        print(f"  FAIL HTTP {e.code}  {os.path.basename(filepath)}  ({url})")
        return False
    except Exception as e:
        print(f"  FAIL {type(e).__name__}: {e}  {os.path.basename(filepath)}")
        return False


def main():
    print(f"\n{'='*70}")
    print("  Downloading external datasets from datos.madrid.es")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Datasets: {len(DATASETS)}")
    print(f"{'='*70}\n")

    successes = []
    failures = []

    for filename, url, description in DATASETS:
        filepath = os.path.join(OUTPUT_DIR, filename)
        print(f"  [{len(successes)+len(failures)+1}/{len(DATASETS)}] {description}")
        ok = download_file(url, filepath, description)
        if ok:
            successes.append((filename, description))
        else:
            failures.append((filename, url, description))
        time.sleep(0.3)  # Be polite to the server

    print(f"\n{'='*70}")
    print(f"  Results: {len(successes)} OK, {len(failures)} FAILED")
    print(f"{'='*70}")

    if failures:
        print("\nFailed downloads:")
        for fn, url, desc in failures:
            print(f"  - {fn}: {url}")

    # Save manifest
    manifest = {
        "downloaded": [
            {"file": fn, "description": desc} for fn, desc in successes
        ],
        "failed": [
            {"file": fn, "url": url, "description": desc}
            for fn, url, desc in failures
        ],
    }
    manifest_path = os.path.join(OUTPUT_DIR, "_download_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\nManifest saved to {manifest_path}")


if __name__ == "__main__":
    main()
