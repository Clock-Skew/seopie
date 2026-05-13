from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import scan_site
from .crawler import Crawler, normalize_url
from .reporters import write_csv, write_html, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seopie",
        description="Run a bounded SEO audit and produce professional JSON, HTML, and CSV reports.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan a URL and write SEO audit reports.")
    scan.add_argument("url", help="Starting URL, for example https://example.com")
    scan.add_argument("--max-pages", type=int, default=5, help="Maximum same-site pages to crawl. Default: 5")
    scan.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds. Default: 10")
    scan.add_argument("--output-dir", default="reports", help="Directory for generated reports. Default: reports")
    scan.add_argument("--json", action="store_true", help="Write JSON output.")
    scan.add_argument("--html", action="store_true", help="Write HTML output.")
    scan.add_argument("--csv", action="store_true", help="Write CSV issue export.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        return run_scan(args)
    parser.print_help()
    return 1


def run_scan(args: argparse.Namespace) -> int:
    formats = selected_formats(args)
    target_url = normalize_url(args.url)
    output_dir = Path(args.output_dir)
    crawler = Crawler(timeout=args.timeout)
    report = scan_site(target_url, max_pages=max(1, args.max_pages), crawler=crawler)

    written: list[Path] = []
    if "json" in formats:
        path = output_dir / "seopie-report.json"
        write_json(report, path)
        written.append(path)
    if "html" in formats:
        path = output_dir / "seopie-report.html"
        write_html(report, path)
        written.append(path)
    if "csv" in formats:
        path = output_dir / "seopie-issues.csv"
        write_csv(report, path)
        written.append(path)

    print(f"SEOpie scanned {report.pages_scanned} page(s). Score: {report.score}/100")
    print(report.client_summary)
    for path in written:
        print(f"Wrote {path}")
    return 0


def selected_formats(args: argparse.Namespace) -> set[str]:
    formats = set()
    if args.json:
        formats.add("json")
    if args.html:
        formats.add("html")
    if args.csv:
        formats.add("csv")
    return formats or {"json", "html", "csv"}


if __name__ == "__main__":
    raise SystemExit(main())
