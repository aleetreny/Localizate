# Diagnóstico de "Sin categoría" y "Actividad no informada"

Fecha: 2026-04-09

## 1. Resumen ejecutivo

### La conclusión corta

No he encontrado un error grande de nuestro pipeline que explique la masa principal de locales sin categoría.

El problema real no era una taxonomía rota, sino esto:

1. La fuente de actividad llega vacía o inútil para muchísimos locales.
2. Una parte menor tiene varias macrocategorías reales a la vez, así que no es correcto forzar una sola.
3. Una parte muy pequeña viene de estados de fuente como "sin actividad", "pendiente de codificar" o meses sin fichero.
4. Nuestro error principal estaba en cómo lo presentábamos: todo eso aparecía agrupado como "Sin categoría", lo que hacía pensar que el fallo era de clasificación cuando en realidad casi siempre era un problema de dato origen.

### Qué sí era error nuestro

Estos son los errores nuestros que sí he confirmado:

1. Error de semántica de producto: usábamos una única etiqueta, "Sin categoría", para mezclar causas muy distintas.
2. Error de UX: exponíamos en el selector estados residuales del dato que no aportaban valor como filtro principal.

### Qué no he encontrado

No he encontrado evidencia de:

1. Un bug masivo de join en el ABT.
2. Una fuga grande de la taxonomía para epígrafes válidos.
3. Una regla nuestra equivocada que, al arreglarla, recupere automáticamente la mayoría de esos locales.

### Recomendación final

1. Mantener "Actividad no informada" como estado explícito del dato.
2. No imputar una categoría de forma masiva con los datos actuales.
3. Seguir tratando "Multiactividad" como caso propio, no como error.
4. Mantener fuera del selector "Sin actividad declarada", "Mes sin fichero de actividad" y "Actividad pendiente de codificar", pero conservarlos en agregados y composición del mapa.
5. Si algún día queremos recuperar parte de este bloque, hacerlo solo como experimento offline con criterio de abstención fuerte y validación manual, no como corrección automática del pipeline actual.

---

## 2. Qué significaba realmente "Sin categoría"

### Universo completo

En el ABT actual:

1. Locales con categoría nula en total: 59.603
2. De esos, visibles en el mapa histórico: 47.421
3. Fuera del mapa histórico: 12.182

### Cómo queda descompuesto ahora en producto

En el mapa histórico visible, el antiguo bloque de "Sin categoría" quedó separado en estos estados:

| Estado | Locales visibles |
|---|---:|
| Actividad no informada | 44.237 |
| Multiactividad | 2.891 |
| Sin actividad declarada | 246 |
| Mes sin fichero de actividad | 40 |
| Actividad pendiente de codificar | 7 |

La suma es 47.421, que coincide con el total visible del antiguo bloque nulo.

### Qué significa cada estado

1. Actividad no informada: hay fila de actividad, pero no trae una actividad usable para asignar macro.
2. Multiactividad: el local arranca con varias macrocategorías reales al mismo tiempo.
3. Sin actividad declarada: la propia fuente dice que no hay actividad.
4. Mes sin fichero de actividad: falta el fichero mensual de origen.
5. Actividad pendiente de codificar: la fuente reconoce la actividad, pero aún no la codifica.

---

## 3. Qué errores eran nuestros y cuáles no

## 3.1 Error nuestro confirmado: mezclar causas distintas bajo una sola etiqueta

### Qué pasaba

Antes, todo lo que no tenía macrocategoría al inicio acababa viéndose como "Sin categoría".

### Por qué era un problema

Eso mezclaba en una misma bolsa:

1. Falta de información real.
2. Actividad múltiple real.
3. Locales sin actividad.
4. Huecos puntuales de fichero.

### Consecuencia

La lectura era engañosa: parecía un fallo de clasificación nuestro cuando en realidad la mayor parte del problema estaba en la fuente o en la propia naturaleza del local.

### Estado actual

Corregido.

---

## 3.2 Error nuestro confirmado: exponer ruido residual en el selector

### Qué pasaba

Estados muy pequeños como "Sin actividad declarada", "Mes sin fichero de actividad" y "Actividad pendiente de codificar" estaban visibles como filtros de primer nivel.

### Por qué era un problema

1. Ensuciaban el selector.
2. Daban la sensación de ser tipos de local comparables a una categoría comercial real.
3. No aportaban casi valor operativo como filtro aislado.

### Estado actual

Corregido.

Se ocultan del selector, pero se conservan en el artefacto y dentro de "Todos los locales" para no deformar agregados ni la composición por hexágono.

---

## 3.3 Lo que no parece error nuestro

### A. La masa principal no viene de una taxonomía rota

La auditoría sobre epígrafes válidos no mostró una fuga grande de cobertura de taxonomía.

Interpretación:

