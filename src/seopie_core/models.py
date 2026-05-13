from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


SEVERITY_WEIGHTS = {
    "critical": 14,
    "high": 8,
    "medium": 4,
    "low": 1,
}


@dataclass(slots=True)
class FetchResult:
    url: str
    final_url: str
    status_code: int | None
    headers: dict[str, str]
    html: str
    elapsed_ms: float
    size_bytes: int
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status_code is not None and 200 <= self.status_code < 400 and not self.error


@dataclass(slots=True)
class Issue:
    id: str
    category: str
    severity: str
    title: str
    description: str
    recommendation: str
    url: str
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "url": self.url,
            "evidence": self.evidence,
        }


@dataclass(slots=True)
class PageAudit:
    url: str
    final_url: str
    status_code: int | None
    title: str | None
    meta_description: str | None
    canonical: str | None
    robots: str | None
    x_robots_tag: str | None
    h1_count: int
    headings: list[dict[str, str]]
    images_total: int
    images_missing_alt: int
    internal_links: list[str]
    external_links: list[str]
    schema_blocks: int
    schema_types: list[str]
    word_count: int
    page_weight_bytes: int
    response_time_ms: float
    indexable: bool
    issues: list[Issue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "final_url": self.final_url,
            "status_code": self.status_code,
            "title": self.title,
            "meta_description": self.meta_description,
            "canonical": self.canonical,
            "robots": self.robots,
            "x_robots_tag": self.x_robots_tag,
            "h1_count": self.h1_count,
            "headings": self.headings,
            "images_total": self.images_total,
            "images_missing_alt": self.images_missing_alt,
            "internal_links": self.internal_links,
            "external_links": self.external_links,
            "schema_blocks": self.schema_blocks,
            "schema_types": self.schema_types,
            "word_count": self.word_count,
            "page_weight_bytes": self.page_weight_bytes,
            "response_time_ms": self.response_time_ms,
            "indexable": self.indexable,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(slots=True)
class AuditReport:
    target_url: str
    scanned_at: str
    pages_scanned: int
    score: int
    client_summary: str
    category_scores: dict[str, int]
    pages: list[PageAudit]
    issues: list[Issue]

    @classmethod
    def build(cls, target_url: str, pages: list[PageAudit]) -> "AuditReport":
        issues = [issue for page in pages for issue in page.issues]
        score = calculate_score(issues, len(pages))
        return cls(
            target_url=target_url,
            scanned_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            pages_scanned=len(pages),
            score=score,
            client_summary=build_client_summary(score, issues, len(pages)),
            category_scores=category_scores(issues, len(pages)),
            pages=pages,
            issues=issues,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_url": self.target_url,
            "scanned_at": self.scanned_at,
            "pages_scanned": self.pages_scanned,
            "score": self.score,
            "client_summary": self.client_summary,
            "category_scores": self.category_scores,
            "issue_counts": issue_counts(self.issues),
            "issues": [issue.to_dict() for issue in self.issues],
            "pages": [page.to_dict() for page in self.pages],
        }


def calculate_score(issues: list[Issue], page_count: int) -> int:
    if page_count <= 0:
        return 0
    penalty = sum(SEVERITY_WEIGHTS.get(issue.severity, 2) for issue in issues)
    normalized_penalty = min(100, round(penalty / max(page_count, 1)))
    return max(0, 100 - normalized_penalty)


def issue_counts(issues: list[Issue]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    return counts


def category_scores(issues: list[Issue], page_count: int) -> dict[str, int]:
    categories = sorted({issue.category for issue in issues})
    scores: dict[str, int] = {}
    for category in categories:
        category_issues = [issue for issue in issues if issue.category == category]
        scores[category] = calculate_score(category_issues, page_count)
    return scores


def build_client_summary(score: int, issues: list[Issue], page_count: int) -> str:
    counts = issue_counts(issues)
    high_priority = counts["critical"] + counts["high"]
    if page_count == 0:
        return "SEOpie could not scan the target. Confirm the URL is reachable and try again."
    if high_priority:
        return (
            f"SEOpie scanned {page_count} page(s) and found {high_priority} high-priority "
            "SEO issue(s). Address indexability, metadata, broken links, and technical "
            "signals first because those items can directly affect search visibility and user trust."
        )
    if counts["medium"]:
        return (
            f"SEOpie scanned {page_count} page(s). The site has a workable SEO foundation, "
            "with medium-priority improvements available around content structure, metadata, "
            "images, and internal linking."
        )
    return (
        f"SEOpie scanned {page_count} page(s). The sampled pages show a clean SEO baseline "
        f"with a score of {score}/100. Continue monitoring content quality, schema, links, and performance."
    )
