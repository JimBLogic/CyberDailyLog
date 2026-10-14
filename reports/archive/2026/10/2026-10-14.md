# CyberDailyLog — Daily Blue Team Brief · 2026-10-14

> Automated, source-backed defensive intelligence for the previous 24 hours.

**Updated:** 2026-10-14T11:25:39+00:00  
**Coverage:** 2026-10-13T09:16:43+00:00 → 2026-10-14T11:20:55+00:00  
**Status:** Operational

[Full JSON](latest.json) · [Compact feed](portfolio-feed.json) · [Source health](source-health.json) · [Archive](archive/)

## Today in 30 seconds

- **2637** source-backed developments assessed.
- **2246** met the editorial threshold of **5.0/10** or an exploitation override.
- **15** unique items are displayed after curation.
- Core sources: **3/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

## Immediate attention

- **[CVE-2021-22555](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2021-22555 exploited in CISA KEV: Linux Kernel. **Action:** Apply mitigations per vendor instructions, follow applicable BOD 22-01 guidance for cloud services, or discontinue use of the product if mitigations are…
- **[CVE-2026-96951](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-96951 exploited in CISA KEV: Microsoft Windows. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **[CVE-2026-104935](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) · 9.6/10** — CVE-2026-104935 exploited in CISA KEV: Ivanti Connect Secure. **Action:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…

## Priority vulnerabilities — 5.0/10 or higher

| Threat | Priority | CVSS | EPSS | Signal | Why it matters |
| --- | ---: | ---: | ---: | --- | --- |
| [CVE-2019-8457 — CVE-2019-8457: SQLite3 from 3.6.0 to and including 3.27.2 is vulnerable to heap out-of-bound read in the…](https://nvd.nist.gov/vuln/detail/CVE-2019-8457) | 9.4 | 9.8 | 45.4% | — | CVSS 9.8; EPSS &gt;= 30% |
| [CVE-2019-5436 — CVE-2019-5436: A heap buffer overflow in the TFTP receiving code allows for DoS or arbitrary code execution…](https://nvd.nist.gov/vuln/detail/CVE-2019-5436) | 9.4 | 7.8 | 49.7% | — | CVSS 7.8; EPSS &gt;= 30% |
| [CVE-2026-97381 — CVE-2026-97381: Legacy Update is a tool for activating and installing updates on legacy Windows PCs. Legacy…](https://nvd.nist.gov/vuln/detail/CVE-2026-97381) | 9.4 | 9.9 | n/a | — | CVSS 9.9; priority technology: windows |
| [CVE-2026-77459 — CVE-2026-77459: Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes. From 2.10.0 until…](https://nvd.nist.gov/vuln/detail/CVE-2026-77459) | 9.4 | 9.9 | n/a | — | CVSS 9.9; priority technology: cloud |
| [CVE-2026-74041 — CVE-2026-74041: Wazuh 4.14.3 before 4.14.8 contains a case-sensitivity mismatch between the ossec.conf…](https://nvd.nist.gov/vuln/detail/CVE-2026-74041) | 9.4 | 9.4 | n/a | — | CVSS 9.4; priority technology: security_products |
| [CVE-2026-74040 — CVE-2026-74040: Wazuh versions from 3.9.0 before 4.14.8 contain an arbitrary file overwrite vulnerability in…](https://nvd.nist.gov/vuln/detail/CVE-2026-74040) | 9.4 | 9.4 | n/a | — | CVSS 9.4; priority technology: security_products |
| [CVE-2026-64037 — CVE-2026-64037: In the Linux kernel, the following vulnerability has been resolved: wifi: iwlwifi: mld: fix…](https://nvd.nist.gov/vuln/detail/CVE-2026-64037) | 9.4 | 9.8 | 0.4% | — | CVSS 9.8; priority technology: linux |
| [CVE-2026-64035 — CVE-2026-64035: In the Linux kernel, the following vulnerability has been resolved: igc: set tx buffer type…](https://nvd.nist.gov/vuln/detail/CVE-2026-64035) | 9.4 | 9.8 | 0.4% | — | CVSS 9.8; priority technology: linux |
| [CVE-2026-64034 — CVE-2026-64034: In the Linux kernel, the following vulnerability has been resolved: net: mana: Fix TOCTOU…](https://nvd.nist.gov/vuln/detail/CVE-2026-64034) | 9.4 | 9.3 | 0.1% | — | CVSS 9.3; priority technology: linux |
| [CVE-2026-64033 — CVE-2026-64033: In the Linux kernel, the following vulnerability has been resolved: RDMA/rtrs: Fix…](https://nvd.nist.gov/vuln/detail/CVE-2026-64033) | 9.4 | 9.8 | 0.5% | — | CVSS 9.8; priority technology: linux |

## Human context

### [Orphaned VBA Projects Inside DWG Files, (Wed, Oct 14th)](https://isc.sans.edu/diary/rss/33420)

**SANS Internet Storm Center Handler&#x27;s Diary**

> Years ago I wrote diary entries about VBA code stored inside AutoCAD drawing files (.dwg).

_Publisher-provided RSS excerpt; open the original article for full context._

## Community pulse

- **[11 year old unsoundness bugs found in Rust borrow checker](https://github.com/rust-lang/rust/issues/164250)**
  Hacker News · 723 points · 408 comments · [Open discussion](https://news.ycombinator.com/item?id=50069499)
  _Community interest signal only; validate claims against primary sources._

## Notable official advisories

No additional official advisory qualified after de-duplication.

## Defensive tooling and detection content

No allowlisted defensive release qualified in this coverage window.

## Analyst next actions

- **CVE-2021-22555:** Apply mitigations per vendor instructions, follow applicable BOD 22-01 guidance for cloud services, or discontinue use of the product if mitigations are…
- **CVE-2026-96951:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2026-104935:** Apply mitigations in accordance with vendor instructions, ensuring compliance with CISA’s BOD 26-04 Prioritizing Security Updates Based on Risk (see URL in…
- **CVE-2019-8457:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.
- **CVE-2019-5436:** Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance.

## Source health

Core sources: **3/3 healthy**. Optional sources: **5 healthy**, **0 degraded**.

<details>
<summary>Collector details</summary>

| Source | Required | Status | Accepted | Duration | Detail |
| --- | --- | --- | ---: | ---: | --- |
| cisa_kev | yes | healthy | 1741 | 338 ms |  |
| nvd | yes | healthy | 4420 | 260166 ms |  |
| github_advisories | yes | healthy | 48 | 2964 ms |  |
| rss_krebs | no | healthy | 1 | 75 ms |  |
| rss_sans_isc | no | healthy | 3 | 408 ms |  |
| github_releases | no | healthy | 0 | 2562 ms |  |
| hacker_news | no | healthy | 2 | 3849 ms |  |
| epss | no | healthy | 3690 | 11288 ms |  |

</details>

<details>
<summary>Methodology and limitations</summary>

The 0–10 priority score is an editorial triage aid, not asset-specific risk. EPSS is probabilistic, and source-backed findings still require asset, exposure and vendor validation. Expert RSS excerpts and Hacker News engagement are contextual signals, not verified threat evidence.

</details>
