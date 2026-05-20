import { parseCsv } from "./utils/csv.js";
import { renderInternalInsightsPage } from "./views/InternalInsightsPage.js";

const ANALYSIS_FILES = {
  commentAnalysis: "../data/analysis/comment_analysis.csv",
  concernSummary: "../data/analysis/concern_category_summary.csv",
  sentimentSummary: "../data/analysis/sentiment_summary.csv",
  platformSummary: "../data/analysis/platform_summary.csv",
  brandSummary: "../data/analysis/brand_competitor_summary.csv",
  keywordSummary: "../data/analysis/keyword_summary.csv",
  marketingOpportunities: "../data/analysis/marketing_opportunities.csv",
  contentIdeas: "../data/analysis/content_ideas.csv",
  urgentComments: "../data/analysis/urgent_comments.csv",
  escalationItems: "../data/analysis/escalation_items.csv",
  emergingConcerns: "../data/analysis/emerging_concerns.csv",
  llmSummary: "../data/analysis/llm_insight_summary.json"
};

const app = document.querySelector("#internal-insights-app");
const state = {
  platform: "",
  brand: "",
  sentiment: "",
  concern: "",
  from: "",
  to: ""
};

let analysisData = null;

init();

async function init() {
  analysisData = await loadAnalysisData();
  render();
}

function render() {
  app.innerHTML = renderInternalInsightsPage({ data: analysisData, filters: state });
  bindInteractions();
}

function bindInteractions() {
  app.querySelector("#internal-filters")?.addEventListener("change", updateFilter);
  app.querySelector("#internal-filters")?.addEventListener("input", updateFilter);

  app.querySelectorAll("[data-set-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      const [key, value] = (button.dataset.setFilter || "").split("::");
      if (!key) return;
      state[key] = value || "";
      render();
      app.querySelector("#customer-voice")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  app.querySelectorAll("[data-clear-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state[button.dataset.clearFilter] = "";
      render();
    });
  });
}

function updateFilter(event) {
  const field = event.target;
  if (!field.name) return;
  state[field.name] = field.value;
  render();
}

async function loadAnalysisData() {
  const entries = await Promise.all(Object.entries(ANALYSIS_FILES).map(async ([key, path]) => {
    if (path.endsWith(".json")) {
      return [key, await fetchJson(path, null)];
    }
    return [key, await fetchCsv(path)];
  }));
  return Object.fromEntries(entries);
}

async function fetchCsv(path) {
  try {
    const response = await fetch(new URL(path, import.meta.url));
    if (!response.ok) throw new Error(path);
    return parseCsv(await response.text());
  } catch (_error) {
    return [];
  }
}

async function fetchJson(path, fallback) {
  try {
    const response = await fetch(new URL(path, import.meta.url));
    if (!response.ok) throw new Error(path);
    return await response.json();
  } catch (_error) {
    return fallback;
  }
}
