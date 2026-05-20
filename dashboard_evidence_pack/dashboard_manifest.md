# Dashboard Evidence Pack Manifest

Created for LLM analysis and presentation generation.

Source pages:

- `http://localhost:8000/frontend/`
- `http://localhost:8000/frontend/internal_insights.html`

Data status visible in dashboard: demo/synthetic sample data. Real-data validation is required before using the metrics for final business decisions.

## Page 01: Marketing Intelligence Dashboard

URL: `http://localhost:8000/frontend/`

Visible filters:

- Platform: All, app_store, instagram, tiktok, x
- Brand / competitor: All, telgani
- Sentiment: All, negative, neutral, positive
- Concern category: All, Poor or Slow Customer Service, Delay or Cancellation of Bookings/Delivery, Lack of Credibility & Unprofessionalism, Refund/Insurance/Fee Issues, Car Condition
- Date range: From / To fields are visible but not filled
- Search comments field is visible

Important metrics visible:

- Total comments: 12
- Negative signals: 2
- Urgent items: 4
- Top concern: 4, Poor or Slow Customer Service
- Market mood: mostly neutral
- Complaint movement: decreasing, recent 5 vs previous 7
- Sentiment split: Positive 33% / 4, Neutral 50% / 6, Negative 17% / 2
- Top concern categories: Poor or Slow Customer Service 4, Delay or Cancellation of Bookings/Delivery 4, Car Condition 2, Refund/Insurance/Fee Issues 1, Lack of Credibility & Unprofessionalism 0
- Urgent comments: 4
- Platform volumes: app_store 3, instagram 3, tiktok 3, x 3
- Raw Data table counts: Market Comments 12, Posts 3, Sources 4, Scrape Runs 4, Raw Records Log 12, Normalization Errors 0, Comment Analysis 12, Concern Category Summary 5, Sentiment Summary 3, Platform Summary 4, Brand Competitor Summary 1, Keyword Summary 95, Emerging Concerns 0, Urgent Comments 4, Marketing Opportunities 25, Content Ideas 4, Escalation Items 4

### Full Page Screenshots

- `screenshots/01_marketing_dashboard_full.png`: full marketing dashboard page from top to bottom.
- `screenshots/01_marketing_dashboard_full_part_01.png` through `screenshots/01_marketing_dashboard_full_part_24.png`: readable top-to-bottom page chunks for LLM review where the full-page screenshot may be too tall.

### Focused Section Screenshots

- `screenshots/01_marketing_dashboard_filters_and_guide.png`: title, global filters, dashboard guide, data-use description, demo/synthetic warning.
- `screenshots/01_marketing_dashboard_kpis_overview.png`: Executive Overview KPI cards and start of Customer Mood.
- `screenshots/01_marketing_dashboard_customer_mood_charts.png`: Customer Mood insight cards, sentiment split, complaint movement chart, traceable signals.
- `screenshots/01_marketing_dashboard_top_concerns.png`: ranked concern category cards with counts, percentages, owners, examples, and actions.
- `screenshots/01_marketing_dashboard_emerging_risks.png`: Emerging Risks section showing validation warning and empty emerging_concerns state.
- `screenshots/01_marketing_dashboard_urgent_comments_table.png`: urgent topic buckets and urgent comments table.
- `screenshots/01_marketing_dashboard_sentiment_trust_charts.png`: sentiment split, sentiment over time, sentiment by platform, sentiment by brand/competitor.
- `screenshots/01_marketing_dashboard_brand_competitors.png`: competitor comparison limitation, Telgani-only comparison, complaint category comparison, positive themes, messaging opportunities table.
- `screenshots/01_marketing_dashboard_platform_signals.png`: platform volume, sentiment by platform, concerns by platform, keywords by platform, best/risk-heavy sources, platform-specific opportunities table.
- `screenshots/01_marketing_dashboard_keyword_intelligence.png`: most frequent keywords, keyword trend, keyword breakdown by sentiment/platform/brand.
- `screenshots/01_marketing_dashboard_marketing_opportunities.png`: opportunity themes, claims to treat carefully, marketing opportunities table.
- `screenshots/01_marketing_dashboard_content_faq_ideas.png`: repeated questions, response templates, content/FAQ ideas table.
- `screenshots/01_marketing_dashboard_comment_explorer_table.png`: comment explorer table with platform, sentiment, concern, keywords, recommended action, and comment text.
- `screenshots/01_marketing_dashboard_raw_data_tables.png`: raw data table selector, table counts, Market Comments field list and visible rows.

Notes about unclear or cut-off content:

- Some long tables extend horizontally; focused screenshots capture the visible table columns, but not every far-right field in very wide raw data tables.
- The full-page screenshot is very tall; use the numbered full-part images for readable analysis.
- Competitor analysis is limited because only Telgani appears in the current data.
- Emerging Risks is empty and requires more historical/current data.
- Some keyword opportunity labels are raw words rather than polished business themes.

## Page 02: Internal Business Briefing

URL: `http://localhost:8000/frontend/internal_insights.html`

Visible date range:

- 2026-05-01 to 2026-05-06

Visible data status:

- Based on prepared sample data
- Demo data / synthetic sample
- Needs real data validation before decision-making

Important metrics visible:

- Comments analyzed: 12
- Positive sentiment: 33%
- Urgent items: 4
- Top concern: Delay or Cancellation of Bookings/Delivery, 4 comments
- Strong platform signal: tiktok, 2 positive signals
- Concern cards: Operations / Delay or Cancellation of Bookings/Delivery, Support / Poor or Slow Customer Service, Fleet / Car Condition
- Team actions: Marketing, Product, Support, Sales, Operations, Finance, Fleet, Management

### Full Page Screenshots

- `screenshots/02_internal_business_briefing_full.png`: full internal briefing page from top to bottom.
- `screenshots/02_internal_business_briefing_full_part_01.png` through `screenshots/02_internal_business_briefing_full_part_04.png`: readable top-to-bottom page chunks.

### Focused Section Screenshots

- `screenshots/02_internal_business_briefing_kpis.png`: page title, date range, sample-data status, executive KPI cards.
- `screenshots/02_internal_business_briefing_achievements.png`: Achievement Highlights / What went well cards.
- `screenshots/02_internal_business_briefing_concerns.png`: Areas of Concern / What needs attention cards.
- `screenshots/02_internal_business_briefing_team_actions.png`: Team Action Board with recommended actions by function.
- `screenshots/02_internal_business_briefing_evidence_strip.png`: Customer Evidence Strip with sample customer comments.

Notes about unclear or cut-off content:

- The page is narrower than the main dashboard, so screenshots are more compact.
- The top concern shown here is Delay or Cancellation of Bookings/Delivery, while the main dashboard overview shows Poor or Slow Customer Service. Both have 4 comments, so the top concern appears to be a tie.
- The achievement section includes a raw repeated keyword theme: "but"; this needs interpretation as a mixed praise/caveat pattern rather than a standalone business opportunity.
