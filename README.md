# CyberDailyLog

[![Daily Blue Team Intelligence](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml/badge.svg)](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml)

CyberDailyLog is an automated, transparent and curated 24-hour Blue Team intelligence pipeline. It collects trusted cybersecurity sources, enriches and correlates vulnerability data, adds clearly separated expert and community context, ranks actionable developments and publishes reproducible daily reports.

<!-- CYBERDAILYLOG:DAILY:START -->
## Latest automated brief

**Updated:** 2026-08-05T08:50:25+00:00  
**Coverage:** 2026-08-04T08:50:19+00:00 → 2026-08-05T08:50:19+00:00  
**Pipeline:** **Operational**

No confirmed exploitation, CISA KEV or ransomware-linked item qualified.

- **Assessed:** 383 source-backed developments
- **Above threshold:** 254
- Core sources: **3/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

### Highest-priority items

- **[CVE-2026-71214](https://nvd.nist.gov/vuln/detail/CVE-2026-71214) · 10.0/10** — The Aerie/PlanDev sequencing-server&#x27;s authorization middleware (sequencing-server/src/app.ts) derives the caller&#x27;s Hasur — CVSS 9.8; detection opportunity
- **[CVE-2026-71207](https://nvd.nist.gov/vuln/detail/CVE-2026-71207) · 10.0/10** — The Stock-Inventory-Management-System application&#x27;s login.php assigns raw $_POST username/password values to $_SESSION a — CVSS 9.8; detection opportunity
- **[CVE-2026-45538](https://nvd.nist.gov/vuln/detail/CVE-2026-45538) · 10.0/10** — OpenSIPS is a Session Initiation Protocol (SIP) server implementation. In versions 4.0.0 and prior, processing a SIP mes — CVSS 9.8; detection opportunity
- **[CVE-2026-70477](https://nvd.nist.gov/vuln/detail/CVE-2026-70477) · 9.8/10** — Flowise is a drag &amp; drop user interface to build a customized large language model flow. Prior to 3.1.3, a prompt inject — CVSS 9.5; detection opportunity
- **[CVE-2026-70376](https://nvd.nist.gov/vuln/detail/CVE-2026-70376) · 9.8/10** — Pluck CMS&#x27;s admin panel relies solely on a Referer-header comparison (requestedByTheSameDomain() in data/inc/functions.a — CVSS 9.6; detection opportunity

### Human context

**[ISC Stormcast For Wednesday, August 5th, 2026 https://isc.sans.edu/podcastdetail/10038, (Wed, Aug 5th)](https://isc.sans.edu/diary/rss/33216)**
SANS Internet Storm Center Handler&#x27;s Diary  
> (c) SANS Internet Storm Center. https://isc.sans.edu Creative Commons Attribution-Noncommercial 3.0 United States License.

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
