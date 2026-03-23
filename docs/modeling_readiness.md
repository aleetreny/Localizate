# Modeling Readiness

Chequeo continuo de calidad para asegurar que el paso a modelos de supervivencia avanzados sea estable y trazable.

- Estado global: ready

## Lectura ejecutiva

- Estado final: ready; gate canonico: pass.
- Discriminacion ensemble: valid Uno=0.5235, test Uno=0.5262.
- Horizontes dinamicos: valid mean AUC=0.5924, test mean AUC=0.6438.

## Resumen

- Filas ABT: 203,870
- Eventos totales: 15,241
- Tasa de evento: 0.07475842448619219
- Mediana duracion (meses): 135.0
- Cobertura H3: 0.8065973414430765
- Cobertura renta observada: 0.7672389267670574
- Filas marcadas por transicion CRS: 142878
- Quality gate canonico: pass
- Uno C-index valid: 0.5234531447553381
- Uno C-index test: 0.5261766177702657
- Dynamic AUC valid: 0.5923551651311448
- Dynamic AUC test: 0.6437722072350108
- IBS valido disponible: True
- IBS test disponible: True

## Checks

{"abt_non_empty": true, "canonical_metrics_available": true, "canonical_quality_gate_acceptable": true, "event_rate_minimum": true, "events_minimum": true, "h3_coverage_minimum": true, "renta_coverage_minimum": true, "transition_rows_flagged": true}

## Warnings

[]

## Siguientes acciones

- stabilize valid/test evaluation under rare-event regime
- monitor robust survival metrics (Uno, dynamic AUC, IBS) in each iteration
- prepare frontend validation on top of local_survival_map_export.csv

