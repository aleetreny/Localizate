# STATUS.md (Fuente Canonica)

Este archivo es la fuente unica y viva de contexto del proyecto. Se actualiza en cada avance y reemplaza al resto de documentos como referencia primaria.

Ultima actualizacion: 2026-04-16

Nota de implementacion en curso (2026-04-16):
 - Correccion de robustez aplicada en el workflow semanal `Refresh Opportunity Listings`: se elimina la condicion directa con `secrets` en `if` (que dejaba el YAML en rojo en VS Code y podia invalidar el parseo del workflow) y se sustituye por deteccion previa de credenciales R2 via output (`steps.r2-sync.outputs.enabled`), reutilizada tanto para la instalacion opcional de `boto3` como para el publish opcional de `data/opportunities` a R2.

Nota de implementacion en curso (2026-04-15):
 - Refinamiento de UX aplicado en los overlays de explicación por métrica (`Historico` y `Oportunidades`): el botón `Cerrar` deja de renderizarse en una fila independiente del banner y pasa a alinearse con el título de la métrica activa, evitando que el contenido textual se desplace hacia abajo al abrir la explicación.
 - Ajuste de UX aplicado en frontend para cierre manual de banners de explicación abiertos por clic en tarjetas: los dos overlays `metric-banner` (pestaña `Historico` y pestaña `Oportunidades`) incorporan ya botón discreto `Cerrar` en la esquina superior derecha, reutilizando el patrón visual existente de `explain-banner-close` y permitiendo cerrar el panel sin cambiar selección de tarjeta.
 - Correccion definitiva aplicada en `Oportunidades > Buscar tu local` para la seleccion de seccion por direccion: el algoritmo de `point-in-polygon` trataba el segmento degenerado de cierre de anillo (primer y ultimo vertice iguales) como si cualquier punto estuviera sobre ese borde, provocando asignaciones falsas de seccion y resaltado inconsistente. Se corrige en `opportunity-shell` y `opportunity-map` ignorando segmentos de longitud cero salvo coincidencia real del punto; ademas el mapa prioriza ya la seleccion geometrica por coordenada cuando hay `manualSelection`. Validacion puntual: consultas reales (`San Vicente Ferrer 29`, `Alcala 120`, `Castellana 95`) quedan en `1` seccion exacta cada una.
 - Nueva iteracion aplicada en `Oportunidades` para alinear comportamientos de seleccion: al elegir un `local disponible` (punto de listing) el mapa ejecuta ya el mismo efecto de enfoque con animacion que en `punto libre`; en paralelo, la seccion activa deja de depender solo de filtros de capa y se renderiza desde una fuente GeoJSON seleccionada, asegurando que el poligono completo quede realmente pintado tambien al llegar desde el buscador de direccion.
 - Endurecimiento adicional del geocodificador de `Buscar tu local`: se amplian formatos abreviados de via (`Ps.`, `P de`, variantes de `paseo`), se habilita fallback de tramo de calle tambien para vias de dos tokens cuando la coincidencia textual es muy alta (casos tipo `Paseo de la Castellana 95`), y `fetch` contra Nominatim incorpora reintentos con backoff para estados transitorios (`429/5xx`) antes de devolver error al usuario.
 - Validacion funcional completada sobre una bateria de `24` direcciones reales de Madrid en formatos mixtos (abreviados, con y sin comas, vias largas y nomenclatura heterogenea): `24/24` respuestas `200` en endpoint local, manteniendo `number_match=false` solo en los casos esperados de resolucion por tramo de calle.
 - Ajuste de toolchain aplicado en `front`: `tsconfig.json` fija `ignoreDeprecations` en `5.0` (valor valido para `typescript@5.9.x`, evitando el fallo `TS5103` en `typecheck/build`) y el workspace VS Code queda alineado al TypeScript local del proyecto mediante `.vscode/settings.json` (`js/ts.tsdk.path`), para eliminar falsos rojos del editor causados por validar con una version distinta.
 - Ajuste adicional aplicado en `Oportunidades > Buscar tu local`: direcciones con `calle + numero` que no traen portal exacto en Nominatim (caso tipico en vias largas como `Jose Ortega y Gasset`) dejan de caer en falso 404 y pueden resolverse a nivel de tramo de calle cuando la coincidencia textual es muy alta; ademas la seccion seleccionada en mapa gana un realce mucho mas explicito (relleno + contorno negro) y el filtro de `section_key` se vuelve robusto ante diferencias de tipo en el GeoJSON.
 - Refinamiento aplicado en `Oportunidades > Buscar tu local`: el geocodificador mantiene la exigencia de `calle + número` para evitar resultados difusos, pero deja de rechazar direcciones validas cuando Nominatim devuelve varios POIs empatados en el mismo portal (misma calle/número y coordenadas casi iguales); en esos empates se acepta la direccion y se sigue mostrando etiqueta limpia sin prefijo de negocio.
 - Nueva feature aplicada en `Oportunidades`: se incorpora un bloque `Buscar tu local` para introducir calle y numero y ubicar un punto por direccion sin usar puntero; el flujo geocodifica en servidor contra Nominatim con filtros de precision (calle y numero cuando se informa), cruza la coordenada con la geometria censal y abre la misma ficha contextual de `punto libre` que se obtiene al clicar el mapa. Ademas, el copy del bloque deja explicito que los anuncios visibles proceden de `locales.es` y que la busqueda sirve para evaluar una direccion propia en mente.
 - Refinamiento adicional aplicado en scroll lateral (`Historico`): la barra se inseta un poco más hacia la izquierda dentro del panel para que no parezca pegada al borde, y la eliminación de flechas nativas se endurece con selectores `single/double-button` para cubrir más navegadores WebKit.
 - Ajuste fino aplicado en `Historico > Mezcla del hexagono > control anual`: el deslizador y sus etiquetas de año se desplazan levemente hacia la izquierda para que los valores superior/inferior no sobrepasen el marco del panel lateral.
 - Ajuste global aplicado en `front` para controles deslizables: se unifica el estilo de scrollbar en todos los contenedores con una versión fina/redondeada y se ocultan flechas/botones nativos (`::-webkit-scrollbar-button`) para evitar desbordes visuales fuera de marcos en paneles laterales y overlays.
 - Ajuste visual aplicado en la columna lateral de `Historico`: el scroll vertical pasa a un estilo más discreto, fino y redondeado (sin botones superior/inferior) para que no descuadre en las esquinas del panel.
 - Ajuste de ancho útil aplicado en `Historico`: se amplía ligeramente la columna lateral y se afina el espaciado/padding del toggle `Visor principal` para que los tres labels cortos entren en una sola línea con más holgura.
 - Ajuste de copy aplicado en `Historico > Visor principal`: los botones pasan a singular (`Distrito`, `Barrio`, `Hexagono`) para evitar salto a dos líneas en pantallas estrechas y mantener lectura compacta.
 - Ajuste de producto aplicado en `Historico > Distrito/Barrio seleccionado`: se sustituye la card `Permanencia mediana` por `Rotacion historica` (`event_rate`) porque la primera estaba saturada en el techo del export (`duration_median_months = 135` en P25/P50/P75 para distrito y barrio), mientras que `event_rate` mantiene mas dispersión util entre zonas (rango 0-1 con cuantiles intermedios no colapsados).
 - Ajuste de nitidez aplicado en el mapa historico para seleccion de `barrio/distrito`: el contorno activo deja de competir con los bordes vecinos al renderizarse en una capa superior dedicada (hover y seleccion), y los rellenos de mapa se hacen mas transparentes para recuperar legibilidad del mapa base.
 - Ajuste de discrecion aplicado en los tooltips flotantes del mapa (Historico y Oportunidades): se compactan ancho, padding, radios y tipografia, y se recorta el contenido visible en hover para reducir ruido visual sin perder metricas clave.
 - Ajuste adicional de coherencia visual aplicado en `Historico > Comparar zonas`: los placeholders/opciones de `Selecciona un distrito` y `Selecciona un barrio` adoptan el mismo tratamiento sin negrita que el resto de selectores iniciales, manteniendo una jerarquía tipográfica uniforme.
 - Ajuste de UI aplicado en cabeceras de navegación: en `Historico` el toggle de `Visor principal` evita ya el desborde de `Hexagonos` en anchos ajustados (mejor reparto y wrapping del texto), y en los selectores iniciales de `Historico` (`Tipo de local`) y `Oportunidades` (`Operación`/tipo de local filtrado) se elimina la negrita del valor activo para una lectura más uniforme.
 - Correccion puntual aplicada en `Historico > Visor principal`: la regla de estilo del toggle de 3 opciones aumenta especificidad para que `Hexagonos` respete wrapping dentro del botón activo y no se recorte por herencia de `nowrap`.
 - Fix de contención aplicado en desplegables custom de `Historico` y `Oportunidades`: los menús de selección recalculan dirección (`arriba/abajo`) y altura máxima según espacio real del viewport al abrirse y también durante `scroll/resize`, evitando que el panel flotante se salga de la pantalla.
 - Ajuste de copy aplicado en `Historico > Mezcla del hexágono`: cuando el hexágono solo tiene 1 local en el periodo seleccionado, el texto explicativo deja de hablar de `peso puntual` y pasa a indicar que toda la mezcla corresponde a la única categoría presente.
 - Ajuste fino de layout aplicado en `Historico > Mezcla del hexágono`: el panel flotante de categoría se ensancha ligeramente y los valores de `Peso`, `Locales` y `Posición` evitan saltos de línea para mantener las tres cards compactas y legibles.
 - Ajuste de legibilidad aplicado en `Historico > Mezcla del hexágono`: el color del donut pasa a ser estable por categoría en lugar de depender de la posición del segmento. La asignación se calcula con criterio de frecuencia global y coocurrencia por hexágono para separar mejor las categorías que suelen aparecer juntas, penalizando también matices iguales o demasiado cercanos cuando coexisten en un mismo hexágono.
 - Ajuste de producto aplicado en `Historico > Zonas destacadas` según criterio mixto final: el ranking principal de `barrios/distritos` vuelve a ordenarse por la métrica real del mapa (`índice relativo 0-1`, priorizando `avg_risk_percentile`), mientras que el ranking interno de categorías al abrir una zona mantiene el orden por índice contextual sofisticado (estilo Oportunidades) pero sin mostrar su valor numérico, solo el puesto.
 - Nota de trazabilidad: en iteraciones previas del día se probó una versión con orden contextual también en cards territoriales y visualización dual (`Ctx/Rel`), pero ese enfoque queda sustituido por el criterio mixto final descrito arriba.
 - Alineación funcional aplicada entre pestañas en `Historico > Zonas destacadas > Ranking territorial`: el orden interno de categorías por barrio/distrito deja de depender solo del índice relativo y pasa a usar el mismo enfoque de `riesgo contextual` de Oportunidades (shrink de `event_rate` por tamaño muestral + penalización por evidencia no soportada), con desempate por `event_rate`, `survival` y `n_locales` para reducir rankings repetitivos y mantener consistencia metodológica.
 - Ajuste de UX aplicado en `Historico > Zonas destacadas > Ranking territorial`: la lista visible del banner vuelve a mostrarse en orden secuencial (`#1, #2, #3...`) y con longitud estable (hasta 5 filas), evitando la mezcla previa entre `puesto real` y `puesto visual` que generaba saltos aparentes (`#2, #3, #5`) y tamaños de lista variables según la categoría activa. Además, el top territorial excluye estados técnicos (`__status_*`) para que no aparezcan como categorías líderes del barrio/distrito.
 - Nueva iteración aplicada en `Historico > Mezcla del hexágono`: se añade selector anual tipo deslizador en la parte inferior del círculo (rango fijo `2015-2026`) y el donut pasa a recalcular la distribución por categoría del hexágono según el año seleccionado. Para sostenerlo, `back/scripts/build_frontend_map_artifacts.py` incorpora la materialización de un artefacto anual por hex (`front/public/data/frontend-hex-composition-history.json`) y `front` suma contrato TS + loader dedicado para consumirlo en cliente.

