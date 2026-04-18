export default {
  fetch(request: Request) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: noStoreHeaders(),
      });
    }

    if (request.method !== "GET") {
      return jsonResponse(
        {
          ok: false,
          error: "Metodo no permitido.",
        },
        { status: 405 }
      );
    }

    return GET(request);
  },
};

type NominatimAddress = {
  road?: string;
  pedestrian?: string;
  footway?: string;
  path?: string;
  house_number?: string;
  city?: string;
  city_district?: string;
  town?: string;
  village?: string;
  municipality?: string;
  county?: string;
  district?: string;
  suburb?: string;
  neighbourhood?: string;
  quarter?: string;
  postcode?: string;
  state?: string;
};

type NominatimRecord = {
  lat: string;
  lon: string;
  display_name: string;
  importance?: number;
  class?: string;
  type?: string;
  address?: NominatimAddress;
};

type RankedCandidate = {
  candidate: NominatimRecord;
  score: number;
  streetCoverage: number;
  displayCoverage: number;
  numberMatched: boolean;
  inMadrid: boolean;
};

const NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search";
const NOMINATIM_LIMIT = 8;
const NOMINATIM_RETRY_DELAYS_MS = [450, 1200];
const MIN_QUERY_LENGTH = 4;
const MAX_QUERY_LENGTH = 220;
const RETRYABLE_NOMINATIM_STATUS = new Set([408, 409, 425, 429, 500, 502, 503, 504]);

const MADRID_VIEWBOX = {
  west: -3.888,
  south: 40.312,
  east: -3.517,
  north: 40.643,
};

const STREET_STOP_WORDS = new Set([
  "de",
  "del",
  "la",
  "el",
  "los",
  "las",
  "y",
  "en",
  "con",
  "a",
  "al",
  "madrid",
  "espana",
  "españa",
  "cp",
]);

const LOCALITY_KEYS: Array<keyof NominatimAddress> = [
  "city",
  "town",
  "village",
  "municipality",
  "county",
  "district",
  "suburb",
  "neighbourhood",
  "quarter",
  "state",
];

const STREET_KEYS: Array<keyof NominatimAddress> = ["road", "pedestrian", "footway", "path"];

class NominatimRequestError extends Error {
  status: number | null;

  constructor(status: number | null) {
    super(status === null ? "Nominatim request failed" : `Nominatim request failed with HTTP ${status}`);
    this.status = status;
    this.name = "NominatimRequestError";
  }
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const rawQuery = (searchParams.get("q") ?? "").trim();

  if (rawQuery.length < MIN_QUERY_LENGTH) {
    return jsonResponse(
      {
        ok: false,
        error: "Escribe al menos calle y número para buscar con precisión.",
      },
      { status: 400, headers: noStoreHeaders() }
    );
  }

  if (rawQuery.length > MAX_QUERY_LENGTH) {
    return jsonResponse(
      {
        ok: false,
        error: "La dirección es demasiado larga. Prueba una versión más corta.",
      },
      { status: 400, headers: noStoreHeaders() }
    );
  }

  const normalizedQuery = normalizeAddress(rawQuery);
  const queryStreetTokens = extractStreetTokens(normalizedQuery);
  const queryHouseNumber = extractHouseNumber(normalizedQuery);

  if (queryHouseNumber === null) {
    return jsonResponse(
      {
        ok: false,
        error: "Asegúrate de indicar la calle y el número para ubicarla con precisión.",
      },
      { status: 400, headers: noStoreHeaders() }
    );
  }

  if (queryStreetTokens.length === 0) {
    return jsonResponse(
      {
        ok: false,
        error: "No he podido identificar la calle. Incluye el nombre de vía (ejemplo: Calle Alcalá 120).",
      },
      { status: 400, headers: noStoreHeaders() }
    );
  }

  let candidates: NominatimRecord[] = [];
  try {
    candidates = await fetchNominatimCandidates(rawQuery);
  } catch (error) {
    const status = error instanceof NominatimRequestError ? error.status : null;
    const isRateLimited = status === 429;

    return jsonResponse(
      {
        ok: false,
        error: isRateLimited
          ? "Hay mucha demanda en el servicio de direcciones. Espera unos segundos y vuelve a intentarlo."
          : "El servicio de direcciones no está disponible ahora mismo. Inténtalo de nuevo en unos segundos.",
      },
      { status: isRateLimited ? 503 : 502, headers: noStoreHeaders() }
    );
  }

