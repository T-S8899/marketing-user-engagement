const TEAMS = ["Marketing", "Product", "Support", "Sales", "Operations", "Finance", "Fleet", "Management"];

export function renderInternalInsightsPage({ data } = {}) {
  const view = prepareBriefing(data || {});
  return `
    <main class="internal-page">
      <header class="briefing-hero">
        <div>
          <span class="internal-kicker">Internal business briefing</span>
          <h1>Customer Feedback Briefing</h1>
          <p>Achievements, concerns, opportunities, and next actions from customer feedback.</p>
          <div class="briefing-meta">
            <span>${escapeHtml(view.dateRange)}</span>
            <span>${escapeHtml(view.dataLabel)}</span>
            <span>Built from prepared comment analysis outputs. Use the dashboard for deeper exploration.</span>
          </div>
        </div>
        <a class="internal-dashboard-link" href="./">Open full dashboard for details</a>
      </header>

      ${dataWarning(view)}
      ${briefingStats(view)}

      <section class="briefing-grid">
        ${achievementHighlights(view)}
        ${areasOfConcern(view)}
      </section>

      ${teamActionBoard(view)}
      ${customerEvidenceStrip(view)}
    </main>
  `;
}

function prepareBriefing(data) {
  const comments = data.commentAnalysis || [];
  const positive = comments.filter((row) => same(row.sentiment_label, "positive"));
  const negative = comments.filter((row) => same(row.sentiment_label, "negative"));
  const urgent = data.urgentComments?.length ? data.urgentComments : comments.filter((row) => row.urgency_flag === "true");
  const dates = comments.map((row) => (row.posted_at || "").slice(0, 10)).filter(Boolean).sort();
  const sample = comments.some((row) => String(row.record_id || "").startsWith("sample-"));
  return {
    raw: data,
    comments,
    positive,
    negative,
    urgent,
    concerns: data.concernSummary || [],
    sentiment: data.sentimentSummary || [],
    platforms: data.platformSummary || [],
    brands: data.brandSummary || [],
    keywords: data.keywordSummary || [],
    opportunities: data.marketingOpportunities || [],
    contentIdeas: data.contentIdeas || [],
    emerging: data.emergingConcerns || [],
    sample,
    dataLabel: sample ? "Based on prepared sample data" : "Latest prepared analysis",
    dateRange: dates.length ? `${dates[0]} to ${dates.at(-1)}` : "Latest prepared analysis"
  };
}

function dataWarning(view) {
  if (!view.sample) return "";
  return `
    <aside class="briefing-warning">
      <strong>Demo data / synthetic sample</strong>
      <span>Needs real data validation before decision-making.</span>
    </aside>
  `;
}

function briefingStats(view) {
  const sentiment = sentimentSplit(view.sentiment);
  const topConcern = topRows(view.concerns, 1)[0];
  return `
    <section class="briefing-stats" aria-label="Briefing summary metrics">
      ${metric("Comments analyzed", view.comments.length || "0", "Prepared comment_analysis.csv")}
      ${metric("Positive sentiment", percent(sentiment.positive), "What is working well")}
      ${metric("Urgent items", view.urgent.length || "0", "Needs team review")}
      ${metric("Top concern", topConcern?.label || "No concern", `${topConcern?.comments_count || 0} comments`)}
    </section>
  `;
}

function achievementHighlights(view) {
  const positiveTheme = topRows(view.opportunities, 2);
  const bestPlatform = [...view.platforms].sort((a, b) => toNumber(b.positive_count) - toNumber(a.positive_count))[0];
  const praise = view.positive.find((row) => row.text) || positiveTheme[0];
  const cards = [
    {
      label: "Customer praise",
      title: praise?.text ? shortText(praise.text, 82) : "Positive feedback is available",
      why: "Use repeated praise to sharpen campaign proof points and reply templates.",
      team: "Marketing",
      evidence: praise?.record_id || praise?.example_record_id || "sentiment_summary.csv"
    },
    {
      label: "Strong platform signal",
      title: bestPlatform ? `${bestPlatform.label}: ${bestPlatform.positive_count || 0} positive signals` : "No platform winner yet",
      why: "Prioritize channels where customers already show positive intent.",
      team: "Sales",
      evidence: bestPlatform?.example_record_id || "platform_summary.csv"
    },
    {
      label: "Reusable opportunity",
      title: positiveTheme[0]?.keyword ? `Repeat theme: ${positiveTheme[0].keyword}` : "Campaign proof points need validation",
      why: positiveTheme[0]?.reason || "Prepared opportunity data is weak or unavailable.",
      team: "Marketing",
      evidence: positiveTheme[0]?.example_record_id || "marketing_opportunities.csv"
    }
  ];

  return `
    <section class="briefing-panel">
      <div class="internal-section-heading">
        <span>Achievement Highlights</span>
        <h2>What went well</h2>
        <p>Signals teams can reuse in campaigns, sales conversations, and product messaging.</p>
      </div>
      <div class="briefing-card-list">
        ${cards.map(highlightCard).join("")}
      </div>
    </section>
  `;
}

