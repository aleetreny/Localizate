# Localizate

Base de datos analitica para construir una macro DB historica de locales comerciales de Madrid, enriquecerla con variables geoespaciales y socioeconomicas, y servir predicciones de supervivencia para un mapa interactivo.

## Estado actual

- Auditoria inicial del repo completada.
- Datos brutos disponibles localmente en `DB/`.
- Contexto funcional revisado en `Context/`.
- Documentacion original de fuentes revisada en `Documentación DB/`.
- Inventario canonico raw, manifest del censo y cobertura de `section_key` ya implementados.
- Metadata geografica de secciones materializada desde el shapefile y validada contra censo, padron y renta.
- Capa socioeconomica (`padron` + `renta` + metadata de secciones) implementada en codigo, pendiente de optimizacion para materializar toda la serie historica de forma eficiente.

## Estructura del repo

- `src/localizate/`: paquete Python principal.
- `scripts/`: scripts operativos y CLI.
- `configs/`: configuracion declarativa.
- `data/intermediate/`: tablas normalizadas temporales.
- `data/features/`: features listas para ensamblar la ABT.
- `data/processed/`: datasets maestros y tablas consolidadas.
- `data/exports/`: salidas para mapa, API o app.
- `models/`: artefactos entrenados.
- `apps/streamlit/`: frontend inicial y exploracion visual.
- `tests/`: pruebas.
- `docs/`: auditoria, bitacora y decisiones.
- `Context/`: contexto funcional legado.
- `Documentación DB/`: PDFs originales de diccionario/metodologia.
- `DB/`: data lake bruto legacy ya descargado en local.

## Hallazgos tecnicos importantes

- El censo de locales cambia de sistema de referencia a mitad de septiembre de 2017; antes de calcular H3, distancias o joins espaciales hay que normalizar CRS.
- `padron` viene duplicado en muchos meses (`csv` y `txt`) y necesita una version canonica por mes.
- `actividades` no cubre todos los meses presentes en `locales`; faltan al menos `2017_12` y `2022_04`.
- La renta disponible llega hasta 2023, asi que para escenarios actuales habra que congelar o imputar con criterio explicito.
- Los datos brutos mezclan encodings, sufijos de fichero y variantes funcionales del mismo dataset.
- El shapefile de secciones censales no cubre todo el universo actual del censo: tras colapsar multipartes quedan `2461` secciones unicas frente a `2499` en el censo `2026-03`.
- La primera version del build socioeconomico completo es correcta pero demasiado lenta; hay que pasarla a una estrategia incremental o con DuckDB antes de usarla como paso operativo frecuente.

## Entorno

El proyecto se fija de momento en Python `3.12` por compatibilidad con el stack geoespacial y `scikit-survival`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Proximos pasos inmediatos

1. Definir una capa de lectura canonica para cada fuente: encoding, separador, CRS y esquema final.
2. Normalizar `locales` y `actividades` en una tabla historica mensual consistente.
3. Resolver la estrategia de seccion censal: join robusto entre `locales`, `padron`, `renta` y shapefile.
4. Crear la capa geoespacial base: reproyeccion a ETRS89, conversion a lat/lon y asignacion H3.
5. Optimizar y materializar el panel socioeconomico historico por seccion.
6. Diseñar la ABT de entrenamiento y las salidas batch para mapa y locales vacios.

## Documentacion viva

- Auditoria inicial: `docs/auditoria_inicial.md`
- Inventario canonico de fuentes raw: `docs/raw_data_inventory.md`
- Manifest canonico del censo historico: `docs/censo_snapshot_manifest.md`
- Perfil operativo de snapshots del censo: `docs/censo_snapshot_profile.md`
- Cobertura de claves de seccion: `docs/section_key_coverage.md`
- Geografia de secciones y cobertura: `docs/section_geography.md`
- Hoja de ruta operativa: `docs/roadmap.md`
- Bitacora resumida del proyecto: `docs/project_log.md`

## Scripts utiles

- `scripts/build_raw_inventory.py`: escanea `DB/`, infiere encoding/delimitador, construye inventario canonico y selecciona el fichero valido por periodo.
- `scripts/build_censo_snapshot_manifest.py`: construye el manifest historico de snapshots `locales + actividades` desde 2015-01 y etiqueta el estado CRS por periodo.
- `scripts/profile_censo_snapshots.py`: perfila calidad de snapshots del censo y puede materializar periodos normalizados bajo `data/intermediate/censo_snapshots/`.
- `scripts/profile_section_keys.py`: compara el solape de claves de seccion entre censo, padron y renta.
- `scripts/build_section_geography.py`: extrae metadata canonica del shapefile de secciones y mide cobertura frente a censo, padron y renta.
- `scripts/build_section_socioeconomic_panel.py`: construye el panel por seccion a partir de `padron`, `renta` y metadata geografica; actualmente funciona pero necesita optimizacion para series completas.
