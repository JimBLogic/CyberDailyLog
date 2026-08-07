import type { Severity, SourceHealth, Vulnerability } from "./types";

const CISA_KEV_URL =
  "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json";
const NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0";
const EPSS_API_URL = "https://api.first.org/data/v1/epss";
const OFFICIAL_TIMEOUT_MS = 6_500;
const OFFICIAL_CACHE_TTL_MS = 2 * 60 * 60 * 1_000;
const NEGATIVE_CACHE_TTL_MS = 10 * 60 * 1_000;
const NVD_WINDOW_MS = 48 * 60 * 60 * 1_000;
const EPSS_BATCH_SIZE = 20;

type JsonRecord = Record<string, unknown>;

export type OfficialBackupResult = {
  generatedAt: string;
  coverageStart: string;
  coverageEnd: string;
  vulnerabilities: Vulnerability[];
  sourceHealth: SourceHealth[];
};

let officialCache: {
  result: OfficialBackupResult | null;
  expiresAt: number;
} | null = null;
let officialInFlight: Promise<OfficialBackupResult | null> | null = null;

function record(value: unknown): JsonRecord | null {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as JsonRecord)
    : null;
}

function records(value: unknown): JsonRecord[] {
  return Array.isArray(value)
    ? value.map(record).filter((item): item is JsonRecord => item !== null)
    : [];
}

