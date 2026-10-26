import assert from 'node:assert/strict';
import test from 'node:test';
const {default:worker}=await import('../dist/server/index.js');
const ctx={waitUntil(){},passThroughOnException(){}};
const closed={ASSETS:{fetch(){throw new Error('Retired Guard must not forward assets')}},get DB(){throw new Error('Retired Guard must not read storage')}};
const req=(path,method='GET')=>new Request('https://retirement-fixture.invalid'+path,{method,headers:{'oai-authenticated-user-id':'forged','X-Plan':'pro'},...(!['GET','HEAD'].includes(method)?{body:'{}'}:{})});
test('public Guard returns a bilingual 410 without scripts, private links or redirects',async()=>{
 for(const path of ['/guard','/guard/']){
  const r=await worker.fetch(req(path),closed,ctx);assert.equal(r.status,410);assert.equal(r.headers.get('location'),null);
  const html=await r.text();assert.match(html,/prueba pública retirada/);assert.match(html,/lang="en"/);assert.doesNotMatch(html,/<script|private-alpha|guard-alpha/);
  assert.equal(r.headers.get('cache-control'),'no-store');assert.match(r.headers.get('content-security-policy'),/script-src 'none'/);
 }
});
test('retired assets, catalog, radar and health cannot revive the public edition',async()=>{
 for(const path of ['/guard/app.js','/guard/style.css','/guard/healthz','/guard/api/catalog?q=Apache','/guard/api/public-intelligence']){
  for(const method of ['GET','HEAD']){
   const r=await worker.fetch(req(path,method),closed,ctx);assert.equal(r.status,410);assert.equal(r.headers.get('location'),null);
   if(method==='HEAD')assert.equal(await r.text(),'');else assert.equal((await r.json()).error,'guard_public_retired');
  }
 }
});
test('retirement preserves all 77 private denials and manipulated-input closure',async()=>{
 const before=globalThis.fetch;let calls=0;globalThis.fetch=()=>{calls++;throw new Error('No network allowed')};
 try{
  for(const path of ['/guard/api','/guard/api/me','/guard/api/assets','/guard/api/assets/00000000-0000-0000-0000-000000000000','/guard/api/groups','/guard/api/alerts','/guard/api/match','/guard/api/preferences','/guard/api/export','/guard/api/account','/guard/api/unknown']){
   for(const method of ['GET','HEAD','POST','PATCH','PUT','DELETE','OPTIONS']){
    const r=await worker.fetch(req(path+'?account_id=forged&plan=pro',method),closed,ctx);assert.equal(r.status,503);
    if(method!=='HEAD')assert.equal((await r.json()).error,'site_test_private_disabled');
   }
  }
  assert.equal(calls,0);
 }finally{globalThis.fetch=before}
});
test('public dashboard routes and export keep their existing contracts',async()=>{
 const env={ASSETS:{fetch:async()=>new Response('missing',{status:404})}};
 const robots=await worker.fetch(req('/robots.txt'),env,ctx);assert.equal(robots.status,200);assert.equal(robots.headers.get('x-robots-tag'),null);
 const lookalike=await worker.fetch(req('/guardian'),env,ctx);assert.equal(lookalike.status,404);
 const exported=await worker.fetch(req('/api/export?format=json'),env,ctx);assert.equal(exported.status,200);const body=await exported.json();assert.ok(Array.isArray(body.vulnerabilities));assert.equal(Object.hasOwn(body,'assets'),false);
});
