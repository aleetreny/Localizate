# Survival Canonical Models

Entrenamiento de modelos de supervivencia canónicos (Cox, RSF, GBSA) con reglas PiT y quality gate.

## Resumen

- Filas modeladas: 203828
- Split rows: {"train": 149684, "test": 51902, "valid": 2242}
- Split events: {"test": 6, "train": 779, "valid": 4}
- Training run: {"rsf_n_estimators": 300, "rsf_chunk_size": 25, "gbsa_n_estimators": 300, "gbsa_chunk_size": 25, "fit_max_rows": null, "quick_mode": false}

## Lectura ejecutiva

- Quality gate canonico: pass_with_caveats.
- Validacion: Uno=0.6637 (bueno), mean Dynamic AUC=0.6940 (bueno).
- Test: Uno=0.5050 (debil), mean Dynamic AUC=0.5124 (debil).
- Regimen de evento raro confirmado: valid=4 eventos, test=6 eventos.
- El modelo es util para ranking y export operativo, pero la lectura fuera de train sigue siendo fragil por muy bajo numero de eventos.

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

## Interpretacion de discriminacion

- En train, el ensemble marca Uno/IPCW C-index=0.5249 y se clasifica como debil.
- En valid, el ensemble marca Uno/IPCW C-index=0.6637 y se clasifica como bueno.
- En test, el ensemble marca Uno/IPCW C-index=0.5050 y se clasifica como debil.

## Uno / IPCW C-index (ensemble)

{
  "train": {
    "rows": 149684,
    "events": 779,
    "tau": 134.99999999999997,
    "uno_c_index": 0.5249371026114025
  },
  "valid": {
    "rows": 2242,
    "events": 4,
    "tau": 52.99999999999999,
    "uno_c_index": 0.6637423312883436
  },
  "test": {
    "rows": 51902,
    "events": 6,
    "tau": 26.999999999999996,
    "uno_c_index": 0.50497627229586
  }
}

## Cumulative Dynamic AUC (ensemble)

{
  "train": {
    "rows": 149684,
    "events": 779,
    "tau": 134.99999999999997,
    "mean_auc": 0.5149323130066861,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 205,
        "controls": 149479,
        "auc": 0.501415697677739,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 296,
        "controls": 149388,
        "auc": 0.5291657191069292,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 460,
        "controls": 149224,
        "auc": 0.5239302775634647,
        "supported": true
      }
    }
  },
  "valid": {
    "rows": 2242,
    "events": 4,
    "tau": 52.99999999999999,
    "mean_auc": 0.6939935336584433,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 1,
        "controls": 2241,
        "auc": 0.9089692101740294,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 2,
        "controls": 2240,
        "auc": 0.47901785714285716,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 2,
        "controls": 2240,
        "auc": 0.47901785714285716,
        "supported": true
      }
    }
  },
  "test": {
    "rows": 51902,
    "events": 6,
    "tau": 26.999999999999996,
    "mean_auc": 0.5124169017509562,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 2,
        "controls": 51162,
        "auc": 0.4891130135647551,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 5,
        "controls": 50464,
        "auc": 0.4387999365884591,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 6,
        "controls": 85,
        "auc": 0.7745098039215687,
        "supported": true
      }
    }
  }
}

## Interpretacion por horizontes

- En valid, la media de Dynamic AUC es 0.6940 (bueno).
- valid:h6 -> AUC=0.9090, cases=1, controls=2241, estado=muy_bueno.
- valid:h12 -> AUC=0.4790, cases=2, controls=2240, estado=debil.
- valid:h24 -> AUC=0.4790, cases=2, controls=2240, estado=debil.
- En test, la media de Dynamic AUC es 0.5124 (debil).
- test:h6 -> AUC=0.4891, cases=2, controls=51162, estado=debil.
- test:h12 -> AUC=0.4388, cases=5, controls=50464, estado=debil.
- test:h24 -> AUC=0.7745, cases=6, controls=85, estado=muy_bueno.

## Integrated Brier Score (modelos base)

{
  "cox": {
    "train": {
      "rows": 149684,
      "events": 779,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.002235506192388577
    },
    "valid": {
      "rows": 2242,
      "events": 4,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.001966830122466364
    },
    "test": {
      "rows": 51902,
      "events": 6,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.0006463670233419147
    }
  },
  "rsf": {
    "train": {
      "rows": 149684,
      "events": 779,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.002235500590033494
    },
    "valid": {
      "rows": 2242,
      "events": 4,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.0008216127593426573
    },
    "test": {
      "rows": 51902,
      "events": 6,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 9.731112036185092e-05
    }
  },
  "gbsa": {
    "train": {
      "rows": 149684,
      "events": 779,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.0022359266408922846
    },
    "valid": {
      "rows": 2242,
      "events": 4,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.0008193181102032215
    },
    "test": {
      "rows": 51902,
      "events": 6,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 9.488876162506395e-05
    }
  }
}

## Interpretacion de IBS

- En valid, el mejor IBS base es gbsa=0.0008 (muy_bueno; menor es mejor).
- En test, el mejor IBS base es gbsa=0.0001 (muy_bueno; menor es mejor).

Nota: el ensemble actual es rank-based; no se reporta IBS para el ensemble hasta definir una agregacion explicita de curvas de supervivencia.

## Calibration (12 meses)

{
  "train": [
    {
      "decile": 1,
      "rows": 195,
      "event_rate": 0.0
    },
    {
      "decile": 5,
      "rows": 145367,
      "event_rate": 0.0018642470436894207
    },
    {
      "decile": 9,
      "rows": 30,
      "event_rate": 0.0
    },
    {
      "decile": 10,
      "rows": 4092,
      "event_rate": 0.006109481915933529
    }
  ],
  "valid": [
    {
      "decile": 1,
      "rows": 509,
      "event_rate": 0.0019646365422396855
    },
    {
      "decile": 2,
      "rows": 1,
      "event_rate": 0.0
    },
    {
      "decile": 5,
      "rows": 1079,
      "event_rate": 0.0
    },
    {
      "decile": 9,
      "rows": 178,
      "event_rate": 0.0
    },
    {
      "decile": 10,
      "rows": 475,
      "event_rate": 0.002105263157894737
    }
  ],
  "test": [
    {
      "decile": 1,
      "rows": 19678,
      "event_rate": 5.0818172578514075e-05
    },
    {
      "decile": 2,
      "rows": 256,
      "event_rate": 0.0
    },
    {
      "decile": 9,
      "rows": 16157,
      "event_rate": 0.0002475707123847249
    },
    {
      "decile": 10,
      "rows": 15811,
      "event_rate": 0.0
    }
  ]
}

## Quality gate

{
  "status": "pass_with_caveats",
  "checks": {
    "events_train_positive": true,
    "uno_c_index_train_finite": true,
    "dynamic_auc_train_finite": true,
    "ibs_train_available": true,
    "events_valid_positive": true,
    "uno_c_index_valid_finite": true,
    "dynamic_auc_valid_finite": true,
    "ibs_valid_available": true,
    "events_test_positive": true,
    "uno_c_index_test_finite": true,
    "dynamic_auc_test_finite": true,
    "ibs_test_available": true
  },
  "warnings": [
    "very_low_validation_events",
    "very_low_test_events"
  ]
}

