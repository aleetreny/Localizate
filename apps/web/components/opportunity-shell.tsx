"use client";

import { useEffect, useMemo, useState } from "react";

import { OpportunityMap } from "@/components/opportunity-map";
import { ViewTabs } from "@/components/view-tabs";
import { formatHorizonShortLabel, isFiniteNumber, type Horizon } from "@/lib/horizon";
import { FALLBACK_OPPORTUNITY_ARTIFACTS, loadOpportunityArtifactsFromPublic } from "@/lib/public-data";
import type { OpportunityActivity, OpportunityArtifacts, OpportunityManualSelection, OpportunityPoint, OpportunitySection } from "@/lib/types";

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
};

const IS_PRODUCTION = process.env.NODE_ENV === "production";
const DEV_ARTIFACT_REVALIDATE_MS = 15000;

export function OpportunityShell({ initialArtifacts }: OpportunityShellProps) {
  const [artifacts, setArtifacts] = useState(initialArtifacts ?? FALLBACK_OPPORTUNITY_ARTIFACTS);
  const [isLoadingArtifacts, setIsLoadingArtifacts] = useState(!initialArtifacts);
  const [operationFilter, setOperationFilter] = useState<OperationFilter>("all");
  const [horizon, setHorizon] = useState<Horizon>("24m");
  const [selectedListingId, setSelectedListingId] = useState<string | null>((initialArtifacts ?? FALLBACK_OPPORTUNITY_ARTIFACTS).points[0]?.listing_id ?? null);
  const [manualSelection, setManualSelection] = useState<OpportunityManualSelection | null>(null);
  const [activeMetricId, setActiveMetricId] = useState<string | null>(null);
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

  const detailMetrics = useMemo(() => {
    if (manualSelection) {
      const section = manualSelection.section;
      return [
        ...buildSectionPrimaryMetrics(section, horizon),
        ...buildContextMetrics({
          scopeId: `section:${section.section_key}`,
          bestActivityLabel: section.best_activity_label,
          bestActivityRisk: section.best_activity_risk,
          bestActivitySurvival24m: section.best_activity_survival_24m,
          uniqueActivityCategories: section.section_unique_activity_category_count_start,
          turnoverRate12m: section.section_turnover_rate_12m_start,
          totalPopulation: section.total_population_start,
          shareForeign: section.share_foreign_start,
          shareYoung: section.share_age_15_29_start,
          avisosBarrio: section.avisos_barrio_per_1000_prev_year,
          avisosDistrict: section.avisos_district_per_1000_prev_year
        })
      ];
    }

    if (!selectedListing) {
      return [];
    }

    return [
      ...buildPointPrimaryMetrics(selectedListing, horizon),
      ...buildContextMetrics({
        scopeId: `listing:${selectedListing.listing_id}`,
        bestActivityLabel: selectedListing.best_activity_label,
        bestActivityRisk: selectedListing.best_activity_risk,
        bestActivitySurvival24m: selectedListing.best_activity_survival_24m,
        uniqueActivityCategories: selectedListing.section_unique_activity_category_count_start,
        turnoverRate12m: selectedListing.section_turnover_rate_12m_start,
        totalPopulation: selectedListing.total_population_start,
        shareForeign: selectedListing.share_foreign_start,
        shareYoung: selectedListing.share_age_15_29_start,
        avisosBarrio: selectedListing.avisos_barrio_per_1000_prev_year,
        avisosDistrict: selectedListing.avisos_district_per_1000_prev_year
      })
    ];
  }, [horizon, manualSelection, selectedListing]);

  const activeMetric = detailMetrics.find((metric) => metric.id === activeMetricId) ?? null;

  useEffect(() => {
    if (!activeMetricId) {
      return;
    }

    if (detailMetrics.some((metric) => metric.id === activeMetricId)) {
      return;
    }

    setActiveMetricId(null);
  }, [activeMetricId, detailMetrics]);

  const activeStats = useMemo(() => {
    const survivalValues = filteredPoints.map((point) => getPointSurvival(point, horizon)).filter(isFiniteNumber);
    const priceValues = filteredPoints.map((point) => point.price_per_m2_eur).filter(isFiniteNumber);
    return {
      selected: filteredPoints.length,
      districts: new Set(filteredPoints.map((point) => point.district_code).filter(Boolean)).size,
      barrios: new Set(filteredPoints.map((point) => point.barrio_code).filter(Boolean)).size,
      medianSurvival: median(survivalValues),
      medianPricePerSquareMeter: median(priceValues)
    };
  }, [filteredPoints, horizon]);

  const activeActivities = manualSelection?.section.top_activities ?? selectedListing?.top_activities ?? [];

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
            Operacion
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
            : "Haz click en un local para abrir su ficha. Si haces click en cualquier otro punto del mapa, la lectura se resuelve sobre la seccion censal que contiene ese punto para comparar riesgo, competencia, renta, metro y avisos en una misma unidad."}
        </p>

        <section className="detail-card">
          {manualSelection ? (
            <ManualPointDetail
              activeMetricId={activeMetricId}
              metrics={detailMetrics}
              onClear={() => setManualSelection(null)}
              onMetricSelect={setActiveMetricId}
              section={manualSelection.section}
              selection={manualSelection}
            />
          ) : selectedListing ? (
            <ListingDetail activeMetricId={activeMetricId} metrics={detailMetrics} onMetricSelect={setActiveMetricId} point={selectedListing} />
          ) : (
            <div className="detail-empty">
              <div className="eyebrow">Ficha activa</div>
              <h3>{isLoadingArtifacts ? "Cargando oportunidades" : "Sin seleccion"}</h3>
              <p>
                {isLoadingArtifacts
                  ? "La vista está esperando el artefacto de oportunidades y la geometría de secciones para habilitar el detalle."
                  : "No hay locales visibles con el filtro actual. Cambia la operacion o haz click en el mapa para explorar una seccion."}
              </p>
            </div>
          )}
        </section>

        <section className="info-card">
          <div className="eyebrow">Actividades recomendadas</div>
          <h3>{manualSelection ? "Ranking por menor riesgo historico de la seccion" : selectedListing ? "Ranking por menor riesgo historico del entorno" : "Selecciona un punto"}</h3>
          <p className="empty-note">El orden usa un riesgo historico ajustado por muestra para cada actividad.</p>
          {activeActivities.length > 0 ? <ActivityList activities={activeActivities} /> : <p className="empty-note">Sin ranking historico suficiente para este entorno.</p>}
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
  metrics,
  activeMetricId,
  onMetricSelect
}: {
  point: OpportunityPoint;
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
        <span className="chip">{point.operation}</span>
        <span className="chip">{formatCurrency(point.price_eur)}</span>
        <span className="chip">{formatArea(point.area_m2)}</span>
        <span className="chip">{point.opportunity_tier}</span>
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
  metrics,
  onMetricSelect,
  section,
  selection,
  onClear
}: {
  activeMetricId: string | null;
  metrics: MetricDefinition[];
  onMetricSelect: (metricId: string | null) => void;
  section: OpportunitySection;
  selection: OpportunityManualSelection;
  onClear: () => void;
}) {
  return (
    <>
      <div className="detail-header-row">
        <div>
          <div className="eyebrow">Punto libre</div>
          <h2>{section.barrio_name}, {section.district_name}</h2>
        </div>
        <button className="ghost-button" onClick={onClear} type="button">
          Limpiar punto
        </button>
      </div>
      <p className="detail-location">Lat {selection.lat.toFixed(5)} · Lon {selection.lng.toFixed(5)} · seccion {section.section_key}</p>
      <p className="detail-subtle">El punto que marcas se interpreta con la seccion censal que lo contiene, no como una direccion inventada.</p>
      <div className="detail-meta">
        <span className="chip">{section.opportunity_tier}</span>
        <span className="chip">{formatRiskPercentile(section.risk_percentile)}</span>
        <span className="chip">Mejor actividad: {section.best_activity_label || "Sin ranking"}</span>
      </div>
      <MetricGrid activeMetricId={activeMetricId} metrics={metrics} onSelect={onMetricSelect} />
    </>
  );
}

