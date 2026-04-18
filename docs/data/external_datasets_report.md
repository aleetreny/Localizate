# Reporte: Datasets Externos para Enriquecimiento de Oportunidades

**Fecha:** 2025-07-15  
**Fuente principal:** [datos.madrid.es](https://datos.madrid.es) (Portal de datos abiertos del Ayuntamiento de Madrid)  
**Estado:** Descargados y transformados — pendiente de integración al frontend

---

## Resumen Ejecutivo

Se realizó un research exhaustivo del catálogo de datos abiertos de Madrid (678 datasets disponibles) buscando datasets que puedan enriquecer la sección de **Oportunidades** de Localízate. Se descargaron **29 archivos** de datos.madrid.es cubriendo:

- **2,129 puntos de interés geocodificados** (equipamientos urbanos con coordenadas)
- **116,930 registros** del Panel de Indicadores (381 indicadores socioeconómicos × 21 distritos × 131 barrios × 2008-2025)
- **6 ficheros IGUALA** de vulnerabilidad territorial por distrito y barrio
- **544 registros IAE** (actividad empresarial por epígrafe)
- **1,071 series** de población por distrito/barrio
- **4,219 inspecciones** de consumo con dirección postal
- **1,068 registros** de inventario de zonas verdes
- **63 rankings** de vulnerabilidad por distrito

### Archivos Generados

| Archivo procesado | Registros | Descripción |
|---|---|---|
| `unified_equipamientos_geo.csv` | 2,129 | Todos los puntos de interés unificados con lat/lon |
| `equipamiento_mercados.csv` | 44 | Mercados municipales |
| `equipamiento_parques.csv` | 207 (203 geo) | Parques y jardines |
| `equipamiento_centros_culturales.csv` | 127 | Centros culturales |
| `equipamiento_instalaciones_deportivas.csv` | 569 | Instalaciones deportivas |
| `equipamiento_polideportivos.csv` | 84 | Polideportivos |
| `equipamiento_colegios.csv` | 249 | Colegios públicos |
| `equipamiento_bibliotecas.csv` | 50 | Bibliotecas públicas |
| `equipamiento_centros_mayores.csv` | 94 | Centros de mayores |
| `equipamiento_servicios_sociales.csv` | 40 | Centros de servicios sociales |
| `equipamiento_aparcamientos.csv` | 5 | Aparcamientos públicos |
| `equipamiento_mercadillos.csv` | 33 | Mercadillos de vía pública |
| `equipamiento_bicimad.csv` | 631 | Estaciones BiciMAD |
| `iae_empresas_2025.csv` | 544 | Impuesto actividades económicas 2023-2025 |
| `poblacion_distrito_barrio.csv` | 1,071 | Población por distrito y barrio |
| `inspecciones_consumo.csv` | 4,219 | Inspecciones de consumo (2016+) |

**Ubicación archivos procesados:** `storage/data/external/processed/`  
**Ubicación archivos raw:** `storage/data/external/`

---

## 1. Equipamientos Urbanos Geocodificados (11 categorías + BiciMAD)

Todos con columnas: `category, title, district_name, neighborhood, lat, lon, street`

### 1.1 Mercados Municipales (44 registros)
- **Fuente:** `mercados_municipales.json`
- **Relevancia:** ★★★★★ — Los mercados municipales son polos de atracción comercial. Un local cerca de un mercado tiene mayor afluencia peatonal.
- **Uso propuesto:** Calcular distancia al mercado más cercano para cada oportunidad. Feature para modelo de supervivencia.

### 1.2 Parques y Jardines (207 registros, 203 geocodificados)
- **Fuente:** `parques_jardines.json`
- **Relevancia:** ★★★★ — Zonas verdes generan tráfico peatonal y definen el carácter del barrio.
- **Uso propuesto:** Densidad de zonas verdes en radio de 500m. Proxy de calidad de vida del entorno.

### 1.3 Centros Culturales (127 registros)
- **Fuente:** `centros_culturales.json`
- **Relevancia:** ★★★★ — Generan actividad y tráfico peatonal regular (clases, eventos).
- **Uso propuesto:** Conteo de equipamientos culturales en proximidad.

### 1.4 Instalaciones Deportivas (569 registros)
- **Fuente:** `instalaciones_deportivas.json`
- **Relevancia:** ★★★ — Mayor dataset de equipamientos. Incluye desde campos de fútbol hasta gimnasios municipales.
- **Uso propuesto:** Indicador de actividad barrial.

### 1.5 Polideportivos (84 registros)
- **Fuente:** `polideportivos.json`
- **Relevancia:** ★★★ — Complemento a instalaciones deportivas, equipamientos de mayor envergadura.

### 1.6 Colegios Públicos (249 registros)
- **Fuente:** `colegios_publicos.json`
- **Relevancia:** ★★★★ — Colegios generan tráfico peatonal predecible (mañana/tarde). Comercios de proximidad (papelerías, cafeterías) se benefician.
- **Uso propuesto:** Proximidad a colegios como feature para categorías comerciales específicas.

### 1.7 Bibliotecas (50 registros)
- **Fuente:** `bibliotecas.json`
- **Relevancia:** ★★★ — Punto de atracción cultural estable.

### 1.8 Centros de Mayores (94 registros)
- **Fuente:** `centros_mayores.json`
- **Relevancia:** ★★★ — Indicador demográfico implícito. Más centros = mayor población envejecida.

### 1.9 Centros de Servicios Sociales (40 registros)
- **Fuente:** `centros_servicios_sociales.json`
- **Relevancia:** ★★ — Puede indicar zonas con mayor vulnerabilidad social.

### 1.10 Aparcamientos Públicos (5 registros)
- **Fuente:** `aparcamientos_publicos.json`
- **Relevancia:** ★★ — Dataset muy pequeño, cobertura limitada.

### 1.11 Mercadillos de Vía Pública (33 registros)
- **Fuente:** `mercadillos_via_publica.json`
- **Relevancia:** ★★★ — Competencia directa potencial para comercio minorista, pero también atracción de público.

### 1.12 BiciMAD Estaciones (631 registros)
- **Fuente:** `bicimad_estaciones.json` + `bicimad_estaciones.csv`
- **Relevancia:** ★★★★ — Proxy de conectividad y movilidad sostenible. Estaciones BiciMAD ≈ zonas con alta demanda de transporte.
- **Uso propuesto:** Número de estaciones BiciMAD en radio de 300m como indicador de accesibilidad.

---

## 2. Panel de Indicadores de Distritos y Barrios (Dataset Estrella)

- **Archivo:** `panel_indicadores_2020_2025.csv` (30 MB, 116,930 filas)
- **Estructura:** `panel_indicadores_estructura.xlsx` (253 KB)
- **Granularidad:** Distrito + Barrio
- **Cobertura temporal:** 2008-2025 (18 años)
- **Relevancia:** ★★★★★

### Columnas
`Orden, Periodo panel, ciudad, cod_distrito, distrito, cod_barrio, barrio, año, fecha_indicador, fuente_indicador, categoría_1, categoría_2, indicador_nivel1, indicador_nivel2, indicador_nivel3, unidad_indicador, indicador_completo, valor_indicador`

### Categorías (19 únicas, 381 indicadores)
| Categoría | Contenido |
|---|---|
| Características Generales | Superficie, densidad |
| Población del distrito | Habitantes, estructura etaria, nacionalidades |
| Indicadores Económicos | Renta, valor catastral, PIB |
| Empresa y comercio | Locales, licencias comerciales, actividad empresarial |
| Indicadores Población desempleo | Paro registrado, tasa paro |
| Indicadores de Vulnerabilidad | Índice compuesto de vulnerabilidad |
| Índice de vulnerabilidad | Subíndices por esfera |
| Educación | Centros, matrículas, nivel educativo |
| Salud | Centros de salud, indicadores sanitarios |
| Servicios Sociales | Prestaciones, atenciones |
| Servicios y equipamientos | Equipamientos municipales |
| Vivienda | Precios, transacciones, alquiler |
| Seguridad | Índices de criminalidad |
| Medio ambiente y residuos | Contaminación, reciclaje, zonas verdes |
| Calidad de vida | Encuestas de satisfacción |
| Participación ciudadana | Datos electorales |
| Resultados Elecciones Locales | Votos, participación |
| Situación socioeconómica ante COVID-19 | Impacto pandemia |

### Uso propuesto
- **Features para modelo de supervivencia:** Renta media del barrio, tasa de paro, densidad de población, índice de vulnerabilidad, valor catastral
- **Contexto para oportunidades:** Mostrar indicadores socioeconómicos clave al usuario cuando consulta una oportunidad
- **Tendencia temporal:** Con datos 2008-2025 se puede derivar la tendencia del barrio (mejorando/empeorando)

---

## 3. IGUALA — Índice de Vulnerabilidad Territorial

6 archivos Excel con datos por distrito y barrio:

| Archivo | Contenido | Filas distrito | Filas barrio |
|---|---|---|---|
| `iguala_global_distritos.xlsx` | Índice agregado + subíndices | 106 | 656 |
| `iguala_economia_empleo.xlsx` | Paro larga duración, ingresos bajos | 106 | 656 |
| `iguala_bienestar_igualdad.xlsx` | Servicios sociales, igualdad | 106 | — |
| `iguala_medio_ambiente.xlsx` | Contaminación, zonas verdes, ruido | 106 | — |
| `iguala_educacion_cultura.xlsx` | Nivel educativo, equipamientos culturales | 106 | — |
| `iguala_salud.xlsx` | Indicadores sanitarios | 106 | — |

### Indicadores clave por barrio (iguala_global_distritos.xlsx / "Descriptivos barrios")
- Valor catastral medio (vivienda residencial)
- Renta neta media por hogar
- Tasa de población extranjera
- Edad media
- Tasa de personas mayores viviendo solas
- Tasa de dependencia

### Relevancia: ★★★★★
Complementa directamente el índice de riesgo contextual de las oportunidades. Los índices IGUALA dan una medida oficial de vulnerabilidad territorial que se puede usar como feature o como contexto informativo.

---

## 4. IAE — Impuesto Actividades Económicas (3 años)

| Archivo | Registros | Año |
|---|---|---|
| `iae_2023.csv` | ~150 | 2023 |
| `iae_2024.csv` | ~200 | 2024 |
| `iae_2025.csv` | ~194 | 2025 |

- **Columnas:** `ANUALIDAD, EPIGRAFE, DESCRIPCION_EPIGRAFE, CONTADOR_EMITIDOS`
- **Relevancia:** ★★★★ — El IAE contabiliza la actividad comercial efectiva por epígrafe. Permite saber cuántas empresas hay de cada tipo a nivel Madrid.
- **Uso propuesto:** Saturación de mercado por tipo de actividad. Comparar el epígrafe de una oportunidad contra el total de altas.
- **Nota:** Datos agregados a nivel ciudad, no por distrito/barrio.

---

## 5. Población por Distrito y Barrio

- **Archivo procesado:** `poblacion_distrito_barrio.csv` (1,071 registros)
- **Columnas:** `fecha, cod_municipio, municipio, cod_distrito, distrito, cod_barrio, barrio, num_personas, num_personas_hombres, num_personas_mujeres`
- **Relevancia:** ★★★★ — Dato base para calcular ratios (comercios/habitante, etc.)
- **Uso propuesto:** Normalizar cualquier indicador por población. Feature: habitantes por barrio.

---

## 6. Inspecciones de Consumo

- **Archivo procesado:** `inspecciones_consumo.csv` (4,219 registros, desde 2016)
- **Columnas:** `FECHA_DE_INSPECCION, DISTRITO, TIPO_VIAL, NOMBRE_VIA, NUMERO_VIA, ACTIVIDAD_INSPECTORA, AMBITO, EPIGRAFE`
- **Relevancia:** ★★★ — Indica la actividad reguladora por zona. Zonas con más inspecciones = más dinámica comercial O más problemas.
- **Uso propuesto:** Conteo de inspecciones por distrito como indicador de actividad comercial. Puede usarse como señal complementaria.

---

## 7. Datasets Raw Adicionales (sin procesar en CSVs pero descargados)

| Archivo | Tamaño | Contenido |
|---|---|---|
| `inventario_zonas_verdes.csv` | 8.5 MB | 1,068 registros con distrito, denominación, superficie |
| `superficie_parques_zonas_verdes.csv` | 0.7 KB | 34 registros superficie verde por distrito |
| `ranking_vulnerabilidad.csv` | 2.1 KB | 63 registros ranking vulnerabilidad distritos (multi-año) |

---

## 8. Datasets Buscados pero No Descargados

Estos datasets se buscaron pero no estaban disponibles o no tenían formato accesible:

| Dataset | Razón |
|---|---|
| Comercios centenarios | No encontrado como dataset descargable |
| Alojamientos turísticos | Formato XML complejo, sin CSV directo |
| Restaurantes turísticos | Formato XML complejo |
| Puntos de interés turístico | Formato XML complejo |
| Ocio nocturno | Formato XML complejo |
| Delimitación de barrios (GeoJSON) | URL no resuelta correctamente |
| Inspecciones urbanísticas | Sin CSV disponible |
| Inspecciones LEPAR | Sin CSV disponible |
| Paradas de taxi | Sin recurso descargable |

---

## 9. Estructura de Archivos

```
storage/data/external/
├── processed/                              # Archivos transformados listos para usar
│   ├── unified_equipamientos_geo.csv       # 2,129 puntos (category, title, lat, lon, ...)
│   ├── equipamiento_mercados.csv
│   ├── equipamiento_parques.csv
│   ├── equipamiento_centros_culturales.csv
│   ├── equipamiento_instalaciones_deportivas.csv
│   ├── equipamiento_polideportivos.csv
│   ├── equipamiento_colegios.csv
│   ├── equipamiento_bibliotecas.csv
│   ├── equipamiento_centros_mayores.csv
│   ├── equipamiento_servicios_sociales.csv
│   ├── equipamiento_aparcamientos.csv
│   ├── equipamiento_mercadillos.csv
│   ├── equipamiento_bicimad.csv
│   ├── iae_empresas_2025.csv
│   ├── poblacion_distrito_barrio.csv
│   ├── inspecciones_consumo.csv
│   └── _processing_report.json
├── panel_indicadores_2020_2025.csv         # 30 MB, 116K filas (raw, muy grande)
├── panel_indicadores_estructura.xlsx
├── iguala_global_distritos.xlsx             # Índice vulnerabilidad global
├── iguala_economia_empleo.xlsx
├── iguala_bienestar_igualdad.xlsx
├── iguala_medio_ambiente.xlsx
├── iguala_educacion_cultura.xlsx
├── iguala_salud.xlsx
├── inventario_zonas_verdes.csv             # 8.5 MB, 1,068 registros
├── superficie_parques_zonas_verdes.csv
├── ranking_vulnerabilidad.csv
├── iae_2023.csv / iae_2024.csv / iae_2025.csv
└── [archivos JSON raw originales]
```

---

## 10. Recomendaciones de Integración (Próximos Pasos)

### Prioridad Alta
1. **Panel de Indicadores → Features modelo supervivencia:** Extraer renta_media, tasa_paro, índice_vulnerabilidad por barrio y unir al ABT.
2. **Equipamientos geocodificados → Capa de mapa:** Mostrar los 2,129 puntos como capas opcionales en el mapa de oportunidades.
3. **IGUALA → Contexto de oportunidad:** Mostrar subíndices de vulnerabilidad del distrito/barrio en la ficha de cada oportunidad.

### Prioridad Media
4. **BiciMAD + Mercados + Colegios → Features proximity:** Calcular distancia a la estación BiciMAD/mercado/colegio más cercano para cada oportunidad.
5. **IAE → Saturación de mercado:** Comparar el tipo de negocio recomendado contra el total de emitidos del IAE.
6. **Población → Normalización:** Ratios per-capita de cualquier indicador.

### Prioridad Baja
7. **Inspecciones consumo → Señal complementaria:** Actividad reguladora por distrito.
8. **Inventario zonas verdes → Detalle:** Complementar parques con superficie real.
9. **IGUALA detallado → Features adicionales:** Extraer indicadores específicos de cada esfera.

---

## 11. Claves de Unión con Datos Existentes

| Dataset externo | Clave de unión | Mapea a |
|---|---|---|
| Panel indicadores | `cod_distrito` (1-21), `cod_barrio` | `district_code`, `barrio_code` en ABT |
| IGUALA | `Codigo distrito`, `Código barrio` | `district_code`, `barrio_code` |
| Equipamientos | `lat`, `lon` | Spatial join a `section_key` o cálculo de distancia |
| BiciMAD | `lat`, `lon` | Spatial join o proximity |
| IAE | Nivel ciudad | Lookup global |
| Población | `cod_distrito`, `cod_barrio` | `district_code`, `barrio_code` |
| Inspecciones | `DISTRITO` (nombre) | Requiere mapeo nombre→código |

---

## Scripts Creados

- `back/scripts/download_external_datasets.py` — Descarga los 29 archivos desde datos.madrid.es
- `back/scripts/transform_external_datasets.py` — Transforma raw → CSVs estandarizados en `storage/data/external/processed/`
