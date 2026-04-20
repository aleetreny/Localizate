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
    min_interval_seconds: float = 11.0
    timeout_seconds: float = 90.0
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
        self._last_request_started_at: float | None = None

    @property
    def request_count(self) -> int:
        return self._request_count

    @property
    def content_endpoint_url(self) -> str:
        return (
            "https://api.cloudflare.com/client/v4/accounts/"
            f"{self.config.account_id}/browser-rendering/content"
        )

    def fetch_html(self, url: str) -> str:
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
        response.raise_for_status()

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

    def _respect_min_interval(self) -> None:
        now = self._monotonic()
        if self._last_request_started_at is not None:
            elapsed = now - self._last_request_started_at
            remaining = self.config.min_interval_seconds - elapsed
            if remaining > 0:
                self._sleep(remaining)
        self._last_request_started_at = self._monotonic()
