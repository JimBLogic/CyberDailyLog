import assert from 'node:assert/strict';

const scenario = process.argv[2];
const now = Date.now();
const iso = (offset = 0) => new Date(now + offset).toISOString();
const old = scenario === 'stale' ? -3 * 86_400_000 : 0;
const health = ['cisa_kev', 'nvd', 'github_advisories'].map(source => ({
  source, required: true, status: 'healthy', finished_at: iso(old), items_accepted: 2,
}));
const report = {
  generated_at: iso(old), coverage_start: iso(old - 86_400_000), coverage_end: iso(old),
  degraded: false, source_health: health,
  items: [{canonical_id: 'CVE-2026-12345', cve_ids: ['CVE-2026-12345'],
    title: '=HYPERLINK("danger")', summary: 'A test advisory', category: 'vulnerability',
    priority_score: 7.5, severity: 'HIGH', cvss_score: 8.1, cisa_kev: true,
    source_name: 'NVD', source_url: 'javascript:alert(1)', published_at: iso(old),
    references: ['data:text/html,bad', 'https://nvd.nist.gov/vuln/detail/CVE-2026-12345', 'https://user:pass@example.com/'],
  }, {canonical_id:'CVE-2026-23456', title:'Second', category:'vulnerability', priority_score:1.5, severity:'LOW'}],
};
if (scenario === 'future') report.generated_at = iso(86_400_000);
if (scenario === 'missing-health') delete report.source_health;
if (scenario === 'cti') {
  report.cti_summary = {new_vulnerabilities:0, state_changes:1};
  report.source_health.push({source:'epss', required:false, status:'failed', finished_at:iso()});
  Object.assign(report.items[0], {
    discovery_type:'state_transition', transition_type:['ransomware_linked','untrusted_transition'],
    first_seen:iso(-86_400_000), last_seen:iso(), state_changed_at:iso(),
    priority_before:9.6, priority_after:10, priority_level_before:'HIGH', priority_level:'EMERGENCY',
    current_state:{known_ransomware_use:true,cisa_kev:true,exploitation_status:'confirmed_exploitation'},
    state_transitions:[{changed_at:iso(),transition_type:['ransomware_linked'],priority_before:9.6,priority_after:10,
      sources:[{name:'Unsafe',url:'javascript:alert(1)'},{name:'CISA',url:'https://www.cisa.gov/'}]}],
  });
}
let reportFetches = 0;
globalThis.fetch = async (input) => {
  const url = new URL(input instanceof Request ? input.url : String(input));
  if (url.pathname.endsWith('/latest.json')) {
    reportFetches++;
    if (scenario === 'offline') throw new Error('offline');
    if (url.hostname === 'raw.githubusercontent.com') {
      if (scenario === 'invalid-json') return new Response('<html>not JSON</html>');
      if (scenario === 'invalid-schema') return Response.json({items: 'invalid'});
    }
    return Response.json(report);
  }
  if (url.pathname.endsWith('/portfolio-feed.json')) return Response.json({
    generated_at: scenario === 'mixed' ? iso(-86_400_000) : report.generated_at,
    minimum_priority: 5, above_threshold: 999, immediate_attention_count: 888,
    human_context: {title: 'Wrong generation', source_url:'javascript:alert(1)'},
  });
  if (url.pathname.endsWith('/dashboard-feed.json')) return Response.json({history:[]});
  if (url.pathname.endsWith('/publication-timing.json')) return Response.json(scenario === 'invalid-timing' ? {
    schema_version:2, status:'made_up', publication_lag_seconds:-3, actual_publication_time:'invalid',
    run_url:'javascript:alert(1)', slo:{attainment_percentage:999,measured_publications:999},
  } : {schema_version:2,status:'on_time',scheduled_for:iso(-120_000),actual_publication_time:iso(-60_000),
    publication_lag_seconds:60,report_generated:report.generated_at,root_cause_stage:'within_threshold',
    run_url:'https://github.com/JimBLogic/CyberDailyLog/actions/runs/123',
    slo:{attainment_percentage:100,measured_publications:1,full_window_observed:false,evaluated_at:iso()},
    ...(scenario === 'skipped-recovery' ? {
      status:'delayed',publication_lag_seconds:3999,root_cause_stage:'dispatch',trigger_origin:'external_push',
      dispatch_requested_at:iso(-4_100_000),workflow_created:iso(-4_097_000),workflow_actual_start:iso(-4_097_000),
      dispatch_creation_lag_seconds:3,workflow_queue_seconds:0,fetch_duration_seconds:76.384,
      last_attempt:{status:'skipped',trigger_origin:'schedule',workflow_created:iso(),trigger_creation_lag_seconds:14790,
        run_url:'https://github.com/JimBLogic/CyberDailyLog/actions/runs/456'},
    } : {}),
  });
  return new Response('Unavailable', {status:503});
};
const {default:worker} = await import('../../dist/server/index.js');
const env = {ASSETS:{fetch:async()=>new Response('Not found',{status:404})}};
const ctx = {waitUntil(){},passThroughOnException(){}};
const api = () => worker.fetch(new Request('http://localhost/api/intelligence'), env, ctx);
const responses = await Promise.all([api(), api()]);
assert.ok(responses.every(r => r.status === 200));
assert.equal(responses[0].headers.get('cache-control'), 'no-store');
assert.equal(responses[0].headers.get('set-cookie'), null);
const data = await responses[0].json();
assert.equal(new Set(data.deliveryChain.map(x=>x.id)).size, data.deliveryChain.length);
if (['future','offline'].includes(scenario)) {
  assert.equal(data.dataMode,'repository-snapshot');
  assert.equal(data.pipelineStatus,'degraded');
  assert.equal(data.coverageConfidence,'low');
} else {
  assert.equal(data.vulnerabilities.length,2);
  assert.equal(data.aboveThreshold,1);
  assert.equal(data.immediateAttentionCount,1);
  assert.equal(data.vulnerabilities[0].sourceUrl,'https://github.com/JimBLogic/CyberDailyLog/blob/main/reports/latest.md');
  assert.deepEqual(data.vulnerabilities[0].references,['https://nvd.nist.gov/vuln/detail/CVE-2026-12345']);
  if (['invalid-json','invalid-schema'].includes(scenario)) {
    assert.equal(data.deliveryOrigin,'jsdelivr-cdn');
    assert.equal(data.deliveryChain[0].status,'failed');
    assert.equal(reportFetches,2);
  } else assert.equal(reportFetches,1, 'concurrent requests must share collection');
  if (['stale','missing-health'].includes(scenario)) {
    assert.equal(data.pipelineStatus,'degraded');
    assert.equal(data.coverageState,'insufficient');
  }
  if (scenario === 'mixed') assert.equal(data.humanContext,null);
  if (scenario === 'cti') {
    assert.equal(data.ctiSummary.stateChanges,1);
    assert.equal(data.ctiSummary.ransomware,1);
    assert.equal(data.ctiSummary.newVulnerabilities,0);
    assert.equal(data.coverageConfidence,'medium');
    assert.deepEqual(data.vulnerabilities[0].cti.changes,['ransomware_linked']);
    assert.equal(data.vulnerabilities[0].cti.priorityBefore,9.6);
    assert.equal(data.vulnerabilities[0].cti.levelAfter,'EMERGENCY');
    assert.equal(data.vulnerabilities[0].cti.history[0].sources.length,1);
  }
  if (scenario === 'invalid-timing') {
    assert.equal(data.publicationReliability.status,'unknown');
    assert.equal(data.publicationReliability.lagSeconds,null);
    assert.equal(data.publicationReliability.actual,null);
    assert.equal(data.publicationReliability.sloPercentage,null);
    assert.equal(data.publicationReliability.runUrl,'');
  }
  if (scenario === 'skipped-recovery') {
    const p = data.publicationReliability;
    assert.equal(p.status,'delayed');
    assert.equal(p.lagSeconds,3999);
    assert.equal(p.origin,'external_push');
    assert.equal(p.rootCause,'dispatch');
    assert.equal(p.dispatchSeconds,3);
    assert.equal(p.queueSeconds,0);
    assert.equal(p.lastAttempt.status,'skipped');
    assert.equal(p.lastAttempt.creationLagSeconds,14790);
    assert.notEqual(p.runUrl,p.lastAttempt.runUrl);
  }
  const csv = await worker.fetch(new Request('http://localhost/api/export?format=csv'),env,ctx);
  const text = await csv.text();
  assert.ok(text.includes('"\'=HYPERLINK(""danger"")"'), 'CSV formulas must be neutralized');
  assert.ok(text.includes('\r\n'));
}
console.log(`PASS ${scenario}`);
