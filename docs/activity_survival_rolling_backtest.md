# Activity Survival Rolling Backtest

Walk-forward backtest temporal para medir estabilidad del ensemble survival sobre `activity_survival` usando multiples cortes contiguos en el tiempo.

## Configuracion

- Filas evaluables: 203828
- Folds ejecutados: 4
- Cutoffs: ["2020-03", "2021-04", "2022-06", "2023-06", "2024-10", "2026-04"]
- Training run: {"rsf_n_estimators": 120, "rsf_chunk_size": 20, "gbsa_n_estimators": 120, "gbsa_chunk_size": 20, "fit_max_rows": 25000, "cut_quantiles": [0.55, 0.65, 0.75, 0.85, 0.95], "min_valid_events": 20, "min_test_events": 20}

## Lectura ejecutiva

- El rolling backtest ejecuta 4 folds walk-forward; media valid Uno=0.6898, test Uno=0.6885, valid mean AUC=0.7080, test mean AUC=0.7230.
- Frente al split unico actual, valid Uno pasa de 0.7756 a media rolling 0.6898; test Uno pasa de 0.6050 a media rolling 0.6885.
- Frente al split unico, valid mean AUC pasa de 0.7928 a 0.7080; test mean AUC pasa de 0.9236 a 0.7230.
- Quality gates por fold: pass, pass, pass, pass_with_caveats.
- La mejor variante por media de Uno test es Ensemble actual (rank equal) con test Uno=0.6885 y valid Uno=0.6898.
- Comparativa clave: ensemble actual test Uno=0.6885, ensemble ponderado=0.6766, GBSA solo=0.6397.

## Resumen agregado

{
  "valid_uno": {
    "count": 4,
    "mean": 0.689782630523571,
    "std": 0.06268290738972619,
    "min": 0.5973506235651797,
    "max": 0.7554767085352586
  },
  "test_uno": {
    "count": 4,
    "mean": 0.688482341402764,
    "std": 0.06652410044091525,
    "min": 0.5876838129615467,
    "max": 0.7554313783667952
  },
  "valid_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.7079868968869623,
    "std": 0.08525281057298136,
    "min": 0.5734470358964588,
    "max": 0.7963530149304056
  },
  "test_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.7229896052396121,
    "std": 0.06788956537567173,
    "min": 0.6139738945833619,
    "max": 0.7932169821231906
  }
}

## Benchmark de variantes

