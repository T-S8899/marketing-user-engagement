# Dashboard Page Notes

These notes describe the dashboard content for business analysis and presentation generation. They intentionally avoid code or implementation details.

## Page 01: Marketing Intelligence Dashboard

### Page Purpose

This page is a customer feedback intelligence dashboard. It converts comments and app reviews into executive KPIs, customer mood, concern categories, urgent escalation items, sentiment and trust views, brand/channel signals, keyword intelligence, marketing opportunities, content ideas, and evidence tables.

It serves marketing, product, support, operations, finance, fleet, sales, and management teams.

### Main KPIs Visible

- Total comments: 12
- Negative signals: 2
- Urgent items: 4
- Top concern: Poor or Slow Customer Service, 4 comments
- Market mood: mostly neutral
- Complaint movement: decreasing
- Sentiment split: 33% positive, 50% neutral, 17% negative
- Top concern counts: Poor or Slow Customer Service 4, Delay or Cancellation of Bookings/Delivery 4, Car Condition 2, Refund/Insurance/Fee Issues 1, Lack of Credibility & Unprofessionalism 0
- Platform volume: app_store 3, instagram 3, tiktok 3, x 3

### Main Charts Visible

- Sentiment split / market mood chart
- Complaint movement over time, May 1 to May 6, 2026
- Sentiment over time
- Sentiment by platform
- Sentiment by brand / competitor
- Complaint category comparison
- Positive theme comparison
- Volume by platform
- Concerns by platform
- Top keywords by platform
- Most frequent keywords
- Keyword trend over time
- Keyword breakdowns by sentiment, platform, and brand / competitor

### Main Tables Visible

- Urgent Comments table
- Messaging Opportunities table
- Platform-Specific Content Opportunities table
- Marketing Opportunities table
- Content & FAQ Ideas table
- Comment Explorer table
- Raw Data tables, including Market Comments and several processed/analysis datasets

### Business Questions This Page Answers

- What is the current customer mood?
- How many comments are negative or urgent?
- Which customer problems are most common?
- Which issues need immediate escalation?
- Which platform is producing which type of feedback?
- What are customers praising?
- What claims should marketing avoid overpromising?
- What FAQ or social content should be created?
- Which records support each dashboard claim?
- Is there enough competitor data for comparison?
- Which data tables are loaded, and which are empty?

### Things That Need Clarification

- The data is marked demo/synthetic and needs production validation.
- Top concern appears to be a tie between Poor or Slow Customer Service and Delay or Cancellation of Bookings/Delivery.
- Competitor comparison is not meaningful yet because only Telgani is present.
- Emerging Risks is empty, likely because there is not enough recent-vs-historical data.
- Neutral sentiment may understate urgent operational risk.
- Some concern classifications appear keyword-driven and should be reviewed against the actual comment text.
- Some marketing opportunity keywords are too literal, such as "but", and should be grouped into cleaner business themes.
- Some urgent items are positive/high-engagement rather than complaints; the dashboard should distinguish amplification opportunities from service recovery.

### Suggested Business Reading

The dashboard shows a customer journey with strengths and friction points. Positive signals include easy booking, fast app, good prices, useful interface, selection, and recommendation intent. Risks concentrate around support responsiveness, booking/delivery clarity, refund/fee transparency, and car condition. The most important strategic point is that urgency is higher than negative sentiment, meaning risk is not fully visible through sentiment alone.

## Page 02: Internal Business Briefing

### Page Purpose

This page is an executive briefing version of the main dashboard. It summarizes achievements, concerns, opportunities, and team actions using compact cards and evidence examples.

It is designed for leadership updates, management reviews, and cross-functional action planning.

### Main KPIs Visible

- Date range: 2026-05-01 to 2026-05-06
- Comments analyzed: 12
- Positive sentiment: 33%
- Urgent items: 4
- Top concern: Delay or Cancellation of Bookings/Delivery, 4 comments
- Strong platform signal: TikTok, 2 positive signals

### Main Charts Visible

- No traditional chart visuals are shown on this page. It uses KPI cards, insight cards, concern cards, team action cards, and evidence cards instead.

### Main Tables Visible

- No table grid is shown. The Team Action Board acts like an action matrix by department.
- The Customer Evidence Strip acts like a compact evidence list.

### Business Questions This Page Answers

- What are the headline metrics leaders should know?
- What went well?
- Which positive customer language can marketing and sales reuse?
- What needs attention?
- Which team owns each issue?
- Which urgent or high-risk issues require review?
- Which comments support the briefing?

### Things That Need Clarification

- The top concern differs from the main dashboard because both top categories have 4 comments.
- The "Repeat theme: but" achievement is a raw keyword and needs human interpretation.
- Some concern evidence examples do not perfectly match the concern label and should be checked before presenting as final findings.
- The briefing is based on sample data and should not be treated as production performance.
- Team action priorities should eventually include owner, status, due date, and impact metric.

### Suggested Business Reading

The briefing tells a concise leadership story: Telgani has positive product experience signals, especially around booking ease and app speed, but customer trust risks exist around booking/delivery clarity, support responsiveness, refunds/fees, and car condition. The briefing is useful as a weekly management artifact once real data is loaded and classification rules are validated.

## Cross-Page Interpretation

The two pages tell the same broad story in different formats:

- The main dashboard is exploratory and evidence-heavy.
- The internal briefing is executive-facing and action-oriented.

Important relationships:

- Negative sentiment is 2 comments, but urgent items are 4. Urgency is therefore a broader risk indicator than sentiment.
- Two concern categories tie at 4 comments: customer service and booking/delivery.
- App Store signals include refund, fee, app crash, and payment confirmation concerns.
- X signals include urgent support response needs.
- Instagram signals include car condition and delivery/change clarity.
- TikTok includes positive booking/app experience and delivery-time visibility.
- Marketing should reuse easy booking, fast app, selection, and pricing language, but only after fixing or clearly explaining support, delivery, fee, and condition concerns.

Recommended presentation angle:

1. Start with the caveat that the current data is demo/sample.
2. Explain what the dashboard is designed to answer.
3. Present the KPI story: 12 comments, 33% positive, 50% neutral, 17% negative, 4 urgent.
4. Explain that neutral does not mean low risk.
5. Highlight the top issue tie: support responsiveness and booking/delivery clarity.
6. Show platform-specific signals.
7. Show the action board by department.
8. End with the data trust caveats and what must happen before production decisions.
