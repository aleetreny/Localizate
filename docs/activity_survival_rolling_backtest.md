# Activity Survival Rolling Backtest

Walk-forward backtest temporal para medir estabilidad del ensemble survival sobre `activity_survival` usando multiples cortes contiguos en el tiempo.

## Configuracion

- Filas evaluables: 203828
- Folds ejecutados: 4
- Cutoffs: ["2020-03", "2021-04", "2022-06", "2023-06", "2024-10", "2026-04"]
- Training run: {"rsf_n_estimators": 120, "rsf_chunk_size": 20, "gbsa_n_estimators": 120, "gbsa_chunk_size": 20, "fit_max_rows": 25000, "cut_quantiles": [0.55, 0.65, 0.75, 0.85, 0.95], "min_valid_events": 20, "min_test_events": 20}

## Lectura ejecutiva

- El rolling backtest ejecuta 4 folds walk-forward; media valid Uno=0.6735, test Uno=0.6753, valid mean AUC=0.6741, test mean AUC=0.6990.
- Frente al split unico actual, valid Uno pasa de 0.7756 a media rolling 0.6735; test Uno pasa de 0.6050 a media rolling 0.6753.
- Frente al split unico, valid mean AUC pasa de 0.7928 a 0.6741; test mean AUC pasa de 0.9236 a 0.6990.
- Quality gates por fold: pass, pass, pass, pass_with_caveats.
- La mejor variante por media de Uno test es Cox solo con test Uno=0.6811 y valid Uno=0.6619.
- Comparativa clave: ensemble actual test Uno=0.6753, ensemble ponderado=0.6608, GBSA solo=0.6299.

## Resumen agregado

{
  "valid_uno": {
    "count": 4,
    "mean": 0.6735158944418711,
    "std": 0.06572175452348683,
    "min": 0.5718495998014519,
    "max": 0.7556044571918372
  },
  "test_uno": {
    "count": 4,
    "mean": 0.6752597443143278,
    "std": 0.06617966863947315,
    "min": 0.5741175409958869,
    "max": 0.7594698842844427
  },
  "valid_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.6741106862085041,
    "std": 0.09842138890200267,
    "min": 0.5104704128134034,
    "max": 0.7710333381557396
  },
  "test_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.699014687480015,
    "std": 0.0714421244921055,
    "min": 0.5904000260871158,
    "max": 0.7900371536907786
  }
}

## Benchmark de variantes

