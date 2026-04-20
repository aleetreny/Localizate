# ABT + Contrato Point-in-Time (PiT)

Especificación operativa para construir la ABT de supervivencia sin leakage temporal en Localízate.

## 1) Objetivo

Construir una ABT mensual por local para estimar supervivencia (tiempo hasta cierre) con joins temporalmente correctos entre censo, padrón, renta y geografía.

## 2) Unidad de observación

- Entidad primaria: `id_local`
- Frecuencia: mensual
- Grano final ABT v1: una fila por `id_local` (tiempo hasta primer evento o censura)

## 3) Tiempo de referencia

- `target_period`: periodo de scoring/entrenamiento (`YYYY-MM`)
- `target_date`: primer día del periodo (`YYYY-MM-01`)
- Regla PiT global: toda feature debe cumplir `feature_effective_date <= target_date`

## 4) Definición de target (survival)

Variables mínimas:

- `event_observed` (bool): 1 si el local cierra dentro de la ventana de observación, 0 si censurado
- `duration_months` (int): meses desde `origin_period` hasta evento o censura
- `origin_period` (YYYY-MM): inicio del riesgo para la fila
- `event_period` (YYYY-MM, nullable): mes de cierre
- `censor_period` (YYYY-MM): último mes observable sin evento

Criterio operativo vigente:

- El target modelado es único y binario: `event_observed = 1` cuando se observa un `cese de actividad`.
- Evento = el primer instante observado entre:
  1. desaparición del `id_local` antes del último periodo global, o
  2. primer cambio robusto `single-single` de actividad entre meses consecutivos, tratado como fin del concepto comercial previo.
- Para cambios robustos, el `event_period` se fija en el mes anterior al cambio (último mes observado de la actividad previa).
- Se excluyen como cambios de cierre los placeholders/no codificados (`0`, `-1`, `PT`, equivalentes) y las duplicidades de formato tras limpieza canónica.
- `event_source` queda unificado en `cese_de_actividad` o `censored`.
- `event_subtype` se mantiene solo para auditoría forense (`cambio_actividad`, `desaparición`, `censored`).
- `event_subtype_detail` conserva el detalle exacto del cierre auditado: fuente concreta del cambio robusto o el subtipo final en desaparición/censura.
- Censura = último mes observable del local sin desaparición ni cambio estructural previo.

## 5) Contrato PiT por fuente

### 5.1 Censo (`locales` + `actividades`)

- Join principal por (`id_local`, `snapshot_period = target_period`) cuando exista snapshot del mes.
- Si no hay snapshot del mes, fallback permitido al último snapshot anterior.
- Campos obligatorios:
  - `censo_reference_period`
  - `censo_lag_months`
  - `censo_source_quality` (`exact_month`, `backfill`, `missing`)

### 5.2 Padrón por sección

- Join ASOF backward por `section_key` usando `padron_period <= target_period`.
- Campos obligatorios:
  - `padron_reference_period`
  - `padron_lag_months`
  - `padron_available` (bool)

### 5.3 Renta por sección/distrito/ciudad

- Join por `reference_year <= target_year`.
- Fallback jerárquico:
  1. `section`
  2. `district`
  3. `city`
- Campos obligatorios:
  - `renta_reference_year`
  - `renta_lag_years`
  - `renta_granularity_used` (`section`, `district`, `city`, `missing`)

### 5.4 Geografía de sección

- Join por `section_key`.
- Campos obligatorios:
  - `geometry_available` (bool)
  - `section_area_m2`
  - `population_density_km2` (si aplica)

## 6) Política de leakage

Checks obligatorios de hard-fail:

1. Ninguna feature con `feature_effective_date > target_date`.
2. Ningún dato de estado futuro del local usado como predictor en la misma fila.
3. Ninguna agregación móvil que use datos posteriores a `target_date`.
4. Ninguna feature de competencia o contexto comercial construida con el mismo mes si existe alternativa estrictamente lagged; por defecto usar `t-1` o ventanas cerradas en `<= t-1`.

