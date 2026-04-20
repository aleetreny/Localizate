# Análisis estrategico: Histórico vs Oportunidades

Fecha: 2026-04-09

## Objetivo

Este documento audita en profundidad la separación entre la vista de Histórico y la vista de Oportunidades del frontend web de Localízate. El alcance no se limita a la estructura actual: se valoran tambien cambios más profundos de arquitectura de producto, narrativa y visualizacion, siempre apoyados en datos ya presentes en el repo o claramente accesibles desde los builders y datasets ya integrados.

La pregunta central es doble:

1. Si la separación actual entre ambas vistas es suficientemente clara para un usuario final.
2. Si el producto final debería conservar esta estructura, reforzarla o reemplazarla por algo más ambicioso.

## Fuentes principales revisadas

Para este análisis se han revisado sobre todo estas piezas del repo:

- frontend actual: `front/components/map-shell.tsx`, `front/components/opportunity-shell.tsx`, `front/components/view-tabs.tsx`, `front/components/madrid-map.tsx`, `front/components/opportunity-map.tsx`
- contratos y carga de artefactos: `front/lib/types.ts`, `front/lib/public-data.ts`, `front/lib/opportunity-insights.ts`
- builders y semántica de datos: `back/scripts/build_frontend_map_artifacts.py`, `back/scripts/build_frontend_opportunity_artifacts.py`
- base documental: `README.md`, `docs/project/project-overview.md`, `docs/product/product-overview.md`, `docs/data/external_datasets_report.md`, `docs/product/web-activity-taxonomy.md`
- senales de datos y modelado: `back/src/localizate/abt_survival.py`, `back/src/localizate/survival_features.py`
- cobertura de tests ya existente en Python: `back/tests/`, con especial foco en `back/tests/test_build_frontend_map_artifacts.py` y `back/tests/test_build_frontend_opportunity_artifacts.py`

---

## Resumen ejecutivo

La separación conceptual del producto existe, pero la separación perceptiva todavía no.

Hoy el sistema ya tiene dos motores distintos:

- Histórico es una lectura observada y agregada del mercado. Responde a que zonas y categorías han funcionado mejor o peor en Madrid.
- Oportunidades es una lectura puntual y decisional. Responde a si una ubicación concreta parece favorable hoy y para que actividades.

El problema no es que Oportunidades use datos históricos. Eso es correcto y necesario. El problema es que esos datos históricos no están jerarquizados como evidencia de soporte, sino que conviven demasiado cerca del lenguaje y de la visualidad de la capa predictiva. El usuario ve dos vistas casi hermanas, con gramática visual parecida, el mismo horizonte temporal, métricas con nombres parecidos y el mismo patron de explicadores. La arquitectura ya separa; la interfaz todavía no remata la separación.

Mi conclusion principal es esta:

- No retiraria el histórico de Oportunidades.
- No me quedaria tampoco con la estructura actual tal cual.
- Recomiendo evolucionar el producto a una entrada por intención de uso y dos vistas mucho más asimetricas, con una narrativa clara de Mercado frente a Decisión.

La estructura final recomendada no es simplemente Histórico vs Oportunidades como dos tabs equivalentes. La recomendación es:

1. Introducir una capa de entrada o onboarding que haga elegir entre entender el mercado o evaluar una ubicación.
2. Mantener dos vistas nucleares, pero redisenadas como productos casi distintos.
3. Reforzar Histórico como observatorio territorial y sectorial.
4. Reforzar Oportunidades como mesa de decisión puntual, con el histórico claramente etiquetado como contexto observado y no como protagonista.

Si se quiere una versión final más solida y con mayor personalidad, el proyecto debería dejar de parecer dos pestañas de un mismo mapa y empezar a parecer dos instrumentos distintos que comparten una base analítica.

---

## 1. Estado actual de cada vista

| Eje | Histórico | Oportunidades |
| --- | --- | --- |
| Pregunta principal | Que ha pasado en el mercado | Que conviene hacer en un punto concreto |
| Unidad de análisis | Hexagono H3 + categoría | Local listado o punto libre + sección censal |
| Tipo de verdad | Observada y agregada | Predictiva, contextual y decisional |
| Datos dominantes | Supervivencia, riesgo relativo, ranking zonal, composicion por categorías | Riesgo contextual, supervivencia esperada, ranking de actividades, contexto demografico y urbano |
| Patron de uso | Exploracion territorial | Evaluacion puntual |
| Interaccion principal | Elegir categoría y leer el mapa | Elegir punto y decidir |

