export function parseCsv(text) {
  const clean = text.replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < clean.length; index += 1) {
    const char = clean[index];
    const next = clean[index + 1];
    if (quoted && char === '"' && next === '"') {
      field += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (!quoted && char === ",") {
      row.push(field);
      field = "";
    } else if (!quoted && (char === "\n" || char === "\r")) {
      if (char === "\r" && next === "\n") index += 1;
      row.push(field);
      if (row.some((value) => value !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }

  const [headers = [], ...body] = rows;
  return body.map((values) =>
    Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]))
  );
}

export function parseSimpleCategoriesYaml(text) {
  const categories = [];
  let current = null;
  let activeListKey = null;

  for (const rawLine of text.split(/\r?\n/)) {
    const withoutComment = rawLine.replace(/\s+#.*$/, "");
    if (!withoutComment.trim()) continue;
    const indent = withoutComment.match(/^\s*/)[0].length;
    const line = withoutComment.trim();

    if (line.startsWith("- id:")) {
      current = { id: unquote(line.slice(5).trim()) };
      categories.push(current);
      activeListKey = null;
      continue;
    }

    if (!current) continue;

    if (line.startsWith("- ") && activeListKey) {
      current[activeListKey].push(unquote(line.slice(2).trim()));
      continue;
    }

    const separator = line.indexOf(":");
    if (separator === -1) continue;
    const key = line.slice(0, separator).trim();
    const value = line.slice(separator + 1).trim();
    if (!value && indent >= 4) {
      current[key] = [];
      activeListKey = key;
    } else {
      current[key] = coerceValue(unquote(value));
      activeListKey = null;
    }
  }

  return categories;
}

function unquote(value) {
  return value.replace(/^["']|["']$/g, "");
}

function coerceValue(value) {
  if (/^\d+$/.test(value)) return Number(value);
  return value;
}
