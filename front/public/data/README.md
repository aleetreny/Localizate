# Public Data Layout

Artefactos públicos servidos por `front/` o publicados externamente para la web.

## Estructura

- `map/shared.json`
  - metadatos, categorías y agregados comunes a la vista Histórico.
- `map/hex/{small,medium,large}.json`
  - geometría H3 y métricas por tamaño de malla.
- `map/historical/rankings.json`
  - series temporales y rankings zonales.
- `map/historical/hex-composition.json`
  - composición anual por hexágono.
- `map/zones/boundaries.json`
  - límites administrativos simplificados.
- `opportunities/listings.json`
  - locales disponibles publicados en la web.
- `opportunities/sections/index.json`
  - contexto descriptivo completo por sección.
- `opportunities/sections/geometry.geojson`
  - geometría mínima usada por el mapa de oportunidades.

## Regla

Los builders deben escribir siempre dentro de `map/` u `opportunities/`. Esta carpeta solo contiene artefactos públicos listos para servir; el procesamiento intermedio vive fuera del frontend.
