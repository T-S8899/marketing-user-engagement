import { kpiCard } from "../components/cards.js";
import { barChart, categoryRanking, keywordCloud, sentimentSplit, sentimentTimeline, timeline } from "../components/charts.js";
import { dataTable } from "../components/table.js";
import { RAW_TABLES, rawTableById } from "../data/rawTables.js";
import { isArabic, number, shortText } from "../utils/format.js";

const commentColumns = [
  { key: "platform", label: "Platform", length: 18 },
  { key: "brand_or_competitor", label: "Brand / competitor", length: 26 },
  { key: "sentiment_label", label: "Sentiment", length: 14 },
  { key: "concern_category_label", label: "Concern", length: 42 },
  { key: "keywords", label: "Keywords", length: 42 },
  { key: "recommended_action", label: "Recommended action", length: 72 },
  { key: "text", label: "Comment", length: 90 }
];

const rawColumns = [
  { key: "platform", label: "Platform", length: 18 },
  { key: "source_type", label: "Source", length: 20 },
  { key: "source_url", label: "Source link", length: 45 },
  { key: "record_id", label: "Record ID", length: 28 },
  { key: "raw_file_path", label: "Raw reference", length: 70 },
  { key: "text", label: "Text", length: 90 }
];

export const navItems = [
  ["overview", "Executive Overview"],
  ["customer-mood", "Customer Mood"],
  ["top-concerns", "Top Concerns"],
  ["emerging-radar", "Emerging Risks"],
  ["urgent-escalation", "Urgent Comments"],
  ["sentiment-trust", "Sentiment & Trust"],
  ["brand-competitors", "Brand vs Competitors"],
  ["platform-performance", "Platform Signals"],
  ["keyword-intelligence", "Keywords"],
  ["marketing-opportunities", "Opportunities"],
  ["content-ideas", "Content & FAQ Ideas"],
  ["comment-explorer", "Comment Explorer"],
  ["raw-data", "Raw Data"]
];

export const navGroups = [
  ["Summary", [
    ["overview", "Overview"],
    ["customer-mood", "Customer Mood"]
  ]],
  ["Customer Problems", [
    ["top-concerns", "Top Concerns"],
    ["emerging-radar", "Emerging Risks"],
    ["urgent-escalation", "Urgent Comments"]
  ]],
  ["Market & Channels", [
    ["sentiment-trust", "Sentiment & Trust"],
    ["brand-competitors", "Brand vs Competitors"],
    ["platform-performance", "Platform Signals"],
    ["keyword-intelligence", "Keywords"]
  ]],
  ["Actions", [
    ["marketing-opportunities", "Opportunities"],
    ["content-ideas", "Content & FAQ Ideas"]
  ]],
  ["Evidence", [
    ["comment-explorer", "Comment Explorer"],
    ["raw-data", "Raw Data"]
  ]]
];

const sectionHelp = {
  overview: {
    en: "This is the quick read on total feedback volume, risk pressure, urgent items, and the leading concern. Use it first to understand whether the dataset has enough signal for decision-making.",
    ar: "هذا ملخص سريع لحجم التعليقات، ضغط المخاطر، التعليقات العاجلة، وأكبر مخاوف العملاء. ابدأ منه لمعرفة هل البيانات كافية لاتخاذ قرار."
  },
  "customer-mood": {
    en: "This section turns sentiment and movement into plain-language answers for marketing, product, support, and operations teams.",
    ar: "هذا القسم يحول الانطباع العام وحركة التعليقات إلى إجابات واضحة لفرق التسويق والمنتج والدعم والعمليات."
  },
  "top-concerns": {
    en: "This ranks repeated customer problems by configured concern categories, with examples and suggested owners.",
    ar: "يرتب هذا القسم المشاكل المتكررة حسب تصنيفات المخاوف المعتمدة، مع أمثلة ومالكين مقترحين."
  },
  "sentiment-trust": {
    en: "This shows how positive, neutral, and negative feedback is distributed and where trust-related risks appear.",
    ar: "يعرض هذا القسم توزيع التعليقات الإيجابية والمحايدة والسلبية، وأين تظهر مخاطر الثقة."
  },
  "brand-competitors": {
    en: "This compares Telgani and competitor mentions when competitor data exists. If only Telgani appears, use it as brand-only context.",
    ar: "يقارن هذا القسم تلقاني والمنافسين عند توفر بيانات منافسين. إذا ظهرت تلقاني فقط، فاعتبره سياقًا خاصًا بالعلامة."
  },
  "platform-performance": {
    en: "This explains which platforms carry the most feedback, risk, praise, and content opportunities.",
    ar: "يوضح هذا القسم المنصات التي تحمل أكبر حجم من التعليقات، المخاطر، الإشادة، وفرص المحتوى."
  },
  "keyword-intelligence": {
    en: "This surfaces repeated Arabic and English terms. Keywords are directional and should be checked against the original comments.",
    ar: "يعرض هذا القسم الكلمات العربية والإنجليزية المتكررة. الكلمات مؤشرات أولية ويجب مراجعتها مع التعليقات الأصلية."
  },
  "emerging-radar": {
    en: "This should show new or rising concerns from the analysis output. If the file is empty, treat this section as not yet validated.",
    ar: "يفترض أن يعرض هذا القسم المخاوف الجديدة أو المتصاعدة من مخرجات التحليل. إذا كان الملف فارغًا، فالقسم غير مثبت بعد."
  },
  "urgent-escalation": {
    en: "This isolates comments that need fast review, escalation, or direct response paths.",
    ar: "يعزل هذا القسم التعليقات التي تحتاج مراجعة سريعة أو تصعيد أو مسار رد مباشر."
  },
  "marketing-opportunities": {
    en: "This turns positive themes, repeated demand signals, and competitor weaknesses into campaign or positioning ideas.",
    ar: "يحول هذا القسم الثيمات الإيجابية وإشارات الطلب ونقاط ضعف المنافسين إلى أفكار حملات أو تموضع."
  },
  "content-ideas": {
    en: "This converts repeated questions and objections into FAQ, explainer, social, and response-template ideas.",
    ar: "يحول هذا القسم الأسئلة والاعتراضات المتكررة إلى أفكار للأسئلة الشائعة والشرح والمحتوى وقوالب الرد."
  },
  "comment-explorer": {
    en: "This is the place to inspect the filtered comment-level evidence before using any insight externally.",
    ar: "هذا هو مكان مراجعة أدلة التعليقات بعد تطبيق الفلاتر وقبل استخدام أي استنتاج خارجيًا."
  },
  "raw-data": {
    en: "This exposes the processed and analysis CSV files so analysts can verify the source fields behind each section.",
    ar: "يعرض هذا القسم ملفات CSV المعالجة والتحليلية حتى يتمكن المحللون من التحقق من الحقول الأصلية وراء كل قسم."
  }
};

