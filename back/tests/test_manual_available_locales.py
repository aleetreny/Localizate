from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest import mock

import requests


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.manual_available_locales import (  # noqa: E402
    LOCALES_ES_BASE_URL,
    LOCALES_ES_BROWSER_HEADERS,
    LOCALES_ES_BROWSER_USER_AGENT,
    NOMINATIM_USER_AGENT,
    _build_http_session,
    _build_locales_es_session,
    _fetch_html,
    _should_retry_with_curl,
)


class ManualAvailableLocalesSessionTests(unittest.TestCase):
    def test_locales_es_session_uses_browser_like_headers(self) -> None:
        session = _build_locales_es_session()

        self.assertEqual(session.headers["User-Agent"], LOCALES_ES_BROWSER_USER_AGENT)
        self.assertEqual(session.headers["Accept"], LOCALES_ES_BROWSER_HEADERS["Accept"])
        self.assertEqual(session.headers["Referer"], f"{LOCALES_ES_BASE_URL}/")
        self.assertEqual(session.headers["Upgrade-Insecure-Requests"], "1")

    def test_generic_http_session_keeps_custom_user_agent(self) -> None:
        session = _build_http_session(user_agent=NOMINATIM_USER_AGENT)

        self.assertEqual(session.headers["User-Agent"], NOMINATIM_USER_AGENT)
        self.assertEqual(session.headers["Accept"], "*/*")
        self.assertNotIn("Referer", session.headers)

    def test_should_retry_with_curl_for_cloudflare_challenge(self) -> None:
        response = mock.Mock()
        response.status_code = 403
        response.headers = {"Cf-Mitigated": "challenge"}
        response.text = "<html><title>Just a moment...</title></html>"

        self.assertTrue(_should_retry_with_curl("https://www.locales.es/madrid/venta/locales?page=1", response))
        self.assertFalse(_should_retry_with_curl("https://www.example.com", response))

    @mock.patch("localizate.manual_available_locales._fetch_html_with_curl", return_value="<html>ok</html>")
    def test_fetch_html_falls_back_to_curl_on_cloudflare_403(self, fetch_html_with_curl: mock.Mock) -> None:
        session = _build_locales_es_session()
        response = mock.Mock()
        response.status_code = 403
        response.headers = {"Cf-Mitigated": "challenge"}
        response.text = "<html><title>Just a moment...</title></html>"
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
        with mock.patch.object(session, "get", return_value=response):
            html = _fetch_html(session, "https://www.locales.es/madrid/venta/locales?page=1", timeout_seconds=5)

        self.assertEqual(html, "<html>ok</html>")
        fetch_html_with_curl.assert_called_once()


if __name__ == "__main__":
    unittest.main()