function ActivityList({ activities }: { activities: OpportunityActivity[] }) {
  return (
    <div className="activity-list">
      {activities.map((activity) => (
        <article className="activity-card" key={`${activity.source_zone}:${activity.display_label}`}>
          <div className="activity-card-top">
            <span className="activity-rank">#{activity.rank}</span>
            <div className="activity-kpi">
              <span className="activity-kpi-label">Riesgo hist.</span>
              <span className="activity-value">{formatPercent(activity.activity_risk)}</span>
            </div>
          </div>
          <strong>{activity.display_label}</strong>
          <span className="activity-meta">{activity.web_supercategory} · {activity.web_category}</span>
          <span className="activity-meta">Supervivencia 24m {formatPercent(activity.survival_24m)}</span>
          <span className="activity-meta">Fuente {activity.source_zone} · {formatCompact(activity.n_locales)} locales</span>
        </article>
      ))}
    </div>
  );
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
  return (
    <div className={className}>
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
            <span className="detail-metric-hint">Qué es y cómo se calcula</span>
          </button>
        );
      })}
    </div>
  );
}

function MetricExplainer({ metric }: { metric: MetricDefinition | null }) {
  return (
    <div className="metric-explainer" data-empty={metric ? "false" : "true"}>
      <div className="eyebrow">Definición de métrica</div>
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
        <p className="metric-explainer-copy">Haz click en cualquier tarjeta para ver qué significa, por qué es útil y cómo la calcula el producto.</p>
      )}
    </div>
  );
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

