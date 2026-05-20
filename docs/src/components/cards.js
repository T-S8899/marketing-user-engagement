import { number } from "../utils/format.js";

export function kpiCard(label, value, detail = "") {
  return `
    <article class="card">
      <p class="card-label">${label}</p>
      <p class="card-value">${number(value)}</p>
      <p class="meta">${detail}</p>
    </article>
  `;
}
