# CyberDailyLog — Daily Blue Team Brief · 2026-09-18

> Automated, source-backed defensive intelligence for the previous 24 hours.

**Updated:** 2026-09-18T14:06:58+00:00  
**Coverage:** 2026-09-17T14:02:08+00:00 → 2026-09-18T14:02:08+00:00  
**Status:** Operational

[Full JSON](latest.json) · [Compact feed](portfolio-feed.json) · [Source health](source-health.json) · [Archive](archive/)

## Today in 30 seconds

- **221** source-backed developments assessed.
- **143** met the editorial threshold of **5.0/10** or an exploitation override.
- **13** unique items are displayed after curation.
- Core sources: **3/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

## Immediate attention

No confirmed exploitation, CISA KEV or ransomware-linked item qualified in this run.

## Priority vulnerabilities — 5.0/10 or higher

| Threat | Priority | CVSS | EPSS | Signal | Why it matters |
| --- | ---: | ---: | ---: | --- | --- |
| [CVE-2026-84609 — CVE-2026-84609: A permissions issue was addressed with improved path validation. This issue is fixed in iOS…](https://nvd.nist.gov/vuln/detail/CVE-2026-84609) | 9.4 | 9.8 | 0.2% | — | CVSS 9.8; detection opportunity |
| [CVE-2026-28198 — CVE-2026-28198: An authenticated, low-privileged user with access to the NetBackup Flex OS management shell…](https://nvd.nist.gov/vuln/detail/CVE-2026-28198) | 9.4 | 9.4 | n/a | — | CVSS 9.4; detection opportunity |
| [CVE-2026-28197 — CVE-2026-28197: An authenticated, low-privileged user with access to the NetBackup Flex OS management shell…](https://nvd.nist.gov/vuln/detail/CVE-2026-28197) | 9.4 | 9.4 | n/a | — | CVSS 9.4; detection opportunity |
| [CVE-2026-13684 — CVE-2026-13684: An improper encoding or escaping of output vulnerability in SCGI in Synology DiskStation…](https://nvd.nist.gov/vuln/detail/CVE-2026-13684) | 9.4 | 9.8 | n/a | — | CVSS 9.8; detection opportunity |
| [CVE-2026-13639 — CVE-2026-13639: An insufficient entropy vulnerability in login logic in Synology DiskStation Manager (DSM)…](https://nvd.nist.gov/vuln/detail/CVE-2026-13639) | 9.4 | 9.8 | n/a | — | CVSS 9.8; detection opportunity |
| [CVE-2026-91732 — CVE-2026-91732: Missing authorization in AppManifest in Google Chrome prior to 153.0.8010.47 allowed a…](https://nvd.nist.gov/vuln/detail/CVE-2026-91732) | 9.2 | 8.1 | 0.2% | — | CVSS 8.1; priority technology: browsers |
| [CVE-2026-27446 — CVE-2026-27446: Missing Authentication for Critical Function (CWE-306) vulnerability in Apache Artemis,…](https://nvd.nist.gov/vuln/detail/CVE-2026-27446) | 9.1 | 9.3 | 10.0% | — | CVSS 9.3; EPSS percentile &gt;= 95% |
| [CVE-2026-67100 — CVE-2026-67100: HCL BigFix Service Management is affected by SQL Injection flaw and a Cross-Tenant Data…](https://nvd.nist.gov/vuln/detail/CVE-2026-67100) | 9.1 | 9.8 | n/a | — | CVSS 9.8; detection opportunity |
| [CVE-2026-20279 — CVE-2026-20279: As part of Cisco&#x27;s ongoing commitment to proactive security and product quality, the Cisco…](https://nvd.nist.gov/vuln/detail/CVE-2026-20279) | 9.1 | 9.8 | 0.3% | — | CVSS 9.8; detection opportunity |
| [CVE-2018-13410 — CVE-2018-13410: Info-ZIP Zip 3.0, when the -T and -TT command-line options are used, allows attackers to…](https://nvd.nist.gov/vuln/detail/CVE-2018-13410) | 9.1 | 9.8 | 4.0% | — | CVSS 9.8; detection opportunity |

## Human context

### [HTTP QUERY Method: The Grey Zone Between GET And POST., (Fri, Sep 18th)](https://isc.sans.edu/diary/rss/33352)

**SANS Internet Storm Center Handler&#x27;s Diary**

> In June 2026 the IETF published RFC 10008\[ 1 \], defining a new HTTP method: &quot;QUERY&quot;. The HTTP protocol faced already by changes (HTTP/2,…

_Publisher-provided RSS excerpt; open the original article for full context._

## Community pulse

- **[Hister: A private search engine for the pages you visit and the files you keep](https://github.com/asciimoo/hister)**
  Hacker News · 663 points · 175 comments · [Open discussion](https://news.ycombinator.com/item?id=49743097)
  _Community interest signal only; validate claims against primary sources._

## Notable official advisories

No additional official advisory qualified after de-duplication.

## Defensive tooling and detection content

- [wazuh/wazuh v4.14.8-rc2](https://github.com/wazuh/wazuh/releases/tag/v4.14.8-rc2) — Allowlisted defensive project release; review release notes for detection or monitoring updates.

## Analyst next actions

- **CVE-2026-84609:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.
- **CVE-2026-28198:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.
- **CVE-2026-28197:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.
- **CVE-2026-13684:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.
- **CVE-2026-13639:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.

## Source health

Core sources: **3/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

<details>
<summary>Collector details</summary>

| Source | Required | Status | Accepted | Duration | Detail |
| --- | --- | --- | ---: | ---: | --- |
| cisa_kev | yes | healthy | 1713 | 365 ms |  |
| nvd | yes | healthy | 2252 | 276402 ms |  |
| github_advisories | yes | healthy | 113 | 2936 ms |  |
| rss_krebs | no | healthy | 0 | 128 ms |  |
| rss_sans_isc | no | healthy | 3 | 395 ms |  |
| github_releases | no | healthy | 1 | 1303 ms |  |
| hacker_news | no | healthy | 2 | 3192 ms |  |
| epss | no | healthy | 2497 | 3142 ms |  |

</details>

<details>
<summary>Methodology and limitations</summary>

The 0–10 priority score is an editorial triage aid, not asset-specific risk. EPSS is probabilistic, and source-backed findings still require asset, exposure and vendor validation. Expert RSS excerpts and Hacker News engagement are contextual signals, not verified threat evidence.

</details>
