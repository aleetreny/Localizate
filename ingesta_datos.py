import os
import requests
import time
import re
from tqdm import tqdm

# Proyecto: MADRID LOCAL PREDICT - Ingesta Filtrada REFINADA
BASE_PATH = "DB"
DATASETS = {
    "censo": "209548-0-censo-locales-historico",
    "padron": "209163-0-padron-municipal-historico",
    "avisos": "212411-0-madrid-avisa"
}

LOG_FILE = "ingestion_log.txt"

MONTHS_MAP = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
}

def log_message(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    print(message)

def extract_period(resource):
    name = resource.get('name', '')
    desc = resource.get('description', '')
    full_text = f"{name} {desc}"
    
    match_date = re.search(r'(\d{2})/(\d{2})/(\d{4})', full_text)
    if match_date:
        return f"{match_date.group(3)}_{match_date.group(2)}"
    
    for month_name, month_num in MONTHS_MAP.items():
        if month_name in full_text.lower():
            year_match = re.search(r'\b(20\d{2})\b', full_text)
            if year_match:
                return f"{year_match.group(1)}_{month_num}"

    years = re.findall(r'\b(20\d{2})\b', full_text)
    if years: return years[0]
    return "desconocido"

def get_resources(dataset_id):
    url = f"https://datos.madrid.es/api/3/action/package_show?id={dataset_id}"
    for i in range(3):
        try:
            response = requests.get(url, timeout=90)
            response.raise_for_status()
            return response.json()['result']['resources']
        except Exception as e:
            time.sleep(5)
    return []

def run_ingestion():
    log_message("--- INGESTA REINICIADA: (Solo Locales y Actividades) ---")
    
    for key, dataset_id in DATASETS.items():
        resources = get_resources(dataset_id)
        if not resources: continue

        for res in tqdm(resources, desc=f"Ingestando {key}"):
            fmt = res.get('format', '').upper()
            if fmt not in ['CSV', 'TXT']: continue

            name = res.get('name', '')
            desc = res.get('description', '')
            
            period = extract_period(res)
            target_folder = ""
            
            if key == "censo":
                # Tomamos la última parte después del punto para saber exactamente qué es
                parts = desc.split('.')
                label = parts[-1].strip().lower() if len(parts) > 1 else desc.lower()
                
                if "actividades" in label and "terrazas" not in label:
                    target_folder = "actividades"
                elif "locales" in label and "licencia" not in label and "actividades" not in label:
                    target_folder = "locales"
                else:
                    continue
            elif key == "avisos":
                full_text = f"{name} {desc}".lower()
                if not ("recibidos" in full_text or "tramitados" in full_text): continue
                target_folder = "avisos"
            else: # Padron
                target_folder = "padron"

            ext = ".csv" if (fmt == 'CSV' or (key == "padron" and fmt == 'TXT')) else ".txt"
            filename = f"{period}_{key}_{target_folder}_{res['id']}{ext}"
            
            dest_dir = os.path.join(BASE_PATH, target_folder)
            os.makedirs(dest_dir, exist_ok=True)
            filepath = os.path.join(dest_dir, filename)
            
            if not os.path.exists(filepath):
                try:
                    with requests.get(res['url'], stream=True, timeout=90) as r:
                        r.raise_for_status()
                        with open(filepath, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
                    log_message(f"DESCARGADO: {target_folder}/{filename}")
                except:
                    pass

if __name__ == "__main__":
    run_ingestion()
