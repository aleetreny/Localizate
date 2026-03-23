# ABT + Contrato Point-in-Time (PiT)

Especificacion operativa para construir la ABT de supervivencia sin leakage temporal en Localizate.

## 1) Objetivo

Construir una ABT mensual por local para estimar supervivencia (tiempo hasta cierre) con joins temporalmente correctos entre censo, padron, renta y geografia.

## 2) Unidad de observacion

- Entidad primaria: `id_local`
- Frecuencia: mensual
- Grano final ABT v1: una fila por `id_local` (tiempo hasta primer evento o censura)

## 3) Tiempo de referencia

- `target_period`: periodo de scoring/entrenamiento (`YYYY-MM`)
- `target_date`: primer dia del periodo (`YYYY-MM-01`)
- Regla PiT global: toda feature debe cumplir `feature_effective_date <= target_date`

## 4) Definicion de target (survival)

Variables minimas:

- `event_observed` (bool): 1 si el local cierra dentro de la ventana de observacion, 0 si censurado
- `duration_months` (int): meses desde `origin_period` hasta evento o censura
- `origin_period` (YYYY-MM): inicio del riesgo para la fila
- `event_period` (YYYY-MM, nullable): mes de cierre
- `censor_period` (YYYY-MM): ultimo mes observable sin evento

Criterio operativo vigente:

- Evento = el primer instante observado entre:
  1. desaparicion del `id_local` antes del ultimo periodo global, o
  2. primer cambio robusto `single-single` de `division` entre meses consecutivos, tratado como cierre estructural del negocio previo.
- Para cambios de division, el `event_period` se fija en el mes anterior al cambio (ultimo mes observado de la actividad previa).
- Se excluyen como cambios de cierre los placeholders/no codificados (`0`, `-1`, `PT`, equivalentes) y las duplicidades de formato (`47` vs `47.0`) tras limpieza canonica.
- Censura = ultimo mes observable del local sin desaparicion ni cambio estructural previo.

## 5) Contrato PiT por fuente

### 5.1 Censo (`locales` + `actividades`)

- Join principal por (`id_local`, `snapshot_period = target_period`) cuando exista snapshot del mes.
- Si no hay snapshot del mes, fallback permitido al ultimo snapshot anterior.
- Campos obligatorios:
  - `censo_reference_period`
  - `censo_lag_months`
  - `censo_source_quality` (`exact_month`, `backfill`, `missing`)

### 5.2 Padron por seccion

- Join ASOF backward por `section_key` usando `padron_period <= target_period`.
- Campos obligatorios:
  - `padron_reference_period`
  - `padron_lag_months`
  - `padron_available` (bool)

### 5.3 Renta por seccion/distrito/ciudad

- Join por `reference_year <= target_year`.
- Fallback jerarquico:
  1. `section`
  2. `district`
  3. `city`
- Campos obligatorios:
  - `renta_reference_year`
  - `renta_lag_years`
  - `renta_granularity_used` (`section`, `district`, `city`, `missing`)

### 5.4 Geografia de seccion

- Join por `section_key`.
- Campos obligatorios:
  - `geometry_available` (bool)
  - `section_area_m2`
  - `population_density_km2` (si aplica)

## 6) Politica de leakage

Checks obligatorios de hard-fail:

1. Ninguna feature con `feature_effective_date > target_date`.
2. Ningun dato de estado futuro del local usado como predictor en la misma fila.
3. Ninguna agregacion movil que use datos posteriores a `target_date`.

Checks obligatorios de soft-fail (warning + auditoria):

1. `lag_months` excesivo (`> 3` en padron/censo backfill).
2. `renta_lag_years` excesivo (`> 2`).
3. Cobertura geometrica baja por periodo.

## 7) Columnas minimas ABT (v1)

Identidad y tiempo:

- `id_local`
- `first_seen_period`
- `last_seen_period`
- `target_end_period`

Target survival:

- `event_observed`
- `duration_months`
- `event_period`
- `censor_reference_period`
- `event_source`
- `change_event_period`
- `change_successor_period`

Covariables base:

- Estado y tipologia local del censo (sin usar futuro)
- Demografia por seccion (padron)
- Renta (`renta_best_eur` + granularidad)
- Geografia (`geometry_available`, `section_area_m2`, `population_density_km2`)

Auditoria de actividad:

- `previous_division_code`, `previous_division_desc`
- `successor_division_code`, `successor_division_desc`
- `previous_epigrafe_code`, `previous_epigrafe_desc`
- `successor_epigrafe_code`, `successor_epigrafe_desc`

Metadatos de calidad temporal:

- `censo_reference_period`, `censo_lag_months`
- `padron_reference_period`, `padron_lag_months`
- `renta_reference_year`, `renta_lag_years`, `renta_granularity_used`
- `feature_quality_flag` (agregado)

## 8) Estrategia de validacion

Split temporal (obligatorio):

- Train: periodos antiguos
- Validation: bloque intermedio
- Test: bloque mas reciente

No permitido:

- KFold aleatorio mezclando tiempo.

Metricas objetivo:

- Concordance index (C-index)
- Uno / IPCW C-index
- Cumulative Dynamic AUC (6/12/24 meses)
- Brier score dependiente de tiempo / IBS
- Calibracion por horizonte (6/12/24 meses)

## 9) Versionado y reproducibilidad

Cada build de ABT debe registrar:

- `abt_version`
- fecha de ejecucion
- rango temporal de entrada
- hash/row-count de insumos clave
- parametros de fallback y thresholds de calidad

## 10) Criterios de aceptacion

1. 100% de filas ABT cumplen regla PiT (`<= target_date`).
2. Reporte de coverage por fuente y lag por periodo generado.
3. Dataset reproducible con mismo `abt_version` y mismos insumos.
4. Split temporal guardado explicitamente para train/validation/test.

## 11) Plan inmediato de implementacion

1. Materializar paneles faltantes (`padron_section_panel`, `section_socioeconomic_panel`) en modo incremental.
2. Construir tabla historica mensual de locales/actividades con metadata de calidad temporal.
3. Crear ensamblador ABT con joins PiT y reporte de auditoria.
4. Entrenar baseline survival (Cox penalizado, RSF, GBSA) con split temporal bloqueado.
5. Publicar export de scoring mensual para mapa con flags de calidad.

## 12) Politicas cerradas (Mar 2026)

### 12.1 Transicion CRS 2017-09

- Politica operativa cerrada: `exclude_transition` para entrenamiento.
- Regla: filas con `coord_transform_status_start = transition_requires_review` no entran en train/valid/test del baseline.
- Motivacion: evitar introducir ruido sistematico por ambiguedad ED50/ETRS89 en el arranque de riesgo.
- En scoring/export se mantienen las filas, pero con flag de calidad para tratamiento aguas abajo.

### 12.2 Renta post-2023

- Politica operativa cerrada: `renta_max_year = 2023` con carry-forward controlado.
- Regla PiT: para periodos con `target_year > 2023`, la referencia maxima permitida de renta es 2023.
- Imputacion jerarquica si falta `renta_best_eur`:
  1. mediana de distrito (`district_median`)
  2. mediana ciudad (`city_median`)
- Campos de auditoria obligatorios: `renta_carry_forward_years`, `renta_imputation_level`.
