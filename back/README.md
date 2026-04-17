# Back

`back/` contiene el pipeline analitico de Localizate: limpieza, integracion de fuentes, construccion de artefactos publicos, entrenamiento de modelos y pruebas.

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
- `sync_public_data_to_r2.py`: publica artefactos estaticos en el bucket configurado.

Los artefactos publicos que consume la web se generan aqui y se sirven despues desde `front/public/data/` o desde almacenamiento externo.
