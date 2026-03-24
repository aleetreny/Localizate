# Survival Feature Validation

Chequeo estadístico ligero de la matriz de variables antes de relanzar el entrenamiento canónico.

## Resumen

- Filas analizadas: 203,828
- Event rate: 0.0747
- Variables analizadas: 35
- Variables con `p < 0.05`: 32
- Variables con missing <= 20% antes de imputación: 14

## Top variables por señal univariante

| Variable | Missing | Media evento | Media no evento | SMD | p-value | Correlación biserial |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| metro_access_count_1000m_start | 0.00% | 17.7291 | 11.6501 | 0.4688 | 0 | 0.1268 |
| metro_access_count_500m_start | 0.00% | 5.1422 | 3.3087 | 0.4162 | 0 | 0.1153 |
| section_local_count_start | 0.32% | 4.4353 | 4.7387 | -0.3573 | 0 | -0.0855 |
| section_unique_division_count_start | 0.32% | 12.4052 | 17.1564 | -0.5296 | 0 | -0.1121 |
| missing_metro_distance_start | 0.00% | 0.0251 | 0.2072 | -0.5929 | 0 | -0.1212 |
| missing_h3 | 0.00% | 0.0249 | 0.2071 | -0.5932 | 0 | -0.1213 |
| renta_carry_forward_years | 0.00% | 0.0184 | 0.2850 | -0.7570 | 0 | -0.1503 |
| section_single_division_share_start | 0.32% | 0.6617 | 0.6092 | 0.2999 | 3.499e-237 | 0.0752 |
| metro_distance_m_start | 19.36% | 5.4694 | 5.6749 | -0.2498 | 3.42e-203 | -0.0687 |
| share_age_00_14_start | 23.28% | 0.1182 | 0.1208 | -0.0681 | 4.129e-108 | -0.0190 |
| avisos_district_per_1000_prev_year | 0.00% | 0.0633 | 0.2532 | -0.2200 | 2.087e-100 | -0.0471 |
| avisos_barrio_per_1000_prev_year | 0.00% | 0.0645 | 0.2552 | -0.2183 | 6.601e-100 | -0.0469 |
| renta_best_eur_delta_12m_start | 23.28% | 2321.3221 | 1306.4232 | 0.1246 | 2.176e-94 | 0.0373 |
| section_same_division_local_count_start | 29.32% | 2.1381 | 2.2931 | -0.1414 | 2.711e-87 | -0.0389 |
| share_male_start | 23.28% | 0.4635 | 0.4658 | -0.0950 | 4.19e-70 | -0.0269 |

## Interpretación

- Este reporte no sustituye al entrenamiento survival final; solo verifica cobertura y señal univariante razonable.
- Un `p-value` bajo o una `SMD` alta indican separación útil entre eventos y no eventos, pero no prueban causalidad ni robustez multivariante.
- Las variables externas de `avisos` y `metro` quedan integradas y listas para el siguiente entrenamiento canónico.
