import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import worker, {planWakeup, performWakeup} from './worker.mjs';

const NOW = new Date('2026-10-19T10:20:03Z');
const OLD = {schema_version:2,status:'stale',core_complete:true,
  actual_publication_time:'2026-10-18T14:41:40Z',report_generated:'2026-10-18T14:40:00Z'};
const CLOSED = {...OLD,status:'on_time',actual_publication_time:'2026-10-19T10:03:00Z',
  report_generated:'2026-10-19T10:02:00Z'};
const SECRET = 'synthetic-dispatch-test-marker';
const ENV = {GITHUB_ACTIONS_TOKEN:SECRET};
const RECEIPT = {workflow_run_id:123,run_url:'https://api.github.com/repos/JimBLogic/CyberDailyLog/actions/runs/123',
  html_url:'https://github.com/JimBLogic/CyberDailyLog/actions/runs/123'};

async function fakeRequests(body, runData, callback, override) {
  const original = globalThis.fetch, calls = [];
  globalThis.fetch = async (url, init) => {
    const address = String(url); calls.push({url:address,init});
    const supplied = override?.(address,init,calls);
    if (supplied !== undefined) return supplied;
    if (address.startsWith('https://raw.githubusercontent.com/')) return Response.json(body);
    if (address.includes('/runs?')) {
      const status = new URL(address).searchParams.get('status');
      return Response.json(runData?.(status) ?? {total_count:0,workflow_runs:[]});
    }
    if (address.endsWith('/dispatches')) return Response.json(RECEIPT);
    throw Error('Unexpected destination');
  };
  try { return await callback(calls); } finally { globalThis.fetch = original; }
}

for (const [at,target] of [
  ['2026-03-28T11:00:00Z','2026-03-28T11:00:00.000Z'],
  ['2026-03-29T10:20:00Z','2026-03-29T10:00:00.000Z'],
  ['2026-10-24T10:40:00Z','2026-10-24T10:00:00.000Z'],
  ['2026-10-25T11:00:00Z','2026-10-25T11:00:00.000Z'],
]) test(`Madrid noon and DST boundary ${at}`, () => {
  assert.equal(planWakeup(new Date(at),OLD).target,target);
});

test('only the actual Madrid hour can dispatch, including delayed previous cron events', async () => {
  for (const at of ['2026-10-19T09:59:59Z','2026-10-19T11:00:00Z','2026-12-19T10:20:00Z']) {
    assert.deepEqual(await performWakeup({},new Date(at)),{action:'skip',reason:'outside_madrid_recovery_hour'});
  }
  assert.throws(() => planWakeup(new Date('invalid'),OLD),/invalid_clock/);
});

test('a complete close suppresses recovery but an on-time quorum partial does not', () => {
  assert.equal(planWakeup(NOW,CLOSED).reason,'complete_daily_close_confirmed');
  for (const core of [false,null,undefined]) assert.equal(planWakeup(NOW,{...CLOSED,core_complete:core}).action,'dispatch');
  assert.equal(planWakeup(NOW,{...CLOSED,report_generated:'2026-10-19T09:59:59Z'}).action,'dispatch');
  assert.equal(planWakeup(NOW,{...CLOSED,status:'failed'}).action,'dispatch');
  assert.equal(planWakeup(NOW,{...CLOSED,actual_publication_time:'2026-10-20T10:03:00Z'}).action,'dispatch');
});

test('invalid evidence never becomes a blind dispatch', async () => {
  for (const data of [{}, {...CLOSED,core_complete:'true'}, {...OLD,actual_publication_time:'bad'},
    {...OLD,actual_publication_time:'2026-10-18T14:41:40'}]) {
    await fakeRequests(data,null,async calls => {
      await assert.rejects(performWakeup(ENV,NOW),/invalid_/);
      assert.equal(calls.length,1);
    });
  }
});

test('public evidence read has no token and complete close needs no API calls', async () => {
  await fakeRequests(CLOSED,null,async calls => {
    assert.equal((await performWakeup({},NOW)).action,'skip');
    assert.equal(calls.length,1); assert.equal(calls[0].init.headers.Authorization,undefined);
  });
});

test('only repository Actions requests carry the secret; dispatch receipt is correlated', async () => {
  await fakeRequests({...CLOSED,core_complete:false},null,async calls => {
    const result = await performWakeup(ENV,NOW);
    assert.equal(result.action,'accepted'); assert.equal(result.run_id,123);
    assert.equal(result.scheduled_for,'2026-10-19T10:00:00.000Z');
    assert.equal(calls.length,7);
    assert.equal(calls[0].init.headers.Authorization,undefined);
    for (const call of calls.slice(1)) {
      assert.equal(new URL(call.url).origin,'https://api.github.com');
      assert.equal(call.init.headers.Authorization,`Bearer ${SECRET}`);
      assert.equal(call.init.headers['X-GitHub-Api-Version'],'2026-03-10');
      assert.equal(call.init.redirect,'manual');
    }
    assert.deepEqual(JSON.parse(calls.at(-1).init.body),{ref:'main',inputs:{dry_run:false,
      lookback_hours:'24',trigger_origin:'external',dispatch_requested_at:'2026-10-19T10:20:03.000Z'}});
    assert.equal(calls.filter(call => call.init.method === 'POST').length,1);
    assert.ok(!JSON.stringify(result).includes(SECRET));
  });
});

