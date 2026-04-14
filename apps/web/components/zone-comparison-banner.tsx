"use client";

import { useMemo } from "react";

import type { HistoricalRankingArtifacts, HistoricalZoneLevel, HistoricalZoneRankingRecord } from "@/lib/types";

const LEFT_SERIES_COLOR = "#c46f4f";
const RIGHT_SERIES_COLOR = "#1e6b61";
const CHART_WIDTH = 320;
const CHART_HEIGHT = 172;
const CHART_PADDING = { top: 18, right: 14, bottom: 22, left: 42 };
const GRID_RATIOS = [0, 0.5, 1] as const;

type ZoneComparisonSelection = {
  leftZoneKey: string;
  rightZoneKey: string;
  zoneLevel: HistoricalZoneLevel;
};

type ZoneComparisonBannerProps = {
  artifacts: HistoricalRankingArtifacts | null;
  categoryCode: string;
  categoryDesc: string;
  comparison: ZoneComparisonSelection;
  isLoading: boolean;
  onClose: () => void;
};

type MetricKind = "rank" | "percent" | "count";

type MetricPoint = {
  left: number | null;
  right: number | null;
  year: number;
};

type MetricCardView = {
  higherIsBetter: boolean;
  id: string;
  kind: MetricKind;
  label: string;
  latestLeftValue: number | null;
  latestRightValue: number | null;
  note: string;
  points: MetricPoint[];
  zoneTotal: number | null;
};

type ZoneSeries = {
  displayLabel: string;
  latest: HistoricalZoneRankingRecord;
  rowsByYear: Map<number, HistoricalZoneRankingRecord>;
  shortLabel: string;
};

type ZoneCardView = {
  latestRankLabel: string;
  localesLabel: string;
  previewLabel: string;
  subtitle: string | null;
  title: string;
};

type ComparisonView = {
  baseYear: number;
  categoryDesc: string;
  footnote: string;
  intro: string;
  left: ZoneCardView;
  leftSeries: ZoneSeries;
  latestYear: number;
  latestYearIsPartial: boolean;
  levelLabel: string;
  metrics: MetricCardView[];
  right: ZoneCardView;
  rightSeries: ZoneSeries;
  summary: string;
  title: string;
};

export function ZoneComparisonBanner({
  artifacts,
  categoryCode,
  categoryDesc,
  comparison,
  isLoading,
  onClose,
}: ZoneComparisonBannerProps) {
  const view = useMemo(() => {
    if (!artifacts) {
      return null;
    }
    return buildZoneComparisonView({ artifacts, categoryCode, categoryDesc, comparison });
  }, [artifacts, categoryCode, categoryDesc, comparison]);

  const levelLabel = comparison.zoneLevel === "district" ? "distritos" : "barrios";

  return (
    <section aria-label={`Comparar ${levelLabel}`} aria-modal="false" className="zone-comparison-banner explain-banner explain-banner-floating" role="dialog">
      <div className="explain-banner-header">
        <div className="explain-banner-headcopy">
          <span className="explain-banner-kicker">Comparador territorial</span>
          <strong className="explain-banner-title">{view?.title ?? `Comparar ${levelLabel}`}</strong>
          <span className="explain-banner-summary">{view?.summary ?? `Ponemos dos ${levelLabel} cara a cara con lecturas simples y temporales.`}</span>
        </div>
        <button aria-label="Cerrar comparador territorial" className="explain-banner-close" onClick={onClose} type="button">
          Cerrar
        </button>
      </div>

      {isLoading && !artifacts ? (
        <div className="zone-comparison-empty">
          <strong>Preparando la serie histórica...</strong>
          <p>Estamos cargando las trayectorias anuales para poder comparar ambas zonas en el mismo corte.</p>
        </div>
      ) : !view ? (
        <div className="zone-comparison-empty">
          <strong>Comparativa no disponible</strong>
          <p>No hay suficiente serie histórica vigente para una de las zonas elegidas en esta categoría.</p>
        </div>
      ) : (
        <div className="zone-comparison-body">
          <p className="zone-comparison-intro">{view.intro}</p>

          <div className="zone-comparison-legend">
            <ZoneSummaryCard color={LEFT_SERIES_COLOR} zone={view.left} />
            <ZoneSummaryCard color={RIGHT_SERIES_COLOR} zone={view.right} />
          </div>

          <div className="zone-comparison-metrics">
            {view.metrics.map((metric) => (
              <MetricCard
                key={metric.id}
                latestYear={view.latestYear}
                latestYearIsPartial={view.latestYearIsPartial}
                leftSeries={view.leftSeries}
                metric={metric}
                rightSeries={view.rightSeries}
              />
            ))}
          </div>

          <p className="zone-comparison-footnote">{view.footnote}</p>
        </div>
      )}
    </section>
  );
}

