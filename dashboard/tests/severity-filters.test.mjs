import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";
import ts from "typescript";
const source = readFileSync(new URL("../lib/severity-filters.ts", import.meta.url), "utf8");
const context = { exports: {} };
vm.runInNewContext(ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, context);
const { availableSeverityOptions, resolveSeverityFilter } = context.exports;
const plain = value => JSON.parse(JSON.stringify(value));

test("severity options count only categories present in the displayed selection", () => {
  assert.deepEqual(plain(availableSeverityOptions([{ severity: "HIGH" }, { severity: "CRITICAL" }, { severity: "HIGH" }])), [
    { severity: "CRITICAL", count: 1 }, { severity: "HIGH", count: 2 },
  ]);
});
test("medium, low and unknown appear automatically when supplied, in severity order", () => {
  assert.deepEqual(plain(availableSeverityOptions([{ severity: "UNKNOWN" }, { severity: "LOW" }, { severity: "MEDIUM" }])), [
    { severity: "MEDIUM", count: 1 }, { severity: "LOW", count: 1 }, { severity: "UNKNOWN", count: 1 },
  ]);
  assert.deepEqual(plain(availableSeverityOptions([])), []);
});
test("a refresh that removes the selected severity falls back to all without an empty stale filter", () => {
  const options = availableSeverityOptions([{ severity: "HIGH" }]);
  assert.equal(resolveSeverityFilter("MEDIUM", options), "ALL");
  assert.equal(resolveSeverityFilter("HIGH", options), "HIGH");
  assert.equal(resolveSeverityFilter("ALL", []), "ALL");
});
