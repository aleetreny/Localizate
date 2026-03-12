# CONTEXTO TÉCNICO FASE 5: DESARROLLO FRONTEND (STREAMLIT) Y CAPA AGÉNTICA

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

### 1. OBJETIVO DE ESTA FASE

Desarrollar la aplicación web final (`app.py`) utilizando **Streamlit**. La aplicación debe cargar los datos precalculados (Fase 4), visualizar el mapa híbrido (Hexágonos + Puntos) y conectar con una API de LLM para ofrecer consultoría en lenguaje natural.

**Prioridad:** UX/UI limpia, velocidad de carga (< 2s) y efecto "Wow" visual.

---

### 2. STACK TECNOLÓGICO FRONTEND

- **Framework:** `streamlit` (Versión más reciente).
- **Mapas:** `pydeck` (PyDeck es superior a Folium para renderizar mallas H3 y grandes volúmenes de puntos con aceleración GPU).
- **Gráficos:** `plotly.graph_objects` (Para la curva de supervivencia interactiva).
- **Base de Datos:** `sqlite3` (Para consultas rápidas de locales) y `pandas` (Para cargar el grid).
- **LLM:** `openai` o `anthropic` (Cliente API).

---

### 3. ARQUITECTURA DE LA INTERFAZ (UI)

#### A. Barra Lateral (Sidebar) - Filtros de Usuario

El usuario define su perfil emprendedor aquí:

1.  **"¿Qué quieres montar?":** Selectbox con las 10 macro-categorías simuladas (Bar, Frutería, Moda...).
2.  **"Tu perfil de riesgo":** Slider (Conservador vs Arriesgado) - _Esto ajustará el umbral de colores del mapa._

#### B. Panel Principal - El Mapa Híbrido (PyDeck)

Debe renderizar dos capas superpuestas (`pdk.Layer`):

1.  **Capa Base (H3HexagonLayer):** Lee del archivo `madrid_heatmap_h3.json`.
    - _Color:_ Escala de semáforo (Rojo a Verde) basada en la columna `prob_survival_3y` de la categoría seleccionada.
    - _Opacidad:_ 0.6 (Para dejar ver el callejero de fondo).
2.  **Capa Superior (ScatterplotLayer):** Lee de la tabla de locales vacíos.
    - _Visualización:_ Puntos negros pequeños (radio 5-10m).
    - _Interacción:_ Al hacer **hover** (pasar el ratón), muestra dirección básica. Al hacer **click**, captura el `id_local` y dispara el análisis detallado.

#### C. Panel Inferior/Modal - "El Informe del Local"

Este panel solo aparece cuando el usuario selecciona un punto negro en el mapa. Se divide en 3 columnas:

1.  **Datos Duros:** KPIs del entorno (Renta, Distancia Metro, Quejas, Competencia).
2.  **La Curva de Vida:** Gráfico de línea Plotly mostrando la probabilidad de supervivencia (Eje Y: 0-100%, Eje X: 0-10 Años).
3.  **El Consultor IA:** Bloque de texto generado en tiempo real.

---

### 4. INTEGRACIÓN DE LA CAPA AGÉNTICA (LLM)

Cuando el usuario selecciona un local, el backend debe construir un JSON de contexto y enviarlo al LLM.

- **System Prompt:** "Eres un consultor experto en urbanismo y negocios comerciales en Madrid. Tu tono es profesional pero cercano. Analiza los datos objetivos y da un veredicto sincero."
- **User Prompt (Template Dinámico):**

  ```text
  Analiza la viabilidad de abrir un/a {CATEGORIA} en la ubicación {CALLE}.
  Datos del modelo predictivo (IA):
  - Probabilidad de sobrevivir 3 años: {PROB_3Y}%
  - Tendencia: {DESCRIBE_CURVA}

  Contexto del Entorno:
  - Nivel Socioeconómico: {RENTA_ZONA}€ (Comparado con la media de Madrid: {COMPARATIVA}).
  - Entorno: {QUEJAS_TXT} (Basado en avisos al 010).
  - Conectividad: Metro a {DIST_METRO} metros.
  - Competencia: {NUM_COMPETENCIA} locales similares cerca.

  Genera:
  1. Un titular corto (Veredicto).
  2. Tres puntos clave (Pros/Contras).
  3. Una recomendación final.
  ```

- **Gestión de Costes:** Usar un modelo eficiente (ej. `gpt-4o-mini` o `claude-3-haiku`) y cachear la respuesta si el usuario vuelve a pinchar el mismo local.

---

### 5. OPTIMIZACIÓN DE RENDIMIENTO (CACHING)

El agente debe implementar `@st.cache_data` rigurosamente:

- Cargar el archivo JSON del Grid H3 **una sola vez** al inicio.
- Conectar a la SQLite DB solo bajo demanda (query puntual por ID).
- No recalcular predicciones en vivo (leerlas de la DB precalculada en Fase 4).

### 6. OUTPUT ESPERADO DE ESTA FASE

- Archivo `app.py` completo y funcional.
- Archivo `requirements.txt` para despliegue.
- Instrucciones para configurar la `.streamlit/secrets.toml` (para la API Key del LLM).
