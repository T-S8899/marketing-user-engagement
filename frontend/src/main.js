import { applyFilters, loadDashboardData, summarize } from "./data/adapter.js";
import { filterBar } from "./components/filters.js";
import { navGroups, renderDashboardViews } from "./views/dashboard.js";

const app = document.querySelector("#app");
const state = {
  platform: "",
  brand: "",
  sentiment: "",
  category: "",
  from: "",
  to: "",
  search: "",
  rawTable: "market_comments",
  rawSearch: "",
  rawSort: "",
  rawPage: "1"
};

let dashboardData = null;

init();

async function init() {
  try {
    dashboardData = await loadDashboardData();
    app.classList.add(dashboardData.brand.themeClass || "brand-golden");
    render();
  } catch (error) {
    app.innerHTML = `<main class="error-state">Dashboard could not load local data. ${error.message}</main>`;
  }
}

function render() {
  const filtered = applyFilters(dashboardData.comments, state);
  const summary = summarize(filtered, dashboardData.categories);
  const logoPath = dashboardData.brand.logoPath || "";
  const logoFallback = dashboardData.brand.logoText || dashboardData.brand.brandName || "T";
  app.innerHTML = `
    <div class="dashboard">
      <aside class="sidebar">
        <div class="sidebar-header">
          <span class="brand-mark">
            ${logoPath ? `<img src="${logoPath}" alt="${dashboardData.brand.brandName || "Telgani"}" data-fallback-image /><span hidden>${logoFallback}</span>` : logoFallback}
          </span>
          <div>
            <strong>${dashboardData.brand.brandName || "Telgani"}</strong>
            <div class="meta">${dashboardData.usingSample ? "Sample mode" : "Local data"}</div>
          </div>
        </div>
        <nav class="nav-list" aria-label="Dashboard navigation">
          <div class="nav-page-links">
            <a class="nav-link page-link" href="./announcement.html">Customer Announcement</a>
            <a class="nav-link page-link" href="./internal_insights.html">Internal Briefing</a>
          </div>
          <label class="nav-search">
            <span>Find section</span>
            <input type="search" data-section-search placeholder="Search sections" />
          </label>
          ${navGroups.map(([group, items]) => `
            <div class="nav-group" data-nav-group>
              <span class="nav-group-title">${group}</span>
              ${items.map(([id, label]) => `<a class="nav-link section-nav-link" data-section-nav="${id}" href="#${id}">${label}</a>`).join("")}
            </div>
          `).join("")}
          <a class="nav-link back-top-link" href="#top">Back to top</a>
        </nav>
      </aside>
      <main class="main">
        <div class="topbar">
          <div>
            <h1 class="brand-title">${dashboardData.brand.dashboardName || "Marketing Intelligence Dashboard"}</h1>
            <p class="section-subtitle">${dashboardData.brand.refreshHint || ""}</p>
          </div>
          <span class="status-pill">${dashboardData.usingSample ? "Sample data shown" : "Live local files loaded"}</span>
        </div>
        ${filterBar(dashboardData.options, state)}
        ${filtered.length ? "" : `<div class="empty-state">No comments match the selected filters.</div>`}
        ${renderDashboardViews(dashboardData, filtered, summary, state)}
      </main>
    </div>
  `;
  bindInteractions();
}

