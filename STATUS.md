# STATUS.md (Fuente Canonica)

Este archivo es la fuente unica y viva de contexto del proyecto. Se actualiza en cada avance y reemplaza al resto de documentos como referencia primaria.

Ultima actualizacion: 2026-03-13

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
- Contrato operativo ABT + Point-in-Time definido en `docs/abt_pit_contract.md` para evitar leakage temporal y fijar reglas de join/fallback.
- Fase 1 completada: paneles `padron_section_panel` y `section_socioeconomic_panel` materializados en `data/processed/`.
- Build de `padron` optimizado con cache incremental mensual en `data/intermediate/padron_section_panel/` (un fichero agregado por periodo).
- Fase 2 arrancada: creado pipeline de materializacion historica normalizada del censo en `scripts/build_censo_historical_normalized.py`.
- Plan historico de ejecucion generado en `data/processed/censo_historical_materialization_manifest.csv` y `docs/censo_historical_materialization.md`.
- Plan actual fase 2: `264` tareas (`132` periodos x `locales/actividades`), con `257` pendientes de materializar, `5` ya cacheadas y `2` sin `actividades` por huecos historicos (`2017-12`, `2022-04`).
- Fase 2 cerrada: manifest historico sin pendientes (`planned_materialize = 0`), con `257` materializados, `5` cacheados y `2` ausentes en manifest de `actividades`.
- Fase 3 cerrada: pipeline geoespacial implementado y materializado en historico completo (`132` periodos del manifest).
- Salida geoespacial consolidada en `data/processed/censo_geospatial/` con manifest en `data/processed/censo_geospatial_manifest.csv`.
- Resultado fase 3: `131` periodos materializados + `1` cacheado, `20,212,017` filas procesadas, `18,873,903` filas con coordenadas WGS84 + H3.
- En `2017-09` se aplica politica conservadora por defecto (`transition_policy=skip`), quedando `142,878` filas marcadas para revision de transicion CRS.
- Robustez operativa añadida: si un snapshot normalizado `locales` esta corrupto, se rematerializa automaticamente y se reintenta lectura.
- Fase ABT iniciada: generado baseline de supervivencia por local en `data/features/local_survival_abt.csv` (`203,870` filas, censura global `2026-03`).
- Reporte ABT disponible en `docs/abt_survival.md` con metricas iniciales de evento/duracion y cobertura de features.
- Verificacion automatica de `DB/actividades`: `134` ficheros detectados y `0` vacios fisicos (`size_0`/cabecera en blanco).
- Politicas cerradas para modelado:
	- CRS transicion `2017-09`: `exclude_transition` en entrenamiento.
	- Renta post-2023: `renta_max_year=2023` + imputacion jerarquica (`district_median` -> `city_median`).
- Siguiente bloque ejecutado: baseline de scoring survival en `scripts/train_survival_baseline.py`.
- Artefactos baseline generados:
	- `data/exports/local_survival_scores.csv`
	- `models/survival_baseline_metrics.json`
	- `docs/survival_baseline.md`
- Resultado baseline heuristico:
	- Filas modeladas: `203,828` (42 bloqueadas por transicion CRS)
	- Split temporal adaptativo (event-aware): train `149,684`, valid `2,242`, test `51,902`
	- Eventos por split: train `779`, valid `4`, test `6`
	- C-index sampled: train `0.5252`, valid `0.5078`, test `0.5690`
	- Quality gate baseline: `pass` (sin `NaN` en C-index)
- README publico actualizado con narrativa no tecnica del proyecto (que hacemos, por que y estado para presentacion externa).
- Nuevo gate continuo de preparacion a modelado: `scripts/run_modeling_readiness.py` -> `docs/modeling_readiness.md` + `models/modeling_readiness.json`.
- Estado readiness actual: `ready_with_caveats` (pipeline util, pero con eventos escasos en valid/test para evaluacion robusta).
- Intento de habilitar stack canonico (`scipy`, `scikit-learn`, `scikit-survival`) bloqueado por entorno (fallo de instalacion de paquetes en la venv).
- Baseline enriquecido con evaluacion por horizontes (`6/12/24` meses) y resumen de calibracion por buckets de riesgo.
- README publico reforzado con bitacora narrativa por iteraciones (enfoque explicativo para presentacion externa).
- Stack survival canonico desbloqueado en venv: `scipy`, `scikit-learn`, `scikit-survival` instalados.
- Nuevo bloque completado: entrenamiento canonico `Cox + RSF + GBSA` en `scripts/train_survival_canonical.py`.
- Artefactos canonicos generados:
	- `models/survival_canonical_metrics.json`
	- `docs/survival_canonical.md`
	- `data/exports/local_survival_map_export.csv`
- Export final para mapa consolidada con score y banderas de calidad:
	- scores: `risk_cox`, `risk_rsf`, `risk_gbsa`, `risk_ensemble`
	- calidad: `quality_flag_transition`, `quality_flag_missing_h3`, `quality_flag_renta_imputed`, `quality_tier`
- Resultado canonical (C-index ensemble): train `0.5246`, valid `0.6637`, test `0.5050`.
- Suite actual de pruebas: `31/31` OK.
- Contexto legado consolidado en este archivo; carpeta `Context/` eliminada para simplificar el repo.
- Documentacion DB movida a `docs/documentacion_db/` para estandarizar nombres.

## Problemas y riesgos actuales

- `actividades` falta en 2017-12 y 2022-04.
- Observacion manual: algunos CSV antiguos en `DB/actividades` parecen vacios. Falta confirmacion automatica.
- Shapefile de secciones no cubre todo el universo actual del censo (2461 vs 2499 en 2026-03).
- `renta` llega solo hasta 2023; hay que definir carry-forward.
- Build historico completo de `padron` sigue siendo costoso si se reconstruye sin cache (se recomienda modo incremental).
- Pendiente definir politica final para `2017-09` (asuncion CRS vs exclusion en modelado).

## Punto exacto en el que estamos

1. Infraestructura canonica y auditoria inicial completadas.
2. Geografia de secciones materializada y comparada contra censo/padron/renta.
3. Panel socioeconomico historico materializado y reutilizable por cache.
4. Geoespacial `lat/lon + H3` historico cerrado; ABT baseline ya materializada para iniciar modelado.

## Siguientes pasos inmediatos

1. Endurecer auditoria PiT (lags/fallbacks/cobertura) como gate formal de entrenamiento canonical.
2. Revisar sensibilidad del split temporal y calibracion por evento raro (valid/test con bajo numero de eventos).
3. Preparar primera iteracion de frontend sobre `data/exports/local_survival_map_export.csv`.
4. Definir protocolo de recalibracion mensual (drift y estabilidad de score).
5. Preparar narrativa final de validacion para entrega del concurso.

## Comandos utiles

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -u scripts/build_raw_inventory.py
PYTHONPATH=src .venv/bin/python -u scripts/build_censo_snapshot_manifest.py
PYTHONPATH=src .venv/bin/python -u scripts/build_section_geography.py
PYTHONPATH=src .venv/bin/python -u scripts/build_section_socioeconomic_panel.py
PYTHONPATH=src .venv/bin/python -u scripts/build_censo_historical_normalized.py
PYTHONPATH=src .venv/bin/python -u scripts/build_censo_geospatial.py
PYTHONPATH=src .venv/bin/python -u scripts/build_local_survival_abt.py
PYTHONPATH=src .venv/bin/python -u scripts/train_survival_baseline.py
PYTHONPATH=src .venv/bin/python -u scripts/run_modeling_readiness.py
PYTHONPATH=src .venv/bin/python -u scripts/train_survival_canonical.py
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
