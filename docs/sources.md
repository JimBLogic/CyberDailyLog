# Sources

Last verification date for documentation review: 2026-07-15. Fixture tests are included; live API success is not claimed by this PR.

## Enabled sources

| Source | Owner | Official documentation / endpoint | Auth | Rate limits | Data collected | Frequency | Tier | Failure behaviour | Licence / attribution |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| CISA KEV | CISA | `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` | None | Public feed; be polite | CVE, date added, required action, ransomware flag | Updated by CISA | 1 | Required for publication quorum | Cite CISA feed |
| NVD CVE API 2.0 | NIST NVD | `https://services.nvd.nist.gov/rest/json/cves/2.0` | Optional `NVD_API_KEY` header | Official NVD guidance recommends modified-date parameters and sleeping scripts for six seconds between requests; unauthenticated access is slower | CVE metadata, CVSS, references, published/modified timestamps | Continuous | 1 | Required major vulnerability source | This product uses data from the NVD API but is not endorsed or certified by the NVD. |
| FIRST EPSS | FIRST.org | `https://api.first.org/data/v1/epss` | None | Batch CVE lookups; avoid one request per CVE | EPSS score, percentile, score date | Daily | 1 | Degraded enrichment only | Cite FIRST EPSS |
| GitHub Advisories | GitHub | `https://api.github.com/advisories` | Optional `GITHUB_TOKEN` | Public or token API limits | Reviewed public advisories, GHSA/CVE, CVSS, packages, ranges | Continuous | 1 | Required major vulnerability source | GitHub advisory links |
| CISA Cybersecurity Advisories RSS | CISA | `https://www.cisa.gov/news.xml` | None | Public RSS | Official advisory metadata | Periodic | 2 | Optional; failure does not block | Link to source |
| GitHub Releases allowlist | GitHub project owners | `https://api.github.com/repos/{owner}/{repo}/releases` | Optional `GITHUB_TOKEN` | Public or token API limits | Significant release metadata | Project-specific | 3 | Optional | Link to release |

## Implemented but disabled / future

Red Hat OVAL, abuse.ch ThreatFox, URLhaus, MalwareBazaar, AlienVault OTX, MISP feeds, paid services, and LLM APIs are documented as future interfaces only. They are disabled until terms, safety, volume, parser reliability, and tests are reviewed.
