# Modeling Readiness

Chequeo continuo de calidad para asegurar que el paso a modelos de supervivencia avanzados sea estable y trazable.

- Estado global: ready_with_caveats

## Resumen

- Filas ABT: 203,870
- Eventos totales: 789
- Tasa de evento: 0.0038701133074998772
- Mediana duracion (meses): 135.0
- Cobertura H3: 0.8034531809486437
- Cobertura renta observada: 0.2603816157355177
- Filas marcadas por transicion CRS: 142878

## Checks

{"abt_non_empty": true, "baseline_quality_gate_pass": true, "event_rate_minimum": true, "events_minimum": true, "h3_coverage_minimum": true, "renta_coverage_minimum": true, "transition_rows_flagged": true}

## Warnings

["low_observed_renta_coverage_expected_due_to_post_2023_carry_forward", "very_low_validation_events", "very_low_test_events"]

## Siguientes acciones

- enable canonical survival stack (scikit-learn/scikit-survival/scipy)
- train Cox/GBSA/RSF with the same policy gate
- stabilize validation/test horizons to increase observed events

