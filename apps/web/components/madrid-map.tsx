"use client";

import type { Color, PickingInfo } from "@deck.gl/core";
import { H3HexagonLayer } from "@deck.gl/geo-layers";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import Map, { NavigationControl, useControl, type ViewState } from "react-map-gl/maplibre";

import { formatHorizonShortLabel, getHorizonSupport, getHorizonSurvival, isFiniteNumber, type Horizon } from "@/lib/horizon";
import type { Bounds, ColorScale, HexAggregate } from "@/lib/types";

type MadridMapProps = {
  bounds: Bounds;
  colorScale: ColorScale;
  hexes: HexAggregate[];
  horizon: Horizon;
  selectedHex: HexAggregate | null;
  onSelectHex: (hex: HexAggregate | null) => void;
};

type TooltipState = {
  x: number;
  y: number;
  object: HexAggregate;
} | null;

const MAP_STYLE = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json";
const INITIAL_ZOOM_INSET = 0.45;
const INITIAL_LATITUDE_FOCUS_RATIO = 0.36;

export function MadridMap({ bounds, colorScale, hexes, horizon, selectedHex, onSelectHex }: MadridMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{ left: number; top: number } | null>(null);
  const minZoom = getMinZoom(bounds);

  useLayoutEffect(() => {
    if (!tooltip) {
      setTooltipPosition(null);
      return;
    }

    const container = containerRef.current;
    const bubble = tooltipRef.current;

    if (!container || !bubble) {
      return;
    }

    const padding = 12;
    const offset = 14;
    const maxLeft = Math.max(padding, container.clientWidth - bubble.offsetWidth - padding);
    const maxTop = Math.max(padding, container.clientHeight - bubble.offsetHeight - padding);

    setTooltipPosition({
      left: clamp(tooltip.x + offset, padding, maxLeft),
      top: clamp(tooltip.y + offset, padding, maxTop)
    });
  }, [tooltip, horizon]);

  const layers = useMemo(() => {
    return [
      new H3HexagonLayer<HexAggregate>({
        id: "madrid-h3-layer",
        data: hexes,
        pickable: true,
        filled: true,
        extruded: false,
        wireframe: false,
        opacity: 0.46,
        stroked: true,
        lineWidthMinPixels: 0.6,
        getLineColor: (item) =>
          selectedHex?.h3_cell === item.h3_cell ? [6, 39, 46, 255] : [255, 255, 255, 70],
        getHexagon: (item) => item.h3_cell,
        getFillColor: (item) => colorForSurvival(getHorizonSurvival(item, horizon), colorScale),
        updateTriggers: {
          getFillColor: [horizon, colorScale.min, colorScale.low, colorScale.mid, colorScale.high, colorScale.max],
          getLineColor: [selectedHex?.h3_cell]
        },
        onHover: (info: PickingInfo<HexAggregate>) => {
          if (!info.object || info.x === undefined || info.y === undefined) {
            setTooltip(null);
            return;
          }
          setTooltip({ x: info.x, y: info.y, object: info.object });
        },
        onClick: (info: PickingInfo<HexAggregate>) => {
          onSelectHex(info.object ?? null);
        }
      })
    ];
  }, [colorScale.high, colorScale.low, colorScale.max, colorScale.mid, colorScale.min, hexes, horizon, onSelectHex, selectedHex?.h3_cell]);

  return (
    <div className="map-canvas" ref={containerRef}>
      <Map
        key={buildBoundsKey(bounds)}
        initialViewState={buildInitialViewState(bounds, minZoom)}
        mapStyle={MAP_STYLE}
        minZoom={minZoom}
        maxZoom={bounds.max_zoom}
        maxBounds={[
          [bounds.min_lng, bounds.min_lat],
          [bounds.max_lng, bounds.max_lat]
        ]}
        dragPan
        scrollZoom
        doubleClickZoom
        touchZoomRotate={false}
        dragRotate={false}
        pitchWithRotate={false}
        touchPitch={false}
        maxPitch={0}
        renderWorldCopies={false}
        reuseMaps
        style={{ width: "100%", height: "100%" }}
      >
        <NavigationControl position="bottom-right" showCompass={false} />
        <DeckOverlay layers={layers} />
      </Map>

      {tooltip ? (
        <div
          className="tooltip"
          ref={tooltipRef}
          style={tooltipPosition ? tooltipPosition : { left: 0, top: 0, visibility: "hidden" }}
        >
          <span className="tooltip-kicker">Hexágono histórico</span>
          <strong className="tooltip-title">{tooltip.object.category_desc}</strong>
          <span className="tooltip-subtitle">{tooltip.object.location_label}</span>
          <div className="tooltip-badges">
            <span className="tooltip-chip">{tooltip.object.n_locales} locales</span>
            <span className="tooltip-chip">{formatTooltipRiskPercentile(tooltip.object.avg_risk_percentile)}</span>
          </div>
          <div className="tooltip-grid">
            <div className="tooltip-item">
              <span className="tooltip-label">Supervivencia {formatHorizonShortLabel(horizon)}</span>
              <strong className="tooltip-value">{formatTooltipPercent(getHorizonSurvival(tooltip.object, horizon))}</strong>
            </div>
            <div className="tooltip-item">
              <span className="tooltip-label">Soporte {formatHorizonShortLabel(horizon)}</span>
              <strong className="tooltip-value">{getHorizonSupport(tooltip.object, horizon)}/{tooltip.object.n_locales}</strong>
            </div>
            <div className="tooltip-item">
              <span className="tooltip-label">Riesgo medio</span>
              <strong className="tooltip-value">{tooltip.object.avg_risk_ensemble.toFixed(2)}</strong>
            </div>
          </div>
          {getHorizonSupport(tooltip.object, horizon) <= 0 ? <small className="tooltip-note">Sin soporte suficiente para este horizonte.</small> : null}
          <small className="tooltip-note">Haz click para fijar el hexágono y abrir su ficha completa.</small>
        </div>
      ) : null}
    </div>
  );
}

