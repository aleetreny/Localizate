# Survival Canonical Models

Entrenamiento de modelos de supervivencia canónicos (Cox, RSF, GBSA) con reglas PiT y quality gate.

## Resumen

- Filas modeladas: 203828
- Split rows: {"train": 149213, "test": 51873, "valid": 2742}
- Split events: {"test": 266, "train": 14918, "valid": 52}
- Training run: {"rsf_n_estimators": 300, "rsf_chunk_size": 25, "gbsa_n_estimators": 300, "gbsa_chunk_size": 25, "fit_max_rows": null, "quick_mode": false}

## Lectura ejecutiva

- Quality gate canonico: pass.
- Validacion: Uno=0.5235 (debil), mean Dynamic AUC=0.5924 (usable).
- Test: Uno=0.5262 (debil), mean Dynamic AUC=0.6438 (bueno).
- Regimen de evento raro confirmado: valid=52 eventos, test=266 eventos.

## C-index por modelo

{
  "cox": {
    "train": 0.5781293744779958,
    "valid": 0.4892845082810451,
    "test": 0.5192000361231514
  },
  "rsf": {
    "train": 0.696770205825141,
    "valid": 0.5760921634377528,
    "test": 0.4819198337262074
  },
  "gbsa": {
    "train": 0.6214582669429161,
    "valid": 0.5306151296931811,
    "test": 0.49938949042811
  },
  "ensemble": {
    "train": 0.6523837559547749,
    "valid": 0.5234531447553381,
    "test": 0.5261766177702657
  }
}

## Interpretacion de discriminacion

- En train, el ensemble marca Uno/IPCW C-index=0.6518 y se clasifica como bueno.
- En valid, el ensemble marca Uno/IPCW C-index=0.5235 y se clasifica como debil.
- En test, el ensemble marca Uno/IPCW C-index=0.5262 y se clasifica como debil.

## Uno / IPCW C-index (ensemble)

{
  "train": {
    "rows": 149213,
    "events": 14918,
    "tau": 134.99999999999997,
    "uno_c_index": 0.6517808136157925
  },
  "valid": {
    "rows": 2742,
    "events": 52,
    "tau": 54.99999999999999,
    "uno_c_index": 0.5234531447553381
  },
  "test": {
    "rows": 51873,
    "events": 266,
    "tau": 25.999999999999996,
    "uno_c_index": 0.5261766177702657
  }
}

## Cumulative Dynamic AUC (ensemble)

{
  "train": {
    "rows": 149213,
    "events": 14918,
    "tau": 134.99999999999997,
    "mean_auc": 0.7142414339175641,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 819,
        "controls": 148394,
        "auc": 0.7303411101913737,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 1492,
        "controls": 147721,
        "auc": 0.7086703036462858,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 2934,
        "controls": 146279,
        "auc": 0.7076975613824183,
        "supported": true
      }
    }
  },
  "valid": {
    "rows": 2742,
    "events": 52,
    "tau": 54.99999999999999,
    "mean_auc": 0.5923551651311448,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 5,
        "controls": 2737,
        "auc": 0.5886737303617099,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 16,
        "controls": 2726,
        "auc": 0.6241860785033015,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 28,
        "controls": 2714,
        "auc": 0.564710759027266,
        "supported": true
      }
    }
  },
  "test": {
    "rows": 51873,
    "events": 266,
    "tau": 25.999999999999996,
    "mean_auc": 0.6437722072350108,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 56,
        "controls": 51081,
        "auc": 0.5317716679671223,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 182,
        "controls": 50265,
        "auc": 0.5393694736577458,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 266,
        "controls": 55,
        "auc": 0.6759740259740259,
        "supported": true
      }
    }
  }
}

## Interpretacion por horizontes

