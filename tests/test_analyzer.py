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

    def test_x_robots_tag_noindex_is_indexability_issue(self):
        html = """<!doctype html>
        <html lang="en">
          <head>
            <title>Example Service Page</title>
            <meta name="description" content="A useful page description that explains the service clearly for searchers.">
            <link rel="canonical" href="https://example.com/">
          </head>
          <body><h1>Example Service Page</h1><p>This page has enough visible copy for the scanner fixture.</p></body>
        </html>"""
        fetch = FetchResult(
            url="https://example.com/",
            final_url="https://example.com/",
            status_code=200,
            headers={"Content-Type": "text/html", "X-Robots-Tag": "googlebot: noindex"},
            html=html,
            elapsed_ms=120,
            size_bytes=len(html.encode("utf-8")),
        )

        page = analyze_page(fetch, {})

        self.assertFalse(page.indexable)
        self.assertIn("x-robots-noindex", {issue.id for issue in page.issues})

    def test_non_html_response_skips_page_level_findings(self):
        fetch = FetchResult(
            url="https://example.com/file.pdf",
            final_url="https://example.com/file.pdf",
            status_code=200,
            headers={"Content-Type": "application/pdf"},
            html="",
            elapsed_ms=80,
            size_bytes=1024,
        )

        page = analyze_page(fetch, {})
        issue_ids = {issue.id for issue in page.issues}

        self.assertEqual(issue_ids, {"non-html-content"})
        self.assertEqual(page.word_count, 0)


if __name__ == "__main__":
    unittest.main()
