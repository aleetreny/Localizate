# Survival Canonical Robustness

Chequeo post-entrenamiento sobre los scores ya exportados para añadir intervalos de confianza y alertas de soporte estadístico sin relanzar el fit.

- Estado global: pass_with_caveats
- Filas evaluadas: 203828
- Split counts: {"train": 149280, "test": 51902, "valid": 2646}
- Split events: {"test": 238, "train": 18588, "valid": 61}
- Bootstrap config: {"iterations": 200, "max_rows": 10000, "random_seed": 20260325}

## Lectura ejecutiva

- El chequeo robusto reutiliza los scores del último run y añade intervalos bootstrap sin relanzar el entrenamiento.
- Uno valid=0.7755 con CI bootstrap [0.7397, 0.8234]; test=0.6052 con CI [0.5283, 0.6919].
- Dynamic AUC mean valid=0.7928 con CI [0.7321, 0.8514]; test=0.9232 con CI [0.6533, 0.9749].
- Los horizontes más extremos siguen siendo frágiles: el soporte de casos/controles en h6 valid y h24 test no alcanza un nivel cómodo para venderlos como KPI principal.

## Uno / IPCW C-index

{
  "train": {
    "rows": 149280,
    "events": 18588,
    "tau": 134.99999999999997,
    "uno_c_index": 0.7991063649435617
  },
  "valid": {
    "rows": 2646,
    "events": 61,
    "tau": 53.99999999999999,
    "uno_c_index": 0.7755370689538181
  },
  "test": {
    "rows": 51902,
    "events": 238,
    "tau": 26.999999999999996,
    "uno_c_index": 0.6051663553178592
  }
}

## Bootstrap Uno / IPCW C-index

{
  "valid": {
    "estimate": 0.7783512550259858,
    "ci_lower": 0.7396505011264926,
    "ci_upper": 0.823362644672254,
    "ci_width": 0.0837121435457614,
    "iterations_requested": 200,
    "iterations_successful": 200,
    "success_rate": 1.0,
    "sample_rows": 2646,
    "skipped_iterations": 0
  },
  "test": {
    "estimate": 0.6046382415698295,
    "ci_lower": 0.528270967465599,
    "ci_upper": 0.691932659192196,
    "ci_width": 0.16366169172659706,
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
    "rows": 149280,
    "events": 18588,
    "tau": 134.99999999999997,
    "mean_auc": 0.8455342757278574,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 1066,
        "controls": 148214,
        "auc": 0.8492900180260119,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 2008,
        "controls": 147272,
        "auc": 0.8429746607843166,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 4084,
        "controls": 145196,
        "auc": 0.8447671928699492,
        "supported": true
      }
    }
  },
  "valid": {
    "rows": 2646,
    "events": 61,
    "tau": 53.99999999999999,
    "mean_auc": 0.7927756854335118,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 8,
        "controls": 2638,
        "auc": 0.8813021228203184,
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
        "auc": 0.7494555999343437,
        "supported": true
      }
    }
  },
  "test": {
    "rows": 51902,
    "events": 238,
    "tau": 26.999999999999996,
    "mean_auc": 0.9231836093203737,
    "horizons": {
      "h6": {
        "time": 6.0,
        "cases": 45,
        "controls": 51121,
        "auc": 0.6281530312613429,
        "supported": true
      },
      "h12": {
        "time": 12.0,
        "cases": 159,
        "controls": 50317,
        "auc": 0.6255646121826612,
        "supported": true
      },
      "h24": {
        "time": 24.0,
        "cases": 238,
        "controls": 81,
        "auc": 0.9678389874468305,
        "supported": true
      }
    }
  }
}

## Bootstrap Dynamic AUC

{
  "valid": {
    "mean_auc": {
      "estimate": 0.7916602370510832,
      "ci_lower": 0.7320838005848752,
      "ci_upper": 0.8513965221335182,
      "ci_width": 0.11931272154864303,
      "iterations_requested": 200,
      "iterations_successful": 200,
      "success_rate": 1.0,
      "sample_rows": 2646,
      "skipped_iterations": 0
    },
    "horizons": {
      "h6": {
        "estimate": 0.8811506434519304,
        "ci_lower": 0.7699487964830328,
        "ci_upper": 0.976745703426717,
        "ci_width": 0.20679690694368413,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 2646,
        "skipped_iterations": 0
      },
      "h12": {
        "estimate": 0.7963034166323395,
        "ci_lower": 0.7208615832065218,
        "ci_upper": 0.8839690763813963,
        "ci_width": 0.1631074931748745,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 2646,
        "skipped_iterations": 0
      },
      "h24": {
        "estimate": 0.7501837141392365,
        "ci_lower": 0.7002835813115407,
        "ci_upper": 0.8102580741805359,
        "ci_width": 0.10997449286899519,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 2646,
        "skipped_iterations": 0
      }
    }
  },
  "test": {
    "mean_auc": {
      "estimate": 0.793619900325021,
      "ci_lower": 0.6533427492949969,
      "ci_upper": 0.9749036465797767,
      "ci_width": 0.32156089728477977,
      "iterations_requested": 200,
      "iterations_successful": 200,
      "success_rate": 1.0,
      "sample_rows": 10000,
      "skipped_iterations": 0
    },
    "horizons": {
      "h6": {
        "estimate": 0.6357147560736316,
        "ci_lower": 0.42822055079163723,
        "ci_upper": 0.8146163863891436,
        "ci_width": 0.38639583559750634,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 10000,
        "skipped_iterations": 0
      },
      "h12": {
        "estimate": 0.6328487324511499,
        "ci_lower": 0.531639180128488,
        "ci_upper": 0.7185021470927186,
        "ci_width": 0.18686296696423066,
        "iterations_requested": 200,
        "iterations_successful": 200,
        "success_rate": 1.0,
        "sample_rows": 10000,
        "skipped_iterations": 0
      },
      "h24": {
        "estimate": 0.9758454106280194,
        "ci_lower": 0.9207492236024845,
        "ci_upper": 1.0,
        "ci_width": 0.07925077639751554,
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