function text(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function numeric(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function safeDate(value: unknown, fallback: string) {
  const candidate = text(value);
  const parsed = Date.parse(candidate);
  return Number.isFinite(parsed) && parsed >= Date.UTC(2000, 0, 1)
    ? new Date(parsed).toISOString()
    : fallback;
}

function safeSeverity(value: unknown): Severity {
  const severity = text(value, "UNKNOWN").toUpperCase();
  return ["CRITICAL", "HIGH", "MEDIUM", "LOW"].includes(severity)
    ? (severity as Severity)
    : "UNKNOWN";
}

async function fetchJson<T>(url: string) {
  const startedAt = Date.now();
  try {
    const response = await fetch(url, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(OFFICIAL_TIMEOUT_MS),
    });
    if (!response.ok) {
      return { data: null as T | null, durationMs: Date.now() - startedAt };
    }
    return {
      data: (await response.json()) as T,
      durationMs: Date.now() - startedAt,
    };
  } catch {
    return { data: null as T | null, durationMs: Date.now() - startedAt };
  }
}

function englishDescription(cve: JsonRecord) {
  const descriptions = records(cve.descriptions);
  const preferred =
    descriptions.find((item) => text(item.lang).toLowerCase() === "en") ??
    descriptions[0];
  return text(
    preferred?.value,
    "Open the official NVD record for the current technical description.",
  );
}

function metricFor(cve: JsonRecord) {
  const metrics = record(cve.metrics);
  const groups = [
    records(metrics?.cvssMetricV40),
    records(metrics?.cvssMetricV31),
    records(metrics?.cvssMetricV30),
    records(metrics?.cvssMetricV2),
  ];
  const entry = groups.find((group) => group.length)?.[0] ?? null;
  const data = record(entry?.cvssData);
  return {
    score: numeric(data?.baseScore),
    version: text(data?.version) || null,
    vector: text(data?.vectorString) || null,
    severity: safeSeverity(data?.baseSeverity ?? entry?.baseSeverity),
  };
}

function referencesFor(cve: JsonRecord) {
  return records(cve.references)
    .map((item) => text(item.url))
    .filter(Boolean)
    .slice(0, 6);
}

function initialPriority(item: Vulnerability) {
  let score = 0.5;
  if (item.cisaKev) score += 5;
  if (item.knownRansomwareUse) score += 2;
  if (item.cvssScore !== null) {
    if (item.cvssScore >= 9) score += 2;
    else if (item.cvssScore >= 7) score += 1.25;
    else if (item.cvssScore >= 4) score += 0.5;
  }
  if (item.epssScore !== null) {
    if (item.epssScore >= 0.5) score += 2;
    else if (item.epssScore >= 0.1) score += 1;
    else if (item.epssScore >= 0.01) score += 0.35;
  }
  return Math.round(Math.min(10, score) * 10) / 10;
}

function cisaMapFrom(value: unknown) {
  const catalog = record(value);
  const entries = records(catalog?.vulnerabilities);
  return new Map(
    entries
      .map((item) => [text(item.cveID).toUpperCase(), item] as const)
      .filter(([id]) => /^CVE-\d{4}-\d{4,}$/.test(id)),
  );
}

function nvdVulnerabilities(value: unknown, cisaMap: Map<string, JsonRecord>) {
  const payload = record(value);
  return records(payload?.vulnerabilities)
    .map((wrapper) => record(wrapper.cve))
    .filter((cve): cve is JsonRecord => cve !== null)
    .map((cve): Vulnerability | null => {
      const id = text(cve.id).toUpperCase();
      if (!/^CVE-\d{4}-\d{4,}$/.test(id)) return null;
      const cisa = cisaMap.get(id);
      const metric = metricFor(cve);
      const ransomware = /^known$/i.test(
        text(cisa?.knownRansomwareCampaignUse),
      );
      const title = text(
        cisa?.vulnerabilityName,
        `${id} · official vulnerability record`,
      );
      const reasons = [
        cisa ? "CISA KEV" : "Official NVD record",
        metric.score === null ? "CVSS pending" : `CVSS ${metric.score.toFixed(1)}`,
        ransomware ? "Known ransomware use" : "",
      ].filter(Boolean);
      const item: Vulnerability = {
        id,
        title,
        summary: text(cisa?.shortDescription, englishDescription(cve)),
        priorityScore: 0,
        cvssScore: metric.score,
        cvssVersion: metric.version,
        cvssVector: metric.vector,
        severity: metric.severity,
        epssScore: null,
        epssPercentile: null,
        cisaKev: Boolean(cisa),
        knownExploited: Boolean(cisa),
        knownRansomwareUse: ransomware,
        sourceName: "NVD API 2.0",
        sourceUrl: `https://nvd.nist.gov/vuln/detail/${id}`,
        publishedAt: safeDate(cve.published, new Date().toISOString()),
        products: cisa
          ? [text(cisa.vendorProject), text(cisa.product)].filter(Boolean)
          : [],
        references: referencesFor(cve),
        reasons,
        actions: [
          text(
            cisa?.requiredAction,
            "Verify exposure, review the vendor advisory and prioritize remediation according to business impact.",
          ),
        ],
      };
      item.priorityScore = initialPriority(item);
      return item;
    })
    .filter((item): item is Vulnerability => item !== null);
}

function latestCisaOnly(
  cisaMap: Map<string, JsonRecord>,
  existing: Set<string>,
) {
  return [...cisaMap.entries()]
    .filter(([id]) => !existing.has(id))
    .sort(
      ([, a], [, b]) =>
        Date.parse(text(b.dateAdded)) - Date.parse(text(a.dateAdded)),
    )
    .slice(0, 24)
    .map(([id, cisa]): Vulnerability => {
      const ransomware = /^known$/i.test(
        text(cisa.knownRansomwareCampaignUse),
      );
      const item: Vulnerability = {
        id,
        title: text(cisa.vulnerabilityName, `${id} · CISA KEV`),
        summary: text(
          cisa.shortDescription,
          "CISA lists this vulnerability as known to be exploited.",
        ),
        priorityScore: 0,
        cvssScore: null,
        cvssVersion: null,
        cvssVector: null,
        severity: "UNKNOWN",
        epssScore: null,
        epssPercentile: null,
        cisaKev: true,
        knownExploited: true,
        knownRansomwareUse: ransomware,
        sourceName: "CISA KEV JSON",
        sourceUrl: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        publishedAt: safeDate(cisa.dateAdded, new Date().toISOString()),
        products: [text(cisa.vendorProject), text(cisa.product)].filter(Boolean),
        references: [],
        reasons: [
          "CISA KEV",
          "Known exploitation",
          ransomware ? "Known ransomware use" : "",
        ].filter(Boolean),
        actions: [
          text(
            cisa.requiredAction,
            "Follow CISA and vendor remediation guidance for this known exploited vulnerability.",
          ),
        ],
      };
      item.priorityScore = initialPriority(item);
      return item;
    });
}

async function enrichWithEpss(items: Vulnerability[]) {
  const candidates = items
    .filter((item) => /^CVE-\d{4}-\d{4,}$/.test(item.id))
    .slice(0, EPSS_BATCH_SIZE);
  if (!candidates.length) {
    return { durationMs: 0, count: 0, ok: false };
  }
  const url = new URL(EPSS_API_URL);
  url.searchParams.set("cve", candidates.map((item) => item.id).join(","));
  const response = await fetchJson<unknown>(url.toString());
  const payload = record(response.data);
  const scores = new Map(
    records(payload?.data).map((item) => [text(item.cve).toUpperCase(), item]),
  );
  for (const item of candidates) {
    const score = scores.get(item.id);
    if (!score) continue;
    item.epssScore = numeric(score.epss);
    item.epssPercentile = numeric(score.percentile);
    item.priorityScore = initialPriority(item);
    if (item.epssScore !== null) item.reasons.push("FIRST EPSS");
  }
  return {
    durationMs: response.durationMs,
    count: scores.size,
    ok: response.data !== null,
  };
}

async function fetchOfficialBackup(): Promise<OfficialBackupResult | null> {
  const now = Date.now();
  const coverageStart = new Date(now - NVD_WINDOW_MS);
  const nvdUrl = new URL(NVD_API_URL);
  nvdUrl.searchParams.set("pubStartDate", coverageStart.toISOString());
  nvdUrl.searchParams.set("pubEndDate", new Date(now).toISOString());
  nvdUrl.searchParams.set("resultsPerPage", "2000");

  const [nvd, cisa] = await Promise.all([
    fetchJson<unknown>(nvdUrl.toString()),
    fetchJson<unknown>(CISA_KEV_URL),
  ]);
  if (nvd.data === null && cisa.data === null) return null;

  const cisaMap = cisaMapFrom(cisa.data);
  const items = nvdVulnerabilities(nvd.data, cisaMap);
  const existing = new Set(items.map((item) => item.id));
  items.push(...latestCisaOnly(cisaMap, existing));
  items.sort(
    (a, b) =>
      b.priorityScore - a.priorityScore ||
      Date.parse(b.publishedAt) - Date.parse(a.publishedAt),
  );
  const epss = await enrichWithEpss(items);
  items.sort(
    (a, b) =>
      b.priorityScore - a.priorityScore ||
      Date.parse(b.publishedAt) - Date.parse(a.publishedAt),
  );

  const generatedAt = new Date(now).toISOString();
  return {
    generatedAt,
    coverageStart: coverageStart.toISOString(),
    coverageEnd: generatedAt,
    vulnerabilities: items.slice(0, 160),
    sourceHealth: [
      {
        source: "official_nvd_backup",
        label: "NVD API 2.0",
        status: nvd.data === null ? "failed" : "healthy",
        required: true,
        durationMs: nvd.durationMs,
        itemsReceived: records(record(nvd.data)?.vulnerabilities).length,
        itemsAccepted: items.filter((item) => item.sourceName === "NVD API 2.0").length,
        itemsRejected: 0,
        finishedAt: generatedAt,
        error: nvd.data === null ? "Official API unavailable" : null,
      },
      {
        source: "official_cisa_backup",
        label: "CISA KEV JSON",
        status: cisa.data === null ? "failed" : "healthy",
        required: true,
        durationMs: cisa.durationMs,
        itemsReceived: cisaMap.size,
        itemsAccepted: items.filter((item) => item.cisaKev).length,
        itemsRejected: 0,
        finishedAt: generatedAt,
        error: cisa.data === null ? "Official feed unavailable" : null,
      },
      {
        source: "official_epss_backup",
        label: "FIRST EPSS API",
        status: epss.ok ? "healthy" : "degraded",
        required: false,
        durationMs: epss.durationMs,
        itemsReceived: epss.count,
        itemsAccepted: epss.count,
        itemsRejected: 0,
        finishedAt: generatedAt,
        error: epss.ok ? null : "Optional enrichment unavailable",
      },
    ],
  };
}

export async function getOfficialBackup() {
  const now = Date.now();
  if (officialCache && officialCache.expiresAt > now) return officialCache.result;
  if (!officialInFlight) {
    officialInFlight = fetchOfficialBackup()
      .then((result) => {
        officialCache = {
          result,
          expiresAt:
            Date.now() +
            (result ? OFFICIAL_CACHE_TTL_MS : NEGATIVE_CACHE_TTL_MS),
        };
        return result;
      })
      .finally(() => {
        officialInFlight = null;
      });
  }
  return officialInFlight;
}
