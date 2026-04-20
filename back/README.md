# Back

`back/` contiene el pipeline analitico de Localízate: limpieza, integracion de fuentes, construccion de artefactos publicos, entrenamiento de modelos y pruebas.

## Contenido

- `src/localizate/`: logica principal del proyecto.
- `scripts/`: builders y utilidades de operacion.
- `tests/`: pruebas unitarias y de integracion ligera.
- `requirements.txt`: dependencias del pipeline completo.
- `requirements-opportunity-weekly.txt`: dependencias minimizadas para el refresco semanal de oportunidades.

## Uso habitual

```powershell
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
..\.venv\Scripts\python.exe -m unittest
```

## Scripts clave

- `build_frontend_map_artifacts.py`: genera los JSON de la vista Historico.
- `build_frontend_opportunity_artifacts.py`: genera los artefactos base de Oportunidades.
- `build_frontend_opportunity_listings.py`: construye el payload publico de locales disponibles.
- `refresh_opportunity_listings_cloudflare.py`: refresca de forma conservadora el snapshot versionado de locales usando Cloudflare Browser Run y reutilizando el contexto previo.
- `sync_public_data_to_r2.py`: publica artefactos estaticos en el bucket configurado.

Los artefactos publicos que consume la web se generan aqui y se sirven despues desde `front/public/data/` o desde almacenamiento externo.

## Snapshot versionado de oportunidades

El refresco semanal de oportunidades ya no depende de un scrape completo efimero dentro de GitHub Actions. Ahora parte de un snapshot versionado en `back/data/opportunities/manual_available_locales_madrid_snapshot.csv`, reutiliza coordenadas y secciones ya conocidas, y solo geocodifica listings nuevos o relocalizados dentro de un presupuesto conservador.
