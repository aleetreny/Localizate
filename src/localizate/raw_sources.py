from dataclasses import dataclass, field


@dataclass(frozen=True)
class RawSourceSpec:
    name: str
    relative_dir: str
    period_granularity: str
    selection_strategy: str
    description: str
    preferred_filenames: tuple[str, ...] = ()
    preferred_suffixes: tuple[str, ...] = ()
    primary_extension: str | None = None
    required_sidecar_suffixes: tuple[str, ...] = field(default_factory=tuple)


RAW_SOURCE_SPECS: tuple[RawSourceSpec, ...] = (
    RawSourceSpec(
        name="locales",
        relative_dir="locales",
        period_granularity="monthly",
        selection_strategy="unique_per_period",
        description="Censo historico de locales, una fila por local.",
        preferred_suffixes=(".csv", ".txt"),
        primary_extension=".csv",
    ),
    RawSourceSpec(
        name="actividades",
        relative_dir="actividades",
        period_granularity="monthly",
        selection_strategy="unique_per_period",
        description="Censo historico de actividades, una fila por local y epigrafe.",
        preferred_suffixes=(".csv", ".txt"),
        primary_extension=".csv",
    ),
    RawSourceSpec(
        name="padron",
        relative_dir="padron",
        period_granularity="monthly",
        selection_strategy="prefer_suffix",
        description="Padron historico mensual por seccion censal y edad.",
        preferred_suffixes=(".csv", ".txt"),
        primary_extension=".csv",
    ),
    RawSourceSpec(
        name="avisos",
        relative_dir="avisos",
        period_granularity="yearly",
        selection_strategy="manual_review",
        description="Avisos historicos acumulados por anio; requiere enriquecer con metadatos CKAN para separar recibidos/resueltos.",
        preferred_suffixes=(".csv", ".txt"),
        primary_extension=".csv",
    ),
    RawSourceSpec(
        name="renta_media",
        relative_dir="Renta Media",
        period_granularity="static",
        selection_strategy="prefer_filename",
        description="Renta media por seccion del INE.",
        preferred_filenames=("Renta_media_secciones_limpio.csv", "Renta_media_secciones.csv"),
        preferred_suffixes=(".csv",),
        primary_extension=".csv",
    ),
    RawSourceSpec(
        name="metro_entradas",
        relative_dir="Metro",
        period_granularity="static",
        selection_strategy="prefer_filename",
        description="Entradas y accesos de metro y nodos de transporte.",
        preferred_filenames=("Entradas_metro_todas.csv", "Entradas_metro_principales.csv"),
        preferred_suffixes=(".csv",),
        primary_extension=".csv",
    ),
    RawSourceSpec(
        name="secciones_censales_json",
        relative_dir="Secciones censales json",
        period_granularity="static",
        selection_strategy="prefer_filename",
        description="Topologia JSON de secciones censales.",
        preferred_filenames=("Secciones_Censales.json.txt",),
        preferred_suffixes=(".txt", ".json"),
        primary_extension=".txt",
    ),
    RawSourceSpec(
        name="secciones_censales_shp",
        relative_dir="Secciones censales shp",
        period_granularity="static",
        selection_strategy="prefer_filename",
        description="Bundle shapefile de secciones censales.",
        preferred_filenames=("SECCIONES_CENSALES.shp",),
        preferred_suffixes=(".shp", ".dbf", ".shx", ".prj", ".cpg", ".sbn", ".sbx", ".xml"),
        primary_extension=".shp",
        required_sidecar_suffixes=(".dbf", ".shx", ".prj"),
    ),
)


RAW_SOURCE_SPECS_BY_NAME = {spec.name: spec for spec in RAW_SOURCE_SPECS}
