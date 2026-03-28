"use client";

import type { Color, PickingInfo } from "@deck.gl/core";
import { H3HexagonLayer } from "@deck.gl/geo-layers";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { useMemo, useState } from "react";
import Map, { NavigationControl, useControl, type ViewState } from "react-map-gl/maplibre";

import type { Bounds, ColorScale, HexAggregate } from "@/lib/types";

type MadridMapProps = {
  bounds: Bounds;
  colorScale: ColorScale;
  hexes: HexAggregate[];
  horizon: "12m" | "24m";
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

export function MadridMap({ bounds, colorScale, hexes, horizon, selectedHex, onSelectHex }: MadridMapProps) {
  const [tooltip, setTooltip] = useState<TooltipState>(null);
  const minZoom = getMinZoom(bounds);

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
        getFillColor: (item) => colorForSurvival(horizon === "24m" ? item.survival_24m : item.survival_12m, colorScale),
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
    <div className="map-canvas">
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
        <div className="tooltip" style={{ left: tooltip.x + 14, top: tooltip.y + 14 }}>
          <strong>{tooltip.object.category_desc}</strong>
          <span>{tooltip.object.n_locales} locales en el hexágono</span>
          <span>
            Supervivencia {horizon}: {((horizon === "24m" ? tooltip.object.survival_24m : tooltip.object.survival_12m) * 100).toFixed(0)}%
          </span>
          <small>Risk ensemble medio {tooltip.object.avg_risk_ensemble.toFixed(2)}</small>
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
    latitude: (bounds.min_lat + bounds.max_lat) / 2,
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

function colorForSurvival(value: number, scale: ColorScale): Color {
  const anchors = [scale.min, scale.low, scale.mid, scale.high, scale.max];
  const palette: ReadonlyArray<Color> = [
    [158, 55, 32, 232],
    [210, 120, 44, 220],
    [235, 196, 91, 212],
    [96, 166, 133, 214],
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