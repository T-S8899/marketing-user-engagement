import { isArabic, shortText } from "../utils/format.js";

export function dataTable(id, rows, columns, options = {}) {
  const searchable = options.searchable !== false;
  const visibleRows = rows.slice(0, options.limit || 100);
  return `
    <div class="panel" data-table="${id}">
      <div class="table-tools">
        ${searchable ? `<input type="search" data-table-search="${id}" placeholder="Search table" />` : ""}
        <select data-table-sort="${id}">
          ${columns.map((column) => `<option value="${column.key}">Sort by ${column.label}</option>`).join("")}
        </select>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th></th>
              ${columns.map((column) => `<th>${column.label}</th>`).join("")}
            </tr>
          </thead>
          <tbody>
            ${visibleRows.map((row, index) => rowMarkup(id, row, columns, index)).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function rowMarkup(id, row, columns, index) {
  const text = row.text || row.example_text || JSON.stringify(row);
  const sourceLink = row.source_url ? `<a href="${escapeAttr(row.source_url)}" target="_blank" rel="noreferrer">Open source</a>` : "No source link";
  const rawReference = row.raw_file_path || row.raw_record_hash || "No raw reference";
  return `
    <tr data-table-row="${id}" data-row-text="${escapeAttr(Object.values(row).join(" ").toLowerCase())}">
      <td><button class="expand-button" data-expand="${id}-${index}">+</button></td>
      ${columns.map((column) => `<td class="${isArabic(row[column.key] || "") ? "arabic" : ""}">${shortText(row[column.key] || "", column.length || 80)}</td>`).join("")}
    </tr>
    <tr id="${id}-${index}" hidden>
      <td colspan="${columns.length + 1}">
        <div class="comment-detail ${isArabic(text) ? "arabic" : ""}">
          <p>${text}</p>
          <dl class="detail-list">
            <dt>Source</dt><dd>${sourceLink}</dd>
            <dt>Recommended action</dt><dd>${row.recommended_action || "No prepared recommendation"}</dd>
            <dt>Keywords</dt><dd>${row.keywords || "No keywords"}</dd>
            <dt>Raw reference</dt><dd>${rawReference}</dd>
          </dl>
        </div>
      </td>
    </tr>
  `;
}

function escapeAttr(value) {
  return String(value).replace(/"/g, "&quot;");
}
