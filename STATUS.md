# STATUS.md (Fuente Canonica)

Este archivo es la fuente unica y viva de contexto del proyecto. Se actualiza en cada avance y reemplaza al resto de documentos como referencia primaria.

Ultima actualizacion: 2026-03-12

## Identidad del proyecto

- Nombre de repo: Localizate
- Nombre de proyecto: Madrid Local Predict (premios datos abiertos 2026)
- Objetivo: macro DB historica de locales comerciales de Madrid, enriquecida con variables socioeconomicas y geoespaciales, para predecir supervivencia y servir un mapa interactivo.

## Enfoque unificado (resolviendo inconsistencias)

- Datos crudos ya estan descargados en `DB/`. No se usa `data/raw/` ni descarga automatica en este momento.
- La ingesta canonica se basa en `scripts/build_raw_inventory.py` y el manifest `data/intermediate/raw_manifest.csv`.
- El corte de pureza del censo es 2015-01.
- El CRS del censo cambia en 2017-09 (ED50 -> ETRS89). Todo join espacial debe normalizar CRS antes de H3 o distancias.
- Modelo previsto: Survival Analysis (RSF o Gradient Boosting) con point-in-time joins.
- Visualizacion: H3 res 10 para mapa; punto exacto para features de distancia.
- Outputs en batch (mapa de calor + locales vacios) para servir con Streamlit.
- LLM es capa opcional para explicacion; no bloquea pipeline de datos.

## Estado actual (hecho)

- Inventario y manifest canonico raw generados (ver `docs/raw_data_inventory.md`).
- Manifest historico del censo `locales+actividades` desde 2015-01, con CRS por periodo.
- Perfilado de snapshots del censo y materializacion puntual de periodos clave.
- Cobertura de claves de seccion entre censo/padron/renta calculada.
- Metadata geografica de secciones materializada desde shapefile (colapsando multipartes).
- Capa socioeconomica en codigo: normaliza padron, agrega demografia, integra renta y geografia.
- Contexto legado consolidado en este archivo; carpeta `Context/` eliminada para simplificar el repo.
- Documentacion DB movida a `docs/documentacion_db/` para estandarizar nombres.

## Problemas y riesgos actuales

- `actividades` falta en 2017-12 y 2022-04.
- Observacion manual: algunos CSV antiguos en `DB/actividades` parecen vacios. Falta confirmacion automatica.
- Shapefile de secciones no cubre todo el universo actual del censo (2461 vs 2499 en 2026-03).
- `renta` llega solo hasta 2023; hay que definir carry-forward.
- Build historico completo de `padron` es lento; requiere optimizacion (DuckDB o cache mensual).
- Stack geoespacial pesado aun no instalado en la venv (pyarrow/geopandas).

## Punto exacto en el que estamos

1. Infraestructura canonica y auditoria inicial completadas.
2. Geografia de secciones materializada y comparada contra censo/padron/renta.
3. Panel socioeconomico listo en codigo, pendiente de materializacion historica eficiente.
4. ABT, H3, modelo y frontend aun no implementados.

## Siguientes pasos inmediatos

1. Confirmar programaticamente CSV vacios en `DB/actividades` y documentar el impacto.
2. Optimizar el build historico de `padron` y materializar:
   - `data/processed/padron_section_panel.csv`
   - `data/processed/section_socioeconomic_panel.csv`
3. Materializar historico completo de `locales` y `actividades` normalizados.
4. Normalizar CRS y generar `lat/lon` + H3.
5. Disenar ABT de supervivencia y comenzar modelado.