  if (candidates.length === 0) {
    return jsonResponse(
      {
        ok: false,
        error: "No encuentro esa dirección con suficiente precisión. Asegúrate de indicar calle y número.",
      },
      { status: 404, headers: noStoreHeaders() }
    );
  }

  const ranked = rankCandidates(candidates, queryStreetTokens, queryHouseNumber);
  if (ranked.length === 0) {
    return jsonResponse(
      {
        ok: false,
        error: "No hay coincidencias válidas para esa dirección.",
      },
      { status: 404, headers: noStoreHeaders() }
    );
  }

  const best = ranked[0];
  const second = ranked[1] ?? null;
  const hasAnyNumberMatched = ranked.some((candidate) => candidate.numberMatched);

  const minimumScore = 0.74;
  const minimumStreetCoverage = 0.7;
  const minimumFallbackStreetCoverage = queryStreetTokens.length >= 3 ? 0.92 : 0.95;
  const minimumFallbackDisplayCoverage = queryStreetTokens.length >= 3 ? 0.85 : 0.9;
  const canUseStreetLevelFallback = !best.numberMatched
    && !hasAnyNumberMatched
    && queryStreetTokens.length >= 2
    && best.inMadrid
    && best.streetCoverage >= minimumFallbackStreetCoverage
    && best.displayCoverage >= minimumFallbackDisplayCoverage;
  const isAmbiguousByScore = Boolean(
    second
      && second.score >= minimumScore
      && Math.abs(best.score - second.score) < 0.07
  );
  const sameAddressCluster = second
    ? candidatesLikelySameAddress(best.candidate, second.candidate)
    : false;
  const hasExactStreetAndNumber = best.numberMatched && best.streetCoverage >= 0.9;
  const isAmbiguous = isAmbiguousByScore && !sameAddressCluster && !hasExactStreetAndNumber && !canUseStreetLevelFallback;
  const meetsScoreThreshold = best.score >= minimumScore || canUseStreetLevelFallback;
  const hasEnoughNumberPrecision = best.numberMatched || canUseStreetLevelFallback;

  if (
    !best.inMadrid
    || !meetsScoreThreshold
    || best.streetCoverage < minimumStreetCoverage
    || !hasEnoughNumberPrecision
    || isAmbiguous
  ) {
    return jsonResponse(
      {
        ok: false,
        error: !best.numberMatched
          ? "No encuentro ese número en la calle indicada. Revisa el portal y vuelve a intentarlo."
          : "No hay una coincidencia suficientemente precisa. Asegúrate de indicar la calle y el número.",
      },
      { status: 404, headers: noStoreHeaders() }
    );
  }

  const lat = Number.parseFloat(best.candidate.lat);
  const lng = Number.parseFloat(best.candidate.lon);

  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    return jsonResponse(
      {
        ok: false,
        error: "La dirección encontrada no trae coordenadas válidas.",
      },
      { status: 502, headers: noStoreHeaders() }
    );
  }

  return jsonResponse(
    {
      ok: true,
      result: {
        lat,
        lng,
        display_name: buildCandidateLabel(best.candidate),
        confidence: classifyConfidence(best.score, queryHouseNumber !== null),
        street_match: round(best.streetCoverage, 4),
        display_match: round(best.displayCoverage, 4),
        number_match: best.numberMatched,
      },
    },
    { status: 200, headers: noStoreHeaders() }
  );
}

