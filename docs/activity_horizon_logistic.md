# Activity Horizon Logistic

Comparativa horizon-based entre regresión logística y el score survival actual sobre el target `activity_survival`.

## Split base

- Split counts: {"train": 149280, "test": 51902, "valid": 2646}
- Split event counts: {"test": 238, "train": 18588, "valid": 61}
- Reglas de soporte: {"min_valid_cases": 15, "min_valid_controls": 1000, "min_test_cases": 100, "min_test_controls": 200, "max_horizons": 3}
- Horizontes elegidos: [12, 15, 18]

## Lectura ejecutiva

- La logística gana en 0 de 3 horizontes en valid y en 0 de 3 en test frente al score survival actual, usando la misma población elegible por horizonte.
- h12: valid AUC logit=0.7816 vs survival=0.7956; test AUC logit=0.5759 vs survival=0.6256.
- h15: valid AUC logit=0.7793 vs survival=0.7930; test AUC logit=0.5773 vs survival=0.6101.
- h18: valid AUC logit=0.7715 vs survival=0.7834; test AUC logit=0.9163 vs survival=0.9508.

## Modelos por horizonte

{
  "h12": {
    "horizon_months": 12,
    "eligible_rows": 202402,
    "eligible_event_count": 2185,
    "support": {
      "horizon_months": 12,
      "train": {
        "cases": 2008,
        "controls": 147272,
        "eligible_rows": 149280
      },
      "valid": {
        "cases": 18,
        "controls": 2628,
        "eligible_rows": 2646
      },
      "test": {
        "cases": 159,
        "controls": 50317,
        "eligible_rows": 50476
      }
    },
    "metrics": {
      "train": {
        "rows": 149280,
        "events": 2008,
        "event_rate": 0.013451232583065381,
        "logistic_auc": 0.8111025836628498,
        "survival_risk_auc": 0.8429746489488837,
        "logistic_brier": 0.18372524883470587,
        "auc_delta_vs_survival": -0.031872065286033924
      },
      "valid": {
        "rows": 2646,
        "events": 18,
        "event_rate": 0.006802721088435374,
        "logistic_auc": 0.781604092677152,
        "survival_risk_auc": 0.7955986808726535,
        "logistic_brier": 0.20938769589706063,
        "auc_delta_vs_survival": -0.013994588195501478
      },
      "test": {
        "rows": 50476,
        "events": 159,
        "event_rate": 0.0031500118868373088,
        "logistic_auc": 0.5759181756219031,
        "survival_risk_auc": 0.6255647996732164,
        "logistic_brier": 0.8371526145609454,
        "auc_delta_vs_survival": -0.04964662405131337
      }
    },
    "top_standardized_coefficients": {
      "share_age_65_plus_start": -16.377971,
      "share_age_30_44_start": -12.070564,
      "share_age_00_14_start": -9.758589,
      "share_age_45_64_start": -8.313384,
      "share_age_15_29_start": -6.378076,
      "macro_category__training_languages": -4.32442,
      "macro_category__auto_repair": -4.114314,
      "macro_category__vehicle_sales_parts": -2.298851,
      "macro_category__early_childhood": -0.787033,
      "missing_h3": 0.685189
    }
  },
  "h15": {
    "horizon_months": 15,
    "eligible_rows": 201903,
    "eligible_event_count": 2856,
    "support": {
      "horizon_months": 15,
      "train": {
        "cases": 2623,
        "controls": 146657,
        "eligible_rows": 149280
      },
      "valid": {
        "cases": 19,
        "controls": 2627,
        "eligible_rows": 2646
      },
      "test": {
        "cases": 214,
        "controls": 49763,
        "eligible_rows": 49977
      }
    },
    "metrics": {
      "train": {
        "rows": 149280,
        "events": 2623,
        "event_rate": 0.01757100750267953,
        "logistic_auc": 0.8106277289358619,
        "survival_risk_auc": 0.8437955307893812,
        "logistic_brier": 0.18480156947298393,
        "auc_delta_vs_survival": -0.03316780185351931
      },
      "valid": {
        "rows": 2646,
        "events": 19,
        "event_rate": 0.007180650037792895,
        "logistic_auc": 0.7792759401358363,
        "survival_risk_auc": 0.7929998196862541,
        "logistic_brier": 0.19962914308307345,
        "auc_delta_vs_survival": -0.013723879550417761
      },
      "test": {
        "rows": 49977,
        "events": 214,
        "event_rate": 0.00428196970606479,
        "logistic_auc": 0.5772915019059501,
        "survival_risk_auc": 0.6101478484652768,
        "logistic_brier": 0.8004544406100836,
        "auc_delta_vs_survival": -0.03285634655932668
      }
    },
    "top_standardized_coefficients": {
      "share_age_65_plus_start": -16.012506,
      "share_age_30_44_start": -11.624486,
      "share_age_00_14_start": -9.284699,
      "share_age_45_64_start": -8.062327,
      "share_age_15_29_start": -6.111265,
      "macro_category__training_languages": -4.647628,
      "macro_category__auto_repair": -4.429718,
      "macro_category__vehicle_sales_parts": -2.476807,
      "macro_category__early_childhood": -0.843408,
      "missing_h3": 0.763454
    }
  },
  "h18": {
    "horizon_months": 18,
    "eligible_rows": 152463,
    "eligible_event_count": 3393,
    "support": {
      "horizon_months": 18,
      "train": {
        "cases": 3135,
        "controls": 146145,
        "eligible_rows": 149280
      },
      "valid": {
        "cases": 23,
        "controls": 2623,
        "eligible_rows": 2646
      },
      "test": {
        "cases": 235,
        "controls": 302,
        "eligible_rows": 537
      }
    },
    "metrics": {
      "train": {
        "rows": 149280,
        "events": 3135,
        "event_rate": 0.0210008038585209,
        "logistic_auc": 0.8079923900707513,
        "survival_risk_auc": 0.8440761313770275,
        "logistic_brier": 0.18633491269150354,
        "auc_delta_vs_survival": -0.03608374130627623
      },
      "valid": {
        "rows": 2646,
        "events": 23,
        "event_rate": 0.008692365835222978,
        "logistic_auc": 0.7714697740721709,
        "survival_risk_auc": 0.7834043329078884,
        "logistic_brier": 0.18804523379581656,
        "auc_delta_vs_survival": -0.01193455883571748
      },
      "test": {
        "rows": 537,
        "events": 235,
        "event_rate": 0.4376163873370577,
        "logistic_auc": 0.9162603917148091,
        "survival_risk_auc": 0.9508242919543469,
        "logistic_brier": 0.1585297739143798,
        "auc_delta_vs_survival": -0.034563900239537815
      }
    },
    "top_standardized_coefficients": {
      "share_age_65_plus_start": -16.441387,
      "share_age_30_44_start": -12.009777,
      "share_age_00_14_start": -9.58181,
      "share_age_45_64_start": -8.291692,
      "share_age_15_29_start": -6.312764,
      "macro_category__training_languages": -4.701763,
      "macro_category__auto_repair": -4.46745,
      "macro_category__vehicle_sales_parts": -2.490614,
      "macro_category__early_childhood": -0.851769,
      "missing_h3": 0.763666
    }
  }
}