- En valid, la media de Dynamic AUC es 0.5924 (usable).
- valid:h6 -> AUC=0.5887, cases=5, controls=2737, estado=usable.
- valid:h12 -> AUC=0.6242, cases=16, controls=2726, estado=bueno.
- valid:h24 -> AUC=0.5647, cases=28, controls=2714, estado=usable.
- En test, la media de Dynamic AUC es 0.6438 (bueno).
- test:h6 -> AUC=0.5318, cases=56, controls=51081, estado=debil.
- test:h12 -> AUC=0.5394, cases=182, controls=50265, estado=debil.
- test:h24 -> AUC=0.6760, cases=266, controls=55, estado=bueno.

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
      "ibs": 0.012280440466704085
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.006620243659141887
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.003595135917524103
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
      "ibs": 0.010903681248608577
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.006356935251209553
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.03014880999341187
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
      "ibs": 0.011080190422102012
    },
    "valid": {
      "rows": 2742,
      "events": 52,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.006344813817999017
    },
    "test": {
      "rows": 51873,
      "events": 266,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.004614068405726437
    }
  }
}

## Interpretacion de IBS

- En valid, el mejor IBS base es gbsa=0.0063 (muy_bueno; menor es mejor).
- En test, el mejor IBS base es cox=0.0036 (muy_bueno; menor es mejor).

Nota: el ensemble actual es rank-based; no se reporta IBS para el ensemble hasta definir una agregacion explicita de curvas de supervivencia.

## Calibration (12 meses)

{
  "train": [
    {
      "decile": 1,
      "rows": 19517,
      "event_rate": 0.00276681867090229
    },
    {
      "decile": 2,
      "rows": 18522,
      "event_rate": 0.004373177842565598
    },
    {
      "decile": 3,
      "rows": 18251,
      "event_rate": 0.00487644512629445
    },
    {
      "decile": 4,
      "rows": 18336,
      "event_rate": 0.007308027923211169
    },
    {
      "decile": 5,
      "rows": 17347,
      "event_rate": 0.009050556292154262
    },
    {
      "decile": 6,
      "rows": 10606,
      "event_rate": 0.007165755232887045
    },
    {
      "decile": 7,
      "rows": 9092,
      "event_rate": 0.011768587769467664
    },
    {
      "decile": 8,
      "rows": 11249,
      "event_rate": 0.011289892434883101
    },
    {
      "decile": 9,
      "rows": 19228,
      "event_rate": 0.013990014562096942
    },
    {
      "decile": 10,
      "rows": 7065,
      "event_rate": 0.05633404104741684
    }
  ],
  "valid": [
    {
      "decile": 1,
      "rows": 257,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 252,
      "event_rate": 0.011904761904761904
    },
    {
      "decile": 3,
      "rows": 278,
      "event_rate": 0.0035971223021582736
    },
    {
      "decile": 4,
      "rows": 345,
      "event_rate": 0.0
    },
    {
      "decile": 5,
      "rows": 349,
      "event_rate": 0.0028653295128939827
    },
    {
      "decile": 6,
      "rows": 256,
      "event_rate": 0.0078125
    },
    {
      "decile": 7,
      "rows": 166,
      "event_rate": 0.006024096385542169
    },
    {
      "decile": 8,
      "rows": 314,
      "event_rate": 0.009554140127388535
    },
    {
      "decile": 9,
      "rows": 435,
      "event_rate": 0.009195402298850575
    },
    {
      "decile": 10,
      "rows": 90,
      "event_rate": 0.011111111111111112
    }
  ],
  "test": [
    {
      "decile": 1,
      "rows": 634,
      "event_rate": 0.0015772870662460567
    },
    {
      "decile": 2,
      "rows": 1583,
      "event_rate": 0.003158559696778269
    },
    {
      "decile": 3,
      "rows": 1861,
      "event_rate": 0.0021493820526598604
    },
    {
      "decile": 4,
      "rows": 1684,
      "event_rate": 0.0059382422802850355
    },
    {
      "decile": 5,
      "rows": 2709,
      "event_rate": 0.0033222591362126247
    },
    {
      "decile": 6,
      "rows": 8024,
      "event_rate": 0.001744765702891326
    },
    {
      "decile": 7,
      "rows": 14144,
      "event_rate": 0.003110859728506787
    },
    {
      "decile": 8,
      "rows": 7291,
      "event_rate": 0.006171992867919353
    },
    {
      "decile": 9,
      "rows": 327,
      "event_rate": 0.0
    },
    {
      "decile": 10,
      "rows": 13616,
      "event_rate": 0.003672150411280846
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

