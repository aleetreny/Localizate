# Survival Canonical Models

Entrenamiento de modelos de supervivencia canónicos (Cox, RSF, GBSA) con reglas PiT y quality gate.

## Resumen

- Filas modeladas: 203828
- Split rows: {"train": 149280, "test": 51902, "valid": 2646}
- Split events: {"test": 238, "train": 18588, "valid": 61}
- Training run: {"rsf_n_estimators": 300, "rsf_chunk_size": 25, "gbsa_n_estimators": 300, "gbsa_chunk_size": 25, "fit_max_rows": null, "quick_mode": false}

## Lectura ejecutiva

- Quality gate canonico: pass.
- Validacion: Uno=0.6432 (bueno), mean Dynamic AUC=0.6607 (bueno).
- Test: Uno=0.5221 (debil), mean Dynamic AUC=0.8833 (muy_bueno).
- Regimen de evento raro confirmado: valid=61 eventos, test=238 eventos.

## C-index por modelo

{
  "cox": {
    "train": 0.754725138385934,
    "valid": 0.6684116601300094,
    "test": 0.5739503870076733
  },
  "rsf": {
    "train": 0.8013784567285138,
    "valid": 0.6567847788619431,
    "test": 0.426750011357017
  },
  "gbsa": {
    "train": 0.6849545180884006,
    "valid": 0.5691845237287445,
    "test": 0.5156623970720476
  },
  "ensemble": {
    "train": 0.7611140456378027,
    "valid": 0.6432172567752792,
    "test": 0.5221075986882793
  }
}

## Interpretacion de discriminacion

- En train, el ensemble marca Uno/IPCW C-index=0.7605 y se clasifica como muy_bueno.
- En valid, el ensemble marca Uno/IPCW C-index=0.6432 y se clasifica como bueno.
- En test, el ensemble marca Uno/IPCW C-index=0.5221 y se clasifica como debil.

## Uno / IPCW C-index (ensemble)

{
  "train": {
    "rows": 149280,
    "events": 18588,
    "tau": 134.99999999999997,
    "uno_c_index": 0.7605353620989778
  },
  "valid": {
    "rows": 2646,
    "events": 61,
    "tau": 53.99999999999999,
    "uno_c_index": 0.6432172567752792
  },
  "test": {
    "rows": 51902,
    "events": 238,
    "tau": 26.999999999999996,
    "uno_c_index": 0.5221075986882793
  }
}

## Cumulative Dynamic AUC (ensemble)

{
  "train": {
    "rows": 149280,
    "events": 18588,
    "tau": 134.99999999999997,
    "mean_auc": 0.8066556614731816,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 1066,
        "controls": 148214,
        "auc": 0.8119792356425148,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 2008,
        "controls": 147272,
        "auc": 0.8044033921216649,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 4084,
        "controls": 145196,
        "auc": 0.8049440563019964,
        "supported": true
      }
    }
  },
  "valid": {
    "rows": 2646,
    "events": 61,
    "tau": 53.99999999999999,
    "mean_auc": 0.6607140573150809,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 8,
        "controls": 2638,
        "auc": 0.7137272554965883,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 18,
        "controls": 2628,
        "auc": 0.6865909859631321,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 35,
        "controls": 2611,
        "auc": 0.6205449472014006,
        "supported": true
      }
    }
  },
  "test": {
    "rows": 51902,
    "events": 238,
    "tau": 26.999999999999996,
    "mean_auc": 0.8832969698806722,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 45,
        "controls": 51121,
        "auc": 0.563998052550702,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 159,
        "controls": 50317,
        "auc": 0.5410253083500918,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 238,
        "controls": 81,
        "auc": 0.9338105612615416,
        "supported": true
      }
    }
  }
}

## Interpretacion por horizontes

