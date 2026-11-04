import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import test from "node:test";
import vm from "node:vm";
import { renderToStaticMarkup } from "react-dom/server";
import ts from "typescript";

const require = createRequire(import.meta.url);
const context = {
  exports: {},
  require: (name) => name === "../../lib/cti" ? { CHANGE_LABELS: {} } : require(name),
};
const source = readFileSync(new URL("../app/components/operational-status.tsx", import.meta.url), "utf8");
vm.runInNewContext(ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
}).outputText, context);

for (const interval of [1, 15]) {
  for (const language of ["es", "en"]) {
    test(`operational caption reports the ${interval}-minute refresh interval in ${language}`, () => {
      const html = renderToStaticMarkup(context.exports.OperationalStatus({
        data: { sourceHealth: [], refreshIntervalMinutes: interval },
        language,
        now: null,
      }));
      const expected = language === "es"
        ? `el panel comprueba novedades cada ${interval} min.`
        : `the dashboard checks updates every ${interval} ${interval === 1 ? "minute" : "minutes"}.`;
      assert.ok(html.includes(expected), expected);
    });
  }
}
