"use client";

import { type CSSProperties, type RefObject, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

export type HexCategoryCompositionItem = {
  categoryCode: string;
  categoryDesc: string;
  nLocales: number;
  share: number;
  color: string;
};

type HexCategoryCompositionProps = {
  items: HexCategoryCompositionItem[];
  totalLocales: number;
  overlayBoundsRef: RefObject<HTMLElement | null>;
  selectedYear: number;
  minYear: number;
  maxYear: number;
  onYearChange: (year: number) => void;
  subjectLabel: string;
};

type DonutSegment = HexCategoryCompositionItem & {
  path: string;
};

type FloatingPanelLayout = {
  top: number;
  left: number;
  width: number;
  maxHeight: number;
};

const DONUT_SIZE = 220;
const DONUT_CENTER = DONUT_SIZE / 2;
const DONUT_OUTER_RADIUS = 82;
const DONUT_INNER_RADIUS = 52;

export function HexCategoryComposition({
  items,
  totalLocales,
  overlayBoundsRef,
  selectedYear,
  minYear,
  maxYear,
  onYearChange,
  subjectLabel,
}: HexCategoryCompositionProps) {
  const [activeCategoryCode, setActiveCategoryCode] = useState<string | null>(null);
  const [floatingPanelLayout, setFloatingPanelLayout] = useState<FloatingPanelLayout | null>(null);
  const chartShellRef = useRef<HTMLDivElement | null>(null);
  const hoverPanelRef = useRef<HTMLElement | null>(null);
  const dismissTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    setActiveCategoryCode(null);
    setFloatingPanelLayout(null);
  }, [items]);

  useEffect(() => {
    return () => {
      if (dismissTimeoutRef.current !== null) {
        window.clearTimeout(dismissTimeoutRef.current);
      }
    };
  }, []);

  const activeItem = items.find((item) => item.categoryCode === activeCategoryCode) ?? null;
  const activeItemRank = activeItem ? items.findIndex((item) => item.categoryCode === activeItem.categoryCode) + 1 : null;
  const segments = useMemo(() => buildDonutSegments(items), [items]);

  useLayoutEffect(() => {
    if (!activeItem || !chartShellRef.current || !overlayBoundsRef.current) {
      setFloatingPanelLayout(null);
      return;
    }

    let frameId = 0;
    const visualViewport = window.visualViewport;
    const scrollContainer = findScrollableAncestor(chartShellRef.current);

    function syncFloatingPanelLayout() {
      if (!chartShellRef.current || !overlayBoundsRef.current) {
        return;
      }

      const triggerRect = chartShellRef.current.getBoundingClientRect();
      const boundsRect = overlayBoundsRef.current.getBoundingClientRect();
      const panelHeight = hoverPanelRef.current?.getBoundingClientRect().height ?? 0;

      setFloatingPanelLayout(
        computeFloatingPanelLayout({
          boundsRect,
          panelHeight,
          triggerRect,
        })
      );
    }

    function scheduleSync() {
      window.cancelAnimationFrame(frameId);
      frameId = window.requestAnimationFrame(syncFloatingPanelLayout);
    }

    scheduleSync();
    window.addEventListener("resize", scheduleSync);
    visualViewport?.addEventListener("resize", scheduleSync);
    scrollContainer?.addEventListener("scroll", scheduleSync, { passive: true });

    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("resize", scheduleSync);
      visualViewport?.removeEventListener("resize", scheduleSync);
      scrollContainer?.removeEventListener("scroll", scheduleSync);
    };
  }, [activeItem, overlayBoundsRef]);

  const fallbackPanelWidth = overlayBoundsRef.current
    ? getFloatingPanelWidth(overlayBoundsRef.current.getBoundingClientRect().width)
    : 320;

  const floatingPanelStyle: CSSProperties = floatingPanelLayout
    ? {
        left: `${floatingPanelLayout.left}px`,
        maxHeight: `${floatingPanelLayout.maxHeight}px`,
        top: `${floatingPanelLayout.top}px`,
        width: `${floatingPanelLayout.width}px`,
      }
    : {
        left: "0px",
        maxHeight: "calc(100dvh - 64px)",
        opacity: 0,
        pointerEvents: "none",
        top: "0px",
        width: `${fallbackPanelWidth}px`,
      };

  function clearDismissTimer() {
    if (dismissTimeoutRef.current !== null) {
      window.clearTimeout(dismissTimeoutRef.current);
      dismissTimeoutRef.current = null;
    }
  }

  function scheduleDismiss() {
    clearDismissTimer();
    dismissTimeoutRef.current = window.setTimeout(() => {
      setActiveCategoryCode(null);
      setFloatingPanelLayout(null);
    }, 120);
  }

  function activateCategory(categoryCode: string) {
    clearDismissTimer();
    setActiveCategoryCode(categoryCode);
  }

  return (
    <>
      <div
        aria-label={`Reparto histórico por categoría dentro del ${subjectLabel} seleccionado`}
        className="hex-category-composition"
      >
        <div className="hex-category-composition-header">
          <p className="hex-category-composition-copy">
            Reparte los {formatInteger(totalLocales)} locales del {subjectLabel} en {selectedYear} entre las categorías históricas observadas. Pasa por cada color del círculo para abrir el detalle al lado.
          </p>
        </div>

        {items.length > 0 ? (
          <div className="hex-category-composition-layout">
            <div
              className="hex-category-composition-chart-shell"
              onMouseEnter={clearDismissTimer}
              onMouseLeave={scheduleDismiss}
              ref={chartShellRef}
            >
              <svg
                aria-label={`Composición por categorías del ${subjectLabel} seleccionado`}
                className="hex-category-composition-chart"
                role="img"
                viewBox={`0 0 ${DONUT_SIZE} ${DONUT_SIZE}`}
              >
                <circle
                  cx={DONUT_CENTER}
                  cy={DONUT_CENTER}
                  fill="none"
                  r={(DONUT_OUTER_RADIUS + DONUT_INNER_RADIUS) / 2}
                  stroke="rgba(23, 32, 38, 0.06)"
                  strokeWidth={DONUT_OUTER_RADIUS - DONUT_INNER_RADIUS}
                />
                {segments.map((segment) => {
                  const isActive = segment.categoryCode === activeItem?.categoryCode;
                  const hasSelection = activeItem !== null;

                  return (
                    <path
                      aria-label={`${segment.categoryDesc}: ${formatCompositionShare(segment.share)} y ${formatInteger(segment.nLocales)} locales`}
                      className="hex-category-composition-slice"
                      d={segment.path}
                      data-active={isActive}
                      data-dimmed={hasSelection && !isActive}
                      fill={segment.color}
                      fillRule="evenodd"
                      key={segment.categoryCode}
                      onMouseEnter={() => activateCategory(segment.categoryCode)}
                    />
                  );
                })}
                <circle
                  cx={DONUT_CENTER}
                  cy={DONUT_CENTER}
                  fill="rgba(255, 250, 242, 0.96)"
                  r={DONUT_INNER_RADIUS - 4}
                  stroke="rgba(23, 32, 38, 0.08)"
                  strokeWidth="1.5"
                />
              </svg>
            </div>
          </div>
        ) : (
          <p className="hex-category-composition-empty">
            Este {subjectLabel} no conserva desglose histórico por categoría para {selectedYear}, aunque figure dentro de Todos los locales.
          </p>
        )}

        <div className="hex-category-composition-year-control">
          <div className="hex-category-composition-year-header">
            <span className="hex-category-composition-year-label">Año</span>
            <strong className="hex-category-composition-year-value">{selectedYear}</strong>
          </div>
          <input
            aria-label={`Seleccionar año de la mezcla del ${subjectLabel}`}
            className="hex-category-composition-year-slider"
            max={maxYear}
            min={minYear}
            onChange={(event) => {
              const nextYear = Number.parseInt(event.target.value, 10);
              if (Number.isFinite(nextYear)) {
                onYearChange(nextYear);
              }
            }}
            step={1}
            type="range"
            value={selectedYear}
          />
          <div className="hex-category-composition-year-range">
            <span>{minYear}</span>
            <span>{maxYear}</span>
          </div>
        </div>
      </div>

      {activeItem && typeof document !== "undefined"
        ? createPortal(
            <aside
              className="hex-category-composition-hover-panel"
              data-floating="true"
              onMouseEnter={clearDismissTimer}
              onMouseLeave={scheduleDismiss}
              ref={hoverPanelRef}
              style={floatingPanelStyle}
            >
              <span className="hex-category-composition-hover-kicker">Categoría resaltada</span>
              <div className="hex-category-composition-hover-title-row">
                <span aria-hidden="true" className="hex-category-composition-swatch" style={{ background: activeItem.color }} />
                <strong className="hex-category-composition-hover-title">{activeItem.categoryDesc}</strong>
              </div>
              <div className="hex-category-composition-hover-stats">
                <div className="hex-category-composition-hover-stat">
                  <span className="hex-category-composition-hover-label">Peso</span>
                  <strong className="hex-category-composition-hover-value">{formatCompositionShare(activeItem.share)}</strong>
                </div>
                <div className="hex-category-composition-hover-stat">
                  <span className="hex-category-composition-hover-label">Locales</span>
                  <strong className="hex-category-composition-hover-value">{formatInteger(activeItem.nLocales)}</strong>
                </div>
                <div className="hex-category-composition-hover-stat">
                  <span className="hex-category-composition-hover-label">Posición</span>
                  <strong className="hex-category-composition-hover-value">#{activeItemRank} de {formatInteger(items.length)}</strong>
                </div>
              </div>
              <p className="hex-category-composition-hover-copy">
                {buildActiveCategoryNarrative(activeItem, totalLocales, subjectLabel)}
              </p>
            </aside>,
            document.body,
          )
        : null}
    </>
  );
}

