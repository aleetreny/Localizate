# Auditoria Inicial

## Resumen ejecutivo

El repo tenia ya la materia prima principal, pero aun no estaba preparado para empezar una pipeline seria de datos. Habia contexto funcional, PDFs de documentacion y un data lake bruto grande en local, pero faltaban estructura de proyecto, inventario tecnico y decisiones base para no mezclar datos incompatibles.

## Estado del repo al inicio

- No habia `README.md`, `requirements.txt`, `.gitignore` ni repo git inicializado.
- Ya existia `.venv`, pero sin el stack geoespacial y de survival analysis necesario.
- El volumen de `DB/` es muy alto y conviene tratarlo como data lake local, no como contenido versionado.

## Inventario de datos revisado

### Censo de locales

- Ultimo snapshot revisado: `2026_03`.
- `locales`: 46 columnas, 203081 filas, una fila por `id_local`.
- `actividades`: 47 columnas, 224416 filas, unas 1.105 actividades por local en media.
- Hallazgo critico: la propia documentacion indica que las coordenadas del censo estan en ED50 hasta el 15 de septiembre de 2017 y en ETRS89 a partir de esa fecha.
- Hallazgo practico: 50375 filas del ultimo snapshot tienen coordenadas locales a cero; 6149 de ellas tienen coordenadas de agrupacion aprovechables.
- Cobertura incompleta en `actividades`: faltan `2017_12` y `2022_04` respecto a `locales`.

### Padron

- Ultimo snapshot revisado: `2026_02`.
- 15 columnas, 241082 filas, 2462 secciones unicas y 101 edades.
- Problema estructural: existen 104 meses duplicados con version `csv` y `txt`, con el mismo numero de filas en la muestra comprobada.
- Decision recomendada: definir una regla canonica por mes, preferiblemente `csv` cuando exista y conservar `txt` solo como fallback.

### Avisos

- Ultimo fichero revisado: enero de 2026 con 113131 filas.
- Los PDFs muestran dos generaciones del dataset: una en ED50 y otra en ETRS89.
- El folder actual mezcla variantes por anio (`recibidos`, `resueltos`, AVISA clasico y SIC-MiNT).
- Para feature engineering la version relevante debe ser `recibidos`, no una mezcla de entradas y resoluciones.

### Renta INE

- El CSV limpio tiene 43414 filas totales y periodos entre 2015 y 2023.
- Para Madrid capital, usando `Municipios = 28079 Madrid`, hay 22153 filas y 2492 secciones unicas.
- La clave util para join parece ser el codigo final de 5 digitos de `Secciones` (ej. `01001`).
- Gap importante: no hay renta 2024, 2025 ni 2026.

### Metro

- 673 puntos en el CSV revisado.
- Hay problemas de encoding en nombres y bastantes estaciones/accesos sin `name`.
- Conviene convertirlo en una tabla de referencia limpia antes de calcular distancias.

### Secciones censales

- Hay shapefile y topologia JSON.
- El shapefile esta en EPSG:25830 (ETRS89 / UTM zone 30N).
- Sera la pieza de union entre coordenadas y fuentes agregadas por seccion.

## Claves de cruce detectadas

- `locales.id_seccion_censal_local` se parece a `padron.COD_DIST_SECCION`, pero no hay solape perfecto y habra que validar cambios historicos de seccion.
- `renta.Secciones` necesita derivar una clave corta de 5 digitos para poder compararse con `desc_seccion_censal_local` o con claves normalizadas.
- Las coordenadas de `locales` y `avisos` no son directamente comparables en toda la serie sin corregir CRS y encodings.

## Recomendacion de stack geoespacial y mapa

- Hex grid: usar H3. No hace falta ninguna "base de datos de hexagonos de Google".
- Prototipo rapido en Python: `Streamlit + pydeck`.
- Si mas adelante quereis un frontend JS separado con base Google, la capa de hexagonos se puede seguir generando con H3 y renderizarse encima del mapa; el grid no depende del proveedor del mapa.

## Estructura decidida en este arranque

- Mantener `DB/`, `Context/` y `Documentación DB/` como carpetas legacy de referencia.
- Empezar el trabajo nuevo en `src/`, `scripts/`, `configs/`, `data/`, `models/`, `apps/streamlit/`, `tests/` y `docs/`.
- No mover aun los datos brutos para evitar roturas y copia innecesaria de decenas de GB.

## Base tecnica ya implementada

- Inventario canonico de fuentes raw y manifiesto por periodo.
- Lectura robusta de CSV/TXT con deteccion de encoding y delimitador por muestra.
- Regla automatica de seleccion de `padron` (`csv` preferido sobre variante `txt` renombrada).
- Resolucion automatica de `avisos` mediante metadata oficial CKAN.
- Manifest canonico del censo desde 2015-01 con cobertura `locales + actividades` y etiquetado de riesgo CRS para el corte de septiembre de 2017.
- Perfil de snapshots criticos del censo con deteccion de parser reparado y cobertura efectiva de coordenadas.
- Informe de solape de secciones censales entre censo, padron y renta para preparar el join socioeconomico.

## Hoja de ruta recomendada

1. Construir un inventario canonico por fuente y mes.
2. Crear lectores robustos por dataset: encoding, delimitador, parseo de fechas y CRS.
3. Normalizar la serie historica de `locales` + `actividades`.
4. Resolver el join por seccion censal entre shapefile, `padron` y `renta`.
5. Reproyectar todo a un CRS comun y generar lat/lon + H3.
6. Diseñar la ABT y las features point-in-time.
7. Solo entonces pasar a modelado e inferencia batch.
