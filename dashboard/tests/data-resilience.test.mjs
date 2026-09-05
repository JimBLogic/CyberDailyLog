import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import test from 'node:test';

for (const scenario of ['mixed', 'invalid-json', 'invalid-schema', 'stale', 'future', 'offline', 'missing-health']) {
  test(`production data boundary: ${scenario}`, () => {
    const result = spawnSync(process.execPath, ['tests/fixtures/data-scenario.mjs', scenario], {
      encoding:'utf8', timeout:30_000,
    });
    assert.equal(result.status,0,`${result.stdout}\n${result.stderr}`);
  });
}
