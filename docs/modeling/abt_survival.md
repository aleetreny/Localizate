# ABT Survival

ABT por local con cierre observado tanto por desaparicion del `id_local` como por primer cambio robusto `single-single` de division, tratado como cierre estructural.

## Resumen

- Filas ABT: 203,870
- Periodo de censura global: 2026-03 (2026-03)
- Tasa de evento observada: 0.0950
- Mediana de duracion (meses): 135.0
- Filas con H3 inicial: 164,441
- Filas con renta inicial: 203,051
- Filas con distancia a metro calculable: 164,412
- Filas con avisos positivos en barrio/año previo: 89,009

## Desglose de eventos

- Cierre por cambio `single-single` de division: 0
- Cierre por desaparicion del local: 0
- Censurados: 184,503
- Candidatos de cambio `single-single` auditados: 23,250

## Limpieza masiva de actividad

- Codigos raw de division detectados: 176
- Codigos limpios y validos de division: 84
- Filas de division corregidas por formato numerico (`47.0 -> 47`): 452,624
- Filas de division remapeadas por descripcion canonica: 98
- Filas de division marcadas como placeholder/no codificadas: 1,173,250
- Filas de division descartadas por codigo no valido: 0
- Codigos raw de epigrafe detectados: 905
- Codigos limpios y validos de epigrafe: 457

## Columnas clave

- `first_seen_period`, `last_seen_period`, `target_end_period`, `duration_months`, `event_observed`
- `event_source`, `event_subtype`, `event_subtype_detail`, `event_period`, `change_event_period`, `change_successor_period`
- Auditoria de cambio: `previous_division_*`, `successor_division_*`, `previous_epigrafe_*`, `successor_epigrafe_*`, `previous_macro_category_*`, `successor_macro_category_*`
- Features iniciales PiT: `renta_best_eur_start`, `share_*_start`, `total_population_start`, `age_mean_start`, `population_density_km2_start`
- Contexto comercial: `n_divisions_start`, `n_epigrafes_start`, `n_activity_categories_start`, `activity_category_code_start`, `section_local_count_*_start (lagged t-1)`, `section_same_division_*_start (lagged t-1)`, `section_*_hhi_start`, `section_*_entry_count_*_start`, `section_*_exit_count_*_start`
- Dinamica interanual: `*_delta_12m_start`
- Externas: `avisos_*_prev_year`, `metro_distance_m_start`, `metro_access_count_500m_start`, `metro_access_count_1000m_start`
- Geoespacial inicial: `h3_cell_start`, `lat_wgs84_start`, `lon_wgs84_start`

## Cambios de division mas frecuentes tratados como cierre

- COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS -> OTROS SERVICIOS PERSONALES: 1,920
- COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS -> SERVICIOS DE COMIDAS Y BEBIDAS: 1,274
- SERVICIOS DE COMIDAS Y BEBIDAS -> COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS: 915
- OTROS SERVICIOS PERSONALES -> COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS: 840
- COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS -> ACTIVIDADES SANITARIAS: 440
- COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS -> ACTIVIDADES INMOBILIARIAS: 386
- SERVICIOS FINANCIEROS, EXCEPTO SEGUROS Y FONDOS DE PENSIONES -> COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS: 361
- COMERCIO AL POR MAYOR E INTERMEDIARIOS DEL COMERCIO, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS -> COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS: 359
- COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS -> ACTIVIDADES ADMINISTRATIVAS DE OFICINA Y OTRAS ACTIVIDADES AUXILIARES A LAS EMPRESAS: 343
- COMERCIO AL POR MENOR, EXCEPTO DE VEHICULOS DE MOTOR Y MOTOCICLETAS -> EDUCACION: 332
