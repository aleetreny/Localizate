# Activity Survival Rolling Backtest

Walk-forward backtest temporal para medir estabilidad del ensemble survival sobre `activity_survival` usando multiples cortes contiguos en el tiempo.

## Configuracion

- Filas evaluables: 203828
- Folds ejecutados: 4
- Cutoffs: ["2020-03", "2021-04", "2022-06", "2023-06", "2024-10", "2026-04"]
- Training run: {"feature_profile": "activity_survival_pruned_with_external", "rsf_n_estimators": 120, "rsf_chunk_size": 20, "gbsa_n_estimators": 120, "gbsa_chunk_size": 20, "fit_max_rows": 25000, "cut_quantiles": [0.55, 0.65, 0.75, 0.85, 0.95], "min_valid_events": 20, "min_test_events": 20}

## Lectura ejecutiva

- El rolling backtest ejecuta 4 folds walk-forward; media valid Uno=0.5596, test Uno=0.5389, valid mean AUC=0.5205, test mean AUC=0.5343.
- Frente al split unico actual, valid Uno pasa de 0.6432 a media rolling 0.5596; test Uno pasa de 0.5221 a media rolling 0.5389.
- Frente al split unico, valid mean AUC pasa de 0.6607 a 0.5205; test mean AUC pasa de 0.8833 a 0.5343.
- Quality gates por fold: pass, pass, pass, pass_with_caveats.
- La mejor variante por media de Uno test es RSF solo con test Uno=0.5510 y valid Uno=0.5695.
- Comparativa clave: ensemble actual test Uno=0.5389, ensemble ponderado=0.5283, GBSA solo=0.5388.

## Resumen agregado

{
  "valid_uno": {
    "count": 4,
    "mean": 0.5596254882298107,
    "std": 0.06789760907424963,
    "min": 0.4507042253521127,
    "max": 0.6258485639686684
  },
  "test_uno": {
    "count": 4,
    "mean": 0.5389103812643956,
    "std": 0.06475320822759958,
    "min": 0.46741585072363434,
    "max": 0.6327222594828229
  },
  "valid_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.5205109579878942,
    "std": 0.09370011815832555,
    "min": 0.36559820361767503,
    "max": 0.6069683992087466
  },
  "test_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.5342504325432029,
    "std": 0.05716722360777232,
    "min": 0.4553421380929787,
    "max": 0.6135367952503326
  }
}

## Benchmark de variantes