### Lo que hace hoy Histórico

Histórico se comporta como un mapa de supervivencia comercial agregado. El usuario selecciona una categoría y examina hexagonos coloreados por supervivencia y riesgo relativo. El lateral complementa la lectura con ranking del hexágono, comparación frente a la media y zonas destacadas.

Esta vista responde bien a preguntas como:

- Donde aguanta mejor una categoría.
- Que barrios y distritos salen mejor para una actividad.
- Como se reparte una mezcla comercial dentro de un hexágono.

La lectura dominante es observada. Incluso cuando aparece un score de riesgo, ese score esta subordinado a un mapa de comportamiento histórico agregado.

### Lo que hace hoy Oportunidades

Oportunidades se comporta como una ficha de decisión sobre ubicaciones. El usuario selecciona un local real o marca un punto libre, y el sistema responde con supervivencia esperada, ranking territorial, ranking de actividades recomendadas y contexto de renta, demografía, metro, competencia, avisos, vulnerabilidad y otros factores.

Esta vista responde bien a preguntas como:

- Si esta ubicación parece fuerte o fragil.
- Que actividad tiene mejor encaje en este entorno.
- Que factores del barrio o de la sección están empujando la lectura.

La lectura dominante es predictiva. Sin embargo, muchas de sus métricas salen de histórico observado o de contexto urbano, y eso no siempre esta comunicado con suficiente jerarquía.

---

## 2. Donde la separación actual funciona bien

La separación actual funciona mejor de lo que parece a primera vista. Hay varios aciertos claros.

### 2.1 La unidad de análisis ya esta bien separada

Histórico trabaja con territorio agregado y Oportunidades con ubicación puntual. Esa diferencia es correcta y no debería perderse.

### 2.2 El motor de recomendación de Oportunidades ya es distinto

Oportunidades no es un espejo del mapa histórico. Tiene su propia logica: locales disponibles, seleccion manual, ranking de actividades, benchmarking territorial y lectura contextual. No es una simple vista más del mismo artefacto.

### 2.3 El producto ya sabe que el punto se interpreta contra la sección censal

La aclaracion de que la ficha se lee contra la sección censal contenedora es una decisión correcta. Sin ella, Oportunidades pareceria una prediccion imposible sobre una dirección individual.

### 2.4 El histórico ya tiene potencial para ser un observatorio, no solo un mapa

Entre los artefactos, la taxonomia, los agregados zonales y los datos de composicion, Histórico ya tiene base suficiente para evolucionar a una herramienta de inteligencia territorial bastante más rica que el estado actual.

---

## 3. Donde se rompe hoy la separación

La confusion actual no viene de una sola decisión. Viene de varias capas acumuladas.

### 3.1 La navegación las presenta como hermanas simetricas

El producto actual sugiere que ambas vistas son dos versiones equivalentes de una misma cosa. Esto empobrece la narrativa. No lo son.

Histórico es una lente de exploracion de mercado.
Oportunidades es una lente de decisión.

Si la interfaz las coloca como dos tabs planas y simetricas, el usuario entra en ambas esperando el mismo tipo de respuesta.

### 3.2 Ambas reutilizan demasiado la misma gramática visual

Comparten sidebar, tarjeta de estadísticas, métricas clicables, banners explicativos y jerarquía visual muy parecida. El usuario cambia de vista, pero no siente que haya cambiado de instrumento.

### 3.3 El horizonte temporal se repite con semanticas distintas

El selector 12m y 24m aparece en ambas pantallas, pero no significa exactamente lo mismo.

- En Histórico habla de continuidad observada de locales comparables.
- En Oportunidades habla de supervivencia esperada o de contexto usado en un ranking.

Ese paralelismo visual favorece una lectura falsa de equivalencia.

### 3.4 El termino supervivencia esta sobrecargado

Esta es la confusion más importante.

Hoy un usuario puede leer supervivencia en Histórico y en Oportunidades y asumir que es la misma magnitud. No lo es.

