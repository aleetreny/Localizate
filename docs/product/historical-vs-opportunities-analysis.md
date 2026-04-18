# Analisis estrategico: Historico vs Oportunidades

Fecha: 2026-04-09

## Objetivo

Este documento audita en profundidad la separacion entre la vista de Historico y la vista de Oportunidades del frontend web de Localízate. El alcance no se limita a la estructura actual: se valoran tambien cambios mas profundos de arquitectura de producto, narrativa y visualizacion, siempre apoyados en datos ya presentes en el repo o claramente accesibles desde los builders y datasets ya integrados.

La pregunta central es doble:

1. Si la separacion actual entre ambas vistas es suficientemente clara para un usuario final.
2. Si el producto final deberia conservar esta estructura, reforzarla o reemplazarla por algo mas ambicioso.

## Fuentes principales revisadas

Para este analisis se han revisado sobre todo estas piezas del repo:

- frontend actual: `front/components/map-shell.tsx`, `front/components/opportunity-shell.tsx`, `front/components/view-tabs.tsx`, `front/components/madrid-map.tsx`, `front/components/opportunity-map.tsx`
- contratos y carga de artefactos: `front/lib/types.ts`, `front/lib/public-data.ts`, `front/lib/opportunity-insights.ts`
- builders y semantica de datos: `back/scripts/build_frontend_map_artifacts.py`, `back/scripts/build_frontend_opportunity_artifacts.py`
- base documental: `README.md`, `docs/project/project-overview.md`, `docs/product/product-overview.md`, `docs/data/external_datasets_report.md`, `docs/product/web-activity-taxonomy.md`
- senales de datos y modelado: `back/src/localizate/abt_survival.py`, `back/src/localizate/survival_features.py`
- cobertura de tests ya existente en Python: `back/tests/`, con especial foco en `back/tests/test_build_frontend_map_artifacts.py` y `back/tests/test_build_frontend_opportunity_artifacts.py`

---

## Resumen ejecutivo

La separacion conceptual del producto existe, pero la separacion perceptiva todavia no.

Hoy el sistema ya tiene dos motores distintos:

- Historico es una lectura observada y agregada del mercado. Responde a que zonas y categorias han funcionado mejor o peor en Madrid.
- Oportunidades es una lectura puntual y decisional. Responde a si una ubicacion concreta parece favorable hoy y para que actividades.

El problema no es que Oportunidades use datos historicos. Eso es correcto y necesario. El problema es que esos datos historicos no estan jerarquizados como evidencia de soporte, sino que conviven demasiado cerca del lenguaje y de la visualidad de la capa predictiva. El usuario ve dos vistas casi hermanas, con gramatica visual parecida, el mismo horizonte temporal, metricas con nombres parecidos y el mismo patron de explicadores. La arquitectura ya separa; la interfaz todavia no remata la separacion.

Mi conclusion principal es esta:

- No retiraria el historico de Oportunidades.
- No me quedaria tampoco con la estructura actual tal cual.
- Recomiendo evolucionar el producto a una entrada por intencion de uso y dos vistas mucho mas asimetricas, con una narrativa clara de Mercado frente a Decision.

La estructura final recomendada no es simplemente Historico vs Oportunidades como dos tabs equivalentes. La recomendacion es:

1. Introducir una capa de entrada o onboarding que haga elegir entre entender el mercado o evaluar una ubicacion.
2. Mantener dos vistas nucleares, pero redisenadas como productos casi distintos.
3. Reforzar Historico como observatorio territorial y sectorial.
4. Reforzar Oportunidades como mesa de decision puntual, con el historico claramente etiquetado como contexto observado y no como protagonista.

Si se quiere una version final mas solida y con mayor personalidad, el proyecto deberia dejar de parecer dos pestañas de un mismo mapa y empezar a parecer dos instrumentos distintos que comparten una base analitica.

---

## 1. Estado actual de cada vista

