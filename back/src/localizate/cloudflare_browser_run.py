from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Callable

import requests


class BrowserRunBudgetExceeded(RuntimeError):
    """Raised when the conservative Browser Run budget would be exceeded."""


@dataclass(frozen=True)
class CloudflareBrowserRunConfig:
    account_id: str
    api_token: str
    max_requests: int = 24
    min_interval_seconds: float = 15.0
    timeout_seconds: float = 90.0
    max_browser_ms_per_run: int = 240_000
    max_rate_limit_retries: int = 2
    rate_limit_buffer_seconds: float = 5.0
    wait_until: str = "networkidle2"
    reject_resource_types: tuple[str, ...] = ("image", "media", "font")


class CloudflareBrowserRunClient:
    def __init__(
        self,
        config: CloudflareBrowserRunConfig,
        *,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self._session = session or requests.Session()
        self._sleep = sleep
        self._monotonic = monotonic
        self._request_count = 0
        self._browser_ms_used_total = 0
        self._last_request_started_at: float | None = None

    @property
    def request_count(self) -> int:
        return self._request_count

    @property
    def browser_ms_used_total(self) -> int:
        return self._browser_ms_used_total

    @property
    def content_endpoint_url(self) -> str:
        return (
            "https://api.cloudflare.com/client/v4/accounts/"
            f"{self.config.account_id}/browser-rendering/content"
        )

    def fetch_html(self, url: str) -> str:
        rate_limit_attempt = 0
        while True:
            self._enforce_budget()
            self._respect_min_interval()

            response = self._session.post(
                self.content_endpoint_url,
                json={
                    "url": url,
                    "gotoOptions": {"waitUntil": self.config.wait_until},
                    "rejectResourceTypes": list(self.config.reject_resource_types),
                },
                headers={
                    "Authorization": f"Bearer {self.config.api_token}",
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout_seconds,
            )
            self._request_count += 1

            if response.status_code == 429:
                rate_limit_attempt += 1
                if rate_limit_attempt > self.config.max_rate_limit_retries:
                    raise BrowserRunBudgetExceeded(
                        "Cloudflare Browser Run rate-limited this refresh repeatedly "
                        f"after {self._request_count} requests."
                    )
                retry_after_seconds = self._parse_retry_after_seconds(response)
                wait_seconds = max(
                    retry_after_seconds,
                    self.config.min_interval_seconds + self.config.rate_limit_buffer_seconds,
                )
                self._sleep(wait_seconds)
                continue

            response.raise_for_status()
            self._record_browser_ms(response)

            payload = response.json()
            if not payload.get("success"):
                serialized = json.dumps(payload, ensure_ascii=False)
                raise RuntimeError(f"Browser Run returned success=false for {url}: {serialized}")

            result = payload.get("result")
            html = result.get("html") if isinstance(result, dict) else result
            html_text = str(html or "")
            if not html_text.strip():
                raise RuntimeError(f"Browser Run returned an empty HTML payload for {url}")
            return html_text

    def _enforce_budget(self) -> None:
        if self._request_count >= self.config.max_requests:
            raise BrowserRunBudgetExceeded(
                "Browser Run request budget exceeded "
                f"({self._request_count}/{self.config.max_requests})."
            )
        if self._browser_ms_used_total >= self.config.max_browser_ms_per_run:
            raise BrowserRunBudgetExceeded(
                "Browser Run time budget exceeded "
                f"({self._browser_ms_used_total}/{self.config.max_browser_ms_per_run} ms)."
            )

    def _respect_min_interval(self) -> None:
        now = self._monotonic()
        if self._last_request_started_at is not None:
            elapsed = now - self._last_request_started_at
            remaining = self.config.min_interval_seconds - elapsed
            if remaining > 0:
                self._sleep(remaining)
        self._last_request_started_at = self._monotonic()

    def _record_browser_ms(self, response: requests.Response) -> None:
        header_value = response.headers.get("X-Browser-Ms-Used")
        if not header_value:
            return
        try:
            browser_ms_used = int(float(header_value))
        except (TypeError, ValueError):
            return
        if browser_ms_used > 0:
            self._browser_ms_used_total += browser_ms_used

    def _parse_retry_after_seconds(self, response: requests.Response) -> float:
        header_value = response.headers.get("Retry-After")
        if not header_value:
            return self.config.min_interval_seconds + self.config.rate_limit_buffer_seconds
        try:
            parsed = float(header_value)
        except ValueError:
            return self.config.min_interval_seconds + self.config.rate_limit_buffer_seconds
        return max(parsed, 0.0)
