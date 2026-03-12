# Project Log

## 2026-03-06

- Revisadas las carpetas `Context/`, `Documentación DB/` y `DB/` para entender objetivo, fuentes y restricciones reales.
- Auditadas las estructuras principales de `locales`, `actividades`, `padron`, `avisos`, `renta` y `metro`.
- Detectados los gaps tecnicos de arranque: cambio de CRS en el censo, duplicados `csv/txt` en `padron`, huecos mensuales en `actividades`, renta disponible solo hasta 2023 y mezcla de encodings.
- Inicializado git y creada la estructura base del proyecto para separar codigo, datos transformados, modelos, app y documentacion.
- Añadidos `README.md`, `requirements.txt`, `.gitignore` y esta bitacora como base documental del proyecto.
- Implementada la primera capa robusta de ingesta canonica en `src/localizate/`: inventario de fuentes raw, lectores tabulares tolerantes a encodings y manifiesto por periodo.
- Añadido `scripts/build_raw_inventory.py` para generar `data/intermediate/raw_inventory.csv`, `data/intermediate/raw_manifest.csv` y `docs/raw_data_inventory.md`.
- Integrada metadata oficial CKAN para resolver automaticamente la seleccion correcta de `avisos` por anio.
- Implementada la capa canonica inicial del censo historico en `src/localizate/censo.py`: manifest de snapshots desde 2015-01, etiquetado CRS por periodo y normalizacion defensiva de columnas/coordenadas.
- Añadido `scripts/build_censo_snapshot_manifest.py` para generar `data/processed/censo_snapshot_manifest.csv` y `docs/censo_snapshot_manifest.md`.
- Detectado que la `venv` actual aun no tiene `pyarrow`, por lo que la salida Parquet queda en fallback a CSV hasta instalar dependencias.
- Añadido `src/localizate/censo_profile.py` y `scripts/profile_censo_snapshots.py` para perfilar snapshots del censo, detectar meses con parser reparado y medir cobertura real de coordenadas/actividades.
- Materializado el snapshot normalizado de `2026-03` en `data/intermediate/censo_snapshots/locales/2026-03.csv.gz` y `data/intermediate/censo_snapshots/actividades/2026-03.csv.gz`.
- Añadido `src/localizate/section_keys.py` y `scripts/profile_section_keys.py` para medir el solape de claves de seccion entre censo, padron y renta.

## 2026-03-09

- Añadido `src/localizate/section_geography.py` para leer la `dbf` del shapefile sin depender de `geopandas`, colapsar secciones multipartes y materializar metadata geografica canonica.
- Añadido `scripts/build_section_geography.py`, generando `data/processed/section_geography.csv`, `data/processed/section_geography_coverage.csv` y `docs/section_geography.md`.
- Detectado y corregido un caso real de seccion duplicada en geometria (`17099`) que habria duplicado filas en merges posteriores.
- Añadido `src/localizate/socioeconomics.py` para normalizar `padron`, agregar demografia por seccion, normalizar `renta` Madrid y preparar el panel socioeconomico alineado al censo.
- Añadido `scripts/build_section_socioeconomic_panel.py` y tests especificos para edades top-coded, fallbacks de renta y merges con geometria multipartes.
- Validado el estado del shapefile frente a los universos actuales: la geometria se queda en `2461` secciones unicas tras colapsar multipartes, por debajo del censo `2026-03`.
- Detectado que la primera materializacion completa del panel socioeconomico funciona en codigo pero es demasiado lenta para una pasada operativa limpia; queda como siguiente bloque inmediato optimizarla y rematerializar.

## 2026-03-12

- Creado `STATUS.md` en la raiz con un resumen operativo para continuidad por terceros.
- Actualizados los documentos de `Context/` para reflejar el estado real del repo y dejar claro que la descarga ya no aplica.
- Anotada la observacion de CSV antiguos de `DB/actividades` posiblemente vacios (pendiente de confirmacion automatica).
- Consolidado README y `Context/` dentro de `STATUS.md` con snapshots verbatim y un enfoque unificado actualizado.
- Eliminada la carpeta `Context/` tras consolidacion en `STATUS.md` para simplificar la estructura del repo.
- Movida `Documentación DB/` a `docs/documentacion_db/` para estandarizar nombres y reducir ruido en la raiz.
- Eliminados `ingesta_datos.py` e `ingestion_log.txt` (legacy de descarga).
