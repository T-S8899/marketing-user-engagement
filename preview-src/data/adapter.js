import { parseCsv, parseSimpleCategoriesYaml } from "../utils/csv.js";
import { RAW_TABLES } from "./rawTables.js";

const FILES = {
  brand: "../../preview-src/config/brand_config.json",
  categories: "../../config/concern_categories.yaml",
  marketComments: "../../data/processed/market_comments.csv",
  commentAnalysis: "../../data/analysis/comment_analysis.csv",
  concernSummary: "../../data/analysis/concern_category_summary.csv",
  sentimentSummary: "../../data/analysis/sentiment_summary.csv",
  platformSummary: "../../data/analysis/platform_summary.csv",
  brandSummary: "../../data/analysis/brand_competitor_summary.csv",
  keywordSummary: "../../data/analysis/keyword_summary.csv",
  emergingConcerns: "../../data/analysis/emerging_concerns.csv",
  urgentComments: "../../data/analysis/urgent_comments.csv",
  opportunities: "../../data/analysis/marketing_opportunities.csv",
  contentIdeas: "../../data/analysis/content_ideas.csv",
  escalationItems: "../../data/analysis/escalation_items.csv",
  llmSummary: "../../data/analysis/llm_insight_summary.json"
};

export async function loadDashboardData() {
  const brand = await fetchJson(FILES.brand, {});
  const categories = await fetchText(FILES.categories).then(parseSimpleCategoriesYaml).catch(() => []);
  const files = await Promise.all([
    fetchCsv(FILES.marketComments),
    fetchCsv(FILES.commentAnalysis),
    fetchCsv(FILES.concernSummary),
    fetchCsv(FILES.sentimentSummary),
    fetchCsv(FILES.platformSummary),
    fetchCsv(FILES.brandSummary),
    fetchCsv(FILES.keywordSummary),
    fetchCsv(FILES.emergingConcerns),
    fetchCsv(FILES.urgentComments),
    fetchCsv(FILES.opportunities),
    fetchCsv(FILES.contentIdeas),
    fetchCsv(FILES.escalationItems),
    fetchJson(FILES.llmSummary, null)
  ]);

  const [
    marketComments,
    commentAnalysis,
    concernSummary,
    sentimentSummary,
    platformSummary,
    brandSummary,
    keywordSummary,
    emergingConcerns,
    urgentComments,
    opportunities,
    contentIdeas,
    escalationItems,
    llmSummary
  ] = files;

  const usingSample = marketComments.length === 0 && commentAnalysis.length === 0;
  const comments = usingSample ? sampleComments(categories) : mergeComments(marketComments, commentAnalysis);
  const rawTables = await loadRawTables();

  return {
    brand,
    categories,
    usingSample,
    comments,
    raw: marketComments,
    rawTables,
    analysis: {
      commentAnalysis,
      concernSummary,
      sentimentSummary,
      platformSummary,
      brandSummary,
      keywordSummary,
      emergingConcerns,
      urgentComments,
      opportunities,
      contentIdeas,
      escalationItems,
      llmSummary
    },
    options: buildOptions(comments, categories)
  };
}

async function loadRawTables() {
  const entries = await Promise.all(RAW_TABLES.map(async (definition) => {
    const result = await fetchCsvWithStatus(definition.path);
    return [
      definition.id,
      {
        ...definition,
        ...result
      }
    ];
  }));
  return Object.fromEntries(entries);
}

export function applyFilters(comments, filters) {
  return comments.filter((comment) => {
    const text = `${comment.text || ""} ${comment.keywords || ""}`.toLowerCase();
    const posted = comment.posted_at ? new Date(comment.posted_at) : null;
    return (
      matches(filters.platform, comment.platform) &&
      matches(filters.brand, comment.brand_or_competitor || comment.brand) &&
      matches(filters.sentiment, comment.sentiment_label) &&
      matches(filters.category, comment.concern_category_label) &&
      (!filters.search || text.includes(filters.search.toLowerCase())) &&
      (!filters.from || (posted && posted >= new Date(filters.from))) &&
      (!filters.to || (posted && posted <= new Date(filters.to)))
    );
  });
}

