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
};

export type HexAggregate = {
  h3_cell: string;
  category_code: string;
  category_desc: string;
  n_locales: number;
  n_events: number;
  avg_risk_ensemble: number;
  avg_risk_percentile: number;
  survival_12m: number;
  survival_24m: number;
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
  category_desc: string;
  web_category: string;
  web_supercategory: string;
  n_locales: number;
  n_events: number;
  survival_12m: number;
  survival_24m: number;
  confidence_tier: string;
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