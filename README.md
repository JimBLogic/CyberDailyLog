# CyberDailyLog

[![Daily Blue Team Intelligence](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml/badge.svg)](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml)

CyberDailyLog is an automated, transparent and curated 24-hour Blue Team intelligence pipeline. It collects trusted cybersecurity sources, enriches and correlates vulnerability data, adds clearly separated expert and community context, ranks actionable developments and publishes reproducible daily reports.

<!-- CYBERDAILYLOG:DAILY:START -->
## Latest automated brief

**Updated:** 2026-08-02T08:36:06+00:00  
**Coverage:** 2026-08-01T08:35:55+00:00 → 2026-08-02T08:35:55+00:00  
**Pipeline:** **Operational**

No confirmed exploitation, CISA KEV or ransomware-linked item qualified.

- **Assessed:** 143 source-backed developments
- **Above threshold:** 110
- Core sources: **3/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

### Highest-priority items

- **[CVE-2026-67305](https://nvd.nist.gov/vuln/detail/CVE-2026-67305) · 10.0/10** — FreeRDP Windows client before 3.29.0 contains a heap buffer overflow vulnerability in the clipboard virtual channel when — CVSS 9.4; priority technology: windows
- **[CVE-2026-8457](https://nvd.nist.gov/vuln/detail/CVE-2026-8457) · 10.0/10** — The WooCommerce - Social Login plugin for WordPress is vulnerable to Authentication Bypass in all versions up to and inc — CVSS 9.8; detection opportunity
- **[CVE-2026-15964](https://nvd.nist.gov/vuln/detail/CVE-2026-15964) · 10.0/10** — The Single Sign On For TNG plugin for WordPress is vulnerable to Authentication Bypass via unauthenticated password rese — CVSS 9.8; detection opportunity
- **[CVE-2026-67336](https://nvd.nist.gov/vuln/detail/CVE-2026-67336) · 9.7/10** — better-auth versions before 1.6.11 contain insecure cryptographic defaults in the oidcProvider and mcp plugins that adve — CVSS 9.4; detection opportunity
- **[CVE-2026-67330](https://nvd.nist.gov/vuln/detail/CVE-2026-67330) · 9.7/10** — @better-auth/scim (a better-auth plugin) versions &gt;= 1.4.0-beta.27 through &lt;= 1.6.21 and &gt;= 1.7.0-beta.0 through &lt;= 1.7. — CVSS 9.4; detection opportunity

### Human context

**[Atomic MacOS (AMOS) stealer infection, (Sun, Aug 2nd)](https://isc.sans.edu/diary/rss/33208)**
SANS Internet Storm Center Handler&#x27;s Diary  
> Introduction

### Community pulse

**[Show HN: I&#x27;m a 15 Year Old Wannabe Engineer, This Is a Cycloidal Gearbox I Built](https://github.com/tom-ilan/cycloidal_gearbox)** — Hacker News · 139 points · 26 comments
[Open discussion](https://news.ycombinator.com/item?id=49140396)

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

The compact feed is designed for portfolios, static websites, dashboards and other repositories. It exposes ranked vulnerabilities plus one optional expert-context item and one optional community-pulse item, while the complete JSON remains the source of truth.

## What it collects

- Tier 1 structured sources: CISA KEV, NVD CVE API 2.0, FIRST EPSS and GitHub-reviewed public security advisories.
- Curated expert and analyst RSS context from Krebs on Security and the SANS Internet Storm Center Handler's Diary.
- A strictly filtered Hacker News community signal using the official API, engagement thresholds and security-topic matching.
- Allowlisted defensive GitHub releases such as SigmaHQ Sigma, Elastic detection rules and Wazuh.

## Trust boundaries

Threat intelligence, expert commentary and community interest are deliberately separated:

- CVE, KEV, EPSS and official advisories remain evidence-bearing security data;
- RSS excerpts are short, attributed, publisher-provided context and never scraped from article bodies;
- Hacker News entries are labelled as community signals and must be checked against primary sources.

## What it excludes

The active pipeline excludes arbitrary search results, proof-of-concept exploitation feeds, malware downloads, LLM-generated claims, commercial-only sources, article-body scraping and unreviewed social-media ingestion.

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

The human brief applies configurable limits and a minimum priority threshold. Lower-priority source-backed records remain available in the complete JSON. Expert commentary and Hacker News engagement are displayed in dedicated sections and are not represented as verified risk scores.

## Provenance and source health

Canonical records retain field-level provenance where collectors provide important values. Every run records timing, accepted and rejected counts, sanitized failures and whether each source is required or optional.

## Automation and safety

`.github/workflows/daily-intelligence.yml` publishes at 08:17 Europe/Madrid, with an idempotent 09:47 recovery schedule if the first event is delayed or dropped. Manual runs publish by default; set `dry_run=true` for a preview. Every publication requires the source quorum and writes only generated README/report outputs with the built-in `GITHUB_TOKEN`.

CyberDailyLog stores defensive metadata, short attributed feed excerpts and official links. It does not execute exploit code, download malware, bypass access controls or print credentials.
