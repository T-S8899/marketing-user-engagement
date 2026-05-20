# Decisions

## Confirmed

### 2026-05-06

- Project will be Python first and local files first.
- Scraping will use Apify API access loaded from `.env`.
- Raw scraped payloads must be preserved.
- `market_comments.csv` is the canonical structured source of truth.
- Dashboard logic must not include analysis logic.
- Analysis outputs must be written as CSV/JSON.
- Competitors must be configurable and not hardcoded.
- Brand styling must remain separate from logic.
- Brands, accounts, concern categories, and actor IDs must always be loaded from config files.
- Concern categories must only come from `config/concern_categories.yaml`.
- A dedicated markdown context system in `context/` will be used to reduce future repo scanning.

## Pending

- Exact `market_comments.csv` field list
- Raw file naming conventions
- Run manifest schema
- Logging file structure
- Analysis output filenames and schemas
- Dashboard data contract
- Reporting templates and export formats

Add new confirmed choices here as implementation begins.