function bindInteractions() {
  document.querySelectorAll("[data-fallback-image]").forEach((image) => {
    image.addEventListener("error", () => {
      image.hidden = true;
      image.nextElementSibling?.removeAttribute("hidden");
    }, { once: true });
  });

  const filters = document.querySelector("#filters");
  filters?.addEventListener("input", updateFilters);
  filters?.addEventListener("change", updateFilters);

  bindSectionNavigation();

  document.querySelectorAll(".raw-explorer input[name], .raw-explorer select[name]").forEach((field) => {
    field.addEventListener("input", updateFilters);
    field.addEventListener("change", updateFilters);
  });

  document.querySelectorAll("[data-raw-table]").forEach((button) => {
    button.addEventListener("click", () => {
      state.rawTable = button.dataset.rawTable || "market_comments";
      state.rawSearch = "";
      state.rawSort = "";
      state.rawPage = "1";
      render();
      document.querySelector("#raw-data")?.scrollIntoView({ behavior: "smooth" });
    });
  });

  document.querySelectorAll("[data-category-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.category = button.dataset.categoryFilter || "";
      render();
      document.querySelector("#comment-explorer")?.scrollIntoView({ behavior: "smooth" });
    });
  });

  document.querySelectorAll("[data-keyword-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.search = button.dataset.keywordFilter || "";
      render();
      document.querySelector("#comment-explorer")?.scrollIntoView({ behavior: "smooth" });
    });
  });

  document.querySelectorAll("[data-expand]").forEach((button) => {
    button.addEventListener("click", () => {
      const row = document.getElementById(button.dataset.expand);
      if (!row) return;
      row.hidden = !row.hidden;
      button.textContent = row.hidden ? "+" : "-";
    });
  });

  document.querySelectorAll("[data-table-search]").forEach((input) => {
    input.addEventListener("input", () => filterTable(input.dataset.tableSearch, input.value));
  });

  document.querySelectorAll("[data-table-sort]").forEach((select) => {
    select.addEventListener("change", () => sortTable(select.dataset.tableSort, select.value));
  });

  document.querySelectorAll("[data-raw-page]").forEach((button) => {
    button.addEventListener("click", () => {
      state.rawPage = button.dataset.rawPage || "1";
      render();
      document.querySelector("#raw-data")?.scrollIntoView({ behavior: "smooth" });
    });
  });
}

function bindSectionNavigation() {
  const search = document.querySelector("[data-section-search]");
  search?.addEventListener("input", () => {
    const needle = search.value.trim().toLowerCase();
    document.querySelectorAll("[data-section-nav]").forEach((link) => {
      const group = link.closest("[data-nav-group]");
      const match = !needle || link.textContent.toLowerCase().includes(needle) || group?.querySelector(".nav-group-title")?.textContent.toLowerCase().includes(needle);
      link.hidden = !match;
    });
  });

  const links = [...document.querySelectorAll("[data-section-nav]")];
  const sections = links.map((link) => document.getElementById(link.dataset.sectionNav)).filter(Boolean);
  if (!sections.length || !("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    links.forEach((link) => link.classList.toggle("active", link.dataset.sectionNav === visible.target.id));
  }, { rootMargin: "-20% 0px -65% 0px", threshold: [0.1, 0.25, 0.5] });
  sections.forEach((section) => observer.observe(section));
}

function updateFilters(event) {
  const field = event.target;
  if (!field.name) return;
  state[field.name] = field.value;
  if (["rawTable", "rawSearch", "rawSort"].includes(field.name)) {
    state.rawPage = "1";
  }
  render();
}

function filterTable(id, query) {
  const needle = query.toLowerCase();
  document.querySelectorAll(`[data-table-row="${id}"]`).forEach((row) => {
    const detail = row.nextElementSibling;
    const visible = row.dataset.rowText.includes(needle);
    row.hidden = !visible;
    if (detail?.id) detail.hidden = true;
  });
}

function sortTable(id, key) {
  const table = document.querySelector(`[data-table="${id}"] tbody`);
  if (!table) return;
  const headerCells = [...document.querySelectorAll(`[data-table="${id}"] th`)];
  const columnIndex = headerCells.findIndex((cell) => cell.textContent.toLowerCase().includes(key.replaceAll("_", " ").split(" ")[0]));
  const pairs = [];
  [...table.children].forEach((row, index, rows) => {
    if (row.dataset.tableRow === id) pairs.push([row, rows[index + 1]]);
  });
  pairs.sort(([a], [b]) => cellText(a, columnIndex).localeCompare(cellText(b, columnIndex), undefined, { numeric: true }));
  table.replaceChildren(...pairs.flat().filter(Boolean));
}

function cellText(row, index) {
  return row.children[Math.max(index, 1)]?.textContent || "";
}
