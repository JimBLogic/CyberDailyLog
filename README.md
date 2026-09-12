# CyberDailyLog

[![Daily Blue Team Intelligence](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml/badge.svg)](https://github.com/JimBLogic/CyberDailyLog/actions/workflows/daily-intelligence.yml)

CyberDailyLog is an automated, transparent and curated 24-hour Blue Team intelligence pipeline. It collects trusted cybersecurity sources, enriches and correlates vulnerability data, adds clearly separated expert and community context, ranks actionable developments and publishes reproducible daily reports.

**Live dashboard:** [CyberDailyLog Intelligence Dashboard](https://cyberdailylog.jimblogic.chatgpt.site) — dynamic risk distribution, historical signal, collector health, ranked triage, EN/ES interface and portable JSON/CSV exports.

<!-- CYBERDAILYLOG:DAILY:START -->
## Latest automated brief

**Updated:** 2026-09-12T13:18:22+00:00  
**Coverage:** 2026-09-11T13:18:09+00:00 → 2026-09-12T13:18:09+00:00  
**Pipeline:** **Operational**

No confirmed exploitation, CISA KEV or ransomware-linked item qualified.

- **Assessed:** 712 source-backed developments
- **Above threshold:** 179
- Core sources: **3/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

### Highest-priority items

- **[CVE-2026-87719](https://nvd.nist.gov/vuln/detail/CVE-2026-87719) · 10.0/10** — GitLab has remediated an issue in GitLab EE affecting all versions from 18.3 before 19.1.8, 19.2 before 19.2.6, and 19.3 — CVSS 9.9; detection opportunity
- **[CVE-2026-80462](https://nvd.nist.gov/vuln/detail/CVE-2026-80462) · 10.0/10** — A vulnerability in the Chef Automate API gateway and identity validation path may allow an unauthenticated actor to gain — CVSS 10.0; detection opportunity
- **[CVE-2026-78159](https://nvd.nist.gov/vuln/detail/CVE-2026-78159) · 10.0/10** — The The Events Calendar plugin for WordPress is vulnerable to Remote Code Execution in all versions up to, and including — CVSS 9.8; detection opportunity
- **[CVE-2026-78006](https://nvd.nist.gov/vuln/detail/CVE-2026-78006) · 10.0/10** — The The Events Calendar plugin for WordPress is vulnerable to Remote Code Execution in all versions up to, and including — CVSS 9.8; detection opportunity
- **[CVE-2026-53952](https://nvd.nist.gov/vuln/detail/CVE-2026-53952) · 10.0/10** — GetSimple CMS is a content management system (CMS), and GetSimple CMS CE is the community edition of that CMS. A logic f — CVSS 9.8; detection opportunity

### Human context

**[The Self-Expanding Stolen Inference Supply Chain: An AI Agent Harvesting and Re-Serving LLM Access, (Fri, Sep 11th)](https://isc.sans.edu/diary/rss/33332)**
SANS Internet Storm Center Handler&#x27;s Diary  
> I identified an attacker using a semi-autonomous coding agent to run an offensive operation: finding poorly secured LLM resale gateways, acquiring API access through…

### Community pulse

**[GrapheneOS&#x27; rewritten Messages app is released](https://github.com/GrapheneOS/Messaging/releases/tag/13)** — Hacker News · 285 points · 210 comments
[Open discussion](https://news.ycombinator.com/item?id=49663373)

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

`.github/workflows/daily-intelligence.yml` publishes at 12:00 Europe/Madrid, with an idempotent 13:30 recovery schedule if the first event is delayed or dropped. The timezone-aware schedule follows Madrid daylight-saving changes automatically. Manual runs publish by default; set `dry_run=true` for a preview. Every publication requires the source quorum and writes only generated README/report outputs with the built-in `GITHUB_TOKEN`.

CyberDailyLog stores defensive metadata, short attributed feed excerpts and official links. It does not execute exploit code, download malware, bypass access controls or print credentials.
