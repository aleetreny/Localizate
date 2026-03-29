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

export type OpportunityMeta = {
  title: string;
  subtitle: string;
  generated_at: string;
  section_geojson_path: string;
  map_bounds: Bounds;
};

export type OpportunityFilters = {
  total_listings: number;
  precise_candidates: number;
  selected_listings: number;
  excluded_incomplete: number;
  excluded_outliers: number;
  operations: Record<string, number>;
};

export type OpportunityStats = {
  selected_listings: number;
  districts: number;
  barrios: number;
  median_survival_24m: number | null;
  median_price_per_m2: number | null;
};

export type OpportunityActivity = {
  rank: number;
  source_zone: "district" | "barrio" | "city";
  display_label: string;
  web_supercategory: string;
  web_category: string;
  event_rate: number | null;
  activity_risk: number | null;
  survival_12m: number | null;
  survival_24m: number | null;
  n_locales: number;
  confidence_tier: string;
  supported_for_stats: boolean;
};

export type OpportunityPoint = {
  listing_id: string;
  listing_url: string;
  card_title: string;
  address_text: string;
  operation: string;
  price_eur: number | null;
  price_per_m2_eur: number | null;
  area_m2: number | null;
  lat_wgs84: number | null;
  lon_wgs84: number | null;
  section_key: string;
  district_code: string;
  district_name: string;
  barrio_code: string;
  barrio_name: string;
  risk_score: number;
  risk_percentile: number;
  expected_survival_12m: number | null;
  expected_survival_24m: number | null;
  opportunity_tier: string;
  city_rank: number;
  city_total_sections: number;
  district_rank: number;
  district_total_sections: number;
  barrio_rank: number;
  barrio_total_sections: number;
  renta_effective_eur: number | null;
  total_population_start: number | null;
  population_density_km2_start: number | null;
  age_mean_start: number | null;
  share_foreign_start: number | null;
  share_age_15_29_start: number | null;
  metro_distance_m_start: number | null;
  metro_access_count_500m_start: number | null;
  metro_access_count_1000m_start: number | null;
  avisos_barrio_per_1000_prev_year: number | null;
  avisos_district_per_1000_prev_year: number | null;
  section_local_count_start: number | null;
  section_unique_activity_category_count_start: number | null;
  section_turnover_rate_12m_start: number | null;
  section_same_activity_category_share_start: number | null;
  best_activity_label: string;
  best_activity_risk: number | null;
  best_activity_survival_24m: number | null;
  top_activities: OpportunityActivity[];
};

export type OpportunitySection = {
  section_key: string;
  district_code: string;
  district_name: string;
  barrio_code: string;
  barrio_name: string;
  centroid_lat: number | null;
  centroid_lon: number | null;
  risk_score: number;
  risk_percentile: number;
  expected_survival_12m: number | null;
  expected_survival_24m: number | null;
  opportunity_tier: string;
  city_rank: number;
  city_total_sections: number;
  district_rank: number;
  district_total_sections: number;
  barrio_rank: number;
  barrio_total_sections: number;
  renta_effective_eur: number | null;
  total_population_start: number | null;
  population_density_km2_start: number | null;
  age_mean_start: number | null;
  share_foreign_start: number | null;
  share_age_15_29_start: number | null;
  metro_distance_m_start: number | null;
  metro_access_count_500m_start: number | null;
  metro_access_count_1000m_start: number | null;
  avisos_barrio_per_1000_prev_year: number | null;
  avisos_district_per_1000_prev_year: number | null;
  section_local_count_start: number | null;
  section_unique_activity_category_count_start: number | null;
  section_turnover_rate_12m_start: number | null;
  section_same_activity_category_share_start: number | null;
  best_activity_label: string;
  best_activity_risk: number | null;
  best_activity_survival_24m: number | null;
  top_activities: OpportunityActivity[];
};

export type OpportunitySectionFeature = {
  type: "Feature";
  geometry: {
    type: "Polygon" | "MultiPolygon";
    coordinates: unknown;
  };
  properties: OpportunitySection;
};

export type OpportunitySectionFeatureCollection = {
  type: "FeatureCollection";
  features: OpportunitySectionFeature[];
};

export type OpportunityManualSelection = {
  lat: number;
  lng: number;
  section: OpportunitySection;
};

export type OpportunityArtifacts = {
  meta: OpportunityMeta;
  filters: OpportunityFilters;
  stats: OpportunityStats;
  points: OpportunityPoint[];
};