"use client";

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import MapView, { Layer, NavigationControl, Source, type MapLayerMouseEvent, type ViewState } from "react-map-gl/maplibre";

import { formatHorizonShortLabel, isFiniteNumber, type Horizon } from "@/lib/horizon";
import { computeTooltipPosition } from "@/lib/tooltip-position";
import type {
  Bounds,
  OpportunityManualSelection,
  OpportunityPoint,
  OpportunitySection,
  OpportunitySectionFeatureCollection
} from "@/lib/types";

type OpportunityMapProps = {
  bounds: Bounds;
  sectionsGeojsonPath: string;
  points: OpportunityPoint[];
  horizon: Horizon;
  selectedListingId: string | null;
  selectedSectionKey: string | null;
  manualSelection: OpportunityManualSelection | null;
  onSelectListing: (point: OpportunityPoint) => void;
  onSelectManual: (selection: OpportunityManualSelection) => void;
};

type TooltipState = {
  x: number;
  y: number;
  point: OpportunityPoint;
} | null;

const MAP_STYLE = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json";
const POINTS_LAYER_ID = "opportunity-points";
const SECTION_FILL_LAYER_ID = "opportunity-sections-fill";
const SECTION_LINE_LAYER_ID = "opportunity-sections-line";
const SELECTED_POINT_LAYER_ID = "opportunity-selected-point";
const MANUAL_POINT_LAYER_ID = "opportunity-manual-point";
const INITIAL_ZOOM_INSET = 0.45;
const INITIAL_LATITUDE_FOCUS_RATIO = 0.36;
const SECTION_FETCH_CACHE_MODE = process.env.NODE_ENV === "production" ? "force-cache" : "no-store";