function findScrollableAncestor(element: HTMLElement) {
  let current: HTMLElement | null = element.parentElement;

  while (current) {
    const styles = window.getComputedStyle(current);
    if ([styles.overflowY, styles.overflow].some((value) => /(auto|scroll|overlay)/.test(value))) {
      return current;
    }
    current = current.parentElement;
  }

  return null;
}

function computeFloatingPanelLayout({
  boundsRect,
  panelHeight,
  triggerRect,
  panelPadding = 18,
}: {
  boundsRect: DOMRect;
  panelHeight: number;
  triggerRect: DOMRect;
  panelPadding?: number;
}): FloatingPanelLayout {
  const width = getFloatingPanelWidth(boundsRect.width, panelPadding);
  const maxHeight = Math.max(180, boundsRect.height - panelPadding * 2);
  const effectiveHeight = panelHeight > 0 ? Math.min(panelHeight, maxHeight) : maxHeight;
  const minTop = boundsRect.top + panelPadding;
  const maxTop = Math.max(minTop, boundsRect.bottom - panelPadding - effectiveHeight);
  const preferredTop = triggerRect.top + triggerRect.height / 2 - effectiveHeight / 2;

  return {
    left: boundsRect.left + panelPadding,
    maxHeight,
    top: Math.min(Math.max(preferredTop, minTop), maxTop),
    width,
  };
}

