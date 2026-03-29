"use client";

import { useEffect, useMemo, useState } from "react";

import { MadridMap } from "@/components/madrid-map";
import { ViewTabs } from "@/components/view-tabs";
import { formatHorizonLongLabel, formatHorizonShortLabel, getHorizonSupport, getHorizonSurvival, isFiniteNumber, type Horizon } from "@/lib/horizon";
import { FALLBACK_MAP_ARTIFACTS, loadMapArtifactsFromPublic } from "@/lib/public-data";
import type { ColorScale, FrontendArtifacts, HexAggregate, ZoneAggregate } from "@/lib/types";

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
};

export function MapShell({ initialArtifacts }: MapShellProps) {
  const [artifacts, setArtifacts] = useState(initialArtifacts ?? FALLBACK_MAP_ARTIFACTS);
  const [isLoadingArtifacts, setIsLoadingArtifacts] = useState(!initialArtifacts);
  const [selectedCategory, setSelectedCategory] = useState((initialArtifacts ?? FALLBACK_MAP_ARTIFACTS).meta.defaultCategoryCode);
  const [horizon, setHorizon] = useState<Horizon>("24m");
  const [selectedHex, setSelectedHex] = useState<HexAggregate | null>(null);
  const [activeMetricId, setActiveMetricId] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;

    if (initialArtifacts) {
      return () => {
        alive = false;
      };
    }

    void loadMapArtifactsFromPublic().then((nextArtifacts) => {
      if (!alive) {
        return;
      }

      setArtifacts(nextArtifacts);
      setIsLoadingArtifacts(false);
      setSelectedHex(null);
      setSelectedCategory((currentCategory) => {
        return nextArtifacts.categories.some((item) => item.category_code === currentCategory)
          ? currentCategory
          : nextArtifacts.meta.defaultCategoryCode;
      });
    });

    return () => {
      alive = false;
    };
  }, [initialArtifacts]);

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
        meanRisk: 0
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
    const meanRisk = filteredHexes.reduce((sum, item) => sum + item.n_locales * item.avg_risk_ensemble, 0) / locales;

    return {
      locales,
      hexes: filteredHexes.length,
      hexesWithSupport: survivalTotals.supportedHexes,
      meanSurvival: survivalTotals.supportedLocales > 0 ? survivalTotals.weightedSurvival / survivalTotals.supportedLocales : null,
      meanRisk
    };
  }, [filteredHexes, horizon]);

  const detail = selectedHex;
  const detailSurvival = detail ? getHorizonSurvival(detail, horizon) : null;
  const detailSupport = detail ? getHorizonSupport(detail, horizon) : 0;

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
      meanSurvival: activeStats.meanSurvival
    });
  }, [activeStats.meanSurvival, detail, detailRank, detailSupport, detailSurvival, horizon]);

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
          <label className="control-label" htmlFor="category">
            Tipo de local
          </label>
          <select
            className="select"
            id="category"
            value={selectedCategory}
            onChange={(event) => {
              setSelectedCategory(event.target.value);
              setSelectedHex(null);
            }}
          >
            {artifacts.categories.map((category) => (
              <option key={category.category_code} value={category.category_code}>
                {category.category_desc}
              </option>
            ))}
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
            <span className="label">Supervivencia media</span>
            <span className="value">{formatPercent(activeStats.meanSurvival, activeStats.hexes > 0 ? "Sin muestra" : "Sin datos")}</span>
          </div>
          <div className="stat-card">
            <span className="label">Riesgo medio</span>
            <span className="value">{activeStats.meanRisk.toFixed(2)}</span>
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
            : buildGlobalSupportNote(activeStats.hexesWithSupport, activeStats.hexes, horizon)}
        </p>

        <section className="info-card">
          <div className="eyebrow">Ficha categoria</div>
          <h2>{selectedCategoryMeta.category_desc}</h2>
          <p>{selectedCategoryMeta.definition ?? buildFallbackCategoryDefinition(selectedCategoryMeta.category_desc)}</p>
        </section>

        <section className="info-card">
          <div className="eyebrow">Zonas destacadas</div>
          <h3>Menor riesgo medio</h3>
          <ZoneList barrioZones={topZones.barrio} districtZones={topZones.district} />
        </section>

        <section className="detail-card">
          <div className="eyebrow">Hexágono seleccionado</div>
          {detail ? (
            <>
              <h2>{detail.category_desc}</h2>
              <p className="detail-subtle">Hex {detail.h3_cell}</p>
              <div className="detail-meta">
                <span className="chip">{detail.n_locales} locales</span>
                <span className={`chip${detailSurvival === null ? " chip-muted" : ""}`}>Surv {formatPercent(detailSurvival, detailSupport > 0 ? "Sin datos" : "Sin muestra")}</span>
                <span className="chip">Soporte {detailSupport}/{detail.n_locales}</span>
              </div>
              <MetricGrid activeMetricId={activeMetricId} metrics={detailMetrics} onSelect={setActiveMetricId} />
              <p className="detail-footnote">{buildDetailSupportNote(detailSupport, detail.n_locales, horizon)}</p>
            </>
          ) : (
            <div className="detail-empty">
              <h3>Selecciona un hexágono</h3>
              <p>Haz click en el mapa para ver su posición en Madrid, su ranking por riesgo y la diferencia frente a la media de la categoría.</p>
            </div>
          )}
        </section>
      </aside>

      <section className="map-panel panel">
        {activeMetric ? (
          <div className="map-overlay panel metric-banner">
            <MetricExplainer metric={activeMetric} />
          </div>
        ) : null}

        <MadridMap
          bounds={artifacts.meta.map_bounds}
          colorScale={colorScale}
          horizon={horizon}
          hexes={filteredHexes}
          onSelectHex={setSelectedHex}
          selectedHex={selectedHex}
        />
      </section>
    </main>
  );
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
            <span className="detail-metric-hint">Qué es, para qué sirve y cómo se calcula</span>
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
        <p className="metric-explainer-copy">Haz click en una tarjeta del hexágono para ver qué significa, por qué es útil y cómo se calcula.</p>
      )}
    </div>
  );
}

