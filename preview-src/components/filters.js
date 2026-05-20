export function filterBar(options, filters) {
  return `
    <form class="filters" id="filters">
      ${selectField("platform", "Platform", options.platforms, filters.platform)}
      ${selectField("brand", "Brand / competitor", options.brands, filters.brand)}
      ${selectField("sentiment", "Sentiment", options.sentiments, filters.sentiment)}
      ${selectField("category", "Concern category", options.categories, filters.category)}
      <div class="filter-field">
        <label for="from">From</label>
        <input id="from" name="from" type="date" value="${filters.from || ""}" />
      </div>
      <div class="filter-field">
        <label for="to">To</label>
        <input id="to" name="to" type="date" value="${filters.to || ""}" />
      </div>
      <div class="filter-field" style="grid-column:1 / -1">
        <label for="search">Search comments</label>
        <input id="search" name="search" type="search" value="${filters.search || ""}" placeholder="Search Arabic or English text" />
      </div>
    </form>
  `;
}

function selectField(name, label, values, selected) {
  return `
    <div class="filter-field">
      <label for="${name}">${label}</label>
      <select id="${name}" name="${name}">
        <option value="">All</option>
        ${values.map((value) => `<option value="${escapeAttr(value)}" ${selected === value ? "selected" : ""}>${value}</option>`).join("")}
      </select>
    </div>
  `;
}

function escapeAttr(value) {
  return String(value).replace(/"/g, "&quot;");
}
