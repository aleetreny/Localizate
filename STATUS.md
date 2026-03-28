# STATUS.md (Fuente Canonica)

Este archivo es la fuente unica y viva de contexto del proyecto. Se actualiza en cada avance y reemplaza al resto de documentos como referencia primaria.

Ultima actualizacion: 2026-03-28

Nota de implementacion en curso (2026-03-27):
- Nuevo pipeline manual para `locales disponibles` preparado fuera del frontend: `scripts/build_manual_available_locales.py` + `src/localizate/manual_available_locales.py`, con crawl paginado de `Locales.es` (`venta` + `alquiler`), export bruto/final a CSV, geocoding cacheado via `Nominatim`, H3 res `10` y join espacial a `section_key` cuando la precision de direccion es suficiente.
- Endurecimiento posterior del pipeline manual de `locales disponibles`: se anade modo `--resume-from-raw` para reanudar desde el CSV bruto y la asignacion H3 pasa a ser conservadora, solo para geocodificaciones con precision `street_approx`, evitando centroides difusos de `Madrid`/barrios cuando la direccion del portal es demasiado generica.
- Refactor ABT arrancado para unificar el target en `cese_de_actividad` con `event_subtype` solo de auditoria.
- Las features de contexto comercial en `abt_survival.py` pasan a construirse con join lagged `t-1` para reducir contemporaneidad evitable.
- ABT y artefactos base ya regenerados con la nueva semantica; el ABT materializa `event_subtype_detail` para auditoria forense y el builder DuckDB se ha endurecido para evitar OOM en la agregacion de actividades.
- Nuevo bloque de variables internas ya materializado en `local_survival_abt`: flujos de entrada/salida por seccion (`3/6/12m`), tasas/net flow/turnover a `12m`, concentracion comercial (`HHI` y `top share` por division y categoria) y features temporales de cohorte/calendario de entrada para modelado.
- Validacion del bloque nuevo completada: `tests.test_survival_baseline` y `tests.test_abt_survival` en verde; artefacto `data/features/local_survival_abt.csv` regenerado y verificado con las nuevas columnas materializadas.
- Arranque frontend web completado: nueva app `apps/web/` en `Next.js + TypeScript + MapLibre + deck.gl`, builder estatico `scripts/build_frontend_map_artifacts.py` y artefacto JSON materializado en `apps/web/public/data/frontend-map-artifacts.json`.
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
- Correccion critica de semantica aplicada en el frontend historico: los horizontes sin soporte suficiente ya no se materializan como `0%`, sino como `sin datos` (`null` en el artefacto), y el mapa/panel excluyen esos casos de la media y los colorean en neutro. Impacto medido antes del fix en hexagonos: a `24m`, `3.170` filas (`4,2%` del universo hex-categoria) se estaban mostrando como `0%` pese a ser realmente `sin soporte`; eso suponia el `72,0%` de todos los `0%` visibles a `24m`.
- Correccion robusta de geografia aplicada en el builder historico: cuando falla el join por `section_key_start`, el artefacto web intenta ahora recuperar `barrio/distrito` mediante fallback espacial por coordenadas contra la geometria real de secciones censales, manteniendo el `section_key` como via primaria y reduciendo los `Sin asignar` que ya eran recuperables con los datos actuales.
- Pendiente tras este bloque: enriquecer detalle de zona, conectar comparativas distrito/barrio en UI y decidir cuando sustituir artefactos estaticos por una API ligera.

## Identidad del proyecto

- Nombre de repo: Localizate
- Nombre de proyecto: Madrid Local Predict (premios datos abiertos 2026)
- Objetivo: macro DB historica de locales comerciales de Madrid, enriquecida con variables socioeconomicas y geoespaciales, para predecir supervivencia y servir un mapa interactivo.

## Enfoque unificado (resolviendo inconsistencias)

- Datos crudos ya estan descargados en `DB/`. No se usa `data/raw/` ni descarga automatica en este momento.
- La ingesta canonica se basa en `scripts/build_raw_inventory.py` y el manifest `data/intermediate/raw_manifest.csv`.
- El corte de pureza del censo es 2015-01.
- El CRS del censo cambia en 2017-09 (ED50 -> ETRS89). Todo join espacial debe normalizar CRS antes de H3 o distancias.
- Modelo previsto: Survival Analysis (RSF o Gradient Boosting) con point-in-time joins.
- Visualizacion: H3 res 10 para mapa; punto exacto para features de distancia.
- Outputs en batch para servir un mapa/app web; `Streamlit` queda como via legacy de exploracion, no como frontend objetivo.
- LLM es capa opcional para explicacion; no bloquea pipeline de datos.

