import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";
import ts from "typescript";
const context = { exports: {} };
vm.runInNewContext(ts.transpileModule(readFileSync(new URL("../lib/official-source-health.ts", import.meta.url), "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, context);
const { officialSourceHealth: health } = context.exports;
const nvd = { totalResults: 1, startIndex: 0, resultsPerPage: 2000, vulnerabilities: [{ cve: { id: "CVE-2026-12345" } }] };
test("JSON success without a source contract is not healthy", () => {
  for (const value of [null, {}, [], { vulnerabilities: "wrong" }]) {
    for (const source of ["nvd", "cisa"]) assert.equal(health(value, source).status, "failed");
  }
});
test("NVD distinguishes complete, truncated and inconsistent pages", () => {
  assert.equal(health(nvd, "nvd").status, "healthy");
  for (const patch of [{ totalResults: 2 }, { totalResults: 0 }, { startIndex: 1 }, { resultsPerPage: 0 }, { totalResults: "1" }]) {
    assert.equal(health({ ...nvd, ...patch }, "nvd").status, "degraded");
  }
  assert.equal(health({ ...nvd, totalResults: 0, vulnerabilities: [] }, "nvd").status, "healthy");
});
test("CISA validates catalog counts and record identities", () => {
  const catalog = { count: 1, vulnerabilities: [{ cveID: "CVE-2026-12345" }] };
  assert.equal(health(catalog, "cisa").status, "healthy");
  assert.equal(health({ ...catalog, count: 2 }, "cisa").status, "degraded");
  assert.equal(health({ count: 1, vulnerabilities: [{}] }, "cisa").rejected, 1);
  assert.equal(health({ count: 2, vulnerabilities: [...catalog.vulnerabilities, ...catalog.vulnerabilities] }, "cisa").rejected, 1);
});
