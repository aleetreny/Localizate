# ABT Survival

ABT baseline por local (una fila por `id_local`) con target de supervivencia censurado.

## Resumen

- Filas ABT: 203,870
- Periodo de censura global: 2026-03 (2026-03)
- Tasa de evento observada: 0.0039
- Mediana de duracion (meses): 135.0
- Filas con H3 inicial: 163,800
- Filas con renta inicial: 53,084

## Columnas clave

- `first_seen_period`, `last_seen_period`, `duration_months`, `event_observed`
- Features iniciales PiT: `renta_best_eur_start`, `share_*_start`, `population_density_km2_start`
- Geoespacial inicial: `h3_cell_start`, `lat_wgs84_start`, `lon_wgs84_start`

