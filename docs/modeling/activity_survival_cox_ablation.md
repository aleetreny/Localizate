# Activity Survival Cox Ablation

Ablation leave-one-block-out sobre `activity_survival` usando `cox_only` y los mismos folds rolling del benchmark temporal.

## Configuracion

{
  "rows": 203828,
  "fold_count": 4,
  "cutoffs": [
    "2020-03",
    "2021-04",
    "2022-06",
    "2023-06",
    "2024-10",
    "2026-04"
  ],
  "transition_policy": "exclude_transition",
  "renta_max_year": 2023,
  "fit_max_rows": null
}

- Cox params: {"alpha": 0.004431207789037498, "ties": "breslow"}

## Baseline

{
  "valid_uno": {
    "count": 4,
    "mean": 0.6687125198217081,
    "std": 0.08004988050660267,
    "min": 0.540392132530868,
    "max": 0.7582253651139024
  },
  "test_uno": {
    "count": 4,
    "mean": 0.6786409794577533,
    "std": 0.041098560223026666,
    "min": 0.6149682241590464,
    "max": 0.7272937065242475
  },
  "valid_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.6787809261358908,
    "std": 0.11793607064911882,
    "min": 0.49858174584993187,
    "max": 0.8126449233574202
  },
  "test_dynamic_auc_mean": {
    "count": 4,
    "mean": 0.7033454518575518,
    "std": 0.06032581152611794,
    "min": 0.6315243862713182,
    "max": 0.7766161469186227
  }
}

## Lectura ejecutiva

- Baseline Cox afinado: valid Uno=0.6687, test Uno=0.6786, test mean AUC=0.7033.
- El bloque cuya retirada mas dana el test Uno es `activity_identity` (Identidad de actividad), con delta=-0.1447.
- Hay al menos un bloque que parece ruidoso: quitar `competition_stock` mejora el test Uno en 0.0117.

## Resultados por bloque

| bloque | cols | delta test Uno | delta valid Uno | delta test AUC | delta objective |
| --- | ---: | ---: | ---: | ---: | ---: |
| Identidad de actividad | 36 | -0.1447 | -0.1017 | -0.1387 | -0.1334 |
| Accesibilidad metro | 3 | -0.0026 | 0.0007 | -0.0014 | -0.0004 |
| Complejidad de actividad | 3 | -0.0001 | -0.0000 | 0.0005 | 0.0001 |
| Flujos competitivos | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Concentracion competitiva | 4 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Dinamica de zona | 6 | 0.0002 | -0.0001 | -0.0005 | 0.0005 |
| Calidad de dato | 4 | 0.0011 | -0.0016 | 0.0008 | -0.0001 |
| Socioeconomia | 12 | 0.0034 | -0.0110 | -0.0068 | -0.0024 |
| Avisos | 3 | 0.0047 | 0.0007 | 0.0091 | 0.0040 |
| Temporalidad de entrada | 6 | 0.0091 | 0.0015 | 0.0123 | 0.0062 |
| Competencia stock | 8 | 0.0117 | 0.0141 | 0.0002 | 0.0069 |

## Payload

