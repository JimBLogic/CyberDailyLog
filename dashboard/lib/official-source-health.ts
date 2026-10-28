type Source = "nvd" | "cisa";

/** Transport success alone does not establish usable, complete source coverage. */
export function officialSourceHealth(value: unknown, source: Source) {
  const failed = { status: "failed" as const, received: 0, rejected: 0, error: "Invalid official source payload" };
  if (!value || typeof value !== "object" || Array.isArray(value)) return failed;
  const payload = value as Record<string, unknown>;
  if (!Array.isArray(payload.vulnerabilities)) return failed;
  const rows = payload.vulnerabilities;
  const seen = new Set<string>();
  let rejected = 0;
  for (const raw of rows) {
    const row = raw && typeof raw === "object" ? raw as Record<string, unknown> : null;
    const cve = row?.cve && typeof row.cve === "object" ? row.cve as Record<string, unknown> : null;
    const id = source === "nvd" ? cve?.id : row?.cveID;
    if (typeof id !== "string" || !/^CVE-\d{4}-\d{4,}$/.test(id) || seen.has(id)) rejected++;
    else seen.add(id);
  }
  const total = source === "nvd" ? payload.totalResults : payload.count;
  const validTotal = typeof total === "number" && Number.isSafeInteger(total) && total >= 0;
  const validPage = source === "cisa" || (payload.startIndex === 0 &&
    typeof payload.resultsPerPage === "number" && Number.isSafeInteger(payload.resultsPerPage) &&
    payload.resultsPerPage >= rows.length);
  const complete = validTotal && validPage && total === rows.length && rejected === 0;
  return {
    status: complete ? "healthy" as const : "degraded" as const,
    received: rows.length,
    rejected,
    error: complete ? null : "Official source data is invalid, partial or truncated",
  };
}
