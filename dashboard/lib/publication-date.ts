/** Retrieval time must never substitute an unknown publication date. */
export function publicationDate(value: unknown, now = Date.now()): string {
  if (typeof value !== "string" || !value.trim()) return "";
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) && parsed >= Date.UTC(2000, 0, 1) && parsed <= now + 5 * 60 * 1000
    ? new Date(parsed).toISOString()
    : "";
}
