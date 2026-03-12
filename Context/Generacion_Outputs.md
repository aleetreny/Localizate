# CONTEXTO TÉCNICO FASE 4: INFERENCIA BATCH Y GENERACIÓN DE BASE DE DATOS FINAL

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

### 1. OBJETIVO DE ESTA FASE

Ejecutar el modelo entrenado sobre el escenario actual (2026) para generar todas las predicciones posibles.
Crearemos dos conjuntos de datos precalculados que alimentarán el Frontend, garantizando tiempos de carga de milisegundos.

---

### 2. PROCESO BATCH 1: EL MAPA DE CALOR (GRID H3)

Este proceso genera la capa visual de fondo ("El Mapa de Colores").

- **Input:** La lista de ~12.000 hexágonos H3 (Resolución 10) de la "Máscara Comercial" creada en la Fase 2.
- **Construcción de Features Sintéticas:**
  - Para cada hexágono, extraemos su **Centroide**.
  - Asignamos variables de entorno ACTUALES (Renta 2025, Quejas último año, Distancia Metro).
  - _Simulación de Negocio:_ Como el hexágono no tiene un "tipo de negocio" per se, generaremos una predicción para una categoría genérica o la más común (ej. "Comercio Minorista") para representar la "salud comercial" de la zona. O mejor: Generar 3 capas (Hostelería, Comercio, Servicios) para que el usuario filtre.
- **Predicción:** Ejecutar `predict_survival_function` para cada hexágono.
- **Extracción de Métrica Ancla:** De la curva resultante, extraer un solo valor: **Probabilidad de Supervivencia a 3 años (t=36 meses)**.
- **Output:** Un archivo ligero (JSON o Parquet) con: `h3_index`, `prob_survival_3y_hosteleria`, `prob_survival_3y_comercio`, etc.

---

### 3. PROCESO BATCH 2: LOS PUNTOS INTERACTIVOS (LOCALES VACÍOS)

Este proceso genera la información detallada para los locales reales disponibles.

- **Input:** Filtrar el Censo de Locales del último mes disponible (ej. Feb-2026). Quedarse SOLO con registros donde `desc_situacion_local` sea "CERRADO", "BAJA" o "SIN ACTIVIDAD". (Estimamos ~6.000 - 8.000 locales).
- **Construcción de Features Reales:**
  - Usar las coordenadas exactas del local.
  - Asignar variables de entorno ACTUALES.
  - _Simulación de Escenarios:_ Para CADA local vacío, debemos predecir qué pasaría si se abriera cada uno de los **Top 10 Tipos de Negocio** (Bar, Frutería, Ropa, Peluquería, etc.). Esto implica replicar cada fila 10 veces cambiando el One-Hot Encoding de la categoría.
- **Predicción:** Ejecutar el modelo para obtener las 10 curvas de supervivencia por local.
- **Output Estructurado:**
  - Guardar en una base de datos ligera (**SQLite** es ideal aquí, o un archivo **DuckDB**) para poder hacer consultas SQL rápidas desde la web.
  - Tabla: `locales_predicciones`. Columnas: `id_local`, `lat`, `lon`, `categoria_simulada`, `prob_1y`, `prob_3y`, `prob_5y`, `renta_zona`, `dist_metro`.

---

### 4. VALIDACIÓN DE COHERENCIA

Antes de cerrar esta fase, el agente debe incluir un script de _Sanity Check_:

- Verificar que no hay probabilidades > 1 o < 0.
- Verificar que la curva es descendente (no puedes tener más probabilidad de vivir 5 años que 1 año).
- Comprobar visualmente (haciendo un mapa rápido en Python) que las zonas ricas/céntricas tienen colores distintos a zonas con alta degradación (el modelo discrimina correctamente).

### 5. OUTPUT ESPERADO DE ESTA FASE

Al finalizar, el backend del proyecto estará "congelado" en dos archivos estáticos listos para subir a la nube:

1.  `madrid_heatmap_h3.json` (Para pintar el mapa con `pydeck`).
2.  `madrid_locales_db.sqlite` (Para consultar los detalles al hacer clic).