export function renderDashboardViews(data, filtered, summary, filters) {
  const urgent = filtered.filter((row) => row.urgency_flag === "true");
  const negative = filtered.filter((row) => row.sentiment_label === "negative");
  const positive = filtered.filter((row) => row.sentiment_label === "positive");
  const topConcern = summary.categoryRows[0];
  const executive = executiveAnswers(summary, filtered, data);
  const emergingRows = data.analysis.emergingConcerns.length ? data.analysis.emergingConcerns : emergingFallback(summary.categoryRows);
  const opportunityRows = data.analysis.opportunities.length ? data.analysis.opportunities : opportunityFallback(summary.opportunitySignals);
  const contentRows = data.analysis.contentIdeas.length ? data.analysis.contentIdeas : contentFallback(summary.repeatedQuestions, summary.categoryRows);

  return `
    ${introPanel(data)}

    <div class="section-cluster" id="summary-group"><span>Summary</span></div>
    ${section(data, "overview", "Executive Overview", "Start with the size of the feedback set, risk pressure, urgent items, and the top customer concern.", `
      <div class="grid kpi">
        ${kpiCard("Total comments", summary.total, data.usingSample ? "Sample mode" : "Local files")}
        ${kpiCard("Negative signals", negative.length, "Risk and trust pressure")}
        ${kpiCard("Urgent items", urgent.length, "Escalation candidates")}
        ${kpiCard("Top concern", topConcern?.count || 0, topConcern?.label || "No category")}
      </div>
    `)}

    ${section(data, "customer-mood", "Customer Mood", "Read the current customer mood, complaint movement, and the clearest signals behind the numbers.", `
      <div class="grid two" style="margin-top:16px">
        <div class="panel">${answerList(executive)}</div>
        <div class="panel"><h3>Market Mood</h3>${sentimentSplit(summary.sentiment)}</div>
      </div>
      <div class="grid two" style="margin-top:16px">
        <div class="panel"><h3>Complaint Movement</h3>${timeline(summary.volume)}<p class="meta">Direction: ${summary.trend.label}; recent ${number(summary.trend.recent)}, previous ${number(summary.trend.previous)}.</p></div>
        <div class="panel"><h3>Biggest Traceable Signals</h3>${signalList(summary.riskSignals.slice(0, 4))}</div>
      </div>
    `)}

    <div class="section-cluster" id="problems-group"><span>Customer Problems</span></div>
    ${section(data, "top-concerns", "Top Concerns", "See the largest customer concern categories with counts, sentiment split, examples, actions, and owners.", `
      <div class="grid">${categoryRanking(summary.categoryRows, filters.category)}</div>
    `)}

    ${section(data, "emerging-radar", "Emerging Risks", "Track new or rising customer issues with why-it-matters context and suggested actions.", `
      ${data.analysis.emergingConcerns.length ? dataTable("emerging-table", data.analysis.emergingConcerns, [
        { key: "concern_category_label", label: "Concern" },
        { key: "platform", label: "Platform" },
        { key: "comments_count", label: "Growth score / count" },
        { key: "reason", label: "Why it matters", length: 90 },
        { key: "recommended_action", label: "Suggested action", length: 90 },
        { key: "example_text", label: "Example", length: 90 }
      ], { limit: 60 }) : validationState("Emerging concerns need validation", "data/analysis/emerging_concerns.csv is empty. Run analysis with enough recent and older data to calculate rising concern signals.")}
    `)}

    ${section(data, "urgent-escalation", "Urgent Comments", "Review high-urgency feedback and route response ownership without blaming teams or individuals.", `
      <div class="grid two">
        <div class="panel"><h3>Top Urgent Topics</h3>${urgent.length ? barChart(toChartItems(countBy(urgent, "concern_category_label")).slice(0, 10), { label: "Urgent topics" }) : validationState("No urgent comments in this filter", "Urgency depends on urgency_flag in data/analysis/comment_analysis.csv or rows in data/analysis/urgent_comments.csv.")}</div>
        <div class="panel"><h3>Escalation Signal Buckets</h3>${escalationBuckets(summary)}</div>
      </div>
      <div style="margin-top:16px">${dataTable("urgent-table", data.analysis.escalationItems.length ? addStatus(data.analysis.escalationItems) : addStatus(urgent), [
        { key: "platform", label: "Platform" },
        { key: "brand_or_competitor", label: "Brand / competitor" },
        { key: "concern_category_label", label: "Signal" },
        { key: "sentiment_label", label: "Sentiment" },
        { key: "recommended_action", label: "Suggested escalation path", length: 90 },
        { key: "status", label: "Status" },
        { key: "text", label: "Comment", length: 90 }
      ], { limit: 80 })}</div>
    `)}

    <div class="section-cluster" id="market-group"><span>Market & Channels</span></div>
    ${section(data, "sentiment-trust", "Sentiment & Trust", "Sentiment, trust-risk signals, and credibility-related comments across platform and brand slices.", `
      <div class="grid two">
        <div class="panel"><h3>Overall Sentiment</h3>${sentimentSplit(summary.sentiment)}</div>
        <div class="panel"><h3>Sentiment Over Time</h3>${sentimentTimeline(summary.sentimentTime)}</div>
      </div>
      <div class="grid two" style="margin-top:16px">
        <div class="panel"><h3>Sentiment by Platform</h3>${sentimentMatrix(summary.platformSentiment)}</div>
        <div class="panel"><h3>Sentiment by Brand / Competitor</h3>${sentimentMatrix(summary.brandSentiment)}</div>
      </div>
      <div class="grid two" style="margin-top:16px">
        ${dataTable("trust-risk-table", summary.trustRiskComments, commentColumns, { limit: 40 })}
        ${dataTable("credibility-table", summary.credibilityComments, commentColumns, { limit: 40 })}
      </div>
    `)}

    ${section(data, "brand-competitors", "Brand vs Competitors", "Compare sentiment, complaint themes, positive themes, repeated questions, and messaging opportunities.", `
      ${unique(filtered.map((row) => row.brand_or_competitor || row.brand)).length < 2 ? validationState("Competitor comparison is limited", "brand_competitor_summary.csv currently contains one brand group. Add competitor records in market_comments.csv for true comparison.") : ""}
      <div class="grid two">
        <div class="panel"><h3>Sentiment Comparison</h3>${sentimentMatrix(summary.brandSentiment)}</div>
        <div class="panel"><h3>Complaint Category Comparison</h3>${groupedList(summary.brand, filtered, "concern_category_label")}</div>
      </div>
      <div class="grid two" style="margin-top:16px">
        <div class="panel"><h3>Positive Theme Comparison</h3>${groupedKeywordList(summary.keywordByBrand)}</div>
        <div class="panel"><h3>Repeated Questions Comparison</h3>${traceList(summary.repeatedQuestions.slice(0, 8), "Repeated question signal")}</div>
      </div>
      <div class="grid two" style="margin-top:16px">
        <div class="panel"><h3>Competitor Praised Features</h3>${traceList(positive.filter((row) => /competitor/i.test(row.brand_or_competitor || "")).slice(0, 8), "Positive competitor signal")}</div>
        <div class="panel"><h3>Competitor Complaint Weaknesses</h3>${traceList(negative.filter((row) => /competitor/i.test(row.brand_or_competitor || "")).slice(0, 8), "Competitor risk signal")}</div>
      </div>
      <div class="panel" style="margin-top:16px"><h3>Messaging Opportunities</h3>${dataTable("brand-message-table", opportunityRows, [
        { key: "keyword", label: "Theme" },
        { key: "brand_or_competitor", label: "Brand / competitor" },
        { key: "comments_count", label: "Comments" },
        { key: "recommended_action", label: "Messaging action", length: 90 },
        { key: "example_text", label: "Example", length: 90 }
      ], { limit: 40 })}</div>
    `)}

    ${section(data, "platform-performance", "Platform Signals", "Understand where feedback is coming from, how each platform feels, and what content opportunities appear.", `
      <div class="grid two">
        <div class="panel"><h3>Volume by Platform</h3>${barChart(toChartItems(summary.platform), { label: "Platform split" })}</div>
        <div class="panel"><h3>Sentiment by Platform</h3>${sentimentMatrix(summary.platformSentiment)}</div>
      </div>
      <div class="grid two" style="margin-top:16px">
        <div class="panel"><h3>Concerns by Platform</h3>${nestedList(summary.categoryByPlatform)}</div>
        <div class="panel"><h3>Top Keywords by Platform</h3>${groupedKeywordList(summary.keywordByPlatform)}</div>
      </div>
      <div class="grid two" style="margin-top:16px">
        <div class="panel"><h3>Best Performing Sources</h3>${sourcePerformance(filtered, "positive")}</div>
        <div class="panel"><h3>Risk-Heavy Sources</h3>${sourcePerformance(filtered, "negative")}</div>
      </div>
      <div class="panel" style="margin-top:16px"><h3>Platform-Specific Content Opportunities</h3>${dataTable("platform-content-table", contentRows, [
        { key: "platform", label: "Platform" },
        { key: "concern_category_label", label: "Signal" },
        { key: "recommended_action", label: "Content opportunity", length: 90 },
        { key: "example_text", label: "Trace example", length: 90 }
      ], { limit: 40 })}</div>
    `)}

    ${section(data, "keyword-intelligence", "Keyword Intelligence", "Explore Arabic and English keyword patterns by sentiment, platform, and brand. Click a keyword to filter comments.", `
      <div class="grid two">
        <div class="panel"><h3>Most Frequent Keywords</h3>${keywordCloud(summary.keywords)}</div>
        <div class="panel"><h3>Keyword Trend Over Time</h3>${barChart(toChartItems(summary.keywords).slice(0, 15), { label: "Keyword trend proxy" })}</div>
      </div>
      <div class="grid three" style="margin-top:16px">
        <div class="panel"><h3>By Sentiment</h3>${groupedKeywordList(summary.keywordBySentiment)}</div>
        <div class="panel"><h3>By Platform</h3>${groupedKeywordList(summary.keywordByPlatform)}</div>
        <div class="panel"><h3>By Brand / Competitor</h3>${groupedKeywordList(summary.keywordByBrand)}</div>
      </div>
    `)}

    <div class="section-cluster" id="actions-group"><span>Actions</span></div>
    ${section(data, "marketing-opportunities", "Marketing Opportunities", "Find messaging angles, campaign ideas, demand signals, competitor weaknesses, and claims to treat carefully.", `
      <div class="grid two">
        <div class="panel"><h3>Opportunity Themes</h3>${signalList(summary.opportunitySignals.slice(0, 8))}</div>
        <div class="panel"><h3>Claims to Treat Carefully</h3>${signalList(summary.riskSignals.slice(0, 8))}</div>
      </div>
      <div style="margin-top:16px">${dataTable("opportunity-table", opportunityRows, [
        { key: "type", label: "Type" },
        { key: "keyword", label: "Demand / theme" },
        { key: "comments_count", label: "Comments" },
        { key: "recommended_action", label: "Marketing action", length: 90 },
        { key: "example_text", label: "Trace example", length: 90 }
      ], { limit: 60 })}</div>
    `)}

    ${section(data, "content-ideas", "Content & FAQ Ideas", "Turn repeated questions, objections, and response patterns into FAQ entries and social content ideas.", `
      <div class="grid two">
        <div class="panel"><h3>Repeated Questions</h3>${traceList(summary.repeatedQuestions.slice(0, 10), "Question signal")}</div>
        <div class="panel"><h3>Suggested Response Templates</h3>${responseTemplates(summary.categoryRows.slice(0, 5))}</div>
      </div>
      <div style="margin-top:16px">${dataTable("content-table", contentRows, [
        { key: "concern_category_label", label: "Objection / theme" },
        { key: "comments_count", label: "Comments" },
        { key: "reason", label: "Why this content helps", length: 90 },
        { key: "recommended_action", label: "FAQ or social post angle", length: 90 },
        { key: "example_text", label: "Trace example", length: 90 }
      ], { limit: 60 })}</div>
    `)}

    <div class="section-cluster" id="evidence-group"><span>Evidence</span></div>
    ${section(data, "comment-explorer", "Comment Explorer", "All comments and reviews with expandable details, source links, keywords, action, and raw references.", `
      ${dataTable("comment-table", filtered, commentColumns, { limit: 300 })}
    `)}

    ${section(data, "raw-data", "Raw Data", "Browse processed and analysis CSVs like sheets, with search, sorting, pagination, downloads, and field notes.", `
      ${rawDataExplorer(data, filters)}
    `)}
  `;
}

