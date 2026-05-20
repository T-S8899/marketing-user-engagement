# CSV Schema Context

## Purpose

This file defines the role of the unified structured dataset and the schema expectations future code should follow.

## Canonical Output

`market_comments.csv` is the source of truth for downstream analysis, dashboarding, and reporting.

## Schema Principles

- Every structured record should map back to a raw source record.
- Platform-specific fields may exist upstream, but the unified dataset should normalize common fields.
- The structured dataset should support both brand and competitor analysis.
- The schema should be stable enough for reproducible analysis pipelines.
- Derived fields should be documented when introduced.

## Implemented Outputs

- `data/processed/market_comments.csv`: canonical unified comment and review dataset
- `data/processed/posts.csv`: post-level references extracted from raw records when available
- `data/processed/sources.csv`: source/account/app references extracted from raw records when available
- `data/processed/normalization_errors.csv`: per-file or per-record normalization errors

## `market_comments.csv` Fields

- `record_id`: stable SHA-256 generated from platform, source ID or URL, comment ID or text, and datetime
- `raw_record_hash`: stable SHA-256 of the full raw JSON record
- `platform`: `tiktok`, `instagram`, `x`, or `app_store`
- `source_type`: `social_comment` or `app_review`
- `scrape_run_id`: raw scrape run ID inferred from the raw file name
- `raw_file_path`: source raw JSON file
- `raw_record_index`: index of the record inside the raw JSON file
- `brand`: brand value from scrape metadata when available
- `brand_or_competitor`: target grouping from scrape metadata when available
- `source_account`: source account, app, or configured target when available
- `source_id`: source/account/app identifier when available
- `source_url`: source URL when available
- `post_id`: related post/video/tweet/thread ID when available
- `comment_id`: comment, review, or tweet ID when available
- `parent_id`: parent comment or reply ID when available
- `author_id`: author/user ID when available
- `author_username`: author username or handle when available
- `author_display_name`: author display name when available
- `text`: comment or review text, preserving Arabic and English
- `language`: language or locale value when available
- `posted_at`: safely parsed UTC ISO timestamp when parseable
- `posted_at_raw`: original timestamp value
- `scraped_at`: scrape metadata creation timestamp when available
- `likes`: like/favorite count when available
- `replies`: reply/comment count when available
- `shares`: share/repost count when available
- `views`: view/play count when available
- `rating`: App Store rating when available
- `app_version`: App Store app version when available
- `country`: country, country code, or region when available
- `sentiment_label`: reserved for later analysis output
- `concern_category`: reserved for later analysis output
- `urgency_flag`: reserved for later analysis output
- `raw_field_names`: field names present in the original raw record
- `raw_record_json`: full raw JSON record serialized without ASCII escaping

## Rules

- Concern categories must come only from `config/concern_categories.yaml`.
- Do not bake analysis conclusions into the canonical CSV beyond clearly defined derived columns.
- Keep schema evolution documented in `context/DECISIONS.md`.
- Missing values are written as empty CSV cells.
- CSVs are written as UTF-8 with BOM to preserve Arabic text and improve spreadsheet compatibility.
- Deduplication uses both `record_id` and `raw_record_hash`; duplicates are not allowed in the final CSV.
- When duplicate records exist, the row with the best combination of populated fields, latest timestamp, and text length is kept.
- Raw references are preserved through `scrape_run_id`, `raw_file_path`, `raw_record_index`, `raw_record_hash`, and `raw_record_json`.

## Normalization Command

```bash
python -m src.structure.run_normalizer
```

## Schema Tests

Run offline schema and transformation tests with:

```bash
python -m unittest discover tests
```

The tests validate the unified `market_comments.csv` header, stable `record_id` generation, `raw_record_hash`, deduplication, platform-specific normalization, Arabic text preservation, safe timestamp parsing, raw references, and downstream analysis/report fixture compatibility.

## Downstream Analysis Outputs

`market_comments.csv` feeds the marketing analysis layer. Analysis outputs are derivative files in `data/analysis/` and must not replace the canonical normalized dataset.

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