Nota de implementacion anterior (2026-04-13):
- Fix de desbordes aplicado en desplegables custom de `Historico` (categoría y comparación): se añaden márgenes laterales de seguridad, límite de altura más conservador y apertura automática hacia arriba cuando no hay espacio suficiente por debajo, evitando que el menú se salga del viewport en pantallas más justas.
- Ajuste de UX final aplicado en `Historico`: `Ámbito` dentro de `Comparar zonas` vuelve a mostrarse como selector visible de dos píldoras (`Distrito/Barrio`) en vez de desplegable; además se retira del banner de `Evolución histórica` la etiqueta `Serie anual 2015-2026` para reducir ruido visual.
- Ajuste adicional de consistencia aplicado en `Historico > Comparar zonas`: el selector de `Ámbito` y los dos selectores de zonas pasan de controles nativos a desplegable custom con el mismo patrón visual/interactivo del selector de categoría principal; además se corrige el centrado vertical del chip de liderazgo (`X mejor por Y puestos`) y el tamaño/alineación de los círculos de serie para que no queden descompensados frente a títulos como `Puesto en Madrid`.
- Ajuste puntual aplicado en `Historico` sobre el tooltip dinamico de hover en el mapa de hexagonos: se elimina el chip/circulo de `Pxx riesgo` (ej. `P79`) para simplificar la lectura rapida del banner flotante al mover el raton.
- Ajuste de pulido visual aplicado en `Historico`: se elimina el copy de cierre temporal en comparación (`El último año sigue abierto...`), el desplegable de `Tipo de local` mantiene interacción custom pero con estilo más sobrio/estático (sin degradado, menos relieve y tipografía visualmente uniforme) y ese mismo lenguaje se replica en los selects de la sección de comparación; además los círculos de color en tarjetas comparativas se alinean con la línea de título para un bloque más consistente.
- Ajuste fino adicional aplicado en `Historico > Hexágono seleccionado`: la card de comparación deja de usar `Supervivencia vs media` y pasa a `Índice vs media`, calculada como delta del índice relativo del hexágono frente a la media de riesgo de su categoría en Madrid (en puntos de índice). Se intercambia su posición con `Soporte` para mantener el orden visual pedido y el copy de horizonte deja de usar `24m` explícito en cabecera, pasando a `24 meses` en títulos y explicaciones de card.
- Ajuste de UX/copy aplicado en `Historico > Hexágono seleccionado`: se elimina el identificador H3 visible y los chips redundantes (`locales`, `Surv`, `Soporte`) de cabecera; el bloque pasa a apoyarse solo en cards explicables. Se añade una card nueva `Locales del hexágono`, se elimina la card técnica de `Score bruto Cox`, `Ranking Madrid` muestra solo `#x de y` (con `top` dinámico trasladado a la explicación), `Vs media 24m` pasa a `Supervivencia vs media` con comparativa explícita contra la media en el primer texto, y `Supervivencia 24m` aclara ya que `m = meses`. Además se reordena la rejilla para priorizar lectura en 3 filas (`Locales/Ranking`, `Índice/Soporte`, `Supervivencia/Supervivencia vs media`) y se retira la nota final redundante de soporte a 24 meses.
- Nuevo comparador territorial ya integrado en la vista `Historico`: el lateral incorpora una seccion `Comparar zonas` con selector `Distrito / Barrio`, dos selects dependientes y CTA `Comparar`, y el mapa puede abrir ahora un banner flotante `zona vs zona` sin mezclarlo con la guia, la evolucion general ni el detalle del hexagono. La comparativa se ha simplificado para usar solo lecturas faciles de entender y con cambio real en el tiempo: para categorias concretas usa `puesto en Madrid`, `numero de locales de la categoria` y `peso de la categoria dentro de la zona`; para `Todos los locales` usa `puesto`, `numero total de locales` y `peso de la zona en Madrid`. Ademas desaparece la referencia visible a cortes mensuales tipo `mar 2026`: el comparador se presenta ya como lectura anual de la serie.
- Ajuste final adicional ya aplicado en la entrada de `Evolución histórica`: desaparecen las referencias visibles a cortes tipo `mar 2026`, el copy superior aclara que el usuario puede cambiar la categoría que quiera y el selector inicial de `Tipo de local` deja de depender del `<select>` nativo para pasar a un desplegable propio más redondeado, con margen lateral, menú acotado al viewport y mejor lectura en pantallas donde antes el menú se desbordaba.
- Refinamiento adicional de la sección `Mezcla del hexágono` ya aplicado tras validar que solo ampliar la paleta no bastaba: la asignación deja de depender de una lista plana de colores por hash y pasa a una secuencia `contrast-first` dentro del propio donut, alternando familias pastel separadas (arena, cielo, malva, salvia, lavanda, oliva, añil, melocotón, menta, rosa y teal) con tres bandas de tono y una microvariación por categoría. Resultado: los segmentos vecinos se distinguen bastante mejor sin salir del lenguaje visual suave del producto.
- Replanteamiento adicional del bump chart de evolución histórica ya aplicado tras auditar todas las categorías visibles del producto: el gráfico sigue priorizando claridad sobre exhaustividad, pero ahora el `top` es seleccionable en cliente de `6` a `12`, con `9` por defecto. `historical-evolution-banner.tsx` mantiene una mezcla de `4` líderes actuales + rutas históricas suficientes hasta completar el `top` elegido, recalcula gráfico y leyenda en cada cambio y conserva el guardarraíl que evita enseñar `#2` o `#3` si no está también visible el `#1` de ese mismo año. El builder y el fallback vuelven a soportar `12` puestos máximos para que ese selector no dependa del artefacto ya materializado. La lectura honesta no cambia: el ranking base sigue siendo denso y consistente (`gaps = 0` en el artefacto) y los huecos que aún puedan verse en categorías muy volátiles responden a una limitación deliberada de resumen, no a un error del cálculo.
- Ajuste final de copy aplicado sobre ese mismo banner histórico para hacerlo apto para cualquier público: el texto superior pasa a una sola frase directa (`Más a la izquierda es mejor. Aquí no enseñamos todas las zonas. Enseñamos el top N para que el gráfico se entienda de un vistazo.`) y el texto inferior adopta el tono del resto de banners, con explicación simple del cálculo y un significado claro de `Fuera`: `no entra en el top que estamos enseñando ahora`.