function highlightCard(card) {
  return `
    <article class="briefing-card success">
      <span class="card-label">${escapeHtml(card.label)}</span>
      <h3>${escapeHtml(card.title)}</h3>
      <p><strong>Why it matters:</strong> ${escapeHtml(card.why)}</p>
      <p><strong>Team:</strong> ${escapeHtml(card.team)}</p>
      <small>Evidence: ${escapeHtml(card.evidence)}</small>
    </article>
  `;
}

function areasOfConcern(view) {
  const concerns = topRows(view.concerns, 3);
  const urgentFallback = view.urgent[0];
  const cards = concerns.length ? concerns.map((concern) => concernCard(concern, view)) : [concernCard(urgentFallback || {}, view)];
  return `
    <section class="briefing-panel">
      <div class="internal-section-heading">
        <span>Areas of Concern</span>
        <h2>What needs attention</h2>
        <p>Risks that need owner review before they become customer trust issues.</p>
      </div>
      <div class="briefing-card-list">
        ${cards.join("")}
      </div>
    </section>
  `;
}

function concernCard(concern, view) {
  const urgentMatch = view.urgent.find((row) => same(row.concern_category_label, concern.label)) || view.urgent[0] || {};
  const urgentCount = toNumber(concern.urgent_count || urgentMatch.urgency_confidence);
  const priority = urgentCount > 0 ? "High" : toNumber(concern.negative_count) > 0 ? "Medium" : "Low";
  const owner = ownerForConcern(concern.label || urgentMatch.concern_category_label);
  return `
    <article class="briefing-card risk">
      <div class="card-row">
        <span class="priority ${priority.toLowerCase()}">${priority}</span>
        <span class="card-label">${escapeHtml(owner)}</span>
      </div>
      <h3>${escapeHtml(concern.label || urgentMatch.concern_category_label || "Concern needs review")}</h3>
      <p><strong>Evidence:</strong> ${escapeHtml(shortText(concern.example_text || urgentMatch.text || "No evidence excerpt available.", 110))}</p>
      <p><strong>Impact:</strong> ${escapeHtml(impactForConcern(concern.label || urgentMatch.concern_category_label))}</p>
      <small>Source: ${escapeHtml(concern.example_record_id || urgentMatch.record_id || "prepared analysis")}</small>
    </article>
  `;
}

function teamActionBoard(view) {
  const actions = actionRows(view);
  return `
    <section class="briefing-panel action-board">
      <div class="internal-section-heading">
        <span>Team Action Board</span>
        <h2>What teams should do next</h2>
        <p>Compact action queue grouped by team. Use the full dashboard to inspect records before execution.</p>
      </div>
      <div class="team-board">
        ${TEAMS.map((team) => teamColumn(team, actions.filter((row) => row.team === team))).join("")}
      </div>
    </section>
  `;
}

function teamColumn(team, rows) {
  const items = rows.length ? rows : [{
    priority: "Low",
    action: "Review the briefing and confirm whether this team has a follow-up.",
    reason: "No direct prepared action was available for this team.",
    evidence: "Needs real data validation before decision-making."
  }];
  return `
    <article class="team-card">
      <h3>${escapeHtml(team)}</h3>
      ${items.slice(0, 2).map((item) => `
        <details ${item.priority === "High" ? "open" : ""}>
          <summary><span class="priority ${item.priority.toLowerCase()}">${escapeHtml(item.priority)}</span>${escapeHtml(item.action)}</summary>
          <p>${escapeHtml(item.reason)}</p>
          <small>Evidence: ${escapeHtml(item.evidence)}</small>
        </details>
      `).join("")}
    </article>
  `;
}

