# Survival Baseline

Baseline heuristico de riesgo para supervivencia, con split temporal bloqueado y politicas PiT de robustez.

## Politicas aplicadas

- `transition_policy`: exclude_transition
- Filas bloqueadas por transición CRS: 42
- `renta_max_year`: 2023
- Mediana ciudad para imputación de renta: 13366.0

## Split temporal

- Train: 149,213
- Validation: 2,742
- Test: 51,873
- Eventos train: 14,918
- Eventos validation: 52
- Eventos test: 266
- Tasa evento train: 0.09997788396453391
- Tasa evento validation: 0.018964259664478483
- Tasa evento test: 0.005127908545871648

## Concordance index (sampled)

- Train C-index: 0.4493215542095379
- Validation C-index: 0.3995656894679696
- Test C-index: 0.4966650786088614

## Horizon metrics (6/12/24 meses)

{"test": {"h12": {"auc": 0.4740558912948691, "brier": 0.39830358901705415, "events": 182, "rows": 51873}, "h24": {"auc": 0.4817436755607118, "brier": 0.39795026462053207, "events": 266, "rows": 51873}, "h6": {"auc": 0.4910398958973751, "brier": 0.39878309021500524, "events": 56, "rows": 51873}}, "train": {"h12": {"auc": 0.45080694335871513, "brier": 0.2618069994693564, "events": 1492, "rows": 149213}, "h24": {"auc": 0.4482248203332276, "brier": 0.26310743933870806, "events": 2934, "rows": 149213}, "h6": {"auc": 0.43636819862273724, "brier": 0.2613290106373431, "events": 819, "rows": 149213}}, "valid": {"h12": {"auc": 0.3309909207630227, "brier": 0.2671429851398653, "events": 16, "rows": 2742}, "h24": {"auc": 0.4132737656595431, "brier": 0.2673088386232743, "events": 28, "rows": 2742}, "h6": {"auc": 0.3596638655462185, "brier": 0.26550967357179867, "events": 5, "rows": 2742}}}

## Quality gate

- Estado: pass
- Checks: {"c_index_test_finite": true, "c_index_train_finite": true, "c_index_valid_finite": true, "events_test_positive": true, "events_train_positive": true, "events_valid_positive": true}
- Warnings: ["c_index_train_outside_expected_range", "c_index_valid_outside_expected_range"]

