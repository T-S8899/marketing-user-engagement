# Reporting Context

## Purpose

This file defines the reporting layer that turns prepared analysis outputs into stakeholder-ready summaries.

## Reporting Rules

- Reporting logic should consume structured and analyzed outputs, not raw platform payloads.
- Reports should be reproducible from saved files in `data/processed/` and `data/analysis/`.
- Generated report artifacts should be written to `data/reports/`.
- Reporting code should live in `src/reports/`.
- Brand styling or narrative templates should remain configurable and separate from analysis logic.
- Concern category names, Arabic labels, recommended actions, and escalation owners must be loaded from config files.
- Reports should include evidence excerpts and record IDs or source references whenever available.
- Reports should use neutral language such as risk, signal, theme, and opportunity.
- Reports should include data limitations when files are missing, empty, or sparse.

## Possible Report Outputs

- Weekly marketing summaries
- Brand vs competitor comparison reports
- Platform-specific feedback snapshots
- Campaign reaction summaries
- Escalation or urgent issue digests

## Implemented Command

```bash
python -m src.reports.run_reports
```

## Implemented Outputs

- `data/reports/executive_summary.md`
- `data/reports/top_concerns_report.md`
- `data/reports/sentiment_trust_report.md`
- `data/reports/brand_vs_competitors_report.md`
- `data/reports/platform_report.md`
- `data/reports/emerging_concerns_report.md`
- `data/reports/marketing_opportunities_report.md`
- `data/reports/content_ideas_report.md`
- `data/reports/escalation_report.md`
- `data/reports/data_quality_report.md`

## Implemented Files

- `src/reports/report_builder.py`: deterministic Markdown report generation from processed and analysis CSVs
- `src/reports/run_reports.py`: command-line entry point
- `src/reports/templates/`: reserved for future reusable Markdown templates

## Input Expectations

- `market_comments.csv`
- Analysis CSV outputs
- Analysis JSON outputs
- Config-driven brand and competitor definitions
- `config/concern_categories.yaml` for report concern labels, Arabic labels, recommended actions, and escalation owners

## Guardrails

- Do not duplicate analysis logic in the reporting layer.
- Keep report generation deterministic from saved inputs.
- Do not make unsupported claims when evidence rows are unavailable.