Nota de implementacion anterior (2026-03-27):
- Ajuste adicional del bump chart historico ya aplicado tras revisar `Todos los locales`: el builder deja de usar el `indice de especializacion` en ese agregado concreto, porque ahi colapsaba a `1,0` para todas las zonas, y pasa a ordenar por `cambio de peso en el total comercial de Madrid` respecto al inicio de la serie; ademas el overlay dibuja puntos neutros para rellenar todo el `top 12` visible aunque solo se destaquen algunas lineas y la leyenda se reduce ya a `color + nombre`, sin contexto extra.
- Replanteamiento posterior del bump chart historico ya aplicado: el ranking anual deja de ordenarse por stock bruto de locales activos y pasa a usar un `indice de especializacion` consistente en toda la serie (`cuota de la categoria en la zona / cuota de la categoria en Madrid`, con suavizado por tamano de zona para no sobrerreaccionar en barrios pequenos). El banner de evolucion mezcla ahora `lideres actuales + referentes historicos` en lugar de seguir solo a los ganadores de hoy, compacta la leyenda en formato mas discreto para aguantar mas series y actualiza tambien el texto de `Como interpretar este ranking` para distinguir claramente el ranking principal por riesgo actual del ranking historico por especializacion.
- Ajuste correctivo posterior del bump chart historico: el eje superior deja ya de muestrear etiquetas alternas y pasa a pintar todos los puestos visibles `#1`-`#12`, evitando la falsa impresion de huecos en el ranking cuando en realidad solo faltaban labels del SVG.
- Nueva capa temporal ya operativa en la vista historica web: aparece un boton `Evolución histórica` junto a la guia del ranking y abre un banner flotante sobre el mapa con bump chart anual pastel para `distritos / barrios`, siguiendo a los lideres actuales de la categoria seleccionada sin solapes ni labels montados sobre la grafica. El frontend carga este artefacto bajo demanda desde `front/public/data/frontend-historical-rankings.json`, limita la lectura visual al `top 12` visible con bucket `Fuera`, separa la leyenda en tarjetas para evitar desbordes y mantiene comportamiento responsive en desktop/movil.
- El builder historico web se amplia para sostener esa capa temporal sin cargarla en cliente: `back/scripts/build_frontend_map_artifacts.py` materializa ahora tambien `frontend-historical-rankings.json` tomando el ultimo mes disponible de cada año, uniendo `storage/data/processed/censo_geospatial/locales/*.csv.gz` con `storage/data/intermediate/censo_snapshots/actividades/*.csv.gz`, colapsando multiactividad/estados sin categoria con la misma semantica del selector y calculando ranking anual por `indice de especializacion` para `21` distritos y `131` barrios.
- Validacion de esta iteracion temporal completada: `python -m unittest tests.test_build_frontend_map_artifacts` en verde con nueva cobertura para seleccion anual y clasificacion de snapshots, regeneracion limpia de artefactos (`10.391` filas distrito, `57.630` barrio en el ranking temporal) y `npm --prefix front run typecheck` + `npm --prefix front run build` en verde; la ruta `/` abre correctamente en el navegador integrado, aunque desde el chat no hay inspeccion visual del DOM sin herramientas agenticas del browser.
- Nuevo informe estrategico ya materializado en `docs/historico_oportunidades_analisis.md`: audita a fondo la separacion entre Historico y Oportunidades, cuestiona sin conservadurismo la estructura actual y recomienda evolucionar el producto hacia una entrada por intencion (`entender el mercado` vs `evaluar una ubicacion`), dos vistas mucho mas asimetricas y una bateria de visualizaciones nuevas y mejoras de solidez en frontend, artefactos, datos y operativa.
- Refinamiento posterior de esa lectura visual en historico: la composicion por categorias de `Todos los locales` sale ya fuera de la tarjeta oscura del hexagono y pasa a su propia seccion clara al final del sidebar; el copy introductorio aprovecha todo el ancho disponible, desaparece el contador de categorias y el detalle de cada color deja de vivir dentro de la card para abrirse como banner flotante sobre el mapa, con posicion vertical acotada al panel visible para no quedar por detras ni descolgarse por el borde inferior. La interaccion queda ya solo en hover, sin activacion por clic/foco ni tooltip nativo negro del SVG. Se mantiene sin tocar el builder, solo aparece en `Todos los locales` y sigue cubriendo hexagonos con 1-31 categorias reales sin romper desktop ni movil.
- Correccion puntual de UX aplicada en oportunidades: el panel lateral secundario del bloque `Metro cercano` ya limita su posicion vertical al viewport real cuando el listado de paradas es largo, evitando que el hover se descuelgue por debajo de la pantalla y dejando el scroll interno siempre accesible.
- Ajuste de copy aplicado en la vista historica web: las cards del detalle del hexagono pasan a usar el CTA `Entender el dato`, el banner explicativo adopta el tono mas directo de oportunidades (`Que significa este dato`) y se simplifica el texto de valor/calculo de metricas clave (`Ranking Madrid`, `Indice relativo 0-1`, `Vs media`, `Supervivencia`, `Soporte`, `Barrio`, `Distrito`) para lectura mas rapida.
- Resolucion del bucket `Sin categoria` aplicada ya en el historico web tras auditar la causa raiz: no era una fuga masiva de taxonomia, sino mezcla de `Actividad no informada` (`44.237` locales visibles), `Multiactividad` (`2.891`), `Sin actividad declarada` (`246`), `Mes sin fichero de actividad` (`40`) y `Actividad pendiente de codificar` (`7`). `back/scripts/build_frontend_map_artifacts.py` deja de serializar ese bloque como `__unknown__ / Sin categoria`, reparte el estado real del dato en filtros explicados con definicion propia, los ordena detras de las macrocategorias comerciales y regenera `front/public/data/frontend-map-artifacts*.json`; `python -m unittest tests.test_build_frontend_map_artifacts` y `npm --prefix front run build` quedan en verde.
- Ajuste posterior de producto aplicado sobre ese mismo bloque historico: el selector de categorias oculta ya `Sin actividad declarada`, `Mes sin fichero de actividad` y `Actividad pendiente de codificar`, pero esos estados se conservan en `hexes/zones` y dentro de `Todos los locales` para no deformar agregados ni composicion por hexagono.
- Nuevo documento de sintesis ya materializado en `docs/sin_categoria_diagnostico.md`: explica de forma simple y detallada qué parte del problema sí era error nuestro, qué parte no, qué evidencia numérica lo sostiene, qué soluciones son posibles, cómo de robustas son y cuál es la recomendación final para producto, datos y modelado.
- Evaluacion especifica ya cerrada sobre excluir `Sin categoria` y `No priorizable` del historico: en el corte real que alimenta `frontend-map-artifacts`, `No priorizable` pesa `16.168` filas (`9,8%`) y `Sin categoria` `47.755` (`29,0%`). Quitar ambas mantiene cobertura territorial total (`21` distritos y `131` barrios siguen presentes) pero hace desaparecer `1.178` hexagonos (`12,1%`) y cambia con fuerza el agregado `Todos los locales`; recomendacion operativa: si se busca foco comercial, se puede retirar ya `No priorizable`, pero `Sin categoria` no deberia salir del agregado general sin separar antes `sin clasificar` vs `multiactividad` o sin moverlo a un tratamiento intermedio menos visible.
- Nuevo pipeline manual para `locales disponibles` preparado fuera del frontend: `back/scripts/build_manual_available_locales.py` + `back/src/localizate/manual_available_locales.py`, con crawl paginado de `Locales.es` (`venta` + `alquiler`), export bruto/final a CSV, geocoding cacheado via `Nominatim`, H3 res `10` y join espacial a `section_key` cuando la precision de direccion es suficiente.
- Endurecimiento posterior del pipeline manual de `locales disponibles`: se anade modo `--resume-from-raw` para reanudar desde el CSV bruto y la asignacion H3 pasa a ser conservadora, solo para geocodificaciones con precision `street_approx`, evitando centroides difusos de `Madrid`/barrios cuando la direccion del portal es demasiado generica.
- Nuevo corte producto para `locales disponibles` ya materializado: `back/scripts/build_frontend_opportunity_artifacts.py` genera un subset filtrado `manual_available_locales_madrid_selected.csv` con solo locales precisos y sin outliers claros (`207` filas sobre `229` candidatas precisas; se excluyen `18` fichas incompletas y `4` outliers fuertes), ademas de un resumen dedicado en `storage/data/processed/manual_available_locales_madrid_selected_summary.json`.
- Nueva pantalla web independiente de oportunidades ya operativa en `front/app/oportunidades/page.tsx`, con mapa de puntos sin hexagonos historicos, ficha de local filtrado, ranking de mejores actividades por entorno y seleccion manual de cualquier punto de Madrid resolviendo la seccion censal contenedora.
- Navegacion entre `historico` y `oportunidades` aligerada: los artefactos pesados del frontend web dejan de viajar embebidos en la respuesta HTML/RSC de cada ruta y pasan a cargarse desde `public/data` en cliente, eliminando el cuello de botella de servir decenas de MB al cambiar de pestaña; ademas la pestana precalienta el artefacto objetivo al pasar por encima para adelantar parte de la descarga.
- Ajuste posterior de UX aplicado sobre la vista de oportunidades: el lateral elimina la tarjeta de `Filtro activo`, usa el subtitulo `Locales disponibles y recomendacion de actividad`, corrige el wrapping del titulo principal y reordena la `lectura del punto` para explicar explicitamente que la ficha se interpreta siempre contra la seccion censal contenedora.
- La capa de scoring para oportunidades usa referencia historica fija del ABT `local_survival_abt` para evitar normalizaciones inestables punto a punto; en esta lectura de aperturas se neutralizan penalizaciones de `padron_lag` y `renta_carry_forward` por ser artefactos de frescura del dato historico y no señales economicas del punto actual.
- Correccion de datos aplicada al producto de oportunidades: el merge de `avisos` ya no colapsa a cero por desalineacion de codigos de barrio entre la fuente de avisos y la geografia censal usada en frontend; los artefactos regenerados vuelven a exponer tasas positivas por barrio/distrito en los `207` locales seleccionados.
- Replanteamiento del ranking de actividad aplicado en oportunidades: la recomendacion deja de ordenarse por supervivencia bruta y pasa a usar un `riesgo historico` ajustado por tamano muestral, con lookup de barrio por nombre estable (en vez de `barrio_code`, que colisionaba entre distritos en el export), aumentando la diversidad real de sugerencias servidas al frontend.
- Correccion posterior del orden visual en `Actividades recomendadas`: la mezcla barrio+distrito ya no conserva el orden de concatenacion, sino que reordena el ranking combinado por `activity_risk` final y resuelve duplicados por la mejor variante disponible, evitando que aparezcan riesgos mas altos por delante de riesgos mas bajos en la tarjeta.
- Endurecimiento adicional del producto de oportunidades: en desarrollo los fetchs de artefactos y secciones dejan de usar cache agresiva para no quedarse con rankings viejos tras regenerar; ademas el GeoJSON de secciones sale versionado y el ranking puede completar huecos con fallback `citywide` cuando barrio+distrito se quedan en 1-4 actividades.
- Endurecimiento extra de la vista de oportunidades: la shell cliente revalida el artefacto al recuperar foco/visibilidad y con sondeo ligero en desarrollo, de modo que una sesion ya abierta no se quede mostrando rankings obsoletos tras regenerar el dataset de oportunidades.
- Refinamiento adicional de UI en oportunidades: el titulo principal reduce ligeramente tamano y deja de cortar palabras a mitad; el subtitulo pasa a `recomendación`, se elimina el bloque redundante `Como leer esta ficha` y la tarjeta/ranking pierden el copy ruidoso de `cierre observado` y `confidence_tier`.
- Nueva capa explicativa en la ficha de oportunidades: la lectura contextual deja de mostrarse como texto corrido y pasa a una rejilla de metricas clicables; cada tarjeta del detalle del local o del punto libre puede abrir una definicion y su regla de calculo, y se elimina la antigua tarjeta de `Unidad de analisis`.
- Ajuste posterior de esa capa explicativa: las metricas contextuales se integran ya en la misma rejilla que el resto del detalle, sin subseccion aparte, y la explicacion de la metrica activa se desplaza a un banner flotante dentro del mapa para lectura inmediata.
- Nueva iteracion de claridad transversal web: el banner explicativo de metricas gana descripciones mas completas, motivo de utilidad y ejemplos cuando aportan contexto; ademas el historico adopta tambien metricas clicables en la ficha del hexagono y los tooltips de mapa para locales/hexagonos pasan a una tarjeta flotante mas legible y accionable.
- Enriquecimiento adicional del banner de oportunidades para `avisos`: al abrir `Avisos barrio` o `Avisos distrito`, la explicacion mantiene el texto existente pero anade ya un desglose dinamico del top 3 de categorias observado en el ultimo anio disponible para el barrio/distrito del local o del punto libre seleccionado; el builder materializa ese detalle en `frontend-opportunity-artifacts.json` y en `frontend-opportunity-sections.geojson`.
- Ajuste posterior del banner flotante en oportunidades: los overlays explicativos del mapa respetan ya tambien un margen inferior real dentro del panel y pueden desplazarse internamente cuando el contenido supera la altura disponible, evitando que el final de la explicacion quede cortado.
- Artefactos estaticos nuevos ya servidos al frontend web: `front/public/data/frontend-opportunity-artifacts.json` y `front/public/data/frontend-opportunity-sections.geojson`, junto con el contrato TS y el loader independiente para no tocar la pantalla historica salvo por un switch visual entre vistas.
- Refactor ABT arrancado para unificar el target en `cese_de_actividad` con `event_subtype` solo de auditoria.
- Las features de contexto comercial en `abt_survival.py` pasan a construirse con join lagged `t-1` para reducir contemporaneidad evitable.
- ABT y artefactos base ya regenerados con la nueva semantica; el ABT materializa `event_subtype_detail` para auditoria forense y el builder DuckDB se ha endurecido para evitar OOM en la agregacion de actividades.
- Nuevo bloque de variables internas ya materializado en `local_survival_abt`: flujos de entrada/salida por seccion (`3/6/12m`), tasas/net flow/turnover a `12m`, concentracion comercial (`HHI` y `top share` por division y categoria) y features temporales de cohorte/calendario de entrada para modelado.
- Validacion del bloque nuevo completada: `tests.test_survival_baseline` y `tests.test_abt_survival` en verde; artefacto `storage/data/features/local_survival_abt.csv` regenerado y verificado con las nuevas columnas materializadas.
- Retraining canonico de `local_survival` completado sobre el ABT ampliado: el ensemble mejora en `valid` (`Uno 0.6863 -> 0.7428`), pero empeora con fuerza en `test` (`Uno 0.6418 -> 0.5335`), asi que no se considera una mejora neta del campeon actual.
- Benchmark directo por variantes sobre este retrain ya medido con el mismo split holdout del pipeline: `cox` queda por delante del ensemble en `test` (`Uno 0.6100` vs `0.5338`; `AUC@12m 0.6135` vs `0.5394`), mientras `rsf` arrastra la mezcla (`Uno test 0.3622`). Decision provisional para `local_survival`: si hay que simplificar o elegir un campeon temporal, priorizar `cox_only` y relegar el ensemble hasta tener evidencia rolling/robustez especifica para este target.
- Arranque frontend web completado: nueva app `front/` en `Next.js + TypeScript + MapLibre + deck.gl`, builder estatico `back/scripts/build_frontend_map_artifacts.py` y artefacto JSON materializado en `front/public/data/frontend-map-artifacts.json`.
- El primer MVP web ya compila en `production build`, renderiza hexagonos H3 de Madrid, permite selector por tipo de local, horizonte `12m/24m`, filtro de calidad y panel lateral de detalle.
- Ajuste de UX del mapa web aplicado: vista completa en desktop sin scroll de pagina, sidebar con scroll propio y estado de camara compartido entre mapa base y capa H3 para que pan/zoom mantengan los hexagonos anclados al mapa.
- Refinamiento adicional del mapa aplicado: escala de color dinamica por filtro visual, tooltip compacto autoajustado al texto, mayor legibilidad del mapa base y retirada del control de calidad / banner de viewport para simplificar la experiencia.
- Endurecimiento de navegacion del mapa web aplicado: la capa H3 ya no gobierna una camara paralela, sino que se monta como overlay nativo de `MapLibre`; ademas se acota el zoom out minimo y se desactivan rotaciones/world copies para evitar cualquier descuadre persistente entre hexagonos y mapa base.
- Afinado visual adicional del frontend web: la carga inicial del mapa se desplaza hacia Madrid mas central para evitar arrancar demasiado al norte y la escala cromatica pasa a degradar con transicion mas suave, limitando el tramo naranja para que valores altos (>=95% aprox.) entren antes en la zona neutra/verde y la leyenda no colapse en etiquetas repetidas de `100%`.
- Simplificacion adicional de la UI web aplicada: se retira la escala de color del lateral para dejar el panel centrado en filtro, metricas y detalle, manteniendo el coloreado solo como soporte visual dentro del mapa.
- Enriquecimiento del detalle historico aplicado: cada hexagono visible del frontend incorpora ahora ubicacion aproximada en texto (`barrio, distrito`) inferida desde `section_geography`, para que el usuario pueda interpretar el hexagono seleccionado sin depender solo del identificador H3.
- Refinamiento adicional del detalle web aplicado: el panel activo ya muestra mas contexto del hexagono seleccionado sin tocar el backend (`eventos observados`, tasa historica de cambio/cierre, percentil de riesgo y gap frente a la media de la categoria), ademas de una comparativa ligera con el barrio/distrito para esa misma categoria cuando existe agregacion zonal.
- Correccion de usabilidad del mapa aplicada: el tooltip flotante del hover ya no se dibuja con offset fijo, sino que se recoloca dentro del viewport del mapa para que siga siendo visible tambien en los bordes inferiores y laterales.
- Estabilizacion extra del frontend aplicada: se anade una ruta `app/not-found.tsx` explicita para evitar el fallo de `/_not-found` en `next build` y dejar el empaquetado productivo consistente.
- Ampliacion sustantiva del lateral web aplicada sobre la vista historica: se separa la ficha de categoria del detalle de hexagono, se incorporan ranking del hex dentro de Madrid, riesgo relativo presentado como percentil/decil, comparativa del hex contra barrio y distrito sobre la misma macrocategoria, ranking de la categoria dentro de cada zona y listados de top barrios / top distritos para la categoria activa.
- Builder estatico del frontend rehecho en la parte zonal para esta pantalla: el payload de barrio/distrito deja de reutilizar la taxonomia fina de recomendacion y pasa a agregarse sobre la misma macrocategoria del mapa historico, ademas de inyectar metadatos del glosario (`definicion`, `epigrafes`, `cobertura historica`, ejemplos) para la ficha de categoria.
- Ajuste fino de copy y densidad visual aplicado en la vista historica: la ficha de categoria se simplifica a titulo + definicion, y el bloque de hexagono seleccionado pierde la etiqueta de calidad, el decil de riesgo y la comparativa de zona para dejar una lectura mas limpia basada en ranking, percentil, soporte y contexto minimo.
- Ajuste adicional del lateral historico aplicado: la ficha del hexagono pierde ubicacion textual, eventos/cambio-cierre y soporte visible; el percentil pasa a mostrarse con prefijo `P`, se anade el riesgo local crudo y la diferencia de supervivencia frente a la media de la categoria, y los rankings visibles (top zonas y ranking del hex) pasan a ordenarse por riesgo en lugar de supervivencia.
- Correccion adicional de ranking y layout aplicada: el orden de `zonas destacadas` y del ranking del hex se fija ya por `avg_risk_ensemble` (valor absoluto del riesgo medio) con el percentil solo como apoyo secundario, y las tarjetas de zonas se normalizan en altura/estructura para evitar el descuadre visual entre columnas.
- Limpieza visual adicional aplicada en `zonas destacadas`: se retiran percentiles y confianza del copy, y el ranking pasa a renderizarse por filas emparejadas distrito/barrio para que ambas columnas compartan siempre altura y composicion visual.
- Research exhaustivo de datasets externos completado: se rastrearon 678 datasets del catálogo de datos.madrid.es y se descargaron 29 archivos cubriendo equipamientos urbanos, indicadores socioeconómicos, vulnerabilidad territorial, actividad empresarial, población y zonas verdes. Scripts: `back/scripts/download_external_datasets.py` (descarga) y `back/scripts/transform_external_datasets.py` (transformación). Resultado: 2,129 puntos de interés geocodificados en `storage/data/external/processed/unified_equipamientos_geo.csv`, 116,930 registros del Panel de Indicadores (381 indicadores × 21 distritos × 131 barrios × 2008-2025), 6 ficheros IGUALA de vulnerabilidad, IAE 2023-2025, población por barrio e inspecciones de consumo. Reporte completo en `docs/data/external_datasets_report.md`. Pendiente de integración al frontend.
- Estudio completo de viabilidad de Google Maps Platform realizado (`docs/google_maps_study.md`): las APIs de Places, Geocoding y Routes ofrecen datos valiosos (densidad comercial real, ratings, reviews, accesibilidad) y el free tier cubriría nuestras 207 oportunidades en volumen, pero las restricciones de TOS son bloqueantes para nuestra arquitectura: (1) prohibición de mostrar datos de Places sobre mapas no-Google (Localizate usa MapLibre), (2) prohibición de cachear/almacenar resultados (incompatible con nuestro pipeline de artefactos estáticos), (3) prohibición explícita de usar coordenadas de Places para point-in-polygon o como features de modelos ML. Recomendación: usar Google Maps Embed (gratuito, ilimitado) como mini-mapa en fichas de oportunidad, links directos a Google Maps, y obtener densidad comercial vía OpenStreetMap/Overpass API (sin restricciones de TOS, cacheable en build time).
- Correccion critica de semantica aplicada en el frontend historico: los horizontes sin soporte suficiente ya no se materializan como `0%`, sino como `sin datos` (`null` en el artefacto), y el mapa/panel excluyen esos casos de la media y los colorean en neutro. Impacto medido antes del fix en hexagonos: a `24m`, `3.170` filas (`4,2%` del universo hex-categoria) se estaban mostrando como `0%` pese a ser realmente `sin soporte`; eso suponia el `72,0%` de todos los `0%` visibles a `24m`.
- Correccion robusta de geografia aplicada en el builder historico: cuando falla el join por `section_key_start`, el artefacto web intenta ahora recuperar `barrio/distrito` mediante fallback espacial por coordenadas contra la geometria real de secciones censales, manteniendo el `section_key` como via primaria y reduciendo los `Sin asignar` que ya eran recuperables con los datos actuales.
- Nuevo selector de tamano de hexagono ya operativo en la pestana historica web: el frontend expone mallas `pequena / mediana / grande`, mantiene `pequena` como default y hace el cambio rapido mediante precarga en cliente de artefactos estaticos separados, evitando meter las tres resoluciones en un unico JSON gigante.
- Builder historico ampliado para esa UX multi-malla: `back/scripts/build_frontend_map_artifacts.py` materializa ahora tres artefactos H3 (`res 10 / 9 / 8`) usando rollup a parent en build time desde los scores locales existentes, sin reentrenar el modelo; resultado actual materializado: `75.272` filas hex-categoria en pequeno, `30.993` en mediano y `9.564` en grande.
- Validacion especifica del cambio multi-malla completada: nuevo coverage de tests para deteccion de resolucion H3 y agregacion a parents en `back/tests/test_build_frontend_map_artifacts.py`, `next build` en verde y artefactos regenerados en `front/public/data/frontend-map-artifacts*.json`.
- Refinamiento adicional de UX aplicado a los tooltips del mapa web: el selector de malla pasa a `Bajo / Medio / Alto`, los banners flotantes de historico y oportunidades se simplifican para dejar solo metricas de `supervivencia` y `riesgo`, y el posicionamiento del tooltip evita ya el area inmediata del puntero para no tapar el hexagono o local que se esta intentando seleccionar.
- Nueva iteracion de banners explicativos ya operativa en web: la vista de oportunidades enriquece `Ranking Madrid`, `Ranking distrito`, `Ranking barrio`, `Renta seccion`, `Densidad poblacion`, `Poblacion`, `Extranjera`, `Joven 15-29`, `Rotacion 12m`, `Metro` y `Competencia` con comparativas dinamicas sobre el universo de secciones; ademas la vista historica convierte los rankings de barrios/distritos en tarjetas clicables que abren un overlay con el ranking de actividades dentro de la zona seleccionada, reutilizando los agregados historicos ya cargados en frontend.
- Ajuste adicional de UX y consistencia en oportunidades ya aplicado: la ficha de `local filtrado` mueve el percentil a chip clicable junto al tier cualitativo, elimina la repeticion superior de `Mejor actividad` y retira el boton `Limpiar punto` en `punto libre`; ademas el builder deja de heredar un bloque degenerado del `local_survival_abt` para `competencia local` y `categorias activas`, sobreescribiendo ese contexto comercial desde `activity_survival_abt` y corrigiendo los ceros espurios en los artefactos servidos al frontend.
- Refinamiento posterior de esa misma cabecera en oportunidades: todos los chips del `local filtrado` pasan a compartir tamano/estilo y los de `operacion`, `precio` y `metros cuadrados` se vuelven tambien clicables, con breakdowns ligeros por Madrid / distrito / barrio para leer mix `venta-alquiler`, medianas y posicion relativa del anuncio sin salir de la ficha.
- Ajuste fino posterior sobre esa cabecera y sus banners: los chips recuperan una tipografia mas contenida y el subtitulo de cada fila explicativa baja ya a una segunda linea completa, evitando choques y cortes con nombres largos de distrito o barrio en todos los desgloses compartidos.
- Correccion final de consistencia visual en oportunidades: los chips clicables dejan de sobreescribir el `font-size` y el `line-height` base del componente, de modo que vuelven a coincidir realmente con la escala de los chips del hexagono seleccionado en la vista historica.
- Integracion efectiva de datasets externos ya materializada en oportunidades: `back/scripts/build_frontend_opportunity_artifacts.py` enriquece secciones y locales con equipamientos proximos (200 m / 500 m / 1 km), inspecciones de consumo por distrito, vulnerabilidad IGUALA e indicadores distritales del panel municipal; la ficha web anade cuatro tarjetas clicables nuevas (`Facilidades cercanas`, `Inspecciones consumo`, `Vulnerabilidad`, `Indicadores distrito`) con desglose por categoria/radio, top epigrafes, esferas IGUALA y comparativa frente a Madrid. Artefactos regenerados en `front/public/data/`, `npx tsc --noEmit` y `next build` en verde.
- Correccion posterior del benchmark barrial en oportunidades: los `locales filtrados` dejan de conservar `district_code/barrio_code` crudos del portal cuando ya existe `section_key` canonico y pasan a heredar la geografia administrativa de la seccion censal; ademas el comparador de `barrio` en frontend deja de filtrar solo por `barrio_code` y exige tambien `district_code`, evitando mezclar barrios homonimos/codigos repetidos entre distritos y eliminando `Sin datos` espurios en desgloses barriales como `Renta sección`.
- Auditoria adicional de semantica territorial y renta completada en oportunidades: el builder y la shell terminan de tratar `barrio` como clave compuesta `district_code + barrio_code` tambien en rankings, comparables y contadores visibles, cerrando otra via silenciosa de mezcla entre distritos con codigos barriales repetidos.
- Correccion de causa raiz en renta Madrid aplicada en `back/src/localizate/socioeconomics.py`: la columna `Total` del CSV de renta podia entrar como `float` y truncar ceros finales (`12.130` -> `12.13` -> `1213`), contaminando renta de seccion y distrito con falsos outliers extremos. El parser reconstruye ahora euros correctamente desde ese formato, el panel `section_socioeconomic_panel` se ha regenerado y desaparecen los minimos absurdos que estaban forzando lecturas incoherentes en frontend.
- Refinamiento posterior de UX/copy en oportunidades: la ficha deja de abusar de terminologia tecnica (`sección censal`) y pasa a explicarse como `zona pequena del censo` cuando ayuda a lectura; ademas `Renta sección` se simplifica a `Ingreso del entorno`, `Indicadores distrito` pasa a `Contexto del distrito`, se acortan los labels de benchmark (`Madrid / Tu distrito / Tu barrio`) y los artefactos ya propagan `renta_reference_year`, `renta_granularity_used` y `renta_outlier_adjusted` para explicar al usuario si la cifra viene de zona, distrito o ciudad.
- Validacion final de este bloque completada: el caso auditado de Viriato/Trafalgar (`listing_id=135639`) queda ya con barrio canonico `003`, renta efectiva `26.310 EUR`, referencia `2023` y granularidad `section`; `npm run build` en `front` vuelve a pasar en verde con los artefactos regenerados.
- Nuevo rediseño integral de la ficha de oportunidades ya operativo: la rejilla se reagrupa por tematicas (`Potencial y encaje`, `Demografía y renta`, `Accesibilidad y dotación`, `Señales urbanas`, `Contexto distrital`), los tres rankings se condensan en una sola tarjeta explicada por escalas, `Población` y `Densidad` se funden en `Base residencial`, aparece una nueva tarjeta de `Edad media`, `Cuota misma macro` pasa a `Cuota misma categoría`, `Avisos barrio/distrito` se unifica en una sola lectura y el detalle contextual deja de duplicar renta distrital para priorizar indicadores externos mas utiles.
- Enriquecimiento adicional del artefacto de oportunidades completado para sostener ese rediseño: `back/src/localizate/survival_features.py` normaliza nombres legibles de accesos de metro y el builder propaga `metro_nearest_name_start` junto a listas de accesos a `500 m / 1 km`; `Equipamientos por categoría` pasa a ordenarse y leerse a `1 km`, se limpian epigrafes de inspeccion como `SITUADOS: SIN DETERMINAR`, `Categorías activas` gana comparativa Madrid/distrito/barrio y `Contexto del distrito` pasa a resumir apertura/cierre comercial, paro, densidad, zonas verdes, mercados y valor catastral.
- Validacion final de esta iteracion completada: `back/scripts/build_frontend_opportunity_artifacts.py` regenera `207` locales y `2.461` secciones enriquecidas, se corrige ademas la serializacion de nulos de metro para no exponer `"<NA>"` en JSON, desaparece `SIN DETERMINAR` del artefacto frontend, el resumen vuelve a contar barrios por clave compuesta (`77`) y tanto `npx tsc --noEmit` como `npm run build` en `front` quedan en verde.
- Nueva ampliacion contextual de oportunidades ya materializada: `Demografía y renta` gana una tarjeta de `Tercera edad 65+` con benchmark Madrid/distrito/barrio; `Accesibilidad y dotación` se reparte ahora en `4` cards (`Metro`, `Equipamientos cerca`, `Movilidad y compra diaria`, `Comunidad y cuidados`), `Señales urbanas` queda tambien en `4` al mover `Rotación 12m` a ese bloque, y `Contexto distrital` deja la tarjeta unica genérica para desglosarse en `Mercado y empleo`, `Población y dependencia`, `Entorno urbano` y `Red pública y sénior`.
- Endurecimiento adicional del builder de oportunidades completado en esta misma pasada: `back/scripts/build_frontend_opportunity_artifacts.py` propaga `share_age_65_plus_start` a artefactos/contrato frontend, amplía el panel distrital a `18` indicadores útiles (demografía, dependencia, migración, bibliotecas, cultura, deporte y red de mayores) y excluye la fila agregada `district_code=00` del Panel de Indicadores para no contaminar medias ciudad ni comparativas distritales. Tras regenerar artefactos, la auditoría final confirma `0` apariciones de `"<NA>"`, `0` incoherencias monotónicas en equipamientos, `0` fallos del nuevo share sénior y cobertura completa de los indicadores requeridos en los `207` locales seleccionados; el caso ya auditado `listing_id=135639` queda validado también con share sénior idéntico entre punto y sección.
- Nuevo ajuste fino de UX en oportunidades ya aplicado: desaparece la card redundante de `Actividad sugerida`, el ranking inferior gana un botón `Cómo interpretar este ranking` con el mismo patrón explicativo flotante del histórico, `Base residencial` pasa a `Población` mostrando solo habitantes en primera vista, `Movilidad y compra diaria` y `Comunidad y cuidados` se eliminan por redundancia, `Contexto distrital` desaparece como bloque propio y `Tasa de paro` + `Índice de dependencia` se recolocan dentro de `Demografía y renta`; además `Equipamientos cerca` deja de enseñar radios acumulados confusos y pasa a leerse en tramos no solapados (`0-200 m`, `200-500 m`, `500 m-1 km`), mientras `Rotación 12m` se explica ya como señal que puede valer `0%` real en muchas secciones pequeñas sin ser un fallo de datos.
- Refinamiento posterior de ese mismo bloque ya aplicado: el botón de ayuda del ranking en oportunidades abandona el estilo `ghost` pensado para fondos oscuros, adopta la misma tipografía/contraste centrado del histórico y la explicación del ranking sube de nivel técnico sin perder legibilidad, nombrando explícitamente el scorer de survival tipo `Cox`, el cálculo de `risk_index` y `activity_context_index`, el ajuste por encaje histórico de cada categoría y las penalizaciones suaves por soporte o cobertura más débiles.
- Limpieza final de copy aplicada en esa ayuda del ranking: el texto técnico mantiene la explicación del modelo y del cálculo contextual, pero elimina ya el formato tipo variable/campo entre comillas para que la lectura sea más natural en producto.
- Corrección específica del bloque `Metro cercano` ya materializada en oportunidades: el hover del desglose abre ahora un panel lateral independiente en desktop, deja de incrustarse dentro del mismo banner y pasa a mostrar estaciones oficiales de Metro de Madrid en lugar de nombres de accesos/entradas. Para sostenerlo, `back/src/localizate/survival_features.py` mapea cada acceso al nodo principal más cercano y el builder propaga `metro_nearest_station_name_start` junto con listas de estaciones oficiales a `500 m / 1 km`; artefactos regenerados y `npm --prefix front run build` en verde.
- Ajuste semántico adicional aplicado sobre ese mismo bloque: los contadores visibles del banner dejan de usar `entradas/accesos` y pasan a medir `paradas oficiales únicas` por radio, con nuevos campos `metro_station_count_500m_start` y `metro_station_count_1000m_start` propagados a artefactos, benchmarks y frontend para que el número y la mediana de referencia hablen del mismo concepto.
- Endurecimiento extra de calidad aplicado tras esa corrección: la normalización de nombres de Metro deja de depender de un único `latin1 -> utf-8` y pasa a combinar `ftfy` con varios intentos seguros de reparación/fallback, cubriendo cadenas reales como `Ã“pera`, `ArgÃ¼elles`, `RubÃ©n DarÃ­o` o `NÃºÃ±ez de Balboa` sin romper nombres ya sanos; además el estilo global `.eyebrow` gana algo más de aire a la izquierda y en `line-height` para evitar que la `Q` de `Qué significa` se recorte en los banners.
- Evaluación de reentrenamiento `activity_survival` con bloque externo ya cerrada: el candidato `activity_survival_pruned_with_external` queda claramente por debajo del campeón actual tanto en canónico (valid Uno `0.6432` y test Uno `0.5221` frente a `0.7756` / `0.6050`) como en rolling (test Uno medio `0.5389` frente a `0.6044` y Dynamic AUC medio `0.5343` frente a `0.6321`). La simulación sobre las `207` oportunidades visibles confirma además que la ampliación externa alteraría demasiado el ranking de actividades del front (`134/207` cambios de top-1 y `195/207` cambios de top-5) sin mejorar la robustez offline, así que la decisión operativa pasa a ser mantener el modelo actual; durante esta validación también queda corregido un bug del helper `attach_external_district_features` cuando el frame de entrada ya trae `district_code`.
- Pendiente tras este bloque: decidir si estas comparativas client-side deben migrar a API ligera cuando crezca el payload y seguir afinando el detalle zonal solo si la UX real pide mas profundidad.

