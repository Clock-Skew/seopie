# SEOpie Core

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CLI](https://img.shields.io/badge/Interface-CLI-111827?style=for-the-badge)](https://docs.python.org/3/library/argparse.html)
[![SEO Audit](https://img.shields.io/badge/Focus-SEO_Audit-2F855A?style=for-the-badge)](https://developers.google.com/search/docs)
[![Reports](https://img.shields.io/badge/Reports-HTML_JSON_CSV-B7791F?style=for-the-badge)](#reports)
[![License](https://img.shields.io/badge/License-MIT-0F172A?style=for-the-badge)](./LICENSE)

[![SEOpie Core project artwork](./Picsart_24-08-11_23-53-03-023.png)](./Picsart_24-08-11_23-53-03-023.png)

**SEOpie Core** is a Python SEO audit CLI for technical SEO triage, client-facing reports, and repeatable website checks. It accepts a starting URL, crawls a bounded number of same-site pages, evaluates practical SEO signals, and writes HTML, JSON, and CSV reports from the same normalized audit model.

The project is designed for web developers, SEO consultants, small business site owners, and technical marketers who need a clear first-pass audit without opening a heavy crawler suite.

## Contents

- [Why SEOpie Core Exists](#why-seopie-core-exists)
- [Feature Summary](#feature-summary)
- [Installation](#installation)
- [CLI Reference](#cli-reference)
- [Reports](#reports)
- [Audit Checks](#audit-checks)
- [Scoring](#scoring)
- [Architecture](#architecture)
- [Development](#development)
- [Limitations](#limitations)
- [Roadmap](#roadmap)

## Why SEOpie Core Exists

Many SEO problems are visible before expensive tooling is involved: missing titles, weak descriptions, bad heading structure, missing canonical tags, noindex directives, missing image alt text, thin pages, broken internal links, and slow responses. SEOpie Core turns those checks into a repeatable command-line workflow with report output that can be shared with clients or used as a development baseline.

SEOpie Core is not trying to replace Search Console, Screaming Frog, Sitebulb, Ahrefs, Semrush, Lighthouse, or browser-based lab testing. It is a small, inspectable audit layer for early technical review and client education.

## Feature Summary

- `seopie scan <url>` command with bounded same-site crawling.
- HTML report with score, executive summary, severity counts, category scores, priority findings, and scanned-page cards.
- JSON report for automation and future integrations.
- CSV issue export for spreadsheets, remediation queues, and client task lists.
- Normalized issue model with IDs, categories, severity, evidence, and recommendations.
- Page-level checks for metadata, headings, links, images, schema, indexability, response time, and page weight.
- Sample reports included in the repository.
- Legacy prototype scripts preserved under `legacy/prototype/` for reference while the new package evolves.

## Installation

### Requirements

- Python 3.10 or newer
- `pip`
- Network access to the site being scanned

On Debian, Ubuntu, or Kali, creating virtual environments may require the distro package matching your Python version, for example:

```bash
sudo apt install python3-venv
```

For Python 3.13 package builds, some systems package this as `python3.13-venv`.

### Editable Install

```bash
git clone git@github.com:Clock-Skew/seopie.git
cd seopie
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verify the command:

```bash
seopie --version
seopie --help
```

### Local Development Without Install

```bash
PYTHONPATH=src python3 -m seopie_core --version
PYTHONPATH=src python3 -m seopie_core scan https://example.com
```

The root `main.py` is a compatibility wrapper for the package CLI:

```bash
python3 main.py scan https://example.com
```

## CLI Reference

### `seopie scan`

```bash
seopie scan <url> [--max-pages N] [--timeout SECONDS] [--output-dir DIR] [--json] [--html] [--csv]
```

| Option | Default | Description |
| --- | --- | --- |
| `<url>` | required | Starting URL for the audit. URLs without a scheme are treated as HTTPS. |
| `--max-pages` | `5` | Maximum number of same-site pages to crawl. |
| `--timeout` | `10.0` | Per-request timeout in seconds. |
| `--output-dir` | `reports` | Directory where report files are written. |
| `--json` | off | Write `seopie-report.json`. |
| `--html` | off | Write `seopie-report.html`. |
| `--csv` | off | Write `seopie-issues.csv`. |

If no output format flag is supplied, SEOpie writes all three formats.

### Examples

Scan a site and write all report formats:

```bash
seopie scan https://example.com
```

Scan up to 10 pages and write reports to a named folder:

```bash
seopie scan https://example.com --max-pages 10 --output-dir audit-output
```

Generate only JSON:

```bash
seopie scan https://example.com --json --output-dir audit-output
```

Generate HTML and CSV for client review:

```bash
seopie scan https://example.com --html --csv --output-dir audit-output
```

## Reports

The report layer is intentionally split by audience.

| File | Audience | Purpose |
| --- | --- | --- |
| `seopie-report.html` | Clients, stakeholders, portfolio visitors | Visual report with score, summary, findings, and page cards. |
| `seopie-report.json` | Developers, automation, integrations | Full structured audit data. |
| `seopie-issues.csv` | SEO teams, spreadsheets, task tracking | Flat list of findings and recommendations. |

Sample reports:

- [`samples/seopie-report.html`](./samples/seopie-report.html)
- [`samples/seopie-report.json`](./samples/seopie-report.json)
- [`samples/seopie-issues.csv`](./samples/seopie-issues.csv)

The checked-in sample reports were generated from `https://example.com` to document the current output contract and keep the repository self-explanatory for both developers and clients.

### JSON Shape

The JSON report includes:

- `target_url`
- `scanned_at`
- `pages_scanned`
- `score`
- `client_summary`
- `category_scores`
- `issue_counts`
- `issues`
- `pages`

Each issue includes:

- `id`
- `category`
- `severity`
- `title`
- `description`
- `recommendation`
- `url`
- `evidence`

## Audit Checks

| Area | Checks |
| --- | --- |
| Metadata | Missing, short, or long titles and meta descriptions. |
| Indexability | Canonical presence, canonical mismatch, robots meta, and `X-Robots-Tag` noindex signals. |
| Content Structure | Missing H1, multiple H1s, skipped heading levels, and thin visible body content. |
| Internal Links | No internal links and broken internal links discovered inside the crawl sample. |
| Images | Missing alt text coverage. |
| Structured Data | JSON-LD and microdata presence. |
| Performance Hints | HTML response size and initial HTTP response timing. |
| Technical SEO | Fetch errors, HTTP error statuses, redirect statuses, and non-HTML crawl results. |

## Scoring

SEOpie scores from `0` to `100`. The score is calculated from issue severity weights normalized by scanned page count.

| Severity | Weight | Meaning |
| --- | ---: | --- |
| `critical` | `14` | The URL could not be fetched or returned a major error status. |
| `high` | `8` | Search visibility, indexability, or primary page understanding may be directly affected. |
| `medium` | `4` | Important quality, accessibility, linking, or performance improvement. |
| `low` | `1` | Cleanup, clarity, or best-practice improvement. |

The score is a triage aid, not a universal SEO grade. A five-page local business site, a SaaS marketing site, and a large ecommerce catalog need different SEO interpretation. Use the score to prioritize work, then read the issue evidence.

## Architecture

```text
seopie/
├── src/seopie_core/
│   ├── cli.py          # argparse CLI and command dispatch
│   ├── crawler.py      # bounded same-site crawler and fetch normalization
│   ├── analyzer.py     # page analysis and issue generation
│   ├── models.py       # dataclasses for fetches, pages, issues, and reports
│   └── reporters.py    # JSON, HTML, and CSV writers
├── samples/            # generated sample reports
├── tests/              # offline behavioral tests
├── legacy/prototype/   # previous prototype analyzer scripts
├── main.py             # compatibility wrapper for local CLI usage
├── pyproject.toml      # package metadata and console script
├── requirements.txt    # runtime dependencies
└── README.md
```

### Data Flow

1. `cli.py` parses command options and creates a crawler.
2. `crawler.py` fetches the start URL and discovers same-site links until `--max-pages` is reached.
3. `analyzer.py` converts each fetched page into a `PageAudit` and normalized `Issue` objects.
4. `models.py` builds the site-level `AuditReport`, score, summary, and category scores.
5. `reporters.py` writes the HTML, JSON, and CSV files.

## Development

Install dependencies:

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

Before committing, verify:

```bash
git diff --check
git status --short
```

## Limitations

- The crawler is intentionally bounded and same-site only.
- Robots.txt parsing is not implemented yet.
- JavaScript-rendered content is not rendered.
- Broken-link checks are limited to internal URLs fetched inside the crawl sample.
- Performance checks use HTTP response time and HTML byte size, not Lighthouse or Core Web Vitals.
- External authority, backlink, and social metrics are excluded because they require third-party data sources.
- The HTML report is static and self-contained; PDF export is not implemented yet.

## Roadmap

- Add robots.txt awareness with an explicit override flag.
- Add sitemap discovery and optional sitemap-first crawling.
- Add richer broken-link checks with bounded concurrency.
- Add per-category report filters.
- Add PDF export or print-optimized HTML.
- Add optional Lighthouse/PageSpeed integration as a separate module.
- Add project configuration files for repeat audits.

## License

SEOpie Core is released under the [MIT License](./LICENSE).
