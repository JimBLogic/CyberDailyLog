import type { Severity } from "./types";

const ORDER: Severity[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"];

/** Filter only the displayed selection, never the full-report distribution. */
export function availableSeverityOptions(items: readonly { severity: Severity }[]) {
  const counts = new Map<Severity, number>();
  for (const item of items) counts.set(item.severity, (counts.get(item.severity) ?? 0) + 1);
  return ORDER.filter(severity => counts.has(severity))
    .map(severity => ({ severity, count: counts.get(severity)! }));
}

export function resolveSeverityFilter(
  selected: Severity | "ALL",
  options: readonly { severity: Severity }[],
): Severity | "ALL" {
  return selected === "ALL" || options.some(option => option.severity === selected)
    ? selected : "ALL";
}
