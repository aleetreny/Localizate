import type { FrontendArtifacts, OpportunityArtifacts } from "@/lib/types";

export const MAP_ARTIFACTS_PATH = "/data/frontend-map-artifacts.json";
export const OPPORTUNITY_ARTIFACTS_PATH = "/data/frontend-opportunity-artifacts.json";
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

let mapArtifactsPromise: Promise<FrontendArtifacts> | null = null;
let opportunityArtifactsPromise: Promise<OpportunityArtifacts> | null = null;

export function loadMapArtifactsFromPublic() {
  if (!IS_PRODUCTION) {
    return fetchPublicJson(MAP_ARTIFACTS_PATH, FALLBACK_MAP_ARTIFACTS);
  }
  mapArtifactsPromise ??= fetchPublicJson(MAP_ARTIFACTS_PATH, FALLBACK_MAP_ARTIFACTS);
  return mapArtifactsPromise;
}

export function loadOpportunityArtifactsFromPublic() {
  if (!IS_PRODUCTION) {
    return fetchPublicJson(OPPORTUNITY_ARTIFACTS_PATH, FALLBACK_OPPORTUNITY_ARTIFACTS);
  }
  opportunityArtifactsPromise ??= fetchPublicJson(OPPORTUNITY_ARTIFACTS_PATH, FALLBACK_OPPORTUNITY_ARTIFACTS);
  return opportunityArtifactsPromise;
}

export function prefetchArtifactsForView(href: string) {
  if (href === "/") {
    void loadMapArtifactsFromPublic();
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