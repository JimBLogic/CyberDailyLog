import { FALLBACK_DATA } from "./fallback-data";
import { SOURCE_LABELS } from "./source-labels";
import type {
  AnalystItem,
  CommunityItem,
  CommunitySignal,
  ContextItem,
  DashboardData,
  DashboardFeed,
  DistributionPoint,
  HistoryPoint,
  ScoreBand,
  Severity,
  SourceHealth,
  Vulnerability,
} from "./types";

const DEFAULT_RAW_BASE =
  "https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main";
const configuredRawBase = process.env.CYBERDAILYLOG_RAW_BASE?.trim();
const RAW_BASE =
  configuredRawBase?.startsWith("https://")
    ? configuredRawBase.replace(/\/+$/, "")
    : DEFAULT_RAW_BASE;
const REPOSITORY_URL = "https://github.com/JimBLogic/CyberDailyLog";
const REPORT_URL = `${REPOSITORY_URL}/blob/main/reports/latest.md`;
const FETCH_TIMEOUT_MS = 8_000;

type RawRecord = Record<string, unknown>;

type RawReport = {
  generated_at?: unknown;
  coverage_start?: unknown;
  coverage_end?: unknown;
  degraded?: unknown;
  items?: unknown;
  source_health?: unknown;
};

type RawCompactFeed = {
  minimum_priority?: unknown;
  above_threshold?: unknown;
  immediate_attention_count?: unknown;
  immediate_attention?: unknown;
  human_context?: unknown;
  community_pulse?: unknown;
};

function stringValue(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function numberValue(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function booleanValue(value: unknown) {
  return value === true;
}

function stringArray(value: unknown) {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is string => typeof item === "string")
    .map((item) => item.trim())
    .filter(Boolean);
}

function safeSeverity(value: unknown): Severity {
  const severity = stringValue(value, "UNKNOWN").toUpperCase();
  return ["CRITICAL", "HIGH", "MEDIUM", "LOW"].includes(severity)
    ? (severity as Severity)
    : "UNKNOWN";
}

function priorityScore(item: RawRecord) {
  return Math.max(
    0,
    Math.min(
      10,
      numberValue(item.priority_score) ?? numberValue(item.cvss_score) ?? 0,
    ),
  );
}

function cleanTitle(id: string, value: unknown) {
  const title = stringValue(value, id);
  const prefix = `${id}:`;
  return title.toLowerCase().startsWith(prefix.toLowerCase())
    ? title.slice(prefix.length).trim()
    : title;
}

function normalizeVulnerability(item: RawRecord): Vulnerability {
  const cveIds = stringArray(item.cve_ids);
  const ghsaIds = stringArray(item.ghsa_ids);
  const id =
    cveIds[0] ??
    ghsaIds[0] ??
    stringValue(item.canonical_id, "unidentified-item");
  const detection = stringArray(item.detection_opportunities);
  const recommended = stringArray(item.recommended_actions);

  return {
    id,
    title: cleanTitle(id, item.title),
    summary: stringValue(
      item.summary,
      "Open the primary source for the complete technical description.",
    ),
    priorityScore: Math.round(priorityScore(item) * 10) / 10,
    cvssScore: numberValue(item.cvss_score),
    cvssVersion: stringValue(item.cvss_version) || null,
    cvssVector: stringValue(item.cvss_vector) || null,
    severity: safeSeverity(item.severity),
    epssScore: numberValue(item.epss_score),
    epssPercentile: numberValue(item.epss_percentile),
    cisaKev: booleanValue(item.cisa_kev),
    knownExploited: booleanValue(item.known_exploited),
    knownRansomwareUse: booleanValue(item.known_ransomware_use),
    sourceName: stringValue(item.source_name, "Unknown source"),
    sourceUrl: stringValue(item.source_url),
    publishedAt: stringValue(item.published_at),
    products: [
      ...stringArray(item.products),
      ...stringArray(item.ecosystems),
      ...stringArray(item.vendors),
    ].slice(0, 4),
    references: stringArray(item.references).slice(0, 6),
    reasons: (
      stringArray(item.priority_reasons).length
        ? stringArray(item.priority_reasons)
        : stringArray(item.selection_reasons)
    ).slice(0, 5),
    actions: (recommended.length ? recommended : detection).slice(0, 4),
  };
}

function normalizeSource(entry: RawRecord): SourceHealth {
  const source = stringValue(entry.source, "unknown");
  const status = stringValue(entry.status, "unknown");
  return {
    source,
    label: SOURCE_LABELS[source] ?? source.replaceAll("_", " "),
    status: ["healthy", "degraded", "failed", "fixture_only"].includes(status)
      ? (status as SourceHealth["status"])
      : "unknown",
    required: booleanValue(entry.required),
    durationMs: numberValue(entry.duration_ms) ?? 0,
    itemsReceived: numberValue(entry.items_received) ?? 0,
    itemsAccepted: numberValue(entry.items_accepted) ?? 0,
    itemsRejected: numberValue(entry.items_rejected) ?? 0,
    finishedAt: stringValue(entry.finished_at),
    error: stringValue(entry.sanitized_error_message) || null,
  };
}

function distributionFor(items: RawRecord[]): DistributionPoint[] {
  const counts: Record<Severity, number> = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
    UNKNOWN: 0,
  };
  items.forEach((item) => {
    counts[safeSeverity(item.severity)] += 1;
  });
  return [
    { key: "CRITICAL", label: "Critical", count: counts.CRITICAL, color: "#c9342f" },
    { key: "HIGH", label: "High", count: counts.HIGH, color: "#f27622" },
    { key: "MEDIUM", label: "Medium", count: counts.MEDIUM, color: "#e7ad24" },
    { key: "LOW", label: "Low", count: counts.LOW, color: "#1747d1" },
    { key: "UNKNOWN", label: "Unknown", count: counts.UNKNOWN, color: "#8b8d91" },
  ];
}

