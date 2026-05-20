# LLM Analysis Prompt

You are a senior business analyst and presentation strategist.

You are given a dashboard evidence pack containing screenshots and notes from two dashboard pages:

1. `Marketing Intelligence Dashboard`
2. `Internal Business Briefing`

Your job is to analyze the dashboard content and create a business-ready presentation outline. Do not explain code or implementation. Focus on what the dashboard means for executives, marketing, finance, product, operations, customer support, fleet, sales, and management.

Use these files:

- `dashboard_manifest.md`
- `page_notes.md`
- All screenshots in `screenshots/`

Reference screenshots by filename whenever you discuss evidence. Example: "See `screenshots/01_marketing_dashboard_kpis_overview.png`."

## Analysis Tasks

For each dashboard page:

1. Explain the page objective.
2. Identify the visible KPIs, metrics, charts, tables, filters, and insight sections.
3. Explain each metric in simple business language.
4. Explain whether higher or lower is good, where applicable.
5. Explain the business logic behind percentages, counts, rankings, and comparisons.
6. Identify the story each chart or table tells.
7. Extract meaningful business insights, not just descriptions.
8. Identify risks, opportunities, and operational implications.
9. Explain what each stakeholder group should care about:
   - Executives / management
   - Marketing
   - Finance
   - Product
   - Operations
   - Customer support
   - Fleet
   - Sales
10. Identify data trust caveats and anything that needs clarification.

## Important Interpretation Rules

- Treat the data as demo/synthetic sample data unless screenshots prove otherwise.
- Do not overstate conclusions from small sample sizes.
- Call out that competitor comparison is limited because only Telgani appears in the current data.
- Call out that Emerging Risks is empty and requires more historical/current data.
- Call out that Top Concern appears to be a tie between Poor or Slow Customer Service and Delay or Cancellation of Bookings/Delivery, both with 4 comments.
- Call out that negative sentiment is lower than urgent items, so urgency is a broader operational risk signal than sentiment.
- Call out that neutral sentiment can still contain urgent or serious operational issues.
- Be careful with raw keyword themes such as "but"; convert them into business meaning, such as mixed praise with caveats.
- When a screenshot or metric is unclear, say "Needs clarification."

## Key Screenshots To Use

Marketing Intelligence Dashboard:

- `screenshots/01_marketing_dashboard_full.png`
- `screenshots/01_marketing_dashboard_filters_and_guide.png`
- `screenshots/01_marketing_dashboard_kpis_overview.png`
- `screenshots/01_marketing_dashboard_customer_mood_charts.png`
- `screenshots/01_marketing_dashboard_top_concerns.png`
- `screenshots/01_marketing_dashboard_urgent_comments_table.png`
- `screenshots/01_marketing_dashboard_sentiment_trust_charts.png`
- `screenshots/01_marketing_dashboard_brand_competitors.png`
- `screenshots/01_marketing_dashboard_platform_signals.png`
- `screenshots/01_marketing_dashboard_keyword_intelligence.png`
- `screenshots/01_marketing_dashboard_marketing_opportunities.png`
- `screenshots/01_marketing_dashboard_content_faq_ideas.png`
- `screenshots/01_marketing_dashboard_comment_explorer_table.png`
- `screenshots/01_marketing_dashboard_raw_data_tables.png`

Internal Business Briefing:

- `screenshots/02_internal_business_briefing_full.png`
- `screenshots/02_internal_business_briefing_kpis.png`
- `screenshots/02_internal_business_briefing_achievements.png`
- `screenshots/02_internal_business_briefing_concerns.png`
- `screenshots/02_internal_business_briefing_team_actions.png`
- `screenshots/02_internal_business_briefing_evidence_strip.png`

Use the numbered `*_full_part_XX.png` screenshots when a full-page image is too tall to inspect clearly.

## Presentation Generation Task

Create a presentation outline with 10 to 14 slides.

For each slide include:

- Slide title
- Main message
- Recommended visual or screenshot filename
- Key points to say verbally
- Business implication
- Suggested audience focus

Recommended slide flow:

1. Title / dashboard purpose
2. Data scope and caveats
3. Executive KPI snapshot
4. Customer mood and sentiment
5. Top concern categories
6. Urgent escalation queue
7. Platform-specific signals
8. Brand / competitor limitations
9. Keyword and content intelligence
10. Marketing opportunities and claims to treat carefully
11. Internal team action board
12. Evidence examples from customer comments
13. Data trust and clarification needs
14. Recommended next actions

## Output Format

Produce the following sections:

1. Executive Summary
2. Page-by-Page Dashboard Interpretation
3. Metric and KPI Glossary
4. Business Insights
5. Risks and Opportunities
6. Stakeholder Interpretation
7. Data Trust Caveats
8. Presentation Outline
9. Questions to Ask Next

Keep the language simple, executive-friendly, and insight-oriented. Avoid implementation details.