Cuando el epígrafe es válido, normalmente sí sabemos mapearlo.

### B. La masa principal tampoco parece venir de un join roto

No apareció evidencia de un bug masivo en el join entre ABT, normalización y taxonomía que explique decenas de miles de locales.

### C. Multiactividad no es un error

El caso de "Multiactividad" es una decisión correcta del pipeline: si un local arranca con varias macrocategorías reales, asignarle una sola a la fuerza sería inventar información.

---

## 4. Evidencia numérica clave

## 4.1 Tamaño real del problema en producto

En el artefacto histórico actual:

1. Total de locales visibles en "Todos los locales": 164.441
2. Total de hexágonos visibles: 9.767
3. Locales en "Actividad no informada": 44.237
4. Peso de "Actividad no informada": 26,9% del total visible
5. Hexágonos que contienen al menos algo de "Actividad no informada": 6.267

Esto último es importante: aunque no todos esos hexágonos dependan por completo de ese estado, sí significa que el bloque toca gran parte del mapa.

### Qué había dentro del bloque nulo original

Cuando se auditó el bloque nulo visible original de 47.421 locales, el subgrupo dominante era muy claro:

1. 43.926 locales tenían fila de actividad, pero sin código ni descripción útiles para mapear una macro.
2. 2.891 locales eran multiactividad real.
3. 40 locales dependían de meses sin fichero de actividad.
4. El resto era una cola pequeña de placeholders como "valor nulo en origen", "sin actividad" o "pendiente de codificar".

La lectura importante es esta:

1. El grueso del problema no era "tenemos el dato y lo mapeamos mal".
2. El grueso del problema era "la fuente no trae una actividad usable".

---

## 4.2 Qué pasa si quitamos por completo "Actividad no informada"

He medido el impacto exacto de eliminarla del mapa histórico entero:

1. Locales eliminados: 44.237
2. Porcentaje de locales eliminados: 26,9%
3. Hexágonos que desaparecerían por completo: 421
4. Porcentaje de hexágonos que desaparecerían: 4,31%
5. Hexágonos que permanecerían: 9.346
6. Distritos que perderían toda representación: 0
7. Barrios que perderían toda representación: 0

### Interpretación sencilla

Quitarla no vacía barrios ni distritos completos.

Pero sí recorta mucho el universo de locales y cambia la composición del agregado general.

Es decir:

1. Territorialmente el mapa aguanta.
2. Analíticamente el agregado "Todos los locales" cambia bastante.
3. Además, aunque solo desaparezcan 421 hexágonos completos, 6.267 hexágonos contienen parte de este bloque, así que el impacto visual y estadístico se notaría mucho más allá de esos 421.

---

## 4.3 Qué dice la historia completa del local

Quería ver si el problema se podía arreglar mirando toda la historia del local, no solo su primer mes visible.

Resultado de la auditoría sobre los 47.421 locales visibles del antiguo bloque nulo:

1. Locales que nunca muestran una macro válida en toda su historia: 43.984
2. Locales que alguna vez muestran exactamente una sola macro en toda su historia: 0
3. Locales que muestran varias macros a lo largo de su historia: 3.437

### Interpretación sencilla

Esta es una de las conclusiones más fuertes de toda la auditoría.

Si miramos toda la historia del local:

1. La gran mayoría nunca ofrece una macro limpia que nos permita rescatar la categoría.
2. El resto no converge a una sola categoría, sino a varias.
3. No aparece un subconjunto grande de "locales recuperables por historial".

Esto deja muy tocada cualquier solución basada en "usa la categoría de antes o de después" como arreglo general del pipeline.

---

## 4.4 Qué dice el rótulo del local

También se evaluó si el rótulo podía ayudarnos a imputar una categoría.

Resultados exactos sobre los 44.237 locales actuales en "Actividad no informada":

1. Con rótulo no vacío: 37.965
2. Sin rótulo: 6.272
3. Con rótulo no-placeholder realmente útil: 0

### El dato decisivo

Cuando se normaliza ese rótulo, el valor dominante y prácticamente único es:

1. "sin actividad"

Es decir:

1. El rótulo no está trayendo un nombre comercial útil.
2. Está trayendo otro placeholder de la propia fuente.
3. Con el dato actual, el rótulo no sirve como señal de clasificación para este bloque.

### Conclusión de esta parte

No hay base real para una imputación seria apoyada en rótulo, al menos en el primer periodo visible y con el dato que hoy estamos materializando.

---

## 5. Qué soluciones posibles hay

Para que se entienda fácil, uso esta escala de robustez:

1. Muy alta: solución fiable, poco riesgo, consecuencia controlada.
2. Alta: buena solución, con trade-offs claros.
3. Media: puede servir en un caso acotado, pero necesita validación fuerte.
4. Baja: demasiado frágil o demasiado especulativa para producción.