| Eje | Historico | Oportunidades |
| --- | --- | --- |
| Pregunta principal | Que ha pasado en el mercado | Que conviene hacer en un punto concreto |
| Unidad de analisis | Hexagono H3 + categoria | Local listado o punto libre + seccion censal |
| Tipo de verdad | Observada y agregada | Predictiva, contextual y decisional |
| Datos dominantes | Supervivencia, riesgo relativo, ranking zonal, composicion por categorias | Riesgo contextual, supervivencia esperada, ranking de actividades, contexto demografico y urbano |
| Patron de uso | Exploracion territorial | Evaluacion puntual |
| Interaccion principal | Elegir categoria y leer el mapa | Elegir punto y decidir |

### Lo que hace hoy Historico

Historico se comporta como un mapa de supervivencia comercial agregado. El usuario selecciona una categoria y examina hexagonos coloreados por supervivencia y riesgo relativo. El lateral complementa la lectura con ranking del hexagono, comparacion frente a la media y zonas destacadas.

Esta vista responde bien a preguntas como:

- Donde aguanta mejor una categoria.
- Que barrios y distritos salen mejor para una actividad.
- Como se reparte una mezcla comercial dentro de un hexagono.

La lectura dominante es observada. Incluso cuando aparece un score de riesgo, ese score esta subordinado a un mapa de comportamiento historico agregado.

### Lo que hace hoy Oportunidades

Oportunidades se comporta como una ficha de decision sobre ubicaciones. El usuario selecciona un local real o marca un punto libre, y el sistema responde con supervivencia esperada, ranking territorial, ranking de actividades recomendadas y contexto de renta, demografia, metro, competencia, avisos, vulnerabilidad y otros factores.

Esta vista responde bien a preguntas como:

- Si esta ubicacion parece fuerte o fragil.
- Que actividad tiene mejor encaje en este entorno.
- Que factores del barrio o de la seccion estan empujando la lectura.

La lectura dominante es predictiva. Sin embargo, muchas de sus metricas salen de historico observado o de contexto urbano, y eso no siempre esta comunicado con suficiente jerarquia.

---

## 2. Donde la separacion actual funciona bien

La separacion actual funciona mejor de lo que parece a primera vista. Hay varios aciertos claros.

### 2.1 La unidad de analisis ya esta bien separada

Historico trabaja con territorio agregado y Oportunidades con ubicacion puntual. Esa diferencia es correcta y no deberia perderse.

### 2.2 El motor de recomendacion de Oportunidades ya es distinto

Oportunidades no es un espejo del mapa historico. Tiene su propia logica: locales disponibles, seleccion manual, ranking de actividades, benchmarking territorial y lectura contextual. No es una simple vista mas del mismo artefacto.

### 2.3 El producto ya sabe que el punto se interpreta contra la seccion censal

La aclaracion de que la ficha se lee contra la seccion censal contenedora es una decision correcta. Sin ella, Oportunidades pareceria una prediccion imposible sobre una direccion individual.

### 2.4 El historico ya tiene potencial para ser un observatorio, no solo un mapa

Entre los artefactos, la taxonomia, los agregados zonales y los datos de composicion, Historico ya tiene base suficiente para evolucionar a una herramienta de inteligencia territorial bastante mas rica que el estado actual.

---

## 3. Donde se rompe hoy la separacion

La confusion actual no viene de una sola decision. Viene de varias capas acumuladas.

### 3.1 La navegacion las presenta como hermanas simetricas

El producto actual sugiere que ambas vistas son dos versiones equivalentes de una misma cosa. Esto empobrece la narrativa. No lo son.

Historico es una lente de exploracion de mercado.
Oportunidades es una lente de decision.

Si la interfaz las coloca como dos tabs planas y simetricas, el usuario entra en ambas esperando el mismo tipo de respuesta.

### 3.2 Ambas reutilizan demasiado la misma gramatica visual

Comparten sidebar, tarjeta de estadisticas, metricas clicables, banners explicativos y jerarquia visual muy parecida. El usuario cambia de vista, pero no siente que haya cambiado de instrumento.

### 3.3 El horizonte temporal se repite con semanticas distintas

