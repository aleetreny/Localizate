# Estudio: Google Maps Platform para Localizate

**Fecha:** 2026-03-30  
**Objetivo:** Evaluar qué podemos obtener gratis (o casi gratis) de Google Maps y cómo sumaría al proyecto

---

## Resumen Ejecutivo

Google Maps Platform ofrece datos **extremadamente valiosos** para Localizate, pero **no es gratis**. El antiguo crédito mensual de $200/mes ya no existe — fue reemplazado por un sistema de "free usage caps" por SKU (uso gratuito limitado por API). El crédito de $300 para nuevos clientes de Google Cloud es una prueba única, no renovable.

**Veredicto:** Se pueden obtener datos útiles dentro del free tier, pero con limitaciones importantes. El mayor valor está en **Nearby Search** (densidad comercial real) y **Geocoding** (validación de direcciones), pero las restricciones de TOS prohíben almacenar/cachear los datos fuera de Google Maps, lo cual limita su uso en nuestro pipeline de build estático.

---

## 1. Estructura de Precios Actual (2026)

### Modelo Pay-as-you-go

Cada SKU tiene un "free usage cap" mensual (se resetea el día 1 de cada mes). Después del free cap, se cobra por cada 1,000 eventos.

| SKU | Free cap/mes | Precio por 1K (tras free cap) | Te interesa |
|---|---|---|---|
| **Geocoding** | 10,000 | $5.00 | ★★★★★ |
| **Place Details Essentials** | 10,000 | $5.00 | ★★★★ |
| **Place Details Essentials (IDs only)** | Ilimitado | $0 | ★★★★★ |
| **Text Search Essentials (IDs only)** | Ilimitado | $0 | ★★★ |
| **Autocomplete Requests** | 10,000 | $2.83 | ★ |
| **Nearby Search Pro** | 5,000 | $32.00 | ★★★★★ |
| **Nearby Search Enterprise** | 1,000 | $35.00 | ★★★★ |
| **Nearby Search Enterprise + Atmosphere** | 1,000 | $40.00 | ★★★★★ |
| **Place Details Pro** (rating, price level) | 5,000 | $17.00 | ★★★★ |
| **Place Details Enterprise + Atmosphere** (reviews) | 1,000 | $25.00 | ★★★ |
| **Places Aggregate API** | 5,000 | $10.00 | ★★★★★ |
| Static Maps | 10,000 | $2.00 | ★ |
| Dynamic Maps | 10,000 | $7.00 | ★ |
| Routes: Compute Routes Essentials | 10,000 | $5.00 | ★★★ |
| Air Quality | 10,000 | $5.00 | ★★ |

### Crédito inicial (solo una vez)
- **$300 de prueba** para cuentas nuevas de Google Cloud (se consume con cualquier API de GCP, no solo Maps)
- Se agota o expira, lo que ocurra primero
- Después: solo free caps por SKU

### Planes de suscripción (NO gratuitos)
- **Starter:** $100/mes (50K llamadas) — Geocoding + Dynamic Maps
- **Essentials:** $275/mes (100K llamadas) — Incluye Places Details, Geocoding, Time Zone, Maps
- **Pro:** $1,200/mes (250K llamadas) — Incluye Nearby Search Pro, Text Search Pro, Place Details Pro

---

## 2. Qué Datos Puede Aportar Google Maps a Localizate

### 2.1 Nearby Search — Densidad Comercial Real (★★★★★)

**Qué obtendríamos:** Para cada oportunidad (207 locales) o punto libre, consultar negocios reales en radio de 300-500m.

```
POST /v1/places:searchNearby
{
  "includedTypes": ["restaurant"],
  "maxResultCount": 20,
  "locationRestriction": {
    "circle": {
      "center": {"latitude": 40.4168, "longitude": -3.7038},
      "radius": 500.0
    }
  }
}
```

**Campos disponibles por tier:**

| Tier | Campos | Coste |
|---|---|---|
| **Pro** (free: 5K/mes) | nombre, dirección, tipo, ubicación, estado del negocio, horarios, Google Maps URI | $32/1K |
| **Enterprise** (free: 1K/mes) | + rating, userRatingCount, priceLevel, teléfono, web, horarios actuales | $35/1K |
| **Enterprise+Atmosphere** (free: 1K/mes) | + reviews, editorial summary, delivery/dineIn/takeout, parking, outdoor seating | $40/1K |

**Valor para Localizate:**
- **Densidad competitiva real**: "Hay 23 restaurantes en 500m" vs "Hay 2 farmacias en 500m"
- **Rating medio de la zona**: Zona con ratings altos = zona comercial sana
- **Volumen de reviews**: Proxy de tráfico/popularidad real
- **Mix comercial**: Qué tipos de negocio dominan la zona

