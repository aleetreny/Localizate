# Activity Survival HPO

Busqueda competitiva de hiperparametros sobre rolling backtest walk-forward para comparar `cox_only` y `ensemble_all_rank`.

## Configuracion

{
  "transition_policy_train": "exclude_transition",
  "renta_max_year": 2023,
  "quantiles": [
    0.55,
    0.65,
    0.75,
    0.85,
    0.95
  ],
  "min_valid_events": 20,
  "min_test_events": 20,
  "cox_screen_trials": 20,
  "ensemble_screen_trials": 8,
  "confirm_top_k": 2,
  "final_top_k": 2,
  "screen_fit_max_rows": 12000,
  "confirm_fit_max_rows": 25000,
  "final_fit_max_rows": null,
  "screen_rsf_estimators": 80,
  "screen_gbsa_estimators": 80,
  "confirm_rsf_estimators": 160,
  "confirm_gbsa_estimators": 160,
  "final_rsf_estimators": 300,
  "final_gbsa_estimators": 300,
  "random_seed": 20260326
}

## Lectura ejecutiva

- La mejor configuracion encontrada pertenece a `cox_only` con objective=0.6793, test Uno mean=0.6886 y valid Uno mean=0.6718.
- Frente al mejor benchmark rolling previo, test Uno pasa de 0.6885 a 0.6886 y valid Uno de 0.6898 a 0.6718.
- Se evaluaron 34 trials en tres fases: cribado, confirmacion y finalistas full-fidelity.

## Baseline rolling

{
  "best_known_variant": "ensemble_all_rank",
  "best_known_label": "Ensemble actual (rank equal)",
  "best_known_test_uno": 0.688482341402764,
  "best_known_valid_uno": 0.689782630523571,
  "best_known_test_dynamic_auc_mean": 0.7229896052396121,
  "best_known_valid_dynamic_auc_mean": 0.7079868968869623
}

## Best trial

{
  "stage": "final",
  "family": "cox_only",
  "params": {
    "alpha": 0.004431207789037498,
    "ties": "breslow"
  },
  "objective": 0.6792500637490694,
  "aggregate": {
    "valid_uno": {
      "count": 4,
      "mean": 0.6717738364544853,
      "std": 0.08012017260196724,
      "min": 0.549637029223801,
      "max": 0.7708395147199419
    },
    "test_uno": {
      "count": 4,
      "mean": 0.6886115522224587,
      "std": 0.05415527810114965,
      "min": 0.6216040876553297,
      "max": 0.7694054330267366
    },
    "valid_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.6763804344418138,
      "std": 0.1226519653943544,
      "min": 0.5010485017466104,
      "max": 0.8250078628328229
    },
    "test_dynamic_auc_mean": {
      "count": 4,
      "mean": 0.7118650667148749,
      "std": 0.0801158793064155,
      "min": 0.6290351264955523,
      "max": 0.8245035103207622
    }
  },
  "fold_results": [
    {
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
          "uno_c_index": 0.7604151470018193
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "uno_c_index": 0.549637029223801
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.7694054330267366
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148334,
          "events": 18521,
          "tau": 134.99999999999997,
          "mean_auc": 0.8002235247843366,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1060,
              "controls": 147274,
              "auc": 0.8032532193234482,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 1999,
              "controls": 146335,
              "auc": 0.7986379854088045,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4064,
              "controls": 144270,
              "auc": 0.7993893094149258,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 510,
          "events": 34,
          "tau": 72.99999999999999,
          "mean_auc": 0.5010485017466104,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 505,
              "auc": 0.4534653465346534,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 7,
              "controls": 503,
              "auc": 0.5631922749218972,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 14,
              "controls": 496,
              "auc": 0.5172811059907835,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.8245035103207622,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.8637873754152824,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.8747292228034026,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.7847712927804462,
              "supported": true
            }
          }
        }
      },
      "fold_id": "fold_1"
    },
    {
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
          "uno_c_index": 0.7600667454780619
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "uno_c_index": 0.7708395147199419
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.6993037423846823
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 148844,
          "events": 18555,
          "tau": 134.99999999999997,
          "mean_auc": 0.7991515877572103,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1065,
              "controls": 147779,
              "auc": 0.801603787434523,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2006,
              "controls": 146838,
              "auc": 0.7978357454095442,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4078,
              "controls": 144766,
              "auc": 0.7984887571552873,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 2112,
          "events": 61,
          "tau": 59.99999999999999,
          "mean_auc": 0.8250078628328229,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 5,
              "controls": 2107,
              "auc": 0.8631229235880399,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 9,
              "controls": 2103,
              "auc": 0.8746235536535109,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 2093,
              "auc": 0.7861040561269395,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.7502605573117477,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.8341708542713568,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.7833052276559865,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.7074035179837228,
              "supported": true
            }
          }
        }
      },
      "fold_id": "fold_2"
    },
    {
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
          "uno_c_index": 0.7602067011025397
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "uno_c_index": 0.7017406440382942
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.6641329458230867
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 150956,
          "events": 18616,
          "tau": 134.99999999999997,
          "mean_auc": 0.7999228292621268,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1070,
              "controls": 149886,
              "auc": 0.8024161540340753,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2015,
              "controls": 148941,
              "auc": 0.798871331851007,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4097,
              "controls": 146859,
              "auc": 0.799118702243646,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 599,
          "events": 20,
          "tau": 45.99999999999999,
          "mean_auc": 0.7488345228283522,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 2,
              "controls": 597,
              "auc": 0.8333333333333333,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 6,
              "controls": 593,
              "auc": 0.7790893760539629,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 13,
              "controls": 586,
              "auc": 0.7074035179837228,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.6290351264955523,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.6251236399604352,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.5914421157684631,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.6584293691338956,
              "supported": true
            }
          }
        }
      },
      "fold_id": "fold_3"
    },
    {
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
          "uno_c_index": 0.7600966043589789
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "uno_c_index": 0.6648781578359043
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "uno_c_index": 0.6216040876553297
        }
      },
      "dynamic_auc": {
        "train": {
          "rows": 151555,
          "events": 18636,
          "tau": 134.99999999999997,
          "mean_auc": 0.7997843858503458,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 1072,
              "controls": 150483,
              "auc": 0.8026212777691653,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 2021,
              "controls": 149534,
              "auc": 0.7987594539703675,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 4110,
              "controls": 147445,
              "auc": 0.7987942050064609,
              "supported": true
            }
          }
        },
        "valid": {
          "rows": 680,
          "events": 23,
          "tau": 33.99999999999999,
          "mean_auc": 0.63063085035947,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 6,
              "controls": 674,
              "auc": 0.6300692383778437,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 12,
              "controls": 668,
              "auc": 0.5919411177644711,
              "supported": true
            },
            "h24": {
              "time": 24.0,
              "cases": 19,
              "controls": 443,
              "auc": 0.6584293691338956,
              "supported": true
            }
          }
        },
        "test": {
          "rows": 51593,
          "events": 228,
          "tau": 17.999999999999996,
          "mean_auc": 0.6436610727314374,
          "horizons": {
            "h6": {
              "time": 6.0,
              "cases": 41,
              "controls": 50816,
              "auc": 0.6508719166615469,
              "supported": true
            },
            "h12": {
              "time": 12.0,
              "cases": 152,
              "controls": 50015,
              "auc": 0.6410401221738742,
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
      "fold_id": "fold_4"
    }
  ],
  "fit_max_rows": null,
  "rsf_n_estimators": 300,
  "gbsa_n_estimators": 300
}

## Final results

