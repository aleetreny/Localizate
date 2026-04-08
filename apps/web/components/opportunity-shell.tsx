"use client";

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";

import { OpportunityMap } from "@/components/opportunity-map";
import { ViewTabs } from "@/components/view-tabs";
import { formatHorizonShortLabel, isFiniteNumber, type Horizon } from "@/lib/horizon";
import { buildOpportunityBenchmarkContext, type OpportunityBenchmarkContext } from "@/lib/opportunity-insights";
import { FALLBACK_OPPORTUNITY_ARTIFACTS, loadOpportunityArtifactsFromPublic } from "@/lib/public-data";
import type {
  FacilityCategory,
  IndicadorDistrito,
  InspeccionEpigrafe,
  OpportunityActivity,
  OpportunityArtifacts,
  OpportunityAvisoCategory,
  OpportunityManualSelection,
  OpportunityPoint,
  OpportunitySection,
  OpportunitySectionFeatureCollection,
  VulnerabilidadEsfera,
} from "@/lib/types";

type OpportunityShellProps = {
  initialArtifacts?: OpportunityArtifacts;
};

type OperationFilter = "all" | "venta" | "alquiler";

type MetricDefinition = {
  id: string;
  label: string;
  value: string;
  summary: string;
  calculation: string;
  breakdownTitle?: string;
  breakdownItems?: MetricBreakdownItem[];
  breakdownEmptyText?: string;
};

type MetricBreakdownItem = {
  rank: number;
  label: string;
  value: string;
  detail: string;
  asideTitle?: string;
  asideItems?: string[];
  asideEmptyText?: string;
};

type DetailHeaderMetrics = {
  operation: MetricDefinition | null;
  price: MetricDefinition | null;
  area: MetricDefinition | null;
  opportunityTier: MetricDefinition | null;
  riskPercentile: MetricDefinition | null;
};

type OpportunityFieldInsight = OpportunityBenchmarkContext["metrics"][keyof OpportunityBenchmarkContext["metrics"]];

const IS_PRODUCTION = process.env.NODE_ENV === "production";
const DEV_ARTIFACT_REVALIDATE_MS = 15000;
const SECTION_FETCH_CACHE_MODE = process.env.NODE_ENV === "production" ? "force-cache" : "no-store";
const EMPTY_SECTION_COLLECTION: OpportunitySectionFeatureCollection = {
  type: "FeatureCollection",
  features: [],
};

export function OpportunityShell({ initialArtifacts }: OpportunityShellProps) {
  const [artifacts, setArtifacts] = useState(initialArtifacts ?? FALLBACK_OPPORTUNITY_ARTIFACTS);
  const [isLoadingArtifacts, setIsLoadingArtifacts] = useState(!initialArtifacts);
  const [operationFilter, setOperationFilter] = useState<OperationFilter>("all");
  const [horizon, setHorizon] = useState<Horizon>("24m");
  const [selectedListingId, setSelectedListingId] = useState<string | null>((initialArtifacts ?? FALLBACK_OPPORTUNITY_ARTIFACTS).points[0]?.listing_id ?? null);
  const [manualSelection, setManualSelection] = useState<OpportunityManualSelection | null>(null);
  const [activeMetricId, setActiveMetricId] = useState<string | null>(null);
  const [sectionUniverse, setSectionUniverse] = useState<OpportunitySectionFeatureCollection>(EMPTY_SECTION_COLLECTION);
  const artifactsSignature = getOpportunityArtifactSignature(artifacts);

  useEffect(() => {
    let alive = true;

    async function syncArtifacts(resetManualSelection: boolean) {
      const nextArtifacts = await loadOpportunityArtifactsFromPublic();
      if (!alive) {
        return;
      }

      if (getOpportunityArtifactSignature(nextArtifacts) === artifactsSignature) {
        setIsLoadingArtifacts(false);
        return;
      }

      setArtifacts(nextArtifacts);
      setIsLoadingArtifacts(false);
      setSelectedListingId((currentListingId) => {
        if (currentListingId && nextArtifacts.points.some((point) => point.listing_id === currentListingId)) {
          return currentListingId;
        }
        return nextArtifacts.points[0]?.listing_id ?? null;
      });
      if (resetManualSelection) {
        setManualSelection(null);
      }
    }

    if (initialArtifacts) {
      return () => {
        alive = false;
      };
    }

    void syncArtifacts(false);

    function handleFocus() {
      void syncArtifacts(true);
    }

    function handleVisibilityChange() {
      if (document.visibilityState === "visible") {
        void syncArtifacts(true);
      }
    }

    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    const intervalId = IS_PRODUCTION
      ? null
      : window.setInterval(() => {
          if (document.visibilityState === "visible") {
            void syncArtifacts(true);
          }
        }, DEV_ARTIFACT_REVALIDATE_MS);

    return () => {
      alive = false;
      window.removeEventListener("focus", handleFocus);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      if (intervalId !== null) {
        window.clearInterval(intervalId);
      }
    };
  }, [artifactsSignature, initialArtifacts]);

  useEffect(() => {
    let alive = true;

    async function loadSectionUniverse() {
      try {
        const response = await fetch(artifacts.meta.section_geojson_path, { cache: SECTION_FETCH_CACHE_MODE });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const payload = (await response.json()) as OpportunitySectionFeatureCollection;
        if (alive) {
          setSectionUniverse(payload);
        }
      } catch {
        if (alive) {
          setSectionUniverse(EMPTY_SECTION_COLLECTION);
        }
      }
    }

    setSectionUniverse(EMPTY_SECTION_COLLECTION);
    void loadSectionUniverse();

    return () => {
      alive = false;
    };
  }, [artifacts.meta.section_geojson_path]);

  const filteredPoints = useMemo(() => {
    if (operationFilter === "all") {
      return artifacts.points;
    }
    return artifacts.points.filter((point) => point.operation === operationFilter);
  }, [artifacts.points, operationFilter]);

  useEffect(() => {
    if (manualSelection) {
      return;
    }
    if (selectedListingId && filteredPoints.some((point) => point.listing_id === selectedListingId)) {
      return;
    }
    setSelectedListingId(filteredPoints[0]?.listing_id ?? null);
  }, [filteredPoints, manualSelection, selectedListingId]);

  const selectedListing = useMemo(() => {
    if (manualSelection) {
      return null;
    }
    return filteredPoints.find((point) => point.listing_id === selectedListingId) ?? filteredPoints[0] ?? null;
  }, [filteredPoints, manualSelection, selectedListingId]);

  const selectedSectionKey = manualSelection?.section.section_key ?? selectedListing?.section_key ?? null;

  const allSections = useMemo(() => {
    return sectionUniverse.features.map((feature) => feature.properties);
  }, [sectionUniverse]);

  const opportunityBenchmarks = useMemo(() => {
    return buildOpportunityBenchmarkContext(allSections, manualSelection?.section ?? selectedListing ?? null);
  }, [allSections, manualSelection?.section, selectedListing]);

  const detailMetrics = useMemo(() => {
    if (manualSelection) {
      const section = manualSelection.section;
      return [
        ...buildSectionPrimaryMetrics(section, horizon, opportunityBenchmarks),
        ...buildContextMetrics({
          scopeId: `section:${section.section_key}`,
          uniqueActivityCategories: section.section_unique_activity_category_count_start,
          turnoverRate12m: section.section_turnover_rate_12m_start,
          shareForeign: section.share_foreign_start,
          shareYoung: section.share_age_15_29_start,
          shareSenior: section.share_age_65_plus_start,
          avisosBarrio: section.avisos_barrio_per_1000_prev_year,
          avisosDistrict: section.avisos_district_per_1000_prev_year,
          topAvisosBarrioCategories: section.top_avisos_barrio_categories,
          topAvisosDistrictCategories: section.top_avisos_district_categories,
          benchmarks: opportunityBenchmarks,
          districtName: section.district_name,
          barrioName: section.barrio_name,
          facilitiesTier: section.facilities_tier,
          facilities200m: section.facilities_200m,
          facilities500m: section.facilities_500m,
          facilities1000m: section.facilities_1000m,
          facilitiesByCategory: section.facilities_by_category,
          vulnerabilidadGlobal: section.vulnerabilidad_global,
          vulnerabilidadGlobalMediaCiudad: section.vulnerabilidad_global_media_ciudad,
          vulnerabilidadEsferas: section.vulnerabilidad_esferas,
          inspeccionesDistritoTotal: section.inspecciones_distrito_total,
          inspeccionesCiudadMedia: section.inspecciones_ciudad_media,
          inspeccionesTopEpigrafes: section.inspecciones_top_epigrafes,
          indicadoresDistrito: section.indicadores_distrito,
        })
      ];
    }

    if (!selectedListing) {
      return [];
    }

    return [
      ...buildPointPrimaryMetrics(selectedListing, horizon, opportunityBenchmarks),
      ...buildContextMetrics({
        scopeId: `listing:${selectedListing.listing_id}`,
        uniqueActivityCategories: selectedListing.section_unique_activity_category_count_start,
        turnoverRate12m: selectedListing.section_turnover_rate_12m_start,
        shareForeign: selectedListing.share_foreign_start,
        shareYoung: selectedListing.share_age_15_29_start,
        shareSenior: selectedListing.share_age_65_plus_start,
        avisosBarrio: selectedListing.avisos_barrio_per_1000_prev_year,
        avisosDistrict: selectedListing.avisos_district_per_1000_prev_year,
        topAvisosBarrioCategories: selectedListing.top_avisos_barrio_categories,
        topAvisosDistrictCategories: selectedListing.top_avisos_district_categories,
        benchmarks: opportunityBenchmarks,
        districtName: selectedListing.district_name,
        barrioName: selectedListing.barrio_name,
        facilitiesTier: selectedListing.facilities_tier,
        facilities200m: selectedListing.facilities_200m,
        facilities500m: selectedListing.facilities_500m,
        facilities1000m: selectedListing.facilities_1000m,
        facilitiesByCategory: selectedListing.facilities_by_category,
        vulnerabilidadGlobal: selectedListing.vulnerabilidad_global,
        vulnerabilidadGlobalMediaCiudad: selectedListing.vulnerabilidad_global_media_ciudad,
        vulnerabilidadEsferas: selectedListing.vulnerabilidad_esferas,
        inspeccionesDistritoTotal: selectedListing.inspecciones_distrito_total,
        inspeccionesCiudadMedia: selectedListing.inspecciones_ciudad_media,
        inspeccionesTopEpigrafes: selectedListing.inspecciones_top_epigrafes,
        indicadoresDistrito: selectedListing.indicadores_distrito,
      })
    ];
  }, [horizon, manualSelection, opportunityBenchmarks, selectedListing]);

  const headerMetrics = useMemo<DetailHeaderMetrics>(() => {
    if (manualSelection) {
      const section = manualSelection.section;
      const scopeId = `section:${section.section_key}`;
      return {
        operation: null,
        price: null,
        area: null,
        opportunityTier: buildOpportunityTierMetric(scopeId, section.opportunity_tier),
        riskPercentile: buildRiskPercentileMetric(scopeId, section.risk_percentile),
      };
    }

    if (!selectedListing) {
      return {
        operation: null,
        price: null,
        area: null,
        opportunityTier: null,
        riskPercentile: null,
      };
    }

    const scopeId = `listing:${selectedListing.listing_id}`;
    return {
      operation: buildListingOperationMetric(scopeId, selectedListing, artifacts.points),
      price: buildListingPriceMetric(scopeId, selectedListing, artifacts.points),
      area: buildListingAreaMetric(scopeId, selectedListing, artifacts.points),
      opportunityTier: buildOpportunityTierMetric(scopeId, selectedListing.opportunity_tier),
      riskPercentile: buildRiskPercentileMetric(scopeId, selectedListing.risk_percentile),
    };
  }, [artifacts.points, manualSelection, selectedListing]);

  const activeActivities = manualSelection?.section.top_activities ?? selectedListing?.top_activities ?? [];

  const activityRankingMetric = useMemo(() => {
    const scopeId = manualSelection
      ? `section:${manualSelection.section.section_key}`
      : selectedListing
        ? `listing:${selectedListing.listing_id}`
        : null;

    if (!scopeId) {
      return null;
    }

    return buildActivityRankingMethodMetric({
      scopeId,
      activities: activeActivities,
    });
  }, [activeActivities, manualSelection, selectedListing]);

  const explainableMetrics = useMemo(() => {
    return [
      headerMetrics.operation,
      headerMetrics.price,
      headerMetrics.area,
      headerMetrics.opportunityTier,
      headerMetrics.riskPercentile,
      activityRankingMetric,
      ...detailMetrics,
    ].filter((metric): metric is MetricDefinition => metric !== null);
  }, [
    activityRankingMetric,
    detailMetrics,
    headerMetrics.area,
    headerMetrics.operation,
    headerMetrics.opportunityTier,
    headerMetrics.price,
    headerMetrics.riskPercentile,
  ]);

  const activeMetric = explainableMetrics.find((metric) => metric.id === activeMetricId) ?? null;

  useEffect(() => {
    if (!activeMetricId) {
      return;
    }

    if (explainableMetrics.some((metric) => metric.id === activeMetricId)) {
      return;
    }

    setActiveMetricId(null);
  }, [activeMetricId, explainableMetrics]);

  const activeStats = useMemo(() => {
    const survivalValues = filteredPoints.map((point) => getPointSurvival(point, horizon)).filter(isFiniteNumber);
    const priceValues = filteredPoints.map((point) => point.price_per_m2_eur).filter(isFiniteNumber);
    return {
      selected: filteredPoints.length,
      districts: new Set(filteredPoints.map((point) => point.district_code).filter(Boolean)).size,
      barrios: new Set(filteredPoints.map((point) => buildBarrioScopeKey(point)).filter(Boolean)).size,
      medianSurvival: median(survivalValues),
      medianPricePerSquareMeter: median(priceValues)
    };
  }, [filteredPoints, horizon]);

  return (
    <main className="app-shell">
      <aside className="sidebar panel">
        <div>
          <ViewTabs />
          <div className="eyebrow">Localizate / Madrid</div>
          <h1>Mapa de oportunidades.</h1>
        </div>

        <p className="lede">{artifacts.meta.subtitle}</p>

        <div className="control-group">
          <label className="control-label" htmlFor="operation-filter">
            Operación
          </label>
          <select
            className="select"
            id="operation-filter"
            value={operationFilter}
            onChange={(event) => {
              setManualSelection(null);
              setOperationFilter(event.target.value as OperationFilter);
            }}
          >
            <option value="all">Todos los locales filtrados</option>
            <option value="venta">Solo venta</option>
            <option value="alquiler">Solo alquiler</option>
          </select>
        </div>

        <div className="control-group">
          <span className="control-label">Horizonte</span>
          <div className="toggle-row">
            <button data-active={horizon === "12m"} onClick={() => setHorizon("12m")} type="button">
              12 meses
            </button>
            <button data-active={horizon === "24m"} onClick={() => setHorizon("24m")} type="button">
              24 meses
            </button>
          </div>
        </div>

        <div className="stat-grid">
          <div className="stat-card">
            <span className="label">Locales visibles</span>
            <span className="value">{formatCompact(activeStats.selected)}</span>
          </div>
          <div className="stat-card">
            <span className="label">Supervivencia mediana</span>
            <span className="value">{formatPercent(activeStats.medianSurvival)}</span>
          </div>
          <div className="stat-card">
            <span className="label">Barrios cubiertos</span>
            <span className="value">{formatCompact(activeStats.barrios)}</span>
          </div>
          <div className="stat-card">
            <span className="label">Precio mediano m²</span>
            <span className="value">{formatPricePerSquareMeter(activeStats.medianPricePerSquareMeter)}</span>
          </div>
        </div>

        <p className="support-note">
          {isLoadingArtifacts
            ? "Cargando el dataset de oportunidades y su contexto espacial. La interfaz aparece primero y los puntos se completan en segundo plano."
            : "Haz clic en un local para abrir su ficha. Si haces clic en cualquier otro punto del mapa, la lectura se hace con la zona pequeña del censo donde cae ese punto para comparar riesgo, competencia, ingresos, metro y avisos con la misma referencia."}
        </p>

        <section className="detail-card">
          {manualSelection ? (
            <ManualPointDetail
              activeMetricId={activeMetricId}
              headerMetrics={headerMetrics}
              metrics={detailMetrics}
              onMetricSelect={setActiveMetricId}
              section={manualSelection.section}
              selection={manualSelection}
            />
          ) : selectedListing ? (
            <ListingDetail
              activeMetricId={activeMetricId}
              headerMetrics={headerMetrics}
              metrics={detailMetrics}
              onMetricSelect={setActiveMetricId}
              point={selectedListing}
            />
          ) : (
            <div className="detail-empty">
              <div className="eyebrow">Ficha activa</div>
              <h3>{isLoadingArtifacts ? "Cargando oportunidades" : "Sin selección"}</h3>
              <p>
                {isLoadingArtifacts
                  ? "La vista está esperando el artefacto de oportunidades y la geometría de secciones para habilitar el detalle."
                  : "No hay locales visibles con el filtro actual. Cambia la operación o haz clic en el mapa para explorar una sección."}
              </p>
            </div>
          )}
        </section>

        <section className="info-card">
          <div className="eyebrow">Actividades recomendadas</div>
          <h3>{manualSelection ? "Actividades con mejor pronóstico en esta sección" : selectedListing ? "Actividades con mejor pronóstico en este entorno" : "Selecciona un punto"}</h3>
          <p className="empty-note">Las ordenamos de menor a mayor riesgo estimado para esta zona. En cada tarjeta verás una referencia rápida de cuánto suele aguantar esa actividad a 2 años y cuánta muestra parecida tenemos cerca.</p>
          {activeActivities.length > 0 ? (
            <ActivityList
              activities={activeActivities}
              explainActive={activeMetricId === activityRankingMetric?.id}
              onExplain={() => {
                if (!activityRankingMetric) {
                  return;
                }
                setActiveMetricId((current) => current === activityRankingMetric.id ? null : activityRankingMetric.id);
              }}
            />
          ) : <p className="empty-note">Sin ranking predictivo disponible para este entorno.</p>}
        </section>
      </aside>

      <section className="map-panel panel">
        {activeMetric ? (
          <div className="map-overlay panel metric-banner">
            <MetricExplainer metric={activeMetric} />
          </div>
        ) : null}

        <OpportunityMap
          bounds={artifacts.meta.map_bounds}
          horizon={horizon}
          manualSelection={manualSelection}
          onSelectListing={(point) => {
            setManualSelection(null);
            setSelectedListingId(point.listing_id);
          }}
          onSelectManual={(selection) => {
            setSelectedListingId(null);
            setManualSelection(selection);
          }}
          points={filteredPoints}
          sectionsGeojsonPath={artifacts.meta.section_geojson_path}
          selectedListingId={manualSelection ? null : selectedListing?.listing_id ?? null}
          selectedSectionKey={selectedSectionKey}
        />
      </section>
    </main>
  );
}