export function summarize(comments, categories) {
  const total = comments.length;
  const sentiment = countBy(comments, "sentiment_label");
  const platform = countBy(comments, "platform");
  const brand = countBy(comments, "brand_or_competitor");
  const category = countBy(comments, "concern_category_label");
  const keywords = countKeywords(comments);
  const volume = countByDate(comments);
  const sentimentTime = sentimentByDate(comments);
  const platformSentiment = sentimentByGroup(comments, "platform");
  const brandSentiment = sentimentByGroup(comments, "brand_or_competitor");
  const categoryByPlatform = nestedCount(comments, "platform", "concern_category_label");
  const keywordByPlatform = keywordByGroup(comments, "platform");
  const keywordByBrand = keywordByGroup(comments, "brand_or_competitor");
  const keywordBySentiment = keywordByGroup(comments, "sentiment_label");
  const trend = volumeTrend(volume);
  const categoryRows = categories
    .map((categoryConfig) => {
      const rows = comments.filter((comment) => sameCategory(comment, categoryConfig));
      const categoryVolume = countByDate(rows);
      return {
        ...categoryConfig,
        count: rows.length,
        percent: total ? rows.length / total : 0,
        change: volumeTrend(categoryVolume),
        sentiment: {
          positive: rows.filter((row) => row.sentiment_label === "positive").length,
          neutral: rows.filter((row) => row.sentiment_label === "neutral").length,
          negative: rows.filter((row) => row.sentiment_label === "negative").length
        },
        examples: rows.slice(0, 3)
      };
    })
    .sort((a, b) => b.count - a.count || Number(a.dashboard_priority || 99) - Number(b.dashboard_priority || 99));

  return {
    total,
    sentiment,
    platform,
    brand,
    category,
    keywords,
    volume,
    sentimentTime,
    platformSentiment,
    brandSentiment,
    categoryByPlatform,
    keywordByPlatform,
    keywordByBrand,
    keywordBySentiment,
    trend,
    categoryRows,
    riskSignals: riskSignals(comments, categoryRows),
    opportunitySignals: opportunitySignals(comments),
    repeatedQuestions: repeatedQuestions(comments),
    trustRiskComments: trustRiskComments(comments, categories),
    credibilityComments: categoryComments(comments, categories, "credibility"),
    refundComments: categoryComments(comments, categories, "refund"),
    safetyConditionComments: categoryComments(comments, categories, "condition"),
    serviceComments: categoryComments(comments, categories, "service")
  };
}

function mergeComments(marketComments, analysisRows) {
  const analysisById = new Map(analysisRows.map((row) => [row.record_id, row]));
  return marketComments.map((comment) => ({ ...comment, ...(analysisById.get(comment.record_id) || {}) }));
}

function buildOptions(comments, categories) {
  return {
    platforms: unique(comments.map((row) => row.platform)),
    brands: unique(comments.map((row) => row.brand_or_competitor || row.brand)),
    sentiments: unique(comments.map((row) => row.sentiment_label)).filter(Boolean),
    categories: categories.map((category) => category.label).filter(Boolean)
  };
}

function sampleComments(categories) {
  const defaults = categories.length ? categories : [{ label: "uncategorized", label_ar: "غير مصنف" }];
  return defaults.map((category, index) => ({
    record_id: `sample-${index + 1}`,
    platform: ["tiktok", "instagram", "x", "app_store"][index % 4],
    brand: index % 2 ? "Competitor" : "Telgani",
    brand_or_competitor: index % 2 ? "Competitor" : "Telgani",
    source_account: "sample_mode",
    posted_at: new Date(Date.now() - index * 86400000).toISOString(),
    text: `Sample display row for ${category.label}. Replace by running scrape, normalize, and analysis.`,
    sentiment_label: index % 3 === 0 ? "negative" : index % 3 === 1 ? "neutral" : "positive",
    concern_category_id: category.id,
    concern_category_label: category.label,
    recommended_action: category.recommended_action || "Monitor this signal and connect it to the next campaign planning cycle.",
    keywords: `${category.label || "sample"}, marketing, feedback`,
    urgency_flag: index === 0 ? "true" : "false",
    raw_file_path: "sample-mode"
  }));
}

function sameCategory(comment, category) {
  return comment.concern_category_id === category.id || comment.concern_category_label === category.label;
}

function matches(filterValue, rowValue) {
  return !filterValue || filterValue === rowValue;
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort();
}