El selector 12m y 24m aparece en ambas pantallas, pero no significa exactamente lo mismo.

- En Historico habla de continuidad observada de locales comparables.
- En Oportunidades habla de supervivencia esperada o de contexto usado en un ranking.

Ese paralelismo visual favorece una lectura falsa de equivalencia.

### 3.4 El termino supervivencia esta sobrecargado

Esta es la confusion mas importante.

Hoy un usuario puede leer supervivencia en Historico y en Oportunidades y asumir que es la misma magnitud. No lo es.

- En Historico, supervivencia es observacion agregada de lo que ha pasado.
- En Oportunidades, supervivencia es una traduccion del score de riesgo a una probabilidad esperada para un entorno.
- Dentro del ranking de actividades de Oportunidades, vuelve a aparecer supervivencia, pero como referencia historica de soporte.

Sin etiquetas como observado, esperado o soporte historico, se mezclan tres cosas distintas bajo la misma palabra.

### 3.5 Oportunidades mezcla bien los datos, pero no siempre los ordena bien

Oportunidades tiene razon al mezclar:

- prediccion del modelo,
- contexto demografico,
- senales urbanas,
- evidencia historica de categorias,
- mercado actual de listings.

El problema no es la mezcla. El problema es que al usuario no siempre le queda claro que papel juega cada capa.

### 3.6 El framing interno del proyecto no siempre acompaña

Hay senales de deriva de lenguaje interno. Por ejemplo, el builder historico todavia habla de regiones de prediccion en su subtitulo, cuando esa vista se usa de facto como lectura historica agregada. Eso alimenta la ambiguedad conceptual.

---

## 4. Decision de producto: que hacer con el historico dentro de Oportunidades

### Veredicto

No retiraria el historico de Oportunidades.

Seria un error. La recomendacion de actividad, la lectura de riesgo contextual y buena parte del valor del producto dependen precisamente de usar historico observado y contexto territorial para informar una decision puntual.

Lo que si cambiaria es el contrato semantico de esa informacion.

### Regla de oro recomendada

En Oportunidades, toda metrica debe pertenecer con claridad a una de estas tres familias:

1. Decision: lo que el producto cree o recomienda para este punto.
2. Contexto observado: lo que sabemos del entorno por historico o por datos urbanos.
3. Mercado actual: lo que sabemos del listing en venta o alquiler.

Si una tarjeta no deja claro a cual de estas familias pertenece, hay riesgo de confusion.

### Traduccion practica

En la vista final recomendada:

- La capa principal de Oportunidades debe ser decisional.
- El contexto historico debe quedar claramente etiquetado como evidencia observada.
- El listing debe quedar claramente etiquetado como mercado actual.

No hay que vaciar Oportunidades de historico; hay que poner cada pieza en su sitio.

---

## 5. No aferrarse a la estructura actual: arquitecturas posibles

He considerado cuatro arquitecturas realistas. No todas valen lo mismo.

### Opcion A. Mantener dos vistas y solo mejorar copy y etiquetas

#### Que seria

Seguir con Historico y Oportunidades como tabs equivalentes, pero afinando nomenclatura, microcopy y algunos labels de metricas.

#### Ventajas

- Bajo riesgo.
- Poco esfuerzo.
- Se puede ejecutar rapido.

#### Riesgos

- Corrige sintomas, no corrige del todo la sensacion de simetria.
- El producto seguiria pareciendo dos versiones del mismo mapa.

#### Mi valoracion

Insuficiente para una version final fuerte. Es una mejora buena, pero demasiado conservadora.

### Opcion B. Mantener dos vistas nucleares, pero con entrada por intencion y mucha mas asimetria

#### Que seria

No arrancar ya con dos tabs iguales. Arrancar con una entrada tipo:

- Entender el mercado.
- Evaluar una ubicacion.

Desde ahi, conducir al usuario a dos vistas que compartan base de datos, pero no look and feel.

#### Ventajas

