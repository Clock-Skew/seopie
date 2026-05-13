# SEOpie Core

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CLI](https://img.shields.io/badge/Interface-CLI-111827?style=for-the-badge)](https://docs.python.org/3/library/argparse.html)
[![SEO Audit](https://img.shields.io/badge/Focus-SEO_Audit-2F855A?style=for-the-badge)](https://developers.google.com/search/docs)
[![Reports](https://img.shields.io/badge/Reports-HTML_JSON_CSV-B7791F?style=for-the-badge)](#output-formats)
[![License](https://img.shields.io/badge/License-MIT-0F172A?style=for-the-badge)](./LICENSE)

[![SEOpie Core project artwork](./Picsart_24-08-11_23-53-03-023.png)](./Picsart_24-08-11_23-53-03-023.png)

**SEOpie Core** is a Python SEO audit CLI for small-site technical checks and professional report generation. It accepts a starting URL, crawls a bounded number of same-site pages, evaluates common SEO signals, and writes client-friendly HTML plus machine-readable JSON and CSV exports.

This repo is being rebuilt from an older interactive prototype into a cleaner package with a real command-line interface, normalized findings, severity scoring, and polished sample reports.

## What It Checks

SEOpie Core currently audits:

- title tags and meta descriptions
- canonical tags and robots indexability hints
- heading structure and H1 coverage
- thin content signals
- internal and external link inventory
- broken internal links found inside the crawl sample
- image alt coverage
- schema and structured data presence
- page weight and response time hints
- HTTP fetch failures and non-success status codes

The goal is practical SEO triage, not a replacement for full enterprise crawlers, browser-based Lighthouse runs, log analysis, Search Console, or paid backlink APIs.

## Quick Start

```bash
git clone git@github.com:Clock-Skew/seopie.git
cd seopie
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run a scan:

```bash
seopie scan https://example.com
```

Equivalent local development command without installing:

```bash
PYTHONPATH=src python3 -m seopie_core scan https://example.com
```

Legacy-compatible entry point:

```bash
python3 main.py scan https://example.com
```

## Example Commands

Scan one URL and write all default reports to `reports/`:

```bash
seopie scan https://example.com
```

Limit the crawl and choose an output directory:

```bash
seopie scan https://example.com --max-pages 10 --output-dir audit-output
```

Write only JSON:

```bash
seopie scan https://example.com --json --output-dir audit-output
```

Write only HTML and CSV:

```bash
seopie scan https://example.com --html --csv --output-dir audit-output
```

## Output Formats

By default, `seopie scan` writes three files:

| File | Purpose |
| --- | --- |
| `seopie-report.html` | Client-facing report with summary, score, findings, and scanned-page cards. |
| `seopie-report.json` | Full structured audit data for automation, review, or future integrations. |
| `seopie-issues.csv` | Flat issue export for spreadsheets, task lists, or client remediation tracking. |

Sample reports are included in [`samples/`](./samples/):

- [`samples/seopie-report.html`](./samples/seopie-report.html)
- [`samples/seopie-report.json`](./samples/seopie-report.json)
- [`samples/seopie-issues.csv`](./samples/seopie-issues.csv)

## Scoring Model

SEOpie Core scores from `0` to `100` using issue severity penalties normalized by scanned page count.

| Severity | Intended Meaning |
| --- | --- |
| `critical` | The page could not be fetched or returned a major error status. |
| `high` | Search visibility, indexability, or core page understanding may be directly affected. |
| `medium` | Important improvement that can affect quality, accessibility, linking, or performance. |
| `low` | Cleanup, clarity, or best-practice improvement. |

The score is meant to prioritize remediation, not to claim a universal SEO grade. SEO context changes by site type, intent, market, and crawl scope.

## Architecture

```text
seopie/
├── src/seopie_core/
│   ├── cli.py          # argparse CLI and command dispatch
│   ├── crawler.py      # bounded same-site crawler and fetch normalization
│   ├── analyzer.py     # page analysis and issue generation
│   ├── models.py       # report, page, and issue dataclasses
│   └── reporters.py    # JSON, HTML, and CSV writers
├── samples/            # generated sample reports
├── tests/              # lightweight offline tests
├── main.py             # compatibility wrapper for local CLI usage
├── pyproject.toml      # package metadata and console script
├── requirements.txt    # minimal runtime dependencies
└── README.md
```

Older analyzer scripts remain in the repository for now as reference material from the previous prototype. The active implementation lives under `src/seopie_core/`.

## Development

Install in editable mode:

```bash
pip install -e .
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Run syntax checks:

```bash
python3 -m compileall src tests main.py
```

Generate fresh sample reports:

```bash
PYTHONPATH=src python3 -m seopie_core scan https://example.com --max-pages 1 --output-dir samples
```

## Current Limitations

- The crawler is intentionally bounded and same-site only.
- Broken-link detection currently covers internal URLs discovered inside the crawl sample.
- Performance checks use HTTP response timing and page weight, not browser lab metrics.
- JavaScript-rendered content is not rendered.
- External authority, backlink, and social metrics are not included because they require third-party data sources.
- Robots.txt parsing is not implemented yet; page-level robots meta is captured.

## Roadmap

- Add configurable crawl rules and robots.txt awareness.
- Add richer broken-link checks with safe concurrency limits.
- Add sitemap discovery.
- Add per-category scoring and report filters.
- Add screenshot or PDF export for client delivery.
- Add optional Lighthouse/PageSpeed integration as a separate module.

## License

SEOpie Core is released under the [MIT License](./LICENSE).
