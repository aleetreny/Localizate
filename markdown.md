# Despliegue gratuito recomendado para Localizate

## Resumen ejecutivo

La ruta que dejo preparada es esta:

1. `front/` se publica como **sitio estatico** en **Cloudflare Pages**.
2. `front/public/data/` se publica por separado en **Cloudflare R2** bajo un dominio publico o `r2.dev`.
3. El buscador de direccion de oportunidades sale de Next y se despliega como **Cloudflare Worker** independiente.
4. El workflow semanal ya no tiene que redeployar la web: actualiza `listings.json`, hace commit y, si R2 esta configurado, sube automaticamente `data/opportunities/` al bucket.

Con esto evitamos subir cientos de MB al despliegue del frontend, mantenemos la funcionalidad completa y dejamos la web servida como producto serio:

- HTML/JS/CSS ligeros en CDN.
- Datos grandes fuera del bundle web.
- Actualizacion semanal automatizable.
- Geocoder separado del build del frontend.

---

## Que problema habia de verdad

El bloqueo no era "Next.js" ni "el hosting" por si solos. El problema real era una mezcla de tres cosas:

1. **Los artefactos pesados estaban empaquetados como parte del frontend.**
   - `front/public/data/` pesa en local unos `362 MB`.
   - Solo `front/public/data/map/historical/hex-composition.json` pesa unos `235.97 MB`.
   - `rankings.json` pesa unos `45.18 MB`.
   - `small.json` pesa unos `32.65 MB`.

2. **La app ya era casi estatica, pero tenia un runtime metido dentro de Next.**
   - El endpoint `/api/geocode/opportunity-address` impedia una exportacion estatica limpia.

3. **Habia peso invisible en la experiencia.**
   - La pestaña de oportunidades estaba serializando demasiado contexto inicial.
   - La geometria de secciones se descargaba dos veces.
   - `hex-composition.json` se cargaba entero aunque la UI solo necesita un año cada vez.

Conclusión:

- El problema principal no era "necesitas Vercel Pro".
- El problema era **como se servian y desplegaban los datos**.

---

## Alternativas evaluadas

### 1. Vercel Hobby

La descarto como solucion por defecto.

Motivos:

- Vercel documenta un limite de **`100 MB`** para `Static File uploads` en Hobby.
- Aunque movieramos parte de los datos fuera, seguiriamos acoplados a un stack mas pensado para fullstack que para este caso, donde el frontend puede ser estatico y el peso real esta en los artefactos.
- No aporta una ventaja clara frente a Cloudflare en el escenario actual.

### 2. GitHub Pages + apaños auxiliares

Es viable solo a medias, pero no la he elegido.

Motivos:

- Para una web con datos grandes, cache, CORS y una pieza auxiliar tipo geocoder, GitHub Pages se queda mas rigido.
- Obliga a montar mas soluciones paralelas para algo que Cloudflare ya resuelve mejor dentro del mismo ecosistema.
- Es mas "barato" en teoria que en practica para este producto concreto.

### 3. Netlify

No la tomo como opcion preferente.

Motivos:

- Ya te ha dado problemas.
- No hay una ventaja tecnica clara aqui que compense forzarte a volver.

### 4. Cloudflare Pages + R2 + Worker

Es la opcion elegida.

Motivos:

- Pages sirve el frontend estatico gratis y muy bien desde CDN.
- R2 encaja justo para sacar los datos pesados del despliegue web.
- Worker resuelve el geocoder sin obligar a mantener un backend completo.
- Todo queda desacoplado:
  - web
  - datos
  - runtime auxiliar

---

## Arquitectura final elegida

### Produccion

- `www.tu-dominio.com` o `tu-proyecto.pages.dev`
  - frontend estatico exportado desde Next

- `data.tu-dominio.com` o `https://<bucket>.r2.dev`
  - JSON y GeoJSON servidos desde R2

- `api.tu-dominio.com` o `https://localizate-opportunity-geocode.<subdominio>.workers.dev`
  - geocoder del buscador de direcciones

### Flujo de datos

1. La web carga HTML/JS/CSS desde Pages.
2. Cuando necesita datos, los pide a R2.
3. Cuando el usuario busca una direccion, la web llama al Worker.
4. El workflow semanal actualiza oportunidades y, si R2 esta configurado, sincroniza automaticamente `data/opportunities/`.

---

## Cambios que ya he dejado hechos en el repo

### Frontend

- Añadido `front/lib/runtime-config.ts`
  - resuelve URLs externas de datos
  - resuelve URL externa del geocoder

- Exportacion estatica preparada:
  - `front/next.config.mjs`
  - `front/scripts/build-static.mjs`
  - `front/package.json` con `npm run build:static`

