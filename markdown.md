# Integración real Cloudflare + GitHub para Localizate

Fecha de auditoría real: 2026-04-16

## Resumen ejecutivo

La base técnica del repo estaba bien orientada, pero la integración real no estaba cerrada:

- Los workflows de GitHub existían y estaban activos.
- El repositorio no tenía variables ni secrets configurados para Cloudflare o R2.
- El workflow semanal estaba inválido para GitHub porque había quedado `schedule:` sin cron activo.
- El deploy del worker usaba el `wrangler` por defecto del action y caía en `3.90.0`.
- La web estática ya podía compilar con datos externos, pero seguía embebiendo parte de los artefactos pesados en el HTML inicial cuando se hacía export estático.

He dejado corregido todo lo que sí podía cerrar desde el repo local y GitHub sin credenciales de Cloudflare:

- workflows endurecidos
- cron semanal reparado
- pin de `wrangler` a `4.83.0`
- validaciones explícitas de variables y secrets
- export estático realmente desacoplado del JSON pesado cuando existe `NEXT_PUBLIC_DATA_BASE_URL`
- documentación actualizada con estado real y no teórico

No he podido crear ni verificar recursos reales en Cloudflare porque en este entorno no había ningún acceso autenticado a Cloudflare disponible.

## Qué he auditado de verdad

### Repo local

He revisado y cruzado estas piezas:

- `.github/workflows/deploy-static-web-cloudflare-pages.yml`
- `.github/workflows/publish-public-data-to-r2.yml`
- `.github/workflows/deploy-opportunity-geocode-worker.yml`
- `.github/workflows/refresh-opportunities-weekly.yml`
- `workers/opportunity-geocode/wrangler.toml`
- `workers/opportunity-geocode/src/index.ts`
- `front/lib/runtime-config.ts`
- `front/lib/data.ts`
- `front/lib/public-data.ts`
- `front/scripts/build-static.mjs`
- `front/app/page.tsx`
- `front/app/oportunidades/page.tsx`
- `back/scripts/sync_public_data_to_r2.py`
- `back/scripts/materialize_hex_composition_parts.py`
- `back/scripts/build_frontend_opportunity_listings.py`

### GitHub real

Repositorio remoto detectado:

- `https://github.com/aleetreny/Localizate.git`

Autenticación verificada con `gh auth status`:

- cuenta activa: `aleetreny`
- scopes presentes: `gist`, `read:org`, `repo`, `workflow`

Workflows visibles en GitHub:

- `Deploy Opportunity Geocode Worker`
- `Deploy Static Web to Cloudflare Pages`
- `Publish Public Data to R2`
- `refresh-opportunities-weekly.yml` como workflow activo, aunque venía roto

Últimos runs reales observados en GitHub el 2026-04-16:

- `24525563709` `Deploy Static Web to Cloudflare Pages`: fallo por variables ausentes
- `24525563696` `Publish Public Data to R2`: fallo por variable y secrets ausentes
- `24525563737` `Deploy Opportunity Geocode Worker`: fallo por `CLOUDFLARE_API_TOKEN` ausente
- `24525560376` `refresh-opportunities-weekly.yml`: fallo por workflow inválido

### Cloudflare real

No he podido inspeccionar recursos reales en Cloudflare porque este entorno no tenía acceso autenticado disponible:

- no había `wrangler` global instalado
- no había variables de entorno `CLOUDFLARE_*` ni `R2_*`
- no existía `~/.wrangler`

Lo que sí he podido validar localmente:

- `npx wrangler@4.83.0 deploy --dry-run` compila el worker correctamente
- bundle estimado del worker: `20.20 KiB` sin bindings

Conclusión honesta:

- no he podido verificar si ya existe proyecto de Pages
- no he podido verificar si ya existe bucket R2
- no he podido verificar si el worker ya existe desplegado
- no he podido inspeccionar CORS real del bucket
- no he podido crear recursos en Cloudflare ni desplegar de verdad por falta de credenciales

