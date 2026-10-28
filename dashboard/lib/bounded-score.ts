/** Preserve unknown/invalid source scores as null instead of clamping them. */
export function boundedScore(value: unknown, maximum: 1 | 10): number | null {
  if (typeof value !== "number" && (typeof value !== "string" || !value.trim())) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 && parsed <= maximum ? parsed : null;
}
