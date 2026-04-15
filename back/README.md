# Back

Backend analítico y pipeline Python de Localizate.

Incluye:

- `src/localizate/`: lógica de negocio y transformaciones.
- `scripts/`: builders y CLI operativas.
- `tests/`: pruebas automáticas.
- `configs/`: configuración local.

Comandos habituales desde esta carpeta:

```powershell
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
..\.venv\Scripts\python.exe -m unittest
```

Los builders del frontend viven aquí porque los artefactos públicos se generan desde el pipeline Python.
