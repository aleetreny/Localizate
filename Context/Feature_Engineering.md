# CONTEXTO TÉCNICO FASE 2: INGENIERÍA DE VARIABLES Y MODELADO ESPACIO-TEMPORAL

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

### 1. OBJETIVO DE ESTA FASE

Transformar el _Data Lake_ crudo (Fase 1) en un **Dataset de Entrenamiento Analítico (Analytical Base Table - ABT)**.
El agente debe generar código Python para construir características (_features_) que expliquen el éxito o fracaso de un negocio, respetando rigurosamente la causalidad temporal (no usar datos del futuro para predecir el pasado).

---

### 2. CONSTRUCCIÓN DE LA VARIABLE OBJETIVO (SURVIVAL TARGET)

Para entrenar un modelo de _Survival Analysis_ (e.g., Random Survival Forests), necesitamos estructurar la variable `Y` como pares de datos, no como un simple binario.

- **Lógica de Agrupación:** Agrupar el Censo Histórico por `id_local`.
- **Variable `T` (Tiempo):** Calcular la duración en **meses** desde la `fecha_alta_inicial` hasta la `fecha_baja` (o fecha actual si sigue activo).
- **Variable `E` (Evento):**
  - `1` (True) = El negocio ha cerrado (tenemos fecha de baja).
  - `0` (False) = El negocio sigue abierto a fecha de hoy (Censurado por la derecha).
- **Limpieza de "Zombies":** Detectar locales que reaparecen con el mismo ID después de una baja. Si el _gap_ es pequeño (<2 meses), considerar continuidad. Si es grande, tratar como nueva vida o descartar inconsistencia.

---

### 3. SISTEMA DE INDEXACIÓN ESPACIAL (H3 UBER)

Implementaremos el sistema H3 para estandarizar el espacio y optimizar el rendimiento del mapa de calor posterior.

- **Librería:** `h3-py`.
- **Resolución:** **10** (Hexágonos de ~15.000 m² / arista de ~66m).
- **Asignación:**
  - Crear columna `h3_index` para cada local basada en su Lat/Lon.
  - Crear columna `h3_index` para cada Aviso/Queja del 010.
- **Máscara Comercial (Filtering):** Generar una lista única de todos los `h3_index` donde haya existido al menos un local comercial desde 2015. _Esto definirá el "tablero de juego" válido, excluyendo parques y zonas no comerciales._

---

### 4. INGENIERÍA DE VARIABLES "POINT-IN-TIME" (EVITAR DATA LEAKAGE)

Para cada local $i$ que abrió en la fecha $t$, debemos calcular el estado del entorno **exactamente en $t$ (o en la ventana $t-12$ meses)**.

#### A. Variables de Competencia (Densidad Comercial)

- **Definición:** ¿Cuántos rivales tenía el local al momento de abrir?
- **Algoritmo:**
  1. Para el local $i$ (Categoría "Frutería", Fecha $t$):
  2. Filtrar el censo histórico para obtener solo locales activos en la fecha $t$.
  3. Calcular distancia euclídea o Haversine contra todos los locales de la misma categoría.
  4. **Feature:** `num_competidores_500m`.
  5. **Feature:** `dist_al_competidor_mas_cercano` (metros).

#### B. Variables de Entorno (Avisos 010 - Rolling Window)

- **Definición:** Nivel de degradación/conflictividad de la calle antes de la apertura.
- **Algoritmo:**
  1. Para el local $i$ (Fecha apertura $t$):
  2. Filtrar el dataset de Avisos 010 para conservar solo los registros entre la fecha $t-365 días$ y $t$ (último año).
  3. Realizar conteo espacial (KDTree o BallTree) de avisos en un radio de 100m.
  4. **Feature:** `densidad_quejas_100m_last_year`.
  5. **Feature:** `top_tipo_queja` (ej: "Limpieza", "Ruido").

#### C. Variables Socioeconómicas (Cruce por Polígono)

- **Definición:** Renta y perfil demográfico del cliente potencial en el año de apertura.
- **Algoritmo:**
  1. Cargar Shapefiles de Secciones Censales.
  2. Realizar **Spatial Join** (`gpd.sjoin`) entre las coordenadas del local y las secciones censales.
  3. Asignar la Renta Media y Datos del Padrón correspondientes al **Año de Apertura** (usar Renta 2015 para aperturas 2014-2015).
  4. **Features:** `renta_media_seccion`, `edad_media_poblacion`, `pct_extranjeros`.

#### D. Variables de Infraestructura (Estáticas)

- **Algoritmo:**
  1. Cargar coordenadas de bocas de Metro/Cercanías.
  2. Calcular distancia al punto más cercano usando `sklearn.neighbors.BallTree`.
  3. **Feature:** `dist_metro_mas_cercano` (logarítmica, ya que importa más pasar de 50m a 100m que de 2km a 2.5km).

---

### 5. ONE-HOT ENCODING DE CATEGORÍAS

El Censo de Madrid tiene epígrafes de actividad muy granulares. Debemos agruparlos para que el modelo generalice bien.

- **Acción:** Mapear los cientos de epígrafes a **10-15 Macro-Categorías** relevantes (Hostelería, Alimentación, Textil/Moda, Salud/Estética, Servicios, etc.).
- **Codificación:** Aplicar _One-Hot Encoding_ a estas macro-categorías.

---

### 6. OUTPUT ESPERADO DE ESTA FASE

Un fichero `training_dataset.parquet` listo para `scikit-survival` con la siguiente estructura (ejemplo):

| id_local | h3_index | lat     | lon     | **duration_months** (T) | **event_occurred** (E) | renta_al_abrir | quejas_entorno | dist_metro | num_competencia | es_hosteleria | es_textil | ... |
| :------- | :------- | :------ | :------ | :---------------------- | :--------------------- | :------------- | :------------- | :--------- | :-------------- | :------------ | :-------- | :-- |
| 10045    | 8a39...  | 40.4... | -3.6... | 48                      | True (Cerró)           | 35000          | 12             | 150        | 3               | 1             | 0         | ... |
| 29932    | 8a39...  | 40.4... | -3.6... | 96                      | False (Vivo)           | 38000          | 5              | 400        | 0               | 0             | 1         | ... |

_Nota: Este dataset debe estar limpio de nulos (imputación realizada) y con los tipos de datos correctos (float32 para distancias, bool para eventos)._