- Mantiene claridad de producto.
- Cambia el marco mental desde el inicio.
- Permite seguir teniendo solo dos modos principales.
- Evita sobrecargar al usuario con una tercera vista si no hace falta.

#### Riesgos

- Requiere redisenar la navegacion y dejar de pensar en tabs simetricas.
- Obliga a aceptar que ambas vistas no deben parecerse tanto.

#### Mi valoracion

Es la opcion recomendada.

### Opcion C. Pasar a tres vistas: Tendencias, Dinamica y Oportunidades

#### Que seria

Separar el actual Historico en dos productos:

- Tendencias: supervivencia, riesgo relativo y fortaleza zonal.
- Dinamica: entradas, salidas, rotacion, cohortes, ganadores y perdedores.
- Oportunidades: decision puntual.

#### Ventajas

- Distincion conceptual muy fuerte.
- Hace visible una dimension temporal y de mercado que hoy esta escondida.

#### Riesgos

- Puede fragmentar demasiado la experiencia.
- Exige mas esfuerzo explicativo.
- Puede penalizar a usuarios que solo quieren una lectura rapida.

#### Mi valoracion

Es atractiva, pero la reservaria para una segunda gran evolucion. No la pondria como primera jugada si el objetivo es cerrar una version final consistente y legible.

### Opcion D. Workspace unico con caminos por tarea

#### Que seria

Eliminar la division rigida en tabs y construir un espacio de trabajo por preguntas: comparar zonas, analizar punto, entender categoria, revisar dinamica, etc.

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

Mi recomendacion es la Opcion B.

No me aferro a la estructura actual, pero tampoco romperia el producto por completo. La version final mas valida me parece esta:

1. Una entrada por intencion de uso.
2. Dos vistas nucleares bien diferenciadas.
3. Historico reforzado como observatorio de mercado.
4. Oportunidades reforzada como instrumento de decision.
5. Dinamica temporal incorporada como capa o modo dentro de Historico, no como tercer producto de primer nivel.

---

## 6. Nomenclatura y narrativa recomendadas

No usaria Historico y Oportunidades como nombres protagonistas en la version final. Son funcionales internamente, pero debiles para producto.

### Propuesta recomendada

#### Pantalla de entrada

- Entender el mercado
- Evaluar una ubicacion

#### Vista 1

Nombre sugerido: Mercado

Subtitulo sugerido: Donde funciona cada tipo de actividad y como cambia el tejido comercial.

#### Vista 2

Nombre sugerido: Decision

Subtitulo sugerido: Que encaje tiene esta ubicacion hoy y que actividades parten con mejor lectura.

### Por que esta nomenclatura es mejor

- Mercado explica exploracion agregada mejor que Historico.
- Decision explica accion puntual mejor que Oportunidades.
- El usuario entiende enseguida que una vista sirve para aprender y la otra para decidir.

---

## 7. Como haria las dos vistas mucho mas distintas

### 7.1 Vista Mercado

La convertiria en un observatorio territorial. No solo un mapa H3 con una ficha lateral.

#### Su nucleo deberia ser

- mapa principal de fortaleza o supervivencia observada,
- selector de categoria,
- lectura zonal clara,
- capas opcionales de dinamica,
- contexto urbano y comercial de apoyo.

#### Lo que cambiaria

1. Mantener H3 como capa base, pero permitir cambiar de modo entre fortaleza, rotacion y concentracion comercial.
2. Dar mas protagonismo a distrito y barrio como unidades de interpretacion, no solo al hexagono.
3. Convertir la ficha lateral en un panel de observacion de mercado, no solo en una tarjeta del hexagono seleccionado.
4. Reservar el lenguaje de probabilidad o decision para Oportunidades. Aqui todo deberia hablar de observado, agregado, historico o estructura territorial.

### 7.2 Vista Decision

La convertiria en una mesa de analisis puntual. Menos mapa de exploracion y mas tablero de juicio.

#### Su nucleo deberia ser

- seleccion de punto o listing,
- lectura principal de riesgo y encaje,
- descomposicion del porque,
- comparacion con el mercado,
- ranking de actividades como recomendacion final.