export function OpportunityMap({
  bounds,
  sectionsGeojsonPath,
  points,
  horizon,
  selectedListingId,
  selectedSectionKey,
  manualSelection,
  onSelectListing,
  onSelectManual
}: OpportunityMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);
  const [sections, setSections] = useState<OpportunitySectionFeatureCollection | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{ left: number; top: number } | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const minZoom = getMinZoom(bounds);

  useEffect(() => {
    let alive = true;

    async function loadSections() {
      try {
        setLoadError(null);
        const response = await fetch(sectionsGeojsonPath, { cache: SECTION_FETCH_CACHE_MODE });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const payload = (await response.json()) as OpportunitySectionFeatureCollection;
        if (alive) {
          setSections(payload);
        }
      } catch (error) {
        if (alive) {
          setLoadError(error instanceof Error ? error.message : "No se pudo cargar la geometría");
        }
      }
    }

    setSections(null);
    void loadSections();

    return () => {
      alive = false;
    };
  }, [sectionsGeojsonPath]);

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
  }, [tooltip]);

  const sectionsByKey = useMemo(() => {
    const entries = (sections?.features ?? []).map((feature) => [feature.properties.section_key, feature.properties] as const);
    return new Map<string, OpportunitySection>(entries);
  }, [sections]);

  const pointsById = useMemo(() => new Map(points.map((point) => [point.listing_id, point] as const)), [points]);

  const pointScale = useMemo(() => buildSurvivalScale(points, horizon), [points, horizon]);

  const pointFeatureCollection = useMemo(() => {
    return {
      type: "FeatureCollection",
      features: points
        .filter((point) => isFiniteNumber(point.lat_wgs84) && isFiniteNumber(point.lon_wgs84))
        .map((point) => ({
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [point.lon_wgs84 as number, point.lat_wgs84 as number]
          },
          properties: {
            listing_id: point.listing_id,
            section_key: point.section_key,
            color: colorForSurvival(getPointSurvival(point, horizon), pointScale),
            radius: buildPointRadius(point.area_m2)
          }
        }))
    };
  }, [horizon, pointScale, points]);

  const selectedPointFeatureCollection = useMemo(() => {
    const selectedPoint = selectedListingId ? pointsById.get(selectedListingId) ?? null : null;
    if (!selectedPoint || !isFiniteNumber(selectedPoint.lat_wgs84) || !isFiniteNumber(selectedPoint.lon_wgs84)) {
      return null;
    }

    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [selectedPoint.lon_wgs84, selectedPoint.lat_wgs84]
          },
          properties: {
            listing_id: selectedPoint.listing_id
          }
        }
      ]
    };
  }, [pointsById, selectedListingId]);

  const manualPointFeatureCollection = useMemo(() => {
    if (!manualSelection) {
      return null;
    }

    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [manualSelection.lng, manualSelection.lat]
          },
          properties: {
            section_key: manualSelection.section.section_key
          }
        }
      ]
    };
  }, [manualSelection]);

  const interactiveLayerIds = useMemo(() => {
    const layers = [POINTS_LAYER_ID];
    if (sections) {
      layers.push(SECTION_FILL_LAYER_ID);
    }
    return layers;
  }, [sections]);

  function handleMapClick(event: MapLayerMouseEvent) {
    const features = event.features ?? [];
    const listingFeature = features.find((feature) => feature.layer.id === POINTS_LAYER_ID);
    if (listingFeature) {
      const listingId = String(listingFeature.properties?.listing_id ?? "");
      const point = pointsById.get(listingId);
      if (point) {
        onSelectListing(point);
        return;
      }
    }

    const sectionFeature = features.find((feature) => feature.layer.id === SECTION_FILL_LAYER_ID);
    if (!sectionFeature) {
      return;
    }

    const sectionKey = String(sectionFeature.properties?.section_key ?? "");
    const section = sectionsByKey.get(sectionKey);
    if (!section) {
      return;
    }

    onSelectManual({
      lng: event.lngLat.lng,
      lat: event.lngLat.lat,
      section
    });
  }

  function handleMouseMove(event: MapLayerMouseEvent) {
    const listingFeature = (event.features ?? []).find((feature) => feature.layer.id === POINTS_LAYER_ID);
    if (!listingFeature) {
      setTooltip(null);
      return;
    }

    const listingId = String(listingFeature.properties?.listing_id ?? "");
    const point = pointsById.get(listingId);
    if (!point) {
      setTooltip(null);
      return;
    }

    setTooltip({ x: event.point.x, y: event.point.y, point });
  }

  return (
    <div className="map-canvas" ref={containerRef}>
      <MapView
        key={buildBoundsKey(bounds)}
        initialViewState={buildInitialViewState(bounds, minZoom)}
        interactiveLayerIds={interactiveLayerIds}
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
        onClick={handleMapClick}
        onMouseLeave={() => setTooltip(null)}
        onMouseMove={handleMouseMove}
      >
        <NavigationControl position="bottom-right" showCompass={false} />

        {sections ? (
          <Source data={sections as any} id="opportunity-sections" type="geojson">
            <Layer
              id={SECTION_FILL_LAYER_ID}
              paint={{
                "fill-color": "#1e6b61",
                "fill-opacity": 0.01
              }}
              type="fill"
            />
            <Layer
              filter={selectedSectionKey ? ["==", ["get", "section_key"], selectedSectionKey] : ["==", ["get", "section_key"], "__none__"]}
              id={SECTION_LINE_LAYER_ID}
              paint={{
                "line-color": "#0d3f45",
                "line-width": 2,
                "line-opacity": 0.9
              }}
              type="line"
            />
          </Source>
        ) : null}

        <Source data={pointFeatureCollection as any} id="opportunity-points-source" type="geojson">
          <Layer
            id={POINTS_LAYER_ID}
            paint={{
              "circle-color": ["get", "color"],
              "circle-opacity": 0.9,
              "circle-radius": ["get", "radius"],
              "circle-stroke-color": "rgba(255,255,255,0.92)",
              "circle-stroke-width": 1.3
            }}
            type="circle"
          />
        </Source>

        {selectedPointFeatureCollection ? (
          <Source data={selectedPointFeatureCollection as any} id="opportunity-selected-point-source" type="geojson">
            <Layer
              id={SELECTED_POINT_LAYER_ID}
              paint={{
                "circle-color": "rgba(13,63,69,0.12)",
                "circle-radius": 12,
                "circle-stroke-color": "#0d3f45",
                "circle-stroke-width": 3
              }}
              type="circle"
            />
          </Source>
        ) : null}

        {manualPointFeatureCollection ? (
          <Source data={manualPointFeatureCollection as any} id="opportunity-manual-point-source" type="geojson">
            <Layer
              id={MANUAL_POINT_LAYER_ID}
              paint={{
                "circle-color": "#c17c3f",
                "circle-radius": 6,
                "circle-stroke-color": "#fffaf1",
                "circle-stroke-width": 2
              }}
              type="circle"
            />
          </Source>
        ) : null}
      </MapView>

      {!sections && !loadError ? (
        <div className="map-overlay panel">
          <h2>Cargando secciones</h2>
          <p>La lectura libre por punto se activa cuando termina de descargarse la geometría censal.</p>
        </div>
      ) : null}

      {loadError ? (
        <div className="map-overlay panel">
          <h2>Geometría no disponible</h2>
          <p>No se ha podido cargar el contexto de secciones: {loadError}.</p>
        </div>
      ) : null}

      {tooltip ? (
        <div
          className="tooltip"
          ref={tooltipRef}
          style={tooltipPosition ? tooltipPosition : { left: 0, top: 0, visibility: "hidden" }}
        >
          <span className="tooltip-kicker">Local disponible</span>
          <strong className="tooltip-title">{tooltip.point.card_title}</strong>
          <span className="tooltip-subtitle">{tooltip.point.barrio_name}, {tooltip.point.district_name}</span>
          <span className="tooltip-subtitle">Actividad sugerida: {tooltip.point.best_activity_label || "Sin ranking"}</span>
          <div className="tooltip-badges">
            <span className="tooltip-chip">{tooltip.point.operation}</span>
            <span className="tooltip-chip">{formatTooltipPrice(tooltip.point.price_eur)}</span>
          </div>
          <div className="tooltip-grid">
            <div className="tooltip-item">
              <span className="tooltip-label">Supervivencia {formatHorizonShortLabel(horizon)}</span>
              <strong className="tooltip-value">{formatTooltipPercent(getPointSurvival(tooltip.point, horizon))}</strong>
            </div>
            <div className="tooltip-item">
              <span className="tooltip-label">Riesgo relativo</span>
              <strong className="tooltip-value">{formatRiskPercentile(tooltip.point.risk_percentile)}</strong>
            </div>
          </div>
          <small className="tooltip-note">Haz clic para abrir la ficha del local.</small>
        </div>
      ) : null}
    </div>
  );
}

