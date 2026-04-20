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
        response.headers = {"X-Browser-Ms-Used": "1234"}
        session.post.return_value = response
        client = CloudflareBrowserRunClient(
            CloudflareBrowserRunConfig(account_id="acc", api_token="token"),
            session=session,
        )

        html = client.fetch_html("https://www.locales.es/madrid/venta/locales?page=1")

        self.assertEqual(html, "<html>ok</html>")
        self.assertEqual(client.request_count, 1)
        self.assertEqual(client.browser_ms_used_total, 1234)
        session.post.assert_called_once()
        _, kwargs = session.post.call_args
        self.assertIn("/accounts/acc/browser-rendering/content", kwargs.get("url", "") or session.post.call_args.args[0])
        self.assertEqual(kwargs["json"]["gotoOptions"]["waitUntil"], "networkidle2")

    def test_fetch_html_respects_min_interval_between_requests(self) -> None:
        session = mock.Mock()
        response = mock.Mock()
        response.json.return_value = {"success": True, "result": "<html>ok</html>"}
        response.headers = {}
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
        response.headers = {}
        session.post.return_value = response
        client = CloudflareBrowserRunClient(
            CloudflareBrowserRunConfig(account_id="acc", api_token="token", max_requests=1),
            session=session,
        )

        client.fetch_html("https://example.com/one")
        with self.assertRaises(BrowserRunBudgetExceeded):
            client.fetch_html("https://example.com/two")

    def test_fetch_html_retries_once_after_429(self) -> None:
        session = mock.Mock()
        rate_limited = mock.Mock()
        rate_limited.status_code = 429
        rate_limited.headers = {"Retry-After": "12"}

        success = mock.Mock()
        success.status_code = 200
        success.headers = {"X-Browser-Ms-Used": "800"}
        success.json.return_value = {"success": True, "result": "<html>ok</html>"}

        session.post.side_effect = [rate_limited, success]
        clock = {"now": 0.0}

        def monotonic() -> float:
            return clock["now"]

        def sleep(seconds: float) -> None:
            clock["now"] += seconds

        client = CloudflareBrowserRunClient(
            CloudflareBrowserRunConfig(
                account_id="acc",
                api_token="token",
                min_interval_seconds=15.0,
            ),
            session=session,
            sleep=sleep,
            monotonic=monotonic,
        )

        html = client.fetch_html("https://example.com/one")

        self.assertEqual(html, "<html>ok</html>")
        self.assertEqual(client.request_count, 2)
        self.assertEqual(client.browser_ms_used_total, 800)
        self.assertEqual(clock["now"], 20.0)

    def test_fetch_html_raises_budget_exceeded_after_repeated_429(self) -> None:
        session = mock.Mock()
        rate_limited = mock.Mock()
        rate_limited.status_code = 429
        rate_limited.headers = {"Retry-After": "10"}
        session.post.side_effect = [rate_limited, rate_limited, rate_limited]
        clock = {"now": 0.0}

        def monotonic() -> float:
            return clock["now"]

        def sleep(seconds: float) -> None:
            clock["now"] += seconds

        client = CloudflareBrowserRunClient(
            CloudflareBrowserRunConfig(
                account_id="acc",
                api_token="token",
                max_rate_limit_retries=2,
                min_interval_seconds=15.0,
            ),
            session=session,
            sleep=sleep,
            monotonic=monotonic,
        )

        with self.assertRaises(BrowserRunBudgetExceeded):
            client.fetch_html("https://example.com/one")

        self.assertEqual(client.request_count, 3)
        self.assertEqual(clock["now"], 40.0)


if __name__ == "__main__":
    unittest.main()
