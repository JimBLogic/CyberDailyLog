# CyberDailyLog — Daily Blue Team Brief · 2026-10-28

> Automated, source-backed defensive intelligence for the previous 24 hours.

**Updated:** 2026-10-28T12:22:34+00:00  
**Coverage:** 2026-10-27T12:21:33+00:00 → 2026-10-28T12:21:33+00:00  
**Status:** Operational

[Full JSON](latest.json) · [Compact feed](portfolio-feed.json) · [Source health](source-health.json) · [Archive](archive/)

## Today in 30 seconds

- **210** source-backed developments assessed.
- **54** met the editorial threshold of **5.0/10** or an exploitation override.
- **13** unique items are displayed after curation.
- Core sources: **3/3 healthy**. Optional sources: **7 healthy**, **0 degraded**.

## Immediate attention

- **[CVE-2026-109619](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-109619 exploited in CISA KEV: PHP Group PHP. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-109618](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-109618 exploited in CISA KEV: PHP Group PHP. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…

## Priority vulnerabilities — 5.0/10 or higher

| Threat | Priority | CVSS | EPSS | Signal | Why it matters |
| --- | ---: | ---: | ---: | --- | --- |
| [CVE-2026-86384 — CVE-2026-86384: Dell PowerProtect Data Domain, Feature Release versions 7.7.1.0 through 8.8, LTS2024 release…](https://nvd.nist.gov/vuln/detail/CVE-2026-86384) | 9.4 | 9.8 | n/a | — | CVSS 9.8; detection opportunity |
| [CVE-2026-114278 — CVE-2026-114278: The che-machine-exec service constructs a shell command by concatenating user-controlled…](https://nvd.nist.gov/vuln/detail/CVE-2026-114278) | 9.4 | 9.8 | n/a | — | CVSS 9.8; detection opportunity |
| [CVE-2026-112197 — CVE-2026-112197: Vulnerability due to a lack of authentication in critical functions of the NoviGest Desktop…](https://nvd.nist.gov/vuln/detail/CVE-2026-112197) | 9.4 | 9.4 | n/a | — | CVSS 9.4; detection opportunity |
| [CVE-2026-103799 — CVE-2026-103799: Dell PowerProtect Data Domain Management Center, Feature Release versions 7.7.1.0 through…](https://nvd.nist.gov/vuln/detail/CVE-2026-103799) | 9.4 | 9.6 | n/a | — | CVSS 9.6; detection opportunity |
| [CVE-2026-103792 — CVE-2026-103792: Dell PowerProtect Data Domain Management Center, Feature Release versions 7.7.1.0 through…](https://nvd.nist.gov/vuln/detail/CVE-2026-103792) | 9.4 | 9.6 | n/a | — | CVSS 9.6; detection opportunity |
| [CVE-2026-103780 — CVE-2026-103780: Dell PowerProtect Data Domain, Feature Release versions 7.7.1.0 through 8.8, LTS2024…](https://nvd.nist.gov/vuln/detail/CVE-2026-103780) | 9.4 | 9.8 | n/a | — | CVSS 9.8; detection opportunity |
| [CVE-2026-14571 — CVE-2026-14571: A Blind SQL Injection vulnerability in Futurum Software’s management software, caused by a…](https://nvd.nist.gov/vuln/detail/CVE-2026-14571) | 9.3 | 9.1 | n/a | — | CVSS 9.1; detection opportunity |
| [CVE-2026-86385 — CVE-2026-86385: Dell PowerProtect Data Domain, Feature Release versions 7.7.1.0 through 8.8, contain an…](https://nvd.nist.gov/vuln/detail/CVE-2026-86385) | 9.1 | 8.8 | n/a | — | CVSS 8.8; detection opportunity |
| [CVE-2026-86378 — CVE-2026-86378: Dell PowerProtect Data Domain, Feature Release versions 7.7.1.0 through 8.8, LTS2024 release…](https://nvd.nist.gov/vuln/detail/CVE-2026-86378) | 9.1 | 8.8 | n/a | — | CVSS 8.8; detection opportunity |
| [CVE-2026-118477 — CVE-2026-118477: The ei_git_repo_url parameter in the Git remote configuration endpoint of KaliFast is…](https://nvd.nist.gov/vuln/detail/CVE-2026-118477) | 8.9 | 8.7 | n/a | — | CVSS 8.7; detection opportunity |

## Human context

### [ISC Stormcast For Wednesday, October 28th, 2026 https://isc.sans.edu/podcastdetail/10154, (Wed, Oct 28th)](https://isc.sans.edu/diary/rss/33464)

**SANS Internet Storm Center Handler&#x27;s Diary**

> (c) SANS Internet Storm Center. https://isc.sans.edu Creative Commons Attribution-Noncommercial 3.0 United States License.

_Publisher-provided RSS excerpt; open the original article for full context._

## Community pulse

No security-focused Hacker News discussion met the engagement threshold.

## Notable official advisories

No additional official advisory qualified after de-duplication.

## Defensive tooling and detection content

No allowlisted defensive release qualified in this coverage window.

## Analyst next actions

- **CVE-2026-109619:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-109618:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-86384:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.
- **CVE-2026-114278:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.
- **CVE-2026-112197:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.

## Source health

Core sources: **3/3 healthy**. Optional sources: **7 healthy**, **0 degraded**.

<details>
<summary>Collector details</summary>

| Source | Required | Status | Accepted | Duration | Detail |
| --- | --- | --- | ---: | ---: | --- |
| cisa_kev | yes | healthy | 1760 | 468 ms |  |
| nvd | yes | healthy | 1947 | 43010 ms |  |
| github_advisories | yes | healthy | 206 | 2374 ms |  |
| rss_cert_eu_advisories | no | healthy | 0 | 635 ms |  |
| rss_cert_eu_guidance | no | healthy | 0 | 502 ms |  |
| rss_krebs | no | healthy | 0 | 193 ms |  |
| rss_sans_isc | no | healthy | 1 | 155 ms |  |
| github_releases | no | healthy | 0 | 1932 ms |  |
| hacker_news | no | healthy | 0 | 5116 ms |  |
| epss | no | healthy | 2864 | 3179 ms |  |

</details>

<details>
<summary>Methodology and limitations</summary>

The 0–10 priority score is an editorial triage aid, not asset-specific risk. EPSS is probabilistic, and source-backed findings still require asset, exposure and vendor validation. Expert RSS excerpts and Hacker News engagement are contextual signals, not verified threat evidence.

</details>
