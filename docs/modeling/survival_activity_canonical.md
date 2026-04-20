# Survival Canonical Models

Entrenamiento de modelos de supervivencia canónicos (Cox, RSF, GBSA) con reglas PiT y quality gate.

## Resumen

- Filas modeladas: 203828
- Split rows: {"train": 149280, "test": 51902, "valid": 2646}
- Split events: {"test": 238, "train": 18588, "valid": 61}
- Training run: {"rsf_n_estimators": 300, "rsf_chunk_size": 25, "gbsa_n_estimators": 300, "gbsa_chunk_size": 25, "fit_max_rows": null, "quick_mode": false}

## Lectura ejecutiva

- Quality gate canónico: pass.
- Validación: Uno=0.7756 (muy_bueno), mean Dynamic AUC=0.7928 (muy_bueno).
- Test: Uno=0.6050 (bueno), mean Dynamic AUC=0.9236 (muy_bueno).
- Régimen de evento raro confirmado: valid=61 eventos, test=238 eventos.

## C-index por modelo

{
  "cox": {
    "train": 0.7604215014161247,
    "valid": 0.7560560207363578,
    "test": 0.6068952249894344
  },
  "rsf": {
    "train": 0.8566627550409879,
    "valid": 0.8026110440104768,
    "test": 0.3850426364670499
  },
  "gbsa": {
    "train": 0.7500853537708131,
    "valid": 0.7278319106490968,
    "test": 0.6552974039580527
  },
  "ensemble": {
    "train": 0.7996424753376822,
    "valid": 0.775564210783449,
    "test": 0.6050411972118083
  }
}

## Interpretación de discriminación

- En train, el ensemble marca Uno/IPCW C-index=0.7991 y se clasifica como muy_bueno.
- En valid, el ensemble marca Uno/IPCW C-index=0.7756 y se clasifica como muy_bueno.
- En test, el ensemble marca Uno/IPCW C-index=0.6050 y se clasifica como bueno.

## Uno / IPCW C-index (ensemble)

{
  "train": {
    "rows": 149280,
    "events": 18588,
    "tau": 134.99999999999997,
    "uno_c_index": 0.7990687730804019
  },
  "valid": {
    "rows": 2646,
    "events": 61,
    "tau": 53.99999999999999,
    "uno_c_index": 0.775564210783449
  },
  "test": {
    "rows": 51902,
    "events": 238,
    "tau": 26.999999999999996,
    "uno_c_index": 0.6050411972118083
  }
}

## Cumulative Dynamic AUC (ensemble)

{
  "train": {
    "rows": 149280,
    "events": 18588,
    "tau": 134.99999999999997,
    "mean_auc": 0.8454626909010465,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 1066,
        "controls": 148214,
        "auc": 0.8492175858693849,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 2008,
        "controls": 147272,
        "auc": 0.8429049940441395,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 4084,
        "controls": 145196,
        "auc": 0.8446951727907178,
        "supported": true
      }
    }
  },
  "valid": {
    "rows": 2646,
    "events": 61,
    "tau": 53.99999999999999,
    "mean_auc": 0.7927701697505469,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 8,
        "controls": 2638,
        "auc": 0.8812547384382108,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 18,
        "controls": 2628,
        "auc": 0.7955986808726534,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 35,
        "controls": 2611,
        "auc": 0.7494665426492313,
        "supported": true
      }
    }
  },
  "test": {
    "rows": 51902,
    "events": 238,
    "tau": 26.999999999999996,
    "mean_auc": 0.9235562832201322,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 45,
        "controls": 51121,
        "auc": 0.6277539780346846,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 159,
        "controls": 50317,
        "auc": 0.6253676846028882,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 238,
        "controls": 81,
        "auc": 0.9683058408548605,
        "supported": true
      }
    }
  }
}

## Interpretación por horizontes

- En valid, la media de Dynamic AUC es 0.7928 (muy_bueno).
- valid:h6 -> AUC=0.8813, cases=8, controls=2638, estado=muy_bueno.
- valid:h12 -> AUC=0.7956, cases=18, controls=2628, estado=muy_bueno.
- valid:h24 -> AUC=0.7495, cases=35, controls=2611, estado=muy_bueno.
- En test, la media de Dynamic AUC es 0.9236 (muy_bueno).
- test:h6 -> AUC=0.6278, cases=45, controls=51121, estado=bueno.
- test:h12 -> AUC=0.6254, cases=159, controls=50317, estado=bueno.
- test:h24 -> AUC=0.9683, cases=238, controls=81, estado=muy_bueno.