function ListingDetail({
  point,
  headerMetrics,
  metrics,
  activeMetricId,
  onMetricSelect
}: {
  point: OpportunityPoint;
  headerMetrics: DetailHeaderMetrics;
  metrics: MetricDefinition[];
  activeMetricId: string | null;
  onMetricSelect: (metricId: string | null) => void;
}) {
  return (
    <>
      <div className="eyebrow">Local filtrado</div>
      <h2>{point.card_title}</h2>
      <p className="detail-location">{point.barrio_name}, {point.district_name}</p>
      <div className="detail-meta">
        <HeaderMetricChip activeMetricId={activeMetricId} metric={headerMetrics.operation} onMetricSelect={onMetricSelect} />
        <HeaderMetricChip activeMetricId={activeMetricId} metric={headerMetrics.price} onMetricSelect={onMetricSelect} />
        <HeaderMetricChip activeMetricId={activeMetricId} metric={headerMetrics.area} onMetricSelect={onMetricSelect} />
        <HeaderMetricChip activeMetricId={activeMetricId} metric={headerMetrics.opportunityTier} onMetricSelect={onMetricSelect} />
        <HeaderMetricChip activeMetricId={activeMetricId} metric={headerMetrics.riskPercentile} onMetricSelect={onMetricSelect} />
      </div>
      <MetricGrid activeMetricId={activeMetricId} metrics={metrics} onSelect={onMetricSelect} />
      <a className="inline-link" href={point.listing_url} rel="noreferrer" target="_blank">
        Ver anuncio original
      </a>
    </>
  );
}

function ManualPointDetail({
  activeMetricId,
  headerMetrics,
  metrics,
  onMetricSelect,
  section,
  selection,
}: {
  activeMetricId: string | null;
  headerMetrics: DetailHeaderMetrics;
  metrics: MetricDefinition[];
  onMetricSelect: (metricId: string | null) => void;
  section: OpportunitySection;
  selection: OpportunityManualSelection;
}) {
  return (
    <>
      <div className="eyebrow">Punto libre</div>
      <h2>{section.barrio_name}, {section.district_name}</h2>
      <p className="detail-location">Lat {selection.lat.toFixed(5)} · Lon {selection.lng.toFixed(5)} · zona {section.section_key}</p>
      <p className="detail-subtle">El punto que marcas se interpreta con la zona pequeña del censo donde cae, no como una dirección inventada.</p>
      <div className="detail-meta">
        <HeaderMetricChip activeMetricId={activeMetricId} metric={headerMetrics.opportunityTier} onMetricSelect={onMetricSelect} />
        <HeaderMetricChip activeMetricId={activeMetricId} metric={headerMetrics.riskPercentile} onMetricSelect={onMetricSelect} />
      </div>
      <MetricGrid activeMetricId={activeMetricId} metrics={metrics} onSelect={onMetricSelect} />
    </>
  );
}

function HeaderMetricChip({
  activeMetricId,
  metric,
  onMetricSelect,
}: {
  activeMetricId: string | null;
  metric: MetricDefinition | null;
  onMetricSelect: (metricId: string | null) => void;
}) {
  if (!metric) {
    return null;
  }

  const isActive = activeMetricId === metric.id;

  return (
    <button
      aria-label={`Abrir explicación de ${metric.label}`}
      aria-pressed={isActive}
      className="chip chip-button"
      data-active={isActive}
      onClick={() => onMetricSelect(isActive ? null : metric.id)}
      type="button"
    >
      {metric.value}
    </button>
  );
}

function ActivityList({
  activities,
  explainActive,
  onExplain,
}: {
  activities: OpportunityActivity[];
  explainActive: boolean;
  onExplain: () => void;
}) {
  return (
    <div className="activity-list">
      {activities.map((activity) => (
        <article className="activity-card" key={`${activity.source_zone}:${activity.display_label}`}>
          <div className="activity-card-top">
            <span className="activity-rank">#{activity.rank}</span>
            <div className="activity-kpi">
              <span className="activity-kpi-label">Riesgo contextual</span>
              <span className="activity-value">{formatSignalPercent(activity.activity_risk)}</span>
            </div>
          </div>
          <strong>{activity.display_label}</strong>
          <ul className="activity-meta-list">
            <li className="activity-meta-item">Locales parecidos cerca: {formatActivitySampleValue(activity.n_locales, activity.source_zone)}</li>
            <li className="activity-meta-item">Supervivencia (2 años): {formatActivityStabilityValue(activity.survival_24m)}</li>
          </ul>
        </article>
      ))}
      <div className="activity-list-footer">
        <button
          aria-pressed={explainActive}
          className="zone-board-action activity-list-action"
          data-active={explainActive}
          onClick={onExplain}
          type="button"
        >
          {explainActive ? "Ocultar guía" : "Cómo interpretar este ranking"}
        </button>
      </div>
    </div>
  );
}

type MetricGroupKey = "potential" | "residential" | "access" | "signals";

const METRIC_GROUP_LABELS: Record<MetricGroupKey, string> = {
  potential: "Potencial y encaje",
  residential: "Demografía y renta",
  access: "Accesibilidad y dotación",
  signals: "Señales urbanas",
};

const METRIC_GROUP_ORDER: MetricGroupKey[] = ["potential", "residential", "access", "signals"];

function resolveMetricGroup(metricId: string): MetricGroupKey {
  if (
    metricId.includes(":survival:")
    || metricId.endsWith(":ranking")
    || metricId.endsWith(":activity-ranking-method")
    || metricId.endsWith(":competition")
    || metricId.endsWith(":active-categories")
  ) {
    return "potential";
  }
  if (
    metricId.endsWith(":income")
    || metricId.endsWith(":residential-base")
    || metricId.endsWith(":age")
    || metricId.endsWith(":foreign-share")
    || metricId.endsWith(":young-share")
    || metricId.endsWith(":senior-share")
    || metricId.endsWith(":district-unemployment")
    || metricId.endsWith(":district-dependency")
  ) {
    return "residential";
  }
  if (
    metricId.endsWith(":metro")
    || metricId.endsWith(":facilities")
  ) {
    return "access";
  }
  if (
    metricId.endsWith(":turnover-12m")
    || metricId.endsWith(":avisos")
    || metricId.endsWith(":inspecciones")
    || metricId.endsWith(":vulnerabilidad")
  ) {
    return "signals";
  }
  return "signals";
}

function buildMetricGroups(metrics: MetricDefinition[]) {
  const grouped = new Map<MetricGroupKey, MetricDefinition[]>();
  for (const metric of metrics) {
    const key = resolveMetricGroup(metric.id);
    const current = grouped.get(key) ?? [];
    current.push(metric);
    grouped.set(key, current);
  }

  return METRIC_GROUP_ORDER
    .map((key) => ({ key, title: METRIC_GROUP_LABELS[key], metrics: grouped.get(key) ?? [] }))
    .filter((group) => group.metrics.length > 0);
}

function hasBreakdownAside(item: MetricBreakdownItem) {
  return Boolean(item.asideTitle || (item.asideItems && item.asideItems.length > 0) || item.asideEmptyText);
}

function buildBreakdownItemKey(item: MetricBreakdownItem) {
  return `${item.rank}:${item.label}`;
}

