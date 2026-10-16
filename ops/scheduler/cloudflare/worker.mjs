// Independent wake-up for the existing GitHub publishing workflow.
// No public write API, no report generation and no secrets in source.
const REPO = 'JimBLogic/CyberDailyLog';
const API = `https://api.github.com/repos/${REPO}`;
const ACTIVE = new Set(['queued', 'waiting', 'pending', 'requested', 'in_progress']);
const VALID_PUBLICATIONS = new Set(['on_time', 'delayed', 'stale']);

function madridClock(now) {
  const fields = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit',
    day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(now);
  return Object.fromEntries(fields.filter(p => p.type !== 'literal').map(p => [p.type, Number(p.value)]));
}

export function planWakeup(now, timing, runs) {
  const local = madridClock(now);
  if (local.hour !== 12) return { action: 'skip', reason: 'outside Madrid noon recovery hour' };
  const today = `${local.year}-${String(local.month).padStart(2, '0')}-${String(local.day).padStart(2, '0')}`;
  // Noon is exactly this many local minutes/seconds before a time in hour 12.
  // Calculating from the local clock avoids hardcoded +01/+02 UTC offsets.
  const noon = new Date(now.getTime() - (local.minute * 60 + local.second) * 1000 - now.getUTCMilliseconds());
  const published = Date.parse(timing?.actual_publication_time);
  if (
    timing?.schema_version === 2 &&
    VALID_PUBLICATIONS.has(timing.status) &&
    Number.isFinite(published) &&
    published >= noon.getTime() &&
    published <= now.getTime() + 30_000
  ) return { action: 'skip', reason: 'measured daily publication already completed', today };

  if (!Array.isArray(runs)) throw new Error('Workflow run inventory unavailable');
  if (runs.some(run =>
    run.name === 'Daily Blue Team Intelligence' &&
    run.head_branch === 'main' &&
    ACTIVE.has(run.status) &&
    Date.parse(run.created_at) >= noon.getTime() &&
    Date.parse(run.created_at) <= now.getTime() + 30_000
  )) return { action: 'skip', reason: 'today\'s workflow already running', today };
  return { action: 'dispatch', reason: 'today\'s publication not confirmed', today, target: noon.toISOString() };
}

async function github(path, env, options = {}) {
  const token = env?.GITHUB_ACTIONS_TOKEN;
  if (typeof token !== 'string' || !token.trim()) throw new Error('Missing scoped GITHUB_ACTIONS_TOKEN secret');
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: options.raw ? 'application/vnd.github.raw+json' : 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'cyberdailylog-independent-wakeup',
      ...(options.body ? {'Content-Type': 'application/json'} : {}),
    },
    redirect: 'manual',
    signal: AbortSignal.timeout(15000),
  });
  if (response.status >= 300 && response.status < 400) {
    await response.body?.cancel();
    throw new Error('GitHub unexpectedly redirected the authenticated request');
  }
  return response;
}

export async function performWakeup(env, now = new Date()) {
  if (madridClock(now).hour !== 12) return { action: 'skip', reason: 'outside Madrid noon recovery hour' };
  const timingReply = await github('/contents/reports/publication-timing.json?ref=main', env, {raw:true});
  if (!timingReply.ok) throw new Error(`GitHub publication evidence read HTTP ${timingReply.status}`);
  const timingPayload = await timingReply.json();
  // GitHub can serve the Contents endpoint as raw JSON or the standard
  // base64 content envelope depending on media negotiation/proxy behavior.
  const timing = timingPayload?.encoding === 'base64' && typeof timingPayload.content === 'string'
    ? JSON.parse(new TextDecoder().decode(Uint8Array.from(
        atob(timingPayload.content.replace(/\s+/g, '')), char => char.charCodeAt(0),
      )))
    : timingPayload;
  if (timing?.schema_version !== 2) throw new Error('Invalid/missing publication timing evidence');
  const runsReply = await github('/actions/runs?branch=main&per_page=30', env);
  if (!runsReply.ok) throw new Error(`GitHub runs read HTTP ${runsReply.status}`);
  const inventory = await runsReply.json();
  const plan = planWakeup(now, timing, inventory.workflow_runs);
  if (plan.action !== 'dispatch') return plan;
  // Only workflow_dispatch: this token needs Actions:write and cannot modify source.
  const requestedAt = now.toISOString();
  const response = await github('/actions/workflows/daily-intelligence.yml/dispatches', env, {
    method:'POST',
    body:JSON.stringify({ref:'main',inputs:{
      dry_run:false, lookback_hours:'24',trigger_origin:'external',dispatch_requested_at:requestedAt,
    }}),
  });
  if (response.status !== 204) throw new Error(`GitHub dispatch HTTP ${response.status}`);
  return { action:'accepted', today:plan.today, scheduled_for:plan.target, requested_at:requestedAt };
}

export default {
  // Workers without HTTP endpoints cannot be directly used as public writers.
  async fetch() { return new Response('Not found', {status:404}); },
  async scheduled(controller, env, context) {
    // The nominal scheduledTime can precede delayed actual execution by minutes.
    // Only the real wall clock is valid for SLO provenance and noon gating.
    const now = new Date();
    const job = performWakeup(env, now).then(result => {
      console.log(JSON.stringify({service:'cyberdailylog-wakeup', ...result}));
    }).catch(error => {
      console.error(JSON.stringify({service:'cyberdailylog-wakeup',status:'failed',
        reason: error instanceof Error ? error.message : 'unknown scheduler error'}));
      throw error;
    });
    context.waitUntil(job);
  },
};
