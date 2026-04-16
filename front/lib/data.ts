import { promises as fs } from "fs";
import path from "path";

import { DEFAULT_HEX_SIZE, type HexSize } from "@/lib/hex-size";
import { normalizeOpportunityArtifactUrls, resolvePublicAssetUrl } from "@/lib/runtime-config";
import type {
  FrontendArtifacts,
  MapHexArtifacts,
  MapSharedArtifacts,
  OpportunityArtifacts,
  OpportunitySectionIndexArtifacts,
  ZoneBoundaryArtifacts,
} from "@/lib/types";

const DATA_DIR = path.join(process.cwd(), "public", "data");
const MAP_SHARED_FILE_PATH = path.join(DATA_DIR, "map", "shared.json");
const MAP_HEX_FILE_NAMES: Record<HexSize, string> = {
  small: path.join("map", "hex", "small.json"),
  medium: path.join("map", "hex", "medium.json"),
  large: path.join("map", "hex", "large.json"),
};

const FALLBACK_SHARED_ARTIFACTS: MapSharedArtifacts = {
  meta: {
    title: "Mapa de supervivencia comercial de Madrid",
    subtitle: "Datos de la web pendientes de materializar. Ejecuta el generador estatico para poblar el mapa.",
    generated_at: new Date(0).toISOString(),
    defaultCategoryCode: "__all__",
    map_bounds: {
      min_lng: -3.888,
      min_lat: 40.312,
      max_lng: -3.517,
      max_lat: 40.643,
      min_zoom: 9.8,
      max_zoom: 15.4,
    },
  },
  categories: [
    {
      category_code: "__all__",
      category_desc: "Todos los locales",
      n_locales: 0,
      n_hexes: 0,
    },
  ],
  zones: {
    district: [],
    barrio: [],
  },
};

const FALLBACK_HEX_ARTIFACTS: MapHexArtifacts = {
  meta: {
    generated_at: new Date(0).toISOString(),
    hex_size: DEFAULT_HEX_SIZE,
    h3_resolution: 0,
    hex_area_km2: 0,
  },
  hexes: [],
};

const FALLBACK_OPPORTUNITY_ARTIFACTS: OpportunityArtifacts = {
  meta: {
    title: "Mapa de oportunidades de Madrid",
    subtitle: "Locales disponibles y recomendacion de actividad",
    generated_at: new Date(0).toISOString(),
    section_index_path: resolvePublicAssetUrl("/data/opportunities/sections/index.json"),
    section_geojson_path: resolvePublicAssetUrl("/data/opportunities/sections/geometry.geojson"),
    map_bounds: {
      min_lng: -3.888,
      min_lat: 40.312,
      max_lng: -3.517,
      max_lat: 40.643,
      min_zoom: 9.8,
      max_zoom: 16.2,
    },
  },
  filters: {
    total_listings: 0,
    precise_candidates: 0,
    selected_listings: 0,
    excluded_incomplete: 0,
    excluded_outliers: 0,
    operations: {},
  },
  stats: {
    selected_listings: 0,
    districts: 0,
    barrios: 0,
    median_survival_24m: null,
    median_price_per_m2: null,
  },
  points: [],
};

const FALLBACK_OPPORTUNITY_SECTION_INDEX_ARTIFACTS: OpportunitySectionIndexArtifacts = {
  meta: {
    generated_at: new Date(0).toISOString(),
  },
  sections: [],
};

const FALLBACK_ZONE_BOUNDARY_ARTIFACTS: ZoneBoundaryArtifacts = {
  meta: {
    title: "Limites territoriales de Madrid",
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

export async function loadMapSharedArtifacts(): Promise<MapSharedArtifacts> {
  try {
    const raw = await fs.readFile(MAP_SHARED_FILE_PATH, "utf-8");
    return JSON.parse(raw) as MapSharedArtifacts;
  } catch {
    return FALLBACK_SHARED_ARTIFACTS;
  }
}

export async function loadMapArtifacts(hexSize: HexSize = DEFAULT_HEX_SIZE): Promise<FrontendArtifacts> {
  try {
    const [sharedArtifacts, hexRaw] = await Promise.all([
      loadMapSharedArtifacts(),
      fs.readFile(path.join(DATA_DIR, MAP_HEX_FILE_NAMES[hexSize]), "utf-8"),
    ]);

    const hexArtifacts = JSON.parse(hexRaw) as MapHexArtifacts;
    return {
      ...sharedArtifacts,
      hexes: hexArtifacts.hexes,
    };
  } catch {
    return {
      ...FALLBACK_SHARED_ARTIFACTS,
      hexes: FALLBACK_HEX_ARTIFACTS.hexes,
    };
  }
}

export async function loadOpportunityArtifacts(): Promise<OpportunityArtifacts> {
  const filePath = path.join(DATA_DIR, "opportunities", "listings.json");

  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return normalizeOpportunityArtifactUrls(JSON.parse(raw) as OpportunityArtifacts);
  } catch {
    return FALLBACK_OPPORTUNITY_ARTIFACTS;
  }
}

export async function loadOpportunitySectionIndexArtifacts(): Promise<OpportunitySectionIndexArtifacts> {
  const filePath = path.join(DATA_DIR, "opportunities", "sections", "index.json");

  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as OpportunitySectionIndexArtifacts;
  } catch {
    return FALLBACK_OPPORTUNITY_SECTION_INDEX_ARTIFACTS;
  }
}

export async function loadZoneBoundaryArtifacts(): Promise<ZoneBoundaryArtifacts> {
  const filePath = path.join(DATA_DIR, "map", "zones", "boundaries.json");

  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as ZoneBoundaryArtifacts;
  } catch {
    return FALLBACK_ZONE_BOUNDARY_ARTIFACTS;
  }
}
