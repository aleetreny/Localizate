export type Bounds = {
  min_lng: number;
  min_lat: number;
  max_lng: number;
  max_lat: number;
  min_zoom: number;
  max_zoom: number;
};

export type FrontendMeta = {
  title: string;
  subtitle: string;
  generated_at: string;
  defaultCategoryCode: string;
  map_bounds: Bounds;
};

export type CategoryOption = {
  category_code: string;
  category_desc: string;
  n_locales: number;
  n_hexes: number;
  definition?: string;
  mapped_epigraphs?: number | null;
  historical_coverage_rows?: number | null;
  example_labels?: string[];
};

export type HexAggregate = {
  h3_cell: string;
  category_code: string;
  category_desc: string;
  district_name: string;
  barrio_name: string;
  location_label: string;
  n_locales: number;
  n_events: number;
  avg_risk_ensemble: number;
  avg_risk_percentile: number;
  survival_12m: number | null;
  survival_24m: number | null;
  support_12m: number;
  support_24m: number;
  quality_tier: "high" | "medium" | "low";
};

export type ColorScale = {
  min: number;
  low: number;
  mid: number;
  high: number;
  max: number;
};

export type ZoneAggregate = {
  zone_level: "district" | "barrio";
  zone_code: string;
  zone_name: string;
  category_code: string;
  category_desc: string;
  n_locales: number;
  n_events: number;
  avg_risk_ensemble: number;
  avg_risk_percentile: number;
  event_rate: number;
  duration_median_months: number;
  survival_12m: number | null;
  survival_24m: number | null;
  support_12m: number;
  support_24m: number;
  supported_for_stats: boolean;
  confidence_tier: string;
  rank_within_zone_risk: number;
  rank_within_zone_12m: number;
  rank_within_zone_24m: number;
};

export type FrontendArtifacts = {
  meta: FrontendMeta;
  categories: CategoryOption[];
  hexes: HexAggregate[];
  zones: {
    district: ZoneAggregate[];
    barrio: ZoneAggregate[];
  };
};