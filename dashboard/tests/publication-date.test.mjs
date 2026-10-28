import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";
import ts from "typescript";
const context = { exports: {} };
vm.runInNewContext(ts.transpileModule(readFileSync(new URL("../lib/publication-date.ts", import.meta.url), "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, context);
const { publicationDate } = context.exports;
const now = Date.parse("2026-10-28T11:00:00Z");
test("unknown and invalid publication dates stay unknown", () => {
  for (const value of [undefined, null, "", "invalid", false, 0, "1999-12-31T23:59:59Z"]) assert.equal(publicationDate(value, now), "");
});
test("valid source dates are preserved with bounded clock skew", () => {
  assert.equal(publicationDate("2026-10-27T10:00:00+01:00", now), "2026-10-27T09:00:00.000Z");
  assert.equal(publicationDate("2026-10-28T11:05:00Z", now), "2026-10-28T11:05:00.000Z");
  assert.equal(publicationDate("2026-10-28T11:05:01Z", now), "");
});