function getFloatingPanelWidth(boundsWidth: number, panelPadding = 18) {
  const availableWidth = Math.max(236, boundsWidth - panelPadding * 2);
  return Math.min(352, availableWidth);
}

function buildDonutSegments(items: HexCategoryCompositionItem[]): DonutSegment[] {
  if (items.length === 0) {
    return [];
  }

  if (items.length === 1) {
    return [
      {
        ...items[0],
        path: describeFullDonutArc(DONUT_CENTER, DONUT_CENTER, DONUT_OUTER_RADIUS, DONUT_INNER_RADIUS),
      },
    ];
  }

  let currentAngle = -Math.PI / 2;

  return items.map((item) => {
    const sweep = Math.max(0, Math.min(Math.PI * 2, item.share * Math.PI * 2));
    const gapAngle = Math.min(0.024, sweep * 0.3);
    const startAngle = currentAngle + gapAngle / 2;
    const endAngle = currentAngle + sweep - gapAngle / 2;

    currentAngle += sweep;

    return {
      ...item,
      path: describeDonutArc(DONUT_CENTER, DONUT_CENTER, DONUT_OUTER_RADIUS, DONUT_INNER_RADIUS, startAngle, endAngle),
    };
  });
}

function describeFullDonutArc(centerX: number, centerY: number, outerRadius: number, innerRadius: number) {
  return [
    `M ${centerX + outerRadius} ${centerY}`,
    `A ${outerRadius} ${outerRadius} 0 1 1 ${centerX - outerRadius} ${centerY}`,
    `A ${outerRadius} ${outerRadius} 0 1 1 ${centerX + outerRadius} ${centerY}`,
    `M ${centerX + innerRadius} ${centerY}`,
    `A ${innerRadius} ${innerRadius} 0 1 0 ${centerX - innerRadius} ${centerY}`,
    `A ${innerRadius} ${innerRadius} 0 1 0 ${centerX + innerRadius} ${centerY}`,
    "Z",
  ].join(" ");
}