for (const status of ['in_progress','queued','waiting','pending','requested']) {
  test(`filtered ${status} workflow prevents duplicate even if created before noon`, async () => {
    await fakeRequests(OLD,filter => filter === status ? {total_count:1,workflow_runs:[{id:9,status,
      head_branch:'main',path:'.github/workflows/daily-intelligence.yml',created_at:'2026-10-18T10:00:00Z'}]}:undefined,
    async calls => {
      assert.equal((await performWakeup(ENV,NOW)).reason,'workflow_already_active');
      assert.ok(calls.slice(1).every(call => call.url.includes('/workflows/daily-intelligence.yml/runs?')));
      assert.ok(calls.slice(1).every(call => new URL(call.url).searchParams.get('per_page') === '1'));
      assert.ok(calls.every(call => call.init.method !== 'POST'));
    });
  });
}

test('malformed/truncated inventory, permissions or redirect failure stops before mutation', async () => {
  for (const data of [{oops:true},{total_count:1,workflow_runs:[]},
    {total_count:1,workflow_runs:[{id:5,status:'in_progress',head_branch:'other'}]}]) {
    await fakeRequests(OLD,() => data,async calls => {
      await assert.rejects(performWakeup(ENV,NOW),/invalid_run_inventory/);
      assert.ok(calls.every(call => call.init.method !== 'POST'));
    });
  }
  for (const status of [301,401,403,429,500]) {
    await fakeRequests(OLD,null,async calls => {
      await assert.rejects(performWakeup(ENV,NOW),/redirect_rejected|upstream_http_/);
      assert.ok(calls.every(call => call.init.method !== 'POST'));
    },url => url.includes('/runs?') ? new Response(SECRET,{status,headers:{Location:'https://example.com'}}):undefined);
  }
});

test('missing/invalid managed secret sends no authenticated request', async () => {
  for (const value of [undefined,'','secret\nother',' secret']) await fakeRequests(OLD,null,async calls => {
    await assert.rejects(performWakeup({GITHUB_ACTIONS_TOKEN:value},NOW),/missing_or_invalid_dispatch_secret/);
    assert.equal(calls.length,1);
  });
});

test('bounded JSON and response formats reject invalid upstream data', async () => {
  for (const response of [() => new Response('not JSON'),
    () => new Response('small',{headers:{'Content-Length':'524289'}}),
    () => new Response('x'.repeat(524289))]) {
    await fakeRequests(OLD,null,async calls => {
      await assert.rejects(performWakeup(ENV,NOW),/invalid_json_response|response_too_large/);
      assert.equal(calls.length,1);
    },url => url.startsWith('https://raw.') ? response():undefined);
  }
});

test('malformed dispatch receipt or ambiguous POST is never blindly retried', async () => {
  for (const response of [() => Response.json({...RECEIPT,html_url:'https://example.com/'}),
    () => new Response(null,{status:204}), () => {throw Error(SECRET);}]) {
    await fakeRequests(OLD,null,async calls => {
      await assert.rejects(performWakeup(ENV,NOW),/invalid_dispatch_receipt|unexpected_dispatch_response|transport_unavailable/);
      assert.equal(calls.filter(call => call.init.method === 'POST').length,1);
    },url => url.endsWith('/dispatches') ? response():undefined);
  }
});

test('HTTP cannot trigger writes, and config exposes no route, preview or embedded credential', async () => {
  const config = JSON.parse(readFileSync(new URL('./wrangler.jsonc',import.meta.url),'utf8'));
  assert.equal(config.workers_dev,false); assert.equal(config.preview_urls,false); assert.deepEqual(config.routes,[]);
  assert.deepEqual(config.triggers.crons,['0,20,40 10,11 * * *']);
  assert.equal(config.vars,undefined);
  for (const method of ['GET','POST','PUT','DELETE']) assert.equal((await worker.fetch(new Request('https://example.com',{method}))).status,404);
});

test('scheduled handler records true clock and nominal cron separately without logging secret/error bodies', async () => {
  const OriginalDate = globalThis.Date, log = console.log, error = console.error, messages = [];
  globalThis.Date = class extends OriginalDate { constructor(...args) {super(...(args.length ? args:[NOW.getTime()]));} };
  console.log = value => messages.push(value); console.error = value => messages.push(value);
  try {
    await fakeRequests(CLOSED,null,async () => {
      let job; await worker.scheduled({scheduledTime:NOW.getTime()-3600000},ENV,{waitUntil(value){job=value;}}); await job;
    });
    const event = JSON.parse(messages[0]);
    assert.equal(event.invocation,'scheduled'); assert.equal(event.observed_at,NOW.toISOString());
    assert.equal(event.nominal_scheduled_at,'2026-10-19T09:20:03.000Z');
    await fakeRequests(OLD,null,async () => {
      let job; await worker.scheduled({scheduledTime:NOW.getTime()},ENV,{waitUntil(value){job=value;}});
      await assert.rejects(job,/transport_unavailable/);
    },() => {throw Error(SECRET);});
    assert.ok(!messages.join('\n').includes(SECRET));
  } finally {globalThis.Date=OriginalDate; console.log=log; console.error=error;}
});