{
  "cox_only": {
    "label": "Cox solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.6605105878139126,
      "std": 0.07909611115819527,
      "min": 0.5415710119749333,
      "max": 0.7634630600336267
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6874786979785115,
      "std": 0.046383234156742836,
      "min": 0.6361043411303767,
      "max": 0.7608916032044308
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6704513034362967,
      "std": 0.11591446279092456,
      "min": 0.497982610759031,
      "max": 0.8179247497981836
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.7193823478693239,
      "std": 0.06938615375307751,
      "min": 0.6481712135978382,
      "max": 0.8244678210506928
    }
  },
  "gbsa_only": {
    "label": "GBSA solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.6408988841377656,
      "std": 0.05353302049684243,
      "min": 0.5701044386422977,
      "max": 0.7123854236530293
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6396541510089124,
      "std": 0.049979963998843684,
      "min": 0.5852915578764143,
      "max": 0.7083985393844549
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6680411266800976,
      "std": 0.07167367118232555,
      "min": 0.5778882392198024,
      "max": 0.758775587049666
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6810272785881879,
      "std": 0.053824080429252574,
      "min": 0.6166294687339212,
      "max": 0.7517739868935024
    }
  },
  "rsf_only": {
    "label": "RSF solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.7173520154188384,
      "std": 0.05724692376866817,
      "min": 0.6222622076068747,
      "max": 0.7647240629017902
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6587619876638933,
      "std": 0.14892028956921527,
      "min": 0.40355696917011746,
      "max": 0.76361553423664
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.741251493746152,
      "std": 0.06482910618726356,
      "min": 0.6463229544379672,
      "max": 0.8047630379387396
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6837051156640473,
      "std": 0.1528203528237879,
      "min": 0.42160486998057267,
      "max": 0.78952299904458
    }
  },
  "cox_gbsa_rank": {
    "label": "Cox + GBSA",
    "valid_uno": {
      "count": 4,
      "mean": 0.6705609614257478,
      "std": 0.06435830096326917,
      "min": 0.5861822919898244,
      "max": 0.7425205222035407
    },
    "test_uno": {
      "count": 4,
      "mean": 0.681004624513106,
      "std": 0.050976472141378903,
      "min": 0.617796387240188,
      "max": 0.7410905614347411
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6886752588752703,
      "std": 0.09403496153204131,
      "min": 0.5362389996899952,
      "max": 0.7849200554000901
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.7169196302642169,
      "std": 0.05560990989359226,
      "min": 0.6350652656161001,
      "max": 0.7894588729016616
    }
  },
  "ensemble_all_rank": {
    "label": "Ensemble actual (rank equal)",
    "valid_uno": {
      "count": 4,
      "mean": 0.689782630523571,
      "std": 0.06268290738972619,
      "min": 0.5973506235651797,
      "max": 0.7554767085352586
    },
    "test_uno": {
      "count": 4,
      "mean": 0.688482341402764,
      "std": 0.06652410044091525,
      "min": 0.5876838129615467,
      "max": 0.7554313783667952
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.7079868968869623,
      "std": 0.08525281057298136,
      "min": 0.5734470358964588,
      "max": 0.7963530149304056
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.7229896052396121,
      "std": 0.06788956537567173,
      "min": 0.6139738945833619,
      "max": 0.7932169821231906
    }
  },
  "ensemble_weighted_rank": {
    "label": "Ensemble ponderado (GBSA dominante)",
    "valid_uno": {
      "count": 4,
      "mean": 0.672429814701519,
      "std": 0.05960156014627636,
      "min": 0.599274058447602,
      "max": 0.733503939603732
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6766481824428238,
      "std": 0.055525304521475596,
      "min": 0.6052602169607035,
      "max": 0.7309654501697821
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6923384585595413,
      "std": 0.08489047284817702,
      "min": 0.5587292625772426,
      "max": 0.773137129576558
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.7129887059705081,
      "std": 0.05802776391252116,
      "min": 0.6234667928857617,
      "max": 0.7728476031489264
    }
  }
}

## Ranking de variantes

[
  {
    "variant": "ensemble_all_rank",
    "label": "Ensemble actual (rank equal)",
    "test_uno_mean": 0.688482341402764,
    "valid_uno_mean": 0.689782630523571,
    "test_dynamic_auc_mean": 0.7229896052396121,
    "valid_dynamic_auc_mean": 0.7079868968869623
  },
  {
    "variant": "cox_only",
    "label": "Cox solo",
    "test_uno_mean": 0.6874786979785115,
    "valid_uno_mean": 0.6605105878139126,
    "test_dynamic_auc_mean": 0.7193823478693239,
    "valid_dynamic_auc_mean": 0.6704513034362967
  },
  {
    "variant": "cox_gbsa_rank",
    "label": "Cox + GBSA",
    "test_uno_mean": 0.681004624513106,
    "valid_uno_mean": 0.6705609614257478,
    "test_dynamic_auc_mean": 0.7169196302642169,
    "valid_dynamic_auc_mean": 0.6886752588752703
  },
  {
    "variant": "ensemble_weighted_rank",
    "label": "Ensemble ponderado (GBSA dominante)",
    "test_uno_mean": 0.6766481824428238,
    "valid_uno_mean": 0.672429814701519,
    "test_dynamic_auc_mean": 0.7129887059705081,
    "valid_dynamic_auc_mean": 0.6923384585595413
  },
  {
    "variant": "rsf_only",
    "label": "RSF solo",
    "test_uno_mean": 0.6587619876638933,
    "valid_uno_mean": 0.7173520154188384,
    "test_dynamic_auc_mean": 0.6837051156640473,
    "valid_dynamic_auc_mean": 0.741251493746152
  },
  {
    "variant": "gbsa_only",
    "label": "GBSA solo",
    "test_uno_mean": 0.6396541510089124,
    "valid_uno_mean": 0.6408988841377656,
    "test_dynamic_auc_mean": 0.6810272785881879,
    "valid_dynamic_auc_mean": 0.6680411266800976
  }
]