#### Lo que cambiaria

1. El mapa dejaria de ser un protagonista equivalente al de Mercado. Seria un selector espacial para abrir la ficha correcta.
2. El lateral se dividiria en tres bloques muy marcados: mercado actual del local, decision del modelo, contexto observado del entorno.
3. El ranking de actividades dejaria de parecer una lista mas y pasaria a ser una conclusion de decision.
4. El lenguaje de Oportunidades deberia hablar de esperado, encaje, soporte historico y benchmark, no de comportamiento agregado del mercado en abstracto.

---

## 8. Visualizaciones nuevas recomendadas

Las siguientes ideas no son fantasias. Se apoyan en datos ya existentes en el repo o muy proximos a los builders actuales.

### 8.1 Visualizaciones para Mercado

| Idea | Pregunta que responde | Datos ya disponibles | Viabilidad | Impacto |
| --- | --- | --- | --- | --- |
| Heatmap de rotacion 12m | Donde el tejido comercial cambia mas | `section_turnover_rate_12m_start`, entradas y salidas | Alta | Alta |
| Indicador de concentracion comercial | La zona esta muy concentrada o es diversa | HHI y shares comerciales del ABT | Alta | Media-alta |
| Ganadores y perdedores por barrio | Que categorias estan entrando o saliendo | flujos por categoria y zona | Media | Alta |
| Cohortes de entrada y mortalidad | Que paso con los locales que entraron en distintos periodos | cohortes del ABT y supervivencia historica | Media | Media-alta |
| Overlay de equipamientos urbanos | Que contexto urbano rodea la zona | mercados, colegios, parques, cultura, BiciMAD, metro | Media | Media |
| Indice de estabilidad vs dinamismo | La zona es segura, estable o volatil | turnover, net flow, concentracion, supervivencia | Media | Media |
| Barrios similares | Que otras zonas se parecen a esta | renta, densidad, edad, mix comercial, vulnerabilidad | Media | Baja-media |

#### Las dos que priorizaria primero

1. Heatmap de rotacion 12m.
2. Ganadores y perdedores por barrio.

Con esas dos piezas, Mercado deja de ser un mapa bonito de supervivencia y pasa a ser un observatorio de comportamiento comercial.

### 8.2 Visualizaciones para Decision

| Idea | Pregunta que responde | Datos ya disponibles | Viabilidad | Impacto |
| --- | --- | --- | --- | --- |
| Radar de drivers de riesgo | Que esta empujando la lectura del punto | score, features del modelo, contexto ya calculado | Media | Muy alta |
| Scatter de actividades: encaje vs soporte | Que actividad encaja bien y ademas tiene suficiente evidencia | top activities, support, survival, source zone | Alta | Muy alta |
| Histograma de percentiles | Donde cae este punto frente a Madrid, distrito y barrio | benchmark context ya calculado | Alta | Alta |
| Anillo de accesibilidad y dotacion | Como de accesible y servido esta el punto | metro, equipamientos por radio, BiciMAD | Media | Alta |
| Mapa de presion regulatoria | Hay senales de inspeccion o friccion en el entorno | inspecciones, avisos, top categorias | Media | Media |
| Matriz precio del local vs lectura del entorno | El anuncio parece caro, barato o razonable para esta lectura | price_eur, price_per_m2_eur, percentiles, tier | Alta | Alta |

#### Las dos que priorizaria primero

1. Radar de drivers de riesgo.
2. Scatter de actividades: encaje vs soporte.

Con esas dos piezas, Decision deja de ser solo una ficha larga y se convierte en una herramienta que explica y compara.

### 8.3 Lo que no haria

Hay ideas que parecen tentadoras pero debilitarian la separacion.

No haria estas tres cosas:

1. No pondria hexagonos historicos como capa principal dentro de Oportunidades.
2. No dejaria la misma escala cromatica y la misma jerarquia visual en ambas vistas.
3. No reutilizaria sin calificador palabras como supervivencia o ranking si la semantica cambia.