function MetricGrid({
  metrics,
  activeMetricId,
  onSelect,
  className = "detail-grid"
}: {
  metrics: MetricDefinition[];
  activeMetricId: string | null;
  onSelect: (metricId: string | null) => void;
  className?: string;
}) {
  const groups = buildMetricGroups(metrics);

  return (
    <div className="detail-groups">
      {groups.map((group) => (
        <section className="detail-group" key={group.key}>
          <div className="detail-group-title">{group.title}</div>
          <div className={className}>
            {group.metrics.map((metric) => {
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
                  <span className="detail-metric-hint">Entender dato</span>
                </button>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}

function MetricExplainer({ metric }: { metric: MetricDefinition | null }) {
  const breakdownItems = metric?.breakdownItems ?? [];
  const asideEnabled = breakdownItems.some(hasBreakdownAside);
  const shellRef = useRef<HTMLDivElement | null>(null);
  const hoverPanelRef = useRef<HTMLElement | null>(null);
  const activeBreakdownTriggerRef = useRef<HTMLElement | null>(null);
  const [activeBreakdownKey, setActiveBreakdownKey] = useState<string | null>(null);
  const [hoverPanelTop, setHoverPanelTop] = useState(0);

  useEffect(() => {
    activeBreakdownTriggerRef.current = null;
    setActiveBreakdownKey(null);
    setHoverPanelTop(0);
  }, [metric?.id]);

  function activateBreakdown(itemKey: string, element?: HTMLElement | null) {
    setActiveBreakdownKey(itemKey);
    if (element) {
      activeBreakdownTriggerRef.current = element;
    }

    if (!activeBreakdownTriggerRef.current || !shellRef.current) {
      return;
    }

    const shellRect = shellRef.current.getBoundingClientRect();
    const elementRect = activeBreakdownTriggerRef.current.getBoundingClientRect();
    const panelHeight = hoverPanelRef.current?.getBoundingClientRect().height ?? 0;
    setHoverPanelTop(computeBreakdownHoverPanelTop({ shellRect, elementRect, panelHeight }));
  }

  const activeBreakdown = asideEnabled
    ? breakdownItems.find((item) => buildBreakdownItemKey(item) === activeBreakdownKey && hasBreakdownAside(item))
      ?? null
    : null;

  useLayoutEffect(() => {
    if (!activeBreakdown || !activeBreakdownTriggerRef.current || !shellRef.current) {
      return;
    }

    function syncHoverPanelTop() {
      if (!activeBreakdownTriggerRef.current || !shellRef.current) {
        return;
      }

      const shellRect = shellRef.current.getBoundingClientRect();
      const elementRect = activeBreakdownTriggerRef.current.getBoundingClientRect();
      const panelHeight = hoverPanelRef.current?.getBoundingClientRect().height ?? 0;
      setHoverPanelTop(computeBreakdownHoverPanelTop({ shellRect, elementRect, panelHeight }));
    }

    syncHoverPanelTop();

    const visualViewport = window.visualViewport;
    window.addEventListener("resize", syncHoverPanelTop);
    visualViewport?.addEventListener("resize", syncHoverPanelTop);

    return () => {
      window.removeEventListener("resize", syncHoverPanelTop);
      visualViewport?.removeEventListener("resize", syncHoverPanelTop);
    };
  }, [activeBreakdown, metric?.id]);

  return (
    <div className="metric-explainer-shell" ref={shellRef}>
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
            {metric.breakdownTitle ? (
              <div className="metric-explainer-block">
                <span className="metric-explainer-label">{metric.breakdownTitle}</span>
                {metric.breakdownItems && metric.breakdownItems.length > 0 ? (
                  <div className="metric-breakdown-list">
                    {metric.breakdownItems.map((item) => {
                      const itemKey = buildBreakdownItemKey(item);
                      const isAsideActive = activeBreakdownKey === itemKey;

                      if (asideEnabled) {
                        return (
                          <button
                            className="metric-breakdown-item metric-breakdown-item-button"
                            data-active={isAsideActive}
                            key={`${metric.id}:${item.rank}:${item.label}`}
                            onClick={(event) => activateBreakdown(itemKey, event.currentTarget)}
                            onFocus={(event) => activateBreakdown(itemKey, event.currentTarget)}
                            onMouseEnter={(event) => activateBreakdown(itemKey, event.currentTarget)}
                            type="button"
                          >
                            <div className="metric-breakdown-main">
                              <span className="metric-breakdown-rank">#{item.rank}</span>
                              <span className="metric-breakdown-name">{item.label}</span>
                            </div>
                            <strong className="metric-breakdown-value">{item.value}</strong>
                            <span className="metric-breakdown-detail">{item.detail}</span>
                          </button>
                        );
                      }

                      return (
                        <div className="metric-breakdown-item" key={`${metric.id}:${item.rank}:${item.label}`}>
                          <div className="metric-breakdown-main">
                            <span className="metric-breakdown-rank">#{item.rank}</span>
                            <span className="metric-breakdown-name">{item.label}</span>
                          </div>
                          <strong className="metric-breakdown-value">{item.value}</strong>
                          <span className="metric-breakdown-detail">{item.detail}</span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="metric-explainer-copy">{metric.breakdownEmptyText ?? "Sin desglose disponible para este ámbito."}</p>
                )}
              </div>
            ) : null}
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
      {asideEnabled && activeBreakdown ? (
        <aside className="metric-breakdown-hover-panel" ref={hoverPanelRef} style={{ top: `${hoverPanelTop}px` }}>
          <span className="metric-breakdown-hover-kicker">Metro de Madrid</span>
          <span className="metric-breakdown-hover-title">{activeBreakdown.asideTitle ?? activeBreakdown.label}</span>
          {activeBreakdown.asideItems && activeBreakdown.asideItems.length > 0 ? (
            <div className="metric-breakdown-aside-list">
              {activeBreakdown.asideItems.map((item) => (
                <span className="metric-breakdown-aside-item" key={`${activeBreakdown.label}:${item}`}>
                  {item}
                </span>
              ))}
            </div>
          ) : (
            <p className="metric-breakdown-aside-empty">{activeBreakdown.asideEmptyText ?? "Sin detalle adicional para este bloque."}</p>
          )}
        </aside>
      ) : null}
    </div>
  );
}

function computeBreakdownHoverPanelTop({
  shellRect,
  elementRect,
  panelHeight,
  viewportPadding = 16,
}: {
  shellRect: DOMRect;
  elementRect: DOMRect;
  panelHeight: number;
  viewportPadding?: number;
}) {
  const baseTop = Math.max(0, elementRect.top - shellRect.top);

  if (panelHeight <= 0) {
    return baseTop;
  }

  const visualViewport = window.visualViewport;
  const viewportTop = visualViewport?.offsetTop ?? 0;
  const viewportHeight = visualViewport?.height ?? window.innerHeight;
  const minTop = Math.max(0, viewportTop + viewportPadding - shellRect.top);
  const maxTop = Math.max(minTop, viewportTop + viewportHeight - viewportPadding - shellRect.top - panelHeight);

  return Math.min(Math.max(baseTop, minTop), maxTop);
}

function getPointSurvival(point: OpportunityPoint, horizon: Horizon) {
  return horizon === "24m" ? point.expected_survival_24m : point.expected_survival_12m;
}

function getSectionSurvival(section: OpportunitySection, horizon: Horizon) {
  return horizon === "24m" ? section.expected_survival_24m : section.expected_survival_12m;
}

function getOpportunityArtifactSignature(artifacts: OpportunityArtifacts) {
  return `${artifacts.meta.generated_at}:${artifacts.meta.section_geojson_path}:${artifacts.points.length}`;
}

function formatPercent(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${(value * 100).toFixed(0)}%`;
}

function formatSignalPercent(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }

  const percent = value * 100;
  if (Math.abs(percent) < 1e-9 || Math.abs(percent - 100) < 1e-9) {
    return `${percent.toFixed(0)}%`;
  }

  const absPercent = Math.abs(percent);
  const decimals = absPercent < 1 || absPercent > 99 ? 2 : absPercent < 10 || absPercent > 90 ? 1 : 0;
  return `${percent.toFixed(decimals)}%`;
}

function formatCurrency(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);
}

function formatPricePerSquareMeter(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${Math.round(value)} €/m²`;
}

function formatArea(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${Math.round(value)} m²`;
}

function formatDistance(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${Math.round(value)} m`;
}

function formatDensity(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${Math.round(value).toLocaleString("es-ES")} hab/km²`;
}

function formatDensityInline(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${Math.round(value).toLocaleString("es-ES")}/km²`;
}

function formatShare(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${(value * 100).toFixed(1)}%`;
}

function formatTurnoverValue(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  if (Math.abs(value) < 1e-9) {
    return "0%";
  }
  return `${(value * 100).toFixed(1)}%`;
}

function formatRate(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return value.toFixed(2);
}

function formatRatePerThousandResidents(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${value.toFixed(2)} / 1.000 hab`;
}

function formatInteger(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0 }).format(value);
}

function formatCompact(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return new Intl.NumberFormat("es-ES", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function formatAge(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${new Intl.NumberFormat("es-ES", { maximumFractionDigits: 1 }).format(value)} años`;
}

function formatHectares(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${new Intl.NumberFormat("es-ES", { maximumFractionDigits: 1 }).format(value)} ha`;
}

function formatResidentialBaseValue(totalPopulation: number | null, density: number | null) {
  if (isFiniteNumber(totalPopulation)) {
    return `${formatCompact(totalPopulation)} hab`;
  }
  return formatDensity(density);
}

function formatRiskPercentile(value: number) {
  if (!Number.isFinite(value)) {
    return "Sin datos";
  }
  return `P${Math.round(value * 100)}`;
}

function formatAvisosCount(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin conteo";
  }
  const amount = new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0 }).format(value);
  return `${amount} avisos`;
}

function formatActivityStabilityValue(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin referencia";
  }
  return formatSignalPercent(value);
}

function formatActivitySampleValue(nLocales: number | null, sourceZone: OpportunityActivity["source_zone"]) {
  if (!isFiniteNumber(nLocales)) {
    return "Sin muestra";
  }

  const amount = formatCompact(nLocales);
  if (sourceZone === "city") {
    return `${amount} en Madrid`;
  }
  if (sourceZone === "district") {
    return `${amount} en la zona`;
  }
  return amount;
}

function formatRank(rank: number | null, total: number | null) {
  if (!isFiniteNumber(rank) || !isFiniteNumber(total) || total <= 0) {
    return "Sin datos";
  }
  return `#${rank} de ${total}`;
}

function buildOpportunityTierMetric(scopeId: string, value: string): MetricDefinition {
  const resolvedTier = value || "Sin lectura";
  return {
    id: `${scopeId}:opportunity-tier`,
    label: "Lectura de oportunidad",
    value: resolvedTier,
    summary: buildOpportunityTierSummary(resolvedTier),
    calculation: "Traducimos el percentil de riesgo de la sección a un tramo cualitativo para lectura rápida. Alta cubre aproximadamente P0-P20, Solida P21-P45, Intermedia P46-P70 y Fragil el tramo restante.",
    breakdownTitle: "Tramos posibles",
    breakdownItems: buildOpportunityTierBreakdownItems(resolvedTier),
  };
}

function buildRiskPercentileMetric(scopeId: string, value: number | null): MetricDefinition {
  return {
    id: `${scopeId}:risk-percentile`,
    label: "Percentil riesgo",
    value: formatRiskPercentile(value ?? Number.NaN),
    summary: "Ubica este entorno dentro de la distribución de riesgo de Madrid. Cuanto más alto, más exigente es el entorno observado.",
    calculation: "Ordenamos todas las secciones por su score de riesgo. Un P80 significa que el riesgo de esta sección queda por encima de aproximadamente el 80% de las secciones de la ciudad.",
  };
}

function buildListingOperationMetric(scopeId: string, point: OpportunityPoint, points: OpportunityPoint[]): MetricDefinition {
  return {
    id: `${scopeId}:operation-chip`,
    label: "Operación",
    value: point.operation || "Sin dato",
    summary: `Sitúa este anuncio dentro del mix de ${point.operation || "operación"} frente a alquiler y venta en Madrid, su distrito y su barrio.`,
    calculation: "Contamos los anuncios disponibles del mismo ámbito y calculamos qué proporción comparte la misma operación que este local.",
    breakdownTitle: "Distribución venta / alquiler",
    breakdownItems: buildOperationBreakdownItems(point, points),
  };
}

function buildListingPriceMetric(scopeId: string, point: OpportunityPoint, points: OpportunityPoint[]): MetricDefinition {
  return {
    id: `${scopeId}:price-chip`,
    label: "Precio",
    value: formatCurrency(point.price_eur),
    summary: "Compara el precio pedido del anuncio con otros locales de la misma operación en Madrid, distrito y barrio.",
    calculation: "Usamos el precio total anunciado y lo contrastamos contra anuncios de la misma operación dentro de cada ámbito territorial para mostrar medianas y posición relativa.",
    breakdownTitle: "Comparación de precio",
    breakdownItems: buildListingValueBreakdownItems({
      point,
      points,
      field: "price_eur",
      formatValue: formatCurrency,
      labelSuffix: "comparables",
      percentileLabel: "precio",
    }),
  };
}

function buildListingAreaMetric(scopeId: string, point: OpportunityPoint, points: OpportunityPoint[]): MetricDefinition {
  return {
    id: `${scopeId}:area-chip`,
    label: "Superficie",
    value: formatArea(point.area_m2),
    summary: "Compara la superficie anunciada con otros locales de la misma operación en Madrid, distrito y barrio.",
    calculation: "Usamos los metros cuadrados anunciados y los contrastamos contra anuncios de la misma operación dentro de cada ámbito territorial para mostrar medianas y posición relativa.",
    breakdownTitle: "Comparación de superficie",
    breakdownItems: buildListingValueBreakdownItems({
      point,
      points,
      field: "area_m2",
      formatValue: formatArea,
      labelSuffix: "comparables",
      percentileLabel: "superficie",
    }),
  };
}

function buildRankingMetric({
  scopeId,
  cityRank,
  cityTotal,
  districtRank,
  districtTotal,
  barrioRank,
  barrioTotal,
  districtName,
  barrioName,
  subject,
}: {
  scopeId: string;
  cityRank: number | null;
  cityTotal: number | null;
  districtRank: number | null;
  districtTotal: number | null;
  barrioRank: number | null;
  barrioTotal: number | null;
  districtName: string;
  barrioName: string;
  subject: string;
}): MetricDefinition {
  return {
    id: `${scopeId}:ranking`,
    label: "Ranking 3 escalas",
    value: buildRankingHeadline(cityRank, cityTotal, districtRank, districtTotal, barrioRank, barrioTotal),
    summary: `Resume cómo queda ${subject} frente a Madrid, su distrito y su barrio. La lectura gana solidez cuando el buen puesto se sostiene en las tres escalas y no solo en una muy pequeña.`,
    calculation: "Ordenamos las secciones por menor riesgo predictivo y mostramos el puesto resultante en Madrid, dentro del distrito y dentro del barrio. Cuanto más cerca de #1, más favorable es la lectura.",
    breakdownTitle: "Madrid, distrito y barrio",
    breakdownItems: buildRankBreakdownItems({
      cityRank,
      cityTotal,
      districtRank,
      districtTotal,
      barrioRank,
      barrioTotal,
      districtName,
      barrioName,
    }),
  };
}

function buildActivityRankingMethodMetric({
  scopeId,
  activities,
}: {
  scopeId: string;
  activities: OpportunityActivity[];
}): MetricDefinition {
  const topActivity = activities[0] ?? null;

  return {
    id: `${scopeId}:activity-ranking-method`,
    label: "Cómo interpretar este ranking",
    value: "Cox + ajuste contextual",
    summary: topActivity
      ? `${topActivity.display_label} aparece arriba porque, al simular esa actividad en esta misma ubicación, es la que obtiene el mejor equilibrio entre riesgo previsto por el modelo, encaje histórico de la categoría y solidez de la evidencia disponible.`
      : "El ranking no ordena por popularidad ni por volumen bruto: compara macrocategorías en esta misma ubicación y coloca arriba las que salen mejor en nuestro score de riesgo contextual.",
    calculation: "La base sale de un modelo de survival analysis tipo Cox, entrenado sobre histórico real de aperturas, cierres y cambios de actividad. Para cada macrocategoría recalculamos el riesgo bruto en esta misma zona con sus features de contexto. Ese score se transforma a una escala comparable de riesgo y además lo contrastamos contra el histórico de esa propia categoría para medir su encaje específico. Después combinamos ambas señales con un peso que sube cuando la categoría tiene más eventos observados y un patrón más específico, generando un índice contextual final. Sobre ese índice añadimos penalizaciones suaves si la evidencia solo llega desde distrito o ciudad, o si el soporte estadístico es débil, y con eso ordenamos la lista de menor a mayor riesgo contextual.",
    breakdownTitle: "Qué entra en juego",
    breakdownItems: [
      {
        rank: 1,
        label: "Modelo ML base",
        value: "Cox survival",
        detail: "Simulamos cada macrocategoría en esta misma ubicación y el modelo estima un riesgo bruto usando demografía, renta, competencia, accesibilidad, avisos y resto de señales del entorno.",
      },
      {
        rank: 2,
        label: "Encaje específico",
        value: "Fit por actividad",
        detail: "No miramos solo el riesgo absoluto: comparamos cada actividad contra su propia distribución histórica para saber si aquí rinde mejor o peor de lo habitual para esa categoría.",
      },
      {
        rank: 3,
        label: "Orden final",
        value: "Score contextual",
        detail: topActivity
          ? `Combinamos riesgo bruto, encaje por categoría y fortaleza de la evidencia. En el #1 actual eso se traduce en ${formatActivityStabilityValue(topActivity.survival_24m)} de supervivencia a 24 meses con ${formatActivitySampleValue(topActivity.n_locales, topActivity.source_zone)} de muestra comparable cerca.`
          : "Combinamos riesgo bruto, encaje por categoría y fortaleza de la evidencia. Después penalizamos ligeramente lecturas con soporte más flojo para evitar sobreinterpretar señales débiles.",
      },
    ],
  };
}

function buildMetroMetric({
  scopeId,
  label,
  summarySubject,
  calculationSubject,
  distance,
  station500,
  station1000,
  nearestName,
  nearestStationName,
  stationNames500,
  stationNames1000,
  distanceBenchmark,
  station500Benchmark,
  station1000Benchmark,
}: {
  scopeId: string;
  label: string;
  summarySubject: string;
  calculationSubject: string;
  distance: number | null;
  station500: number | null;
  station1000: number | null;
  nearestName: string;
  nearestStationName: string;
  stationNames500: string[];
  stationNames1000: string[];
  distanceBenchmark: OpportunityFieldInsight | null | undefined;
  station500Benchmark: OpportunityFieldInsight | null | undefined;
  station1000Benchmark: OpportunityFieldInsight | null | undefined;
}): MetricDefinition {
  return {
    id: `${scopeId}:metro`,
    label,
    value: formatDistance(distance),
    summary: buildMetroSummary({
      subject: summarySubject,
      distance,
      station500,
      station1000,
      nearestName,
      nearestStationName,
      cityPercentile: distanceBenchmark?.cityPercentile ?? null,
    }),
    calculation: `Medimos en metros la distancia en línea recta desde ${calculationSubject} hasta el acceso de metro más cercano. Después agrupamos todos los accesos cercanos por estación oficial para contar cuántas paradas únicas hay a 500 m y a 1 km usando la malla principal de Metro de Madrid.`,
    breakdownTitle: "Cercanía y paradas",
    breakdownItems: buildMetroBreakdownItems({
      distance,
      station500,
      station1000,
      nearestName,
      nearestStationName,
      stationNames500,
      stationNames1000,
      distanceBenchmark,
      station500Benchmark,
      station1000Benchmark,
    }),
  };
}

function buildResidentialBaseMetric({
  scopeId,
  totalPopulation,
  density,
  populationBenchmark,
  densityBenchmark,
}: {
  scopeId: string;
  totalPopulation: number | null;
  density: number | null;
  populationBenchmark: OpportunityFieldInsight | null | undefined;
  densityBenchmark: OpportunityFieldInsight | null | undefined;
}): MetricDefinition {
  return {
    id: `${scopeId}:residential-base`,
    label: "Población",
    value: formatResidentialBaseValue(totalPopulation, density),
    summary: buildResidentialBaseSummary(totalPopulation, density),
    calculation: "La tarjeta muestra primero cuánta población vive en la zona. En el desglose mantenemos densidad y superficie aproximada para distinguir entre una base residencial grande y una base muy concentrada en pocas hectáreas.",
    breakdownTitle: "Población y concentración",
    breakdownItems: buildResidentialBaseBreakdownItems({
      totalPopulation,
      density,
      populationBenchmark,
      densityBenchmark,
    }),
  };
}

function buildAgeMetric({
  scopeId,
  ageMean,
  benchmark,
  districtName,
  barrioName,
  subject,
}: {
  scopeId: string;
  ageMean: number | null;
  benchmark: OpportunityFieldInsight | null | undefined;
  districtName: string;
  barrioName: string;
  subject: string;
}): MetricDefinition {
  return {
    id: `${scopeId}:age`,
    label: "Edad media",
    value: formatAge(ageMean),
    summary: `Aproxima la edad media ${subject}. Ayuda a distinguir entornos más jóvenes, maduros o sénior sin reducir la lectura a un único tramo de edad.`,
    calculation: "Usamos la edad media estimada del padrón en la sección de referencia más reciente disponible.",
    breakdownTitle: "Comparación territorial",
    breakdownItems: buildTerritorialBreakdownItems({
      benchmark,
      districtName,
      barrioName,
      formatValue: formatAge,
    }),
  };
}

function buildCompetitionMetric({
  scopeId,
  localCount,
  sameCategoryShare,
  bestActivityLabel,
  localCountBenchmark,
  sameCategoryBenchmark,
  sectionSubject,
}: {
  scopeId: string;
  localCount: number | null;
  sameCategoryShare: number | null;
  bestActivityLabel: string;
  localCountBenchmark: OpportunityFieldInsight | null | undefined;
  sameCategoryBenchmark: OpportunityFieldInsight | null | undefined;
  sectionSubject: string;
}): MetricDefinition {
  return {
    id: `${scopeId}:competition`,
    label: "Competencia local",
    value: formatCompact(localCount),
    summary: bestActivityLabel
      ? `Resume cuántos locales activos hay en ${sectionSubject} y qué parte del stock ya pertenece a la misma categoría amplia que hoy lidera el ranking, ${bestActivityLabel}.`
      : `Resume cuántos locales activos hay en ${sectionSubject} y qué parte del stock ya cae en la misma categoría amplia usada como referencia competitiva.`,
    calculation: "Tomamos el stock histórico de locales activos observado en la sección usada para puntuar el entorno. La cuota de misma categoría se calcula sobre una familia amplia de actividad, no sobre el epígrafe exacto ni sobre competencia directa uno a uno.",
    breakdownTitle: "Lectura competitiva",
    breakdownItems: buildCompetitionBreakdownItems({
      localCount,
      sameCategoryShare,
      bestActivityLabel,
      localCountBenchmark,
      sameCategoryBenchmark,
    }),
  };
}

function buildPointPrimaryMetrics(point: OpportunityPoint, horizon: Horizon, benchmarks: OpportunityBenchmarkContext | null): MetricDefinition[] {
  const horizonLabel = formatHorizonShortLabel(horizon);
  return [
    {
      id: `listing:${point.listing_id}:survival:${horizon}`,
      label: `Supervivencia ${horizonLabel}`,
      value: formatPercent(getPointSurvival(point, horizon)),
      summary: `Es la probabilidad esperada de que un local comparable siga activo dentro de ${horizonLabel} en este entorno.`,
      calculation: "Partimos del score de riesgo del modelo para la sección donde cae el local y lo transformamos a supervivencia esperada en ese horizonte."
    },
    buildRankingMetric({
      scopeId: `listing:${point.listing_id}`,
      cityRank: point.city_rank,
      cityTotal: point.city_total_sections,
      districtRank: point.district_rank,
      districtTotal: point.district_total_sections,
      barrioRank: point.barrio_rank,
      barrioTotal: point.barrio_total_sections,
      districtName: point.district_name,
      barrioName: point.barrio_name,
      subject: "esta sección",
    }),
    {
      id: `listing:${point.listing_id}:income`,
      label: "Ingreso del entorno",
      value: formatCurrency(point.renta_effective_eur),
      summary: buildIncomeSummary({
        subject: "alrededor del local",
        granularityUsed: point.renta_granularity_used,
        referenceYear: point.renta_reference_year,
        outlierAdjusted: point.renta_outlier_adjusted,
      }),
      calculation: buildIncomeCalculation({
        granularityUsed: point.renta_granularity_used,
        outlierAdjusted: point.renta_outlier_adjusted,
      }),
      breakdownTitle: "Comparación rápida",
      breakdownItems: buildTerritorialBreakdownItems({
        benchmark: benchmarks?.metrics.renta_effective_eur,
        districtName: point.district_name,
        barrioName: point.barrio_name,
        formatValue: formatCurrency,
      })
    },
    buildResidentialBaseMetric({
      scopeId: `listing:${point.listing_id}`,
      totalPopulation: point.total_population_start,
      density: point.population_density_km2_start,
      populationBenchmark: benchmarks?.metrics.total_population_start,
      densityBenchmark: benchmarks?.metrics.population_density_km2_start,
    }),
    buildAgeMetric({
      scopeId: `listing:${point.listing_id}`,
      ageMean: point.age_mean_start,
      benchmark: benchmarks?.metrics.age_mean_start,
      districtName: point.district_name,
      barrioName: point.barrio_name,
      subject: "del entorno inmediato",
    }),
    buildMetroMetric({
      scopeId: `listing:${point.listing_id}`,
      label: "Metro cercano",
      summarySubject: "el local",
      calculationSubject: "el local",
      distance: point.metro_distance_m_start,
      station500: point.metro_station_count_500m_start,
      station1000: point.metro_station_count_1000m_start,
      nearestName: point.metro_nearest_name_start,
      nearestStationName: point.metro_nearest_station_name_start,
      stationNames500: point.metro_station_names_500m_start,
      stationNames1000: point.metro_station_names_1000m_start,
      distanceBenchmark: benchmarks?.metrics.metro_distance_m_start,
      station500Benchmark: benchmarks?.metrics.metro_station_count_500m_start,
      station1000Benchmark: benchmarks?.metrics.metro_station_count_1000m_start,
    }),
    buildCompetitionMetric({
      scopeId: `listing:${point.listing_id}`,
      localCount: point.section_local_count_start,
      sameCategoryShare: point.section_same_activity_category_share_start,
      bestActivityLabel: point.best_activity_label,
      localCountBenchmark: benchmarks?.metrics.section_local_count_start,
      sameCategoryBenchmark: benchmarks?.metrics.section_same_activity_category_share_start,
      sectionSubject: "la sección de referencia",
    }),
  ];
}

function buildSectionPrimaryMetrics(section: OpportunitySection, horizon: Horizon, benchmarks: OpportunityBenchmarkContext | null): MetricDefinition[] {
  const horizonLabel = formatHorizonShortLabel(horizon);
  return [
    {
      id: `section:${section.section_key}:survival:${horizon}`,
      label: `Supervivencia ${horizonLabel}`,
      value: formatPercent(getSectionSurvival(section, horizon)),
      summary: `Es la probabilidad esperada de que un local comparable siga activo dentro de ${horizonLabel} en esta sección.`,
      calculation: "Partimos del score de riesgo agregado de la sección y lo transformamos a supervivencia esperada para el horizonte seleccionado."
    },
    buildRankingMetric({
      scopeId: `section:${section.section_key}`,
      cityRank: section.city_rank,
      cityTotal: section.city_total_sections,
      districtRank: section.district_rank,
      districtTotal: section.district_total_sections,
      barrioRank: section.barrio_rank,
      barrioTotal: section.barrio_total_sections,
      districtName: section.district_name,
      barrioName: section.barrio_name,
      subject: "esta sección",
    }),
    {
      id: `section:${section.section_key}:income`,
      label: "Ingreso del entorno",
      value: formatCurrency(section.renta_effective_eur),
      summary: buildIncomeSummary({
        subject: "de esta zona",
        granularityUsed: section.renta_granularity_used,
        referenceYear: section.renta_reference_year,
        outlierAdjusted: section.renta_outlier_adjusted,
      }),
      calculation: buildIncomeCalculation({
        granularityUsed: section.renta_granularity_used,
        outlierAdjusted: section.renta_outlier_adjusted,
      }),
      breakdownTitle: "Comparación rápida",
      breakdownItems: buildTerritorialBreakdownItems({
        benchmark: benchmarks?.metrics.renta_effective_eur,
        districtName: section.district_name,
        barrioName: section.barrio_name,
        formatValue: formatCurrency,
      })
    },
    buildResidentialBaseMetric({
      scopeId: `section:${section.section_key}`,
      totalPopulation: section.total_population_start,
      density: section.population_density_km2_start,
      populationBenchmark: benchmarks?.metrics.total_population_start,
      densityBenchmark: benchmarks?.metrics.population_density_km2_start,
    }),
    buildAgeMetric({
      scopeId: `section:${section.section_key}`,
      ageMean: section.age_mean_start,
      benchmark: benchmarks?.metrics.age_mean_start,
      districtName: section.district_name,
      barrioName: section.barrio_name,
      subject: "de la sección",
    }),
    buildMetroMetric({
      scopeId: `section:${section.section_key}`,
      label: "Metro de referencia",
      summarySubject: "la sección",
      calculationSubject: "el centroide de la sección",
      distance: section.metro_distance_m_start,
      station500: section.metro_station_count_500m_start,
      station1000: section.metro_station_count_1000m_start,
      nearestName: section.metro_nearest_name_start,
      nearestStationName: section.metro_nearest_station_name_start,
      stationNames500: section.metro_station_names_500m_start,
      stationNames1000: section.metro_station_names_1000m_start,
      distanceBenchmark: benchmarks?.metrics.metro_distance_m_start,
      station500Benchmark: benchmarks?.metrics.metro_station_count_500m_start,
      station1000Benchmark: benchmarks?.metrics.metro_station_count_1000m_start,
    }),
    buildCompetitionMetric({
      scopeId: `section:${section.section_key}`,
      localCount: section.section_local_count_start,
      sameCategoryShare: section.section_same_activity_category_share_start,
      bestActivityLabel: section.best_activity_label,
      localCountBenchmark: benchmarks?.metrics.section_local_count_start,
      sameCategoryBenchmark: benchmarks?.metrics.section_same_activity_category_share_start,
      sectionSubject: "la sección",
    }),
  ];
}

function buildContextMetrics({
  scopeId,
  uniqueActivityCategories,
  turnoverRate12m,
  shareForeign,
  shareYoung,
  shareSenior,
  avisosBarrio,
  avisosDistrict,
  topAvisosBarrioCategories,
  topAvisosDistrictCategories,
  benchmarks,
  districtName,
  barrioName,
  facilitiesTier,
  facilities200m,
  facilities500m,
  facilities1000m,
  facilitiesByCategory,
  vulnerabilidadGlobal,
  vulnerabilidadGlobalMediaCiudad,
  vulnerabilidadEsferas,
  inspeccionesDistritoTotal,
  inspeccionesCiudadMedia,
  inspeccionesTopEpigrafes,
  indicadoresDistrito,
}: {
  scopeId: string;
  uniqueActivityCategories: number | null;
  turnoverRate12m: number | null;
  shareForeign: number | null;
  shareYoung: number | null;
  shareSenior: number | null;
  avisosBarrio: number | null;
  avisosDistrict: number | null;
  topAvisosBarrioCategories: OpportunityAvisoCategory[];
  topAvisosDistrictCategories: OpportunityAvisoCategory[];
  benchmarks: OpportunityBenchmarkContext | null;
  districtName: string;
  barrioName: string;
  facilitiesTier: string;
  facilities200m: number;
  facilities500m: number;
  facilities1000m: number;
  facilitiesByCategory: FacilityCategory[];
  vulnerabilidadGlobal: number | null;
  vulnerabilidadGlobalMediaCiudad: number | null;
  vulnerabilidadEsferas: VulnerabilidadEsfera[];
  inspeccionesDistritoTotal: number | null;
  inspeccionesCiudadMedia: number | null;
  inspeccionesTopEpigrafes: InspeccionEpigrafe[];
  indicadoresDistrito: IndicadorDistrito[];
}): MetricDefinition[] {
  return [
    {
      id: `${scopeId}:active-categories`,
      label: "Categorías activas",
      value: formatCompact(uniqueActivityCategories),
      summary: "Cuenta cuántas categorías comerciales distintas siguen activas en la sección. Más alto significa más mezcla real del tejido, no necesariamente más competencia directa.",
      calculation: "Contamos cuántas categorías de actividad distintas aparecen activas en la sección censal.",
      breakdownTitle: "Comparación territorial",
      breakdownItems: buildTerritorialBreakdownItems({
        benchmark: benchmarks?.metrics.section_unique_activity_category_count_start,
        districtName,
        barrioName,
        formatValue: formatCompact,
      })
    },
    {
      id: `${scopeId}:turnover-12m`,
      label: "Rotación 12m",
      value: formatTurnoverValue(turnoverRate12m),
      summary: buildTurnoverSummary(turnoverRate12m),
      calculation: "Dividimos los cambios o salidas observados en los últimos 12 meses entre el stock de locales de la sección. En zonas tan pequeñas es normal observar ceros exactos cuando no se registra ningún movimiento en ese año.",
      breakdownTitle: "Comparación territorial",
      breakdownItems: buildTerritorialBreakdownItems({
        benchmark: benchmarks?.metrics.section_turnover_rate_12m_start,
        districtName,
        barrioName,
        formatValue: formatShare,
      })
    },
    {
      id: `${scopeId}:foreign-share`,
      label: "Extranjera",
      value: formatShare(shareForeign),
      summary: "Mide el peso de residentes extranjeros dentro de la sección.",
      calculation: "Dividimos la población extranjera entre la población total de la sección.",
      breakdownTitle: "Comparación territorial",
      breakdownItems: buildTerritorialBreakdownItems({
        benchmark: benchmarks?.metrics.share_foreign_start,
        districtName,
        barrioName,
        formatValue: formatShare,
      })
    },
    {
      id: `${scopeId}:young-share`,
      label: "Joven 15-29",
      value: formatShare(shareYoung),
      summary: "Aproxima el peso de poblacion joven en el entorno.",
      calculation: "Dividimos los residentes de 15 a 29 años entre la población total de la sección.",
      breakdownTitle: "Comparación territorial",
      breakdownItems: buildTerritorialBreakdownItems({
        benchmark: benchmarks?.metrics.share_age_15_29_start,
        districtName,
        barrioName,
        formatValue: formatShare,
      })
    },
    {
      id: `${scopeId}:senior-share`,
      label: "Tercera edad 65+",
      value: formatShare(shareSenior),
      summary: "Aproxima el peso de población de 65 años o más en el entorno.",
      calculation: "Dividimos los residentes de 65 años o más entre la población total de la sección.",
      breakdownTitle: "Comparación territorial",
      breakdownItems: buildTerritorialBreakdownItems({
        benchmark: benchmarks?.metrics.share_age_65_plus_start,
        districtName,
        barrioName,
        formatValue: formatShare,
      })
    },
    buildDistrictUnemploymentMetric({
      scopeId,
      districtName,
      indicators: indicadoresDistrito,
    }),
    buildDistrictDependencyMetric({
      scopeId,
      districtName,
      indicators: indicadoresDistrito,
    }),
    buildAvisosMetric({
      scopeId,
      avisosBarrio,
      avisosDistrict,
      topAvisosBarrioCategories,
      topAvisosDistrictCategories,
      districtName,
      barrioName,
    }),
    {
      id: `${scopeId}:facilities`,
      label: "Equipamientos cerca",
      value: facilitiesTier || "Sin datos",
      summary: buildFacilitiesSummary(facilitiesTier, facilities200m, facilities500m, facilities1000m),
      calculation: "Contamos equipamientos públicos (BiciMAD, colegios, parques, deportivos, culturales, bibliotecas, mercados, etc.) en radios de 200 m, 500 m y 1 km desde la ubicación del local usando distancia haversine sobre coordenadas WGS-84. Como esos radios son acumulados, en el detalle visible los convertimos a tramos no solapados: 0-200 m, 200-500 m y 500 m-1 km.",
      breakdownTitle: "Equipamientos por categoría",
      breakdownItems: buildFacilitiesBreakdownItems(facilitiesByCategory),
      breakdownEmptyText: "Sin datos de equipamientos disponibles para esta ubicación."
    },
    {
      id: `${scopeId}:inspecciones`,
      label: "Inspecciones consumo",
      value: formatCompact(inspeccionesDistritoTotal),
      summary: buildInspeccionesSummary(inspeccionesDistritoTotal, inspeccionesCiudadMedia, districtName),
      calculation: "Recuento de inspecciones de consumo realizadas en el distrito según el último dataset publicado por el Ayuntamiento de Madrid. La media ciudad es el promedio por distrito.",
      breakdownTitle: `Top epígrafes inspeccionados · ${districtName || "Distrito"}`,
      breakdownItems: buildInspeccionesBreakdownItems(inspeccionesTopEpigrafes),
      breakdownEmptyText: "Sin datos de inspecciones disponibles para este distrito."
    },
    {
      id: `${scopeId}:vulnerabilidad`,
      label: "Vulnerabilidad",
      value: formatVulnerabilidad(vulnerabilidadGlobal),
      summary: buildVulnerabilidadSummary(vulnerabilidadGlobal, vulnerabilidadGlobalMediaCiudad, districtName),
      calculation: "Índice global IGUALA del Ayuntamiento de Madrid. Combina cinco esferas: bienestar social, medio ambiente, educación, economía y salud. Valores más altos indican mayor vulnerabilidad relativa dentro de Madrid.",
      breakdownTitle: "Esferas de vulnerabilidad",
      breakdownItems: buildVulnerabilidadBreakdownItems(vulnerabilidadEsferas),
      breakdownEmptyText: "Sin datos IGUALA disponibles para este distrito."
    }
  ];
}

function buildAvisosMetric({
  scopeId,
  avisosBarrio,
  avisosDistrict,
  topAvisosBarrioCategories,
  topAvisosDistrictCategories,
  districtName,
  barrioName,
}: {
  scopeId: string;
  avisosBarrio: number | null;
  avisosDistrict: number | null;
  topAvisosBarrioCategories: OpportunityAvisoCategory[];
  topAvisosDistrictCategories: OpportunityAvisoCategory[];
  districtName: string;
  barrioName: string;
}): MetricDefinition {
  const useBarrioScope = isFiniteNumber(avisosBarrio) || topAvisosBarrioCategories.length > 0;
  const activeValue = useBarrioScope ? avisosBarrio : avisosDistrict;
  const scopeLabel = useBarrioScope ? "barrio" : "distrito";
  const scopeName = useBarrioScope ? (barrioName || "El barrio") : (districtName || "El distrito");
  const activeCategories = useBarrioScope ? topAvisosBarrioCategories : topAvisosDistrictCategories;
  const districtComparison = useBarrioScope && isFiniteNumber(avisosDistrict)
    ? ` El distrito completo marca ${formatRatePerThousandResidents(avisosDistrict)}.`
    : "";

  return {
    id: `${scopeId}:avisos`,
    label: "Avisos recientes",
    value: formatRatePerThousandResidents(activeValue),
    summary: isFiniteNumber(activeValue)
      ? `${scopeName} registra ${formatRatePerThousandResidents(activeValue)} en el último año por cada 1.000 habitantes.${districtComparison} Funciona como una señal indirecta de fricción vecinal o intensidad de uso reciente.`
      : "No hay datos recientes de avisos vecinales ni a escala de barrio ni de distrito para este entorno.",
    calculation: "Priorizamos la lectura del barrio por cercanía. Si falta, usamos el distrito. En ambos casos normalizamos el total del año previo por cada 1.000 habitantes y mostramos las categorías con más peso.",
    breakdownTitle: `Top categorías · ${scopeName}`,
    breakdownItems: buildAvisosBreakdownItems(activeCategories, scopeLabel),
    breakdownEmptyText: `Sin desglose de categorías de avisos disponible para este ${scopeLabel}.`,
  };
}

function buildAvisosBreakdownItems(categories: OpportunityAvisoCategory[], scopeLabel: string): MetricBreakdownItem[] {
  return categories.slice(0, 3).map((category, index) => ({
    rank: Number.isFinite(category.rank) ? category.rank : index + 1,
    label: category.label,
    value: formatSignalPercent(category.share_of_zone),
    detail: `${formatAvisosCount(category.count)} · ${formatSignalPercent(category.share_of_zone)} del ${scopeLabel}`
  }));
}

function buildResidentialBaseBreakdownItems({
  totalPopulation,
  density,
  populationBenchmark,
  densityBenchmark,
}: {
  totalPopulation: number | null;
  density: number | null;
  populationBenchmark: OpportunityFieldInsight | null | undefined;
  densityBenchmark: OpportunityFieldInsight | null | undefined;
}): MetricBreakdownItem[] {
  const areaHectares = computeApproxSectionAreaHectares(totalPopulation, density);
  return [
    {
      rank: 1,
      label: "Población sección",
      value: formatCompact(totalPopulation),
      detail: buildTerritorialMedianSummary(populationBenchmark, formatCompact),
    },
    {
      rank: 2,
      label: "Densidad",
      value: formatDensity(density),
      detail: buildTerritorialMedianSummary(densityBenchmark, formatDensity),
    },
    {
      rank: 3,
      label: "Superficie aprox.",
      value: formatHectares(areaHectares),
      detail: isFiniteNumber(areaHectares)
        ? "Sección compacta: una población moderada puede convivir con densidad alta cuando el área es pequeña."
        : "Sin datos suficientes para aproximar la superficie usada en la densidad.",
    },
  ];
}

function buildTerritorialBreakdownItems({
  benchmark,
  districtName,
  barrioName,
  formatValue,
}: {
  benchmark: OpportunityFieldInsight | null | undefined;
  districtName: string;
  barrioName: string;
  formatValue: (value: number | null) => string;
}): MetricBreakdownItem[] {
  return [
    {
      rank: 1,
      label: "Madrid",
      value: formatValue(benchmark?.cityMedian ?? null),
      detail: formatCityPercentileDetail(benchmark?.cityPercentile ?? null),
    },
    {
      rank: 2,
      label: "Tu distrito",
      value: formatValue(benchmark?.districtMedian ?? null),
      detail: districtName || "Sin distrito",
    },
    {
      rank: 3,
      label: "Tu barrio",
      value: formatValue(benchmark?.barrioMedian ?? null),
      detail: barrioName || "Sin barrio",
    },
  ];
}

function buildTerritorialMedianSummary(
  benchmark: OpportunityFieldInsight | null | undefined,
  formatValue: (value: number | null) => string,
) {
  const parts = [
    isFiniteNumber(benchmark?.cityMedian) ? `Madrid: ${formatValue(benchmark?.cityMedian ?? null)}` : null,
    isFiniteNumber(benchmark?.districtMedian) ? `Distrito: ${formatValue(benchmark?.districtMedian ?? null)}` : null,
    isFiniteNumber(benchmark?.barrioMedian) ? `Barrio: ${formatValue(benchmark?.barrioMedian ?? null)}` : null,
  ].filter((value): value is string => Boolean(value));

  return parts.length > 0 ? parts.join(" · ") : "Sin medianas territoriales";
}

function buildMetroSummary({
  subject,
  distance,
  station500,
  station1000,
  nearestName,
  nearestStationName,
  cityPercentile,
}: {
  subject: string;
  distance: number | null;
  station500: number | null;
  station1000: number | null;
  nearestName: string;
  nearestStationName: string;
  cityPercentile: number | null;
}) {
  if (!isFiniteNumber(distance)) {
    return `No hay una lectura fiable de cercanía al metro para ${subject}.`;
  }

  const intro = nearestStationName
    ? `La estación más cercana para ${subject} es ${nearestStationName}; el acceso más próximo queda a ${formatDistance(distance)}.`
    : nearestName
      ? `El acceso más cercano para ${subject} es ${nearestName}, a ${formatDistance(distance)}.`
      : `El acceso de metro más cercano para ${subject} está a ${formatDistance(distance)}.`;
  const counts = `Hay ${formatCompact(station500)} paradas oficiales únicas a 500 m y ${formatCompact(station1000)} a 1 km.`;
  const cityRead = buildMetroPercentileNarrative(cityPercentile);

  return [intro, counts, cityRead].filter(Boolean).join(" ");
}

function buildMetroAccessDetail(cityMedian: number | null, names: string[], formatValue: (value: number | null) => string) {
  const base = buildMedianDetail(cityMedian, formatValue);
  if (names.length === 0) {
    return base;
  }
  const identified = names.length === 1 ? "1 parada oficial" : `${names.length} paradas oficiales`;
  return `${base} · ${identified}`;
}

function buildResidentialBaseSummary(totalPopulation: number | null, density: number | null) {
  if (!isFiniteNumber(totalPopulation) && !isFiniteNumber(density)) {
    return "No hay suficiente señal residencial para resumir la población de esta zona.";
  }

  if (isFiniteNumber(totalPopulation) && isFiniteNumber(density)) {
    const areaHectares = computeApproxSectionAreaHectares(totalPopulation, density);
    const explanation = isFiniteNumber(areaHectares)
      ? `Al abrir el detalle verás también densidad y superficie aproximada: esta zona ocupa unas ${formatHectares(areaHectares)}, así que una población contenida y una densidad alta pueden convivir sin contradicción.`
      : "Al abrir el detalle verás también densidad, que reparte esa población sobre la superficie y ayuda a distinguir una base extendida de otra muy concentrada.";
    return `La zona reúne ${formatCompact(totalPopulation)} residentes. ${explanation}`;
  }

  if (isFiniteNumber(totalPopulation)) {
    return `La zona reúne ${formatCompact(totalPopulation)} residentes. Falta la densidad para medir cuán concentrada está esa población.`;
  }

  return `La densidad observada es ${formatDensity(density)}. Falta la población total para completar la lectura residencial.`;
}

function computeApproxSectionAreaHectares(totalPopulation: number | null, density: number | null) {
  if (!isFiniteNumber(totalPopulation) || !isFiniteNumber(density) || density <= 0) {
    return null;
  }
  return (totalPopulation / density) * 100;
}

function buildFacilityBands(count200: number, count500: number, count1000: number) {
  return {
    near: Math.max(0, count200),
    mid: Math.max(0, count500 - count200),
    far: Math.max(0, count1000 - count500),
    total: Math.max(0, count1000),
  };
}

function buildTurnoverSummary(turnoverRate12m: number | null) {
  if (!isFiniteNumber(turnoverRate12m)) {
    return "No hay suficiente histórico reciente para medir la rotación comercial de esta zona.";
  }
  if (Math.abs(turnoverRate12m) < 1e-9) {
    return "En el último año observado no aparece ningún cambio o salida registrado en esta zona pequeña del censo. En este corte esto es frecuente y significa ausencia de movimientos observados, no falta de datos.";
  }
  if (turnoverRate12m < 0.01) {
    return `La rotación existe, pero es muy baja: ${formatTurnoverValue(turnoverRate12m)} del stock comercial en el último año observado.`;
  }
  return `Resume cuánto se ha movido el tejido comercial en el último año observado: ${formatTurnoverValue(turnoverRate12m)} del stock comercial.`;
}

function buildFacilitiesSummary(tier: string, n200: number, n500: number, n1000: number): string {
  if (!tier || tier === "Sin datos") {
    return "No hay datos de equipamientos públicos para esta ubicación.";
  }
  const bands = buildFacilityBands(n200, n500, n1000);
  if (bands.total === 0) {
    return "No aparecen equipamientos públicos identificados dentro de 1 km para esta ubicación.";
  }
  return `El entorno entra en nivel ${tier}. Dentro de 1 km aparecen ${formatInteger(bands.total)} equipamientos públicos: ${formatInteger(bands.near)} a 0-200 m, ${formatInteger(bands.mid)} adicionales entre 200-500 m y ${formatInteger(bands.far)} adicionales entre 500 m y 1 km.`;
}

function buildFacilitiesBreakdownItems(categories: FacilityCategory[]): MetricBreakdownItem[] {
  return categories
    .filter((cat) => cat.count_200m > 0 || cat.count_500m > 0 || cat.count_1000m > 0)
    .slice(0, 6)
    .map((cat, index) => {
      const bands = buildFacilityBands(cat.count_200m, cat.count_500m, cat.count_1000m);
      return {
        rank: index + 1,
        label: cat.label,
        value: `${formatInteger(bands.total)} total`,
        detail: `0-200 m: ${formatInteger(bands.near)} · 200-500 m: ${formatInteger(bands.mid)} · 500 m-1 km: ${formatInteger(bands.far)}`,
      };
    });
}

function buildInspeccionesSummary(total: number | null, cityAvg: number | null, districtName: string): string {
  if (!isFiniteNumber(total)) {
    return "No hay datos de inspecciones de consumo para este distrito.";
  }
  const comparison = isFiniteNumber(cityAvg)
    ? total > cityAvg
      ? `por encima de la media por distrito (${formatCompact(cityAvg)})`
      : `por debajo de la media por distrito (${formatCompact(cityAvg)})`
    : "";
  return `${districtName || "El distrito"} registra ${formatCompact(total)} inspecciones de consumo${comparison ? `, ${comparison}` : ""}. Los epígrafes más inspeccionados revelan el foco regulatorio de la zona.`;
}

function buildInspeccionesBreakdownItems(epigrafes: InspeccionEpigrafe[]): MetricBreakdownItem[] {
  return epigrafes.slice(0, 5).map((ep, index) => ({
    rank: index + 1,
    label: ep.label,
    value: formatCompact(ep.count),
    detail: `${(ep.share * 100).toFixed(1)}% del distrito`,
  }));
}

function formatVulnerabilidad(value: number | null): string {
  if (!isFiniteNumber(value)) return "Sin dato";
  return value.toFixed(1);
}

function buildVulnerabilidadSummary(global: number | null, cityAvg: number | null, districtName: string): string {
  if (!isFiniteNumber(global)) {
    return "No hay datos del índice IGUALA de vulnerabilidad para este distrito.";
  }
  const comparison = isFiniteNumber(cityAvg)
    ? global > cityAvg
      ? `por encima de la media Madrid (${cityAvg.toFixed(1)})`
      : `por debajo de la media Madrid (${cityAvg.toFixed(1)})`
    : "";
  return `${districtName || "El distrito"} tiene un índice global de vulnerabilidad de ${global.toFixed(1)}${comparison ? `, ${comparison}` : ""}. El índice combina bienestar social, medio ambiente, educación, economía y salud.`;
}

function buildVulnerabilidadBreakdownItems(esferas: VulnerabilidadEsfera[]): MetricBreakdownItem[] {
  return esferas.map((esfera, index) => ({
    rank: index + 1,
    label: esfera.label,
    value: isFiniteNumber(esfera.valor) ? esfera.valor.toFixed(1) : "–",
    detail: isFiniteNumber(esfera.media_ciudad) ? `Media Madrid: ${esfera.media_ciudad.toFixed(1)}` : "Sin media",
  }));
}

function buildIndicadoresValue(indicadores: IndicadorDistrito[]): string {
  if (!indicadores || indicadores.length === 0) return "Sin datos";
  const first = indicadores.find((i) => isFiniteNumber(i.valor));
  if (!first) return "Sin datos";
  return `${indicadores.length} señales`;
}

function buildIndicadoresSummary(indicadores: IndicadorDistrito[], districtName: string): string {
  if (!indicadores || indicadores.length === 0) {
    return "No hay indicadores del Panel de datos municipales para este distrito.";
  }
  return `${districtName || "El distrito"} resume aquí apertura y cierre comercial, paro, densidad, zonas verdes, mercados municipales y valor catastral. Cada cifra se compara con la media de Madrid.`;
}

function buildIndicadoresBreakdownItems(indicadores: IndicadorDistrito[]): MetricBreakdownItem[] {
  return indicadores.map((ind, index) => ({
    rank: index + 1,
    label: ind.label,
    value: isFiniteNumber(ind.valor) ? formatIndicadorValue(ind.id, ind.valor) : "–",
    detail: isFiniteNumber(ind.media_ciudad) ? `Media Madrid: ${formatIndicadorValue(ind.id, ind.media_ciudad)}` : "Sin media",
  }));
}

function getDistrictIndicator(indicadores: IndicadorDistrito[], id: string) {
  return indicadores.find((indicator) => indicator.id === id) ?? null;
}

function pickFirstDistrictIndicator(indicadores: IndicadorDistrito[], ids: readonly string[]) {
  return ids
    .map((id) => getDistrictIndicator(indicadores, id))
    .find((indicator): indicator is IndicadorDistrito => Boolean(indicator && isFiniteNumber(indicator.valor))) ?? null;
}

function sumDistrictIndicatorValues(indicadores: IndicadorDistrito[], ids: readonly string[]) {
  let total = 0;
  let found = false;

  for (const id of ids) {
    const value = getDistrictIndicator(indicadores, id)?.valor ?? null;
    if (isFiniteNumber(value)) {
      total += value;
      found = true;
    }
  }

  return found ? total : null;
}

function buildSelectedIndicatorBreakdownItems(indicadores: IndicadorDistrito[], ids: readonly string[]): MetricBreakdownItem[] {
  return ids.map((id) => {
    const indicator = getDistrictIndicator(indicadores, id);
    if (!indicator || !isFiniteNumber(indicator.valor)) {
      return null;
    }

    return {
      label: indicator.label,
      value: formatIndicadorValue(indicator.id, indicator.valor),
      detail: isFiniteNumber(indicator.media_ciudad) ? `Media Madrid: ${formatIndicadorValue(indicator.id, indicator.media_ciudad)}` : "Sin media Madrid",
    };
  })
    .filter((item): item is Omit<MetricBreakdownItem, "rank"> => item !== null)
    .map((item, index) => ({
      rank: index + 1,
      ...item,
    }));
}

function buildDistrictIndicatorMetric({
  scopeId,
  metricId,
  label,
  summary,
  emptySummary,
  districtName,
  indicators,
  breakdownIds,
  headlineIds,
  aggregateHeadline = false,
}: {
  scopeId: string;
  metricId: string;
  label: string;
  summary: string;
  emptySummary: string;
  districtName: string;
  indicators: IndicadorDistrito[];
  breakdownIds: readonly string[];
  headlineIds?: readonly string[];
  aggregateHeadline?: boolean;
}): MetricDefinition {
  const breakdownItems = buildSelectedIndicatorBreakdownItems(indicators, breakdownIds);
  const headlineValueIds = headlineIds ?? breakdownIds;
  const headlineIndicator = aggregateHeadline ? null : pickFirstDistrictIndicator(indicators, headlineValueIds);
  const aggregateValue = aggregateHeadline ? sumDistrictIndicatorValues(indicators, headlineValueIds) : null;

  return {
    id: `${scopeId}:${metricId}`,
    label,
    value: aggregateHeadline
      ? formatInteger(aggregateValue)
      : headlineIndicator && isFiniteNumber(headlineIndicator.valor)
        ? formatIndicadorValue(headlineIndicator.id, headlineIndicator.valor)
        : "Sin datos",
    summary: breakdownItems.length > 0 ? summary : emptySummary,
    calculation: "Usamos la última lectura distrital disponible del Panel de Indicadores del Ayuntamiento de Madrid y la contrastamos con la media de la ciudad cuando esa referencia existe.",
    breakdownTitle: `Detalle distrital · ${districtName || "Distrito"}`,
    breakdownItems,
    breakdownEmptyText: `Sin indicadores distritales disponibles para ${label.toLowerCase()}.`,
  };
}

function formatIndicadorValue(id: string, value: number): string {
  if (id === "tasa_paro") return `${value.toFixed(1)}%`;
  if (id === "indice_dependencia" || id === "proporcion_migrantes") return `${(value * 100).toFixed(1)}%`;
  if (id === "valor_catastral") return `${Math.round(value).toLocaleString("es-ES")} €`;
  if (id === "densidad_distrito") return formatDensity(value * 100);
  if (id === "zonas_verdes_por_10k") return `${new Intl.NumberFormat("es-ES", { maximumFractionDigits: 1 }).format(value)} ha`;
  if (id === "edad_media_distrito") return formatAge(value);
  if (
    id === "locales_abiertos"
    || id === "locales_cerrados"
    || id === "habitantes_distrito"
    || id === "mercados_municipales"
    || id === "bibliotecas_municipales"
    || id === "centros_culturales_distrito"
    || id === "centros_deportivos_municipales"
    || id === "instalaciones_deportivas_basicas"
    || id === "centros_municipales_mayores"
    || id === "apartamentos_municipales_mayores"
    || id === "socios_centros_mayores"
  ) {
    return formatInteger(value);
  }
  return formatCompact(value);
}

function buildDistrictIndicatorComparisonBreakdownItems(indicator: IndicadorDistrito | null, districtName: string): MetricBreakdownItem[] {
  if (!indicator || !isFiniteNumber(indicator.valor)) {
    return [];
  }

  return [
    {
      rank: 1,
      label: "Tu distrito",
      value: formatIndicadorValue(indicator.id, indicator.valor),
      detail: districtName || "Sin distrito",
    },
    {
      rank: 2,
      label: "Media Madrid",
      value: isFiniteNumber(indicator.media_ciudad) ? formatIndicadorValue(indicator.id, indicator.media_ciudad) : "Sin media",
      detail: "Promedio de distritos",
    },
  ];
}

function buildDistrictUnemploymentMetric({
  scopeId,
  districtName,
  indicators,
}: {
  scopeId: string;
  districtName: string;
  indicators: IndicadorDistrito[];
}): MetricDefinition {
  const indicator = getDistrictIndicator(indicators, "tasa_paro");
  const districtValue = indicator?.valor ?? null;
  const cityValue = indicator?.media_ciudad ?? null;
  const comparison = isFiniteNumber(districtValue) && isFiniteNumber(cityValue)
    ? districtValue > cityValue
      ? `, por encima de la media Madrid (${formatIndicadorValue("tasa_paro", cityValue)})`
      : districtValue < cityValue
        ? `, por debajo de la media Madrid (${formatIndicadorValue("tasa_paro", cityValue)})`
        : `, en línea con la media Madrid (${formatIndicadorValue("tasa_paro", cityValue)})`
    : "";

  return {
    id: `${scopeId}:district-unemployment`,
    label: "Tasa de paro",
    value: isFiniteNumber(districtValue) ? formatIndicadorValue("tasa_paro", districtValue) : "Sin datos",
    summary: isFiniteNumber(districtValue)
      ? `${districtName || "El distrito"} marca ${formatIndicadorValue("tasa_paro", districtValue)} de paro registrado${comparison}.`
      : "No hay dato distrital reciente de tasa de paro para este entorno.",
    calculation: "Usamos la última tasa de paro distrital disponible en el Panel de Indicadores del Ayuntamiento de Madrid y la contrastamos con la media de distritos de la ciudad.",
    breakdownTitle: "Comparación rápida",
    breakdownItems: buildDistrictIndicatorComparisonBreakdownItems(indicator, districtName),
    breakdownEmptyText: "Sin lectura distrital de paro disponible.",
  };
}

function buildDistrictDependencyMetric({
  scopeId,
  districtName,
  indicators,
}: {
  scopeId: string;
  districtName: string;
  indicators: IndicadorDistrito[];
}): MetricDefinition {
  const indicator = getDistrictIndicator(indicators, "indice_dependencia");
  const districtValue = indicator?.valor ?? null;
  const cityValue = indicator?.media_ciudad ?? null;
  const comparison = isFiniteNumber(districtValue) && isFiniteNumber(cityValue)
    ? districtValue > cityValue
      ? `, por encima de la media Madrid (${formatIndicadorValue("indice_dependencia", cityValue)})`
      : districtValue < cityValue
        ? `, por debajo de la media Madrid (${formatIndicadorValue("indice_dependencia", cityValue)})`
        : `, en línea con la media Madrid (${formatIndicadorValue("indice_dependencia", cityValue)})`
    : "";

  return {
    id: `${scopeId}:district-dependency`,
    label: "Índice de dependencia",
    value: isFiniteNumber(districtValue) ? formatIndicadorValue("indice_dependencia", districtValue) : "Sin datos",
    summary: isFiniteNumber(districtValue)
      ? `${districtName || "El distrito"} marca ${formatIndicadorValue("indice_dependencia", districtValue)} de dependencia${comparison}. Resume la carga demográfica de menores y mayores sobre la población en edad activa del distrito.`
      : "No hay dato distrital reciente de índice de dependencia para este entorno.",
    calculation: "Usamos la última lectura distrital del índice de dependencia en el Panel de Indicadores del Ayuntamiento de Madrid y la comparamos con la media de la ciudad.",
    breakdownTitle: "Comparación rápida",
    breakdownItems: buildDistrictIndicatorComparisonBreakdownItems(indicator, districtName),
    breakdownEmptyText: "Sin lectura distrital de dependencia disponible.",
  };
}

function buildRankBreakdownItems({
  cityRank,
  cityTotal,
  districtRank,
  districtTotal,
  barrioRank,
  barrioTotal,
  districtName,
  barrioName,
}: {
  cityRank: number | null;
  cityTotal: number | null;
  districtRank: number | null;
  districtTotal: number | null;
  barrioRank: number | null;
  barrioTotal: number | null;
  districtName: string;
  barrioName: string;
}): MetricBreakdownItem[] {
  const scopes = {
    city: {
      label: "Madrid",
      rank: cityRank,
      total: cityTotal,
      name: "Madrid",
    },
    district: {
      label: "Distrito",
      rank: districtRank,
      total: districtTotal,
      name: districtName || "Distrito actual",
    },
    barrio: {
      label: "Barrio",
      rank: barrioRank,
      total: barrioTotal,
      name: barrioName || "Barrio actual",
    },
  } satisfies Record<"city" | "district" | "barrio", { label: string; rank: number | null; total: number | null; name: string }>;

  return (["city", "district", "barrio"] as const).map((scope, index) => {
    const row = scopes[scope];
    return {
      rank: index + 1,
      label: row.label,
      value: formatRank(row.rank, row.total),
      detail: `${row.name} · ${formatTopBand(row.rank, row.total)}`,
    };
  });
}

function buildMetroBreakdownItems({
  distance,
  station500,
  station1000,
  nearestName,
  nearestStationName,
  stationNames500,
  stationNames1000,
  distanceBenchmark,
  station500Benchmark,
  station1000Benchmark,
}: {
  distance: number | null;
  station500: number | null;
  station1000: number | null;
  nearestName: string;
  nearestStationName: string;
  stationNames500: string[];
  stationNames1000: string[];
  distanceBenchmark: OpportunityFieldInsight | null | undefined;
  station500Benchmark: OpportunityFieldInsight | null | undefined;
  station1000Benchmark: OpportunityFieldInsight | null | undefined;
}): MetricBreakdownItem[] {
  return [
    {
      rank: 1,
      label: "Paradas a 500 m",
      value: formatCompact(station500),
      detail: buildMetroAccessDetail(station500Benchmark?.cityMedian ?? null, stationNames500, formatCompact),
      asideTitle: "Paradas oficiales a 500 m",
      asideItems: stationNames500,
      asideEmptyText: "No hay paradas oficiales de metro identificadas dentro de 500 m.",
    },
    {
      rank: 2,
      label: "Paradas a 1 km",
      value: formatCompact(station1000),
      detail: buildMetroAccessDetail(station1000Benchmark?.cityMedian ?? null, stationNames1000, formatCompact),
      asideTitle: "Paradas oficiales a 1 km",
      asideItems: stationNames1000,
      asideEmptyText: "No hay paradas oficiales de metro identificadas dentro de 1 km.",
    },
    {
      rank: 3,
      label: "Parada más cercana",
      value: formatDistance(distance),
      detail: nearestStationName
        ? `${nearestStationName} · ${formatMetroPercentile(distanceBenchmark?.cityPercentile ?? null)}`
        : nearestName
          ? `${nearestName} · ${formatMetroPercentile(distanceBenchmark?.cityPercentile ?? null)}`
          : formatMetroPercentile(distanceBenchmark?.cityPercentile ?? null),
      asideTitle: "Parada oficial más cercana",
      asideItems: nearestStationName ? [nearestStationName] : [],
      asideEmptyText: "No hay una parada oficial legible disponible para este punto.",
    },
  ];
}

function buildCompetitionBreakdownItems({
  localCount,
  sameCategoryShare,
  bestActivityLabel,
  localCountBenchmark,
  sameCategoryBenchmark,
}: {
  localCount: number | null;
  sameCategoryShare: number | null;
  bestActivityLabel: string;
  localCountBenchmark: OpportunityFieldInsight | null | undefined;
  sameCategoryBenchmark: OpportunityFieldInsight | null | undefined;
}): MetricBreakdownItem[] {
  const sameCategoryMedian = buildMedianDetail(sameCategoryBenchmark?.cityMedian ?? null, formatShare);
  const sameCategoryDetail = bestActivityLabel
    ? `${bestActivityLabel} · ${sameCategoryMedian}`
    : sameCategoryMedian;

  return [
    {
      rank: 1,
      label: "Locales activos",
      value: formatCompact(localCount),
      detail: buildMedianDetail(localCountBenchmark?.cityMedian ?? null, formatCompact),
    },
    {
      rank: 2,
      label: "Cuota misma categoría",
      value: formatShare(sameCategoryShare),
      detail: sameCategoryDetail,
    },
    {
      rank: 3,
      label: "Categoría usada",
      value: bestActivityLabel ? "Top ranking" : "Sin ranking",
      detail: bestActivityLabel
        ? `${bestActivityLabel} · familia amplia usada para calcular la cuota anterior.`
        : "Sin ranking suficiente para fijar una categoría de referencia.",
    },
  ];
}

function buildOperationBreakdownItems(point: OpportunityPoint, points: OpportunityPoint[]): MetricBreakdownItem[] {
  return buildListingScopeRows(point, points).map((scope, index) => {
    const total = scope.points.length;
    const sameOperation = scope.points.filter((candidate) => candidate.operation === point.operation).length;
    const share = total > 0 ? sameOperation / total : null;

    return {
      rank: index + 1,
      label: scope.label,
      value: formatOperationShare(point.operation, share),
      detail: `${scope.detailName} · ${sameOperation} de ${total} anuncios`,
    };
  });
}

function buildListingValueBreakdownItems({
  point,
  points,
  field,
  formatValue,
  labelSuffix,
  percentileLabel,
}: {
  point: OpportunityPoint;
  points: OpportunityPoint[];
  field: "price_eur" | "area_m2";
  formatValue: (value: number | null) => string;
  labelSuffix: string;
  percentileLabel: string;
}): MetricBreakdownItem[] {
  const currentValue = point[field];

  return buildListingScopeRows(point, points).map((scope, index) => {
    const comparables = scope.points.filter((candidate) => candidate.operation === point.operation);
    const values = comparables.map((candidate) => candidate[field]).filter(isFiniteNumber).map((value) => Number(value));
    const percentile = computeDistributionPercentile(values, currentValue);

    return {
      rank: index + 1,
      label: scope.label,
      value: formatValue(median(values)),
      detail: `${scope.detailName} · ${comparables.length} ${labelSuffix}${formatListingPercentileDetail(percentile, percentileLabel)}`,
    };
  });
}

function buildListingScopeRows(point: OpportunityPoint, points: OpportunityPoint[]) {
  const barrioScopeKey = buildBarrioScopeKey(point);

  return [
    {
      label: "Madrid",
      detailName: "Madrid",
      points,
    },
    {
      label: "Distrito",
      detailName: point.district_name || "Distrito actual",
      points: points.filter((candidate) => candidate.district_code === point.district_code),
    },
    {
      label: "Barrio",
      detailName: point.barrio_name || "Barrio actual",
      points: barrioScopeKey
        ? points.filter((candidate) => buildBarrioScopeKey(candidate) === barrioScopeKey)
        : [],
    },
  ];
}

function buildBarrioScopeKey(location: { district_code: string; barrio_code: string }) {
  const districtCode = location.district_code || "";
  const barrioCode = location.barrio_code || "";
  if (!districtCode || !barrioCode) {
    return "";
  }
  return `${districtCode}:${barrioCode}`;
}

function buildIncomeSummary({
  subject,
  granularityUsed,
  referenceYear,
  outlierAdjusted,
}: {
  subject: string;
  granularityUsed: string;
  referenceYear: number | null;
  outlierAdjusted: boolean;
}) {
  const parts = [`Estimación de ingresos ${subject}.`];

  if (outlierAdjusted) {
    parts.push("El dato fino de la zona salía incoherente y se ha sustituido por la referencia del distrito.");
  } else if (granularityUsed === "district") {
    parts.push("No había dato fino fiable para la zona y se usa la referencia del distrito.");
  } else if (granularityUsed === "city") {
    parts.push("Faltaba detalle local y se usa la referencia general de Madrid.");
  } else {
    parts.push("Usa el dato de la zona pequeña del censo donde cae el local.");
  }

  if (isFiniteNumber(referenceYear)) {
    parts.push(`Base de renta ${Math.round(referenceYear)}.`);
  }

  return parts.join(" ");
}

function buildIncomeCalculation({ granularityUsed, outlierAdjusted }: { granularityUsed: string; outlierAdjusted: boolean }) {
  if (outlierAdjusted) {
    return "Partimos del dato anual de ingresos de la zona pequeña del censo. Si ese dato sale incoherente frente a su distrito, lo descartamos y usamos la referencia distrital para no arrastrar outliers al mapa.";
  }
  if (granularityUsed === "district") {
    return "Partimos del dato anual de ingresos de la zona pequeña del censo. Si falta o no es fiable, usamos la referencia del distrito.";
  }
  if (granularityUsed === "city") {
    return "Partimos del dato anual de ingresos de la zona pequeña del censo. Si faltan referencias local y distrital, usamos la referencia general de Madrid.";
  }
  return "Usamos el dato anual de ingresos de la zona pequeña del censo donde cae el local. Si esa lectura faltara, el pipeline conserva el mejor fallback territorial disponible.";
}

function buildOpportunityTierSummary(value: string) {
  if (value === "Alta") {
    return "La sección cae dentro del tramo más defensivo del mapa de oportunidades. Sigue exigiendo validar local, renta y competencia, pero parte de una lectura comparativamente favorable en Madrid.";
  }
  if (value === "Solida") {
    return "La sección está en un tramo favorable, aunque ya no tan selecto como Alta. Suele combinar una base razonable de contexto con riesgo por debajo de buena parte de la ciudad.";
  }
  if (value === "Intermedia") {
    return "La sección está en una zona media del mapa. No es una mala lectura por sí sola, pero conviene apoyarse más en competencia, metro, demografía y encaje de actividad.";
  }
  if (value === "Fragil") {
    return "La sección cae en el tramo más exigente del mapa. No invalida una apertura, pero sí exige una tesis más fuerte sobre producto, precio, ubicación exacta y demanda.";
  }
  return "No hay suficiente señal para ubicar esta sección en un tramo cualitativo de oportunidad.";
}

function buildOpportunityTierBreakdownItems(activeTier: string): MetricBreakdownItem[] {
  return [
    {
      rank: 1,
      label: "Alta",
      value: "P0-P20",
      detail: activeTier === "Alta" ? "Tu sección cae aquí" : "Tramo más defensivo",
    },
    {
      rank: 2,
      label: "Solida",
      value: "P21-P45",
      detail: activeTier === "Solida" ? "Tu sección cae aquí" : "Lectura favorable",
    },
    {
      rank: 3,
      label: "Intermedia",
      value: "P46-P70",
      detail: activeTier === "Intermedia" ? "Tu sección cae aquí" : "Lectura mixta",
    },
    {
      rank: 4,
      label: "Fragil",
      value: "P71-P100",
      detail: activeTier === "Fragil" ? "Tu sección cae aquí" : "Tramo más exigente",
    },
  ];
}

function buildMedianDetail(value: number | null, formatValue: (value: number | null) => string) {
  if (!isFiniteNumber(value)) {
    return "Sin mediana Madrid";
  }
  return `Mediana Madrid: ${formatValue(value)}`;
}

function computeDistributionPercentile(values: number[], currentValue: number | null) {
  if (!isFiniteNumber(currentValue) || values.length === 0) {
    return null;
  }

  const lessOrEqual = values.filter((value) => value <= currentValue).length;
  return lessOrEqual / values.length;
}

function formatListingPercentileDetail(value: number | null, label: string) {
  if (!isFiniteNumber(value)) {
    return "";
  }
  return ` · tu local P${Math.round(value * 100)} por ${label}`;
}

function formatOperationShare(operation: string, share: number | null) {
  if (!operation) {
    return "Sin dato";
  }
  if (!isFiniteNumber(share)) {
    return operation;
  }
  return `${Math.round(share * 100)}% ${operation}`;
}

function formatCityPercentileDetail(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin percentil Madrid";
  }
  return `Tu zona: P${Math.round(value * 100)} frente a Madrid`;
}

function formatMetroPercentile(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin comparación Madrid";
  }
  const percentile = Math.round(value * 100);
  if (percentile >= 60) {
    return `Mejor que el ${percentile}% de Madrid por cercanía al metro`;
  }
  if (percentile >= 45) {
    return "Muy cerca de la mediana Madrid por cercanía al metro";
  }
  if (percentile >= 25) {
    return `Por debajo de la media Madrid: solo mejora al ${percentile}%`;
  }
  return `Claramente por debajo de la media Madrid: solo mejora al ${percentile}%`;
}

function buildMetroPercentileNarrative(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "";
  }
  const percentile = Math.round(value * 100);
  if (percentile >= 60) {
    return `Frente a Madrid, la cercanía al metro es mejor que en el ${percentile}% de las secciones.`;
  }
  if (percentile >= 45) {
    return "Frente a Madrid, la cercanía al metro está muy alineada con la mediana de la ciudad.";
  }
  return `Frente a Madrid, la cercanía al metro queda por debajo de la media y solo mejora al ${percentile}% de la ciudad.`;
}

function formatTopBand(rank: number | null, total: number | null) {
  if (!isFiniteNumber(rank) || !isFiniteNumber(total) || total <= 0) {
    return "Sin tramo";
  }
  return `Top ${Math.max(1, Math.round((rank / total) * 100))}%`;
}

function buildRankingHeadline(
  cityRank: number | null,
  cityTotal: number | null,
  districtRank: number | null,
  districtTotal: number | null,
  barrioRank: number | null,
  barrioTotal: number | null,
) {
  const candidates = [
    { label: "Madrid", rank: cityRank, total: cityTotal },
    { label: "distrito", rank: districtRank, total: districtTotal },
    { label: "barrio", rank: barrioRank, total: barrioTotal },
  ];
  const primary = candidates.find((candidate) => isFiniteNumber(candidate.rank) && isFiniteNumber(candidate.total) && candidate.total > 0);
  if (!primary) {
    return "Sin datos";
  }
  return `${formatTopBand(primary.rank, primary.total)} ${primary.label}`;
}

function buildMetricWhyUseful(metric: MetricDefinition) {
  if (metric.id.includes(":survival:")) {
    return "Te sirve para comparar de un vistazo qué entornos aguantan mejor una apertura parecida en el horizonte que estás mirando.";
  }
  if (metric.id.endsWith(":operation-chip")) {
    return "Te ayuda a entender si el entorno se está moviendo más en compra o en alquiler, algo útil para leer liquidez, perfil de demanda y tipo de mercado disponible.";
  }
  if (metric.id.endsWith(":price-chip") || metric.id.endsWith(":area-chip")) {
    return "Te da una referencia rápida de si este anuncio entra pequeño, grande, barato o caro frente a los comparables inmediatos de la misma operación.";
  }
  if (metric.id.endsWith(":opportunity-tier")) {
    return "Condensa el percentil de riesgo en un lenguaje más rápido de leer, útil para filtrar primero y entrar después al detalle de ranking, competencia o demografía.";
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Te permite entender si estás en una zona estructuralmente más delicada o más favorable que la media de Madrid sin tener que interpretar el score bruto del modelo.";
  }
  if (metric.id.endsWith(":ranking")) {
    return "Te ayuda a priorizar ubicaciones sin perder contexto: ves si la buena lectura se sostiene en Madrid, dentro del distrito y dentro del barrio.";
  }
  if (metric.id.endsWith(":activity-ranking-method")) {
    return "Te abre la caja negra del ranking: explica qué parte viene del modelo de supervivencia, qué parte es ajuste por categoría y cómo se resuelve el orden final de la lista.";
  }
  if (metric.id.endsWith(":income")) {
    return "Aporta contexto de poder adquisitivo y ayuda a valorar si el entorno puede sostener conceptos de ticket medio más alto o más sensible a precio.";
  }
  if (metric.id.endsWith(":metro")) {
    return "Es útil para estimar accesibilidad y paso potencial, especialmente en actividades que dependen de conveniencia o tráfico peatonal.";
  }
  if (metric.id.endsWith(":facilities")) {
    return "Resume la dotación pública cercana sin mezclar radios acumulados, así que te deja ver mejor qué queda realmente pegado al punto y qué exige un paseo algo más largo.";
  }
  if (metric.id.endsWith(":residential-base")) {
    return "Sirve para leer primero cuánta gente vive alrededor y, al abrir el detalle, distinguir si esa base está muy concentrada o más extendida.";
  }
  if (metric.id.endsWith(":age")) {
    return "Aporta una lectura sintética del ciclo de vida dominante del entorno y complementa mejor que un único porcentaje joven o sénior.";
  }
  if (metric.id.endsWith(":competition") || metric.id.endsWith(":active-categories")) {
    return "Te orienta sobre cuánta oferta comercial ya existe y si el entorno está más saturado o más diverso.";
  }
  if (metric.id.endsWith(":turnover-12m")) {
    return "Sirve para detectar si el tejido comercial es estable o si cambia mucho de manos y conceptos en poco tiempo.";
  }
  if (metric.id.endsWith(":foreign-share") || metric.id.endsWith(":young-share") || metric.id.endsWith(":senior-share")) {
    return "Aporta una lectura rápida del perfil demográfico dominante y puede ayudarte a valorar afinidad con ciertos formatos o surtidos.";
  }
  if (metric.id.endsWith(":district-unemployment") || metric.id.endsWith(":district-dependency")) {
    return "Añade dos señales de distrito bastante estables que completan la lectura demográfica del punto sin volver a abrir un bloque entero de contexto distrital.";
  }
  if (metric.id.endsWith(":avisos")) {
    return "Funciona como señal indirecta de fricción vecinal o presión urbana reciente, útil para actividades más sensibles a convivencia, ruido o intensidad de uso.";
  }
  return "Te da una señal adicional para interpretar el entorno con algo más de contexto que el anuncio puro.";
}

function buildMetricExample(metric: MetricDefinition) {
  if (metric.id.endsWith(":operation-chip")) {
    return "Ejemplo: 68% alquiler en el barrio significa que, dentro de los anuncios capturados en ese ámbito, algo más de dos tercios están saliendo al mercado en alquiler y no en venta.";
  }
  if (metric.id.endsWith(":price-chip")) {
    return "Ejemplo: si la mediana del distrito es 320.000 € y tu local cae en P75, significa que está por encima de tres cuartas partes de los comparables de venta del distrito.";
  }
  if (metric.id.endsWith(":area-chip")) {
    return "Ejemplo: si la mediana del barrio es 95 m² y tu local cae en P30, la lectura es que el anuncio es más pequeño que la mayoría de comparables del barrio.";
  }
  if (metric.id.endsWith(":opportunity-tier")) {
    return "Ejemplo: Intermedia no significa que el punto sea malo, sino que cae en la banda central del mapa y necesita más contraste con competencia, ranking de actividades y resto de contexto antes de priorizarlo.";
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Ejemplo: un P85 implica que esta sección tiene más riesgo histórico que aproximadamente el 85% de Madrid y solo mejora frente al 15% restante.";
  }
  if (metric.id.endsWith(":ranking")) {
    return "Ejemplo: Top 5% Madrid con #3 de 41 en distrito y #1 de 8 en barrio significa que la buena lectura no depende solo de un ámbito, sino que se sostiene también cerca del local.";
  }
  if (metric.id.endsWith(":activity-ranking-method")) {
    return "Ejemplo: dos categorías pueden tener una supervivencia parecida, pero si una sale mejor en el scorer Cox y además encaja mejor frente a su propio histórico, subirá puestos aunque la otra tenga más locales observados.";
  }
  if (metric.id.endsWith(":residential-base")) {
    return "Ejemplo: 1,3 mil residentes en la tarjeta y 27.211 hab/km² en el detalle pueden convivir si la sección apenas ocupa unas pocas hectáreas; no es una contradicción, sino una zona pequeña y compacta.";
  }
  if (metric.id.endsWith(":age")) {
    return "Ejemplo: una edad media de 44 años no implica ausencia de jóvenes, sino que el equilibrio general del entorno es más maduro que otro barrio con media 36.";
  }
  if (metric.id.endsWith(":turnover-12m")) {
    return "Ejemplo: 0% significa que en el último año observado no vemos movimientos registrados en esta zona pequeña; 0,6% ya indica algo de rotación, aunque siga siendo baja.";
  }
  if (metric.id.endsWith(":senior-share")) {
    return "Ejemplo: un 24,5% significa que aproximadamente 1 de cada 4 residentes del entorno cae ya en el tramo de 65 años o más.";
  }
  if (metric.id.endsWith(":facilities")) {
    return "Ejemplo: 3 total con 0-200 m: 0, 200-500 m: 1 y 500 m-1 km: 2 significa exactamente un equipamiento a distancia caminable corta y dos más algo más lejos; no son conteos duplicados.";
  }
  if (metric.id.endsWith(":avisos")) {
    return "Ejemplo: 2,40 / 1.000 hab significa que el año anterior hubo 2,4 avisos por cada mil residentes de ese ámbito.";
  }
  if (metric.id.endsWith(":competition")) {
    return "Ejemplo: 120 locales no significa 120 competidores directos. Y una cuota misma categoría del 18% significa que el 18% del stock cae en la misma familia amplia de negocio que hoy lidera el ranking, no en el mismo epígrafe exacto.";
  }
  if (metric.id.endsWith(":district-unemployment")) {
    return "Ejemplo: 7,1% frente a 6,3% en Madrid indica un mercado laboral distrital algo más presionado que la media de la ciudad.";
  }
  if (metric.id.endsWith(":district-dependency")) {
    return "Ejemplo: 58% de dependencia significa que, a escala distrital, la carga de menores y mayores sobre la población en edad activa es relativamente alta.";
  }
  return null;
}

function median(values: number[]) {
  if (values.length === 0) {
    return null;
  }
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) {
    return sorted[middle];
  }
  return (sorted[middle - 1] + sorted[middle]) / 2;
}