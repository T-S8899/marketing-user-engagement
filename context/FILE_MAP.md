# File Map

## Top-Level Intent

- `context/`: lightweight project memory for future sessions
- `config/`: editable configuration, never hardcoded into business logic
- `data/`: raw, processed, analysis, and report artifacts
- `src/`: Python implementation by responsibility
- `frontend/`: dashboard presentation layer
- `state/`: logs, run state, and traceability artifacts
- `tests/`: offline unit tests and generated local fixtures

## Context Files

- `context/PROJECT_OVERVIEW.md`: project goal, workflow, and non-negotiable architecture rules
- `context/CLAUDE_RULES.md`: how future sessions should use the context system
- `context/APIFY_SCRAPING_CONTEXT.md`: scraping constraints and configuration boundaries
- `context/CSV_SCHEMA_CONTEXT.md`: unified CSV role and schema expectations
- `context/MARKETING_ANALYSIS_CONTEXT.md`: marketing questions and analysis boundaries
- `context/DASHBOARD_CONTEXT.md`: dashboard responsibilities and prohibitions
- `context/REPORTING_CONTEXT.md`: reporting responsibilities and output expectations
- `context/FILE_MAP.md`: repo navigation reference
- `context/DECISIONS.md`: running log of confirmed architectural decisions

## Config Files

- `config/brands.yaml`: brand, competitor, and account target definitions
- `config/apify_actors.yaml`: platform actor IDs and scraping configuration
- `config/concern_categories.yaml`: the only valid source for concern categories
- `config/analysis_rules.yaml`: configurable thresholds and rule settings for analysis

## Data Areas

- `data/raw/`: immutable raw scrape payloads by platform
- `data/raw/runs/`: run-level metadata and manifests
- `data/processed/`: cleaned and unified structured datasets
- `data/processed/market_comments.csv`: canonical normalized comments and reviews
- `data/processed/posts.csv`: normalized post-level references
- `data/processed/sources.csv`: normalized source/account/app references
- `data/processed/normalization_errors.csv`: normalization error log
- `data/analysis/`: derived CSV/JSON outputs
- `data/reports/`: generated report artifacts
- `data/reports/executive_summary.md`: manager-readable executive summary
- `data/reports/top_concerns_report.md`: fixed concern category report with evidence
- `data/reports/sentiment_trust_report.md`: sentiment and trust signal report
- `data/reports/brand_vs_competitors_report.md`: brand and competitor comparison report
- `data/reports/platform_report.md`: platform performance report
- `data/reports/emerging_concerns_report.md`: emerging concern report
- `data/reports/marketing_opportunities_report.md`: campaign and positioning opportunity report
- `data/reports/content_ideas_report.md`: FAQ and content idea report
- `data/reports/escalation_report.md`: urgent comment escalation report
- `data/reports/data_quality_report.md`: input availability and quality report

## Source Areas

- `src/scrape/`: platform scraping orchestration
- `src/scrape/apify_client.py`: Apify API client for run start, polling, and dataset fetch
- `src/scrape/run_manager.py`: configured target execution, raw JSON preservation, metadata, and logs
- `src/scrape/run_scraper.py`: command-line scraper entry point
- `src/scrape/platforms/`: platform-specific actor input builders for TikTok, Instagram, X, and App Store
- `src/structure/`: raw-to-unified transformations
- `src/structure/normalization.py`: raw JSON normalization, timestamp parsing, deduplication, and CSV writing
- `src/structure/run_normalizer.py`: command-line entry point for writing processed CSV outputs
- `src/analyze/`: marketing analysis logic
- `src/dashboard/`: backend support for dashboard data preparation if needed
- `src/dashboard/run_dashboard.py`: local HTTP dashboard server entry point
- `src/reports/`: reporting generation logic
- `src/reports/report_builder.py`: Markdown-first report builder for executive, concern, sentiment, competitor, platform, opportunity, content, escalation, and data-quality reports
- `src/reports/run_reports.py`: command-line entry point for generating all Markdown reports
- `src/reports/templates/`: placeholder area for future Markdown templates
- `src/utils/`: shared helpers
- `src/utils/config.py`: YAML config loading and `.env` token loading
- `src/utils/logging.py`: JSON and CSV logging helpers
- `src/run_all.py`: full workflow entry point for scrape, normalize, analyze, report, and dashboard preparation
- `state/workflow.log`: step-by-step workflow execution log

## Tests

- `tests/test_pipeline.py`: offline `unittest` coverage for Apify run logging, raw JSON preservation, platform normalization, unified schema, stable IDs, deduplication, Arabic text, timestamp parsing, marketing analysis outputs, concern classification, urgency detection, brand grouping, keyword summaries, and report generation
- `tests/.tmp/`: ignored scratch area for generated test fixtures

## Frontend Areas

- `frontend/index.html`: local dashboard HTML entry point
- `frontend/announcement.html`: standalone announcement/campaign landing page entry point
- `frontend/internal_insights.html`: standalone internal insights announcement page entry point
- `frontend/src/main.js`: dashboard app controller and interaction wiring
- `frontend/src/announcement.js`: static browser entry point for the announcement page
- `frontend/src/internal_insights.js`: static browser entry point for the internal insights page
- `frontend/src/assets/`: optional local logo, car, and sticker assets referenced by frontend config files
- `frontend/src/data/adapter.js`: shared data adapter for local CSV/JSON and config files
- `frontend/src/data/rawTables.js`: Raw Data Explorer sheet catalog, download paths, descriptions, and frontend data dictionary entries
- `frontend/src/components/cards.js`: KPI card component
- `frontend/src/components/charts.js`: bar, sentiment, keyword, timeline, and category chart components
- `frontend/src/components/filters.js`: shared filter bar component
- `frontend/src/components/table.js`: searchable, sortable, expandable table component
- `frontend/src/views/dashboard.js`: Golden Market Insights Dashboard view composition
- `frontend/src/views/AnnouncementPage.js`: browser-safe announcement landing page renderer
- `frontend/src/views/AnnouncementPage.jsx`: requested announcement page export for future React/build usage
- `frontend/src/views/InternalInsightsPage.js`: browser-safe internal insights page renderer
- `frontend/src/views/InternalInsightsPage.jsx`: requested internal insights page export for future React/build usage
- `frontend/src/utils/csv.js`: CSV parser and simple concern-category YAML parser
- `frontend/src/utils/format.js`: display formatting helpers
- `frontend/src/styles/theme.css`: base dashboard design tokens
- `frontend/src/styles/brand.css`: replaceable brand styling
- `frontend/src/styles/layout.css`: responsive layout and component structure
- `frontend/src/styles/announcement.css`: isolated mobile-first announcement landing page styling
- `frontend/src/styles/internal_insights.css`: isolated data-first internal insights page styling
- `frontend/src/config/brand_config.json`: local dashboard presentation config
- `frontend/src/config/announcement_content.json`: editable Arabic-first announcement copy, CTA, section nav, logo/car/sticker asset paths, feature expansion text, bilingual copy, and quote-placeholder content
