# Blue Team Intelligence Digest — 2026-07-16

Coverage:
2026-07-14T00:00:00+00:00 → 2026-07-16T00:00:00+00:00

Generated:
2026-07-15T17:59:08+00:00

## Executive Summary

5 source-backed developments qualified for this coverage window.

## 1. Immediate Attention

- **CVE-2099-0001** — CVE-2099-0001 exploited in CISA KEV: ExampleCorp Example VPN. Selected because: CISA KEV +50 + confirmed exploitation +40 + known ransomware use +25 + critical CVSS +20 + EPSS &gt;= 0.70 +25 + EPSS percentile &gt;= 0.95 +10 + priority technology: vpn_remote_access +8 + official source +5

## 2. Vulnerability Priorities

| Priority | CVE/GHSA | Product | CVSS | EPSS | KEV | Reason |
| --- | --- | --- | ---: | ---: | --- | --- |
| 1 | CVE-2099-0001, GHSA-xxxx-yyyy-zzzz | Example VPN, example-vpn-client | 10.0 | 0.91 | yes | CISA KEV +50; confirmed exploitation +40; known ransomware use +25; critical CVSS +20; EPSS &gt;= 0.70 +25; EPSS percentile &gt;= 0.95 +10; priority technology: vpn_remote_access +8; official source +5 |
| 2 | CVE-2099-0003 |  | n/a | 0.12 | no | official source +5 |
| 3 | GHSA-with-drawn |  | 3.1 | n/a | no | Withdrawn advisory retained for transparency but excluded from priority scoring |

## 3. Threat and Ransomware Activity

Only verified and source-backed activity is shown.
- CVE-2099-0001 exploited in CISA KEV: ExampleCorp Example VPN

## 4. Detection Opportunities

Analyst context generated from structured source fields.
- **CVE-2099-0001 exploited in CISA KEV: ExampleCorp Example VPN**: Analyst context generated from structured source fields: inventory affected products, review exposure, authentication and network telemetry where applicable, and follow vendor guidance.
- **SigmaHQ/sigma v2099.1**: Review release notes for defensive content changes.
- **CVE-2099-0003: Example library issue with missing optional CVSS data.**: Analyst context generated from structured source fields: inventory affected products, review exposure, authentication and network telemetry where applicable, and follow vendor guidance.

## 5. Vendor and Government Advisories

- [CISA advisory fixture](https://www.cisa.gov/news-events/alerts/fixture) — CISA Cybersecurity Advisories

## 6. Blue Team Tools and Detection Content

- [SigmaHQ/sigma v2099.1](https://github.com/SigmaHQ/sigma/releases/tag/v2099.1) — Allowlisted defensive project release; review release notes for detection or monitoring updates.

## 7. Analyst Queue

- Review CVE-2099-0001 against asset inventory and vendor guidance.
- Review release:SigmaHQ/sigma:v2099.1 against asset inventory and vendor guidance.
- Review url:https://www.cisa.gov/news-events/alerts/fixture against asset inventory and vendor guidance.
- Review CVE-2099-0003 against asset inventory and vendor guidance.
- Review GHSA-with-drawn against asset inventory and vendor guidance.

## 8. Source Health

| Source | Status | Items | Duration | Detail |
| --- | --- | ---: | ---: | --- |
| cisa_kev | fixture_only | 1 | 0 ms |  |
| nvd | fixture_only | 2 | 0 ms |  |
| github_advisories | fixture_only | 2 | 0 ms |  |
| rss_official | fixture_only | 1 | 0 ms |  |
| github_releases | fixture_only | 1 | 0 ms |  |
| epss | fixture_only | 2 | 0 ms |  |

## Methodology and Limitations

Ranking assists prioritisation and does not replace asset-specific risk assessment. EPSS is a probability signal, not proof of exploitation. This product uses data from the NVD API but is not endorsed or certified by the NVD.
