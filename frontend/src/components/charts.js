import { number, percent } from "../utils/format.js";

export function barChart(items, options = {}) {
  const total = Math.max(...items.map((item) => Number(item.value || 0)), 1);
  if (!items.length) return emptyChart("No data available");
  return `
    <div class="chart" role="img" aria-label="${options.label || "Bar chart"}">
      ${items.map((item) => `
        <div class="bar-row">
          <div class="bar-label">
            <span>${item.label}</span>
            <strong>${number(item.value)}</strong>
          </div>
          <div class="bar-track"><div class="bar-fill" style="width:${Math.round((Number(item.value || 0) / total) * 100)}%"></div></div>
        </div>
      `).join("")}
    </div>
  `;
}

export function sentimentSplit(sentiment) {
  const positive = Number(sentiment.positive || 0);
  const neutral = Number(sentiment.neutral || 0);
  const negative = Number(sentiment.negative || 0);
  const total = positive + neutral + negative || 1;
  return `
    <div class="chart">
      <div class="sentiment-stack" title="Sentiment split">
        <div class="sentiment-positive" style="width:${(positive / total) * 100}%"></div>
        <div class="sentiment-neutral" style="width:${(neutral / total) * 100}%"></div>
        <div class="sentiment-negative" style="width:${(negative / total) * 100}%"></div>
      </div>
      <div class="grid three" style="margin-top:16px">
        ${miniMetric("Positive", positive, total, "sentiment-positive")}
        ${miniMetric("Neutral", neutral, total, "sentiment-neutral")}
        ${miniMetric("Negative", negative, total, "sentiment-negative")}
      </div>
    </div>
  `;
}

export function keywordCloud(keywords) {
  const entries = Object.entries(keywords).sort((a, b) => b[1] - a[1]).slice(0, 40);
  if (!entries.length) return emptyChart("No keywords available");
  const max = Math.max(...entries.map(([, count]) => count), 1);
  return `<div class="tag-cloud">${entries.map(([word, count]) => `<button class="tag tag-button" data-keyword-filter="${word}" style="font-size:${13 + (count / max) * 10}px">${word} <strong>${count}</strong></button>`).join("")}</div>`;
}

export function timeline(volume) {
  const entries = Object.entries(volume).sort(([a], [b]) => a.localeCompare(b)).slice(-30);
  return barChart(entries.map(([label, value]) => ({ label, value })), { label: "Comment volume over time" });
}

export function sentimentTimeline(sentimentTime) {
  const entries = Object.entries(sentimentTime).sort(([a], [b]) => a.localeCompare(b)).slice(-14);
  if (!entries.length) return emptyChart("No sentiment timeline available");
  return `
    <div class="chart">
      ${entries.map(([date, split]) => {
        const total = (split.positive || 0) + (split.neutral || 0) + (split.negative || 0) || 1;
        return `
          <div class="bar-row">
            <div class="bar-label"><span>${date}</span><strong>${number(total)}</strong></div>
            <div class="sentiment-stack">
              <div class="sentiment-positive" style="width:${((split.positive || 0) / total) * 100}%"></div>
              <div class="sentiment-neutral" style="width:${((split.neutral || 0) / total) * 100}%"></div>
              <div class="sentiment-negative" style="width:${((split.negative || 0) / total) * 100}%"></div>
            </div>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

export function categoryRanking(rows, activeCategory = "") {
  if (!rows.length) return emptyChart("No concern categories configured");
  return rows.slice(0, 5).map((category, index) => `
    <button class="category-button ${activeCategory === category.label ? "active" : ""}" data-category-filter="${category.label}">
      <div class="bar-label">
        <strong>${index + 1}. ${category.label}</strong>
        <span>${percent(category.percent)}</span>
      </div>
      <div class="arabic">${category.label_ar || ""}</div>
      <div class="category-meta">
        <span>${number(category.count)} comments</span>
        <span>Change: ${category.change?.label || "not enough data"}</span>
        <span>Owner: ${category.escalation_team || "Review owner"}</span>
      </div>
      <div class="sentiment-stack" style="margin-top:10px">
        <div class="sentiment-positive" style="width:${splitWidth(category.sentiment.positive, category.count)}%"></div>
        <div class="sentiment-neutral" style="width:${splitWidth(category.sentiment.neutral, category.count)}%"></div>
        <div class="sentiment-negative" style="width:${splitWidth(category.sentiment.negative, category.count)}%"></div>
      </div>
      <p class="meta">Recommended action: ${category.recommended_action || "Monitor this signal and connect it to campaign planning."}</p>
      ${category.examples.map((item) => `<p class="${/[\u0600-\u06FF]/.test(item.text || "") ? "arabic" : ""}">${item.text || ""}</p>`).join("")}
    </button>
  `).join("");
}

function miniMetric(label, count, total, className) {
  return `<div class="panel"><span class="tag ${className}"></span><p class="card-value">${percent(count / total)}</p><p class="meta">${label} ${number(count)}</p></div>`;
}

function splitWidth(value, total) {
  return total ? (Number(value || 0) / total) * 100 : 0;
}

function emptyChart(message) {
  return `<div class="empty-state">${message}</div>`;
}
