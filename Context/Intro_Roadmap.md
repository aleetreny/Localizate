# CONTEXTO GENERAL Y ROADMAP DEL PROYECTO: "MADRID LOCAL PREDICT"

## PREMIOS A LA REUTILIZACIÓN DE DATOS ABIERTOS - AYUNTAMIENTO DE MADRID 2026

### 1. VISIÓN GENERAL DEL PROYECTO

El objetivo es desarrollar una aplicación web interactiva orientada a emprendedores y pequeños comerciantes. La herramienta evaluará locales comerciales actualmente vacíos o inactivos en la ciudad de Madrid y predecirá la **probabilidad de supervivencia (éxito) a lo largo del tiempo** para diferentes tipologías de negocio (ej. frutería, bar, peluquería).

El proyecto compite en la **Categoría A (Servicios web, aplicaciones y visualizaciones)** de los Premios del Ayuntamiento de Madrid 2026. Para maximizar la puntuación (basada en utilidad, variedad de datasets, innovación y calidad técnica), el proyecto integra:

1. **Machine Learning Avanzado:** Modelos de _Survival Analysis_ para manejar datos censurados por la derecha.
2. **Inteligencia Geoespacial:** Uso de coordenadas exactas combinadas con el sistema de indexación hexagonal H3 de Uber.
3. **Cruce Temporal (Point-in-Time Join):** Entrenado con datos históricos desde 2015, emparejando el entorno socioeconómico exacto del año en que abrió cada negocio.
4. **Capa Agéntica (IA Generativa):** Un LLM que interpreta los resultados numéricos para dar consejo hiper-personalizado al usuario.

---

### 2. FUENTES DE DATOS Y CORTE TEMPORAL

Utilizaremos datos desde **Enero de 2015** en adelante. Este es nuestro "corte de pureza", ya que a partir de 2015 convergen con alta calidad todas las bases de datos necesarias:

1. **Censo de Locales y sus Actividades (Ayto. Madrid):** Histórico mensual. Aporta ID de local, coordenadas X/Y, fecha de apertura, tipo de actividad y estado (abierto/cerrado).
2. **Padrón Municipal (Ayto. Madrid):** Datos demográficos (edad, sexo) por Sección Censal.
3. **Atlas de Distribución de Renta (INE) / Panel de Indicadores:** Renta media por Sección Censal.
4. **Avisos, Incidencias y Peticiones 010 (Ayto. Madrid):** Quejas ciudadanas (limpieza, ruido, desperfectos) con coordenadas exactas. Servirá como proxy de "degradación del entorno".
5. **Infraestructura de Transporte:** Coordenadas de paradas de Metro/Tren (estáticas).

---

### 3. ARQUITECTURA GEOESPACIAL Y RESOLUCIÓN

Para no perder precisión pero mantener un rendimiento web óptimo, utilizaremos una **Arquitectura Espacial Híbrida**:

- **Unidad de Estudio (Nivel Micro - Exacto):** El modelo de ML se entrena a nivel de PUNTO EXACTO (Coordenadas del local). Las distancias críticas (ej. metros hasta la parada de metro más cercana) se calculan usando la coordenada real.
- **Unidad de Agregación y Visualización (Nivel Macro - H3):** Utilizaremos el sistema **H3 de Uber a Resolución 10** (hexágonos de ~66m de lado, equivalentes a una manzana/bloque de edificios).
- **Cambio de Soporte Espacial (Spatial Join):** Para pasar datos de polígonos irregulares (Secciones Censales de Renta/Padrón) a nuestro sistema, calcularemos el _centroide_ de cada hexágono H3 y haremos un cruce espacial (`GeoPandas.sjoin`) para heredar la demografía de la sección censal en la que caiga.
- **Máscara Comercial:** Filtraremos el mapa de Madrid para conservar ÚNICAMENTE aquellos hexágonos H3 donde haya existido al menos un local comercial en el histórico (aprox. 10.000 - 15.000 hexágonos), eliminando parques, autovías y ruido visual.

---

### 4. METODOLOGÍA DE MACHINE LEARNING: SURVIVAL ANALYSIS

NO usaremos una simple clasificación binaria. Queremos predecir "cuánto tiempo vivirá el negocio".

- **El Problema:** Tenemos negocios que cerraron (sabemos su tiempo de vida exacto) y negocios que siguen abiertos hoy (no han muerto, son "datos censurados por la derecha").
- **La Solución:** Uso de **Survival Analysis** (ej. _Random Survival Forests_, _Cox Proportional Hazards_ vía la librería `scikit-survival`).
- **Variable Objetivo (Target):** Una tupla compuesta por `(Evento_Cierre [Boolean], Tiempo_Observado_En_Meses [Int])`.
- **Output del Modelo:** Una **Función de Supervivencia**. Para un local dado, el modelo no escupe un número, sino una curva de probabilidad de seguir abierto en el mes 12, mes 36, mes 60, etc.

---

### 5. PREPARACIÓN DE DATOS TEMPORALES (Evitar Data Leakage)

Para entrenar el modelo sin sesgos del futuro, aplicaremos **Point-in-Time Joins**:

