import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const packageJson = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8"));
const lock = JSON.parse(readFileSync(new URL("../package-lock.json", import.meta.url), "utf8"));
const dependencies = {
  react: packageJson.dependencies.react,
  "react-dom": packageJson.dependencies["react-dom"],
  "react-server-dom-webpack": packageJson.devDependencies["react-server-dom-webpack"],
};

test("React, React DOM and the RSC transport stay on one exact release", () => {
  assert.equal(dependencies["react-dom"], dependencies.react);
  assert.equal(dependencies["react-server-dom-webpack"], dependencies.react);
  for (const [name, version] of Object.entries(dependencies)) {
    assert.equal(lock.packages["node_modules/" + name].version, version);
    const root = name === "react-server-dom-webpack" ? lock.packages[""].devDependencies : lock.packages[""].dependencies;
    assert.equal(root[name], version);
  }
});

test("the October 2026 vulnerable React Server Components versions cannot return", () => {
  const [major, minor, patch] = dependencies["react-server-dom-webpack"].split(".").map(Number);
  assert.ok([major, minor, patch].every(Number.isInteger), "RSC version must be pinned, not ranged");
  assert.ok(
    major > 19 || (major === 19 && (minor > 3 || (minor === 3 && patch >= 1) || (minor === 2 && patch >= 9) || (minor === 1 && patch >= 10) || (minor === 0 && patch >= 9))),
    "React RSC must exclude the releases affected by GHSA-xqc2-xf4c-x3h3",
  );
});
