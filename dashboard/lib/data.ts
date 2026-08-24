import { FALLBACK_DATA } from "./fallback-data";
import { getOfficialBackup } from "./official-backup";
import { SOURCE_LABELS, sourceExpectedIntervalMs } from "./source-labels";
import type {
  AnalystItem,
  CommunityItem,
  CommunitySignal,
  ContextItem,
  DashboardData,
  DashboardFeed,
  DeliveryAttempt,
  DistributionPoint,
  HistoryPoint,
  ScoreBand,
  Severity,
  SourceHealth,
  Vulnerability,
} from "./types";

const RAW_BASE =
  "https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main";
const CDN_BASE =
  "https://cdn.jsdelivr.net/gh/JimBLogic/CyberDailyLog@main";
const REPOSITORY_URL = "https://github.com/JimBLogic/CyberDailyLog";
const REPORT_URL = `${REPOSITORY_URL}/blob/main/reports/latest.md`;
const FETCH_TIMEOUT_MS = 4_500;
const DATA_CACHE_TTL_MS = 15 * 60 * 1_000;
const MAX_REPOSITORY_AGE_MS = 36 * 60 * 60 * 1_000;
const MIN_VALID_TIMESTAMP = Date.UTC(2000, 0, 1);

let cachedSnapshot: { data: DashboardData; expiresAt: number } | null = null;
let refreshInFlight: Promise<DashboardData> | null = null;

type CircuitState = {
  failures: number;
  cooldownUntil: number;
  lastReason: string;
};

const endpointCircuits = new Map<string, CircuitState>();

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

function dateValue(value: unknown, fallback = "") {
  const candidate = stringValue(value);
  const parsed = Date.parse(candidate);
  return Number.isFinite(parsed) && parsed >= MIN_VALID_TIMESTAMP
    ? new Date(parsed).toISOString()
    : fallback;
}

