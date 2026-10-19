// Reconciled from PR43 against PR47. This Worker only wakes the existing workflow.
const REPO = 'JimBLogic/CyberDailyLog';
const API = `https://api.github.com/repos/${REPO}`;
const TIMING = `https://raw.githubusercontent.com/${REPO}/main/reports/publication-timing.json`;
const WORKFLOW = 'daily-intelligence.yml';
const ACTIVE = ['in_progress', 'queued', 'waiting', 'pending', 'requested'];
const PUBLISHED = new Set(['on_time', 'delayed', 'stale']);
const MAX_JSON = 512 * 1024;

class WakeupError extends Error {
  constructor(code) { super(code); this.code = code; }
}

function clock(now) {
  if (!(now instanceof Date) || !Number.isFinite(now.getTime())) throw new WakeupError('invalid_clock');
  const fields = new Intl.DateTimeFormat('en-GB', {
    timeZone:'Europe/Madrid', year:'numeric', month:'2-digit', day:'2-digit',
    hour:'2-digit', minute:'2-digit', second:'2-digit', hourCycle:'h23',
  }).formatToParts(now);
  return Object.fromEntries(fields.filter(p => p.type !== 'literal').map(p => [p.type, Number(p.value)]));
}

function stamp(value) {
  if (value === null || value === undefined) return null;
  if (typeof value !== 'string' || !/(Z|[+-]\d{2}:\d{2})$/.test(value) || !Number.isFinite(Date.parse(value))) {
    throw new WakeupError('invalid_evidence_timestamp');
  }
  return Date.parse(value);
}

export function planWakeup(now, timing, runs = []) {
  const local = clock(now);
  if (local.hour !== 12) return {action:'skip', reason:'outside_madrid_recovery_hour'};
  if (timing?.schema_version !== 2 || !['on_time','delayed','stale','failed','unknown','skipped'].includes(timing.status)
      || ![true, false, null, undefined].includes(timing.core_complete)) throw new WakeupError('invalid_timing_evidence');
  const noon = now.getTime() - (local.minute * 60 + local.second) * 1000 - now.getUTCMilliseconds();
  const today = `${local.year}-${String(local.month).padStart(2,'0')}-${String(local.day).padStart(2,'0')}`;
  const published = stamp(timing.actual_publication_time), generated = stamp(timing.report_generated);
  if (timing.core_complete === true && PUBLISHED.has(timing.status) && published !== null && generated !== null
      && generated >= noon && generated <= published && published <= now.getTime() + 30_000) {
    return {action:'skip', reason:'complete_daily_close_confirmed', today};
  }
  if (!Array.isArray(runs)) throw new WakeupError('invalid_run_inventory');
  if (runs.some(run => ACTIVE.includes(run.status) && run.head_branch === 'main')) {
    return {action:'skip', reason:'workflow_already_active', today};
  }
  return {action:'dispatch', reason:'complete_daily_close_not_confirmed', today, target:new Date(noon).toISOString()};
}

async function jsonBody(response) {
  if (Number(response.headers.get('Content-Length')) > MAX_JSON) {
    await response.body?.cancel(); throw new WakeupError('response_too_large');
  }
  const reader = response.body?.getReader();
  if (!reader) throw new WakeupError('empty_json_response');
  const chunks = []; let size = 0;
  try {
    for (;;) {
      const {done, value} = await reader.read();
      if (done) break;
      size += value.length;
      if (size > MAX_JSON) throw new WakeupError('response_too_large');
      chunks.push(value);
    }
    const joined = new Uint8Array(size); let offset = 0;
    for (const chunk of chunks) { joined.set(chunk, offset); offset += chunk.length; }
    try { return JSON.parse(new TextDecoder().decode(joined)); }
    catch { throw new WakeupError('invalid_json_response'); }
  } finally { await reader.cancel().catch(() => {}); }
}

