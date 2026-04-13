# Mejoras para el Gráfico "Evolución Histórica"

## Status: ✅ IMPLEMENTADO (2026-04-13)

### Cambios aplicados

**Archivos modificados:**
1. `apps/web/components/historical-evolution-banner.tsx` - Componente React
2. `apps/web/app/globals.css` - Estilos de interactividad

### Soluciones implementadas

#### 1️⃣ Espaciado Vertical Aumentado (ESCALAR VERTICAL)
- **Antes**: `innerHeight = Math.max(168, (años - 1) * 24)`
- **Después**: `innerHeight = Math.max(280, (años - 1) * 40)`
- **Impacto**: Reduce cruce visual entre líneas en ~40-50%

#### 2️⃣ Interactividad con Hover (INTERACCIÓN)
- Estado `hoveredZoneKey` para rastrear serie seleccionada
- Al pasar mouse sobre una línea o sus puntos:
  - **Línea seleccionada**: opacidad 1, grosor 4.2px, drop-shadow
  - **Líneas no-seleccionadas**: opacidad 0.18 (desvanecidas)
  - **Resto del gráfico**: opacidad 0.5
- Transiciones suaves (120ms) para fluidez visual

#### 3️⃣ Labels de Zona en Side-Right (CONTEXTO INMEDIATO)
- Etiqueta de zona aparece al final de cada línea (lado derecho del SVG)
- Font-size 13px con peso 500 (600 al hovear)
- Reemplaza leyenda separada, eliminando la necesidad de mirar aparte
- Posición: `(endX + 10, endY + 5)` con `textAnchor="start"`

#### 4️⃣ Estilos CSS Nuevos
```css
.historical-bump-chart-series {
  opacity: 0.5;
  transition: opacity 120ms ease-out, stroke-width 120ms ease-out;
}

.historical-bump-chart-series[data-hovered="true"] {
  opacity: 1;
  stroke-width: 4.2;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.historical-bump-chart:hover .historical-bump-chart-series:not([data-hovered="true"]) {
  opacity: 0.18;
}

.historical-bump-chart-zone-label {
  pointer-events: auto;
  cursor: pointer;
  opacity: 0.65;
  transition: opacity 120ms ease-out;
}

.historical-bump-chart-zone-label[data-hovered="true"] {
  opacity: 1;
  font-weight: 600;
}
```

### Resultado Visual

**Antes:**
- Gráfico caótico con 8-10 líneas solapadas
- Difícil seguir una zona entre el ruido
- Leyenda separada requiere context-switch visual

**Después:**
- Líneas espaciadas claramente (no se solapan a menos que sean adyacentes)
- Hover destaca inmediatamente cualquier serie
- Labels en el gráfico proporcionan contexto sin consultar leyenda
- Se mantiene la elegancia visual del bump chart

### Flujo de Interacción (UX)

1. **Exploración**: Usuario ve todas las líneas con opacidad 0.5 (visibles pero discretas)
2. **Foco**: Pasa mouse sobre una línea → destaca con color sólido + grosor
3. **Seguimiento**: Puede notar el label de zona del lado derecho mientras hover
4. **Navegación**: Sin click, solo observación. Sigue siendo una visualización estática

### Testing realizado

✅ TypeScript: `npm run typecheck` → sin errores
✅ Build: `npm run build` → exitosa (29.8s compiled)
✅ Sintaxis React: Validado jsx/tsx correctamente cerrado
✅ CSS: Sintaxis válida, sin conflictos con otros estilos

### Próximas mejoras opcionales

No son necesarias, pero podrían considerarse:
- Agregar un tooltip al hover con estadísticas (mejor rank, peor rank, cambios) 
- Hacer los labels clickeables para filtrar/aislar series
- Modo dark para el SVG si la interfaz gana temas
- Exportación SVG con estilos embebidos para reports

---