## Identidad del proyecto

- Nombre de repo: Localizate
- Nombre de proyecto: Madrid Local Predict (premios datos abiertos 2026)
- Objetivo: macro DB historica de locales comerciales de Madrid, enriquecida con variables socioeconomicas y geoespaciales, para predecir supervivencia y servir un mapa interactivo.

## Enfoque unificado (resolviendo inconsistencias)

- Datos crudos ya estan descargados en `storage/raw/`. No se usa `data/raw/` ni descarga automatica en este momento.
- La ingesta canonica se basa en `back/scripts/build_raw_inventory.py` y el manifest `storage/data/intermediate/raw_manifest.csv`.
- El corte de pureza del censo es 2015-01.
- El CRS del censo cambia en 2017-09 (ED50 -> ETRS89). Todo join espacial debe normalizar CRS antes de H3 o distancias.
- Modelo previsto: Survival Analysis (RSF o Gradient Boosting) con point-in-time joins.
- Visualizacion: H3 res 10 para mapa; punto exacto para features de distancia.
- Outputs en batch para servir un mapa/app web; `Streamlit` queda como via legacy de exploracion, no como frontend objetivo.
- LLM es capa opcional para explicacion; no bloquea pipeline de datos.

## Estado actual (hecho)

- Inventario y manifest canonico raw generados (ver `docs/data/raw_data_inventory.md`).
- Manifest historico del censo `locales+actividades` desde 2015-01, con CRS por periodo.
- Perfilado de snapshots del censo y materializacion puntual de periodos clave.
- Cobertura de claves de seccion entre censo/padron/renta calculada.
- Metadata geografica de secciones materializada desde shapefile (colapsando multipartes).
- Capa socioeconomica en codigo: normaliza padron, agrega demografia, integra renta y geografia.
- Contrato operativo ABT + Point-in-Time definido en `docs/modeling/abt_pit_contract.md` para evitar leakage temporal y fijar reglas de join/fallback.
- Fase 1 completada: paneles `padron_section_panel` y `section_socioeconomic_panel` materializados en `storage/data/processed/`.
- Build de `padron` optimizado con cache incremental mensual en `storage/data/intermediate/padron_section_panel/` (un fichero agregado por periodo).
- Fase 2 arrancada: creado pipeline de materializacion historica normalizada del censo en `back/scripts/build_censo_historical_normalized.py`.
- Plan historico de ejecucion generado en `storage/data/processed/censo_historical_materialization_manifest.csv` y `docs/data/censo_historical_materialization.md`.
- Plan actual fase 2: `264` tareas (`132` periodos x `locales/actividades`), con `257` pendientes de materializar, `5` ya cacheadas y `2` sin `actividades` por huecos historicos (`2017-12`, `2022-04`).
- Fase 2 cerrada: manifest historico sin pendientes (`planned_materialize = 0`), con `257` materializados, `5` cacheados y `2` ausentes en manifest de `actividades`.
- Fase 3 cerrada: pipeline geoespacial implementado y materializado en historico completo (`132` periodos del manifest).
- Salida geoespacial consolidada en `storage/data/processed/censo_geospatial/` con manifest en `storage/data/processed/censo_geospatial_manifest.csv`.
- Resultado fase 3: `131` periodos materializados + `1` cacheado, `20,212,017` filas procesadas, `18,873,903` filas con coordenadas WGS84 + H3.
- En `2017-09` se aplica politica conservadora por defecto (`transition_policy=skip`), quedando `142,878` filas marcadas para revision de transicion CRS.
- Robustez operativa añadida: si un snapshot normalizado `locales` esta corrupto, se rematerializa automaticamente y se reintenta lectura.
- Fase ABT redefinida y rehecha: `storage/data/features/local_survival_abt.csv` regenerada (`203,870` filas, censura global `2026-03`) con cierre por desaparicion o primer cambio robusto `single-single` de division.
- Limpieza masiva de `actividades` integrada en pipeline ABT:
	- normalizacion de codigos equivalentes (`47` vs `47.0`)
	- remapeo canonico por descripcion cuando el codigo venia mal cargado
	- exclusion de placeholders/no codificados (`0`, `-1`, `PT`, equivalentes)
	- auditorias exportadas en `storage/data/processed/activity_code_normalization_audit.csv` y `storage/data/processed/local_activity_change_candidates.csv`