---

## 9. Propuesta de experiencia final

Si tuviera que definir una version final del producto con ambicion pero con cabeza, la experiencia seria esta.

### Paso 1. Pantalla de entrada

Dos tarjetas muy claras:

- Entender el mercado.
- Evaluar una ubicacion.

No es cosmetica. Es el momento en que el producto deja de presentar dos tabs equivalentes y se explica por intencion.

### Paso 2. Mercado

Un observatorio donde el usuario puede responder a cuatro tipos de pregunta:

- que zonas son fuertes para una categoria,
- que zonas estan cambiando,
- que categorias ganan o pierden en cada barrio,
- que contexto urbano y social acompaña a esa lectura.

### Paso 3. Decision

Una mesa donde el usuario puede responder a cuatro tipos de pregunta:

- esta ubicacion parece favorable o fragil,
- por que,
- que actividades encajan mejor,
- como se compara con su distrito, su barrio y Madrid.

### Paso 4. Conexion entre ambas vistas

La conexion no debe ser una simetria de tabs, sino una escalera de lectura.

- Desde Mercado puedes saltar a Decision si encuentras una zona prometedora y quieres evaluar un punto.
- Desde Decision puedes saltar a Mercado si quieres comprobar si la buena lectura del punto se sostiene en el tejido zonal.

Eso si une ambas vistas de forma inteligente.

---

## 10. Roadmap de producto recomendado

### Fase 0. Claridad semantica

Objetivo: eliminar la confusion mas peligrosa sin rehacer aun el frontend entero.

Acciones:

- etiquetar observado, esperado y soporte historico,
- renombrar vistas y subtitulos,
- redibujar la jerarquia interna de Oportunidades,
- limpiar el framing interno del builder historico.

### Fase 1. Rediseno de la entrada

Objetivo: dejar de arrancar con dos tabs equivalentes.

Acciones:

- pantalla de entrada por intencion,
- cards de navegacion a Mercado y Decision,
- persistencia suave del ultimo modo usado.

### Fase 2. Mercado como observatorio

Objetivo: convertir Historico en una herramienta mas profunda.

Acciones:

- modo de rotacion,
- ganadores y perdedores,
- capas de contexto urbano,
- cohortes o estabilidad si hay tiempo.

### Fase 3. Decision como mesa de juicio

Objetivo: convertir Oportunidades en un tablero de decision.

Acciones:

- radar de drivers,
- scatter de actividades,
- histograma de percentiles,
- matriz precio vs lectura,
- etiquetado fuerte de mercado actual frente a contexto observado.

### Fase 4. Endurecimiento

Objetivo: preparar la version final del proyecto para crecer con seguridad.

Acciones:

- mejorar contratos de artefactos,
- añadir pruebas frontend,
- automatizar checks y build,
- preparar estrategia de cache y payload.

---

## 11. Mejoras sugeridas para hacer el proyecto mas solido

Esta seccion va mas alla del binomio Historico/Oportunidades. Aqui el foco es la solidez general del proyecto.

### 11.1 Navegacion y framing de producto

#### Problema actual

La navegacion actual presenta dos vistas como si fuesen equivalentes, cuando responden a tareas distintas.

#### Evidencia

- `front/components/view-tabs.tsx`
- `front/components/map-shell.tsx`
- `front/components/opportunity-shell.tsx`

#### Viabilidad

Alta. Es un cambio de frontend y copy, no de pipeline.

#### Impacto

Muy alto. Es la mejora con mejor retorno sobre esfuerzo para claridad de producto.

#### Recomendacion

Cambiar tabs simetricas por entrada por intencion y vistas mas asimetricas.

### 11.2 Diferenciacion visual radical entre Mercado y Decision

#### Problema actual

Ambas vistas comparten demasiada gramatica visual: lateral, cards, banners, tonos y patron de lectura.

#### Evidencia

- `front/components/map-shell.tsx`
- `front/components/opportunity-shell.tsx`
- `front/components/madrid-map.tsx`
- `front/components/opportunity-map.tsx`

