# Data Quality Report

Generated: `2026-05-06T07:47:21.173440+00:00`

## Input File Status

| Input | Path | Rows | Status |
| --- | --- | --- | --- |
| market_comments | data/processed/market_comments.csv | 12 | available |
| comment_analysis | data/analysis/comment_analysis.csv | 0 | available |
| concern_summary | data/analysis/concern_category_summary.csv | 0 | available |
| sentiment_summary | data/analysis/sentiment_summary.csv | 0 | available |
| platform_summary | data/analysis/platform_summary.csv | 0 | available |
| brand_summary | data/analysis/brand_competitor_summary.csv | 0 | available |
| keyword_summary | data/analysis/keyword_summary.csv | 0 | available |
| emerging_concerns | data/analysis/emerging_concerns.csv | 0 | available |
| urgent_comments | data/analysis/urgent_comments.csv | 0 | available |
| marketing_opportunities | data/analysis/marketing_opportunities.csv | 0 | available |
| content_ideas | data/analysis/content_ideas.csv | 0 | available |
| escalation_items | data/analysis/escalation_items.csv | 0 | available |

## Quality Checks

- **Processed comments:** 12
- **Analyzed comments:** 12
- **Missing text rows:** 0
- **Missing sentiment rows:** 12
- **Missing category rows:** 12
- **Configured concern categories:** 5

## Data Limitations

- Findings are based only on local processed and analysis CSV files available at report generation time.
- Small samples, missing dates, missing source URLs, or empty analysis files reduce confidence.
- Reports summarize prepared rule-based outputs and do not add unsupported claims beyond the evidence excerpts.
- Concern category names, Arabic labels, recommended actions, and owners are loaded from config files.
