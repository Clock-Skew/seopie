from __future__ import annotations

import json
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .crawler import extract_links, is_probably_html, normalize_url
from .models import AuditReport, FetchResult, Issue, PageAudit


def scan_site(target_url: str, max_pages: int, crawler) -> AuditReport:
    fetches = crawler.crawl(target_url, max_pages=max_pages)
    status_by_url = {normalize_url(fetch.url): fetch.status_code for fetch in fetches}
    status_by_url.update({normalize_url(fetch.final_url): fetch.status_code for fetch in fetches})
    pages = [analyze_page(fetch, status_by_url) for fetch in fetches]
    return AuditReport.build(target_url=normalize_url(target_url), pages=pages)


def analyze_page(fetch: FetchResult, status_by_url: dict[str, int | None]) -> PageAudit:
    soup = BeautifulSoup(fetch.html, "html.parser") if fetch.html else BeautifulSoup("", "html.parser")
    issues: list[Issue] = []

    if fetch.error:
        issues.append(issue("fetch-error", "Technical SEO", "critical", "Page could not be fetched", fetch, fetch.error))
    elif fetch.status_code is None or fetch.status_code >= 400:
        issues.append(issue("bad-status", "Technical SEO", "critical", "Page returned an error status", fetch, str(fetch.status_code)))
    elif fetch.status_code >= 300:
        issues.append(issue("redirect-status", "Technical SEO", "low", "Page resolved through a redirect", fetch, str(fetch.status_code)))

    if fetch.ok and not is_probably_html(fetch.headers):
        issues.append(issue("non-html-content", "Technical SEO", "low", "Fetched URL is not HTML", fetch, content_type(fetch.headers)))
        return minimal_page_audit(fetch, issues)

    title = get_text(soup.find("title"))
    meta_description = get_meta_content(soup, "description")
    canonical = get_link_href(soup, "canonical")
    robots = get_meta_content(soup, "robots")
    x_robots_tag = get_header(fetch.headers, "X-Robots-Tag")
    headings = extract_headings(soup)
    h1_count = sum(1 for heading in headings if heading["level"] == "h1")
    images = soup.find_all("img")
    images_missing_alt = sum(1 for img in images if not img.get("alt", "").strip())
    all_links = extract_links(fetch.final_url, fetch.html) if fetch.html else []
    host = urlparse(fetch.final_url).netloc.lower()
    internal_links = [link for link in all_links if urlparse(link).netloc.lower() == host]
    external_links = [link for link in all_links if urlparse(link).netloc.lower() != host]
    broken_internal = [link for link in internal_links if is_broken(status_by_url.get(normalize_url(link)))]
    schema_types, schema_blocks = extract_schema(soup)
    word_count = count_words(soup)
    indexable = is_indexable(robots, x_robots_tag)

    issues.extend(metadata_issues(fetch, title, meta_description, canonical, robots, x_robots_tag, indexable))
    issues.extend(structure_issues(fetch, h1_count, headings, word_count))
    issues.extend(link_issues(fetch, internal_links, broken_internal))
    issues.extend(image_issues(fetch, len(images), images_missing_alt))
    issues.extend(schema_issues(fetch, schema_blocks))
    issues.extend(performance_issues(fetch))

    return PageAudit(
        url=fetch.url,
        final_url=fetch.final_url,
        status_code=fetch.status_code,
        title=title,
        meta_description=meta_description,
        canonical=canonical,
        robots=robots,
        x_robots_tag=x_robots_tag,
        h1_count=h1_count,
        headings=headings,
        images_total=len(images),
        images_missing_alt=images_missing_alt,
        internal_links=internal_links,
        external_links=external_links,
        schema_blocks=schema_blocks,
        schema_types=schema_types,
        word_count=word_count,
        page_weight_bytes=fetch.size_bytes,
        response_time_ms=round(fetch.elapsed_ms, 2),
        indexable=indexable,
        issues=issues,
    )


