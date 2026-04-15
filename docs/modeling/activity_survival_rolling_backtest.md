# Activity Survival Rolling Backtest

Walk-forward backtest temporal para medir estabilidad del ensemble survival sobre `activity_survival` usando multiples cortes contiguos en el tiempo.

## Configuracion

- Filas evaluables: 203828
- Folds ejecutados: 4
- Cutoffs: ["2020-03", "2021-04", "2022-06", "2023-06", "2024-10", "2026-04"]
- Training run: {"rsf_n_estimators": 120, "rsf_chunk_size": 20, "gbsa_n_estimators": 120, "gbsa_chunk_size": 20, "fit_max_rows": 25000, "cut_quantiles": [0.55, 0.65, 0.75, 0.85, 0.95], "min_valid_events": 20, "min_test_events": 20}

## Lectura ejecutiva

- El rolling backtest ejecuta 4 folds walk-forward; media valid Uno=0.6041, test Uno=0.6044, valid mean AUC=0.6031, test mean AUC=0.6321.
- Frente al split unico actual, valid Uno pasa de 0.7756 a media rolling 0.6041; test Uno pasa de 0.6050 a media rolling 0.6044.
- Frente al split unico, valid mean AUC pasa de 0.7928 a 0.6031; test mean AUC pasa de 0.9236 a 0.6321.
- Quality gates por fold: pass, pass, pass, pass_with_caveats.
- La mejor variante por media de Uno test es Cox solo con test Uno=0.6835 y valid Uno=0.6678.
- Comparativa clave: ensemble actual test Uno=0.6044, ensemble ponderado=0.5910, GBSA solo=0.5389.

## Resumen agregado

{
  "valid_uno": {
    "count": 4,
    "mean": 0.6041099443488672,
    "std": 0.054454683588327016,
    "min": 0.5222125705776509,
    "max": 0.6751145616984802
  },
  "test_uno": {
    "count": 4,
    "mean": 0.6044144648856077,
    "std": 0.06384313762837801,
    "min": 0.5045814090425264,
    "max": 0.6825239837800415
  },
  "valid_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.6031263129296229,
    "std": 0.08712066117991377,
    "min": 0.4827808302909714,
    "max": 0.7282654334499818
  },
  "test_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.6321266758957451,
    "std": 0.07224869464563034,
    "min": 0.5316872554177795,
    "max": 0.7343927300266018
  }
}

## Benchmark de variantes