function countBy(rows, key) {
  return rows.reduce((acc, row) => {
    const value = row[key] || "unknown";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function countKeywords(rows) {
  const counts = {};
  rows.forEach((row) => {
    (row.keywords || "").split(",").map((item) => item.trim()).filter(Boolean).forEach((keyword) => {
      counts[keyword] = (counts[keyword] || 0) + 1;
    });
  });
  return counts;
}

function countByDate(rows) {
  return countBy(rows.map((row) => ({ date: (row.posted_at || "").slice(0, 10) || "unknown" })), "date");
}

function sentimentByDate(rows) {
  const grouped = {};
  rows.forEach((row) => {
    const date = (row.posted_at || "").slice(0, 10) || "unknown";
    grouped[date] ||= { positive: 0, neutral: 0, negative: 0 };
    grouped[date][row.sentiment_label || "neutral"] = (grouped[date][row.sentiment_label || "neutral"] || 0) + 1;
  });
  return grouped;
}

function sentimentByGroup(rows, groupKey) {
  const grouped = {};
  rows.forEach((row) => {
    const group = row[groupKey] || "unknown";
    grouped[group] ||= { positive: 0, neutral: 0, negative: 0, total: 0 };
    const sentiment = row.sentiment_label || "neutral";
    grouped[group][sentiment] = (grouped[group][sentiment] || 0) + 1;
    grouped[group].total += 1;
  });
  return grouped;
}

function nestedCount(rows, groupKey, valueKey) {
  const grouped = {};
  rows.forEach((row) => {
    const group = row[groupKey] || "unknown";
    const value = row[valueKey] || "unknown";
    grouped[group] ||= {};
    grouped[group][value] = (grouped[group][value] || 0) + 1;
  });
  return grouped;
}

function keywordByGroup(rows, groupKey) {
  const grouped = {};
  rows.forEach((row) => {
    const group = row[groupKey] || "unknown";
    grouped[group] ||= {};
    (row.keywords || "").split(",").map((item) => item.trim()).filter(Boolean).forEach((keyword) => {
      grouped[group][keyword] = (grouped[group][keyword] || 0) + 1;
    });
  });
  return grouped;
}

function volumeTrend(volume) {
  const entries = Object.entries(volume)
    .filter(([date]) => date !== "unknown")
    .sort(([a], [b]) => a.localeCompare(b));
  if (entries.length < 2) return { label: "not enough data", delta: 0, recent: 0, previous: 0 };
  const midpoint = Math.floor(entries.length / 2);
  const previous = entries.slice(0, midpoint).reduce((sum, [, value]) => sum + Number(value || 0), 0);
  const recent = entries.slice(midpoint).reduce((sum, [, value]) => sum + Number(value || 0), 0);
  const delta = recent - previous;
  const label = delta > 0 ? "increasing" : delta < 0 ? "decreasing" : "stable";
  return { label, delta, recent, previous };
}

function riskSignals(comments, categoryRows) {
  const negativeOrUrgent = comments.filter((row) => row.sentiment_label === "negative" || row.urgency_flag === "true");
  const risks = categoryRows
    .filter((row) => row.count > 0)
    .map((row) => ({
      label: row.label,
      count: row.count,
      urgency: row.examples.filter((item) => item.urgency_flag === "true").length,
      action: row.recommended_action || "Review this signal and decide whether messaging or operations follow-up is needed.",
      team: row.escalation_team || "Review owner",
      example: row.examples[0]
    }));
  return risks.length ? risks.slice(0, 5) : negativeOrUrgent.slice(0, 5).map((row) => ({
    label: row.concern_category_label || "Uncategorized risk signal",
    count: 1,
    urgency: row.urgency_flag === "true" ? 1 : 0,
    action: row.recommended_action || "Review this signal and connect it to a response path.",
    team: "Review owner",
    example: row
  }));
}

function opportunitySignals(comments) {
  return comments
    .filter((row) => row.sentiment_label === "positive" || row.recommended_action)
    .slice(0, 8)
    .map((row) => ({
      label: row.keywords || row.concern_category_label || "Opportunity signal",
      action: row.recommended_action || "Reuse this positive theme in campaign planning or community replies.",
      example: row
    }));
}

function repeatedQuestions(comments) {
  return comments
    .filter((row) => /question|faq/i.test(`${row.keywords || ""} ${row.recommended_action || ""} ${row.concern_category_label || ""}`))
    .slice(0, 12);
}

function trustRiskComments(comments, categories) {
  const trustCategories = categories.filter((category) => category.trust_risk === true || category.trust_risk === "true");
  return comments.filter((comment) => trustCategories.some((category) => sameCategory(comment, category))).slice(0, 20);
}

function categoryComments(comments, categories, needle) {
  const matched = categories.filter((category) => category.dashboard_group === needle);
  return comments.filter((comment) => matched.some((category) => sameCategory(comment, category))).slice(0, 20);
}

async function fetchCsv(path) {
  return fetchText(path).then(parseCsv).catch(() => []);
}

async function fetchCsvWithStatus(path) {
  try {
    const text = await fetchText(path);
    return { rows: parseCsv(text), status: "loaded", error: "" };
  } catch (error) {
    return { rows: [], status: "error", error: error.message || "Unable to load CSV." };
  }
}

async function fetchJson(path, fallback) {
  return fetch(new URL(path, import.meta.url)).then((response) => {
    if (!response.ok) throw new Error(path);
    return response.json();
  }).catch(() => fallback);
}

async function fetchText(path) {
  const response = await fetch(new URL(path, import.meta.url));
  if (!response.ok) throw new Error(path);
  return response.text();
}