**Presupuesto con free tier:**
- 207 locales × 4 categorías comerciales = 828 requests → **Cabe en los 1,000 gratuitos de Enterprise**
- Pero solo una vez al mes (no cacheable)

### 2.2 Places Aggregate API — Insights de Zona (★★★★★)

**Qué obtendríamos:** Estadísticas agregadas de una zona sin necesidad de pedir negocio por negocio.

- Free: 5,000/mes
- $10/1K requests

**Valor:** Podríamos obtener insights estadísticos sobre densidad de negocios por categoría en áreas específicas. Ideal para nuestro caso de uso ya que resume la información sin necesitar iterar lugar por lugar.

### 2.3 Geocoding — Validación de Direcciones (★★★★★)

**Qué obtendríamos:** Validar y enriquecer las 207 direcciones de oportunidades con coordenadas precisas de Google.

- Free: 10,000/mes
- $5/1K requests

**Valor para Localizate:**
- Verificar que las coordenadas de Nominatim (que usamos ahora) son correctas
- Obtener coordenadas más precisas para locales que Nominatim resolvió a nivel de barrio
- 207 requests << 10,000 free → **100% gratis**

### 2.4 Place Details — Información Detallada (★★★★)

**Qué obtendríamos:** Detalles de negocios específicos cercanos a cada oportunidad.

| Tier | Free cap | Campos útiles |
|---|---|---|
| Essentials (IDs only) | **Ilimitado** | Solo place IDs — gratis para siempre |
| Essentials | 10,000/mes | Nombre, dirección, tipo, horarios |
| Pro | 5,000/mes | + rating, reviews count, price level, teléfono |
| Enterprise+Atmosphere | 1,000/mes | + reviews texto, editorial summary |

**Enfoque inteligente:** Usar Text Search IDs-only (ilimitado, gratis) para obtener IDs de negocios cercanos, luego Place Details Essentials (10K gratis) para datos básicos.

### 2.5 Routes API — Accesibilidad Real (★★★)

**Qué obtendríamos:** Tiempo de viaje real (no solo distancia euclidiana) desde cada oportunidad a puntos clave.

- Free: 10,000/mes
- Modos: conducción, transporte público, bicicleta, a pie

**Valor para Localizate:**
- "15 min andando a Sol" es más útil que "1,200m al metro más cercano"
- Accesibilidad en transporte público (metro + bus + cercanías combinados)
- 207 locales × 3-5 destinos clave = 600-1,000 requests → **Gratis**

### 2.6 Air Quality API (★★)

- Free: 10,000/mes
- Calidad del aire por coordenada
- Complementaría los datos IGUALA de medio ambiente

---

## 3. Restricciones Críticas de TOS

### 3.1 Prohibición de Cachear/Almacenar (BLOQUEANTE)

**Sección 3.2.3 (a) - No Scraping:**
> "Customer will not: (i) pre-fetch, index, store, reshare, or rehost Google Maps Content outside the services; (ii) bulk download Google Maps tiles, Street View images, geocodes, directions, distance matrix results, roads information, **places information**, elevation values, and time zone details; (iii) copy and save **business names, addresses, or user reviews**"

**Sección 3.2.3 (b) - No Caching:**
> "Customer will not cache Google Maps Content except as expressly permitted under the Maps Service Specific Terms."

**Sección 3.2.3 (c) - No Creating Content From Google Maps Content:**
> "Customer will not create content based on Google Maps Content. For example, Customer will not: ... (iv) **use latitude/longitude values from the Places API as an input for point-in-polygon analysis**"

**Excepción:** Los **Place IDs** sí se pueden almacenar indefinidamente.

### 3.2 Prohibición de Uso con Non-Google Maps (BLOQUEANTE)

**Sección 3.2.3 (e):**
> "Customer will not use the Google Maps Core Services with or near a non-Google Map in a Customer Application. For example, Customer will not (i) **display or use Places content on a non-Google Map**"

**Impacto directo:** Localizate usa **MapLibre GL** (no Google Maps). Esto significa que **NO podemos mostrar datos de Places API en nuestro mapa MapLibre**. Tendríamos que:
- Usar Google Maps JS API en lugar de MapLibre (cambio gigante), o
- Mostrar los datos de Google SOLO en paneles de texto/tarjetas, nunca sobre el mapa, o
- No usar Places API en absoluto

### 3.3 Prohibición de Crear Modelos ML con Datos Google

**Sección 3.2.3 (c)(vii):**
> "use Google Maps Content to improve machine learning and artificial intelligence models, including to train, test, validate or fine-tune the models"

**Impacto:** No podemos usar densidad comercial de Google como feature en nuestros modelos de supervivencia. Solo como dato de visualización en el frontend.

