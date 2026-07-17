# CyberDailyLog

[![Daily Blue Team Intelligence](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml/badge.svg)](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml)

CyberDailyLog is an automated, transparent and curated 24-hour Blue Team intelligence pipeline. It collects trusted cybersecurity sources, correlates vulnerability and exploitation data, ranks actionable developments, and publishes reproducible daily reports.

The current report lives at [`reports/latest.md`](reports/latest.md); the README deliberately does not embed a manually maintained latest summary.

## What it collects

- Tier 1 structured sources: CISA KEV, NVD CVE API 2.0, FIRST EPSS, and GitHub-reviewed public security advisories.
- Tier 2 official RSS/Atom advisories configured in `config/sources.yml`.
- Tier 3 allowlisted defensive GitHub releases such as SigmaHQ Sigma, Elastic detection rules, and Wazuh.

## What it excludes

The active pipeline excludes personal progress tracking, certification-offer scraping, arbitrary search results, proof-of-concept exploitation feeds, malware downloads, LLM-generated claims, and sources that require commercial access or fragile scraping.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m cyberdailylog run --offline-fixtures --output-dir tmp/reports
python -m cyberdailylog validate --output-dir tmp/reports
python -m cyberdailylog.portfolio_feed \
  --report tmp/reports/latest.json \
  --output tmp/reports/portfolio-feed.json
```

A real run is:

```bash
python -m cyberdailylog run --lookback-hours 24
python -m cyberdailylog.portfolio_feed
```

Optional secrets are documented in `.env.example`: `NVD_API_KEY` and `GITHUB_TOKEN`. No repository secret is required for local offline fixture mode.

## Reports

The pipeline writes:

- `reports/latest.md`: the complete human-readable daily brief;
- `reports/latest.json`: the complete structured report and provenance payload;
- `reports/portfolio-feed.json`: a compact, stable JSON view for the public portfolio and other lightweight clients;
- `reports/source-health.json`: collector health and sanitized errors;
- dated archive files under `reports/archive/YYYY/MM/`.

The compact portfolio feed contains coverage timestamps, generation time, the qualified-item count, immediate-attention status, source-health totals and the five highest-ranked vulnerabilities. It avoids making a static website download the full daily report while preserving links to the complete brief and repository.

## Scoring transparency

Scoring is deterministic and configurable in `config/scoring.yml`. It boosts confirmed exploitation, CISA KEV entries, known ransomware use, high CVSS, high EPSS, official sources, priority technology categories, and detection opportunities. Ranking assists prioritisation but does not replace asset-specific risk assessment.

## Provenance and source health

Every canonical item keeps field-level provenance where collectors provide important values. Every run creates source-health records with status, timing, accepted/rejected counts, HTTP status when available, and sanitized errors.

## Daily workflow

`.github/workflows/daily-intelligence.yml` runs at 06:17 UTC and can also be dispatched manually. The workflow owns committing generated reports with the built-in `GITHUB_TOKEN`; the Python application never runs `git push`.

## Security and copyright

CyberDailyLog stores metadata, identifiers, official links, and conservative defensive context. It does not download malware, execute exploit code, bypass access controls, republish full articles, or print secrets.

## Relationship to homelab work

This repository is independently useful and is not coupled to any Raspberry Pi or private homelab repository. `config/technologies.yml` is an editorial relevance list, not a claim about the maintainer's environment.

## Current status

Live GitHub Actions generation is operating on `main`, and the public portfolio feed updates from the generated reports. Unit tests continue to use deterministic fixtures. Review [`reports/source-health.json`](reports/source-health.json) alongside each report because optional sources can degrade independently without invalidating healthy required-source coverage.