{
  "cox_only": {
    "label": "Cox solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.6677686339679356,
      "std": 0.09435190348286247,
      "min": 0.5239498666004839,
      "max": 0.7879207463818284
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6834864042388389,
      "std": 0.07481815715193156,
      "min": 0.5812495971401743,
      "max": 0.7914152902779151
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6658022650272486,
      "std": 0.12771563897102228,
      "min": 0.47604780525047524,
      "max": 0.8308669860224905
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.7058263369142574,
      "std": 0.08966954124850057,
      "min": 0.5979734549394962,
      "max": 0.8376956995501944
    }
  },
  "gbsa_only": {
    "label": "GBSA solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.5495929321885439,
      "std": 0.02633320257640252,
      "min": 0.5136812061798102,
      "max": 0.5797646127979428
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5388881296743546,
      "std": 0.03286253904445105,
      "min": 0.48320379393785245,
      "max": 0.5682713546302707
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5573758083490316,
      "std": 0.06040592213279867,
      "min": 0.48668031182215604,
      "max": 0.6507092547556623
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5581914930275984,
      "std": 0.05374571251458925,
      "min": 0.49292516464215946,
      "max": 0.6419152167298772
    }
  },
  "rsf_only": {
    "label": "RSF solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.5708070388732226,
      "std": 0.04885674355769266,
      "min": 0.516938636222622,
      "max": 0.6387728459530027
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5601071991376317,
      "std": 0.06278369304026898,
      "min": 0.4557229178026588,
      "max": 0.6156222802436901
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5599467876006867,
      "std": 0.0692417026565067,
      "min": 0.490167948622347,
      "max": 0.659266195003806
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5895218699593903,
      "std": 0.07407308926449657,
      "min": 0.48077045859234835,
      "max": 0.6715969768634865
    }
  },
  "cox_gbsa_rank": {
    "label": "Cox + GBSA",
    "valid_uno": {
      "count": 4,
      "mean": 0.6174493133465859,
      "std": 0.06905115067097625,
      "min": 0.5199789042625799,
      "max": 0.7132166287541621
    },
    "test_uno": {
      "count": 4,
      "mean": 0.615240652950737,
      "std": 0.07285534523976517,
      "min": 0.5068254471526303,
      "max": 0.7116259519335377
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6179152142987872,
      "std": 0.09858414613376774,
      "min": 0.4782167995836438,
      "max": 0.756934720403015
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6384017620581932,
      "std": 0.07977572730779084,
      "min": 0.5338344914306503,
      "max": 0.7584133342861241
    }
  },
  "ensemble_all_rank": {
    "label": "Ensemble actual (rank equal)",
    "valid_uno": {
      "count": 4,
      "mean": 0.6041099443488672,
      "std": 0.054454683588327016,
      "min": 0.5222125705776509,
      "max": 0.6751145616984802
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6044144648856077,
      "std": 0.06384313762837801,
      "min": 0.5045814090425264,
      "max": 0.6825239837800415
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6031263129296229,
      "std": 0.08712066117991377,
      "min": 0.4827808302909714,
      "max": 0.7282654334499818
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6321266758957451,
      "std": 0.07224869464563034,
      "min": 0.5316872554177795,
      "max": 0.7343927300266018
    }
  },
  "ensemble_weighted_rank": {
    "label": "Ensemble ponderado (GBSA dominante)",
    "valid_uno": {
      "count": 4,
      "mean": 0.5931793624824074,
      "std": 0.04914396870253512,
      "min": 0.5231432648755971,
      "max": 0.661589687798767
    },
    "test_uno": {
      "count": 4,
      "mean": 0.5909931835032843,
      "std": 0.05706013039769993,
      "min": 0.5022473045411231,
      "max": 0.6615814459499555
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.5970773430568692,
      "std": 0.07830925547241605,
      "min": 0.49268842660490053,
      "max": 0.7134768482623804
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6148966603919708,
      "std": 0.0688479373813094,
      "min": 0.5235405035063044,
      "max": 0.7175152705750919
    }
  }
}

## Ranking de variantes