- En Histórico, supervivencia es observación agregada de lo que ha pasado.
- En Oportunidades, supervivencia es una traduccion del score de riesgo a una probabilidad esperada para un entorno.
- Dentro del ranking de actividades de Oportunidades, vuelve a aparecer supervivencia, pero como referencia historica de soporte.

Sin etiquetas como observado, esperado o soporte histórico, se mezclan tres cosas distintas bajo la misma palabra.

### 3.5 Oportunidades mezcla bien los datos, pero no siempre los ordena bien

Oportunidades tiene razon al mezclar:

- prediccion del modelo,
- contexto demografico,
- senales urbanas,
- evidencia historica de categorías,
- mercado actual de listings.

El problema no es la mezcla. El problema es que al usuario no siempre le queda claro que papel juega cada capa.

### 3.6 El framing interno del proyecto no siempre acompaña

Hay senales de deriva de lenguaje interno. Por ejemplo, el builder histórico todavía habla de regiones de prediccion en su subtitulo, cuando esa vista se usa de facto como lectura historica agregada. Eso alimenta la ambigüedad conceptual.

---

## 4. Decisión de producto: que hacer con el histórico dentro de Oportunidades

### Veredicto

No retiraria el histórico de Oportunidades.

Seria un error. La recomendación de actividad, la lectura de riesgo contextual y buena parte del valor del producto dependen precisamente de usar histórico observado y contexto territorial para informar una decisión puntual.

Lo que si cambiaría es el contrato semantico de esa informacion.

### Regla de oro recomendada

En Oportunidades, toda metrica debe pertenecer con claridad a una de estas tres familias:

1. Decisión: lo que el producto cree o recomienda para este punto.
2. Contexto observado: lo que sabemos del entorno por histórico o por datos urbanos.
3. Mercado actual: lo que sabemos del listing en venta o alquiler.

Si una tarjeta no deja claro a cual de estas familias pertenece, hay riesgo de confusion.

### Traduccion practica

En la vista final recomendada:

- La capa principal de Oportunidades debe ser decisional.
- El contexto histórico debe quedar claramente etiquetado como evidencia observada.
- El listing debe quedar claramente etiquetado como mercado actual.

No hay que vaciar Oportunidades de histórico; hay que poner cada pieza en su sitio.

---

## 5. No aferrarse a la estructura actual: arquitecturas posibles

He considerado cuatro arquitecturas realistas. No todas valen lo mismo.

### Opcion A. Mantener dos vistas y solo mejorar copy y etiquetas

#### Qué sería

Seguir con Histórico y Oportunidades como tabs equivalentes, pero afinando nomenclatura, microcopy y algunos labels de métricas.

#### Ventajas

- Bajo riesgo.
- Poco esfuerzo.
- Se puede ejecutar rapido.

#### Riesgos

- Corrige sintomas, no corrige del todo la sensacion de simetria.
- El producto seguiria pareciendo dos versiones del mismo mapa.

#### Mi valoracion

Insuficiente para una versión final fuerte. Es una mejora buena, pero demasiado conservadora.

### Opcion B. Mantener dos vistas nucleares, pero con entrada por intención y mucha más asimetria

#### Qué sería

No arrancar ya con dos tabs iguales. Arrancar con una entrada tipo:

- Entender el mercado.
- Evaluar una ubicación.

Desde ahi, conducir al usuario a dos vistas que compartan base de datos, pero no look and feel.

#### Ventajas

- Mantiene claridad de producto.
- Cambia el marco mental desde el inicio.
- Permite seguir teniendo solo dos modos principales.
- Evita sobrecargar al usuario con una tercera vista si no hace falta.

#### Riesgos

- Requiere redisenar la navegación y dejar de pensar en tabs simetricas.
- Obliga a aceptar que ambas vistas no deben parecerse tanto.

#### Mi valoracion

Es la opcion recomendada.

### Opcion C. Pasar a tres vistas: Tendencias, Dinamica y Oportunidades

#### Qué sería

Separar el actual Histórico en dos productos:

- Tendencias: supervivencia, riesgo relativo y fortaleza zonal.
- Dinamica: entradas, salidas, rotación, cohortes, ganadores y perdedores.
- Oportunidades: decisión puntual.

#### Ventajas