[
  {
    "stage": "final",
    "family": "cox_only",
    "params": {
      "alpha": 0.004431207789037498,
      "ties": "breslow"
    },
    "objective": 0.6792500637490694,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6717738364544853,
        "std": 0.08012017260196724,
        "min": 0.549637029223801,
        "max": 0.7708395147199419
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6886115522224587,
        "std": 0.05415527810114965,
        "min": 0.6216040876553297,
        "max": 0.7694054330267366
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6763804344418138,
        "std": 0.1226519653943544,
        "min": 0.5010485017466104,
        "max": 0.8250078628328229
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7118650667148749,
        "std": 0.0801158793064155,
        "min": 0.6290351264955523,
        "max": 0.8245035103207622
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7604151470018193
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.549637029223801
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7694054330267366
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8002235247843366,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8032532193234482,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7986379854088045,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7993893094149258,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5010485017466104,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4534653465346534,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5631922749218972,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5172811059907835,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8245035103207622,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8637873754152824,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8747292228034026,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7847712927804462,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7600667454780619
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7708395147199419
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6993037423846823
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7991515877572103,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.801603787434523,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7978357454095442,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7984887571552873,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8250078628328229,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8631229235880399,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8746235536535109,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7861040561269395,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7502605573117477,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8341708542713568,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7833052276559865,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7074035179837228,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7602067011025397
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7017406440382942
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6641329458230867
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7999228292621268,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8024161540340753,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.798871331851007,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.799118702243646,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7488345228283522,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8333333333333333,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7790893760539629,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7074035179837228,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6290351264955523,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6251236399604352,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5914421157684631,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6584293691338956,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7600966043589789
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6648781578359043
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6216040876553297
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7997843858503458,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8026212777691653,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7987594539703675,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7987942050064609,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.63063085035947,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6300692383778437,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5919411177644711,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6584293691338956,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6436610727314374,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6508719166615469,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6410401221738742,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": null,
    "rsf_n_estimators": 300,
    "gbsa_n_estimators": 300
  },
  {
    "stage": "final",
    "family": "cox_only",
    "params": {
      "alpha": 0.00035772556943475974,
      "ties": "breslow"
    },
    "objective": 0.6792390476227276,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6717593481268276,
        "std": 0.08007820490419329,
        "min": 0.5496990755103307,
        "max": 0.7708065473246959
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6886190676866485,
        "std": 0.054196130747651935,
        "min": 0.621584401964388,
        "max": 0.7694301585731711
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6763865239560526,
        "std": 0.12265934478883928,
        "min": 0.5010485017466104,
        "max": 0.8250322208897777
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7118125753920367,
        "std": 0.08013407829541261,
        "min": 0.6289367939505575,
        "max": 0.8244902753322172
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7604153094094283
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5496990755103307
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7694301585731711
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8002232186482886,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8032528381830197,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7986370606972943,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7993893230595084,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5010485017466104,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4534653465346534,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5631922749218972,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5172811059907835,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8244902753322172,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8637873754152824,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8747292228034026,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7847461463022105,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7600669939318898
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7708065473246959
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6994778067885118
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7991508910065586,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8016031329869019,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7978345911339111,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7984882464462766,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8250322208897777,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8631229235880399,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8746763882284567,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7861292026051752,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7501898745159402,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8341708542713568,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7833052276559865,
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
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7602069278944221
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7016536118363794
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6639839034205232
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.799921916387742,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.802414963097811,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7988701689677677,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7991180457499426,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7488345228283522,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8333333333333333,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7790893760539629,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7074035179837228,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6289367939505575,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6251236399604352,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5914421157684631,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6581917547819889,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7600969462791393
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6648781578359043
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.621584401964388
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7997837650136387,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8026205462936707,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7987587938294755,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7987936588008939,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.63063085035947,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6300692383778437,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5919411177644711,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6584293691338956,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6436333577694318,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.650822959544142,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6410201281720747,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": null,
    "rsf_n_estimators": 300,
    "gbsa_n_estimators": 300
  }
]

## Confirmation results

[
  {
    "stage": "confirm",
    "family": "cox_only",
    "params": {
      "alpha": 0.004431207789037498,
      "ties": "breslow"
    },
    "objective": 0.6781577405296344,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6604733272132718,
        "std": 0.07909646718206759,
        "min": 0.5415710119749333,
        "max": 0.7634630600336267
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6874804725477276,
        "std": 0.046411903016436905,
        "min": 0.6360742028601741,
        "max": 0.7609163287508653
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6704117528512558,
        "std": 0.11592084099710194,
        "min": 0.497982610759031,
        "max": 0.8179247497981836
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7193883859436885,
        "std": 0.06945188804952811,
        "min": 0.6481470689834754,
        "max": 0.8245171584996493
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7546325133959335
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
            "uno_c_index": 0.7609163287508653
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7992952239190972,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8047770155538605,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7985180669058006,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7968347160753377,
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
            "mean_auc": 0.8245171584996493,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8615092548647366,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.85111216780261,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7953831065959213,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7548633695127059
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
            "uno_c_index": 0.6894691035683203
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.799073858417848,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8035474206233665,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7989407793047125,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7968349026729558,
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
            "mean_auc": 0.738449485112843,
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
                "auc": 0.7408656548622822,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7092412706747178,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7530669173754302
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
            "uno_c_index": 0.6634622550115508
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7968008381742471,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8007416820584268,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7964965826643464,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7949136232370636,
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
            "mean_auc": 0.6664398311787858,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6995548961424333,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6191367265469062,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6764880598788167,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7536416151445305
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
            "uno_c_index": 0.6360742028601741
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7978855068554446,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8030751986067549,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7980415019427632,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7951514767476082,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.651658729203763,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6780415430267062,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6022954091816368,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.66793394321017,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6481470689834754,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6523924671315353,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.646603979332516,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 25000,
    "rsf_n_estimators": 160,
    "gbsa_n_estimators": 160
  },
  {
    "stage": "confirm",
    "family": "cox_only",
    "params": {
      "alpha": 0.00035772556943475974,
      "ties": "breslow"
    },
    "objective": 0.6781575069108575,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6604774481376776,
        "std": 0.07910183308518833,
        "min": 0.5415710119749333,
        "max": 0.7634795437312498
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6874789969869873,
        "std": 0.04642462244018934,
        "min": 0.63605181691959,
        "max": 0.7609328124484884
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6704273959606312,
        "std": 0.11594074881372406,
        "min": 0.497982610759031,
        "max": 0.817987322235685
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7193866654602181,
        "std": 0.06945365290278713,
        "min": 0.6481401870495944,
        "max": 0.8245171584996493
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7546346600543692
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
            "uno_c_index": 0.7609328124484884
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7992962146929969,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8047772205369481,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7985188753873982,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7968361931014082,
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
            "mean_auc": 0.8245171584996493,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8615092548647366,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.85111216780261,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7953831065959213,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7548649789959196
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7634795437312498
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6894691035683203
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7990735170486339,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8035460354817991,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7989400544875134,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7968352719418258,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.817987322235685,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8499288087327954,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8514820098272309,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7886187039505117,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.738449485112843,
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
                "auc": 0.7408656548622822,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7092412706747178,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7530686396768169
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
            "uno_c_index": 0.6634622550115508
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7968011411292806,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8007409992965371,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7964967742568572,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7949144833269156,
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
            "mean_auc": 0.6664398311787858,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6995548961424333,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6191367265469062,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6764880598788167,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7536428936404208
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
            "uno_c_index": 0.63605181691959
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7978850027849306,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.803073946419891,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.798040130371837,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7951517506754756,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.651658729203763,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6780415430267062,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6022954091816368,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.66793394321017,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6481401870495944,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6523699084597898,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6466027954771463,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 25000,
    "rsf_n_estimators": 160,
    "gbsa_n_estimators": 160
  },
  {
    "stage": "confirm",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.03230627034485517,
      "cox_ties": "breslow",
      "rsf_min_samples_split": 12,
      "rsf_min_samples_leaf": 40,
      "rsf_max_features": 0.75,
      "rsf_max_depth": 16,
      "gbsa_learning_rate": 0.02,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 2,
      "gbsa_min_samples_split": 30,
      "gbsa_min_samples_leaf": 20,
      "gbsa_dropout_rate": 0.1
    },
    "objective": 0.6630317122747463,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6546769630443647,
        "std": 0.03528776793465349,
        "min": 0.601011354470435,
        "max": 0.6918990868031517
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6612778778001093,
        "std": 0.032747748391864326,
        "min": 0.6078877340724468,
        "max": 0.6932707355242567
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6746513897028992,
        "std": 0.07309626653565478,
        "min": 0.5588431070461322,
        "max": 0.7613794086754118
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6951570251572395,
        "std": 0.048171759812218044,
        "min": 0.6214811048218438,
        "max": 0.7550731856054546
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7687872067968635
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.601011354470435
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6816379850328026
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8313857666257624,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8364128049347629,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8298513386942556,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8295030388873335,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5588431070461322,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.5112871287128713,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5938653791536495,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5828052995391705,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7550731856054546,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.9041290934978643,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7734453426322185,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6731963688485427,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.769961701251695
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6918990868031517
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6623150565709313
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.8332312642778524,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8389093890899832,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8316296547505905,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.8310401019420581,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7613794086754118,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.89359278595159,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7906694140645638,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6835567178816606,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.711238012572864,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7269681742043551,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7408656548622822,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6898135993699134,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7677728164256803
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6458659704090514
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6932707355242567
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8315660818049372,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8372428715605793,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.8303318967060465,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8292088002871247,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6863526616482633,
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
                "auc": 0.715008431703204,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6657915463376215,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6928357976287957,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7181008902077152,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6963572854291418,
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
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.768379801868827
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6799314404948208
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6078877340724468
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8376582462895812,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8444256632945398,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8360801255388777,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.8349023657549243,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6920303814417897,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7420870425321464,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6838822355289422,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6623500059403588,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6214811048218438,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6515028395128095,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6105690003525259,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 25000,
    "rsf_n_estimators": 160,
    "gbsa_n_estimators": 160
  },
  {
    "stage": "confirm",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.02385437968130336,
      "cox_ties": "breslow",
      "rsf_min_samples_split": 12,
      "rsf_min_samples_leaf": 20,
      "rsf_max_features": "sqrt",
      "rsf_max_depth": 8,
      "gbsa_learning_rate": 0.015,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 2,
      "gbsa_min_samples_split": 20,
      "gbsa_min_samples_leaf": 10,
      "gbsa_dropout_rate": 0.05
    },
    "objective": 0.646029259981261,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6635241985627731,
        "std": 0.03392224581660453,
        "min": 0.6144133523608613,
        "max": 0.6974005208848449
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6380578918615075,
        "std": 0.0684507216014141,
        "min": 0.5262228211163006,
        "max": 0.7025113644831955
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6776634027673525,
        "std": 0.06847947902731313,
        "min": 0.5646680976898115,
        "max": 0.7493266762498748
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6753515925609453,
        "std": 0.07655456664241612,
        "min": 0.5457523835518788,
        "max": 0.7445143724187562
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7560481908012061
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.6144133523608613
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6836366333695975
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.8136316495080859,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8213071752279989,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.8122662486127404,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.8103125474149246,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5646680976898115,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.5144554455445545,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5924453280318092,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5925979262672811,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7445143724187562,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8812529663028001,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7466053785597294,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6753086730203435,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7593427371127908
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6974005208848449
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6398607484769364
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.816300577445609,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8245876447850198,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.8150490165863569,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.8126094539186226,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7493266762498748,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.867157095396298,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.781079938711893,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6777101616918549,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7012872484668379,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7696817420435511,
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
                "auc": 0.669729587818325,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7575564077431256
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6496083550913838
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.7025113644831955
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.8145249826190404,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8225388304457182,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.813159629898581,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.8110261551196596,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6984390491393003,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7562814070351759,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7183811129848229,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6705171961144658,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.7098523658063083,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7539564787339268,
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
                "auc": 0.6793394321016989,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7532550589968906
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6926745659140026
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.5262228211163006
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.8120880018616576,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8213880254585211,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.8114030381715568,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.8076267310364151,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6982197879904237,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7413452027695351,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.687624750499002,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6751811809433289,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5457523835518788,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.5591951545892978,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5408662927437559,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 25000,
    "rsf_n_estimators": 160,
    "gbsa_n_estimators": 160
  }
]