function introPanel(data) {
  const sample = isDemoData(data);
  return `
    <section class="dashboard-intro" id="top">
      <div>
        <span class="intro-eyebrow">Dashboard guide</span>
        <h2>What this dashboard is</h2>
        <p>This dashboard turns customer comments into marketing, product, support, and operations signals. Use it to explore sentiment, repeated concerns, competitor mentions, urgent comments, and content opportunities.</p>
        <p class="arabic">تحول هذه اللوحة تعليقات العملاء إلى مؤشرات تساعد فرق التسويق والمنتج والدعم والعمليات على فهم الانطباع العام، المخاوف المتكررة، المنافسين، الفرص، والتعليقات العاجلة.</p>
      </div>
      <div class="intro-grid">
        <div><strong>Data used</strong><span>Processed comments plus prepared analysis CSV files.</span></div>
        <div><strong>For</strong><span>Marketing, Product, Support, Operations, Sales, Management, Finance, and Fleet.</span></div>
        <div><strong>How to use</strong><span>Filter first, scan summaries, then verify claims in Comment Explorer and Raw Data.</span></div>
        <div class="${sample ? "intro-warning" : ""}"><strong>${sample ? "Demo/synthetic warning" : "Data status"}</strong><span>${sample ? "Current records use sample IDs. Validate with real data before decisions." : "Local prepared files loaded."}</span></div>
      </div>
    </section>
  `;
}