function formatShare(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
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

function formatCompact(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return new Intl.NumberFormat("es-ES", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function formatRiskPercentile(value: number) {
  if (!Number.isFinite(value)) {
    return "Sin datos";
  }
  return `P${Math.round(value * 100)}`;
}

function formatRank(rank: number | null, total: number | null) {
  if (!isFiniteNumber(rank) || !isFiniteNumber(total) || total <= 0) {
    return "Sin datos";
  }
  return `#${rank} de ${total}`;
}

function buildBestActivitySummary(label: string, risk: number | null, survival24m: number | null) {
  if (!label) {
    return "Sin ranking historico suficiente para proponer una actividad.";
  }

  const parts = [label];
  if (isFiniteNumber(risk)) {
    parts.push(`riesgo historico ${formatPercent(risk)}`);
  }
  if (isFiniteNumber(survival24m)) {
    parts.push(`supervivencia 24m ${formatPercent(survival24m)}`);
  }
  return parts.join(" · ");
}

function buildPointPrimaryMetrics(point: OpportunityPoint, horizon: Horizon): MetricDefinition[] {
  const horizonLabel = formatHorizonShortLabel(horizon);
  return [
    {
      id: `listing:${point.listing_id}:survival:${horizon}`,
      label: `Supervivencia ${horizonLabel}`,
      value: formatPercent(getPointSurvival(point, horizon)),
      summary: `Es la probabilidad esperada de que un local comparable siga activo dentro de ${horizonLabel} en este entorno.`,
      calculation: "Partimos del score de riesgo del modelo para la seccion donde cae el local y lo transformamos a supervivencia esperada en ese horizonte."
    },
    {
      id: `listing:${point.listing_id}:risk-percentile`,
      label: "Percentil riesgo",
      value: formatRiskPercentile(point.risk_percentile),
      summary: "Ubica este entorno dentro de la distribucion de riesgo de Madrid. Cuanto mas alto, mas exigente es el entorno historico.",
      calculation: "Ordenamos todas las secciones por su score de riesgo. Un P80 significa que el riesgo de esta seccion queda por encima de aproximadamente el 80% de las secciones de la ciudad."
    },
    {
      id: `listing:${point.listing_id}:city-rank`,
      label: "Ranking Madrid",
      value: formatRank(point.city_rank, point.city_total_sections),
      summary: "Mide la posicion de esta seccion frente a todo Madrid cuando ordenamos por menor riesgo historico.",
      calculation: "Comparamos la seccion con el total de secciones candidatas y asignamos el puesto por score de riesgo ascendente. Cuanto mas cerca de #1, mejor."
    },
    {
      id: `listing:${point.listing_id}:district-rank`,
      label: "Ranking distrito",
      value: formatRank(point.district_rank, point.district_total_sections),
      summary: "Es la posicion relativa de la seccion dentro de su distrito.",
      calculation: "Aplicamos el mismo orden por menor riesgo, pero comparando solo contra secciones del mismo distrito."
    },
    {
      id: `listing:${point.listing_id}:income`,
      label: "Renta seccion",
      value: formatCurrency(point.renta_effective_eur),
      summary: "Aproxima la capacidad economica residencial del entorno inmediato.",
      calculation: "Usamos la renta anual efectiva mas reciente disponible para la seccion censal. Si la fuente puntual falla, el pipeline conserva el mejor fallback territorial disponible."
    },
    {
      id: `listing:${point.listing_id}:metro`,
      label: "Metro mas cercano",
      value: formatDistance(point.metro_distance_m_start),
      summary: "Resume la accesibilidad del local al transporte subterraneo.",
      calculation: "Medimos en metros la distancia en linea recta desde el local hasta el acceso de metro mas cercano."
    },
    {
      id: `listing:${point.listing_id}:density`,
      label: "Densidad poblacion",
      value: formatDensity(point.population_density_km2_start),
      summary: "Mide la intensidad residencial del entorno.",
      calculation: "Dividimos la poblacion total de la seccion entre su superficie para obtener habitantes por kilometro cuadrado."
    },
    {
      id: `listing:${point.listing_id}:competition`,
      label: "Competencia local",
      value: formatCompact(point.section_local_count_start),
      summary: "Cuenta cuantos locales activos compiten por la misma atencion en esa seccion.",
      calculation: "Tomamos el stock historico de locales activos observado en la seccion censal usada para puntuar el entorno."
    }
  ];
}

function buildSectionPrimaryMetrics(section: OpportunitySection, horizon: Horizon): MetricDefinition[] {
  const horizonLabel = formatHorizonShortLabel(horizon);
  return [
    {
      id: `section:${section.section_key}:survival:${horizon}`,
      label: `Supervivencia ${horizonLabel}`,
      value: formatPercent(getSectionSurvival(section, horizon)),
      summary: `Es la probabilidad esperada de que un local comparable siga activo dentro de ${horizonLabel} en esta seccion.`,
      calculation: "Partimos del score de riesgo agregado de la seccion y lo transformamos a supervivencia esperada para el horizonte seleccionado."
    },
    {
      id: `section:${section.section_key}:city-rank`,
      label: "Ranking Madrid",
      value: formatRank(section.city_rank, section.city_total_sections),
      summary: "Posicion de la seccion frente al total de Madrid por menor riesgo historico.",
      calculation: "Ordenamos todas las secciones candidatas por score de riesgo ascendente. Cuanto mas cerca de #1, mas favorable es la lectura."
    },
    {
      id: `section:${section.section_key}:district-rank`,
      label: "Ranking distrito",
      value: formatRank(section.district_rank, section.district_total_sections),
      summary: "Posicion relativa de la seccion dentro de su distrito.",
      calculation: "Comparamos solo con secciones del mismo distrito y ordenamos por menor riesgo historico."
    },
    {
      id: `section:${section.section_key}:barrio-rank`,
      label: "Ranking barrio",
      value: formatRank(section.barrio_rank, section.barrio_total_sections),
      summary: "Posicion relativa de la seccion dentro de su barrio.",
      calculation: "Comparamos la seccion con el resto de secciones del mismo barrio y ordenamos por score de riesgo ascendente."
    },
    {
      id: `section:${section.section_key}:income`,
      label: "Renta seccion",
      value: formatCurrency(section.renta_effective_eur),
      summary: "Aproxima la capacidad economica residencial de la seccion.",
      calculation: "Usamos la renta anual efectiva mas reciente disponible para la seccion censal; si falta, se conserva el mejor fallback territorial del pipeline."
    },
    {
      id: `section:${section.section_key}:metro`,
      label: "Metro centroide",
      value: formatDistance(section.metro_distance_m_start),
      summary: "Resume la accesibilidad media de la seccion al metro.",
      calculation: "Medimos en metros la distancia en linea recta desde el centroide de la seccion hasta el acceso de metro mas cercano."
    },
    {
      id: `section:${section.section_key}:density`,
      label: "Densidad poblacion",
      value: formatDensity(section.population_density_km2_start),
      summary: "Mide la intensidad residencial de la seccion.",
      calculation: "Dividimos la poblacion total de la seccion entre su superficie para obtener habitantes por kilometro cuadrado."
    },
    {
      id: `section:${section.section_key}:competition`,
      label: "Competencia local",
      value: formatCompact(section.section_local_count_start),
      summary: "Cuenta cuantos locales activos hay en la seccion.",
      calculation: "Tomamos el stock historico de locales activos observado para la propia seccion censal."
    }
  ];
}

function buildContextMetrics({
  scopeId,
  bestActivityLabel,
  bestActivityRisk,
  bestActivitySurvival24m,
  uniqueActivityCategories,
  turnoverRate12m,
  totalPopulation,
  shareForeign,
  shareYoung,
  avisosBarrio,
  avisosDistrict
}: {
  scopeId: string;
  bestActivityLabel: string;
  bestActivityRisk: number | null;
  bestActivitySurvival24m: number | null;
  uniqueActivityCategories: number | null;
  turnoverRate12m: number | null;
  totalPopulation: number | null;
  shareForeign: number | null;
  shareYoung: number | null;
  avisosBarrio: number | null;
  avisosDistrict: number | null;
}): MetricDefinition[] {
  return [
    {
      id: `${scopeId}:best-activity`,
      label: "Actividad sugerida",
      value: bestActivityLabel || "Sin ranking",
      summary: bestActivityLabel
        ? `${bestActivityLabel} es la mejor candidata actual para este entorno. ${buildBestActivitySummary(bestActivityLabel, bestActivityRisk, bestActivitySurvival24m)}`
        : "No hay ranking historico suficiente para proponer una actividad con fiabilidad minima.",
      calculation: "Ordenamos las actividades por riesgo historico ajustado por muestra. Primero usamos barrio; si falta cobertura suficiente, completamos con distrito y ciudad."
    },
    {
      id: `${scopeId}:active-categories`,
      label: "Categorias activas",
      value: formatCompact(uniqueActivityCategories),
      summary: "Mide la diversidad comercial real del entorno.",
      calculation: "Contamos cuantas categorias de actividad distintas aparecen activas en la seccion censal."
    },
    {
      id: `${scopeId}:turnover-12m`,
      label: "Rotacion 12m",
      value: formatShare(turnoverRate12m),
      summary: "Resume cuanto se ha movido el tejido comercial en el ultimo ano observado.",
      calculation: "Dividimos los cambios o salidas observados en los ultimos 12 meses entre el stock de locales de la seccion."
    },
    {
      id: `${scopeId}:population`,
      label: "Poblacion",
      value: formatCompact(totalPopulation),
      summary: "Es el tamano residencial del entorno inmediato.",
      calculation: "Tomamos la poblacion total mas reciente asociada a la seccion censal."
    },
    {
      id: `${scopeId}:foreign-share`,
      label: "Extranjera",
      value: formatShare(shareForeign),
      summary: "Mide el peso de residentes extranjeros dentro de la seccion.",
      calculation: "Dividimos la poblacion extranjera entre la poblacion total de la seccion."
    },
    {
      id: `${scopeId}:young-share`,
      label: "Joven 15-29",
      value: formatShare(shareYoung),
      summary: "Aproxima el peso de poblacion joven en el entorno.",
      calculation: "Dividimos los residentes de 15 a 29 anos entre la poblacion total de la seccion."
    },
    {
      id: `${scopeId}:avisos-barrio`,
      label: "Avisos barrio",
      value: formatRatePerThousandResidents(avisosBarrio),
      summary: "Mide la presion vecinal reciente registrada a escala de barrio.",
      calculation: "Tomamos el numero de avisos del ano previo y lo normalizamos por cada 1.000 habitantes del barrio."
    },
    {
      id: `${scopeId}:avisos-district`,
      label: "Avisos distrito",
      value: formatRatePerThousandResidents(avisosDistrict),
      summary: "Mide la presion vecinal reciente registrada a escala de distrito.",
      calculation: "Tomamos el numero de avisos del ano previo y lo normalizamos por cada 1.000 habitantes del distrito."
    }
  ];
}

function buildMetricWhyUseful(metric: MetricDefinition) {
  if (metric.id.includes(":survival:")) {
    return "Te sirve para comparar de un vistazo qué entornos aguantan mejor una apertura parecida en el horizonte que estás mirando.";
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Te permite entender si estás en una zona estructuralmente más delicada o más favorable que la media de Madrid sin tener que interpretar el score bruto del modelo.";
  }
  if (metric.id.endsWith(":city-rank") || metric.id.endsWith(":district-rank") || metric.id.endsWith(":barrio-rank")) {
    return "Te ayuda a priorizar ubicaciones: el ranking te dice si esta sección está entre las mejores o peores comparables dentro del ámbito que te importa.";
  }
  if (metric.id.endsWith(":income")) {
    return "Aporta contexto de poder adquisitivo y ayuda a valorar si el entorno puede sostener conceptos de ticket medio más alto o más sensible a precio.";
  }
  if (metric.id.endsWith(":metro")) {
    return "Es útil para estimar accesibilidad y paso potencial, especialmente en actividades que dependen de conveniencia o tráfico peatonal.";
  }
  if (metric.id.endsWith(":density") || metric.id.endsWith(":population")) {
    return "Ayuda a dimensionar la base residencial alrededor del local y a distinguir zonas con más masa crítica de consumo cotidiano.";
  }
  if (metric.id.endsWith(":competition") || metric.id.endsWith(":active-categories")) {
    return "Te orienta sobre cuánta oferta comercial ya existe y si el entorno está más saturado o más diverso.";
  }
  if (metric.id.endsWith(":best-activity")) {
    return "Resume la actividad que mejor ha resistido históricamente en entornos parecidos, útil para abrir con una hipótesis inicial más defensiva.";
  }
  if (metric.id.endsWith(":turnover-12m")) {
    return "Sirve para detectar si el tejido comercial es estable o si cambia mucho de manos y conceptos en poco tiempo.";
  }
  if (metric.id.endsWith(":foreign-share") || metric.id.endsWith(":young-share")) {
    return "Aporta una lectura rápida del perfil demográfico dominante y puede ayudarte a valorar afinidad con ciertos formatos o surtidos.";
  }
  if (metric.id.endsWith(":avisos-barrio") || metric.id.endsWith(":avisos-district")) {
    return "Funciona como señal indirecta de fricción vecinal o presión urbana reciente, útil para actividades más sensibles a convivencia, ruido o intensidad de uso.";
  }
  return "Te da una señal adicional para interpretar el entorno con algo más de contexto que el anuncio puro.";
}

function buildMetricExample(metric: MetricDefinition) {
  if (metric.id.endsWith(":risk-percentile")) {
    return "Ejemplo: un P85 implica que esta sección tiene más riesgo histórico que aproximadamente el 85% de Madrid y solo mejora frente al 15% restante.";
  }
  if (metric.id.endsWith(":city-rank")) {
    return "Ejemplo: #120 de 2.461 significa que la sección está muy arriba dentro de Madrid cuando ordenas por menor riesgo.";
  }
  if (metric.id.endsWith(":district-rank") || metric.id.endsWith(":barrio-rank")) {
    return "Ejemplo: #3 de 41 indica que, dentro de ese ámbito, la sección está entre las primeras posiciones por menor riesgo.";
  }
  if (metric.id.endsWith(":turnover-12m")) {
    return "Ejemplo: una rotación del 18% sugiere que casi 1 de cada 5 locales del entorno ha cambiado o salido en el último año observado.";
  }
  if (metric.id.endsWith(":avisos-barrio") || metric.id.endsWith(":avisos-district")) {
    return "Ejemplo: 2,40 / 1.000 hab significa que el año anterior hubo 2,4 avisos por cada mil residentes de ese ámbito.";
  }
  if (metric.id.endsWith(":best-activity")) {
    return "Ejemplo: si aparece 'Farmacia' con riesgo 3% y supervivencia 24m 97%, la lectura es que esa actividad ha aguantado mejor que otras comparables en ese entorno.";
  }
  if (metric.id.endsWith(":competition")) {
    return "Ejemplo: 120 locales no significa 120 competidores directos, sino 120 locales activos en la sección que comparten atención y espacio comercial.";
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