function actionRows(view) {
  const topConcern = topRows(view.concerns, 1)[0];
  const urgent = view.urgent[0];
  const opportunity = view.opportunities[0];
  const content = view.contentIdeas[0];
  const financeConcern = view.concerns.find((row) => /fee|refund|insurance/i.test(row.label || ""));
  const fleetConcern = view.concerns.find((row) => /car condition/i.test(row.label || ""));

  return [
    action("Support", "High", "Respond to urgent customer cases first.", urgent?.urgency_reason || "Urgent comments were found.", urgent?.record_id || "urgent_comments.csv"),
    action("Product", "Medium", "Clarify booking and confirmation moments in the flow.", topConcern?.label || "Top concern requires product review.", topConcern?.example_record_id || "concern_category_summary.csv"),
    action("Marketing", "Medium", opportunity?.recommended_action || "Turn positive themes into proof points.", opportunity?.reason || "Positive opportunity signals are available.", opportunity?.example_record_id || "marketing_opportunities.csv"),
    action("Sales", "Low", "Use positive booking and selection phrases in customer conversations.", "Positive phrases mention easy booking, useful interface, and car selection.", view.positive[0]?.record_id || "comment_analysis.csv"),
    action("Operations", "High", "Review service timing and response handoffs.", topConcern?.label || "Prepared concerns point to operational friction.", topConcern?.example_record_id || "concern_category_summary.csv"),
    action("Finance", financeConcern ? "High" : "Low", "Validate refund, fee, and insurance explanations.", financeConcern?.example_text || "Financial concern support is limited in sample data.", financeConcern?.example_record_id || "Needs real data validation before decision-making."),
    action("Fleet", fleetConcern ? "High" : "Low", "Check vehicle condition signals and inspection messaging.", fleetConcern?.example_text || "Fleet concern support is limited in sample data.", fleetConcern?.example_record_id || "Needs real data validation before decision-making."),
    action("Management", "Medium", "Confirm owners for high-risk categories and monitor progress.", `${view.urgent.length} urgent items and ${view.concerns.length} concern categories in prepared outputs.`, "prepared analysis summary"),
    action("Marketing", "Medium", content?.recommended_action || "Create FAQ content for repeated questions.", content?.reason || "Content idea output is limited.", content?.example_record_id || "content_ideas.csv")
  ];
}

function action(team, priority, actionText, reason, evidence) {
  return { team, priority, action: actionText, reason, evidence };
}

function customerEvidenceStrip(view) {
  const chosen = uniqueByRecord([
    ...view.urgent,
    ...view.positive,
    ...view.negative,
    ...view.comments
  ]).slice(0, 6);
  return `
    <section class="briefing-panel evidence-panel" id="customer-voice">
      <div class="internal-section-heading">
        <span>Customer Evidence Strip</span>
        <h2>Comments behind the briefing</h2>
        <p>Compact evidence only. Open the full dashboard for deeper exploration and source review.</p>
      </div>
      <div class="evidence-strip">
        ${chosen.length ? chosen.map(evidenceCard).join("") : emptyState("No prepared comments available.")}
      </div>
    </section>
  `;
}

function evidenceCard(row) {
  return `
    <article class="evidence-card">
      <div>
        <span class="internal-pill">${escapeHtml(row.platform || "unknown")}</span>
        <span class="internal-pill soft">${escapeHtml(row.sentiment_label || "unknown")}</span>
      </div>
      <p>${escapeHtml(shortText(row.text || row.example_text || "", 130))}</p>
      <small>${escapeHtml(row.concern_category_label || "uncategorized")} · ${escapeHtml(row.record_id || row.example_record_id || "no record")}</small>
    </article>
  `;
}

function ownerForConcern(label = "") {
  if (/service|response/i.test(label)) return "Support";
  if (/condition|car/i.test(label)) return "Fleet";
  if (/refund|fee|insurance/i.test(label)) return "Finance";
  if (/booking|delivery|cancellation/i.test(label)) return "Operations";
  return "Management";
}

function impactForConcern(label = "") {
  if (/service|response/i.test(label)) return "Can reduce trust when customers need quick help.";
  if (/condition|car/i.test(label)) return "Can affect delivery quality, safety perception, and fleet confidence.";
  if (/refund|fee|insurance/i.test(label)) return "Can create billing confusion and escalation risk.";
  if (/booking|delivery|cancellation/i.test(label)) return "Can create uncertainty around confirmation and delivery timing.";
  return "Needs owner review before it informs business decisions.";
}

function metric(label, value, note) {
  return `<article class="briefing-metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><p>${escapeHtml(note)}</p></article>`;
}

function sentimentSplit(rows) {
  const output = { positive: 0, neutral: 0, negative: 0 };
  rows.forEach((row) => {
    const label = (row.label || "").toLowerCase();
    if (label in output) output[label] = toNumber(row.share_of_total);
  });
  return output;
}

function topRows(rows, limit) {
  return [...(rows || [])].sort((a, b) => toNumber(b.comments_count) - toNumber(a.comments_count)).slice(0, limit);
}

function uniqueByRecord(rows) {
  const seen = new Set();
  return rows.filter((row) => {
    const key = row.record_id || row.example_record_id || row.text || row.example_text;
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function percent(value) {
  return `${Math.round(toNumber(value) * 100)}%`;
}

function toNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
}

function same(left, right) {
  return String(left || "").toLowerCase() === String(right || "").toLowerCase();
}

function shortText(value, limit) {
  const text = String(value || "");
  return text.length > limit ? `${text.slice(0, limit - 3)}...` : text;
}

function emptyState(message) {
  return `<div class="internal-empty-state">${escapeHtml(message)}</div>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