async function fetchNominatimCandidates(query: string): Promise<NominatimRecord[]> {
  const endpoint = new URL(NOMINATIM_SEARCH_URL);
  endpoint.searchParams.set("q", appendMadridContext(query));
  endpoint.searchParams.set("format", "jsonv2");
  endpoint.searchParams.set("addressdetails", "1");
  endpoint.searchParams.set("limit", String(NOMINATIM_LIMIT));
  endpoint.searchParams.set("countrycodes", "es");
  endpoint.searchParams.set("bounded", "1");
  endpoint.searchParams.set("viewbox", `${MADRID_VIEWBOX.west},${MADRID_VIEWBOX.north},${MADRID_VIEWBOX.east},${MADRID_VIEWBOX.south}`);

  let lastStatus: number | null = null;

  for (let attempt = 0; attempt <= NOMINATIM_RETRY_DELAYS_MS.length; attempt += 1) {
    try {
      const response = await fetch(endpoint, {
        method: "GET",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "Accept-Language": "es",
          "User-Agent": "Localízate/0.1 (opportunity address lookup)",
        },
      });

      if (response.ok) {
        const payload = (await response.json()) as unknown;
        if (!Array.isArray(payload)) {
          return [];
        }

        return payload.filter(isNominatimRecord);
      }

      lastStatus = response.status;

      const canRetryStatus = RETRYABLE_NOMINATIM_STATUS.has(response.status);
      const hasRetryLeft = attempt < NOMINATIM_RETRY_DELAYS_MS.length;
      if (!canRetryStatus || !hasRetryLeft) {
        break;
      }
    } catch {
      const hasRetryLeft = attempt < NOMINATIM_RETRY_DELAYS_MS.length;
      if (!hasRetryLeft) {
        break;
      }
    }

    await delayMs(NOMINATIM_RETRY_DELAYS_MS[attempt]);
  }

  throw new NominatimRequestError(lastStatus);
}

function rankCandidates(
  candidates: NominatimRecord[],
  queryStreetTokens: string[],
  queryHouseNumber: string | null,
): RankedCandidate[] {
  const ranked: RankedCandidate[] = [];

  for (const candidate of candidates) {
    const displayLabel = buildCandidateLabel(candidate);
    const displayTokens = new Set(tokenizeAddress(displayLabel));
    const streetName = getCandidateStreet(candidate) ?? displayLabel;
    const streetTokens = new Set(tokenizeAddress(streetName));

    const streetCoverage = tokenCoverage(queryStreetTokens, streetTokens);
    const displayCoverage = tokenCoverage(queryStreetTokens, displayTokens);
    const numberMatched = queryHouseNumber === null
      ? true
      : candidateMatchesHouseNumber(candidate, queryHouseNumber, displayLabel);
    const inMadrid = isCandidateInMadrid(candidate, displayLabel);
    const importance = clamp(Number(candidate.importance ?? 0), 0, 1);

    let score = (streetCoverage * 0.66) + (displayCoverage * 0.2) + (importance * 0.1);

    if (isBuildingLikeCandidate(candidate)) {
      score += 0.04;
    }

    if (queryHouseNumber !== null) {
      score += numberMatched ? 0.18 : -0.38;
    }

    if (!inMadrid) {
      score -= 0.5;
    }

    if (streetCoverage < 0.4) {
      score -= 0.25;
    }

    ranked.push({
      candidate,
      score,
      streetCoverage,
      displayCoverage,
      numberMatched,
      inMadrid,
    });
  }

  return ranked.sort((left, right) => right.score - left.score);
}

function buildCandidateLabel(candidate: NominatimRecord) {
  const street = getCandidateStreet(candidate)?.trim() ?? "";
  const houseNumber = normalizeHouseNumber(candidate.address?.house_number ?? null);
  const neighborhood = firstNonEmpty(
    candidate.address?.suburb,
    candidate.address?.neighbourhood,
    candidate.address?.quarter,
    candidate.address?.city_district,
    candidate.address?.district,
  );
  const city = firstNonEmpty(
    candidate.address?.city,
    candidate.address?.town,
    candidate.address?.village,
    candidate.address?.municipality,
    "Madrid",
  );
  const postcode = candidate.address?.postcode?.trim() ?? "";

  const streetPart = street
    ? `${street}${houseNumber ? ` ${houseNumber.toUpperCase()}` : ""}`
    : null;

  const parts = dedupeAddressParts([
    streetPart,
    neighborhood,
    city,
    postcode || null,
    "España",
  ]);

  if (parts.length > 0) {
    return parts.join(", ");
  }

  return stripPointOfInterestPrefix(candidate.display_name);
}

function firstNonEmpty(...values: Array<string | null | undefined>) {
  for (const value of values) {
    const trimmed = value?.trim();
    if (trimmed) {
      return trimmed;
    }
  }
  return null;
}

function dedupeAddressParts(parts: Array<string | null | undefined>) {
  const normalizedSeen = new Set<string>();
  const output: string[] = [];

  for (const part of parts) {
    const trimmed = part?.trim();
    if (!trimmed) {
      continue;
    }

    const normalized = normalizeAddress(trimmed);
    if (!normalized || normalizedSeen.has(normalized)) {
      continue;
    }

    normalizedSeen.add(normalized);
    output.push(trimmed);
  }

  return output;
}

