# CyberDailyLog

[![Daily Blue Team Intelligence](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml/badge.svg)](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml)

CyberDailyLog is an automated, transparent and curated 24-hour Blue Team intelligence pipeline. It collects trusted cybersecurity sources, enriches and correlates vulnerability data, ranks actionable developments and publishes reproducible daily reports.

<!-- CYBERDAILYLOG:DAILY:START -->
## Latest automated brief

**Updated:** 2026-07-19T08:32:33+00:00  
**Coverage:** 2026-07-18T08:32:31+00:00 → 2026-07-19T08:32:31+00:00  
**Pipeline:** **Operational**

No confirmed exploitation, CISA KEV or ransomware-linked item qualified.

- **Assessed:** 100 source-backed developments
- **Above threshold:** 59
- Core sources: **3/3 healthy**. Optional sources: **2 healthy**, **1 degraded**.

### Highest-priority items

- **[CVE-2026-16117](https://nvd.nist.gov/vuln/detail/CVE-2026-16117) · 10.0/10** — Impact: @fastify/http-proxy versions up to and including 11.5.0 fail to rewrite the request prefix when the prefix segme — critical CVSS +20; official source +5
- **[CVE-2026-47865](https://nvd.nist.gov/vuln/detail/CVE-2026-47865) · 9.8/10** — VMware Avi Load Balancer contains an authentication bypass vulnerability. A malicious user with network access may be ab — critical CVSS +20; official source +5
- **[CVE-2025-71392](https://nvd.nist.gov/vuln/detail/CVE-2025-71392) · 9.4/10** — SurrealDB before 2.0.5, 2.1.x before 2.1.5, and 2.2.x before 2.2.2 fails to properly escape table and field names in the — critical CVSS +20; official source +5
- **[CVE-2026-9323](https://nvd.nist.gov/vuln/detail/CVE-2026-9323) · 9.2/10** — The urwid web display backend (urwid/display/web.py) generates web session identifiers (urwid_id) in Screen.start() by c — critical CVSS +20; official source +5
- **[CVE-2024-58366](https://nvd.nist.gov/vuln/detail/CVE-2024-58366) · 9.0/10** — SurrealDB before 1.1.1 contains a format string vulnerability in the rquickjs Exception::throw_type function when script — critical CVSS +20; official source +5

[Open the concise report](reports/latest.md) · [Use the compact JSON feed](reports/portfolio-feed.json) · [Inspect source health](reports/source-health.json) · [Integration guide](docs/INTEGRATION.md)
<!-- CYBERDAILYLOG:DAILY:END -->

## Use the data

- **Human brief:** [`reports/latest.md`](reports/latest.md)
- **Compact integration feed:** [`reports/portfolio-feed.json`](reports/portfolio-feed.json)
- **Compact-feed contract:** [`schemas/portfolio-feed.schema.json`](schemas/portfolio-feed.schema.json)
- **Complete evidence JSON:** [`reports/latest.json`](reports/latest.json)
- **Collector health:** [`reports/source-health.json`](reports/source-health.json)
- **Daily archive:** [`reports/archive/`](reports/archive/)
- **Integration examples:** [`docs/INTEGRATION.md`](docs/INTEGRATION.md)

The compact feed is designed for portfolios, static websites, dashboards and other repositories. It exposes a small ranked set with stable metadata and a downloadable JSON Schema contract, while the complete JSON remains the source of truth.

## What it collects

- Tier 1 structured sources: CISA KEV, NVD CVE API 2.0, FIRST EPSS and GitHub-reviewed public security advisories.
- Tier 2 official RSS/Atom advisories configured in `config/sources.yml`.
- Tier 3 allowlisted defensive GitHub releases such as SigmaHQ Sigma, Elastic detection rules and Wazuh.

## What it excludes

The active pipeline excludes arbitrary search results, proof-of-concept exploitation feeds, malware downloads, LLM-generated claims, commercial-only sources and fragile scraping.

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install .
python -m cyberdailylog run --offline-fixtures --output-dir tmp/reports
python -m cyberdailylog validate --output-dir tmp/reports
python -m cyberdailylog.portfolio_feed \
  --report tmp/reports/latest.json \
  --output tmp/reports/portfolio-feed.json
```

A real collection run is:

```bash
python -m cyberdailylog run --lookback-hours 24
python -m cyberdailylog.portfolio_feed
```

Optional secrets are documented in `.env.example`. Offline fixture mode requires no repository secret.

## Scoring and curation

The pipeline keeps two transparent signals:

- `selection_score`: the original deterministic source and evidence ranking;
- `priority_score`: a normalized 0–10 editorial triage score for human and lightweight-feed curation.

The human brief applies configurable limits and a minimum priority threshold. Lower-priority source-backed records remain available in the complete JSON.

## Provenance and source health

Canonical records retain field-level provenance where collectors provide important values. Every run records timing, accepted and rejected counts, sanitized failures and whether each source is required or optional.

## Automation and safety

`.github/workflows/daily-intelligence.yml` runs daily and can also be dispatched manually. Manual runs default to `dry_run=true`. Scheduled publication requires the source quorum and writes only generated README/report outputs with the built-in `GITHUB_TOKEN`.

CyberDailyLog stores defensive metadata and official links. It does not execute exploit code, download malware, bypass access controls or print credentials.
