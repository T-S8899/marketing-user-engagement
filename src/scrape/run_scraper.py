from __future__ import annotations

import argparse
import sys
from typing import Any

from src.scrape.apify_client import ApifyClient
from src.scrape.run_manager import SUPPORTED_PLATFORMS, RunManager
from src.utils.config import ConfigError, load_apify_actors_config, load_brands_config, require_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Apify scraping for configured marketing targets.")
    parser.add_argument(
        "--platform",
        choices=sorted(SUPPORTED_PLATFORMS | {"all"}),
        default="all",
        help="Platform to scrape. Defaults to all configured platforms.",
    )
    parser.add_argument("--brand", default="", help="Only scrape targets for this brand name or role.")
    parser.add_argument("--fail-fast", action=argparse.BooleanOptionalAction, default=True, help="Stop on the first platform failure.")
    parser.add_argument("--sample", action="store_true", help="Validate scraper configuration without calling Apify.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        brands_config = load_brands_config()
        if args.brand:
            brands_config = filter_brand_targets(brands_config, args.brand)
        platforms = sorted(SUPPORTED_PLATFORMS) if args.platform == "all" else [args.platform]
        if args.sample:
            print(f"Sample scrape check: platforms={', '.join(platforms)} brand={args.brand or 'all'}")
            return 0
        token = require_env("APIFY_TOKEN")
        actors_config = load_apify_actors_config()
        manager = RunManager(ApifyClient(token), brands_config, actors_config)
        failures = []
        for platform in platforms:
            try:
                for result in manager.run_platform(platform):
                    print(
                        f"{result.platform} {result.run_id}: {result.status} "
                        f"({result.records_count} records) -> {result.raw_path}"
                    )
            except Exception as exc:
                failures.append(f"{platform}: {exc}")
                print(f"Platform failed: {platform}: {exc}", file=sys.stderr)
                if args.fail_fast:
                    raise
        if failures:
            print("Scraping completed with platform failures:", file=sys.stderr)
            for failure in failures:
                print(f"- {failure}", file=sys.stderr)
            return 1
        return 0
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Scraping failed: {exc}", file=sys.stderr)
        return 1


def filter_brand_targets(brands_config: dict[str, Any], brand: str) -> dict[str, Any]:
    wanted = brand.strip().lower()
    filtered = dict(brands_config)
    platform_targets = brands_config.get("platform_targets", {})
    filtered_targets = {}
    for platform, targets in platform_targets.items():
        if isinstance(targets, list):
            filtered_targets[platform] = [
                target for target in targets
                if str(target.get("brand", "")).lower() == wanted
                or str(target.get("role", "")).lower() == wanted
                or str(target.get("account", "")).lower() == wanted
            ]
    filtered["platform_targets"] = filtered_targets
    return filtered


if __name__ == "__main__":
    raise SystemExit(main())
