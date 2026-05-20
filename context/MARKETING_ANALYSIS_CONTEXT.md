# Marketing Analysis Context

## Purpose

This file captures the business questions and guardrails for the analysis layer.

## Reference Questions

- What are customers complaining about most?
- What positive themes exist?
- How does brand sentiment compare with competitors?
- How do themes differ by platform?
- How are campaigns being received?
- What trust blockers appear repeatedly?
- What feature requests repeat over time?
- What strengths and weaknesses stand out for competitors?
- Which comments are urgent?
- What should marketing do next?

## Analysis Layer Rules

- Analysis logic belongs in `src/analyze/`, not the dashboard.
- Analysis outputs must be written as CSV and/or JSON for downstream use.
- Concern categories must be loaded from `config/concern_categories.yaml`.
- Brand and competitor definitions must be loaded from `config/brands.yaml`.
- Analysis rules and thresholds should come from `config/analysis_rules.yaml`.
- Keep the canonical structured CSV separate from derivative analysis outputs.
- Preserve original text in analysis outputs.
- Include confidence scores and explainable reason fields for per-comment labels.
- Keep sentiment, urgency, keyword, and aggregation rules configurable in `config/analysis_rules.yaml`.

## Expected Output Types

- Sentiment summaries
- Concern category rollups
- Positive theme summaries
- Competitor comparison tables
- Platform comparison views
- Urgent issue extracts
- Recommended next-action summaries

## Implemented Command

```bash
python -m src.analyze.run_analysis
python -m src.analyze.run_llm_analysis
```

## Implemented Outputs

All files are written to `data/analysis/`.

- `comment_analysis.csv`: per-comment sentiment, concern category, urgency, keywords, confidence scores, reasons, and original text
- `concern_category_summary.csv`: category rollup with sentiment and urgency counts
- `sentiment_summary.csv`: sentiment rollup
- `platform_summary.csv`: platform rollup
- `brand_competitor_summary.csv`: brand or competitor rollup
- `keyword_summary.csv`: repeated keyword rollup
- `emerging_concerns.csv`: recent concern growth candidates
- `urgent_comments.csv`: urgent per-comment subset
- `marketing_opportunities.csv`: positive repeated themes for marketing use
- `content_ideas.csv`: repeated neutral or negative concerns to address in content
- `escalation_items.csv`: urgent items formatted for follow-up
- `llm_comment_analysis.csv`: optional LLM enrichment output, separate from rule-based results
- `llm_insight_summary.json`: optional LLM run summary, cost-control settings, cache stats, and error counts

## Implemented Logic

- Concern categories are loaded only from `config/concern_categories.yaml`.
- Category matching uses category `keywords` when provided, with `id`, `label`, and `description` as fallback matching text.
- Sentiment uses configurable positive and negative keyword lists plus App Store rating signals, including phrase-aware keyword matching.
- Urgency uses configurable urgency keywords, optional engagement thresholds, and optional negative-sentiment escalation, including phrase-aware keyword matching.
- Keywords are extracted with configurable stopwords and minimum length.
- Emerging concerns compare recent category volume against older volume using configurable thresholds.
- Competitor comparison is produced from `brand_or_competitor` values already present in `market_comments.csv`.

## Tested Logic

- Rule-based sentiment output schema
- Concern category classification loaded from config
- Top concern ranking through summary outputs
- Phrase-aware keyword matching for configured sentiment and urgency phrases
- Emerging concern output schema
- Urgent comment detection
- Brand vs competitor grouping
- Keyword summary output schema
- Markdown report generation from small fixture CSVs

## Optional LLM Layer

- LLM analysis is optional and defaults to off through `llm.enabled: false` in `config/analysis_rules.yaml`.
- LLM API keys are loaded from `.env` using the configured `llm.api_key_env`.
- Cost controls are required and configurable: `llm.max_records`, `llm.batch_size`, `llm.retry_limit`, and `llm.timeout_seconds`.
- Caching is required and stored at `llm.cache_path`.
- LLM outputs never overwrite rule-based outputs.
- LLM enrichment merges safely by `record_id` and preserves original text, rule-based labels, raw references, cache status, and error messages.
- Prompts require JSON-only responses with brief evidence summaries and no chain-of-thought.
- Concern category choices for LLM analysis are loaded only from `config/concern_categories.yaml`; `uncategorized` is used when no configured category fits.

## Guardrails

- Avoid hardcoded brand assumptions.
- Keep rules configurable where possible.
- Preserve reproducibility by saving generated analysis artifacts to `data/analysis/`.
- When concern categories are empty, comments are tagged as `uncategorized` with zero category confidence.
