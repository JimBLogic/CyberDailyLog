# CyberDailyLog

[![Daily Blue Team Intelligence](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml/badge.svg)](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml)

CyberDailyLog is an automated, transparent and curated 24-hour Blue Team intelligence pipeline. It collects trusted cybersecurity sources, enriches and correlates vulnerability data, adds clearly separated expert and community context, ranks actionable developments and publishes reproducible daily reports.

<!-- CYBERDAILYLOG:DAILY:START -->
## Latest automated brief

**Updated:** 2026-07-26T08:38:41+00:00  
**Coverage:** 2026-07-25T08:38:35+00:00 → 2026-07-26T08:38:35+00:00  
**Pipeline:** **Operational**

No confirmed exploitation, CISA KEV or ransomware-linked item qualified.

- **Assessed:** 289 source-backed developments
- **Above threshold:** 6
- Core sources: **3/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

### Highest-priority items

- **[CVE-2026-66012](https://nvd.nist.gov/vuln/detail/CVE-2026-66012) · 10.0/10** — SiYuan before v3.7.2 contains a missing authorization vulnerability in the POST /mcp kernel endpoint, which is gated onl — CVSS 10.0; priority technology: linux
- **[CVE-2026-66013](https://nvd.nist.gov/vuln/detail/CVE-2026-66013) · 9.6/10** — OpenRemote before 1.26.2 contains an authentication bypass vulnerability in the console registration API that allows una — CVSS 9.3; detection opportunity
- **[CVE-2026-15962](https://nvd.nist.gov/vuln/detail/CVE-2026-15962) · 9.1/10** — The Fluent Forms Pro Add On Pack plugin for WordPress is vulnerable to PHP Object Injection in all versions up to, and i — CVSS 8.8; detection opportunity
- **[CVE-2026-63720](https://nvd.nist.gov/vuln/detail/CVE-2026-63720) · 7.8/10** — datamodel-code-generator prior to version 0.70.0 contains a code injection vulnerability that allows attackers who contr — CVSS 7.5; detection opportunity
- **[CVE-2026-10681](https://nvd.nist.gov/vuln/detail/CVE-2026-10681) · 7.2/10** — In Zephyr&#x27;s userspace dynamic-objects subsystem, thread_idx_alloc() in kernel/userspace/userspace.c allocated a new thre — CVSS 6.5; priority technology: linux

### Community pulse

**[Running a 28.9M parameter LLM on an $8 microcontroller](https://github.com/slvDev/esp32-ai)** — Hacker News · 174 points · 37 comments
[Open discussion](https://news.ycombinator.com/item?id=49050512)

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
