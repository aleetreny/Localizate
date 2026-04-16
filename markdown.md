# Plan Temporal: Automatizacion Semanal + Publicacion Web

## 1. Objetivo real

Durante los proximos 5 meses no hace falta recalcular todo el modelo ni rehacer el pipeline pesado.
Lo que si queremos automatizar es esto:

1. Raspar `locales.es` una vez por semana.
2. Actualizar los anuncios visibles en `Oportunidades`.
3. Recalcular el `listings.json` del frontend con esos anuncios.
4. Mantener fija la foto estructural de secciones (`index.json` + `geometry.geojson`).
5. Publicar solo si el resultado final es sano y no vacio.

Ese flujo ya queda preparado en el repo con:

- `.github/workflows/refresh-opportunities-weekly.yml`
- `back/scripts/build_manual_available_locales.py`
- `back/scripts/build_frontend_opportunity_listings.py`
- `back/src/localizate/section_geography.py`
- `.gitignore` ajustado para permitir versionar `front/public/data/opportunities/sections/geometry.geojson`

## 2. Como funciona la automatizacion semanal

Cada semana GitHub Actions hace esto:

1. Clona el repo.
2. Restaura la cache de geocoding si existe.
3. Instala solo las dependencias minimas del refresh semanal.
4. Ejecuta el scraping de `locales.es`.
5. Regenera `front/public/data/opportunities/listings.json`.
6. Valida que el JSON no este vacio y que el numero de puntos sea coherente.
7. Si hay cambios reales, hace commit y push.
8. Si falla, no publica nada nuevo y se mantiene la version anterior.

Horario actual del workflow:

- Lunes a las `05:00 UTC`
- En Madrid, mientras haya horario de verano, equivale a `07:00`

## 3. Lo que tienes que hacer tu en GitHub

### Paso 1. Subir estos cambios al repo

Antes de nada, tienes que committear y subir:

- `.github/workflows/refresh-opportunities-weekly.yml`
- `back/requirements-opportunity-weekly.txt`
- `back/scripts/build_frontend_opportunity_listings.py`
- `back/src/localizate/section_geography.py`
- `front/public/data/opportunities/sections/geometry.geojson`
- `.gitignore`
- `back/tests/test_build_frontend_opportunity_listings.py`
- `back/tests/test_section_geography_fallback.py`

Punto importante:

- `front/public/data/opportunities/sections/geometry.geojson` estaba bloqueado por el ignore global de `*.geojson`.
- Ahora ya no.
- Si no lo subes, el workflow semanal no tendra geometria fallback en GitHub Actions.

### Paso 2. Confirmar que el repo vive en GitHub

Necesitas que el proyecto este en GitHub con una rama principal estable:

- `main` o
- `master`

El workflow esta pensado para ejecutarse ahi.

### Paso 3. Activar permisos de escritura para Actions

En GitHub:

1. Abre el repo.
2. Ve a `Settings`.
3. Ve a `Actions`.
4. En `General`, busca `Workflow permissions`.
5. Marca `Read and write permissions`.
6. Guarda.

Esto es necesario porque el workflow hace `commit` y `push` automatico del `listings.json`.

### Paso 4. Lanzar una primera prueba manual

En GitHub:

1. Entra en la pestaña `Actions`.
2. Abre el workflow `Refresh Opportunity Listings`.
3. Pulsa `Run workflow`.
4. Espera a que termine.

Que debes comprobar despues:

1. Que el job termina en verde.
2. Que, si hubo cambios, aparece un commit nuevo tipo `chore: refresh opportunity listings`.
3. Que `front/public/data/opportunities/listings.json` cambia.
4. Que la web sigue cargando bien `Oportunidades`.

### Paso 5. Dejarlo ya en automatico

Una vez la primera prueba manual salga bien:

- no tienes que tocar nada mas.
- el workflow correra cada semana solo.

## 4. Lo que NO hace este flujo

Este flujo semanal NO:

- rehace `index.json`
- rehace `geometry.geojson`
- rehace el historico
- rehace ABTs
- rehace rankings profundos
- rehace avisos o indicadores estructurales

Esto es intencional.
Para tribunal y 5 meses de vida del proyecto, es suficiente y mas robusto.

## 5. Validacion local recomendada antes de empujar

Desde la raiz:

```powershell
.\.venv\Scripts\python.exe back\scripts\build_frontend_opportunity_listings.py
cd back
..\.venv\Scripts\python.exe -m unittest tests.test_build_frontend_opportunity_listings tests.test_section_geography_fallback
```

## 6. Plan recomendado para publicar la web

### Recomendacion principal

La via mas simple para este proyecto es:

1. GitHub para el codigo y el workflow semanal.
2. Vercel para publicar `front/`.
3. Git integration entre GitHub y Vercel.

Con esto ocurre algo muy util:

- GitHub Actions actualiza `listings.json`
- ese commit entra en `main`
- Vercel detecta el commit
- Vercel redepliega la web automaticamente

Tu no haces nada manual cada semana.