[
  {
    "variant": "cox_only",
    "label": "Cox solo",
    "test_uno_mean": 0.6834864042388389,
    "valid_uno_mean": 0.6677686339679356,
    "test_dynamic_auc_mean": 0.7058263369142574,
    "valid_dynamic_auc_mean": 0.6658022650272486
  },
  {
    "variant": "cox_gbsa_rank",
    "label": "Cox + GBSA",
    "test_uno_mean": 0.615240652950737,
    "valid_uno_mean": 0.6174493133465859,
    "test_dynamic_auc_mean": 0.6384017620581932,
    "valid_dynamic_auc_mean": 0.6179152142987872
  },
  {
    "variant": "ensemble_all_rank",
    "label": "Ensemble actual (rank equal)",
    "test_uno_mean": 0.6044144648856077,
    "valid_uno_mean": 0.6041099443488672,
    "test_dynamic_auc_mean": 0.6321266758957451,
    "valid_dynamic_auc_mean": 0.6031263129296229
  },
  {
    "variant": "ensemble_weighted_rank",
    "label": "Ensemble ponderado (GBSA dominante)",
    "test_uno_mean": 0.5909931835032843,
    "valid_uno_mean": 0.5931793624824074,
    "test_dynamic_auc_mean": 0.6148966603919708,
    "valid_dynamic_auc_mean": 0.5970773430568692
  },
  {
    "variant": "rsf_only",
    "label": "RSF solo",
    "test_uno_mean": 0.5601071991376317,
    "valid_uno_mean": 0.5708070388732226,
    "test_dynamic_auc_mean": 0.5895218699593903,
    "valid_dynamic_auc_mean": 0.5599467876006867
  },
  {
    "variant": "gbsa_only",
    "label": "GBSA solo",
    "test_uno_mean": 0.5388881296743546,
    "valid_uno_mean": 0.5495929321885439,
    "test_dynamic_auc_mean": 0.5581914930275984,
    "valid_dynamic_auc_mean": 0.5573758083490316
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
          "uno_c_index": 0.7432305031465564
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "uno_c_index": 0.5222125705776509
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.6825239837800415
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148334,
          "events": 18521,
          "tau": 134.99999999999997,
          "mean_auc": 0.80149771363463,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1060,
              "controls": 147274,
              "auc": 0.8091173818996347,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 1999,
              "controls": 146335,
              "auc": 0.7982074168255755,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4064,
              "controls": 144270,
              "auc": 0.7990825757861054,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "mean_auc": 0.4827808302909714,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 505,
              "auc": 0.435049504950495,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 7,
              "controls": 503,
              "auc": 0.5224368077250781,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 14,
              "controls": 496,
              "auc": 0.5055443548387096,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.7343927300266018,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.7400094921689606,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.7725471548581391,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.7163225790228079,
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
            "ibs": 0.019482454322114918
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.021701862236632945
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.009037596049045341
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
            "ibs": 0.0203806318477689
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023999943853379224
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.013028944679052079
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
            "ibs": 0.02276811309446428
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02410756009387723
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.014238947246176744
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
            "uno_c_index": 0.751801167034844
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5239498666004839
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7914152902779151
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7975196959137024,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8015585857038132,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7948443692581248,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.796662993033349,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.47604780525047524,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4568316831683168,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5266969610905993,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4753024193548387,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8376956995501944,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8511627906976744,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8731441855550273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.8167827595745216,
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
            "uno_c_index": 0.6929945641220748
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
            "mean_auc": 0.7505555843388385,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7641900086887206,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7482810732594917,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7445910691294592,
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
            "uno_c_index": 0.7302592450388706
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.516938636222622
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6017909537467445
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8041331219845106,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.812595361975791,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8009207784949639,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8012500305297536,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.490167948622347,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4405940594059406,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5217267821641579,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5165610599078341,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6715969768634865,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7053630754627432,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7176784487768795,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6362813387985012,
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
            "uno_c_index": 0.7390857433171069
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5199789042625799
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7116259519335377
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7895398235031038,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7974710788080541,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7864708450169322,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.78686410445965,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.4782167995836438,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.433069306930693,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.52215279750071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.49791186635944695,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7584133342861241,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7591836734693878,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7925186241876685,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7443860487338749,
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
            "uno_c_index": 0.7432305031465564
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5222125705776509
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6825239837800415
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.80149771363463,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8091173818996347,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7982074168255755,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7990825757861054,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.4827808302909714,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.435049504950495,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5224368077250781,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5055443548387096,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7343927300266018,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7400094921689606,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7725471548581391,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7163225790228079,
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
            "uno_c_index": 0.7289615724677107
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5231432648755971
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6615814459499555
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.783884414789718,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7933377678007953,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7809108572463701,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7803839868679079,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.49268842660490053,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4461386138613861,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5318091451292246,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5147609447004609,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7175152705750919,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7324157570004746,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7448090030115708,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6991475343878091,
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
          "uno_c_index": 0.7404729468732636
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.6751145616984802
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.6154917319408181
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148844,
          "events": 18555,
          "tau": 134.99999999999997,
          "mean_auc": 0.7990440058477402,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1065,
              "controls": 147779,
              "auc": 0.8074714980912845,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2006,
              "controls": 146838,
              "auc": 0.7963843745055711,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4078,
              "controls": 144766,
              "auc": 0.7959201804875118,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.7282654334499818,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.743141907925961,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.762033074443916,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.707320139814419,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.6440858919065916,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.6030150753768844,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.6587970770095559,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.6474140194276713,
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
            "ibs": 0.019528151967378015
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.009245469686248746
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01587753111559759
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
            "ibs": 0.020544815403749066
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.013230904107136688
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01967646074984379
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
            "uno_c_index": 0.7511491450382168
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7879207463818284
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6923411662315057
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7964778900309734,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8000336786370538,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7947847759381929,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7954191571621658,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8308669860224905,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8414807783578548,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8722988323558937,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.8089873513214475,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7315827486204742,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7881072026800671,
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
                "auc": 0.7268311892885272,
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
            "uno_c_index": 0.7246558783277852
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.594801865954571
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6156222802436901
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7993819399470152,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8103849051084306,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7971250171630602,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.79475144112597,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.659266195003806,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7325106786900807,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6893591166059069,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.610606784519828,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6417720059182574,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5988274706867671,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6812816188870152,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6314649514308217,
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
            "uno_c_index": 0.7372843997617518
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7132166287541621
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6136640557006092
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7876698243017358,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7954584670860658,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7850441375311541,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7848589491500979,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.756934720403015,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7429520645467489,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7901939028900512,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7506223753363342,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6310745092653804,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5745393634840872,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6360314783586285,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6443948542924652,
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
            "uno_c_index": 0.7404729468732636
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6751145616984802
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6154917319408181
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7990440058477402,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8074714980912845,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7963843745055711,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7959201804875118,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7282654334499818,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.743141907925961,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.762033074443916,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.707320139814419,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6440858919065916,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6030150753768844,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6587970770095559,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6474140194276713,
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
            "uno_c_index": 0.7268205155000675
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.661589687798767
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5999129677980853
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7819949071824903,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7918303969126338,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7793514894507967,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7781400131298459,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7134768482623804,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7169435215946844,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7337137422729434,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7036487539920036,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6124439509030424,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5175879396984925,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6214165261382799,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6344184825413495,
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
          "uno_c_index": 0.7425951788826662
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.6147084421235858
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.6150607347790447
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 150956,
          "events": 18616,
          "tau": 134.99999999999997,
          "mean_auc": 0.8017563484440019,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1070,
              "controls": 149886,
              "auc": 0.808813679704987,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2015,
              "controls": 148941,
              "auc": 0.798762647250715,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4097,
              "controls": 146859,
              "auc": 0.7994881943510153,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.610871344399123,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.551926298157454,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.623946037099494,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.6202415332108165,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.6183408262320077,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.6742087042532147,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.625561377245509,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.573660449091125,
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
            "ibs": 0.019539429072749945
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01688160171297186
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.020862973524324098
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
            "ibs": 0.020464006992237518
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02020910707012437
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023161080801538145
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
            "ibs": 0.022579901986390722
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02016642898453373
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02329166111000644
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
            "uno_c_index": 0.7501742218675703
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6898172323759791
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6689395633057605
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7964929833806113,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.799469469070637,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7945314282773519,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7958536125277067,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.707192177266526,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7621440536013401,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.685778527262507,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7037280126017327,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6560534445468652,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6539317507418397,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6075973053892215,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6918735891647856,
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
            "uno_c_index": 0.6931422218291381
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
            "uno_c_index": 0.5542514345331246
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7510452742905244,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7632660697519522,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7488851639972749,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7457451076639119,
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
            "mean_auc": 0.5565362094728369,
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
                "auc": 0.590818363273453,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.48639657835333255,
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
            "uno_c_index": 0.7269979909057687
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6387728459530027
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5672926447574335
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.801980712584682,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8113603410242876,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.799058889256913,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7984864381439343,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5899420029364253,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5251256281407035,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6135469364811692,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.594972433709635,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5639480384634685,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6076904055390702,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5967440119760479,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5097421884281811,
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
            "uno_c_index": 0.7389821710315744
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.604177545691906
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6288471570161711
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7901269346897593,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7966864536674041,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7874205088920333,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.787984229153146,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6141905041232175,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5619765494137353,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6177627880831928,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6270674717773694,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6302847132506179,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6779179030662711,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6193238522954092,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6043127004871094,
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
            "uno_c_index": 0.7425951788826662
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6147084421235858
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6150607347790447
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8017563484440019,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.808813679704987,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.798762647250715,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7994881943510153,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.610871344399123,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.551926298157454,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.623946037099494,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6202415332108165,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6183408262320077,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6742087042532147,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.625561377245509,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.573660449091125,
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
            "uno_c_index": 0.7287880757349339
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5879025239338556
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6002310157239734
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7844606654553691,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7927816386559704,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7816949832900509,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7814395935637177,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5886908557680066,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.48157453936348404,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.5966835300730746,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6147282751378315,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6060869165834445,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6635756676557863,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6177020958083832,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5571462516335987,
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
          "uno_c_index": 0.7390931710364164
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.6044042029957523
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "uno_c_index": 0.5045814090425264
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 151555,
          "events": 18636,
          "tau": 134.99999999999997,
          "mean_auc": 0.7987873540114908,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1072,
              "controls": 150483,
              "auc": 0.8070938040950923,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2021,
              "controls": 149534,
              "auc": 0.7961051564931985,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4110,
              "controls": 147445,
              "auc": 0.7957432616013609,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.5905876435784159,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.6245054401582592,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.5998627744510978,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.5599976238564809,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "mean_auc": 0.5316872554177795,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 41,
              "controls": 50816,
              "auc": 0.5554472952632549,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 152,
              "controls": 50015,
              "auc": 0.5230511109824948,
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
            "ibs": 0.01953298405351334
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02107354985296718
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.114372238612175
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
            "ibs": 0.02048295281631686
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02316668327609111
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.07961314168166833
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
            "ibs": 0.02260759843778537
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023307608888870405
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.005684639981155225
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
            "uno_c_index": 0.750316853527961
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6693866905134511
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5812495971401743
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7970696457985235,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8010630489971545,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.795534306688302,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7957178547916626,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6491020915695028,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6403313550939663,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5989895209580838,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6908043245812046,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5979734549394962,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5883695168028507,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6014642317830966,
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
            "uno_c_index": 0.6925264117073943
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5691556747894776
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.48320379393785245
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7511353328155418,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7638774570013909,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7490815074271938,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7455295516601143,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.563808986520184,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.607566765578635,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5936252495009979,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5117025068314126,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.49292516464215946,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5233170270934446,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.48187852854669905,
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
            "uno_c_index": 0.7268824298864558
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5327148073626947
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4557229178026588
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8039187324311139,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8154416937907698,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8007553163329968,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7994426516745614,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5004110038401686,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5027200791295747,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5364271457085829,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.4732683854104789,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.48077045859234835,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4921922997173926,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.47661892221807145,
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
            "uno_c_index": 0.7340698881047939
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6324241746776958
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5068254471526303
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7865745106099297,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7943052351527584,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7843368479719748,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7836239146949018,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6223188330852724,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.65986646884273,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6127120758483033,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.602530592847808,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5338344914306503,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5606787472353628,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5240773162788006,
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
            "uno_c_index": 0.7390931710364164
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6044042029957523
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5045814090425264
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7987873540114908,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8070938040950923,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7961051564931985,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7957432616013609,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5905876435784159,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6245054401582592,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5998627744510978,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5599976238564809,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5316872554177795,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5554472952632549,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5230511109824948,
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
            "uno_c_index": 0.7251224494523406
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6000819733214099
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5022473045411231
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7813734017788513,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7906322673330185,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7789334326299946,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7777305232954612,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5934532415921892,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6356330365974283,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6057260479041916,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5548889152904836,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5235405035063044,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5496965138692633,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5140334873222244,
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