- Distincion conceptual muy fuerte.
- Hace visible una dimension temporal y de mercado que hoy esta escondida.

#### Riesgos

- Puede fragmentar demasiado la experiencia.
- Exige más esfuerzo explicativo.
- Puede penalizar a usuarios que solo quieren una lectura rápida.

#### Mi valoracion

Es atractiva, pero la reservaria para una segunda gran evolución. No la pondría como primera jugada si el objetivo es cerrar una versión final consistente y legible.

### Opcion D. Workspace unico con caminos por tarea

#### Qué sería

Eliminar la division rigida en tabs y construir un espacio de trabajo por preguntas: comparar zonas, analizar punto, entender categoría, revisar dinámica, etc.

#### Ventajas

- Maxima potencia.
- Muy buena para usuarios expertos.

#### Riesgos

- Muy alta complejidad de frontend y narrativa.
- Alto riesgo de sobrecarga cognitiva.
- Facil de convertir en un producto brillante para el equipo y confuso para el usuario final.

#### Mi valoracion

No la recomiendo como objetivo inmediato.

### Recomendacion final de arquitectura

Mi recomendación es la Opcion B.

No me aferro a la estructura actual, pero tampoco romperia el producto por completo. La versión final más valida me parece esta:

1. Una entrada por intención de uso.
2. Dos vistas nucleares bien diferenciadas.
3. Histórico reforzado como observatorio de mercado.
4. Oportunidades reforzada como instrumento de decisión.
5. Dinamica temporal incorporada como capa o modo dentro de Histórico, no como tercer producto de primer nivel.

---

## 6. Nomenclatura y narrativa recomendadas

No usaria Histórico y Oportunidades como nombres protagonistas en la versión final. Son funcionales internamente, pero debiles para producto.

### Propuesta recomendada

#### Pantalla de entrada

- Entender el mercado
- Evaluar una ubicación

#### Vista 1

Nombre sugerido: Mercado

Subtitulo sugerido: Donde funciona cada tipo de actividad y como cambia el tejido comercial.

#### Vista 2

Nombre sugerido: Decisión

Subtitulo sugerido: Que encaje tiene esta ubicación hoy y que actividades parten con mejor lectura.

### Por que esta nomenclatura es mejor

- Mercado explica exploracion agregada mejor que Histórico.
- Decisión explica accion puntual mejor que Oportunidades.
- El usuario entiende enseguida que una vista sirve para aprender y la otra para decidir.

---

## 7. Como haría las dos vistas mucho más distintas

### 7.1 Vista Mercado

La convertiría en un observatorio territorial. No solo un mapa H3 con una ficha lateral.

#### Su núcleo debería ser

- mapa principal de fortaleza o supervivencia observada,
- selector de categoría,
- lectura zonal clara,
- capas opcionales de dinámica,
- contexto urbano y comercial de apoyo.

#### Lo que cambiaría

1. Mantener H3 como capa base, pero permitir cambiar de modo entre fortaleza, rotación y concentración comercial.
2. Dar más protagonismo a distrito y barrio como unidades de interpretación, no solo al hexágono.
3. Convertir la ficha lateral en un panel de observación de mercado, no solo en una tarjeta del hexágono seleccionado.
4. Reservar el lenguaje de probabilidad o decisión para Oportunidades. Aquí todo debería hablar de observado, agregado, histórico o estructura territorial.

### 7.2 Vista Decisión

La convertiría en una mesa de análisis puntual. Menos mapa de exploracion y más tablero de juicio.

#### Su núcleo debería ser

- seleccion de punto o listing,
- lectura principal de riesgo y encaje,
- descomposicion del porque,
- comparación con el mercado,
- ranking de actividades como recomendación final.

#### Lo que cambiaría

1. El mapa dejaría de ser un protagonista equivalente al de Mercado. Seria un selector espacial para abrir la ficha correcta.
2. El lateral se dividiria en tres bloques muy marcados: mercado actual del local, decisión del modelo, contexto observado del entorno.
3. El ranking de actividades dejaría de parecer una lista más y pasaría a ser una conclusion de decisión.
4. El lenguaje de Oportunidades debería hablar de esperado, encaje, soporte histórico y benchmark, no de comportamiento agregado del mercado en abstracto.

