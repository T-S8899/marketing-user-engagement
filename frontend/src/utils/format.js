export function number(value) {
  const parsed = Number(value || 0);
  return new Intl.NumberFormat("en").format(parsed);
}

export function percent(value) {
  const parsed = Number(value || 0);
  return `${Math.round(parsed * 100)}%`;
}

export function shortText(value, length = 120) {
  const text = value || "";
  return text.length > length ? `${text.slice(0, length - 1)}...` : text;
}

export function isArabic(text = "") {
  return /[\u0600-\u06FF]/.test(text);
}

export function safeDate(value) {
  const date = value ? new Date(value) : null;
  return date && !Number.isNaN(date.getTime()) ? date : null;
}
