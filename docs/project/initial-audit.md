# Auditoría inicial

## Objetivo

La auditoría inicial se hizo para convertir un entorno de trabajo con datos, ideas y materiales dispersos en un repositorio reproducible, legible y listo para evolucionar como producto.

## Hallazgos principales

- El proyecto tenía materia prima muy valiosa, pero una estructura documental y técnica poco homogénea.
- El volumen de datos brutos justificaba separar con claridad código, artefactos públicos y almacenamiento local no versionado.
- Había retos técnicos relevantes desde el inicio: cambios de CRS, heterogeneidad de formatos, fuentes con distinta granularidad y necesidad de joins territoriales robustos.

## Decisiones que salieron de esa auditoría

- Crear un backend Python separado para builders, transformaciones y validación.
- Construir un frontend propio en `Next.js` en lugar de depender de una app exploratoria legacy.
- Tratar `storage/` como espacio operativo local, no como contenido para versionar.
- Consolidar documentación funcional y metodológica bajo `docs/`.
- Diseñar una salida pública basada en artefactos estáticos ligeros para hacer viable una web rápida.

## Valor de esa fase

La auditoría inicial no se conserva aquí como bitácora interna detallada, sino como referencia de las decisiones fundacionales que explican la arquitectura actual del proyecto.