function boundedPlainText(value: unknown, fallback: string, limit: number) {
  const source = stringValue(value, fallback)
    .replace(/```[\s\S]*?```/g, " [Code sample omitted in dashboard] ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*|__|\*|_/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return source.length > limit
    ? `${source.slice(0, Math.max(0, limit - 1)).trimEnd()}…`
    : source;
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
    summary: boundedPlainText(
      item.summary,
      "Open the primary source for the complete technical description.",
      1_200,
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
    publishedAt: dateValue(item.published_at),
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
    finishedAt: dateValue(entry.finished_at),
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

function distributionForVulnerabilities(
  items: Vulnerability[],
): DistributionPoint[] {
  const counts: Record<Severity, number> = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
    UNKNOWN: 0,
  };
  for (const item of items) counts[item.severity] += 1;
  return [
    { key: "CRITICAL", label: "Critical", count: counts.CRITICAL, color: "#c9342f" },
    { key: "HIGH", label: "High", count: counts.HIGH, color: "#f27622" },
    { key: "MEDIUM", label: "Medium", count: counts.MEDIUM, color: "#e7ad24" },
    { key: "LOW", label: "Low", count: counts.LOW, color: "#1747d1" },
    { key: "UNKNOWN", label: "Unknown", count: counts.UNKNOWN, color: "#8b8d91" },
  ];
}

function scoreBandsForVulnerabilities(items: Vulnerability[]): ScoreBand[] {
  const bands = [
    { label: "0–2.4", from: 0, to: 2.4 },
    { label: "2.5–4.9", from: 2.5, to: 4.9 },
    { label: "5–7.4", from: 5, to: 7.4 },
    { label: "7.5–8.9", from: 7.5, to: 8.9 },
    { label: "9–10", from: 9, to: 10 },
  ];
  return bands.map((band) => ({
    ...band,
    count: items.filter(
      (item) =>
        item.priorityScore >= band.from && item.priorityScore <= band.to,
    ).length,
  }));
}

function attentionItem(item: Vulnerability) {
  return item.cisaKev || item.knownExploited || item.knownRansomwareUse;
}

function normalizeHumanContext(value: unknown): ContextItem {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const item = value as RawRecord;
  return {
    title: stringValue(item.title, "Untitled analyst context"),
    sourceName: stringValue(item.source_name, "Unknown publisher"),
    author: stringValue(item.author) || null,
    excerpt: boundedPlainText(
      item.excerpt,
      stringValue(item.summary),
      520,
    ),
    sourceUrl: stringValue(item.source_url),
    publishedAt: dateValue(item.published_at),
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
    publishedAt: dateValue(item.published_at),
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

const REPOSITORY_TRANSPORTS = [
  {
    id: "github-raw" as const,
    label: "GitHub Raw",
    role: "primary" as const,
    base: RAW_BASE,
  },
  {
    id: "jsdelivr-cdn" as const,
    label: "jsDelivr CDN",
    role: "transport-backup" as const,
    base: CDN_BASE,
  },
];

function retryAfterMs(value: string | null) {
  if (!value) return null;
  const seconds = Number(value);
  if (Number.isFinite(seconds) && seconds >= 0) return seconds * 1_000;
  const date = Date.parse(value);
  return Number.isFinite(date) ? Math.max(0, date - Date.now()) : null;
}

function recordEndpointFailure(
  key: string,
  reason: string,
  requestedDelay: number | null = null,
) {
  const failures = (endpointCircuits.get(key)?.failures ?? 0) + 1;
  const cooldownMs = Math.min(
    15 * 60_000,
    Math.max(requestedDelay ?? 0, 30_000 * 2 ** (failures - 1)),
  );
  const state = {
    failures,
    cooldownUntil: Date.now() + cooldownMs,
    lastReason: reason,
  };
  endpointCircuits.set(key, state);
  return state;
}

function endpointFailureReason(error: unknown) {
  return error instanceof DOMException &&
    ["AbortError", "TimeoutError"].includes(error.name)
    ? "Request timed out"
    : "Network request failed";
}

async function fetchJson<T>(path: string) {
  const attempts: DeliveryAttempt[] = [];
  for (const transport of REPOSITORY_TRANSPORTS) {
    const url = `${transport.base}/${path}`;
    const circuitKey = `${transport.id}:${path}`;
    const circuit = endpointCircuits.get(circuitKey);
    if (circuit && circuit.cooldownUntil > Date.now()) {
      attempts.push({
        id: transport.id,
        label: transport.label,
        role: transport.role,
        status: "cooldown",
        url,
        reason: circuit.lastReason,
        retryAt: new Date(circuit.cooldownUntil).toISOString(),
      });
      continue;
    }
    try {
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
      });
      if (response.ok) {
        endpointCircuits.delete(circuitKey);
        attempts.push({
          id: transport.id,
          label: transport.label,
          role: transport.role,
          status: "used",
          url,
          reason: null,
          retryAt: null,
        });
        for (const skipped of REPOSITORY_TRANSPORTS.slice(attempts.length)) {
          attempts.push({
            id: skipped.id,
            label: skipped.label,
            role: skipped.role,
            status: "skipped",
            url: `${skipped.base}/${path}`,
            reason: "An earlier repository route succeeded",
            retryAt: null,
          });
        }
        return {
          data: (await response.json()) as T,
          transport: transport.id,
          attempts,
        };
      }
      const reason = `HTTP ${response.status}`;
      const state = recordEndpointFailure(
        circuitKey,
        reason,
        retryAfterMs(response.headers.get("retry-after")),
      );
      attempts.push({
        id: transport.id,
        label: transport.label,
        role: transport.role,
        status: "failed",
        url,
        reason,
        retryAt: new Date(state.cooldownUntil).toISOString(),
      });
      continue;
    } catch (error) {
      const reason = endpointFailureReason(error);
      const state = recordEndpointFailure(circuitKey, reason);
      attempts.push({
        id: transport.id,
        label: transport.label,
        role: transport.role,
        status: "failed",
        url,
        reason,
        retryAt: new Date(state.cooldownUntil).toISOString(),
      });
    }
  }
  return { data: null as T | null, transport: null, attempts };
}

function assessCoverage(
  sourceHealth: SourceHealth[],
  dataMode: DashboardData["dataMode"],
) {
  const now = Date.now();
  const core = sourceHealth.filter((source) => source.required);
  const currentCore = core.filter((source) => {
    const finishedAt = Date.parse(source.finishedAt);
    return (
      source.status === "healthy" &&
      Number.isFinite(finishedAt) &&
      now - finishedAt <= sourceExpectedIntervalMs(source.source) * 2
    );
  }).length;

  if (dataMode === "live" && core.length > 0 && currentCore === core.length) {
    return { coverageConfidence: "high", coverageState: "sufficient" } as const;
  }
  if (dataMode !== "repository-snapshot" && currentCore > 0) {
    return { coverageConfidence: "medium", coverageState: "limited" } as const;
  }
  return { coverageConfidence: "low", coverageState: "insufficient" } as const;
}

function completionChain(
  attempts: DeliveryAttempt[],
  officialStatus: DeliveryAttempt["status"],
  snapshotStatus: DeliveryAttempt["status"],
) {
  return [
    ...attempts,
    {
      id: "official-apis" as const,
      label: "NVD + CISA KEV + FIRST EPSS",
      role: "official-backup" as const,
      status: officialStatus,
      url: "https://nvd.nist.gov/developers/vulnerabilities",
    },
    {
      id: "bundled-snapshot" as const,
      label: "Copia verificada incluida",
      role: "offline-fallback" as const,
      status: snapshotStatus,
      url: REPOSITORY_URL,
    },
  ];
}

function cloneFallback(): DashboardData {
  return JSON.parse(JSON.stringify(FALLBACK_DATA)) as DashboardData;
}

async function fetchDashboardData(): Promise<DashboardData> {
  const reportResult = await fetchJson<RawReport>("reports/latest.json");
  const report = reportResult.data;
  const generatedAt = dateValue(report?.generated_at);
  const reportIsStale =
    !generatedAt || Date.now() - Date.parse(generatedAt) > MAX_REPOSITORY_AGE_MS;

  if (!report || !Array.isArray(report.items) || reportIsStale) {
    const official = await getOfficialBackup();
    if (official?.vulnerabilities.length) {
      const fetchedAt = Date.now();
      const items = official.vulnerabilities;
      const coverage = assessCoverage(official.sourceHealth, "official-backup");
      const immediateItems = items.filter(
        (item) =>
          item.cisaKev || item.knownExploited || item.knownRansomwareUse,
      );
      return {
        schemaVersion: 1,
        project: "CyberDailyLog",
        generatedAt: official.generatedAt,
        coverageStart: official.coverageStart,
        coverageEnd: official.coverageEnd,
        pipelineStatus: "degraded",
        dataMode: "official-backup",
        deliveryOrigin: "official-apis",
        deliveryChain: completionChain(
          reportResult.attempts.map((attempt) => ({
            ...attempt,
            status: attempt.status === "used" ? "available" : attempt.status,
          })),
          "used",
          "skipped",
        ),
        ...coverage,
        minimumPriority: 5,
        assessed: items.length,
        aboveThreshold: items.filter(
          (item) => item.priorityScore >= 5 || attentionItem(item),
        ).length,
        immediateAttentionCount: immediateItems.length,
        immediateAttention: immediateItems.length
          ? `${immediateItems.length} item(s) are backed by CISA KEV or exploitation signals.`
          : "No CISA KEV or exploitation signal was available in the official backup window.",
        distribution: distributionForVulnerabilities(items),
        scoreBands: scoreBandsForVulnerabilities(items),
        vulnerabilities: items.slice(0, 80),
        sourceHealth: official.sourceHealth,
        history: [],
        humanContext: null,
        communityPulse: null,
        analystBriefs: [],
        communitySignals: [],
        repositoryUrl: REPOSITORY_URL,
        reportUrl: REPORT_URL,
        lastFetchAt: new Date(fetchedAt).toISOString(),
        nextRefreshAt: new Date(fetchedAt + DATA_CACHE_TTL_MS).toISOString(),
        refreshIntervalMinutes: DATA_CACHE_TTL_MS / 60_000,
      };
    }
  }

  if (!report || !Array.isArray(report.items)) {
    const fallback = cloneFallback();
    const fetchedAt = Date.now();
    fallback.lastFetchAt = new Date(fetchedAt).toISOString();
    fallback.nextRefreshAt = new Date(fetchedAt + DATA_CACHE_TTL_MS).toISOString();
    fallback.refreshIntervalMinutes = DATA_CACHE_TTL_MS / 60_000;
    fallback.deliveryOrigin = "bundled-snapshot";
    fallback.deliveryChain = completionChain(
      reportResult.attempts,
      "failed",
      "used",
    );
    return fallback;
  }

  const [compactResult, healthResult, feedResult] = await Promise.all([
    fetchJson<RawCompactFeed>("reports/portfolio-feed.json"),
    fetchJson<unknown>("reports/source-health.json"),
    fetchJson<DashboardFeed>("reports/dashboard-feed.json"),
  ]);
  const compact = compactResult.data;
  const separateHealth = healthResult.data;
  const dashboardFeed = feedResult.data;

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
  const resolvedGeneratedAt = dateValue(
    report.generated_at,
    FALLBACK_DATA.generatedAt,
  );
  const currentPoint: HistoryPoint = {
    date: resolvedGeneratedAt.slice(0, 10),
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

  const fetchedAt = Date.now();
  const coverage = assessCoverage(sourceHealth, "live");

  return {
    schemaVersion: 1,
    project: "CyberDailyLog",
    generatedAt: resolvedGeneratedAt,
    coverageStart: dateValue(
      report.coverage_start,
      FALLBACK_DATA.coverageStart,
    ),
    coverageEnd: dateValue(report.coverage_end, FALLBACK_DATA.coverageEnd),
    pipelineStatus: booleanValue(report.degraded)
      ? "degraded"
      : "operational",
    dataMode: "live",
    deliveryOrigin: reportResult.transport ?? "github-raw",
    deliveryChain: completionChain(
      reportResult.attempts,
      reportIsStale ? "failed" : "skipped",
      "skipped",
    ),
    ...coverage,
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
    lastFetchAt: new Date(fetchedAt).toISOString(),
    nextRefreshAt: new Date(fetchedAt + DATA_CACHE_TTL_MS).toISOString(),
    refreshIntervalMinutes: DATA_CACHE_TTL_MS / 60_000,
  };
}

export async function getDashboardData(): Promise<DashboardData> {
  const now = Date.now();
  if (cachedSnapshot && cachedSnapshot.expiresAt > now) {
    return cachedSnapshot.data;
  }

  if (!refreshInFlight) {
    refreshInFlight = fetchDashboardData()
      .then((data) => {
        cachedSnapshot = {
          data,
          expiresAt: Date.parse(data.nextRefreshAt),
        };
        return data;
      })
      .finally(() => {
        refreshInFlight = null;
      });
  }

  return refreshInFlight;
}