def minimal_page_audit(fetch: FetchResult, issues: list[Issue]) -> PageAudit:
    return PageAudit(
        url=fetch.url,
        final_url=fetch.final_url,
        status_code=fetch.status_code,
        title=None,
        meta_description=None,
        canonical=None,
        robots=None,
        x_robots_tag=get_header(fetch.headers, "X-Robots-Tag"),
        h1_count=0,
        headings=[],
        images_total=0,
        images_missing_alt=0,
        internal_links=[],
        external_links=[],
        schema_blocks=0,
        schema_types=[],
        word_count=0,
        page_weight_bytes=fetch.size_bytes,
        response_time_ms=round(fetch.elapsed_ms, 2),
        indexable=is_indexable(None, get_header(fetch.headers, "X-Robots-Tag")),
        issues=issues,
    )


def metadata_issues(
    fetch: FetchResult,
    title: str | None,
    description: str | None,
    canonical: str | None,
    robots: str | None,
    x_robots_tag: str | None,
    indexable: bool,
) -> list[Issue]:
    issues: list[Issue] = []
    if not title:
        issues.append(issue("missing-title", "Metadata", "high", "Missing title tag", fetch, "No <title> tag was found."))
    elif len(title) > 60:
        issues.append(issue("long-title", "Metadata", "medium", "Title tag is longer than 60 characters", fetch, f"{len(title)} characters"))
    elif len(title) < 20:
        issues.append(issue("short-title", "Metadata", "low", "Title tag is very short", fetch, f"{len(title)} characters"))

    if not description:
        issues.append(issue("missing-meta-description", "Metadata", "high", "Missing meta description", fetch, "No meta description was found."))
    elif len(description) > 160:
        issues.append(issue("long-meta-description", "Metadata", "medium", "Meta description is longer than 160 characters", fetch, f"{len(description)} characters"))
    elif len(description) < 70:
        issues.append(issue("short-meta-description", "Metadata", "low", "Meta description is short", fetch, f"{len(description)} characters"))

    if not canonical:
        issues.append(issue("missing-canonical", "Indexability", "low", "Missing canonical tag", fetch, "No rel=canonical tag was found."))
    elif normalize_url(urljoin(fetch.final_url, canonical)) != normalize_url(fetch.final_url):
        issues.append(issue("canonical-mismatch", "Indexability", "low", "Canonical differs from final URL", fetch, canonical))
    if robots and not indexable:
        issues.append(issue("noindex", "Indexability", "high", "Page is marked noindex", fetch, robots))
    elif x_robots_tag and not indexable:
        issues.append(issue("x-robots-noindex", "Indexability", "high", "X-Robots-Tag marks page noindex", fetch, x_robots_tag))
    return issues


def structure_issues(fetch: FetchResult, h1_count: int, headings: list[dict[str, str]], word_count: int) -> list[Issue]:
    issues: list[Issue] = []
    if h1_count == 0:
        issues.append(issue("missing-h1", "Content Structure", "high", "Missing H1 heading", fetch, "No H1 heading was found."))
    elif h1_count > 1:
        issues.append(issue("multiple-h1", "Content Structure", "medium", "Multiple H1 headings", fetch, f"{h1_count} H1 headings found."))
    if has_heading_skip(headings):
        issues.append(issue("heading-skip", "Content Structure", "low", "Heading hierarchy skips a level", fetch, "One or more headings skip an intermediate level."))
    if word_count < 300:
        issues.append(issue("thin-content", "Content Quality", "medium", "Page has thin body content", fetch, f"{word_count} words found."))
    return issues