#### Viabilidad

Media. No es dificil tecnicamente, pero requiere criterio de diseno y no solo cambios cosmeticos.

#### Impacto

Muy alto. El usuario necesita sentir que ha cambiado de instrumento, no solo de tab.

#### Recomendacion

Dar a Mercado una visualidad mas cartografica y a Decision una visualidad mas analitica y puntual.

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

Separar estado, builders de metricas, explicadores y componentes visuales en capas mas pequenas y testeables.

### 11.4 Pruebas frontend e interaccion

#### Problema actual

El proyecto tiene una base Python bien cubierta con `unittest`, pero el frontend no expone hoy una suite visible de pruebas de componentes o interaccion.

#### Evidencia

- `back/tests/` contiene bateria Python amplia
- `front/package.json` no muestra scripts de test frontend
- no hay archivos `*.test.tsx` visibles en `front`

#### Viabilidad

Alta. Se puede arrancar por componentes criticos y rutas principales.

#### Impacto

Alto. Reduciria regresiones en UX, especialmente en banners, overlays, hover panels y explicadores.

#### Recomendacion

Introducir pruebas de componentes y al menos un smoke test de navegacion Mercado/Decision.

### 11.5 CI y checks automaticos

#### Problema actual

No hay una pipeline visible de CI en el repo para ejecutar automaticamente tests Python, typecheck web y build de Next.

#### Evidencia

- no hay `.github/workflows` visible
- `front/package.json`
- `back/tests/`

#### Viabilidad

Alta. El proyecto ya tiene comandos claros para validar Python y web.

#### Impacto

Muy alto. Es clave para cerrar una version final con mas seguridad.

#### Recomendacion

Montar una CI minima con tres checks: unit tests Python, `tsc --noEmit` y `npm run build` en `front`.

### 11.6 Validacion runtime de artefactos frontend

#### Problema actual

El frontend tipa los artefactos en TypeScript, pero no hace validacion runtime al cargar JSON grandes desde `public/data`.

#### Evidencia

- `front/lib/types.ts`
- `front/lib/public-data.ts`

#### Viabilidad

Alta. Se puede introducir un validador ligero sin cambiar el pipeline de fondo.

#### Impacto

Alto. Ayudaria a detectar roturas de schema, nulos inesperados o cambios de artefacto antes de que se conviertan en bugs opacos.

#### Recomendacion

Incorporar validacion runtime de metadatos y campos criticos en la carga de artefactos.

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

Anadir metadata uniforme de version de build, origen de datos y parametros, y usar escritura atomica para JSON, GeoJSON y CSV criticos.

### 11.8 Auditoria explicita de soporte, fallback e imputacion

#### Problema actual

El proyecto ha avanzado mucho en soporte y semantica de nulos, pero sigue costando ver, desde producto o desde artefacto, cuando una lectura sale de soporte fuerte, fallback territorial o imputacion.

#### Evidencia

- `docs/project/project-overview.md`
- `back/scripts/build_frontend_map_artifacts.py`
- `back/scripts/build_frontend_opportunity_artifacts.py`
- memorias del repo sobre `frontend_map_artifact_semantics` y `opportunity_artifact_semantics`

#### Viabilidad

Media-alta. Gran parte del trabajo es serializar mejor y exponer mas claramente flags ya existentes.

#### Impacto

Muy alto. Esta mejora sube la credibilidad del producto y evita malas lecturas sobre evidencia debil.

#### Recomendacion

Exponer mas claramente si una metrica viene de soporte directo, fallback distrital o lectura ciudad, y estandarizar esa semantica entre Mercado y Decision.

### 11.9 Reconciliacion offline frente a producto

#### Problema actual

El pipeline Python y el frontend estan bien conectados, pero falta una capa explicita de reconciliacion que garantice que lo servido al usuario coincide exactamente con la semantica calculada offline.

#### Evidencia

- builders de artefactos
- `front/lib/types.ts`
- `front/lib/public-data.ts`

#### Viabilidad

