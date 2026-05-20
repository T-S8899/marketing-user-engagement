# Apify Scraping Context

## Purpose

This context file defines how scraping should be organized once implementation begins.

## Data Sources

- X / Twitter comments or replies
- TikTok comments
- Instagram comments
- App Store reviews

## Required Rules

- Use Apify API for scraping workflows.
- Read `APIFY_TOKEN` from `.env`.
- Never hardcode actor IDs.
- Load actor IDs and platform actor settings from `config/apify_actors.yaml`.
- Load brand and competitor targets from `config/brands.yaml`.
- Preserve raw actor outputs in platform-specific `data/raw/<platform>/` directories.
- Preserve run metadata in `data/raw/runs/`.
- Keep structured outputs separate from raw payloads.
- Keep logs for traceability in `state/` or a dedicated logging pattern chosen later.
- Write run summaries to `data/processed/scrape_runs.csv`.
- Write raw record trace rows to `data/processed/raw_records_log.csv`.

## Expected Scraping Responsibilities

- Resolve the correct actor and input template from config.
- Execute a run with brand or competitor targets from config.
- Save the raw payload without mutation.
- Capture run metadata such as timestamps, actor used, platform, target brand, and output file path.

## Implemented Flow

1. Start an Apify actor run.
2. Poll until the actor run reaches a terminal status.
3. Fetch the default dataset when the run succeeds.
4. Save raw JSON to `data/raw/<platform>/<run_id>.json`.
5. Save metadata to `data/raw/runs/<run_id>/run_metadata.json`.
6. Append run logs to `data/processed/scrape_runs.csv`.
7. Append raw record trace rows to `data/processed/raw_records_log.csv`.

## X / Twitter Fallback

- The main X actor ID is loaded from `actors.x.actor_id` in the legacy nested shape or `x.main_actor` in the current top-level config shape.
- An optional fallback actor ID may be configured at `actors.x.fallback_actor_id`, `x.fallback_actor_id`, or `x.fallback_replies_actor`.
- The fallback actor is only called when the main actor returns zero records.
- X records are deduplicated before raw JSON is written.

## Actor Config Compatibility

- Scraper config loading supports the legacy nested shape `actors.<platform>.actor_id`.
- Scraper config loading also supports the current top-level keys: `tiktok.comments_actor`, `instagram.comments_actor`, `x.main_actor`, and `app_store.actor`.
- Platform `default_input` values are normalized into actor input defaults when present.

## Implemented Files

- `src/scrape/apify_client.py`: Apify HTTP client for starting runs, polling, and fetching datasets
- `src/scrape/run_manager.py`: target orchestration, raw JSON writing, metadata writing, and CSV logs
- `src/scrape/run_scraper.py`: command-line entry point
- `src/scrape/platforms/`: platform-specific input builders
- `src/utils/config.py`: `.env`, brand config, and actor config loading
- `src/utils/logging.py`: JSON and CSV writing helpers

## Open Implementation Decisions

- Retry behavior
- Pagination strategy per platform
- Rate-limit handling
- Exact platform-specific actor input templates

Record final choices in `context/DECISIONS.md`.
