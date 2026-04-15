"use client";

import type { Color, Layer, PickingInfo } from "@deck.gl/core";
import { H3HexagonLayer } from "@deck.gl/geo-layers";
import { GeoJsonLayer } from "@deck.gl/layers";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { useCallback, useLayoutEffect, useMemo, useRef, useState } from "react";
import MapLibreMap, { NavigationControl, useControl, type ViewState } from "react-map-gl/maplibre";

import { formatHorizonShortLabel, getHorizonSurvival, isFiniteNumber, type Horizon } from "@/lib/horizon";
import { computeTooltipPosition } from "@/lib/tooltip-position";
import type { Bounds, ColorScale, HexAggregate, HistoricalZoneLevel, ZoneAggregate, ZoneBoundaryFeature } from "@/lib/types";

type MapViewMode = HistoricalZoneLevel | "hex";

type MadridMapProps = {
  bounds: Bounds;
  colorScale: ColorScale;
  hexes: HexAggregate[];
  horizon: Horizon;
  mapViewMode: MapViewMode;
  onSelectHex: (hex: HexAggregate | null) => void;
  onSelectZone: (zone: ZoneAggregate | null) => void;
  selectedHex: HexAggregate | null;
  selectedZone: ZoneAggregate | null;
  zoneBoundaries: ZoneBoundaryFeature[];
  zoneColorFloorLocales: number;
  zones: ZoneAggregate[];
};

type TooltipState =
  | {
      kind: "hex";
      object: HexAggregate;
      x: number;
      y: number;
    }
  | {
      feature: ZoneBoundaryFeature;
      kind: "zone";
      object: ZoneAggregate | null;
      x: number;
      y: number;
    }
  | null;

const MAP_STYLE = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json";
const INITIAL_ZOOM_INSET = 0.45;
const INITIAL_LATITUDE_FOCUS_RATIO = 0.36;
const HEX_LAYER_OPACITY = 0.4;
const ZONE_LAYER_OPACITY = 0.62;

