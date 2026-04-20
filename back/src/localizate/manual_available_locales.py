from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import json
from pathlib import Path
import re
import time
from typing import Any, Iterable, Sequence
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .paths import DATA_DIR
from .section_geography import load_section_geodataframe
from .section_keys import normalize_section_key_series


LOCALES_ES_BASE_URL = "https://www.locales.es"
LOCALES_ES_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
)
LOCALES_ES_BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": f"{LOCALES_ES_BASE_URL}/",
    "Upgrade-Insecure-Requests": "1",
}
NOMINATIM_USER_AGENT = "LocalizateManualLocales-Geocoder/1.0 (+manual extraction for research)"
MADRID_BBOX = {
    "min_lon": -3.8885,
    "max_lon": -3.5174,
    "min_lat": 40.3121,
    "max_lat": 40.6437,
}
OUTPUT_COLUMNS = [
    "source_portal",
    "city_slug",
    "operation",
    "page_number",
    "listing_id",
    "listing_key",
    "listing_url",
    "contact_url",
    "card_title",
    "detail_title",
    "product_name",
    "listing_type",
    "advertiser_type",
    "price_eur",
    "price_per_m2_eur",
    "area_m2",
    "bathroom_count",
    "tag_list",
    "description_short",
    "description_full",
    "breadcrumb_zone",
    "breadcrumb_path",
    "address_text",
    "geocode_query",
    "geocode_status",
    "coord_source",
    "coord_precision",
    "geocode_display_name",
    "lat_wgs84",
    "lon_wgs84",
    "h3_cell",
    "h3_resolution",
    "section_key",
    "district_code",
    "district_name",
    "barrio_code",
    "barrio_name",
    "published_at",
    "modified_at",
    "detail_fetch_status",
]
TEXT_COLUMNS = {
    "source_portal",
    "city_slug",
    "operation",
    "listing_id",
    "listing_key",
    "listing_url",
    "contact_url",
    "card_title",
    "detail_title",
    "product_name",
    "listing_type",
    "advertiser_type",
    "tag_list",
    "description_short",
    "description_full",
    "breadcrumb_zone",
    "breadcrumb_path",
    "address_text",
    "geocode_query",
    "geocode_status",
    "coord_source",
    "coord_precision",
    "geocode_display_name",
    "h3_cell",
    "section_key",
    "district_code",
    "district_name",
    "barrio_code",
    "barrio_name",
    "published_at",
    "modified_at",
    "detail_fetch_status",
}
NUMERIC_COLUMNS = {
    "page_number",
    "price_eur",
    "price_per_m2_eur",
    "area_m2",
    "bathroom_count",
    "lat_wgs84",
    "lon_wgs84",
    "h3_resolution",
}


@dataclass(frozen=True)
class ManualAvailableLocalesConfig:
    city_slug: str = "madrid"
    operations: tuple[str, ...] = ("venta", "alquiler")
    max_pages: int = 250
    max_listings: int | None = None
    resume_from_raw: bool = False
    request_delay_seconds: float = 0.25
    request_timeout_seconds: float = 30.0
    geocode_enabled: bool = True
    geocode_delay_seconds: float = 1.1
    geocode_email: str | None = None
    h3_resolution: int = 10


