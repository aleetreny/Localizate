# Censo Historical Materialization

Materializacion historica incremental de snapshots normalizados del censo (locales + actividades).

## Resumen

- Filas de manifest: 264
- Periodos procesados: 132
- Materializados: 257
- Saltados por cache: 5
- Sin dataset en manifest (actividades faltantes): 2

## Calidad coordenadas (locales)

- Filas locales (materializadas en esta ejecucion): 19,866,257
- Filas con coordenada best disponible: 18,717,019
- Filas con coordenada missing: 1,149,238
- Cobertura coordenada best: 94.22%

## Cobertura actividades

- Periodos sin actividades en manifest: 2017-12, 2022-04

## Ultimos periodos

| Periodo | Dataset | Estado | Filas | Reader mode |
| --- | --- | --- | ---: | --- |
| 2025-06 | actividades | materialized | 222906 | pandas_default |
| 2025-06 | locales | materialized | 202053 | pandas_default |
| 2025-07 | actividades | materialized | 223032 | pandas_default |
| 2025-07 | locales | materialized | 202124 | pandas_default |
| 2025-08 | actividades | materialized | 223175 | pandas_default |
| 2025-08 | locales | materialized | 202203 | pandas_default |
| 2025-09 | actividades | materialized | 223493 | pandas_default |
| 2025-09 | locales | materialized | 202346 | pandas_default |
| 2025-10 | actividades | materialized | 223775 | pandas_default |
| 2025-10 | locales | materialized | 202654 | pandas_default |
| 2025-11 | actividades | materialized | 223961 | pandas_default |
| 2025-11 | locales | materialized | 202801 | pandas_default |
| 2025-12 | actividades | materialized | 224096 | pandas_default |
| 2025-12 | locales | materialized | 202888 | pandas_default |
| 2026-01 | actividades | materialized | 224217 | pandas_default |
| 2026-01 | locales | materialized | 202992 | pandas_default |
| 2026-02 | actividades | materialized | 224396 | pandas_default |
| 2026-02 | locales | materialized | 203069 | pandas_default |
| 2026-03 | actividades | skipped_existing | 0 | - |
| 2026-03 | locales | skipped_existing | 0 | - |

