# CyberDailyLog — Daily Blue Team Brief · 2026-11-03

> Automated, source-backed defensive intelligence for the previous 24 hours.

**Updated:** 2026-11-03T18:11:51+00:00  
**Coverage:** 2026-11-02T18:10:39+00:00 → 2026-11-03T18:10:39+00:00  
**Status:** Operational

[Full JSON](latest.json) · [Compact feed](portfolio-feed.json) · [Source health](source-health.json) · [Archive](archive/)

## Today in 30 seconds

- **652** source-backed developments assessed.
- **441** met the editorial threshold of **5.0/10** or an exploitation override.
- **15** unique items are displayed after curation.
- Core sources: **3/3 healthy**. Optional sources: **7 healthy**, **0 degraded**.

## Immediate attention

- **[CVE-2026-96652](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-96652 exploited in CISA KEV: Plex Media Server. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-110936](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-110936 exploited in CISA KEV: Siemens Software Center. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-118527](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-118527 exploited in CISA KEV: Ivanti Connect Secure. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-96655](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-96655 exploited in CISA KEV: Plex Media Server. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…

## Priority vulnerabilities — 5.0/10 or higher

| Threat | Priority | CVSS | EPSS | Signal | Why it matters |
| --- | ---: | ---: | ---: | --- | --- |
| [CVE-2025-71336, GHSA-6933-jpx5-q87q — CVE-2025-71336: Flowise before 3.0.6 (affected versions 2.2.7-patch.1 and earlier) contains an unsandboxed…](https://nvd.nist.gov/vuln/detail/CVE-2025-71336) | 9.4 | 9.3 | 1.1% | — | CVSS 9.3; priority technology: cloud |
| [CVE-2025-71334, GHSA-q67q-549q-p849 — CVE-2025-71334: Flowise before 3.0.6 contains an arbitrary file access vulnerability due to missing…](https://nvd.nist.gov/vuln/detail/CVE-2025-71334) | 9.4 | 9.3 | 4.4% | — | CVSS 9.3; priority technology: browsers |
| [CVE-2026-28336 — CVE-2026-28336: SolarWinds Dameware was found to be affected by a command injection vulnerability that could…](https://nvd.nist.gov/vuln/detail/CVE-2026-28336) | 9.4 | 9.9 | n/a | — | CVSS 9.9; detection opportunity |
| [CVE-2026-18948, GHSA-gg2p-37pv-v7fq — CVE-2026-18948: A flaw was found in Feast. The system improperly deserializes user-defined functions (UDFs)…](https://nvd.nist.gov/vuln/detail/CVE-2026-18948) | 9.4 | 9.9 | 1.1% | — | CVSS 9.9; detection opportunity |
| [CVE-2026-61666, GHSA-2x63-gw47-w4mm — CVE-2026-61666: websocket-driver is a WebSocket protocol handler with pluggable I/O. Prior to 0.8.2,…](https://nvd.nist.gov/vuln/detail/CVE-2026-61666) | 9.4 | 8.9 | 0.4% | — | CVSS 8.9; priority technology: browsers |
| [CVE-2026-79589 — CVE-2026-79589: The WIFI4 N300 router (Model: T1 Pro) v1.0.0 by U-speed contains an insecure access control…](https://nvd.nist.gov/vuln/detail/CVE-2026-79589) | 9.4 | 9.8 | 0.3% | — | CVSS 9.8; detection opportunity |
| [CVE-2026-76528 — CVE-2026-76528: As part of Cisco&#x27;s ongoing commitment to proactive security and product quality, Cisco has…](https://nvd.nist.gov/vuln/detail/CVE-2026-76528) | 9.4 | 9.8 | 0.4% | — | CVSS 9.8; detection opportunity |
| [CVE-2026-76407 — CVE-2026-76407: As part of Cisco&#x27;s ongoing commitment to proactive security and product quality, Cisco has…](https://nvd.nist.gov/vuln/detail/CVE-2026-76407) | 9.4 | 9.8 | 0.4% | — | CVSS 9.8; detection opportunity |
| [CVE-2026-41242 — CVE-2026-41242: protobufjs compiles protobuf definitions into JavaScript (JS) functions. In versions prior…](https://nvd.nist.gov/vuln/detail/CVE-2026-41242) | 9.4 | 9.4 | 0.8% | — | CVSS 9.4; detection opportunity |

## Human context

### [Tech Firms Dismantle Botnet That Turned 1.3M TV Boxes Into Proxies](https://krebsonsecurity.com/2026/11/tech-firms-dismantle-botnet-that-turned-1-3m-tv-boxes-into-proxies/)

**Brian Krebs · Krebs on Security**

> Google said today it worked with industry partners to dismantle a botnet made up of more than 1.3 million Android TV set-top boxes that…

_Publisher-provided RSS excerpt; open the original article for full context._

## Community pulse

- **[Nvidia – open-source auto-ontology](https://github.com/NVIDIA/auto-ontology)**
  Hacker News · 243 points · 105 comments · [Open discussion](https://news.ycombinator.com/item?id=50348962)
  _Community interest signal only; validate claims against primary sources._

## Notable official advisories

No additional official advisory qualified after de-duplication.

## Defensive tooling and detection content

No allowlisted defensive release qualified in this coverage window.

## Analyst next actions

- **CVE-2026-96652:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-110936:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-118527:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-96655:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2025-71336, GHSA-6933-jpx5-q87q:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.

## Source health

Core sources: **3/3 healthy**. Optional sources: **7 healthy**, **0 degraded**.

<details>
<summary>Collector details</summary>

| Source | Required | Status | Accepted | Duration | Detail |
| --- | --- | --- | ---: | ---: | --- |
| cisa_kev | yes | healthy | 1766 | 450 ms |  |
| nvd | yes | healthy | 1748 | 50458 ms |  |
| github_advisories | yes | healthy | 54 | 950 ms |  |
| rss_cert_eu_advisories | no | healthy | 0 | 789 ms |  |
| rss_cert_eu_guidance | no | healthy | 0 | 677 ms |  |
| rss_krebs | no | healthy | 1 | 81 ms |  |
| rss_sans_isc | no | healthy | 1 | 330 ms |  |
| github_releases | no | healthy | 0 | 2596 ms |  |
| hacker_news | no | healthy | 2 | 4369 ms |  |
| epss | no | healthy | 3149 | 8258 ms |  |

</details>

<details>
<summary>Methodology and limitations</summary>

The 0–10 priority score is an editorial triage aid, not asset-specific risk. EPSS is probabilistic, and source-backed findings still require asset, exposure and vendor validation. Expert RSS excerpts and Hacker News engagement are contextual signals, not verified threat evidence.

</details>
