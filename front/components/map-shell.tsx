"use client";

import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";

import { HexCategoryComposition, type HexCategoryCompositionItem } from "@/components/hex-category-composition";
import { HistoricalEvolutionBanner } from "@/components/historical-evolution-banner";
import { MadridMap } from "@/components/madrid-map";
import { ViewTabs } from "@/components/view-tabs";
import { ZoneComparisonBanner } from "@/components/zone-comparison-banner";
import { DEFAULT_HEX_SIZE, formatHexSizeLabel, HEX_SIZE_OPTIONS, type HexSize } from "@/lib/hex-size";
import { formatHorizonLongLabel, formatHorizonShortLabel, getHorizonSupport, getHorizonSurvival, isFiniteNumber, type Horizon } from "@/lib/horizon";
import {
  FALLBACK_MAP_ARTIFACTS,
  loadHexCompositionHistoryFromPublic,
  loadHistoricalRankingsFromPublic,
  loadMapArtifactsFromPublic,
  loadMapSharedArtifactsFromPublic,
  loadZoneBoundariesFromPublic,
} from "@/lib/public-data";
import type {
  ColorScale,
  FrontendArtifacts,
  HexAggregate,
  HexCompositionHistoryArtifacts,
  HexCompositionHistoryRecord,
  HistoricalRankingArtifacts,
  HistoricalZoneLevel,
  HistoricalZoneRankingRecord,
  ZoneAggregate,
  ZoneBoundaryArtifacts,
} from "@/lib/types";

type MapShellProps = {
  initialArtifacts?: FrontendArtifacts;
  initialZoneBoundaries?: ZoneBoundaryArtifacts;
};

type MetricDefinition = {
  id: string;
  label: string;
  value: string;
  summary: string;
  calculation: string;
};

type MapViewMode = HistoricalZoneLevel | "hex";

type ZoneListProps = {
  districtZones: ZoneAggregate[];
  barrioZones: ZoneAggregate[];
  onSelectZone: (zone: ZoneAggregate) => void;
};

type RiskAggregate = {
  avg_risk_primary?: number;
  avg_risk_ensemble: number;
};

type ZoneActivityRankingItem = {
  rank: number;
  categoryCode: string;
  categoryDesc: string;
  riskIndex: number | null;
  survival: number | null;
  nLocales: number;
  support: number;
};

type ZoneActivityRankingRow = Omit<ZoneActivityRankingItem, "rank"> & {
  globalRank: number;
  activityRisk: number;
  eventRate: number | null;
};

type ZoneActivityInsight = {
  zoneLevel: ZoneAggregate["zone_level"];
  zoneCode: string;
  zoneName: string;
  horizon: Horizon;
  totalActivities: number;
  currentCategoryDesc: string;
  currentCategoryRank: number | null;
  items: ZoneActivityRankingItem[];
};

type ZoneComparisonOption = {
  label: string;
  zoneKey: string;
};

type CategoryOption = FrontendArtifacts["categories"][number];

type PickerOption = {
  label: string;
  value: string;
};

type HexCategoryColorStats = {
  nLocales: number;
};

type MapAggregateMetrics = {
  avg_risk_percentile: number;
  n_locales: number;
  support_12m: number;
  support_24m: number;
  survival_12m: number | null;
  survival_24m: number | null;
};

type VisibleStats = {
  locales: number;
  meanRelativeRisk: number | null;
  meanSurvival: number | null;
  units: number;
  unitsWithSupport: number;
};

type ZoneCompositionHistoryIndex = {
  byCode: Map<string, HistoricalZoneRankingRecord[]>;
  byIdentity: Map<string, HistoricalZoneRankingRecord[]>;
};

const HEX_COMPOSITION_YEAR_MIN = 2015;
const HEX_COMPOSITION_YEAR_MAX = 2026;
const MIN_UNSUPPORTED_BARRIO_LOCALES = 5;
const MIN_UNSUPPORTED_DISTRICT_LOCALES = 10;
const DISTRICT_COLOR_FLOOR_MIN = 4;
const DISTRICT_COLOR_FLOOR_MAX = 24;
const BARRIO_COLOR_FLOOR_MIN = 2;
const BARRIO_COLOR_FLOOR_MAX = 16;
const ZONE_COLOR_FLOOR_QUANTILE = 0.2;
const ZONE_ACTIVITY_VISIBLE_LIMIT = 5;
const ZONE_ACTIVITY_PRIOR_STRENGTH = 25;
const ZONE_ACTIVITY_UNSUPPORTED_PENALTY = 0.03;
const ZONE_ACTIVITY_DEFAULT_PRIOR_EVENT_RATE = 0.15;

