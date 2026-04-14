import { DEFAULT_HEX_SIZE, type HexSize } from "@/lib/hex-size";
import type {
  FrontendArtifacts,
  HexCompositionHistoryArtifacts,
  HistoricalRankingArtifacts,
  OpportunityArtifacts,
  ZoneBoundaryArtifacts,
} from "@/lib/types";

export const MAP_ARTIFACTS_PATHS: Record<HexSize, string> = {
  small: "/data/frontend-map-artifacts.json",
  medium: "/data/frontend-map-artifacts-medium.json",
  large: "/data/frontend-map-artifacts-large.json"
};
export const OPPORTUNITY_ARTIFACTS_PATH = "/data/frontend-opportunity-artifacts.json";
export const HISTORICAL_RANKING_ARTIFACTS_PATH = "/data/frontend-historical-rankings.json";
export const HEX_COMPOSITION_HISTORY_ARTIFACTS_PATH = "/data/frontend-hex-composition-history.json";
export const ZONE_BOUNDARY_ARTIFACTS_PATH = "/data/frontend-zone-boundaries.json";
const IS_PRODUCTION = process.env.NODE_ENV === "production";

export const FALLBACK_MAP_ARTIFACTS: FrontendArtifacts = {
  meta: {
    title: "Madrid Survival Grid",
    subtitle: "Datos frontend pendientes de materializar. Ejecuta el builder estático para poblar el mapa.",
    generated_at: new Date(0).toISOString(),
    defaultCategoryCode: "__all__",
    map_bounds: {
      min_lng: -3.888,
      min_lat: 40.312,
      max_lng: -3.517,
      max_lat: 40.643,
      min_zoom: 9.8,
      max_zoom: 15.4
    }
  },
  categories: [
    {
      category_code: "__all__",
      category_desc: "Todos los locales",
      n_locales: 0,
      n_hexes: 0
    }
  ],
  hexes: [],
  zones: {
    district: [],
    barrio: []
  }
};

export const FALLBACK_OPPORTUNITY_ARTIFACTS: OpportunityArtifacts = {
  meta: {
    title: "Madrid Opportunity Map",
    subtitle: "Locales disponibles y recomendación de actividad",
    generated_at: new Date(0).toISOString(),
    section_geojson_path: "/data/frontend-opportunity-sections.geojson",
    map_bounds: {
      min_lng: -3.888,
      min_lat: 40.312,
      max_lng: -3.517,
      max_lat: 40.643,
      min_zoom: 9.8,
      max_zoom: 16.2
    }
  },
  filters: {
    total_listings: 0,
    precise_candidates: 0,
    selected_listings: 0,
    excluded_incomplete: 0,
    excluded_outliers: 0,
    operations: {}
  },
  stats: {
    selected_listings: 0,
    districts: 0,
    barrios: 0,
    median_survival_24m: null,
    median_price_per_m2: null
  },
  points: []
};

export const FALLBACK_HISTORICAL_RANKING_ARTIFACTS: HistoricalRankingArtifacts = {
  meta: {
    title: "Madrid Historical Category Ranking",
    subtitle: "Artefacto temporal pendiente de materializar.",
    generated_at: new Date(0).toISOString(),
    metric_key: "specialization_index",
    metric_label: "Indice de especializacion",
    metric_short_label: "Especializacion vs Madrid",
    metric_definition: "Cuota suavizada de la categoria en la zona comparada con la cuota de esa categoria en Madrid.",
    metric_direction: "higher_better",
    smoothing_weight: 12,
    years: [],
    latest_period_by_year: {},
    latest_year: 0,
    latest_period: "",
    latest_year_is_partial: false,
    current_series_limit: 4,
    series_limit: 12,
    rank_focus_limit: 12,
    zone_totals: {
      district: 0,
      barrio: 0,
    }
  },
  zones: {
    district: [],
    barrio: []
  }
};

export const FALLBACK_HEX_COMPOSITION_HISTORY_ARTIFACTS: HexCompositionHistoryArtifacts = {
  meta: {
    title: "Madrid Historical Hex Composition",
    subtitle: "Artefacto temporal pendiente de materializar.",
    generated_at: new Date(0).toISOString(),
    years: [],
    latest_period_by_year: {},
    latest_year: 0,
    latest_period: "",
    latest_year_is_partial: false,
  },
  hexes: [],
};