function DeckOverlay({ layers }: { layers: H3HexagonLayer<HexAggregate>[] }) {
  const overlay = useControl<MapboxOverlay>(() => new MapboxOverlay({ interleaved: false }));

  overlay.setProps({
    layers,
    getCursor: ({ isDragging, isHovering }) => {
      if (isDragging) {
        return "grabbing";
      }
      return isHovering ? "pointer" : "grab";
    }
  });

  return null;
}

function buildInitialViewState(bounds: Bounds, minZoom: number): ViewState {
  return {
    longitude: (bounds.min_lng + bounds.max_lng) / 2,
    latitude: bounds.min_lat + (bounds.max_lat - bounds.min_lat) * INITIAL_LATITUDE_FOCUS_RATIO,
    zoom: minZoom,
    pitch: 0,
    bearing: 0,
    padding: { top: 0, right: 0, bottom: 0, left: 0 }
  };
}

function getMinZoom(bounds: Bounds) {
  return Math.min(bounds.max_zoom, bounds.min_zoom + INITIAL_ZOOM_INSET);
}

function buildBoundsKey(bounds: Bounds) {
  return [bounds.min_lng, bounds.min_lat, bounds.max_lng, bounds.max_lat, bounds.min_zoom, bounds.max_zoom].join(":");
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function colorForSurvival(value: number | null, scale: ColorScale): Color {
  if (!isFiniteNumber(value)) {
    return [136, 142, 147, 96];
  }

  const anchors = [scale.min, scale.low, scale.mid, scale.high, scale.max];
  const palette: ReadonlyArray<Color> = [
    [156, 56, 32, 232],
    [196, 106, 52, 224],
    [228, 192, 122, 214],
    [142, 181, 156, 216],
    [27, 112, 123, 230]
  ];

  if (anchors[0] === anchors[4]) {
    return palette[2];
  }

  if (value <= anchors[0]) {
    return palette[0];
  }

  if (value >= anchors[4]) {
    return palette[4];
  }

  for (let index = 0; index < anchors.length - 1; index += 1) {
    const left = anchors[index];
    const right = anchors[index + 1];
    if (value <= right) {
      const span = right - left || 1;
      const ratio = (value - left) / span;
      return interpolateColor(palette[index], palette[index + 1], ratio);
    }
  }

  return palette[4];
}

function formatTooltipPercent(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin muestra";
  }
  return `${(value * 100).toFixed(0)}%`;
}

function formatTooltipRiskPercentile(value: number) {
  const clamped = Math.max(0, Math.min(1, value));
  return `P${Math.round(clamped * 100)} riesgo`;
}

function interpolateColor(left: Color, right: Color, ratio: number): Color {
  const clamped = Math.max(0, Math.min(1, ratio));
  const leftAlpha = left[3] ?? 255;
  const rightAlpha = right[3] ?? 255;
  return [
    Math.round(left[0] + (right[0] - left[0]) * clamped),
    Math.round(left[1] + (right[1] - left[1]) * clamped),
    Math.round(left[2] + (right[2] - left[2]) * clamped),
    Math.round(leftAlpha + (rightAlpha - leftAlpha) * clamped)
  ] as const;
}