Media. Requiere tests de reconciliacion, no un rediseno completo.

#### Impacto

Alto. Reduce bugs silenciosos y hace mas robusta la auditoria de datos.

#### Recomendacion

Introducir tests de reconciliacion sobre una muestra fija de puntos y zonas entre outputs Python y lectura frontend.

### 11.10 Estrategia de payload y futura API ligera

#### Problema actual

El frontend ya descarga artefactos desde `public/data`, pero el crecimiento de campos, capas y visualizaciones puede empujar el payload a una zona incomoda.

#### Evidencia

- `front/lib/public-data.ts`
- `docs/project/project-overview.md` ya recoge la necesidad de seguir endureciendo la capa de artefactos y su mantenimiento operativo

#### Viabilidad

Media. No urge hoy, pero conviene disenar la transicion antes de que duela.

#### Impacto

Medio-alto. Evita que la siguiente evolucion de producto quede frenada por peso, cache o tiempo de parseo.

#### Recomendacion

Definir desde ya que partes deben seguir como artefacto estatico y que partes pasarian mejor a una API ligera bajo demanda si el proyecto crece.

### 11.11 Runbooks y documentacion operativa

#### Problema actual

`docs/project/project-overview.md` resume bien el contexto publico del proyecto, pero no sustituye del todo a runbooks operativos cortos para reconstruir artefactos, validar resultados y depurar fallos.

#### Evidencia

- `docs/project/project-overview.md`
- ausencia visible de runbooks dedicados en `docs/`

#### Viabilidad

Alta. Es sobre todo trabajo documental.

#### Impacto

Medio-alto. Mejora onboarding, continuidad y resiliencia del proyecto.

#### Recomendacion

Anadir runbooks cortos para reconstruccion de artefactos, chequeos de salud del frontend y procedimiento de validacion antes de publicar.

### 11.12 Lenguaje unificado entre producto, builders y docs

#### Problema actual

Hay pequenos desajustes de vocabulario entre docs, builders y frontend: prediccion, historico, supervivencia, riesgo relativo, riesgo contextual, soporte, ranking.

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

Definir un pequeno glosario de producto para Mercado y Decision y usarlo de forma coherente en builders, docs y frontend.

---

## 12. Priorizacion sugerida

### Prioridad 1

- Reencuadrar navegacion y narrativa.
- Diferenciar visualmente Mercado y Decision.
- Etiquetar de forma explicita observado, esperado y soporte historico.
- Introducir radar de drivers y scatter de actividades en Decision.
- Introducir modo de rotacion y ganadores/perdedores en Mercado.

### Prioridad 2

- Descomponer shells monoliticas.
- Anadir pruebas frontend.
- Montar CI minima.
- Endurecer contratos de artefactos y metadata.

### Prioridad 3

- Preparar runbooks.
- Definir estrategia futura de API ligera.
- Explorar barrio similares, cohortes y estabilidad compuesta si aportan valor real tras la fase 1.

---

## 13. Conclusiones finales

La pregunta correcta no es si Oportunidades tiene demasiado historico. La pregunta correcta es si el historico dentro de Oportunidades esta jugando el papel correcto.

Mi respuesta es que hoy no del todo.

No porque sobren datos, sino porque falta una jerarquia mas clara entre:

- lo que el producto observa,
- lo que el producto estima,
- y lo que el mercado actual ofrece.

La version final mas valida de Localízate no deberia ser un frontend con dos tabs parecidas. Deberia ser un sistema con dos modos de pensamiento:

- Mercado para entender.
- Decision para actuar.

Los datos del repo ya permiten llegar bastante mas lejos de donde esta hoy el frontend. Hay base suficiente para construir una version final mas clara, mas distinta entre vistas, mas util para usuario real y tambien mas defendible como producto serio.

Si tuviera que resumir la recomendacion en una sola frase, seria esta:

Localízate no necesita menos historico en Oportunidades; necesita que el historico deje de parecer el protagonista equivocado y pase a ser la evidencia correcta dentro de una herramienta de decision mucho mas clara.