{
  "cox_only": {
    "label": "Cox solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.6619402677650145,
      "std": 0.08726565827754902,
      "min": 0.5325743004281194,
      "max": 0.7773794217518873
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6811182438237625,
      "std": 0.07215932101728381,
      "min": 0.5908805165664671,
      "max": 0.7901378037121287
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6715586838930316,
      "std": 0.10983900168849071,
      "min": 0.5075964218485878,
      "max": 0.808996391791924
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.7091114299983602,
      "std": 0.0880897095778036,
      "min": 0.6072581168953309,
      "max": 0.839010904840543
    }
  },
  "gbsa_only": {
    "label": "GBSA solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.6261920345793575,
      "std": 0.03745919220822548,
      "min": 0.584289880250667,
      "max": 0.6804099495598853
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6299423776448964,
      "std": 0.027912863807504205,
      "min": 0.6028285465622281,
      "max": 0.6669880987703162
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6397188740996306,
      "std": 0.0682116306250662,
      "min": 0.52887010907087,
      "max": 0.6984829282636108
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6595024934931886,
      "std": 0.0419928796871045,
      "min": 0.6028833212245147,
      "max": 0.7009542650210331
    }
  },
  "rsf_only": {
    "label": "RSF solo",
    "valid_uno": {
      "count": 4,
      "mean": 0.6853745423625252,
      "std": 0.059283561554143625,
      "min": 0.5875783334367438,
      "max": 0.7473584874559062
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6626843441614138,
      "std": 0.12551830359023788,
      "min": 0.4519878192609678,
      "max": 0.7828355256651172
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6796399116887633,
      "std": 0.08898151901421816,
      "min": 0.5329573011597668,
      "max": 0.7599110780601804
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6761688841692105,
      "std": 0.12343613562990816,
      "min": 0.4720677774213008,
      "max": 0.7987248926738759
    }
  },
  "cox_gbsa_rank": {
    "label": "Cox + GBSA",
    "valid_uno": {
      "count": 4,
      "mean": 0.6569883716443731,
      "std": 0.06661457045644446,
      "min": 0.563101073400757,
      "max": 0.7513928724491478
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6647467159830465,
      "std": 0.04473987771155213,
      "min": 0.6092100289013817,
      "max": 0.7339696040615831
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6629857309528124,
      "std": 0.10017608524579873,
      "min": 0.49858613560393905,
      "max": 0.769894192038185
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6957380903860875,
      "std": 0.056296260144172536,
      "min": 0.6186929509076295,
      "max": 0.7777532121852456
    }
  },
  "ensemble_all_rank": {
    "label": "Ensemble actual (rank equal)",
    "valid_uno": {
      "count": 4,
      "mean": 0.6735158944418711,
      "std": 0.06572175452348683,
      "min": 0.5718495998014519,
      "max": 0.7556044571918372
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6752597443143278,
      "std": 0.06617966863947315,
      "min": 0.5741175409958869,
      "max": 0.7594698842844427
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6741106862085041,
      "std": 0.09842138890200267,
      "min": 0.5104704128134034,
      "max": 0.7710333381557396
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.699014687480015,
      "std": 0.0714421244921055,
      "min": 0.5904000260871158,
      "max": 0.7900371536907786
    }
  },
  "ensemble_weighted_rank": {
    "label": "Ensemble ponderado (GBSA dominante)",
    "valid_uno": {
      "count": 4,
      "mean": 0.654628190812877,
      "std": 0.05875648677386828,
      "min": 0.5717255072283923,
      "max": 0.7376042593874658
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6608042385308085,
      "std": 0.043639446117755464,
      "min": 0.6025046557530125,
      "max": 0.7249447796129628
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.661153956759343,
      "std": 0.0899325963372902,
      "min": 0.5124717765892411,
      "max": 0.7520008070765114
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6904211982273801,
      "std": 0.0537993816782074,
      "min": 0.6106738937866553,
      "max": 0.7612648679554173
    }
  }
}

## Ranking de variantes

