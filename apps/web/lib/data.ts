import { promises as fs } from "fs";
import path from "path";

import type { FrontendArtifacts } from "@/lib/types";

const DATA_DIR = path.join(process.cwd(), "public", "data");

const FALLBACK_ARTIFACTS: FrontendArtifacts = {
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

export async function loadMapArtifacts(): Promise<FrontendArtifacts> {
  const filePath = path.join(DATA_DIR, "frontend-map-artifacts.json");

  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as FrontendArtifacts;
  } catch {
    return FALLBACK_ARTIFACTS;
  }
}