def build_manual_available_locales_dataset(
    config: ManualAvailableLocalesConfig,
    *,
    output_path: Path,
    raw_output_path: Path,
    summary_path: Path,
    geocode_cache_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    listing_session = _build_locales_es_session()
    geocode_session = _build_http_session(
        user_agent=NOMINATIM_USER_AGENT,
    )

    if config.resume_from_raw and raw_output_path.exists():
        listings = pd.read_csv(raw_output_path, low_memory=False)
    else:
        listings = crawl_locales_es_listings(listing_session, config=config)

        raw_output_path.parent.mkdir(parents=True, exist_ok=True)
        listings.to_csv(raw_output_path, index=False)

    if config.max_listings is not None:
        listings = listings.head(config.max_listings).reset_index(drop=True)

    enriched = enrich_locales_listings(
        listings,
        config=config,
        listing_session=listing_session,
        geocode_session=geocode_session,
        geocode_cache_path=geocode_cache_path,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(output_path, index=False)

    summary = build_manual_available_locales_summary(enriched, config=config)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return enriched, summary


def crawl_locales_es_listings(
    session: requests.Session,
    *,
    config: ManualAvailableLocalesConfig,
) -> pd.DataFrame:
    operations = _normalize_operations(config.operations)
    if not operations:
        raise ValueError("At least one operation must be provided")

    seen_keys: set[str] = set()
    records: list[dict[str, Any]] = []
    consecutive_empty_pages = 0

    for operation in operations:
        for page_number in range(1, config.max_pages + 1):
            page_url = build_locales_search_url(config.city_slug, operation, page_number)
            html = _fetch_html(session, page_url, timeout_seconds=config.request_timeout_seconds)
            page_records = extract_listing_cards(
                html,
                city_slug=config.city_slug,
                operation=operation,
                page_number=page_number,
            )
            fresh_records = [record for record in page_records if record["listing_key"] not in seen_keys]

            if not fresh_records:
                consecutive_empty_pages += 1
            else:
                consecutive_empty_pages = 0

            for record in fresh_records:
                seen_keys.add(record["listing_key"])
                records.append(record)

            if consecutive_empty_pages >= 2:
                consecutive_empty_pages = 0
                break

            time.sleep(config.request_delay_seconds)

    if not records:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    frame = pd.DataFrame.from_records(records)
    frame = frame.sort_values(["operation", "page_number", "listing_id"]).reset_index(drop=True)
    return _finalize_output_columns(frame)


def build_locales_search_url(city_slug: str, operation: str, page_number: int) -> str:
    return f"{LOCALES_ES_BASE_URL}/{city_slug}/{operation}/locales?page={page_number}"


def extract_listing_cards(
    html: str,
    *,
    city_slug: str,
    operation: str,
    page_number: int,
) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []

    for card in soup.select(".js-card"):
        anchor = card.select_one("a.card__link[href*='/local']")
        if anchor is None:
            continue

        href = _normalize_whitespace(anchor.get("href"))
        if not href:
            continue
        if not href.startswith(f"/{city_slug}/"):
            continue

        absolute_url = urljoin(LOCALES_ES_BASE_URL, href)
        listing_id = _extract_listing_id(absolute_url)
        if listing_id is None:
            continue

        card_title = _first_non_empty_text(
            card.select_one(".card__caption"),
            anchor,
        )
        description_short = _node_text(card.select_one(".card__article"))
        price_text = _node_text(card.select_one(".card__heading"))
        price_per_m2_text = _node_text(card.select_one(".card_price2"))

        metrics = _extract_card_metrics(card)
        tags = [_normalize_whitespace(tag.get_text(" ", strip=True)) for tag in card.select(".badge.badge_transparent")]
        tags = [tag for tag in tags if tag]

        contact_anchor = card.select_one("a[href*='/contactar/propietario/']")
        contact_href = _normalize_whitespace(contact_anchor.get("href")) if contact_anchor is not None else None

        records.append(
            {
                "source_portal": "locales.es",
                "city_slug": city_slug,
                "operation": operation,
                "page_number": page_number,
                "listing_id": listing_id,
                "listing_key": f"{operation}:{listing_id}",
                "listing_url": absolute_url,
                "contact_url": urljoin(LOCALES_ES_BASE_URL, contact_href) if contact_href else pd.NA,
                "card_title": card_title,
                "detail_title": pd.NA,
                "product_name": pd.NA,
                "listing_type": _normalize_listing_type(card_title),
                "advertiser_type": _node_text(card.select_one(".card__badge")),
                "price_eur": _parse_number(price_text),
                "price_per_m2_eur": _parse_number(price_per_m2_text),
                "area_m2": metrics.get("area_m2"),
                "bathroom_count": metrics.get("bathroom_count"),
                "tag_list": " | ".join(tags) if tags else pd.NA,
                "description_short": description_short,
                "description_full": pd.NA,
                "breadcrumb_zone": pd.NA,
                "breadcrumb_path": pd.NA,
                "address_text": _extract_address_text(card_title),
                "geocode_query": pd.NA,
                "geocode_status": pd.NA,
                "coord_source": pd.NA,
                "coord_precision": pd.NA,
                "geocode_display_name": pd.NA,
                "lat_wgs84": pd.NA,
                "lon_wgs84": pd.NA,
                "h3_cell": pd.NA,
                "h3_resolution": pd.NA,
                "section_key": pd.NA,
                "district_code": pd.NA,
                "district_name": pd.NA,
                "barrio_code": pd.NA,
                "barrio_name": pd.NA,
                "published_at": pd.NA,
                "modified_at": pd.NA,
                "detail_fetch_status": "pending",
            }
        )

    return records


def enrich_locales_listings(
    listings: pd.DataFrame,
    *,
    config: ManualAvailableLocalesConfig,
    listing_session: requests.Session,
    geocode_session: requests.Session,
    geocode_cache_path: Path,
) -> pd.DataFrame:
    if listings.empty:
        return _finalize_output_columns(listings.copy())

    enriched = _prepare_frame_for_enrichment(listings)

    for index, row in enriched.iterrows():
        try:
            html = _fetch_html(
                listing_session,
                row["listing_url"],
                timeout_seconds=config.request_timeout_seconds,
            )
            detail_record = extract_listing_detail(row.to_dict(), html)
            for key, value in detail_record.items():
                enriched.at[index, key] = value
            enriched.at[index, "detail_fetch_status"] = "ok"
        except Exception as exc:
            enriched.at[index, "detail_fetch_status"] = f"error:{type(exc).__name__}"
        time.sleep(config.request_delay_seconds)

    if config.geocode_enabled:
        cache = _load_geocode_cache(geocode_cache_path)
        _geocode_locales_listings(
            enriched,
            session=geocode_session,
            geocode_cache_path=geocode_cache_path,
            cache=cache,
            geocode_delay_seconds=config.geocode_delay_seconds,
            geocode_email=config.geocode_email,
            city_slug=config.city_slug,
        )

    _assign_h3_cells(enriched, resolution=config.h3_resolution)
    _assign_section_geography(enriched)
    return _finalize_output_columns(enriched)


def extract_listing_detail(base_record: dict[str, Any], html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    json_ld_documents = _extract_json_ld_documents(soup)

    web_page = _first_json_ld_document(json_ld_documents, "WebPage")
    product = _first_json_ld_document(json_ld_documents, "Product")
    breadcrumb = _first_json_ld_document(json_ld_documents, "BreadcrumbList")

    card_title = _string_or_na(base_record.get("card_title"))
    detail_title = _clean_detail_title(_value_or_none(web_page.get("name") if isinstance(web_page, dict) else None))
    product_name = _value_or_none(product.get("name") if isinstance(product, dict) else None)
    breadcrumb_names = _extract_breadcrumb_names(breadcrumb)
    breadcrumb_zone = _extract_breadcrumb_zone(breadcrumb_names)
    description_full = _normalize_whitespace(_value_or_none(product.get("description") if isinstance(product, dict) else None))

    record = {
        "detail_title": _na_if_missing(detail_title),
        "product_name": _na_if_missing(product_name),
        "listing_type": _first_non_empty_value(
            _normalize_listing_type(product_name),
            _normalize_listing_type(detail_title),
            _normalize_listing_type(card_title),
        ),
        "description_full": _na_if_missing(description_full),
        "breadcrumb_zone": _na_if_missing(breadcrumb_zone),
        "breadcrumb_path": _na_if_missing(" > ".join(breadcrumb_names) if breadcrumb_names else None),
        "published_at": _na_if_missing(_value_or_none(web_page.get("datePublished") if isinstance(web_page, dict) else None)),
        "modified_at": _na_if_missing(_value_or_none(web_page.get("dateModified") if isinstance(web_page, dict) else None)),
    }

    detail_price = _extract_offer_price(product)
    if pd.isna(base_record.get("price_eur")) and detail_price is not None:
        record["price_eur"] = detail_price

    record["address_text"] = _first_non_empty_value(
        _extract_address_text(card_title),
        _extract_address_text(detail_title),
        _build_address_from_breadcrumbs(breadcrumb_names),
        base_record.get("address_text"),
    )
    return record


def build_manual_available_locales_summary(
    frame: pd.DataFrame,
    *,
    config: ManualAvailableLocalesConfig,
) -> dict[str, Any]:
    operation_counts = (
        frame.groupby("operation", dropna=False).size().sort_index().astype(int).to_dict() if not frame.empty else {}
    )
    return {
        "generated_at_utc": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_portal": "locales.es",
        "city_slug": config.city_slug,
        "operations": list(_normalize_operations(config.operations)),
        "max_pages": int(config.max_pages),
        "listing_count": int(len(frame)),
        "unique_listing_ids": int(frame["listing_id"].nunique()) if not frame.empty else 0,
        "geocoded_count": int(frame["lat_wgs84"].notna().sum()) if "lat_wgs84" in frame.columns else 0,
        "street_precision_count": int(frame["coord_precision"].eq("street_approx").sum()) if "coord_precision" in frame.columns else 0,
        "zone_precision_count": int(frame["coord_precision"].eq("zone_approx").sum()) if "coord_precision" in frame.columns else 0,
        "h3_count": int(frame["h3_cell"].notna().sum()) if "h3_cell" in frame.columns else 0,
        "section_key_count": int(frame["section_key"].notna().sum()) if "section_key" in frame.columns else 0,
        "records_by_operation": operation_counts,
    }


def _build_locales_es_session() -> requests.Session:
    return _build_http_session(
        user_agent=LOCALES_ES_BROWSER_USER_AGENT,
        extra_headers=LOCALES_ES_BROWSER_HEADERS,
    )


def _build_http_session(
    *,
    user_agent: str,
    extra_headers: dict[str, str] | None = None,
) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    if extra_headers:
        headers.update(extra_headers)
    session.headers.update(headers)
    return session


def _fetch_html(session: requests.Session, url: str, *, timeout_seconds: float) -> str:
    response = session.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    return response.text


def _extract_card_metrics(card: BeautifulSoup) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    text_nodes = [_normalize_whitespace(node.get_text(" ", strip=True)) for node in card.select(".font-m span, .card__subhead span")]
    for text in text_nodes:
        if not text:
            continue
        if "m²" in text or "m2" in text:
            metrics["area_m2"] = _parse_number(text)
        elif "baño" in text.lower() or "aseo" in text.lower():
            metrics["bathroom_count"] = _parse_number(text)
    return metrics


def _extract_json_ld_documents(soup: BeautifulSoup) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for node in soup.select("script[type='application/ld+json']"):
        raw_content = node.string or node.get_text("", strip=True)
        raw_content = raw_content.strip()
        if not raw_content:
            continue
        try:
            payload = json.loads(raw_content)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            documents.extend([item for item in payload if isinstance(item, dict)])
        elif isinstance(payload, dict):
            documents.append(payload)
    return documents


def _first_json_ld_document(documents: Iterable[dict[str, Any]], target_type: str) -> dict[str, Any]:
    for document in documents:
        doc_type = document.get("@type")
        if isinstance(doc_type, list) and target_type in doc_type:
            return document
        if isinstance(doc_type, str) and doc_type == target_type:
            return document
    return {}


def _extract_breadcrumb_names(breadcrumb: dict[str, Any]) -> list[str]:
    if not isinstance(breadcrumb, dict):
        return []
    items = breadcrumb.get("itemListElement") or []
    names: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = _normalize_whitespace(item.get("name"))
        if name:
            names.append(name)
    return names


def _extract_breadcrumb_zone(names: Sequence[str]) -> str | None:
    filtered = [name for name in names if name.lower() not in {"madrid", "venta", "alquiler"}]
    if not filtered:
        return None
    return filtered[0]


def _build_address_from_breadcrumbs(names: Sequence[str]) -> str | None:
    zone = _extract_breadcrumb_zone(names)
    if not zone:
        return None
    return _normalize_geocode_query(f"{zone}, Madrid")


def _extract_offer_price(product: dict[str, Any]) -> float | None:
    if not isinstance(product, dict):
        return None
    offers = product.get("offers")
    if isinstance(offers, list) and offers:
        return _parse_number(offers[0].get("price"))
    if isinstance(offers, dict):
        return _parse_number(offers.get("price"))
    return None


def _geocode_locales_listings(
    frame: pd.DataFrame,
    *,
    session: requests.Session,
    geocode_cache_path: Path,
    cache: dict[str, dict[str, Any]],
    geocode_delay_seconds: float,
    geocode_email: str | None,
    city_slug: str,
) -> None:
    for index, row in frame.iterrows():
        candidates = _build_geocode_candidates(row)
        if not candidates:
            frame.at[index, "geocode_status"] = "missing_query"
            continue

        selected_result: dict[str, Any] | None = None
        selected_query: str | None = None

        for query in candidates:
            cached = cache.get(query)
            if cached is None:
                cached = _query_nominatim(
                    session,
                    query,
                    geocode_email=geocode_email,
                    city_slug=city_slug,
                )
                cache[query] = cached
                _write_geocode_cache(geocode_cache_path, cache)
                time.sleep(geocode_delay_seconds)

            if cached.get("geocode_status") == "ok":
                selected_result = cached
                selected_query = query
                break

            if selected_result is None:
                selected_result = cached
                selected_query = query

        if selected_result is None:
            frame.at[index, "geocode_status"] = "missing_query"
            continue

        frame.at[index, "geocode_query"] = _na_if_missing(selected_query)
        frame.at[index, "geocode_status"] = _na_if_missing(selected_result.get("geocode_status"))
        frame.at[index, "coord_source"] = _na_if_missing(selected_result.get("coord_source"))
        frame.at[index, "coord_precision"] = _na_if_missing(selected_result.get("coord_precision"))
        frame.at[index, "geocode_display_name"] = _na_if_missing(selected_result.get("geocode_display_name"))
        frame.at[index, "lat_wgs84"] = selected_result.get("lat_wgs84", pd.NA)
        frame.at[index, "lon_wgs84"] = selected_result.get("lon_wgs84", pd.NA)


def _build_geocode_candidates(row: pd.Series) -> list[str]:
    values = [
        row.get("address_text"),
        row.get("detail_title"),
        row.get("breadcrumb_zone"),
    ]
    candidates: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = _normalize_geocode_query(value)
        if not normalized or normalized in seen:
            continue
        candidates.append(normalized)
        seen.add(normalized)
    return candidates


def _normalize_geocode_query(value: object) -> str | None:
    text = _normalize_whitespace(value)
    if not text:
        return None
    text = _extract_address_text(text) or text
    text = text.replace("Comunitat de Madrid", "Madrid")
    text = re.sub(r"\bLO\d+\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s*,", ", ", text)
    text = text.strip(" ,")
    if not text:
        return None
    if "madrid" not in text.lower():
        text = f"{text}, Madrid"
    if "españa" not in text.lower() and "espana" not in text.lower():
        text = f"{text}, España"
    return _normalize_whitespace(text)


def _query_nominatim(
    session: requests.Session,
    query: str,
    *,
    geocode_email: str | None,
    city_slug: str,
) -> dict[str, Any]:
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "es",
        "accept-language": "es",
    }
    if geocode_email:
        params["email"] = geocode_email

    try:
        response = session.get("https://nominatim.openstreetmap.org/search", params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return {
            "query": query,
            "geocode_status": f"error:{type(exc).__name__}",
            "coord_source": "nominatim",
            "coord_precision": pd.NA,
            "geocode_display_name": pd.NA,
            "lat_wgs84": pd.NA,
            "lon_wgs84": pd.NA,
        }

    if not payload:
        return {
            "query": query,
            "geocode_status": "not_found",
            "coord_source": "nominatim",
            "coord_precision": pd.NA,
            "geocode_display_name": pd.NA,
            "lat_wgs84": pd.NA,
            "lon_wgs84": pd.NA,
        }

    result = payload[0]
    lat = _parse_number(result.get("lat"))
    lon = _parse_number(result.get("lon"))
    display_name = _normalize_whitespace(result.get("display_name"))

    if lat is None or lon is None:
        status = "missing_coordinates"
    elif not _is_in_city_scope(lat, lon, city_slug=city_slug):
        status = "outside_scope"
    else:
        status = "ok"

    coord_precision = _infer_coord_precision(result)
    return {
        "query": query,
        "geocode_status": status,
        "coord_source": "nominatim",
        "coord_precision": coord_precision,
        "geocode_display_name": _na_if_missing(display_name),
        "lat_wgs84": lat if status == "ok" else pd.NA,
        "lon_wgs84": lon if status == "ok" else pd.NA,
    }


def _infer_coord_precision(result: dict[str, Any]) -> str:
    addresstype = str(result.get("addresstype") or result.get("type") or "").strip().lower()
    if addresstype in {"house", "building", "road", "pedestrian", "commercial", "retail", "amenity"}:
        return "street_approx"
    if addresstype in {"suburb", "quarter", "neighbourhood", "city_district", "district", "administrative"}:
        return "zone_approx"
    return "unknown"


def _is_in_city_scope(lat: float, lon: float, *, city_slug: str) -> bool:
    if city_slug != "madrid":
        return True
    return (
        MADRID_BBOX["min_lon"] <= lon <= MADRID_BBOX["max_lon"]
        and MADRID_BBOX["min_lat"] <= lat <= MADRID_BBOX["max_lat"]
    )


def _load_geocode_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    frame = pd.read_csv(path, low_memory=False)
    cache: dict[str, dict[str, Any]] = {}
    for row in frame.to_dict(orient="records"):
        query = _normalize_whitespace(row.get("query"))
        if query:
            cache[query] = row
    return cache


def _write_geocode_cache(path: Path, cache: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cache:
        pd.DataFrame(columns=["query", "geocode_status", "coord_source", "coord_precision", "geocode_display_name", "lat_wgs84", "lon_wgs84"]).to_csv(path, index=False)
        return
    frame = pd.DataFrame.from_records(list(cache.values()))
    frame = frame.sort_values("query").drop_duplicates("query", keep="last")
    frame.to_csv(path, index=False)


def _assign_h3_cells(frame: pd.DataFrame, *, resolution: int) -> None:
    frame["h3_cell"] = frame["h3_cell"].astype("object")
    frame["h3_resolution"] = pd.to_numeric(frame["h3_resolution"], errors="coerce")

    valid_mask = frame["lat_wgs84"].notna() & frame["lon_wgs84"].notna() & frame["coord_precision"].eq("street_approx")
    if not bool(valid_mask.any()):
        return
    frame.loc[valid_mask, "h3_cell"] = _latlon_to_h3(
        frame.loc[valid_mask, "lat_wgs84"],
        frame.loc[valid_mask, "lon_wgs84"],
        resolution=resolution,
    )
    frame.loc[valid_mask, "h3_resolution"] = resolution


def _assign_section_geography(frame: pd.DataFrame) -> None:
    for column in ["section_key", "district_code", "district_name", "barrio_code", "barrio_name"]:
        frame[column] = frame[column].astype("object")

    valid_mask = frame["lat_wgs84"].notna() & frame["lon_wgs84"].notna() & frame["coord_precision"].eq("street_approx")
    if not bool(valid_mask.any()):
        return

    try:
        import geopandas as gpd
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("geopandas is required to assign section geography") from exc

    sections = load_section_geodataframe()
    sections = sections.copy()
    sections["section_key"] = normalize_section_key_series(sections["COD_SECCIO"])
    sections["district_code"] = sections["COD_DIS"].astype("string").str.strip().replace({"": pd.NA}).str.zfill(2)
    sections["district_name"] = sections["NOM_DIS"].astype("string").str.strip().replace({"": pd.NA})
    sections["barrio_code"] = sections["COD_BAR"].astype("string").str.strip().replace({"": pd.NA}).str.zfill(3)
    sections["barrio_name"] = sections["NOM_BAR"].astype("string").str.strip().replace({"": pd.NA})
    sections = sections[["section_key", "district_code", "district_name", "barrio_code", "barrio_name", "geometry"]]
    sections = sections.dropna(subset=["section_key", "geometry"])
    sections = sections.to_crs("EPSG:4326")
    sections = sections.dissolve(
        by="section_key",
        aggfunc={
            "district_code": "first",
            "district_name": "first",
            "barrio_code": "first",
            "barrio_name": "first",
        },
    ).reset_index()

    point_rows = frame.loc[valid_mask, ["lat_wgs84", "lon_wgs84"]].copy()
    point_rows["row_id"] = point_rows.index
    points = gpd.GeoDataFrame(
        point_rows,
        geometry=gpd.points_from_xy(point_rows["lon_wgs84"], point_rows["lat_wgs84"]),
        crs="EPSG:4326",
    )
    joined = points.sjoin(sections, how="left", predicate="within")
    joined = joined.sort_values(["row_id", "section_key"]).drop_duplicates("row_id", keep="first")

    for row_id, row in joined.set_index("row_id").iterrows():
        frame.at[row_id, "section_key"] = row.get("section_key", pd.NA)
        frame.at[row_id, "district_code"] = row.get("district_code", pd.NA)
        frame.at[row_id, "district_name"] = row.get("district_name", pd.NA)
        frame.at[row_id, "barrio_code"] = row.get("barrio_code", pd.NA)
        frame.at[row_id, "barrio_name"] = row.get("barrio_name", pd.NA)


def _latlon_to_h3(lat: pd.Series, lon: pd.Series, *, resolution: int) -> pd.Series:
    try:
        import h3
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("h3 is required to compute H3 cells") from exc

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


def _extract_address_text(value: object) -> str | None:
    text = _normalize_whitespace(value)
    if not text:
        return None
    patterns = [
        r"\ben\s+venta\s+en\s+(.+)$",
        r"\ben\s+alquiler\s+en\s+(.+)$",
        r"\ben\s+la\s+zona\s+de\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            candidate = _normalize_whitespace(match.group(1))
            if candidate:
                candidate = re.sub(r"\bLO\d+\b", "", candidate, flags=re.IGNORECASE)
                candidate = candidate.replace("Comunitat de Madrid", "Madrid")
                return candidate.strip(" ,")
    return text


def _clean_detail_title(value: object) -> str | None:
    title = _normalize_whitespace(value)
    if not title:
        return None
    title = title.replace("Comunitat de Madrid", "Madrid")
    title = re.sub(r"\bLO\d+\b", "", title, flags=re.IGNORECASE)
    return title.strip(" ,")


def _normalize_listing_type(value: object) -> str | None:
    text = _normalize_whitespace(value)
    if not text:
        return None
    lowered = text.lower()
    if "local comercial" in lowered:
        return "local_comercial"
    if re.search(r"\bnave\b", lowered):
        return "nave"
    if re.search(r"\boficina\b", lowered):
        return "oficina"
    return None


def _extract_listing_id(url: str) -> str | None:
    match = re.search(r"local(\d+)", url, flags=re.IGNORECASE)
    if match is None:
        return None
    return match.group(1)


def _parse_number(value: object) -> float | None:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (int, float)) and not pd.isna(value):
        return float(value)
    text = _normalize_whitespace(value)
    if not text:
        return None
    match = re.search(r"[-+]?\d[\d\s.,]*", text)
    if match is None:
        return None
    token = match.group(0).replace("\xa0", "").replace(" ", "")
    if token.count(",") > 0 and token.count(".") > 0:
        if token.rfind(",") > token.rfind("."):
            token = token.replace(".", "").replace(",", ".")
        else:
            token = token.replace(",", "")
    elif token.count(",") == 1 and token.count(".") == 0:
        token = token.replace(",", ".")
    else:
        token = token.replace(",", "")
    try:
        return float(token)
    except ValueError:
        return None


def _first_non_empty_text(*nodes: Any) -> str | None:
    for node in nodes:
        text = _node_text(node)
        if text:
            return text
    return None


def _node_text(node: Any) -> str | None:
    if node is None:
        return None
    if hasattr(node, "get_text"):
        return _normalize_whitespace(node.get_text(" ", strip=True))
    return _normalize_whitespace(node)


def _first_non_empty_value(*values: object) -> Any:
    for value in values:
        normalized = _value_or_none(value)
        if normalized is not None:
            return normalized
    return pd.NA


def _value_or_none(value: object) -> Any:
    if value is None:
        return None
    if value is pd.NA:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, str):
        normalized = _normalize_whitespace(value)
        return normalized if normalized else None
    return value


def _string_or_na(value: object) -> str | None:
    normalized = _value_or_none(value)
    if normalized is None:
        return None
    return str(normalized)


def _na_if_missing(value: object) -> object:
    normalized = _value_or_none(value)
    if normalized is None:
        return pd.NA
    return normalized


def _prepare_frame_for_enrichment(frame: pd.DataFrame) -> pd.DataFrame:
    prepared = frame.copy()

    for column in OUTPUT_COLUMNS:
        if column not in prepared.columns:
            prepared[column] = pd.NA

    for column in TEXT_COLUMNS:
        if column in prepared.columns:
            prepared[column] = prepared[column].astype("object")

    for column in NUMERIC_COLUMNS:
        if column in prepared.columns:
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce")

    return prepared


def _normalize_whitespace(value: object) -> str | None:
    if value is None:
        return None
    if value is pd.NA:
        return None
    text = unescape(str(value))
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _normalize_operations(operations: Sequence[str]) -> tuple[str, ...]:
    normalized = []
    for operation in operations:
        value = _normalize_whitespace(operation)
        if not value:
            continue
        lowered = value.lower()
        if lowered not in normalized:
            normalized.append(lowered)
    return tuple(normalized)


def _finalize_output_columns(frame: pd.DataFrame) -> pd.DataFrame:
    finalized = frame.copy()
    for column in OUTPUT_COLUMNS:
        if column not in finalized.columns:
            finalized[column] = pd.NA
    return finalized[OUTPUT_COLUMNS]
