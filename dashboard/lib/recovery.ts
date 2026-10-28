type Row = Record<string, unknown>;
const record = (value: unknown): Row => value && typeof value === "object" && !Array.isArray(value) ? value as Row : {};
const id = (value: unknown) => typeof value === "string" && /^\d{1,24}$/.test(value) ? value : null;
const date = (value: unknown) => {
  if (typeof value !== "string" || !/(Z|[+-]\d{2}:\d{2})$/.test(value)) return null;
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) && parsed >= Date.UTC(2000,0,1) && parsed <= Date.now() + 300000 ? new Date(parsed).toISOString() : null;
};
export function normalizeRecovery(value: unknown) {
  const raw = record(value);
  if (raw.schema_version !== 1 || !Array.isArray(raw.attempts)) return null;
  const attempts = raw.attempts.slice(-100).map(value => {
    const row = record(value), prior = record(row.recovered_from);
    const started = date(row.started_at), finished = date(row.finished_at);
    return {
      run_id: id(row.run_id), run_attempt: id(row.run_attempt),
      trigger: typeof row.trigger === "string" ? row.trigger.slice(0,80) : "unknown",
      started_at: started, finished_at: finished && (!started || finished >= started) ? finished : null,
      outcome: ["published","partial","failed","skipped"].includes(String(row.outcome)) ? String(row.outcome) : "unknown",
      recovered_from: id(prior.run_id) && id(prior.run_attempt) ? {run_id:id(prior.run_id)!,run_attempt:id(prior.run_attempt)!} : null,
      publication_id: typeof row.publication_id === "string" && /^[a-f0-9]{40}$/i.test(row.publication_id) ? row.publication_id : null,
    };
  }).filter(row => row.run_id && row.run_attempt);
  let duration: number | null = null;
  let chainStart: number | null = null;
  for (let index = 0; index < attempts.length; index++) {
    const row = attempts[index], prior = attempts[index - 1];
    const linked = Boolean(row.recovered_from && prior && ["failed","partial"].includes(prior.outcome) &&
      row.recovered_from.run_id === prior.run_id && row.recovered_from.run_attempt === prior.run_attempt &&
      prior.finished_at && row.started_at && row.started_at >= prior.finished_at && row.outcome !== "skipped");
    if (!linked) {
      row.recovered_from = null;
      if (row.outcome !== "skipped") { chainStart = null; duration = null; }
    } else {
      chainStart ??= Date.parse(prior.finished_at!);
      duration = row.outcome === "published" && row.finished_at ? (Date.parse(row.finished_at) - chainStart) / 1000 : null;
    }
  }
  return {attempts, recovery_seconds:duration, retry_count:attempts.filter(row=>row.recovered_from).length};
}