function scoreBandsFor(items: RawRecord[]): ScoreBand[] {
  const scores = items.map(priorityScore);
  const bands = [
    { label: "0–2.4", from: 0, to: 2.4 },
    { label: "2.5–4.9", from: 2.5, to: 4.9 },
    { label: "5–7.4", from: 5, to: 7.4 },
    { label: "7.5–8.9", from: 7.5, to: 8.9 },
    { label: "9–10", from: 9, to: 10 },
  ];
  return bands.map((band) => ({
    ...band,
    count: scores.filter((score) => score >= band.from && score <= band.to)
      .length,
  }));
}

function normalizeHumanContext(value: unknown): ContextItem {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const item = value as RawRecord;
  return {
    title: stringValue(item.title, "Untitled analyst context"),
    sourceName: stringValue(item.source_name, "Unknown publisher"),
    author: stringValue(item.author) || null,
    excerpt: stringValue(item.excerpt, stringValue(item.summary)),
    sourceUrl: stringValue(item.source_url),
    publishedAt: stringValue(item.published_at),
  };
}

function normalizeCommunity(value: unknown): CommunityItem {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const item = value as RawRecord;
  return {
    title: stringValue(item.title, "Untitled community signal"),
    sourceName: stringValue(item.source_name, "Community"),
    sourceUrl: stringValue(item.source_url),
    discussionUrl: stringValue(item.discussion_url, stringValue(item.source_url)),
    score: numberValue(item.score) ?? numberValue(item.community_score) ?? 0,
    comments:
      numberValue(item.comments) ?? numberValue(item.community_comments) ?? 0,
    publishedAt: stringValue(item.published_at),
    caveat: stringValue(
      item.caveat,
      "Community interest signal; validate claims against primary sources.",
    ),
  };
}

function historyFromFeed(value: DashboardFeed | null): HistoryPoint[] {
  if (!value?.history || !Array.isArray(value.history)) return [];
  return value.history
    .map((point) => ({
      date:
        stringValue(point.date) ||
        stringValue(point.generated_at).slice(0, 10),
      assessed: numberValue(point.assessed) ?? 0,
      aboveThreshold: numberValue(point.above_threshold) ?? 0,
      immediateAttention: numberValue(point.immediate_attention) ?? 0,
      critical: numberValue(point.critical) ?? 0,
      high: numberValue(point.high) ?? 0,
      degraded: booleanValue(point.degraded),
    }))
    .filter((point) => /^\d{4}-\d{2}-\d{2}$/.test(point.date))
    .slice(-30);
}

