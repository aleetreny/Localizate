from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest import mock


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from localizate.cloudflare_browser_run import (  # noqa: E402
    BrowserRunBudgetExceeded,
    CloudflareBrowserRunClient,
    CloudflareBrowserRunConfig,
)


class CloudflareBrowserRunClientTests(unittest.TestCase):
    def test_fetch_html_uses_content_endpoint_and_parses_html(self) -> None:
        session = mock.Mock()
        response = mock.Mock()
        response.json.return_value = {"success": True, "result": {"html": "<html>ok</html>"}}
        session.post.return_value = response
        client = CloudflareBrowserRunClient(
            CloudflareBrowserRunConfig(account_id="acc", api_token="token"),
            session=session,
        )

        html = client.fetch_html("https://www.locales.es/madrid/venta/locales?page=1")

        self.assertEqual(html, "<html>ok</html>")
        self.assertEqual(client.request_count, 1)
        session.post.assert_called_once()
        _, kwargs = session.post.call_args
        self.assertIn("/accounts/acc/browser-rendering/content", kwargs.get("url", "") or session.post.call_args.args[0])
        self.assertEqual(kwargs["json"]["gotoOptions"]["waitUntil"], "networkidle2")

    def test_fetch_html_respects_min_interval_between_requests(self) -> None:
        session = mock.Mock()
        response = mock.Mock()
        response.json.return_value = {"success": True, "result": "<html>ok</html>"}
        session.post.return_value = response
        sleep = mock.Mock()
        monotonic_values = iter([0.0, 0.0, 5.0, 5.0])
        client = CloudflareBrowserRunClient(
            CloudflareBrowserRunConfig(
                account_id="acc",
                api_token="token",
                min_interval_seconds=11.0,
            ),
            session=session,
            sleep=sleep,
            monotonic=lambda: next(monotonic_values),
        )

        client.fetch_html("https://example.com/one")
        client.fetch_html("https://example.com/two")

        sleep.assert_called_once_with(6.0)

    def test_fetch_html_raises_when_budget_is_exhausted(self) -> None:
        session = mock.Mock()
        response = mock.Mock()
        response.json.return_value = {"success": True, "result": "<html>ok</html>"}
        session.post.return_value = response
        client = CloudflareBrowserRunClient(
            CloudflareBrowserRunConfig(account_id="acc", api_token="token", max_requests=1),
            session=session,
        )

        client.fetch_html("https://example.com/one")
        with self.assertRaises(BrowserRunBudgetExceeded):
            client.fetch_html("https://example.com/two")


if __name__ == "__main__":
    unittest.main()