[
  {
    "block": {
      "name": "socioeconomic",
      "label": "Socioeconomia",
      "columns": [
        "renta_effective_eur",
        "renta_carry_forward_years",
        "share_foreign_start",
        "share_age_00_14_start",
        "share_age_15_29_start",
        "share_age_30_44_start",
        "share_age_45_64_start",
        "share_age_65_plus_start",
        "share_male_start",
        "age_mean_start",
        "total_population_start",
        "population_density_km2_start"
      ]
    },
    "selected_feature_count": 83,
    "selected_columns": [
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6576637140995538,
        "std": 0.07652033288328262,
        "min": 0.5338152261587144,
        "max": 0.743159265486434
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6819918851002631,
        "std": 0.02327350739476622,
        "min": 0.6555184827732783,
        "max": 0.7194557083044869
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6539211203241533,
        "std": 0.10399119634763924,
        "min": 0.4814871552028472,
        "max": 0.7433829786579542
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6965423525911192,
        "std": 0.039949599880688864,
        "min": 0.6482166703350678,
        "max": 0.7409251570357747
      }
    },
    "objective": 0.6710759005370407,
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
            "uno_c_index": 0.745473722746709
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5338152261587144
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7194557083044869
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7441065183705154,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.727273358527463,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7401247707599998,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7545578551452902,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.4814871552028472,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.43762376237623757,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5359272933825618,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4972638248847926,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7409251570357747,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7654485049833887,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7818988746235537,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7122739960268565,
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
            "uno_c_index": 0.7451087801558781
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.743159265486434
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6774586597040905
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7433009567135785,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7261052802263703,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7395419334554123,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7538466306251668,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7433829786579542,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.735453251067869,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.7815290325989326,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7320894208766062,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7306922321357401,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8115577889447236,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7422709387296234,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7009713835652402,
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
            "uno_c_index": 0.7455202545711944
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
            "uno_c_index": 0.6755346896191967
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7448091619119634,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7278175556725293,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7412576279017873,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7551536471741205,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7276375475513069,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8040201005025125,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7349634626194492,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7016277238120241,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6663353508578942,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7114243323442137,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6020459081836327,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6799334679814661,
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
            "uno_c_index": 0.7453712191994308
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6724793203666443
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6555184827732783
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7445388182051758,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7279927507802983,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7409674741666685,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7546520732420411,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6631767998845046,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.708704253214639,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5976796407185628,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6773197101104906,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6482166703350678,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6256186835719113,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6564304392892658,
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
    "delta_vs_baseline": {
      "valid_uno_mean": -0.011048805722154276,
      "test_uno_mean": 0.0033509056425098382,
      "valid_dynamic_auc_mean": -0.024859805811737523,
      "test_dynamic_auc_mean": -0.006803099266432633,
      "objective": -0.002421926093644333
    }
  },
  {
    "block": {
      "name": "data_quality",
      "label": "Calidad de dato",
      "columns": [
        "padron_lag_months_start",
        "geometry_available_start",
        "missing_h3",
        "missing_metro_distance_start"
      ]
    },
    "selected_feature_count": 91,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6671070905000378,
        "std": 0.0815524888683012,
        "min": 0.5349941056027797,
        "max": 0.7576319519994725
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6797013953665603,
        "std": 0.03988793931142447,
        "min": 0.6171145742054733,
        "max": 0.7277305245112584
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6739315489298154,
        "std": 0.12402654986421376,
        "min": 0.4773978320775327,
        "max": 0.8130024565853136
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7041314493176125,
        "std": 0.05598044174962866,
        "min": 0.6315992780382367,
        "max": 0.7762625158621336
      }
    },
    "objective": 0.6734251421652342,
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
            "uno_c_index": 0.7593290843136216
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5349941056027797
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7277305245112584
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7983036783934497,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8013576254092936,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7967123343678879,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7974596533102576,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.4773978320775327,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4221782178217821,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5373473445044021,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.4997119815668203,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7762625158621336,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8247745609871855,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8244835420299044,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7327180828324994,
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
            "uno_c_index": 0.7589387378512505
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7576319519994725
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6911227154046997
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7973053197125824,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7997780310638329,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7959673669711252,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7966419876375965,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8130024565853136,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8592311343141908,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8606223912928621,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7708401438378556,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7365139248724385,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8417085427135678,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7582911748173131,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6940141769493305,
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
            "uno_c_index": 0.7591952539090063
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.694604003481288
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6828377673448096
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7986621615321572,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8013765976160574,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7975732376117157,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.797761386553792,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.733591369657965,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8358458961474036,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7512647554806071,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6942767130480442,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.672150078497641,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7007912957467853,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.623627744510978,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6862302483069977,
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
            "uno_c_index": 0.7590168218256853
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6811983009166108
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6171145742054733
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7983033036107335,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8014834335429966,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7972283804304539,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7971596955737299,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6717345373984503,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.7030168150346192,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.623003992015968,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6840917191398359,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6315992780382367,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6169897516434233,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6369094534797456,
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
    "delta_vs_baseline": {
      "valid_uno_mean": -0.001605429321670293,
      "test_uno_mean": 0.0010604159088070109,
      "valid_dynamic_auc_mean": -0.004849377206075367,
      "test_dynamic_auc_mean": 0.0007859974600606945,
      "objective": -7.268446545083407e-05
    }
  },
  {
    "block": {
      "name": "activity_complexity",
      "label": "Complejidad de actividad",
      "columns": [
        "n_divisions_start",
        "n_epigrafes_start",
        "n_activity_categories_start"
      ]
    },
    "selected_feature_count": 92,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6686909280305438,
        "std": 0.08000623802544213,
        "min": 0.5400198548116896,
        "max": 0.7578792074638183
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6784948848587019,
        "std": 0.04067935308622341,
        "min": 0.6151480956271634,
        "max": 0.726642600468137
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6793189256586475,
        "std": 0.1179811823552268,
        "min": 0.49716506906649977,
        "max": 0.8120183297323634
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7038404268410218,
        "std": 0.05914277765881891,
        "min": 0.6316245596250637,
        "max": 0.7755043207022347
      }
    },
    "objective": 0.6736173587596344,
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
            "uno_c_index": 0.7592148333672758
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5400198548116896
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.726642600468137
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7980186589042629,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8011923706063476,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.79641765222653,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7971175503648835,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.49716506906649977,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.44990099009900986,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5620562340244248,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5123847926267281,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7755043207022347,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8302800189843379,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8300311723992181,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7263057308823899,
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
            "uno_c_index": 0.7588290544215307
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7578792074638183
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6953872932985204
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7970727066756678,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7996696818593505,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.795766173333335,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7963312343322859,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8120183297323634,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8643569055529188,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8660115179373382,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7642517665400961,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7467806555625564,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8492462311557788,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7731871838111298,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.702415332108165,
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
            "uno_c_index": 0.7590923778898224
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
            "uno_c_index": 0.6768015500409866
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7984049773307561,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8012584860444094,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7973725436236572,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7974070885361353,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.746860908777433,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8417085427135678,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7700955593029792,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7064846416382253,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6614521714742322,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6933728981206726,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6111526946107784,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6744683378876084,
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
            "uno_c_index": 0.7589294450267067
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6759072956256055
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6151480956271634
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7981152980472965,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8014679702750179,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7970960064639407,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7968578749187601,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6612313950582936,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6958456973293768,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6107784431137724,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6724486158964001,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6316245596250637,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.623034515727714,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6347468127982658,
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
    "delta_vs_baseline": {
      "valid_uno_mean": -2.1591791164343732e-05,
      "test_uno_mean": -0.00014609459905134958,
      "valid_dynamic_auc_mean": 0.0005379995227566825,
      "test_dynamic_auc_mean": 0.0004949749834699535,
      "objective": 0.00011953212894932896
    }
  },
  {
    "block": {
      "name": "competition_stock",
      "label": "Competencia stock",
      "columns": [
        "section_local_count_start",
        "section_unique_division_count_start",
        "section_unique_activity_category_count_start",
        "section_single_division_share_start",
        "section_same_division_local_count_start",
        "section_same_division_share_start",
        "section_same_activity_category_local_count_start",
        "section_same_activity_category_share_start"
      ]
    },
    "selected_feature_count": 87,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.682810954008352,
        "std": 0.0886622258997084,
        "min": 0.5429670534218527,
        "max": 0.7850731876174464
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6902947862001665,
        "std": 0.05834032454283436,
        "min": 0.6002936739248216,
        "max": 0.7575948636798207
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6829232179331117,
        "std": 0.1231974573513147,
        "min": 0.5035081761166814,
        "max": 0.8277529112244838
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7035599824271185,
        "std": 0.07538715989018796,
        "min": 0.6168460278576107,
        "max": 0.793860995579681
      }
    },
    "objective": 0.6804467584312195,
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
            "uno_c_index": 0.7546841143648235
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5429670534218527
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7575948636798207
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7971139145259524,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8013570713143849,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7943191108999677,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7962066866368778,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5035081761166814,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4691089108910891,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5556660039761431,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5131768433179724,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.793860995579681,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8181300427147603,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8454060337084588,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7611084567606307,
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
            "uno_c_index": 0.7542782329758588
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7850731876174464
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7207136640557006
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7961905749729798,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7999780855354781,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7936524043826244,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7953965208110416,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8277529112244838,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8501186521120077,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.876948274951128,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7968918952900647,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7611502856034186,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8174204355108878,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.751264755480607,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7507219742714624,
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
            "uno_c_index": 0.7546637361087323
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.720626631853786
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6825769431403235
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7975146878096527,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8012767460279158,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7953108715938163,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7965815485351204,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7591522287638048,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8149078726968174,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.746486790331647,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7504594381727487,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6423826206677637,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6296983184965381,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5947480039920159,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6851015801354402,
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
            "uno_c_index": 0.7545381625483484
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6825769431403235
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6002936739248216
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7972902947393232,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8015261752678764,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.795009421881564,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7961527573603882,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6412795556274768,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6292037586547973,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.594498502994012,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6829630509682785,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6168460278576107,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6152966513331695,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6174091851391951,
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
    "delta_vs_baseline": {
      "valid_uno_mean": 0.014098434186643916,
      "test_uno_mean": 0.01165380674241323,
      "valid_dynamic_auc_mean": 0.0041422917972209206,
      "test_dynamic_auc_mean": 0.00021453056956666217,
      "objective": 0.006948931800534464
    }
  },
  {
    "block": {
      "name": "competition_flow",
      "label": "Flujos competitivos",
      "columns": [
        "section_entry_count_3m_start",
        "section_entry_count_6m_start",
        "section_entry_count_12m_start",
        "section_exit_count_3m_start",
        "section_exit_count_6m_start",
        "section_exit_count_12m_start",
        "section_entry_rate_12m_start",
        "section_exit_rate_12m_start",
        "section_net_flow_12m_start",
        "section_turnover_rate_12m_start"
      ]
    },
    "selected_feature_count": 85,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6687125198217081,
        "std": 0.08004988050660267,
        "min": 0.540392132530868,
        "max": 0.7582253651139024
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6786409794577533,
        "std": 0.041098560223026666,
        "min": 0.6149682241590464,
        "max": 0.7272937065242475
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6787809261358908,
        "std": 0.11793607064911882,
        "min": 0.49858174584993187,
        "max": 0.8126449233574202
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7033454518575518,
        "std": 0.06032581152611794,
        "min": 0.6315243862713182,
        "max": 0.7766161469186227
      }
    },
    "objective": 0.673497826630685,
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
            "uno_c_index": 0.75940915776408
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.540392132530868
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7272937065242475
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.798419763190002,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8018216494681585,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7966273463721303,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7974885670336513,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.49858174584993187,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.45148514851485144,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5634762851462652,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5136808755760369,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7766161469186227,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.831798766018035,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8310878638981349,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7272361505771118,
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
            "uno_c_index": 0.7590254462174669
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7582253651139024
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.696692776327241
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7974816234667946,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8003167590025545,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7959801624560118,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7967062641355023,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8126449233574202,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8651162790697675,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8665926982617425,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7648301355395177,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7475032797320448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8492462311557788,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7734682405845981,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.703596744552376,
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
            "uno_c_index": 0.7592902867426642
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7022628372497824
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6756092108204784
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7988148134358719,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8019029696213983,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7975904709415554,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7977834380941887,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7476151253697485,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8417085427135678,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7709387296233838,
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
            "mean_auc": 0.6577379945082217,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6857072205736895,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6081586826347305,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6730426517761674,
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
            "uno_c_index": 0.759125794271407
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6739697443922796
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6149682241590464
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.798527080912878,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.802113977817299,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7973185020708934,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7972354523056517,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6562819099664626,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6852126607319486,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6065369261477046,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6710229297849589,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6315243862713182,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6233752956625914,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6344863646169308,
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
    "delta_vs_baseline": {
      "valid_uno_mean": 0.0,
      "test_uno_mean": 0.0,
      "valid_dynamic_auc_mean": 0.0,
      "test_dynamic_auc_mean": 0.0,
      "objective": 0.0
    }
  },
  {
    "block": {
      "name": "competition_concentration",
      "label": "Concentracion competitiva",
      "columns": [
        "section_division_hhi_start",
        "section_division_top_share_start",
        "section_activity_category_hhi_start",
        "section_activity_category_top_share_start"
      ]
    },
    "selected_feature_count": 91,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6687125198217081,
        "std": 0.08004988050660267,
        "min": 0.540392132530868,
        "max": 0.7582253651139024
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6786409794577533,
        "std": 0.041098560223026666,
        "min": 0.6149682241590464,
        "max": 0.7272937065242475
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6787809261358908,
        "std": 0.11793607064911882,
        "min": 0.49858174584993187,
        "max": 0.8126449233574202
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7033454518575518,
        "std": 0.06032581152611794,
        "min": 0.6315243862713182,
        "max": 0.7766161469186227
      }
    },
    "objective": 0.673497826630685,
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
            "uno_c_index": 0.75940915776408
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.540392132530868
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7272937065242475
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.798419763190002,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8018216494681585,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7966273463721303,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7974885670336513,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.49858174584993187,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.45148514851485144,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5634762851462652,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5136808755760369,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7766161469186227,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.831798766018035,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8310878638981349,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7272361505771118,
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
            "uno_c_index": 0.7590254462174669
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7582253651139024
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.696692776327241
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7974816234667946,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.8003167590025545,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7959801624560118,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7967062641355023,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8126449233574202,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8651162790697675,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8665926982617425,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7648301355395177,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7475032797320448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8492462311557788,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7734682405845981,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.703596744552376,
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
            "uno_c_index": 0.7592902867426642
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7022628372497824
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6756092108204784
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7988148134358719,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8019029696213983,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7975904709415554,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7977834380941887,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7476151253697485,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8417085427135678,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7709387296233838,
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
            "mean_auc": 0.6577379945082217,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6857072205736895,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6081586826347305,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6730426517761674,
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
            "uno_c_index": 0.759125794271407
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6739697443922796
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6149682241590464
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.798527080912878,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.802113977817299,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7973185020708934,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7972354523056517,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6562819099664626,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6852126607319486,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6065369261477046,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6710229297849589,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6315243862713182,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6233752956625914,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6344863646169308,
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
    "delta_vs_baseline": {
      "valid_uno_mean": 0.0,
      "test_uno_mean": 0.0,
      "valid_dynamic_auc_mean": 0.0,
      "test_dynamic_auc_mean": 0.0,
      "objective": 0.0
    }
  },
  {
    "block": {
      "name": "zone_dynamics",
      "label": "Dinamica de zona",
      "columns": [
        "section_local_count_delta_12m_start",
        "total_population_delta_12m_start",
        "share_foreign_delta_12m_start",
        "share_age_15_29_delta_12m_start",
        "population_density_km2_delta_12m_start",
        "renta_best_eur_delta_12m_start"
      ]
    },
    "selected_feature_count": 89,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6686297762387416,
        "std": 0.07725710345374956,
        "min": 0.5435564931438853,
        "max": 0.75340388355916
      },
      "test_uno": {
        "count": 4,
        "mean": 0.678793011315882,
        "std": 0.03806183156412391,
        "min": 0.61836526886647,
        "max": 0.7209886921834305
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6799329224748651,
        "std": 0.11579780744703451,
        "min": 0.5001092415889686,
        "max": 0.8066750277612572
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7028503607798592,
        "std": 0.05740204814846267,
        "min": 0.6333405332449026,
        "max": 0.7691216648914136
      }
    },
    "objective": 0.6740167869800479,
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
            "uno_c_index": 0.7593609161033287
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5435564931438853
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7209886921834305
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7981785089127725,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8014126889912039,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7963403849736397,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7973541832448345,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5001092415889686,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.44990099009900986,
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
                "auc": 0.5171370967741936,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7691216648914136,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8270526815377314,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8244307074549585,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7180325395428371,
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
            "uno_c_index": 0.7589826098565574
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.75340388355916
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6978241949521323
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.797264986818197,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.799935219216285,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7957244937981924,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.79659211347257,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8066750277612572,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8617940199335548,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.860305383843187,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7576633892423366,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7489175394111764,
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
                "auc": 0.774592467678471,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7043843528485167,
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
            "uno_c_index": 0.7592129539615877
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6995648389904264
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6779938892614948
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7985072277646903,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8014066484921063,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7972269766320279,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7975982254313718,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.750220621847432,
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
                "auc": 0.7726250702641934,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.70792859018115,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6600217055719442,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6869436201780416,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6115269461077845,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6752999881192825,
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
            "uno_c_index": 0.7590423790737829
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6779938892614948
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.61836526886647
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7982213795686439,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8016432392422767,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7969691915786246,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7970342531121547,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6627267987018026,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6928783382789319,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6136477045908184,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6761316383509564,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6333405332449026,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6220760121644038,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6374348879546663,
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
    "delta_vs_baseline": {
      "valid_uno_mean": -8.274358296644913e-05,
      "test_uno_mean": 0.00015203185812873166,
      "valid_dynamic_auc_mean": 0.001151996338974337,
      "test_dynamic_auc_mean": -0.0004950910776926332,
      "objective": 0.0005189603493628292
    }
  },
  {
    "block": {
      "name": "avisos",
      "label": "Avisos",
      "columns": [
        "avisos_district_per_1000_prev_year",
        "avisos_barrio_per_1000_prev_year",
        "avisos_barrio_share_of_district_prev_year"
      ]
    },
    "selected_feature_count": 92,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6693831488330497,
        "std": 0.08687505197616141,
        "min": 0.5302165415399889,
        "max": 0.7680166815019945
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6833729005348643,
        "std": 0.04555617412129602,
        "min": 0.6144147600871745,
        "max": 0.7407114363894108
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.683600678534157,
        "std": 0.1277443391437847,
        "min": 0.48810676275519443,
        "max": 0.8311391091738448
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7124915489613305,
        "std": 0.06793977237585005,
        "min": 0.6309136596444058,
        "max": 0.7999782894586286
      }
    },
    "objective": 0.6775220876687862,
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
            "uno_c_index": 0.7593458101718549
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5302165415399889
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7407114363894108
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7981394495130787,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.80123986582832,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7963451110869952,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7973638768680116,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.48810676275519443,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4459405940594059,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5523998863959103,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.49985599078341014,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7999782894586286,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8533459895586142,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8540180694246315,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7516785274222346,
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
            "uno_c_index": 0.7589456558216845
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7680166815019945
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6989556135770235
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7972160590464467,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7998346947908861,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7957114606683227,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7965534046091816,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8311391091738448,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8790697674418604,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8821788978707666,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7867578645610683,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7550174027928195,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8601340033500837,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7855536818437324,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7075347860330796,
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
            "uno_c_index": 0.7592277262692921
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7013054830287206
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6794097920858484
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7986459480268862,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8015617414406289,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7974167248566442,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7977053701897939,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7530709525427209,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8567839195979899,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7802136031478358,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.70792859018115,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6640568439494683,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6933728981206726,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6165169660678642,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6769632885826304,
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
            "uno_c_index": 0.7590702046868809
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6779938892614948
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6144147600871745
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7983249505289031,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8016811271933231,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7971197003930541,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7971502071084446,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6620858896648679,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6906528189910979,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6140219560878244,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6758940239990496,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6309136596444058,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6227743710450329,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6338720752195395,
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
    "delta_vs_baseline": {
      "valid_uno_mean": 0.000670629011341628,
      "test_uno_mean": 0.004731921077111068,
      "valid_dynamic_auc_mean": 0.004819752398266153,
      "test_dynamic_auc_mean": 0.009146097103778672,
      "objective": 0.004024261038101162
    }
  },
  {
    "block": {
      "name": "metro",
      "label": "Accesibilidad metro",
      "columns": [
        "metro_distance_m_start",
        "metro_access_count_500m_start",
        "metro_access_count_1000m_start"
      ]
    },
    "selected_feature_count": 92,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6694437754200635,
        "std": 0.07123102192609608,
        "min": 0.5557796115902464,
        "max": 0.7521470016154024
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6760323033947335,
        "std": 0.036873321309657536,
        "min": 0.6181089629125067,
        "max": 0.7204488510862757
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6800819970147761,
        "std": 0.10938203060510696,
        "min": 0.5122255652965839,
        "max": 0.8087907903348671
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7019488598837167,
        "std": 0.0540671961051488,
        "min": 0.6364102014226203,
        "max": 0.7726082871238411
      }
    },
    "objective": 0.6730539952323299,
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
            "uno_c_index": 0.7586844222644786
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5557796115902464
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7204488510862757
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7971122087835697,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.8005470582236525,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7952958233310798,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7961749911241991,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5122255652965839,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.4641584158415841,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5819369497301903,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5266417050691246,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.7726082871238411,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8371143806359753,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8291065673376656,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7177559282822441,
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
            "uno_c_index": 0.7583251877697569
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7521470016154024
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6859007832898172
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7962156188075799,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.799073737407721,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7947178517159672,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7954267686744028,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8087907903348671,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8706217370669197,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8646642362762191,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7555259385923001,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7339707341788494,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8291457286432161,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7650365373805509,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6890259910737726,
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
            "uno_c_index": 0.7585570479593325
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6902523933855527
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6796706162903347
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7975039779371667,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8006648105519697,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7962822522875854,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7964340643161363,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7339319780032829,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8232830820770519,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7627880831928049,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.691913888159622,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6648062168095559,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.695351137487636,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6175149700598803,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6766662706427469,
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
            "uno_c_index": 0.7583877892645483
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6795960950890528
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6181089629125067
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7972079151976849,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8008929561488624,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7960225892470282,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7958553591553252,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6653796544243703,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6983184965380811,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6180139720558881,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.675597006059166,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6364102014226203,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6306504673004854,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6385037120442815,
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
    "delta_vs_baseline": {
      "valid_uno_mean": 0.000731255598355407,
      "test_uno_mean": -0.0026086760630197325,
      "valid_dynamic_auc_mean": 0.0013010708788853131,
      "test_dynamic_auc_mean": -0.0013965919738351262,
      "objective": -0.0004438313983551323
    }
  },
  {
    "block": {
      "name": "temporal",
      "label": "Temporalidad de entrada",
      "columns": [
        "cohort_2015_2017",
        "cohort_2018_2019",
        "cohort_2020_2021",
        "cohort_2022_plus",
        "entry_month_sin",
        "entry_month_cos"
      ]
    },
    "selected_feature_count": 89,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "macro_category__fresh_produce",
      "macro_category__butcher",
      "macro_category__fish_shop",
      "macro_category__bakery_pastry",
      "macro_category__ready_meals",
      "macro_category__supermarket",
      "macro_category__food_convenience",
      "macro_category__food_specialty",
      "macro_category__bar_cafe",
      "macro_category__restaurant",
      "macro_category__nightlife",
      "macro_category__catering_collective",
      "macro_category__tourist_accommodation",
      "macro_category__pharmacy_optics",
      "macro_category__clinic_health",
      "macro_category__beauty_personal_care",
      "macro_category__fashion_accessories",
      "macro_category__home_decor",
      "macro_category__home_improvement",
      "macro_category__electronics_telecom",
      "macro_category__books_leisure_retail",
      "macro_category__bazaar_gifts",
      "macro_category__pet_retail",
      "macro_category__personal_services_repair",
      "macro_category__business_services",
      "macro_category__creative_tech_services",
      "macro_category__consumer_services",
      "macro_category__logistics_mobility",
      "macro_category__finance_insurance",
      "macro_category__auto_repair",
      "macro_category__vehicle_sales_parts",
      "macro_category__fuel_station",
      "macro_category__early_childhood",
      "macro_category__training_languages",
      "macro_category__fitness_sports",
      "macro_category__entertainment"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.6701955896614498,
        "std": 0.08193301314203331,
        "min": 0.5382205125023267,
        "max": 0.7609245705996769
      },
      "test_uno": {
        "count": 4,
        "mean": 0.6877510831293794,
        "std": 0.05197842531140791,
        "min": 0.6143134571731697,
        "max": 0.759828404707744
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.6799870675689418,
        "std": 0.12533972414970773,
        "min": 0.48983743977417227,
        "max": 0.8258342085358469
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.7156181623481696,
        "std": 0.07831511823953216,
        "min": 0.6305703980404779,
        "max": 0.8265025740449066
      }
    },
    "objective": 0.6797425055352653,
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
            "uno_c_index": 0.7593279425011938
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5382205125023267
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.759828404707744
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.798366195144152,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.801488459067824,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7966894524584874,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7975259344287751,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.48983743977417227,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.44712871287128714,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5575120704345357,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.5010080645161291,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8265025740449066,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.8773611770289511,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8783219738997199,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.780345512610959,
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
            "uno_c_index": 0.7589687896847507
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.7609245705996769
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6988685813751088
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7972836238076504,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7998387803231237,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7958802446227832,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7966076286937415,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.8258342085358469,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.874608448030375,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.8775822898504781,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.7807478562627305,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7510257625158275,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.847571189279732,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.781618887015177,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7059595694407981,
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
            "uno_c_index": 0.7591277867634884
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.7040905134899913
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6779938892614948
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7981779201956275,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.8008975949447437,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.7970510597206684,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7972916719570503,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.7492050781940554,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.8400335008375208,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7774030354131535,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.7071409818850092,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6543739147914664,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6671612265084075,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6153942115768463,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6729238446002138,
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
            "uno_c_index": 0.7590235597347967
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.6775467620538043
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.6143134571731697
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7980270372841956,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.8010855108738915,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7969295682347005,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7969561011615613,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.6550715437716926,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.6698813056379822,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.6158932135728543,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.6723298087204467,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.6305703980404779,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.6230177167168397,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.6333155974260354,
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
    "delta_vs_baseline": {
      "valid_uno_mean": 0.0014830698397416686,
      "test_uno_mean": 0.009110103671626124,
      "valid_dynamic_auc_mean": 0.0012061414330509779,
      "test_dynamic_auc_mean": 0.012272710490617733,
      "objective": 0.0062446789045802475
    }
  },
  {
    "block": {
      "name": "activity_identity",
      "label": "Identidad de actividad",
      "columns": [
        "macro_category__fresh_produce",
        "macro_category__butcher",
        "macro_category__fish_shop",
        "macro_category__bakery_pastry",
        "macro_category__ready_meals",
        "macro_category__supermarket",
        "macro_category__food_convenience",
        "macro_category__food_specialty",
        "macro_category__bar_cafe",
        "macro_category__restaurant",
        "macro_category__nightlife",
        "macro_category__catering_collective",
        "macro_category__tourist_accommodation",
        "macro_category__pharmacy_optics",
        "macro_category__clinic_health",
        "macro_category__beauty_personal_care",
        "macro_category__fashion_accessories",
        "macro_category__home_decor",
        "macro_category__home_improvement",
        "macro_category__electronics_telecom",
        "macro_category__books_leisure_retail",
        "macro_category__bazaar_gifts",
        "macro_category__pet_retail",
        "macro_category__personal_services_repair",
        "macro_category__business_services",
        "macro_category__creative_tech_services",
        "macro_category__consumer_services",
        "macro_category__logistics_mobility",
        "macro_category__finance_insurance",
        "macro_category__auto_repair",
        "macro_category__vehicle_sales_parts",
        "macro_category__fuel_station",
        "macro_category__early_childhood",
        "macro_category__training_languages",
        "macro_category__fitness_sports",
        "macro_category__entertainment"
      ]
    },
    "selected_feature_count": 59,
    "selected_columns": [
      "renta_effective_eur",
      "renta_carry_forward_years",
      "share_foreign_start",
      "share_age_00_14_start",
      "share_age_15_29_start",
      "share_age_30_44_start",
      "share_age_45_64_start",
      "share_age_65_plus_start",
      "share_male_start",
      "age_mean_start",
      "total_population_start",
      "population_density_km2_start",
      "padron_lag_months_start",
      "geometry_available_start",
      "missing_h3",
      "n_divisions_start",
      "n_epigrafes_start",
      "n_activity_categories_start",
      "section_local_count_start",
      "section_unique_division_count_start",
      "section_unique_activity_category_count_start",
      "section_single_division_share_start",
      "section_same_division_local_count_start",
      "section_same_division_share_start",
      "section_same_activity_category_local_count_start",
      "section_same_activity_category_share_start",
      "section_entry_count_3m_start",
      "section_entry_count_6m_start",
      "section_entry_count_12m_start",
      "section_exit_count_3m_start",
      "section_exit_count_6m_start",
      "section_exit_count_12m_start",
      "section_entry_rate_12m_start",
      "section_exit_rate_12m_start",
      "section_net_flow_12m_start",
      "section_turnover_rate_12m_start",
      "section_division_hhi_start",
      "section_division_top_share_start",
      "section_activity_category_hhi_start",
      "section_activity_category_top_share_start",
      "section_local_count_delta_12m_start",
      "total_population_delta_12m_start",
      "share_foreign_delta_12m_start",
      "share_age_15_29_delta_12m_start",
      "population_density_km2_delta_12m_start",
      "renta_best_eur_delta_12m_start",
      "avisos_district_per_1000_prev_year",
      "avisos_barrio_per_1000_prev_year",
      "avisos_barrio_share_of_district_prev_year",
      "metro_distance_m_start",
      "metro_access_count_500m_start",
      "metro_access_count_1000m_start",
      "missing_metro_distance_start",
      "cohort_2015_2017",
      "cohort_2018_2019",
      "cohort_2020_2021",
      "cohort_2022_plus",
      "entry_month_sin",
      "entry_month_cos"
    ],
    "aggregate": {
      "valid_uno": {
        "count": 4,
        "mean": 0.5670252670188789,
        "std": 0.06410392077776952,
        "min": 0.5087562411506074,
        "max": 0.6753698868581375
      },
      "test_uno": {
        "count": 4,
        "mean": 0.5339023841375794,
        "std": 0.0806328174112369,
        "min": 0.45332875452291815,
        "max": 0.6682332463011315
      },
      "valid_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5806079391578793,
        "std": 0.0697962065768498,
        "min": 0.5007441976265393,
        "max": 0.6665515880961077
      },
      "test_dynamic_auc_mean": {
        "count": 4,
        "mean": 0.5646087496839283,
        "std": 0.07809291684857174,
        "min": 0.46446382903750705,
        "max": 0.672847369456346
      }
    },
    "objective": 0.5400703115451269,
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
            "uno_c_index": 0.6932678625619768
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "uno_c_index": 0.5469690389030216
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.5035027857448983
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148334,
            "events": 18521,
            "tau": 134.99999999999997,
            "mean_auc": 0.7425777454068453,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1060,
                "controls": 147274,
                "auc": 0.75860277506104,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 1999,
                "controls": 146335,
                "auc": 0.7374000151406555,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4064,
                "controls": 144270,
                "auc": 0.7367062477247659,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 510,
            "events": 34,
            "tau": 72.99999999999999,
            "mean_auc": 0.5007441976265393,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 505,
                "auc": 0.39920792079207923,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 7,
                "controls": 503,
                "auc": 0.5313831297926725,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 14,
                "controls": 496,
                "auc": 0.564516129032258,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.5967327220868782,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7360227812055053,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.5818143393036403,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.533055045640858,
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
            "uno_c_index": 0.6929501870047113
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "uno_c_index": 0.537005901163749
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6682332463011315
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 148844,
            "events": 18555,
            "tau": 134.99999999999997,
            "mean_auc": 0.7417663225547219,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1065,
                "controls": 147779,
                "auc": 0.7570102284762423,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2006,
                "controls": 146838,
                "auc": 0.7368109240971836,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4078,
                "controls": 144766,
                "auc": 0.7361815108472527,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 2112,
            "events": 61,
            "tau": 59.99999999999999,
            "mean_auc": 0.6309675695765652,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 5,
                "controls": 2107,
                "auc": 0.7738965353583294,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 9,
                "controls": 2103,
                "auc": 0.6150472869445766,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 2093,
                "auc": 0.5658711997384767,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.672847369456346,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6306532663316583,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7276559865092749,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6535836177474403,
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
            "uno_c_index": 0.6929981854393177
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "uno_c_index": 0.6753698868581375
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5105447499813697
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 150956,
            "events": 18616,
            "tau": 134.99999999999997,
            "mean_auc": 0.7432454251234184,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1070,
                "controls": 149886,
                "auc": 0.7590244723061177,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2015,
                "controls": 148941,
                "auc": 0.738265939168245,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4097,
                "controls": 146859,
                "auc": 0.7373962578525974,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 599,
            "events": 20,
            "tau": 45.99999999999999,
            "mean_auc": 0.6665515880961077,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 2,
                "controls": 597,
                "auc": 0.6180904522613065,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 6,
                "controls": 593,
                "auc": 0.7141652613827993,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 13,
                "controls": 586,
                "auc": 0.6531898135993699,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5243910781549816,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5954500494559841,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5420409181636726,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.46156587857906617,
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
            "uno_c_index": 0.6928737667903015
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "uno_c_index": 0.5087562411506074
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "uno_c_index": 0.45332875452291815
          }
        },
        "dynamic_auc": {
          "train": {
            "rows": 151555,
            "events": 18636,
            "tau": 134.99999999999997,
            "mean_auc": 0.7429499839136361,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 1072,
                "controls": 150483,
                "auc": 0.7590452988888218,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 2021,
                "controls": 149534,
                "auc": 0.7380438871856739,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 4110,
                "controls": 147445,
                "auc": 0.7369192075332804,
                "supported": true
              }
            }
          },
          "valid": {
            "rows": 680,
            "events": 23,
            "tau": 33.99999999999999,
            "mean_auc": 0.5241684013323052,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 6,
                "controls": 674,
                "auc": 0.5981701285855588,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 12,
                "controls": 668,
                "auc": 0.5419161676646705,
                "supported": true
              },
              "h24": {
                "time": 24.0,
                "cases": 19,
                "controls": 443,
                "auc": 0.4591897350599976,
                "supported": true
              }
            }
          },
          "test": {
            "rows": 51593,
            "events": 228,
            "tau": 17.999999999999996,
            "mean_auc": 0.46446382903750705,
            "horizons": {
              "h6": {
                "time": 6.0,
                "cases": 41,
                "controls": 50816,
                "auc": 0.45778000591325185,
                "supported": true
              },
              "h12": {
                "time": 12.0,
                "cases": 152,
                "controls": 50015,
                "auc": 0.46689322150723206,
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
    "delta_vs_baseline": {
      "valid_uno_mean": -0.1016872528028292,
      "test_uno_mean": -0.14473859532017386,
      "valid_dynamic_auc_mean": -0.09817298697801147,
      "test_dynamic_auc_mean": -0.13873670217362355,
      "objective": -0.13342751508555817
    }
  }
]