function ZoneSummaryCard({ color, zone }: { color: string; zone: ZoneCardView }) {
  return (
    <article className="zone-comparison-zone-card">
      <div className="zone-comparison-zone-heading">
        <span aria-hidden="true" className="zone-comparison-zone-swatch" style={{ backgroundColor: color }} />
        <div className="zone-comparison-zone-copy">
          <strong className="zone-comparison-zone-title">{zone.title}</strong>
          {zone.subtitle ? <span className="zone-comparison-zone-context">{zone.subtitle}</span> : null}
        </div>
      </div>

      <div className="zone-comparison-zone-meta">
        <span className="zone-comparison-zone-chip">Hoy {zone.latestRankLabel}</span>
        <span className="zone-comparison-zone-chip">{zone.localesLabel}</span>
      </div>

      <p className="zone-comparison-zone-preview">{zone.previewLabel}</p>
    </article>
  );
}

function MetricCard({
  latestYear,
  latestYearIsPartial,
  leftSeries,
  metric,
  rightSeries,
}: {
  latestYear: number;
  latestYearIsPartial: boolean;
  leftSeries: ZoneSeries;
  metric: MetricCardView;
  rightSeries: ZoneSeries;
}) {
  return (
    <article className="zone-comparison-metric-card">
      <div className="zone-comparison-metric-head">
        <div className="zone-comparison-metric-title-row">
          <h3 className="zone-comparison-metric-title">{metric.label}</h3>
          <span className="zone-comparison-metric-lead">{buildMetricLeadLabel(metric, leftSeries.shortLabel, rightSeries.shortLabel)}</span>
        </div>
        <p className="zone-comparison-metric-note">{metric.note}</p>
      </div>

      <div className="zone-comparison-metric-latest">
        <MetricSeriesValue color={LEFT_SERIES_COLOR} label={leftSeries.displayLabel} value={formatMetricValue(metric.kind, metric.latestLeftValue)} />
        <MetricSeriesValue color={RIGHT_SERIES_COLOR} label={rightSeries.displayLabel} value={formatMetricValue(metric.kind, metric.latestRightValue)} />
      </div>

      <ComparisonTrendChart latestYear={latestYear} latestYearIsPartial={latestYearIsPartial} metric={metric} />
    </article>
  );
}

function MetricSeriesValue({ color, label, value }: { color: string; label: string; value: string }) {
  return (
    <div className="zone-comparison-metric-series">
      <span aria-hidden="true" className="zone-comparison-zone-swatch zone-comparison-zone-swatch-small" style={{ backgroundColor: color }} />
      <span className="zone-comparison-metric-series-name">{label}</span>
      <strong className="zone-comparison-metric-series-value">{value}</strong>
    </div>
  );
}