## Hallazgos reales antes de tocar nada

### 1. GitHub no tenía configuración operativa para Cloudflare

`gh variable list --repo aleetreny/Localizate` devolvía vacío.

`gh secret list --repo aleetreny/Localizate` devolvía vacío.

Eso explica los fallos inmediatos de los workflows.

### 2. El workflow semanal estaba roto

Estado observado en el repo:

```yaml
on:
  workflow_dispatch:
  schedule:
#    - cron: "0 5 * * 1"
```

Ese `schedule:` vacío hace que GitHub rechace el workflow.

### 3. El worker dependía del `wrangler` por defecto del action

En el run `24525563737`, `cloudflare/wrangler-action@v3` instaló `wrangler 3.90.0`.

No es un fallo de código del worker, pero sí un punto débil evitable del pipeline.

### 4. La exportación estática seguía arrastrando demasiados datos en el HTML

Antes del ajuste del frontend:

- `front/public/data/` pesaba `627,735,424` bytes
- `front/public/data/map/historical/hex-composition.json` pesaba `235.97 MB`
- `front/public/data/map/historical/rankings.json` pesaba `45.18 MB`
- `front/public/data/map/hex/small.json` pesaba `32.65 MB`
- el export estático con URLs externas ya eliminaba `front/out/data`, pero el HTML seguía embebiendo artefactos iniciales

Medición real del export estático antes del ajuste de páginas:

- `front/out/` total: `14,704,994` bytes
- `index.html`: alrededor de `3.9 MB`
- `oportunidades.html`: alrededor de `2.0 MB`

Eso significa que la separación `Pages + R2` existía solo a medias.

## Cambios que he aplicado

### Frontend

He cambiado estas dos páginas:

- `front/app/page.tsx`
- `front/app/oportunidades/page.tsx`

Cambio aplicado:

- cuando existe `NEXT_PUBLIC_DATA_BASE_URL`, dejan de cargar artefactos locales en build-time
- la exportación estática ya no embebe los JSON grandes en el HTML inicial
- el cliente arranca ligero y hace fetch a los artefactos públicos desde la base externa configurada

### Workflows

#### `.github/workflows/deploy-static-web-cloudflare-pages.yml`

He añadido:

- validación explícita de:
  - `NEXT_PUBLIC_DATA_BASE_URL`
  - `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT`
  - `CLOUDFLARE_PAGES_PROJECT_NAME`
  - `CLOUDFLARE_API_TOKEN`
  - `CLOUDFLARE_ACCOUNT_ID`
- inclusión de `front/tsconfig.json` en los paths de despliegue
- pin de `wranglerVersion: "4.83.0"`

#### `.github/workflows/deploy-opportunity-geocode-worker.yml`

He añadido:

- validación explícita de:
  - `CLOUDFLARE_API_TOKEN`
  - `CLOUDFLARE_ACCOUNT_ID`
- pin de `wranglerVersion: "4.83.0"`

#### `.github/workflows/publish-public-data-to-r2.yml`

He añadido:

- validación explícita de:
  - `R2_BUCKET_NAME`
  - `CLOUDFLARE_ACCOUNT_ID`
  - `R2_ACCESS_KEY_ID`
  - `R2_SECRET_ACCESS_KEY`
- trigger cuando cambie `back/scripts/materialize_hex_composition_parts.py`
- exclusión de `front/public/data/opportunities/listings.json` del trigger automático por `push`

Motivo de esa exclusión:

- el workflow semanal ya sincroniza `data/opportunities/` directamente a R2
- sin esa exclusión, una actualización semanal de `listings.json` dispararía además un sync completo del árbol `front/public/data/**`, duplicando trabajo y tráfico

#### `.github/workflows/refresh-opportunities-weekly.yml`

He reparado el cron:

- antes: inválido
- ahora: `0 5 * * 1`

Interpretación real:

- cada lunes a las `05:00 UTC`

## Validaciones que sí he ejecutado

### Frontend

Comandos ejecutados:

```powershell
cd front
npm run typecheck
```

Resultado:

- OK

Comandos ejecutados:

```powershell
cd front
$env:NEXT_PUBLIC_DATA_BASE_URL='https://data.example.com'
$env:NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT='https://localizate-opportunity-geocode.example.workers.dev'
npm run build:static
```

Resultado:

- OK

### Tamaño del export estático después del ajuste

Medición real después del cambio en `front/app/page.tsx` y `front/app/oportunidades/page.tsx`:

- `front/out/` total: `3,223,502` bytes
- `front/out/data`: no existe
- `front/out/index.html`: `10.06 KB`
- `front/out/oportunidades.html`: `8.51 KB`

Esto sí deja el frontend realmente ligero para Pages.

### Worker

Comando ejecutado:

```powershell
cd workers/opportunity-geocode
npx wrangler@4.83.0 deploy --dry-run
```

Resultado:

- OK
- bundle compilado localmente
- upload estimado: `20.20 KiB`

### Python y builders relevantes

Comandos ejecutados:

```powershell
.\.venv\Scripts\python.exe -m py_compile `
  back\scripts\sync_public_data_to_r2.py `
  back\scripts\materialize_hex_composition_parts.py `
  back\scripts\build_frontend_opportunity_listings.py `
  back\scripts\build_manual_available_locales.py
```

Resultado:

- OK

Tests ejecutados:

```powershell
cd back
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe -m unittest tests.test_build_frontend_opportunity_listings
..\.venv\Scripts\python.exe -m unittest tests.test_build_frontend_opportunity_artifacts
..\.venv\Scripts\python.exe -m unittest tests.test_build_frontend_map_artifacts
```

Resultado real:

- `test_build_frontend_opportunity_listings`: OK
- `test_build_frontend_opportunity_artifacts`: OK
- `test_build_frontend_map_artifacts`: OK

Nota:

- el primer intento desde la raíz falló por contexto de import del test, no por un bug del código; al relanzarlo desde `back/` con `PYTHONPATH=src` pasó correctamente

### Materialización de históricos

Comando ejecutado:

```powershell
.\.venv\Scripts\python.exe back\scripts\materialize_hex_composition_parts.py
```

Resultado:

- OK
- manifest válido
- `12` particiones anuales detectadas en `front/public/data/map/historical/hex-composition/`

Primeras filas del manifest verificadas:

- `2015 -> /data/map/historical/hex-composition/2015.json`
- `2016 -> /data/map/historical/hex-composition/2016.json`
- `2017 -> /data/map/historical/hex-composition/2017.json`

## Variables y secrets que faltan ahora mismo en GitHub

### Variables de repositorio ausentes

- `CLOUDFLARE_PAGES_PROJECT_NAME`
- `NEXT_PUBLIC_DATA_BASE_URL`
- `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT`
- `R2_BUCKET_NAME`

### Secrets de repositorio ausentes

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

## Estado final esperado de cada workflow

### `Deploy Opportunity Geocode Worker`

Queda listo para usar cuando existan:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Usará:

- `wrangler 4.83.0`
- worker configurado en `workers/opportunity-geocode/wrangler.toml`
- nombre actual del worker: `localizate-opportunity-geocode`

### `Publish Public Data to R2`

Queda listo para usar cuando existan:

- `R2_BUCKET_NAME`
- `CLOUDFLARE_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

Publicará:

- `front/public/data/**`
- bajo prefijo remoto `data/`

Antes del sync:

- materializa las `12` particiones anuales de `hex-composition`

### `Deploy Static Web to Cloudflare Pages`

Queda listo para usar cuando existan:

- `CLOUDFLARE_PAGES_PROJECT_NAME`
- `NEXT_PUBLIC_DATA_BASE_URL`
- `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Publicará:

- `front/out`

Con el ajuste aplicado:

- sin `front/out/data`
- sin embebidos pesados en HTML inicial

### `Refresh Opportunity Listings`

Queda listo para usar con:

- cron semanal real: lunes `05:00 UTC`
- ejecución manual por `workflow_dispatch`

Si además existen credenciales R2:

- reconstruye `listings.json`
- hace commit si hubo cambios
- sincroniza `data/opportunities/` a R2

## CORS de R2

No he podido inspeccionarlo ni confirmarlo porque no he tenido acceso al bucket real.

Cuando exista el bucket público, la configuración mínima recomendada es:

```json
[
  {
    "AllowedOrigins": [
      "https://<tu-proyecto>.pages.dev",
      "https://www.<tu-dominio>",
      "http://localhost:3000"
    ],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
    "MaxAgeSeconds": 3600
  }
]
```

## Qué no he podido completar y por qué

### No he podido crear recursos reales en Cloudflare

Motivo exacto:

- no existía ningún método de autenticación utilizable en este entorno
- no había token ni account ID en local
- no había sesión `wrangler` ya iniciada

### No he podido verificar si Pages, Worker o R2 ya existen

Motivo exacto:

- sin autenticación de Cloudflare no hay forma fiable de inspeccionar el estado real de la cuenta

### No he podido lanzar despliegues reales a Cloudflare

Motivo exacto:

- GitHub no tiene configurados los secrets necesarios
- el entorno local tampoco tiene credenciales de Cloudflare

## Hallazgo adicional importante fuera del wiring

He ejecutado `back/scripts/build_frontend_opportunity_listings.py` para comprobar el flujo semanal con los datos locales actuales.

Resultado:

- el script funciona
- genera `207` listings seleccionados
- pero el `front/public/data/opportunities/listings.json` resultante deriva bastante del snapshot versionado actual

No he dejado ese cambio en el árbol final porque:

- depende de `storage/`, que es local y no versionado como fuente cerrada de despliegue
- mezclarlo con esta intervención de DevOps habría introducido un diff funcional muy grande y ajeno al wiring Cloudflare/GitHub

Conclusión operativa:

- el pipeline semanal está vivo
- pero conviene tratar el refresh de `listings.json` como una decisión funcional separada del cierre de infraestructura

## Lo mínimo que falta hacer manualmente

Solo queda lo que realmente no podía hacer yo sin acceso a tu cuenta de Cloudflare.

### 1. Crear o confirmar los recursos reales en Cloudflare

Necesitas confirmar o crear:

- proyecto de Pages
- bucket R2 público
- worker `localizate-opportunity-geocode`

Nombres recomendados si aún no existen:

- Pages: `localizate`
- bucket R2: `localizate-public-data`
- worker: `localizate-opportunity-geocode`

### 2. Crear los secrets en GitHub

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

### 3. Crear las variables en GitHub

- `CLOUDFLARE_PAGES_PROJECT_NAME`
- `R2_BUCKET_NAME`
- `NEXT_PUBLIC_DATA_BASE_URL`
- `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT`

### 4. Lanzar los workflows en este orden

1. `Deploy Opportunity Geocode Worker`
2. `Publish Public Data to R2`
3. `Deploy Static Web to Cloudflare Pages`
4. `Refresh Opportunity Listings` para validar la automatización semanal

## Checklist final de producción

- workflow semanal reparado
- workflows endurecidos con validación clara de configuración
- `wrangler` fijado a versión moderna y validado en dry-run
- frontend realmente desacoplado del JSON pesado cuando usa base externa
- export estático reducido de ~`14.7 MB` a ~`3.2 MB`
- `front/out/data` eliminado correctamente
- sync a R2 preparado con materialización previa del histórico troceado
- pendientes reales reducidos a credenciales y recursos Cloudflare
