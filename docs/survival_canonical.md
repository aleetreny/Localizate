# Survival Canonical Models

Entrenamiento de modelos de supervivencia canónicos (Cox, RSF, GBSA) con reglas PiT y quality gate.

## Resumen

- Filas modeladas: 203828
- Split rows: {"train": 149213, "test": 51873, "valid": 2742}
- Split events: {"test": 266, "train": 14918, "valid": 52}
- Training run: {"rsf_n_estimators": 300, "rsf_chunk_size": 25, "gbsa_n_estimators": 300, "gbsa_chunk_size": 25, "fit_max_rows": null, "quick_mode": false}

## Lectura ejecutiva

- Quality gate canonico: pass.
- Validacion: Uno=0.6863 (bueno), mean Dynamic AUC=0.7398 (muy_bueno).
- Test: Uno=0.6418 (bueno), mean Dynamic AUC=0.8773 (muy_bueno).
- Regimen de evento raro confirmado: valid=52 eventos, test=266 eventos.

## C-index por modelo

{
  "cox": {
    "train": 0.6722624775930948,
    "valid": 0.5364538750893285,
    "test": 0.5395937084319244
  },
  "rsf": {
    "train": 0.823096704662214,
    "valid": 0.7726226843308021,
    "test": 0.3568127980271752
  },
  "gbsa": {
    "train": 0.7067441241237733,
    "valid": 0.7007868759767235,
    "test": 0.6884383413274185
  },
  "ensemble": {
    "train": 0.7499628993949655,
    "valid": 0.6863451102961386,
    "test": 0.6418470390192624
  }
}

## Interpretacion de discriminacion

- En train, el ensemble marca Uno/IPCW C-index=0.7494 y se clasifica como muy_bueno.
- En valid, el ensemble marca Uno/IPCW C-index=0.6863 y se clasifica como bueno.
- En test, el ensemble marca Uno/IPCW C-index=0.6418 y se clasifica como bueno.

## Uno / IPCW C-index (ensemble)

{
  "train": {
    "rows": 149213,
    "events": 14918,
    "tau": 134.99999999999997,
    "uno_c_index": 0.749418520998962
  },
  "valid": {
    "rows": 2742,
    "events": 52,
    "tau": 54.99999999999999,
    "uno_c_index": 0.6863451102961386
  },
  "test": {
    "rows": 51873,
    "events": 266,
    "tau": 25.999999999999996,
    "uno_c_index": 0.6418470390192624
  }
}

## Cumulative Dynamic AUC (ensemble)

{
  "train": {
    "rows": 149213,
    "events": 14918,
    "tau": 134.99999999999997,
    "mean_auc": 0.8016250653222365,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 819,
        "controls": 148394,
        "auc": 0.8095258953480984,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 1492,
        "controls": 147721,
        "auc": 0.7998655529218157,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 2934,
        "controls": 146279,
        "auc": 0.7979588878286874,
        "supported": true
      }
    }
  },
  "valid": {
    "rows": 2742,
    "events": 52,
    "tau": 54.99999999999999,
    "mean_auc": 0.7397564434685907,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 5,
        "controls": 2737,
        "auc": 0.8530507855316039,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 16,
        "controls": 2726,
        "auc": 0.7473404255319149,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 28,
        "controls": 2714,
        "auc": 0.6855984840509527,
        "supported": true
      }
    }
  },
  "test": {
    "rows": 51873,
    "events": 266,
    "tau": 25.999999999999996,
    "mean_auc": 0.8772892767478985,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 56,
        "controls": 51081,
        "auc": 0.6461673616413148,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 182,
        "controls": 50265,
        "auc": 0.6530279081308624,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 266,
        "controls": 55,
        "auc": 0.9455912508544089,
        "supported": true
      }
    }
  }
}

## Interpretacion por horizontes

