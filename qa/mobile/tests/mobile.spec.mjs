import { test, expect } from '@playwright/test';

test('public mobile journey: layout, touch navigation, search, detail, recovery', async ({ page }, info) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const response = await page.goto('/', { waitUntil: 'networkidle' });
  expect(response.status()).toBe(200);
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  await page.getByRole('button', { name: 'Español', exact: true }).tap();
  const theme = info.project.use.colorScheme;
  if (await page.locator('html').getAttribute('data-theme') !== theme) {
    await page.locator('.theme-toggle').tap();
  }
  await expect(page.locator('html')).toHaveAttribute('data-theme', theme);
  await expect(page.locator('meta[name="viewport"]')).toHaveAttribute('content', /width=device-width/);
  expect(await page.evaluate(() => navigator.maxTouchPoints)).toBeGreaterThan(0);
  expect(await page.evaluate(() => innerWidth)).toBe(info.project.use.viewport.width);

  async function audit(label) {
    await page.evaluate(() => document.fonts.ready);
    const layout = await page.evaluate(() => ({ width: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      brokenImages: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src) }));
    await info.attach(`${label}-layout`, { body: JSON.stringify(layout), contentType: 'application/json' });
    await page.screenshot({ path: info.outputPath(`${label}.png`), fullPage: true });
    expect.soft(layout.scrollWidth, `${label}: page must not overflow horizontally`).toBeLessThanOrEqual(layout.width + 1);
    expect.soft(layout.brokenImages, `${label}: broken images`).toEqual([]);
  }
  await audit('home');
  await page.getByRole('navigation').getByRole('button', { name: 'Prioridades', exact: true }).tap();
  await expect(page).toHaveURL(/#vulnerabilities$/);
  const search = page.getByRole('searchbox');
  await expect(search).toBeVisible();
  const first = page.locator('.vulnerability-main').first();
  const name = await first.getAttribute('aria-label');
  const id = name.match(/CVE-\d{4}-\d+/)?.[0];
  expect(id, 'live feed must expose a searchable CVE').toBeTruthy();
  await search.fill(id);
  await expect(first).toHaveAttribute('aria-label', new RegExp(id));
  await first.tap();
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('heading', { level: 2 })).toHaveText(id);
  await audit('detail');
  await dialog.getByRole('button', { name: 'Cerrar', exact: true }).tap();
  await expect(dialog).not.toBeVisible();
  await audit('priorities');
  for (const [name, hash] of [['Fuentes','sources'], ['Método','methodology'], ['Proyecto','engineering']]) {
    await page.getByRole('navigation').getByRole('button', { name, exact: true }).tap();
    await expect(page).toHaveURL(new RegExp(`#${hash}$`));
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await audit(hash);
  }
  const recovery = page.locator('summary').filter({ hasText: 'Intento inicial observado y reintentos' });
  await expect(recovery).toBeVisible();
  await recovery.tap();
  const region = page.getByRole('region', { name: 'Telemetría de recuperación' });
  await expect(region).toBeVisible();
  await expect(region.locator('thead th')).toHaveText(['run_id','trigger','started_at','finished_at','outcome','recovered_from','publication_id']);
  await expect(region).toHaveAttribute('tabindex', '0');
  await audit('recovery');
  expect(errors, 'uncaught application errors').toEqual([]);
});
