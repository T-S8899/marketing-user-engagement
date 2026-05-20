# Claude Rules

## Session Objective

Future sessions should read only the context files relevant to the task instead of scanning the whole repository.

## Repository Rules

- Do not hardcode brands, competitor accounts, concern categories, or Apify actor IDs.
- Load secrets from `.env`.
- Load concern categories only from `config/concern_categories.yaml`.
- Preserve raw scraped responses before transformation.
- Treat `market_comments.csv` as the source of truth after structuring.
- Keep logs and run metadata for traceability.
- Keep dashboard rendering separate from analysis logic.
- Write analysis outputs as CSV/JSON that other layers can consume.
- Keep brand styling and visual config separate from data logic.

## Working Pattern

- Read `context/PROJECT_OVERVIEW.md` first for any new implementation task.
- Read only the domain-specific context file needed for the task:
  - scraping -> `context/APIFY_SCRAPING_CONTEXT.md`
  - structuring/schema -> `context/CSV_SCHEMA_CONTEXT.md`
  - analysis -> `context/MARKETING_ANALYSIS_CONTEXT.md`
  - dashboard -> `context/DASHBOARD_CONTEXT.md`
  - reports -> `context/REPORTING_CONTEXT.md`
- Check `context/DECISIONS.md` before introducing new patterns or changing assumptions.
- Check `context/FILE_MAP.md` before searching the repo broadly.

## Out of Scope For This Scaffold

- Scraper implementation
- CSV generation code
- Analysis models or heuristics
- Dashboard code
- Reporting code

This scaffold exists to reduce context-loading cost and keep future work aligned.
