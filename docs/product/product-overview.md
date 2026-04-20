# Visión de producto

## Qué es Localízate

Localízate es una web de lectura comercial para Madrid que combina datos históricos, contexto urbano y modelado de supervivencia para ayudar a explorar el mercado y evaluar ubicaciones concretas.

## Vistas principales

### Histórico

- Explora el comportamiento del tejido comercial por categoría.
- Permite leer Madrid por distrito, barrio y hexágono.
- Resume ranking, supervivencia observada, índice relativo y comparativas territoriales.

### Oportunidades

- Parte de locales disponibles o de una dirección introducida manualmente.
- Abre una ficha contextual por sección censal.
- Combina riesgo esperado, benchmarks, actividades sugeridas y contexto socioeconómico y urbano.

## Stack del producto

- `Next.js` App Router
- `TypeScript`
- `MapLibre GL`
- `deck.gl`
- artefactos estáticos generados offline desde el pipeline Python

## Artefactos que consume la web

- `front/public/data/map/shared.json`
- `front/public/data/map/hex/{small,medium,large}.json`
- `front/public/data/map/historical/{rankings,hex-composition}.json`
- `front/public/data/map/zones/boundaries.json`
- `front/public/data/opportunities/listings.json`
- `front/public/data/opportunities/sections/index.json`
- `front/public/data/opportunities/sections/geometry.geojson`

## Arranque local

### Regenerar artefactos

```powershell
$env:PYTHONPATH = "back/src"
.venv\Scripts\python.exe back\scripts\build_frontend_map_artifacts.py
.venv\Scripts\python.exe back\scripts\build_frontend_opportunity_artifacts.py
```

### Ejecutar frontend

```powershell
cd front
npm install
npm run dev
```

### Validar tipos y build

```powershell
cd front
npm run typecheck
npm run build
```

## Criterios de producto

- La experiencia prioriza claridad visual y tiempos de carga bajos.
- El frontend no debe recalcular analítica pesada en cliente.
- Cuando una métrica no tiene soporte suficiente, la interfaz debe ser prudente y explicarlo.
- Las vistas están pensadas como apoyo a la decisión, no como un sustituto del análisis comercial completo.
