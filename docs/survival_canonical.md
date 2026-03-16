# Survival Canonical Models

Entrenamiento de modelos de supervivencia canónicos (Cox, RSF, GBSA) con reglas PiT y quality gate.

## Resumen

- Filas modeladas: 203828
- Split rows: {"train": 149684, "test": 51902, "valid": 2242}
- Split events: {"test": 6, "train": 779, "valid": 4}

## C-index por modelo

{
  "cox": {
    "train": 0.5245678420817634,
    "valid": 0.6286503067484662,
    "test": 0.42544428080510555
  },
  "rsf": {
    "train": 0.5246035515813315,
    "valid": 0.6877914110429448,
    "test": 0.5821551300932745
  },
  "gbsa": {
    "train": 0.5247986195804228,
    "valid": 0.6742331288343558,
    "test": 0.3826525936835215
  },
  "ensemble": {
    "train": 0.5246315751184774,
    "valid": 0.6637423312883436,
    "test": 0.50497627229586
  }
}

## Horizon metrics (ensemble)

{"train": {"h6": {"rows": 149684, "events": 205, "auc": 0.5014156976777389, "brier": 0.24359672444635985}, "h12": {"rows": 149684, "events": 296, "auc": 0.5291657191069292, "brier": 0.24350513735356896}, "h24": {"rows": 149684, "events": 460, "auc": 0.5239302775634646, "brier": 0.24350257688584914}}, "valid": {"h6": {"rows": 2242, "events": 1, "auc": 0.9089692101740294, "brier": 0.3310286852160171}, "h12": {"rows": 2242, "events": 2, "auc": 0.47901785714285716, "brier": 0.3314533609661675}, "h24": {"rows": 2242, "events": 2, "auc": 0.47901785714285716, "brier": 0.3314533609661675}}, "test": {"h6": {"rows": 51902, "events": 2, "auc": 0.49028901734104047, "brier": 0.38732394102415774}, "h12": {"rows": 51902, "events": 5, "auc": 0.4401757327013122, "brier": 0.3873238024803006}, "h24": {"rows": 51902, "events": 6, "auc": 0.5067651328297621, "brier": 0.3873076172052598}}}

## Quality gate

{"status": "pass", "checks": {"events_train_positive": true, "events_valid_positive": true, "events_test_positive": true, "c_index_train_finite": true, "c_index_valid_finite": true, "c_index_test_finite": true}, "warnings": []}

