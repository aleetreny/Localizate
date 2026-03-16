# Survival Baseline

Baseline heuristico de riesgo para supervivencia, con split temporal bloqueado y politicas PiT de robustez.

## Politicas aplicadas

- `transition_policy`: exclude_transition
- Filas bloqueadas por transicion CRS: 42
- `renta_max_year`: 2023
- Mediana ciudad para imputacion de renta: 24909.0

## Split temporal

- Train: 149,684
- Validation: 2,242
- Test: 51,902
- Eventos train: 779
- Eventos validation: 4
- Eventos test: 6
- Tasa evento train: 0.005204297052457177
- Tasa evento validation: 0.001784121320249777
- Tasa evento test: 0.00011560248159993835

## Concordance index (sampled)

- Train C-index: 0.5251727541954591
- Validation C-index: 0.5078125
- Test C-index: 0.5689655172413793

## Horizon metrics (6/12/24 meses)

{"test": {"h12": {"auc": 0.6491049578973737, "brier": 0.469534193147273, "events": 5, "rows": 51902}, "h24": {"auc": 0.6373082703869277, "brier": 0.46952472389454375, "events": 6, "rows": 51902}, "h6": {"auc": 0.8978227360308285, "brier": 0.46954968538920533, "events": 2, "rows": 51902}}, "train": {"h12": {"auc": 0.5279662305992232, "brier": 0.1838148022363069, "events": 296, "rows": 149684}, "h24": {"auc": 0.5227304763891576, "brier": 0.18396405069224195, "events": 460, "rows": 149684}, "h6": {"auc": 0.5002220884604233, "brier": 0.1837716053859373, "events": 205, "rows": 149684}}, "valid": {"h12": {"auc": 0.3752232142857143, "brier": 0.295261771870887, "events": 2, "rows": 2242}, "h24": {"auc": 0.3752232142857143, "brier": 0.295261771870887, "events": 2, "rows": 2242}, "h6": {"auc": 0.7434181169120928, "brier": 0.29481840585661134, "events": 1, "rows": 2242}}}

## Quality gate

- Estado: pass
- Checks: {"c_index_test_finite": true, "c_index_train_finite": true, "c_index_valid_finite": true, "events_test_positive": true, "events_train_positive": true, "events_valid_positive": true}
- Warnings: []

