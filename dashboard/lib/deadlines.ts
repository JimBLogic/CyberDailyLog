// CISA publishes dates, not instants. Never call a deadline overdue at midnight UTC.
export function calendarDate(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const day = value.slice(0, 10);
  return /^\d{4}-\d{2}-\d{2}$/.test(day) && Number.isFinite(Date.parse(day)) && new Date(day).toISOString().slice(0,10) === day ? day : null;
}
export function deadlineDays(value: unknown, now = new Date()): number | null {
  const due = calendarDate(value);
  if (!due) return null;
  const today = new Intl.DateTimeFormat("en-CA", {timeZone:"Europe/Madrid", year:"numeric", month:"2-digit", day:"2-digit"}).format(now);
  return Math.round((Date.parse(due) - Date.parse(today)) / 86400000);
}
export function deadlineRank(value: unknown, now = new Date()) {
  const days = deadlineDays(value, now);
  return days !== null && days >= 0 && days <= 2 ? days : 3;
}
export function deadlineLabel(value: unknown, language: "es" | "en", now = new Date()) {
  const days = deadlineDays(value, now), day = calendarDate(value);
  if (days === null || !day) return "";
  const es = language === "es";
  const status = days === 0 ? (es ? "Vence hoy" : "Due today") : days === 1 ? (es ? "Vence mañana" : "Due tomorrow") : days < 0 ? (es ? "Plazo vencido" : "Past deadline") : (es ? "Plazo CISA" : "CISA deadline");
  return `${status} · ${day}`;
}
