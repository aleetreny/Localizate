# Resumen del proyecto

## Resumen ejecutivo

Localizate es un proyecto de inteligencia comercial para Madrid basado en datos abiertos, analitica geoespacial y modelado de supervivencia. Su salida principal es una web publica con dos lecturas complementarias:

- `Historico`: como se comporta el tejido comercial por zona y categoria.
- `Oportunidades`: como leer una ubicacion concreta, ya sea desde un local disponible o desde una direccion introducida por la persona usuaria.

Web publica: https://localizate.pages.dev/

## Que publica este repositorio

- El codigo del frontend, backend y worker de geocodificacion.
- Los workflows de publicacion y despliegue.
- La documentacion funcional, tecnica y metodologica.
- Los artefactos publicos necesarios para entender la estructura del producto.

## Que no publica este repositorio

- Credenciales, tokens o configuracion sensible de despliegue.
- El lago de datos bruto completo de trabajo.
- Artefactos locales intermedios de entrenamiento almacenados en `storage/`.

## Stack

- `Python` para pipeline, integracion de fuentes, modelado y generacion de artefactos.
- `Next.js` + `TypeScript` para la experiencia web.
- `MapLibre` + `deck.gl` para cartografia interactiva.
- `Cloudflare Pages`, `Cloudflare R2` y `Cloudflare Workers` para la capa de publicacion.
- `GitHub Actions` para automatizar refrescos y despliegues.

## Estado actual

- La web publica esta desplegada y operativa.
- El frontend se exporta de forma estatica.
- Los datos publicos pesados pueden servirse desde almacenamiento externo.
- El repositorio esta preparado para revisarse como entrega tecnica y funcional.

## Documentacion clave

- [Vision de producto](../product/product-overview.md)
- [Auditoria inicial](initial-audit.md)
- [Roadmap publico](roadmap.md)
- [Inventario documental general](../README.md)

## Limites reconocidos

- Algunas fuentes municipales tienen desfases temporales y huecos puntuales.
- La renta de detalle no es en tiempo real y requiere criterio de continuidad.
- La lectura del modelo debe entenderse como apoyo a la decision, no como certeza determinista.
- Las oportunidades publicadas no representan todo el mercado, sino el conjunto de listings integrados por el pipeline actual.
