# CyberDailyLog — Daily Blue Team Brief · 2026-10-21

> Automated, source-backed defensive intelligence for the previous 24 hours.

**Updated:** 2026-10-21T14:54:49+00:00  
**Coverage:** 2026-10-20T08:42:24+00:00 → 2026-10-21T14:48:14+00:00  
**Status:** Operational

[Full JSON](latest.json) · [Compact feed](portfolio-feed.json) · [Source health](source-health.json) · [Archive](archive/)

## Today in 30 seconds

- **76** source-backed developments assessed.
- **38** met the editorial threshold of **5.0/10** or an exploitation override.
- **15** unique items are displayed after curation.
- Core sources: **2/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

## Immediate attention

- **[CVE-2026-96656](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-96656 exploited in CISA KEV: Plex Media Server. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-110936](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-110936 exploited in CISA KEV: Siemens Software Center. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-106931](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-106931 exploited in CISA KEV: EG Secure Solutions SiteGuard Server Edition. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-96655](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-96655 exploited in CISA KEV: Plex Media Server. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-96654](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-96654 exploited in CISA KEV: Plex Media Server. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…

## Priority vulnerabilities — 5.0/10 or higher

| Threat | Priority | CVSS | EPSS | Signal | Why it matters |
| --- | ---: | ---: | ---: | --- | --- |
| [CVE-2026-96652 — CVE-2026-96652 exploited in CISA KEV: Plex Media Server](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) | 9.6 | 5.3 | 0.2% | KEV | CVSS 5.3; detection opportunity |
| [CVE-2026-112403, GHSA-8g5g-8vmr-9782 — CVE-2026-112403: Pillow is a Python imaging library. Prior to 13.0.0, Pillow&#x27;s JPEG decoder can write a…](https://nvd.nist.gov/vuln/detail/CVE-2026-112403) | 9.4 | 9.2 | 0.3% | — | CVSS 9.2; priority technology: linux |
| [CVE-2026-112397, GHSA-58r4-6rv3-gfh8 — CVE-2026-112397: Pillow is a Python imaging library. Prior to 13.0.0, Pillow&#x27;s ImageMorph.MorphOp.apply()…](https://nvd.nist.gov/vuln/detail/CVE-2026-112397) | 9.4 | 8.7 | 0.4% | — | CVSS 8.7; priority technology: browsers |
| [CVE-2026-112896, GHSA-pchr-8j38-3x4p — CVE-2026-112896: Pillow is a Python imaging library. Prior to 13.0.0, Pillow&#x27;s TIFF encoder can read beyond…](https://nvd.nist.gov/vuln/detail/CVE-2026-112896) | 9.1 | 8.8 | 0.3% | — | CVSS 8.8; detection opportunity |
| [CVE-2026-112404, GHSA-c6hw-5grf-ff96 — CVE-2026-112404: Pillow is a Python imaging library. From 8.1.0 until 13.0.0, Pillow&#x27;s TIFF tile and RGBA…](https://nvd.nist.gov/vuln/detail/CVE-2026-112404) | 9.1 | 8.8 | 0.3% | — | CVSS 8.8; detection opportunity |
| [CVE-2026-111755, GHSA-8r9p-f939-6h3c — CVE-2026-111755: follow-redirects is a Node.js HTTP and HTTPS client wrapper that automatically follows…](https://nvd.nist.gov/vuln/detail/CVE-2026-111755) | 8.9 | 8.2 | 0.4% | — | CVSS 8.2; priority technology: windows |
| [CVE-2026-112897, GHSA-q45j-58j2-45rg — CVE-2026-112897: Pillow is a Python imaging library. From 5.3.0 until 13.0.0, Pillow can return…](https://nvd.nist.gov/vuln/detail/CVE-2026-112897) | 8.9 | 8.7 | 0.3% | — | CVSS 8.7; detection opportunity |
| [CVE-2026-112895, GHSA-p4wg-p73j-c528 — CVE-2026-112895: Pillow is a Python imaging library. From 5.1.0 until 13.0.0, Pillow can exhaust resources…](https://nvd.nist.gov/vuln/detail/CVE-2026-112895) | 8.9 | 8.7 | 0.3% | — | CVSS 8.7; detection opportunity |

## Human context

### [Critical PHP Vulnerability (CVE-2026-109618, CVE-2026-109619) \[infocon yellow\], (Wed, Oct 21st)](https://isc.sans.edu/diary/rss/33440)

**SANS Internet Storm Center Handler&#x27;s Diary**

> PHP.net announced that it will release a critical update today. We decided to change the infoCon to YELLOW due to the widespread use of…

_Publisher-provided RSS excerpt; open the original article for full context._

## Community pulse

- **[Upcoming critical PHP security release (CVE-2026-109618 / -109619)](https://news-web.php.net/php.announce/509)**
  Hacker News · 1393 points · 590 comments · [Open discussion](https://news.ycombinator.com/item?id=50172041)
  _Community interest signal only; validate claims against primary sources._

## Notable official advisories

No additional official advisory qualified after de-duplication.

## Defensive tooling and detection content

No allowlisted defensive release qualified in this coverage window.

## Analyst next actions

- **CVE-2026-96656:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-110936:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-106931:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-96655:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-96654:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…

## Source health

Core sources: **2/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

<details>
<summary>Collector details</summary>

| Source | Required | Status | Accepted | Duration | Detail |
| --- | --- | --- | ---: | ---: | --- |
| cisa_kev | yes | healthy | 1754 | 411 ms |  |
| nvd | yes | failed | 0 | 381495 ms | Source transport failed for services.nvd.nist.gov |
| github_advisories | yes | healthy | 65 | 2466 ms |  |
| rss_krebs | no | healthy | 0 | 118 ms |  |
| rss_sans_isc | no | healthy | 2 | 265 ms |  |
| github_releases | no | healthy | 1 | 2641 ms |  |
| hacker_news | no | healthy | 3 | 1935 ms |  |
| epss | no | healthy | 1658 | 3985 ms |  |

</details>

<details>
<summary>Methodology and limitations</summary>

The 0–10 priority score is an editorial triage aid, not asset-specific risk. EPSS is probabilistic, and source-backed findings still require asset, exposure and vendor validation. Expert RSS excerpts and Hacker News engagement are contextual signals, not verified threat evidence.

</details>