async function request(url, env, body) {
  const headers = {'Accept':'application/vnd.github+json', 'User-Agent':'cyberdailylog-independent-wakeup'};
  if (url.startsWith(API + '/')) {
    const token = env?.GITHUB_ACTIONS_TOKEN;
    if (typeof token !== 'string' || !token || token !== token.trim() || /[\s\u0000-\u001f\u007f]/.test(token)
        || token.length > 4096) throw new WakeupError('missing_or_invalid_dispatch_secret');
    headers.Authorization = `Bearer ${token}`;
    headers['X-GitHub-Api-Version'] = '2026-03-10';
  } else if (url !== TIMING) throw new WakeupError('unapproved_origin');
  if (body) headers['Content-Type'] = 'application/json';
  let response;
  try {
    response = await fetch(url, {method:body ? 'POST':'GET', headers, body:body ? JSON.stringify(body):undefined,
      redirect:'manual', signal:AbortSignal.timeout(15000)});
  } catch { throw new WakeupError('transport_unavailable'); }
  if (response.status >= 300 && response.status < 400) {
    await response.body?.cancel(); throw new WakeupError('authenticated_redirect_rejected');
  }
  if (!response.ok) {
    await response.body?.cancel(); throw new WakeupError(`upstream_http_${response.status}`);
  }
  return response;
}

async function activeRuns(env) {
  const inventories = await Promise.all(ACTIVE.map(async status => {
    const reply = await request(`${API}/actions/workflows/${WORKFLOW}/runs?branch=main&status=${status}&per_page=1`, env);
    const data = await jsonBody(reply), runs = data?.workflow_runs;
    if (!Number.isSafeInteger(data?.total_count) || data.total_count < 0 || !Array.isArray(runs) || runs.length > 1
        || (data.total_count > 0) !== (runs.length > 0)) throw new WakeupError('invalid_run_inventory');
    for (const run of runs) {
      if (!Number.isSafeInteger(run.id) || run.id < 1 || run.head_branch !== 'main' || run.status !== status
          || run.path !== '.github/workflows/daily-intelligence.yml') throw new WakeupError('invalid_run_inventory');
    }
    return runs;
  }));
  return inventories.flat();
}

export async function performWakeup(env, now = new Date()) {
  if (clock(now).hour !== 12) return {action:'skip', reason:'outside_madrid_recovery_hour'};
  // This public read sends NO token and needs NO Contents permission.
  const timing = await jsonBody(await request(TIMING, env));
  let plan = planWakeup(now, timing);
  if (plan.action !== 'dispatch') return plan;
  plan = planWakeup(now, timing, await activeRuns(env));
  if (plan.action !== 'dispatch') return plan;
  // Do not retry an ambiguous POST: next cron reconciles runs before dispatch.
  const requestedAt = now.toISOString();
  const reply = await request(`${API}/actions/workflows/${WORKFLOW}/dispatches`, env, {
    ref:'main', inputs:{dry_run:false,lookback_hours:'24',trigger_origin:'external',dispatch_requested_at:requestedAt},
  });
  if (reply.status !== 200) { await reply.body?.cancel(); throw new WakeupError('unexpected_dispatch_response'); }
  const accepted = await jsonBody(reply), id = accepted?.workflow_run_id;
  if (!Number.isSafeInteger(id) || id < 1 || accepted.run_url !== `${API}/actions/runs/${id}`
      || accepted.html_url !== `https://github.com/${REPO}/actions/runs/${id}`) {
    throw new WakeupError('invalid_dispatch_receipt');
  }
  return {action:'accepted',today:plan.today,scheduled_for:plan.target,requested_at:requestedAt,
    run_id:id,run_url:accepted.html_url};
}

export default {
  async fetch() { return new Response('Not found',{status:404}); },
  async scheduled(controller, env, context) {
    const now = new Date();
    const nominal = new Date(controller.scheduledTime);
    const provenance = {service:'cyberdailylog-wakeup', invocation:'scheduled',
      observed_at:now.toISOString(), nominal_scheduled_at:Number.isFinite(nominal.getTime()) ? nominal.toISOString():null};
    const job = performWakeup(env, now).then(result => console.log(JSON.stringify({...provenance,...result})))
      .catch(error => {
        console.error(JSON.stringify({...provenance,status:'failed',
          reason:error instanceof WakeupError ? error.code:'scheduler_failure'}));
        throw new WakeupError(error instanceof WakeupError ? error.code:'scheduler_failure');
      });
    context.waitUntil(job);
  },
};
