# Troubleshooting

CyberDailyLog was refactored on 2026-07-15 for the Blue Team intelligence mission.

## Key points

- The old active project mixed a personal CSV diary with a static intelligence report.
- Static scripts contained hard-coded CVE identifiers and certification offers, selected entries randomly, appended one Markdown archive, and performed Git publishing from scripts.
- The new architecture uses `src/cyberdailylog`, typed models, official-source collectors, correlation, deterministic scoring, report renderers, source health, and fixture-backed tests.
- Ranking assists prioritisation and does not replace analyst judgement or environment-specific risk assessment.

## Operational notes

Use `python -m cyberdailylog run --offline-fixtures --output-dir tmp/reports` for deterministic local output. Use `python -m cyberdailylog run --lookback-hours 24` for live collection when network access and optional tokens are available.