## Comandos utiles

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -u scripts/build_raw_inventory.py
PYTHONPATH=src .venv/bin/python -u scripts/build_censo_snapshot_manifest.py
PYTHONPATH=src .venv/bin/python -u scripts/build_section_geography.py
PYTHONPATH=src .venv/bin/python -u scripts/build_section_socioeconomic_panel.py
```

## Apéndices (verbatim, preservados)

### README.md (snapshot)

````markdown
# Localizate

Nota: la fuente canonica y actualizada del contexto es `STATUS.md`. Este README se mantiene pero puede quedar desactualizado.

Base de datos analitica para construir una macro DB historica de locales comerciales de Madrid, enriquecerla con variables geoespaciales y socioeconomicas, y servir predicciones de supervivencia para un mapa interactivo.

## Estado actual

- Auditoria inicial del repo completada.
- Datos brutos disponibles localmente en `DB/`.
- Contexto funcional legado consolidado dentro de `STATUS.md`.
- Documentacion original de fuentes revisada en `docs/documentacion_db/`.
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
- `STATUS.md`: fuente canonica con contexto legado embebido.
- `docs/documentacion_db/`: PDFs originales de diccionario/metodologia.
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
````

### Context/Intro_Roadmap.md (snapshot)

````markdown
# CONTEXTO GENERAL Y ROADMAP DEL PROYECTO: "MADRID LOCAL PREDICT"

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PREMIOS A LA REUTILIZACIÓN DE DATOS ABIERTOS - AYUNTAMIENTO DE MADRID 2026

## ESTADO REAL (Mar 2026)

- Datos crudos ya disponibles en `DB/` (no se usa `data/raw/`).
- Inventario canonico y manifest raw generados: `data/intermediate/raw_inventory.csv` y `data/intermediate/raw_manifest.csv`.
- Manifest historico del censo desde 2015-01 con cambio de CRS en `2017-09`.
- Cobertura de claves de seccion y metadata geografica materializadas.
- Capa socioeconomica (`padron` + `renta` + secciones) implementada en codigo, pero el build historico completo es lento y requiere optimizacion antes de materializar.
- ABT, modelo y frontend aun no implementados.
````

### Context/Data_Processing.md (snapshot)

````markdown
# CONTEXTO TÉCNICO: SCRIPT DE DESCARGA E INGESTA AUTOMÁTICA

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Datos Abiertos Ayuntamiento de Madrid)

## ESTADO REAL (Mar 2026)

- Los datos ya estan descargados en `DB/` y no se usa `data/raw/`.
- La ingesta canonica se hace con `scripts/build_raw_inventory.py`, que genera `data/intermediate/raw_inventory.csv` y `data/intermediate/raw_manifest.csv`.
- La seleccion correcta de `avisos` se resuelve con metadata CKAN (ver `src/localizate/ckan.py`).
- Hay indicios de que algunos CSV antiguos de `DB/actividades` estan vacios; pendiente de confirmacion automatica.
````

### Context/Feature_Engineering.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 2: INGENIERÍA DE VARIABLES Y MODELADO ESPACIO-TEMPORAL

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Normalizacion del censo implementada en `src/localizate/censo.py` con cambio de CRS en `2017-09` y columnas de coordenadas `x_utm_best/y_utm_best`.
- Metadata de secciones censales materializada en `data/processed/section_geography.csv`.
- Capa socioeconomica por seccion implementada en codigo (`src/localizate/socioeconomics.py`), pero el build historico completo es lento y necesita optimizacion.
- No se han generado H3 ni features espaciales finales.
````

### Context/Model_Training.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 3: ENTRENAMIENTO Y EVALUACIÓN DEL MODELO (SURVIVAL ANALYSIS)

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Todavia no hay ABT ni dataset de entrenamiento listo.
- No se ha entrenado ningun modelo.
- Este documento queda como plan; las decisiones finales dependen de cerrar el panel socioeconomico y la tabla historica de locales.
````

### Context/Generacion_Outputs.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 4: INFERENCIA BATCH Y GENERACIÓN DE BASE DE DATOS FINAL

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Esta fase aun no se ha iniciado porque falta ABT y modelo entrenado.
- Mantener este documento como guia futura; puede cambiar al conocer la capacidad real del panel socioeconomico.
````

### Context/Frontend.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 5: DESARROLLO FRONTEND (STREAMLIT) Y CAPA AGÉNTICA

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Frontend aun no iniciado.
- Esta guia asume que ya existen outputs batch y modelo entrenado; ambos siguen pendientes.
````
