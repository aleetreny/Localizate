# Roadmap

Hoja de ruta operativa para pasar del lago de datos actual a la macro DB historica de locales.

## Bloque 1. Infraestructura canonica

- Cerrar la optimizacion del panel socioeconomico por seccion para que la serie completa se materialice en una sola pasada razonable.
- Guardar caches canonicas por mes para `padron` agregado, evitando releer e inferir formatos en cada ejecucion.
- Dejar los outputs maestros en `csv` y `parquet` cuando la `venv` tenga `pyarrow`.

## Bloque 2. Censo historico base

- Materializar la tabla historica row-level de `locales` y `actividades` con la normalizacion ya definida.
- Reproyectar coordenadas del censo a un CRS unico y sacar `lat/lon`.
- Etiquetar el origen y calidad geometrica de cada local para joins posteriores.

## Bloque 3. Enriquecimiento geografico

- Generar H3 para cada local y cada seccion una vez cerrado el CRS comun.
- Resolver el gap entre el shapefile actual de secciones y el universo mas reciente del censo.
- Normalizar nodos de transporte (`Metro`) y distancias espaciales base.

## Bloque 4. Macro DB y ABT

- Construir la tabla mensual de locales con joins point-in-time a seccion, renta, demografia y geografia.
- Definir la ABT de supervivencia: target, censura, fecha de inicio, fecha de cierre y features leakage-safe.
- Versionar datasets maestros y particiones train/validation/test.

## Bloque 5. Serving y mapa

- Exportar una capa lista para mapa con `lat/lon`, H3, features explicativas y scores.
- Montar un primer explorador con `Streamlit + pydeck`.
- Si se necesita frontend propio despues, mantener H3/deck.gl y decidir solo la base map provider.

## Riesgos abiertos

- `actividades` sigue faltando en `2017-12` y `2022-04`.
- `renta` se corta en `2023`, asi que hay que dejar fijada la politica de carry-forward.
- El shapefile de secciones no refleja todo el universo actual del censo.
- La materializacion mensual de `padron` es hoy el mayor cuello de botella operativo.
