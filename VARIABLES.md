# Variables

Inventario de variables del pipeline de supervivencia justo antes del siguiente reentrenamiento canónico.

## Variables de modelado activas

| Variable | Estado | Categoría | Fuente | Descripción |
|---------------|---------------|---------------|---------------|---------------|
| renta_effective_eur | existing | socioeconomic | renta + policy fill | Renta usable en entrenamiento tras fallback sección→distrito→ciudad. |
| renta_carry_forward_years | existing | socioeconomic | renta + policy fill | Años de carry-forward aplicados a la renta por falta de dato reciente. |
| share_foreign_start | existing | socioeconomic | section_socioeconomic_panel | Peso de población extranjera en la sección al alta del local. |
| share_age_00_14_start | new | socioeconomic | section_socioeconomic_panel | Peso de población infantil en la sección al alta. |
| share_age_15_29_start | existing | socioeconomic | section_socioeconomic_panel | Peso de población joven en la sección al alta. |
| share_age_30_44_start | new | socioeconomic | section_socioeconomic_panel | Peso de población adulta joven en la sección al alta. |
| share_age_45_64_start | existing | socioeconomic | section_socioeconomic_panel | Peso de población madura en la sección al alta. |
| share_age_65_plus_start | existing | socioeconomic | section_socioeconomic_panel | Peso de población sénior en la sección al alta. |
| share_male_start | new | socioeconomic | section_socioeconomic_panel | Peso masculino en la sección al alta. |
| age_mean_start | new | socioeconomic | section_socioeconomic_panel | Edad media estimada de la sección al alta. |
| total_population_start | new | socioeconomic | section_socioeconomic_panel | Población total de la sección al alta (log-transform en modelado). |
| population_density_km2_start | existing | socioeconomic | section_socioeconomic_panel | Densidad de población por km² en la sección al alta. |
| padron_lag_months_start | existing | data_quality | section_socioeconomic_panel | Meses de retraso del padrón usado para el join PiT. |
| geometry_available_start | existing | data_quality | section_geography | Flag de disponibilidad geométrica para la sección. |
| missing_h3 | existing | data_quality | censo_geospatial | Flag de H3 ausente en el punto inicial del local. |
| n_divisions_start | new | activity | actividades | Número de divisiones activas del local en su primer mes observado. |
| n_epigrafes_start | new | activity | actividades | Número de epígrafes activos del local en su primer mes observado. |
| section_local_count_start | new | competition | censo locales historico | Stock de locales observados en la sección el mes de alta. |
| section_unique_division_count_start | new | competition | censo actividades historico | Diversidad de divisiones presentes en la sección el mes de alta. |
| section_single_division_share_start | new | competition | censo actividades historico | Peso de locales single-division en la sección el mes de alta. |
| section_same_division_local_count_start | new | competition | censo actividades historico | Número de competidores single-division de la misma división en la sección. |
| section_same_division_share_start | new | competition | censo actividades historico | Cuota de competidores de la misma división dentro del stock de la sección. |
| section_local_count_delta_12m_start | new | zone_dynamics | censo locales historico | Cambio de stock de locales en la sección frente a 12 meses antes. |
| total_population_delta_12m_start | new | zone_dynamics | section_socioeconomic_panel | Cambio interanual de población total en la sección. |
| share_foreign_delta_12m_start | new | zone_dynamics | section_socioeconomic_panel | Cambio interanual del peso de población extranjera. |
| share_age_15_29_delta_12m_start | new | zone_dynamics | section_socioeconomic_panel | Cambio interanual del peso de población de 15-29 años. |
| population_density_km2_delta_12m_start | new | zone_dynamics | section_socioeconomic_panel | Cambio interanual de densidad poblacional. |
| renta_best_eur_delta_12m_start | new | zone_dynamics | section_socioeconomic_panel | Cambio interanual de renta disponible en la sección. |
| avisos_district_per_1000_prev_year | new | avisos | DB/avisos + section_socioeconomic_panel | Avisos recibidos del distrito en el año anterior por cada 1.000 habitantes. |
| avisos_barrio_per_1000_prev_year | new | avisos | DB/avisos + section_socioeconomic_panel | Avisos recibidos del barrio en el año anterior por cada 1.000 habitantes. |
| avisos_barrio_share_of_district_prev_year | new | avisos | DB/avisos | Peso del barrio dentro del total de avisos del distrito en el año anterior. |
| metro_distance_m_start | new | metro | DB/Metro | Distancia al acceso de metro más cercano desde la localización inicial (log-transform en modelado). |
| metro_access_count_500m_start | new | metro | DB/Metro | Número de accesos de metro a 500 m o menos. |
| metro_access_count_1000m_start | new | metro | DB/Metro | Número de accesos de metro a 1 km o menos. |
| missing_metro_distance_start | new | data_quality | DB/Metro + censo_geospatial | Flag de imposibilidad de calcular cercanía a metro por falta de coordenadas iniciales. |

## Variables auxiliares y de target

| Variable | Estado | Categoría | Fuente | Descripción |
|---------------|---------------|---------------|---------------|---------------|
| district_code_start | new | join_helper | section_socioeconomic_panel | Código de distrito del local en el periodo inicial. |
| barrio_code_start | new | join_helper | section_socioeconomic_panel | Código de barrio del local en el periodo inicial. |
| division_code_start | new | join_helper | actividades | Firma/división principal single-division del local al alta. |
| event_source | existing | target | abt_survival | Origen del evento: censura, desaparición o cambio robusto de división. |
| event_period | existing | target | abt_survival | Periodo en el que ocurre el evento objetivo. |
| duration_months | existing | target | abt_survival | Duración observada en meses desde el alta hasta evento/censura. |

## Criterio de uso

- Todas las variables de modelado son point-in-time y se congelan en `first_seen_period` o en información histórica estrictamente anterior.
- `avisos_*_prev_year` usa el año natural anterior al alta del local para evitar leakage intraanual.
- `metro_*` usa la posición inicial del local y la malla estática de accesos de metro.
- Las variables con sufijo `_delta_12m_start` miden cambio frente a 12 meses antes en la misma sección.