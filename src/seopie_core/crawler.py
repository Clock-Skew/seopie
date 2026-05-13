from __future__ import annotations

from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from .models import FetchResult


DEFAULT_USER_AGENT = "SEOpieCore/0.1 (+https://github.com/Clock-Skew/seopie)"


class Crawler:
    def __init__(self, timeout: float = 10.0, user_agent: str = DEFAULT_USER_AGENT):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def crawl(self, start_url: str, max_pages: int = 5) -> list[FetchResult]:
        start_url = normalize_url(start_url)
        start_host = urlparse(start_url).netloc.lower()
        queue: deque[str] = deque([start_url])
        queued = {start_url}
        seen: set[str] = set()
        results: list[FetchResult] = []

        while queue and len(results) < max_pages:
            url = queue.popleft()
            if url in seen:
                continue
            seen.add(url)

            result = self.fetch(url)
            results.append(result)

            if not result.ok or not is_html_response(result):
                continue

            for link in extract_links(result.final_url, result.html):
                parsed = urlparse(link)
                if parsed.netloc.lower() != start_host:
                    continue
                if link not in queued and link not in seen:
                    queued.add(link)
                    queue.append(link)

        return results

    def fetch(self, url: str) -> FetchResult:
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            return FetchResult(
                url=url,
                final_url=normalize_url(response.url),
                status_code=response.status_code,
                headers=dict(response.headers),
                html=response.text if is_probably_html(response.headers) else "",
                elapsed_ms=response.elapsed.total_seconds() * 1000,
                size_bytes=len(response.content),
            )
        except requests.RequestException as exc:
            return FetchResult(
                url=url,
                final_url=url,
                status_code=None,
                headers={},
                html="",
                elapsed_ms=0,
                size_bytes=0,
                error=str(exc),
            )


def normalize_url(url: str) -> str:
    url = url.strip()
    if not urlparse(url).scheme:
        url = "https://" + url
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    normalized = urlunparse((scheme, netloc, path, "", parsed.query, ""))
    return urldefrag(normalized)[0]


def extract_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = normalize_url(urljoin(base_url, href))
        if urlparse(absolute).scheme in {"http", "https"}:
            links.append(absolute)
    return sorted(set(links))


def is_html_response(result: FetchResult) -> bool:
    return is_probably_html(result.headers) and bool(result.html)


def is_probably_html(headers: dict[str, str]) -> bool:
    content_type = headers.get("Content-Type", headers.get("content-type", ""))
    return not content_type or "html" in content_type.lower()
