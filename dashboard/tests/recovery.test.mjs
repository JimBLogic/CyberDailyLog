import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";
import ts from "typescript";
const context = { exports: {} };
vm.runInNewContext(ts.transpileModule(readFileSync(new URL("../lib/recovery.ts", import.meta.url), "utf8"), { compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022} }).outputText,context);
const { normalizeRecovery } = context.exports;
const valid = {run_id:"101",run_attempt:"1",trigger:"schedule",started_at:"2026-10-20T11:00:00Z",finished_at:"2026-10-20T11:01:00Z",outcome:"published",publication_id:"a".repeat(40)};
test("legacy timing has no invented telemetry",()=>{
  for (const input of [null,{}, {schema_version:2,attempts:[]}]) assert.equal(normalizeRecovery(input),null);
});
test("recovery contract retains observed fields and safe identifiers",()=>{
  const data=normalizeRecovery({schema_version:1,attempts:[{...valid,outcome:"failed",publication_id:null},{...valid,run_id:"102",started_at:"2026-10-20T11:01:30Z",finished_at:"2026-10-20T11:02:00Z",recovered_from:{run_id:"101",run_attempt:"1"}}],recovery_seconds:60});
  assert.equal(data.attempts.length,2);
  assert.equal(data.attempts[1].recovered_from.run_id,"101");
  assert.equal(data.retry_count,1); assert.equal(data.recovery_seconds,60);
});
test("bad identifiers, reversed dates and invalid duration cannot form evidence links",()=>{
  const data=normalizeRecovery({schema_version:1,attempts:[{...valid,run_id:"javascript:alert(1)"},{...valid,finished_at:"2026-10-20T10:00:00Z",publication_id:"bad"}],recovery_seconds:-1});
  assert.equal(data.attempts.length,1); assert.equal(data.attempts[0].finished_at,null);
  assert.equal(data.attempts[0].publication_id,null); assert.equal(data.recovery_seconds,null);
});