- En valid, la media de Dynamic AUC es 0.7398 (muy_bueno).
- valid:h6 -> AUC=0.8531, cases=5, controls=2737, estado=muy_bueno.
- valid:h12 -> AUC=0.7473, cases=16, controls=2726, estado=muy_bueno.
- valid:h24 -> AUC=0.6856, cases=28, controls=2714, estado=bueno.
- En test, la media de Dynamic AUC es 0.8773 (muy_bueno).
- test:h6 -> AUC=0.6462, cases=56, controls=51081, estado=bueno.
- test:h12 -> AUC=0.6530, cases=182, controls=50265, estado=bueno.
- test:h24 -> AUC=0.9456, cases=266, controls=55, estado=muy_bueno.

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
      "ibs": 0.011112514965522902
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.00645542371378309
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.06969880068818216
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
      "ibs": 0.010608983476922814
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.006308049094627375
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.015795378554777195
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
      "ibs": 0.011367682694577405
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.00645043731647577
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.0036192245402403974
    }
  }
}

## Interpretacion de IBS

- En valid, el mejor IBS base es rsf=0.0063 (muy_bueno; menor es mejor).
- En test, el mejor IBS base es gbsa=0.0036 (muy_bueno; menor es mejor).

Nota: el ensemble actual es rank-based; no se reporta IBS para el ensemble hasta definir una agregacion explicita de curvas de supervivencia.

## Calibration (12 meses)

{
  "train": [
    {
      "decile": 1,
      "rows": 20089,
      "event_rate": 4.977848573846384e-05
    },
    {
      "decile": 2,
      "rows": 19713,
      "event_rate": 0.0009638309744838432
    },
    {
      "decile": 3,
      "rows": 17927,
      "event_rate": 0.003012216210185753
    },
    {
      "decile": 4,
      "rows": 19263,
      "event_rate": 0.006852515184550693
    },
    {
      "decile": 5,
      "rows": 19156,
      "event_rate": 0.007151806222593443
    },
    {
      "decile": 6,
      "rows": 17274,
      "event_rate": 0.010072941993747829
    },
    {
      "decile": 7,
      "rows": 15935,
      "event_rate": 0.015563225604016316
    },
    {
      "decile": 8,
      "rows": 9408,
      "event_rate": 0.01796343537414966
    },
    {
      "decile": 9,
      "rows": 8683,
      "event_rate": 0.023033513762524473
    },
    {
      "decile": 10,
      "rows": 1765,
      "event_rate": 0.2028328611898017
    }
  ],
  "valid": [
    {
      "decile": 1,
      "rows": 248,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 384,
      "event_rate": 0.0
    },
    {
      "decile": 3,
      "rows": 448,
      "event_rate": 0.004464285714285714
    },
    {
      "decile": 4,
      "rows": 622,
      "event_rate": 0.001607717041800643
    },
    {
      "decile": 5,
      "rows": 362,
      "event_rate": 0.008287292817679558
    },
    {
      "decile": 6,
      "rows": 185,
      "event_rate": 0.021621621621621623
    },
    {
      "decile": 7,
      "rows": 195,
      "event_rate": 0.010256410256410256
    },
    {
      "decile": 8,
      "rows": 123,
      "event_rate": 0.008130081300813009
    },
    {
      "decile": 9,
      "rows": 168,
      "event_rate": 0.011904761904761904
    },
    {
      "decile": 10,
      "rows": 7,
      "event_rate": 0.14285714285714285
    }
  ],
  "test": [
    {
      "decile": 1,
      "rows": 45,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 286,
      "event_rate": 0.0
    },
    {
      "decile": 3,
      "rows": 2008,
      "event_rate": 0.00149402390438247
    },
    {
      "decile": 4,
      "rows": 498,
      "event_rate": 0.002008032128514056
    },
    {
      "decile": 5,
      "rows": 865,
      "event_rate": 0.003468208092485549
    },
    {
      "decile": 6,
      "rows": 2923,
      "event_rate": 0.004105371193978789
    },
    {
      "decile": 7,
      "rows": 4220,
      "event_rate": 0.0016587677725118483
    },
    {
      "decile": 8,
      "rows": 10886,
      "event_rate": 0.0010104721660848797
    },
    {
      "decile": 9,
      "rows": 11531,
      "event_rate": 0.0026884051686757436
    },
    {
      "decile": 10,
      "rows": 18611,
      "event_rate": 0.006125409703938531
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

