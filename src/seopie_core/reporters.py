from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path

from .models import AuditReport, issue_counts


def write_json(report: AuditReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")


def write_csv(report: AuditReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["severity", "category", "id", "title", "url", "evidence", "recommendation"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for issue in report.issues:
            row = issue.to_dict()
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_html(report: AuditReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(report), encoding="utf-8")


def render_html(report: AuditReport) -> str:
    counts = issue_counts(report.issues)
    issue_rows = "\n".join(render_issue_row(issue) for issue in report.issues) or (
        "<tr><td colspan=\"5\">No issues found in the scanned sample.</td></tr>"
    )
    page_cards = "\n".join(render_page_card(page) for page in report.pages)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SEOpie Core Report</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172018;
      --muted: #5a665c;
      --paper: #f7f5ed;
      --panel: #ffffff;
      --line: #d9ded4;
      --green: #18794e;
      --amber: #b7791f;
      --red: #b42318;
      --blue: #1f5c99;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font: 16px/1.55 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 48px 24px 34px;
      background: #111811;
      color: #f6ffe9;
      border-bottom: 6px solid #a6ff4d;
    }}
    main {{ width: min(1180px, calc(100% - 32px)); margin: 28px auto 56px; }}
    h1, h2, h3 {{ line-height: 1.1; margin: 0; }}
    h1 {{ font-size: clamp(2.2rem, 5vw, 4.8rem); letter-spacing: 0; }}
    h2 {{ font-size: clamp(1.4rem, 2.4vw, 2rem); margin-bottom: 14px; }}
    h3 {{ font-size: 1rem; margin-bottom: 8px; }}
    .eyebrow {{ color: #a6ff4d; font-weight: 800; text-transform: uppercase; letter-spacing: .12em; }}
    .meta {{ color: #cbd8c8; max-width: 920px; margin-top: 14px; }}
    .summary-grid {{ display: grid; grid-template-columns: 1.3fr repeat(4, minmax(100px, .45fr)); gap: 14px; margin-top: 20px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 10px 30px rgba(23, 32, 24, .08);
    }}
    .score {{
      display: grid;
      place-items: center;
      min-height: 160px;
      background: #eaf8df;
      border-color: #9fd377;
    }}
    .score strong {{ display: block; font-size: clamp(3rem, 9vw, 6rem); line-height: .9; color: var(--green); }}
    .metric strong {{ display: block; font-size: 2rem; }}
    .critical, .high {{ color: var(--red); }}
    .medium {{ color: var(--amber); }}
    .low {{ color: var(--blue); }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); padding: 12px; }}
    th {{ background: #edf2e8; font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; }}
    .tag {{ display: inline-block; border: 1px solid currentColor; border-radius: 999px; padding: 2px 8px; font-size: .78rem; font-weight: 700; text-transform: uppercase; }}
    .pages {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }}
    .page-card dl {{ display: grid; grid-template-columns: auto 1fr; gap: 6px 14px; margin: 12px 0 0; }}
    .page-card dt {{ color: var(--muted); }}
    .page-card dd {{ margin: 0; word-break: break-word; }}
    section {{ margin-top: 28px; }}
    @media (max-width: 760px) {{
      header {{ padding-top: 34px; }}
      .summary-grid {{ grid-template-columns: 1fr 1fr; }}
      .score {{ grid-column: 1 / -1; }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">SEOpie Core SEO Audit</div>
    <h1>{escape(report.target_url)}</h1>
    <p class="meta">Scanned {report.pages_scanned} page(s) on {escape(report.scanned_at)}. {escape(report.client_summary)}</p>
  </header>
  <main>
    <section class="summary-grid" aria-label="Audit summary">
      <div class="panel score"><div><strong>{report.score}</strong><span>SEO score</span></div></div>
      <div class="panel metric"><span>Critical</span><strong class="critical">{counts["critical"]}</strong></div>
      <div class="panel metric"><span>High</span><strong class="high">{counts["high"]}</strong></div>
      <div class="panel metric"><span>Medium</span><strong class="medium">{counts["medium"]}</strong></div>
      <div class="panel metric"><span>Low</span><strong class="low">{counts["low"]}</strong></div>
    </section>

    <section>
      <h2>Priority Findings</h2>
      <table>
        <thead>
          <tr><th>Severity</th><th>Category</th><th>Finding</th><th>URL</th><th>Recommendation</th></tr>
        </thead>
        <tbody>
          {issue_rows}
        </tbody>
      </table>
    </section>

    <section>
      <h2>Scanned Pages</h2>
      <div class="pages">
        {page_cards}
      </div>
    </section>
  </main>
</body>
</html>
"""


def render_issue_row(issue) -> str:
    return f"""<tr>
  <td><span class="tag {escape(issue.severity)}">{escape(issue.severity)}</span></td>
  <td>{escape(issue.category)}</td>
  <td><strong>{escape(issue.title)}</strong><br>{escape(issue.evidence)}</td>
  <td>{escape(issue.url)}</td>
  <td>{escape(issue.recommendation)}</td>
</tr>"""


def render_page_card(page) -> str:
    return f"""<article class="panel page-card">
  <h3>{escape(page.title or "Untitled page")}</h3>
  <a href="{escape(page.final_url)}">{escape(page.final_url)}</a>
  <dl>
    <dt>Status</dt><dd>{escape(str(page.status_code))}</dd>
    <dt>H1 count</dt><dd>{page.h1_count}</dd>
    <dt>Words</dt><dd>{page.word_count}</dd>
    <dt>Images missing alt</dt><dd>{page.images_missing_alt} / {page.images_total}</dd>
    <dt>Internal links</dt><dd>{len(page.internal_links)}</dd>
    <dt>External links</dt><dd>{len(page.external_links)}</dd>
    <dt>Schema blocks</dt><dd>{page.schema_blocks}</dd>
    <dt>Response</dt><dd>{page.response_time_ms:.0f} ms</dd>
    <dt>Page weight</dt><dd>{page.page_weight_bytes:,} bytes</dd>
  </dl>
</article>"""