function section(data, id, title, subtitle, content) {
  const support = dataSupport(data, id);
  const help = sectionHelp[id] || { en: "Use this section as supporting context.", ar: "استخدم هذا القسم كسياق مساعد." };
  return `
    <section class="section" id="${id}">
      <div class="section-header">
        <div>
          <h2 class="section-title">${title}</h2>
          <p class="section-subtitle">${subtitle}</p>
        </div>
        <span class="confidence-pill ${support.kind}">${support.label}</span>
      </div>
      <details class="section-help">
        <summary>What does this mean?</summary>
        <p>${help.en}</p>
        <p class="arabic">${help.ar}</p>
        <p class="meta">Data note: ${support.note}</p>
      </details>
      ${content}
    </section>
  `;
}

function dataSupport(data, id) {
  const demo = isDemoData(data);
  const strong = (note) => ({ label: demo ? "Demo/synthetic only" : "Strong data support", kind: demo ? "demo" : "strong", note: demo ? `${note} Current rows appear to be sample/demo records.` : note });
  const partial = (note) => ({ label: demo ? "Demo/synthetic only" : "Partial data support", kind: demo ? "demo" : "partial", note: demo ? `${note} Current rows appear to be sample/demo records.` : note });
  const needs = (note) => ({ label: "Needs validation", kind: "needs", note });
  const has = (key) => Array.isArray(data.analysis?.[key]) && data.analysis[key].length > 0;
  const comments = data.comments?.length || 0;
  const map = {
    overview: comments && has("commentAnalysis") ? strong("Supported by market_comments.csv and comment_analysis.csv.") : partial("Needs comment rows and analysis fields."),
    "customer-mood": has("sentimentSummary") ? strong("Supported by sentiment_summary.csv and comment_analysis.csv.") : partial("Needs sentiment_summary.csv."),
    "top-concerns": has("concernSummary") ? strong("Supported by concern_category_summary.csv.") : partial("Needs concern_category_summary.csv."),
    "sentiment-trust": has("sentimentSummary") ? strong("Supported by sentiment_summary.csv and configured trust categories where available.") : partial("Trust category coverage depends on config/concern_categories.yaml."),
    "brand-competitors": has("brandSummary") && unique((data.comments || []).map((row) => row.brand_or_competitor || row.brand)).length > 1 ? strong("Supported by brand_competitor_summary.csv with multiple brand groups.") : partial("brand_competitor_summary.csv is present, but competitor coverage is limited."),
    "platform-performance": has("platformSummary") ? strong("Supported by platform_summary.csv and platform fields in comments.") : partial("Needs platform_summary.csv."),
    "keyword-intelligence": has("keywordSummary") ? strong("Supported by keyword_summary.csv and per-comment keywords.") : partial("Needs keyword_summary.csv."),
    "emerging-radar": has("emergingConcerns") ? partial("Supported by emerging_concerns.csv; verify growth thresholds before action.") : needs("data/analysis/emerging_concerns.csv is empty or unavailable."),
    "urgent-escalation": has("urgentComments") || has("escalationItems") ? strong("Supported by urgent_comments.csv, escalation_items.csv, and urgency flags.") : partial("Needs urgent_comments.csv or urgency_flag values."),
    "marketing-opportunities": has("opportunities") ? partial("Supported by marketing_opportunities.csv; validate themes before campaign claims.") : needs("Needs marketing_opportunities.csv."),
    "content-ideas": has("contentIdeas") ? partial("Supported by content_ideas.csv; validate content angles before publishing.") : needs("Needs content_ideas.csv."),
    "comment-explorer": comments ? strong("Supported by market_comments.csv merged with comment_analysis.csv.") : needs("Needs data/processed/market_comments.csv."),
    "raw-data": data.rawTables ? strong("Supported by the raw table catalog and available CSV files.") : partial("Some CSVs may be missing; check table status.")
  };
  return map[id] || partial("Support depends on prepared CSV availability.");
}

