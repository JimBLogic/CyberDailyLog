# CyberDailyLog

[![Daily Blue Team Intelligence](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml/badge.svg)](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml)

CyberDailyLog is an automated, transparent and curated 24-hour Blue Team intelligence pipeline. It collects trusted cybersecurity sources, enriches and correlates vulnerability data, adds clearly separated expert and community context, ranks actionable developments and publishes reproducible daily reports.

**Live dashboard:** [CyberDailyLog Intelligence Dashboard](https://cyberdailylog.jimblogic.chatgpt.site) — dynamic risk distribution, historical signal, collector health, ranked triage, EN/ES interface and portable JSON/CSV exports.

<!-- CYBERDAILYLOG:DAILY:START -->
## Latest automated brief

**Updated:** 2026-09-18T05:34:07+00:00  
**Coverage:** 2026-09-17T05:33:00+00:00 → 2026-09-18T05:33:00+00:00  
**Pipeline:** **Operational**

37 item(s) include exploitation, KEV or ransomware signals.

- **Assessed:** 150 source-backed developments
- **Above threshold:** 72
- Core sources: **2/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

### Highest-priority items

- **[CVE-2026-20316](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 10.0/10** — CVE-2026-20316 exploited in CISA KEV: Cisco Secure Firewall Management Center (FMC) — CVSS 5.3; EPSS percentile &gt;= 95%
- **[CVE-2026-72898](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-72898 exploited in CISA KEV: Metabase Metabase — CVSS 10.0; EPSS &gt;= 70%
- **[CVE-2026-63077](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-63077 exploited in CISA KEV: JetBrains TeamCity — CVSS 9.8; EPSS &gt;= 70%
- **[CVE-2026-63030](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-63030 exploited in CISA KEV: WordPress Core — CVSS 9.8; EPSS &gt;= 70%
- **[CVE-2026-16232](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-16232 exploited in CISA KEV: Check Point SmartConsole — CVSS 9.1; EPSS &gt;= 70%

### Human context

**[ISC Stormcast For Friday, September 18th, 2026 https://isc.sans.edu/podcastdetail/10100, (Fri, Sep 18th)](https://isc.sans.edu/diary/rss/33350)**
SANS Internet Storm Center Handler&#x27;s Diary  
> (c) SANS Internet Storm Center. https://isc.sans.edu Creative Commons Attribution-Noncommercial 3.0 United States License.

### Community pulse

**[Hister: A private search engine for the pages you visit and the files you keep](https://github.com/asciimoo/hister)** — Hacker News · 539 points · 142 comments
[Open discussion](https://news.ycombinator.com/item?id=49743097)

[Open the concise report](reports/latest.md) · [Use the compact JSON feed](reports/portfolio-feed.json) · [Inspect source health](reports/source-health.json) · [Integration guide](docs/INTEGRATION.md)
<!-- CYBERDAILYLOG:DAILY:END -->

## Use the data

- **Human brief:** [`reports/latest.md`](reports/latest.md)
- **Compact integration feed:** [`reports/portfolio-feed.json`](reports/portfolio-feed.json)
- **Compact-feed contract:** [`schemas/portfolio-feed.schema.json`](schemas/portfolio-feed.schema.json)
- **Dashboard history feed:** [`reports/dashboard-feed.json`](reports/dashboard-feed.json)
- **Dashboard-feed contract:** [`schemas/dashboard-feed.schema.json`](schemas/dashboard-feed.schema.json)
- **Complete evidence JSON:** [`reports/latest.json`](reports/latest.json)
- **Collector health:** [`reports/source-health.json`](reports/source-health.json)
- **Publication timing and SLO:** [`reports/publication-timing.json`](reports/publication-timing.json)
- **CTI state and reliability design:** [`docs/cti-reliability.md`](docs/cti-reliability.md)
- **Daily archive:** [`reports/archive/`](reports/archive/)
- **Integration examples:** [`docs/INTEGRATION.md`](docs/INTEGRATION.md)
- **Full-stack dashboard:** [`dashboard/`](dashboard/)
- **Dashboard architecture and local setup:** [`docs/DASHBOARD.md`](docs/DASHBOARD.md)

The compact feed is designed for portfolios, static websites, dashboards and other repositories. It exposes ranked vulnerabilities plus one optional expert-context item and one optional community-pulse item, while the complete JSON remains the source of truth.

The dashboard is a separate full-stack presentation layer in this same repository. Its backend reads the generated public artifacts, derives complete-distribution charts from `latest.json`, and uses `dashboard-feed.json` for the rolling history. The Python pipeline remains independently runnable; the website is a consumer, not a replacement.

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

`.github/workflows/daily-intelligence.yml` targets 12:00 Europe/Madrid, with idempotent recovery at 12:17 and 13:30. The timezone-aware schedule follows Madrid daylight-saving changes automatically. Publication is measured against a rolling 30-day objective of at least 95% within 60 minutes; this is a monitored objective, not a scheduler guarantee. Manual runs publish by default; set `dry_run=true` for a preview. Changes to the pipeline, configuration or workflow also trigger a freshness check and collection when needed. Every publication requires the source quorum and writes generated README/report outputs with the built-in `GITHUB_TOKEN`.

The durable per-CVE ledger preserves observations and material transitions, including KEV entry, confirmed exploitation, ransomware, vendor evidence, public exploit references, severity and remediation changes. Unchanged CVEs are not presented as daily discoveries. Unknown evidence stays unknown, and an optional-source outage does not erase previously confirmed intelligence. See [CTI state and reliability](docs/cti-reliability.md) for migration, timing evidence and operating limits.

CyberDailyLog stores defensive metadata, short attributed feed excerpts and official links. It does not execute exploit code, download malware, bypass access controls or print credentials.
