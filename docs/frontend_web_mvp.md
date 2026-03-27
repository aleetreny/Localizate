# Frontend Web MVP

Estado inicial del nuevo frontend web para el mapa de supervivencia comercial de Madrid.

## Stack

- `Next.js` App Router
- `TypeScript`
- `MapLibre GL`
- `deck.gl` con `H3HexagonLayer`
- Datos estaticos generados offline desde el pipeline Python actual

## Objetivo del corte actual

- Sustituir la idea inicial de `Streamlit` como frontend final.
- Levantar un mapa minimalista de Madrid con dimensiones definidas y UX limpia.
- Pintar regiones de prediccion por hexagono H3.
- Permitir filtro por tipo de local y horizonte `12m/24m`.
- Dejar una frontera de datos clara para pasar a API mas adelante sin rehacer componentes.

## Artefacto de datos actual

- Script generador: `scripts/build_frontend_map_artifacts.py`
- Salida: `apps/web/public/data/frontend-map-artifacts.json`

El builder cruza:

- `data/features/activity_survival_abt.csv`
- `data/exports/activity_survival_map_export.csv`
- `data/exports/district_category_survival.csv`
- `data/exports/barrio_category_survival.csv`

Y produce:

- agregados por hexagono H3 y categoria
- opciones de selector
- payload zonal para siguientes iteraciones de detalle
- metadata de viewport fijo sobre Madrid

## Convenciones del MVP

- Color principal: supervivencia observada agregada por hexagono
- Riesgo `ensemble`: metrica secundaria de apoyo
- Region primaria de UI: H3, no poligonos administrativos completos
- Carga inicial: artefacto estatico, no fetch a backend

## Arranque local

1. Regenerar artefactos del mapa si cambian los exports:

```powershell
C:/Users/Z0058EYW/Workspace/Localizate/.venv/Scripts/python.exe .\scripts\build_frontend_map_artifacts.py
```

2. Instalar dependencias web:

```powershell
Set-Location .\apps\web
npm install
```

3. Arrancar en desarrollo:

```powershell
npm run dev
```

4. Validar tipos:

```powershell
npm run typecheck
```

5. Validar build de produccion:

```powershell
npm run build
```

## Siguiente iteracion natural

- enriquecer el panel lateral con resumen de distrito/barrio
- exponer mas comparativas de categoria en click de hexagono
- evaluar si conviene servir artefactos por viewport desde API ligera