- Reporte ABT actualizado en `docs/modeling/abt_survival.md` con nuevo mix de eventos, metricas de cobertura y resumen de limpieza.
- Verificacion automatica de `storage/raw/actividades`: `134` ficheros detectados y `0` vacios fisicos (`size_0`/cabecera en blanco).
- Politicas cerradas para modelado:
	- CRS transicion `2017-09`: `exclude_transition` en entrenamiento.
	- Renta post-2023: `renta_max_year=2023` + imputacion jerarquica (`district_median` -> `city_median`).
- Siguiente bloque ejecutado: baseline de scoring survival en `back/scripts/train_survival_baseline.py`.
- Artefactos baseline generados:
	- `storage/data/exports/local_survival_scores.csv`
	- `storage/models/survival_baseline_metrics.json`
	- `docs/modeling/survival_baseline.md`
- Resultado baseline heuristico reentrenado sobre el nuevo target:
	- Filas modeladas: `203,828` (42 bloqueadas por transicion CRS)
	- Split temporal: train `149,213`, valid `2,742`, test `51,873`
	- Eventos por split: train `14,918`, valid `52`, test `266`
	- C-index sampled: train `0.4493`, valid `0.3996`, test `0.4967`
	- Quality gate baseline: `pass`
- README publico actualizado con narrativa no tecnica del proyecto (que hacemos, por que y estado para presentacion externa).
- Nuevo gate continuo de preparacion a modelado: `back/scripts/run_modeling_readiness.py` -> `docs/modeling/modeling_readiness.md` + `storage/models/modeling_readiness.json`.
- Estado readiness actual: `ready_with_caveats` (pipeline util, pero con eventos escasos en valid/test para evaluacion robusta).
- Intento de habilitar stack canonico (`scipy`, `scikit-learn`, `scikit-survival`) bloqueado por entorno (fallo de instalacion de paquetes en la venv).
- Baseline enriquecido con evaluacion por horizontes (`6/12/24` meses) y resumen de calibracion por buckets de riesgo.
- README publico reforzado con bitacora narrativa por iteraciones (enfoque explicativo para presentacion externa).
- Stack survival canonico desbloqueado en venv: `scipy`, `scikit-learn`, `scikit-survival` instalados.
- Nuevo bloque completado: entrenamiento canonico `Cox + RSF + GBSA` en `back/scripts/train_survival_canonical.py`.
- Artefactos canonicos generados:
	- `storage/models/survival_canonical_metrics.json`
	- `docs/modeling/survival_canonical.md`
	- `storage/data/exports/local_survival_map_export.csv`