---

## 8. Visualizaciones nuevas recomendadas

Las siguientes ideas no son fantasias. Se apoyan en datos ya existentes en el repo o muy proximos a los builders actuales.

### 8.1 Visualizaciones para Mercado

| Idea | Pregunta que responde | Datos ya disponibles | Viabilidad | Impacto |
| --- | --- | --- | --- | --- |
| Heatmap de rotación 12m | Donde el tejido comercial cambia más | `section_turnover_rate_12m_start`, entradas y salidas | Alta | Alta |
| Indicador de concentración comercial | La zona esta muy concentrada o es diversa | HHI y shares comerciales del ABT | Alta | Media-alta |
| Ganadores y perdedores por barrio | Que categorías están entrando o saliendo | flujos por categoría y zona | Media | Alta |
| Cohortes de entrada y mortalidad | Que paso con los locales que entraron en distintos periodos | cohortes del ABT y supervivencia historica | Media | Media-alta |
| Overlay de equipamientos urbanos | Que contexto urbano rodea la zona | mercados, colegios, parques, cultura, BiciMAD, metro | Media | Media |
| Índice de estabilidad vs dinamismo | La zona es segura, estable o volátil | turnover, net flow, concentración, supervivencia | Media | Media |
| Barrios similares | Que otras zonas se parecen a esta | renta, densidad, edad, mix comercial, vulnerabilidad | Media | Baja-media |

#### Las dos que priorizaria primero

1. Heatmap de rotación 12m.
2. Ganadores y perdedores por barrio.

Con esas dos piezas, Mercado deja de ser un mapa bonito de supervivencia y pasa a ser un observatorio de comportamiento comercial.

### 8.2 Visualizaciones para Decisión

| Idea | Pregunta que responde | Datos ya disponibles | Viabilidad | Impacto |
| --- | --- | --- | --- | --- |
| Radar de drivers de riesgo | Que esta empujando la lectura del punto | score, features del modelo, contexto ya calculado | Media | Muy alta |
| Scatter de actividades: encaje vs soporte | Que actividad encaja bien y ademas tiene suficiente evidencia | top activities, support, survival, source zone | Alta | Muy alta |
| Histograma de percentiles | Donde cae este punto frente a Madrid, distrito y barrio | benchmark context ya calculado | Alta | Alta |
| Anillo de accesibilidad y dotacion | Como de accesible y servido esta el punto | metro, equipamientos por radio, BiciMAD | Media | Alta |
| Mapa de presion regulatoria | Hay senales de inspeccion o friccion en el entorno | inspecciones, avisos, top categorías | Media | Media |
| Matriz precio del local vs lectura del entorno | El anuncio parece caro, barato o razonable para esta lectura | price_eur, price_per_m2_eur, percentiles, tier | Alta | Alta |

#### Las dos que priorizaria primero

1. Radar de drivers de riesgo.
2. Scatter de actividades: encaje vs soporte.

Con esas dos piezas, Decisión deja de ser solo una ficha larga y se convierte en una herramienta que explica y compara.

### 8.3 Lo que no haría

Hay ideas que parecen tentadoras pero debilitarian la separación.

No haría estas tres cosas:

1. No pondría hexagonos históricos como capa principal dentro de Oportunidades.
2. No dejaría la misma escala cromatica y la misma jerarquía visual en ambas vistas.
3. No reutilizaria sin calificador palabras como supervivencia o ranking si la semántica cambia.

---

## 9. Propuesta de experiencia final

Si tuviera que definir una versión final del producto con ambicion pero con cabeza, la experiencia sería esta.

### Paso 1. Pantalla de entrada

Dos tarjetas muy claras:

- Entender el mercado.
- Evaluar una ubicación.

No es cosmetica. Es el momento en que el producto deja de presentar dos tabs equivalentes y se explica por intención.

### Paso 2. Mercado

Un observatorio donde el usuario puede responder a cuatro tipos de pregunta:

- que zonas son fuertes para una categoría,
- que zonas están cambiando,
- que categorías ganan o pierden en cada barrio,
- que contexto urbano y social acompaña a esa lectura.

### Paso 3. Decisión

Una mesa donde el usuario puede responder a cuatro tipos de pregunta:

