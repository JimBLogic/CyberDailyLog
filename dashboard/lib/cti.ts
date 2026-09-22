import { safeWebUrl } from "./safe-url";

export const CHANGE_LABELS: Record<string, [string, string]> = {
  entered_cisa_kev: ["Incorporación a CISA KEV", "Added to CISA KEV"],
  exploitation_confirmed: ["Explotación confirmada", "Exploitation confirmed"],
  exploitation_status_confirmed: ["Confirmación de explotación activa", "Active exploitation confirmed"],
  ransomware_linked: ["Vínculo con ransomware", "Ransomware linked"],
  vendor_exploitation_confirmed: ["Explotación confirmada por el fabricante", "Vendor-confirmed exploitation"],
  public_exploit_published: ["Exploit público documentado", "Public exploit documented"],
  critical_asset_exposure: ["Exposición confirmada de activo crítico", "Confirmed critical asset exposure"],
  cvss_material_change: ["Cambio material de CVSS", "Material CVSS change"],
  severity_escalated: ["Aumento de severidad", "Severity increased"],
  cisa_due_date_changed: ["Cambio de plazo CISA", "CISA deadline changed"],
  required_action_changed: ["Cambio de acción requerida", "Required action changed"],
  vendor_remediation_updated: ["Corrección del fabricante actualizada", "Vendor remediation updated"],
  advisory_withdrawn: ["Aviso retirado", "Advisory withdrawn"],
};
type RecordValue = Record<string, unknown>;
const record = (value: unknown): RecordValue => value && typeof value === "object" && !Array.isArray(value) ? value as RecordValue : {};
const text = (value: unknown, length = 400) => typeof value === "string" ? value.trim().slice(0, length) : "";
const number = (value: unknown, max = 10) => typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= max ? value : null;
const date = (value: unknown, future = false) => {
  const parsed = Date.parse(text(value, 64));
  return Number.isFinite(parsed) && parsed >= Date.UTC(2000, 0, 1) && (future || parsed <= Date.now() + 300_000) ? new Date(parsed).toISOString() : null;
};
const changes = (value: unknown) => Array.isArray(value) ? [...new Set(value.filter((v): v is string => typeof v === "string" && Object.hasOwn(CHANGE_LABELS, v)))].slice(0, 16) : [];
const level = (value: unknown) => ["NORMAL", "HIGH", "EMERGENCY"].includes(String(value)) ? String(value) : null;
const snapshot = (value: unknown) => {
  const s = record(value);
  return {
    exploitation: ["unknown", "no_known_evidence", "confirmed_not_exploited", "confirmed_exploitation"].includes(String(s.exploitation_status)) ? String(s.exploitation_status) : "unknown",
    kev: s.cisa_kev === true, ransomware: s.known_ransomware_use === true,
    vendor: s.vendor_confirmed_exploitation === true, publicExploit: s.public_exploit === true,
    cvss: number(s.cvss_score), deadline: date(s.cisa_due_date, true), action: text(s.cisa_required_action),
  };
};

export function normalizeCti(value: RecordValue) {
  if (!["new_vulnerability", "state_transition"].includes(String(value.discovery_type))) return undefined;
  const history = Array.isArray(value.state_transitions) ? value.state_transitions : [];
  return {
    kind: value.discovery_type === "state_transition" ? "transition" as const : "new" as const,
    firstSeen: date(value.first_seen), lastSeen: date(value.last_seen), changedAt: date(value.state_changed_at),
    changes: changes(value.transition_type), previous: snapshot(value.previous_state), current: snapshot(value.current_state),
    priorityBefore: number(value.priority_before), priorityAfter: number(value.priority_after),
    levelBefore: level(value.priority_level_before), levelAfter: level(value.priority_level),
    history: history.slice(-8).map(raw => {
      const event = record(raw);
      return {
        at: date(event.changed_at), changes: changes(event.transition_type),
        before: number(event.priority_before), after: number(event.priority_after),
        previous: snapshot(event.previous_state), current: snapshot(event.current_state),
        sources: (Array.isArray(event.sources) ? event.sources : []).slice(0, 6).map(rawSource => {
          const source = record(rawSource);
          return { name: text(source.name, 100), url: safeWebUrl(source.url) };
        }).filter(source => source.url),
      };
    }),
    historyCount: history.length,
  };
}
export type CtiState = NonNullable<ReturnType<typeof normalizeCti>>;

export function normalizePublication(value: unknown) {
  const raw = record(value);
  if (raw.schema_version !== 2) return null;
  const statuses = ["on_time", "delayed", "stale", "failed", "unknown"];
  const stages = ["scheduler", "dispatch", "workflow_queue", "pipeline", "publication", "within_threshold", "unknown"];
  const slo = record(raw.slo);
  const evidenceUrl = (value: unknown) => {
    const url = safeWebUrl(value);
    return /^https:\/\/github\.com\/JimBLogic\/CyberDailyLog\/actions\/runs\/\d+(?:\?[^#]*)?$/.test(url) ? url : "";
  };
  const origin = (value: unknown) => ["external_push", "external", "schedule", "manual", "push", "workflow_dispatch"].includes(String(value)) ? String(value) : "unknown";
  const attempt = record(raw.last_attempt);
  return {
    status: statuses.includes(String(raw.status)) ? String(raw.status) : "unknown",
    scheduledFor: date(raw.scheduled_for), actual: date(raw.actual_publication_time),
    reportGenerated: date(raw.report_generated), lagSeconds: number(raw.publication_lag_seconds, 31_536_000),
    rootCause: stages.includes(String(raw.root_cause_stage)) ? String(raw.root_cause_stage) : "unknown",
    runUrl: evidenceUrl(raw.run_url), origin: origin(raw.trigger_origin),
    requestedAt: date(raw.dispatch_requested_at), workflowCreated: date(raw.workflow_created),
    workflowStarted: date(raw.workflow_actual_start), fetchSeconds: number(raw.fetch_duration_seconds, 86_400),
    requestLagSeconds: number(raw.scheduler_request_lag_seconds, 31_536_000),
    dispatchSeconds: number(raw.dispatch_creation_lag_seconds, 31_536_000),
    queueSeconds: number(raw.workflow_queue_seconds, 31_536_000),
    lastAttempt: Object.keys(attempt).length ? {
      status: [...statuses, "skipped"].includes(String(attempt.status)) ? String(attempt.status) : "unknown",
      origin: origin(attempt.trigger_origin), created: date(attempt.workflow_created),
      scheduledFor: date(attempt.trigger_scheduled_for),
      creationLagSeconds: number(attempt.trigger_creation_lag_seconds, 31_536_000),
      runUrl: evidenceUrl(attempt.run_url),
    } : null,
    sloPercentage: number(slo.attainment_percentage, 100), measuredDays: number(slo.measured_publications, 30),
    fullWindow: slo.full_window_observed === true, evaluatedAt: date(slo.evaluated_at),
  };
}
export type PublicationReliability = NonNullable<ReturnType<typeof normalizePublication>>;