## Estado actual (hecho)

- Inventario y manifest canonico raw generados (ver `docs/raw_data_inventory.md`).
- Manifest historico del censo `locales+actividades` desde 2015-01, con CRS por periodo.
- Perfilado de snapshots del censo y materializacion puntual de periodos clave.
- Cobertura de claves de seccion entre censo/padron/renta calculada.
- Metadata geografica de secciones materializada desde shapefile (colapsando multipartes).
- Capa socioeconomica en codigo: normaliza padron, agrega demografia, integra renta y geografia.
- Contrato operativo ABT + Point-in-Time definido en `docs/abt_pit_contract.md` para evitar leakage temporal y fijar reglas de join/fallback.
- Fase 1 completada: paneles `padron_section_panel` y `section_socioeconomic_panel` materializados en `data/processed/`.
- Build de `padron` optimizado con cache incremental mensual en `data/intermediate/padron_section_panel/` (un fichero agregado por periodo).
- Fase 2 arrancada: creado pipeline de materializacion historica normalizada del censo en `scripts/build_censo_historical_normalized.py`.
- Plan historico de ejecucion generado en `data/processed/censo_historical_materialization_manifest.csv` y `docs/censo_historical_materialization.md`.
- Plan actual fase 2: `264` tareas (`132` periodos x `locales/actividades`), con `257` pendientes de materializar, `5` ya cacheadas y `2` sin `actividades` por huecos historicos (`2017-12`, `2022-04`).
- Fase 2 cerrada: manifest historico sin pendientes (`planned_materialize = 0`), con `257` materializados, `5` cacheados y `2` ausentes en manifest de `actividades`.
- Fase 3 cerrada: pipeline geoespacial implementado y materializado en historico completo (`132` periodos del manifest).
- Salida geoespacial consolidada en `data/processed/censo_geospatial/` con manifest en `data/processed/censo_geospatial_manifest.csv`.
- Resultado fase 3: `131` periodos materializados + `1` cacheado, `20,212,017` filas procesadas, `18,873,903` filas con coordenadas WGS84 + H3.
- En `2017-09` se aplica politica conservadora por defecto (`transition_policy=skip`), quedando `142,878` filas marcadas para revision de transicion CRS.
- Robustez operativa añadida: si un snapshot normalizado `locales` esta corrupto, se rematerializa automaticamente y se reintenta lectura.
- Fase ABT redefinida y rehecha: `data/features/local_survival_abt.csv` regenerada (`203,870` filas, censura global `2026-03`) con cierre por desaparicion o primer cambio robusto `single-single` de division.
- Limpieza masiva de `actividades` integrada en pipeline ABT:
	- normalizacion de codigos equivalentes (`47` vs `47.0`)
	- remapeo canonico por descripcion cuando el codigo venia mal cargado
	- exclusion de placeholders/no codificados (`0`, `-1`, `PT`, equivalentes)
	- auditorias exportadas en `data/processed/activity_code_normalization_audit.csv` y `data/processed/local_activity_change_candidates.csv`
- Reporte ABT actualizado en `docs/abt_survival.md` con nuevo mix de eventos, metricas de cobertura y resumen de limpieza.
- Verificacion automatica de `DB/actividades`: `134` ficheros detectados y `0` vacios fisicos (`size_0`/cabecera en blanco).
- Politicas cerradas para modelado:
	- CRS transicion `2017-09`: `exclude_transition` en entrenamiento.
	- Renta post-2023: `renta_max_year=2023` + imputacion jerarquica (`district_median` -> `city_median`).
- Siguiente bloque ejecutado: baseline de scoring survival en `scripts/train_survival_baseline.py`.
- Artefactos baseline generados:
	- `data/exports/local_survival_scores.csv`
	- `models/survival_baseline_metrics.json`
	- `docs/survival_baseline.md`
- Resultado baseline heuristico reentrenado sobre el nuevo target:
	- Filas modeladas: `203,828` (42 bloqueadas por transicion CRS)
	- Split temporal: train `149,213`, valid `2,742`, test `51,873`
	- Eventos por split: train `14,918`, valid `52`, test `266`
	- C-index sampled: train `0.4493`, valid `0.3996`, test `0.4967`
	- Quality gate baseline: `pass`