export function MapShell({ initialArtifacts, initialZoneBoundaries }: MapShellProps) {
  const [artifacts, setArtifacts] = useState(initialArtifacts ?? FALLBACK_MAP_ARTIFACTS);
  const [isLoadingArtifacts, setIsLoadingArtifacts] = useState(!initialArtifacts);
  const [isSwitchingHexSize, setIsSwitchingHexSize] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState((initialArtifacts ?? FALLBACK_MAP_ARTIFACTS).meta.defaultCategoryCode);
  const horizon: Horizon = "24m";
  const [mapViewMode, setMapViewMode] = useState<MapViewMode>("district");
  const [hexSize, setHexSize] = useState<HexSize>(DEFAULT_HEX_SIZE);
  const [selectedHex, setSelectedHex] = useState<HexAggregate | null>(null);
  const [selectedZone, setSelectedZone] = useState<ZoneAggregate | null>(null);
  const [activeMetricId, setActiveMetricId] = useState<string | null>(null);
  const [isRiskExplainerOpen, setIsRiskExplainerOpen] = useState(false);
  const [activeZoneInsight, setActiveZoneInsight] = useState<ZoneActivityInsight | null>(null);
  const [historicalRankingArtifacts, setHistoricalRankingArtifacts] = useState<HistoricalRankingArtifacts | null>(null);
  const [hexCompositionHistoryArtifacts, setHexCompositionHistoryArtifacts] = useState<HexCompositionHistoryArtifacts | null>(null);
  const [zoneBoundaryArtifacts, setZoneBoundaryArtifacts] = useState<ZoneBoundaryArtifacts | null>(initialZoneBoundaries ?? null);
  const [compositionYear, setCompositionYear] = useState(HEX_COMPOSITION_YEAR_MAX);
  const [historicalZoneLevel, setHistoricalZoneLevel] = useState<HistoricalZoneLevel>("district");
  const [isHistoricalEvolutionOpen, setIsHistoricalEvolutionOpen] = useState(false);
  const [comparisonZoneLevel, setComparisonZoneLevel] = useState<HistoricalZoneLevel>("district");
  const [comparisonLeftZoneKey, setComparisonLeftZoneKey] = useState("");
  const [comparisonRightZoneKey, setComparisonRightZoneKey] = useState("");
  const [isZoneComparisonOpen, setIsZoneComparisonOpen] = useState(false);
  const [isLoadingHistoricalRankings, setIsLoadingHistoricalRankings] = useState(false);
  const [isLoadingZoneBoundaries, setIsLoadingZoneBoundaries] = useState(false);
  const loadedArtifactsRef = useRef<Partial<Record<HexSize, FrontendArtifacts>>>(
    initialArtifacts && initialArtifacts.hexes.length > 0 ? { [DEFAULT_HEX_SIZE]: initialArtifacts } : {}
  );
  const historicalRankingsRequestRef = useRef<Promise<HistoricalRankingArtifacts> | null>(null);
  const hexCompositionHistoryRequestRef = useRef<Promise<HexCompositionHistoryArtifacts> | null>(null);
  const zoneBoundariesRequestRef = useRef<Promise<ZoneBoundaryArtifacts> | null>(null);
  const mapPanelRef = useRef<HTMLElement | null>(null);

  const ensureHistoricalRankingsLoaded = useCallback(async () => {
    if (historicalRankingArtifacts) {
      return historicalRankingArtifacts;
    }

    if (historicalRankingsRequestRef.current) {
      return historicalRankingsRequestRef.current;
    }

    setIsLoadingHistoricalRankings(true);
    const request = loadHistoricalRankingsFromPublic()
      .then((nextArtifacts) => {
        setHistoricalRankingArtifacts(nextArtifacts);
        return nextArtifacts;
      })
      .finally(() => {
        historicalRankingsRequestRef.current = null;
        setIsLoadingHistoricalRankings(false);
      });

    historicalRankingsRequestRef.current = request;
    return request;
  }, [historicalRankingArtifacts]);

  const ensureHexCompositionHistoryLoaded = useCallback(async () => {
    if (hexCompositionHistoryArtifacts) {
      return hexCompositionHistoryArtifacts;
    }

    if (hexCompositionHistoryRequestRef.current) {
      return hexCompositionHistoryRequestRef.current;
    }

    const request = loadHexCompositionHistoryFromPublic()
      .then((nextArtifacts) => {
        setHexCompositionHistoryArtifacts(nextArtifacts);
        return nextArtifacts;
      })
      .finally(() => {
        hexCompositionHistoryRequestRef.current = null;
      });

    hexCompositionHistoryRequestRef.current = request;
    return request;
  }, [hexCompositionHistoryArtifacts]);

  useEffect(() => {
    if (mapViewMode !== "hex" || selectedCategory !== "__all__") {
      return;
    }
    void ensureHexCompositionHistoryLoaded();
  }, [ensureHexCompositionHistoryLoaded, mapViewMode, selectedCategory]);

  const ensureZoneBoundariesLoaded = useCallback(async () => {
    if (zoneBoundaryArtifacts) {
      return zoneBoundaryArtifacts;
    }

    if (zoneBoundariesRequestRef.current) {
      return zoneBoundariesRequestRef.current;
    }

    setIsLoadingZoneBoundaries(true);
    const request = loadZoneBoundariesFromPublic()
      .then((nextArtifacts) => {
        setZoneBoundaryArtifacts(nextArtifacts);
        return nextArtifacts;
      })
      .finally(() => {
        zoneBoundariesRequestRef.current = null;
        setIsLoadingZoneBoundaries(false);
      });

    zoneBoundariesRequestRef.current = request;
    return request;
  }, [zoneBoundaryArtifacts]);

  useEffect(() => {
    void ensureZoneBoundariesLoaded();
  }, [ensureZoneBoundariesLoaded]);

  useEffect(() => {
    if (initialArtifacts) {
      setIsLoadingArtifacts(false);
      return;
    }

    let alive = true;

    async function loadSharedArtifacts() {
      const nextSharedArtifacts = await loadMapSharedArtifactsFromPublic();
      if (!alive) {
        return;
      }

      setArtifacts((currentArtifacts) => ({
        ...nextSharedArtifacts,
        hexes: currentArtifacts.hexes,
      }));
      setIsLoadingArtifacts(false);
    }

    void loadSharedArtifacts();

    return () => {
      alive = false;
    };
  }, [initialArtifacts]);

  useEffect(() => {
    if (mapViewMode !== "hex") {
      setIsSwitchingHexSize(false);
      return;
    }

    let alive = true;

    async function loadSelectedHexArtifacts() {
      const cachedArtifacts = loadedArtifactsRef.current[hexSize];
      if (cachedArtifacts) {
        setArtifacts(cachedArtifacts);
        setIsLoadingArtifacts(false);
        setIsSwitchingHexSize(false);
        return;
      }

      if (artifacts.hexes.length === 0) {
        setIsLoadingArtifacts(true);
      } else {
        setIsSwitchingHexSize(true);
      }

      const nextArtifacts = await loadMapArtifactsFromPublic(hexSize);
      if (!alive) {
        return;
      }

      loadedArtifactsRef.current[hexSize] = nextArtifacts;
      setArtifacts(nextArtifacts);
      setIsLoadingArtifacts(false);
      setIsSwitchingHexSize(false);
      setSelectedCategory((currentCategory) => {
        return nextArtifacts.categories.some((item) => item.category_code === currentCategory)
          ? currentCategory
          : nextArtifacts.meta.defaultCategoryCode;
      });
    }

    void loadSelectedHexArtifacts();

    return () => {
      alive = false;
    };
  }, [artifacts.hexes.length, hexSize, mapViewMode]);

  useEffect(() => {
    const cancel = scheduleIdleTask(() => {
      void fetch("/data/opportunities/sections/geometry.geojson", { cache: "force-cache" }).catch(() => undefined);
    }, 1200);

    return cancel;
  }, []);

  useEffect(() => {
    if (!selectedHex) {
      return;
    }

    const matchedHex = artifacts.hexes.find(
      (item) => item.h3_cell === selectedHex.h3_cell && item.category_code === selectedHex.category_code
    );
    if (matchedHex) {
      if (matchedHex !== selectedHex) {
        setSelectedHex(matchedHex);
      }
      return;
    }

    setSelectedHex(null);
  }, [artifacts.hexes, selectedHex]);


  const selectedCategoryMeta = useMemo(() => {
    return artifacts.categories.find((item) => item.category_code === selectedCategory) ?? artifacts.categories[0];
  }, [artifacts.categories, selectedCategory]);

  const filteredHexes = useMemo(() => {
    return artifacts.hexes.filter((item) => item.category_code === selectedCategory);
  }, [artifacts.hexes, selectedCategory]);

  const filteredDistrictZones = useMemo(() => {
    return artifacts.zones.district.filter((item) => item.category_code === selectedCategory);
  }, [artifacts.zones.district, selectedCategory]);

  const filteredBarrioZones = useMemo(() => {
    return artifacts.zones.barrio.filter((item) => item.category_code === selectedCategory);
  }, [artifacts.zones.barrio, selectedCategory]);

  const districtZoneColorThresholds = useMemo(
    () => buildZoneColorThresholds(artifacts.zones.district, "district"),
    [artifacts.zones.district]
  );

  const barrioZoneColorThresholds = useMemo(
    () => buildZoneColorThresholds(artifacts.zones.barrio, "barrio"),
    [artifacts.zones.barrio]
  );

  useEffect(() => {
    if (!selectedZone) {
      return;
    }

    const zonePool = selectedZone.zone_level === "district" ? filteredDistrictZones : filteredBarrioZones;
    const matchedZone = zonePool.find(
      (item) => item.zone_code === selectedZone.zone_code && item.category_code === selectedZone.category_code
    );
    if (matchedZone) {
      if (matchedZone !== selectedZone) {
        setSelectedZone(matchedZone);
      }
      return;
    }

    setSelectedZone(null);
  }, [filteredBarrioZones, filteredDistrictZones, selectedZone]);

  const currentZoneRows = useMemo(() => {
    if (mapViewMode === "district") {
      return filteredDistrictZones;
    }
    if (mapViewMode === "barrio") {
      return filteredBarrioZones;
    }
    return [];
  }, [filteredBarrioZones, filteredDistrictZones, mapViewMode]);

  const currentZoneBoundaries = useMemo(() => {
    if (!zoneBoundaryArtifacts || mapViewMode === "hex") {
      return [];
    }
    return zoneBoundaryArtifacts.zones[mapViewMode].features;
  }, [mapViewMode, zoneBoundaryArtifacts]);

  const currentMapRows = useMemo<MapAggregateMetrics[]>(() => {
    return mapViewMode === "hex" ? filteredHexes : currentZoneRows;
  }, [currentZoneRows, filteredHexes, mapViewMode]);

  const currentZoneColorFloor = useMemo(() => {
    if (mapViewMode === "district") {
      return districtZoneColorThresholds.get(selectedCategory) ?? DISTRICT_COLOR_FLOOR_MIN;
    }
    if (mapViewMode === "barrio") {
      return barrioZoneColorThresholds.get(selectedCategory) ?? BARRIO_COLOR_FLOOR_MIN;
    }
    return 0;
  }, [barrioZoneColorThresholds, districtZoneColorThresholds, mapViewMode, selectedCategory]);

  const colorableMapRows = useMemo<MapAggregateMetrics[]>(() => {
    if (mapViewMode === "hex") {
      return filteredHexes;
    }
    return currentZoneRows.filter((item) => item.n_locales >= currentZoneColorFloor);
  }, [currentZoneColorFloor, currentZoneRows, filteredHexes, mapViewMode]);

  const colorScale = useMemo(() => buildColorScale(colorableMapRows), [colorableMapRows]);

  const activeStats = useMemo(() => buildVisibleStats(currentMapRows, horizon), [currentMapRows, horizon]);

  const selectedZoneForView = useMemo(() => {
    if (mapViewMode === "hex") {
      return null;
    }
    if (!selectedZone || selectedZone.zone_level !== mapViewMode) {
      return null;
    }
    return selectedZone;
  }, [mapViewMode, selectedZone]);

  const detailHex = mapViewMode === "hex" ? selectedHex : null;
  const detailZone = selectedZoneForView;
  const detailSurvival = detailHex
    ? getHorizonSurvival(detailHex, horizon)
    : detailZone
      ? getHorizonSurvival(detailZone, horizon)
      : null;
  const detailSupport = detailHex
    ? getHorizonSupport(detailHex, horizon)
    : detailZone
      ? getHorizonSupport(detailZone, horizon)
      : 0;
  const activeUnitLabelPlural = getMapViewUnitLabel(mapViewMode, true);
  const activeUnitLabelSingular = getMapViewUnitLabel(mapViewMode, false);

  const hasHexCompositionHistory = (hexCompositionHistoryArtifacts?.meta.years.length ?? 0) > 0;
  const hexCategoryColorMap = useMemo(() => buildHexCategoryColorMap(artifacts.hexes), [artifacts.hexes]);

  const hexCompositionHistoryIndex = useMemo(() => {
    const index = new Map<string, HexCompositionHistoryRecord[]>();
    if (!hexCompositionHistoryArtifacts) {
      return index;
    }

    for (const row of hexCompositionHistoryArtifacts.hexes) {
      const key = `${row.year}::${row.h3_cell}`;
      const bucket = index.get(key);
      if (bucket) {
        bucket.push(row);
      } else {
        index.set(key, [row]);
      }
    }

    return index;
  }, [hexCompositionHistoryArtifacts]);

  const zoneCompositionHistoryIndex = useMemo<ZoneCompositionHistoryIndex>(() => {
    const grouped = new Map<string, HistoricalZoneRankingRecord[]>();
    const byCode = new Map<string, HistoricalZoneRankingRecord[]>();
    const byIdentity = new Map<string, HistoricalZoneRankingRecord[]>();
    if (!historicalRankingArtifacts) {
      return { byCode, byIdentity };
    }

    for (const zoneLevel of ["district", "barrio"] as const) {
      for (const row of historicalRankingArtifacts.zones[zoneLevel]) {
        const key = `${zoneLevel}::${row.year}::${row.zone_key}`;
        const bucket = grouped.get(key);
        if (bucket) {
          bucket.push(row);
        } else {
          grouped.set(key, [row]);
        }
      }
    }

    for (const bucket of grouped.values()) {
      const sample = bucket[0];
      if (!sample) {
        continue;
      }

      byCode.set(`${sample.zone_level}::${sample.year}::${sample.zone_key}`, bucket);
      byCode.set(`${sample.zone_level}::${sample.year}::${sample.zone_code}`, bucket);

      for (const identityKey of buildZoneHistoryIdentityKeys(
        sample.zone_level,
        sample.zone_name,
        sample.zone_context_name
      )) {
        byIdentity.set(`${sample.zone_level}::${sample.year}::${identityKey}`, bucket);
      }
    }

    return { byCode, byIdentity };
  }, [historicalRankingArtifacts]);

  const compositionYears = useMemo(() => {
    if (mapViewMode === "hex") {
      return (hexCompositionHistoryArtifacts?.meta.years ?? []).filter(
        (year) => year >= HEX_COMPOSITION_YEAR_MIN && year <= HEX_COMPOSITION_YEAR_MAX
      );
    }
    return historicalRankingArtifacts?.meta.years ?? [];
  }, [hexCompositionHistoryArtifacts, historicalRankingArtifacts, mapViewMode]);

  useEffect(() => {
    if (compositionYears.length === 0) {
      return;
    }

    const availableYears = new Set(compositionYears);
    if (availableYears.size === 0) {
      return;
    }

    setCompositionYear((currentYear) => {
      if (availableYears.has(currentYear)) {
        return currentYear;
      }

      return compositionYears[compositionYears.length - 1] ?? currentYear;
    });
  }, [compositionYears]);

  const detailCategoryCompositionState = useMemo(() => {
    if (selectedCategory !== "__all__") {
      return { items: [], totalLocales: 0 };
    }

    if (detailHex) {
      if (!hasHexCompositionHistory) {
        return {
          items: buildHexCategoryComposition(artifacts.hexes, detailHex, hexCategoryColorMap),
          totalLocales: detailHex.n_locales,
        };
      }

      const historyRows = hexCompositionHistoryIndex.get(`${compositionYear}::${detailHex.h3_cell}`) ?? [];
      return buildHexCategoryCompositionForYear(historyRows, hexCategoryColorMap);
    }

    if (!detailZone) {
      return { items: [], totalLocales: 0 };
    }

    if (!historicalRankingArtifacts) {
      return {
        items: buildZoneCategoryComposition(
          detailZone.zone_level === "district" ? artifacts.zones.district : artifacts.zones.barrio,
          detailZone,
          hexCategoryColorMap
        ),
        totalLocales: detailZone.n_locales,
      };
    }

    const historyRows = resolveZoneCompositionHistoryRows(zoneCompositionHistoryIndex, detailZone, compositionYear);
    return buildZoneCategoryCompositionForYear(historyRows, hexCategoryColorMap);
  }, [
    artifacts.hexes,
    artifacts.zones.barrio,
    artifacts.zones.district,
    compositionYear,
    detailHex,
    detailZone,
    hasHexCompositionHistory,
    hexCategoryColorMap,
    hexCompositionHistoryIndex,
    historicalRankingArtifacts,
    selectedCategory,
    zoneCompositionHistoryIndex,
  ]);

  const detailCategoryComposition = detailCategoryCompositionState.items;
  const detailCategoryCompositionTotalLocales = detailCategoryCompositionState.totalLocales;
  const currentRankableZoneRows = useMemo(() => {
    return currentZoneRows.filter((item) => item.n_locales >= currentZoneColorFloor);
  }, [currentZoneColorFloor, currentZoneRows]);

  const meanRiskIndexForDetail = useMemo(() => {
    return mapViewMode === "hex"
      ? computeWeightedMeanRiskIndex(filteredHexes)
      : computeWeightedMeanRiskIndex(currentRankableZoneRows);
  }, [currentRankableZoneRows, filteredHexes, mapViewMode]);

  const detailHexRank = useMemo(() => {
    if (!detailHex) {
      return null;
    }
    return buildHexRanking(filteredHexes, detailHex, horizon);
  }, [detailHex, filteredHexes, horizon]);

  const detailZoneRank = useMemo(() => {
    if (!detailZone) {
      return null;
    }
    return buildZoneRanking(currentRankableZoneRows, detailZone);
  }, [currentRankableZoneRows, detailZone]);

  const topZones = useMemo(() => {
    return {
      district: buildTopZones(filteredDistrictZones, districtZoneColorThresholds.get(selectedCategory) ?? DISTRICT_COLOR_FLOOR_MIN),
      barrio: buildTopZones(filteredBarrioZones, barrioZoneColorThresholds.get(selectedCategory) ?? BARRIO_COLOR_FLOOR_MIN)
    };
  }, [barrioZoneColorThresholds, districtZoneColorThresholds, filteredBarrioZones, filteredDistrictZones, selectedCategory]);

  const detailMetrics = useMemo(() => {
    if (detailHex) {
      return buildHexMetrics({
        detail: detailHex,
        detailRank: detailHexRank,
        detailSupport,
        detailSurvival,
        horizon,
        meanRiskIndex: meanRiskIndexForDetail
      });
    }

    if (detailZone) {
      return buildZoneMetrics({
        detail: detailZone,
        detailRank: detailZoneRank,
        detailSupport,
        detailSurvival,
        horizon,
        meanRiskIndex: meanRiskIndexForDetail
      });
    }

    return [];
  }, [
    detailHex,
    detailHexRank,
    detailSupport,
    detailSurvival,
    detailZone,
    detailZoneRank,
    horizon,
    meanRiskIndexForDetail,
  ]);

  const activeMetric = detailMetrics.find((metric) => metric.id === activeMetricId) ?? null;
  const comparisonOptions = useMemo(() => {
    return buildZoneComparisonOptions({
      artifacts: historicalRankingArtifacts,
      categoryCode: selectedCategory,
      zoneLevel: comparisonZoneLevel,
    });
  }, [comparisonZoneLevel, historicalRankingArtifacts, selectedCategory]);
  const comparisonZoneLabel = comparisonZoneLevel === "district" ? "distrito" : "barrio";
  const comparisonOptionsPlaceholder = comparisonOptions.length > 0
    ? `Selecciona un ${comparisonZoneLabel}`
    : isLoadingHistoricalRankings
      ? "Cargando serie histórica..."
      : `Sin ${comparisonZoneLevel === "district" ? "distritos" : "barrios"} comparables`;
  const comparisonZonePickerOptions = comparisonOptions.map((option) => ({
    label: option.label,
    value: option.zoneKey,
  }));
  const canCompareZones = comparisonLeftZoneKey.length > 0
    && comparisonRightZoneKey.length > 0
    && comparisonLeftZoneKey !== comparisonRightZoneKey;
  const comparisonMetricNote = selectedCategory === "__all__"
    ? "Comparamos puesto, número de locales y peso en Madrid. Son lecturas fáciles y con cambio real en el tiempo."
    : "Comparamos puesto, número de locales y peso de la categoría en la zona. Son lecturas más claras que supervivencia o rotación.";

  useEffect(() => {
    if (!activeMetricId) {
      return;
    }

    if (detailMetrics.some((metric) => metric.id === activeMetricId)) {
      return;
    }

    setActiveMetricId(null);
  }, [activeMetricId, detailMetrics]);

  useEffect(() => {
    const validKeys = new Set(comparisonOptions.map((item) => item.zoneKey));
    setComparisonLeftZoneKey((current) => (current && validKeys.has(current) ? current : ""));
    setComparisonRightZoneKey((current) => (current && validKeys.has(current) ? current : ""));
  }, [comparisonOptions]);

  useEffect(() => {
    if (!canCompareZones && isZoneComparisonOpen) {
      setIsZoneComparisonOpen(false);
    }
  }, [canCompareZones, isZoneComparisonOpen]);

  const handleMapViewModeChange = (nextMode: MapViewMode) => {
    if (mapViewMode === nextMode) {
      return;
    }

    setMapViewMode(nextMode);
    setActiveMetricId(null);
    setActiveZoneInsight(null);
    setIsHistoricalEvolutionOpen(false);
    setIsZoneComparisonOpen(false);

    if (nextMode !== "hex") {
      setHistoricalZoneLevel(nextMode);
      setComparisonZoneLevel(nextMode);
    }
  };

  return (
    <main className="app-shell">
      <aside className="sidebar panel">
        <div>
          <ViewTabs />
          <div className="eyebrow">Localizate / Madrid</div>
          <h1>Mapa de supervivencia comercial.</h1>
        </div>

        <p className="lede">Explora qué zonas sostienen mejor cada tipo de local en Madrid.</p>

        <div className="control-group">
          <span className="control-label" id="category-label">
            Tipo de local
          </span>
          <CategoryPicker
            labelledBy="category-label"
            onChange={(nextCategory) => {
              setSelectedCategory(nextCategory);
              setSelectedHex(null);
              setSelectedZone(null);
              setActiveMetricId(null);
              setActiveZoneInsight(null);
            }}
            options={artifacts.categories}
            value={selectedCategory}
          />
        </div>

        <div className="control-group">
          <span className="control-label">Vista principal</span>
          <div className="toggle-row toggle-row-three map-view-toggle-row">
            <button data-active={mapViewMode === "district"} onClick={() => handleMapViewModeChange("district")} type="button">
              Distrito
            </button>
            <button data-active={mapViewMode === "barrio"} onClick={() => handleMapViewModeChange("barrio")} type="button">
              Barrio
            </button>
            <button data-active={mapViewMode === "hex"} onClick={() => handleMapViewModeChange("hex")} type="button">
              Hexágono
            </button>
          </div>
        </div>

        {mapViewMode === "hex" && (
        <div className="control-group">
          <span className="control-label">Tamaño del hexágono</span>
          <div className="toggle-row toggle-row-three">
            {HEX_SIZE_OPTIONS.map((option) => (
              <button
                data-active={hexSize === option.value}
                key={option.value}
                onClick={() => {
                  if (hexSize === option.value) {
                    return;
                  }
                  setSelectedHex(null);
                  setActiveMetricId(null);
                  setActiveZoneInsight(null);
                  setHexSize(option.value);
                }}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
        )}

        <div className="stat-grid">
          <div className="stat-card">
            <span className="label">Índice relativo 0-1</span>
            <span className="value">{formatRelativeRiskIndex(activeStats.meanRelativeRisk)}</span>
          </div>
          <div className="stat-card">
            <span className="label">Supervivencia media 24m</span>
            <span className="value">{formatPercent(activeStats.meanSurvival, activeStats.units > 0 ? "Sin muestra" : "Sin datos")}</span>
          </div>
          <div className="stat-card">
            <span className="label">Locales visibles</span>
            <span className="value">{formatCompact(activeStats.locales)}</span>
          </div>
          <div className="stat-card">
            <span className="label">{activeUnitLabelPlural} visibles</span>
            <span className="value">{formatCompact(activeStats.units)}</span>
          </div>
        </div>
        <p className="support-note">
          {isLoadingArtifacts
            ? "Cargando los datos históricos del mapa. La vista aparece primero y el contenido se completa en segundo plano."
            : mapViewMode !== "hex" && isLoadingZoneBoundaries && currentZoneBoundaries.length === 0
              ? `Cargando límites de ${activeUnitLabelPlural.toLowerCase()}...`
            : isSwitchingHexSize && mapViewMode === "hex"
              ? `Cambiando a nivel ${formatHexSizeLabel(hexSize).toLowerCase()}...`
                : buildGlobalSupportNote({
                    activeUnitLabelPlural,
                    mapViewMode,
                    totalUnits: activeStats.units,
                    unitsWithSupport: activeStats.unitsWithSupport,
                    zoneColorFloor: currentZoneColorFloor,
                  })}
        </p>

        <section className="info-card">
          <div className="eyebrow">Ficha categoría</div>
          <h2>{selectedCategoryMeta.category_desc}</h2>
          <p>{selectedCategoryMeta.definition ?? buildFallbackCategoryDefinition(selectedCategoryMeta.category_desc)}</p>
        </section>

        <section className="info-card">
          <div className="info-card-heading">
            <div className="info-card-heading-copy">
              <div className="eyebrow">Zonas destacadas</div>
              <h3>Menor índice relativo</h3>
            </div>
          </div>
          <ZoneList
            barrioZones={topZones.barrio}
            districtZones={topZones.district}
            onSelectZone={(zone) => {
              const zonePool = zone.zone_level === "district" ? artifacts.zones.district : artifacts.zones.barrio;
              const nextInsight = buildZoneActivityInsight({
                zone,
                zonePool,
                currentCategoryCode: selectedCategory,
                horizon,
              });

              setMapViewMode(zone.zone_level);
              setHistoricalZoneLevel(zone.zone_level);
              setComparisonZoneLevel(zone.zone_level);
              setSelectedHex(null);
              setSelectedZone(zone);
              setIsRiskExplainerOpen(false);
              setIsHistoricalEvolutionOpen(false);
              setIsZoneComparisonOpen(false);
              setActiveMetricId(null);
              setActiveZoneInsight((current) => {
                if (!nextInsight) {
                  return null;
                }
                if (current && current.zoneLevel === nextInsight.zoneLevel && current.zoneCode === nextInsight.zoneCode) {
                  return null;
                }
                return nextInsight;
              });
            }}
          />
          <div className="zone-board-footer zone-board-footer-group">
            <button
              aria-expanded={isRiskExplainerOpen}
              className="zone-board-action"
              onClick={() => {
                setIsHistoricalEvolutionOpen(false);
                setIsZoneComparisonOpen(false);
                setActiveZoneInsight(null);
                setIsRiskExplainerOpen((current) => !current);
              }}
              type="button"
            >
              {isRiskExplainerOpen ? "Ocultar guía" : "Cómo interpretar este ranking"}
            </button>
            <button
              aria-expanded={isHistoricalEvolutionOpen}
              className="zone-board-action"
              onClick={() => {
                const nextOpen = !isHistoricalEvolutionOpen;
                setIsRiskExplainerOpen(false);
                setIsZoneComparisonOpen(false);
                setActiveZoneInsight(null);
                setActiveMetricId(null);
                setIsHistoricalEvolutionOpen(nextOpen);
                if (nextOpen) {
                  void ensureHistoricalRankingsLoaded();
                }
              }}
              onFocus={() => {
                void ensureHistoricalRankingsLoaded();
              }}
              onMouseEnter={() => {
                void ensureHistoricalRankingsLoaded();
              }}
              type="button"
            >
              {isHistoricalEvolutionOpen ? "Ocultar evolución histórica" : "Evolución histórica"}
            </button>
          </div>
        </section>

        <section
          className="info-card"
          onFocusCapture={() => {
            void ensureHistoricalRankingsLoaded();
          }}
          onMouseEnter={() => {
            void ensureHistoricalRankingsLoaded();
          }}
        >
          <div className="info-card-heading-copy">
            <div className="eyebrow">Comparar zonas</div>
            <h3>Dos trayectorias cara a cara</h3>
          </div>
          <p className="comparison-note">{comparisonMetricNote}</p>

          <div className="control-group">
            <span className="control-label">Ámbito</span>
            <div className="toggle-row">
              <button
                data-active={comparisonZoneLevel === "district"}
                onClick={() => {
                  if (comparisonZoneLevel === "district") {
                    return;
                  }
                  setComparisonZoneLevel("district");
                  setComparisonLeftZoneKey("");
                  setComparisonRightZoneKey("");
                  setIsZoneComparisonOpen(false);
                }}
                type="button"
              >
                Distrito
              </button>
              <button
                data-active={comparisonZoneLevel === "barrio"}
                onClick={() => {
                  if (comparisonZoneLevel === "barrio") {
                    return;
                  }
                  setComparisonZoneLevel("barrio");
                  setComparisonLeftZoneKey("");
                  setComparisonRightZoneKey("");
                  setIsZoneComparisonOpen(false);
                }}
                type="button"
              >
                Barrio
              </button>
            </div>
          </div>

          <div className="control-group">
            <span className="control-label" id="comparison-left-label">Primera zona</span>
            <SimplePicker
              disabled={comparisonZonePickerOptions.length === 0}
              labelledBy="comparison-left-label"
              onChange={(nextValue) => {
                setComparisonLeftZoneKey(nextValue);
              }}
              options={comparisonZonePickerOptions}
              placeholder={comparisonOptionsPlaceholder}
              value={comparisonLeftZoneKey}
            />
          </div>

          <div className="control-group">
            <span className="control-label" id="comparison-right-label">Segunda zona</span>
            <SimplePicker
              disabled={comparisonZonePickerOptions.length === 0}
              labelledBy="comparison-right-label"
              onChange={(nextValue) => {
                setComparisonRightZoneKey(nextValue);
              }}
              options={comparisonZonePickerOptions}
              placeholder={comparisonOptionsPlaceholder}
              value={comparisonRightZoneKey}
            />
          </div>

          <div className="comparison-actions">
            <button
              className="sidebar-primary-action"
              disabled={!canCompareZones}
              onClick={() => {
                if (!canCompareZones) {
                  return;
                }
                setIsRiskExplainerOpen(false);
                setActiveZoneInsight(null);
                setActiveMetricId(null);
                setIsHistoricalEvolutionOpen(false);
                setIsZoneComparisonOpen(true);
              }}
              type="button"
            >
              Comparar
            </button>
            {!canCompareZones && comparisonLeftZoneKey && comparisonRightZoneKey && comparisonLeftZoneKey === comparisonRightZoneKey ? (
              <p className="comparison-note">Elige dos {comparisonZoneLevel === "district" ? "distritos" : "barrios"} distintos.</p>
            ) : null}
            {!isLoadingHistoricalRankings && comparisonOptions.length < 2 ? (
              <p className="comparison-note">No hay suficiente histórico vigente para comparar dos {comparisonZoneLevel === "district" ? "distritos" : "barrios"} en esta categoría.</p>
            ) : null}
          </div>
        </section>

        <section className="detail-card">
          <div className="eyebrow">
            {mapViewMode === "hex" ? "Hexágono seleccionado" : `${capitalize(activeUnitLabelSingular)} seleccionado`}
          </div>
          {detailHex || detailZone ? (
            <>
              <div className="detail-header-row">
                <div className="detail-guide">
                  <h2>{detailHex ? detailHex.location_label : detailZone?.zone_name}</h2>
                  <p className="detail-location">
                    {buildSelectedUnitSummary({
                      categoryDesc: selectedCategoryMeta.category_desc,
                      detailHex,
                      detailZone,
                    })}
                  </p>
                  <p className="detail-subtle">
                    {detailHex
                      ? "Lectura fina por celda H3. Sirve para detectar contrastes internos dentro de un barrio o distrito."
                      : `Lectura histórica agregada por ${activeUnitLabelSingular}. Prioriza estabilidad y narrativa territorial.`}
                  </p>
                </div>
              </div>
              <MetricGrid
                activeMetricId={activeMetricId}
                metrics={detailMetrics}
                onSelect={(metricId) => {
                  setActiveZoneInsight(null);
                  setIsHistoricalEvolutionOpen(false);
                  setIsZoneComparisonOpen(false);
                  setActiveMetricId(metricId);
                }}
              />
            </>
          ) : (
            <div className="detail-empty">
              <h3>{`Selecciona ${mapViewMode === "hex" ? "un hexágono" : `un ${activeUnitLabelSingular}`}`}</h3>
              <p>
                {mapViewMode === "hex"
                  ? "Haz clic en el mapa para ver su posición en Madrid, su ranking por riesgo y la diferencia frente a la media de la categoría."
                  : `Haz clic en el mapa para ver la ficha histórica del ${activeUnitLabelSingular}, su ranking en Madrid y el soporte real de la métrica.`}
              </p>
            </div>
          )}
        </section>

        {selectedCategory === "__all__" ? (
          <section className="info-card info-card-hex-category-composition">
            <div className="eyebrow">{mapViewMode === "hex" ? "Mezcla del hexágono" : `Mezcla del ${activeUnitLabelSingular}`}</div>
            {detailHex || detailZone ? (
              <HexCategoryComposition
                items={detailCategoryComposition}
                maxYear={compositionYears[compositionYears.length - 1] ?? HEX_COMPOSITION_YEAR_MAX}
                minYear={compositionYears[0] ?? HEX_COMPOSITION_YEAR_MIN}
                onYearChange={setCompositionYear}
                overlayBoundsRef={mapPanelRef}
                selectedYear={compositionYear}
                subjectLabel={mapViewMode === "hex" ? "hexágono" : activeUnitLabelSingular}
                totalLocales={detailCategoryCompositionTotalLocales}
              />
            ) : (
              <p className="empty-note">
                {mapViewMode === "hex"
                  ? "Selecciona un hexágono para ver cómo se reparten sus locales históricos entre las distintas categorías."
                  : `Selecciona un ${activeUnitLabelSingular} para ver cómo cambia su mezcla histórica por categorías a lo largo del tiempo.`}
              </p>
            )}
          </section>
        ) : null}
      </aside>

      <section className="map-panel panel" ref={mapPanelRef}>
        {isZoneComparisonOpen && canCompareZones ? (
          <div className="map-overlay panel zone-comparison-overlay">
            <ZoneComparisonBanner
              artifacts={historicalRankingArtifacts}
              categoryCode={selectedCategory}
              categoryDesc={selectedCategoryMeta.category_desc}
              comparison={{
                leftZoneKey: comparisonLeftZoneKey,
                rightZoneKey: comparisonRightZoneKey,
                zoneLevel: comparisonZoneLevel,
              }}
              isLoading={isLoadingHistoricalRankings}
              onClose={() => setIsZoneComparisonOpen(false)}
            />
          </div>
        ) : isHistoricalEvolutionOpen ? (
          <div className="map-overlay panel historical-evolution-overlay">
            <HistoricalEvolutionBanner
              artifacts={historicalRankingArtifacts}
              categoryCode={selectedCategory}
              categoryDesc={selectedCategoryMeta.category_desc}
              isLoading={isLoadingHistoricalRankings}
              onClose={() => setIsHistoricalEvolutionOpen(false)}
              onSelectZoneLevel={setHistoricalZoneLevel}
              zoneLevel={historicalZoneLevel}
            />
          </div>
        ) : isRiskExplainerOpen ? (
          <div className="map-overlay panel risk-explainer-overlay">
            <RelativeRiskExplainerBanner onClose={() => setIsRiskExplainerOpen(false)} />
          </div>
        ) : activeZoneInsight ? (
          <div className="map-overlay panel zone-explainer-overlay">
            <ZoneActivityExplainer insight={activeZoneInsight} onClose={() => setActiveZoneInsight(null)} />
          </div>
        ) : activeMetric ? (
          <div className="map-overlay panel metric-banner">
            <MetricExplainer metric={activeMetric} onClose={() => setActiveMetricId(null)} />
          </div>
        ) : null}

        <MadridMap
          bounds={artifacts.meta.map_bounds}
          colorScale={colorScale}
          horizon={horizon}
          hexes={filteredHexes}
          mapViewMode={mapViewMode}
          onSelectHex={(hex) => {
            setActiveZoneInsight(null);
            setIsHistoricalEvolutionOpen(false);
            setIsZoneComparisonOpen(false);
            setSelectedHex(hex);
          }}
          onSelectZone={(zone) => {
            setActiveZoneInsight(null);
            setIsHistoricalEvolutionOpen(false);
            setIsZoneComparisonOpen(false);
            setSelectedZone(zone);
          }}
          selectedHex={selectedHex}
          selectedZone={selectedZoneForView}
          zoneColorFloorLocales={currentZoneColorFloor}
          zoneBoundaries={currentZoneBoundaries}
          zones={currentZoneRows}
        />
      </section>
    </main>
  );
}

function CategoryPicker({
  labelledBy,
  onChange,
  options,
  value,
}: {
  labelledBy: string;
  onChange: (value: string) => void;
  options: CategoryOption[];
  value: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [openUpward, setOpenUpward] = useState(false);
  const [menuMaxHeight, setMenuMaxHeight] = useState<number | null>(null);
  const pickerRef = useRef<HTMLDivElement | null>(null);
  const selectedOption = options.find((option) => option.category_code === value) ?? options[0] ?? null;

  useLayoutEffect(() => {
    if (!isOpen || !pickerRef.current) {
      setMenuMaxHeight(null);
      return;
    }

    function updateMenuPlacement() {
      if (!pickerRef.current) {
        return;
      }

      const triggerRect = pickerRef.current.getBoundingClientRect();
      const availableBelow = Math.max(0, window.innerHeight - triggerRect.bottom - PICKER_VIEWPORT_PADDING_PX - PICKER_MENU_OFFSET_PX);
      const availableAbove = Math.max(0, triggerRect.top - PICKER_VIEWPORT_PADDING_PX - PICKER_MENU_OFFSET_PX);
      const nextOpenUpward = availableAbove > availableBelow;
      const availableSpace = nextOpenUpward ? availableAbove : availableBelow;

      setOpenUpward(nextOpenUpward);
      setMenuMaxHeight(Math.min(PICKER_MENU_MAX_HEIGHT_PX, availableSpace));
    }

    updateMenuPlacement();
    window.addEventListener("resize", updateMenuPlacement);
    window.addEventListener("scroll", updateMenuPlacement, true);

    return () => {
      window.removeEventListener("resize", updateMenuPlacement);
      window.removeEventListener("scroll", updateMenuPlacement, true);
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    function handlePointerDown(event: MouseEvent) {
      if (pickerRef.current && event.target instanceof Node && !pickerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  if (!selectedOption) {
    return null;
  }

  return (
    <div className="category-picker" ref={pickerRef}>
      <button
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-labelledby={labelledBy}
        className="category-picker-trigger"
        onClick={() => setIsOpen((current) => !current)}
        type="button"
      >
        <span className="category-picker-trigger-copy">
          <span className="category-picker-trigger-title">{selectedOption.category_desc}</span>
          <span className="category-picker-trigger-subtitle">Elige la categoría que quieras analizar</span>
        </span>
        <span aria-hidden="true" className="category-picker-trigger-icon">
          {isOpen ? "˄" : "˅"}
        </span>
      </button>

      {isOpen ? (
        <div
          className={`category-picker-menu${openUpward ? " category-picker-menu-up" : ""}`}
          role="listbox"
          style={menuMaxHeight === null ? undefined : { maxHeight: `${menuMaxHeight}px` }}
        >
          {options.map((option) => {
            const isActive = option.category_code === value;
            return (
              <button
                aria-selected={isActive}
                className="category-picker-option"
                data-active={isActive}
                key={option.category_code}
                onClick={() => {
                  onChange(option.category_code);
                  setIsOpen(false);
                }}
                role="option"
                type="button"
              >
                {option.category_desc}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

function SimplePicker({
  disabled = false,
  labelledBy,
  onChange,
  options,
  placeholder = "Selecciona una opción",
  value,
}: {
  disabled?: boolean;
  labelledBy: string;
  onChange: (value: string) => void;
  options: PickerOption[];
  placeholder?: string;
  value: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [openUpward, setOpenUpward] = useState(false);
  const [menuMaxHeight, setMenuMaxHeight] = useState<number | null>(null);
  const pickerRef = useRef<HTMLDivElement | null>(null);
  const selectedOption = options.find((option) => option.value === value) ?? null;
  const triggerLabel = selectedOption?.label ?? placeholder;

  useLayoutEffect(() => {
    if (!isOpen || !pickerRef.current) {
      setMenuMaxHeight(null);
      return;
    }

    function updateMenuPlacement() {
      if (!pickerRef.current) {
        return;
      }

      const triggerRect = pickerRef.current.getBoundingClientRect();
      const availableBelow = Math.max(0, window.innerHeight - triggerRect.bottom - PICKER_VIEWPORT_PADDING_PX - PICKER_MENU_OFFSET_PX);
      const availableAbove = Math.max(0, triggerRect.top - PICKER_VIEWPORT_PADDING_PX - PICKER_MENU_OFFSET_PX);
      const nextOpenUpward = availableAbove > availableBelow;
      const availableSpace = nextOpenUpward ? availableAbove : availableBelow;

      setOpenUpward(nextOpenUpward);
      setMenuMaxHeight(Math.min(PICKER_MENU_MAX_HEIGHT_PX, availableSpace));
    }

    updateMenuPlacement();
    window.addEventListener("resize", updateMenuPlacement);
    window.addEventListener("scroll", updateMenuPlacement, true);

    return () => {
      window.removeEventListener("resize", updateMenuPlacement);
      window.removeEventListener("scroll", updateMenuPlacement, true);
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    function handlePointerDown(event: MouseEvent) {
      if (pickerRef.current && event.target instanceof Node && !pickerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  return (
    <div className="category-picker" ref={pickerRef}>
      <button
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-labelledby={labelledBy}
        className="category-picker-trigger"
        disabled={disabled}
        onClick={() => {
          if (disabled) {
            return;
          }
          setIsOpen((current) => !current);
        }}
        type="button"
      >
        <span className="category-picker-trigger-copy">
          <span className="category-picker-trigger-title">{triggerLabel}</span>
        </span>
        <span aria-hidden="true" className="category-picker-trigger-icon">
          {isOpen ? "˄" : "˅"}
        </span>
      </button>

      {isOpen && !disabled ? (
        <div
          className={`category-picker-menu${openUpward ? " category-picker-menu-up" : ""}`}
          role="listbox"
          style={menuMaxHeight === null ? undefined : { maxHeight: `${menuMaxHeight}px` }}
        >
          {options.map((option) => {
            const isActive = option.value === value;
            return (
              <button
                aria-selected={isActive}
                className="category-picker-option"
                data-active={isActive}
                key={option.value}
                onClick={() => {
                  onChange(option.value);
                  setIsOpen(false);
                }}
                role="option"
                type="button"
              >
                {option.label}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

const PICKER_VIEWPORT_PADDING_PX = 16;
const PICKER_MENU_OFFSET_PX = 8;
const PICKER_MENU_MAX_HEIGHT_PX = 360;

function scheduleIdleTask(task: () => void, timeout = 0) {
  if (typeof window === "undefined") {
    return () => {};
  }

  const connection = (navigator as Navigator & {
    connection?: { saveData?: boolean; effectiveType?: string };
  }).connection;
  if (connection?.saveData || connection?.effectiveType === "slow-2g" || connection?.effectiveType === "2g") {
    return () => {};
  }

  if ("requestIdleCallback" in window) {
    const idleId = window.requestIdleCallback(() => {
      task();
    }, { timeout: Math.max(timeout, 1) });

    return () => {
      window.cancelIdleCallback(idleId);
    };
  }

  const timeoutId = globalThis.setTimeout(task, timeout);
  return () => {
    globalThis.clearTimeout(timeoutId);
  };
}

function MetricGrid({
  metrics,
  activeMetricId,
  onSelect
}: {
  metrics: MetricDefinition[];
  activeMetricId: string | null;
  onSelect: (metricId: string | null) => void;
}) {
  return (
    <div className="detail-grid">
      {metrics.map((metric) => {
        const isActive = activeMetricId === metric.id;
        return (
          <button
            aria-pressed={isActive}
            className="detail-metric detail-metric-button"
            data-active={isActive}
            key={metric.id}
            onClick={() => onSelect(isActive ? null : metric.id)}
            type="button"
          >
            <span className="detail-metric-label">{metric.label}</span>
            <strong className="detail-metric-value">{metric.value}</strong>
            <span className="detail-metric-hint">Entender el dato</span>
          </button>
        );
      })}
    </div>
  );
}

function MetricExplainer({
  metric,
  onClose,
}: {
  metric: MetricDefinition | null;
  onClose: () => void;
}) {
  return (
    <div className="metric-explainer" data-empty={metric ? "false" : "true"}>
      {metric ? (
        <>
          <div className="eyebrow">Qué significa este dato</div>
          <div className="metric-explainer-title-row">
            <h3>{metric.label}</h3>
            <button aria-label="Cerrar explicación de métrica" className="explain-banner-close metric-explainer-close" onClick={onClose} type="button">
              Cerrar
            </button>
          </div>
          <div className="metric-explainer-block">
            <span className="metric-explainer-label">Qué significa</span>
            <p className="metric-explainer-copy">{metric.summary}</p>
          </div>
          <div className="metric-explainer-block">
            <span className="metric-explainer-label">Por qué te ayuda</span>
            <p className="metric-explainer-copy">{buildMetricWhyUseful(metric)}</p>
          </div>
          <div className="metric-explainer-block">
            <span className="metric-explainer-label">Cómo se calcula</span>
            <p className="metric-explainer-copy">{metric.calculation}</p>
          </div>
          {buildMetricExample(metric) ? (
            <div className="metric-explainer-block">
              <span className="metric-explainer-label">Ejemplo rápido</span>
              <p className="metric-explainer-copy">{buildMetricExample(metric)}</p>
            </div>
          ) : null}
        </>
      ) : (
        <>
          <div className="metric-explainer-head-row">
            <div className="eyebrow">Qué significa este dato</div>
            <button aria-label="Cerrar explicación de métrica" className="explain-banner-close metric-explainer-close" onClick={onClose} type="button">
              Cerrar
            </button>
          </div>
          <p className="metric-explainer-copy">Haz clic en cualquier tarjeta para ver qué significa, por qué es útil y cómo la calcula el producto.</p>
        </>
      )}
    </div>
  );
}

function RelativeRiskExplainerBanner({ onClose }: { onClose: () => void }) {
  return (
    <section aria-label="Cómo leer el ranking de zonas destacadas" aria-modal="false" className="explain-banner explain-banner-floating" role="dialog">
      <div className="explain-banner-header">
        <div className="explain-banner-headcopy">
          <span className="explain-banner-kicker">Cómo leer el ranking</span>
          <strong className="explain-banner-title">Cuanto más bajo, mejor</strong>
          <span className="explain-banner-summary">
            Este índice sirve para comparar zonas de un vistazo.
          </span>
        </div>
        <button aria-label="Cerrar explicación" className="explain-banner-close" onClick={onClose} type="button">
          Cerrar
        </button>
      </div>
      <div className="explain-banner-body">
        <p className="explain-banner-copy">
          El ranking principal de Zonas destacadas usa el índice relativo 0-1 del modelo para ordenar barrios y distritos. Cuanto más bajo, mejor.
        </p>
        <p className="explain-banner-copy">
          Al entrar en un barrio o distrito, el ranking interno de categorías se ordena con un índice contextual más robusto (el mismo enfoque de Oportunidades), que combina tasa de eventos, tamaño de muestra y penalización por soporte débil. Ahí mostramos solo el puesto de cada categoría para evitar mezclar escalas numéricas distintas.
        </p>
        <div className="explain-banner-example">
          <span className="explain-banner-example-label">Ejemplo</span>
          <p className="explain-banner-copy">
            Si un barrio marca 0,40 y otro 0,70, el de 0,40 tiene menos riesgo. Si ves un 0,20, tiene todavía menos riesgo.
          </p>
        </div>
      </div>
    </section>
  );
}

type ZoneRankCardProps = {
  rank: number;
  zone: ZoneAggregate | null;
  emptyLabel: string;
  onSelectZone: (zone: ZoneAggregate) => void;
};

function ZoneList({ districtZones, barrioZones, onSelectZone }: ZoneListProps) {
  const rowCount = Math.max(districtZones.length, barrioZones.length);

  if (rowCount === 0) {
    return <p className="empty-note">Sin zonas suficientes para esta categoría.</p>;
  }

  const rows = Array.from({ length: rowCount }, (_, index) => ({
    rank: index + 1,
    district: districtZones[index] ?? null,
    barrio: barrioZones[index] ?? null
  }));

  return (
    <div className="zone-board">
      <div className="zone-board-head">
        <div className="section-title">Distritos</div>
        <div className="section-title">Barrios</div>
      </div>
      <div className="zone-board-body">
        {rows.map((row) => (
          <div className="zone-row" key={`zone-row:${row.rank}`}>
            <ZoneRankCard emptyLabel="Sin distrito suficiente" onSelectZone={onSelectZone} rank={row.rank} zone={row.district} />
            <ZoneRankCard emptyLabel="Sin barrio suficiente" onSelectZone={onSelectZone} rank={row.rank} zone={row.barrio} />
          </div>
        ))}
      </div>
    </div>
  );
}

function ZoneRankCard({ rank, zone, emptyLabel, onSelectZone }: ZoneRankCardProps) {
  if (!zone) {
    return (
      <div className="zone-list-item zone-list-item-empty">
        <div className="zone-list-top">
          <span className="zone-list-rank">#{rank}</span>
        </div>
        <strong className="zone-list-title">{emptyLabel}</strong>
      </div>
    );
  }

  return (
    <button
      aria-label={`Ver ranking de actividades en ${zone.zone_name}${zone.zone_context_name ? `, ${zone.zone_context_name}` : ""}`}
      className="zone-list-item zone-list-item-button"
      onClick={() => onSelectZone(zone)}
      type="button"
    >
      <div className="zone-list-top">
        <span className="zone-list-rank">#{rank}</span>
        <span className="zone-list-value">{formatRelativeRiskIndex(zone.avg_risk_percentile)}</span>
      </div>
      <strong className="zone-list-title">{zone.zone_name}</strong>
      <span className="zone-list-meta">{formatCompact(zone.n_locales)} locales · ver actividades</span>
    </button>
  );
}

function ZoneActivityExplainer({ insight, onClose }: { insight: ZoneActivityInsight; onClose: () => void }) {
  const scopeLabel = insight.zoneLevel === "district" ? "distrito" : "barrio";

  return (
    <section aria-label={`Ranking de actividades del ${scopeLabel}`} aria-modal="false" className="explain-banner explain-banner-floating" role="dialog">
      <div className="explain-banner-header">
        <div className="explain-banner-headcopy">
          <span className="explain-banner-kicker">Ranking territorial</span>
          <strong className="explain-banner-title">{insight.zoneName}</strong>
          <span className="explain-banner-summary">{buildZoneActivityInsightSummary(insight)}</span>
        </div>
        <button aria-label="Cerrar ranking territorial" className="explain-banner-close" onClick={onClose} type="button">
          Cerrar
        </button>
      </div>
      <div className="explain-banner-body">
        <p className="explain-banner-copy">
          Ordenamos las macrocategorías de este {scopeLabel} por menor riesgo contextual, con el mismo criterio de Oportunidades: combinamos tasa de eventos, tamaño de muestra y una penalización suave cuando la evidencia local es débil.
        </p>
        <div className="metric-breakdown-list">
          {insight.items.map((item) => (
            <div className="metric-breakdown-item" key={`${insight.zoneLevel}:${insight.zoneCode}:${item.categoryCode}`}>
              <div className="metric-breakdown-main">
                <span className="metric-breakdown-rank">#{item.rank}</span>
                <span className="metric-breakdown-name">{item.categoryDesc}</span>
              </div>
              <span className="metric-breakdown-detail">{formatZoneActivityDetail(item, insight.horizon)}</span>
            </div>
          ))}
        </div>
        {insight.currentCategoryRank && insight.currentCategoryRank > insight.items.length ? (
          <p className="explain-banner-note">
            La categoría activa ahora mismo ocupa el puesto #{insight.currentCategoryRank} de {insight.totalActivities} actividades en este {scopeLabel}.
          </p>
        ) : null}
      </div>
    </section>
  );
}

function formatPercent(value: number | null, missingLabel = "Sin datos") {
  if (!isFiniteNumber(value)) {
    return missingLabel;
  }
  return `${(value * 100).toFixed(0)}%`;
}

function formatCompact(value: number) {
  return new Intl.NumberFormat("es-ES", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function formatHexRank(rank: number, total: number) {
  if (total <= 0) {
    return "-";
  }
  if (total === 1) {
    return "#1 de 1";
  }
  return `#${rank} de ${total}`;
}

function formatHexTopShare(rank: number, total: number) {
  if (total <= 0) {
    return "-";
  }
  const topShare = Math.max(1, Math.round((rank / total) * 100));
  return `top ${topShare}%`;
}

function formatRelativeRiskIndex(value: number | null, missingLabel = "Sin datos") {
  if (!isFiniteNumber(value)) {
    return missingLabel;
  }
  const clamped = Math.max(0, Math.min(1, value));
  return new Intl.NumberFormat("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(clamped);
}

function formatSignedPercent(value: number | null, missingLabel = "Sin muestra") {
  if (!isFiniteNumber(value)) {
    return missingLabel;
  }
  const points = value * 100;
  const prefix = points > 0 ? "+" : "";
  return `${prefix}${points.toFixed(0)} pp`;
}

function formatSignedIndexPoints(value: number | null, missingLabel = "Sin muestra") {
  if (!isFiniteNumber(value)) {
    return missingLabel;
  }
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${new Intl.NumberFormat("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)} pts`;
}

function formatSupport(support: number, total: number) {
  return `${formatCompact(support)} / ${formatCompact(total)}`;
}

function formatZoneConfidenceTier(value: string) {
  if (value === "high") {
    return "Alta";
  }
  if (value === "medium") {
    return "Media";
  }
  if (value === "low") {
    return "Baja";
  }
  if (value === "very_low") {
    return "Muy baja";
  }
  return value;
}

function buildFallbackCategoryDefinition(categoryDesc: string) {
  return `Lectura agregada de la macrocategoría ${categoryDesc.toLowerCase()} sobre los locales históricos visibles en el mapa.`;
}

function capitalize(value: string) {
  if (!value) {
    return value;
  }
  return `${value.slice(0, 1).toUpperCase()}${value.slice(1)}`;
}

function getMapViewUnitLabel(mode: MapViewMode, plural: boolean) {
  if (mode === "district") {
    return plural ? "Distritos" : "distrito";
  }
  if (mode === "barrio") {
    return plural ? "Barrios" : "barrio";
  }
  return plural ? "Hexágonos" : "hexágono";
}

function buildSelectedUnitSummary({
  categoryDesc,
  detailHex,
  detailZone,
}: {
  categoryDesc: string;
  detailHex: HexAggregate | null;
  detailZone: ZoneAggregate | null;
}) {
  if (detailHex) {
    return [detailHex.barrio_name, detailHex.district_name, categoryDesc].filter(Boolean).join(" · ");
  }

  if (!detailZone) {
    return categoryDesc;
  }

  const contextParts = [
    detailZone.zone_level === "barrio" ? detailZone.zone_context_name : "Madrid",
    categoryDesc,
  ].filter((value): value is string => Boolean(value));
  return contextParts.join(" · ");
}

function buildVisibleStats<T extends MapAggregateMetrics>(items: T[], horizon: Horizon): VisibleStats {
  if (items.length === 0) {
    return {
      locales: 0,
      meanRelativeRisk: null,
      meanSurvival: null,
      units: 0,
      unitsWithSupport: 0,
    };
  }

  const locales = items.reduce((sum, item) => sum + item.n_locales, 0);
  const survivalTotals = items.reduce(
    (accumulator, item) => {
      const support = getHorizonSupport(item, horizon);
      const survival = getHorizonSurvival(item, horizon);
      if (support > 0 && isFiniteNumber(survival)) {
        accumulator.unitsWithSupport += 1;
        accumulator.supportedLocales += support;
        accumulator.weightedSurvival += support * survival;
      }
      return accumulator;
    },
    { unitsWithSupport: 0, supportedLocales: 0, weightedSurvival: 0 }
  );
  const meanRelativeRisk = locales > 0
    ? items.reduce((sum, item) => sum + item.n_locales * item.avg_risk_percentile, 0) / locales
    : null;

  return {
    locales,
    meanRelativeRisk,
    meanSurvival: survivalTotals.supportedLocales > 0 ? survivalTotals.weightedSurvival / survivalTotals.supportedLocales : null,
    units: items.length,
    unitsWithSupport: survivalTotals.unitsWithSupport,
  };
}

function computeWeightedMeanRiskIndex<T extends Pick<MapAggregateMetrics, "avg_risk_percentile" | "n_locales">>(items: T[]) {
  const totalLocales = items.reduce((sum, item) => sum + item.n_locales, 0);
  if (totalLocales <= 0) {
    return null;
  }
  return items.reduce((sum, item) => sum + item.n_locales * item.avg_risk_percentile, 0) / totalLocales;
}

function buildTopZones(zones: ZoneAggregate[], minLocalesForColor: number) {
  if (zones.length === 0) {
    return [];
  }

  const rankedColorable = sortZonesByRisk(zones.filter((item) => item.n_locales >= minLocalesForColor));
  if (rankedColorable.length >= 3) {
    return rankedColorable.slice(0, 3);
  }

  const fallbackMinLocales = zones[0].zone_level === "district"
    ? MIN_UNSUPPORTED_DISTRICT_LOCALES
    : MIN_UNSUPPORTED_BARRIO_LOCALES;
  const fallbackFloor = Math.min(minLocalesForColor, fallbackMinLocales);
  const rankedFallback = sortZonesByRisk(zones.filter((item) => item.n_locales >= fallbackFloor));
  if (rankedFallback.length >= 3) {
    return rankedFallback.slice(0, 3);
  }

  return sortZonesByRisk(zones).slice(0, 3);
}

function buildZoneActivityInsight({
  zone,
  zonePool,
  currentCategoryCode,
  horizon,
}: {
  zone: ZoneAggregate;
  zonePool: ZoneAggregate[];
  currentCategoryCode: string;
  horizon: Horizon;
}): ZoneActivityInsight | null {
  const matchingZones = zonePool.filter(
    (item) => item.zone_code === zone.zone_code && item.category_code !== "__all__" && !item.category_code.startsWith("__status_")
  );
  if (matchingZones.length === 0) {
    return null;
  }

  const priorEventRate = resolveZoneActivityPriorEventRate(matchingZones);

  const rankedActivities: ZoneActivityRankingRow[] = sortZoneActivitiesByOpportunityMethod(
    matchingZones.map((item) => {
      const eventRate = isFiniteNumber(item.event_rate) ? item.event_rate : null;
      const activityRisk = computeZoneActivityContextualRisk({
        eventRate,
        nLocales: item.n_locales,
        priorEventRate,
        supportedForStats: item.supported_for_stats,
      });
      return {
        globalRank: 0,
        categoryCode: item.category_code,
        categoryDesc: item.category_desc,
        riskIndex: activityRisk,
        survival: horizon === "24m" ? item.survival_24m : item.survival_12m,
        support: horizon === "24m" ? item.support_24m : item.support_12m,
        nLocales: item.n_locales,
        activityRisk,
        eventRate,
      };
    })
  ).map((item, index) => ({
    ...item,
    globalRank: index + 1,
  }));

  const visibleActivities = rankedActivities.slice(0, ZONE_ACTIVITY_VISIBLE_LIMIT);
  const currentCategoryRow = currentCategoryCode === "__all__"
    ? null
    : rankedActivities.find((item) => item.categoryCode === currentCategoryCode) ?? null;
  const currentCategoryRank = currentCategoryRow?.globalRank ?? null;

  return {
    zoneLevel: zone.zone_level,
    zoneCode: zone.zone_code,
    zoneName: zone.zone_name,
    horizon,
    totalActivities: rankedActivities.length,
    currentCategoryDesc: currentCategoryRow?.categoryDesc ?? zone.category_desc,
    currentCategoryRank,
    items: visibleActivities.map(({ globalRank: _globalRank, ...item }, index) => ({
      ...item,
      rank: index + 1,
    })),
  };
}

function resolveZoneActivityPriorEventRate(zones: ZoneAggregate[]) {
  const supportedRates = zones
    .filter((item) => item.supported_for_stats)
    .map((item) => item.event_rate)
    .filter(isFiniteNumber);
  const fallbackRates = zones.map((item) => item.event_rate).filter(isFiniteNumber);
  const baseRates = supportedRates.length > 0 ? supportedRates : fallbackRates;
  if (baseRates.length === 0) {
    return ZONE_ACTIVITY_DEFAULT_PRIOR_EVENT_RATE;
  }
  return quantile([...baseRates].sort((left, right) => left - right), 0.5);
}

function computeZoneActivityContextualRisk({
  eventRate,
  nLocales,
  priorEventRate,
  supportedForStats,
}: {
  eventRate: number | null;
  nLocales: number;
  priorEventRate: number;
  supportedForStats: boolean;
}) {
  const resolvedEventRate = clamp(eventRate ?? priorEventRate, 0, 1);
  const resolvedSupport = Math.max(0, nLocales);
  const shrunk = ((resolvedEventRate * resolvedSupport) + (priorEventRate * ZONE_ACTIVITY_PRIOR_STRENGTH))
    / (resolvedSupport + ZONE_ACTIVITY_PRIOR_STRENGTH);
  const withSupportPenalty = supportedForStats ? shrunk : shrunk + ZONE_ACTIVITY_UNSUPPORTED_PENALTY;
  return clamp(withSupportPenalty, 0, 1);
}

function sortZoneActivitiesByOpportunityMethod(activities: ZoneActivityRankingRow[]) {
  return [...activities].sort((left, right) => {
    const contextualRiskDiff = left.activityRisk - right.activityRisk;
    if (Math.abs(contextualRiskDiff) > 1e-6) {
      return contextualRiskDiff;
    }

    const leftEventRate = left.eventRate ?? Number.POSITIVE_INFINITY;
    const rightEventRate = right.eventRate ?? Number.POSITIVE_INFINITY;
    const eventRateDiff = leftEventRate - rightEventRate;
    if (Math.abs(eventRateDiff) > 1e-6) {
      return eventRateDiff;
    }

    const leftSurvival = left.survival ?? Number.NEGATIVE_INFINITY;
    const rightSurvival = right.survival ?? Number.NEGATIVE_INFINITY;
    const survivalDiff = rightSurvival - leftSurvival;
    if (Math.abs(survivalDiff) > 1e-6) {
      return survivalDiff;
    }

    if (right.nLocales !== left.nLocales) {
      return right.nLocales - left.nLocales;
    }

    return left.categoryDesc.localeCompare(right.categoryDesc, "es");
  });
}

function buildZoneActivityInsightSummary(insight: ZoneActivityInsight) {
  const scopeLabel = insight.zoneLevel === "district" ? "distrito" : "barrio";
  if (isFiniteNumber(insight.currentCategoryRank)) {
    return `${insight.currentCategoryDesc} ocupa el puesto #${insight.currentCategoryRank} de ${insight.totalActivities} actividades en este ${scopeLabel}.`;
  }
  return `Consulta qué macrocategorías salen mejor dentro de este ${scopeLabel}.`;
}

function formatZoneActivityDetail(item: ZoneActivityRankingItem, horizon: Horizon) {
  const horizonLabel = formatHorizonShortLabel(horizon);
  const survivalLabel = formatPercent(item.survival, item.support > 0 ? "Sin datos" : "Sin muestra");
  return `Superv. ${horizonLabel} ${survivalLabel} · ${formatCompact(item.nLocales)} locales`;
}

function sortZonesByRisk(zones: ZoneAggregate[]) {
  return [...zones].sort((left, right) => {
    const riskDiff = left.avg_risk_percentile - right.avg_risk_percentile;
    if (Math.abs(riskDiff) > 1e-6) {
      return riskDiff;
    }
    const rawRiskDiff = getPrimaryRiskValue(left) - getPrimaryRiskValue(right);
    if (Math.abs(rawRiskDiff) > 1e-6) {
      return rawRiskDiff;
    }
    if (right.n_locales !== left.n_locales) {
      return right.n_locales - left.n_locales;
    }
    return left.zone_name.localeCompare(right.zone_name, "es");
  });
}

function buildZoneRanking(zones: ZoneAggregate[], detail: ZoneAggregate) {
  const sorted = sortZonesByRisk(zones);
  const rankIndex = sorted.findIndex((item) => item.zone_code === detail.zone_code);
  if (rankIndex < 0) {
    return null;
  }

  return { rank: rankIndex + 1, total: sorted.length };
}

function buildZoneMetrics({
  detail,
  detailRank,
  detailSupport,
  detailSurvival,
  horizon,
  meanRiskIndex,
}: {
  detail: ZoneAggregate;
  detailRank: { rank: number; total: number } | null;
  detailSupport: number;
  detailSurvival: number | null;
  horizon: Horizon;
  meanRiskIndex: number | null;
}): MetricDefinition[] {
  const horizonLabel = horizon === "24m" ? "24 meses" : "12 meses";
  const unitLabel = detail.zone_level === "district" ? "distrito" : "barrio";
  const rankTopShare = detailRank ? formatHexTopShare(detailRank.rank, detailRank.total) : "-";
  const detailKey = `zone:${detail.zone_level}:${detail.zone_code}`;
  const confidenceLabel = formatZoneConfidenceTier(detail.confidence_tier);
  const desiredOrder = [
    `${detailKey}:locales`,
    `${detailKey}:city-rank`,
    `${detailKey}:risk-percentile`,
    `${detailKey}:vs-category`,
    `${detailKey}:survival:${horizon}`,
    `${detailKey}:support:${horizon}`,
    `${detailKey}:event-rate`,
    `${detailKey}:confidence`,
  ];

  return [
    {
      id: `${detailKey}:locales`,
      label: `Locales del ${unitLabel}`,
      value: new Intl.NumberFormat("es-ES").format(detail.n_locales),
      summary: `Cuenta cuántos locales históricos visibles de la categoría activa quedan agregados dentro de este ${unitLabel}.`,
      calculation: `Es el recuento agregado de locales asociados a este ${unitLabel} después de aplicar la categoría seleccionada.`,
    },
    {
      id: `${detailKey}:city-rank`,
      label: "Ranking Madrid",
      value: detailRank ? formatHexRank(detailRank.rank, detailRank.total) : "-",
      summary: `Top dinámico actual: ${rankTopShare}. Sitúa este ${unitLabel} frente al resto de ${detail.zone_level === "district" ? "distritos" : "barrios"} visibles de Madrid en la categoría activa.`,
      calculation: `Ordenamos todos los ${detail.zone_level === "district" ? "distritos" : "barrios"} visibles de esta categoría por menor riesgo medio. El puesto #1 es el que sale mejor en esa comparación.`,
    },
    {
      id: `${detailKey}:risk-percentile`,
      label: "Índice relativo 0-1",
      value: formatRelativeRiskIndex(detail.avg_risk_percentile),
      summary: `Es la lectura principal del mapa territorial. Cuanto más cerca de 0, mejor posición relativa tiene este ${unitLabel} dentro de la categoría activa.`,
      calculation: `Convertimos el riesgo agregado del ${unitLabel} en un índice entre 0 y 1 comparándolo con el resto de ${detail.zone_level === "district" ? "distritos" : "barrios"} de la misma categoría en Madrid.`,
    },
    {
      id: `${detailKey}:vs-category`,
      label: "Índice vs. media",
      value: formatSignedIndexPoints(
        computeRiskIndexDelta(detail.avg_risk_percentile, meanRiskIndex),
        isFiniteNumber(meanRiskIndex) ? "Sin datos" : "Sin muestra"
      ),
      summary: `Compara el índice relativo de este ${unitLabel} con la media de la categoría activa dentro del mismo tipo de unidad territorial.`,
      calculation: `Restamos la media del índice relativo de la categoría al índice de este ${unitLabel}. Los valores negativos indican mejor posición relativa que la media.`,
    },
    {
      id: `${detailKey}:survival:${horizon}`,
      label: `Supervivencia ${horizonLabel}`,
      value: formatPercent(detailSurvival, detailSupport > 0 ? "Sin datos" : "Sin muestra"),
      summary: `Muestra que parte de los locales comparables sigue activa en este ${unitLabel} al llegar a ${horizonLabel}.`,
      calculation: `Tomamos los locales de esta categoría con observación suficiente en ${horizonLabel} y calculamos su supervivencia observada agregada en este ${unitLabel}.`,
    },
    {
      id: `${detailKey}:support:${horizon}`,
      label: `Soporte ${horizonLabel}`,
      value: formatSupport(detailSupport, detail.n_locales),
      summary: `Te dice cuántos locales sostienen de verdad la métrica frente al total visible en este ${unitLabel}.`,
      calculation: `El numerador cuenta los locales con observacion valida en ${horizonLabel}; el denominador es el total de locales agregados del ${unitLabel}.`,
    },
    {
      id: `${detailKey}:event-rate`,
      label: "Rotación histórica",
      value: formatPercent(detail.event_rate, "Sin muestra"),
      summary: `Mide qué porcentaje de locales de esta categoría registra cierres o cambios de actividad dentro de este ${unitLabel}.`,
      calculation: `Calculamos los eventos observados divididos por los locales históricos agregados del ${unitLabel}. Cuanto más alto, mayor rotación comercial observada.`,
    },
    {
      id: `${detailKey}:confidence`,
      label: "Confianza histórica",
      value: confidenceLabel,
      summary: `Te indica cuánta base histórica sostiene la lectura de este ${unitLabel}; sirve para separar señales robustas de lecturas más finas o frágiles.`,
      calculation: "La asignamos a partir del número de locales y eventos históricos disponibles en la unidad. Distritos y barrios usan umbrales distintos según su escala.",
    },
  ].sort((left, right) => desiredOrder.indexOf(left.id) - desiredOrder.indexOf(right.id));
}

function buildHexMetrics({
  detail,
  detailRank,
  detailSupport,
  detailSurvival,
  horizon,
  meanRiskIndex
}: {
  detail: HexAggregate;
  detailRank: { rank: number; total: number } | null;
  detailSupport: number;
  detailSurvival: number | null;
  horizon: Horizon;
  meanRiskIndex: number | null;
}): MetricDefinition[] {
  const horizonLabel = horizon === "24m" ? "24 meses" : "12 meses";
  const rankTopShare = detailRank ? formatHexTopShare(detailRank.rank, detailRank.total) : "-";
  const desiredOrder = [
    `hex:${detail.h3_cell}:locales`,
    `hex:${detail.h3_cell}:city-rank`,
    `hex:${detail.h3_cell}:risk-percentile`,
    `hex:${detail.h3_cell}:vs-category`,
    `hex:${detail.h3_cell}:survival:${horizon}`,
    `hex:${detail.h3_cell}:support:${horizon}`,
    `hex:${detail.h3_cell}:barrio-name`,
    `hex:${detail.h3_cell}:district-name`,
  ];
  return [
    {
      id: `hex:${detail.h3_cell}:locales`,
      label: "Locales del hexágono",
      value: new Intl.NumberFormat("es-ES").format(detail.n_locales),
      summary: "Cuenta cuántos locales históricos caen dentro de este hexágono para la categoría activa.",
      calculation: "Es el recuento agregado de locales visibles en este hexágono tras aplicar la categoría seleccionada."
    },
    {
      id: `hex:${detail.h3_cell}:city-rank`,
      label: "Ranking Madrid",
      value: detailRank ? formatHexRank(detailRank.rank, detailRank.total) : "-",
      summary: `Top dinámico actual: ${rankTopShare}. Te dice en qué puesto queda este hexágono dentro de Madrid para la categoría activa cuando ordenas de menor a mayor riesgo.`,
      calculation: "Ordenamos todos los hexágonos visibles de esta categoría por riesgo medio. El puesto #1 es el que sale mejor en esa comparación."
    },
    {
      id: `hex:${detail.h3_cell}:risk-percentile`,
      label: "Índice relativo 0-1",
      value: formatRelativeRiskIndex(detail.avg_risk_percentile),
      summary: "Es la lectura principal del mapa. Cuanto más cerca de 0, mejor posición relativa tiene esta zona dentro de la categoría activa.",
      calculation: "Convertimos el riesgo del hexágono en un índice entre 0 y 1 comparándolo con el resto de hexágonos de la misma categoría en Madrid. Los valores bajos salen mejor; los altos, peor."
    },
    {
      id: `hex:${detail.h3_cell}:vs-category`,
      label: "Índice vs media",
      value: formatSignedIndexPoints(computeRiskIndexDelta(detail.avg_risk_percentile, meanRiskIndex), isFiniteNumber(meanRiskIndex) ? "Sin datos" : "Sin muestra"),
      summary: "Compara el índice relativo de este hexágono contra la media de riesgo de la categoría activa en Madrid.",
      calculation: "Restamos la media de índice relativo de la categoría al índice del hexágono y mostramos la diferencia en puntos de índice. Valores negativos indican mejor posición relativa (menos riesgo) que la media."
    },
    {
      id: `hex:${detail.h3_cell}:survival:${horizon}`,
      label: `Supervivencia ${horizonLabel}`,
      value: formatPercent(detailSurvival, detailSupport > 0 ? "Sin datos" : "Sin muestra"),
      summary: `Muestra qué parte de los locales comparables sigue activa en este hexágono al llegar a ${horizonLabel}.`,
      calculation: `Tomamos los locales de esta categoría con observación suficiente en ${horizonLabel} y calculamos su supervivencia observada agregada en este hexágono.`
    },
    {
      id: `hex:${detail.h3_cell}:support:${horizon}`,
      label: `Soporte ${horizonLabel}`,
      value: formatSupport(detailSupport, detail.n_locales),
      summary: "Te dice cuántos locales sostienen de verdad la métrica frente al total visible en el hexágono.",
      calculation: `El numerador cuenta los locales con observación válida en ${horizonLabel}; el denominador es el total de locales agregados del hexágono.`
    },
    {
      id: `hex:${detail.h3_cell}:barrio-name`,
      label: "Barrio",
      value: detail.barrio_name || "Sin asignar",
      summary: "Sitúa el hexágono en un nombre reconocible de barrio para leer el mapa más rápido.",
      calculation: "Se infiere a partir de la geografía censal enlazada al hexágono y se usa como referencia interpretativa, no como límite exacto del polígono H3."
    },
    {
      id: `hex:${detail.h3_cell}:district-name`,
      label: "Distrito",
      value: detail.district_name || "Sin asignar",
      summary: "Añade la referencia administrativa más útil para ubicar la zona de un vistazo.",
      calculation: "Se recupera desde la mejor asignación geográfica disponible entre las secciones históricas y el hexágono H3."
    }
  ].sort((left, right) => desiredOrder.indexOf(left.id) - desiredOrder.indexOf(right.id));
}

function buildMetricWhyUsefulLegacy(metric: MetricDefinition) {
  if (metric.id.endsWith(":locales")) {
    return "Te da una lectura de tamaño inmediato: ayuda a diferenciar si estás viendo un hexágono muy representativo o uno con base pequeña.";
  }
  if (metric.id.endsWith(":city-rank")) {
    return "Te ayuda a priorizar rápido: con una sola cifra ves si este hexágono está entre los mejores o peores de la categoría activa dentro de Madrid.";
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Es la lectura más fácil de comparar entre zonas: 0,10 se entiende enseguida como mejor posición relativa que 0,70 sin tener que entrar en la puntuación técnica del modelo.";
  }
  if (metric.id.endsWith(":vs-category")) {
    return "Te da una lectura relativa inmediata: ves si el riesgo de este hexágono está por encima o por debajo del nivel medio de su categoría en Madrid.";
  }
  if (metric.id.includes(":survival:")) {
    return "Convierte el mapa en una pregunta de negocio muy directa: qué continuidad histórica ha tenido esta categoría aquí en el horizonte elegido.";
  }
  if (metric.id.includes(":support:")) {
    return "Te protege de falsas certezas: una cifra buena con poco soporte vale menos que una lectura parecida con más base histórica.";
  }
  if (metric.id.endsWith(":barrio-name") || metric.id.endsWith(":district-name")) {
    return "Te orienta territorialmente y hace más fácil relacionar el hexágono con zonas reconocibles de Madrid sin tener que leer un identificador H3.";
  }
  return "Aporta contexto adicional para interpretar mejor el comportamiento histórico del hexágono seleccionado.";
}

function buildMetricExampleLegacy(metric: MetricDefinition) {
  if (metric.id.endsWith(":locales")) {
    return "Ejemplo: 34 locales significa que el histórico útil de esta categoría en este hexágono está construido con 34 observaciones agregadas.";
  }
  if (metric.id.endsWith(":city-rank")) {
    return "Ejemplo: #45 de 3.200 significa que este hexágono sale muy arriba dentro del mapa de esa categoría cuando ordenas por menor riesgo.";
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Ejemplo: 0,20 indica que el hexágono cae en una franja mejor que buena parte del mapa; equivale aproximadamente a un P20.";
  }
  if (metric.id.endsWith(":vs-category")) {
    return "Ejemplo: -0,08 pts significa que el índice del hexágono está por debajo de la media (mejor posición relativa de riesgo).";
  }
  if (metric.id.includes(":support:")) {
    return "Ejemplo: 18 / 26 quiere decir que 18 locales del total de 26 tienen observación válida para ese horizonte.";
  }
  return null;
}

function buildMetricWhyUseful(metric: MetricDefinition) {
  const unitLabel = metric.id.startsWith("hex:") ? "hexágono" : "unidad territorial";
  if (metric.id.endsWith(":locales")) {
    return `Te da una lectura de tamaño inmediato: ayuda a diferenciar si estás viendo un ${unitLabel} muy representativo o uno con base pequeña.`;
  }
  if (metric.id.endsWith(":city-rank")) {
    return `Te ayuda a priorizar rápido: con una sola cifra ves si este ${unitLabel} está entre los mejores o peores de la categoría activa dentro de Madrid.`;
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Es la lectura más fácil de comparar entre zonas: 0,10 se entiende enseguida como mejor posición relativa que 0,70 sin tener que entrar en la puntuación técnica del modelo.";
  }
  if (metric.id.endsWith(":vs-category")) {
    return `Te da una lectura relativa inmediata: ves si el riesgo de este ${unitLabel} está por encima o por debajo del nivel medio de su categoría en Madrid.`;
  }
  if (metric.id.includes(":survival:")) {
    return "Convierte el mapa en una pregunta de negocio muy directa: qué continuidad histórica ha tenido esta categoría aquí en el horizonte elegido.";
  }
  if (metric.id.includes(":support:")) {
    return "Te protege de falsas certezas: una cifra buena con poco soporte vale menos que una lectura parecida con más base histórica.";
  }
  if (metric.id.endsWith(":event-rate")) {
    return "Resume la rotación comercial de forma muy directa: cuánto porcentaje de locales termina cerrando o cambiando de actividad en esta zona.";
  }
  if (metric.id.endsWith(":confidence")) {
    return "Te recuerda cuánta evidencia real hay detrás de la lectura. Es clave cuando comparas zonas pequeñas o categorías con poca historia.";
  }
  if (metric.id.endsWith(":barrio-name") || metric.id.endsWith(":district-name")) {
    return "Te orienta territorialmente y hace más fácil relacionar el hexágono con zonas reconocibles de Madrid sin tener que leer un identificador H3.";
  }
  return `Aporta contexto adicional para interpretar mejor el comportamiento histórico del ${unitLabel} seleccionado.`;
}

function buildMetricExample(metric: MetricDefinition) {
  const unitLabel = metric.id.startsWith("hex:") ? "hexágono" : "unidad";
  if (metric.id.endsWith(":locales")) {
    return `Ejemplo: 34 locales significa que el histórico útil de esta categoría en esta ${unitLabel} está construido con 34 observaciones agregadas.`;
  }
  if (metric.id.endsWith(":city-rank")) {
    return `Ejemplo: #45 de 3.200 significa que esta ${unitLabel} sale muy arriba dentro del mapa de esa categoría cuando ordenas por menor riesgo.`;
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return `Ejemplo: 0,20 indica que esta ${unitLabel} cae en una franja mejor que buena parte del mapa; equivale aproximadamente a un P20.`;
  }
  if (metric.id.endsWith(":vs-category")) {
    return `Ejemplo: -0,08 pts significa que el índice de esta ${unitLabel} está por debajo de la media, con una mejor posición relativa de riesgo.`;
  }
  if (metric.id.includes(":support:")) {
    return "Ejemplo: 18 / 26 quiere decir que 18 locales del total de 26 tienen observacion valida para ese horizonte.";
  }
  if (metric.id.endsWith(":event-rate")) {
    return "Ejemplo: 22% implica que, históricamente, unos 22 de cada 100 locales comparables acabaron cerrando o cambiando de actividad.";
  }
  if (metric.id.endsWith(":confidence")) {
    return "Ejemplo: confianza media significa que la unidad ya tiene cierta base histórica, pero todavía conviene leerla junto con soporte y volumen.";
  }
  return null;
}

function buildHexRanking(hexes: HexAggregate[], detail: HexAggregate, _horizon: Horizon) {
  const sorted = [...hexes].sort((left, right) => {
    const rawRiskDiff = getPrimaryRiskValue(left) - getPrimaryRiskValue(right);
    if (Math.abs(rawRiskDiff) > 1e-6) {
      return rawRiskDiff;
    }
    const riskDiff = left.avg_risk_percentile - right.avg_risk_percentile;
    if (Math.abs(riskDiff) > 1e-6) {
      return riskDiff;
    }
    if (right.n_locales !== left.n_locales) {
      return right.n_locales - left.n_locales;
    }
    return left.h3_cell.localeCompare(right.h3_cell, "es");
  });

  const rankIndex = sorted.findIndex((item) => item.h3_cell === detail.h3_cell);
  if (rankIndex < 0) {
    return null;
  }

  return { rank: rankIndex + 1, total: sorted.length };
}

function buildHexCategoryComposition(
  hexes: HexAggregate[],
  detail: HexAggregate,
  categoryColorMap: Map<string, string>
): HexCategoryCompositionItem[] {
  const totalLocales = detail.n_locales;
  if (totalLocales <= 0) {
    return [];
  }

  const orderedItems = hexes
    .filter((item) => item.h3_cell === detail.h3_cell && item.category_code !== "__all__" && item.n_locales > 0)
    .sort((left, right) => {
      if (right.n_locales !== left.n_locales) {
        return right.n_locales - left.n_locales;
      }
      return left.category_desc.localeCompare(right.category_desc, "es");
    });

  return orderedItems.map((item) => ({
    categoryCode: item.category_code,
    categoryDesc: item.category_desc,
    nLocales: item.n_locales,
    share: item.n_locales / totalLocales,
    color: colorForCategoryCode(item.category_code, categoryColorMap),
  }));
}

function buildHexCategoryCompositionForYear(
  rows: HexCompositionHistoryRecord[],
  categoryColorMap: Map<string, string>
): { items: HexCategoryCompositionItem[]; totalLocales: number } {
  if (rows.length === 0) {
    return { items: [], totalLocales: 0 };
  }

  const totalRow = rows.find((item) => item.category_code === "__all__") ?? null;
  const fallbackTotal = rows.reduce((maxTotal, item) => Math.max(maxTotal, item.hex_total_locales), 0);
  const totalLocales = Math.max(totalRow?.n_locales ?? fallbackTotal, 0);
  if (totalLocales <= 0) {
    return { items: [], totalLocales: 0 };
  }

  const orderedItems = rows
    .filter((item) => item.category_code !== "__all__" && item.n_locales > 0)
    .sort((left, right) => {
      if (right.n_locales !== left.n_locales) {
        return right.n_locales - left.n_locales;
      }
      return left.category_desc.localeCompare(right.category_desc, "es");
    });

  return {
    totalLocales,
    items: orderedItems.map((item) => ({
      categoryCode: item.category_code,
      categoryDesc: item.category_desc,
      nLocales: item.n_locales,
      share: item.share_in_hex ?? item.n_locales / totalLocales,
      color: colorForCategoryCode(item.category_code, categoryColorMap),
    })),
  };
}

function buildZoneCategoryComposition(
  zones: ZoneAggregate[],
  detail: ZoneAggregate,
  categoryColorMap: Map<string, string>
): HexCategoryCompositionItem[] {
  const totalLocales = detail.n_locales;
  if (totalLocales <= 0) {
    return [];
  }

  const orderedItems = zones
    .filter((item) => item.zone_code === detail.zone_code && item.category_code !== "__all__" && item.n_locales > 0)
    .sort((left, right) => {
      if (right.n_locales !== left.n_locales) {
        return right.n_locales - left.n_locales;
      }
      return left.category_desc.localeCompare(right.category_desc, "es");
    });

  return orderedItems.map((item) => ({
    categoryCode: item.category_code,
    categoryDesc: item.category_desc,
    nLocales: item.n_locales,
    share: item.n_locales / totalLocales,
    color: colorForCategoryCode(item.category_code, categoryColorMap),
  }));
}

function buildZoneCategoryCompositionForYear(
  rows: HistoricalZoneRankingRecord[],
  categoryColorMap: Map<string, string>
): { items: HexCategoryCompositionItem[]; totalLocales: number } {
  if (rows.length === 0) {
    return { items: [], totalLocales: 0 };
  }

  const totalLocales = rows.reduce((maxTotal, item) => Math.max(maxTotal, item.zone_total_locales), 0);
  if (totalLocales <= 0) {
    return { items: [], totalLocales: 0 };
  }

  const orderedItems = rows
    .filter((item) => item.category_code !== "__all__" && item.n_locales > 0)
    .sort((left, right) => {
      if (right.n_locales !== left.n_locales) {
        return right.n_locales - left.n_locales;
      }
      return left.category_desc.localeCompare(right.category_desc, "es");
    });

  return {
    totalLocales,
    items: orderedItems.map((item) => ({
      categoryCode: item.category_code,
      categoryDesc: item.category_desc,
      nLocales: item.n_locales,
      share: item.share_of_zone ?? item.n_locales / totalLocales,
      color: colorForCategoryCode(item.category_code, categoryColorMap),
    })),
  };
}

function resolveZoneCompositionHistoryRows(
  index: ZoneCompositionHistoryIndex,
  detailZone: ZoneAggregate,
  year: number,
): HistoricalZoneRankingRecord[] {
  const directMatch = index.byCode.get(`${detailZone.zone_level}::${year}::${detailZone.zone_code}`);
  if (directMatch) {
    return directMatch;
  }

  for (const identityKey of buildZoneHistoryIdentityKeys(
    detailZone.zone_level,
    detailZone.zone_name,
    detailZone.zone_context_name
  )) {
    const matchedRows = index.byIdentity.get(`${detailZone.zone_level}::${year}::${identityKey}`);
    if (matchedRows) {
      return matchedRows;
    }
  }

  return [];
}

function buildZoneHistoryIdentityKeys(
  zoneLevel: HistoricalZoneLevel,
  zoneName: string,
  zoneContextName?: string | null,
) {
  const normalizedContext = normalizeZoneHistoryIdentityPart(zoneContextName ?? "");
  if (!normalizedContext && zoneLevel === "barrio") {
    return [];
  }

  const nameVariants = buildZoneHistoryNameVariants(zoneName);
  return nameVariants.map((nameVariant) => `${normalizedContext}::${nameVariant}`);
}

function buildZoneHistoryNameVariants(zoneName: string) {
  const variants = new Set<string>();
  const normalizedName = normalizeZoneHistoryIdentityPart(zoneName);
  if (!normalizedName) {
    return [];
  }

  variants.add(normalizedName);
  variants.add(stripZoneArticles(normalizedName));
  variants.add(canonicalizeZoneHistoryName(normalizedName));
  variants.add(stripZoneArticles(canonicalizeZoneHistoryName(normalizedName)));

  const explicitAlias = BARRIO_HISTORY_NAME_ALIASES.get(normalizedName);
  if (explicitAlias) {
    variants.add(explicitAlias);
    variants.add(stripZoneArticles(explicitAlias));
    variants.add(canonicalizeZoneHistoryName(explicitAlias));
  }

  return [...variants].filter(Boolean);
}

function normalizeZoneHistoryIdentityPart(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function stripZoneArticles(value: string) {
  return value
    .split(" ")
    .filter((token) => !ZONE_HISTORY_ARTICLES.has(token))
    .join(" ")
    .trim();
}

function canonicalizeZoneHistoryName(value: string) {
  return value
    .replace(/\bcasco h\b/g, "casco historico")
    .replace(/\bcasco historico de\b/g, "casco historico")
    .replace(/\bfuentelareina\b/g, "fuentelarreina");
}

const HEX_COMPOSITION_COLOR_HUES = [16, 198, 332, 92, 258, 44, 172, 286, 8, 218, 126, 308, 64, 238, 152, 348, 106, 266, 186, 28, 138, 324];
const HEX_COMPOSITION_COLOR_TONES = [
  { saturation: 58, lightness: 67 },
  { saturation: 50, lightness: 75 },
];
const HEX_COMPOSITION_STATUS_COLORS: Record<string, string> = {
  __status_multi_activity__: "hsl(18 30% 69%)",
  __status_no_activity__: "hsl(8 20% 74%)",
  __status_uncoded_activity__: "hsl(28 28% 66%)",
  __status_pending_coding__: "hsl(12 18% 78%)",
  __status_missing_snapshot__: "hsl(35 20% 80%)",
  __status_unmapped_activity__: "hsl(24 24% 72%)",
};
const ZONE_HISTORY_ARTICLES = new Set(["de", "del", "el", "la", "las", "los"]);
const BARRIO_HISTORY_NAME_ALIASES = new Map<string, string>([
  ["aguilas", "las aguilas"],
  ["carmenes", "los carmenes"],
  ["casco historico de barajas", "casco h barajas"],
  ["casco historico de vallecas", "casco h vallecas"],
  ["casco historico de vicalvaro", "casco h vicalvaro"],
  ["fuentelareina", "fuentelarreina"],
  ["jeronimos", "los jeronimos"],
  ["penagrande", "pena grande"],
  ["pilar", "el pilar"],
  ["salvador", "el salvador"],
  ["villaverde alto casco historico de villaverde", "san andres"],
]);
const HEX_COMPOSITION_COLOR_PALETTE = buildHexCompositionPalette();

function buildHexCompositionPalette() {
  const colors: string[] = [];
  for (const tone of HEX_COMPOSITION_COLOR_TONES) {
    for (const hue of HEX_COMPOSITION_COLOR_HUES) {
      colors.push(`hsl(${hue} ${tone.saturation}% ${tone.lightness}%)`);
    }
  }
  return colors;
}

function buildHexCategoryColorMap(hexes: HexAggregate[]) {
  const categoryColorMap = new Map<string, string>();
  for (const [statusCode, statusColor] of Object.entries(HEX_COMPOSITION_STATUS_COLORS)) {
    categoryColorMap.set(statusCode, statusColor);
  }

  const categoryStats = new Map<string, HexCategoryColorStats>();
  const categoriesByHex = new Map<string, Array<{ categoryCode: string; nLocales: number }>>();

  for (const item of hexes) {
    if (item.category_code === "__all__" || item.n_locales <= 0 || item.category_code.startsWith("__status_")) {
      continue;
    }

    const currentStats = categoryStats.get(item.category_code) ?? { nLocales: 0 };
    currentStats.nLocales += item.n_locales;
    categoryStats.set(item.category_code, currentStats);

    const currentHexRows = categoriesByHex.get(item.h3_cell);
    if (currentHexRows) {
      currentHexRows.push({ categoryCode: item.category_code, nLocales: item.n_locales });
    } else {
      categoriesByHex.set(item.h3_cell, [{ categoryCode: item.category_code, nLocales: item.n_locales }]);
    }
  }

  if (categoryStats.size === 0) {
    return categoryColorMap;
  }

  const adjacency = new Map<string, Map<string, number>>();
  for (const entries of categoriesByHex.values()) {
    const sortedEntries = [...entries]
      .sort((left, right) => {
        if (right.nLocales !== left.nLocales) {
          return right.nLocales - left.nLocales;
        }
        return left.categoryCode.localeCompare(right.categoryCode, "es");
      })
      .slice(0, 10);

    for (let leftIndex = 0; leftIndex < sortedEntries.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < sortedEntries.length; rightIndex += 1) {
        const leftCategory = sortedEntries[leftIndex];
        const rightCategory = sortedEntries[rightIndex];
        const weight = Math.min(leftCategory.nLocales, rightCategory.nLocales);
        addCategoryAdjacency(adjacency, leftCategory.categoryCode, rightCategory.categoryCode, weight);
      }
    }
  }

  const orderedCategories = [...categoryStats.entries()]
    .sort((left, right) => {
      if (right[1].nLocales !== left[1].nLocales) {
        return right[1].nLocales - left[1].nLocales;
      }
      return left[0].localeCompare(right[0], "es");
    })
    .map(([categoryCode]) => categoryCode);

  const assignedPaletteIndexes = new Map<string, number>();
  const paletteUsageCounts = new Array(HEX_COMPOSITION_COLOR_PALETTE.length).fill(0);
  const hueFamilyUsageCounts = new Array(HEX_COMPOSITION_COLOR_HUES.length).fill(0);

  for (const categoryCode of orderedCategories) {
    let bestPaletteIndex = 0;
    let bestScore = Number.POSITIVE_INFINITY;

    for (let paletteIndex = 0; paletteIndex < HEX_COMPOSITION_COLOR_PALETTE.length; paletteIndex += 1) {
      let conflictScore = 0;
      const neighbors = adjacency.get(categoryCode);
      if (neighbors) {
        for (const [neighborCode, edgeWeight] of neighbors.entries()) {
          const neighborPaletteIndex = assignedPaletteIndexes.get(neighborCode);
          if (typeof neighborPaletteIndex !== "number") {
            continue;
          }

          const hueDistance = paletteHueDistanceSteps(paletteIndex, neighborPaletteIndex, HEX_COMPOSITION_COLOR_HUES.length);
          if (hueDistance === 0) {
            conflictScore += edgeWeight * 1.2;
          } else if (hueDistance === 1) {
            conflictScore += edgeWeight * 0.4;
          } else if (hueDistance === 2) {
            conflictScore += edgeWeight * 0.12;
          }
        }
      }

      const exactReusePenalty = paletteUsageCounts[paletteIndex] * 0.08;
      const hueFamilyPenalty = hueFamilyUsageCounts[paletteIndex % HEX_COMPOSITION_COLOR_HUES.length] * 0.03;
      const score = conflictScore + exactReusePenalty + hueFamilyPenalty;
      if (score < bestScore) {
        bestScore = score;
        bestPaletteIndex = paletteIndex;
      }
    }

    assignedPaletteIndexes.set(categoryCode, bestPaletteIndex);
    paletteUsageCounts[bestPaletteIndex] += 1;
    hueFamilyUsageCounts[bestPaletteIndex % HEX_COMPOSITION_COLOR_HUES.length] += 1;
    categoryColorMap.set(categoryCode, HEX_COMPOSITION_COLOR_PALETTE[bestPaletteIndex]);
  }

  return categoryColorMap;
}

function addCategoryAdjacency(
  adjacency: Map<string, Map<string, number>>,
  leftCategoryCode: string,
  rightCategoryCode: string,
  weight: number,
) {
  if (leftCategoryCode === rightCategoryCode || weight <= 0) {
    return;
  }

  const leftNeighbors = adjacency.get(leftCategoryCode) ?? new Map<string, number>();
  leftNeighbors.set(rightCategoryCode, (leftNeighbors.get(rightCategoryCode) ?? 0) + weight);
  adjacency.set(leftCategoryCode, leftNeighbors);

  const rightNeighbors = adjacency.get(rightCategoryCode) ?? new Map<string, number>();
  rightNeighbors.set(leftCategoryCode, (rightNeighbors.get(leftCategoryCode) ?? 0) + weight);
  adjacency.set(rightCategoryCode, rightNeighbors);
}

function paletteHueDistanceSteps(leftPaletteIndex: number, rightPaletteIndex: number, hueCount: number) {
  const leftHueIndex = leftPaletteIndex % hueCount;
  const rightHueIndex = rightPaletteIndex % hueCount;
  const directDistance = Math.abs(leftHueIndex - rightHueIndex);
  return Math.min(directDistance, hueCount - directDistance);
}

function colorForCategoryCode(categoryCode: string, categoryColorMap: Map<string, string>) {
  const mappedColor = categoryColorMap.get(categoryCode);
  if (mappedColor) {
    return mappedColor;
  }

  const seed = hashString(categoryCode);
  const baseHue = HEX_COMPOSITION_COLOR_HUES[seed % HEX_COMPOSITION_COLOR_HUES.length];
  const tone = HEX_COMPOSITION_COLOR_TONES[(seed >>> 3) % HEX_COMPOSITION_COLOR_TONES.length];
  const hueShift = ((seed % 5) - 2) * 2;
  const saturation = clamp(tone.saturation + (((seed >>> 5) % 3) - 1), 44, 62);
  const lightness = clamp(tone.lightness + (((seed >>> 7) % 3) - 1), 64, 80);
  return `hsl(${normalizeHue(baseHue + hueShift)} ${saturation}% ${lightness}%)`;
}

function normalizeHue(value: number) {
  return ((value % 360) + 360) % 360;
}

function hashString(value: string) {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) >>> 0;
  }
  return hash;
}

function getPrimaryRiskValue(item: RiskAggregate) {
  return item.avg_risk_primary ?? item.avg_risk_ensemble;
}

function buildColorScale<T extends MapAggregateMetrics>(items: T[]): ColorScale {
  const values = items
    .map((item) => item.avg_risk_percentile)
    .filter(isFiniteNumber)
    .sort((left, right) => left - right);

  if (values.length === 0) {
    return { min: 0, low: 0.25, mid: 0.5, high: 0.75, max: 1 };
  }

  const min = quantile(values, 0);
  const max = quantile(values, 1);
  const range = max - min;

  if (range <= 1e-6) {
    return { min, low: min, mid: min, high: min, max };
  }

  if (range < 0.025) {
    return {
      min,
      low: min + range * 0.24,
      mid: min + range * 0.52,
      high: min + range * 0.8,
      max
    };
  }

  const rawScale = {
    min,
    low: quantile(values, 0.18),
    mid: Math.min(quantile(values, 0.5), max > 0.95 ? 0.95 : max),
    high: quantile(values, 0.88),
    max
  };

  return ensureProgressiveScale(rawScale);
}

function ensureProgressiveScale(scale: ColorScale): ColorScale {
  const range = scale.max - scale.min;
  if (range <= 1e-6) {
    return scale;
  }

  const epsilon = Math.min(0.012, range / 6);
  const low = clamp(scale.low, scale.min + epsilon, scale.max - epsilon * 3);
  const mid = clamp(scale.mid, low + epsilon, scale.max - epsilon * 2);
  const high = clamp(scale.high, mid + epsilon, scale.max - epsilon);

  return {
    min: scale.min,
    low,
    mid,
    high,
    max: scale.max
  };
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function quantile(sortedValues: number[], q: number) {
  if (sortedValues.length === 1) {
    return sortedValues[0];
  }

  const position = (sortedValues.length - 1) * q;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);

  if (lower === upper) {
    return sortedValues[lower];
  }

  const weight = position - lower;
  return sortedValues[lower] * (1 - weight) + sortedValues[upper] * weight;
}

function buildGlobalSupportNoteLegacy(hexesWithSupport: number, totalHexes: number, horizon: Horizon) {
  const horizonLabel = formatHorizonLongLabel(horizon);
  if (totalHexes <= 0) {
    return `No hay hexágonos visibles para la categoría activa.`;
  }
  if (hexesWithSupport <= 0) {
    return `Ningún hexágono visible tiene soporte suficiente a ${horizonLabel}.`;
  }
  if (hexesWithSupport === totalHexes) {
    return `Todos los hexágonos visibles tienen soporte suficiente a ${horizonLabel}.`;
  }
  return `La supervivencia media y el color del mapa ignoran hexágonos sin soporte a ${horizonLabel}: ${formatCompact(hexesWithSupport)} de ${formatCompact(totalHexes)} sí tienen datos útiles.`;
}

function buildGlobalSupportNote({
  activeUnitLabelPlural,
  mapViewMode,
  totalUnits,
  unitsWithSupport,
  zoneColorFloor,
}: {
  activeUnitLabelPlural: string;
  mapViewMode: MapViewMode;
  totalUnits: number;
  unitsWithSupport: number;
  zoneColorFloor: number;
}) {
  const normalizedLabel = activeUnitLabelPlural.toLowerCase();
  const singularLabel = normalizedLabel.endsWith("s") ? normalizedLabel.slice(0, -1) : normalizedLabel;
  if (totalUnits <= 0) {
    return `No hay ${normalizedLabel} visibles para la categoría activa.`;
  }

  if (mapViewMode === "hex") {
    return unitsWithSupport > 0
      ? "El color del mapa usa el índice relativo 0-1. La supervivencia media se presenta en un horizonte de 24 meses para facilitar la comparación."
      : "El color del mapa usa el índice relativo 0-1. La supervivencia media queda fijada en 24 meses, pero ahora mismo no hay muestra suficiente para resumirla.";
  }

  if (unitsWithSupport <= 0) {
    return `El color del mapa usa el índice relativo 0-1 y se activa desde ${formatCompact(zoneColorFloor)} locales por ${singularLabel}. La supervivencia media a 24 meses sale sin muestra en esta categoría.`;
  }

  return `El color del mapa usa el índice relativo 0-1 y se activa desde ${formatCompact(zoneColorFloor)} locales por ${singularLabel}. La supervivencia media a 24 meses se calcula solo con unidades que sí tienen soporte real.`;
}

function buildZoneColorThresholds(
  zones: ZoneAggregate[],
  zoneLevel: HistoricalZoneLevel
) {
  const grouped = new Map<string, number[]>();
  for (const zone of zones) {
    if (zone.n_locales <= 0) {
      continue;
    }
    const bucket = grouped.get(zone.category_code);
    if (bucket) {
      bucket.push(zone.n_locales);
    } else {
      grouped.set(zone.category_code, [zone.n_locales]);
    }
  }

  const thresholds = new Map<string, number>();
  for (const [categoryCode, values] of grouped.entries()) {
    const ordered = [...values].sort((left, right) => left - right);
    const rawThreshold = Math.round(quantile(ordered, ZONE_COLOR_FLOOR_QUANTILE));
    const minFloor = zoneLevel === "district" ? DISTRICT_COLOR_FLOOR_MIN : BARRIO_COLOR_FLOOR_MIN;
    const maxFloor = zoneLevel === "district" ? DISTRICT_COLOR_FLOOR_MAX : BARRIO_COLOR_FLOOR_MAX;
    thresholds.set(categoryCode, clamp(rawThreshold, minFloor, maxFloor));
  }
  return thresholds;
}

function computeRiskIndexDelta(value: number | null, baseline: number | null) {
  if (!isFiniteNumber(value) || !isFiniteNumber(baseline)) {
    return null;
  }
  return value - baseline;
}

function buildZoneComparisonOptions({
  artifacts,
  categoryCode,
  zoneLevel,
}: {
  artifacts: HistoricalRankingArtifacts | null;
  categoryCode: string;
  zoneLevel: HistoricalZoneLevel;
}): ZoneComparisonOption[] {
  if (!artifacts) {
    return [];
  }

  const latestYear = artifacts.meta.latest_year;
  const rows = artifacts.zones[zoneLevel].filter((item) => item.category_code === categoryCode && item.year === latestYear);
  if (rows.length === 0) {
    return [];
  }

  const latestByZone = new Map<string, HistoricalZoneRankingRecord>();
  for (const row of rows) {
    const current = latestByZone.get(row.zone_key);
    if (!current || compareHistoricalRowsByTime(current, row) < 0) {
      latestByZone.set(row.zone_key, row);
    }
  }

  return [...latestByZone.values()]
    .sort((left, right) => formatZoneComparisonOptionLabel(left, zoneLevel).localeCompare(formatZoneComparisonOptionLabel(right, zoneLevel), "es"))
    .map((row) => ({
      label: formatZoneComparisonOptionLabel(row, zoneLevel),
      zoneKey: row.zone_key,
    }));
}

function formatZoneComparisonOptionLabel(row: HistoricalZoneRankingRecord, zoneLevel: HistoricalZoneLevel) {
  if (zoneLevel === "district" || !row.zone_context_name) {
    return row.zone_name;
  }
  return `${row.zone_name} · ${row.zone_context_name}`;
}

function compareHistoricalRowsByTime(left: HistoricalZoneRankingRecord, right: HistoricalZoneRankingRecord) {
  if (left.year !== right.year) {
    return left.year - right.year;
  }
  return left.period.localeCompare(right.period, "es");
}