function stripPointOfInterestPrefix(displayName: string) {
  const parts = displayName
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part.length > 0);

  if (parts.length <= 1) {
    return displayName.trim();
  }

  const [first, second] = parts;
  if (!first || !second) {
    return displayName.trim();
  }

  const firstHasNumber = /\d/.test(first);
  const secondLooksLikeStreet = /(calle|avenida|paseo|plaza|camino|carretera|ronda|\d)/i.test(second);

  if (!firstHasNumber && secondLooksLikeStreet) {
    return parts.slice(1).join(", ");
  }

  return displayName.trim();
}

function candidatesLikelySameAddress(left: NominatimRecord, right: NominatimRecord) {
  const leftStreet = normalizeAddress(getCandidateStreet(left) ?? "");
  const rightStreet = normalizeAddress(getCandidateStreet(right) ?? "");
  if (!leftStreet || !rightStreet || leftStreet !== rightStreet) {
    return false;
  }

  const leftHouse = normalizeHouseNumber(left.address?.house_number ?? null);
  const rightHouse = normalizeHouseNumber(right.address?.house_number ?? null);
  if (!leftHouse || !rightHouse) {
    return false;
  }

  if (stripHouseNumberSuffix(leftHouse) !== stripHouseNumberSuffix(rightHouse)) {
    return false;
  }

  const distanceMeters = distanceBetweenCandidatesMeters(left, right);
  if (distanceMeters === null) {
    return false;
  }

  return distanceMeters <= 60;
}