type ZoneRankCardProps = {
  rank: number;
  zone: ZoneAggregate | null;
  emptyLabel: string;
};

function ZoneList({ districtZones, barrioZones }: ZoneListProps) {
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
            <ZoneRankCard emptyLabel="Sin distrito suficiente" rank={row.rank} zone={row.district} />
            <ZoneRankCard emptyLabel="Sin barrio suficiente" rank={row.rank} zone={row.barrio} />
          </div>
        ))}
      </div>
    </div>
  );
}

function ZoneRankCard({ rank, zone, emptyLabel }: ZoneRankCardProps) {
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
    <div className="zone-list-item">
      <div className="zone-list-top">
        <span className="zone-list-rank">#{rank}</span>
        <span className="zone-list-value">{formatRiskValue(zone.avg_risk_ensemble)}</span>
      </div>
      <strong className="zone-list-title">{zone.zone_name}</strong>
      <span className="zone-list-meta">{formatCompact(zone.n_locales)} locales</span>
    </div>
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
  const topShare = Math.max(1, Math.round((rank / total) * 100));
  return `#${rank} de ${total} · top ${topShare}%`;
}

function formatRiskPercentile(value: number) {
  const clamped = Math.max(0, Math.min(1, value));
  return `P${Math.round(clamped * 100)}`;
}

function formatRiskValue(value: number) {
  return value.toFixed(2);
}

function formatSignedPercent(value: number | null, missingLabel = "Sin muestra") {
  if (!isFiniteNumber(value)) {
    return missingLabel;
  }
  const points = value * 100;
  const prefix = points > 0 ? "+" : "";
  return `${prefix}${points.toFixed(0)} pp`;
}

function formatSupport(support: number, total: number) {
  return `${formatCompact(support)} / ${formatCompact(total)}`;
}

function buildFallbackCategoryDefinition(categoryDesc: string) {
  return `Lectura agregada de la macrocategoría ${categoryDesc.toLowerCase()} sobre los locales históricos visibles en el mapa.`;
}