- La build estatica ya no publica `front/public/data` dentro de `front/out` cuando existe `NEXT_PUBLIC_DATA_BASE_URL`.

- `front/app/oportunidades/page.tsx`
  - deja de embutir el indice completo de secciones en el payload inicial

- `front/components/opportunity-shell.tsx`
  - revalida oportunidades desde el CDN externo cuando aplica
  - usa endpoint de geocoder configurable
  - comparte la geometria con el mapa en vez de descargarla dos veces

- `front/components/opportunity-map.tsx`
  - ya no re-descarga la geometria

- `front/components/map-shell.tsx`
  - usa URL de datos resoluble
  - carga la composicion historica del hexagono por año

### Datos

- `back/scripts/build_frontend_map_artifacts.py`
  - ahora genera `hex-composition.manifest.json`
  - ahora genera particiones por año en:
    - `front/public/data/map/historical/hex-composition/2015.json`
    - ...
    - `front/public/data/map/historical/hex-composition/2026.json`

- `back/scripts/materialize_hex_composition_parts.py`
  - genera esas particiones a partir del monolito actual sin rehacer todo el pipeline
  - el workflow de publicacion a R2 lo ejecuta antes del sync
  - no hace falta versionar esas particiones en Git

### Runtime auxiliar

- El endpoint de geocoder ya no vive dentro de Next.
- Se ha movido a:
  - `workers/opportunity-geocode/src/index.ts`
  - `workers/opportunity-geocode/wrangler.toml`

### Automatizacion

- Nuevo workflow para desplegar la web estatica:
  - `.github/workflows/deploy-static-web-cloudflare-pages.yml`

- Nuevo workflow para publicar datos en R2:
  - `.github/workflows/publish-public-data-to-r2.yml`

- Nuevo workflow para desplegar el Worker:
  - `.github/workflows/deploy-opportunity-geocode-worker.yml`

- El workflow semanal ya existente:
  - `.github/workflows/refresh-opportunities-weekly.yml`
  - ahora, si R2 esta configurado, publica automaticamente `data/opportunities/`

---

## Lo que tienes que hacer tu una sola vez

## 1. Crear el proyecto de Pages

En Cloudflare:

1. Ve a **Workers & Pages**.
2. Crea un proyecto de **Pages**.
3. No hace falta conectar el repo por UI si vas a usar los workflows de GitHub que ya dejo montados.
4. Apunta el nombre exacto del proyecto.

Valor que luego pondras en GitHub Variables:

- `CLOUDFLARE_PAGES_PROJECT_NAME`

---

## 2. Crear el bucket R2 para los datos

En Cloudflare:

1. Ve a **R2**.
2. Crea un bucket, por ejemplo:
   - `localizate-public-data`
3. Activa **public bucket**.
4. Si tienes dominio, lo recomendable es asociar:
   - `data.tu-dominio.com`
5. Si no tienes dominio, puedes usar el subdominio `r2.dev` que te da Cloudflare.

### CORS del bucket

Configura CORS para permitir lectura desde la web.

Ejemplo razonable:

```json
[
  {
    "AllowedOrigins": [
      "https://tu-proyecto.pages.dev",
      "https://www.tu-dominio.com",
      "http://localhost:3000"
    ],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
    "MaxAgeSeconds": 3600
  }
]
```

### Access keys S3 para R2

Necesitas crear unas credenciales de acceso S3 para el workflow de sync.

Apunta:

- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

---

## 3. Desplegar el Worker de geocoding

El worker ya esta preparado en:

- `workers/opportunity-geocode/`

En Cloudflare:

1. Crea o reutiliza un API token que permita desplegar Workers y Pages.
2. Puedes dejar el nombre por defecto:
   - `localizate-opportunity-geocode`
3. Tras el primer deploy tendras una URL tipo:
   - `https://localizate-opportunity-geocode.<subdominio>.workers.dev`

Si tienes dominio propio, lo ideal es mapearlo luego a:

- `api.tu-dominio.com`

---

## 4. Crear los secrets y variables en GitHub

### GitHub Secrets

Crea estos secrets en el repositorio:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

### GitHub Variables

Crea estas variables:

- `CLOUDFLARE_PAGES_PROJECT_NAME`
- `R2_BUCKET_NAME`
- `NEXT_PUBLIC_DATA_BASE_URL`
- `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT`

### Valores esperados

Ejemplo con dominios Cloudflare por defecto:

- `CLOUDFLARE_PAGES_PROJECT_NAME = localizate`
- `R2_BUCKET_NAME = localizate-public-data`
- `NEXT_PUBLIC_DATA_BASE_URL = https://<tu-bucket-publico>.r2.dev`
- `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT = https://localizate-opportunity-geocode.<subdominio>.workers.dev`