## 5.1 Solución A: mantener el estado explícito y separar mejor el dato del tipo de local

### Qué es

No inventar categoría. Mostrar que el problema es de dato o de naturaleza del local.

### Robustez

Muy alta.

### Ventajas

1. Es honesta.
2. No mete sesgo artificial en el producto.
3. No obliga a tocar el modelo.
4. Es coherente con la evidencia.

### Inconvenientes

1. Sigues teniendo un bloque grande sin categoría comercial.
2. Al usuario le obliga a aceptar que no todo se puede clasificar con la fuente actual.

### Mi valoración

Es la mejor solución base para el estado actual del proyecto.

---

## 5.2 Solución B: esconder estados residuales pequeños del selector

### Qué es

Quitar del selector:

1. Sin actividad declarada
2. Mes sin fichero de actividad
3. Actividad pendiente de codificar

pero mantenerlos dentro del artefacto y de "Todos los locales".

### Robustez

Muy alta.

### Ventajas

1. Limpia la UI.
2. No pierde información analítica.
3. No cambia el agregado global.

### Inconvenientes

Ninguno importante.

### Estado

Ya implementado.

---

## 5.3 Solución C: quitar "Actividad no informada" del selector, pero no del mapa general

### Qué es

No dejar que el usuario la elija como filtro principal, pero conservarla dentro de "Todos los locales" y de la composición de cada hexágono.

### Robustez

Alta.

### Ventajas

1. El selector se centra en categorías comerciales reales.
2. No destruye el agregado global.
3. Reduce ruido de producto.

### Inconvenientes

1. El usuario pierde la capacidad de inspeccionar ese bloque de forma directa.
2. Si queremos auditarlo visualmente, sería peor.

### Mi valoración

Es una decisión de producto razonable si se quiere máxima limpieza visual, pero yo no la tomaría todavía sin ofrecer una forma alternativa de ver ese estado.

---

## 5.4 Solución D: quitar "Actividad no informada" de todo el mapa

### Qué es

Eliminarla por completo del histórico.

### Robustez

Alta técnicamente, baja analíticamente.

### Consecuencias medidas

1. Se eliminan 44.237 locales.
2. Se elimina el 26,9% del universo visible.
3. Desaparecen 421 hexágonos.
4. No desaparece ningún distrito ni barrio completo.
5. El agregado "Todos los locales" cambia de forma material.

### Mi valoración

No lo recomiendo como solución por defecto.

No rompe la cobertura territorial, pero sí cambia demasiado el agregado y puede dar una imagen sesgada del mercado real visible en la fuente.

---

## 5.5 Solución E: imputación temporal usando la historia del local

### Qué es

Intentar recuperar la categoría mirando periodos anteriores o posteriores del mismo local.

### Robustez

Baja con el dato actual.

### Limitación práctica adicional

Aunque el builder del ABT trabaja con columnas de auditoría temporal durante su construcción, la materialización actual del CSV que consumimos para análisis y frontend no expone esas columnas como una solución enchufable inmediata.

Eso significa que, incluso si esta vía fuera prometedora, hoy no sería un parche rápido de producto: primero habría que volver a materializar y endurecer esa parte del pipeline.

### Por qué

La auditoría histórica completa mostró:

1. 43.984 nunca muestran una macro válida en toda su historia.
2. 3.437 muestran varias macros a lo largo de la historia.
3. 0 muestran una macro única histórica que permita rescate limpio.

### Conclusión

Con el dato actual, esta vía no resuelve el problema de forma robusta.

Puede sonar intuitiva, pero la evidencia va justo en contra.

---

## 5.6 Solución F: imputación usando rótulo

### Qué es

Usar el nombre comercial del local para inferir la categoría.

### Robustez

Muy baja con el dato actual materializado.

### Por qué

En este bloque:

1. 37.965 rótulos no están vacíos.
2. Pero todos son placeholders y no nombres comerciales útiles.
3. El valor dominante es "sin actividad".
4. Quedan 0 rótulos no-placeholder útiles en el primer periodo visible.

### Conclusión

Con la información actual, esta vía no es viable.

Si en el futuro consiguiéramos otro campo textual real de negocio, entonces sí merecería la pena revisarla.

---

## 5.7 Solución G: enriquecimiento externo o revisión manual de un subconjunto

### Qué es

Intentar rescatar una parte del bloque con datos que hoy no están en el pipeline principal:

1. Rótulos reales de otra fuente
2. Directorios externos
3. Geocodificación y POIs externos
4. Revisión manual de una muestra o de un subconjunto prioritario

### Robustez

Media, pero cara.

### Ventajas

1. Puede rescatar un subconjunto real.
2. Permite trabajar con alta precisión si se hace con criterio estricto.