function getPointSurvival(point: OpportunityPoint, horizon: Horizon) {
  return horizon === "24m" ? point.expected_survival_24m : point.expected_survival_12m;
}

function buildPointRadius(area: number | null) {
  if (!isFiniteNumber(area)) {
    return 6;
  }
  return clamp(4 + Math.log1p(Math.max(area, 0)) * 1.15, 5, 14);
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

function buildSurvivalScale(points: OpportunityPoint[], horizon: Horizon) {
  const values = points
    .map((point) => getPointSurvival(point, horizon))
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

  return {
    min,
    low: quantile(values, 0.18),
    mid: quantile(values, 0.5),
    high: quantile(values, 0.88),
    max
  };
}

function colorForSurvival(value: number | null, scale: { min: number; low: number; mid: number; high: number; max: number }) {
  if (!isFiniteNumber(value)) {
    return "rgba(136,142,147,0.75)";
  }

  const anchors = [scale.min, scale.low, scale.mid, scale.high, scale.max];
  const palette = [
    [156, 56, 32],
    [196, 106, 52],
    [228, 192, 122],
    [142, 181, 156],
    [27, 112, 123]
  ] as const;

  if (anchors[0] === anchors[4]) {
    return rgba(palette[2], 0.92);
  }
  if (value <= anchors[0]) {
    return rgba(palette[0], 0.92);
  }
  if (value >= anchors[4]) {
    return rgba(palette[4], 0.92);
  }

  for (let index = 0; index < anchors.length - 1; index += 1) {
    const left = anchors[index];
    const right = anchors[index + 1];
    if (value <= right) {
      const span = right - left || 1;
      const ratio = (value - left) / span;
      return rgba(interpolateColor(palette[index], palette[index + 1], ratio), 0.92);
    }
  }

  return rgba(palette[4], 0.92);
}

function rgba(rgb: readonly [number, number, number], alpha: number) {
  return `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${alpha})`;
}

function interpolateColor(left: readonly [number, number, number], right: readonly [number, number, number], ratio: number) {
  const clamped = clamp(ratio, 0, 1);
  return [
    Math.round(left[0] + (right[0] - left[0]) * clamped),
    Math.round(left[1] + (right[1] - left[1]) * clamped),
    Math.round(left[2] + (right[2] - left[2]) * clamped)
  ] as const;
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

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function formatTooltipPercent(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Sin datos";
  }
  return `${(value * 100).toFixed(0)}%`;
}

function formatTooltipPrice(value: number | null) {
  if (!isFiniteNumber(value)) {
    return "Precio s/d";
  }
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);
}

function formatRiskPercentile(value: number) {
  if (!Number.isFinite(value)) {
    return "Sin datos";
  }
  return `P${Math.round(value * 100)}`;
}