async function fetchJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${RAW_BASE}/${path}`, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

function cloneFallback(): DashboardData {
  return JSON.parse(JSON.stringify(FALLBACK_DATA)) as DashboardData;
}

export async function getDashboardData(): Promise<DashboardData> {
  const [report, compact, separateHealth, dashboardFeed] = await Promise.all([
    fetchJson<RawReport>("reports/latest.json"),
    fetchJson<RawCompactFeed>("reports/portfolio-feed.json"),
    fetchJson<unknown>("reports/source-health.json"),
    fetchJson<DashboardFeed>("reports/dashboard-feed.json"),
  ]);

  if (!report || !Array.isArray(report.items)) {
    const fallback = cloneFallback();
    fallback.lastFetchAt = new Date().toISOString();
    return fallback;
  }

  const records = report.items.filter(
    (item): item is RawRecord =>
      Boolean(item) && typeof item === "object" && !Array.isArray(item),
  );
  const securityItems = records.filter((item) =>
    ["vulnerability", "advisory"].includes(
      stringValue(item.category, "vulnerability"),
    ),
  );
  const analystBriefs = records
    .filter((item) =>
      ["expert_commentary", "analyst_diary"].includes(
        stringValue(item.category),
      ),
    )
    .map(normalizeHumanContext)
    .filter((item): item is AnalystItem => item !== null)
    .sort((a, b) => Date.parse(b.publishedAt) - Date.parse(a.publishedAt))
    .slice(0, 4);
  const communitySignals = records
    .filter((item) => stringValue(item.category) === "community_pulse")
    .map(normalizeCommunity)
    .filter((item): item is CommunitySignal => item !== null)
    .sort((a, b) => b.score - a.score || b.comments - a.comments)
    .slice(0, 4);
  const ranked = [...securityItems].sort((a, b) => {
    const attentionA =
      Number(booleanValue(a.cisa_kev)) +
      Number(booleanValue(a.known_exploited)) +
      Number(booleanValue(a.known_ransomware_use));
    const attentionB =
      Number(booleanValue(b.cisa_kev)) +
      Number(booleanValue(b.known_exploited)) +
      Number(booleanValue(b.known_ransomware_use));
    return (
      attentionB - attentionA ||
      priorityScore(b) - priorityScore(a) ||
      (numberValue(b.selection_score) ?? 0) -
        (numberValue(a.selection_score) ?? 0)
    );
  });
  const minimumPriority =
    numberValue(compact?.minimum_priority) ?? FALLBACK_DATA.minimumPriority;
  const immediateItems = securityItems.filter(
    (item) =>
      booleanValue(item.cisa_kev) ||
      booleanValue(item.known_exploited) ||
      booleanValue(item.known_ransomware_use),
  );
  const healthValue = Array.isArray(separateHealth)
    ? separateHealth
    : report.source_health;
  const sourceHealth = Array.isArray(healthValue)
    ? healthValue
        .filter(
          (entry): entry is RawRecord =>
            Boolean(entry) &&
            typeof entry === "object" &&
            !Array.isArray(entry),
        )
        .map(normalizeSource)
    : cloneFallback().sourceHealth;
  const history = historyFromFeed(dashboardFeed);
  const generatedAt = stringValue(
    report.generated_at,
    FALLBACK_DATA.generatedAt,
  );
  const currentPoint: HistoryPoint = {
    date: generatedAt.slice(0, 10),
    assessed: records.length,
    aboveThreshold: securityItems.filter(
      (item) =>
        priorityScore(item) >= minimumPriority ||
        booleanValue(item.cisa_kev) ||
        booleanValue(item.known_exploited) ||
        booleanValue(item.known_ransomware_use),
    ).length,
    immediateAttention: immediateItems.length,
    critical: securityItems.filter(
      (item) => safeSeverity(item.severity) === "CRITICAL",
    ).length,
    high: securityItems.filter(
      (item) => safeSeverity(item.severity) === "HIGH",
    ).length,
    degraded: booleanValue(report.degraded),
  };
  const resolvedHistory =
    history.length > 0
      ? [...history.filter((point) => point.date !== currentPoint.date), currentPoint]
          .sort((a, b) => a.date.localeCompare(b.date))
          .slice(-30)
      : [currentPoint];

  return {
    schemaVersion: 1,
    project: "CyberDailyLog",
    generatedAt,
    coverageStart: stringValue(
      report.coverage_start,
      FALLBACK_DATA.coverageStart,
    ),
    coverageEnd: stringValue(report.coverage_end, FALLBACK_DATA.coverageEnd),
    pipelineStatus: booleanValue(report.degraded)
      ? "degraded"
      : "operational",
    dataMode: "live",
    minimumPriority,
    assessed: records.length,
    aboveThreshold:
      numberValue(compact?.above_threshold) ?? currentPoint.aboveThreshold,
    immediateAttentionCount:
      numberValue(compact?.immediate_attention_count) ?? immediateItems.length,
    immediateAttention:
      stringValue(compact?.immediate_attention) ||
      (immediateItems.length
        ? `${immediateItems.length} item(s) include exploitation, KEV or ransomware signals.`
        : "No confirmed exploitation, CISA KEV or ransomware-linked item qualified."),
    distribution: distributionFor(securityItems),
    scoreBands: scoreBandsFor(securityItems),
    vulnerabilities: ranked.slice(0, 80).map(normalizeVulnerability),
    sourceHealth,
    history: resolvedHistory,
    humanContext:
      normalizeHumanContext(compact?.human_context) ??
      analystBriefs[0] ??
      null,
    communityPulse:
      normalizeCommunity(compact?.community_pulse) ??
      communitySignals[0] ??
      null,
    analystBriefs,
    communitySignals,
    repositoryUrl: REPOSITORY_URL,
    reportUrl: REPORT_URL,
    lastFetchAt: new Date().toISOString(),
  };
}