function isDemoData(data) {
  return Boolean(data.usingSample || (data.comments || []).some((row) => String(row.record_id || "").startsWith("sample-")));
}

function validationState(title, text) {
  return `<div class="validation-state"><strong>${title}</strong><p>${text}</p></div>`;
}

function executiveAnswers(summary, rows, data) {
  const mood = moodLabel(summary.sentiment);
  const comparison = comparisonSignal(summary.brandSentiment);
  const topRisk = summary.riskSignals[0];
  const topOpportunity = summary.opportunitySignals[0];
  return [
    ["Market mood right now", mood, "Based on filtered sentiment counts."],
    ["Complaint movement", `${summary.trend.label}`, `Recent ${number(summary.trend.recent)} vs previous ${number(summary.trend.previous)} comments.`],
    ["Biggest risk", topRisk?.label || "No risk signal", topRisk?.example?.text || "Run analysis to populate trace examples."],
    ["Biggest opportunity", topOpportunity?.label || "No opportunity signal", topOpportunity?.example?.text || "Positive themes will appear here after analysis."],
    ["Brand vs competitors", comparison, "Computed from filtered brand/competitor sentiment splits."],
    ["What marketing should do next", nextAction(summary, rows, data), topRisk?.action || "Use the prepared analysis outputs to prioritize response themes."]
  ];
}

