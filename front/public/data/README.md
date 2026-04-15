# Frontend Data Layout

Artefactos estaticos servidos por `apps/web`.

## Estructura

- `map/shared.json`
  - metadatos, categorias y agregados zonales comunes a la vista historica
- `map/hex/{small,medium,large}.json`
  - solo filas hexagonales por tamano
- `map/historical/rankings.json`
  - series temporales zonales para comparativas y evolucion historica
- `map/historical/hex-composition.json`
  - composicion anual por hexagono
- `map/zones/boundaries.json`
  - limites administrativos simplificados
- `opportunities/listings.json`
  - puntos de locales disponibles
- `opportunities/sections/index.json`
  - indice descriptivo completo por seccion para metricas y benchmarks
- `opportunities/sections/geometry.geojson`
  - geometria minima de secciones para el mapa

## Regla

No volver a introducir artefactos planos `frontend-*.json` o `frontend-*.geojson` en esta carpeta raiz.
Los builders deben escribir siempre dentro de `map/` u `opportunities/`.