- esta ubicación parece favorable o fragil,
- por que,
- que actividades encajan mejor,
- como se compara con su distrito, su barrio y Madrid.

### Paso 4. Conexion entre ambas vistas

La conexion no debe ser una simetria de tabs, sino una escalera de lectura.

- Desde Mercado puedes saltar a Decisión si encuentras una zona prometedora y quieres evaluar un punto.
- Desde Decisión puedes saltar a Mercado si quieres comprobar si la buena lectura del punto se sostiene en el tejido zonal.

Eso si une ambas vistas de forma inteligente.

---

## 10. Roadmap de producto recomendado

### Fase 0. Claridad semántica

Objetivo: eliminar la confusion más peligrosa sin rehacer aún el frontend entero.

Acciones:

- etiquetar observado, esperado y soporte histórico,
- renombrar vistas y subtítulos,
- redibujar la jerarquía interna de Oportunidades,
- limpiar el framing interno del builder histórico.

### Fase 1. Rediseño de la entrada

Objetivo: dejar de arrancar con dos tabs equivalentes.

Acciones:

- pantalla de entrada por intención,
- cards de navegación a Mercado y Decisión,
- persistencia suave del ultimo modo usado.

### Fase 2. Mercado como observatorio

Objetivo: convertir Histórico en una herramienta más profunda.

Acciones:

- modo de rotación,
- ganadores y perdedores,
- capas de contexto urbano,
- cohortes o estabilidad si hay tiempo.

### Fase 3. Decisión como mesa de juicio

Objetivo: convertir Oportunidades en un tablero de decisión.

Acciones:

- radar de drivers,
- scatter de actividades,
- histograma de percentiles,
- matriz precio vs lectura,
- etiquetado fuerte de mercado actual frente a contexto observado.

### Fase 4. Endurecimiento

Objetivo: preparar la versión final del proyecto para crecer con seguridad.

Acciones:

- mejorar contratos de artefactos,
- añadir pruebas frontend,
- automatizar checks y build,
- preparar estrategia de cache y payload.

---

## 11. Mejoras sugeridas para hacer el proyecto más solido

Esta sección va más alla del binomio Histórico/Oportunidades. Aquí el foco es la solidez general del proyecto.

### 11.1 Navegacion y framing de producto

#### Problema actual

La navegación actual presenta dos vistas como si fuesen equivalentes, cuando responden a tareas distintas.

#### Evidencia

- `front/components/view-tabs.tsx`
- `front/components/map-shell.tsx`
- `front/components/opportunity-shell.tsx`

#### Viabilidad

Alta. Es un cambio de frontend y copy, no de pipeline.

#### Impacto

Muy alto. Es la mejora con mejor retorno sobre esfuerzo para claridad de producto.

#### Recomendacion

Cambiar tabs simetricas por entrada por intención y vistas más asimetricas.

### 11.2 Diferenciacion visual radical entre Mercado y Decisión

#### Problema actual

Ambas vistas comparten demasiada gramática visual: lateral, cards, banners, tonos y patron de lectura.

#### Evidencia

- `front/components/map-shell.tsx`
- `front/components/opportunity-shell.tsx`
- `front/components/madrid-map.tsx`
- `front/components/opportunity-map.tsx`

#### Viabilidad

Media. No es difícil tecnicamente, pero requiere criterio de diseño y no solo cambios cosméticos.

#### Impacto

Muy alto. El usuario necesita sentir que ha cambiado de instrumento, no solo de tab.

#### Recomendacion

Dar a Mercado una visualidad más cartografica y a Decisión una visualidad más analítica y puntual.

### 11.3 Descomposicion de las shells monoliticas

#### Problema actual

`opportunity-shell.tsx` y, en menor medida, `map-shell.tsx` concentran demasiada logica de estado, calculo y presentacion.

#### Evidencia

- `front/components/opportunity-shell.tsx`
- `front/components/map-shell.tsx`

#### Viabilidad

Media. Requiere refactor, pero no es un cambio de producto incierto.

#### Impacto

Alto. Mejoraria mantenibilidad, pruebas y velocidad de iteracion.

#### Recomendacion

Separar estado, builders de métricas, explicadores y componentes visuales en capas más pequeñas y testeables.

### 11.4 Pruebas frontend e interaccion