export function MadridMap({
  bounds,
  colorScale,
  hexes,
  horizon,
  mapViewMode,
  onSelectHex,
  onSelectZone,
  selectedHex,
  selectedZone,
  zoneBoundaries,
  zoneColorFloorLocales,
  zones,
}: MadridMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{ left: number; top: number } | null>(null);
  const [hoveredHexCell, setHoveredHexCell] = useState<string | null>(null);
  const [hoveredZoneCode, setHoveredZoneCode] = useState<string | null>(null);
  const minZoom = getMinZoom(bounds);

  const clearHoverState = useCallback(() => {
    setTooltip(null);
    setHoveredHexCell(null);
    setHoveredZoneCode(null);
  }, []);

  const zoneLookup = useMemo(() => {
    const nextLookup = new Map<string, ZoneAggregate>();
    for (const zone of zones) {
      nextLookup.set(zone.zone_code, zone);
    }
    return nextLookup;
  }, [zones]);

  const renderedZoneBoundaries = useMemo(() => {
    return zoneBoundaries.filter((feature) => feature.geometry !== null);
  }, [zoneBoundaries]);

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
        viewport: { width: container.clientWidth, height: container.clientHeight },
      })
    );
  }, [horizon, mapViewMode, tooltip]);

  const layers = useMemo<Layer[]>(() => {
    if (mapViewMode === "hex") {
      return [
        new H3HexagonLayer<HexAggregate>({
          id: "madrid-h3-layer",
          data: hexes,
          pickable: true,
          filled: true,
          extruded: false,
          wireframe: false,
          opacity: HEX_LAYER_OPACITY,
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
          getFillColor: (item) => colorForRelativeRiskIndex(item.avg_risk_percentile, colorScale),
          updateTriggers: {
            getFillColor: [colorScale.min, colorScale.low, colorScale.mid, colorScale.high, colorScale.max],
            getLineColor: [selectedHex?.h3_cell, hoveredHexCell],
            getLineWidth: [selectedHex?.h3_cell, hoveredHexCell],
          },
          onHover: (info: PickingInfo<HexAggregate>) => {
            if (!info.object || info.x === undefined || info.y === undefined) {
              clearHoverState();
              return;
            }
            setTooltip({ x: info.x, y: info.y, kind: "hex", object: info.object });
            setHoveredHexCell(info.object.h3_cell);
          },
          onClick: (info: PickingInfo<HexAggregate>) => {
            onSelectHex(info.object ?? null);
          },
        }),
      ];
    }

    const selectedZoneCode =
      selectedZone?.zone_level === mapViewMode ? selectedZone.zone_code : null;
    const selectedZoneFeature = selectedZoneCode
      ? renderedZoneBoundaries.find((feature) => feature.properties.zone_code === selectedZoneCode) ?? null
      : null;
    const hoveredZoneFeature =
      hoveredZoneCode && hoveredZoneCode !== selectedZoneCode
        ? renderedZoneBoundaries.find((feature) => feature.properties.zone_code === hoveredZoneCode) ?? null
        : null;

    const zoneLayers: Layer[] = [
      new GeoJsonLayer<any>({
        id: `madrid-zone-layer:${mapViewMode}`,
        data: renderedZoneBoundaries as never,
        pickable: true,
        filled: true,
        stroked: true,
        lineWidthMinPixels: 0.9,
        lineWidthMaxPixels: 12,
        opacity: ZONE_LAYER_OPACITY,
        getFillColor: (feature) => {
          const zone = zoneLookup.get(feature.properties.zone_code) ?? null;
          return colorForZone(zone, colorScale, zoneColorFloorLocales);
        },
        getLineColor: [255, 255, 255, 92],
        getLineWidth: 1,
        updateTriggers: {
          getFillColor: [
            mapViewMode,
            colorScale.min,
            colorScale.low,
            colorScale.mid,
            colorScale.high,
            colorScale.max,
            zoneColorFloorLocales,
            zones,
          ],
        },
        onHover: (info: PickingInfo<ZoneBoundaryFeature>) => {
          if (!info.object || info.x === undefined || info.y === undefined) {
            clearHoverState();
            return;
          }

          const zone = zoneLookup.get(info.object.properties.zone_code) ?? null;
          setTooltip({ x: info.x, y: info.y, feature: info.object, kind: "zone", object: zone });
          setHoveredZoneCode(info.object.properties.zone_code);
        },
        onClick: (info: PickingInfo<ZoneBoundaryFeature>) => {
          if (!info.object) {
            onSelectZone(null);
            return;
          }
          onSelectZone(zoneLookup.get(info.object.properties.zone_code) ?? null);
        },
      }),
    ];

    if (hoveredZoneFeature) {
      zoneLayers.push(
        new GeoJsonLayer<any>({
          id: `madrid-zone-layer:${mapViewMode}:hover-outline`,
          data: [hoveredZoneFeature] as never,
          pickable: false,
          filled: false,
          stroked: true,
          lineWidthMinPixels: 2,
          lineWidthMaxPixels: 16,
          getLineColor: [255, 180, 0, 255],
          getLineWidth: 2.4,
        })
      );
    }

    if (selectedZoneFeature) {
      zoneLayers.push(
        new GeoJsonLayer<any>({
          id: `madrid-zone-layer:${mapViewMode}:selected-outline`,
          data: [selectedZoneFeature] as never,
          pickable: false,
          filled: false,
          stroked: true,
          lineWidthMinPixels: 3,
          lineWidthMaxPixels: 18,
          getLineColor: [6, 39, 46, 255],
          getLineWidth: 3.6,
        })
      );
    }

    return zoneLayers;
  }, [
    clearHoverState,
    colorScale.high,
    colorScale.low,
    colorScale.max,
    colorScale.mid,
    colorScale.min,
    hexes,
    hoveredHexCell,
    hoveredZoneCode,
    mapViewMode,
    onSelectHex,
    onSelectZone,
    renderedZoneBoundaries,
    selectedHex?.h3_cell,
    selectedZone?.zone_code,
    selectedZone?.zone_level,
    zoneColorFloorLocales,
    zoneLookup,
    zones,
  ]);

  return (
    <div className="map-canvas" onPointerLeave={clearHoverState} ref={containerRef}>
      <MapLibreMap
        key={buildBoundsKey(bounds)}
        initialViewState={buildInitialViewState(bounds, minZoom)}
        mapStyle={MAP_STYLE}
        minZoom={minZoom}
        maxZoom={bounds.max_zoom}
        maxBounds={[
          [bounds.min_lng, bounds.min_lat],
          [bounds.max_lng, bounds.max_lat],
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
      </MapLibreMap>

      {tooltip ? (
        <div
          className="tooltip"
          ref={tooltipRef}
          style={tooltipPosition ? tooltipPosition : { left: 0, top: 0, visibility: "hidden" }}
        >
          {tooltip.kind === "hex" ? (
            <HexTooltip horizon={horizon} object={tooltip.object} />
          ) : (
            <ZoneTooltip
              fallbackFeature={tooltip.feature}
              horizon={horizon}
              mapViewMode={mapViewMode}
              object={tooltip.object}
            />
          )}
        </div>
      ) : null}
    </div>
  );
}

function HexTooltip({ horizon, object }: { horizon: Horizon; object: HexAggregate }) {
  return (
    <>
      <span className="tooltip-kicker">Hexágono</span>
      <strong className="tooltip-title">{object.category_desc}</strong>
      <span className="tooltip-subtitle">{object.location_label}</span>
      <div className="tooltip-badges">
        <span className="tooltip-chip">{object.n_locales} locales</span>
      </div>
      <div className="tooltip-grid">
        <div className="tooltip-item">
          <span className="tooltip-label">Superv. {formatHorizonShortLabel(horizon)}</span>
          <strong className="tooltip-value">{formatTooltipPercent(getHorizonSurvival(object, horizon))}</strong>
        </div>
        <div className="tooltip-item">
          <span className="tooltip-label">Índice 0-1</span>
          <strong className="tooltip-value">{formatRelativeRiskIndex(object.avg_risk_percentile)}</strong>
        </div>
      </div>
    </>
  );
}

function ZoneTooltip({
  fallbackFeature,
  horizon,
  mapViewMode,
  object,
}: {
  fallbackFeature: ZoneBoundaryFeature;
  horizon: Horizon;
  mapViewMode: MapViewMode;
  object: ZoneAggregate | null;
}) {
  const zoneLevel = mapViewMode === "hex" ? "district" : mapViewMode;
  const zoneLabel = zoneLevel === "district" ? "Distrito" : "Barrio";
  const zoneName = object?.zone_name ?? fallbackFeature.properties.zone_name;
  const contextName = object?.zone_context_name ?? fallbackFeature.properties.zone_context_name ?? null;

  return (
    <>
      <span className="tooltip-kicker">{zoneLabel}</span>
      <strong className="tooltip-title">{zoneName}</strong>
      <span className="tooltip-subtitle">
        {object?.category_desc ?? "Sin datos de categoría"}
      </span>
      <div className="tooltip-badges">
        {object ? <span className="tooltip-chip">{formatCompact(object.n_locales)} locales</span> : null}
        {contextName ? <span className="tooltip-chip">{contextName}</span> : null}
      </div>
      <div className="tooltip-grid">
        <div className="tooltip-item">
          <span className="tooltip-label">Superv. {formatHorizonShortLabel(horizon)}</span>
          <strong className="tooltip-value">
            {object ? formatTooltipPercent(getHorizonSurvival(object, horizon)) : "Sin muestra"}
          </strong>
        </div>
        <div className="tooltip-item">
          <span className="tooltip-label">Índice 0-1</span>
          <strong className="tooltip-value">
            {object ? formatRelativeRiskIndex(object.avg_risk_percentile) : "Sin datos"}
          </strong>
        </div>
      </div>
    </>
  );
}

function DeckOverlay({ layers }: { layers: Layer[] }) {
  const overlay = useControl<MapboxOverlay>(() => new MapboxOverlay({ interleaved: false }));

  overlay.setProps({
    layers,
    getCursor: ({ isDragging, isHovering }) => {
      if (isDragging) {
        return "grabbing";
      }
      return isHovering ? "pointer" : "grab";
    },
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
    padding: { top: 0, right: 0, bottom: 0, left: 0 },
  };
}

function getMinZoom(bounds: Bounds) {
  return Math.min(bounds.max_zoom, bounds.min_zoom + INITIAL_ZOOM_INSET);
}

function buildBoundsKey(bounds: Bounds) {
  return [bounds.min_lng, bounds.min_lat, bounds.max_lng, bounds.max_lat, bounds.min_zoom, bounds.max_zoom].join(":");
}

function colorForZone(zone: ZoneAggregate | null, scale: ColorScale, zoneColorFloorLocales: number): Color {
  if (!zone) {
    return [214, 210, 201, 98];
  }

  if (!isZoneEligibleForColor(zone, zoneColorFloorLocales) || !isFiniteNumber(zone.avg_risk_percentile)) {
    return [191, 186, 178, 122];
  }

  return colorForRelativeRiskIndex(zone.avg_risk_percentile, scale);
}

function colorForRelativeRiskIndex(value: number | null, scale: ColorScale): Color {
  if (!isFiniteNumber(value)) {
    return [136, 142, 147, 78];
  }

  const anchors = [scale.min, scale.low, scale.mid, scale.high, scale.max];
  const palette: ReadonlyArray<Color> = [
    [27, 112, 123, 196],
    [142, 181, 156, 184],
    [228, 192, 122, 182],
    [196, 106, 52, 188],
    [156, 56, 32, 198],
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

function isZoneEligibleForColor(zone: ZoneAggregate, zoneColorFloorLocales: number) {
  if (zoneColorFloorLocales <= 0) {
    return zone.n_locales > 0;
  }
  return zone.n_locales >= zoneColorFloorLocales;
}

function formatCompact(value: number) {
  return new Intl.NumberFormat("es-ES", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function interpolateColor(left: Color, right: Color, ratio: number): Color {
  const clamped = Math.max(0, Math.min(1, ratio));
  const leftAlpha = left[3] ?? 255;
  const rightAlpha = right[3] ?? 255;
  return [
    Math.round(left[0] + (right[0] - left[0]) * clamped),
    Math.round(left[1] + (right[1] - left[1]) * clamped),
    Math.round(left[2] + (right[2] - left[2]) * clamped),
    Math.round(leftAlpha + (rightAlpha - leftAlpha) * clamped),
  ] as const;
}