function answerList(items) {
  return `<div class="insight-list">${items.map(([question, answer, trace]) => `
    <article class="insight-item">
      <span class="meta">${question}</span>
      <strong>${answer}</strong>
      <p>${shortText(trace || "", 150)}</p>
    </article>
  `).join("")}</div>`;
}

function signalList(items) {
  if (!items.length) return `<div class="empty-state">No traceable signals in the current filter.</div>`;
  return `<div class="insight-list">${items.map((item) => `
    <article class="insight-item">
      <strong>${item.label}</strong>
      <p>${shortText(item.action || item.example?.recommended_action || "", 140)}</p>
      <p class="meta">Trace: ${shortText(item.example?.text || item.example_text || "", 160)}</p>
    </article>
  `).join("")}</div>`;
}

function traceList(rows, label) {
  if (!rows.length) return `<div class="empty-state">No traceable comments in the current filter.</div>`;
  return `<div class="insight-list">${rows.map((row) => `
    <article class="insight-item">
      <strong>${label}</strong>
      <p>${shortText(row.text || row.example_text || "", 150)}</p>
      <p class="meta">${row.platform || ""} ${row.brand_or_competitor || ""} ${row.concern_category_label || ""}</p>
    </article>
  `).join("")}</div>`;
}

function sentimentMatrix(groups) {
  const rows = Object.entries(groups || {}).sort(([a], [b]) => a.localeCompare(b));
  if (!rows.length) return `<div class="empty-state">No sentiment data available.</div>`;
  return `<div class="matrix">${rows.map(([label, split]) => {
    const total = split.total || split.positive + split.neutral + split.negative || 1;
    return `
      <div class="matrix-row">
        <strong>${label}</strong>
        <div class="sentiment-stack">
          <div class="sentiment-positive" style="width:${((split.positive || 0) / total) * 100}%"></div>
          <div class="sentiment-neutral" style="width:${((split.neutral || 0) / total) * 100}%"></div>
          <div class="sentiment-negative" style="width:${((split.negative || 0) / total) * 100}%"></div>
        </div>
        <span class="meta">${number(total)} comments</span>
      </div>
    `;
  }).join("")}</div>`;
}

function groupedList(groups, rows, field) {
  const groupNames = Object.keys(groups || {});
  if (!groupNames.length) return `<div class="empty-state">No comparison data available.</div>`;
  return groupNames.map((group) => {
    const counts = rows.filter((row) => (row.brand_or_competitor || "unknown") === group).reduce((acc, row) => {
      const value = row[field] || "unknown";
      acc[value] = (acc[value] || 0) + 1;
      return acc;
    }, {});
    return `<div class="comparison-block"><h4>${group}</h4>${barChart(toChartItems(counts).slice(0, 5), { label: `${group} themes` })}</div>`;
  }).join("");
}

function nestedList(grouped) {
  const rows = Object.entries(grouped || {});
  if (!rows.length) return `<div class="empty-state">No grouped data available.</div>`;
  return rows.map(([group, counts]) => `<div class="comparison-block"><h4>${group}</h4>${barChart(toChartItems(counts).slice(0, 5), { label: group })}</div>`).join("");
}

function groupedKeywordList(grouped) {
  const rows = Object.entries(grouped || {});
  if (!rows.length) return `<div class="empty-state">No keyword groups available.</div>`;
  return rows.map(([group, counts]) => `
    <div class="comparison-block">
      <h4>${group}</h4>
      <div class="tag-cloud">${toChartItems(counts).slice(0, 8).map((item) => `<button class="tag tag-button" data-keyword-filter="${item.label}">${item.label} <strong>${item.value}</strong></button>`).join("")}</div>
    </div>
  `).join("");
}

function sourcePerformance(rows, sentiment) {
  const counts = rows.filter((row) => row.sentiment_label === sentiment).reduce((acc, row) => {
    const source = row.source_account || row.source_url || "unknown";
    acc[source] = (acc[source] || 0) + 1;
    return acc;
  }, {});
  return barChart(toChartItems(counts).slice(0, 8), { label: `${sentiment} source performance` });
}

function escalationBuckets(summary) {
  const buckets = [
    ["Refund / insurance signals", summary.refundComments.length],
    ["Safety or condition signals", summary.safetyConditionComments.length],
    ["Credibility signals", summary.credibilityComments.length],
    ["Customer response signals", summary.serviceComments.length]
  ];
  return barChart(buckets.map(([label, value]) => ({ label, value })), { label: "Escalation signal buckets" });
}