function ComparisonTrendChart({
  latestYear,
  latestYearIsPartial,
  metric,
}: {
  latestYear: number;
  latestYearIsPartial: boolean;
  metric: MetricCardView;
}) {
  const domain = resolveMetricDomain(metric);
  const innerWidth = CHART_WIDTH - CHART_PADDING.left - CHART_PADDING.right;
  const innerHeight = CHART_HEIGHT - CHART_PADDING.top - CHART_PADDING.bottom;
  const leftPath = buildMetricPath(metric, "left", domain);
  const rightPath = buildMetricPath(metric, "right", domain);
  const leftLastIndex = findLastPointIndex(metric.points, "left");
  const rightLastIndex = findLastPointIndex(metric.points, "right");
  const startYear = metric.points[0]?.year ?? latestYear;

  return (
    <div className="zone-comparison-chart-shell">
      <div className="zone-comparison-chart-frame">
        <svg className="zone-comparison-chart" viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img">
          {GRID_RATIOS.map((ratio) => {
            const y = CHART_PADDING.top + ratio * innerHeight;
            return (
              <line
                className="zone-comparison-chart-grid"
                key={`grid:${ratio}`}
                x1={CHART_PADDING.left}
                x2={CHART_WIDTH - CHART_PADDING.right}
                y1={y}
                y2={y}
              />
            );
          })}

          <text className="zone-comparison-chart-axis" x="0" y={CHART_PADDING.top + 4}>
            {formatAxisValue(metric.kind, domain.max, metric.zoneTotal, true)}
          </text>
          <text className="zone-comparison-chart-axis" x="0" y={CHART_HEIGHT - 2}>
            {formatAxisValue(metric.kind, domain.min, metric.zoneTotal, false)}
          </text>

          {leftPath ? <path d={leftPath} fill="none" stroke={LEFT_SERIES_COLOR} strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" /> : null}
          {rightPath ? <path d={rightPath} fill="none" stroke={RIGHT_SERIES_COLOR} strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" /> : null}

          {metric.points.map((point, index) => {
            const x = positionX(index, metric.points.length);
            const leftY = isFiniteNumber(point.left) ? positionY(point.left, metric.kind, domain.min, domain.max) : null;
            const rightY = isFiniteNumber(point.right) ? positionY(point.right, metric.kind, domain.min, domain.max) : null;
            return (
              <g key={`point:${metric.id}:${point.year}`}>
                {leftY !== null ? (
                  <circle
                    cx={x}
                    cy={leftY}
                    fill={LEFT_SERIES_COLOR}
                    r={index === leftLastIndex ? 4.8 : 3.6}
                    stroke="rgba(255, 255, 255, 0.96)"
                    strokeWidth="2"
                  />
                ) : null}
                {rightY !== null ? (
                  <circle
                    cx={x}
                    cy={rightY}
                    fill={RIGHT_SERIES_COLOR}
                    r={index === rightLastIndex ? 4.8 : 3.6}
                    stroke="rgba(255, 255, 255, 0.96)"
                    strokeWidth="2"
                  />
                ) : null}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="zone-comparison-chart-years">
        <span>{startYear}</span>
        <span>{latestYearIsPartial ? `${latestYear}*` : latestYear}</span>
      </div>
    </div>
  );
}

function buildZoneComparisonView({
  artifacts,
  categoryCode,
  categoryDesc,
  comparison,
}: {
  artifacts: HistoricalRankingArtifacts;
  categoryCode: string;
  categoryDesc: string;
  comparison: ZoneComparisonSelection;
}): ComparisonView | null {
  const rows = artifacts.zones[comparison.zoneLevel].filter((item) => item.category_code === categoryCode);
  if (rows.length === 0) {
    return null;
  }

  const leftSeries = buildZoneSeries(rows, comparison.leftZoneKey, comparison.zoneLevel);
  const rightSeries = buildZoneSeries(rows, comparison.rightZoneKey, comparison.zoneLevel);
  if (!leftSeries || !rightSeries) {
    return null;
  }

  const baseYear = artifacts.meta.years[0] ?? artifacts.meta.latest_year;
  const latestYear = artifacts.meta.latest_year;
  const years = artifacts.meta.years.filter((year) => year <= latestYear);
  const zoneTotal = artifacts.meta.zone_totals[comparison.zoneLevel];
  const metrics = categoryCode === "__all__"
    ? buildAllLocalesMetrics({ leftSeries, rightSeries, years, zoneTotal })
    : buildCategoryMetrics({ leftSeries, rightSeries, years, zoneTotal });

  if (metrics.length === 0) {
    return null;
  }

  const levelLabel = comparison.zoneLevel === "district" ? "Distritos" : "Barrios";
    const footnote = `Serie ${baseYear}-${latestYear}.`;

  return {
    baseYear,
    categoryDesc,
    footnote,
    intro: categoryCode === "__all__"
      ? "Aquí comparamos solo tres lecturas muy directas: puesto anual, número de locales y peso de la zona dentro de Madrid."
      : "Aquí comparamos solo tres lecturas muy directas: puesto anual, número de locales de la categoría y peso de esa categoría dentro de cada zona.",
    left: buildZoneCardView(leftSeries, categoryCode),
    leftSeries,
    latestYear,
    latestYearIsPartial: artifacts.meta.latest_year_is_partial,
    levelLabel,
    metrics,
    right: buildZoneCardView(rightSeries, categoryCode),
    rightSeries,
    summary: `${levelLabel} · ${categoryDesc}. ${buildComparisonSummary(metrics, leftSeries.shortLabel, rightSeries.shortLabel)}`,
    title: `${leftSeries.shortLabel} vs ${rightSeries.shortLabel}`,
  };
}

function buildZoneSeries(
  rows: HistoricalZoneRankingRecord[],
  zoneKey: string,
  zoneLevel: HistoricalZoneLevel
): ZoneSeries | null {
  const zoneRows = rows
    .filter((item) => item.zone_key === zoneKey)
    .sort(compareHistoricalRowsByTime);

  if (zoneRows.length === 0) {
    return null;
  }

  const latest = zoneRows[zoneRows.length - 1];
  const rowsByYear = new Map<number, HistoricalZoneRankingRecord>();

  for (const row of zoneRows) {
    rowsByYear.set(row.year, row);
  }

  return {
    displayLabel: formatZoneDisplayLabel(latest, zoneLevel),
    latest,
    rowsByYear,
    shortLabel: latest.zone_name,
  };
}

function buildZoneCardView(series: ZoneSeries, categoryCode: string): ZoneCardView {
  const latestZoneShare = categoryCode === "__all__"
    ? computeZoneShareOfMadrid(series.latest)
    : series.latest.share_of_zone;

  return {
    latestRankLabel: formatMetricValue("rank", series.latest.rank),
    localesLabel: `${formatCompact(series.latest.n_locales)} locales`,
    previewLabel: categoryCode === "__all__"
      ? `Peso Madrid ${formatMetricValue("percent", latestZoneShare)}`
      : `Peso local ${formatMetricValue("percent", latestZoneShare)}`,
    subtitle: series.latest.zone_context_name,
    title: series.latest.zone_name,
  };
}

function buildCategoryMetrics({
  leftSeries,
  rightSeries,
  years,
  zoneTotal,
}: {
  leftSeries: ZoneSeries;
  rightSeries: ZoneSeries;
  years: number[];
  zoneTotal: number;
}): MetricCardView[] {
  return [
    buildMetricCard({
      higherIsBetter: false,
      id: "rank",
      kind: "rank",
      label: "Puesto en Madrid",
      note: "Puesto anual de cada zona dentro del ranking de Madrid para esta categoría. Más arriba es mejor.",
      points: years.map((year) => ({
        left: leftSeries.rowsByYear.get(year)?.rank ?? null,
        right: rightSeries.rowsByYear.get(year)?.rank ?? null,
        year,
      })),
      zoneTotal,
    }),
    buildMetricCard({
      higherIsBetter: true,
      id: "category-locales",
      kind: "count",
      label: "Locales de la categoría",
      note: "Cuántos locales visibles de esta categoría hay en cada zona en cada año.",
      points: years.map((year) => ({
        left: leftSeries.rowsByYear.get(year)?.n_locales ?? null,
        right: rightSeries.rowsByYear.get(year)?.n_locales ?? null,
        year,
      })),
      zoneTotal: null,
    }),
    buildMetricCard({
      higherIsBetter: true,
      id: "share-of-zone",
      kind: "percent",
      label: "Peso en la zona",
      note: "Qué parte del propio distrito o barrio corresponde a esta categoría en cada corte anual.",
      points: years.map((year) => ({
        left: leftSeries.rowsByYear.get(year)?.share_of_zone ?? null,
        right: rightSeries.rowsByYear.get(year)?.share_of_zone ?? null,
        year,
      })),
      zoneTotal: null,
    }),
  ];
}

function buildAllLocalesMetrics({
  leftSeries,
  rightSeries,
  years,
  zoneTotal,
}: {
  leftSeries: ZoneSeries;
  rightSeries: ZoneSeries;
  years: number[];
  zoneTotal: number;
}): MetricCardView[] {
  return [
    buildMetricCard({
      higherIsBetter: false,
      id: "rank",
      kind: "rank",
      label: "Puesto en Madrid",
      note: "Puesto anual por ganancia o pérdida de peso dentro del total comercial de Madrid. Más arriba es mejor.",
      points: years.map((year) => ({
        left: leftSeries.rowsByYear.get(year)?.rank ?? null,
        right: rightSeries.rowsByYear.get(year)?.rank ?? null,
        year,
      })),
      zoneTotal,
    }),
    buildMetricCard({
      higherIsBetter: true,
      id: "total-locales",
      kind: "count",
      label: "Locales totales",
      note: "Cuántos locales visibles tiene cada zona en cada año.",
      points: years.map((year) => ({
        left: leftSeries.rowsByYear.get(year)?.n_locales ?? null,
        right: rightSeries.rowsByYear.get(year)?.n_locales ?? null,
        year,
      })),
      zoneTotal: null,
    }),
    buildMetricCard({
      higherIsBetter: true,
      id: "share-of-city-total",
      kind: "percent",
      label: "Peso en Madrid",
      note: "Qué parte de todos los locales de Madrid cae dentro de cada zona en cada año.",
      points: years.map((year) => ({
        left: computeZoneShareOfMadrid(leftSeries.rowsByYear.get(year)),
        right: computeZoneShareOfMadrid(rightSeries.rowsByYear.get(year)),
        year,
      })),
      zoneTotal: null,
    }),
  ];
}

function buildMetricCard({
  higherIsBetter,
  id,
  kind,
  label,
  note,
  points,
  zoneTotal,
}: {
  higherIsBetter: boolean;
  id: string;
  kind: MetricKind;
  label: string;
  note: string;
  points: MetricPoint[];
  zoneTotal: number | null;
}): MetricCardView {
  return {
    higherIsBetter,
    id,
    kind,
    label,
    latestLeftValue: findLatestMetricValue(points, "left"),
    latestRightValue: findLatestMetricValue(points, "right"),
    note,
    points,
    zoneTotal,
  };
}

function buildComparisonSummary(metrics: MetricCardView[], leftLabel: string, rightLabel: string) {
  const leaders = metrics.map((metric) => resolveMetricLeader(metric));
  const leftWins = leaders.filter((item) => item === "left").length;
  const rightWins = leaders.filter((item) => item === "right").length;
  const ties = leaders.filter((item) => item === "tie").length;

  if (leftWins === 0 && rightWins === 0) {
    return "La foto actual sale empatada en todas las lecturas útiles.";
  }

  if (leftWins === rightWins) {
    return `La foto actual está equilibrada: ${leftLabel} manda en ${leftWins} lecturas y ${rightLabel} en ${rightWins}.`;
  }

  const leaderLabel = leftWins > rightWins ? leftLabel : rightLabel;
  const winCount = Math.max(leftWins, rightWins);
  const tieTail = ties > 0
    ? ` Queda${ties > 1 ? "n" : ""} ${ties} empate${ties > 1 ? "s" : ""} técnico${ties > 1 ? "s" : ""}.`
    : "";
  return `${leaderLabel} llega hoy por delante en ${winCount} de ${metrics.length} lecturas.${tieTail}`;
}

function buildMetricLeadLabel(metric: MetricCardView, leftLabel: string, rightLabel: string) {
  const leader = resolveMetricLeader(metric);
  if (leader === "tie") {
    return "Empate técnico";
  }

  const leftValue = metric.latestLeftValue;
  const rightValue = metric.latestRightValue;
  if (!isFiniteNumber(leftValue) && !isFiniteNumber(rightValue)) {
    return "Sin lectura actual";
  }

  const leaderLabel = leader === "left" ? leftLabel : rightLabel;
  if (!isFiniteNumber(leftValue) || !isFiniteNumber(rightValue)) {
    return `${leaderLabel} sí tiene corte actual`;
  }

  if (metric.kind === "rank") {
    return `${leaderLabel} mejor por ${Math.abs(Math.round(leftValue - rightValue))} puestos`;
  }

  return `${leaderLabel} manda por ${formatMetricDifference(metric.kind, Math.abs(leftValue - rightValue))}`;
}

function resolveMetricLeader(metric: MetricCardView) {
  const left = metric.latestLeftValue;
  const right = metric.latestRightValue;

  if (!isFiniteNumber(left) && !isFiniteNumber(right)) {
    return "tie" as const;
  }
  if (!isFiniteNumber(left)) {
    return "right" as const;
  }
  if (!isFiniteNumber(right)) {
    return "left" as const;
  }

  const threshold = metric.kind === "rank"
    ? 0.5
    : metric.kind === "count"
      ? 0.5
      : 0.0005;
  if (Math.abs(left - right) <= threshold) {
    return "tie" as const;
  }

  if (metric.higherIsBetter) {
    return left > right ? "left" as const : "right" as const;
  }

  return left < right ? "left" as const : "right" as const;
}

function findLatestMetricValue(points: MetricPoint[], key: "left" | "right") {
  for (let index = points.length - 1; index >= 0; index -= 1) {
    const value = points[index][key];
    if (isFiniteNumber(value)) {
      return value;
    }
  }
  return null;
}

function findLastPointIndex(points: MetricPoint[], key: "left" | "right") {
  for (let index = points.length - 1; index >= 0; index -= 1) {
    if (isFiniteNumber(points[index][key])) {
      return index;
    }
  }
  return -1;
}

function resolveMetricDomain(metric: MetricCardView) {
  if (metric.kind === "rank" && isFiniteNumber(metric.zoneTotal)) {
    return { max: metric.zoneTotal, min: 1 };
  }

  const values = metric.points
    .flatMap((point) => [point.left, point.right])
    .filter(isFiniteNumber);

  if (values.length === 0) {
    return { max: 1, min: 0 };
  }

  let min = Math.min(...values);
  let max = Math.max(...values);

  const basePadding = max === min
    ? metric.kind === "percent"
      ? 0.005
      : Math.max(1, Math.abs(max) * 0.15)
    : (max - min) * 0.16;

  min -= basePadding;
  max += basePadding;

  if (metric.kind === "percent") {
    min = Math.max(0, min);
  }

  return { max, min };
}

function buildMetricPath(metric: MetricCardView, key: "left" | "right", domain: { max: number; min: number }) {
  let hasStarted = false;
  let path = "";

  metric.points.forEach((point, index) => {
    const value = point[key];
    if (!isFiniteNumber(value)) {
      hasStarted = false;
      return;
    }

    const x = positionX(index, metric.points.length);
    const y = positionY(value, metric.kind, domain.min, domain.max);
    path += `${hasStarted ? " L" : "M"}${x.toFixed(2)} ${y.toFixed(2)}`;
    hasStarted = true;
  });

  return path;
}

function positionX(index: number, totalPoints: number) {
  const innerWidth = CHART_WIDTH - CHART_PADDING.left - CHART_PADDING.right;
  if (totalPoints <= 1) {
    return CHART_PADDING.left + innerWidth / 2;
  }
  return CHART_PADDING.left + (index / (totalPoints - 1)) * innerWidth;
}

function positionY(value: number, kind: MetricKind, min: number, max: number) {
  const innerHeight = CHART_HEIGHT - CHART_PADDING.top - CHART_PADDING.bottom;
  const safeRange = max - min <= 1e-9 ? 1 : max - min;
  const ratio = kind === "rank"
    ? (value - min) / safeRange
    : 1 - (value - min) / safeRange;
  return CHART_PADDING.top + clamp(ratio, 0, 1) * innerHeight;
}

function computeZoneShareOfMadrid(row: HistoricalZoneRankingRecord | undefined) {
  if (!row || row.city_total_locales <= 0) {
    return null;
  }
  return row.n_locales / row.city_total_locales;
}

function formatMetricValue(kind: MetricKind, value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin dato";
  }

  if (kind === "rank") {
    return `#${Math.round(value)}`;
  }

  if (kind === "count") {
    return formatCompact(value);
  }

  return new Intl.NumberFormat("es-ES", {
    maximumFractionDigits: 1,
    style: "percent",
  }).format(value);
}

function formatMetricDifference(kind: MetricKind, value: number) {
  if (kind === "rank") {
    return `${Math.round(value)} puestos`;
  }

  if (kind === "count") {
    return `${formatCompact(value)} locales`;
  }

  return new Intl.NumberFormat("es-ES", {
    maximumFractionDigits: 1,
    style: "percent",
  }).format(value);
}

function formatAxisValue(kind: MetricKind, value: number, zoneTotal: number | null, isTop: boolean) {
  if (kind === "rank") {
    if (isTop) {
      return "#1";
    }
    return isFiniteNumber(zoneTotal) ? `#${Math.round(zoneTotal)}` : `#${Math.round(value)}`;
  }

  if (kind === "count") {
    return formatCompact(value);
  }

  return formatMetricValue(kind, value);
}

function compareHistoricalRowsByTime(left: HistoricalZoneRankingRecord, right: HistoricalZoneRankingRecord) {
  if (left.year !== right.year) {
    return left.year - right.year;
  }
  return left.period.localeCompare(right.period, "es");
}

function formatZoneDisplayLabel(row: HistoricalZoneRankingRecord, zoneLevel: HistoricalZoneLevel) {
  if (zoneLevel === "district" || !row.zone_context_name) {
    return row.zone_name;
  }
  return `${row.zone_name} · ${row.zone_context_name}`;
}

function formatCompact(value: number) {
  return new Intl.NumberFormat("es-ES", { maximumFractionDigits: 1, notation: "compact" }).format(value);
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function isFiniteNumber(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}