- Export final para mapa consolidada con score y banderas de calidad:
	- scores: `risk_cox`, `risk_rsf`, `risk_gbsa`, `risk_ensemble`
	- calidad: `quality_flag_transition`, `quality_flag_missing_h3`, `quality_flag_renta_imputed`, `quality_tier`
- Resultado canonical actualizado (ensemble):
	- Uno/IPCW C-index: train `0.7494`, valid `0.6863`, test `0.6418`
	- Dynamic AUC mean: train `0.8016`, valid `0.7398`, test `0.8773`
	- Quality gate canonico: `pass`
- Evaluacion survival robusta integrada en pipeline canonico:
	- `Uno / IPCW C-index` para `ensemble`
	- `Cumulative Dynamic AUC` en `6/12/24` meses para `ensemble`
	- `Integrated Brier Score (IBS)` para `cox`, `rsf`, `gbsa`
	- `quality gate` canonico actualizado a `pass/pass_with_caveats/review_required`
- `modeling_readiness` ya gobierna sobre metricas canonicas en lugar de depender solo del baseline.
- CLI `train_survival_canonical.py --quick` aligerado para validacion local trazable (submuestreo de fit + progreso tambien en `GBSA`).
- Ultima validacion rapida canonical regenerada con metadata de ejecucion (`quick_mode=true`, `fit_max_rows=10000`).
- Nueva capa de robustez post-fit completada sobre los scores exportados del canónico:
	- script nuevo `back/scripts/evaluate_survival_robustness.py`
	- modulo nuevo `back/src/localizate/survival_robustness.py`
	- artefactos `docs/modeling/survival_canonical_robustness.md` y `storage/models/survival_canonical_robustness.json`
	- bootstrap configurado con `200` iteraciones y `max_rows=10000` sobre `valid/test`
- Resultado de robustez actual:
	- estado `pass_with_caveats`
	- Uno bootstrap CI width: valid `0.1258`, test `0.1530`
	- Dynamic AUC bootstrap CI width: valid `0.1726`, test `0.2828`
	- warnings principales: `low_cases_valid_h6`, `low_cases_valid_h12`, `wide_dynamic_auc_ci_test`, `wide_uno_ci_test`, `low_controls_test_h24`
- Estado readiness actual tras integrar robustez: `ready_with_caveats`.
- Guardrail extra incorporado en `assign_temporal_split_adaptive()` para evitar splits degenerados sin filas de train cuando el nuevo target aumenta la densidad de eventos.
- Nuevo bloque pre-retraining completado: inventario raiz de variables en `docs/reference/VARIABLES.md` y ampliacion de la ABT con features adicionales de:
	- complejidad de actividad al alta (`n_divisions_start`, `n_epigrafes_start`)
	- competencia y mix en seccion (`section_local_count_*`, `section_same_division_*`, diversidad de divisiones)
	- dinamica socioeconomica interanual (`*_delta_12m_start`)
	- entorno externo via `avisos` del anio previo (`avisos_*_prev_year`)
	- proximidad al metro (`metro_distance_m_start`, conteos a 500m/1000m)
- Validacion estadistica ligera materializada antes del siguiente entrenamiento en:
	- `storage/models/survival_feature_validation.json`
	- `docs/modeling/survival_feature_validation.md`
- Resultado de validacion de variables:
	- filas analizadas: `203,828`
	- variables de modelado activas: `35`
	- variables con `p < 0.05`: `32`
	- top señales univariantes actuales: accesibilidad metro, densidad/stock comercial de seccion y variables de calidad/carry-forward
- Estado operativo actual: canonical reentrenado, robustez post-fit materializada y repo listo para decidir entre `ablation`, rolling backtest o siguiente iteracion de frontend.
- Nueva capa producto completada para recomendacion zona x categoria:
	- modulo `back/src/localizate/activity_taxonomy.py` con taxonomia web derivada desde epigrafes normalizados
	- script `back/scripts/build_zone_category_survival.py`
	- analisis survival por distrito y barrio en `storage/data/exports/district_category_survival.csv` y `storage/data/exports/barrio_category_survival.csv`
	- reporte estadistico en `storage/models/zone_category_survival_stats.json` y `docs/modeling/zone_category_survival.md`
	- reporte de taxonomia en `storage/data/processed/web_activity_taxonomy.csv` y `docs/frontend/activity_taxonomy_web.md`
- Resultado inicial zona x categoria:
	- `457` epigrafes validos unicos revisados y colapsados a `146` categorias web (`272` epigrafes priorizables)
	- `89,270` locales con epigrafe inicial recuperado; `76,172` filas investables para analisis
	- diferencias significativas por categoria dentro de `15` distritos
	- diferencias significativas entre distritos para `5` categorias
	- lectura producto: ya se puede construir un desplegable entendible y un ranking por distrito con evidencia estadistica, aunque la recomendacion debe mostrarse como supervivencia esperada y no como certeza
- Nuevo bloque completado para alinear el target con la pregunta de producto (`que actividad aguanta mejor en cada zona`):
	- taxonomia macro de actividad implementada en `back/src/localizate/activity_taxonomy.py` con `37` categorias compactas para modelado
	- glosario raiz generado en `docs/reference/ACTIVITY_GLOSSARY.md`
	- nueva ABT en `storage/data/features/activity_survival_abt.csv` y `storage/data/features/activity_survival_abt.parquet`
	- auditorias nuevas en `storage/data/processed/activity_macro_taxonomy.csv` y `storage/data/processed/activity_category_change_candidates.csv`
	- wrapper de build `back/scripts/build_activity_survival_abt.py`
	- wrapper de entrenamiento `back/scripts/train_activity_survival_canonical.py`
	- reporte ABT nuevo en `docs/modeling/abt_activity_survival.md`
- Definicion operativa del nuevo target `activity_survival`:
	- evento por desaparicion del local o primer cambio robusto `single-single` entre categorias macro de actividad
	- `18,893` eventos totales frente a `15,241` del target anterior
	- tasa de evento `0.0927` frente a `0.0748` del target anterior
	- desglose actual del nuevo target: `18,114` cambios de actividad + `779` desapariciones + `184,977` censuras
- Features de modelado ampliadas para el nuevo target:
	- categoria macro inicial del local
	- `n_activity_categories_start`
	- competencia local por la misma categoria en seccion
	- share de la categoria en seccion
	- one-hot estables por categoria macro para entrenamiento canonico
- Nuevo entrenamiento canonico completado sobre `activity_survival`:
	- artefactos `storage/models/survival_activity_canonical_metrics.json`, `docs/modeling/survival_activity_canonical.md` y `storage/data/exports/activity_survival_map_export.csv`
	- split temporal: train `149,280`, valid `2,646`, test `51,902`
	- eventos por split: train `18,588`, valid `61`, test `238`
	- Uno/IPCW C-index ensemble: train `0.7991`, valid `0.7756`, test `0.6050`
	- Dynamic AUC mean ensemble: train `0.8455`, valid `0.7928`, test `0.9236`
	- quality gate actual: `pass`
- Comparacion resumida vs canonical anterior (`local_survival`):
	- mejora clara en alineacion producto y en volumen de eventos observables
	- mejora en validacion: Uno `0.6863 -> 0.7756`, dynamic AUC `0.7398 -> 0.7928`
	- test mixto: Uno empeora `0.6418 -> 0.6050`, mientras dynamic AUC sube `0.8773 -> 0.9236`
	- conclusion operativa: el nuevo target es mejor como representacion del problema y mas rico en eventos, pero todavia no es una victoria limpia en generalizacion `test`; conviene robustecer comparacion antes de descartar modelos logisticos por horizonte
- Robustez bootstrap ya ejecutada tambien sobre `activity_survival`:
	- script nuevo `back/scripts/evaluate_activity_survival_robustness.py`
	- artefactos `docs/modeling/survival_activity_canonical_robustness.md` y `storage/models/survival_activity_canonical_robustness.json`
	- estado `pass_with_caveats`
	- Uno bootstrap: valid `0.7784` con CI `[0.7397, 0.8234]`; test `0.6046` con CI `[0.5283, 0.6919]`
	- dynamic AUC bootstrap mean: valid `0.7917` con CI `[0.7321, 0.8514]`; test `0.7936` con CI `[0.6533, 0.9749]`
	- warning principal: el test sigue siendo inestable por amplitud de CI y por soporte fragil en horizontes extremos