def link_issues(fetch: FetchResult, internal_links: list[str], broken_internal: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    if not internal_links:
        issues.append(issue("no-internal-links", "Internal Links", "medium", "No internal links found", fetch, "The page does not link to another same-site URL."))
    if broken_internal:
        issues.append(issue("broken-internal-links", "Internal Links", "high", "Broken internal links found", fetch, ", ".join(broken_internal[:5])))
    return issues


def image_issues(fetch: FetchResult, total: int, missing_alt: int) -> list[Issue]:
    if total == 0 or missing_alt == 0:
        return []
    severity = "high" if missing_alt == total else "medium"
    return [issue("missing-image-alt", "Images", severity, "Images missing alt text", fetch, f"{missing_alt} of {total} image(s) are missing alt text.")]


def schema_issues(fetch: FetchResult, schema_blocks: int) -> list[Issue]:
    if schema_blocks:
        return []
    return [issue("missing-schema", "Structured Data", "low", "No structured data detected", fetch, "No JSON-LD or microdata blocks were found.")]


def performance_issues(fetch: FetchResult) -> list[Issue]:
    issues: list[Issue] = []
    if fetch.size_bytes > 1_000_000:
        issues.append(issue("large-html", "Performance", "medium", "HTML response is over 1 MB", fetch, f"{fetch.size_bytes} bytes"))
    if fetch.elapsed_ms > 1500:
        issues.append(issue("slow-response", "Performance", "medium", "Slow server response", fetch, f"{fetch.elapsed_ms:.0f} ms"))
    return issues


def issue(issue_id: str, category: str, severity: str, title: str, fetch: FetchResult, evidence: str) -> Issue:
    recommendations = {
        "missing-title": "Add a concise, descriptive title tag to the page.",
        "long-title": "Shorten the title so the main topic and brand fit cleanly in search results.",
        "short-title": "Expand the title with clearer topic or brand context.",
        "missing-meta-description": "Add a plain-language meta description that summarizes the page value.",
        "long-meta-description": "Reduce the description to roughly 150-160 characters.",
        "short-meta-description": "Expand the description so it gives searchers a clear reason to click.",
        "missing-canonical": "Add a canonical URL to reduce duplicate-content ambiguity.",
        "canonical-mismatch": "Confirm the canonical target is intentional and points to the preferred indexable URL.",
        "noindex": "Confirm whether this page should be excluded from search results.",
        "x-robots-noindex": "Confirm whether the HTTP X-Robots-Tag should exclude this page from search results.",
        "missing-h1": "Add one clear H1 that describes the page's primary topic.",
        "multiple-h1": "Use one primary H1 and move secondary section titles to H2 or lower.",
        "heading-skip": "Use heading levels in sequence so users and crawlers can understand the structure.",
        "thin-content": "Add useful, specific content that answers the searcher's intent.",
        "no-internal-links": "Add relevant internal links to related pages or conversion paths.",
        "broken-internal-links": "Fix, redirect, or remove broken internal links.",
        "missing-image-alt": "Add useful alt text to meaningful images and empty alt text to decorative images.",
        "missing-schema": "Add relevant structured data when it helps describe the entity, service, article, or product.",
        "large-html": "Reduce unnecessary markup, inline payloads, and heavy embedded content.",
        "slow-response": "Review hosting, caching, backend work, and third-party dependencies affecting response time.",
        "fetch-error": "Confirm the page is reachable from the scanner environment.",
        "bad-status": "Fix the page response so important URLs return a successful status.",
        "redirect-status": "Point internal references directly at the final canonical URL when practical.",
        "non-html-content": "Review whether this URL belongs in the crawl path or should be linked with clearer context.",
    }
    descriptions = {
        "missing-title": "Search engines and browser tabs rely on title text to understand the page topic.",
        "long-title": "Long titles can be truncated in search results and dilute the page's primary topic.",
        "short-title": "Very short titles often miss useful keyword, service, or brand context.",
        "missing-meta-description": "A missing description gives search engines less control over the snippet shown to users.",
        "long-meta-description": "Long descriptions are likely to be truncated before the value proposition is complete.",
        "short-meta-description": "Short descriptions often fail to explain why a searcher should click.",
        "missing-canonical": "Canonical tags help clarify the preferred URL when duplicate or similar pages exist.",
        "canonical-mismatch": "A mismatched canonical can consolidate ranking signals to another URL.",
        "noindex": "The page includes a robots directive that can keep it out of search results.",
        "x-robots-noindex": "The HTTP robots header can prevent indexing even when page markup looks indexable.",
        "missing-h1": "The page lacks a primary visible heading for users and crawlers.",
        "multiple-h1": "Multiple H1 tags can make the primary topic less clear.",
        "heading-skip": "Skipped heading levels make the document outline harder to parse.",
        "thin-content": "The page may not contain enough useful body copy for its target intent.",
        "no-internal-links": "Internal links help crawlers discover related pages and help users move toward conversion paths.",
        "broken-internal-links": "Broken internal links waste crawl paths and create poor user experience.",
        "missing-image-alt": "Missing alt text weakens accessibility and image context.",
        "missing-schema": "Structured data can help describe the page entity, service, article, product, or organization.",
        "large-html": "Large HTML responses can slow delivery before assets are even considered.",
        "slow-response": "Slow initial responses can affect user experience and performance diagnostics.",
        "fetch-error": "The scanner could not retrieve the URL.",
        "bad-status": "Important pages should generally return successful HTTP status codes.",
        "redirect-status": "Redirects are sometimes correct, but internal links should usually point to final URLs.",
        "non-html-content": "This fetched URL is not an HTML document, so page-level SEO checks were skipped.",
    }
    return Issue(
        id=issue_id,
        category=category,
        severity=severity,
        title=title,
        description=descriptions.get(issue_id, title),
        recommendation=recommendations.get(issue_id, "Review and resolve this issue."),
        url=fetch.final_url,
        evidence=evidence,
    )


def get_text(tag) -> str | None:
    if not tag:
        return None
    text = tag.get_text(" ", strip=True)
    return text or None


def get_meta_content(soup: BeautifulSoup, name: str) -> str | None:
    tag = soup.find("meta", attrs={"name": re.compile(f"^{re.escape(name)}$", re.I)})
    if not tag:
        return None
    content = tag.get("content", "").strip()
    return content or None


def get_link_href(soup: BeautifulSoup, rel: str) -> str | None:
    tag = soup.find("link", rel=lambda value: rel_matches(value, rel))
    if not tag:
        return None
    href = tag.get("href", "").strip()
    return href or None


def rel_matches(value, rel: str) -> bool:
    if not value:
        return False
    if isinstance(value, str):
        values = value.split()
    else:
        values = list(value)
    return rel.lower() in [item.lower() for item in values]


def extract_headings(soup: BeautifulSoup) -> list[dict[str, str]]:
    headings = []
    for tag in soup.find_all(re.compile("^h[1-6]$")):
        headings.append({"level": tag.name, "text": tag.get_text(" ", strip=True)})
    return headings


def has_heading_skip(headings: list[dict[str, str]]) -> bool:
    previous_level = 0
    for heading in headings:
        level = int(heading["level"][1])
        if previous_level and level > previous_level + 1:
            return True
        previous_level = level
    return False


def count_words(soup: BeautifulSoup) -> int:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return len(re.findall(r"\b[\w'-]+\b", soup.get_text(" ", strip=True)))


def is_indexable(robots: str | None, x_robots_tag: str | None = None) -> bool:
    directives = ",".join(value for value in [robots, x_robots_tag] if value)
    if not directives:
        return True
    parsed = {part.strip().lower() for part in directives.split(",")}
    return not any(part == "none" or "noindex" in part for part in parsed)


def get_header(headers: dict[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.lower() == name.lower():
            cleaned = value.strip()
            return cleaned or None
    return None


def content_type(headers: dict[str, str]) -> str:
    return get_header(headers, "Content-Type") or "unknown content type"


def is_broken(status_code: int | None) -> bool:
    return status_code is not None and status_code >= 400


def extract_schema(soup: BeautifulSoup) -> tuple[list[str], int]:
    types: list[str] = []
    blocks = 0
    for script in soup.find_all("script", attrs={"type": re.compile("ld\\+json", re.I)}):
        blocks += 1
        try:
            collect_schema_types(json.loads(script.string or ""), types)
        except json.JSONDecodeError:
            continue
    microdata = soup.find_all(attrs={"itemscope": True})
    blocks += len(microdata)
    for tag in microdata:
        itemtype = tag.get("itemtype")
        if itemtype:
            types.append(str(itemtype))
    return sorted(set(types)), blocks


def collect_schema_types(value, types: list[str]) -> None:
    if isinstance(value, dict):
        schema_type = value.get("@type")
        if isinstance(schema_type, str):
            types.append(schema_type)
        elif isinstance(schema_type, list):
            types.extend(str(item) for item in schema_type)
        for child in value.values():
            collect_schema_types(child, types)
    elif isinstance(value, list):
        for item in value:
            collect_schema_types(item, types)