function responseTemplates(categories) {
  if (!categories.length) return `<div class="empty-state">No concern categories available.</div>`;
  return `<div class="insight-list">${categories.map((category) => `
    <article class="insight-item">
      <strong>${category.label}</strong>
      <p>${category.recommended_action || "Prepare a concise response that acknowledges the signal and explains the next step."}</p>
      <p class="meta">Owner: ${category.escalation_team || "Review owner"}</p>
    </article>
  `).join("")}</div>`;
}

function emergingFallback(categories) {
  return categories.filter((category) => category.count > 0).slice(5).map((category) => ({
    concern_category_label: category.label,
    platform: "filtered view",
    comments_count: category.count,
    reason: `This signal appears ${number(category.count)} times in the current filter.`,
    recommended_action: category.recommended_action || "Monitor this emerging signal and connect it to campaign planning.",
    example_text: category.examples[0]?.text || ""
  }));
}

function opportunityFallback(items) {
  return items.map((item) => ({
    type: "opportunity",
    keyword: item.label,
    comments_count: 1,
    recommended_action: item.action,
    example_text: item.example?.text || ""
  }));
}

function contentFallback(questions, categories) {
  const questionRows = questions.map((row) => ({
    concern_category_label: row.concern_category_label || "Repeated question",
    comments_count: 1,
    reason: "Question appears in filtered comments.",
    recommended_action: row.recommended_action || "Turn this into an FAQ entry or response template.",
    example_text: row.text,
    platform: row.platform
  }));
  if (questionRows.length) return questionRows;
  return categories.filter((category) => category.count > 0).slice(0, 8).map((category) => ({
    concern_category_label: category.label,
    comments_count: category.count,
    reason: "Repeated concern can become support content.",
    recommended_action: category.recommended_action || "Create a helpful explanation or response template.",
    example_text: category.examples[0]?.text || ""
  }));
}

function addStatus(rows) {
  return rows.map((row) => ({ ...row, status: row.status || "Needs review" }));
}

function moodLabel(sentiment) {
  const positive = Number(sentiment.positive || 0);
  const neutral = Number(sentiment.neutral || 0);
  const negative = Number(sentiment.negative || 0);
  if (positive > negative && positive >= neutral) return "mostly positive";
  if (negative > positive && negative >= neutral) return "risk-heavy";
  if (neutral >= positive && neutral >= negative) return "mostly neutral";
  return "mixed";
}

function comparisonSignal(groups) {
  const rows = Object.entries(groups || {});
  if (rows.length < 2) return "not enough comparison data";
  const ranked = rows.map(([label, split]) => {
    const total = split.total || 1;
    return { label, score: ((split.positive || 0) - (split.negative || 0)) / total };
  }).sort((a, b) => b.score - a.score);
  return `${ranked[0].label} leads sentiment vs ${ranked.at(-1).label}`;
}

function nextAction(summary, rows, data) {
  if (!rows.length) return data.usingSample ? "Load real analysis files to replace sample signals." : "Run scraping, normalization, and analysis to populate signals.";
  if (summary.riskSignals[0]?.action) return summary.riskSignals[0].action;
  if (summary.opportunitySignals[0]?.action) return summary.opportunitySignals[0].action;
  return "Review top concern examples and align messaging with the strongest traceable themes.";
}

function toChartItems(counts) {
  return Object.entries(counts || {})
    .map(([label, value]) => ({ label, value: Number(value || 0) }))
    .sort((a, b) => b.value - a.value || a.label.localeCompare(b.label));
}

