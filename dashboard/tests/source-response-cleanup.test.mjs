import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";
import ts from "typescript";

// Expose only the internal transport boundary; execute its actual source with
// controlled HTTP streams rather than a real external service.
function transport(file, fetch) {
  const context = {
    exports: {}, URL, Date, Response, AbortSignal, DOMException, fetch,
    require: (name) => name.includes("network-policy")
      ? { essentialServerUrl: (url) => url }
      : {},
  };
  const source = readFileSync(new URL(file, import.meta.url), "utf8");
  vm.runInNewContext(ts.transpileModule(
    `${source}\nexport { fetchJson as fetchJsonUnderTest };`,
    { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } },
  ).outputText, context);
  return context.exports.fetchJsonUnderTest;
}

for (const file of ["../lib/data.ts", "../lib/official-backup.ts"]) {
  for (const status of [302, 429, 503]) {
    test(`${file}: HTTP ${status} releases body before fallback`, async () => {
      let pending = false;
      let calls = 0;
      const fetchJson = transport(file, async () => {
        assert.equal(pending, false, "prior upstream body must be closed before another request");
        pending = true;
        calls++;
        const body = new ReadableStream({
          start(controller) { controller.enqueue(new TextEncoder().encode("unparsed error")); },
          cancel() { pending = false; },
        });
        return new Response(body, { status });
      });
      const result = await fetchJson("https://www.cisa.gov/fixture.json");
      assert.equal(pending, false, "last failed response must also be closed");
      assert.equal(result.data, null);
      assert.equal(calls, file.endsWith("/data.ts") ? 2 : 1);
    });
  }
  test(`${file}: cancellation failure does not prevent safe fallback`, async () => {
    let calls = 0;
    const fetchJson = transport(file, async () => {
      calls++;
      return new Response(new ReadableStream({
        cancel() { throw new Error("upstream already disconnected"); },
      }), { status: 503 });
    });
    const result = await fetchJson("https://www.cisa.gov/fixture.json");
    assert.equal(result.data, null);
    assert.equal(calls, file.endsWith("/data.ts") ? 2 : 1);
  });
}
