# ABT Cese de Actividad

ABT por local con target unico de `cese de actividad`: evento por desaparicion del `id_local` o por primer cambio robusto `single-single` entre macrocategorias de actividad. El subtipo del evento se conserva solo para auditoria.

## Resumen

- Filas ABT: 203,870
- Periodo de censura global: 2026-03 (2026-03)
- Tasa de evento observada: 0.1112
- Mediana de duracion (meses): 135.0
- Filas con H3 inicial: 164,441
- Filas con renta inicial: 167,574
- Filas con distancia a metro calculable: 164,412
- Filas con avisos positivos en barrio/año previo: 53,545

## Desglose de eventos

- Evento unificado `cese_de_actividad`: 22,673
- Subtipo auditoria `cambio_actividad`: 21,906
- Subtipo auditoria `desaparicion`: 767
- Censurados: 181,197
- Candidatos de cambio `single-single` auditados: 28,294

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
- Contexto comercial: `n_divisions_start`, `n_epigrafes_start`, `n_activity_categories_start`, `activity_category_code_start`, `section_local_count_*_start (lagged t-1)`, `section_same_activity_category_*_start (lagged t-1)`, `section_*_hhi_start`, `section_*_entry_count_*_start`, `section_*_exit_count_*_start`
- Dinamica interanual: `*_delta_12m_start`
- Externas: `avisos_*_prev_year`, `metro_distance_m_start`, `metro_access_count_500m_start`, `metro_access_count_1000m_start`
- Geoespacial inicial: `h3_cell_start`, `lat_wgs84_start`, `lon_wgs84_start`

## Cambios de macrocategoria de actividad mas frecuentes tratados como cierre

- Restaurante -> Bar y cafetería: 651
- Bar y cafetería -> Restaurante: 643
- Moda y complementos -> Belleza y cuidado personal: 596
- No priorizable -> Servicios profesionales y oficina: 538
- No priorizable -> Belleza y cuidado personal: 320
- No priorizable -> Logística y movilidad: 303
- Moda y complementos -> Bazar, regalos y retail variado: 241
- Bazar, regalos y retail variado -> Belleza y cuidado personal: 231
- Finanzas y seguros -> Servicios profesionales y oficina: 224
- No priorizable -> Formación e idiomas: 222
