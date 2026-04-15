from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd

from .censo import build_censo_snapshot_manifest, load_raw_manifest
from .censo_profile import materialize_and_profile_censo_period
from .paths import DATA_DIR


TransitionPolicy = Literal["skip", "assume_etrs89", "assume_ed50"]


@dataclass(frozen=True)
class CensoGeospatialConfig:
    h3_resolution: int = 10
    transition_policy: TransitionPolicy = "skip"


def transform_locales_geospatial_frame(
    frame: pd.DataFrame,
    *,
    config: CensoGeospatialConfig = CensoGeospatialConfig(),
) -> pd.DataFrame:
    transformed = frame.copy()

    transformed["lat_wgs84"] = pd.NA
    transformed["lon_wgs84"] = pd.NA
    transformed["h3_cell"] = pd.NA
    transformed["h3_resolution"] = pd.NA
    transformed["coord_transform_status"] = "missing_input"

    if "x_utm_best" not in transformed.columns or "y_utm_best" not in transformed.columns:
        return transformed

    has_xy = transformed["x_utm_best"].notna() & transformed["y_utm_best"].notna()
    transformed.loc[has_xy, "coord_transform_status"] = "pending_crs_resolution"

    def _transform_subset(mask: pd.Series, source_epsg: str) -> None:
        if not bool(mask.any()):
            return
        lon, lat = _utm_to_wgs84(
            transformed.loc[mask, "x_utm_best"],
            transformed.loc[mask, "y_utm_best"],
            source_epsg=source_epsg,
        )
        transformed.loc[mask, "lon_wgs84"] = lon
        transformed.loc[mask, "lat_wgs84"] = lat
        transformed.loc[mask, "coord_transform_status"] = "transformed"

    mask_ed50 = has_xy & transformed["coord_crs_status"].eq("ed50_utm30")
    mask_etrs = has_xy & transformed["coord_crs_status"].eq("etrs89_utm30")
    mask_transition = has_xy & transformed["coord_crs_status"].eq("transition_2017_09")

    _transform_subset(mask_ed50, "EPSG:23030")
    _transform_subset(mask_etrs, "EPSG:25830")

    if config.transition_policy == "assume_etrs89":
        _transform_subset(mask_transition, "EPSG:25830")
        transformed.loc[mask_transition, "coord_transform_status"] = "transformed_transition_assume_etrs89"
    elif config.transition_policy == "assume_ed50":
        _transform_subset(mask_transition, "EPSG:23030")
        transformed.loc[mask_transition, "coord_transform_status"] = "transformed_transition_assume_ed50"
    else:
        transformed.loc[mask_transition, "coord_transform_status"] = "transition_requires_review"

    h3_mask = transformed["lat_wgs84"].notna() & transformed["lon_wgs84"].notna()
    if bool(h3_mask.any()):
        transformed.loc[h3_mask, "h3_cell"] = _latlon_to_h3(
            transformed.loc[h3_mask, "lat_wgs84"],
            transformed.loc[h3_mask, "lon_wgs84"],
            resolution=config.h3_resolution,
        )
        transformed.loc[h3_mask, "h3_resolution"] = config.h3_resolution

    return transformed


def ensure_locales_period_normalized(
    period: str,
    snapshot_manifest: pd.DataFrame,
    *,
    normalized_root: Path | None = None,
    force_rematerialize: bool = False,
) -> Path:
    resolved_root = normalized_root or (DATA_DIR / "intermediate" / "censo_snapshots")
    target_path = resolved_root / "locales" / f"{period}.csv.gz"
    if target_path.exists() and not force_rematerialize:
        return target_path

    if force_rematerialize and target_path.exists():
        target_path.unlink()

    materialize_and_profile_censo_period(
        period,
        snapshot_manifest,
        output_root=resolved_root,
        skip_existing=False,
    )
    if not target_path.exists():
        raise FileNotFoundError(f"Unable to materialize normalized locales period {period}")
    return target_path


def build_censo_geospatial_period(
    period: str,
    *,
    snapshot_manifest: pd.DataFrame | None = None,
    normalized_root: Path | None = None,
    output_root: Path | None = None,
    config: CensoGeospatialConfig = CensoGeospatialConfig(),
) -> tuple[pd.DataFrame, Path]:
    manifest = snapshot_manifest
    if manifest is None:
        raw_manifest = load_raw_manifest()
        manifest = build_censo_snapshot_manifest(raw_manifest)

    locales_path = ensure_locales_period_normalized(period, manifest, normalized_root=normalized_root)
    try:
        frame = pd.read_csv(locales_path, low_memory=False)
    except Exception:
        locales_path = ensure_locales_period_normalized(
            period,
            manifest,
            normalized_root=normalized_root,
            force_rematerialize=True,
        )
        try:
            frame = pd.read_csv(locales_path, low_memory=False)
        except Exception as retry_exc:
            raise RuntimeError(
                f"Unable to read normalized locales snapshot for period {period} after rematerialization"
            ) from retry_exc

    transformed = transform_locales_geospatial_frame(frame, config=config)

    resolved_output_root = output_root or (DATA_DIR / "processed" / "censo_geospatial" / "locales")
    resolved_output_root.mkdir(parents=True, exist_ok=True)
    output_path = resolved_output_root / f"{period}.csv.gz"
    transformed.to_csv(output_path, index=False, compression="gzip")
    return transformed, output_path


def _utm_to_wgs84(x: pd.Series, y: pd.Series, *, source_epsg: str) -> tuple[pd.Series, pd.Series]:
    try:
        from pyproj import Transformer
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("pyproj is required for CRS transformation") from exc

    transformer = Transformer.from_crs(source_epsg, "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(x.to_numpy(), y.to_numpy())
    return pd.Series(lon, index=x.index), pd.Series(lat, index=y.index)


def _latlon_to_h3(lat: pd.Series, lon: pd.Series, *, resolution: int) -> pd.Series:
    try:
        import h3
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("h3 package is required for H3 indexing") from exc

    if hasattr(h3, "latlng_to_cell"):
        return pd.Series(
            [h3.latlng_to_cell(float(lat_value), float(lon_value), resolution) for lat_value, lon_value in zip(lat, lon)],
            index=lat.index,
        )

    if hasattr(h3, "geo_to_h3"):
        return pd.Series(
            [h3.geo_to_h3(float(lat_value), float(lon_value), resolution) for lat_value, lon_value in zip(lat, lon)],
            index=lat.index,
        )

    raise AttributeError("Unsupported h3 python API: missing latlng_to_cell/geo_to_h3")
