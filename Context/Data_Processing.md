# CONTEXTO TÉCNICO: SCRIPT DE DESCARGA E INGESTA AUTOMÁTICA

## PROYECTO: MADRID LOCAL PREDICT (Datos Abiertos Ayuntamiento de Madrid)

### 1. OBJETIVO

Automatizar la descarga masiva de históricos desde `datos.madrid.es` usando la API CKAN (`package_show`). El agente debe crear una estructura de carpetas `data/raw/` y gestionar reintentos, logs de errores y normalización de nombres de archivos.

### 2. ESTRATEGIA DE API (CKAN)

Usar el endpoint `https://datos.madrid.es/api/3/action/package_show?id={ID_DATASET}`.

- El agente debe extraer la lista de `resources` del JSON.
- Debe filtrar por `format == 'CSV'`.
- Debe implementar `requests.Session()` con `max_retries=3`.

### 3. CONFIGURACIÓN DE DATASETS

El agente debe ejecutar la descarga para estos IDs:

1. **Censo de Locales:** `209548-0-censo-locales-historico`
   - _Filtro nombre:_ "Locales", "Actividades" (Omitir "Licencias", "Terrazas").
   - _Destino:_ `data/raw/locales/` y `data/raw/actividades/`
2. **Padrón Municipal:** `209163-0-padron-municipal-historico`
   - _Destino:_ `data/raw/padron/`
3. **Avisos Madrid:** `212411-0-madrid-avisa`
   - _Filtro (2018-2026):_ Solo ficheros que contengan "(SIC)" y sean "recibidos".
   - _Filtro (2014-2017):_ Solo ficheros que contengan "(AVISA)" y sean "recibidos".
   - _Destino:_ `data/raw/avisos/`

### 4. REQUISITOS DEL CÓDIGO

- Usar `tqdm` para mostrar progreso de descarga.
- Crear un `ingestion_log.txt` para registrar éxito/fallo.
- Si un archivo `.txt` aparece en el padrón, descargarlo y renombrarlo a `.csv`.

```python

import os
import requests
import time
from tqdm import tqdm

# Configuración
BASE_PATH = "data/raw"
DATASETS = {
    "censo": "209548-0-censo-locales-historico",
    "padron": "209163-0-padron-municipal-historico",
    "avisos": "212411-0-madrid-avisa"
}

def get_resources(dataset_id):
    url = f"https://datos.madrid.es/api/3/action/package_show?id={dataset_id}"
    response = requests.get(url).json()
    return response['result']['resources']

def download_file(url, folder, filename):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    if os.path.exists(filepath):
        return "Exists"

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    with session.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return "Downloaded"

def run_ingestion():
    for key, dataset_id in DATASETS.items():
        print(f"Procesando {key}...")
        resources = get_resources(dataset_id)

        for res in tqdm(resources):
            if res['format'].upper() in ['CSV', 'TXT']:
                name = res['name']
                url = res['url']

                # Lógica de filtrado inteligente
                if key == "censo":
                    if "Locales" in name: folder = "locales"
                    elif "Actividades" in name: folder = "actividades"
                    else: continue
                elif key == "avisos":
                    # Lógica de solapamiento SIC/AVISA
                    if "2018" in name or "2019" in name or "2020" in name or "2021" in name or "2022" in name or "2023" in name or "2024" in name or "2025" in name or "2026" in name:
                        if "(SIC)" not in name or "recibidos" not in name.lower(): continue
                    else:
                        if "(AVISA)" not in name or "recibidos" not in name.lower(): continue
                    folder = "avisos"
                else:
                    folder = "padron"

                ext = ".csv" if res['format'].upper() == 'CSV' else ".txt"
                filename = f"{name.replace(' ', '_')}{ext}"

                status = download_file(url, os.path.join(BASE_PATH, folder), filename)
                # Log opcional aquí

if __name__ == "__main__":
    run_ingestion()
```

# el data set del INE y de las entradas de metro los descargo yo solo aqui en local, no hace falta que lo hagas tu
