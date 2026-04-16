import type { OpportunityArtifacts } from "@/lib/types"

const ABSOLUTE_URL_PATTERN = /^[a-zA-Z][a-zA-Z\d+\-.]*:\/\//

function trimTrailingSlashes(value: string) {
  return value.replace(/\/+$/, "")
}

export const PUBLIC_DATA_BASE_URL = trimTrailingSlashes(process.env.NEXT_PUBLIC_DATA_BASE_URL?.trim() ?? "")
export const HAS_EXTERNAL_PUBLIC_DATA_BASE_URL = PUBLIC_DATA_BASE_URL.length > 0

export const OPPORTUNITY_GEOCODE_ENDPOINT =
  (process.env.NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT?.trim() ?? "") || "/api/geocode/opportunity-address"

export function resolvePublicAssetUrl(path: string) {
  if (!path || ABSOLUTE_URL_PATTERN.test(path) || !HAS_EXTERNAL_PUBLIC_DATA_BASE_URL) {
    return path
  }

  const normalizedBase = `${PUBLIC_DATA_BASE_URL}/`
  const normalizedPath = path.startsWith("/") ? path.slice(1) : path
  return new URL(normalizedPath, normalizedBase).toString()
}

export function buildOpportunityGeocodeUrl(query: string) {
  if (ABSOLUTE_URL_PATTERN.test(OPPORTUNITY_GEOCODE_ENDPOINT)) {
    const url = new URL(OPPORTUNITY_GEOCODE_ENDPOINT)
    url.searchParams.set("q", query)
    return url.toString()
  }

  const url = new URL(OPPORTUNITY_GEOCODE_ENDPOINT, "https://localizate.invalid")
  url.searchParams.set("q", query)
  return `${url.pathname}${url.search}${url.hash}`
}

export function normalizeOpportunityArtifactUrls(artifacts: OpportunityArtifacts): OpportunityArtifacts {
  return {
    ...artifacts,
    meta: {
      ...artifacts.meta,
      section_index_path: resolvePublicAssetUrl(artifacts.meta.section_index_path),
      section_geojson_path: resolvePublicAssetUrl(artifacts.meta.section_geojson_path),
    },
  }
}
