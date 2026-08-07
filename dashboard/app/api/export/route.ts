import { getDashboardData } from "@/lib/data";
import type { Vulnerability } from "@/lib/types";

function csvCell(value: unknown) {
  const text = value === null || value === undefined ? "" : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

function toCsv(vulnerabilities: Vulnerability[]) {
  const header = [
    "id",
    "priority_score",
    "severity",
    "cvss_score",
    "epss_score",
    "cisa_kev",
    "known_exploited",
    "known_ransomware_use",
    "published_at",
    "source",
    "title",
    "source_url",
  ];
  const rows = vulnerabilities.map((item) => [
    item.id,
    item.priorityScore,
    item.severity,
    item.cvssScore,
    item.epssScore,
    item.cisaKev,
    item.knownExploited,
    item.knownRansomwareUse,
    item.publishedAt,
    item.sourceName,
    item.title,
    item.sourceUrl,
  ]);
  return [header, ...rows]
    .map((row) => row.map(csvCell).join(","))
    .join("\n");
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const format = url.searchParams.get("format") === "csv" ? "csv" : "json";
  const data = await getDashboardData();
  const date = data.generatedAt.slice(0, 10);

  if (format === "csv") {
    return new Response(toCsv(data.vulnerabilities), {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": `attachment; filename="cyberdailylog-${date}.csv"`,
        "Cache-Control": "private, no-store",
        "X-Content-Type-Options": "nosniff",
      },
    });
  }

  return Response.json(data, {
    headers: {
      "Content-Disposition": `attachment; filename="cyberdailylog-${date}.json"`,
      "Cache-Control": "private, no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
