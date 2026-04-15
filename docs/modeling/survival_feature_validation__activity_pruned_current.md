# Survival Feature Validation

Chequeo estadístico ligero de la matriz de variables antes de relanzar el entrenamiento canónico.

## Resumen

- Perfil de features: `activity_survival_pruned`
- Filas analizadas: 203,828
- Event rate: 0.0927
- Variables analizadas: 78
- Variables con `p < 0.05`: 57
- Variables con missing <= 20% antes de imputación: 8

## Top variables por señal univariante

| Variable | Missing | Media evento | Media no evento | SMD | p-value | Correlación biserial |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| metro_access_count_1000m_start | 0.00% | 18.5842 | 11.4428 | 0.5425 | 0 | 0.1643 |
| metro_access_count_500m_start | 0.00% | 5.4000 | 3.2462 | 0.4812 | 0 | 0.1494 |
| macro_category__fashion_accessories | 29.53% | 0.1156 | 0.0296 | 0.3361 | 0 | 0.1311 |
| metro_distance_m_start | 19.36% | 5.4364 | 5.6823 | -0.2982 | 0 | -0.0906 |
| missing_h3 | 0.00% | 0.0235 | 0.2108 | -0.6087 | 0 | -0.1375 |
| missing_metro_distance_start | 0.00% | 0.0236 | 0.2109 | -0.6088 | 0 | -0.1375 |
| renta_carry_forward_years | 0.00% | 0.0133 | 0.2908 | -0.7916 | 0 | -0.1725 |
| macro_category__electronics_telecom | 29.53% | 0.0337 | 0.0067 | 0.1925 | 1.215e-298 | 0.0818 |
| macro_category__bazaar_gifts | 29.53% | 0.0605 | 0.0197 | 0.2093 | 2.006e-273 | 0.0783 |
| macro_category__finance_insurance | 29.53% | 0.0554 | 0.0174 | 0.2042 | 1.12e-265 | 0.0771 |
| macro_category__home_decor | 29.53% | 0.0389 | 0.0100 | 0.1879 | 2.087e-250 | 0.0749 |
| macro_category__books_leisure_retail | 29.53% | 0.0302 | 0.0072 | 0.1700 | 8.63e-214 | 0.0691 |
| share_age_00_14_start | 23.28% | 0.1174 | 0.1210 | -0.0908 | 1.63e-207 | -0.0283 |
| renta_best_eur_delta_12m_start | 23.28% | 2432.4839 | 1275.0353 | 0.1406 | 2.237e-154 | 0.0469 |
| macro_category__consumer_services | 29.53% | 0.0204 | 0.0047 | 0.1416 | 1.181e-152 | 0.0583 |

## Interpretación

- Este reporte no sustituye al entrenamiento survival final; solo verifica cobertura y señal univariante razonable.
- Un `p-value` bajo o una `SMD` alta indican separación útil entre eventos y no eventos, pero no prueban causalidad ni robustez multivariante.
- Las variables externas de `avisos` y `metro` quedan integradas y listas para el siguiente entrenamiento canónico.