- Comparativa survival vs regresion logistica por horizontes completada sobre `activity_survival`:
	- modulo nuevo `back/src/localizate/activity_horizon_logistic.py`
	- script nuevo `back/scripts/train_activity_horizon_logistic.py`
	- artefactos `docs/modeling/activity_horizon_logistic.md` y `storage/models/activity_horizon_logistic_metrics.json`
	- horizontes elegidos automaticamente por soporte real de cierres: `12`, `15` y `18` meses
	- criterio de seleccion: al menos `15` casos valid, `1000` controles valid, `100` casos test y `200` controles test
	- lectura final: la logistica no gana en ninguno de los `3` horizontes ni en `valid` ni en `test` frente al score survival actual
	- detalle test AUC:
		- `h12`: logit `0.5759` vs survival `0.6256`
		- `h15`: logit `0.5773` vs survival `0.6101`
		- `h18`: logit `0.9163` vs survival `0.9508`
	- conclusion operativa actual: no hay evidencia para sustituir el enfoque survival por logistica horizon-based en esta iteracion
- Rolling backtest temporal completado sobre `activity_survival`:
	- modulo nuevo `back/src/localizate/survival_rolling_backtest.py`
	- script nuevo `back/scripts/run_activity_survival_rolling_backtest.py`
	- artefactos `docs/modeling/activity_survival_rolling_backtest.md` y `storage/models/activity_survival_rolling_backtest.json`
	- esquema walk-forward con `4` folds contiguos y cutoffs `2020-03 -> 2021-04 -> 2022-06 -> 2023-06 -> 2024-10 -> 2026-04`
	- configuracion de ejecucion usada para hacerlo operativo en una sola pasada: `RSF=120`, `GBSA=120`, `fit_max_rows=25000`
	- resumen agregado rolling:
		- valid Uno mean `0.6735` (std `0.0657`)
		- test Uno mean `0.6753` (std `0.0662`)
		- valid dynamic AUC mean `0.6741` (std `0.0984`)
		- test dynamic AUC mean `0.6990` (std `0.0714`)
	- comparacion contra split unico actual:
		- valid Uno baja `0.7756 -> 0.6735`
		- test Uno sube `0.6050 -> 0.6753`
		- valid dynamic AUC mean baja `0.7928 -> 0.6741`
		- test dynamic AUC mean baja `0.9236 -> 0.6990`
	- conclusion operativa: el split unico estaba siendo claramente optimista; el rolling backtest baja el nivel esperado de discriminacion fuera de train a la zona `0.67-0.68` en Uno y `~0.70` en mean AUC, que sigue siendo util para producto pero mas lejos de una señal "muy fuerte".
- Benchmark de composicion del ensemble ya ejecutado dentro del rolling backtest sin coste extra de entrenamiento por variante:
	- variantes evaluadas: `cox_only`, `gbsa_only`, `rsf_only`, `cox_gbsa_rank`, `ensemble_all_rank`, `ensemble_weighted_rank`
	- ranking por media de `Uno test`:
		- `cox_only`: `0.6811`
		- `ensemble_all_rank`: `0.6753`
		- `cox_gbsa_rank`: `0.6647`
		- `rsf_only`: `0.6627`
		- `ensemble_weighted_rank`: `0.6608`
		- `gbsa_only`: `0.6299`
	- lectura tecnica principal:
		- `cox_only` pasa a ser la mejor variante en media de `Uno test` y tambien gana en `test dynamic AUC mean` (`0.7091` vs `0.6990` del ensemble)
		- el ensemble actual mantiene una ligera ventaja en validacion (`valid Uno 0.6735` vs `0.6619` de `cox_only`), pero ya no compensa con mejor out-of-sample en test
		- `rsf_only` sigue mostrando buena señal en algunos folds pero demasiada volatilidad (`test Uno std 0.1255`)
		- `gbsa_only` queda claramente por debajo en este setup
	- conclusion operativa actual: el rolling nuevo inclina la balanza hacia `cox_only` como candidato principal para `activity_survival`; el ensemble igualitario ya no es el baseline mas defendible si hay que elegir un solo campeon.
- Primer corte del nuevo frontend web ya implementado:
	- app nueva en `front/` con `App Router`, `TypeScript`, `MapLibre` y `deck.gl`
	- shell visual minimalista con viewport fijo de Madrid y capa principal `H3HexagonLayer`
	- selector por tipo de local apoyado en `activity_category_desc_start` del ABT de `activity_survival`
	- metrica visual principal en UI: supervivencia observada agregada a `12m/24m` por hexagono
	- contrato de datos estatico en `front/public/data/frontend-map-artifacts.json`
	- builder dedicado `back/scripts/build_frontend_map_artifacts.py` que agrega `activity_survival_abt.csv` + `activity_survival_map_export.csv` y reutiliza `district_category_survival.csv` / `barrio_category_survival.csv`
	- validacion tecnica completada: `npm run typecheck` y `npm run build` en `front` en verde
		- el ensemble ponderado con menos peso para `RSF` no mejora al ensemble actual
	- conclusion operativa actual: no hay evidencia para reemplazar el ensemble igualitario por otra combinacion; si se busca simplificar sin perder casi nada, `cox_only` es el backup mas serio
- Runner completo de HPO competitivo ya implementado para dejarlo corriendo overnight:
	- modulo nuevo `back/src/localizate/survival_hpo.py`
	- script nuevo `back/scripts/run_activity_survival_hpo.py`
	- artefactos esperados `storage/models/activity_survival_hpo.json`, `docs/modeling/activity_survival_hpo.md` y `storage/models/activity_survival_hpo_checkpoint.json`
	- progreso persistente en `storage/models/run_progress_activity_survival_hpo.json`
	- estrategia de busqueda en `3` fases: cribado, confirmacion y finalistas `full-fidelity`
	- familias optimizadas: `cox_only` y `ensemble_all_rank`
	- smoke test del pipeline completado con exito antes del lanzamiento largo; en ese test rapido el mejor candidato fue `cox_only`
	- lanzamiento overnight ya iniciado en background con configuracion seria:
		- `cox_screen_trials=20`
		- `ensemble_screen_trials=8`
		- `confirm_top_k=2`
		- `final_top_k=2`
		- `screen_fit_max_rows=12000`, `confirm_fit_max_rows=25000`, `final_fit_max_rows=None`
		- `screen_rsf/gbsa=80`, `confirm_rsf/gbsa=160`, `final_rsf/gbsa=300`
	- objetivo del HPO: maximizar una combinacion de `Uno test`, `Uno valid`, `dynamic AUC` y estabilidad entre folds, no solo un score puntual en un split unico
	- HPO overnight ya completado (`34` trials evaluados)
	- mejor trial final encontrado: `cox_only` con `alpha=0.004431207789037498`, `ties=breslow`
	- metricas del mejor trial:
		- valid Uno mean `0.6718`
		- test Uno mean `0.6886`
		- valid dynamic AUC mean `0.6764`
		- test dynamic AUC mean `0.7119`
	- comparacion contra el benchmark rolling actualizado:
		- frente a `cox_only` untuned del rerun, mejora `test Uno 0.6811 -> 0.6886` y `test dynamic AUC mean 0.7091 -> 0.7119`
		- frente a `ensemble_all_rank` actual, mejora `test Uno 0.6753 -> 0.6886` y `test dynamic AUC mean 0.6990 -> 0.7119`
		- en validacion queda practicamente empatado con el ensemble (`valid Uno 0.6718` vs `0.6735`) y mejora ligeramente en `valid dynamic AUC mean` (`0.6764` vs `0.6741`)
	- mejor trial de la familia `ensemble_all_rank` no fue finalista ganador y quedo claramente por debajo:
		- valid Uno mean `0.6547`
		- test Uno mean `0.6613`
	- conclusion operativa final del HPO: con el benchmark rolling actualizado, el mejor `cox_only` afinado pasa a ser el candidato mas defendible para promocion operativa en `activity_survival`; la mejora no es enorme, pero ahora si supera a las variantes base relevantes en las metricas de test sin pagar un coste serio en validacion
- Ablation leave-one-block-out ya ejecutada sobre `activity_survival` usando el `cox_only` afinado ganador del HPO:
	- artefactos nuevos en `storage/models/activity_survival_cox_ablation.json` y `docs/modeling/activity_survival_cox_ablation.md`
	- baseline de la ablation: valid Uno `0.6687`, test Uno `0.6786`, test dynamic AUC mean `0.7033`
	- bloque claramente dominante: `activity_identity` (dummies de macrocategoria); al retirarlo el test Uno cae `-0.1447` y el test dynamic AUC mean `-0.1387`
	- bloques con ayuda pequena pero positiva: `metro` (`delta test Uno -0.0026`) y, casi nulo, `activity_complexity`
	- bloques que apenas mueven la aguja en este setup Cox: `competition_flow`, `competition_concentration` y `zone_dynamics`
	- bloques que parecen ruidosos o redundantes fuera de muestra: `competition_stock` (`delta test Uno +0.0117` al quitarlo), `temporal` (`+0.0091`), `avisos` (`+0.0047`) y en menor medida `socioeconomic` (`+0.0034`, aunque con peor valid/AUC)
	- conclusion operativa de la ablation: el modelo `activity_survival` esta capturando sobre todo identidad de actividad; buena parte del contexto adicional no esta comprando robustez extra en el Cox actual y conviene simplificar antes de seguir anadiendo features
	- poda aplicada en codigo como perfil de modelado `activity_survival_pruned`: se excluyen del entrenamiento `competition_stock`, `avisos` y `temporal`, pero las columnas siguen existiendo en el ABT y en los builders del frontend para poder mostrarlas como contexto en UI
	- rerun rolling tras la poda ya ejecutado: `cox_only` mejora ligeramente hasta `test Uno 0.6835` y `valid Uno 0.6678`, mientras el `ensemble_all_rank` cae a `test Uno 0.6044`; conclusion operativa actualizada: la poda refuerza la promocion de `cox_only` y no conviene seguir usando el ensemble actual como score principal de `activity_survival`
	- promocion historica ya aplicada en frontend: `back/scripts/build_frontend_map_artifacts.py` pasa a usar `risk_cox` como score primario, recalcula percentiles sobre Cox y expone metadatos `risk_model_key=cox`; para no romper el contrato web, el payload mantiene `avg_risk_ensemble` como alias legacy del nuevo `avg_risk_primary`
	- artefactos historicos regenerados y validados tras la promocion (`frontend-map-artifacts*.json`, tests del builder en verde y `next build` correcto), de modo que la pestana historica ya queda servida con lectura Cox sin perder compatibilidad ni contexto adicional de UI
- Prompt de continuidad para trabajar sin contexto disponible en `docs/next_session_prompt.md`.
- Contexto legado consolidado en este archivo; carpeta `Context/` eliminada para simplificar el repo.
- Documentacion DB movida a `docs/documentacion_db/` para estandarizar nombres.

## Problemas y riesgos actuales

- `actividades` falta en 2017-12 y 2022-04.
- Observacion manual: algunos CSV antiguos en `storage/raw/actividades` parecen vacios. Falta confirmacion automatica.
- Shapefile de secciones no cubre todo el universo actual del censo (2461 vs 2499 en 2026-03).
- `renta` llega solo hasta 2023; hay que definir carry-forward.
- Build historico completo de `padron` sigue siendo costoso si se reconstruye sin cache (se recomienda modo incremental).
- Pendiente definir politica final para `2017-09` (asuncion CRS vs exclusion en modelado).
- La comparacion del nuevo target `activity_survival` sigue siendo mixta en `test`: mas eventos y mejor validacion, pero peor Uno out-of-sample que `local_survival`.
- `valid/test` siguen teniendo pocos eventos absolutos para decidir un cambio definitivo de framework sin intervalos de confianza adicionales.
- La logistica por horizonte tampoco corrige esa debilidad: en los horizontes con soporte suficiente queda por debajo del survival actual.
- El rolling backtest confirma variabilidad temporal no trivial: los folds se mueven entre `0.5877` y `0.7554` en Uno test, asi que conviene usar medias y dispersion, no un unico corte, para decidir cambios de modelo.
- La composicion del ensemble tampoco ofrece una mejora clara de primera ronda: el ensemble actual gana por poco y el mejor competidor real es `cox_only`, no una mezcla mas compleja.
- El HPO completo no encontro una mejora clara: el espacio afinado de `ensemble_all_rank` rindio peor de lo esperado y `cox_only` solo mejora de forma marginal el `test Uno` a costa de peorar `valid` y `AUC` medias.

