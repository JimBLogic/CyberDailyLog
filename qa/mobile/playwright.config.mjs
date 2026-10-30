import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests', timeout: 90000, expect: { timeout: 15000 },
  retries: 0, workers: 2, fullyParallel: true,
  reporter: [['list'], ['html', { open: 'never' }], ['json', { outputFile: 'test-results/results.json' }]],
  use: { browserName: 'chromium', baseURL: 'https://cyberdailylog.jimblogic.chatgpt.site',
    locale: 'es-ES', timezoneId: 'Europe/Madrid', isMobile: true, hasTouch: true,
    screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  projects: [360, 390, 412].flatMap(width => ['portrait', 'landscape'].flatMap(orientation =>
    ['light', 'dark'].map(colorScheme => ({ name: `${width}-${orientation}-${colorScheme}`,
      use: { colorScheme, viewport: orientation === 'portrait' ? { width, height: 844 } : { width: 844, height: width } }
    }))))
});