## Screening results

[
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.04862727480767296,
      "ties": "efron"
    },
    "objective": 0.5756833449606346,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5781437299659292,
        "std": 0.07402784231722295,
        "min": 0.46221381150338153,
        "max": 0.6440382941688425
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5804787123563895,
        "std": 0.07039239468976624,
        "min": 0.47155374106522235,
        "max": 0.6440382941688425
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5795329631798765,
        "std": 0.13031100961732756,
        "min": 0.3673982241676622,
        "max": 0.7103601764227766
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6130128902805212,
        "std": 0.078352821188482,
        "min": 0.501317932570241,
        "max": 0.7103601764227766
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7060271547293636
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.46221381150338153
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6411540236705898
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7635586828778168,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7690467402436378,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7656317122240349,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7597989175684372,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3673982241676622,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26495049504950496,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.3882419767111616,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.43461981566820274,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6555524779715803,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6939724727100143,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6962540286363397,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6200618603364598,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7055643315102519
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6411540236705898
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6440382941688425
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7621716159732383,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7668354283758385,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7643797027311126,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7587716305253963,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6555524779715803,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6939724727100143,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6962540286363397,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6200618603364598,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7103601764227766,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8634840871021776,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6911186059584036,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6776056707797322,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7052782371362771
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6440382941688425
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5651687905209032
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7621030647032009,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7669441516985931,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7644869186714616,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7585330814730973,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7103601764227766,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8634840871021776,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6911186059584036,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6776056707797322,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5848209741574869,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6186943620178041,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5266966067864272,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6019959605560177,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7051500447359469
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5651687905209032
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47155374106522235
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7619712885220649,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7671387033007447,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7642642466362612,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7582779013065947,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5848209741574869,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6186943620178041,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5266966067864272,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6019959605560177,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.501317932570241,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4970409742274375,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5028724935151033,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.00037732926463270196,
      "ties": "efron"
    },
    "objective": 0.5758442293726027,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.578375069699124,
        "std": 0.07418270679800058,
        "min": 0.4626481355090898,
        "max": 0.6448215839860748
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5806220931559909,
        "std": 0.07069751805892946,
        "min": 0.47163622933655736,
        "max": 0.6448215839860748
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5799721141516364,
        "std": 0.13025035429150364,
        "min": 0.3685360236880106,
        "max": 0.7115891584190566
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6131992229270591,
        "std": 0.07890790272218315,
        "min": 0.5014444587897013,
        "max": 0.7115891584190566
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7063656533510358
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4626481355090898
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416815019945274
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7638203785363761,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7692512781336085,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7658599792259543,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7601051540227778,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3685360236880106,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26653465346534655,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.39023004828173813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4351958525345623,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562602876657337,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6206150828576458,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7059035989764405
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416815019945274
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7624370101836044,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7670456299625437,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7646127900231259,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7590800657369055,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562602876657337,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6206150828576458,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7056187741301598
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5643490573068037
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623700881744986,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7671563222940401,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7647226391025354,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7588425035756012,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835029868337448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5254491017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6005702744445764,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7054903464274437
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5643490573068037
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47163622933655736
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7622392094367938,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7673510512567443,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7645022332185849,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7585879389725015,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835029868337448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5254491017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6005702744445764,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5014444587897013,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4971196895926768,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5030163977122653,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.0002331931289086742,
      "ties": "efron"
    },
    "objective": 0.5758444321773317,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.578375069699124,
        "std": 0.07418270679800058,
        "min": 0.4626481355090898,
        "max": 0.6448215839860748
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5806223762466792,
        "std": 0.07069708165240392,
        "min": 0.47163736169931064,
        "max": 0.6448215839860748
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5799721141516364,
        "std": 0.13025035429150364,
        "min": 0.3685360236880106,
        "max": 0.7115891584190566
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6131993110207205,
        "std": 0.07890777795796883,
        "min": 0.5014448111643467,
        "max": 0.7115891584190566
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7063666016411827
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4626481355090898
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416815019945274
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7638209861954748,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7692514831166961,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7658604817493997,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7601060161898431,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3685360236880106,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26653465346534655,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.39023004828173813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4351958525345623,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562602876657337,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6206150828576458,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.705904549997424
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416815019945274
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7624376308324482,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7670458459937972,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7646133162370174,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7590809372453167,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562602876657337,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6206150828576458,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7056197314648847
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5643490573068037
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623707094246184,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7671565342931657,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7647231755615655,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7588433736375094,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835029868337448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5254491017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6005702744445764,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7054913066913545
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5643490573068037
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47163736169931064
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7622398403836262,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7673512620208699,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7645027825087508,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.758588822637399,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835029868337448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5254491017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6005702744445764,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5014448111643467,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4971206495361553,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5030165292517508,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 1.6535338257428227,
      "ties": "efron"
    },
    "objective": 0.569091843574058,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5682445860945761,
        "std": 0.07519726779679518,
        "min": 0.446888378730533,
        "max": 0.6390774586597041
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5740762917084477,
        "std": 0.06588799665855234,
        "min": 0.47021520118601934,
        "max": 0.6390774586597041
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5708089873538784,
        "std": 0.13266397369381602,
        "min": 0.3495298652100203,
        "max": 0.6990826648987026
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6083627241061305,
        "std": 0.072186311340074,
        "min": 0.49974481221902844,
        "max": 0.6990826648987026
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.6974147801358813
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.446888378730533
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.621769195265882
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7567344528847714,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7636809972478458,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7595054352269244,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7519086468585532,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3495298652100203,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.2502970297029703,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.35927293382561776,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.41762672811059903,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6354131882500739,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6735643094447081,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6710519363871716,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6020821283979179,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6969317846517143
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.621769195265882
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6390774586597041
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7552676075275115,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7613581243175358,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7581448828985333,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7508303891368227,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6354131882500739,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6735643094447081,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6710519363871716,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6020821283979179,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6990826648987026,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8484087102177554,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6750983698707138,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6701233919663955,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.6966086505326264
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6390774586597041
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.565243311722185
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7551430718184909,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7614015873247468,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7581705367604136,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.750552502192261,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6990826648987026,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8484087102177554,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6750983698707138,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6701233919663955,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.599210231056717,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6449060336300693,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5381736526946108,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6100748485208507,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6964826111367561
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.565243311722185
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47021520118601934
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7549832193721687,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7615862618884603,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7578848237394368,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.75027662094134,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.599210231056717,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6449060336300693,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5381736526946108,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6100748485208507,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.49974481221902844,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4962610201511335,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5010110782554706,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.011965725872577831,
      "ties": "efron"
    },
    "objective": 0.5758436899038772,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5783183097922365,
        "std": 0.07422501636929497,
        "min": 0.46239995036297077,
        "max": 0.6447345517841602
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5806220879173823,
        "std": 0.07064824749744299,
        "min": 0.47161506286355376,
        "max": 0.6447345517841602
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5799585425623706,
        "std": 0.13033490691020724,
        "min": 0.36824143058562464,
        "max": 0.7115026794118355
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6132460264935541,
        "std": 0.07884350190683925,
        "min": 0.5013913663103587,
        "max": 0.7115026794118355
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7062839002378434
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.46239995036297077
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6415661161111661
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7637590424877201,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7692043145865196,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7658071134176443,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7600325887211697,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.36824143058562464,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26613861386138615,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.389662027833002,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.43505184331797236,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6561483777792758,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6947318462268628,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6969408781106355,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6205396434229385,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7058216634430847
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6415661161111661
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6447345517841602
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623747771728563,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7669973438004288,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7645588123600976,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7590069149288607,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6561483777792758,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6947318462268628,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6969408781106355,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6205396434229385,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115026794118355,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.692804946599213,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252298,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7055364488251474
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6447345517841602
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5645726209106491
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623074762466048,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7671075593775256,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7646680285728742,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7587691424817586,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115026794118355,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.692804946599213,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252298,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5839416824727462,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6179525222551929,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5259481037924152,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6009266959724368,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7054080780650743
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5645726209106491
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47161506286355376
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7621763313430283,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7673021756759155,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7644470576832171,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7585143761387705,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5839416824727462,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6179525222551929,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5259481037924152,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6009266959724368,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5013913663103587,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.49705153360570126,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.502968780418506,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.4770632302341544,
      "ties": "efron"
    },
    "objective": 0.5740658816829614,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5756748375701171,
        "std": 0.07393303133649765,
        "min": 0.45849103431159643,
        "max": 0.6430809399477807
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5787801978241073,
        "std": 0.06904510887400982,
        "min": 0.4709124753275577,
        "max": 0.6430809399477807
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5775221575271918,
        "std": 0.13051456268427378,
        "min": 0.3629036316892254,
        "max": 0.7069702161052029
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6119488097919547,
        "std": 0.07623935672567403,
        "min": 0.5006102407482763,
        "max": 0.7069702161052029
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7031949364022625
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.45849103431159643
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6348407674809613
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7613451219522902,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7673239054351522,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7636725989331496,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7572177556680961,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3629036316892254,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.260990099009901,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.38028969042885546,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.43073156682027647,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6491873545473743,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6874228761271951,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6885401806942464,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.614328463298715,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7027258102431129
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6348407674809613
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6430809399477807
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7599300421097677,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7650709581656431,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7623838107845113,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7561732506414082,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6491873545473743,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6874228761271951,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6885401806942464,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.614328463298715,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7069702161052029,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8584589614740369,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6860595840359753,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6756366500393804,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7024284913247111
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6430809399477807
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5662866085401297
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7598434805372888,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7651569834819011,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7624636467788475,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7559234491977076,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7069702161052029,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8584589614740369,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6860595840359753,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6756366500393804,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5910274277669648,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6283382789317508,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.531686626746507,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6066294404182012,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7023014060971464
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5662866085401297
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4709124753275577
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7597021643692536,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7653492755813842,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7622196976419707,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7556605931412919,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5910274277669648,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6283382789317508,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.531686626746507,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6066294404182012,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5006102407482763,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.49687682389260923,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5019672387757357,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.0006046665065701741,
      "ties": "efron"
    },
    "objective": 0.5758617935487927,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5783916395372415,
        "std": 0.07417743336072463,
        "min": 0.4626481355090898,
        "max": 0.6448215839860748
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5806384670082473,
        "std": 0.07069176014328903,
        "min": 0.4716354453931128,
        "max": 0.6448215839860748
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5799902375583965,
        "std": 0.13024900328834224,
        "min": 0.3685360236880106,
        "max": 0.7115891584190566
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6132162803187311,
        "std": 0.07889955073586029,
        "min": 0.5014401947293488,
        "max": 0.7115891584190566
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7063641112306589
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4626481355090898
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416732601457159
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7638190758017883,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7692502756381956,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7658589177733706,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7601035874541338,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3685360236880106,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26653465346534655,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.39023004828173813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4351958525345623,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562470526771886,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6205899363794101,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7059020488520764
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416732601457159
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7624356950931083,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7670446165218099,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7646117121333802,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7590784878747381,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562470526771886,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6205899363794101,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.705617224529811
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5644235785080856
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623687736817554,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7671553277687304,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7647215595203878,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7588409180186568,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835887154493303,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5255738522954092,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6006890816205298,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7054887971140755
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5644235785080856
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4716354453931128
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7622378779952103,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.767350037729258,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7645011280202993,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7585863416099978,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835887154493303,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5255738522954092,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6006890816205298,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5014401947293488,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4971105701296308,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5030138984620404,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.05179814692566144,
      "ties": "breslow"
    },
    "objective": 0.5786689746659633,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5818070022089681,
        "std": 0.0749151083850679,
        "min": 0.46581249612210707,
        "max": 0.6510030330003627
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5835984633068599,
        "std": 0.07215470998136339,
        "min": 0.4729783405136746,
        "max": 0.6510030330003627
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5823554068061375,
        "std": 0.13210977123078813,
        "min": 0.36803712455321097,
        "max": 0.7123898256852171
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6161701415375784,
        "std": 0.07993165070585463,
        "min": 0.5032960634789743,
        "max": 0.7123898256852171
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7068878068560311
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.46581249612210707
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6510030330003627
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7648262119755324,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7705753984166595,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7669726071564158,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7608990435966246,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.36803712455321097,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.2633663366336634,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.38256177222380006,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.43865207373271886,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.665842263241626,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7038443284290461,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7038093728535955,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6316543868031282,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.706426563766337
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6510030330003627
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6446475195822454
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7634420496178108,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7683680398661534,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7657070976422263,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7598814367773379,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.665842263241626,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7038443284290461,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7038093728535955,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6316543868031282,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7123898256852171,
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
                "auc": 0.6964586846543002,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6776056707797322,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7061610477647895
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6446475195822454
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5657649601311573
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7633872960788124,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7684809863596022,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.765814556475916,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.759667790951191,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7123898256852171,
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
                "auc": 0.6964586846543002,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6776056707797322,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5831524137444962,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6179525222551929,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5220808383233533,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6017583462041107,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.706026298218775
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5657649601311573
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4729783405136746
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7632462672980075,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7686664487613566,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7655969221935179,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7593969585260834,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5831524137444962,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6179525222551929,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5220808383233533,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6017583462041107,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5032960634789743,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.49778877019721085,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5052978185491721,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.004431207789037498,
      "ties": "breslow"
    },
    "objective": 0.5788860057595003,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.582170414931713,
        "std": 0.07483020872519741,
        "min": 0.4665570515604641,
        "max": 0.6516871064517192
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5838128220501855,
        "std": 0.07230410928365041,
        "min": 0.47312668003435415,
        "max": 0.6516871064517192
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5825979771410865,
        "std": 0.1321270879477877,
        "min": 0.36859744553977314,
        "max": 0.7129477901015235
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6162881769929065,
        "std": 0.08026963754522133,
        "min": 0.5033582449470532,
        "max": 0.7129477901015235
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7072123682839386
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4665570515604641
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6516871064517192
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.765079224341269,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7707754651130314,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7671957754255541,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.761192804638503,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.36859744553977314,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.2637623762376238,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.38398182334564046,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.43908410138248855,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6665199328157226,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7045490569028372,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6324087811501999,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7067518750137931
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6516871064517192
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7636987562564641,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7685736603195095,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7659349686268562,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.760177497246965,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6665199328157226,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7045490569028372,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6324087811501999,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7129477901015235,
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
                "auc": 0.6975829117481731,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6779994749278025,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7064876947118613
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5656159177285938
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7636463624819679,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7686901515556808,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7660455703953117,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.759965235783129,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7129477901015235,
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
                "auc": 0.6975829117481731,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6779994749278025,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5823267401073268,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6164688427299704,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5210828343313374,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6015207318522038,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7063528158699223
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5656159177285938
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47312668003435415
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7635066273640446,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7688763605320221,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7658306352321714,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7596953121783462,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5823267401073268,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6164688427299704,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5210828343313374,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6015207318522038,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5033582449470532,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4976159803710758,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5054454058519287,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.0005447555743249387,
      "ties": "breslow"
    },
    "objective": 0.5788783722092591,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5822054077666515,
        "std": 0.07477108554977202,
        "min": 0.46674319042005336,
        "max": 0.6518024923350806
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5838011930653996,
        "std": 0.07231769498846964,
        "min": 0.47312633161504547,
        "max": 0.6518024923350806
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5826049340263811,
        "std": 0.1320210508724738,
        "min": 0.3688514657529636,
        "max": 0.7128771073057161
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6162326224846321,
        "std": 0.08028668688312933,
        "min": 0.5033622195859673,
        "max": 0.7128771073057161
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7072394494130593
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.46674319042005336
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6518024923350806
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7651018493497094,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7707942050512445,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7672162216345813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.761218414667326,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3688514657529636,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26415841584158417,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.38426583357000854,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4392281105990784,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6666083538952674,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7046547260527289,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6325345135413786,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7067790246357237
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6518024923350806
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6447345517841602
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7637216739575523,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.768592839447129,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7659558406462467,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7602032656079094,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6666083538952674,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7046547260527289,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6325345135413786,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7128771073057161,
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
                "auc": 0.6975829117481731,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6778682068784458,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7065149896324239
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6447345517841602
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5655413965273121
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7636695172055118,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7687096024754514,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7660667388687208,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7599911955385725,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7128771073057161,
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
                "auc": 0.6975829117481731,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6778682068784458,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5820828091515774,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6162215628090999,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5208333333333334,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6012831175002971,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7063800849124358
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5655413965273121
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47312633161504547
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7635299444421737,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7688959770930639,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.765852093947387,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7597213724545232,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5820828091515774,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6162215628090999,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5208333333333334,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6012831175002971,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5033622195859673,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.49762509983412173,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.505447510483697,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.0019499964131241504,
      "ties": "breslow"
    },
    "objective": 0.5788669036028931,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5821714171274307,
        "std": 0.07481420748897463,
        "min": 0.46661909784699385,
        "max": 0.6517035901493423
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5837980078073757,
        "std": 0.07231314114840008,
        "min": 0.4731254605667737,
        "max": 0.6517035901493423
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5826004994554468,
        "std": 0.13202443418386478,
        "min": 0.3688514657529636,
        "max": 0.7129477901015235
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.616227954087316,
        "std": 0.0802944361070718,
        "min": 0.5033612842804406,
        "max": 0.7129477901015235
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7072292850532618
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.46661909784699385
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6517035901493423
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.765093061382334,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7707867167628251,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.76720821886325,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7612086025068372,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3688514657529636,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26415841584158417,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.38426583357000854,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4392281105990784,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6665199328157226,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7045490569028372,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6324087811501999,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7067688249572233
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6517035901493423
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7637127378452344,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7685851067990215,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7659476554740361,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7601933698797492,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6665199328157226,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7045490569028372,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6324087811501999,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7129477901015235,
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
                "auc": 0.6975829117481731,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6779994749278025,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7065047285270215
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5655413965273121
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7636605662411377,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7687019143895155,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7660585453733466,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7599812517364778,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7129477901015235,
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
                "auc": 0.6975829117481731,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6779994749278025,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5820828091515774,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6162215628090999,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5208333333333334,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6012831175002971,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7063698468099475
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5655413965273121
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4731254605667737
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.763520970995893,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7688882780035351,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7658438281230834,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7597114235924005,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5820828091515774,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6162215628090999,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5208333333333334,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6012831175002971,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5033612842804406,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4976270197210788,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5054455373914141,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.011449965396554981,
      "ties": "breslow"
    },
    "objective": 0.5788237302089283,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5820907615888374,
        "std": 0.07485639037729515,
        "min": 0.4664329589874046,
        "max": 0.6516541390564732
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5837607620980049,
        "std": 0.07228795685971989,
        "min": 0.473112961024074,
        "max": 0.6516541390564732
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5825116332535598,
        "std": 0.13212974235669747,
        "min": 0.36848486804228275,
        "max": 0.712790628298495
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6162282436081963,
        "std": 0.08022583225172927,
        "min": 0.5033513094608286,
        "max": 0.712790628298495
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7071637297581725
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4664329589874046
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6516541390564732
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7650404961789422,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7707444646238906,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7671619285913158,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7611478900836086,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.36848486804228275,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.2637623762376238,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.3836978131212724,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4389400921658987,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6664934628386322,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7045490569028372,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6323584881937284,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7067031289213397
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6516541390564732
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6447345517841602
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7636596257035756,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7685422055335961,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7659005746079159,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7601322702798516,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6664934628386322,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7045490569028372,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6323584881937284,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.712790628298495,
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
                "auc": 0.6973018549747049,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6778682068784458,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7064387728872669
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6447345517841602
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5655413965273121
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7636069259433969,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7686581552758913,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7660107771953533,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7599198679132009,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.712790628298495,
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
                "auc": 0.6973018549747049,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6778682068784458,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5822775738348293,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6164688427299704,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5210828343313374,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6014019246762504,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7063039247436701
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5655413965273121
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.473112961024074
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7634670287806284,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7688443336833506,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7657954343358782,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.759649830251356,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5822775738348293,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6164688427299704,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5210828343313374,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6014019246762504,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5033513094608286,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.49761982014498984,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.505434553844373,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.00023079240965345345,
      "ties": "efron"
    },
    "objective": 0.5758444321773317,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.578375069699124,
        "std": 0.07418270679800058,
        "min": 0.4626481355090898,
        "max": 0.6448215839860748
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5806223762466792,
        "std": 0.07069708165240392,
        "min": 0.47163736169931064,
        "max": 0.6448215839860748
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5799721141516364,
        "std": 0.13025035429150364,
        "min": 0.3685360236880106,
        "max": 0.7115891584190566
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6131993110207205,
        "std": 0.07890777795796887,
        "min": 0.5014448111643466,
        "max": 0.7115891584190566
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7063666078276345
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4626481355090898
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416815019945274
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7638209920387455,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7692514863195568,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7658604902957169,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.760106022159348,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3685360236880106,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26653465346534655,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.39023004828173813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4351958525345623,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562602876657337,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6206150828576458,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7059045559845771
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416815019945274
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7624376366328695,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7670458491707275,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7646133247243383,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7590809431739453,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562602876657337,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6206150828576458,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7056197367635496
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5643490573068037
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623707142717211,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7671565374107998,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7647231838916748,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7588433777925329,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835029868337448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5254491017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6005702744445764,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7054913119613971
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5643490573068037
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47163736169931064
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7622398451989993,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7673512651203422,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.764502790781193,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7585888267628187,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835029868337448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5254491017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6005702744445764,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5014448111643466,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.49712064953615526,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5030165292517508,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.0003609773008789247,
      "ties": "efron"
    },
    "objective": 0.5758441864113713,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.578375069699124,
        "std": 0.07418270679800058,
        "min": 0.4626481355090898,
        "max": 0.6448215839860748
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5806220496035773,
        "std": 0.07069758519845765,
        "min": 0.47163605512690304,
        "max": 0.6448215839860748
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5799721141516364,
        "std": 0.13025035429150364,
        "min": 0.3685360236880106,
        "max": 0.7115891584190566
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6131991505716995,
        "std": 0.07890800519682095,
        "min": 0.5014441693682629,
        "max": 0.7115891584190566
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7063657383049395
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4626481355090898
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416815019945274
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7638204315735982,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.769251271727887,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7658600322131204,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7601052375958465,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3685360236880106,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26653465346534655,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.39023004828173813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4351958525345623,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562602876657337,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6206150828576458,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7059036840161946
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416815019945274
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7624370694301749,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7670456299625437,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7646128528292999,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7590801538193883,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562602876657337,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6206150828576458,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7056188603479568
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5643490573068037
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623701480009187,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7671563222940401,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7647227007453432,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7588425933241075,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835029868337448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5254491017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6005702744445764,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7054904331943994
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5643490573068037
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47163605512690304
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7622392713048014,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7673510512567443,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7645022977436344,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7585880313819027,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5835029868337448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6174579624134521,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5254491017964071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6005702744445764,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5014441693682629,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4971196895926767,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5030160030938087,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.0022134084023557325,
      "ties": "efron"
    },
    "objective": 0.575862812526129,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5783740675034061,
        "std": 0.07419988031768278,
        "min": 0.46258608922256,
        "max": 0.6448215839860748
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5806354048405318,
        "std": 0.07069152581364853,
        "min": 0.4716314385710627,
        "max": 0.6448215839860748
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5800073533530142,
        "std": 0.13026623424566341,
        "min": 0.3684954507988152,
        "max": 0.7115891584190566
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6132435393356477,
        "std": 0.07888932816863548,
        "min": 0.5014401947293486,
        "max": 0.7115891584190566
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7063528263325167
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.46258608922256
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416650182969044
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7638109649354676,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7692442254342503,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7658517645059588,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7600939833735303,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3684954507988152,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26653465346534655,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.38994603805737005,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4351958525345623,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562470526771886,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6205899363794101,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7058907594950455
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416650182969044
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7624275100563648,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7670384564541513,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7646044724487103,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7590688326795119,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562470526771886,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6205899363794101,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7056058897569465
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5644235785080856
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623605255970836,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7671491267943076,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7647142223602355,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7588312044048606,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5836977515169967,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6177052423343224,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.525698602794411,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6006890816205298,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7054774797372764
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5644235785080856
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4716314385710627
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7622296130830133,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7673438542817501,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7644937192210136,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.758576619645958,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5836977515169967,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6177052423343224,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.525698602794411,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6006890816205298,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5014401947293486,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4971105701296308,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5030138984620403,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.00035772556943475974,
      "ties": "breslow"
    },
    "objective": 0.5788839667152365,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.582220919338284,
        "std": 0.07474713342468368,
        "min": 0.46680523670658314,
        "max": 0.6518024923350806
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5838031311478042,
        "std": 0.07231472896796745,
        "min": 0.47313408394466405,
        "max": 0.6518024923350806
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5826049340263811,
        "std": 0.1320210508724738,
        "min": 0.3688514657529636,
        "max": 0.7128771073057161
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6162327671953512,
        "std": 0.08028648344284434,
        "min": 0.503362798428844,
        "max": 0.7128771073057161
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7072407148312468
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.46680523670658314
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6518024923350806
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7651028910439609,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7707949417092156,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7672171172886133,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7612196793495791,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3688514657529636,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26415841584158417,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.38426583357000854,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4392281105990784,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6666083538952674,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7046547260527289,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6325345135413786,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.706780286623591
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6518024923350806
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6447345517841602
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.763722715656785,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7685935764949354,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7659567403022548,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7602045284058113,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6666083538952674,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7043189368770764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7046547260527289,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6325345135413786,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7128771073057161,
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
                "auc": 0.6975829117481731,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6778682068784458,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7065162507503386
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6447345517841602
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5655413965273121
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7636705385122996,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7687103008255121,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.766067635188467,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7599924395525901,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7128771073057161,
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
                "auc": 0.6975829117481731,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6778682068784458,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5820828091515774,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6162215628090999,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5208333333333334,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6012831175002971,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7063813463108709
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5655413965273121
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47313408394466405
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7635309742031413,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7688966775738342,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.765853007225012,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7597226241068569,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5820828091515774,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6162215628090999,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5208333333333334,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6012831175002971,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.503362798428844,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.49762509983412173,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5054482997206101,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.08497179229724826,
      "ties": "breslow"
    },
    "objective": 0.578336767614726,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5814752953801716,
        "std": 0.07481822016700522,
        "min": 0.4656884035490476,
        "max": 0.6505085220716711
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5832774841965965,
        "std": 0.07204283475443832,
        "min": 0.4728971588147472,
        "max": 0.6505085220716711
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5819349271452852,
        "std": 0.1318429923139605,
        "min": 0.3678956818375108,
        "max": 0.7114062227706885
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.615773341048295,
        "std": 0.07957507298324414,
        "min": 0.50324933744955,
        "max": 0.7114062227706885
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7066609674245492
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4656884035490476
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6505085220716711
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7646494520826908,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7704330728937795,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.766815707030062,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7606955772859179,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3678956818375108,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.262970297029703,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.38256177222380006,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.43865207373271886,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6653213016099353,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7033697199810156,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7031225233792994,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6311766037166494,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7061992156270792
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6505085220716711
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6443864229765013
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7632623857557111,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7682216691610334,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7655465039523688,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7596759996313274,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6653213016099353,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7033697199810156,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7031225233792994,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6311766037166494,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7114062227706885,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8634840871021776,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6958965711073637,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6768180624835916,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7059328900466635
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6443864229765013
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5653178329234667
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.763206334900317,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7683328831469549,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7656519794013728,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7594615987440249,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7114062227706885,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8634840871021776,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6958965711073637,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6768180624835916,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5831165023630062,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6177052423343224,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5222055888223553,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6017583462041107,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7057982836083951
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5653178329234667
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4728971588147472
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7630647199003672,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7685183280731567,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7654328234109481,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7591903311053592,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5831165023630062,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6177052423343224,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5222055888223553,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6017583462041107,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.50324933744955,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4978118088406954,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5052257349111057,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.03973111794259305,
      "ties": "efron"
    },
    "objective": 0.5756570086650371,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5781012390564134,
        "std": 0.0741249421641637,
        "min": 0.462089718930322,
        "max": 0.6441253263707571
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5804696399728858,
        "std": 0.0704401266208975,
        "min": 0.47156332259621164,
        "max": 0.6441253263707571
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5795403103385642,
        "std": 0.1302902332099117,
        "min": 0.36755137455434805,
        "max": 0.710517338225805
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6129908480187652,
        "std": 0.07842239804230385,
        "min": 0.5013535252751522,
        "max": 0.710517338225805
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7060891107726208
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.462089718930322
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6412446840075166
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7636074720597357,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.769084604463353,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7656743942408899,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7598560917808309,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.36755137455434805,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26495049504950496,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.3888099971598978,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.43476382488479265,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6555879590969447,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6939724727100142,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6963596977862313,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6200870068146955,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7056264361863257
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6412446840075166
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6441253263707571
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7622210245943569,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7668742059858639,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7644232240148756,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7588291771828399,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6555879590969447,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.6939724727100142,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6963596977862313,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6200870068146955,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.710517338225805,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8634840871021776,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6913996627318718,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.677736938829089,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7053404818763117
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6441253263707571
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.564945226917058
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7621527449336815,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7669834214189699,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7645308933177414,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7585907016761428,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.710517338225805,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8634840871021776,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6913996627318718,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.677736938829089,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5845045694771591,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6181998021760633,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5264471057884232,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6017583462041107,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7052122547741155
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.564945226917058
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.47156332259621164
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7620211403558548,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.767178029407001,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7643085786543181,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.758335662132748,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5845045694771591,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6181998021760633,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5264471057884232,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6017583462041107,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5013535252751522,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4970452939730909,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5029194531114349,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.07433222049809093,
      "ties": "breslow"
    },
    "objective": 0.5785794993308052,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.581676127749698,
        "std": 0.07498481826897149,
        "min": 0.4655643109759881,
        "max": 0.6506156661062209
      },
      "test_uno": {
        "count": 4,
        "mean": 0.583515872571426,
        "std": 0.07215015403002405,
        "min": 0.4729232902628998,
        "max": 0.6506156661062209
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5822348115156769,
        "std": 0.13224839638923638,
        "min": 0.36767052684253004,
        "max": 0.7125469874882456
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.616135563300179,
        "std": 0.07993522470813874,
        "min": 0.5032735339805388,
        "max": 0.7125469874882456
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7067336258759189
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4655643109759881
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6506156661062209
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7647065553836159,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7704784830534075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7668666858115565,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7607614678282573,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.36767052684253004,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.262970297029703,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.3819937517750639,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.43836405529953915,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6655327556443476,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7035595633602277,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7033866962540287,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6313777755425352,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7062720923685526
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6506156661062209
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6449086161879896
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7633203638389994,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7682683001425139,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7655985940352441,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.759742484119931,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6655327556443476,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7035595633602277,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7033866962540287,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6313777755425352,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7125469874882456,
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
                "auc": 0.6967397414277684,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.677736938829089,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7060059852028572
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6449086161879896
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5656159177285938
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7632648127737574,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.76838022130464,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7657048006235854,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7595283691396882,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7125469874882456,
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
                "auc": 0.6967397414277684,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.677736938829089,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5831889760875845,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6179525222551929,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5222055888223553,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6017583462041107,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7058713298790561
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5656159177285938
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4729232902628998
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.763123383880124,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7685656508182954,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7654861029025505,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7592572610893138,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5831889760875845,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6179525222551929,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5222055888223553,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6017583462041107,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5032735339805388,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4978247680776556,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.505254015900493,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "cox_only",
    "params": {
      "alpha": 0.0014086864661637727,
      "ties": "efron"
    },
    "objective": 0.5758825900444161,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5783947582659296,
        "std": 0.07419814168838572,
        "min": 0.46258608922256,
        "max": 0.6448215839860748
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5806562915889163,
        "std": 0.0706887367312363,
        "min": 0.4716322225145073,
        "max": 0.6448215839860748
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5800297881434375,
        "std": 0.1302501139890657,
        "min": 0.3685360236880106,
        "max": 0.7115891584190566
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6132564726998557,
        "std": 0.07888381772949374,
        "min": 0.5014427619136836,
        "max": 0.7115891584190566
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.7063584894236886
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.46258608922256
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416732601457159
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.763814765609855,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7692468197514528,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7658550155249833,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7600986532319377,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3685360236880106,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.26653465346534655,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.39023004828173813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4351958525345623,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562470526771886,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6205899363794101,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.7058964177339793
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.6416732601457159
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7624313773523284,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.767041163198682,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7646077960835482,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7590735433984459,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6562470526771886,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.694921689606075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6970465472605273,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6205899363794101,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.7056115486981096
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6448215839860748
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5644980997093673
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7623643859729672,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7671517767833771,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7647175810602507,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7588359145394313,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7115891584190566,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.864321608040201,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.6930860033726813,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6785245471252297,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5837469177894941,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6177052423343224,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.525698602794411,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6008078887964833,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.7054831262420344
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5644980997093673
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4716322225145073
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7622334707473741,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7673464640375405,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7644971076133623,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7585813308752434,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5837469177894941,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6177052423343224,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.525698602794411,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6008078887964833,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.5014427619136836,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4971144099035449,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.5030160030938087,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.004277020518110843,
      "cox_ties": "efron",
      "rsf_min_samples_split": 12,
      "rsf_min_samples_leaf": 40,
      "rsf_max_features": 0.75,
      "rsf_max_depth": 12,
      "gbsa_learning_rate": 0.05,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 1,
      "gbsa_min_samples_split": 20,
      "gbsa_min_samples_leaf": 5,
      "gbsa_dropout_rate": 0.05
    },
    "objective": 0.5064706927859208,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5157289490346161,
        "std": 0.03847718596781761,
        "min": 0.46823324630113144,
        "max": 0.5657649601311573
      },
      "test_uno": {
        "count": 4,
        "mean": 0.4929234829849597,
        "std": 0.057308422853937654,
        "min": 0.4108860564334754,
        "max": 0.553841567926075
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5449541792372528,
        "std": 0.09188853627586754,
        "min": 0.40775260005678143,
        "max": 0.6461478483089983
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5501122257328857,
        "std": 0.08108056393863707,
        "min": 0.4345220120057155,
        "max": 0.6462149263206369
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.6408806754511285
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.49038282558788854
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5386460290772426
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7512684908426177,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7649917327758476,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7515845444504464,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.744080398451831,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.40775260005678143,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.35445544554455455,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.4419199091167283,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4360599078341013,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6462149263206369,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.848220218319886,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6167908279177894,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5569819196821486,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6405517648849262
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.538534764118287
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.46832027850304614
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7503095843027375,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7636060470578974,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7507648484965023,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7432684952870147,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6461478483089983,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8481252966302801,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6166851587678976,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5569441999647949,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5179661073893282,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6700167504187604,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4536256323777403,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5112890522446837,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.6396534527167859
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.46823324630113144
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.553841567926075
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7495777820228929,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7636700403209866,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7499228706862342,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7421787305503581,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5178954245935208,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6700167504187604,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4536256323777403,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5111577841953269,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.601745857215862,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6973293768545994,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5858283433133733,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5453249376262327,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6373579263319263
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5657649601311573
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4108860564334754
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7459295798174279,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7612190890853838,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7462039301155461,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7379589180806336,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6080208439897107,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7000494559841741,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5924401197604791,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5538790542948795,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.4345220120057155,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.46001955404865763,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.4252543315952583,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.0003476866532186573,
      "cox_ties": "efron",
      "rsf_min_samples_split": 32,
      "rsf_min_samples_leaf": 40,
      "rsf_max_features": 0.75,
      "rsf_max_depth": 12,
      "gbsa_learning_rate": 0.08,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 2,
      "gbsa_min_samples_split": 12,
      "gbsa_min_samples_leaf": 5,
      "gbsa_dropout_rate": 0.0
    },
    "objective": 0.4269773005172099,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.4244181814859218,
        "std": 0.024861825286884767,
        "min": 0.38429680545940065,
        "max": 0.4496953872932985
      },
      "test_uno": {
        "count": 4,
        "mean": 0.4080855064331824,
        "std": 0.03832038736951084,
        "min": 0.35779731926183883,
        "max": 0.4496953872932985
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.4755835644557255,
        "std": 0.0704240525485741,
        "min": 0.3702191089574119,
        "max": 0.5543395478153832
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.4778384227957855,
        "std": 0.0672928140696651,
        "min": 0.378350090517034,
        "max": 0.554326312826838
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.6106643308305858
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.42430353043370356
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.3843544984010813
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7355404150931794,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7492063247019226,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7376797241344559,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7275526788340867,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3702191089574119,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.3556435643564357,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.43226356148821354,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.3629032258064516,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.554326312826838,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7765543426672995,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.5543403603318011,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.4432066789046194,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6102675178450501
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.38429680545940065
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.4496953872932985
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7344579676300256,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7477825869088174,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7368159112469046,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7265383033079233,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.5543395478153832,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7765543426672994,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.5543403603318011,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.4432318253828551,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5217458618567979,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6582914572864321,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4775154581225408,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5080073510107639,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.6088849869343402
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.4496953872932985
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.4404948207765109
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7332503328136075,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7474965147967284,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7356565458006146,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7248366507796686,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5219030236598265,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6582914572864321,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.47779651489600905,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5081386190601207,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.4569314259824719,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.4940652818991098,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.44797904191616766,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.4369727931567067,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6073285480004271
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.4393770027572845
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.35779731926183883
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7320713874487571,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.746728516143193,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7343794599838375,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7235013526013534,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.4558725773902806,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.4920870425321464,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.44785429141716565,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.4359035285731258,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.378350090517034,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.384771504653806,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.3760160767559206,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.013520326230746641,
      "cox_ties": "breslow",
      "rsf_min_samples_split": 16,
      "rsf_min_samples_leaf": 5,
      "rsf_max_features": 0.75,
      "rsf_max_depth": 8,
      "gbsa_learning_rate": 0.05,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 2,
      "gbsa_min_samples_split": 12,
      "gbsa_min_samples_leaf": 30,
      "gbsa_dropout_rate": 0.1
    },
    "objective": 0.5143682579350031,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5194102314052211,
        "std": 0.02539151041982498,
        "min": 0.4955613577023499,
        "max": 0.5563752887696549
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5006795621944097,
        "std": 0.04226478375764541,
        "min": 0.4340523691641943,
        "max": 0.5436321633504733
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5582388627913786,
        "std": 0.060513022413313085,
        "min": 0.48261384901244414,
        "max": 0.6454956384812994
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5490929908718594,
        "std": 0.07074416405516396,
        "min": 0.4505734711257452,
        "max": 0.645459536020888
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.661014410259541
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.49615313023515545
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5295593907625359
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7629314800290898,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7779346467795492,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7649465471451686,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7543138021707438,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.48261384901244414,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.46534653465346537,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5410394774211871,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.47825460829493094,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.645459536020888,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8390128144280968,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6192740529402441,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5591570900495386,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6606758587243071
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5295511489137243
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.4954743255004352
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7621648875591228,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7769235859650467,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.764337736324526,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7535921730366552,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6454956384812994,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8391077361177028,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.61932688751519,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5591570900495386,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5275418120657946,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6641541038525963,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4564362001124227,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5291415069572066,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.6598179982238601
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.4955613577023499
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5436321633504733
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7614710046745243,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7769812440632451,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7635779638157718,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7525435154649134,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5274553330585736,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6641541038525963,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.45615514333895446,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5291415069572066,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5727971442750096,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6337784371909001,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.560503992015968,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5383153142449804,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6574576728019578
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5563752887696549
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4340523691641943
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7571502094787615,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7732938402275022,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7589847475158302,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.748032474313693,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5773906306131973,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6330365974282888,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5683632734530938,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5443744802186052,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.4505734711257452,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.45985996344535235,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.4471980774188796,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.02385437968130336,
      "cox_ties": "breslow",
      "rsf_min_samples_split": 12,
      "rsf_min_samples_leaf": 20,
      "rsf_max_features": "sqrt",
      "rsf_max_depth": 8,
      "gbsa_learning_rate": 0.015,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 2,
      "gbsa_min_samples_split": 20,
      "gbsa_min_samples_leaf": 10,
      "gbsa_dropout_rate": 0.05
    },
    "objective": 0.5158154199531223,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5264529700213898,
        "std": 0.045109496072940895,
        "min": 0.4736923745113855,
        "max": 0.577576570534317
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5013896072201565,
        "std": 0.07821046850091423,
        "min": 0.3779520696977985,
        "max": 0.5730680378567703
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.562557518735215,
        "std": 0.1136661811219307,
        "min": 0.3811252017176238,
        "max": 0.6678754597105279
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5682539605949153,
        "std": 0.1018282220595304,
        "min": 0.4087686525695295,
        "max": 0.6678769502956166
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.6376219485670191
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4736923745113855
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5643729601424191
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7380830490673812,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7525983111699641,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7391188948764197,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7301610940826719,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.3811252017176238,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.31683168316831684,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.3873899460380573,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.42525921658986177,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6678769502956166,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.833032747982914,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6468537010619749,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5937083511454221,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6372668574966069
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5642905416543039
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.49016536118363796
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7370066175758532,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7509969445238412,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.738122505432123,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7293088624251016,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6678754597105279,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8331276696725202,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6468537010619749,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5936580581889507,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5516883720174478,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7453936348408711,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.48510399100618323,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5343922289314781,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.6366053362753087
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.49025239338555265
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5730680378567703
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7366529728726602,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7512974440013662,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7376840060721164,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.728658779557962,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5517590548132554,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7453936348408711,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.48510399100618323,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5345234969808349,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6446818674970671,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.776706231454006,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6032934131736527,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5804918617084471,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6276565435530772
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.577576570534317
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.3779520696977985
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7266716844388016,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7424717688892513,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7274468142020786,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7182115175282069,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6494703586994526,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7818991097922849,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6094061876247505,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5840560769870501,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.4087686525695295,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.43974194799410216,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.39751068100622444,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.00025139640016239647,
      "cox_ties": "efron",
      "rsf_min_samples_split": 8,
      "rsf_min_samples_leaf": 20,
      "rsf_max_features": "sqrt",
      "rsf_max_depth": 16,
      "gbsa_learning_rate": 0.02,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 2,
      "gbsa_min_samples_split": 12,
      "gbsa_min_samples_leaf": 10,
      "gbsa_dropout_rate": 0.0
    },
    "objective": 0.505914733752553,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.505901188205814,
        "std": 0.03178152836851731,
        "min": 0.4787801700068251,
        "max": 0.5601013488337432
      },
      "test_uno": {
        "count": 4,
        "mean": 0.48765567373246255,
        "std": 0.047641453330172154,
        "min": 0.4159997195224565,
        "max": 0.5501155078619867
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5611917306063744,
        "std": 0.07487671492361082,
        "min": 0.450367413890198,
        "max": 0.6501689655210752
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5557035396798229,
        "std": 0.08219530402405209,
        "min": 0.4302404060183798,
        "max": 0.650211685475759
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.6625147860652687
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4787801700068251
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.492862558929219
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7701931029090485,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7827983669766096,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7701054767654439,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7637624496583124,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.450367413890198,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.39603960396039606,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.48253337120136325,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.47998271889400923,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.650211685475759,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8540104413858567,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6678290273154752,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5412653707848216,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6621315135438647
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.4928172287607556
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.491644908616188
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7693039607868353,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.781517722489238,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7693368514704052,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7630111971061896,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6501689655210752,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8539155196962506,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6677761927405294,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5412527975457038,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5405838209322231,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6608040201005024,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4876335019673974,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5364925177211867,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.6611031286751591
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.4919060052219321
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5501155078619867
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7686478607758003,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7816620662856418,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7687834023841073,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7618979632179808,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5405838209322232,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6608040201005025,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4876335019673974,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5364925177211867,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6017782462929294,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7272502472799209,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.565244510978044,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.538790542948794,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6599930199576313
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5601013488337432
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.4159997195224565
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7652516554088343,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7786189508340359,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7652413709708101,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7583967100933096,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6036467220820012,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7257665677546983,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5682385229540918,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5422359510514435,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.4302404060183798,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4435286850310254,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.42541046896457374,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.1320337030223455,
      "cox_ties": "breslow",
      "rsf_min_samples_split": 8,
      "rsf_min_samples_leaf": 5,
      "rsf_max_features": 0.5,
      "rsf_max_depth": 8,
      "gbsa_learning_rate": 0.05,
      "gbsa_subsample": 0.8,
      "gbsa_max_depth": 1,
      "gbsa_min_samples_split": 12,
      "gbsa_min_samples_leaf": 20,
      "gbsa_dropout_rate": 0.0
    },
    "objective": 0.5156324047457332,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5191824530006905,
        "std": 0.01847158057943139,
        "min": 0.4903207793013588,
        "max": 0.5416946121171473
      },
      "test_uno": {
        "count": 4,
        "mean": 0.4937227876829894,
        "std": 0.05520108920055273,
        "min": 0.3983562012539611,
        "max": 0.5317087711453908
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5805060853499576,
        "std": 0.07328124567385645,
        "min": 0.4645032090583103,
        "max": 0.6635614896409899
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5666379985906578,
        "std": 0.09332980468921641,
        "min": 0.41459430547843973,
        "max": 0.6635614896409899
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.6672627195356546
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4903207793013588
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5239384498730755
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7679091677727494,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7811771973738592,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7699688279920874,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7601618881973815,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.4645032090583103,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.43287128712871287,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5211587617154217,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.47091013824884786,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6635614896409899,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8364499288087328,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6554657367781476,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5803555712022532,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6669142973165887
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.523913724326641
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.52088772845953
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7670845730444548,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7800487893878586,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7692966249645892,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7594164112381947,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6635614896409899,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8364499288087328,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6554657367781476,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5803555712022532,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6143381555183877,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8056951423785594,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.5820685778527263,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.578104489367288,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.666013787586868
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.5208006962576153
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5317087711453908
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7664576895244473,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7800962469794801,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7686665676050084,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7584458517420192,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6140521443402788,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8048576214405361,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.581787521079258,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5779732213179313,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5740580437248137,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6649357072205737,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5425399201596806,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5320185339194488,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6640666909735615
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5416946121171473
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.3983562012539611
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7635301913723239,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7776440737690309,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7654742054760961,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7554043171196914,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5799074983602518,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6708704253214639,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5553892215568862,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5328501841511227,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.41459430547843973,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.42700949768077656,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.41008171232840673,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.42113714589407525,
      "cox_ties": "efron",
      "rsf_min_samples_split": 8,
      "rsf_min_samples_leaf": 20,
      "rsf_max_features": "sqrt",
      "rsf_max_depth": 12,
      "gbsa_learning_rate": 0.02,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 2,
      "gbsa_min_samples_split": 8,
      "gbsa_min_samples_leaf": 20,
      "gbsa_dropout_rate": 0.1
    },
    "objective": 0.5155156764353158,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5301919769593575,
        "std": 0.03466949977536888,
        "min": 0.4840731070496084,
        "max": 0.5637094913130913
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5004681250812493,
        "std": 0.07015554009503487,
        "min": 0.3923453584450743,
        "max": 0.56383723996967
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5574226221075693,
        "std": 0.10423342221254808,
        "min": 0.39918503440570663,
        "max": 0.6699727248777971
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5612499264516734,
        "std": 0.09554800276888982,
        "min": 0.4199358290019551,
        "max": 0.6699877611189541
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.642050214501483
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5093069429794627
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.56383723996967
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.751150320338399,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7645571494129413,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.751466451440775,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7441246128690792,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.39918503440570663,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.33227722772277235,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.4106787844362397,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4436923963133641,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6699877611189541,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8288561936402468,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6433666191155492,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6012020016596675,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6417217704617217
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5637094913130913
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.48424717145343776
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7500677004674117,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7629205131746183,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7504863879873204,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7432712571810176,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6699727248777971,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8289036544850499,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6433930364030221,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6011391354640783,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5317478511502896,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7093802345058626,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4716132658797077,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.515358361774744,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.6410205691301933
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.4840731070496084
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5614427304568149
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7497741172925436,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7632666870435239,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7501120741217112,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.742686500175775,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5317478511502896,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7093802345058626,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4716132658797077,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.515358361774744,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6233282645354948,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.76162215628091,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5767215568862275,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5583937269811097,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6318169296131912
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5636783664952679
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.3923453584450743
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7392569001712201,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7540979705795101,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.739431326310674,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.731561755181259,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6287848779964841,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7678041543026706,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5839570858283434,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.562076749435666,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.4199358290019551,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4385561778122504,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.41316782596799906,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  },
  {
    "stage": "screen",
    "family": "ensemble_all_rank",
    "params": {
      "cox_alpha": 0.03230627034485517,
      "cox_ties": "breslow",
      "rsf_min_samples_split": 12,
      "rsf_min_samples_leaf": 40,
      "rsf_max_features": 0.75,
      "rsf_max_depth": 16,
      "gbsa_learning_rate": 0.02,
      "gbsa_subsample": 1.0,
      "gbsa_max_depth": 2,
      "gbsa_min_samples_split": 30,
      "gbsa_min_samples_leaf": 20,
      "gbsa_dropout_rate": 0.1
    },
    "objective": 0.5212388772960291,
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5320060043431902,
        "std": 0.04764002577965973,
        "min": 0.4802692808835391,
        "max": 0.5846188240554437
      },
      "test_uno": {
        "count": 4,
        "mean": 0.50783139735678,
        "std": 0.07742749990250168,
        "min": 0.38897827779819905,
        "max": 0.5791042551605932
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5758018610754517,
        "std": 0.09061225319435064,
        "min": 0.4370279308382428,
        "max": 0.6666766849026593
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5673327146034458,
        "std": 0.09980844397871723,
        "min": 0.41004697724572825,
        "max": 0.6666781754877479
      }
    },
    "fold_results": [
      {
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
            "uno_c_index": 0.6309997783192576
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.4802692808835391
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5742961461114957
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7490444160889155,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.7637656264372839,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.749341322521718,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7413527559873794,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.4370279308382428,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4063366336633663,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.45867651235444473,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.45276497695852536,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6666781754877479,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8286663502610346,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6226026311618323,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6033143058314683,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_1"
      },
      {
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
            "uno_c_index": 0.6306607630733729
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5741890020769459
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.488946910356832
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7481156042134989,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7624555376704976,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7485259424874426,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.740558578418381,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6666766849026593,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8287612719506406,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6226026311618323,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.6032640128749969,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5541125674392007,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7763819095477387,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4761101742551996,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.5351798372276189,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_2"
      },
      {
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
            "uno_c_index": 0.6298967433950685
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.488946910356832
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5791042551605932
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7476093005870664,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7625885174290092,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7478559057050302,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7397991162175397,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.5540418846433931,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.7763819095477387,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.4761101742551996,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.535048569178262,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6384931382411065,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7569238377843719,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6022954091816368,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5802542473565403,
                "supported": true
              }
            }
          }
        },
        "fold_id": "fold_3"
      },
      {
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
            "uno_c_index": 0.6209804491716537
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5846188240554437
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.38897827779819905
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7371849770172458,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7535465093443887,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7372269206422033,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7287697701456414,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6454609439175115,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7685459940652819,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6084081836327345,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.5845313056908638,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.41004697724572825,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.4160810211494747,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.407853762292365,
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
        "fold_id": "fold_4"
      }
    ],
    "fit_max_rows": 12000,
    "rsf_n_estimators": 80,
    "gbsa_n_estimators": 80
  }
]

