"use client";

import { useEffect, useMemo, useRef, useState, type ChangeEvent, type PointerEvent } from "react";

import type { HistoricalRankingArtifacts, HistoricalZoneLevel, HistoricalZoneRankingRecord } from "@/lib/types";

const SERIES_COLORS = ["#d7c8a2", "#b8d5d8", "#d8b9d3", "#bfd8c4", "#c9c2e8", "#ecc6b6", "#c6d8af", "#b9cbe7", "#e3cfb5", "#c8b6d9", "#bcd8ce", "#dfc5a6"];
const CHART_WIDTH = 620;
const CHART_PADDING = { top: 36, right: 18, bottom: 18, left: 60 };
const HOVER_CARD_HEIGHT = 58;
const HOVER_CARD_WIDTH = 196;
const MAX_VISIBLE_CURRENT_SERIES = 4;
const DEFAULT_RANK_LIMIT = 9;
const MIN_RANK_LIMIT = 6;
const MAX_RANK_LIMIT = 12;
const MAX_VISIBLE_SERIES = 12;
const TOP_LIMIT_OPTIONS = [6, 7, 8, 9, 10, 11, 12] as const;

type HistoricalEvolutionBannerProps = {
  artifacts: HistoricalRankingArtifacts | null;
  categoryCode: string;
  categoryDesc: string;
  isLoading: boolean;
  onClose: () => void;
  onSelectZoneLevel: (zoneLevel: HistoricalZoneLevel) => void;
  zoneLevel: HistoricalZoneLevel;
};

type ChartPoint = {
  actualRank: number | null;
  isOutOfRange: boolean;
  nLocales: number | null;
  plotRank: number;
  shareOfZone: number | null;
  year: number;
};

type ChartSeries = {
  color: string;
  bestMetricValue: number | null;
  bestRank: number;
  currentRank: number;
  currentRankInFocus: boolean;
  currentRankIsLeader: boolean;
  latestMetricValue: number | null;
  points: ChartPoint[];
  zoneContextName: string | null;
  zoneKey: string;
  zoneName: string;
};

type ChartHoverState = {
  nLocales: number | null;
  point: ChartPoint;
  popoverLeft: number;
  popoverTop: number;
  yearIndex: number;
  zoneContextName: string | null;
  zoneKey: string;
  zoneName: string;
};

type ChartView = {
  contextPoints: { rank: number; year: number; yearIndex: number }[];
  currentSeriesLimit: number;
  fallbackRank: number;
  latestPeriod: string;
  latestYear: number;
  latestYearIsPartial: boolean;
  rankFocusLimit: number;
  rankTicks: number[];
  series: ChartSeries[];
  years: number[];
};