export const FALLBACK_ZONE_BOUNDARY_ARTIFACTS: ZoneBoundaryArtifacts = {
  meta: {
    title: "Madrid Zone Boundaries",
    subtitle: "Limites administrativos pendientes de materializar.",
    generated_at: new Date(0).toISOString(),
  },
  zones: {
    district: {
      type: "FeatureCollection",
      features: [],
    },
    barrio: {
      type: "FeatureCollection",
      features: [],
    },
  },
};

const mapArtifactsPromises = new Map<HexSize, Promise<FrontendArtifacts>>();
let opportunityArtifactsPromise: Promise<OpportunityArtifacts> | null = null;
let historicalRankingArtifactsPromise: Promise<HistoricalRankingArtifacts> | null = null;
let hexCompositionHistoryArtifactsPromise: Promise<HexCompositionHistoryArtifacts> | null = null;
let zoneBoundaryArtifactsPromise: Promise<ZoneBoundaryArtifacts> | null = null;

export function loadMapArtifactsFromPublic(hexSize: HexSize = DEFAULT_HEX_SIZE) {
  const path = MAP_ARTIFACTS_PATHS[hexSize];

  if (!IS_PRODUCTION) {
    return fetchPublicJson(path, FALLBACK_MAP_ARTIFACTS);
  }

  const cached = mapArtifactsPromises.get(hexSize);
  if (cached) {
    return cached;
  }

  const promise = fetchPublicJson(path, FALLBACK_MAP_ARTIFACTS);
  mapArtifactsPromises.set(hexSize, promise);
  return promise;
}

export function loadOpportunityArtifactsFromPublic() {
  if (!IS_PRODUCTION) {
    return fetchPublicJson(OPPORTUNITY_ARTIFACTS_PATH, FALLBACK_OPPORTUNITY_ARTIFACTS);
  }
  opportunityArtifactsPromise ??= fetchPublicJson(OPPORTUNITY_ARTIFACTS_PATH, FALLBACK_OPPORTUNITY_ARTIFACTS);
  return opportunityArtifactsPromise;
}

export function loadHistoricalRankingsFromPublic() {
  if (!IS_PRODUCTION) {
    return fetchPublicJson(HISTORICAL_RANKING_ARTIFACTS_PATH, FALLBACK_HISTORICAL_RANKING_ARTIFACTS);
  }

  historicalRankingArtifactsPromise ??= fetchPublicJson(
    HISTORICAL_RANKING_ARTIFACTS_PATH,
    FALLBACK_HISTORICAL_RANKING_ARTIFACTS
  );
  return historicalRankingArtifactsPromise;
}

export function loadHexCompositionHistoryFromPublic() {
  if (!IS_PRODUCTION) {
    return fetchPublicJson(HEX_COMPOSITION_HISTORY_ARTIFACTS_PATH, FALLBACK_HEX_COMPOSITION_HISTORY_ARTIFACTS);
  }

  hexCompositionHistoryArtifactsPromise ??= fetchPublicJson(
    HEX_COMPOSITION_HISTORY_ARTIFACTS_PATH,
    FALLBACK_HEX_COMPOSITION_HISTORY_ARTIFACTS
  );
  return hexCompositionHistoryArtifactsPromise;
}

export function loadZoneBoundariesFromPublic() {
  if (!IS_PRODUCTION) {
    return fetchPublicJson(ZONE_BOUNDARY_ARTIFACTS_PATH, FALLBACK_ZONE_BOUNDARY_ARTIFACTS);
  }

  zoneBoundaryArtifactsPromise ??= fetchPublicJson(
    ZONE_BOUNDARY_ARTIFACTS_PATH,
    FALLBACK_ZONE_BOUNDARY_ARTIFACTS
  );
  return zoneBoundaryArtifactsPromise;
}

export function prefetchArtifactsForView(href: string) {
  if (href === "/") {
    void loadMapArtifactsFromPublic();
    void loadZoneBoundariesFromPublic();
    return;
  }

  if (href === "/oportunidades") {
    void loadOpportunityArtifactsFromPublic();
  }
}

async function fetchPublicJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(path, { cache: IS_PRODUCTION ? "force-cache" : "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}
