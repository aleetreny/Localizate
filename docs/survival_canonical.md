# Survival Canonical Models

Entrenamiento de modelos de supervivencia canónicos (Cox, RSF, GBSA) con reglas PiT y quality gate.

## Resumen

- Filas modeladas: 203828
- Split rows: {"train": 149213, "test": 51873, "valid": 2742}
- Split events: {"test": 266, "train": 14918, "valid": 52}
- Training run: {"rsf_n_estimators": 300, "rsf_chunk_size": 25, "gbsa_n_estimators": 300, "gbsa_chunk_size": 25, "fit_max_rows": null, "quick_mode": false}

## Lectura ejecutiva

- Quality gate canonico: pass.
- Validacion: Uno=0.7428 (muy_bueno), mean Dynamic AUC=0.8025 (muy_bueno).
- Test: Uno=0.5335 (debil), mean Dynamic AUC=0.8655 (muy_bueno).
- Regimen de evento raro confirmado: valid=52 eventos, test=266 eventos.

## C-index por modelo

{
  "cox": {
    "train": 0.743690583357841,
    "valid": 0.5569621247221982,
    "test": 0.6099492085244677
  },
  "rsf": {
    "train": 0.8894028367606309,
    "valid": 0.8121588829816474,
    "test": 0.3618987633781584
  },
  "gbsa": {
    "train": 0.7311671480514903,
    "valid": 0.7093270718318818,
    "test": 0.5573511283567036
  },
  "ensemble": {
    "train": 0.8158195017304891,
    "valid": 0.7427732273694626,
    "test": 0.533520466358229
  }
}

## Interpretacion de discriminacion

- En train, el ensemble marca Uno/IPCW C-index=0.8151 y se clasifica como muy_bueno.
- En valid, el ensemble marca Uno/IPCW C-index=0.7428 y se clasifica como muy_bueno.
- En test, el ensemble marca Uno/IPCW C-index=0.5335 y se clasifica como debil.

## Uno / IPCW C-index (ensemble)

{
  "train": {
    "rows": 149213,
    "events": 14918,
    "tau": 134.99999999999997,
    "uno_c_index": 0.8150904860072549
  },
  "valid": {
    "rows": 2742,
    "events": 52,
    "tau": 54.99999999999999,
    "uno_c_index": 0.7427732273694626
  },
  "test": {
    "rows": 51873,
    "events": 266,
    "tau": 25.999999999999996,
    "uno_c_index": 0.533520466358229
  }
}

## Cumulative Dynamic AUC (ensemble)

{
  "train": {
    "rows": 149213,
    "events": 14918,
    "tau": 134.99999999999997,
    "mean_auc": 0.8421770871151985,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 819,
        "controls": 148394,
        "auc": 0.8476788264380755,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 1492,
        "controls": 147721,
        "auc": 0.8387537830581391,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 2934,
        "controls": 146279,
        "auc": 0.8406500129993625,
        "supported": true
      }
    }
  },
  "valid": {
    "rows": 2742,
    "events": 52,
    "tau": 54.99999999999999,
    "mean_auc": 0.8024609060633587,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 5,
        "controls": 2737,
        "auc": 0.8919254658385094,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 16,
        "controls": 2726,
        "auc": 0.8034207630227439,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 28,
        "controls": 2714,
        "auc": 0.764304137277608,
        "supported": true
      }
    }
  },
  "test": {
    "rows": 51873,
    "events": 266,
    "tau": 25.999999999999996,
    "mean_auc": 0.8655353997712787,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 56,
        "controls": 51081,
        "auc": 0.48933871134640505,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 182,
        "controls": 50265,
        "auc": 0.5390191326628211,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 266,
        "controls": 55,
        "auc": 0.968626110731374,
        "supported": true
      }
    }
  }
}

## Interpretacion por horizontes

- En valid, la media de Dynamic AUC es 0.8025 (muy_bueno).
- valid:h6 -> AUC=0.8919, cases=5, controls=2737, estado=muy_bueno.
- valid:h12 -> AUC=0.8034, cases=16, controls=2726, estado=muy_bueno.
- valid:h24 -> AUC=0.7643, cases=28, controls=2714, estado=muy_bueno.
- En test, la media de Dynamic AUC es 0.8655 (muy_bueno).
- test:h6 -> AUC=0.4893, cases=56, controls=51081, estado=debil.
- test:h12 -> AUC=0.5390, cases=182, controls=50265, estado=debil.
- test:h24 -> AUC=0.9686, cases=266, controls=55, estado=muy_bueno.