{
  "cox_only": {
    "label": "Cox solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.5605518588505907,
      "std": 0.10419434440986228,
      "min": 0.41403487001302974,
      "max": 0.67763272410792
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5192861445422841,
      "std": 0.09026549416120437,
      "min": 0.4175805047867711,
      "max": 0.6399508160071541
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5310510342048609,
      "std": 0.10162440354667639,
      "min": 0.4178562008389827,
      "max": 0.6704343468442666
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.4705269013756155,
      "std": 0.1452865937016792,
      "min": 0.2533713500966227,
      "max": 0.6225778123498957
    }
  },
  "gbsa_only": {
    "label": "GBSA solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.5494438897859804,
      "std": 0.026223516974791694,
      "min": 0.5136812061798102,
      "max": 0.5797646127979428
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5387765003058794,
      "std": 0.03281055226597578,
      "min": 0.4832044036716427,
      "max": 0.5682713546302707
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5572591946324926,
      "std": 0.060393839349382326,
      "min": 0.48668031182215604,
      "max": 0.6507092547556623
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5580914717797232,
      "std": 0.05375847337719124,
      "min": 0.49289320197181946,
      "max": 0.6419152167298772
    }
  },
  "rsf_only": {
    "label": "RSF solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.5695471032517345,
      "std": 0.05512141087358313,
      "min": 0.5002171620028542,
      "max": 0.6467798085291558
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5510421865509765,
      "std": 0.07181742379518716,
      "min": 0.4353291952733437,
      "max": 0.6160574412532637
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5608334062501816,
      "std": 0.07881440301677203,
      "min": 0.4629160666528989,
      "max": 0.6751234553869079
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5786619282166834,
      "std": 0.08999753546637934,
      "min": 0.46617507946195996,
      "max": 0.677354753965171
    }
  },
  "cox_gbsa_rank": {
    "label": "Cox + GBSA",
    "valid_uno": {
      "count": 4,
      "mean": 0.5508044971834787,
      "std": 0.076655014271579,
      "min": 0.44220388409753675,
      "max": 0.6318280050674416
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5245910394219531,
      "std": 0.07920052935350293,
      "min": 0.4276860185276761,
      "max": 0.6478500633430211
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.512202492615394,
      "std": 0.10246088700259574,
      "min": 0.35585704969321735,
      "max": 0.609160197878975
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5104322580299394,
      "std": 0.0913295025295197,
      "min": 0.3820871237641347,
      "max": 0.6386743387154195
    }
  },
  "ensemble_all_rank": {
    "label": "Ensemble actual (rank equal)",
    "valid_uno": {
      "count": 4,
      "mean": 0.5596254882298107,
      "std": 0.06789760907424963,
      "min": 0.4507042253521127,
      "max": 0.6258485639686684
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5389103812643956,
      "std": 0.06475320822759958,
      "min": 0.46741585072363434,
      "max": 0.6327222594828229
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5205109579878942,
      "std": 0.09370011815832555,
      "min": 0.36559820361767503,
      "max": 0.6069683992087466
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5342504325432029,
      "std": 0.05716722360777232,
      "min": 0.4553421380929787,
      "max": 0.6135367952503326
    }
  },
  "ensemble_weighted_rank": {
    "label": "Ensemble ponderado (GBSA dominante)",
    "valid_uno": {
      "count": 4,
      "mean": 0.5503617749312957,
      "std": 0.054174705771178985,
      "min": 0.45976298318545633,
      "max": 0.5974737312765481
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5282845451083898,
      "std": 0.056707686045979054,
      "min": 0.4735271816173804,
      "max": 0.6217676428944034
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.510754763227904,
      "std": 0.09196057212136446,
      "min": 0.3538225274855733,
      "max": 0.5798334944205316
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5336801417000923,
      "std": 0.06508977587088288,
      "min": 0.44233611872556644,
      "max": 0.6208692941186196
    }
  }
}

## Ranking de variantes

[
  {
    "variant": "rsf_only",
    "label": "RSF solo",
    "test_uno_mean": 0.5510421865509765,
    "valid_uno_mean": 0.5695471032517345,
    "test_dynamic_auc_mean": 0.5786619282166834,
    "valid_dynamic_auc_mean": 0.5608334062501816
  },
  {
    "variant": "ensemble_all_rank",
    "label": "Ensemble actual (rank equal)",
    "test_uno_mean": 0.5389103812643956,
    "valid_uno_mean": 0.5596254882298107,
    "test_dynamic_auc_mean": 0.5342504325432029,
    "valid_dynamic_auc_mean": 0.5205109579878942
  },
  {
    "variant": "gbsa_only",
    "label": "GBSA solo",
    "test_uno_mean": 0.5387765003058794,
    "valid_uno_mean": 0.5494438897859804,
    "test_dynamic_auc_mean": 0.5580914717797232,
    "valid_dynamic_auc_mean": 0.5572591946324926
  },
  {
    "variant": "ensemble_weighted_rank",
    "label": "Ensemble ponderado (GBSA dominante)",
    "test_uno_mean": 0.5282845451083898,
    "valid_uno_mean": 0.5503617749312957,
    "test_dynamic_auc_mean": 0.5336801417000923,
    "valid_dynamic_auc_mean": 0.510754763227904
  },
  {
    "variant": "cox_gbsa_rank",
    "label": "Cox + GBSA",
    "test_uno_mean": 0.5245910394219531,
    "valid_uno_mean": 0.5508044971834787,
    "test_dynamic_auc_mean": 0.5104322580299394,
    "valid_dynamic_auc_mean": 0.512202492615394
  },
  {
    "variant": "cox_only",
    "label": "Cox solo",
    "test_uno_mean": 0.5192861445422841,
    "valid_uno_mean": 0.5605518588505907,
    "test_dynamic_auc_mean": 0.4705269013756155,
    "valid_dynamic_auc_mean": 0.5310510342048609
  }
]

