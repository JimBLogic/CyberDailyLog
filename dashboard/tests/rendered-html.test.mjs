import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("renders the CyberDailyLog product shell", async () => {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  const response = await worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );

  assert.equal(response.status, 200);
  assert.match(
    response.headers.get("content-type") ?? "",
    /^text\/html\b/i,
  );
  const html = await response.text();
  assert.match(html, /CyberDailyLog/);
  assert.match(html, /Inteligencia Blue Team diaria/i);
  assert.match(html, /Entiende la amenaza/i);
  assert.match(html, /Estado de los datos/i);
  assert.match(html, /rel="canonical"/i);
  assert.match(html, /https:\/\/cyberdailylog\.jimblogic\.chatgpt\.site/i);
  assert.doesNotMatch(html, /cyberdailylog-dashboard\.jimblogic\.chatgpt\.site/i);
  assert.match(html, /application\/ld\+json/i);
  assert.match(html, /SecurityApplication/i);
  assert.match(
    html,
    /(Conectado al repositorio|Respaldo oficial activo|Informe de respaldo verificado)/i,
  );
  assert.match(html, /Proyecto/i);
  assert.match(html, /role="group"[^>]*aria-label="Idioma"/i);
  assert.match(html, /aria-label="English"[^>]*aria-pressed="false"/i);
  assert.match(html, /aria-label="Español"[^>]*aria-pressed="true"/i);
  assert.doesNotMatch(html, /(1 ene 1970|Jan 1, 1970|Invalid Date)/i);
  assert.doesNotMatch(html, /Protección por delante/i);
  assert.doesNotMatch(html, /Starter Project/);

  const apiResponse = await worker.fetch(
    new Request("http://localhost/api/intelligence"),
    {
      ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) },
    },
    { waitUntil() {}, passThroughOnException() {} },
  );
  assert.equal(apiResponse.status, 200);
  const data = await apiResponse.json();
  assert.ok(Array.isArray(data.deliveryChain));
  assert.deepEqual(
    data.deliveryChain.map((item) => item.id),
    ["github-raw", "jsdelivr-cdn", "official-apis", "bundled-snapshot"],
  );
  assert.ok(
    ["live", "official-backup", "repository-snapshot"].includes(data.dataMode),
  );
  assert.ok(["high", "medium", "low"].includes(data.coverageConfidence));
  assert.ok(
    ["sufficient", "limited", "insufficient"].includes(data.coverageState),
  );
  assert.ok(
    data.deliveryChain.every((item) =>
      ["used", "available", "failed", "skipped", "cooldown"].includes(item.status),
    ),
  );
});

test("publishes crawl directives and a daily sitemap", async () => {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("seo-test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  const env = {
    ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) },
  };
  const ctx = { waitUntil() {}, passThroughOnException() {} };

  const robotsResponse = await worker.fetch(
    new Request("http://localhost/robots.txt"),
    env,
    ctx,
  );
  assert.equal(robotsResponse.status, 200);
  const robots = await robotsResponse.text();
  assert.match(
    robots,
    /Sitemap: https:\/\/cyberdailylog\.jimblogic\.chatgpt\.site\/sitemap\.xml/i,
  );
  assert.doesNotMatch(robots, /cyberdailylog-dashboard/i);

  const sitemapResponse = await worker.fetch(
    new Request("http://localhost/sitemap.xml"),
    env,
    ctx,
  );
  assert.equal(sitemapResponse.status, 200);
  const sitemap = await sitemapResponse.text();
  assert.match(sitemap, /<changefreq>daily<\/changefreq>/i);
  assert.match(sitemap, /https:\/\/cyberdailylog\.jimblogic\.chatgpt\.site/i);
  assert.doesNotMatch(sitemap, /cyberdailylog-dashboard/i);
});

test("keeps language controls touch-ready on mobile", async () => {
  const css = await readFile(
    new URL("../app/globals.css", import.meta.url),
    "utf8",
  );

  assert.doesNotMatch(
    css,
    /\.language-toggle\s*\{\s*display:\s*none/i,
    "the language selector must never be hidden on small screens",
  );
  assert.match(
    css,
    /\.language-toggle button\s*\{[^}]*min-width:\s*44px[^}]*min-height:\s*44px/is,
  );
  assert.match(css, /touch-action:\s*manipulation/i);
  assert.match(css, /overscroll-behavior-x:\s*contain/i);
});
