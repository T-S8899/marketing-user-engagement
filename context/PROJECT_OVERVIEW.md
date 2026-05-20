# Project Overview

## Goal

Build a local marketing intelligence system that collects public feedback from social platforms and the App Store, standardizes it, analyzes it, and produces reporting outputs for marketing decision-making.

## Supported Platforms

- X / Twitter
- TikTok
- Instagram
- App Store

## Core Workflow

1. Scrape platform data using Apify actors and API access loaded from configuration.
2. Preserve raw responses in `data/raw/` and run-level metadata in `data/raw/runs/`.
3. Transform raw records into a unified schema.
4. Write the canonical structured dataset to `market_comments.csv`.
5. Produce analysis outputs in CSV and JSON.
6. Feed dashboards and reports from prepared outputs only.

## Local Commands

```bash
python -m src.scrape.run_scraper
python -m src.structure.run_normalize
python -m src.analyze.run_analysis
python -m src.reports.run_reports
python -m src.dashboard.run_dashboard
python -m src.run_all
python -m unittest discover tests
```

## Workflow Safety

- `src.run_all` runs scrape, normalize, analysis, reports, and dashboard preparation in order.
- `--skip-scrape` uses existing local files for downstream work.
- `--sample` supports local testing without Apify scraping.
- `--fail-fast` / `--no-fail-fast` controls whether one platform failure stops scraping immediately.
- If scraping fails for all requested platforms, later steps must not continue silently.
- Each workflow step logs progress and failures to `state/workflow.log`.

## Test Coverage

- Offline tests use mocked Apify responses and small local fixture CSV/JSON files.
- Tests do not require a live Apify token or network access.
- Important transformations and calculations are covered, including raw preservation, normalization, deduplication, Arabic text preservation, timestamp parsing, sentiment/category/urgency outputs, brand grouping, keyword summaries, and Markdown report generation.

## Non-Negotiable Rules

- Python first
- Local files first
- Use `.env` for secrets
- Never hardcode brands, accounts, concern categories, or actor IDs
- Preserve raw scraped payloads
- Keep logs for traceability
- Dashboard contains no analysis logic
- Competitors are configurable
- Brand styling is separate from logic

## Required User-Supplied Inputs

- `config/brands.yaml`
- `config/apify_actors.yaml`
- `.env` with `APIFY_TOKEN`
- `frontend/src/config/brand_config.json`

## Canonical Dataset

`market_comments.csv` is the source of truth for downstream marketing analysis.