## Integrated Brier Score (modelos base)

{
  "cox": {
    "train": {
      "rows": 149280,
      "events": 18588,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.01547217527702183
    },
    "valid": {
      "rows": 2646,
      "events": 61,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.008125144887706475
    },
    "test": {
      "rows": 51902,
      "events": 238,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.031205789110197016
    }
  },
  "rsf": {
    "train": {
      "rows": 149280,
      "events": 18588,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.014221721606034706
    },
    "valid": {
      "rows": 2646,
      "events": 61,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.007940357964162712
    },
    "test": {
      "rows": 51902,
      "events": 238,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.009781593330257536
    }
  },
  "gbsa": {
    "train": {
      "rows": 149280,
      "events": 18588,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.015748587895414893
    },
    "valid": {
      "rows": 2646,
      "events": 61,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.008153848062813818
    },
    "test": {
      "rows": 51902,
      "events": 238,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.0031739139670986533
    }
  }
}

## Interpretación de IBS

- En valid, el mejor IBS base es rsf=0.0079 (muy_bueno; menor es mejor).
- En test, el mejor IBS base es gbsa=0.0032 (muy_bueno; menor es mejor).

Nota: el ensemble actual es rank-based; no se reporta IBS para el ensemble hasta definir una agregación explicita de curvas de supervivencia.

## Calibration (12 meses)

{
  "train": [
    {
      "decile": 1,
      "rows": 20244,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 19755,
      "event_rate": 0.00045558086560364467
    },
    {
      "decile": 3,
      "rows": 18520,
      "event_rate": 0.0014578833693304535
    },
    {
      "decile": 4,
      "rows": 19186,
      "event_rate": 0.004378192431981653
    },
    {
      "decile": 5,
      "rows": 17990,
      "event_rate": 0.007726514730405781
    },
    {
      "decile": 6,
      "rows": 15628,
      "event_rate": 0.014397235730739697
    },
    {
      "decile": 7,
      "rows": 13682,
      "event_rate": 0.023753837158310188
    },
    {
      "decile": 8,
      "rows": 8381,
      "event_rate": 0.03054528099272163
    },
    {
      "decile": 9,
      "rows": 10702,
      "event_rate": 0.03205008409643057
    },
    {
      "decile": 10,
      "rows": 5192,
      "event_rate": 0.11556240369799692
    }
  ],
  "valid": [
    {
      "decile": 1,
      "rows": 123,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 504,
      "event_rate": 0.0
    },
    {
      "decile": 3,
      "rows": 738,
      "event_rate": 0.0013550135501355014
    },
    {
      "decile": 4,
      "rows": 353,
      "event_rate": 0.0056657223796034
    },
    {
      "decile": 5,
      "rows": 326,
      "event_rate": 0.015337423312883436
    },
    {
      "decile": 6,
      "rows": 257,
      "event_rate": 0.007782101167315175
    },
    {
      "decile": 7,
      "rows": 206,
      "event_rate": 0.014563106796116505
    },
    {
      "decile": 8,
      "rows": 51,
      "event_rate": 0.0
    },
    {
      "decile": 9,
      "rows": 66,
      "event_rate": 0.045454545454545456
    },
    {
      "decile": 10,
      "rows": 22,
      "event_rate": 0.09090909090909091
    }
  ],
  "test": [
    {
      "decile": 1,
      "rows": 15,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 125,
      "event_rate": 0.0
    },
    {
      "decile": 3,
      "rows": 1124,
      "event_rate": 0.0008896797153024911
    },
    {
      "decile": 4,
      "rows": 844,
      "event_rate": 0.0
    },
    {
      "decile": 5,
      "rows": 2067,
      "event_rate": 0.001451378809869376
    },
    {
      "decile": 6,
      "rows": 4497,
      "event_rate": 0.00266844563042028
    },
    {
      "decile": 7,
      "rows": 6495,
      "event_rate": 0.002155504234026174
    },
    {
      "decile": 8,
      "rows": 11951,
      "event_rate": 0.0011714500878587566
    },
    {
      "decile": 9,
      "rows": 9613,
      "event_rate": 0.004889212524706127
    },
    {
      "decile": 10,
      "rows": 15171,
      "event_rate": 0.004482235844703711
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

