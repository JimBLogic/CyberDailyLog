import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";
import ts from "typescript";
const context = { exports: {}, TextDecoder };
vm.runInNewContext(ts.transpileModule(readFileSync(new URL("../lib/bounded-json.ts", import.meta.url), "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText, context);
const { readBoundedJson, ResponseLimitError } = context.exports;

test("JSON at the byte boundary preserves split multibyte UTF-8", async () => {
  const bytes = new TextEncoder().encode('"é"');
  const body = new ReadableStream({ start(c) { c.enqueue(bytes.slice(0, 2)); c.enqueue(bytes.slice(2)); c.close(); } });
  assert.equal(await readBoundedJson(new Response(body), bytes.length), "é");
});

test("oversized declared bodies are cancelled before consumption", async () => {
  let cancelled = false;
  const body = new ReadableStream({ cancel() { cancelled = true; } });
  await assert.rejects(readBoundedJson(new Response(body, { headers: { "Content-Length": "100" } }), 10), error => error instanceof ResponseLimitError);
  assert.equal(cancelled, true);
});

test("streamed size wins over a missing or misleading header", async () => {
  for (const headers of [{}, { "Content-Length": "1" }]) {
    let cancelled = false;
    const body = new ReadableStream({ start(c) { c.enqueue(new TextEncoder().encode('"oversized"')); }, cancel() { cancelled = true; } });
    await assert.rejects(readBoundedJson(new Response(body, { headers }), 4), error => error instanceof ResponseLimitError);
    assert.equal(cancelled, true);
  }
});

test("malformed JSON and invalid budgets are rejected", async () => {
  await assert.rejects(readBoundedJson(new Response("invalid"), 100));
  await assert.rejects(readBoundedJson(new Response("{}"), 0));
});


test("larger JSON survives buffer growth and small network chunks", async () => {
  const original = { text: "é".repeat(80000) };
  const bytes = new TextEncoder().encode(JSON.stringify(original));
  let offset = 0;
  const body = new ReadableStream({ pull(c) {
    if (offset >= bytes.length) { c.close(); return; }
    c.enqueue(bytes.slice(offset, offset + 997));
    offset += 997;
  } });
  const parsed = await readBoundedJson(new Response(body), bytes.length);
  assert.equal(parsed.text, original.text);
});

test("the default budget does not preallocate its full limit for a tiny feed", async () => {
  const allocations = [];
  class ObservedBuffer extends Uint8Array {
    constructor(...args) { super(...args); if (typeof args[0] === "number") allocations.push(args[0]); }
  }
  const observed = { exports: {}, TextDecoder, Uint8Array: ObservedBuffer };
  vm.runInNewContext(ts.transpileModule(readFileSync(new URL("../lib/bounded-json.ts", import.meta.url), "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText, observed);
  assert.equal((await observed.exports.readBoundedJson(new Response('{"ok":true}'))).ok, true);
  assert.ok(allocations.length > 0 && Math.max(...allocations) <= 64 * 1024);
});