- En valid, la media de Dynamic AUC es 0.6607 (bueno).
- valid:h6 -> AUC=0.7137, cases=8, controls=2638, estado=muy_bueno.
- valid:h12 -> AUC=0.6866, cases=18, controls=2628, estado=bueno.
- valid:h24 -> AUC=0.6205, cases=35, controls=2611, estado=bueno.
- En test, la media de Dynamic AUC es 0.8833 (muy_bueno).
- test:h6 -> AUC=0.5640, cases=45, controls=51121, estado=usable.
- test:h12 -> AUC=0.5410, cases=159, controls=50317, estado=debil.
- test:h24 -> AUC=0.9338, cases=238, controls=81, estado=muy_bueno.

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
      "ibs": 0.015529333386494695
    },
    "valid": {
      "rows": 2646,
      "events": 61,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.008263253409489952
    },
    "test": {
      "rows": 51902,
      "events": 238,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.039272227560065064
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
      "ibs": 0.014872116515566093
    },
    "valid": {
      "rows": 2646,
      "events": 61,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.008029241274953178
    },
    "test": {
      "rows": 51902,
      "events": 238,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.04128745183805722
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
      "ibs": 0.015656071844017058
    },
    "valid": {
      "rows": 2646,
      "events": 61,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.008134597458300488
    },
    "test": {
      "rows": 51902,
      "events": 238,
      "times": [
        6.0,
        12.0,
        24.0
      ],
      "ibs": 0.0032902030108107414
    }
  }
}

## Interpretacion de IBS

- En valid, el mejor IBS base es rsf=0.0080 (muy_bueno; menor es mejor).
- En test, el mejor IBS base es gbsa=0.0033 (muy_bueno; menor es mejor).

Nota: el ensemble actual es rank-based; no se reporta IBS para el ensemble hasta definir una agregacion explicita de curvas de supervivencia.

## Calibration (12 meses)

{
  "train": [
    {
      "decile": 1,
      "rows": 19021,
      "event_rate": 0.0004205877714105462
    },
    {
      "decile": 2,
      "rows": 18898,
      "event_rate": 0.0009524817440999048
    },
    {
      "decile": 3,
      "rows": 18647,
      "event_rate": 0.0027886523301335333
    },
    {
      "decile": 4,
      "rows": 19395,
      "event_rate": 0.006702758442897654
    },
    {
      "decile": 5,
      "rows": 19260,
      "event_rate": 0.010851505711318795
    },
    {
      "decile": 6,
      "rows": 16492,
      "event_rate": 0.014067426631093864
    },
    {
      "decile": 7,
      "rows": 17087,
      "event_rate": 0.02153684087317844
    },
    {
      "decile": 8,
      "rows": 4918,
      "event_rate": 0.030703538023586822
    },
    {
      "decile": 9,
      "rows": 6653,
      "event_rate": 0.02600330677889674
    },
    {
      "decile": 10,
      "rows": 8909,
      "event_rate": 0.0748681108990908
    }
  ],
  "valid": [
    {
      "decile": 1,
      "rows": 186,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 349,
      "event_rate": 0.0028653295128939827
    },
    {
      "decile": 3,
      "rows": 512,
      "event_rate": 0.00390625
    },
    {
      "decile": 4,
      "rows": 400,
      "event_rate": 0.0075
    },
    {
      "decile": 5,
      "rows": 682,
      "event_rate": 0.005865102639296188
    },
    {
      "decile": 6,
      "rows": 355,
      "event_rate": 0.011267605633802818
    },
    {
      "decile": 7,
      "rows": 117,
      "event_rate": 0.008547008547008548
    },
    {
      "decile": 8,
      "rows": 15,
      "event_rate": 0.0
    },
    {
      "decile": 9,
      "rows": 12,
      "event_rate": 0.0
    },
    {
      "decile": 10,
      "rows": 18,
      "event_rate": 0.16666666666666666
    }
  ],
  "test": [
    {
      "decile": 1,
      "rows": 1175,
      "event_rate": 0.0
    },
    {
      "decile": 2,
      "rows": 1136,
      "event_rate": 0.0017605633802816902
    },
    {
      "decile": 3,
      "rows": 1224,
      "event_rate": 0.0032679738562091504
    },
    {
      "decile": 4,
      "rows": 588,
      "event_rate": 0.003401360544217687
    },
    {
      "decile": 5,
      "rows": 441,
      "event_rate": 0.009070294784580499
    },
    {
      "decile": 6,
      "rows": 3535,
      "event_rate": 0.004526166902404526
    },
    {
      "decile": 7,
      "rows": 3227,
      "event_rate": 0.004338394793926247
    },
    {
      "decile": 8,
      "rows": 15402,
      "event_rate": 0.0016880924555252564
    },
    {
      "decile": 9,
      "rows": 13718,
      "event_rate": 0.0029158769499927103
    },
    {
      "decile": 10,
      "rows": 11456,
      "event_rate": 0.0044518156424581
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