Checks obligatorios de soft-fail (warning + auditoría):

1. `lag_months` excesivo (`> 3` en padrón/censo backfill).
2. `renta_lag_years` excesivo (`> 2`).
3. Cobertura geométrica baja por periodo.

## 7) Columnas mínimas ABT (v1)

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
- `event_subtype`
- `event_subtype_detail`
- `change_event_period`
- `change_successor_period`

Covariables base:

- Estado y tipología local del censo (sin usar futuro)
- Demografía por sección (padrón)
- Renta (`renta_best_eur` + granularidad)
- Geografía (`geometry_available`, `section_area_m2`, `population_density_km2`)
- Competencia/contexto comercial lagged (`t-1` como mínimo para stock, diversidad y cuota de categoría/actividad)

Auditoría de actividad:

- `previous_division_code`, `previous_division_desc`
- `successor_division_code`, `successor_division_desc`
- `previous_epigrafe_code`, `previous_epigrafe_desc`
- `successor_epigrafe_code`, `successor_epigrafe_desc`

Metadatos de calidad temporal:

- `censo_reference_period`, `censo_lag_months`
- `padron_reference_period`, `padron_lag_months`
- `renta_reference_year`, `renta_lag_years`, `renta_granularity_used`
- `feature_quality_flag` (agregado)

## 8) Estrategia de validación

Split temporal (obligatorio):

- Train: periodos antiguos
- Validation: bloque intermedio
- Test: bloque más reciente

No permitido:

- KFold aleatorio mezclando tiempo.

Métricas objetivo:

- Concordance index (C-index)
- Uno / IPCW C-index
- Cumulative Dynamic AUC (6/12/24 meses)
- Brier score dependiente de tiempo / IBS
- Calibración por horizonte (6/12/24 meses)

## 9) Versionado y reproducibilidad

Cada build de ABT debe registrar:

- `abt_version`
- fecha de ejecución
- rango temporal de entrada
- hash/row-count de insumos clave
- parámetros de fallback y thresholds de calidad

## 10) Criterios de aceptación

1. 100% de filas ABT cumplen regla PiT (`<= target_date`).
2. Reporte de coverage por fuente y lag por periodo generado.
3. Dataset reproducible con mismo `abt_version` y mismos insumos.
4. Split temporal guardado explícitamente para train/validation/test.

## 11) Plan inmediato de implementación

1. Materializar paneles faltantes (`padron_section_panel`, `section_socioeconomic_panel`) en modo incremental.
2. Construir tabla histórica mensual de locales/actividades con metadata de calidad temporal.
3. Crear ensamblador ABT con joins PiT y reporte de auditoría.
4. Entrenar baseline survival (Cox penalizado, RSF, GBSA) con split temporal bloqueado.
5. Publicar export de scoring mensual para mapa con flags de calidad.

## 12) Políticas cerradas (Mar 2026)

### 12.1 Transición CRS 2017-09

- Política operativa cerrada: `exclude_transition` para entrenamiento.
- Regla: filas con `coord_transform_status_start = transition_requires_review` no entran en train/valid/test del baseline.
- Motivación: evitar introducir ruido sistemático por ambigüedad ED50/ETRS89 en el arranque de riesgo.
- En scoring/export se mantienen las filas, pero con flag de calidad para tratamiento aguas abajo.

### 12.2 Renta post-2023

- Política operativa cerrada: `renta_max_year = 2023` con carry-forward controlado.
- Regla PiT: para periodos con `target_year > 2023`, la referencia máxima permitida de renta es 2023.
- Imputación jerárquica si falta `renta_best_eur`:
  1. mediana de distrito (`district_median`)
  2. mediana ciudad (`city_median`)
- Campos de auditoría obligatorios: `renta_carry_forward_years`, `renta_imputation_level`.