#### Problema actual

El proyecto tiene una base Python bien cubierta con `unittest`, pero el frontend no expone hoy una suite visible de pruebas de componentes o interaccion.

#### Evidencia

- `back/tests/` contiene batería Python amplia
- `front/package.json` no muestra scripts de test frontend
- no hay archivos `*.test.tsx` visibles en `front`

#### Viabilidad

Alta. Se puede arrancar por componentes críticos y rutas principales.

#### Impacto

Alto. Reduciria regresiones en UX, especialmente en banners, overlays, hover panels y explicadores.

#### Recomendacion

Introducir pruebas de componentes y al menos un smoke test de navegación Mercado/Decisión.

### 11.5 CI y checks automaticos

#### Problema actual

No hay una pipeline visible de CI en el repo para ejecutar automáticamente tests Python, typecheck web y build de Next.

#### Evidencia

- no hay `.github/workflows` visible
- `front/package.json`
- `back/tests/`

#### Viabilidad

Alta. El proyecto ya tiene comandos claros para validar Python y web.

#### Impacto

Muy alto. Es clave para cerrar una versión final con más seguridad.

#### Recomendacion

Montar una CI mínima con tres checks: unit tests Python, `tsc --noEmit` y `npm run build` en `front`.

### 11.6 Validación runtime de artefactos frontend

#### Problema actual

El frontend tipa los artefactos en TypeScript, pero no hace validación runtime al cargar JSON grandes desde `public/data`.

#### Evidencia

- `front/lib/types.ts`
- `front/lib/public-data.ts`

#### Viabilidad

Alta. Se puede introducir un validador ligero sin cambiar el pipeline de fondo.

#### Impacto

Alto. Ayudaría a detectar roturas de schema, nulos inesperados o cambios de artefacto antes de que se conviertan en bugs opacos.

#### Recomendacion

Incorporar validación runtime de metadatos y campos críticos en la carga de artefactos.

### 11.7 Metadatos, versionado y escritura atomica de artefactos

#### Problema actual

Los builders escriben salidas directamente a disco. Oportunidades ya versiona el path del GeoJSON, pero el ecosistema de artefactos no esta homogeneizado ni protegido por escrituras atomicas.

#### Evidencia

- `back/scripts/build_frontend_opportunity_artifacts.py`
- `back/scripts/build_frontend_map_artifacts.py`

#### Viabilidad

Alta. Es un endurecimiento tecnico muy razonable.

#### Impacto

Alto. Mejora trazabilidad, evita estados parciales y facilita debugging de cache.

#### Recomendacion

Anadir metadata uniforme de versión de build, origen de datos y parámetros, y usar escritura atomica para JSON, GeoJSON y CSV críticos.

### 11.8 Auditoría explicita de soporte, fallback e imputación

#### Problema actual

El proyecto ha avanzado mucho en soporte y semántica de nulos, pero sigue costando ver, desde producto o desde artefacto, cuando una lectura sale de soporte fuerte, fallback territorial o imputación.

#### Evidencia

- `docs/project/project-overview.md`
- `back/scripts/build_frontend_map_artifacts.py`
- `back/scripts/build_frontend_opportunity_artifacts.py`
- memorias del repo sobre `frontend_map_artifact_semantics` y `opportunity_artifact_semantics`

#### Viabilidad

Media-alta. Gran parte del trabajo es serializar mejor y exponer más claramente flags ya existentes.

#### Impacto

Muy alto. Esta mejora sube la credibilidad del producto y evita malas lecturas sobre evidencia débil.

#### Recomendacion

Exponer más claramente si una metrica viene de soporte directo, fallback distrital o lectura ciudad, y estandarizar esa semántica entre Mercado y Decisión.

### 11.9 Reconciliacion offline frente a producto

#### Problema actual

El pipeline Python y el frontend están bien conectados, pero falta una capa explicita de reconciliacion que garantice que lo servido al usuario coincide exactamente con la semántica calculada offline.

#### Evidencia

- builders de artefactos
- `front/lib/types.ts`
- `front/lib/public-data.ts`

#### Viabilidad

Media. Requiere tests de reconciliacion, no un rediseño completo.

#### Impacto

Alto. Reduce bugs silenciosos y hace más robusta la auditoría de datos.

