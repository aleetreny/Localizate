"use client";

import type { Color, PickingInfo } from "@deck.gl/core";
import { H3HexagonLayer } from "@deck.gl/geo-layers";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { useCallback, useLayoutEffect, useMemo, useRef, useState } from "react";
import Map, { NavigationControl, useControl, type ViewState } from "react-map-gl/maplibre";

import { formatHorizonShortLabel, getHorizonSurvival, isFiniteNumber, type Horizon } from "@/lib/horizon";
import { computeTooltipPosition } from "@/lib/tooltip-position";
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
  const [hoveredHexCell, setHoveredHexCell] = useState<string | null>(null);
  const minZoom = getMinZoom(bounds);
  const clearHoverState = useCallback(() => {
    setTooltip(null);
    setHoveredHexCell(null);
  }, []);

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

    setTooltipPosition(
      computeTooltipPosition({
        anchor: { x: tooltip.x, y: tooltip.y },
        tooltip: { width: bubble.offsetWidth, height: bubble.offsetHeight },
        viewport: { width: container.clientWidth, height: container.clientHeight }
      })
    );
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
        lineWidthMaxPixels: 10,
        getLineWidth: (item) =>
          selectedHex?.h3_cell === item.h3_cell ? 3 : hoveredHexCell === item.h3_cell ? 2 : 0.6,
        getLineColor: (item) => {
          if (selectedHex?.h3_cell === item.h3_cell) {
            return [6, 39, 46, 255];
          }
          if (hoveredHexCell === item.h3_cell) {
            return [255, 180, 0, 255];
          }
          return [255, 255, 255, 70];
        },
        getHexagon: (item) => item.h3_cell,
        getFillColor: (item) => colorForSurvival(getHorizonSurvival(item, horizon), colorScale),
        updateTriggers: {
          getFillColor: [horizon, colorScale.min, colorScale.low, colorScale.mid, colorScale.high, colorScale.max],
          getLineColor: [selectedHex?.h3_cell, hoveredHexCell],
          getLineWidth: [selectedHex?.h3_cell, hoveredHexCell]
        },
        onHover: (info: PickingInfo<HexAggregate>) => {
          if (!info.object || info.x === undefined || info.y === undefined) {
            clearHoverState();
            return;
          }
          setTooltip({ x: info.x, y: info.y, object: info.object });
          setHoveredHexCell(info.object.h3_cell);
        },
        onClick: (info: PickingInfo<HexAggregate>) => {
          onSelectHex(info.object ?? null);
        }
      })
    ];
  }, [clearHoverState, colorScale.high, colorScale.low, colorScale.max, colorScale.mid, colorScale.min, hexes, horizon, onSelectHex, selectedHex?.h3_cell, hoveredHexCell]);

  return (
    <div className="map-canvas" onPointerLeave={clearHoverState} ref={containerRef}>
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
          </div>
          <div className="tooltip-grid">
            <div className="tooltip-item">
              <span className="tooltip-label">Supervivencia {formatHorizonShortLabel(horizon)}</span>
              <strong className="tooltip-value">{formatTooltipPercent(getHorizonSurvival(tooltip.object, horizon))}</strong>
            </div>
            <div className="tooltip-item">
              <span className="tooltip-label">Índice relativo 0-1</span>
              <strong className="tooltip-value">{formatRelativeRiskIndex(tooltip.object.avg_risk_percentile)}</strong>
            </div>
          </div>
            <small className="tooltip-note">Haz clic para fijar el hexágono y abrir su ficha completa.</small>
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

function formatRelativeRiskIndex(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  const clamped = Math.max(0, Math.min(1, value));
  return new Intl.NumberFormat("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(clamped);
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