- README publico actualizado con narrativa no tecnica del proyecto (que hacemos, por que y estado para presentacion externa).
- Nuevo gate continuo de preparacion a modelado: `scripts/run_modeling_readiness.py` -> `docs/modeling_readiness.md` + `models/modeling_readiness.json`.
- Estado readiness actual: `ready_with_caveats` (pipeline util, pero con eventos escasos en valid/test para evaluacion robusta).
- Intento de habilitar stack canonico (`scipy`, `scikit-learn`, `scikit-survival`) bloqueado por entorno (fallo de instalacion de paquetes en la venv).
- Baseline enriquecido con evaluacion por horizontes (`6/12/24` meses) y resumen de calibracion por buckets de riesgo.
- README publico reforzado con bitacora narrativa por iteraciones (enfoque explicativo para presentacion externa).
- Stack survival canonico desbloqueado en venv: `scipy`, `scikit-learn`, `scikit-survival` instalados.
- Nuevo bloque completado: entrenamiento canonico `Cox + RSF + GBSA` en `scripts/train_survival_canonical.py`.
- Artefactos canonicos generados:
	- `models/survival_canonical_metrics.json`
	- `docs/survival_canonical.md`
	- `data/exports/local_survival_map_export.csv`
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
	- script nuevo `scripts/evaluate_survival_robustness.py`
	- modulo nuevo `src/localizate/survival_robustness.py`
	- artefactos `docs/survival_canonical_robustness.md` y `models/survival_canonical_robustness.json`
	- bootstrap configurado con `200` iteraciones y `max_rows=10000` sobre `valid/test`
- Resultado de robustez actual:
	- estado `pass_with_caveats`
	- Uno bootstrap CI width: valid `0.1258`, test `0.1530`
	- Dynamic AUC bootstrap CI width: valid `0.1726`, test `0.2828`
	- warnings principales: `low_cases_valid_h6`, `low_cases_valid_h12`, `wide_dynamic_auc_ci_test`, `wide_uno_ci_test`, `low_controls_test_h24`
- Estado readiness actual tras integrar robustez: `ready_with_caveats`.
- Guardrail extra incorporado en `assign_temporal_split_adaptive()` para evitar splits degenerados sin filas de train cuando el nuevo target aumenta la densidad de eventos.
- Nuevo bloque pre-retraining completado: inventario raiz de variables en `VARIABLES.md` y ampliacion de la ABT con features adicionales de:
	- complejidad de actividad al alta (`n_divisions_start`, `n_epigrafes_start`)
	- competencia y mix en seccion (`section_local_count_*`, `section_same_division_*`, diversidad de divisiones)
	- dinamica socioeconomica interanual (`*_delta_12m_start`)
	- entorno externo via `avisos` del anio previo (`avisos_*_prev_year`)
	- proximidad al metro (`metro_distance_m_start`, conteos a 500m/1000m)
- Validacion estadistica ligera materializada antes del siguiente entrenamiento en:
	- `models/survival_feature_validation.json`
	- `docs/survival_feature_validation.md`
- Resultado de validacion de variables:
	- filas analizadas: `203,828`
	- variables de modelado activas: `35`
	- variables con `p < 0.05`: `32`
	- top señales univariantes actuales: accesibilidad metro, densidad/stock comercial de seccion y variables de calidad/carry-forward
- Estado operativo actual: canonical reentrenado, robustez post-fit materializada y repo listo para decidir entre `ablation`, rolling backtest o siguiente iteracion de frontend.
- Nueva capa producto completada para recomendacion zona x categoria:
	- modulo `src/localizate/activity_taxonomy.py` con taxonomia web derivada desde epigrafes normalizados
	- script `scripts/build_zone_category_survival.py`
	- analisis survival por distrito y barrio en `data/exports/district_category_survival.csv` y `data/exports/barrio_category_survival.csv`
	- reporte estadistico en `models/zone_category_survival_stats.json` y `docs/zone_category_survival.md`
	- reporte de taxonomia en `data/processed/web_activity_taxonomy.csv` y `docs/activity_taxonomy_web.md`
