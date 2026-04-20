# Censo Snapshot Profile

Perfil operativo y de calidad de los snapshots canonicos del censo histórico.

## Resumen

- Periodos perfilados: 5
- Periodos con actividades: 3
- Periodos que necesitaron reparacion de parser en locales: 2
- Periodos que necesitaron reparacion de parser en actividades: 0

## Periodos con incidencias relevantes

| Periodo | Cobertura | Reader locales | Reader actividades | IDs sin actividad | IDs fuera de locales |
| --- | --- | --- | --- | ---: | ---: |
| 2017-09 | complete | last_column_overflow_fix | pandas_default | 0 | 0 |
| 2017-12 | missing_actividades | last_column_overflow_fix | - | 0 | 0 |
| 2022-04 | missing_actividades | pandas_default | - | 0 | 0 |

## Muestra del perfil

| Periodo | Locales | Coord OK | Coord missing | Actividades | Avg acts/local | CRS |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2015-01 | 142575 | 140856 | 1719 | 154990 | 1.087 | ed50_utm30 |
| 2017-09 | 145723 | 142878 | 2845 | 160880 | 1.104 | transition_2017_09 |
| 2017-12 | 145801 | 142871 | 2930 | 0 | - | etrs89_utm30 |
| 2022-04 | 150181 | 144705 | 5476 | 0 | - | etrs89_utm30 |
| 2026-03 | 203081 | 158855 | 44226 | 224416 | 1.105 | etrs89_utm30 |

