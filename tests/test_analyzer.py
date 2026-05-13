import unittest

from seopie_core.analyzer import analyze_page
from seopie_core.crawler import normalize_url
from seopie_core.models import FetchResult


class AnalyzerTests(unittest.TestCase):
    def test_detects_core_page_findings(self):
        html = """<!doctype html>
        <html lang="en">
          <head>
            <title>Short</title>
            <meta name="robots" content="index, follow">
          </head>
          <body>
            <h2>Skipped heading</h2>
            <img src="/hero.png">
            <a href="/about">About</a>
          </body>
        </html>"""
        fetch = FetchResult(
            url="https://example.com/",
            final_url="https://example.com/",
            status_code=200,
            headers={"Content-Type": "text/html"},
            html=html,
            elapsed_ms=120,
            size_bytes=len(html.encode("utf-8")),
        )
        statuses = {normalize_url("https://example.com/about"): 404}

        page = analyze_page(fetch, statuses)
        issue_ids = {issue.id for issue in page.issues}

        self.assertIn("short-title", issue_ids)
        self.assertIn("missing-meta-description", issue_ids)
        self.assertIn("missing-h1", issue_ids)
        self.assertIn("missing-image-alt", issue_ids)
        self.assertIn("broken-internal-links", issue_ids)


if __name__ == "__main__":
    unittest.main()
