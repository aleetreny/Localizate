# Localízate

Localízate es una web de inteligencia comercial para Madrid construida sobre datos abiertos, analitica geoespacial y modelos de supervivencia. Su objetivo es ayudar a explorar el tejido comercial de la ciudad y a evaluar ubicaciones concretas con una lectura visual, explicable y util para la toma de decisiones.

Web publica: https://localizate.pages.dev/

![Vista previa de Localízate](Preview.png)

## Que ofrece

- Vista `Historico`: lectura territorial del mercado por distrito, barrio y hexagono.
- Vista `Oportunidades`: evaluacion puntual de locales disponibles o direcciones concretas.
- Contexto urbano y socioeconomico: renta, poblacion, accesibilidad, equipamientos, avisos e indicadores territoriales.
- Arquitectura de publicacion ligera: frontend estatico, datos publicos precalculados y servicios dinamicos solo donde aportan valor.

## Arquitectura

- `front/`: aplicacion web en `Next.js`, `TypeScript`, `MapLibre` y `deck.gl`.
- `back/`: pipeline analitico en Python para construir artefactos, features y exportaciones publicas.
- `workers/opportunity-geocode/`: worker para geocodificacion y resolucion de direccion a seccion censal.
- `.github/workflows/`: automatizaciones de build, publicacion de datos y despliegue.
- `docs/`: documentacion funcional, tecnica y metodologica preparada para una lectura publica.

La publicacion actual sigue un patron simple:

- `Cloudflare Pages` sirve la web estatica.
- `Cloudflare R2` aloja los JSON publicos pesados.
- `Cloudflare Workers` resuelve la geocodificacion bajo demanda.
- `GitHub Actions` orquesta build, publicacion y despliegue.

## Arranque local

Backend:

```powershell
.venv\Scripts\python.exe -m pip install -r back\requirements.txt
cd back
$env:PYTHONPATH = "src"
..\.venv\Scripts\python.exe -m unittest
```

Frontend:

```powershell
cd front
npm install
npm run typecheck
npm run dev
```

Build estatico:

```powershell
cd front
npm run build:static
```

Builders mas habituales desde la raiz:

```powershell
$env:PYTHONPATH = "back/src"
.venv\Scripts\python.exe back\scripts\build_frontend_map_artifacts.py
.venv\Scripts\python.exe back\scripts\build_frontend_opportunity_artifacts.py
.venv\Scripts\python.exe back\scripts\build_frontend_opportunity_listings.py
```

## Estructura del repo

```text
Localízate/
|- front/                  # web publica
|- back/                   # pipeline, scripts y tests
|- workers/                # servicios dinamicos
|- docs/                   # documentacion publica del proyecto
|- storage/                # datos locales no versionados
`- .github/workflows/      # automatizacion de despliegues y refrescos
```

## Documentacion recomendada

- [Resumen del proyecto](docs/project/project-overview.md)
- [Vision de producto](docs/product/product-overview.md)
- [Inventario documental](docs/README.md)
- [Fuentes y contratos de datos](docs/data/raw_data_inventory.md)
- [Panel socioeconomico por seccion](docs/data/section_socioeconomic_panel.md)
- [Resultados y decisiones de modelado](docs/modeling/survival_canonical.md)
- [Glosario de categorias comerciales](docs/reference/ACTIVITY_GLOSSARY.md)

## Alcance y limites

El repositorio publica codigo, documentacion y artefactos necesarios para entender el proyecto, pero no incluye el lago de datos bruto, modelos locales intermedios ni credenciales de despliegue. La web no pretende sustituir trabajo de campo, analisis financiero ni validacion comercial in situ: es una herramienta de apoyo a la decision, no una garantia de exito.