[
  {
    "variant": "cox_only",
    "label": "Cox solo",
    "test_uno_mean": 0.6811182438237625,
    "valid_uno_mean": 0.6619402677650145,
    "test_dynamic_auc_mean": 0.7091114299983602,
    "valid_dynamic_auc_mean": 0.6715586838930316
  },
  {
    "variant": "ensemble_all_rank",
    "label": "Ensemble actual (rank equal)",
    "test_uno_mean": 0.6752597443143278,
    "valid_uno_mean": 0.6735158944418711,
    "test_dynamic_auc_mean": 0.699014687480015,
    "valid_dynamic_auc_mean": 0.6741106862085041
  },
  {
    "variant": "cox_gbsa_rank",
    "label": "Cox + GBSA",
    "test_uno_mean": 0.6647467159830465,
    "valid_uno_mean": 0.6569883716443731,
    "test_dynamic_auc_mean": 0.6957380903860875,
    "valid_dynamic_auc_mean": 0.6629857309528124
  },
  {
    "variant": "rsf_only",
    "label": "RSF solo",
    "test_uno_mean": 0.6626843441614138,
    "valid_uno_mean": 0.6853745423625252,
    "test_dynamic_auc_mean": 0.6761688841692105,
    "valid_dynamic_auc_mean": 0.6796399116887633
  },
  {
    "variant": "ensemble_weighted_rank",
    "label": "Ensemble ponderado (GBSA dominante)",
    "test_uno_mean": 0.6608042385308085,
    "valid_uno_mean": 0.654628190812877,
    "test_dynamic_auc_mean": 0.6904211982273801,
    "valid_dynamic_auc_mean": 0.661153956759343
  },
  {
    "variant": "gbsa_only",
    "label": "GBSA solo",
    "test_uno_mean": 0.6299423776448964,
    "valid_uno_mean": 0.6261920345793575,
    "test_dynamic_auc_mean": 0.6595024934931886,
    "valid_dynamic_auc_mean": 0.6397188740996306
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
          "uno_c_index": 0.7751733033955768
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "uno_c_index": 0.5718495998014519
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.7594698842844427
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148334,
          "events": 18521,
          "tau": 134.99999999999997,
          "mean_auc": 0.828061486079472,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1060,
              "controls": 147274,
              "auc": 0.8374313402742315,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 1999,
              "controls": 146335,
              "auc": 0.8252360676528513,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4064,
              "controls": 144270,
              "auc": 0.8245365574868098,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "mean_auc": 0.5104704128134034,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 505,
              "auc": 0.3996039603960396,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 7,
              "controls": 503,
              "auc": 0.4916216983811417,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 14,
              "controls": 496,
              "auc": 0.5950460829493088,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.7900371536907786,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.8433792121499762,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.7910920906641306,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.7629441496718385,
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
            "ibs": 0.019378713583934996
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.045808845333723244
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.025939527512393378
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
            "ibs": 0.019501666887898995
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023590115634845695
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.011482140257668725
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
            "ibs": 0.021326802339125754
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023780144160407166
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.011921232706150904
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
            "uno_c_index": 0.7550725354977847
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5325743004281194
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7901378037121287
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8029326139493052,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8101747230998773,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8010103849204815,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8000891937839102,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5075964218485878,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4582178217821782,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5603521726782164,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5277937788018434,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.839010904840543,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8691029900332226,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8706081259576266,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.8113259737973697,
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
            "uno_c_index": 0.7440716366956922
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.584289880250667
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6669880987703162
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7883317684793114,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8020528928110123,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7858989425693133,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7823947378439049,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.52887010907087,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4314851485148515,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5001420051121841,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.6066388248847927,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7009542650210331,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.80640721404841,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6938236381888307,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6510800412402243,
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
            "uno_c_index": 0.7866880771500688
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5875783334367438
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7828355256651172
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.851594320031845,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8609791183728648,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8487512574410006,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8480697435336958,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5329573011597668,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4297029702970297,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5117864243112752,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.6127592165898619,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7987248926738759,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8158519221642144,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7961377925714587,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7911962179696733,
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
            "uno_c_index": 0.7596225518685389
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.563101073400757
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7339696040615831
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.805869828521762,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8157180711296439,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8033365471473906,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8019664939194282,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.49858613560393905,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.38851485148514847,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.4779892076114739,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5830933179723502,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7777532121852456,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8573327005220692,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7830084006974164,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7358613926119647,
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
            "uno_c_index": 0.7751733033955768
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5718495998014519
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7594698842844427
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.828061486079472,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8374313402742315,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8252360676528513,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8245365574868098,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5104704128134034,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.3996039603960396,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.4916216983811417,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5950460829493088,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7900371536907786,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8433792121499762,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7910920906641306,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7629441496718385,
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
            "uno_c_index": 0.7617223879778506
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5717255072283923
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7249447796129628
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.809438723680515,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8202583408258923,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8067874388897732,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8050904245252641,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5124717765892411,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4059405940594059,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.4887815961374609,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5953341013824885,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7612648679554173,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8397721879449453,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7620330744439161,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7217039253652526,
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
          "uno_c_index": 0.7748265397435417
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.7556044571918372
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.678503046127067
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148844,
          "events": 18555,
          "tau": 134.99999999999997,
          "mean_auc": 0.827295339632555,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1065,
              "controls": 147779,
              "auc": 0.8359565881383528,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2006,
              "controls": 146838,
              "auc": 0.8245673415064467,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4078,
              "controls": 144766,
              "auc": 0.8240824132705826,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.7710333381557396,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.8154722354057902,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.8023458551275955,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.736288882741972,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.6983521404130185,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.7010050251256281,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.7121978639685216,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.6896823313205567,
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
            "ibs": 0.019420706847590043
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01642552513425772
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02648648597400257
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
            "ibs": 0.01958660161925013
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.011775454129468807
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.01884660413907223
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
            "ibs": 0.021475145886043264
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.012189484920028264
          },
          "test": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.0187914935938985
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
            "uno_c_index": 0.7551754810891017
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7773794217518873
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
            "mean_auc": 0.8023228724570988,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8086081179398484,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8008880083485904,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7997439249122039,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.808996391791924,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8483151400094922,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8459343794579173,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7745618226167426,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7363068109239498,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8659966499162479,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7296233839235525,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7030716723549488,
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
            "uno_c_index": 0.7434942289192118
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6804099495598853
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6028285465622281
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7869599260117738,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8001578267154223,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7845422771579567,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7812742326343878,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6984829282636108,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7839107736117703,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7037301209911766,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6536701284985038,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6353481825533487,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.5938023450586265,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6687745924676785,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6281176161722237,
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
            "uno_c_index": 0.784530737967188
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7473584874559062
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7012184508268059
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8497312249033933,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8587140479119832,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8465889294619038,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.846541163854307,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7599110780601804,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7826293308020882,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7880541026047444,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.737294741871401,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6952172555513546,
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
                "auc": 0.7223159078133783,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.707272249934366,
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
            "uno_c_index": 0.759914651274374
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7513928724491478
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6536118363794604
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8054330268147138,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8144519444353636,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.803208618400373,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.8018075543494159,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.769894192038185,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.826578073089701,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8006551487293284,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7292478688359696,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6921826923494563,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7378559463986599,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7015177065767285,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6737988973483854,
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
            "uno_c_index": 0.7748265397435417
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7556044571918372
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.678503046127067
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.827295339632555,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8359565881383528,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8245673415064467,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.8240824132705826,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7710333381557396,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8154722354057902,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8023458551275955,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.736288882741972,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6983521404130185,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7010050251256281,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7121978639685216,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6896823313205567,
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
            "uno_c_index": 0.7616564651707064
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7376042593874658
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6512619669277633
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8087475152039947,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8189327566823789,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8062490211572884,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.804647032927678,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7520008070765114,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8124347413383958,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7764040788291858,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7120225312444992,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6859455743438052,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6959798994974875,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7051714446318156,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6720924127067471,
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
          "uno_c_index": 0.7750157165406986
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.6809399477806789
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.6889485058499143
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 150956,
          "events": 18616,
          "tau": 134.99999999999997,
          "mean_auc": 0.828488691338725,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1070,
              "controls": 149886,
              "auc": 0.8375407833317807,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2015,
              "controls": 148941,
              "auc": 0.8259699366693454,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4097,
              "controls": 146859,
              "auc": 0.8249797983175887,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.6942536138658678,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.6976549413735343,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.7062956717256885,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.686400630086637,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.7172694297291475,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.8125618199802177,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.6939870259481038,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.6662706427468219,
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
            "ibs": 0.019488756423832552
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.015880599979759755
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.020781096919255018
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
            "ibs": 0.019537747894623203
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.019989244167293748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.02312166273218763
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
            "ibs": 0.021401038331943692
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.018871336089787374
          },
          "test": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.022381040271432062
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
            "uno_c_index": 0.7536526773169472
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6812010443864229
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6540725836500484
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8004338020221285,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8061107345008998,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7991210335373027,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7981121154063144,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7174851788054769,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8534338358458962,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.718381112984823,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6781307429771594,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6538698873336172,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6866963402571711,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5948103792415169,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6724486158964003,
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
            "uno_c_index": 0.7418109250785975
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5995213228894691
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6468812877263581
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7870450241652628,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8009928667282461,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7848969339750382,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7808518222859977,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6382454623520983,
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
                "auc": 0.6808600337268128,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6257547912838015,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6988242051738578,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8136745796241345,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6972929141716566,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6185695616015208,
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
            "uno_c_index": 0.7864878393102331
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7009573542210618
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.714695580892764
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8520470159809814,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8617515386460065,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8494519896074224,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8482374389739865,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.685401558227156,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6197654941373534,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6978639685216413,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6970333420845365,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7386656110303109,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8439663699307616,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7239271457085829,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6745277414755853,
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
            "uno_c_index": 0.7589020587700531
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6533507397737163
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6621953945897607
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8054721524254927,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.814667380854309,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8032922623965062,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8017358900136575,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6877481486568946,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7345058626465661,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7009555930297919,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6668416907324757,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.694323506102019,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.787833827893175,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6654191616766467,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6485683735297612,
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
            "uno_c_index": 0.7750157165406986
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6809399477806789
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6889485058499143
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.828488691338725,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8375407833317807,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8259699366693454,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8249797983175887,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6942536138658678,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6976549413735343,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7062956717256885,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.686400630086637,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7172694297291475,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8125618199802177,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6939870259481038,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6662706427468219,
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
            "uno_c_index": 0.7608658011970333
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6495213228894691
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6645055518294954
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.809300645370553,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8198868710313296,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8069308690737916,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8049356968323247,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6774327148189059,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6842546063651591,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6989881956155143,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6631661853504858,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7038004568236428,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8076162215628091,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6835079840319361,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6446477367232981,
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
          "uno_c_index": 0.7769867721077287
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.6856695729935166
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "uno_c_index": 0.5741175409958869
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 151555,
          "events": 18636,
          "tau": 134.99999999999997,
          "mean_auc": 0.8285803869969081,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1072,
              "controls": 150483,
              "auc": 0.8380302366677805,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2021,
              "controls": 149534,
              "auc": 0.8260518524489875,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4110,
              "controls": 147445,
              "auc": 0.8248797361777607,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.7206853799990056,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.8281404549950544,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.68687624750499,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.668527979089937,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "mean_auc": 0.5904000260871158,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 41,
              "controls": 50816,
              "auc": 0.5997484468114517,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 152,
              "controls": 50015,
              "auc": 0.5870021230472963,
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
            "ibs": 0.019496649679489334
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.028069201075470826
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.11392563508602893
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
            "ibs": 0.019428106379635705
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.023092950453527335
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.022579078358957335
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
            "ibs": 0.021343672421296637
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "times": [
              6.0,
              12.0,
              24.0
            ],
            "ibs": 0.022404786534203334
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "times": [
              6.0,
              12.0
            ],
            "ibs": 0.004587732486110257
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
            "uno_c_index": 0.7539987715528752
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6566063044936284
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5908805165664671
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8007827890920989,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8078182685831226,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7996576443153858,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.797683568593642,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6521567431261375,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6909000989119684,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5830838323353293,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6736366876559343,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6072581168953309,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5943005275849358,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6119678570113176,
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
            "uno_c_index": 0.747866867152362
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6405469856174082
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6030715775206831
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7902777828315269,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.803591657499667,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.788379061066818,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7843081386527155,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6932769967119433,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.812809099901088,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6981037924151696,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6052037543067601,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6028833212245147,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6152311351907599,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5983952182766222,
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
            "uno_c_index": 0.7925092731328335
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7056039943363887
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4519878192609678
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8571923089448438,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8671893914530535,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8542760091888171,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.8533869934923155,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7402897093079499,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8533630069238378,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.7088323353293413,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6824878222644648,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.4720677774213008,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4984926487528415,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.46246303740456807,
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
            "uno_c_index": 0.7598523493037687
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6601088009538714
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6092100289013817
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8040419972552462,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8136912574346425,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8021474806770144,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7999509916642595,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.695714447512231,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8006923837784371,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6626746506986028,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6447665438992515,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6186929509076295,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6249952002826074,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6164022503775184,
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
            "uno_c_index": 0.7769867721077287
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6856695729935166
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5741175409958869
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8285803869969081,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8380302366677805,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8260518524489875,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.8248797361777607,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7206853799990056,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.8281404549950544,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.68687624750499,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.668527979089937,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5904000260871158,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5997484468114517,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5870021230472963,
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
            "uno_c_index": 0.7624493946279945
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6596616737461808
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6025046557530125
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.808286485685368,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8189982237295412,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8061221244634997,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.803772840695516,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7027105285527131,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.818001978239367,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6801397205588822,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6370440774622788,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6106738937866553,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6181714420654911,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6079487338009124,
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

