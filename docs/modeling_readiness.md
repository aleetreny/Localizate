# Modeling Readiness

Chequeo continuo de calidad para asegurar que el paso a modelos de supervivencia avanzados sea estable y trazable.

- Estado global: ready_with_caveats

## Lectura ejecutiva

- Estado final: ready_with_caveats; gate canonico: pass_with_caveats.
- Discriminacion ensemble: valid Uno=0.6637, test Uno=0.5050.
- Horizontes dinamicos: valid mean AUC=0.6940, test mean AUC=0.5124.
- La principal limitacion sigue siendo estadistica: muy pocos eventos en valid/test para declarar estabilidad fuerte.
- La pipeline sirve para export operativo y comparacion iterativa, pero todavia no para afirmar excelencia robusta fuera de muestra.

## Resumen

- Filas ABT: 203,870
- Eventos totales: 789
- Tasa de evento: 0.0038701133074998772
- Mediana duracion (meses): 135.0
- Cobertura H3: 0.8034531809486437
- Cobertura renta observada: 0.2603816157355177
- Filas marcadas por transicion CRS: 142878
- Quality gate canonico: pass_with_caveats
- Uno C-index valid: 0.6637423312883436
- Uno C-index test: 0.50497627229586
- Dynamic AUC valid: 0.6939935336584433
- Dynamic AUC test: 0.5124169017509562
- IBS valido disponible: True
- IBS test disponible: True

## Checks

{"abt_non_empty": true, "canonical_metrics_available": true, "canonical_quality_gate_acceptable": true, "event_rate_minimum": true, "events_minimum": true, "h3_coverage_minimum": true, "renta_coverage_minimum": true, "transition_rows_flagged": true}

## Warnings

["low_observed_renta_coverage_expected_due_to_post_2023_carry_forward", "very_low_validation_events", "very_low_test_events"]

## Siguientes acciones

- stabilize valid/test evaluation under rare-event regime
- monitor robust survival metrics (Uno, dynamic AUC, IBS) in each iteration
- prepare frontend validation on top of local_survival_map_export.csv

