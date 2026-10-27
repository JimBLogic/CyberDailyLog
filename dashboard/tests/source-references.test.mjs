import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import ts from 'typescript';
function load(file) {
  const context = { exports: {}, URL };
  vm.runInNewContext(ts.transpileModule(readFileSync(new URL(file, import.meta.url), 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, context);
  return context.exports;
}
const { referenceUrls } = load('../lib/safe-url.ts');
test('compound CISA references become separate links, including previously encoded separators', () => {
  for (const separator of [' ; BOD: ', '%20;%20BOD:%20']) {
    assert.deepEqual(Array.from(referenceUrls(['https://vendor.test/a' + separator + 'https://cisa.gov/b'])), ['https://vendor.test/a', 'https://cisa.gov/b']);
  }
  assert.deepEqual(Array.from(referenceUrls(['https://vendor.test/a%20b', 'https://vendor.test/a%20b', 'javascript:https://evil.test', 'https://user:pass@evil.test'])), ['https://vendor.test/a%20b']);
});
test('CERT-EU sources have explicit labels, official links and contextual provenance', () => {
  const m = load('../lib/source-labels.ts');
  for (const source of ['rss_cert_eu_advisories', 'rss_cert_eu_guidance']) {
    assert.match(m.SOURCE_LABELS[source], /^CERT-EU/);
    assert.equal(new URL(m.SOURCE_URLS[source]).hostname, 'cert.europa.eu');
    assert.equal(m.SOURCE_PROFILES[source].lane, 'expert');
    assert.equal(m.SOURCE_PROFILES[source].provenance, 'government');
  }
});
