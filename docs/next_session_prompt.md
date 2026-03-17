# Prompt de continuidad (sin contexto previo)

Copia y pega este bloque en un chat nuevo para retomar el proyecto desde cero contexto:

---

Estoy trabajando en el repo **Localizate** (Madrid Local Predict). Quiero que actúes con autonomía, pero con estas reglas operativas:

1. **Antes de cualquier ejecución larga**, avísame explícitamente y espera confirmación.
2. Si ejecutas algo de entrenamiento, debe incluir **progreso (%) + ETA** y, si aplica, archivo de progreso.
3. Prioriza cambios robustos y trazables; evita ejecutar entrenamientos pesados innecesarios.

## Contexto canónico que debes leer primero

1. `STATUS.md` (fuente única de estado)
2. `README.md` (narrativa pública)
3. `docs/survival_canonical.md`
4. `models/survival_canonical_metrics.json`
5. `src/localizate/survival_canonical.py`
6. `scripts/train_survival_canonical.py`

## Estado actual resumido

- Pipeline de datos histórico: cerrado (raw -> normalizado -> geoespacial -> panel socioeconómico -> ABT).
- ABT survival disponible: `data/features/local_survival_abt.csv`.
- Modelos canónicos entrenados al menos una iteración: Cox + RSF + GBSA + ensemble.
- Export mapa disponible: `data/exports/local_survival_map_export.csv`.
- Readiness actual: `ready_with_caveats` por régimen de evento raro en valid/test.
- Tests: `31/31` en verde.

## Decisiones de política ya cerradas

- Transición CRS `2017-09`: excluir en entrenamiento (`exclude_transition`).
- Renta post-2023: `renta_max_year=2023` + imputación jerárquica (`district -> city`).

## Problema principal pendiente

- **Robustecer evaluación y estabilidad** bajo censura alta y evento raro.

## Objetivo inmediato

Implementar (sin lanzar entrenamiento largo al inicio) una mejora de evaluación survival con métricas más robustas:

- IPCW / Uno C-index
- Cumulative Dynamic AUC (por horizontes)
- Integrated Brier Score (IBS)

y dejar:

1. módulo/código integrado en pipeline,
2. reporte claro en `docs/` con interpretación,
3. quality gate actualizado,
4. tests nuevos/ajustados en verde.

## Restricciones de ejecución

- Si necesitas un entrenamiento largo para validar resultados, primero propón:
  - comando exacto,
  - duración estimada,
  - criterio de éxito,
  - plan de rollback.
- No ejecutes ese entrenamiento hasta mi confirmación.

## Criterio de finalización de esta iteración

- Código actualizado + tests en verde + documentación actualizada + resumen ejecutivo corto de cambios/riesgos.

---

## Comandos de referencia

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -u scripts/run_modeling_readiness.py
PYTHONPATH=src .venv/bin/python -u scripts/train_survival_canonical.py --quick --rsf-chunk-size 20
```
