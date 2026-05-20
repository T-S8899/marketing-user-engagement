# Dashboard Context

## Purpose

This file defines the dashboard boundary so visualization work stays clean and maintainable.

## Dashboard Rules

- The dashboard must not contain analysis logic.
- The dashboard should read prepared CSV/JSON outputs only.
- Brand styling must be separate from rendering and business logic.
- Frontend brand configuration belongs in `frontend/src/config/brand_config.json`.
- Dashboard components belong in `frontend/src/components/`.
- Dashboard views belong in `frontend/src/views/`.
- Prepared frontend data assets belong in `frontend/src/data/`.
- Styles belong in `frontend/src/styles/`.

## Expected Inputs

- Structured CSV outputs
- Analysis CSV/JSON outputs
- Brand presentation config from frontend config files
- Concern category presentation labels from `config/concern_categories.yaml`

## Expected Responsibilities

- Filter and display prepared metrics
- Render charts, tables, and summaries
- Apply brand styling without altering underlying logic
- Provide sample display mode when local CSV/JSON outputs are missing or empty
- Preserve Arabic and English text display
- Support shared filters for platform, brand/competitor, date, sentiment, concern category, and search
- Present marketing-ready signals from prepared analysis outputs and concern category config
- Keep every insight traceable to source comments, examples, source links, or raw references
- Use neutral language such as risk, signal, theme, and opportunity

## Explicit Non-Responsibilities

- Scraping
- Data cleaning
- Sentiment or categorization logic
- Competitor inference logic
- Concern category definition

## Implemented Dashboard

- Dashboard name: Golden Market Insights Dashboard
- Local entry file: `frontend/index.html`
- Announcement landing page entry file: `frontend/announcement.html`
- Internal insights announcement page entry file: `frontend/internal_insights.html`
- Recommended local server command: `python -m http.server 8000`
- Open URL: `http://localhost:8000/frontend/`
- Announcement URL: `http://localhost:8000/frontend/announcement.html`
- Internal insights URL: `http://localhost:8000/frontend/internal_insights.html`

## Implemented Frontend Structure

- `frontend/src/main.js`: app controller, shared filters, category-click filtering, expandable rows, table search, and table sorting
- `frontend/src/data/adapter.js`: shared local data adapter for processed CSV, analysis CSV/JSON, brand config, and concern category config
- `frontend/src/components/`: reusable cards, charts, filters, and table components
- `frontend/src/views/dashboard.js`: dashboard sections and view composition
- `frontend/src/views/AnnouncementPage.jsx`: requested announcement page export for future React/build integration
- `frontend/src/views/AnnouncementPage.js`: browser-safe implementation used by the current static ES-module frontend
- `frontend/src/views/InternalInsightsPage.jsx`: requested internal insights page export for future React/build integration
- `frontend/src/views/InternalInsightsPage.js`: browser-safe internal insights implementation used by the current static ES-module frontend
- `frontend/src/utils/`: CSV/YAML parsing and formatting helpers
- `frontend/src/styles/theme.css`: base design tokens
- `frontend/src/styles/brand.css`: replaceable brand tokens and brand mark styling
- `frontend/src/styles/layout.css`: responsive dashboard layout
- `frontend/src/styles/announcement.css`: isolated announcement landing page styling
- `frontend/src/styles/internal_insights.css`: isolated internal insights page styling
- `frontend/src/config/brand_config.json`: dashboard presentation config
- `frontend/src/config/announcement_content.json`: editable announcement landing page copy and CTA config

## Announcement Landing Page

- The announcement page is Arabic-first, RTL, mobile-first, and separate from dashboard analysis views.
- All campaign copy is loaded from `frontend/src/config/announcement_content.json`; component text is limited to safe fallback/empty-state copy.
- Brand name, logo text, and theme class come from `frontend/src/config/brand_config.json`.
- Current configured brand is Telgani; brand name, logo path, logo text, and theme class remain config-driven.
- Styling is isolated in `frontend/src/styles/announcement.css` and relies on CSS variables plus brand tokens from `brand.css`.
- The page includes a hero, CTA buttons, hook statements, expandable feature cards, editable quote-placeholder cards, a final CTA section, section navigation, a language toggle when English copy exists, and a mobile sticky CTA.
- Optional local logo, car, hero sticker, and feature sticker paths are loaded from `frontend/src/config/brand_config.json` and `frontend/src/config/announcement_content.json`.
- Missing logo/image/sticker assets fall back to text or lightweight placeholder visuals instead of broken images.
- Quote cards are explicitly placeholders unless connected to real sourced data later.
- The page does not read analysis CSVs, define concern categories, or perform marketing analysis logic.