---

## 4. Análisis de Viabilidad para Localizate

### Escenario A: Build-time enrichment (nuestro pipeline actual)

Nuestro pipeline pre-genera JSONs estáticos en build time → los sirve al frontend.

| API | ¿Compatible con TOS? | Razón |
|---|---|---|
| Nearby Search | **NO** | Pre-fetch + store = violación TOS 3.2.3(a) |
| Place Details | **NO** | Store places information = violación TOS 3.2.3(a) |
| Geocoding | **NO** | Bulk download geocodes = violación TOS 3.2.3(a)(ii) |
| Routes | **NO** | Store distance results = violación TOS 3.2.3(a)(ii) |

**Veredicto: Nuestro pipeline estático es INCOMPATIBLE con Google Maps TOS.**

### Escenario B: Real-time client-side queries

El frontend hace las llamadas a Google Maps API en tiempo real cuando el usuario interactúa.

| API | ¿Compatible? | Requisito |
|---|---|---|
| Nearby Search | **Parcial** | Solo si se muestra en Google Map o en panel sin mapa |
| Place Details | **Parcial** | Misma restricción |
| Geocoding | **SÍ** | Para autocompletado/geocoding en vivo |
| Routes | **SÍ** | Calculo real-time de rutas |

**Pero:** Requiere API key expuesta en frontend → necesita restricciones de dominio/referrer.  
**Y:** No podemos mostrar resultados sobre nuestro mapa MapLibre (TOS 3.2.3(e)).

### Escenario C: Dato auxiliar no persistido (zona gris)

Hacer queries puntuales y mostrar el resultado de forma efímera al usuario, sin almacenar.

- El usuario selecciona un local → se disparan queries a Google
- Se muestran en un panel lateral (no en el mapa)
- No se guarda nada en base de datos ni en archivos estáticos
- Se muestra atribución de Google Maps

**Viabilidad TOS:** Más favorable pero requiere cuidado. La key está en que los datos se muestran y se descartan, no se persisten.

---

## 5. Lo que SÍ Podemos Hacer Gratis y Legal

### 5.1 Geocoding en Vivo (10K free/mes)

**Caso de uso:** Autocompletado de direcciones en la interfaz de "punto libre" de oportunidades.
- El usuario escribe una dirección → Google la resuelve → se posiciona el punto en el mapa
- Esto es uso legítimo del Geocoding API
- 10,000 requests/mes gratis = más que suficiente

**Valor:** Mejoraría la UX de la funcionalidad "punto libre" (actualmente el usuario tiene que hacer click en el mapa).

### 5.2 Place IDs como Índice (Ilimitado, gratis)

**Caso de uso:** Hacer una búsqueda inicial de Place IDs cerca de cada oportunidad y almacenarlos.
- Place IDs se pueden guardar indefinidamente (excepción explícita en TOS)
- Luego, en el frontend, hacer Place Details real-time con el ID guardado
- Essentials IDs-only = ilimitado y gratis

**Valor:** Podemos precomputar un índice de "qué Place IDs hay cerca de cada oportunidad" sin violar TOS.

### 5.3 Google Maps Embed (Ilimitado, gratis)

**Caso de uso:** Integrar un iframe de Google Maps en la ficha de detalle de cada oportunidad.
- Embed API = ilimitado, gratis, sin restricciones
- Muestra un mini-mapa de Google con la ubicación del local
- El usuario puede explorar los alrededores dentro del embed

**Valor:** Le da al usuario acceso a toda la información de Google Maps (negocios cercanos, reviews, fotos, Street View) sin que nosotros tengamos que procesar nada.

### 5.4 Links a Google Maps (Sin coste)

**Caso de uso:** Desde la ficha de cada oportunidad, link directo a Google Maps.
- `https://www.google.com/maps/search/?api=1&query=lat,lng`
- No requiere API key
- El usuario abre Google Maps y explora por su cuenta

**Valor:** Mínimo esfuerzo, máxima información. El usuario puede ver negocios cercanos, reviews, fotos, tráfico, Street View.

---

## 6. Comparativa: Google vs Alternativas Gratuitas

| Necesidad | Google Maps | Alternativa Gratuita | Recomendación |
|---|---|---|---|
| Densidad comercial | Nearby Search ($32-40/1K) | **OpenStreetMap/Overpass API** (gratis, sin TOS restrictivos) | **OSM** — sin restricciones de almacenamiento |
| Geocoding | Geocoding ($5/1K, 10K free) | **Nominatim** (ya lo usamos, gratis) | Ya lo tenemos. Google solo como validación |
| Ratings/Reviews | Place Details ($17-25/1K) | **No hay alternativa** comparable | Google es único aquí |
| Rutas/tiempo viaje | Routes ($5-15/1K) | **OSRM/Valhalla** (gratis, self-hosted) | **OSRM** para build time, Google para real-time |
| Mapas | Dynamic Maps ($7/1K) | **MapLibre GL** (ya lo usamos, gratis) | **MapLibre** — ya funciona bien |
| Datos POI | Places API | **datos.madrid.es** (ya descargado, 2,129 puntos) | **Datos propios** — sin restricciones |