function buildTopZones(zones: ZoneAggregate[]) {
  const source = zones.some((item) => item.supported_for_stats) ? zones.filter((item) => item.supported_for_stats) : zones;
  return [...source]
    .sort((left, right) => {
      const rawRiskDiff = left.avg_risk_ensemble - right.avg_risk_ensemble;
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
    })
    .slice(0, 3);
}

function buildHexMetrics({
  detail,
  detailRank,
  detailSupport,
  detailSurvival,
  horizon,
  meanSurvival
}: {
  detail: HexAggregate;
  detailRank: { rank: number; total: number } | null;
  detailSupport: number;
  detailSurvival: number | null;
  horizon: Horizon;
  meanSurvival: number | null;
}): MetricDefinition[] {
  const horizonLabel = formatHorizonShortLabel(horizon);
  return [
    {
      id: `hex:${detail.h3_cell}:city-rank`,
      label: "Ranking Madrid",
      value: detailRank ? formatHexRank(detailRank.rank, detailRank.total) : "-",
      summary: "Posición del hexágono frente al resto de hexágonos visibles de la categoría cuando ordenas por menor riesgo.",
      calculation: "Ordenamos todos los hexágonos visibles por riesgo medio ascendente y asignamos la posición relativa del hexágono seleccionado."
    },
    {
      id: `hex:${detail.h3_cell}:risk-percentile`,
      label: "Percentil riesgo",
      value: formatRiskPercentile(detail.avg_risk_percentile),
      summary: "Ubica el riesgo del hexágono dentro de la distribución de la categoría en Madrid.",
      calculation: "Convertimos el riesgo relativo del hexágono a percentil para expresar qué parte del mapa tiene un riesgo igual o menor."
    },
    {
      id: `hex:${detail.h3_cell}:risk-value`,
      label: "Riesgo local",
      value: formatRiskValue(detail.avg_risk_ensemble),
      summary: "Es el score bruto medio de riesgo del modelo en este hexágono.",
      calculation: "Promediamos el score ensemble de los locales históricos de esta categoría que caen dentro del hexágono."
    },
    {
      id: `hex:${detail.h3_cell}:vs-category`,
      label: `Vs media ${horizonLabel}`,
      value: formatSignedPercent(computeSurvivalDelta(detailSurvival, meanSurvival), detailSupport > 0 && isFiniteNumber(meanSurvival) ? "Sin datos" : "Sin muestra"),
      summary: "Mide cuánto mejor o peor rinde este hexágono frente a la media de la categoría activa.",
      calculation: `Restamos la supervivencia media de la categoría a la supervivencia del hexágono en ${horizonLabel} y expresamos la diferencia en puntos porcentuales.`
    },
    {
      id: `hex:${detail.h3_cell}:survival:${horizon}`,
      label: `Supervivencia ${horizonLabel}`,
      value: formatPercent(detailSurvival, detailSupport > 0 ? "Sin datos" : "Sin muestra"),
      summary: `Es la supervivencia observada de la categoría en este hexágono para ${horizonLabel}.`,
      calculation: `Usamos solo locales con soporte suficiente en ${horizonLabel} y calculamos la supervivencia observada agregada para este hexágono.`
    },
    {
      id: `hex:${detail.h3_cell}:support:${horizon}`,
      label: `Soporte ${horizonLabel}`,
      value: formatSupport(detailSupport, detail.n_locales),
      summary: "Indica cuántos locales realmente sostienen la métrica del horizonte frente al total visible en el hexágono.",
      calculation: `El numerador cuenta los locales con observación válida en ${horizonLabel}; el denominador es el total de locales agregados del hexágono.`
    },
    {
      id: `hex:${detail.h3_cell}:barrio-name`,
      label: "Barrio",
      value: detail.barrio_name || "Sin asignar",
      summary: "Nombre aproximado del barrio al que pertenece la mayor parte del hexágono.",
      calculation: "Se infiere a partir de la geografía censal enlazada al hexágono y se usa como referencia interpretativa, no como límite exacto del polígono H3."
    },
    {
      id: `hex:${detail.h3_cell}:district-name`,
      label: "Distrito",
      value: detail.district_name || "Sin asignar",
      summary: "Distrito administrativo asociado al hexágono para facilitar lectura territorial rápida.",
      calculation: "Se recupera desde la mejor asignación geográfica disponible entre las secciones históricas y el hexágono H3."
    }
  ];
}