## Comparacion con split unico

{
  "valid_uno": 0.6432172567752792,
  "test_uno": 0.5221075986882793,
  "valid_dynamic_auc_mean": 0.6607140573150809,
  "test_dynamic_auc_mean": 0.8832969698806722,
  "quality_gate": "pass"
}

## Folds

[
  {
    "fold_id": "fold_1",
    "valid_start": "2020-03",
    "test_start": "2021-04",
    "test_end": "2022-06",
    "train_rows": 148334,
    "train_events": 18521,
    "valid_rows": 510,
    "valid_events": 34,
    "test_rows": 2112,
    "test_events": 61,
    "training_rows_used": 25000,
    "metrics": {
      "split_event_counts": {
        "train": 18521,
        "valid": 34,
        "test": 61
      },
      "uno_c_index": {
        "train": {
          "rows": 148334,
          "events": 18521,
          "tau": 134.99999999999997,
          "uno_c_index": 0.7429192358735524
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "uno_c_index": 0.4507042253521127
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.46741585072363434
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148334,
          "events": 18521,
          "tau": 134.99999999999997,
          "mean_auc": 0.801292077528825,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1060,
              "controls": 147274,
              "auc": 0.8091108448608563,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 1999,
              "controls": 146335,
              "auc": 0.7981176582756133,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4064,
              "controls": 144270,
              "auc": 0.7987220466846666,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "mean_auc": 0.36559820361767503,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 505,
              "auc": 0.31346534653465347,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 7,
              "controls": 503,
              "auc": 0.4133768815677364,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 14,
              "controls": 496,
              "auc": 0.3891849078341013,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.5507863514477322,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.68343616516374,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.596872193163206,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.4660271079035381,
              "supported": true
            }
          }
        }
      },
      "integrated_brier_score": {
        "cox": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.019637586876589435
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.3906380282590627
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.5059353865436181
          }
        },
        "rsf": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.020427709416161458
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023771412952682355
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01313955890568662
          }
        },
        "gbsa": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.022768120689348456
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.024107560093877232
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.014238947246176751
          }
        }
      },
      "quality_gate": {
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
    },
    "variant_metrics": {
      "cox_only": {
        "label": "Cox solo",
        "uno_c_index": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7518572745512977
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.41403487001302974
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.4485378960208354
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7978845399800814,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8020012562900982,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7952878410709097,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7969521336784322,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.4178562008389827,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.44574257425742575,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.4610905992615735,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.38558467741935487,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.4254987563200584,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.43540579022306597,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.4416442119723146,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.41408705710765215,
                "supported": true
              }
            }
          }
        }
      },
      "gbsa_only": {
        "label": "GBSA solo",
        "uno_c_index": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "uno_c_index": 0.6929939633564921
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5136812061798102
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5682713546302707
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.750555143051078,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7641896435625959,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7482806220139488,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7445905932746397,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.48668031182215604,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4253465346534654,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5046861687020732,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5253456221198156,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6419152167298772,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6965353583293782,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6551487293284726,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6093117408906882,
                "supported": true
              }
            }
          }
        }
      },
      "rsf_only": {
        "label": "RSF solo",
        "uno_c_index": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7295700830240054
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5002171620028542
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6057964922691458
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8032523783863493,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8122156596317325,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.800331542407005,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7999795390955498,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.4629160666528989,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.41485148514851483,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.4734450440215848,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4942396313364056,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.677354753965171,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7285714285714285,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7027526813546785,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6415872457062388,
                "supported": true
              }
            }
          }
        }
      },
      "cox_gbsa_rank": {
        "label": "Cox + GBSA",
        "uno_c_index": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7387908490747019
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.44220388409753675
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.4276860185276761
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7894887862297421,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7974761425308903,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7864543198581899,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7867685761782507,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.35585704969321735,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.3126732673267327,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.40059642147117297,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.37391993087557607,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.4955539142431453,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6355007119126721,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.5341575527024884,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.4101390600246435,
                "supported": true
              }
            }
          }
        }
      },
      "ensemble_all_rank": {
        "label": "Ensemble actual (rank equal)",
        "uno_c_index": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7429192358735524
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4507042253521127
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.46741585072363434
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.801292077528825,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8091108448608563,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7981176582756133,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7987220466846666,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.36559820361767503,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.31346534653465347,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.4133768815677364,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.3891849078341013,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.5507863514477322,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.68343616516374,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.596872193163206,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.4660271079035381,
                "supported": true
              }
            }
          }
        }
      },
      "ensemble_weighted_rank": {
        "label": "Ensemble ponderado (GBSA dominante)",
        "uno_c_index": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7286562480126204
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.45976298318545633
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.4735271816173804
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7837380694215207,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7932862497857286,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7808127438168122,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7801670328872645,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3538225274855733,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.2805940594059406,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.39548423743254757,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.39422523041474655,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.5580331845386792,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.684765068818225,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6003064405346858,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.477757940000503,
                "supported": true
              }
            }
          }
        }
      }
    }
  },
  {
    "fold_id": "fold_2",
    "valid_start": "2021-04",
    "test_start": "2022-06",
    "test_end": "2023-06",
    "train_rows": 148844,
    "train_events": 18555,
    "valid_rows": 2112,
    "valid_events": 61,
    "test_rows": 599,
    "test_events": 20,
    "training_rows_used": 25000,
    "metrics": {
      "split_event_counts": {
        "train": 18555,
        "valid": 61,
        "test": 20
      },
      "uno_c_index": {
        "train": {
          "rows": 148844,
          "events": 18555,
          "tau": 134.99999999999997,
          "uno_c_index": 0.7402230891277259
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.5556819305706656
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.563881636205396
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148844,
          "events": 18555,
          "tau": 134.99999999999997,
          "mean_auc": 0.7986776921500406,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1065,
              "controls": 147779,
              "auc": 0.8073159810041177,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2006,
              "controls": 146838,
              "auc": 0.7958319280027499,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4078,
              "controls": 144766,
              "auc": 0.7955300504671297,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.529214772636618,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.5597532036070242,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.5697680562159877,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.4977242437196671,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.4553421380929787,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.2964824120603015,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.43732433951658234,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.5110265161459701,
              "supported": true
            }
          }
        }
      },
      "integrated_brier_score": {
        "cox": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.019701126960901247
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.23358747001282923
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.2505360963126222
          }
        },
        "rsf": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.020546337728438602
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.013217829516741515
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.019546435010759585
          }
        },
        "gbsa": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.022742681982260624
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.014371708224815809
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01992807160515084
          }
        }
      },
      "quality_gate": {
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
    },
    "variant_metrics": {
      "cox_only": {
        "label": "Cox solo",
        "uno_c_index": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7512822594045283
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5127501401114298
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.4175805047867711
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7965974431230751,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8003257242995798,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7948477314891974,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7954757535451319,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.451902342717833,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.49492168960607497,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.49574681671685944,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.4128548796741016,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.2533713500966227,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.04020100502512558,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.2265317594154019,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.329614071934891,
                "supported": true
              }
            }
          }
        }
      },
      "gbsa_only": {
        "label": "GBSA solo",
        "uno_c_index": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "uno_c_index": 0.6912854857191725
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5797646127979428
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5498259355961705
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.749227117572945,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7634659031359701,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.746770180611681,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7430242561134511,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6507092547556623,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6804935927859516,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6551751466159454,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.634030728996404,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5413893812655202,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.32202680067001677,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.5602866779089376,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5932659490679969,
                "supported": true
              }
            }
          }
        }
      },
      "rsf_only": {
        "label": "RSF solo",
        "uno_c_index": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "uno_c_index": 0.72479348801173
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5915834239936703
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6160574412532637
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7988680526807436,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8102421179805768,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7961620270693388,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7942507701305552,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6751234553869079,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.691219743711438,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7164632535531251,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6505393919581562,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.65594900658918,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7051926298157454,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6700393479482856,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6338277763192439,
                "supported": true
              }
            }
          }
        }
      },
      "cox_gbsa_rank": {
        "label": "Cox + GBSA",
        "uno_c_index": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7371495873023797
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5157831404740711
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5203655352480417
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.787640419445891,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7955232701082924,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7849765699700093,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7847984534233754,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.48539508872973147,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.5317513051732321,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.5055740476567865,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.454145396937159,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.3820871237641347,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.17169179229480735,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.36340640809443514,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.4528747702809136,
                "supported": true
              }
            }
          }
        }
      },
      "ensemble_all_rank": {
        "label": "Ensemble actual (rank equal)",
        "uno_c_index": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7402230891277259
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5556819305706656
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.563881636205396
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7986776921500406,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8073159810041177,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7958319280027499,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7955300504671297,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.529214772636618,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.5597532036070242,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.5697680562159877,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.4977242437196671,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.4553421380929787,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.2964824120603015,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.43732433951658234,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5110265161459701,
                "supported": true
              }
            }
          }
        }
      },
      "ensemble_weighted_rank": {
        "label": "Ensemble ponderado (GBSA dominante)",
        "uno_c_index": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7265926554140184
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5585706985791052
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5226283724978242
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7818164528799857,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7917728055219622,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7790990069332178,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7779330557140607,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.5378252043634142,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.5656383483626009,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.5677603423680456,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5119445771619685,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.44233611872556644,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.22194304857621439,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4401349072512648,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5065634024678394,
                "supported": true
              }
            }
          }
        }
      }
    }
  },
  {
    "fold_id": "fold_3",
    "valid_start": "2022-06",
    "test_start": "2023-06",
    "test_end": "2024-10",
    "train_rows": 150956,
    "train_events": 18616,
    "valid_rows": 599,
    "valid_events": 20,
    "test_rows": 680,
    "test_events": 23,
    "training_rows_used": 25000,
    "metrics": {
      "split_event_counts": {
        "train": 18616,
        "valid": 20,
        "test": 23
      },
      "uno_c_index": {
        "train": {
          "rows": 150956,
          "events": 18616,
          "tau": 134.99999999999997,
          "uno_c_index": 0.7425224160560427
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.6258485639686684
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.6327222594828229
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 150956,
          "events": 18616,
          "tau": 134.99999999999997,
          "mean_auc": 0.801307229186991,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1070,
              "controls": 149886,
              "auc": 0.8083585082294943,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2015,
              "controls": 148941,
              "auc": 0.7982754291618096,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4097,
              "controls": 146859,
              "auc": 0.7990594782015529,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.6069683992087466,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.6298157453936348,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.6053962900505903,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.6013389341034392,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.6135367952503326,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.5619436201780416,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.6204466067864272,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.6451823690150885,
              "supported": true
            }
          }
        }
      },
      "integrated_brier_score": {
        "cox": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01960735715079089
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.016673950271888952
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02153446244876003
          }
        },
        "rsf": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.020473369911340092
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.020365331607056947
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023399193628428558
          }
        },
        "gbsa": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.022579875391035526
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.020165218607001593
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02329233029247762
          }
        }
      },
      "quality_gate": {
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
    },
    "variant_metrics": {
      "cox_only": {
        "label": "Cox solo",
        "uno_c_index": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7497422662533917
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.67763272410792
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6399508160071541
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7949768303441851,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7977245385620797,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7927597123533336,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7945710324134492,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6704343468442666,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8433835845896147,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6419336706014616,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6373063796271987,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6225778123498957,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5018545994065282,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5746631736526946,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.742010217417132,
                "supported": true
              }
            }
          }
        }
      },
      "gbsa_only": {
        "label": "GBSA solo",
        "uno_c_index": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "uno_c_index": 0.6931433985581706
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5357702349869452
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5538043073254341
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7510467369216137,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7632674726873421,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7488866467567061,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7457465918382844,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5283046802981239,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.31909547738693467,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.544266441821248,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5789577316881072,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5561680871516759,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6212908011869435,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.590568862275449,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.485683735297612,
                "supported": true
              }
            }
          }
        }
      },
      "rsf_only": {
        "label": "RSF solo",
        "uno_c_index": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7279026728488042
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6467798085291558
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5469856174081527
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8023603426211819,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8120276924481297,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7995274845537701,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.798677819354549,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5847623668085421,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5117252931323284,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.5882518268690275,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.603636124967183,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5151688728504228,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5087784371909001,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5575723552894212,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.4896637756920518,
                "supported": true
              }
            }
          }
        }
      },
      "cox_gbsa_rank": {
        "label": "Cox + GBSA",
        "uno_c_index": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7388996027422444
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6134029590948651
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6478500633430211
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7896625244190651,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.796104743655022,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7867931150581502,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7876540793007132,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.609160197878975,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6675041876046901,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6003372681281619,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5975321606720925,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6386743387154195,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5876607319485658,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6209456087824351,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6873589164785553,
                "supported": true
              }
            }
          }
        }
      },
      "ensemble_all_rank": {
        "label": "Ensemble actual (rank equal)",
        "uno_c_index": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7425224160560427
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6258485639686684
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6327222594828229
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.801307229186991,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8083585082294943,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7982754291618096,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7990594782015529,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6069683992087466,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6298157453936348,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6053962900505903,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6013389341034392,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6135367952503326,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5619436201780416,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6204466067864272,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6451823690150885,
                "supported": true
              }
            }
          }
        }
      },
      "ensemble_weighted_rank": {
        "label": "Ensemble ponderado (GBSA dominante)",
        "uno_c_index": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7287036251756814
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5856396866840731
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6217676428944034
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7841298122047946,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7924000277594149,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7812926706718164,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7811672608624416,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5715378266420972,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5293132328308208,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.5657672849915683,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5868994486741927,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6208692941186196,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.611646884272997,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6331711576846307,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6186883687774741,
                "supported": true
              }
            }
          }
        }
      }
    }
  },
  {
    "fold_id": "fold_4",
    "valid_start": "2023-06",
    "test_start": "2024-10",
    "test_end": "2026-04",
    "train_rows": 151555,
    "train_events": 18636,
    "valid_rows": 680,
    "valid_events": 23,
    "test_rows": 51593,
    "test_events": 228,
    "training_rows_used": 25000,
    "metrics": {
      "split_event_counts": {
        "train": 18636,
        "valid": 23,
        "test": 228
      },
      "uno_c_index": {
        "train": {
          "rows": 151555,
          "events": 18636,
          "tau": 134.99999999999997,
          "uno_c_index": 0.738107367292628
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.6062672330277964
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "uno_c_index": 0.491621778645729
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 151555,
          "events": 18636,
          "tau": 134.99999999999997,
          "mean_auc": 0.7975406026655419,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1072,
              "controls": 150483,
              "auc": 0.8057384791865714,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2021,
              "controls": 149534,
              "auc": 0.7950385872039865,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4110,
              "controls": 147445,
              "auc": 0.7944703724321636,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.5802624564885371,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.5841988130563799,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.6191991017964071,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.5498990139004396,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "mean_auc": 0.5173364453817679,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 41,
              "controls": 50816,
              "auc": 0.5438206998371935,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 152,
              "controls": 50015,
              "auc": 0.5077101211741741,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 228,
              "controls": 0,
              "auc": NaN,
              "supported": false
            }
          }
        }
      },
      "integrated_brier_score": {
        "cox": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.019670069079254764
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.03900547899172288
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.13216322325137173
          }
        },
        "rsf": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02050789483090111
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023339657707073393
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.07432269524323712
          }
        },
        "gbsa": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.022607563749526723
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02331291709913064
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.005703971830299473
          }
        }
      },
      "quality_gate": {
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
          "limited_dynamic_auc_horizon_support_test"
        ]
      }
    },
    "variant_metrics": {
      "cox_only": {
        "label": "Cox solo",
        "uno_c_index": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7499309992122034
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6377897011699829
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5710753613543755
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7954549186500313,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.799071293916177,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.794074295081867,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7942263200291022,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.584011246418361,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5142185954500494,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6063498003992016,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6176191041938933,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.580659686735885,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5556224849480863,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5897600456705093,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 228,
                "controls": 0,
                "auc": NaN,
                "supported": false
              }
            }
          }
        }
      },
      "gbsa_only": {
        "label": "GBSA solo",
        "uno_c_index": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "uno_c_index": 0.6925330914568366
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5685595051792235
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4832044036716427
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7511412613166715,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7638823820630902,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7490868282620537,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7455362711437042,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5633425316540281,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6075667655786351,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.593375748502994,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5107520494237852,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.49289320197181946,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5232474311912515,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.48186024455821147,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 228,
                "controls": 0,
                "auc": NaN,
                "supported": false
              }
            }
          }
        }
      },
      "rsf_only": {
        "label": "RSF solo",
        "uno_c_index": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7258592822475741
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.539608018481258
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4353291952733437
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8020335284278508,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8134714118548225,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7993056370069411,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7974032545765962,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.520531736152378,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5399357072205737,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5557010978043913,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.4818819056671023,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.46617507946195996,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.49869447686920193,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.45435514082617323,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 228,
                "controls": 0,
                "auc": NaN,
                "supported": false
              }
            }
          }
        }
      },
      "cox_gbsa_rank": {
        "label": "Cox + GBSA",
        "uno_c_index": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7335256121862699
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6318280050674416
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5024625405690732
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.785861891489131,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.793459919135012,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7836649949560934,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7829608714668566,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5983976341596522,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.595326409495549,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6384106786427146,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.572234762979684,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5254136553970584,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5499115412084536,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5165093235187339,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 228,
                "controls": 0,
                "auc": NaN,
                "supported": false
              }
            }
          }
        }
      },
      "ensemble_all_rank": {
        "label": "Ensemble actual (rank equal)",
        "uno_c_index": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "uno_c_index": 0.738107367292628
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6062672330277964
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.491621778645729
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7975406026655419,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8057384791865714,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7950385872039865,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7944703724321636,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5802624564885371,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5841988130563799,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6191991017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5498990139004396,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5173364453817679,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5438206998371935,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5077101211741741,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 228,
                "controls": 0,
                "auc": NaN,
                "supported": false
              }
            }
          }
        }
      },
      "ensemble_weighted_rank": {
        "label": "Ensemble ponderado (GBSA dominante)",
        "uno_c_index": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "uno_c_index": 0.7244671147189995
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5974737312765481
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.49521498342395137
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7806499185004362,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7898301021705134,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7782969889759515,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7770078760037455,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5798334944205316,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5992828882294757,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6170783433133733,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5396815967684448,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5134819694175036,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5411542168397125,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.503423841268672,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 228,
                "controls": 0,
                "auc": NaN,
                "supported": false
              }
            }
          }
        }
      }
    }
  }
]

