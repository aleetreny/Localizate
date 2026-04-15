# Localizate

Proyecto para construir un mapa inteligente de locales comerciales de Madrid, con dos superficies claras:

- `front/`: aplicación web pública en `Next.js`.
- `back/`: pipeline Python, builders de artefactos, lógica analítica y tests.

La raíz queda reservada para la orquestación del monorepo, la documentación y el almacenamiento local no versionado.

## Estructura

- `front/`
  - app web lista para desplegar en Vercel u otro proveedor frontend.
- `back/`
  - `src/localizate/`: paquete Python principal.
  - `scripts/`: CLI y builders operativos.
  - `tests/`: batería de pruebas del backend.
  - `configs/`: configuración local del pipeline.
  - `requirements.txt`: dependencias Python.
- `docs/`
  - `frontend/`: decisiones y auditorías del producto web.
  - `modeling/`: ABT, validaciones y resultados de modelado.
  - `data/`: contratos, ingesta y materialización de datasets.
  - `project/`: bitácora, roadmap y estado operativo.
  - `reference/`: glosarios e inventarios de variables.
- `storage/`
  - `raw/`: lago de datos local bruto.
  - `data/`: tablas intermedias, features y exports.
  - `models/`: artefactos y métricas de entrenamiento.

## Comandos habituales

Backend:

```powershell
.venv\Scripts\python.exe -m pip install -r back\requirements.txt
cd back
..\.venv\Scripts\python.exe -m unittest
```

Frontend:

```powershell
cd front
npm run typecheck
npm run build
```

Builders principales desde la raíz:

```powershell
$env:PYTHONPATH = "back/src"
.venv\Scripts\python.exe back\scripts\build_frontend_map_artifacts.py
.venv\Scripts\python.exe back\scripts\build_frontend_opportunity_artifacts.py
```

## Despliegue

- `front/` es la carpeta pensada para desplegar la web en Vercel.
- `back/` es la carpeta pensada para desplegar o ejecutar el backend/pipeline en el proveedor que toque.
- `storage/` es local y operativo; no forma parte del despliegue de hobby.

## Documentación clave

- `docs/project/STATUS.md`: contexto operativo acumulado.
- `docs/frontend/frontend_web_mvp.md`: contrato funcional de la web.
- `docs/modeling/abt_pit_contract.md`: reglas para evitar leakage temporal.
- `docs/reference/ACTIVITY_GLOSSARY.md`: glosario de categorías.
- `docs/reference/VARIABLES.md`: inventario de variables.
