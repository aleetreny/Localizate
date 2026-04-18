# Front

Aplicacion publica de Localízate construida con `Next.js`, `TypeScript`, `MapLibre` y `deck.gl`.

## Comandos

```powershell
npm install
npm run dev
npm run typecheck
npm run build
npm run build:static
```

## Variables publicas relevantes

- `NEXT_PUBLIC_DATA_BASE_URL`: base externa para cargar artefactos publicos cuando no se sirven desde el propio `front/public/data/`.
- `NEXT_PUBLIC_OPPORTUNITY_GEOCODE_ENDPOINT`: endpoint del worker que resuelve direcciones en la vista Oportunidades.

## Notas

- El frontend esta preparado para exportacion estatica.
- Si `NEXT_PUBLIC_DATA_BASE_URL` esta definida, las paginas dejan de incrustar los JSON pesados en build-time y cargan los artefactos por `fetch`.
- Los datos publicos versionados viven en `front/public/data/`.
