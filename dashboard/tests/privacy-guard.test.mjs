import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SCAN_ROOTS = ["app", "lib", "worker"];
const SOURCE_EXTENSIONS = new Set([".css", ".html", ".js", ".jsx", ".ts", ".tsx"]);

const APPROVED_EXTERNAL_HOSTS = new Set([
  "api.first.org",
  "cdn.jsdelivr.net",
  "cyberdailylog.jimblogic.chatgpt.site",
  "github.com",
  "help.openai.com",
  "isc.sans.edu",
  "jira.mongodb.org",
  "krebsonsecurity.com",
  "news.ycombinator.com",
  "nvd.nist.gov",
  "openai.com",
  "privacy.openai.com",
  "raw.githubusercontent.com",
  "schema.org",
  "security.eu.fsastech.com",
  "services.nvd.nist.gov",
  "siberguvenlik.gov.tr",
  "www.cisa.gov",
  "www.crowdstrike.com",
  "www.first.org",
  "www.justice.gov",
  "www.oracle.com",
]);

const ESSENTIAL_SERVER_HOSTS = [
  "api.first.org",
  "cdn.jsdelivr.net",
  "raw.githubusercontent.com",
  "services.nvd.nist.gov",
  "www.cisa.gov",
];

const FORBIDDEN_CODE = [
  ["Google Analytics or gtag", /googletagmanager|google-analytics|\bgtag\s*\(/i],
  ["Meta Pixel", /connect\.facebook\.net|\bfbq\s*\(/i],
  ["Hotjar", /hotjar|\bhj\s*\(/i],
  ["Microsoft Clarity", /clarity\.ms|\bclarity\s*\(/i],
  ["advertising SDK", /doubleclick\.net|googlesyndication|adsbygoogle/i],
  ["fingerprinting library", /fingerprintjs|clientjs|deviceprint/i],
  ["canvas fingerprinting", /\.toDataURL\s*\(|getImageData\s*\(/i],
  ["audio fingerprinting", /\b(?:AudioContext|OfflineAudioContext)\s*\(/i],
  ["device enumeration", /enumerateDevices\s*\(|navigator\.(?:plugins|mimeTypes)/i],
  ["WebRTC fingerprinting", /\bRTCPeerConnection\s*\(/i],
  ["cookie access", /document\.cookie/i],
  ["IndexedDB access", /\bindexedDB\s*[.(]/i],
  ["service-worker registration", /serviceWorker\s*\.\s*register\s*\(/i],
  ["embedded document", /<\s*(?:iframe|embed|object)\b/i],
  ["visitor form", /<\s*form\b/i],
];

async function sourceFiles(relativeDirectory) {
  const directory = path.join(ROOT, relativeDirectory);
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const relativePath = path.join(relativeDirectory, entry.name);
    if (entry.isDirectory()) files.push(...(await sourceFiles(relativePath)));
    else if (SOURCE_EXTENSIONS.has(path.extname(entry.name))) files.push(relativePath);
  }
  return files;
}

test("source contains no tracking, advertising, fingerprinting, embeds or forms", async () => {
  const files = (await Promise.all(SCAN_ROOTS.map(sourceFiles))).flat();
  for (const relativePath of files) {
    const source = await readFile(path.join(ROOT, relativePath), "utf8");
    for (const [label, pattern] of FORBIDDEN_CODE) {
      assert.doesNotMatch(source, pattern, `${label} found in ${relativePath}`);
    }
  }
});

test("all literal external hosts require an explicit approval", async () => {
  const files = (await Promise.all(SCAN_ROOTS.map(sourceFiles))).flat();
  const found = new Set();
  for (const relativePath of files) {
    const source = await readFile(path.join(ROOT, relativePath), "utf8");
    for (const match of source.matchAll(/https:\/\/([a-z0-9.-]+)/gi)) {
      found.add(match[1].toLowerCase());
    }
  }
  const unapproved = [...found].filter((host) => !APPROVED_EXTERNAL_HOSTS.has(host));
  assert.deepEqual(unapproved, [], `unapproved hosts: ${unapproved.join(", ")}`);
});

test("outbound server requests are restricted to the essential data hosts", async () => {
  const policy = await readFile(path.join(ROOT, "lib/network-policy.ts"), "utf8");
  const declared = [...policy.matchAll(/^\s+"([a-z0-9.-]+)",$/gim)].map(
    (match) => match[1],
  );
  assert.deepEqual(declared, ESSENTIAL_SERVER_HOSTS);
  assert.match(policy, /url\.protocol !== "https:"/);
  assert.match(policy, /essentialServerHosts\.has\(url\.hostname\)/);

  for (const relativePath of ["lib/data.ts", "lib/official-backup.ts"]) {
    const source = await readFile(path.join(ROOT, relativePath), "utf8");
    assert.doesNotMatch(source, /fetch\(\s*(?:url|currentUrl)\s*,/);
    assert.match(source, /fetch\(essentialServerUrl\(/);
  }
});

test("application source only persists the two documented local preferences", async () => {
  const files = (await Promise.all(SCAN_ROOTS.map(sourceFiles))).flat();
  const storageFiles = [];
  for (const relativePath of files) {
    const source = await readFile(path.join(ROOT, relativePath), "utf8");
    if (/window\.localStorage|\.(?:getItem|setItem|removeItem)\(/.test(source)) {
      storageFiles.push(relativePath);
    }
    assert.doesNotMatch(
      source,
      /window\.sessionStorage|sessionStorage\s*\.\s*(?:getItem|setItem|removeItem)\s*\(/,
      `sessionStorage API found in ${relativePath}`,
    );
  }
  assert.deepEqual(storageFiles, ["lib/local-preferences.ts"]);

  const helper = await readFile(path.join(ROOT, "lib/local-preferences.ts"), "utf8");
  assert.match(helper, /"cyberdailylog-language"/);
  assert.match(helper, /"cyberdailylog-watchlist"/);
  assert.equal((helper.match(/\.getItem\(/g) ?? []).length, 2);
  assert.equal((helper.match(/\.setItem\(/g) ?? []).length, 2);
  assert.equal((helper.match(/\.removeItem\(/g) ?? []).length, 2);

  const dashboard = await readFile(path.join(ROOT, "app/components/dashboard.tsx"), "utf8");
  assert.match(dashboard, /onClick=\{\(\) => changeLanguage\("en"\)\}/);
  assert.match(dashboard, /onClick=\{\(\) => changeLanguage\("es"\)\}/);
  assert.match(dashboard, /onWatchlist=\{toggleWatchlist\}/);
  assert.doesNotMatch(dashboard, /cyberdailylog-(?:language|watchlist)/);
});

test("production client adds only Vinext's documented session reload guard", async () => {
  const assetDirectory = path.join(ROOT, "dist/client/assets");
  const assetNames = await readdir(assetDirectory);
  const scripts = assetNames.filter((name) => name.endsWith(".js"));
  const sessionStorageUsers = [];
  const localStorageUsers = [];

  for (const name of scripts) {
    const source = await readFile(path.join(assetDirectory, name), "utf8");
    if (/\bsessionStorage\b/.test(source)) sessionStorageUsers.push({ name, source });
    if (/\blocalStorage\b/.test(source)) localStorageUsers.push({ name, source });
    assert.doesNotMatch(source, /\bindexedDB\s*[.(]/i, `IndexedDB found in ${name}`);
    assert.doesNotMatch(source, /document\.cookie/i, `cookie access found in ${name}`);
    assert.doesNotMatch(
      source,
      /serviceWorker\s*\.\s*register\s*\(/i,
      `service-worker registration found in ${name}`,
    );
  }

  assert.equal(sessionStorageUsers.length, 1);
  assert.match(sessionStorageUsers[0].source, /__vinext_rsc_initial_reload__/);
  assert.equal(localStorageUsers.length, 1);
  assert.match(localStorageUsers[0].source, /cyberdailylog-language/);
  assert.match(localStorageUsers[0].source, /cyberdailylog-watchlist/);
});

test("production client contains no tracking or advertising SDK", async () => {
  const assetDirectory = path.join(ROOT, "dist/client/assets");
  const assetNames = await readdir(assetDirectory);
  const forbidden =
    /googletagmanager|google-analytics|\bgtag\s*\(|connect\.facebook\.net|\bfbq\s*\(|hotjar|clarity\.ms|doubleclick\.net|googlesyndication|adsbygoogle|fingerprintjs|deviceprint/i;

  for (const name of assetNames.filter((entry) => entry.endsWith(".js"))) {
    const source = await readFile(path.join(assetDirectory, name), "utf8");
    assert.doesNotMatch(source, forbidden, `forbidden SDK marker found in ${name}`);
  }
});

test("non-essential remote media and unused app authentication are absent", async () => {
  await assert.rejects(readFile(path.join(ROOT, "app/api/source-media/route.ts")));
  await assert.rejects(readFile(path.join(ROOT, "app/chatgpt-auth.ts")));
});

test("local preferences are never sent to application APIs", async () => {
  const dashboard = await readFile(
    path.join(ROOT, "app/components/dashboard.tsx"),
    "utf8",
  );
  assert.match(
    dashboard,
    /fetch\("\/api\/intelligence",\s*\{[^}]*credentials:\s*"omit"[^}]*referrerPolicy:\s*"no-referrer"/s,
  );

  for (const relativePath of [
    "app/api/intelligence/route.ts",
    "app/api/export/route.ts",
  ]) {
    const source = await readFile(path.join(ROOT, relativePath), "utf8");
    assert.doesNotMatch(source, /local-preferences|cyberdailylog-language|cyberdailylog-watchlist/);
  }
});