### OpenStreetMap como alternativa clave

**Overpass API** permite queries tipo "¿cuántos restaurantes hay en un radio de 500m de este punto?" completamente gratis, sin API key, sin restricciones de TOS, y con datos descargables y cacheables.

```
[out:json];
(
  node["amenity"="restaurant"](around:500,40.4168,-3.7038);
  way["amenity"="restaurant"](around:500,40.4168,-3.7038);
);
out count;
```

Esto podríamos bakearlo en build time sin ningún problema legal.

---

## 7. Recomendación Final

### Lo que SÍ recomiendo hacer con Google Maps:

1. **Google Maps Embed (gratuito, ilimitado):** Añadir un mini-mapa embed de Google en la ficha de cada oportunidad. El usuario puede explorar negocios cercanos, ver Street View, reviews, fotos, todo dentro del embed. Zero coste, zero riesgo legal.

2. **Links directos a Google Maps (gratuito):** Botón "Ver en Google Maps" desde cada oportunidad.

### Lo que recomiendo hacer con alternativas gratuitas:

3. **Densidad comercial via OpenStreetMap/Overpass:** Script de build que para cada oportunidad cuente restaurantes, comercios, farmacias, bancos, etc. en radio de 300/500m. Sin restricciones de TOS, cacheable, bakeado en artefacto estático.

4. **Datos municipales ya descargados (datos.madrid.es):** Ya tenemos 2,129 puntos de equipamientos geocodificados. Pendiente de integrar al frontend.

### Lo que NO recomiendo:

5. **NO usar Places API para build-time enrichment:** Viola TOS directamente.
6. **NO usar datos de Google como features de modelo ML:** Prohibido explícitamente.
7. **NO mostrar datos de Places sobre nuestro mapa MapLibre:** Viola TOS 3.2.3(e).

### Presupuesto estimado si quisiéramos más:

| Escenario | Coste mensual |
|---|---|
| Solo Embed + Links | **$0** |
| + Geocoding real-time (autocompletado) | **$0** (dentro del free cap 10K) |
| + Nearby Search Pro para 207 locales × 4 tipos/mes | **$0** (dentro del free cap 5K) , pero requiere real-time display |
| + Place Details Pro para resultados | **~$0-17** (dentro del free cap 5K si moderado) |
| Plan Essentials si escalamos | **$275/mes** |

---

## 8. Plan de Acción Propuesto

### Fase 0 — Sin coste (inmediato)
1. Integrar los 2,129 equipamientos de datos.madrid.es ya descargados como capa en el mapa
2. Añadir botón "Ver en Google Maps" en cada ficha de oportunidad
3. Añadir Google Maps Embed iframe en el detalle de cada oportunidad

### Fase 1 — Sin coste extra (con Overpass API)
4. Script de enriquecimiento via OSM Overpass: densidad de negocios por tipo en 300/500m
5. Bakear en artefacto estático → nueva feature en ficha de oportunidad
6. Esto SÍ se puede usar como feature para modelos (sin restricciones de TOS)

### Fase 2 — Evaluación (opcional, requiere API key)
7. Si la Fase 0-1 no satisface, evaluar Geocoding real-time para autocompletado de "punto libre"
8. Evaluar Places Aggregate API para insights de zona en real-time

---

## Apéndice: Resumen de TOS Relevantes

| Restricción | Sección TOS | Impacto |
|---|---|---|
| No pre-fetch/store places data | 3.2.3(a) | No podemos bakear Nearby Search en JSONs estáticos |
| No bulk download geocodes | 3.2.3(a)(ii) | No podemos geocodificar 207 locales en batch y guardar |
| No cachear resultados | 3.2.3(b) | Datos solo en real-time, efímeros |
| No lat/lon para point-in-polygon | 3.2.3(c)(iv) | No podemos cruzar coordenadas de Google con census sections |
| No Places content en non-Google maps | 3.2.3(e) | No podemos pintar datos de Google en MapLibre |
| No ML training con Google data | 3.2.3(c)(vii) | No podemos usar como features de modelo |
| Place IDs sí se pueden guardar | Policies (excepción) | Podemos indexar IDs para consultas futuras |
| Embed es gratuito e ilimitado | Pricing | Mini-mapa embed sin coste |