Ejemplo con dominio propio:

- `NEXT_PUBLIC_DATA_BASE_URL = https://data.tu-dominio.com`
- `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT = https://api.tu-dominio.com`

---

## Orden exacto del primer despliegue

Hazlo en este orden:

1. **Deploy del Worker**
   - lanza manualmente `Deploy Opportunity Geocode Worker`

2. **Publicacion inicial de datos en R2**
   - lanza manualmente `Publish Public Data to R2`

3. **Deploy de la web estatica**
   - lanza manualmente `Deploy Static Web to Cloudflare Pages`

4. **Prueba en navegador**
   - abre la home
   - abre `oportunidades`
   - comprueba que:
     - carga el mapa
     - carga oportunidades
     - el buscador de direccion responde
     - el historico de composicion del hexagono funciona

5. **Prueba del flujo semanal**
   - ejecuta manualmente `Refresh Opportunity Listings`
   - comprueba que:
     - si hay cambio, se actualiza `listings.json`
     - hace commit
     - si R2 esta configurado, sincroniza `data/opportunities/`

---

## Que automatizacion queda funcionando

### Web estatica

- Cuando cambie codigo del frontend, el workflow de Pages puede volver a desplegar la web sin subir los datos pesados.

### Datos

- Cuando cambie `front/public/data/**`, el workflow de R2 puede volver a publicar el arbol completo de datos.
- Antes del sync, ese workflow materializa automaticamente las 12 particiones anuales de `hex-composition`.

### Oportunidades semanales

- El workflow semanal:
  - scrapea
  - reconstruye `listings.json`
  - valida
  - hace commit si hay cambios
  - sincroniza `data/opportunities/` a R2 si las credenciales existen

Esto es justo lo que querias para no tocarlo a mano cada semana.

---

## Verificaciones que ya he pasado

- `python -m py_compile` en:
  - `back/scripts/build_frontend_map_artifacts.py`
  - `back/scripts/sync_public_data_to_r2.py`

- `npm run typecheck` en `front/`

- `npm run build:static` en `front/` con:
  - `NEXT_PUBLIC_DATA_BASE_URL`
  - `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT`

### Resultado importante

La exportacion estatica sale bien y el `out/` final queda alrededor de `14 MB`, porque ya no arrastra `public/data` dentro del despliegue web.

---

## Riesgos y limitaciones que siguen existiendo

### 1. `rankings.json` sigue monolitico

No lo he troceado porque:

- se carga bajo demanda
- comprimido pesa mucho menos por red
- no era el principal cuello de botella frente a `hex-composition.json`

Si en una segunda iteracion quieres exprimir mas rendimiento, el siguiente paso natural es partir `rankings.json` por ambito o por año.

### 2. La home sigue entregando bastante contenido inicial

La pagina principal sigue enviando bastantes datos iniciales del mapa porque priorice mantener el comportamiento actual sin vaciar la UX.

No rompe el despliegue gratuito, pero si algun dia quieres apretar mas la carga inicial, la siguiente optimizacion seria diferir parte de `shared.json`.

### 3. R2 requiere configuracion correcta de CORS

Si CORS no esta bien configurado en el bucket, la web cargara pero los fetch cross-origin a datos fallaran.

### 4. El geocoder depende de Nominatim

La arquitectura queda desacoplada y mas limpia, pero la fiabilidad del endpoint sigue dependiendo del servicio externo.

Para un tribunal y trafico moderado me parece razonable.

### 5. El workflow semanal publica automaticamente oportunidades, no todo el historico

Eso esta bien y es deliberado.

- Para tu ventana de 5 meses, no necesitas rebuild profundo semanal.
- Si algun dia regeneras artefactos del mapa historico, entonces si deberias lanzar manualmente `Publish Public Data to R2`.

---

## Recomendacion operativa para los 5 meses del tribunal

Haz esto y no mas:

1. Deja la web publica con Pages + R2 + Worker.
2. Deja el semanal activo.
3. Durante las primeras 2 semanas, lanza tambien el workflow semanal manualmente y revisa logs.
4. Si no hay incidencias, deja solo el semanal.
5. No rehagas el pipeline historico profundo salvo que cambies el modelo, la taxonomia o los artefactos del mapa.

Para el uso que describes, esto es suficiente y sensato.

---

## Si quieres el minimo absoluto para salir hoy

Sin dominio propio:

- web en `pages.dev`
- datos en `r2.dev`
- geocoder en `workers.dev`

Con eso ya puedes salir gratis.

La version mas profesional es la misma arquitectura, pero con:

- `www.tu-dominio.com`
- `data.tu-dominio.com`
- `api.tu-dominio.com`