export function HistoricalEvolutionBanner({
  artifacts,
  categoryCode,
  categoryDesc,
  isLoading,
  onClose,
  onSelectZoneLevel,
  zoneLevel,
}: HistoricalEvolutionBannerProps) {
  const [selectedRankLimit, setSelectedRankLimit] = useState(DEFAULT_RANK_LIMIT);
  const chartView = useMemo(() => {
    if (!artifacts) {
      return null;
    }
    return buildHistoricalChartView({ artifacts, categoryCode, zoneLevel, selectedRankLimit });
  }, [artifacts, categoryCode, selectedRankLimit, zoneLevel]);
  const [selectedZoneKey, setSelectedZoneKey] = useState<string | null>(null);
  const [hoverState, setHoverState] = useState<ChartHoverState | null>(null);

  useEffect(() => {
    setHoverState(null);
    setSelectedZoneKey((current) => {
      if (!current || !chartView?.series.some((series) => series.zoneKey === current)) {
        return null;
      }
      return current;
    });
  }, [chartView]);

  const levelLabel = zoneLevel === "district" ? "distritos" : "barrios";
  const activeZoneKey = hoverState?.zoneKey ?? selectedZoneKey;
  const metricCopy = buildHistoricalMetricCopy({
    categoryCode,
    defaultMetricLabel: artifacts?.meta.metric_short_label ?? "Especializacion vs Madrid",
    fallbackBaseYear: chartView?.years[0] ?? artifacts?.meta.years[0] ?? null,
  });

  const handleRankLimitChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setSelectedRankLimit(Number(event.target.value));
  };

  return (
    <section
      aria-label={`Evolución histórica de ${levelLabel}`}
      aria-modal="false"
      className="explain-banner explain-banner-floating historical-evolution-banner"
      role="dialog"
    >
      <div className="explain-banner-header historical-evolution-header">
        <div className="explain-banner-headcopy">
          <span className="explain-banner-kicker">Evolución histórica</span>
          <strong className="explain-banner-title">Cómo se movieron los líderes de {categoryDesc}</strong>
          <span className="explain-banner-summary">Un resumen rápido para ver quién estuvo arriba y cómo fue cambiando.</span>
        </div>
        <button aria-label="Cerrar evolución histórica" className="explain-banner-close" onClick={onClose} type="button">
          Cerrar
        </button>
      </div>

      <div className="historical-evolution-toolbar">
        <div aria-label="Cambiar ámbito territorial" className="historical-evolution-toggle" role="tablist">
          <button
            aria-selected={zoneLevel === "district"}
            className="historical-evolution-toggle-button"
            data-active={zoneLevel === "district"}
            onClick={() => onSelectZoneLevel("district")}
            role="tab"
            type="button"
          >
            Distritos
          </button>
          <button
            aria-selected={zoneLevel === "barrio"}
            className="historical-evolution-toggle-button"
            data-active={zoneLevel === "barrio"}
            onClick={() => onSelectZoneLevel("barrio")}
            role="tab"
            type="button"
          >
            Barrios
          </button>
        </div>

        <div className="historical-evolution-toolbar-side">
          <label className="historical-evolution-rank-control" htmlFor="historical-evolution-top-limit">
            <span className="historical-evolution-rank-control-label">Top</span>
            <select id="historical-evolution-top-limit" onChange={handleRankLimitChange} value={selectedRankLimit}>
              {TOP_LIMIT_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>

        </div>
      </div>

      <p className="historical-evolution-intro">
        Más a la izquierda es mejor. Aquí no enseñamos todas las zonas. Enseñamos el top {selectedRankLimit} para que el gráfico se entienda de un vistazo. Puedes cambiar la categoría si quieres mirar otra.
      </p>

      {isLoading && !artifacts ? (
        <div className="historical-evolution-empty">
          <strong>Cargando evolución histórica...</strong>
          <p>Estamos preparando el corte anual para que el gráfico salga ligero y no bloquee el mapa.</p>
        </div>
      ) : chartView ? (
        <>
          <div className="historical-evolution-summary">
            <span className="historical-evolution-chip">{metricCopy.chipLabel}</span>
            <span className="historical-evolution-chip">{buildSeriesMixLabel(chartView, chartView.currentSeriesLimit)}</span>
            <span className="historical-evolution-chip">Top visible #{chartView.rankFocusLimit}</span>
          </div>

          <div className="historical-evolution-layout">
            <div className="historical-evolution-chart-shell">
              <RankingBumpChart
                activeZoneKey={activeZoneKey}
                categoryDesc={categoryDesc}
                hoverState={hoverState}
                onHoverChange={setHoverState}
                view={chartView}
                zoneLevel={zoneLevel}
              />
            </div>

            <div className="historical-evolution-legend historical-evolution-legend-compact">
              {chartView.series.map((series) => (
                <button
                  aria-pressed={selectedZoneKey === series.zoneKey}
                  className="historical-evolution-legend-item historical-evolution-legend-item-compact"
                  data-active={activeZoneKey === series.zoneKey}
                  data-selected={selectedZoneKey === series.zoneKey}
                  key={series.zoneKey}
                  onClick={() => setSelectedZoneKey((current) => (current === series.zoneKey ? null : series.zoneKey))}
                  type="button"
                >
                  <span aria-hidden="true" className="historical-evolution-legend-swatch" style={{ backgroundColor: series.color }} />
                  <span className="historical-evolution-legend-copy">
                    <strong className="historical-evolution-legend-title">{series.zoneName}</strong>
                    {series.zoneContextName ? <span className="historical-evolution-legend-context">{series.zoneContextName}</span> : null}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <p className="historical-evolution-footnote">{buildHistoricalFootnote(chartView, metricCopy.footnoteLead)}</p>
        </>
      ) : (
        <div className="historical-evolution-empty">
          <strong>No hay recorrido suficiente para esta categoría.</strong>
          <p>Prueba con otra categoría o regenera el artefacto temporal si acabas de tocar el builder.</p>
        </div>
      )}
    </section>
  );
}

function RankingBumpChart({
  activeZoneKey,
  categoryDesc,
  hoverState,
  onHoverChange,
  view,
  zoneLevel,
}: {
  activeZoneKey: string | null;
  categoryDesc: string;
  hoverState: ChartHoverState | null;
  onHoverChange: (state: ChartHoverState | null) => void;
  view: ChartView;
  zoneLevel: HistoricalZoneLevel;
}) {
  const VERTICAL_SPACING = 40;
  const innerHeight = Math.max(280, (view.years.length - 1) * VERTICAL_SPACING);
  const innerWidth = CHART_WIDTH - CHART_PADDING.left - CHART_PADDING.right;
  const chartHeight = CHART_PADDING.top + innerHeight + CHART_PADDING.bottom;
  const svgRef = useRef<SVGSVGElement | null>(null);
  const plotSeries = useMemo(
    () =>
      view.series.map((series) => ({
        points: series.points.map((point, index) => ({
          index,
          point,
          x: positionX(point.plotRank, innerWidth, view.fallbackRank),
          y: positionY(index, view.years.length, innerHeight),
        })),
        series,
      })),
    [innerHeight, innerWidth, view.fallbackRank, view.series, view.years.length]
  );

  const handlePointerMove = (event: PointerEvent<SVGSVGElement>) => {
    const svg = svgRef.current;
    if (!svg) {
      return;
    }

    const rect = svg.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) {
      onHoverChange(null);
      return;
    }

    const relativeX = event.clientX - rect.left;
    const relativeY = event.clientY - rect.top;
    const scaleX = CHART_WIDTH / rect.width;
    const scaleY = chartHeight / rect.height;
    const pointerX = relativeX * scaleX;
    const pointerY = relativeY * scaleY;

    onHoverChange(
      findNearestSeriesHover({
        chartHeightPx: rect.height,
        chartWidthPx: rect.width,
        pointerX,
        pointerY,
        relativeX,
        relativeY,
        seriesCollection: plotSeries,
      })
    );
  };

  return (
    <div className="historical-bump-chart-frame">
      <svg
        aria-label={`Ranking anual de ${categoryDesc} por ${zoneLevel === "district" ? "distritos" : "barrios"}`}
        className="historical-bump-chart"
        onPointerLeave={() => onHoverChange(null)}
        onPointerMove={handlePointerMove}
        ref={svgRef}
        role="img"
        viewBox={`0 0 ${CHART_WIDTH} ${chartHeight}`}
      >
        <g>
          {view.rankTicks.map((rank) => {
            const x = positionX(rank, innerWidth, view.fallbackRank);
            return (
              <g key={`rank:${rank}`}>
                <line
                  className="historical-bump-chart-vertical"
                  x1={x}
                  x2={x}
                  y1={CHART_PADDING.top}
                  y2={chartHeight - CHART_PADDING.bottom}
                />
                <text className="historical-bump-chart-axis-label" textAnchor="middle" x={x} y={20}>
                  #{rank}
                </text>
              </g>
            );
          })}

          <line
            className="historical-bump-chart-vertical historical-bump-chart-vertical-out"
            x1={positionX(view.fallbackRank, innerWidth, view.fallbackRank)}
            x2={positionX(view.fallbackRank, innerWidth, view.fallbackRank)}
            y1={CHART_PADDING.top}
            y2={chartHeight - CHART_PADDING.bottom}
          />
          <text
            className="historical-bump-chart-axis-label historical-bump-chart-axis-label-out"
            textAnchor="middle"
            x={positionX(view.fallbackRank, innerWidth, view.fallbackRank)}
            y={20}
          >
            Fuera
          </text>

          {view.years.map((year, index) => {
            const y = positionY(index, view.years.length, innerHeight);
            return (
              <g key={`year:${year}`}>
                <line
                  className="historical-bump-chart-horizontal"
                  x1={CHART_PADDING.left}
                  x2={CHART_WIDTH - CHART_PADDING.right}
                  y1={y}
                  y2={y}
                />
                <text className="historical-bump-chart-year-label" textAnchor="end" x={CHART_PADDING.left - 12} y={y + 4}>
                  {year}
                </text>
              </g>
            );
          })}

          {view.contextPoints.map((point) => (
            <circle
              className="historical-bump-chart-context-point"
              cx={positionX(point.rank, innerWidth, view.fallbackRank)}
              cy={positionY(point.yearIndex, view.years.length, innerHeight)}
              key={`context:${point.year}:${point.rank}`}
              r={2.35}
            />
          ))}

          {view.series.map((series) => {
            const isActive = activeZoneKey === series.zoneKey;
            const isDimmed = activeZoneKey !== null && !isActive;

            return (
              <g key={`series:${series.zoneKey}`}>
                <path
                  className="historical-bump-chart-series"
                  d={buildSeriesPath(series.points, innerWidth, innerHeight, view.fallbackRank, view.years.length)}
                  data-active={isActive}
                  data-dimmed={isDimmed}
                  stroke={series.color}
                />
                {series.points.map((point, index) => (
                  <circle
                    className="historical-bump-chart-point"
                    cx={positionX(point.plotRank, innerWidth, view.fallbackRank)}
                    cy={positionY(index, view.years.length, innerHeight)}
                    data-active={isActive}
                    data-dimmed={isDimmed}
                    data-out-of-range={point.isOutOfRange}
                    fill={point.isOutOfRange ? "#fffaf2" : series.color}
                    key={`point:${series.zoneKey}:${point.year}`}
                    r={point.year === view.latestYear && isActive ? 5.2 : point.year === view.latestYear ? 4 : 3}
                    stroke={series.color}
                    strokeWidth={point.isOutOfRange ? 2 : 1.5}
                  />
                ))}
              </g>
            );
          })}
        </g>
      </svg>

      {hoverState ? (
        <div
          className="historical-bump-chart-popover"
          style={{ left: `${hoverState.popoverLeft}px`, top: `${hoverState.popoverTop}px` }}
        >
          <strong className="historical-bump-chart-popover-title">{truncateLabel(hoverState.zoneName, 28)}</strong>
          <span className="historical-bump-chart-popover-meta">
            {hoverState.zoneContextName ? `${truncateLabel(hoverState.zoneContextName, 24)} · ` : ""}
            {hoverState.point.year} · {formatRankLabel(hoverState.point.actualRank, view.rankFocusLimit)}
            {hoverState.nLocales ? ` · ${formatCompact(hoverState.nLocales)} locales` : ""}
          </span>
        </div>
      ) : null}
    </div>
  );
}

function buildHistoricalChartView({
  artifacts,
  categoryCode,
  selectedRankLimit,
  zoneLevel,
}: {
  artifacts: HistoricalRankingArtifacts;
  categoryCode: string;
  selectedRankLimit: number;
  zoneLevel: HistoricalZoneLevel;
}): ChartView | null {
  const rows = artifacts.zones[zoneLevel].filter((item) => item.category_code === categoryCode);
  if (rows.length === 0) {
    return null;
  }

  const latestYear = rows.reduce((currentMax, item) => Math.max(currentMax, item.year), rows[0].year);
  const latestRows = rows
    .filter((item) => item.year === latestYear)
    .sort((left, right) => {
      if (left.rank !== right.rank) {
        return left.rank - right.rank;
      }
      const metricDelta = (right.metric_value ?? -Infinity) - (left.metric_value ?? -Infinity);
      if (Math.abs(metricDelta) > 1e-9) {
        return metricDelta;
      }
      return left.zone_name.localeCompare(right.zone_name, "es");
    });

  if (latestRows.length === 0) {
    return null;
  }

  const years = artifacts.meta.years.filter((year) => year <= latestYear);
  const rankFocusLimit = clamp(Math.round(selectedRankLimit), MIN_RANK_LIMIT, MAX_RANK_LIMIT);
  const seriesLimit = Math.min(MAX_VISIBLE_SERIES, rankFocusLimit);
  const currentLeaderLimit = Math.max(1, Math.min(MAX_VISIBLE_CURRENT_SERIES, seriesLimit));
  const fallbackRank = Math.max(2, rankFocusLimit + 1);
  const rankTicks = buildRankTicks(rankFocusLimit);
  const byZoneYear = new Map<string, HistoricalZoneRankingRecord>();

  for (const row of rows) {
    byZoneYear.set(`${row.zone_key}:${row.year}`, row);
  }

  const contextPoints = years.flatMap((year, yearIndex) => {
    const ranks = [...new Set(rows.filter((item) => item.year === year && item.rank <= rankFocusLimit).map((item) => item.rank))].sort((left, right) => left - right);
    return ranks.map((rank) => ({ rank, year, yearIndex }));
  });

  const zoneStats = buildZoneStats(rows, latestYear, rankFocusLimit, currentLeaderLimit);
  const currentLeaderKeys = latestRows.slice(0, currentLeaderLimit).map((row) => row.zone_key);
  const selectedZoneKeys = buildSelectedZoneKeys({
    currentLeaderKeys,
    rankFocusLimit,
    rows,
    seriesLimit,
    years,
    zoneStats,
  });
  const visibleRanksByYear = buildVisibleRanksByYear({
    rankFocusLimit,
    rows,
    selectedZoneKeys,
    years,
  });

  const series = selectedZoneKeys.map((zoneKey, index) => {
    const zoneSummary = zoneStats.find((item) => item.zoneKey === zoneKey);
    const latestRow = latestRows.find((item) => item.zone_key === zoneKey) ?? rows.find((item) => item.zone_key === zoneKey && item.year === latestYear) ?? null;
    if (!zoneSummary || !latestRow) {
      return null;
    }
    const points = years.map((year) => {
      const matched = byZoneYear.get(`${zoneKey}:${year}`) ?? null;
      const actualRank = matched?.rank ?? null;
      const visibleRanks = visibleRanksByYear.get(year);
      const isVisibleRank = actualRank !== null && actualRank <= rankFocusLimit && visibleRanks?.has(actualRank);
      return {
        actualRank,
        isOutOfRange: !isVisibleRank,
        nLocales: matched?.n_locales ?? null,
        plotRank: isVisibleRank ? actualRank : fallbackRank,
        shareOfZone: matched?.share_of_zone ?? null,
        year,
      } satisfies ChartPoint;
    });

    return {
      color: SERIES_COLORS[index % SERIES_COLORS.length],
      bestMetricValue: zoneSummary.bestMetricValue,
      bestRank: zoneSummary.bestRank,
      currentRank: zoneSummary.currentRank,
      currentRankInFocus: zoneSummary.currentRankInFocus,
      currentRankIsLeader: zoneSummary.currentRankIsLeader,
      latestMetricValue: zoneSummary.latestMetricValue,
      points,
      zoneContextName: zoneLevel === "barrio" ? latestRow.zone_context_name : null,
      zoneKey,
      zoneName: latestRow.zone_name,
    } satisfies ChartSeries;
  }).filter((item): item is ChartSeries => item !== null);

  const latestPeriod = artifacts.meta.latest_period_by_year[String(latestYear)] ?? rows[0].period;

  return {
    contextPoints,
    currentSeriesLimit: currentLeaderLimit,
    fallbackRank,
    latestPeriod,
    latestYear,
    latestYearIsPartial: !latestPeriod.endsWith("-12"),
    rankFocusLimit,
    rankTicks,
    series,
    years,
  };
}

function buildRankTicks(rankFocusLimit: number) {
  return Array.from({ length: Math.max(0, rankFocusLimit) }, (_, index) => index + 1);
}

function buildHistoricalMetricCopy({
  categoryCode,
  defaultMetricLabel,
  fallbackBaseYear,
}: {
  categoryCode: string;
  defaultMetricLabel: string;
  fallbackBaseYear: number | null;
}) {
  if (categoryCode === "__all__") {
    const baseYearText = fallbackBaseYear ? String(fallbackBaseYear) : "el inicio de la serie";
    return {
      chipLabel: "Cambio de peso en Madrid",
      footnoteLead: `Cada año miramos si la zona gana o pierde peso dentro del total de locales de Madrid frente a ${baseYearText}. Si gana peso, sube. Si lo pierde, baja.`,
      introLabel: `cambio de peso sobre el total de Madrid desde ${baseYearText}`,
    };
  }

  return {
    chipLabel: defaultMetricLabel,
    footnoteLead: "Cada año miramos cuánto pesa esta categoría en la zona y lo comparamos con cuánto pesa en Madrid. Si aquí pesa más, sube. Si pesa menos, baja.",
    introLabel: defaultMetricLabel.toLowerCase(),
  };
}

function buildHistoricalFootnote(view: ChartView, metricLead: string) {
  return `${metricLead} Fuera no significa que la zona desaparezca. Solo significa que no entra en el top ${view.rankFocusLimit} que estamos enseñando ahora.`;
}

function buildSeriesMixLabel(view: ChartView, currentSeriesLimit: number) {
  const currentLeaders = Math.min(currentSeriesLimit, view.series.filter((item) => item.currentRankIsLeader).length);
  const historicalOnly = Math.max(0, view.series.length - currentLeaders);
  if (historicalOnly <= 0) {
    return `${currentLeaders} líderes actuales`;
  }
  return `${currentLeaders} actuales + ${historicalOnly} históricos`;
}

function buildZoneStats(
  rows: HistoricalZoneRankingRecord[],
  latestYear: number,
  rankFocusLimit: number,
  currentSeriesLimit: number
) {
  const grouped = new Map<string, HistoricalZoneRankingRecord[]>();
  for (const row of rows) {
    const bucket = grouped.get(row.zone_key);
    if (bucket) {
      bucket.push(row);
    } else {
      grouped.set(row.zone_key, [row]);
    }
  }

  return [...grouped.entries()].map(([zoneKey, zoneRows]) => {
    const ordered = [...zoneRows].sort((left, right) => left.year - right.year);
    const latest = ordered.find((item) => item.year === latestYear) ?? ordered[ordered.length - 1];
    const rankChangeCount = ordered.reduce((accumulator, item, index) => {
      if (index === 0) {
        return 0;
      }
      return accumulator + (ordered[index - 1].rank !== item.rank ? 1 : 0);
    }, 0);
    const bestRank = ordered.reduce((best, item) => Math.min(best, item.rank), ordered[0].rank);
    const bestMetricValue = ordered.reduce<number | null>((best, item) => {
      if (!isFiniteNumber(item.metric_value)) {
        return best;
      }
      if (!isFiniteNumber(best) || item.metric_value > best) {
        return item.metric_value;
      }
      return best;
    }, null);
    const currentRank = latest.rank;
    return {
      bestMetricValue,
      bestRank,
      currentRank,
      currentRankInFocus: currentRank <= rankFocusLimit,
      latestMetricValue: latest.metric_value,
      rankChangeCount,
      zoneKey,
      zoneName: latest.zone_name,
      currentRankIsLeader: latest.rank <= Math.min(currentSeriesLimit, rankFocusLimit),
    };
  });
}

function buildSelectedZoneKeys({
  currentLeaderKeys,
  rankFocusLimit,
  rows,
  seriesLimit,
  years,
  zoneStats,
}: {
  currentLeaderKeys: string[];
  rankFocusLimit: number;
  rows: HistoricalZoneRankingRecord[];
  seriesLimit: number;
  years: number[];
  zoneStats: ReturnType<typeof buildZoneStats>;
}) {
  const selectedZoneKeys = [...currentLeaderKeys];
  const candidateStats = zoneStats.filter((item) => !selectedZoneKeys.includes(item.zoneKey) && item.bestRank <= rankFocusLimit);
  let currentScore = computeSelectionCoverageScore(rows, years, selectedZoneKeys, rankFocusLimit);

  while (selectedZoneKeys.length < seriesLimit && candidateStats.length > 0) {
    let bestCandidateIndex = 0;
    let bestGain = -Infinity;

    for (let index = 0; index < candidateStats.length; index += 1) {
      const candidate = candidateStats[index];
      const nextScore = computeSelectionCoverageScore(rows, years, [...selectedZoneKeys, candidate.zoneKey], rankFocusLimit);
      const gain = nextScore - currentScore;
      const currentBest = candidateStats[bestCandidateIndex];
      if (gain > bestGain || (gain === bestGain && compareZoneStatsPriority(candidate, currentBest) < 0)) {
        bestCandidateIndex = index;
        bestGain = gain;
      }
    }

    const [selectedCandidate] = candidateStats.splice(bestCandidateIndex, 1);
    selectedZoneKeys.push(selectedCandidate.zoneKey);
    currentScore += bestGain === -Infinity ? 0 : bestGain;
  }

  return selectedZoneKeys;
}

function buildVisibleRanksByYear({
  rankFocusLimit,
  rows,
  selectedZoneKeys,
  years,
}: {
  rankFocusLimit: number;
  rows: HistoricalZoneRankingRecord[];
  selectedZoneKeys: string[];
  years: number[];
}) {
  const selectedSet = new Set(selectedZoneKeys);
  const visibleRanksByYear = new Map<number, Set<number>>();

  for (const year of years) {
    const ranks = rows
      .filter((item) => item.year === year && selectedSet.has(item.zone_key) && item.rank <= rankFocusLimit)
      .map((item) => item.rank)
      .sort((left, right) => left - right);
    const visibleRanks = new Set<number>();
    let expectedRank = 1;
    for (const rank of ranks) {
      if (rank !== expectedRank) {
        break;
      }
      visibleRanks.add(rank);
      expectedRank += 1;
    }
    visibleRanksByYear.set(year, visibleRanks);
  }

  return visibleRanksByYear;
}

function computeSelectionCoverageScore(
  rows: HistoricalZoneRankingRecord[],
  years: number[],
  selectedZoneKeys: string[],
  rankFocusLimit: number
) {
  const selectedSet = new Set(selectedZoneKeys);
  return years.reduce((score, year) => {
    const ranks = rows
      .filter((item) => item.year === year && selectedSet.has(item.zone_key) && item.rank <= rankFocusLimit)
      .map((item) => item.rank)
      .sort((left, right) => left - right);
    if (ranks.length === 0) {
      return score;
    }

    const prefixLength = countContiguousPrefix(ranks);
    const firstRank = ranks[0] ?? rankFocusLimit + 1;
    const outOfPrefixCount = Math.max(0, ranks.length - prefixLength);
    return score + prefixLength * 1000 - (firstRank - 1) * 500 - outOfPrefixCount * 5;
  }, 0);
}

function countContiguousPrefix(ranks: number[]) {
  let expectedRank = 1;
  const uniqueRanks = [...new Set(ranks)].sort((left, right) => left - right);
  for (const rank of uniqueRanks) {
    if (rank !== expectedRank) {
      break;
    }
    expectedRank += 1;
  }
  return expectedRank - 1;
}

function compareZoneStatsPriority(
  left: ReturnType<typeof buildZoneStats>[number],
  right: ReturnType<typeof buildZoneStats>[number]
) {
  if (left.bestRank !== right.bestRank) {
    return left.bestRank - right.bestRank;
  }
  if (left.currentRankInFocus !== right.currentRankInFocus) {
    return left.currentRankInFocus ? -1 : 1;
  }
  if (right.rankChangeCount !== left.rankChangeCount) {
    return right.rankChangeCount - left.rankChangeCount;
  }
  if ((right.latestMetricValue ?? -Infinity) !== (left.latestMetricValue ?? -Infinity)) {
    return (right.latestMetricValue ?? -Infinity) - (left.latestMetricValue ?? -Infinity);
  }
  return left.zoneName.localeCompare(right.zoneName, "es");
}

function buildSeriesPath(
  points: ChartPoint[],
  innerWidth: number,
  innerHeight: number,
  fallbackRank: number,
  totalYears: number
) {
  return points
    .map((point, index) => {
      const x = positionX(point.plotRank, innerWidth, fallbackRank);
      const y = positionY(index, totalYears, innerHeight);
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

function positionX(rank: number, innerWidth: number, fallbackRank: number) {
  if (fallbackRank <= 1) {
    return CHART_PADDING.left;
  }
  return CHART_PADDING.left + ((rank - 1) / (fallbackRank - 1)) * innerWidth;
}

function positionY(index: number, totalYears: number, innerHeight: number) {
  if (totalYears <= 1) {
    return CHART_PADDING.top + innerHeight / 2;
  }
  return CHART_PADDING.top + (index / (totalYears - 1)) * innerHeight;
}

function findNearestSeriesHover({
  chartHeightPx,
  chartWidthPx,
  pointerX,
  pointerY,
  relativeX,
  relativeY,
  seriesCollection,
}: {
  chartHeightPx: number;
  chartWidthPx: number;
  pointerX: number;
  pointerY: number;
  relativeX: number;
  relativeY: number;
  seriesCollection: Array<{
    points: Array<{ index: number; point: ChartPoint; x: number; y: number }>;
    series: ChartSeries;
  }>;
}): ChartHoverState | null {
  let bestMatch: {
    distanceSq: number;
    pointIndex: number;
    series: ChartSeries;
  } | null = null;

  for (const candidate of seriesCollection) {
    const nearest = findNearestPointIndexOnSeries(pointerX, pointerY, candidate.points);
    if (nearest === null) {
      continue;
    }

    if (!bestMatch || nearest.distanceSq < bestMatch.distanceSq) {
      bestMatch = {
        distanceSq: nearest.distanceSq,
        pointIndex: nearest.pointIndex,
        series: candidate.series,
      };
    }
  }

  if (!bestMatch) {
    return null;
  }

  const activePoint = bestMatch.series.points[bestMatch.pointIndex];
  const popoverLeft = clamp(relativeX + 16, 12, Math.max(12, chartWidthPx - HOVER_CARD_WIDTH - 12));
  const popoverTop = clamp(relativeY - HOVER_CARD_HEIGHT - 10, 12, Math.max(12, chartHeightPx - HOVER_CARD_HEIGHT - 12));

  return {
    nLocales: activePoint.nLocales,
    point: activePoint,
    popoverLeft,
    popoverTop,
    yearIndex: bestMatch.pointIndex,
    zoneContextName: bestMatch.series.zoneContextName,
    zoneKey: bestMatch.series.zoneKey,
    zoneName: bestMatch.series.zoneName,
  };
}

function findNearestPointIndexOnSeries(
  pointerX: number,
  pointerY: number,
  points: Array<{ index: number; point: ChartPoint; x: number; y: number }>
) {
  if (points.length === 0) {
    return null;
  }

  let bestDistanceSq = Infinity;
  let bestPointIndex = points[0].index;

  if (points.length === 1) {
    return {
      distanceSq: squaredDistance(pointerX, pointerY, points[0].x, points[0].y),
      pointIndex: points[0].index,
    };
  }

  for (let index = 0; index < points.length - 1; index += 1) {
    const start = points[index];
    const end = points[index + 1];
    const candidate = distanceToSegment(pointerX, pointerY, start.x, start.y, end.x, end.y);
    const nearestPointIndex = Math.abs(pointerY - start.y) <= Math.abs(pointerY - end.y) ? start.index : end.index;
    if (candidate.distanceSq < bestDistanceSq) {
      bestDistanceSq = candidate.distanceSq;
      bestPointIndex = nearestPointIndex;
    }
  }

  return { distanceSq: bestDistanceSq, pointIndex: bestPointIndex };
}

function distanceToSegment(px: number, py: number, ax: number, ay: number, bx: number, by: number) {
  const dx = bx - ax;
  const dy = by - ay;
  if (dx === 0 && dy === 0) {
    return { distanceSq: squaredDistance(px, py, ax, ay) };
  }

  const ratio = clamp(((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy), 0, 1);
  const closestX = ax + ratio * dx;
  const closestY = ay + ratio * dy;
  return { distanceSq: squaredDistance(px, py, closestX, closestY) };
}

function squaredDistance(ax: number, ay: number, bx: number, by: number) {
  const dx = ax - bx;
  const dy = ay - by;
  return dx * dx + dy * dy;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function formatCompact(value: number) {
  return new Intl.NumberFormat("es-ES", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function formatRankLabel(rank: number | null, rankFocusLimit: number) {
  if (!isFiniteNumber(rank) || rank > rankFocusLimit) {
    return "Fuera";
  }
  return `#${rank}`;
}

function formatPercent(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin dato";
  }
  return new Intl.NumberFormat("es-ES", { style: "percent", maximumFractionDigits: value < 0.1 ? 1 : 0 }).format(value);
}

function truncateLabel(value: string, maxLength: number) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, Math.max(0, maxLength - 1)).trimEnd()}…`;
}

function isFiniteNumber(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}