# Source catalogue and responsible reuse

Review date: 26 October 2026. This catalogue distinguishes live connectors from
reading resources and candidates. Public access or an educational purpose does
not by itself grant redistribution rights. No affiliation or endorsement is implied.

## Optional additions in this change

| Publisher | Feed | What CyberDailyLog retains |
| --- | --- | --- |
| CERT-EU | [Security advisories](https://cert.europa.eu/publications/security-advisories-rss) | Title, publisher/author, feed timestamp, original link and attribution links |
| CERT-EU | [Security guidance](https://cert.europa.eu/publications/security-guidance-rss) | The same metadata, for defensive learning |

The publisher's [legal notice](https://cert.europa.eu/legal-notice) states
CC BY 4.0 unless otherwise noted, with attribution and identification of changes.
The connector deliberately omits descriptions, summaries, article bodies,
images, attachments and logos. Its configuration records the legal notice and
[licence](https://creativecommons.org/licenses/by/4.0/); these links are retained
in each item's references. Displayed titles are attributed to CERT-EU and link
to the original. No publisher text is presented as a CyberDailyLog explanation.

These are **optional context/reference sources**, using the existing analyst
context lane. RSS headlines do not establish affected versions, CVSS, active
exploitation or confirmed asset exposure. No such fields are inferred or added
to the CVE ledger. Read the original and its vendor references for mitigation.
The feed timestamp is not asserted to be the original CVE disclosure date.
Literal spaces in legacy article URLs are percent-encoded before strict HTTPS
origin validation; other control characters and off-origin links remain rejected.

Each feed is fetched once per existing collection, using the normal identified,
bounded HTTPS client. No new scheduler, article crawler, credential or private
query is introduced. Article links are restricted to HTTPS on cert.europa.eu.
The feeds each retained ten entries when probed. They are a recent-reference
window, not a complete archive or guaranteed delivery of every advisory.
Security guidance may legitimately publish infrequently; transport health is
measured separately from whether there is a new article in today's window.

The existing JSON report exposes all retained context items; the existing
dashboard shows up to four analyst briefs and the Markdown digest selects one.
These editorial limits are not claims that other source entries do not exist.

## Accessible learning and verification directory

The following links are **reading resources/candidates, not newly enabled
connectors**. Descriptions below are written for this project.

| Resource | Use | Integration decision |
| --- | --- | --- |
| [INCIBE-CERT advisories](https://www.incibe.es/incibe-cert/alerta-temprana/avisos) | Spanish advisories and remediation references | Link only; its [legal notice](https://www.incibe.es/incibe/aviso-legal) restricts distribution; no text redistribution enabled |
| [AWS security bulletins](https://aws.amazon.com/security/security-bulletins/) | Vendor announcements and service-specific action | Not enabled: tested RSS returned zero entries. [Site terms](https://aws.amazon.com/terms/) and separate RSS permissions need reconciliation before redistribution |
| [Ubuntu security notices](https://ubuntu.com/security/notices) | Package fixes and supported release information | RSS parsed successfully; keep as a reading resource until feed-specific reuse terms are established. General software/documentation licences are not assumed to cover every feed |
| [OSV API](https://google.github.io/osv.dev/api/) | Future package/version/commit matching | Candidate; validate ecosystem names, version matching, pagination and per-source data licences before activation |
| [CVEProject/cvelistV5](https://github.com/CVEProject/cvelistV5) | Original CVE JSON records | Candidate; no automatic complete mirror or extra weight for duplicated downstream evidence |
| [CISA Vulnrichment](https://github.com/cisagov/vulnrichment) | SSVC and structured enrichment | Candidate; preserve per-field provenance and distinguish an assessment from observed exploitation |
| [CIRCL Vulnerability-Lookup](https://www.vulnerability-lookup.org/documentation/) | Correlation and alternative lookup | Candidate; use the documented API sync path for complete ingestion, not a short RSS window |
| [Microsoft MSRC API](https://github.com/microsoft/MSRC-Microsoft-Security-Updates-API) | Microsoft product and security-update details | Candidate; validate API contract and redistribution conditions |
| [Red Hat security data](https://access.redhat.com/security/data) | CSAF/VEX product status and fixes | Candidate; separate parser required; existing OVAL source stays disabled |
| [Openwall oss-security](https://www.openwall.com/lists/oss-security/) | Maintainer disclosures and technical discussion | Discovery/reference; retain author and upstream advisory when verifying claims |
| [The DFIR Report](https://thedfirreport.com/) | Incident timelines and detection learning | Reading resource; no full-text copying or crawler added |
| [Cisco Talos](https://blog.talosintelligence.com/) | Threat research and detection context | Reading resource; no copying or new feed enabled |
| [Unit 42](https://unit42.paloaltonetworks.com/) | Campaign and incident research | Reading resource; no copying or new feed enabled |

Krebs, SANS ISC, Hacker News and existing defensive releases are retained without
expanding their excerpt permissions. This change is not a blanket legal clearance
of every historical source. Forums are discovery signals; follow the original
research or vendor announcement before accepting a claim. A public exploit or
popular post is not proof of exploitation in the wild.

## Reliability and rollout evidence

- Base: `0e1732a8e8c96ae9eafa02e202b85462fcf60029`.
- Direct read-only probes with the actual collector: advisories 10/10 accepted.
  Guidance initially rejected one legacy URL containing spaces; that observed
  incompatibility is repaired by percent-encoding spaces, with a regression test.
  Test fixtures are synthetic, not copied articles. No archive completeness or
  future provider uptime is inferred from a successful probe.
- New regression cases cover no body copying, attribution links, no inferred CVE
  state, CET/CEST conversion, unsafe origin rejection, DTD/entity rejection,
  empty/HTML/error payloads and successful core publication during RSS outages.
- Required CISA KEV/NVD/GHSA collectors, quorum, complete-close SLO, publication
  workflow, historical reports and durable ledger are unchanged.
- Frontend source has no changes; Sites remains version 27. GitHub versions
  this pipeline/config change separately. New data will flow through existing
  report/API contracts after an authorized merge and subsequent collection.

Keep every new connector optional until its actual production behaviour has
been observed. Do not count local tests as a provider uptime measurement or a
successful scheduled publication. Guard remains paused.