## Internal Insights Announcement Page

- The internal insights page is for Marketing, Management, Operations, Customer Care, Product, Finance, and Fleet teams.
- Entry file: `frontend/internal_insights.html`.
- It reads prepared files only from `data/analysis/*.csv` and `data/analysis/*.json`.
- It does not read `data/processed/market_comments.csv`, define concern categories, or add sentiment/categorization rules.
- It presents executive snapshot, top risks, opportunities, brand-vs-competitor summary, platform signals, real customer voice, and recommended action queue from prepared outputs.
- Global filters support date, platform, brand/competitor, sentiment, and concern category.
- Click interactions set platform or concern filters and jump to customer evidence excerpts.
- Where prepared outputs do not include an explicit escalation team, owner labels are shown as routing suggestions rather than unsupported source claims.

## Implemented Views

- Executive Overview
- Top 5 Concern Categories
- Sentiment & Trust
- Brand vs Competitors
- Platform Performance
- Keyword Intelligence
- Emerging Concern Radar
- Urgent Comments / Escalation
- Marketing Opportunities
- Content Ideas / FAQ
- Comment Explorer
- Raw Data Explorer

## View-Level Analysis Presentation

- Executive Overview answers market mood, complaint movement, biggest risks, biggest opportunities, brand-vs-competitor position, and next recommended action.
- Top 5 Concern Categories displays rank, English and Arabic labels, count, percentage, sentiment split, movement, example comments, recommended action, and escalation owner from category config.
- Sentiment & Trust displays overall sentiment, sentiment by platform, sentiment by brand/competitor, sentiment over time, trust-risk comments, and credibility-related comments.
- Brand vs Competitors displays sentiment comparison, complaint theme comparison, positive theme comparison, repeated question signals, competitor praise, competitor risk signals, and messaging opportunities.
- Platform Performance displays volume, sentiment, concerns, keywords, source-level performance, and platform-specific content opportunities.
- Keyword Intelligence displays clickable Arabic and English keywords, plus keyword views by sentiment, platform, and brand/competitor.
- Emerging Concern Radar displays growth candidates, why-it-matters fields, example comments, and suggested actions from analysis outputs when available.
- Urgent Comments / Escalation displays high-urgency signals, grouped escalation buckets, suggested escalation paths, and status placeholders.
- Marketing Opportunities displays messaging themes, campaign opportunities, demand signals, competitor weaknesses, and claims to treat carefully.
- Content Ideas / FAQ displays repeated question signals, FAQ/social post angles, response templates, objections, and trace examples.
- Comment Explorer and Raw Data Explorer show expandable rows with source links, keywords, recommended actions, and raw references.
- Raw Data Explorer acts like a local multi-sheet browser for processed and analysis CSV files.

## Data Boundary

- The dashboard reads `data/processed/market_comments.csv`.
- The dashboard reads CSV and JSON files from `data/analysis/`.
- The dashboard loads concern category labels from `config/concern_categories.yaml`.
- The dashboard loads concern category dashboard metadata such as Arabic label, recommended action, dashboard group, trust-risk flag, and escalation owner from `config/concern_categories.yaml`.
- The dashboard does not hardcode concern categories in UI code.
- The dashboard does not overwrite or create analysis outputs.
- The dashboard does not define analysis rules; it renders prepared analysis fields and config metadata.

## Raw Data Explorer

- Loads sheet definitions from `frontend/src/data/rawTables.js`.
- Supports table selection across processed and analysis CSV outputs.
- Supports table-local search, sortable columns, pagination, expandable long-text rows, and CSV download links.
- Shows each table's meaning, row count, load status, empty/error state, and a selected-table data dictionary.
- Preserves Arabic display by reusing dashboard text-direction helpers.
- Shows raw references such as `raw_file_path`, `raw_record_hash`, source URLs, run IDs, and record IDs when those fields are present.
- Does not perform analysis calculations; it only browses local CSV outputs and field metadata.