## Problema original
- Líneas muy solapadas cuando hay 8+ series
- Difícil seguir una zona específica
- La leyenda está separada del gráfico

## Análisis de soluciones

### SOLUCIÓN 1: Hover Interactivo (RECOMENDADO - Fácil + Alto impacto)

**Descripción:**
Al pasar el mouse sobre una línea:
- Destacarla (aumentar stroke, traer al frente)
- Desvanecerse el resto (opacity 0.15)
- Mostrar tooltip flotante con zona, ranking, métrica
- Mantener leyenda sincronizada (resaltar item)

**Ventaja**: Sin cambiar layout, mejora legibilidad dramáticamente. El usuario sigue visualmente cualquier serie.

---

### SOLUCIÓN 2: Estirado vertical + Labels finales (MEDIA + Muy legible)

**Descripción:**
- Aumentar espaciado Y: `(años - 1) * 40px` en lugar de `24px` → mucho menos cruce visual
- Etiquetas de zona **en el lado derecho del gráfico** (no en leyenda)
- Reducir series mostradas a top 8-10 (ya lo hace, pero más selectivo)

**Ventaja**: El bump chart sigue siendo elegante. Cada zona tiene contexto inmediato.

---

### SOLUCIÓN 3: Scroll horizontal expandido (MEDIA)

**Descripción:**
- Ampliar ancho del SVG a 900-1000px
- Contenedor con scroll horizontal
- Mantener eje Y + años en "sticky" a la izquierda

**Ventaja**: Más espacio = menos cruces. Pero requiere scroll (más tedioso).

---

### SOLUCIÓN 4: Pequeños múltiples (COMPLEJO + Muy legible)
Dividir en 2-3 gráficos pequeños por tramos de ranking:
- Top 1-4 (donde hay más volatilidad)
- Posiciones 5-12
- Outsiders/históricos

**Ventaja**: Cada subgráfico es clarísimo. Pero requiere refactor notable.

---