function distanceBetweenCandidatesMeters(left: NominatimRecord, right: NominatimRecord) {
  const leftLat = Number.parseFloat(left.lat);
  const leftLng = Number.parseFloat(left.lon);
  const rightLat = Number.parseFloat(right.lat);
  const rightLng = Number.parseFloat(right.lon);

  if (!Number.isFinite(leftLat) || !Number.isFinite(leftLng) || !Number.isFinite(rightLat) || !Number.isFinite(rightLng)) {
    return null;
  }

  const earthRadiusMeters = 6_371_000;
  const lat1 = toRadians(leftLat);
  const lat2 = toRadians(rightLat);
  const deltaLat = toRadians(rightLat - leftLat);
  const deltaLng = toRadians(rightLng - leftLng);

  const a = Math.sin(deltaLat / 2) ** 2
    + Math.cos(lat1) * Math.cos(lat2) * (Math.sin(deltaLng / 2) ** 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return earthRadiusMeters * c;
}

function toRadians(value: number) {
  return value * (Math.PI / 180);
}

function isBuildingLikeCandidate(candidate: NominatimRecord) {
  const kind = `${candidate.class ?? ""}:${candidate.type ?? ""}`.toLowerCase();
  return kind.includes("building") || kind.includes("house");
}

function isCandidateInMadrid(candidate: NominatimRecord, displayLabel: string) {
  const localityText = LOCALITY_KEYS
    .map((key) => candidate.address?.[key] ?? "")
    .filter(Boolean)
    .join(" ");

  const localityTokens = tokenizeAddress(localityText);
  if (localityTokens.includes("madrid")) {
    return true;
  }

  return tokenizeAddress(displayLabel).includes("madrid");
}

function getCandidateStreet(candidate: NominatimRecord) {
  for (const key of STREET_KEYS) {
    const value = candidate.address?.[key];
    if (value) {
      return value;
    }
  }
  return null;
}

function appendMadridContext(query: string) {
  const normalized = normalizeAddress(query);
  const hasMadrid = normalized.includes("madrid");
  if (hasMadrid) {
    return normalized;
  }
  return `${normalized} madrid espana`;
}

function candidateMatchesHouseNumber(candidate: NominatimRecord, expectedHouseNumber: string, displayLabel: string) {
  const candidates = new Set<string>();

  const fromAddress = normalizeHouseNumber(candidate.address?.house_number ?? null);
  if (fromAddress) {
    candidates.add(fromAddress);
  }

  const fromDisplay = extractHouseNumber(normalizeAddress(displayLabel));
  if (fromDisplay) {
    candidates.add(fromDisplay);
  }

  if (candidates.size === 0) {
    return false;
  }

  const expectedBase = stripHouseNumberSuffix(expectedHouseNumber);

  for (const observed of candidates) {
    if (observed === expectedHouseNumber) {
      return true;
    }

    if (stripHouseNumberSuffix(observed) === expectedBase) {
      return true;
    }
  }

  return false;
}

function stripHouseNumberSuffix(value: string) {
  return value.replace(/[a-z]$/i, "");
}

function extractStreetTokens(normalizedAddress: string) {
  return tokenizeAddress(normalizedAddress).filter((token) => {
    if (STREET_STOP_WORDS.has(token)) {
      return false;
    }
    if (/^\d+[a-z]?$/.test(token)) {
      return false;
    }
    return token.length >= 2;
  });
}

function tokenCoverage(queryTokens: string[], candidateTokens: Set<string>) {
  if (queryTokens.length === 0 || candidateTokens.size === 0) {
    return 0;
  }

  const candidateList = [...candidateTokens];
  let matches = 0;

  for (const token of queryTokens) {
    const matched = candidateTokens.has(token)
      || candidateList.some((candidateToken) => {
        if (token.length <= 2 || candidateToken.length <= 2) {
          return false;
        }
        return candidateToken.startsWith(token) || token.startsWith(candidateToken);
      });

    if (matched) {
      matches += 1;
    }
  }

  return matches / queryTokens.length;
}

function extractHouseNumber(normalizedAddress: string) {
  const tokens = tokenizeAddress(normalizedAddress);
  for (const token of tokens) {
    if (/^\d{1,4}[a-z]?$/.test(token)) {
      return token;
    }
  }
  return null;
}

function normalizeHouseNumber(value: string | null) {
  if (!value) {
    return null;
  }

  const compact = normalizeAddress(value).replace(/\s+/g, "");
  if (!compact) {
    return null;
  }

  const match = compact.match(/\d{1,4}[a-z]?/);
  return match?.[0] ?? null;
}

function normalizeAddress(value: string) {
  const withoutAccents = value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();

  return withoutAccents
    .replace(/\b(c\/|c\.|cl\.)\s*/g, " calle ")
    .replace(/\b(avda\.?|av\.)\b/g, " avenida ")
    .replace(/\b(plz\.?|pl\.)\b/g, " plaza ")
    .replace(/\b(ps\.?|pso\.?)\b/g, " paseo ")
    .replace(/\bp[ºo]\b/g, " paseo ")
    .replace(/\bp\b(?=\s+de\b)/g, " paseo ")
    .replace(/\bn[ºo]?\b/g, " ")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function tokenizeAddress(value: string) {
  if (!value) {
    return [];
  }

  return normalizeAddress(value)
    .split(" ")
    .map((token) => canonicalizeToken(token))
    .filter((token) => token.length > 0);
}

function canonicalizeToken(token: string) {
  const clean = token.replace(/\./g, "");

  if (clean === "c" || clean === "cl" || clean === "calle") {
    return "calle";
  }

  if (clean === "av" || clean === "avenida" || clean === "avda") {
    return "avenida";
  }

  if (clean === "pl" || clean === "plaza") {
    return "plaza";
  }

  if (clean === "p" || clean === "ps" || clean === "pso" || clean === "paseo") {
    return "paseo";
  }

  return clean;
}

function classifyConfidence(score: number, hasHouseNumber: boolean) {
  if (hasHouseNumber) {
    if (score >= 0.9) {
      return "high";
    }
    return "medium";
  }

  return score >= 0.8 ? "high" : "medium";
}

function isNominatimRecord(value: unknown): value is NominatimRecord {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as Partial<NominatimRecord>;
  return typeof candidate.lat === "string"
    && typeof candidate.lon === "string"
    && typeof candidate.display_name === "string";
}

function round(value: number, decimals: number) {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function delayMs(ms: number) {
  return new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });
}

function noStoreHeaders() {
  return {
    "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Vary": "Origin",
  };
}

function jsonResponse(body: unknown, init: ResponseInit = {}) {
  const headers = new Headers(init.headers);
  const defaultHeaders = noStoreHeaders();
  for (const [key, value] of Object.entries(defaultHeaders)) {
    if (!headers.has(key)) {
      headers.set(key, value);
    }
  }
  headers.set("Content-Type", "application/json; charset=utf-8");

  return new Response(JSON.stringify(body), {
    ...init,
    headers,
  });
}