1. Si un local de entrenamiento abrió en 2017, su variable `renta_entorno` será la renta de 2017.
2. Su variable de `quejas_ruido` será el sumatorio de quejas a <100m ocurridas _exclusivamente durante su año de apertura_.
3. Su variable de `competencia_cercana` será el conteo de locales de su mismo tipo abiertos en un radio de 500m _exactamente en la fecha en la que abrió_.

---

### 6. PIPELINE DE PRODUCCIÓN (BATCH PREDICTION)

Para que la aplicación web (Streamlit) vuele y no se sature, el modelo no inferirá en tiempo real. Haremos dos procesos Batch offline y guardaremos los resultados:

1. **Batch Grid (Para el Mapa de Calor):**
   Pasaremos por el modelo los centroides de nuestros 12.000 hexágonos de la "máscara comercial". Extraeremos de la curva generada una métrica ancla (Ej: _Probabilidad de supervivencia a 3 años_) para cada tipo de negocio. Esto servirá para teñir el mapa interactivo de verde a rojo.
2. **Batch Locales Disponibles (Puntos Interactivos):**
   Aislaremos del último censo mensual los locales con estado "Cerrado/Sin Actividad". Calcularemos sus variables basándonos en la actualidad (renta 2025, quejas últimos 12 meses, metro, etc.). Generaremos la predicción de su curva completa.
   En la web, estos serán los marcadores (puntos negros). Al hacer clic en ellos, se mostrará el detalle y el gráfico de la curva.

---

### 7. CAPA AGÉNTICA (LLM)

Se integrará una llamada a la API de un LLM (OpenAI o Anthropic) en la interfaz de usuario. Al seleccionar un local y un tipo de negocio, el backend construirá un prompt oculto inyectando el JSON con el contexto:
_Prompt interno: "Un usuario evalúa abrir una Frutería en estas coordenadas. Demografía: edad media 50 años, renta media baja. Competencia: 0 fruterías a 500m. Probabilidad IA a 3 años: 85%. Escribe un consejo de 3 líneas justificando si es buena idea o advirtiendo de riesgos."_

---

### 8. ROADMAP PASO A PASO PARA EL DESARROLLO

**Fase 1: Ingesta y Limpieza de Datos (EDA)**

- [ ] 1.1 Descargar Censo de Locales (Enero 2015 a Actualidad). Identificar IDs únicos, limpiar estados (abierto/cerrado) y calcular `Fecha_Apertura`, `Fecha_Cierre` y `Tiempo_Observado`.
- [ ] 1.2 Descargar polígonos de Secciones Censales, Padrón Histórico y Renta (INE).
- [ ] 1.3 Descargar Avisos y Quejas (histórico desde 2015).
- [ ] 1.4 Descargar dataset de transporte (Metro/Cercanías).

**Fase 2: Ingeniería de Variables Espacio-Temporales (Feature Engineering)**

- [ ] 2.1 Crear el grid de hexágonos H3 (Resolución 10) y filtrar la "máscara comercial" usando el histórico de locales.
- [ ] 2.2 Script de _Point-in-Time Join_: Para cada local de entrenamiento, cruzar su año de apertura con las características temporales de la sección censal en la que cae.
- [ ] 2.3 Script de _Cálculo Espacial_: Calcular distancia a metro y densidad de quejas (radio 100m) en el año de apertura. Calcular competencia (mismo epígrafe a 500m en el año de apertura).

**Fase 3: Modelado de Survival Analysis**

- [ ] 3.1 Construir matriz de entrenamiento `X` (features espaciotemporales) e `y` (array estructurado con boolean de evento y entero de duración).
- [ ] 3.2 Entrenar modelo (ej. `RandomSurvivalForest` o `GradientBoostingSurvivalAnalysis` de `sksurv`).
- [ ] 3.3 Evaluar con métricas propias de supervivencia (Concordance Index).
- [ ] 3.4 Guardar el artefacto del modelo entrenado (`.pkl` o `.joblib`).

**Fase 4: Inferencia Batch (Pre-cálculo)**

- [ ] 4.1 Generar DataFrame de Locales Vacíos (datos de entorno actuales). Ingerirlos en el modelo y exportar JSON/SQLite con sus curvas de probabilidad para el top 10 de categorías de negocio.
- [ ] 4.2 Generar DataFrame de Centroides H3. Ingerirlos en el modelo y exportar valor puntual (prob. a 3 años) para coloreado del mapa.

**Fase 5: Desarrollo Frontend (Streamlit / PWA)**

- [ ] 5.1 Montar aplicación Streamlit.
- [ ] 5.2 Integrar mapa interactivo (usar `pydeck` o `folium`) que cargue el GeoJSON de hexágonos (capa base) y los Puntos (capa superior).
- [ ] 5.3 Crear panel lateral de filtros (Tipo de negocio a explorar).
- [ ] 5.4 Programar el Pop-up / Sidebar de detalle al hacer clic en un local: Mostrar gráfica de curva de supervivencia (usando `Plotly` o `Altair`) y variables del entorno.
- [ ] 5.5 Integrar API de LLM para generar el veredicto en texto basado en los datos del punto seleccionado.