## Comparacion con split unico

{
  "valid_uno": 0.775564210783449,
  "test_uno": 0.6050411972118083,
  "valid_dynamic_auc_mean": 0.7927701697505469,
  "test_dynamic_auc_mean": 0.9235562832201322,
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
          "uno_c_index": 0.7741816259854306
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "uno_c_index": 0.5973506235651797
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.7554313783667952
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148334,
          "events": 18521,
          "tau": 134.99999999999997,
          "mean_auc": 0.8307098157920892,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1060,
              "controls": 147274,
              "auc": 0.8373862824292853,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 1999,
              "controls": 146335,
              "auc": 0.8283115333591899,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4064,
              "controls": 144270,
              "auc": 0.8283732213945418,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "mean_auc": 0.5734470358964588,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 505,
              "auc": 0.5192079207920792,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 7,
              "controls": 503,
              "auc": 0.5850610621982391,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 14,
              "controls": 496,
              "auc": 0.6088709677419355,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.7932169821231906,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.8802088277171334,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.7932583082369102,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.7497045288807302,
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
            "ibs": 0.019341663228770248
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.03528033089116262
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01904204447954849
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
            "ibs": 0.01892659873110084
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02366715961701962
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.011574876708625228
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
            "ibs": 0.021200965964708208
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02470868122824304
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.012947503893768217
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
            "uno_c_index": 0.7546298330164118
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5415710119749333
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7608916032044308
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7992954839036278,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8047790301532685,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7985189864895204,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7968337754519221,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.497982610759031,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.44950495049504946,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5455836410110764,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5190092165898618,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8244678210506928,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8614143331751305,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8510593332276641,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7953579601176856,
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
            "uno_c_index": 0.7469637211877151
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.6146615375069802
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6656858866580951
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.795562535153932,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8066033540101483,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7940737529731142,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7905720743695247,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5778882392198024,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.5075247524752475,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5677364385117863,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.6310483870967742,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.712607668093294,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8633602278120551,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6931367887145348,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6450197399854151,
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
            "uno_c_index": 0.7845275739307392
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.6222622076068747
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.76361553423664
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8578891964830992,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8633880988356704,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8541537160762702,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8567651188115677,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.6463229544379672,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.6134653465346535,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.6458392502130076,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.6699308755760368,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7874411140133445,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8625533934504034,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7812912770116764,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7523449090954812,
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
            "uno_c_index": 0.7604153470227762
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5861822919898244
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7410905614347411
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8072475019241485,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8149622792684461,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8058434588531496,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8039258227273992,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5362389996899952,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4685148514851485,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5501278046009656,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5806451612903225,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7894588729016616,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.883531086853346,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7919374438632641,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7414313375411774,
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
            "uno_c_index": 0.7741816259854306
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5973506235651797
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7554313783667952
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8307098157920892,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8373862824292853,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8283115333591899,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8283732213945418,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5734470358964588,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.5192079207920792,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5850610621982391,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.6088709677419355,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7932169821231906,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8802088277171334,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7932583082369102,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7497045288807302,
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
            "uno_c_index": 0.7625321585278726
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.599274058447602
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7309654501697821
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8128562259781872,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8212764309677174,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8110587873292234,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8093513240907659,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5587292625772426,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.49306930693069306,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.566032377165578,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.6035426267281105,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7728476031489264,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8813478879924063,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7681618851376341,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7204717479317022,
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
          "uno_c_index": 0.7765331752600845
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.7554767085352586
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.6701479547432551
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148844,
          "events": 18555,
          "tau": 134.99999999999997,
          "mean_auc": 0.8334985383114872,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1065,
              "controls": 147779,
              "auc": 0.8397940180119869,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2006,
              "controls": 146838,
              "auc": 0.8311786826556384,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4078,
              "controls": 144766,
              "auc": 0.8313162498419513,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.7963530149304056,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.8685334598955862,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.8175622127119988,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.7517791133351774,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.7215583634225765,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.728643216080402,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.7476110174255199,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.7046468889472302,
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
            "ibs": 0.01937810228530347
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01642240828045829
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02342947732691193
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
            "ibs": 0.0189708127723062
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.011655226538935845
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.018722321096291676
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
            "ibs": 0.02120134850310193
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.012739505230329675
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.019374038177685602
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
            "uno_c_index": 0.7548615460435187
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7634630600336267
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6893820713664056
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7990738963902954,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8035489614345137,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7989408709677774,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7968341438084888,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8179247497981836,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8498338870431894,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8514291752522851,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7885684109940403,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7382923233098145,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8358458961474037,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7405845980888139,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.709110002625361,
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
            "uno_c_index": 0.751422438529865
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6664441367487555
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5852915578764143
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8009315474038645,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8118709841021012,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7988090255310425,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7962726637159803,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7135106179425963,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8393450403417181,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7190521477254714,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.648376794829884,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.643097990632034,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5724455611390284,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.684654300168634,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6395379364662641,
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
            "uno_c_index": 0.7865270023446513
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7647240629017902
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7086161879895562
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8609421317485353,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8666363428679045,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8573622575388016,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.8596411311641874,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8047630379387396,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8754627432368296,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8274422782268717,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7603414891744411,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7362514796176922,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6683417085427136,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7754356379988758,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7332633237070098,
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
            "uno_c_index": 0.7626388716070954
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7425205222035407
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6452567449956483
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8098002504656244,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8169687752556023,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8084126683950654,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.806745827602241,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7849200554000901,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8583768391077361,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8059386062239129,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7397842432167374,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7080793427355087,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7546063651591289,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7259696458684655,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6845628773956419,
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
            "uno_c_index": 0.7765331752600845
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7554767085352586
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6701479547432551
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8334985383114872,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8397940180119869,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8311786826556384,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.8313162498419513,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7963530149304056,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8685334598955862,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8175622127119988,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7517791133351774,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7215583634225765,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.728643216080402,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7476110174255199,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7046468889472302,
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
            "uno_c_index": 0.7654798387390656
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.733503939603732
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.639686684073107
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8163879205269708,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8244535846844261,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8144564725849963,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.8131193684930463,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.773137129576558,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8598006644518272,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7915676018386433,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7224331732340885,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7010650481733889,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7068676716917923,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7268128161888702,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6846941454449987,
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
          "uno_c_index": 0.7739044422529958
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.6677980852915579
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.740666219539459
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 150956,
          "events": 18616,
          "tau": 134.99999999999997,
          "mean_auc": 0.8320750183733053,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1070,
              "controls": 149886,
              "auc": 0.838215573430823,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2015,
              "controls": 148941,
              "auc": 0.8300644252308811,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4097,
              "controls": 146859,
              "auc": 0.8298317986845671,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.6986961946397187,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.721105527638191,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.7136031478358629,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.6837752690995013,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.7632091808293192,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.8320969337289812,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.7543662674650699,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.7206843293334918,
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
            "ibs": 0.019447689831209133
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02454101713922106
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.025826520516620335
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
            "ibs": 0.018914148129327086
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.019593801340548018
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02242250333911235
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
            "ibs": 0.02108390280374238
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.019713294353080203
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.022713905196862793
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
            "uno_c_index": 0.753064161093036
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6771975630983463
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6635367762128326
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7968005643130616,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8007432907576737,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7964967009518966,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7949122038810568,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7140809216440454,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8006700167504188,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7217537942664418,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6849566815437123,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6665980335189496,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6998021760633036,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6192614770459082,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6766068670547701,
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
            "uno_c_index": 0.7448712154358187
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5701044386422977
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7083985393844549
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7955791597207929,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8062449517708224,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7947475129751029,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7904751773390182,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.621990062508326,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5967336683417086,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6488195615514334,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6138750328170124,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7517739868935024,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8340751730959446,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7764471057884231,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6760128311750029,
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
            "uno_c_index": 0.7844981843943087
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7227154046997389
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7592592592592593
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8606402627615919,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8667263880673923,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8569639870887973,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8591810535558206,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7165088205903689,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6750418760469012,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7240022484541878,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7240745602520346,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.78952299904458,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8709198813056379,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7931636726546907,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.7292978495901152,
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
            "uno_c_index": 0.7594707322845647
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6309834638816362
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7198748043818466
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8071120237726732,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8137234391595556,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8062731819649205,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8040949685586302,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6913575906801983,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7554438860971524,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7116357504215851,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6614597007088474,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7350750398035971,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7925321463897131,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.717564870259481,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.7067838897469407,
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
            "uno_c_index": 0.7739044422529958
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6677980852915579
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.740666219539459
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8320750183733053,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.838215573430823,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8300644252308811,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8298317986845671,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6986961946397187,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.721105527638191,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7136031478358629,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6837752690995013,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7632091808293192,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8320969337289812,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7543662674650699,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.7206843293334918,
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
            "uno_c_index": 0.7616407000907981
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6281984334203655
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7306803785677025
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.813436408560806,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8211001887914566,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8121644317566886,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8100751084806401,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6796844631201379,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7018425460636516,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7034851039910062,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6597532160672093,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7545753796739557,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8222057368941642,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7522455089820359,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.7083283830343353,
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
          "uno_c_index": 0.7751321600335549
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.7385051047022878
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "uno_c_index": 0.5876838129615467
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 151555,
          "events": 18636,
          "tau": 134.99999999999997,
          "mean_auc": 0.8334578379206793,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1072,
              "controls": 150483,
              "auc": 0.8400851930911817,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2021,
              "controls": 149534,
              "auc": 0.8315130259828081,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4110,
              "controls": 147445,
              "auc": 0.8309404141706846,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.7634513420812657,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.8382789317507419,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.7480039920159681,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.7213971723892123,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "mean_auc": 0.6139738945833619,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 41,
              "controls": 50816,
              "auc": 0.6455816681513792,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 152,
              "controls": 50015,
              "auc": 0.6024853070394671,
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
            "ibs": 0.019427517383168277
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02557322917900478
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.10332716302670097
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
            "ibs": 0.018871759591903847
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.022658083579544304
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.03127927477849919
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
            "ibs": 0.02109809868503299
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02267993820975674
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.0055009563395901585
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
            "uno_c_index": 0.7536400675990994
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6598107161487443
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6361043411303767
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7978863206745498,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8030778238599074,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7980426203769564,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7951512226217554,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6518169315439268,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6782888229475766,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6024201596806388,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6680527503861233,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6481712135978382,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6524193455489341,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.646627130281968,
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
            "uno_c_index": 0.7527204612260043
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7123854236530293
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5992406201166857
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8038850393520091,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8139006918865532,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8024632745422333,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7993912505954012,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.758775587049666,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8532393669634026,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7780688622754491,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6782107639301413,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6166294687339212,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6499285322080237,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6045261421573528,
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
            "uno_c_index": 0.7867258460261879
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7597063864669499
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.40355696917011746
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8637260854941209,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8700438939847521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8601582963592114,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.8621048031518866,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7974111620175323,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8958951533135509,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7821856287425148,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.7384460021385291,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.42160486998057267,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4414475275695767,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.4143925901177015,
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
            "uno_c_index": 0.7625914848700456
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7225575676279902
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.617796387240188
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8117284152575979,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8189030575278944,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8107482528585408,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.8084919181790661,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7421843897307973,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8093471810089021,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7251746506986028,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.7066650825709873,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6350652656161001,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6644008800761811,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6244025476567556,
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
            "uno_c_index": 0.7751321600335549
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7385051047022878
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5876838129615467
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8334578379206793,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8400851930911817,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8315130259828081,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.8309404141706846,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7634513420812657,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8382789317507419,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7480039920159681,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.7213971723892123,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6139738945833619,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6455816681513792,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6024853070394671,
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
            "uno_c_index": 0.7643913660550725
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7287428273343767
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6052602169607035
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.816773755825991,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8246487758422854,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8153105775609395,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.813397276513433,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7578029789642269,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8380316518298714,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.751122754491018,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.7057146251633598,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6234667928857617,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6543687507679548,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6122347506274434,
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

