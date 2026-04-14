"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { HexCategoryComposition, type HexCategoryCompositionItem } from "@/components/hex-category-composition";
import { HistoricalEvolutionBanner } from "@/components/historical-evolution-banner";
import { MadridMap } from "@/components/madrid-map";
import { ViewTabs } from "@/components/view-tabs";
import { ZoneComparisonBanner } from "@/components/zone-comparison-banner";
import { DEFAULT_HEX_SIZE, formatHexSizeLabel, HEX_SIZE_OPTIONS, type HexSize } from "@/lib/hex-size";
import { formatHorizonLongLabel, formatHorizonShortLabel, getHorizonSupport, getHorizonSurvival, isFiniteNumber, type Horizon } from "@/lib/horizon";
import { FALLBACK_MAP_ARTIFACTS, loadHistoricalRankingsFromPublic, loadMapArtifactsFromPublic } from "@/lib/public-data";
import type { ColorScale, FrontendArtifacts, HexAggregate, HistoricalRankingArtifacts, HistoricalZoneLevel, HistoricalZoneRankingRecord, ZoneAggregate } from "@/lib/types";

type MapShellProps = {
  initialArtifacts?: FrontendArtifacts;
};

type MetricDefinition = {
  id: string;
  label: string;
  value: string;
  summary: string;
  calculation: string;
};

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