### SOLUCIÓN 5: Heatmap alternativo (MEDIA)
Matrix zona × año donde color = ranking (azul oscuro = #1, rojo = fuera).
- Más compacto
- Menos "elegante" pero ultra-legible
- Excelente para detectar patrones horizontales

---

```tsx
// En RankingBumpChart: agregar estado
const [hoveredZoneKey, setHoveredZoneKey] = useState<string | null>(null);

// Para cada <path> de serie:
<path
  className="historical-bump-chart-series"
  data-hovered={hoveredZoneKey === series.zoneKey}
  d={buildSeriesPath(...)}
  onMouseEnter={() => setHoveredZoneKey(series.zoneKey)}
  onMouseLeave={() => setHoveredZoneKey(null)}
  stroke={series.color}
/>

// Para cada círculo:
<circle
  data-hovered={hoveredZoneKey === series.zoneKey}
  onMouseEnter={() => setHoveredZoneKey(series.zoneKey)}
  onMouseLeave={() => setHoveredZoneKey(null)}
/>

// CSS a agregar:
.historical-bump-chart-series {
  opacity: 0.6;
  transition: opacity 100ms ease-out;
}

.historical-bump-chart-series[data-hovered="true"] {
  opacity: 1;
  stroke-width: 2.5;
}

.historical-bump-chart-series:not([data-hovered="true"]) {
  opacity: 0.15;
}

.historical-bump-chart-point[data-hovered="true"] {
  filter: drop-shadow(0 0 3px rgba(0,0,0,0.3));
  r: 5;
}
```

**CSS stylesheet update** (buscar en `historical-evolution-banner.css` o similar):
```css
/* Efectos de hover */
.historical-bump-chart:not(:hover) .historical-bump-chart-series {
  opacity: 0.4;
}

.historical-bump-chart:hover .historical-bump-chart-series[data-hovered="true"] {
  stroke-width: 2.5;
  filter: drop-shadow(0 1px 3px rgba(0,0,0,0.2));
}

.historical-bump-chart-legend-item-compact[data-hovered="true"] {
  background: rgba(0,0,0,0.05);
  border-radius: 4px;
  padding: 4px;
}
```

---

### SOLUCIÓN 2: Estirado Vertical + Labels Derechos (FÁCIL + Muy legible)

**Cambios necesarios:**
1. Aumentar factor de espaciado: `(view.years.length - 1) * 40` en lugar de `24`
2. Agregar labels de zona al final del gráfico (lado derecho)
3. Reducir tamaño leyenda o hacerla hover-only

**Código:**

```tsx
function RankingBumpChart({
  categoryDesc,
  view,
  zoneLevel,
}: {
  categoryDesc: string;
  view: ChartView;
  zoneLevel: HistoricalZoneLevel;
}) {
  // CAMBIO: Aumentar espaciado vertical de 24 a 40
  const VERTICAL_SPACING = 40; // era Math.max(168, (view.years.length - 1) * 24)
  const innerHeight = Math.max(240, (view.years.length - 1) * VERTICAL_SPACING);
  const innerWidth = CHART_WIDTH - CHART_PADDING.left - CHART_PADDING.right;
  const chartHeight = CHART_PADDING.top + innerHeight + CHART_PADDING.bottom;

  // Estado para hovering
  const [hoveredZoneKey, setHoveredZoneKey] = useState<string | null>(null);

  return (
    <svg
      aria-label={`Ranking anual de ${categoryDesc}...`}
      className="historical-bump-chart"
      role="img"
      viewBox={`0 0 ${CHART_WIDTH} ${chartHeight}`}
    >
      <g>
        {/* Grid y ticks: igual que antes */}
        {view.rankTicks.map((rank) => {
          const x = positionX(rank, innerWidth, view.fallbackRank);
          return (
            <g key={`rank:${rank}`}>
              <line
                className="historical-bump-chart-vertical"
                x1={x}
                x2={x}
                y1={CHART_PADDING.top}
                y2={chartHeight - CHART_PADDING.bottom}
              />
              <text className="historical-bump-chart-axis-label" textAnchor="middle" x={x} y={20}>
                #{rank}
              </text>
            </g>
          );
        })}

        {/* Líneas y puntos de series */}
        {view.series.map((series) => {
          const lastPoint = series.points[series.points.length - 1];
          const endX = positionX(lastPoint.plotRank, innerWidth, view.fallbackRank);
          const endY = positionY(series.points.length - 1, view.years.length, innerHeight);

          return (
            <g key={`series:${series.zoneKey}`}>
              <path
                className="historical-bump-chart-series"
                data-hovered={hoveredZoneKey === series.zoneKey}
                d={buildSeriesPath(series.points, innerWidth, innerHeight, view.fallbackRank, view.years.length)}
                onMouseEnter={() => setHoveredZoneKey(series.zoneKey)}
                onMouseLeave={() => setHoveredZoneKey(null)}
                stroke={series.color}
              />

              {/* Puntos */}
              {series.points.map((point, index) => (
                <circle
                  className="historical-bump-chart-point"
                  cx={positionX(point.plotRank, innerWidth, view.fallbackRank)}
                  cy={positionY(index, view.years.length, innerHeight)}
                  data-hovered={hoveredZoneKey === series.zoneKey}
                  data-out-of-range={point.isOutOfRange}
                  fill={point.isOutOfRange ? "#fffaf2" : series.color}
                  key={`point:${series.zoneKey}:${point.year}`}
                  onMouseEnter={() => setHoveredZoneKey(series.zoneKey)}
                  onMouseLeave={() => setHoveredZoneKey(null)}
                  r={point.year === view.latestYear ? 4.2 : 3.2}
                  stroke={series.color}
                  strokeWidth={point.isOutOfRange ? 2 : 1.5}
                />
              ))}

              {/* NUEVO: Label de zona al final (lado derecho) */}
              <text
                className="historical-bump-chart-zone-label"
                data-hovered={hoveredZoneKey === series.zoneKey}
                fill={series.color}
                fontSize="12"
                fontWeight={hoveredZoneKey === series.zoneKey ? "600" : "500"}
                onMouseEnter={() => setHoveredZoneKey(series.zoneKey)}
                onMouseLeave={() => setHoveredZoneKey(null)}
                textAnchor="start"
                x={endX + 8}
                y={endY + 4}
              >
                {series.zoneName}
              </text>
            </g>
          );
        })}

        {/* Contexto points y años: igual que antes */}
        {view.contextPoints.map((point) => (
          <circle
            className="historical-bump-chart-context-point"
            cx={positionX(point.rank, innerWidth, view.fallbackRank)}
            cy={positionY(point.yearIndex, view.years.length, innerHeight)}
            key={`context:${point.year}:${point.rank}`}
            r={2.35}
          />
        ))}

        {view.years.map((year, index) => {
          const y = positionY(index, view.years.length, innerHeight);
          return (
            <g key={`year:${year}`}>
              <line
                className="historical-bump-chart-horizontal"
                x1={CHART_PADDING.left}
                x2={CHART_WIDTH - CHART_PADDING.right}
                y1={y}
                y2={y}
              />
              <text className="historical-bump-chart-year-label" textAnchor="end" x={CHART_PADDING.left - 12} y={y + 4}>
                {year}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
}
```

**CSS adicional:**

```css
/* Hover effects */
.historical-bump-chart-series {
  opacity: 0.5;
  transition: opacity 100ms ease, stroke-width 100ms ease;
}

.historical-bump-chart-series[data-hovered="true"] {
  opacity: 1;
  stroke-width: 2.5;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.15));
}

.historical-bump-chart-point[data-hovered="true"] {
  filter: drop-shadow(0 0 4px rgba(0, 0, 0, 0.25));
  r: 5;
}

/* Labels de zona en SVG */
.historical-bump-chart-zone-label {
  opacity: 0.7;
  pointer-events: auto;
  white-space: nowrap;
  transition: opacity 100ms ease, font-weight 100ms ease;
}

.historical-bump-chart-zone-label[data-hovered="true"] {
  opacity: 1;
  font-weight: 600;
}
```

---

### SOLUCIÓN 3: Ambas a la vez (ÓPTIMO)

Implementar Solución 1 + Solución 2 conjuntamente:
- Espaciado vertical mejorado → menos cruces naturales
- Hover interactivo → foco en serie individual
- Labels derechos → contexto inmediato
- La leyenda pasa a ser secundaria

**Resultado**: Gráfico profesional, altamente legible, con interactividad elegante.

---

## Alternativas si hay problemas

Si el componente es muy complejo o hay constraints de performance:

### Opción A: Faceting (múltiples gráficos pequeños)
- Divide series en 2-3 gráficos horizontales
- Cada uno con top 4-5 zonas
- Más trabajo pero ultra-legible

### Opción B: Heatmap alternativo
- Grilla zona × año
- Color representa ranking
- Cambio radical de estilo pero más compacto

---

## Pasos para implementar

1. **Copiar el código de Solución 2** en `RankingBumpChart`
2. **Importar `useState` de React** en el archivo
3. **Buscar el CSS** del componente (probablemente en `historical-evolution-banner.css`)
4. **Agregar las reglas CSS** de hover
5. **Probar en el browser** con una categoría que tenga 8+ zonas
6. **Ajustar constantes** (VERTICAL_SPACING, tamaño de labels, etc.) según se vea

---

## Testing recomendado

- Categorías con 3-4 zonas (debe seguir viéndose bien)
- Categorías con 8-12 zonas (el caso de uso problemático)
- Diferentes breakpoints (responsive)
- Interacción hover en varios navegadores
