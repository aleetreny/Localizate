# Back

`back/` contiene el pipeline analítico de Localízate: limpieza, integración de fuentes, construcción de artefactos públicos, entrenamiento de modelos y pruebas.

## Contenido

- `src/localizate/`: lógica principal del proyecto.
- `scripts/`: builders y utilidades de operación.
- `tests/`: pruebas unitarias y de integración ligera.
- `requirements.txt`: dependencias del pipeline completo.
- `requirements-opportunity-weekly.txt`: dependencias minimizadas para el refresco semanal de oportunidades.

## Uso habitual

```powershell
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
..\.venv\Scripts\python.exe -m unittest
```

## Scripts clave

- `build_frontend_map_artifacts.py`: genera los JSON de la vista Histórico.
- `build_frontend_opportunity_artifacts.py`: genera los artefactos base de Oportunidades.
- `build_frontend_opportunity_listings.py`: construye el payload público de locales disponibles.
- `refresh_opportunity_listings_cloudflare.py`: refresca de forma conservadora el snapshot versionado de locales usando Cloudflare Browser Run y reutilizando el contexto previo.
- `sync_public_data_to_r2.py`: publica artefactos estáticos en el bucket configurado.

Los artefactos públicos que consume la web se generan aquí y se sirven después desde `front/public/data/` o desde almacenamiento externo.

## Snapshot versionado de oportunidades

El refresco semanal de oportunidades ya no depende de un scrape completo efímero dentro de GitHub Actions. Ahora parte de un snapshot versionado en `back/data/opportunities/manual_available_locales_madrid_snapshot.csv`, reutiliza coordenadas y secciones ya conocidas, y solo geocodifica listings nuevos o relocalizados dentro de un presupuesto conservador.