## 7. Importante: con el repo actual, Vercel Hobby probablemente NO es la mejor opcion

Hoy el directorio `front/public/data` pesa aproximadamente:

- `362.36 MB` en total
- `337.2 MB` solo la parte `map/`
- `281.15 MB` solo la parte `map/historical/`
- `25.15 MB` la parte `opportunities/`

El fichero mas pesado ahora mismo es:

- `front/public/data/map/historical/hex-composition.json` con unos `235.97 MB`

Esto importa porque, segun la documentacion oficial de Vercel consultada el `16 de abril de 2026`:

- en `Hobby`, el limite de `Static File uploads` es `100 MB`
- en `Pro`, el limite es `1 GB`
- esa limitacion tambien aplica al flujo de importacion de repositorios Git existentes

Fuentes oficiales:

- https://vercel.com/docs/platform/limits/
- https://vercel.com/docs/limits/overview
- https://vercel.com/docs/monorepos/

## Conclusiones practicas

### Opcion A. La mas simple y la que recomiendo

Usar `Vercel Pro` durante el periodo del tribunal.

Ventajas:

- cero inventos
- despliegue natural de `Next.js`
- redeploy automatico por cada commit del workflow semanal
- mantiene API route de geocoding sin tocar codigo

### Opcion B. Intentar quedarte en gratis

Solo la recomiendo si quieres dedicar tiempo a adelgazar la web antes.
Para que sea realista tendrias que:

1. sacar o recortar el historico pesado
2. mover artefactos muy grandes fuera del repo
3. o desactivar temporalmente la parte historica para la demo publica

Si no haces eso, lo normal es que Hobby te de guerra por tamano.

## 8. Paso a paso para desplegar en Vercel

### Opcion recomendada: Vercel Pro

1. Crea cuenta en Vercel con tu GitHub.
2. Pulsa `Add New Project`.
3. Importa el repo de `Localizate`.
4. Cuando Vercel detecte el monorepo:
   - selecciona como `Root Directory` la carpeta `front`
5. Verifica la configuracion:
   - Framework: `Next.js`
   - Install Command: `npm install`
   - Build Command: `npm run build`
   - Output Directory: la de Next por defecto
6. Variables de entorno:
   - ahora mismo no necesitas ninguna obligatoria para levantar la web
7. Pulsa `Deploy`.

### Despues del primer deploy

1. Abre la URL publica que te da Vercel.
2. Revisa:
   - home
   - mapa historico
   - pestaña `Oportunidades`
   - buscador de direccion en oportunidades
3. Si todo esta bien, añade dominio propio si quieres.

## 9. Que partes de la web tiran de internet en runtime

La web publicada no depende de un backend Python vivo para servir el mapa.
Sirve artefactos estaticos desde `front/public/data`.

Lo unico dinamico relevante es:

- `front/app/api/geocode/opportunity-address/route.ts`

Ese endpoint:

- vive dentro de la propia app Next.js
- consulta `Nominatim`
- se usa para buscar direcciones en `Oportunidades`

Esto significa que Vercel te lo resuelve bien sin desplegar un backend Python aparte.

## 10. Paso a paso completo recomendado

### Fase 1. Dejar la automatizacion semanal cerrada

1. Commit de los archivos preparados.
2. Push a GitHub.
3. Activar permisos `Read and write` para Actions.
4. Lanzar `Run workflow` manual.
5. Comprobar commit automatico si hubo cambios.

### Fase 2. Publicar la web

1. Conectar repo a Vercel.
2. Configurar `Root Directory = front`.
3. Desplegar.
4. Verificar la web.

### Fase 3. Probar el flujo extremo a extremo

1. Lanzar de nuevo el workflow semanal manualmente.
2. Esperar a que GitHub genere commit.
3. Confirmar que Vercel detecta el commit.
4. Confirmar que la web publicada refleja el `listings.json` nuevo.

## 11. Lo que te recomiendo hacer ya

Si quieres ir por el camino mas corto y menos arriesgado:

1. Sube estos cambios a GitHub.
2. Activa el workflow.
3. Haz una primera corrida manual.
4. Publica en Vercel Pro con `front` como root.
5. Verifica la web.
6. Dejalo ya correr semanalmente solo.

## 12. Si quieres mantener el coste al minimo

Mi recomendacion realista es:

- mantener gratis GitHub Actions
- usar Vercel Pro solo durante la fase publica del tribunal, si no quieres tocar el historico pesado

Si mas adelante quieres bajar a gratis:

- hacemos una pasada de adelgazamiento del `front/public/data/map/historical/`
- y dejamos una version publica mas ligera

## 13. Checklist corto final

- [ ] Committeado `geometry.geojson`
- [ ] Push al repo en GitHub
- [ ] Actions con permiso `Read and write`
- [ ] Primera corrida manual en verde
- [ ] Proyecto importado en Vercel con root `front`
- [ ] Web publica validada
- [ ] Confirmado que un commit nuevo de Actions dispara redeploy en Vercel