function buildMetricWhyUseful(metric: MetricDefinition) {
  if (metric.id.endsWith(":city-rank")) {
    return "Te ayuda a priorizar rápido: con una sola cifra ves si este hexágono está entre los mejores o peores de la categoría activa dentro de Madrid.";
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Es útil cuando quieres comparar zonas sin entrar en el detalle técnico del score: te dice si estás en una parte más segura o más delicada del mapa.";
  }
  if (metric.id.endsWith(":risk-value")) {
    return "Sirve para comparar intensidad de riesgo con más precisión cuando dos hexágonos tienen percentiles parecidos pero no idénticos.";
  }
  if (metric.id.endsWith(":vs-category")) {
    return "Te da contexto relativo: no solo ves cómo rinde el hexágono, sino si está por encima o por debajo del nivel normal de la categoría.";
  }
  if (metric.id.includes(":survival:")) {
    return "Es la señal más directa para entender qué probabilidad histórica tiene esa categoría de aguantar en esta zona durante el horizonte elegido.";
  }
  if (metric.id.includes(":support:")) {
    return "Evita sobreinterpretar celdas con poca base histórica: cuanto mayor es el soporte, más robusta suele ser la lectura.";
  }
  if (metric.id.endsWith(":barrio-name") || metric.id.endsWith(":district-name")) {
    return "Te orienta territorialmente y hace más fácil relacionar el hexágono con zonas reconocibles de Madrid sin tener que leer un identificador H3.";
  }
  return "Aporta contexto adicional para interpretar mejor el comportamiento histórico del hexágono seleccionado.";
}

function buildMetricExample(metric: MetricDefinition) {
  if (metric.id.endsWith(":city-rank")) {
    return "Ejemplo: #45 de 3.200 significa que este hexágono está muy arriba dentro del mapa de esa categoría cuando ordenas por menor riesgo.";
  }
  if (metric.id.endsWith(":risk-percentile")) {
    return "Ejemplo: P20 indica que el hexágono tiene menos riesgo que aproximadamente el 80% de los hexágonos comparables.";
  }
  if (metric.id.endsWith(":vs-category")) {
    return "Ejemplo: +6 pp significa que la supervivencia del hexágono está 6 puntos porcentuales por encima de la media de la categoría.";
  }
  if (metric.id.includes(":support:")) {
    return "Ejemplo: 18 / 26 quiere decir que 18 locales del total de 26 tienen observación válida para ese horizonte.";
  }
  return null;
}

function buildHexRanking(hexes: HexAggregate[], detail: HexAggregate, _horizon: Horizon) {
  const sorted = [...hexes].sort((left, right) => {
    const rawRiskDiff = left.avg_risk_ensemble - right.avg_risk_ensemble;
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

function buildDetailSupportNote(support: number, total: number, horizon: Horizon) {
  const horizonLabel = formatHorizonLongLabel(horizon);
  if (total <= 0) {
    return `No hay locales visibles en este hexágono.`;
  }
  if (support <= 0) {
    return `Sin soporte suficiente a ${horizonLabel}: ninguno de los ${total} locales del hexágono permite resolver todavía ese horizonte.`;
  }
  if (support < total) {
    return `Soporte ${horizonLabel}: ${support} de ${total} locales ya permiten medir este horizonte.`;
  }
  return `Soporte ${horizonLabel} completo: ${support} de ${total} locales permiten medir este horizonte.`;
}

function computeSurvivalDelta(value: number | null, baseline: number | null) {
  if (!isFiniteNumber(value) || !isFiniteNumber(baseline)) {
    return null;
  }
  return value - baseline;
}
