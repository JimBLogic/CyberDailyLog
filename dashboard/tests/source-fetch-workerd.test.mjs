import assert from "node:assert/strict";
import test from "node:test";
import { readFile, readdir } from "node:fs/promises";
import { resolve, sep } from "node:path";
import { Miniflare } from "miniflare";
const root = resolve(import.meta.dirname, "../dist/server");
const modules = Object.fromEntries(await Promise.all((await readdir(root, {recursive:true})).filter(n => n.endsWith(".js")).map(async n => [n.split(sep).join("/"), {type:"esm", contents:await readFile(resolve(root,n),"utf8")}])));

for (const redirect of [false, true]) {
  test(`real Worker source fetch and safe redirect fallback: ${redirect}`, {timeout:60000}, async () => {
    const calls = [];
    const now = new Date().toISOString();
    const report = {
      generated_at: now, coverage_start: now, coverage_end: now, degraded:false,
      source_health:["cisa_kev","nvd","github_advisories"].map(source => ({source,status:"healthy",required:true,finished_at:now})),
      items:[{canonical_id:"CVE-2026-12345",title:"Runtime fixture",category:"vulnerability",severity:"HIGH",priority_score:8,published_at:now}],
    };
    const mf = new Miniflare({host:"127.0.0.1",port:0,cf:false,telemetry:{enabled:false},workers:[{
      config:{name:"source-fetch-contract",compatibilityDate:"2026-10-16",compatibilityFlags:["nodejs_compat"],manifest:{mainModule:"index.js",modulesRoot:root,modules}},
      dev:{outboundService:{type:"fetcher",handler:async request => {
        const url = new URL(request.url);
        calls.push(url.href);
        assert.ok(["raw.githubusercontent.com","cdn.jsdelivr.net"].includes(url.hostname), "no off-policy request");
        if (url.pathname.endsWith("/latest.json")) {
          if (redirect && url.hostname === "raw.githubusercontent.com") return new Response(null,{status:302,headers:{Location:"https://disallowed.invalid/private"}});
          return Response.json(report);
        }
        if (url.pathname.endsWith("/dashboard-feed.json")) return Response.json({history:[]});
        return Response.json({});
      }}},
    }]});
    try {
      const response = await mf.dispatchFetch("https://runtime.invalid/api/intelligence");
      assert.equal(response.status,200);
      const data = await response.json();
      assert.equal(data.dataMode,"live");
      assert.equal(data.vulnerabilities[0].id,"CVE-2026-12345");
      assert.equal(data.deliveryOrigin,redirect ? "jsdelivr-cdn" : "github-raw");
      assert.ok(calls.some(url => url.endsWith("/latest.json")), "native fetch reached the outbound fixture");
      assert.ok(!calls.some(url => url.includes("disallowed.invalid")));
      if (redirect) assert.equal(data.deliveryChain[0].reason,"HTTP 302");
    } finally { await mf.dispose(); }
  });
}
