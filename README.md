# Localizate

Proyecto para construir un mapa inteligente de locales comerciales de Madrid, con contexto social y geográfico, para estimar riesgo de cierre y apoyar decisiones públicas y privadas.

## Qué problema queremos resolver

Madrid tiene mucha información abierta, pero está repartida en muchos ficheros, formatos y periodos. Si queremos explicar **qué zonas son más estables**, **dónde hay más riesgo de cierre** o **qué patrones cambian en el tiempo**, primero hay que unir y limpiar todo.

Este proyecto hace justo eso: convertir datos complejos en una base clara, trazable y útil para un producto final (mapa + métricas de riesgo).

## Cómo estamos trabajando (en lenguaje sencillo)

### 1) Ordenar y entender los datos
Primero revisamos todas las fuentes y dejamos un inventario único para no mezclar versiones ni archivos dudosos.

**Por qué:** sin una base ordenada, cualquier análisis posterior puede salir mal aunque el modelo sea bueno.

### 2) Construir el histórico mensual
Después montamos una serie histórica consistente de locales y actividades, mes a mes.

**Por qué:** el proyecto es temporal; no basta una foto actual, necesitamos ver evolución y cambios.

### 3) Añadir la parte geográfica
Transformamos coordenadas y generamos una capa geográfica homogénea para comparar zonas de forma estable.

**Por qué:** la localización es una pieza central del problema, pero había cambios históricos de referencia espacial que podían introducir errores.

### 4) Añadir contexto social y económico
Integramos padrón, renta y datos de secciones censales para que cada local tenga contexto del entorno.

**Por qué:** el riesgo no depende solo del local; también depende del barrio y la dinámica socioeconómica.

### 5) Crear la base para modelar
Construimos la ABT (tabla de entrenamiento) y un baseline de riesgo con controles de calidad automáticos.

**Por qué:** antes de usar modelos avanzados, necesitamos una línea base robusta y auditable.

## Decisiones importantes tomadas (y motivo)

- **Transición geográfica de 2017-09:** se excluye en entrenamiento cuando hay ambigüedad.
	- Motivo: priorizar calidad y evitar ruido por mezcla de referencias espaciales.
- **Renta después de 2023:** usamos carry-forward controlado con imputación jerárquica (distrito → ciudad).
	- Motivo: mantener cobertura sin romper la lógica temporal del proyecto.

## Estado actual (resumen público)

- Extracción y procesamiento histórico: completados.
- Capa geográfica e integración socioeconómica: completadas.
- ABT de supervivencia: generada.
- Baseline de riesgo con quality gate: ejecutado.
- Próximo bloque: modelos de supervivencia canónicos (Cox/GBSA/RSF) con validación temporal estricta.

## Bitácora pública de avance (versión explicativa)

### Iteración 1 — Poner orden y base sólida
- Inventariamos fuentes, unificamos formatos y construimos histórico mensual.
- Motivo: sin una base limpia y consistente, los resultados del modelo no serían fiables.

### Iteración 2 — Contexto real del entorno
- Añadimos geografía (H3) y variables sociales/económicas por zona.
- Motivo: el riesgo de cierre depende del entorno, no solo del local.

### Iteración 3 — Preparar modelado con reglas de seguridad
- Definimos reglas temporales para evitar usar “información del futuro”.
- Cerramos dos políticas clave:
	- transición geográfica dudosa (2017-09) fuera de entrenamiento,
	- renta post-2023 con estrategia controlada de continuidad.
- Motivo: priorizar robustez y trazabilidad antes de complejidad.

### Iteración 4 — Baseline + control continuo
- Entrenamos un baseline de riesgo y añadimos chequeos automáticos de calidad.
- Incorporamos validaciones por horizonte temporal (6/12/24 meses) y reporte continuo de preparación a modelado.
- Motivo: detectar temprano si el sistema está listo para subir a modelos más avanzados.

### Iteración 5 — Modelos canónicos + export final para mapa
- Instalamos y activamos el stack completo de supervivencia.
- Entrenamos tres modelos estándar del estado del arte para este tipo de problema (Cox, RSF y GBSA), y además un score combinado.
- Generamos una exportación final lista para mapa con score y banderas de calidad por local.
- Motivo: pasar de una base “de seguridad” a una predicción más sólida sin perder trazabilidad.

### Situación en este momento
- El proyecto está **listo con cautelas** para pasar al siguiente nivel de modelado.
- Ya existe una primera versión de modelado canónico y una salida final para visualización en mapa.
- Cautela principal: pocos eventos observados en parte de validación/test, algo normal en problemas de cierre de negocio (evento raro).
- Cautela operativa: seguimos con régimen de evento raro, por lo que mantenemos validación temporal estricta y quality gates en cada iteración.

## Dónde ver el progreso

- **`README.md` (este archivo):** versión explicativa y pública (qué hacemos y por qué).
- **`STATUS.md`:** versión operativa interna (checkpoints, incidencias, métricas técnicas y roadmap de ejecución).

## Estructura del repo

- `src/localizate/`: lógica principal.
- `scripts/`: pasos ejecutables del pipeline.
- `data/processed/`: tablas consolidadas.
- `data/features/`: base lista para modelar.
- `data/exports/`: salidas para mapa/app.
- `models/`: métricas y artefactos de modelado.
- `docs/`: documentación de avance y decisiones.
- `tests/`: pruebas automáticas.

## Documentos clave

- `STATUS.md` → seguimiento interno detallado.
- `docs/abt_pit_contract.md` → reglas para evitar leakage temporal.
- `docs/survival_baseline.md` → resultados del baseline actual.

## Próximos pasos

1. Entrenar modelos de supervivencia canónicos sobre la misma base.
2. Mantener validación temporal y quality gates en cada iteración.
3. Publicar export final para mapa con score y banderas de calidad.
4. Preparar narrativa final de resultados para presentación pública.