function countBy(rows, key) {
  return rows.reduce((acc, row) => {
    const value = row[key] || "unknown";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort();
}

function rawDataExplorer(data, filters) {
  const selectedDefinition = rawTableById(filters.rawTable || "market_comments");
  const table = data.rawTables?.[selectedDefinition.id] || { ...selectedDefinition, rows: [], status: "error", error: "Table was not loaded." };
  const rows = table.rows || [];
  const columns = rawColumnsFor(table, rows);
  const query = (filters.rawSearch || "").toLowerCase();
  const sortKey = filters.rawSort || columns[0] || "";
  const pageSize = 25;
  const filteredRows = rows.filter((row) => !query || Object.values(row).join(" ").toLowerCase().includes(query));
  const sortedRows = [...filteredRows].sort((a, b) => String(a[sortKey] || "").localeCompare(String(b[sortKey] || ""), undefined, { numeric: true }));
  const totalPages = Math.max(1, Math.ceil(sortedRows.length / pageSize));
  const page = Math.min(Math.max(Number(filters.rawPage || 1), 1), totalPages);
  const pageRows = sortedRows.slice((page - 1) * pageSize, page * pageSize);

  return `
    <div class="raw-explorer">
      <aside class="raw-sidebar panel">
        <label class="filter-field">
          <span>Table</span>
          <select name="rawTable">
            ${RAW_TABLES.map((definition) => `<option value="${definition.id}" ${definition.id === selectedDefinition.id ? "selected" : ""}>${definition.label}</option>`).join("")}
          </select>
        </label>
        <div class="raw-table-list">
          ${RAW_TABLES.map((definition) => {
            const item = data.rawTables?.[definition.id];
            return `<button type="button" class="raw-table-button ${definition.id === selectedDefinition.id ? "active" : ""}" data-raw-table="${definition.id}">${definition.label}<span>${number(item?.rows?.length || 0)} rows</span></button>`;
          }).join("")}
        </div>
      </aside>
      <div class="raw-workspace">
        <div class="panel">
          <div class="raw-header">
            <div>
              <h3>${table.label}</h3>
              <p class="section-subtitle">${table.description}</p>
              <p class="meta">Status: ${table.status}${table.error ? `; ${table.error}` : ""}</p>
            </div>
            <a class="download-link" href="${table.downloadPath}" download>Download CSV</a>
          </div>
          <div class="raw-controls">
            <label class="filter-field">
              <span>Search this table</span>
              <input name="rawSearch" type="search" value="${escapeAttr(filters.rawSearch || "")}" placeholder="Search any field, Arabic or English" />
            </label>
            <label class="filter-field">
              <span>Sort column</span>
              <select name="rawSort">
                ${columns.map((column) => `<option value="${escapeAttr(column)}" ${column === sortKey ? "selected" : ""}>${column}</option>`).join("")}
              </select>
            </label>
          </div>
          ${rawTableState(table, rows, filteredRows)}
          ${rawSheetTable(selectedDefinition.id, pageRows, columns)}
          ${rawPagination(page, totalPages, filteredRows.length)}
        </div>
        <div class="panel">
          <h3>Data Dictionary</h3>
          <p class="section-subtitle">Field notes for the selected sheet. These describe the CSV contract and do not add analysis logic.</p>
          ${dataDictionary(table, columns)}
        </div>
      </div>
    </div>
  `;
}

function rawColumnsFor(table, rows) {
  if (rows.length) return Object.keys(rows[0]);
  const dictionaryColumns = (table.dictionary || []).map(([field]) => field);
  return dictionaryColumns.length ? dictionaryColumns : ["status"];
}

function rawTableState(table, rows, filteredRows) {
  if (table.status === "error") return `<div class="error-state">Could not load this CSV. ${table.error || ""}</div>`;
  if (!rows.length) return `<div class="empty-state">This CSV is available but currently has no rows.</div>`;
  if (!filteredRows.length) return `<div class="empty-state">No rows match the current table search.</div>`;
  return `<p class="meta">${number(filteredRows.length)} matching rows from ${number(rows.length)} total.</p>`;
}

function rawSheetTable(id, rows, columns) {
  if (!rows.length) return "";
  return `
    <div class="table-wrap raw-table-wrap">
      <table>
        <thead>
          <tr>
            <th></th>
            ${columns.map((column) => `<th>${column}</th>`).join("")}
          </tr>
        </thead>
        <tbody>
          ${rows.map((row, index) => rawRow(id, row, columns, index)).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function rawRow(id, row, columns, index) {
  const detailId = `raw-${id}-${index}`;
  return `
    <tr>
      <td><button class="expand-button" data-expand="${detailId}">+</button></td>
      ${columns.map((column) => `<td class="${isArabic(row[column] || "") ? "arabic" : ""}">${shortText(row[column] || "", 90)}</td>`).join("")}
    </tr>
    <tr id="${detailId}" hidden>
      <td colspan="${columns.length + 1}">
        <div class="comment-detail ${isArabic(Object.values(row).join(" ")) ? "arabic" : ""}">
          ${rawDetail(row, columns)}
        </div>
      </td>
    </tr>
  `;
}

function rawDetail(row, columns) {
  const preferred = ["text", "example_text", "input_json", "raw_record_json", "raw_file_path", "source_url", "record_id", "run_id"];
  const ordered = [...preferred.filter((key) => columns.includes(key)), ...columns.filter((key) => !preferred.includes(key))];
  return `<dl class="detail-list">${ordered.map((column) => `<dt>${column}</dt><dd>${linkValue(column, row[column] || "")}</dd>`).join("")}</dl>`;
}

function linkValue(column, value) {
  const escaped = escapeHtml(value);
  if (!value) return "";
  if (column.includes("url") && /^https?:\/\//i.test(value)) {
    return `<a href="${escapeAttr(value)}" target="_blank" rel="noreferrer">${escaped}</a>`;
  }
  return escaped;
}

function rawPagination(page, totalPages, count) {
  return `
    <div class="pagination">
      <button type="button" data-raw-page="${Math.max(1, page - 1)}" ${page <= 1 ? "disabled" : ""}>Previous</button>
      <span>Page ${number(page)} of ${number(totalPages)}; ${number(count)} rows</span>
      <button type="button" data-raw-page="${Math.min(totalPages, page + 1)}" ${page >= totalPages ? "disabled" : ""}>Next</button>
    </div>
  `;
}

function dataDictionary(table, columns) {
  const notes = new Map(table.dictionary || []);
  const rows = columns.map((column) => [column, notes.get(column) || "Field from the selected CSV output."]);
  return `
    <div class="table-wrap">
      <table>
        <thead><tr><th>Field</th><th>Meaning</th></tr></thead>
        <tbody>${rows.map(([field, meaning]) => `<tr><td>${field}</td><td>${meaning}</td></tr>`).join("")}</tbody>
      </table>
    </div>
  `;
}

function escapeAttr(value) {
  return String(value).replace(/"/g, "&quot;");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
