export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";

export type Vulnerability = {
  id: string;
  title: string;
  summary: string;
  priorityScore: number;
  cvssScore: number | null;
  cvssVersion: string | null;
  cvssVector: string | null;
  severity: Severity;
  epssScore: number | null;
  epssPercentile: number | null;
  cisaKev: boolean;
  knownExploited: boolean;
  knownRansomwareUse: boolean;
  sourceName: string;
  sourceUrl: string;
  publishedAt: string;
  products: string[];
  references: string[];
  reasons: string[];
  actions: string[];
};

export type SourceHealth = {
  source: string;
  label: string;
  status: "healthy" | "degraded" | "failed" | "fixture_only" | "unknown";
  required: boolean;
  durationMs: number;
  itemsReceived: number;
  itemsAccepted: number;
  itemsRejected: number;
  finishedAt: string;
  error: string | null;
};

export type DeliveryAttempt = {
  id: "github-raw" | "jsdelivr-cdn" | "official-apis" | "bundled-snapshot";
  label: string;
  role: "primary" | "transport-backup" | "official-backup" | "offline-fallback";
  status: "used" | "available" | "failed" | "skipped" | "cooldown";
  url: string;
  reason?: string | null;
  retryAt?: string | null;
};

export type DistributionPoint = {
  key: Severity;
  label: string;
  count: number;
  color: string;
};

export type ScoreBand = {
  label: string;
  count: number;
  from: number;
  to: number;
};

export type HistoryPoint = {
  date: string;
  assessed: number;
  aboveThreshold: number;
  immediateAttention: number;
  critical: number;
  high: number;
  degraded: boolean;
};

export type AnalystItem = {
  title: string;
  sourceName: string;
  author: string | null;
  excerpt: string;
  sourceUrl: string;
  publishedAt: string;
};

export type ContextItem = AnalystItem | null;

export type CommunitySignal = {
  title: string;
  sourceName: string;
  sourceUrl: string;
  discussionUrl: string;
  score: number;
  comments: number;
  publishedAt: string;
  caveat: string;
};

export type CommunityItem = CommunitySignal | null;

export type DashboardData = {
  schemaVersion: 1;
  project: "CyberDailyLog";
  generatedAt: string;
  coverageStart: string;
  coverageEnd: string;
  pipelineStatus: "operational" | "degraded";
  dataMode: "live" | "official-backup" | "repository-snapshot";
  deliveryOrigin: DeliveryAttempt["id"];
  deliveryChain: DeliveryAttempt[];
  coverageConfidence: "high" | "medium" | "low";
  coverageState: "sufficient" | "limited" | "insufficient";
  minimumPriority: number;
  assessed: number;
  aboveThreshold: number;
  immediateAttentionCount: number;
  immediateAttention: string;
  distribution: DistributionPoint[];
  scoreBands: ScoreBand[];
  vulnerabilities: Vulnerability[];
  sourceHealth: SourceHealth[];
  history: HistoryPoint[];
  humanContext: ContextItem;
  communityPulse: CommunityItem;
  analystBriefs: AnalystItem[];
  communitySignals: CommunitySignal[];
  repositoryUrl: string;
  reportUrl: string;
  lastFetchAt: string;
  nextRefreshAt: string;
  refreshIntervalMinutes: number;
};

export type DashboardFeed = {
  schema_version?: number;
  history?: Array<{
    date?: string;
    generated_at?: string;
    assessed?: number;
    above_threshold?: number;
    immediate_attention?: number;
    critical?: number;
    high?: number;
    degraded?: boolean;
  }>;
};
