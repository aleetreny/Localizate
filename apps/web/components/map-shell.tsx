"use client";

import { useMemo, useState } from "react";

import { MadridMap } from "@/components/madrid-map";
import type { ColorScale, FrontendArtifacts, HexAggregate } from "@/lib/types";

type Horizon = "12m" | "24m";

type MapShellProps = {
  initialArtifacts: FrontendArtifacts;
};

export function MapShell({ initialArtifacts }: MapShellProps) {
  const [selectedCategory, setSelectedCategory] = useState(initialArtifacts.meta.defaultCategoryCode);
  const [horizon, setHorizon] = useState<Horizon>("24m");
  const [selectedHex, setSelectedHex] = useState<HexAggregate | null>(null);

  const filteredHexes = useMemo(() => {
    return initialArtifacts.hexes.filter((item) => item.category_code === selectedCategory);
  }, [initialArtifacts.hexes, selectedCategory]);

  const colorScale = useMemo(() => buildColorScale(filteredHexes, horizon), [filteredHexes, horizon]);

  const activeStats = useMemo(() => {
    if (filteredHexes.length === 0) {
      return {
        locales: 0,
        hexes: 0,
        meanSurvival: 0,
        meanRisk: 0
      };
    }

    const locales = filteredHexes.reduce((sum, item) => sum + item.n_locales, 0);
    const meanSurvival =
      filteredHexes.reduce(
        (sum, item) => sum + item.n_locales * (horizon === "24m" ? item.survival_24m : item.survival_12m),
        0
      ) / locales;
    const meanRisk = filteredHexes.reduce((sum, item) => sum + item.n_locales * item.avg_risk_ensemble, 0) / locales;

    return {
      locales,
      hexes: filteredHexes.length,
      meanSurvival,
      meanRisk
    };
  }, [filteredHexes, horizon]);

  const detail = selectedHex ?? filteredHexes[0] ?? null;

  return (
    <main className="app-shell">
      <aside className="sidebar panel">
        <div>
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
            {initialArtifacts.categories.map((category) => (
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
            <span className="value">{formatPercent(activeStats.meanSurvival)}</span>
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

        <section className="detail-card">
          <div className="eyebrow">Detalle activo</div>
          {detail ? (
            <>
              <h2>{detail.category_desc}</h2>
              <p>Hex {detail.h3_cell}</p>
              <div className="detail-meta">
                <span className="chip">{detail.n_locales} locales</span>
                <span className="chip">Surv {horizon === "24m" ? formatPercent(detail.survival_24m) : formatPercent(detail.survival_12m)}</span>
                <span className="chip">Risk {detail.avg_risk_ensemble.toFixed(2)}</span>
              </div>
              <p>
                Soporte 12m: {detail.support_12m} observaciones. Soporte 24m: {detail.support_24m} observaciones.
              </p>
            </>
          ) : (
            <>
              <h3>Sin datos visibles</h3>
              <p>Ajusta el filtro de categoría.</p>
            </>
          )}
        </section>
      </aside>

      <section className="map-panel panel">
        <MadridMap
          bounds={initialArtifacts.meta.map_bounds}
          colorScale={colorScale}
          horizon={horizon}
          hexes={filteredHexes}
          onSelectHex={setSelectedHex}
          selectedHex={detail}
        />
      </section>
    </main>
  );
}

function formatPercent(value: number) {
  return `${(value * 100).toFixed(0)}%`;
}

function formatCompact(value: number) {
  return new Intl.NumberFormat("es-ES", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function buildColorScale(hexes: HexAggregate[], horizon: Horizon): ColorScale {
  const values = hexes
    .map((item) => (horizon === "24m" ? item.survival_24m : item.survival_12m))
    .filter((value) => Number.isFinite(value))
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