# Public Data Layout

Artefactos publicos servidos por `front/` o publicados externamente para la web.

## Estructura

- `map/shared.json`
  - metadatos, categorias y agregados comunes a la vista Historico.
- `map/hex/{small,medium,large}.json`
  - geometria H3 y metricas por tamano de malla.
- `map/historical/rankings.json`
  - series temporales y rankings zonales.
- `map/historical/hex-composition.json`
  - composicion anual por hexagono.
- `map/zones/boundaries.json`
  - limites administrativos simplificados.
- `opportunities/listings.json`
  - locales disponibles publicados en la web.
- `opportunities/sections/index.json`
  - contexto descriptivo completo por seccion.
- `opportunities/sections/geometry.geojson`
  - geometria minima usada por el mapa de oportunidades.

## Regla

Los builders deben escribir siempre dentro de `map/` u `opportunities/`. Esta carpeta solo contiene artefactos publicos listos para servir; el procesamiento intermedio vive fuera del frontend.
