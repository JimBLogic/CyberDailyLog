import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";
import ts from "typescript";
const context = { exports: {} };
vm.runInNewContext(ts.transpileModule(readFileSync(new URL("../lib/bounded-score.ts", import.meta.url), "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, context);
const { boundedScore } = context.exports;
test("CVSS retains zero, ten and valid decimal strings", () => {
  for (const value of [0, 10, "7.5"]) assert.equal(boundedScore(value, 10), Number(value));
  for (const value of [-0.1, 10.1, "99"]) assert.equal(boundedScore(value, 10), null);
});
test("EPSS probabilities and percentiles stay within zero and one", () => {
  for (const value of [0, 1, "0.25"]) assert.equal(boundedScore(value, 1), Number(value));
  for (const value of [-0.1, 1.01, "7.5"]) assert.equal(boundedScore(value, 1), null);
});
test("unknown, non-finite and nonnumeric values remain unknown", () => {
  for (const maximum of [1, 10]) {
    for (const value of [null, undefined, true, false, "", " ", [], {}, NaN, Infinity, "NaN", "Infinity", "invalid"]) {
      assert.equal(boundedScore(value, maximum), null);
    }
  }
});