- Resultado inicial zona x categoria:
	- `457` epigrafes validos unicos revisados y colapsados a `146` categorias web (`272` epigrafes priorizables)
	- `89,270` locales con epigrafe inicial recuperado; `76,172` filas investables para analisis
	- diferencias significativas por categoria dentro de `15` distritos
	- diferencias significativas entre distritos para `5` categorias
	- lectura producto: ya se puede construir un desplegable entendible y un ranking por distrito con evidencia estadistica, aunque la recomendacion debe mostrarse como supervivencia esperada y no como certeza
- Nuevo bloque completado para alinear el target con la pregunta de producto (`que actividad aguanta mejor en cada zona`):
	- taxonomia macro de actividad implementada en `src/localizate/activity_taxonomy.py` con `37` categorias compactas para modelado
	- glosario raiz generado en `ACTIVITY_GLOSSARY.md`
	- nueva ABT en `data/features/activity_survival_abt.csv` y `data/features/activity_survival_abt.parquet`
	- auditorias nuevas en `data/processed/activity_macro_taxonomy.csv` y `data/processed/activity_category_change_candidates.csv`
	- wrapper de build `scripts/build_activity_survival_abt.py`
	- wrapper de entrenamiento `scripts/train_activity_survival_canonical.py`
	- reporte ABT nuevo en `docs/abt_activity_survival.md`
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
	- artefactos `models/survival_activity_canonical_metrics.json`, `docs/survival_activity_canonical.md` y `data/exports/activity_survival_map_export.csv`
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
	- script nuevo `scripts/evaluate_activity_survival_robustness.py`
	- artefactos `docs/survival_activity_canonical_robustness.md` y `models/survival_activity_canonical_robustness.json`
	- estado `pass_with_caveats`
	- Uno bootstrap: valid `0.7784` con CI `[0.7397, 0.8234]`; test `0.6046` con CI `[0.5283, 0.6919]`
	- dynamic AUC bootstrap mean: valid `0.7917` con CI `[0.7321, 0.8514]`; test `0.7936` con CI `[0.6533, 0.9749]`
	- warning principal: el test sigue siendo inestable por amplitud de CI y por soporte fragil en horizontes extremos
- Comparativa survival vs regresion logistica por horizontes completada sobre `activity_survival`:
	- modulo nuevo `src/localizate/activity_horizon_logistic.py`
	- script nuevo `scripts/train_activity_horizon_logistic.py`
	- artefactos `docs/activity_horizon_logistic.md` y `models/activity_horizon_logistic_metrics.json`
	- horizontes elegidos automaticamente por soporte real de cierres: `12`, `15` y `18` meses
	- criterio de seleccion: al menos `15` casos valid, `1000` controles valid, `100` casos test y `200` controles test
	- lectura final: la logistica no gana en ninguno de los `3` horizontes ni en `valid` ni en `test` frente al score survival actual
	- detalle test AUC:
		- `h12`: logit `0.5759` vs survival `0.6256`
		- `h15`: logit `0.5773` vs survival `0.6101`
		- `h18`: logit `0.9163` vs survival `0.9508`
	- conclusion operativa actual: no hay evidencia para sustituir el enfoque survival por logistica horizon-based en esta iteracion
- Rolling backtest temporal completado sobre `activity_survival`:
	- modulo nuevo `src/localizate/survival_rolling_backtest.py`
	- script nuevo `scripts/run_activity_survival_rolling_backtest.py`
	- artefactos `docs/activity_survival_rolling_backtest.md` y `models/activity_survival_rolling_backtest.json`
	- esquema walk-forward con `4` folds contiguos y cutoffs `2020-03 -> 2021-04 -> 2022-06 -> 2023-06 -> 2024-10 -> 2026-04`
	- configuracion de ejecucion usada para hacerlo operativo en una sola pasada: `RSF=120`, `GBSA=120`, `fit_max_rows=25000`
	- resumen agregado rolling:
		- valid Uno mean `0.6898` (std `0.0627`)
		- test Uno mean `0.6885` (std `0.0665`)
		- valid dynamic AUC mean `0.7080` (std `0.0853`)
		- test dynamic AUC mean `0.7230` (std `0.0679`)
	- comparacion contra split unico actual:
		- valid Uno baja `0.7756 -> 0.6898`
		- test Uno sube `0.6050 -> 0.6885`
		- valid dynamic AUC mean baja `0.7928 -> 0.7080`
		- test dynamic AUC mean baja `0.9236 -> 0.7230`
	- conclusion operativa: el split unico estaba dando una foto optimista para algunas metricas y pesimista para otras; el rolling backtest sugiere un nivel de discriminacion mas estable alrededor de `0.69` en Uno fuera de train, sin mejora real del modelo pero con una lectura mucho mas robusta
