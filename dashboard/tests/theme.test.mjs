import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";
import ts from "typescript";

const source = readFileSync(new URL("../lib/local-preferences.ts", import.meta.url), "utf8");
function preferences({ blocked = false, initial = {} } = {}) {
  const values = new Map(Object.entries(initial));
  const window = new EventTarget();
  Object.defineProperty(window, "localStorage", { get() {
    if (blocked) throw new Error("Storage blocked");
    return { getItem: key => values.get(key) ?? null, setItem: (key,value) => values.set(key,value), removeItem: key => values.delete(key) };
  }});
  const document = { documentElement: { dataset: {} } };
  const context = { exports: {}, window, document, Event };
  vm.runInNewContext(ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, context);
  return { api: context.exports, values, window, document, context };
}

test("theme defaults to light without writing storage; invalid preferences are ignored", () => {
  const { api, values } = preferences({ initial: { "cyberdailylog-theme": "unknown" } });
  assert.equal(api.readThemePreference(), null);
  assert.equal(api.themeSnapshot(), "light");
  assert.equal(values.get("cyberdailylog-theme"), "unknown");
});

test("theme persists and clearing preferences restores light without removing unrelated storage", () => {
  const p = preferences({ initial: { unrelated: "keep", "cyberdailylog-language": "en", "cyberdailylog-watchlist": '["CVE-2026-1"]' } });
  let changes = 0;
  const stop = p.api.subscribeThemePreference(() => changes++);
  p.api.saveThemePreference("dark");
  assert.equal(p.api.themeSnapshot(), "dark");
  assert.equal(p.document.documentElement.dataset.theme, "dark");
  assert.equal(p.values.get("cyberdailylog-theme"), "dark");
  p.api.clearLocalPreferences();
  assert.equal(p.api.themeSnapshot(), "light");
  assert.equal(p.document.documentElement.dataset.theme, "light");
  assert.deepEqual([...p.values], [["unrelated", "keep"]]);
  assert.equal(changes, 2);
  stop();
  p.api.saveThemePreference("dark");
  assert.equal(changes, 2);
});

test("theme works for the current visit when storage is blocked", () => {
  const p = preferences({ blocked: true });
  p.api.saveThemePreference("dark");
  assert.equal(p.api.themeSnapshot(), "dark");
  p.api.clearLocalPreferences();
  assert.equal(p.api.themeSnapshot(), "light");
  assert.doesNotThrow(() => vm.runInNewContext(p.api.THEME_BOOTSTRAP_SCRIPT, p.context));
});

test("bootstrap restores dark before hydration and other tabs can change the preference", () => {
  const p = preferences({ initial: { "cyberdailylog-theme": "dark" } });
  vm.runInNewContext(p.api.THEME_BOOTSTRAP_SCRIPT, p.context);
  assert.equal(p.document.documentElement.dataset.theme, "dark");
  let changes = 0;
  const stop = p.api.subscribeThemePreference(() => changes++);
  p.api.saveThemePreference("dark");
  p.values.set("cyberdailylog-theme", "light");
  const event = new Event("storage");
  Object.defineProperty(event, "key", { value: "cyberdailylog-theme" });
  p.window.dispatchEvent(event);
  assert.equal(p.api.themeSnapshot(), "light");
  assert.equal(p.document.documentElement.dataset.theme, "light");
  assert.equal(changes, 2);
  stop();
});

const css = readFileSync(new URL("../app/globals.css", import.meta.url), "utf8");
const luminance = hex => {
  const channels = hex.match(/[a-f0-9]{2}/gi).map(x => parseInt(x,16)/255).map(x => x <= .04045 ? x/12.92 : ((x+.055)/1.055)**2.4);
  return channels[0]*.2126 + channels[1]*.7152 + channels[2]*.0722;
};
const ratio = (a,b) => { const l = [luminance(a),luminance(b)].sort((x,y)=>y-x); return (l[0]+.05)/(l[1]+.05); };
for (const mode of ["light", "dark"]) {
  test(`${mode} text, links, status colors and primary controls meet 4.5:1 token contrast`, () => {
    const block = mode === "light" ? css.match(/:root \{([^}]+)\}/)[1] : css.match(/:root\[data-theme="dark"\] \{([^}]+)\}/)[1];
    const tokens = Object.fromEntries([...block.matchAll(/--([\w-]+):\s*(#[a-f0-9]{6})/gi)].map(m=>[m[1],m[2]]));
    for (const foreground of ["ink", "muted", "body-muted", "blue", "red", "green", "orange", "warning-ink", "expert-ink"]) {
      for (const background of ["paper", "paper-light"]) {
        assert.ok(ratio(tokens[foreground],tokens[background]) >= 4.5, `${foreground} on ${background} is below 4.5:1`);
      }
    }
    assert.ok(ratio(tokens["on-accent"],tokens.blue) >= 4.5);
    assert.ok(ratio(tokens["on-ink"],tokens.ink) >= 4.5);
  });
}

// Check the component's actual color binding, not just unrelated palette pairs.
for (const mode of ["light", "dark"]) {
  test(`${mode} proof heading contrasts with its persistent dark panel and gradient`, () => {
    const base = css.match(/:root \{([^}]+)\}/)[1];
    const overrides = mode === "dark" ? css.match(/:root\[data-theme="dark"\] \{([^}]+)\}/)[1] : "";
    const tokens = Object.fromEntries([...`${base}${overrides}`.matchAll(/--([\w-]+):\s*([^;]+);/g)].map(m => [m[1], m[2].trim()]));
    const heading = [...css.matchAll(/\.proof-story h2\s*\{([^}]+)\}/g)].map(m => m[1]).join(";");
    const foregroundToken = heading.match(/color:\s*var\(--([\w-]+)\)/)[1];
    const panel = css.match(/\.interview-proof\s*\{([^}]+)\}/)[1];
    const backgroundToken = panel.match(/var\(--([\w-]+)\);/)[1];
    const foreground = tokens[foregroundToken];
    const background = tokens[backgroundToken];
    assert.ok(ratio(foreground, background) >= 4.5, `${foregroundToken} on ${backgroundToken} is below 4.5:1`);
    const alpha = Number(panel.match(/accent-rgb\) \/ ([\d.]+)/)[1]);
    const accent = tokens["accent-rgb"].split(/\s+/).map(Number);
    const baseRgb = background.match(/[a-f0-9]{2}/gi).map(x => parseInt(x, 16));
    const gradientPeak = "#" + baseRgb.map((v, i) => Math.round(v * (1 - alpha) + accent[i] * alpha).toString(16).padStart(2, "0")).join("");
    assert.ok(ratio(foreground, gradientPeak) >= 4.5, "Heading fails on the brightest gradient stop");
  });
}
