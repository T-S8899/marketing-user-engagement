from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.analyze.marketing_analysis import MarketingAnalyzer
from src.reports.report_builder import MarkdownReportBuilder
from src.scrape.apify_client import ApifyClient
from src.scrape.run_manager import SUPPORTED_PLATFORMS, RunManager
from src.scrape.run_scraper import filter_brand_targets
from src.structure.normalization import MarketCommentsNormalizer
from src.utils.config import PROJECT_ROOT, ConfigError, load_apify_actors_config, load_brands_config, require_env


LOG_PATH = PROJECT_ROOT / "state" / "workflow.log"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full local marketing intelligence workflow.")
    parser.add_argument("--platform", choices=sorted(SUPPORTED_PLATFORMS | {"all"}), default="all", help="Platform to scrape.")
    parser.add_argument("--brand", default="", help="Only scrape configured targets for this brand name, role, or account.")
    parser.add_argument("--fail-fast", action=argparse.BooleanOptionalAction, default=True, help="Stop on the first platform failure.")
    parser.add_argument("--sample", action="store_true", help="Testing mode: skip scraping and run local processing on existing files.")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip Apify scraping and use existing local raw/processed files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log("Workflow started")
    try:
        if args.sample:
            log("Sample mode enabled; skipping scrape.")
        elif args.skip_scrape:
            log("Skipping scrape by request.")
        else:
            scrape(args)

        normalize()
        ensure_file(PROJECT_ROOT / "data" / "processed" / "market_comments.csv", "normalization")
        analyze()
        ensure_file(PROJECT_ROOT / "data" / "analysis" / "comment_analysis.csv", "analysis")
        reports()
        ensure_file(PROJECT_ROOT / "data" / "reports" / "executive_summary.md", "report generation")
        prepare_dashboard()
        log("Workflow completed successfully")
        print("Workflow completed successfully.")
        print(f"Dashboard: http://localhost:8000/frontend/ after running python -m src.dashboard.run_dashboard")
        return 0
    except Exception as exc:
        log(f"Workflow failed: {exc}")
        print(f"Workflow failed: {exc}", file=sys.stderr)
        return 1


def scrape(args: argparse.Namespace) -> None:
    log("Step 1/5 scrape started")
    token = require_env("APIFY_TOKEN")
    brands_config = load_brands_config()
    if args.brand:
        brands_config = filter_brand_targets(brands_config, args.brand)
    actors_config = load_apify_actors_config()
    manager = RunManager(ApifyClient(token), brands_config, actors_config)
    platforms = sorted(SUPPORTED_PLATFORMS) if args.platform == "all" else [args.platform]
    failures = []
    successes = 0
    for platform in platforms:
        try:
            results = manager.run_platform(platform)
            successes += len(results)
            for result in results:
                log(f"Scraped {platform}: {result.run_id} records={result.records_count}")
        except Exception as exc:
            failures.append(f"{platform}: {exc}")
            log(f"Scrape platform failed: {platform}: {exc}")
            if args.fail_fast:
                raise
    if failures and successes == 0:
        raise RuntimeError("Scraping failed for all requested platforms. " + "; ".join(failures))
    if failures:
        log("Scraping completed with failures: " + "; ".join(failures))
    log("Step 1/5 scrape finished")


def normalize() -> None:
    log("Step 2/5 normalization started")
    outputs = MarketCommentsNormalizer().normalize_all()
    log(f"Normalization finished records={outputs.records_count} errors={outputs.errors_count}")


def analyze() -> None:
    log("Step 3/5 analysis started")
    outputs = MarketingAnalyzer().run()
    log(f"Analysis finished comments={outputs.comments_count}")


def reports() -> None:
    log("Step 4/5 reports started")
    result = MarkdownReportBuilder().build_all()
    log(f"Reports finished count={len(result.reports)}")


def prepare_dashboard() -> None:
    log("Step 5/5 dashboard preparation started")
    required = [
        PROJECT_ROOT / "frontend" / "index.html",
        PROJECT_ROOT / "frontend" / "src" / "data" / "rawTables.js",
        PROJECT_ROOT / "data" / "processed" / "market_comments.csv",
        PROJECT_ROOT / "data" / "analysis" / "comment_analysis.csv",
    ]
    for path in required:
        ensure_file(path, "dashboard preparation")
    log("Dashboard preparation finished")


def ensure_file(path: Path, step: str) -> None:
    if not path.exists():
        raise RuntimeError(f"{step} did not produce required file: {path}")


def log(message: str) -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    line = f"{stamp} {message}"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line)


if __name__ == "__main__":
    raise SystemExit(main())
