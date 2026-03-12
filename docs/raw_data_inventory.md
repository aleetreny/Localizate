# Raw Data Inventory

Inventario generado automaticamente a partir del contenido actual de `DB/`.

## Resumen por fuente

| Fuente | Archivos | Periodos | Assets primarios | Seleccionados | Incidencias |
| --- | ---: | ---: | ---: | ---: | ---: |
| actividades | 134 | 134 | 134 | 134 | 0 |
| avisos | 31 | 13 | 31 | 13 | 0 |
| locales | 136 | 136 | 136 | 136 | 0 |
| metro_entradas | 2 | 0 | 2 | 1 | 0 |
| padron | 250 | 146 | 250 | 146 | 0 |
| renta_media | 2 | 0 | 2 | 1 | 0 |
| secciones_censales_json | 1 | 0 | 1 | 1 | 0 |
| secciones_censales_shp | 8 | 0 | 1 | 1 | 0 |

## Hallazgos operativos

- `actividades` no cubre todos los periodos de `locales`. Faltan: 2017-12, 2022-04.
- `padron` tiene 104 periodos resueltos por preferencia de formato; se escoge la variante `csv` y se deja `txt` como respaldo.
- `avisos` ya se resuelve automaticamente con metadata oficial CKAN: `recibidos + AVISA` para 2014-2017 y `recibidos + SIC` para 2018+.
- El shapefile principal de secciones censales tiene sidecars minimos completos.

## Incidencias y periodos pendientes

No quedan incidencias abiertas en el manifiesto canonico actual.

