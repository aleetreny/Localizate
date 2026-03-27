"use client";

import type { Color, PickingInfo } from "@deck.gl/core";
import { H3HexagonLayer } from "@deck.gl/geo-layers";
import { DeckGL } from "@deck.gl/react";
import { useEffect, useMemo, useState } from "react";
import Map, { NavigationControl, type ViewState } from "react-map-gl/maplibre";

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

export function MadridMap({ bounds, colorScale, hexes, horizon, selectedHex, onSelectHex }: MadridMapProps) {
  const [tooltip, setTooltip] = useState<TooltipState>(null);
  const [viewState, setViewState] = useState<ViewState>(() => buildInitialViewState(bounds));

  useEffect(() => {
    setViewState(buildInitialViewState(bounds));
  }, [bounds]);

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
  }, [hexes, horizon, onSelectHex, selectedHex?.h3_cell]);

  return (
    <div className="map-canvas">
      <div className="map-base">
        <Map
          longitude={viewState.longitude}
          latitude={viewState.latitude}
          zoom={viewState.zoom}
          bearing={viewState.bearing}
          pitch={viewState.pitch}
          onMove={(event) => setViewState(event.viewState)}
          mapStyle={MAP_STYLE}
          minZoom={bounds.min_zoom}
          maxZoom={bounds.max_zoom}
          reuseMaps
          dragPan
          scrollZoom
          doubleClickZoom
          touchZoomRotate
          style={{ width: "100%", height: "100%" }}
          maxBounds={[
            [bounds.min_lng, bounds.min_lat],
            [bounds.max_lng, bounds.max_lat]
          ]}
        >
          <NavigationControl position="bottom-right" showCompass={false} />
        </Map>
      </div>

      <div className="map-stage">
        <DeckGL
          controller={{ dragRotate: false, touchRotate: false }}
          viewState={viewState}
          onViewStateChange={({ viewState: nextViewState }) => setViewState(nextViewState as ViewState)}
          layers={layers}
          style={{ position: "absolute", top: "0px", right: "0px", bottom: "0px", left: "0px" }}
          getCursor={({ isDragging, isHovering }) => {
            if (isDragging) {
              return "grabbing";
            }
            return isHovering ? "pointer" : "grab";
          }}
        />
      </div>

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

function buildInitialViewState(bounds: Bounds): ViewState {
  return {
    longitude: (bounds.min_lng + bounds.max_lng) / 2,
    latitude: (bounds.min_lat + bounds.max_lat) / 2,
    zoom: Math.min(bounds.min_zoom + 0.25, bounds.max_zoom),
    pitch: 0,
    bearing: 0,
    padding: { top: 0, right: 0, bottom: 0, left: 0 }
  };
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