- Benchmark de composicion del ensemble ya ejecutado dentro del rolling backtest sin coste extra de entrenamiento por variante:
	- variantes evaluadas: `cox_only`, `gbsa_only`, `rsf_only`, `cox_gbsa_rank`, `ensemble_all_rank`, `ensemble_weighted_rank`
	- ranking por media de `Uno test`:
		- `ensemble_all_rank`: `0.6885`
		- `cox_only`: `0.6875`
		- `cox_gbsa_rank`: `0.6810`
		- `ensemble_weighted_rank`: `0.6766`
		- `rsf_only`: `0.6588`
		- `gbsa_only`: `0.6397`
	- lectura tecnica principal:
		- el ensemble actual sigue siendo el mejor en media, aunque por margen minimo frente a `cox_only`
		- `cox_only` casi empata en rendimiento y es mas estable en `test` (`std 0.0464` vs `0.0665` del ensemble)
		- `rsf_only` gana `3/4` folds individualmente pero es demasiado volatil (`test Uno` entre `0.4036` y `0.7636`)
		- `gbsa_only` queda claramente por debajo en este setup
- Primer corte del nuevo frontend web ya implementado:
	- app nueva en `apps/web/` con `App Router`, `TypeScript`, `MapLibre` y `deck.gl`
	- shell visual minimalista con viewport fijo de Madrid y capa principal `H3HexagonLayer`
	- selector por tipo de local apoyado en `activity_category_desc_start` del ABT de `activity_survival`
	- metrica visual principal en UI: supervivencia observada agregada a `12m/24m` por hexagono
	- contrato de datos estatico en `apps/web/public/data/frontend-map-artifacts.json`
	- builder dedicado `scripts/build_frontend_map_artifacts.py` que agrega `activity_survival_abt.csv` + `activity_survival_map_export.csv` y reutiliza `district_category_survival.csv` / `barrio_category_survival.csv`
	- validacion tecnica completada: `npm run typecheck` y `npm run build` en `apps/web` en verde
		- el ensemble ponderado con menos peso para `RSF` no mejora al ensemble actual
	- conclusion operativa actual: no hay evidencia para reemplazar el ensemble igualitario por otra combinacion; si se busca simplificar sin perder casi nada, `cox_only` es el backup mas serio
- Runner completo de HPO competitivo ya implementado para dejarlo corriendo overnight:
	- modulo nuevo `src/localizate/survival_hpo.py`
	- script nuevo `scripts/run_activity_survival_hpo.py`
	- artefactos esperados `models/activity_survival_hpo.json`, `docs/activity_survival_hpo.md` y `models/activity_survival_hpo_checkpoint.json`
	- progreso persistente en `models/run_progress_activity_survival_hpo.json`
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
	- comparacion contra el mejor benchmark rolling previo (`ensemble_all_rank`):
		- test Uno mejora solo de `0.6885 -> 0.6886` (cambio marginal)
		- valid Uno empeora de `0.6898 -> 0.6718`
		- test dynamic AUC mean empeora de `0.7230 -> 0.7119`
		- valid dynamic AUC mean empeora de `0.7080 -> 0.6764`
	- mejor trial de la familia `ensemble_all_rank` no fue finalista ganador y quedo claramente por debajo:
		- valid Uno mean `0.6547`
		- test Uno mean `0.6613`
	- conclusion operativa final del HPO: no hay mejora material sobre el benchmark rolling actual; `cox_only` queda como opcion simplificada muy competitiva, pero no como salto claro de performance frente al ensemble baseline
- Prompt de continuidad para trabajar sin contexto disponible en `docs/next_session_prompt.md`.
- Contexto legado consolidado en este archivo; carpeta `Context/` eliminada para simplificar el repo.
- Documentacion DB movida a `docs/documentacion_db/` para estandarizar nombres.

## Problemas y riesgos actuales

