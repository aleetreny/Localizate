# Resumen del proyecto

## Resumen ejecutivo

Localízate es un proyecto de inteligencia comercial para Madrid basado en datos abiertos, analítica geoespacial y modelado de supervivencia. Su salida principal es una web pública con dos lecturas complementarias:

- `Histórico`: cómo se comporta el tejido comercial por zona y categoría.
- `Oportunidades`: cómo leer una ubicación concreta, ya sea desde un local disponible o desde una dirección introducida por la persona usuaria.

Web pública: https://localizate.pages.dev/

## Qué publica este repositorio

- El código del frontend, backend y worker de geocodificación.
- Los workflows de publicación y despliegue.
- La documentación funcional, técnica y metodológica.
- Los artefactos públicos necesarios para entender la estructura del producto.

## Qué no publica este repositorio

- Credenciales, tokens o configuración sensible de despliegue.
- El lago de datos bruto completo de trabajo.
- Artefactos locales intermedios de entrenamiento almacenados en `storage/`.

## Stack

- `Python` para pipeline, integración de fuentes, modelado y generación de artefactos.
- `Next.js` + `TypeScript` para la experiencia web.
- `MapLibre` + `deck.gl` para cartografía interactiva.
- `Cloudflare Pages`, `Cloudflare R2` y `Cloudflare Workers` para la capa de publicación.
- `GitHub Actions` para automatizar refrescos y despliegues.

## Estado actual

- La web pública está desplegada y operativa.
- El frontend se exporta de forma estática.
- Los datos públicos pesados pueden servirse desde almacenamiento externo.
- El repositorio está preparado para revisarse como entrega técnica y funcional.

## Documentación clave

- [Visión de producto](../product/product-overview.md)
- [Auditoría inicial](initial-audit.md)
- [Roadmap público](roadmap.md)
- [Inventario documental general](../README.md)

## Límites reconocidos

- Algunas fuentes municipales tienen desfases temporales y huecos puntuales.
- La renta de detalle no es en tiempo real y requiere criterio de continuidad.
- La lectura del modelo debe entenderse como apoyo a la decisión, no como certeza determinista.
- Las oportunidades publicadas no representan todo el mercado, sino el conjunto de listings integrados por el pipeline actual.
