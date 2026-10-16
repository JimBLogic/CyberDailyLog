import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import worker, { planWakeup, performWakeup } from './worker.mjs';

const base = {
  schema_version:2, status:'stale',
  actual_publication_time:'2026-10-15T14:41:40+00:00',
};
const t = x => new Date(x);
const active = created_at => [{
  name:'Daily Blue Team Intelligence', head_branch:'main',
  status:'in_progress', created_at,
}];

test('both UTC daylight regimes target 12:00 Madrid without a fixed offset', () => {
  const summer = planWakeup(t('2026-10-16T10:00:00Z'),base,[]);
  const winter = planWakeup(t('2026-12-16T11:20:00Z'),base,[]);
  assert.equal(summer.action,'dispatch');
  assert.equal(summer.target,'2026-10-16T10:00:00.000Z');
  assert.equal(winter.action,'dispatch');
  assert.equal(winter.target,'2026-12-16T11:00:00.000Z');
  assert.equal(planWakeup(t('2026-10-16T11:00:00Z'),base,[]).action,'skip');
  assert.equal(planWakeup(t('2026-12-16T10:00:00Z'),base,[]).action,'skip');
});

test('measured publication or ongoing run prevents a second dispatch', () => {
  const now=t('2026-10-16T10:20:00Z');
  assert.equal(planWakeup(now,{...base,status:'on_time',
    actual_publication_time:'2026-10-16T10:02:00Z'},[]).action,'skip');
  assert.equal(planWakeup(now,base,active('2026-10-16T10:02:00Z')).action,'skip');
  assert.equal(planWakeup(now,base,active('2026-10-15T10:02:00Z')).action,'dispatch');
  assert.equal(planWakeup(now,{...base, status:'failed',
    actual_publication_time:'2026-10-16T10:02:00Z'},[]).action,'dispatch');
  assert.throws(()=>planWakeup(now,base,null),/inventory unavailable/);
});

test('read and dispatch send no public write request and only Actions workflow input', async () => {
  const original=globalThis.fetch, calls=[];
  globalThis.fetch=async(url,init)=>{
    calls.push({url:String(url),init});
    if(String(url).includes('/contents/')) return Response.json(base);
    if(String(url).includes('/actions/runs?')) return Response.json({workflow_runs:[]});
    if(String(url).includes('/dispatches')) return new Response(null,{status:204});
    throw Error('Unexpected URL');
  };
  try {
    const result=await performWakeup({GITHUB_ACTIONS_TOKEN:'fake-test-value'},t('2026-10-16T10:20:03Z'));
    assert.equal(result.action,'accepted');
    assert.equal(result.scheduled_for,'2026-10-16T10:00:00.000Z');
    assert.equal(calls.length,3);
    assert.deepEqual(calls.map(c=>c.init.method||'GET'),['GET','GET','POST']);
    assert.ok(calls.every(c=>c.init.headers.Authorization==='Bearer fake-test-value'));
    assert.ok(calls.every(c=>c.init.redirect==='manual'));
    const dispatch=JSON.parse(calls[2].init.body);
    assert.deepEqual(dispatch,{
      ref:'main',inputs:{dry_run:false,lookback_hours:'24',trigger_origin:'external',
        dispatch_requested_at:'2026-10-16T10:20:03.000Z'},
    });
    assert.match(calls[2].url,/\/actions\/workflows\/daily-intelligence\.yml\/dispatches$/);
  } finally { globalThis.fetch=original; }
});

test('secret and upstream failures stop before mutation', async () => {
  const original=globalThis.fetch;
  let called=0;
  globalThis.fetch=async()=>{called++;return new Response('not authorized',{status:401});};
  try {
    await assert.rejects(performWakeup({},t('2026-10-16T10:00:00Z')),/Missing scoped/);
    assert.equal(called,0);
    await assert.rejects(performWakeup({GITHUB_ACTIONS_TOKEN:'fake'},t('2026-10-16T10:00:00Z')),/evidence read HTTP 401/);
    assert.equal(called,1);
  } finally {globalThis.fetch=original;}
  assert.equal((await worker.fetch()).status,404);
});

test('failure to reconcile running workflows cannot send a blind duplicate', async () => {
  const original=globalThis.fetch;let calls=0;
  globalThis.fetch=async(url)=>{
    calls++;
    if(String(url).includes('/contents/')) return Response.json(base);
    if(String(url).includes('/actions/runs?')) return Response.json({oops:true});
    throw Error('unexpected dispatch');
  };
  try {
    await assert.rejects(performWakeup({GITHUB_ACTIONS_TOKEN:'fake'},t('2026-10-16T10:40:00Z')),/inventory unavailable/);
    assert.equal(calls,2);
  }finally{globalThis.fetch=original;}
});

test('cron runtime always measures the actual execution timestamp, not nominal delayed scheduledTime', () => {
  const code = readFileSync(new URL('./worker.mjs', import.meta.url), 'utf8');
  assert.ok(code.includes('const now = new Date();'));
  assert.ok(!code.includes('new Date(controller.scheduledTime)'));
});
