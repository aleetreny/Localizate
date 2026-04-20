from __future__ import annotations

from pathlib import Path
import sys
import unittest


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


if __name__ == "__main__":
    unittest.main()