- `actividades` falta en 2017-12 y 2022-04.
- Observacion manual: algunos CSV antiguos en `DB/actividades` parecen vacios. Falta confirmacion automatica.
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
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -u scripts/build_raw_inventory.py
PYTHONPATH=src .venv/bin/python -u scripts/build_censo_snapshot_manifest.py
PYTHONPATH=src .venv/bin/python -u scripts/build_section_geography.py
PYTHONPATH=src .venv/bin/python -u scripts/build_section_socioeconomic_panel.py
PYTHONPATH=src .venv/bin/python -u scripts/build_censo_historical_normalized.py
PYTHONPATH=src .venv/bin/python -u scripts/build_censo_geospatial.py
PYTHONPATH=src .venv/bin/python -u scripts/build_local_survival_abt.py
PYTHONPATH=src .venv/bin/python -u scripts/write_survival_feature_inventory.py
PYTHONPATH=src .venv/bin/python -u scripts/validate_survival_features.py
PYTHONPATH=src .venv/bin/python -u scripts/train_survival_baseline.py
PYTHONPATH=src .venv/bin/python -u scripts/run_modeling_readiness.py
PYTHONPATH=src .venv/bin/python -u scripts/train_survival_canonical.py
PYTHONPATH=src .venv/bin/python -u scripts/evaluate_survival_robustness.py
PYTHONPATH=src .venv/bin/python -u scripts/build_zone_category_survival.py
PYTHONPATH=src .venv/bin/python -u scripts/build_activity_survival_abt.py
PYTHONPATH=src .venv/bin/python -u scripts/train_activity_survival_canonical.py
PYTHONPATH=src .venv/bin/python -u scripts/evaluate_activity_survival_robustness.py
PYTHONPATH=src .venv/bin/python -u scripts/train_activity_horizon_logistic.py
PYTHONPATH=src .venv/bin/python -u scripts/run_activity_survival_rolling_backtest.py
PYTHONPATH=src .venv/bin/python -u scripts/run_activity_survival_hpo.py
```

## Apéndices (verbatim, preservados)

### README.md (snapshot)

````markdown
# Localizate

Nota: la fuente canonica y actualizada del contexto es `STATUS.md`. Este README se mantiene pero puede quedar desactualizado.

Base de datos analitica para construir una macro DB historica de locales comerciales de Madrid, enriquecerla con variables geoespaciales y socioeconomicas, y servir predicciones de supervivencia para un mapa interactivo.

## Estado actual

- Auditoria inicial del repo completada.
- Datos brutos disponibles localmente en `DB/`.
- Contexto funcional legado consolidado dentro de `STATUS.md`.
- Documentacion original de fuentes revisada en `docs/documentacion_db/`.
- Inventario canonico raw, manifest del censo y cobertura de `section_key` ya implementados.
- Metadata geografica de secciones materializada desde el shapefile y validada contra censo, padron y renta.
- Capa socioeconomica (`padron` + `renta` + metadata de secciones) implementada en codigo, pendiente de optimizacion para materializar toda la serie historica de forma eficiente.

## Estructura del repo

- `src/localizate/`: paquete Python principal.
- `scripts/`: scripts operativos y CLI.
- `configs/`: configuracion declarativa.
- `data/intermediate/`: tablas normalizadas temporales.
- `data/features/`: features listas para ensamblar la ABT.
- `data/processed/`: datasets maestros y tablas consolidadas.
- `data/exports/`: salidas para mapa, API o app.
- `models/`: artefactos entrenados.
- `apps/web/`: frontend web moderno del producto de mapa.
- `apps/streamlit/`: frontend inicial y exploracion visual.
- `tests/`: pruebas.
- `docs/`: auditoria, bitacora y decisiones.
- `STATUS.md`: fuente canonica con contexto legado embebido.
- `docs/documentacion_db/`: PDFs originales de diccionario/metodologia.
- `DB/`: data lake bruto legacy ya descargado en local.

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
pip install -r requirements.txt
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
- Inventario canonico de fuentes raw: `docs/raw_data_inventory.md`
- Manifest canonico del censo historico: `docs/censo_snapshot_manifest.md`
- Perfil operativo de snapshots del censo: `docs/censo_snapshot_profile.md`
- Cobertura de claves de seccion: `docs/section_key_coverage.md`
- Geografia de secciones y cobertura: `docs/section_geography.md`
- Hoja de ruta operativa: `docs/roadmap.md`
- Bitacora resumida del proyecto: `docs/project_log.md`

## Scripts utiles

- `scripts/build_raw_inventory.py`: escanea `DB/`, infiere encoding/delimitador, construye inventario canonico y selecciona el fichero valido por periodo.
- `scripts/build_censo_snapshot_manifest.py`: construye el manifest historico de snapshots `locales + actividades` desde 2015-01 y etiqueta el estado CRS por periodo.
- `scripts/profile_censo_snapshots.py`: perfila calidad de snapshots del censo y puede materializar periodos normalizados bajo `data/intermediate/censo_snapshots/`.
- `scripts/profile_section_keys.py`: compara el solape de claves de seccion entre censo, padron y renta.
- `scripts/build_section_geography.py`: extrae metadata canonica del shapefile de secciones y mide cobertura frente a censo, padron y renta.
- `scripts/build_section_socioeconomic_panel.py`: construye el panel por seccion a partir de `padron`, `renta` y metadata geografica; actualmente funciona pero necesita optimizacion para series completas.
````

### Context/Intro_Roadmap.md (snapshot)

````markdown
# CONTEXTO GENERAL Y ROADMAP DEL PROYECTO: "MADRID LOCAL PREDICT"

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PREMIOS A LA REUTILIZACIÓN DE DATOS ABIERTOS - AYUNTAMIENTO DE MADRID 2026

## ESTADO REAL (Mar 2026)

- Datos crudos ya disponibles en `DB/` (no se usa `data/raw/`).
- Inventario canonico y manifest raw generados: `data/intermediate/raw_inventory.csv` y `data/intermediate/raw_manifest.csv`.
- Manifest historico del censo desde 2015-01 con cambio de CRS en `2017-09`.
- Cobertura de claves de seccion y metadata geografica materializadas.
- Capa socioeconomica (`padron` + `renta` + secciones) implementada en codigo, pero el build historico completo es lento y requiere optimizacion antes de materializar.
- ABT, modelo y frontend aun no implementados.
````

### Context/Data_Processing.md (snapshot)

````markdown
# CONTEXTO TÉCNICO: SCRIPT DE DESCARGA E INGESTA AUTOMÁTICA

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Datos Abiertos Ayuntamiento de Madrid)

## ESTADO REAL (Mar 2026)

- Los datos ya estan descargados en `DB/` y no se usa `data/raw/`.
- La ingesta canonica se hace con `scripts/build_raw_inventory.py`, que genera `data/intermediate/raw_inventory.csv` y `data/intermediate/raw_manifest.csv`.
- La seleccion correcta de `avisos` se resuelve con metadata CKAN (ver `src/localizate/ckan.py`).
- Hay indicios de que algunos CSV antiguos de `DB/actividades` estan vacios; pendiente de confirmacion automatica.
````

### Context/Feature_Engineering.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 2: INGENIERÍA DE VARIABLES Y MODELADO ESPACIO-TEMPORAL

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Normalizacion del censo implementada en `src/localizate/censo.py` con cambio de CRS en `2017-09` y columnas de coordenadas `x_utm_best/y_utm_best`.
- Metadata de secciones censales materializada en `data/processed/section_geography.csv`.
- Capa socioeconomica por seccion implementada en codigo (`src/localizate/socioeconomics.py`), pero el build historico completo es lento y necesita optimizacion.
- No se han generado H3 ni features espaciales finales.
````

### Context/Model_Training.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 3: ENTRENAMIENTO Y EVALUACIÓN DEL MODELO (SURVIVAL ANALYSIS)

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Todavia no hay ABT ni dataset de entrenamiento listo.
- No se ha entrenado ningun modelo.
- Este documento queda como plan; las decisiones finales dependen de cerrar el panel socioeconomico y la tabla historica de locales.
````

### Context/Generacion_Outputs.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 4: INFERENCIA BATCH Y GENERACIÓN DE BASE DE DATOS FINAL

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Esta fase aun no se ha iniciado porque falta ABT y modelo entrenado.
- Mantener este documento como guia futura; puede cambiar al conocer la capacidad real del panel socioeconomico.
````

### Context/Frontend.md (snapshot)

````markdown
# CONTEXTO TÉCNICO FASE 5: DESARROLLO FRONTEND WEB Y CAPA AGÉNTICA

Nota: la fuente canonica y actualizada es `STATUS.md`. Este documento es legado y puede quedar desalineado.

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

## ESTADO REAL (Mar 2026)

- Frontend web ya iniciado en `apps/web/` con stack moderno (`Next.js`, `TypeScript`, `MapLibre`, `deck.gl`).
- La primera iteracion funciona sobre artefactos estaticos generados offline desde el pipeline actual; la API queda para una fase posterior.
````
