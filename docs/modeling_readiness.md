# Modeling Readiness

Chequeo continuo de calidad para asegurar que el paso a modelos de supervivencia avanzados sea estable y trazable.

- Estado global: ready_with_caveats

## Lectura ejecutiva

- Estado final: ready_with_caveats; gate canonico: pass.
- Discriminacion ensemble: valid Uno=0.6863, test Uno=0.6418.
- Horizontes dinamicos: valid mean AUC=0.7398, test mean AUC=0.8773.
- La robustez post-fit ya está materializada con bootstrap; usa los anchos de CI para distinguir mejora real de ruido estadístico.
- La pipeline sirve para export operativo y comparacion iterativa, pero todavia no para afirmar excelencia robusta fuera de muestra.

## Resumen

- Filas ABT: 203,870
- Eventos totales: 15,241
- Tasa de evento: 0.07475842448619219
- Mediana duracion (meses): 135.0
- Cobertura H3: 0.8065973414430765
- Cobertura renta observada: 0.7672389267670574
- Filas marcadas por transicion CRS: 142878
- Quality gate canonico: pass
- Robustez post-fit: pass_with_caveats
- Uno C-index valid: 0.6863451102961386
- Uno C-index test: 0.6418470390192624
- Dynamic AUC valid: 0.7397564434685907
- Dynamic AUC test: 0.8772892767478985
- IBS valido disponible: True
- IBS test disponible: True
- Robustez disponible: True
- CI width Uno valid: 0.12580080587315778
- CI width Uno test: 0.15298947239507243
- CI width Dynamic AUC valid: 0.17264492879960391
- CI width Dynamic AUC test: 0.2827991036665666

## Checks

{"abt_non_empty": true, "canonical_metrics_available": true, "canonical_quality_gate_acceptable": true, "event_rate_minimum": true, "events_minimum": true, "h3_coverage_minimum": true, "renta_coverage_minimum": true, "robustness_status_acceptable": true, "transition_rows_flagged": true}

## Warnings

["low_cases_valid_h6", "low_cases_valid_h12", "wide_dynamic_auc_ci_test", "wide_uno_ci_test", "low_controls_test_h24"]

## Siguientes acciones

- stabilize valid/test evaluation under rare-event regime
- monitor robust survival metrics (Uno, dynamic AUC, IBS) in each iteration
- refresh survival_canonical_robustness after each training run to keep readiness tied to bootstrap intervals
- prepare frontend validation on top of local_survival_map_export.csv