### Inconvenientes

1. Requiere fuente nueva o proceso manual.
2. No es una corrección rápida del pipeline actual.
3. Si se integra en el ABT, habría que volver a medir impacto en modelado y probablemente reentrenar si cambia `activity_category_code_start`.

### Mi valoración

Es la única vía que veo razonable para recuperar algo de este bloque, pero como proyecto aparte, no como bugfix.

---

## 6. Qué nos dice la literatura y cómo aplicaría aquí

No hace falta complicarlo mucho. La literatura relevante converge en tres ideas muy simples:

## 6.1 Si las señales son ruidosas, no etiquetes a mano todo ni fuerces reglas débiles

Trabajos como Snorkel plantean combinar reglas o señales débiles y modelar su ruido, en vez de tratar cada heurística como verdad absoluta.

### Traducción práctica para este proyecto

Si alguna vez hacemos un experimento de imputación, no debería ser:

1. "si aparece tal palabra, asigna esta categoría a todo"

sino algo como:

1. varias reglas débiles
2. varias señales externas
3. una capa de consenso
4. validación manual

Con el dato actual, ni siquiera tenemos señales suficientemente buenas para arrancar ese esquema a escala.

---

## 6.2 Si la confianza es baja, lo correcto es abstenerse

La idea de selective classification o reject option es muy útil aquí: un modelo no tiene por qué predecir siempre; puede decir "no sé" cuando la confianza no alcanza un umbral seguro.

### Traducción práctica para este proyecto

Si algún día imputamos, la regla buena no sería:

1. clasificar el 100%

sino:

1. clasificar solo el subconjunto con confianza muy alta
2. dejar el resto como no clasificado

Ese enfoque sí sería compatible con un proyecto serio.

---

## 6.3 Para texto corto, primero van los modelos simples

Trabajos como fastText muestran que para texto corto y ruidoso conviene empezar por baselines simples, baratos y fáciles de auditar.

### Traducción práctica para este proyecto

Si tuviéramos un rótulo real de negocio útil:

1. primero probaría un baseline simple de texto corto
2. mediría precisión-cobertura
3. pondría umbral de abstención
4. solo después pensaría en algo más complejo

Pero hoy ese rótulo útil no existe en este bloque.

---

## 7. Qué haría un científico de datos experimentado aquí

Si el objetivo del proyecto es producto fiable y señal defendible, yo haría esto:

## 7.1 Lo que haría ya

1. Mantener la semántica nueva que separa estados del dato.
2. Mantener ocultos del selector los tres estados pequeños ya corregidos.
3. Mantener "Actividad no informada" explícita.
4. Considerar separar visualmente "Categorías comerciales" de "Estados del dato".

---

## 7.2 Lo que no haría ahora

1. No imputaría masivamente categorías en el ABT actual.
2. No tocaría el modelo por esta vía.
3. No vendería al usuario una categoría inventada como si fuera fiable.

---

## 7.3 Lo que sí abriría como experimento futuro, si negocio lo pide

Un proyecto aparte y muy acotado:

1. Elegir un subconjunto prioritario.
2. Conseguir señales externas nuevas o mejores nombres comerciales.
3. Hacer una muestra manual etiquetada.
4. Probar reglas débiles y un clasificador con abstención.
5. Exigir precisión muy alta antes de aceptar ninguna imputación.

### Umbral razonable

Para usarlo en producto, yo pediría una precisión muy alta en el subconjunto aceptado, no una accuracy media bonita sobre todo el universo.

En este problema, la métrica importante es:

1. cuántos casos recupero con confianza alta
2. cuántos errores introduzco al hacerlo

---

## 8. Recomendación final

### Recomendación principal

La mejor decisión para el estado actual del proyecto es esta:

1. Tratar el problema como un problema de calidad y semántica del dato, no como un bug masivo de taxonomía.
2. Mantener "Actividad no informada" explícita.
3. No imputar categoría automáticamente con los datos actuales.
4. No quitar ese bloque de todo el mapa salvo que producto acepte alterar el agregado global.

### Recomendación de producto

La interfaz ideal sería:

1. Categorías comerciales reales por un lado
2. Estados del dato por otro lado

De esa forma el usuario entiende mejor qué está viendo.

### Recomendación técnica

No reentrenaría nada por esto ahora mismo.

Primero haría, si de verdad interesa, un experimento offline pequeño y muy disciplinado. Solo si demuestra recuperación robusta y útil, entonces tendría sentido plantear cambios en el ABT o en el modelo.

---

## 9. Decisión recomendada en una línea

No hay evidencia de un error nuestro grande que explique el bloque masivo de no categoría; la decisión correcta hoy es dejarlo explícito como problema de dato, no inventar categorías, y solo explorar recuperación futura en un experimento offline con validación fuerte.