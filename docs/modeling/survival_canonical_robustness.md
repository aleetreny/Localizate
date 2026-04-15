# Survival Canonical Robustness

Chequeo post-entrenamiento sobre los scores ya exportados para añadir intervalos de confianza y alertas de soporte estadístico sin relanzar el fit.

- Estado global: pass_with_caveats
- Filas evaluadas: 203828
- Split counts: {"train": 149213, "test": 51873, "valid": 2742}
- Split events: {"test": 266, "train": 14918, "valid": 52}
- Bootstrap config: {"iterations": 200, "max_rows": 10000, "random_seed": 20260325}

## Lectura ejecutiva

- El chequeo robusto reutiliza los scores del último run y añade intervalos bootstrap sin relanzar el entrenamiento.
- Uno valid=0.6863 con CI bootstrap [0.6266, 0.7524]; test=0.6421 con CI [0.5684, 0.7214].
- Dynamic AUC mean valid=0.7398 con CI [0.6323, 0.8049]; test=0.8774 con CI [0.6701, 0.9529].
- Los horizontes más extremos siguen siendo frágiles: el soporte de casos/controles en h6 valid y h24 test no alcanza un nivel cómodo para venderlos como KPI principal.

## Uno / IPCW C-index

{
  "train": {
    "rows": 149213,
    "events": 14918,
    "tau": 134.99999999999997,
    "uno_c_index": 0.7494211280390881
  },
  "valid": {
    "rows": 2742,
    "events": 52,
    "tau": 54.99999999999999,
    "uno_c_index": 0.6863294041888188
  },
  "test": {
    "rows": 51873,
    "events": 266,
    "tau": 25.999999999999996,
    "uno_c_index": 0.6421461652383815
  }
}

## Bootstrap Uno / IPCW C-index

{
  "valid": {
    "estimate": 0.6918534081575232,
    "ci_lower": 0.6266304435796752,
    "ci_upper": 0.752431249452833,
    "ci_width": 0.12580080587315778,
    "iterations_requested": 200,
    "iterations_successful": 200,
    "success_rate": 1.0,
    "sample_rows": 2742,
    "skipped_iterations": 0
  },
  "test": {
    "estimate": 0.6434994245874865,
    "ci_lower": 0.5683767649650666,
    "ci_upper": 0.721366237360139,
    "ci_width": 0.15298947239507243,
    "iterations_requested": 200,
    "iterations_successful": 200,
    "success_rate": 1.0,
    "sample_rows": 10000,
    "skipped_iterations": 0
  }
}

## Dynamic AUC

{
  "train": {
    "rows": 149213,
    "events": 14918,
    "tau": 134.99999999999997,
    "mean_auc": 0.8016273202664479,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 819,
        "controls": 148394,
        "auc": 0.8095269732296835,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 1492,
        "controls": 147721,
        "auc": 0.799867624158454,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 2934,
        "controls": 146279,
        "auc": 0.7979618970374533,
        "supported": true
      }
    }
  },
  "valid": {
    "rows": 2742,
    "events": 52,
    "tau": 54.99999999999999,
    "mean_auc": 0.7397548452953936,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 5,
        "controls": 2737,
        "auc": 0.8531238582389478,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 16,
        "controls": 2726,
        "auc": 0.7473174981658107,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 28,
        "controls": 2714,
        "auc": 0.6855853247710285,
        "supported": true
      }
    }
  },
  "test": {
    "rows": 51873,
    "events": 266,
    "tau": 25.999999999999996,
    "mean_auc": 0.8773755650140926,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 56,
        "controls": 51081,
        "auc": 0.6468015085284715,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 182,
        "controls": 50265,
        "auc": 0.653285553598893,
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

## Bootstrap Dynamic AUC

{
  "valid": {
    "mean_auc": {
      "estimate": 0.7272943415906372,
      "ci_lower": 0.6322625046723208,
      "ci_upper": 0.8049074334719247,
      "ci_width": 0.17264492879960391,
      "iterations_requested": 200,
      "iterations_successful": 200,
      "success_rate": 1.0,
      "sample_rows": 2742,
      "skipped_iterations": 0
    },
    "horizons": {
      "h6": {
        "estimate": 0.846055561135831,
        "ci_lower": 0.7736201608024666,
        "ci_upper": 0.9500103557504873,
        "ci_width": 0.17639019494802066,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 2742,
        "skipped_iterations": 0
      },
      "h12": {
        "estimate": 0.734245584376666,
        "ci_lower": 0.6143269600565856,
        "ci_upper": 0.83653538889426,
        "ci_width": 0.22220842883767444,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 2742,
        "skipped_iterations": 0
      },
      "h24": {
        "estimate": 0.6807546578965462,
        "ci_lower": 0.5821091799237279,
        "ci_upper": 0.7724938022044285,
        "ci_width": 0.19038462228070063,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 2742,
        "skipped_iterations": 0
      }
    }
  },
  "test": {
    "mean_auc": {
      "estimate": 0.7685591922903976,
      "ci_lower": 0.6701436599909667,
      "ci_upper": 0.9529427636575333,
      "ci_width": 0.2827991036665666,
      "iterations_requested": 200,
      "iterations_successful": 200,
      "success_rate": 1.0,
      "sample_rows": 10000,
      "skipped_iterations": 0
    },
    "horizons": {
      "h6": {
        "estimate": 0.6636211862386819,
        "ci_lower": 0.4881776626444976,
        "ci_upper": 0.8092136937761797,
        "ci_width": 0.3210360311316821,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 10000,
        "skipped_iterations": 0
      },
      "h12": {
        "estimate": 0.6573968159444974,
        "ci_lower": 0.5640086429519486,
        "ci_upper": 0.7325608245073106,
        "ci_width": 0.168552181555362,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 10000,
        "skipped_iterations": 0
      },
      "h24": {
        "estimate": 0.9509803921568628,
        "ci_lower": 0.8872303921568628,
        "ci_upper": 0.9888032990974167,
        "ci_width": 0.10157290694055388,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 10000,
        "skipped_iterations": 0
      }
    }
  }
}

## Warnings

[
  "low_cases_valid_h6",
  "low_cases_valid_h12",
  "wide_dynamic_auc_ci_test",
  "wide_uno_ci_test",
  "low_controls_test_h24"
]

