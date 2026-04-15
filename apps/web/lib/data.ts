import { promises as fs } from "fs";
import path from "path";

import { DEFAULT_HEX_SIZE, type HexSize } from "@/lib/hex-size";
import type { FrontendArtifacts, OpportunityArtifacts } from "@/lib/types";

const DATA_DIR = path.join(process.cwd(), "public", "data");
const MAP_ARTIFACT_FILE_NAMES: Record<HexSize, string> = {
  small: "frontend-map-artifacts.json",
  medium: "frontend-map-artifacts-medium.json",
  large: "frontend-map-artifacts-large.json"
};

const FALLBACK_ARTIFACTS: FrontendArtifacts = {
  meta: {
    title: "Mapa de supervivencia comercial de Madrid",
    subtitle: "Datos de la web pendientes de materializar. Ejecuta el generador estático para poblar el mapa.",
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

const FALLBACK_OPPORTUNITY_ARTIFACTS: OpportunityArtifacts = {
  meta: {
    title: "Mapa de oportunidades de Madrid",
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

export async function loadMapArtifacts(hexSize: HexSize = DEFAULT_HEX_SIZE): Promise<FrontendArtifacts> {
  const filePath = path.join(DATA_DIR, MAP_ARTIFACT_FILE_NAMES[hexSize]);

  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as FrontendArtifacts;
  } catch {
    return FALLBACK_ARTIFACTS;
  }
}

export async function loadOpportunityArtifacts(): Promise<OpportunityArtifacts> {
  const filePath = path.join(DATA_DIR, "frontend-opportunity-artifacts.json");

  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as OpportunityArtifacts;
  } catch {
    return FALLBACK_OPPORTUNITY_ARTIFACTS;
  }
}