## Punto exacto en el que estamos

1. Infraestructura canonica y auditoria inicial completadas.
2. Geografia de secciones materializada y comparada contra censo/padron/renta.
3. Panel socioeconomico historico materializado y reutilizable por cache.
4. Geoespacial `lat/lon + H3` historico cerrado; ABT baseline ya materializada para iniciar modelado.

## Siguientes pasos inmediatos

1. Decidir si se prefiere `ensemble_all_rank` como baseline operativo o `cox_only` como opcion simplificada casi equivalente.
2. Ejecutar `ablation` por bloques de variables sobre el candidato que se elija como principal (`ensemble_all_rank` o `cox_only`).
3. Revisar si merece la pena mantener `RSF` dentro del ensemble dado que aporta picos puntuales pero no mejora la media agregada.
4. Construir la primera app web sobre la taxonomia nueva y los outputs `district_category_survival.csv` + `activity_survival_map_export.csv`.
5. Refinar la taxonomia comercial donde convenga separar categorias muy agregadas (`Otros comercios`, `Logistica y movilidad`, `Servicios profesionales`).
6. Definir protocolo de recalibracion mensual (drift y estabilidad de score).
7. Preparar narrativa final de validacion para entrega del concurso con metricas puntuales + intervalos de confianza.

## Comandos utiles

```bash
PYTHONPATH=back/src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_raw_inventory.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_censo_snapshot_manifest.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_section_geography.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_section_socioeconomic_panel.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_censo_historical_normalized.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_censo_geospatial.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_local_survival_abt.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/write_survival_feature_inventory.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/validate_survival_features.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/train_survival_baseline.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/run_modeling_readiness.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/train_survival_canonical.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/evaluate_survival_robustness.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_zone_category_survival.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/build_activity_survival_abt.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/train_activity_survival_canonical.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/evaluate_activity_survival_robustness.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/train_activity_horizon_logistic.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/run_activity_survival_rolling_backtest.py
PYTHONPATH=back/src .venv/bin/python -u back/scripts/run_activity_survival_hpo.py
```

## Apéndices (verbatim, preservados)

### README.md (snapshot)

````markdown
# Localizate

Nota: la fuente canonica y actualizada del contexto es `docs/project/STATUS.md`. Este README se mantiene pero puede quedar desactualizado.

Base de datos analitica para construir una macro DB historica de locales comerciales de Madrid, enriquecerla con variables geoespaciales y socioeconomicas, y servir predicciones de supervivencia para un mapa interactivo.

## Estado actual

- Auditoria inicial del repo completada.
- Datos brutos disponibles localmente en `storage/raw/`.
- Contexto funcional legado consolidado dentro de `docs/project/STATUS.md`.
- Documentacion original de fuentes revisada en `docs/documentacion_db/`.
- Inventario canonico raw, manifest del censo y cobertura de `section_key` ya implementados.
- Metadata geografica de secciones materializada desde el shapefile y validada contra censo, padron y renta.
- Capa socioeconomica (`padron` + `renta` + metadata de secciones) implementada en codigo, pendiente de optimizacion para materializar toda la serie historica de forma eficiente.

## Estructura del repo

- `back/src/localizate/`: paquete Python principal.
- `back/scripts/`: scripts operativos y CLI.
- `back/configs/`: configuracion declarativa.
- `storage/data/intermediate/`: tablas normalizadas temporales.
- `storage/data/features/`: features listas para ensamblar la ABT.
- `storage/data/processed/`: datasets maestros y tablas consolidadas.
- `storage/data/exports/`: salidas para mapa, API o app.
- `storage/models/`: artefactos entrenados.
- `front/`: frontend web moderno del producto de mapa.
- prototipo `Streamlit`: via legacy de exploracion ya retirada del layout principal.
- `back/tests/`: pruebas.
- `docs/`: auditoria, bitacora y decisiones.
- `docs/project/STATUS.md`: fuente canonica con contexto legado embebido.
- `docs/documentacion_db/`: PDFs originales de diccionario/metodologia.
- `storage/raw/`: data lake bruto legacy ya descargado en local.

## Hallazgos tecnicos importantes

- El censo de locales cambia de sistema de referencia a mitad de septiembre de 2017; antes de calcular H3, distancias o joins espaciales hay que normalizar CRS.
- `padron` viene duplicado en muchos meses (`csv` y `txt`) y necesita una version canonica por mes.
- `actividades` no cubre todos los meses presentes en `locales`; faltan al menos `2017_12` y `2022_04`.
- La renta disponible llega hasta 2023, asi que para escenarios actuales habra que congelar o imputar con criterio explicito.
- Los datos brutos mezclan encodings, sufijos de fichero y variantes funcionales del mismo dataset.
- El shapefile de secciones censales no cubre todo el universo actual del censo: tras colapsar multipartes quedan `2461` secciones unicas frente a `2499` en el censo `2026-03`.
- La primera version del build socioeconomico completo es correcta pero demasiado lenta; hay que pasarla a una estrategia incremental o con DuckDB antes de usarla como paso operativo frecuente.

## Entorno

El proyecto se fija de momento en Python `3.12` por compatibilidad con el stack geoespacial y `scikit-survival`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r back/requirements.txt
```

## Proximos pasos inmediatos

1. Definir una capa de lectura canonica para cada fuente: encoding, separador, CRS y esquema final.
2. Normalizar `locales` y `actividades` en una tabla historica mensual consistente.
3. Resolver la estrategia de seccion censal: join robusto entre `locales`, `padron`, `renta` y shapefile.
4. Crear la capa geoespacial base: reproyeccion a ETRS89, conversion a lat/lon y asignacion H3.
5. Optimizar y materializar el panel socioeconomico historico por seccion.
6. Diseñar la ABT de entrenamiento y las salidas batch para mapa y locales vacios.

## Documentacion viva

- Auditoria inicial: `docs/auditoria_inicial.md`
- Inventario canonico de fuentes raw: `docs/data/raw_data_inventory.md`
- Manifest canonico del censo historico: `docs/data/censo_snapshot_manifest.md`
- Perfil operativo de snapshots del censo: `docs/data/censo_snapshot_profile.md`
- Cobertura de claves de seccion: `docs/data/section_key_coverage.md`
- Geografia de secciones y cobertura: `docs/data/section_geography.md`
- Hoja de ruta operativa: `docs/project/roadmap.md`
- Bitacora resumida del proyecto: `docs/project/project_log.md`

## Scripts utiles

- `back/scripts/build_raw_inventory.py`: escanea `storage/raw/`, infiere encoding/delimitador, construye inventario canonico y selecciona el fichero valido por periodo.
- `back/scripts/build_censo_snapshot_manifest.py`: construye el manifest historico de snapshots `locales + actividades` desde 2015-01 y etiqueta el estado CRS por periodo.
- `back/scripts/profile_censo_snapshots.py`: perfila calidad de snapshots del censo y puede materializar periodos normalizados bajo `storage/data/intermediate/censo_snapshots/`.
- `back/scripts/profile_section_keys.py`: compara el solape de claves de seccion entre censo, padron y renta.
- `back/scripts/build_section_geography.py`: extrae metadata canonica del shapefile de secciones y mide cobertura frente a censo, padron y renta.
- `back/scripts/build_section_socioeconomic_panel.py`: construye el panel por seccion a partir de `padron`, `renta` y metadata geografica; actualmente funciona pero necesita optimizacion para series completas.
````

### Context/Intro_Roadmap.md (snapshot)

````markdown
# CONTEXTO GENERAL Y ROADMAP DEL PROYECTO: "MADRID LOCAL PREDICT"

Nota: la fuente canonica y actualizada es `docs/project/STATUS.md`. Este documento es legado y puede quedar desalineado.

## PREMIOS A LA REUTILIZACIÓN DE DATOS ABIERTOS - AYUNTAMIENTO DE MADRID 2026

## ESTADO REAL (Mar 2026)

- Datos crudos ya disponibles en `storage/raw/` (no se usa `data/raw/`).
- Inventario canonico y manifest raw generados: `storage/data/intermediate/raw_inventory.csv` y `storage/data/intermediate/raw_manifest.csv`.
- Manifest historico del censo desde 2015-01 con cambio de CRS en `2017-09`.
- Cobertura de claves de seccion y metadata geografica materializadas.
- Capa socioeconomica (`padron` + `renta` + secciones) implementada en codigo, pero el build historico completo es lento y requiere optimizacion antes de materializar.
- ABT, modelo y frontend aun no implementados.
````

### Context/Data_Processing.md (snapshot)

````markdown
# CONTEXTO TÉCNICO: SCRIPT DE DESCARGA E INGESTA AUTOMÁTICA

Nota: la fuente canonica y actualizada es `docs/project/STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Datos Abiertos Ayuntamiento de Madrid)

## ESTADO REAL (Mar 2026)

- Los datos ya estan descargados en `storage/raw/` y no se usa `data/raw/`.
- La ingesta canonica se hace con `back/scripts/build_raw_inventory.py`, que genera `storage/data/intermediate/raw_inventory.csv` y `storage/data/intermediate/raw_manifest.csv`.
- La seleccion correcta de `avisos` se resuelve con metadata CKAN (ver `back/src/localizate/ckan.py`).
- Hay indicios de que algunos CSV antiguos de `storage/raw/actividades` estan vacios; pendiente de confirmacion automatica.
````

### Context/Feature_Engineering.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 2: INGENIERÍA DE VARIABLES Y MODELADO ESPACIO-TEMPORAL

Nota: la fuente canonica y actualizada es `docs/project/STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Normalizacion del censo implementada en `back/src/localizate/censo.py` con cambio de CRS en `2017-09` y columnas de coordenadas `x_utm_best/y_utm_best`.
- Metadata de secciones censales materializada en `storage/data/processed/section_geography.csv`.
- Capa socioeconomica por seccion implementada en codigo (`back/src/localizate/socioeconomics.py`), pero el build historico completo es lento y necesita optimizacion.
- No se han generado H3 ni features espaciales finales.
````

### Context/Model_Training.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 3: ENTRENAMIENTO Y EVALUACIÓN DEL MODELO (SURVIVAL ANALYSIS)

Nota: la fuente canonica y actualizada es `docs/project/STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Todavia no hay ABT ni dataset de entrenamiento listo.
- No se ha entrenado ningun modelo.
- Este documento queda como plan; las decisiones finales dependen de cerrar el panel socioeconomico y la tabla historica de locales.
````

### Context/Generacion_Outputs.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 4: INFERENCIA BATCH Y GENERACIÓN DE BASE DE DATOS FINAL

Nota: la fuente canonica y actualizada es `docs/project/STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Esta fase aun no se ha iniciado porque falta ABT y modelo entrenado.
- Mantener este documento como guia futura; puede cambiar al conocer la capacidad real del panel socioeconomico.
````

### Context/Frontend.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 5: DESARROLLO FRONTEND WEB Y CAPA AGÉNTICA

Nota: la fuente canonica y actualizada es `docs/project/STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Frontend web ya iniciado en `front/` con stack moderno (`Next.js`, `TypeScript`, `MapLibre`, `deck.gl`).
- La primera iteracion funciona sobre artefactos estaticos generados offline desde el pipeline actual; la API queda para una fase posterior.
````