export function MapShell({ initialArtifacts }: MapShellProps) {
  const [artifacts, setArtifacts] = useState(initialArtifacts ?? FALLBACK_MAP_ARTIFACTS);
  const [isLoadingArtifacts, setIsLoadingArtifacts] = useState(!initialArtifacts);
  const [isSwitchingHexSize, setIsSwitchingHexSize] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState((initialArtifacts ?? FALLBACK_MAP_ARTIFACTS).meta.defaultCategoryCode);
  const [horizon, setHorizon] = useState<Horizon>("24m");
  const [hexSize, setHexSize] = useState<HexSize>(DEFAULT_HEX_SIZE);
  const [selectedHex, setSelectedHex] = useState<HexAggregate | null>(null);
  const [activeMetricId, setActiveMetricId] = useState<string | null>(null);
  const [isRiskExplainerOpen, setIsRiskExplainerOpen] = useState(false);
  const [activeZoneInsight, setActiveZoneInsight] = useState<ZoneActivityInsight | null>(null);
  const [historicalRankingArtifacts, setHistoricalRankingArtifacts] = useState<HistoricalRankingArtifacts | null>(null);
  const [historicalZoneLevel, setHistoricalZoneLevel] = useState<HistoricalZoneLevel>("district");
  const [isHistoricalEvolutionOpen, setIsHistoricalEvolutionOpen] = useState(false);
  const [comparisonZoneLevel, setComparisonZoneLevel] = useState<HistoricalZoneLevel>("district");
  const [comparisonLeftZoneKey, setComparisonLeftZoneKey] = useState("");
  const [comparisonRightZoneKey, setComparisonRightZoneKey] = useState("");
  const [isZoneComparisonOpen, setIsZoneComparisonOpen] = useState(false);
  const [isLoadingHistoricalRankings, setIsLoadingHistoricalRankings] = useState(false);
  const loadedArtifactsRef = useRef<Partial<Record<HexSize, FrontendArtifacts>>>(
    initialArtifacts ? { [DEFAULT_HEX_SIZE]: initialArtifacts } : {}
  );
  const historicalRankingsRequestRef = useRef<Promise<HistoricalRankingArtifacts> | null>(null);
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

  useEffect(() => {
    void ensureHistoricalRankingsLoaded();
  }, [ensureHistoricalRankingsLoaded]);

  useEffect(() => {
    let alive = true;

    async function loadSelectedArtifacts() {
      const cachedArtifacts = loadedArtifactsRef.current[hexSize];
      if (cachedArtifacts) {
        setArtifacts(cachedArtifacts);
        setIsLoadingArtifacts(false);
        setIsSwitchingHexSize(false);
        prefetchRemainingHexSizes(hexSize, loadedArtifactsRef.current, alive);
        return;
      }

      const isFirstLoad = Object.keys(loadedArtifactsRef.current).length === 0;
      if (isFirstLoad) {
        setIsLoadingArtifacts(true);
      } else {
        setIsSwitchingHexSize(true);
      }

      const nextArtifacts = initialArtifacts && hexSize === DEFAULT_HEX_SIZE
        ? initialArtifacts
        : await loadMapArtifactsFromPublic(hexSize);

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
      prefetchRemainingHexSizes(hexSize, loadedArtifactsRef.current, alive);
    }

    void loadSelectedArtifacts();

    return () => {
      alive = false;
    };
  }, [hexSize, initialArtifacts]);

  useEffect(() => {
    if (!selectedHex) {
      return;
    }

    if (artifacts.hexes.some((item) => item.h3_cell === selectedHex.h3_cell && item.category_code === selectedHex.category_code)) {
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

  const colorScale = useMemo(() => buildColorScale(filteredHexes, horizon), [filteredHexes, horizon]);

  const activeStats = useMemo(() => {
    if (filteredHexes.length === 0) {
      return {
        locales: 0,
        hexes: 0,
        hexesWithSupport: 0,
        meanSurvival: null,
        meanRelativeRisk: null
      };
    }

    const locales = filteredHexes.reduce((sum, item) => sum + item.n_locales, 0);
    const survivalTotals = filteredHexes.reduce(
      (accumulator, item) => {
        const support = getHorizonSupport(item, horizon);
        const survival = getHorizonSurvival(item, horizon);
        if (support > 0 && isFiniteNumber(survival)) {
          accumulator.supportedHexes += 1;
          accumulator.supportedLocales += support;
          accumulator.weightedSurvival += support * survival;
        }
        return accumulator;
      },
      { supportedHexes: 0, supportedLocales: 0, weightedSurvival: 0 }
    );
    const meanRelativeRisk = filteredHexes.reduce((sum, item) => sum + item.n_locales * item.avg_risk_percentile, 0) / locales;

    return {
      locales,
      hexes: filteredHexes.length,
      hexesWithSupport: survivalTotals.supportedHexes,
      meanSurvival: survivalTotals.supportedLocales > 0 ? survivalTotals.weightedSurvival / survivalTotals.supportedLocales : null,
      meanRelativeRisk
    };
  }, [filteredHexes, horizon]);

  const detail = selectedHex;
  const detailSurvival = detail ? getHorizonSurvival(detail, horizon) : null;
  const detailSupport = detail ? getHorizonSupport(detail, horizon) : 0;

  const detailCategoryComposition = useMemo(() => {
    if (!detail || selectedCategory !== "__all__") {
      return [];
    }

    return buildHexCategoryComposition(artifacts.hexes, detail);
  }, [artifacts.hexes, detail, selectedCategory]);

  const detailRank = useMemo(() => {
    if (!detail) {
      return null;
    }
    return buildHexRanking(filteredHexes, detail, horizon);
  }, [detail, filteredHexes, horizon]);

  const topZones = useMemo(() => {
    return {
      district: buildTopZones(filteredDistrictZones),
      barrio: buildTopZones(filteredBarrioZones)
    };
  }, [filteredBarrioZones, filteredDistrictZones]);

  const detailMetrics = useMemo(() => {
    if (!detail) {
      return [];
    }

    return buildHexMetrics({
      detail,
      detailRank,
      detailSupport,
      detailSurvival,
      horizon,
      meanRiskIndex: activeStats.meanRelativeRisk
    });
  }, [activeStats.meanRelativeRisk, detail, detailRank, detailSupport, detailSurvival, horizon]);

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
  const comparisonSeriesMeta = historicalRankingArtifacts
    ? `Serie anual ${historicalRankingArtifacts.meta.years[0]}-${historicalRankingArtifacts.meta.latest_year}`
    : "Serie histórica no disponible todavía.";

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

  return (
    <main className="app-shell">
      <aside className="sidebar panel">
        <div>
          <ViewTabs />
          <div className="eyebrow">Localizate / Madrid</div>
          <h1>Mapa de supervivencia comercial.</h1>
        </div>

        <p className="lede">Explora qué zonas sostienen mejor cada tipo de local en Madrid</p>

        <div className="control-group">
          <span className="control-label" id="category-label">
            Tipo de local
          </span>
          <CategoryPicker
            labelledBy="category-label"
            onChange={(nextCategory) => {
              setSelectedCategory(nextCategory);
              setSelectedHex(null);
              setActiveZoneInsight(null);
            }}
            options={artifacts.categories}
            value={selectedCategory}
          />
        </div>

        <div className="control-group">
          <span className="control-label">Tamaño hexágono</span>
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

        <div className="control-group">
          <span className="control-label">Horizonte</span>
          <div className="toggle-row">
            <button data-active={horizon === "12m"} onClick={() => {
              setActiveZoneInsight(null);
              setHorizon("12m");
            }} type="button">
              12 meses
            </button>
            <button data-active={horizon === "24m"} onClick={() => {
              setActiveZoneInsight(null);
              setHorizon("24m");
            }} type="button">
              24 meses
            </button>
          </div>
        </div>

        <div className="stat-grid">
          <div className="stat-card">
            <span className="label">Supervivencia media</span>
            <span className="value">{formatPercent(activeStats.meanSurvival, activeStats.hexes > 0 ? "Sin muestra" : "Sin datos")}</span>
          </div>
          <div className="stat-card">
            <span className="label">Índice relativo 0-1</span>
            <span className="value">{formatRelativeRiskIndex(activeStats.meanRelativeRisk)}</span>
          </div>
          <div className="stat-card">
            <span className="label">Locales visibles</span>
            <span className="value">{formatCompact(activeStats.locales)}</span>
          </div>
          <div className="stat-card">
            <span className="label">Hexágonos</span>
            <span className="value">{formatCompact(activeStats.hexes)}</span>
          </div>
        </div>
        <p className="support-note">
          {isLoadingArtifacts
            ? "Cargando el artefacto histórico del mapa. La vista aparece primero y los hexágonos se hidratan en segundo plano."
            : isSwitchingHexSize
              ? `Cambiando a nivel ${formatHexSizeLabel(hexSize).toLowerCase()}...`
            : buildGlobalSupportNote(activeStats.hexesWithSupport, activeStats.hexes, horizon)}
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
          <div className="info-meta">
            <span className="chip chip-light">{comparisonSeriesMeta}</span>
          </div>

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
          <div className="eyebrow">Hexágono seleccionado</div>
          {detail ? (
            <>
              <h2>{detail.category_desc}</h2>
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
              <h3>Selecciona un hexágono</h3>
              <p>Haz clic en el mapa para ver su posición en Madrid, su ranking por riesgo y la diferencia frente a la media de la categoría.</p>
            </div>
          )}
        </section>

        {selectedCategory === "__all__" ? (
          <section className="info-card info-card-hex-category-composition">
            <div className="eyebrow">Mezcla del hexágono</div>
            {detail ? (
              <HexCategoryComposition items={detailCategoryComposition} overlayBoundsRef={mapPanelRef} totalLocales={detail.n_locales} />
            ) : (
              <p className="empty-note">Selecciona un hexágono para ver cómo se reparten sus locales históricos entre las distintas categorías.</p>
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
            <MetricExplainer metric={activeMetric} />
          </div>
        ) : null}

        <MadridMap
          bounds={artifacts.meta.map_bounds}
          colorScale={colorScale}
          horizon={horizon}
          hexes={filteredHexes}
          onSelectHex={(hex) => {
            setActiveZoneInsight(null);
            setIsHistoricalEvolutionOpen(false);
            setIsZoneComparisonOpen(false);
            setSelectedHex(hex);
          }}
          selectedHex={selectedHex}
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
  const pickerRef = useRef<HTMLDivElement | null>(null);
  const selectedOption = options.find((option) => option.category_code === value) ?? options[0] ?? null;

  useEffect(() => {
    if (!isOpen || !pickerRef.current) {
      return;
    }
    const triggerRect = pickerRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const spaceBelow = viewportHeight - triggerRect.bottom;
    const spaceAbove = triggerRect.top;
    const nextOpenUpward = spaceBelow < 280 && spaceAbove > spaceBelow;
    setOpenUpward(nextOpenUpward);
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
          <strong className="category-picker-trigger-title">{selectedOption.category_desc}</strong>
          <span className="category-picker-trigger-subtitle">Elige la categoría que quieras analizar</span>
        </span>
        <span aria-hidden="true" className="category-picker-trigger-icon">
          {isOpen ? "˄" : "˅"}
        </span>
      </button>

      {isOpen ? (
        <div className={`category-picker-menu${openUpward ? " category-picker-menu-up" : ""}`} role="listbox">
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
  const pickerRef = useRef<HTMLDivElement | null>(null);
  const selectedOption = options.find((option) => option.value === value) ?? null;
  const triggerLabel = selectedOption?.label ?? placeholder;

  useEffect(() => {
    if (!isOpen || !pickerRef.current) {
      return;
    }
    const triggerRect = pickerRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const spaceBelow = viewportHeight - triggerRect.bottom;
    const spaceAbove = triggerRect.top;
    const nextOpenUpward = spaceBelow < 280 && spaceAbove > spaceBelow;
    setOpenUpward(nextOpenUpward);
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
          <strong className="category-picker-trigger-title">{triggerLabel}</strong>
        </span>
        <span aria-hidden="true" className="category-picker-trigger-icon">
          {isOpen ? "˄" : "˅"}
        </span>
      </button>

      {isOpen && !disabled ? (
        <div className={`category-picker-menu${openUpward ? " category-picker-menu-up" : ""}`} role="listbox">
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

function prefetchRemainingHexSizes(
  selectedHexSize: HexSize,
  cache: Partial<Record<HexSize, FrontendArtifacts>>,
  alive: boolean
) {
  for (const option of HEX_SIZE_OPTIONS) {
    if (option.value === selectedHexSize || cache[option.value]) {
      continue;
    }

    void loadMapArtifactsFromPublic(option.value).then((nextArtifacts) => {
      if (!alive || cache[option.value]) {
        return;
      }
      cache[option.value] = nextArtifacts;
    });
  }
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

function MetricExplainer({ metric }: { metric: MetricDefinition | null }) {
  return (
    <div className="metric-explainer" data-empty={metric ? "false" : "true"}>
      <div className="eyebrow">Qué significa este dato</div>
      {metric ? (
        <>
          <h3>{metric.label}</h3>
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
        <p className="metric-explainer-copy">Haz clic en cualquier tarjeta para ver qué significa, por qué es útil y cómo la calcula el producto.</p>
      )}
    </div>
  );
}

function RelativeRiskExplainerBanner({ onClose }: { onClose: () => void }) {
  return (
    <section aria-label="Cómo leer el índice relativo 0-1" aria-modal="false" className="explain-banner explain-banner-floating" role="dialog">
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
          No es una probabilidad de cierre. Solo resume qué zonas salen mejor o peor para la categoría que estás viendo en Madrid.
        </p>
        <p className="explain-banner-copy">
          Este ranking principal sigue usando el índice relativo 0-1 del modelo actual. La evolución histórica del banner superior adapta la métrica al caso: para categorías concretas ordena por especialización frente a Madrid, suavizada por tamaño de zona; para Todos los locales ordena por la ganancia o pérdida de peso de cada zona dentro del total comercial de Madrid desde el inicio de la serie.
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
      aria-label={`Ver ranking de actividades en ${zone.zone_name}`}
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
          Ordenamos las macrocategorías de este {scopeLabel} por menor índice relativo. Cuanto más bajo sale el valor, más defensiva es la lectura histórica dentro de ese ámbito.
        </p>
        <div className="metric-breakdown-list">
          {insight.items.map((item) => (
            <div className="metric-breakdown-item" key={`${insight.zoneLevel}:${insight.zoneCode}:${item.categoryCode}`}>
              <div className="metric-breakdown-main">
                <span className="metric-breakdown-rank">#{item.rank}</span>
                <span className="metric-breakdown-name">{item.categoryDesc}</span>
              </div>
              <strong className="metric-breakdown-value">{formatRelativeRiskIndex(item.riskIndex)}</strong>
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

function buildFallbackCategoryDefinition(categoryDesc: string) {
  return `Lectura agregada de la macrocategoría ${categoryDesc.toLowerCase()} sobre los locales históricos visibles en el mapa.`;
}

function buildTopZones(zones: ZoneAggregate[]) {
  const source = zones.some((item) => item.supported_for_stats) ? zones.filter((item) => item.supported_for_stats) : zones;
  return sortZonesByRisk(source).slice(0, 3);
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
  const matchingZones = zonePool.filter((item) => item.zone_code === zone.zone_code);
  if (matchingZones.length === 0) {
    return null;
  }

  const scopedZones = matchingZones.some((item) => item.supported_for_stats)
    ? matchingZones.filter((item) => item.supported_for_stats)
    : matchingZones;

  const sorted = sortZonesByRisk(scopedZones).map((item, index) => ({
    rank: index + 1,
    categoryCode: item.category_code,
    categoryDesc: item.category_desc,
    riskIndex: item.avg_risk_percentile,
    survival: horizon === "24m" ? item.survival_24m : item.survival_12m,
    support: horizon === "24m" ? item.support_24m : item.support_12m,
    nLocales: item.n_locales,
  }));

  const currentCategoryRank = sorted.find((item) => item.categoryCode === currentCategoryCode)?.rank ?? null;

  return {
    zoneLevel: zone.zone_level,
    zoneCode: zone.zone_code,
    zoneName: zone.zone_name,
    horizon,
    totalActivities: sorted.length,
    currentCategoryDesc: zone.category_desc,
    currentCategoryRank,
    items: sorted.slice(0, 5),
  };
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
  return `Surv ${horizonLabel} ${survivalLabel} · ${formatCompact(item.nLocales)} locales`;
}

function sortZonesByRisk(zones: ZoneAggregate[]) {
  return [...zones].sort((left, right) => {
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
    return left.zone_name.localeCompare(right.zone_name, "es");
  });
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

function buildMetricWhyUseful(metric: MetricDefinition) {
  if (metric.id.endsWith(":locales")) {
    return "Te da una lectura de tamaño inmediato: ayuda a diferenciar si estás viendo un hexágono muy representativo o uno con base pequeña.";
  }
  if (metric.id.endsWith(":city-rank")) {
    return "Te ayuda a priorizar rápido: con una sola cifra ves si este hexágono está entre los mejores o peores de la categoría activa dentro de Madrid.";
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Es la lectura más fácil de comparar entre zonas: 0,10 se entiende enseguida como mejor posición relativa que 0,70 sin tener que entrar en el score técnico del modelo.";
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

function buildMetricExample(metric: MetricDefinition) {
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

function buildHexCategoryComposition(hexes: HexAggregate[], detail: HexAggregate): HexCategoryCompositionItem[] {
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

  return orderedItems.map((item, position) => ({
    categoryCode: item.category_code,
    categoryDesc: item.category_desc,
    nLocales: item.n_locales,
    share: item.n_locales / totalLocales,
    color: colorForCategoryPosition(position, item.category_code),
  }));
}

// Alternate hue families so adjacent donut slices stay visually distinct without leaving the pastel theme.
const HEX_COMPOSITION_COLOR_HUES = [42, 222, 318, 138, 278, 82, 248, 18, 168, 344, 198];
const HEX_COMPOSITION_COLOR_TONES = [
  { saturation: 52, lightness: 72 },
  { saturation: 44, lightness: 79 },
  { saturation: 56, lightness: 67 },
];

function colorForCategoryPosition(position: number, categoryCode: string) {
  const seed = hashString(categoryCode);
  const baseHue = HEX_COMPOSITION_COLOR_HUES[position % HEX_COMPOSITION_COLOR_HUES.length];
  const tone = HEX_COMPOSITION_COLOR_TONES[
    Math.floor(position / HEX_COMPOSITION_COLOR_HUES.length) % HEX_COMPOSITION_COLOR_TONES.length
  ];
  const hueShift = ((seed % 3) - 1) * 4;
  const saturation = clamp(tone.saturation + (((seed >>> 3) % 3) - 1) * 2, 38, 60);
  const lightness = clamp(tone.lightness + (((seed >>> 5) % 3) - 1), 64, 82);

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

function buildColorScale(hexes: HexAggregate[], horizon: Horizon): ColorScale {
  const values = hexes
    .map((item) => getHorizonSurvival(item, horizon))
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

function buildGlobalSupportNote(hexesWithSupport: number, totalHexes: number, horizon: Horizon) {
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