#### Recomendacion

Introducir tests de reconciliacion sobre una muestra fija de puntos y zonas entre outputs Python y lectura frontend.

### 11.10 Estrategia de payload y futura API ligera

#### Problema actual

El frontend ya descarga artefactos desde `public/data`, pero el crecimiento de campos, capas y visualizaciones puede empujar el payload a una zona incomoda.

#### Evidencia

- `front/lib/public-data.ts`
- `docs/project/project-overview.md` ya recoge la necesidad de seguir endureciendo la capa de artefactos y su mantenimiento operativo

#### Viabilidad

Media. No urge hoy, pero conviene disenar la transición antes de que duela.

#### Impacto

Medio-alto. Evita que la siguiente evolución de producto quede frenada por peso, cache o tiempo de parseo.

#### Recomendacion

Definir desde ya que partes deben seguir como artefacto estático y que partes pasarian mejor a una API ligera bajo demanda si el proyecto crece.

### 11.11 Runbooks y documentación operativa

#### Problema actual

`docs/project/project-overview.md` resume bien el contexto público del proyecto, pero no sustituye del todo a runbooks operativos cortos para reconstruir artefactos, validar resultados y depurar fallos.

#### Evidencia

- `docs/project/project-overview.md`
- ausencia visible de runbooks dedicados en `docs/`

#### Viabilidad

Alta. Es sobre todo trabajo documental.

#### Impacto

Medio-alto. Mejora onboarding, continuidad y resiliencia del proyecto.

#### Recomendacion

Anadir runbooks cortos para reconstruccion de artefactos, chequeos de salud del frontend y procedimiento de validación antes de publicar.

### 11.12 Lenguaje unificado entre producto, builders y docs

#### Problema actual

Hay pequenos desajustes de vocabulario entre docs, builders y frontend: prediccion, histórico, supervivencia, riesgo relativo, riesgo contextual, soporte, ranking.

#### Evidencia

- `README.md`
- `docs/project/project-overview.md`
- `docs/product/product-overview.md`
- `back/scripts/build_frontend_map_artifacts.py`
- `back/scripts/build_frontend_opportunity_artifacts.py`

#### Viabilidad

Alta.

#### Impacto

Alto. Unifica la experiencia y reduce deuda conceptual.

#### Recomendacion

Definir un pequeno glosario de producto para Mercado y Decisión y usarlo de forma coherente en builders, docs y frontend.

---

## 12. Priorizacion sugerida

### Prioridad 1

- Reencuadrar navegación y narrativa.
- Diferenciar visualmente Mercado y Decisión.
- Etiquetar de forma explicita observado, esperado y soporte histórico.
- Introducir radar de drivers y scatter de actividades en Decisión.
- Introducir modo de rotación y ganadores/perdedores en Mercado.

### Prioridad 2

- Descomponer shells monoliticas.
- Anadir pruebas frontend.
- Montar CI mínima.
- Endurecer contratos de artefactos y metadata.

### Prioridad 3

- Preparar runbooks.
- Definir estrategia futura de API ligera.
- Explorar barrio similares, cohortes y estabilidad compuesta si aportan valor real tras la fase 1.

---

## 13. Conclusiones finales

La pregunta correcta no es si Oportunidades tiene demasiado histórico. La pregunta correcta es si el histórico dentro de Oportunidades esta jugando el papel correcto.

Mi respuesta es que hoy no del todo.

No porque sobren datos, sino porque falta una jerarquía más clara entre:

- lo que el producto observa,
- lo que el producto estima,
- y lo que el mercado actual ofrece.

La versión final más valida de Localízate no debería ser un frontend con dos tabs parecidas. Debería ser un sistema con dos modos de pensamiento:

- Mercado para entender.
- Decisión para actuar.

Los datos del repo ya permiten llegar bastante más lejos de donde esta hoy el frontend. Hay base suficiente para construir una versión final más clara, más distinta entre vistas, más útil para usuario real y tambien más defendible como producto serio.

Si tuviera que resumir la recomendación en una sola frase, sería esta:

Localízate no necesita menos histórico en Oportunidades; necesita que el histórico deje de parecer el protagonista equivocado y pase a ser la evidencia correcta dentro de una herramienta de decisión mucho más clara.