## Integrated Brier Score (modelos base)

{
  "cox": {
    "train": {
      "rows": 149213,
      "events": 14918,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.011227814247236043
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.006523989195188659
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.02705434733720965
    }
  },
  "rsf": {
    "train": {
      "rows": 149213,
      "events": 14918,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.010467716181318575
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.006277824441185378
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.04045738310553929
    }
  },
  "gbsa": {
    "train": {
      "rows": 149213,
      "events": 14918,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.011270272364350355
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.006411272788298049
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.00411738123018396
    }
  }
}

## Interpretacion de IBS

- En valid, el mejor IBS base es rsf=0.0063 (muy_bueno; menor es mejor).
- En test, el mejor IBS base es gbsa=0.0041 (muy_bueno; menor es mejor).

Nota: el ensemble actual es rank-based; no se reporta IBS para el ensemble hasta definir una agregacion explicita de curvas de supervivencia.

## Calibration (12 meses)

{
  "train": [
    {
      "decile": 1,
      "rows": 19650,
      "event_rate": 5.089058524173028e-05
    },
    {
      "decile": 2,
      "rows": 18167,
      "event_rate": 0.00016513458468651952
    },
    {
      "decile": 3,
      "rows": 18742,
      "event_rate": 0.001440614662255896
    },
    {
      "decile": 4,
      "rows": 18962,
      "event_rate": 0.00421896424427803
    },
    {
      "decile": 5,
      "rows": 19184,
      "event_rate": 0.007402001668056714
    },
    {
      "decile": 6,
      "rows": 20060,
      "event_rate": 0.009122632103688933
    },
    {
      "decile": 7,
      "rows": 20165,
      "event_rate": 0.01567071658814778
    },
    {
      "decile": 8,
      "rows": 13614,
      "event_rate": 0.032466578522109595
    },
    {
      "decile": 9,
      "rows": 8,
      "event_rate": 0.0
    },
    {
      "decile": 10,
      "rows": 661,
      "event_rate": 0.4508320726172466
    }
  ],
  "valid": [
    {
      "decile": 1,
      "rows": 322,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 640,
      "event_rate": 0.0
    },
    {
      "decile": 3,
      "rows": 561,
      "event_rate": 0.0017825311942959
    },
    {
      "decile": 4,
      "rows": 454,
      "event_rate": 0.006607929515418502
    },
    {
      "decile": 5,
      "rows": 294,
      "event_rate": 0.013605442176870748
    },
    {
      "decile": 6,
      "rows": 188,
      "event_rate": 0.015957446808510637
    },
    {
      "decile": 7,
      "rows": 197,
      "event_rate": 0.01015228426395939
    },
    {
      "decile": 8,
      "rows": 85,
      "event_rate": 0.023529411764705882
    },
    {
      "decile": 10,
      "rows": 1,
      "event_rate": 1.0
    }
  ],
  "test": [
    {
      "decile": 1,
      "rows": 410,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 1576,
      "event_rate": 0.0031725888324873096
    },
    {
      "decile": 3,
      "rows": 1080,
      "event_rate": 0.002777777777777778
    },
    {
      "decile": 4,
      "rows": 962,
      "event_rate": 0.0
    },
    {
      "decile": 5,
      "rows": 910,
      "event_rate": 0.002197802197802198
    },
    {
      "decile": 6,
      "rows": 134,
      "event_rate": 0.014925373134328358
    },
    {
      "decile": 7,
      "rows": 21,
      "event_rate": 0.0
    },
    {
      "decile": 8,
      "rows": 6684,
      "event_rate": 0.005535607420706164
    },
    {
      "decile": 9,
      "rows": 20377,
      "event_rate": 0.0023555969966138294
    },
    {
      "decile": 10,
      "rows": 19719,
      "event_rate": 0.0043105634159947255
    }
  ]
}

## Quality gate

{
  "status": "pass",
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
  "warnings": []
}

