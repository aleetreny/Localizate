# STATUS

## 2026-04-18

- Reemplazo global de marca: todas las apariciones exactas de la marca sin tilde en archivos versionados pasan a "Localízate".
- Alcance principal: documentación, frontend, memoria de candidatura, etiquetas de tareas locales y cadenas visibles en scripts/worker.
- Se actualizan también artefactos estáticos ya generados en `front/out` para mantener coherencia visual inmediata.
- Excepción técnica intencionada: se conservan dominios/URLs e identificadores de sistema en minúsculas para no romper rutas ni configuración.
- Validación: búsqueda exacta de la marca sin tilde en archivos versionados devuelve 0 coincidencias y en salida estática web (`front/out`) devuelve 0 coincidencias.
