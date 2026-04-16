"use client";

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import MapView, { Layer, NavigationControl, Source, type MapLayerMouseEvent, type MapRef, type ViewState } from "react-map-gl/maplibre";

import { isFiniteNumber } from "@/lib/horizon";
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
  sections: OpportunitySectionFeatureCollection | null;
  sectionsByKey: ReadonlyMap<string, OpportunitySection>;
  sectionsError: string | null;
  sectionsLoading: boolean;
  points: OpportunityPoint[];
  highlightAddressSelection: boolean;
  selectedListingId: string | null;
  selectedListingFocusNonce: number;
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
const SECTION_SELECTED_FILL_LAYER_ID = "opportunity-sections-selected-fill";
const SECTION_LINE_LAYER_ID = "opportunity-sections-line";
const SELECTED_POINT_LAYER_ID = "opportunity-selected-point";
const MANUAL_POINT_HALO_LAYER_ID = "opportunity-manual-point-halo";
const MANUAL_POINT_LAYER_ID = "opportunity-manual-point";
const INITIAL_ZOOM_INSET = 0.45;
const INITIAL_LATITUDE_FOCUS_RATIO = 0.36;

export function OpportunityMap({
  bounds,
  sections,
  sectionsByKey,
  sectionsError,
  sectionsLoading,
  points,
  highlightAddressSelection,
  selectedListingId,
  selectedListingFocusNonce,
  selectedSectionKey,
  manualSelection,
  onSelectListing,
  onSelectManual
}: OpportunityMapProps) {
  const mapRef = useRef<MapRef | null>(null);
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

    setTooltipPosition(
      computeTooltipPosition({
        anchor: { x: tooltip.x, y: tooltip.y },
        tooltip: { width: bubble.offsetWidth, height: bubble.offsetHeight },
        viewport: { width: container.clientWidth, height: container.clientHeight }
      })
    );
  }, [tooltip]);

  const pointsById = useMemo(() => new Map(points.map((point) => [point.listing_id, point] as const)), [points]);
  const pointPositions = useMemo(() => buildPointPositionIndex(points), [points]);
  const normalizedSelectedSectionKey = normalizeSectionKey(selectedSectionKey);

  const selectedSectionFeatureCollection = useMemo(() => {
    if (!sections) {
      return null;
    }

    // Prefer geometric containment when a manual point is active (address search / free click).
    if (manualSelection) {
      const matchedFeature = sections.features.find((feature) =>
        doesFeatureContainCoordinate(feature, manualSelection.lng, manualSelection.lat)
      );

      if (matchedFeature) {
        return {
          type: "FeatureCollection",
          features: [matchedFeature]
        } as OpportunitySectionFeatureCollection;
      }
    }

    if (!normalizedSelectedSectionKey) {
      return null;
    }

    const selectedFeatures = sections.features.filter(
      (feature) => normalizeSectionKey(feature.properties?.section_key) === normalizedSelectedSectionKey
    );

    if (selectedFeatures.length === 0) {
      return null;
    }

    return {
      type: "FeatureCollection",
      features: selectedFeatures
    } as OpportunitySectionFeatureCollection;
  }, [manualSelection, normalizedSelectedSectionKey, sections]);

  useEffect(() => {
    if (!manualSelection || !mapRef.current) {
      return;
    }

    mapRef.current.flyTo({
      center: [manualSelection.lng, manualSelection.lat],
      zoom: Math.max(minZoom + 1.4, 15),
      duration: 900,
      essential: true,
    });
  }, [manualSelection, minZoom]);

  useEffect(() => {
    if (selectedListingFocusNonce <= 0 || manualSelection || !selectedListingId || !mapRef.current) {
      return;
    }

    const selectedPoint = pointsById.get(selectedListingId);
    if (!selectedPoint || !isFiniteNumber(selectedPoint.lat_wgs84) || !isFiniteNumber(selectedPoint.lon_wgs84)) {
      return;
    }

    const position = pointPositions.get(selectedPoint.listing_id) ?? {
      lat: selectedPoint.lat_wgs84,
      lng: selectedPoint.lon_wgs84,
    };

    mapRef.current.flyTo({
      center: [position.lng, position.lat],
      zoom: Math.max(minZoom + 1.15, 14.6),
      duration: 850,
      essential: true,
    });
  }, [manualSelection, minZoom, pointPositions, pointsById, selectedListingFocusNonce, selectedListingId]);

  const pointScale = useMemo(() => buildSurvivalScale(points), [points]);

  const pointFeatureCollection = useMemo(() => {
    return {
      type: "FeatureCollection",
      features: points
        .filter((point) => isFiniteNumber(point.lat_wgs84) && isFiniteNumber(point.lon_wgs84))
        .map((point) => {
          const position = pointPositions.get(point.listing_id) ?? {
            lat: point.lat_wgs84 as number,
            lng: point.lon_wgs84 as number,
          };

          return {
            type: "Feature",
            geometry: {
              type: "Point",
              coordinates: [position.lng, position.lat]
            },
            properties: {
              listing_id: point.listing_id,
              section_key: point.section_key,
              color: colorForSurvival(getPointSurvival(point), pointScale),
              radius: buildPointRadius(point.area_m2)
            }
          };
        })
    };
  }, [pointPositions, pointScale, points]);

  const selectedPointFeatureCollection = useMemo(() => {
    const selectedPoint = selectedListingId ? pointsById.get(selectedListingId) ?? null : null;
    if (!selectedPoint || !isFiniteNumber(selectedPoint.lat_wgs84) || !isFiniteNumber(selectedPoint.lon_wgs84)) {
      return null;
    }

    const position = pointPositions.get(selectedPoint.listing_id) ?? {
      lat: selectedPoint.lat_wgs84,
      lng: selectedPoint.lon_wgs84,
    };

    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [position.lng, position.lat]
          },
          properties: {
            listing_id: selectedPoint.listing_id
          }
        }
      ]
    };
  }, [pointPositions, pointsById, selectedListingId]);

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

    const sectionKey = normalizeSectionKey(sectionFeature.properties?.section_key);
    if (!sectionKey) {
      return;
    }

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
        ref={mapRef}
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
          </Source>
        ) : null}

        {selectedSectionFeatureCollection ? (
          <Source data={selectedSectionFeatureCollection as any} id="opportunity-selected-sections" type="geojson">
            <Layer
              id={SECTION_SELECTED_FILL_LAYER_ID}
              paint={{
                "fill-color": highlightAddressSelection ? "#111111" : "#0d3f45",
                "fill-opacity": highlightAddressSelection ? 0.3 : 0.16
              }}
              type="fill"
            />
            <Layer
              id={SECTION_LINE_LAYER_ID}
              paint={{
                "line-color": highlightAddressSelection ? "#111111" : "#0d3f45",
                "line-width": highlightAddressSelection ? 4.8 : 2.8,
                "line-opacity": highlightAddressSelection ? 1 : 0.9
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
            {highlightAddressSelection ? (
              <Layer
                id={MANUAL_POINT_HALO_LAYER_ID}
                paint={{
                  "circle-color": "rgba(0,0,0,0)",
                  "circle-radius": 11,
                  "circle-stroke-color": "rgba(17,17,17,0.9)",
                  "circle-stroke-width": 2.1
                }}
                type="circle"
              />
            ) : null}
            <Layer
              id={MANUAL_POINT_LAYER_ID}
              paint={{
                "circle-color": "#c17c3f",
                "circle-radius": highlightAddressSelection ? 7 : 6,
                "circle-stroke-color": highlightAddressSelection ? "#111111" : "#fffaf1",
                "circle-stroke-width": highlightAddressSelection ? 2.7 : 2
              }}
              type="circle"
            />
          </Source>
        ) : null}
      </MapView>

      {!sections && sectionsLoading ? (
        <div className="map-overlay panel">
          <h2>Cargando secciones</h2>
          <p>La lectura libre por punto se activa en cuanto termina de descargarse la geometría censal.</p>
        </div>
      ) : null}

      {sectionsError ? (
        <div className="map-overlay panel">
          <h2>Geometría no disponible</h2>
          <p>No se ha podido cargar el contexto de secciones: {sectionsError}.</p>
        </div>
      ) : null}

      {tooltip ? (
        <div
          className="tooltip"
          ref={tooltipRef}
          style={tooltipPosition ? tooltipPosition : { left: 0, top: 0, visibility: "hidden" }}
        >
          <span className="tooltip-kicker">Local</span>
          <strong className="tooltip-title">{tooltip.point.card_title}</strong>
          <span className="tooltip-subtitle">{tooltip.point.barrio_name}, {tooltip.point.district_name}</span>
          <div className="tooltip-badges">
            <span className="tooltip-chip">{tooltip.point.operation}</span>
            <span className="tooltip-chip">{formatTooltipPrice(tooltip.point.price_eur)}</span>
            {tooltip.point.best_activity_label ? <span className="tooltip-chip">{tooltip.point.best_activity_label}</span> : null}
          </div>
          <div className="tooltip-grid">
            <div className="tooltip-item">
              <span className="tooltip-label">Superv. 24m</span>
              <strong className="tooltip-value">{formatTooltipPercent(getPointSurvival(tooltip.point))}</strong>
            </div>
            <div className="tooltip-item">
              <span className="tooltip-label">Riesgo</span>
              <strong className="tooltip-value">{formatRiskPercentile(tooltip.point.risk_percentile)}</strong>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function getPointSurvival(point: OpportunityPoint) {
  return point.expected_survival_24m;
}

function buildPointRadius(area: number | null) {
  if (!isFiniteNumber(area)) {
    return 6;
  }
  return clamp(4 + Math.log1p(Math.max(area, 0)) * 1.15, 5, 14);
}

function buildPointPositionIndex(points: OpportunityPoint[]) {
  const groupedPoints = new Map<string, OpportunityPoint[]>();
  for (const point of points) {
    if (!isFiniteNumber(point.lat_wgs84) || !isFiniteNumber(point.lon_wgs84)) {
      continue;
    }

    const groupKey = `${point.lat_wgs84}:${point.lon_wgs84}`;
    const bucket = groupedPoints.get(groupKey);
    if (bucket) {
      bucket.push(point);
    } else {
      groupedPoints.set(groupKey, [point]);
    }
  }

  const positions = new Map<string, { lat: number; lng: number }>();
  for (const bucket of groupedPoints.values()) {
    const referencePoint = bucket[0];
    if (!referencePoint || !isFiniteNumber(referencePoint.lat_wgs84) || !isFiniteNumber(referencePoint.lon_wgs84)) {
      continue;
    }

    if (bucket.length === 1) {
      positions.set(referencePoint.listing_id, {
        lat: referencePoint.lat_wgs84,
        lng: referencePoint.lon_wgs84,
      });
      continue;
    }

    const sortedBucket = [...bucket].sort(comparePointsForLayout);
    for (let index = 0; index < sortedBucket.length; index += 1) {
      const point = sortedBucket[index];
      const offset = buildPointOffset(
        referencePoint.lat_wgs84,
        referencePoint.lon_wgs84,
        index,
        sortedBucket.length
      );
      positions.set(point.listing_id, offset);
    }
  }

  return positions;
}

function comparePointsForLayout(left: OpportunityPoint, right: OpportunityPoint) {
  const operationDiff = left.operation.localeCompare(right.operation, "es");
  if (operationDiff !== 0) {
    return operationDiff;
  }

  const priceDiff = (left.price_eur ?? Number.POSITIVE_INFINITY) - (right.price_eur ?? Number.POSITIVE_INFINITY);
  if (Math.abs(priceDiff) > 1e-6) {
    return priceDiff;
  }

  const areaDiff = (left.area_m2 ?? Number.POSITIVE_INFINITY) - (right.area_m2 ?? Number.POSITIVE_INFINITY);
  if (Math.abs(areaDiff) > 1e-6) {
    return areaDiff;
  }

  return left.listing_id.localeCompare(right.listing_id, "es");
}

function buildPointOffset(baseLat: number, baseLng: number, index: number, total: number) {
  const pointsPerRing = 6;
  const ring = Math.floor(index / pointsPerRing);
  const indexWithinRing = index % pointsPerRing;
  const ringCount = Math.min(pointsPerRing, total - ring * pointsPerRing);
  const angle = (-Math.PI / 2) + ((Math.PI * 2) / ringCount) * indexWithinRing;
  const distanceMeters = total <= 2 ? 16 : total <= 4 ? 20 : 24 + ring * 8;

  return offsetCoordinate(baseLat, baseLng, distanceMeters, angle);
}

function offsetCoordinate(baseLat: number, baseLng: number, distanceMeters: number, angleRad: number) {
  const metersPerLatDegree = 111_320;
  const metersPerLngDegree = Math.max(1, Math.cos((baseLat * Math.PI) / 180) * metersPerLatDegree);
  const latOffset = (Math.sin(angleRad) * distanceMeters) / metersPerLatDegree;
  const lngOffset = (Math.cos(angleRad) * distanceMeters) / metersPerLngDegree;

  return {
    lat: baseLat + latOffset,
    lng: baseLng + lngOffset,
  };
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

function buildSurvivalScale(points: OpportunityPoint[]) {
  const values = points
    .map((point) => getPointSurvival(point))
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

function normalizeSectionKey(value: unknown) {
  if (typeof value !== "string" && typeof value !== "number") {
    return null;
  }

  const key = String(value).trim();
  if (!key) {
    return null;
  }

  if (/^\d+$/.test(key) && key.length < 5) {
    return key.padStart(5, "0");
  }

  return key;
}

function doesFeatureContainCoordinate(
  feature: OpportunitySectionFeatureCollection["features"][number],
  lng: number,
  lat: number,
) {
  const geometry = feature.geometry;
  if (!geometry) {
    return false;
  }

  if (geometry.type === "Polygon") {
    return isPointInsidePolygonRings(lng, lat, geometry.coordinates as number[][][]);
  }

  if (geometry.type === "MultiPolygon") {
    const polygons = geometry.coordinates as number[][][][];
    for (const polygonRings of polygons) {
      if (isPointInsidePolygonRings(lng, lat, polygonRings)) {
        return true;
      }
    }
  }

  return false;
}

function isPointInsidePolygonRings(lng: number, lat: number, polygonRings: number[][][]) {
  if (!polygonRings || polygonRings.length === 0) {
    return false;
  }

  const [outerRing, ...innerRings] = polygonRings;
  if (!isPointInsideRing(lng, lat, outerRing)) {
    return false;
  }

  for (const holeRing of innerRings) {
    if (isPointInsideRing(lng, lat, holeRing)) {
      return false;
    }
  }

  return true;
}

function isPointInsideRing(lng: number, lat: number, ring: number[][]) {
  if (!ring || ring.length < 3) {
    return false;
  }

  let inside = false;

  for (let index = 0, previousIndex = ring.length - 1; index < ring.length; previousIndex = index, index += 1) {
    const currentVertex = ring[index];
    const previousVertex = ring[previousIndex];

    if (!currentVertex || !previousVertex || currentVertex.length < 2 || previousVertex.length < 2) {
      continue;
    }

    const currentLng = currentVertex[0];
    const currentLat = currentVertex[1];
    const previousLng = previousVertex[0];
    const previousLat = previousVertex[1];

    if (isPointOnSegment(lng, lat, previousLng, previousLat, currentLng, currentLat)) {
      return true;
    }

    const crossesRay = ((currentLat > lat) !== (previousLat > lat))
      && (lng < ((previousLng - currentLng) * (lat - currentLat)) / ((previousLat - currentLat) || 1e-12) + currentLng);

    if (crossesRay) {
      inside = !inside;
    }
  }

  return inside;
}

function isPointOnSegment(
  pointLng: number,
  pointLat: number,
  startLng: number,
  startLat: number,
  endLng: number,
  endLat: number,
) {
  const epsilon = 1e-10;
  const deltaLng = endLng - startLng;
  const deltaLat = endLat - startLat;
  const segmentLengthSquared = (deltaLng ** 2) + (deltaLat ** 2);

  if (segmentLengthSquared <= epsilon) {
    const distanceSquared = ((pointLng - startLng) ** 2) + ((pointLat - startLat) ** 2);
    return distanceSquared <= epsilon;
  }

  const crossProduct = ((pointLat - startLat) * deltaLng) - ((pointLng - startLng) * deltaLat);
  if (Math.abs(crossProduct) > epsilon) {
    return false;
  }

  const dotProduct = ((pointLng - startLng) * deltaLng) + ((pointLat - startLat) * deltaLat);
  if (dotProduct < 0) {
    return false;
  }

  if (dotProduct - segmentLengthSquared > epsilon) {
    return false;
  }

  return true;
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

