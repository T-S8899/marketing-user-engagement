# Local Marketing Intelligence

This project is a Python-first, local-file-first marketing intelligence system for collecting social comments and App Store reviews, structuring them into unified datasets, and producing analysis-ready outputs, dashboards, and reports.

## Purpose

- Scrape comments and reviews from X, TikTok, Instagram, and the App Store
- Preserve raw source data for traceability
- Standardize records into `market_comments.csv` as the source of truth
- Generate analysis outputs as CSV/JSON
- Feed dashboards and reports without embedding analysis logic in the dashboard layer

## Key Rules

- Secrets live in `.env` only. Never hardcode tokens or credentials.
- Brands, competitor accounts, concern categories, and actor IDs must come from config files.
- Raw scraped payloads must be preserved before transformation.
- Dashboard code must only read prepared datasets and presentation config.
- Brand styling must remain separate from business and analysis logic.

## Folder Structure

```text
context/
config/
data/
  raw/
    runs/
    tiktok/
    instagram/
    x/
    app_store/
  processed/
  analysis/
  reports/
frontend/
  src/
    components/
    views/
    data/
    styles/
    config/
src/
  scrape/
  structure/
  analyze/
  dashboard/
  reports/
  utils/
state/
```

## Commands

```bash
python -m src.scrape.run_scraper --platform tiktok
python -m src.scrape.run_scraper --platform instagram
python -m src.scrape.run_scraper --platform x
python -m src.scrape.run_scraper --platform app_store
python -m src.scrape.run_scraper --platform all
python -m src.scrape.run_scraper --platform tiktok --brand telgani
python -m src.structure.run_normalizer
python -m src.structure.run_normalize
python -m src.analyze.run_analysis
python -m src.analyze.run_llm_analysis
python -m src.reports.run_reports
python -m src.dashboard.run_dashboard
python -m src.run_all
```

Scraping requires configured platform targets and actor IDs before these commands can run successfully.

Useful workflow options:

- `--platform`: scrape one platform or `all` where supported.
- `--brand`: scrape configured targets for one brand, role, or account where supported.
- `--sample`: run a local testing path without calling Apify where supported.
- `--skip-scrape`: run downstream steps from existing local files.
- `--fail-fast` / `--no-fail-fast`: choose whether one platform failure stops scraping immediately.

## Setup Warnings

- Fill `.env` with `APIFY_TOKEN` before scraping.
- Do not commit secrets to source control.
- Fill `config/brands.yaml` before implementing brand or competitor workflows.
- Fill `config/apify_actors.yaml`, including the App Store actor, before scraper wiring.
- Fill `frontend/src/config/brand_config.json` before dashboard branding work.

## Source of Truth

`market_comments.csv` is the canonical structured dataset for downstream analysis, dashboards, and reporting.

Run normalization after scraping:

```bash
python -m src.structure.run_normalizer
```

## Scraping Outputs

- Raw JSON: `data/raw/<platform>/<run_id>.json`
- Run metadata: `data/raw/runs/<run_id>/run_metadata.json`
- Run log: `data/processed/scrape_runs.csv`
- Raw record trace log: `data/processed/raw_records_log.csv`

For X / Twitter, configure an optional `fallback_actor_id` in `config/apify_actors.yaml`. The fallback is used only when the main actor returns zero records, and records are deduplicated before raw JSON is written.

## Normalization Outputs

- Canonical comments and reviews: `data/processed/market_comments.csv`
- Post references: `data/processed/posts.csv`
- Source references: `data/processed/sources.csv`
- Error log: `data/processed/normalization_errors.csv`

Normalization preserves the full raw JSON record in `raw_record_json`, writes CSV files as UTF-8 with BOM for Arabic and English compatibility, and deduplicates using both `record_id` and `raw_record_hash`.

## Analysis Outputs

Run analysis after normalization:

```bash
python -m src.analyze.run_analysis
```

Analysis files are written to `data/analysis/`:

- `comment_analysis.csv`
- `concern_category_summary.csv`
- `sentiment_summary.csv`
- `platform_summary.csv`
- `brand_competitor_summary.csv`
- `keyword_summary.csv`
- `emerging_concerns.csv`
- `urgent_comments.csv`
- `marketing_opportunities.csv`
- `content_ideas.csv`
- `escalation_items.csv`

Concern categories are loaded only from `config/concern_categories.yaml`. Sentiment, urgency, keyword, and aggregation rules are configurable in `config/analysis_rules.yaml`.

## Optional LLM Analysis

LLM analysis is off by default. Enable it only when needed by setting `llm.enabled: true` in `config/analysis_rules.yaml`, filling `llm.model`, and adding the configured API key to `.env`.

```bash
python -m src.analyze.run_llm_analysis
```

LLM cost controls are required and configurable:

- `llm.max_records`
- `llm.batch_size`
- `llm.retry_limit`
- `llm.timeout_seconds`
- `llm.cache_path`

LLM outputs are separate from rule-based results:

- `data/analysis/llm_comment_analysis.csv`
- `data/analysis/llm_insight_summary.json`

The LLM layer preserves original text, includes rule-based labels beside LLM labels, uses caching, and does not overwrite `comment_analysis.csv`.

## Dashboard

The local dashboard is available at `frontend/index.html` and is designed to be served from the project root so it can read local CSV, JSON, and config files.

```bash
python -m http.server 8000
```

Or use the project dashboard command:

```bash
python -m src.dashboard.run_dashboard
```

Open:

```text
http://localhost:8000/frontend/
```

Additional frontend pages:

```text
http://localhost:8000/frontend/announcement.html
http://localhost:8000/frontend/internal_insights.html
```

The dashboard reads:

- `data/processed/market_comments.csv`
- `data/analysis/*.csv`
- `data/analysis/*.json`
- `config/concern_categories.yaml`
- `frontend/src/config/brand_config.json`

Styling is split for easy replacement:

- `frontend/src/styles/theme.css`
- `frontend/src/styles/brand.css`
- `frontend/src/styles/layout.css`

The UI includes sample mode when local data is empty, shared filters, reusable charts, searchable/sortable tables, expandable comment rows, Arabic text support, brand vs competitor filtering, platform filtering, date filtering, sentiment filtering, and concern category filtering.

The dashboard views are designed for marketing analysis, not only charts. They answer executive market mood questions, show traceable risks and opportunities, compare brand and competitors, expose platform and keyword signals, and keep comments expandable back to source links and raw references. Concern category names, Arabic labels, recommended actions, dashboard grouping, and escalation owners come from `config/concern_categories.yaml`.

The Raw Data Explorer works like a local multi-sheet browser for processed and analysis CSVs. It includes a table selector, searchable/sortable table, pagination, CSV download links, expandable long-text rows, raw references where available, clear empty/error states, and a data dictionary panel from `frontend/src/data/rawTables.js`.

## GitHub Pages Preview

The production-oriented project structure stays unchanged. Source files remain in `frontend/`, pipeline code remains in `src/`, and data/config inputs remain in `data/` and `config/`.

GitHub Pages uses a generated static preview bundle in `docs/`. Build it locally with:

```bash
python scripts/build_pages.py
```

To inspect the Pages bundle locally:

```bash
cd docs
python -m http.server 8000
```

Open:

```text
http://localhost:8000/
```

The build copies the static frontend, prepared `data/analysis` and `data/processed` files, and `config/concern_categories.yaml` into `docs/`, then adjusts relative paths so the dashboard works from the GitHub Pages site root.

Deployment is automated by `.github/workflows/pages.yml`. On pushes to `main`, GitHub Actions prepares a temporary root-style preview artifact from the root entry files plus the required static frontend, data, and config files. This supports quick stakeholder demos while keeping the original structured source as the source of truth. See `DEPLOYMENT_NOTES.md` for the temporary root preview note.

Expected public URL:

```text
https://t-s8899.github.io/marketing-user-engagement/
```

## Announcement Landing Page

The frontend includes a standalone Arabic-first campaign announcement page:

```text
http://localhost:8000/frontend/announcement.html
```

Run the local server first:

```bash
python -m src.dashboard.run_dashboard
```

The page is designed to be rebranded without editing component logic:

- Campaign copy and CTA links: `frontend/src/config/announcement_content.json`
- Brand name, logo text, and theme class: `frontend/src/config/brand_config.json`
- Brand tokens: `frontend/src/styles/brand.css`
- Page-specific layout and motion: `frontend/src/styles/announcement.css`
- Optional local logo, car, and sticker files: `frontend/src/assets/`

Quote cards are editable placeholders and should not be treated as real customer reviews unless connected to sourced data later.

Customize the announcement page by editing:

- `brandName`, `logoText`, `logoPath`, and `themeClass` in `frontend/src/config/brand_config.json`.
- `assets.logo_path`, `assets.hero_car_image`, `assets.hero_sticker_image`, and each feature `sticker_path` in `frontend/src/config/announcement_content.json`.
- Arabic and English headline, CTA, hook, feature, quote-placeholder, and final CTA text in `frontend/src/config/announcement_content.json`.
- Brand colors and gradients in `frontend/src/styles/brand.css`; page-specific spacing, glass effects, motion, and responsive behavior stay in `frontend/src/styles/announcement.css`.

If configured assets are missing, the page shows clean fallback text or placeholder visuals instead of broken images.

## Markdown Reports

Generate manager-readable Markdown reports from processed and analyzed local CSV files:

```bash
python -m src.reports.run_reports
```

Reports are written to `data/reports/`:

- `executive_summary.md`
- `top_concerns_report.md`
- `sentiment_trust_report.md`
- `brand_vs_competitors_report.md`
- `platform_report.md`
- `emerging_concerns_report.md`
- `marketing_opportunities_report.md`
- `content_ideas_report.md`
- `escalation_report.md`
- `data_quality_report.md`

Reports include evidence excerpts, record IDs or source references where available, and data limitations. Concern category labels, Arabic labels, recommended actions, and escalation owners are loaded from `config/concern_categories.yaml`.

## Full Workflow

Run the full local pipeline:

```bash
python -m src.run_all
```

The full workflow:

1. Scrapes configured Apify targets.
2. Normalizes raw JSON into `data/processed/market_comments.csv`.
3. Runs marketing analysis.
4. Generates Markdown reports.
5. Verifies dashboard files and data inputs are ready.

Testing without scraping:

```bash
python -m src.run_all --sample --skip-scrape
```

Workflow logs are written to `state/workflow.log`. If scraping fails for all requested platforms, downstream steps stop. If one platform fails while others succeed, `--fail-fast` controls whether the workflow stops immediately or continues and logs the platform failure.

## Tests

Run the offline unit tests without live Apify access:

```bash
python -m unittest discover tests
```

The tests use small local fixtures and mocked Apify responses to validate run logging, raw JSON preservation, normalization, deduplication, Arabic text preservation, timestamp parsing, analysis schemas, concern classification, urgency, keyword summaries, brand/competitor grouping, and Markdown report generation.
