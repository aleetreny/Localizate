# Auditoria inicial

## Objetivo

La auditoria inicial se hizo para convertir un entorno de trabajo con datos, ideas y materiales dispersos en un repositorio reproducible, legible y listo para evolucionar como producto.

## Hallazgos principales

- El proyecto tenia materia prima muy valiosa, pero una estructura documental y tecnica poco homogena.
- El volumen de datos brutos justificaba separar con claridad codigo, artefactos publicos y almacenamiento local no versionado.
- Habia retos tecnicos relevantes desde el inicio: cambios de CRS, heterogeneidad de formatos, fuentes con distinta granularidad y necesidad de joins territoriales robustos.

## Decisiones que salieron de esa auditoria

- Crear un backend Python separado para builders, transformaciones y validacion.
- Construir un frontend propio en `Next.js` en lugar de depender de una app exploratoria legacy.
- Tratar `storage/` como espacio operativo local, no como contenido para versionar.
- Consolidar documentacion funcional y metodologica bajo `docs/`.
- Diseñar una salida publica basada en artefactos estaticos ligeros para hacer viable una web rapida.

## Valor de esa fase

La auditoria inicial no se conserva aqui como bitacora interna detallada, sino como referencia de las decisiones fundacionales que explican la arquitectura actual del proyecto.