function describeDonutArc(
  centerX: number,
  centerY: number,
  outerRadius: number,
  innerRadius: number,
  startAngle: number,
  endAngle: number,
) {
  const safeEndAngle = Math.max(endAngle, startAngle + 0.001);
  const startOuter = polarToCartesian(centerX, centerY, outerRadius, startAngle);
  const endOuter = polarToCartesian(centerX, centerY, outerRadius, safeEndAngle);
  const startInner = polarToCartesian(centerX, centerY, innerRadius, safeEndAngle);
  const endInner = polarToCartesian(centerX, centerY, innerRadius, startAngle);
  const largeArcFlag = safeEndAngle - startAngle > Math.PI ? 1 : 0;

  return [
    `M ${startOuter.x} ${startOuter.y}`,
    `A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${endOuter.x} ${endOuter.y}`,
    `L ${startInner.x} ${startInner.y}`,
    `A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${endInner.x} ${endInner.y}`,
    "Z",
  ].join(" ");
}

function polarToCartesian(centerX: number, centerY: number, radius: number, angleInRadians: number) {
  return {
    x: centerX + radius * Math.cos(angleInRadians),
    y: centerY + radius * Math.sin(angleInRadians),
  };
}

function formatCompositionShare(value: number) {
  const percent = value * 100;
  const decimals = percent >= 10 || Math.abs(percent - Math.round(percent)) < 0.05 ? 0 : percent >= 1 ? 1 : 2;

  return `${new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(percent)}%`;
}

function formatInteger(value: number) {
  return new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0 }).format(value);
}

function buildActiveCategoryNarrative(item: HexCategoryCompositionItem, totalLocales: number, subjectLabel: string) {
  if (totalLocales <= 1 && item.nLocales <= 1) {
    return `En este ${subjectLabel} solo se observa 1 local en el período seleccionado, así que toda la mezcla corresponde a esta categoría.`;
  }

  if (item.nLocales <= 1) {
    return `Esta categoría solo aparece en 1 local de los ${formatInteger(totalLocales)} observados en el ${subjectLabel}, así que su peso histórico aquí es muy puntual.`;
  }

  if (item.share >= 0.25) {
    return `Es una de las categorías dominantes del ${subjectLabel}: concentra una parte muy visible del histórico local y condiciona bastante la mezcla observada.`;
  }

  if (item.share >= 0.1) {
    return `Tiene un peso intermedio dentro del ${subjectLabel}: no domina la mezcla, pero sí aparece con suficiente frecuencia como para dejar una huella clara.`;
  }

  return `Su presencia es minoritaria dentro del ${subjectLabel}: forma parte de la mezcla histórica, pero queda por detrás de las categorías principales.`;
}
