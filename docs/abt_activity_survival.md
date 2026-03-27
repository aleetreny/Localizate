# ABT Cese de Actividad

ABT por local con target unico de `cese de actividad`: evento por desaparicion del `id_local` o por primer cambio robusto `single-single` entre macrocategorias de actividad. El subtipo del evento se conserva solo para auditoria.

## Resumen

- Filas ABT: 203,870
- Periodo de censura global: 2026-03 (2026-03)
- Tasa de evento observada: 0.0927
- Mediana de duracion (meses): 135.0
- Filas con H3 inicial: 164,441
- Filas con renta inicial: 156,417
- Filas con distancia a metro calculable: 164,412
- Filas con avisos positivos en barrio/año previo: 25,001

## Desglose de eventos

- Evento unificado `cese_de_actividad`: 18,893
- Subtipo auditoria `cambio_actividad`: 18,114
- Subtipo auditoria `desaparicion`: 779
- Censurados: 184,977
- Candidatos de cambio `single-single` auditados: 23,234

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
- Contexto comercial: `n_divisions_start`, `n_epigrafes_start`, `n_activity_categories_start`, `activity_category_code_start`, `section_local_count_*_start (lagged t-1)`, `section_same_activity_category_*_start (lagged t-1)`
- Dinamica interanual: `*_delta_12m_start`
- Externas: `avisos_*_prev_year`, `metro_distance_m_start`, `metro_access_count_500m_start`, `metro_access_count_1000m_start`
- Geoespacial inicial: `h3_cell_start`, `lat_wgs84_start`, `lon_wgs84_start`

## Cambios de macrocategoria de actividad mas frecuentes tratados como cierre

- Restaurante -> Bar y cafeteria: 654
- Bar y cafeteria -> Restaurante: 650
- Moda y complementos -> Belleza y cuidado personal: 597
- No priorizable -> Servicios profesionales y oficina: 264
- Moda y complementos -> Bazar, regalos y retail variado: 241
- Bazar, regalos y retail variado -> Belleza y cuidado personal: 236
- Belleza y cuidado personal -> Moda y complementos: 229
- Finanzas y seguros -> Servicios profesionales y oficina: 215
- Servicios profesionales y oficina -> Belleza y cuidado personal: 210
- No priorizable -> Belleza y cuidado personal: 203
