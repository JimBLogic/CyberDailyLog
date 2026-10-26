# CyberDailyLog original reliability review — 26 October 2026

Baseline: `cd546cf76113a2995bffeed83e373accc6141968`.
Scope: original repository and its public Site only. No Guard, other project,
production data, scheduler configuration or credential changes.

## Verified findings

**DEGRADED — dashboard SLO selection, confirmed.** The public
`https://cyberdailylog.jimblogic.chatgpt.site/api/intelligence` returned 70%,
30 measured days and a full window for the evidence evaluated on 25 October.
At the baseline, `reports/publication-timing.json` instead records a
`complete_close_slo` of 50%, 6 measured days and an incomplete window.
The old parser selects the distinct legacy `slo` publication-only series.
Impact: readers can mistake historical publication timeliness for complete
CISA KEV/NVD/GHSA close reliability. High reporting impact, high confidence;
not a security exploit or evidence of data loss.

The candidate selects only `complete_close_slo.measured_days` and its associated
percentage, window flag and evaluation date. No fallback to the legacy or
prospective series. Absent/invalid day counts remain unknown; zero observed
days cannot produce a percentage. A full window requires 30 integer measured
days, window_days=30 and the canonical full-window flag. Partial core coverage
is explicitly visible beside publication timing. The target remains unchanged.

**DEGRADED — active external automation can suppress partial-close recovery.**
Read-only inspection found the existing enabled combined task
"Proyectos + QA + Vulns" checks publication time and publication status before
exiting its 12:00/13:00 blocks; neither exit predicate requires
`core_complete === true`. This can stop recovery after a quorum-only partial
publication. This is a confirmed instruction mismatch, not proof it caused
a specific missed close. Confidence high; operational impact medium/high.
The independent Worker already requires complete core coverage.

Prepared activation change: preserve the existing task, times, request IDs,
write scope, other project blocks and deduplication; require schema_version=2,
core_complete=true, today's valid report_generated >= Madrid noon,
report_generated <= actual_publication_time <= actual current time, and accepted
publication status before suppressing recovery. Partial/missing completeness
must continue through the existing bounded active-run/request reconciliation.
Do not create another task or extend the 60-minute deadline. Live automation
editing requires owner approval; this review did not change it.

## Verified working behavior

- Latest publication: 25 October 2026, 12:44:08 Europe/Madrid (CET),
  [run 40189946624](https://github.com/JimBLogic/CyberDailyLog/actions/runs/40189946624).
  Complete core coverage, all eight recorded sources healthy; 1,425 report items.
- Newest 16 observed daily workflow runs (22–25 October) completed successfully.
  Many were deduplication skips; their successful conclusion is not counted as
  another successful daily close.
- `reports/cti-state.json.gz` is approximately 12 MB. The publication workflow
  uses gzip and validates the 50 MiB file budget before upload/commit. This
  addresses the historical uncompressed >100 MB rejection; no history rewrite.

## Candidate validation

- Python: 242 tests passed; coverage 94.16%; Ruff and mypy passed.
- Independent scheduler Worker: 20 tests passed, including Madrid CET/CEST,
  idempotency, partial-close recovery, token boundaries and ambiguous POSTs.
- GitHub dashboard build and all 27 tests passed; TypeScript and ESLint passed.
- Sites source build and all 38 tests passed, preserving its existing routes.
- Six new production-Worker scenarios assert canonical SLO selection, missing
  evidence, zero days, fractional day rejection, full window and partial core.
  They check API values and server-rendered page text together.
- npm production dependency audit: zero known vulnerabilities.
- pip-audit of requirements and development requirements: none found.

## Pending verification and deployment

Overall **DEGRADED**. Fixing the displayed metric does not raise reliability.
Complete-close measurement is 50% over 6 elapsed observed days at baseline,
below the owner's 90% gate; a full 30-day window is not yet available.

The code candidate is not merged or publicly deployed. Production rollout and
the existing automation predicate update require explicit owner approval.
After rollout compare canonical JSON, API and rendered page for the same
evaluation date. Preserve the separate publication-only history.

Independent Cloudflare scheduler: source/tests verified, actual managed secret,
deployment and provider-timed invocation **NOT TESTED** here. Do not infer live
operation from local tests. Automation run history was unavailable in the
read-only task response; timing effectiveness remains **NOT TESTED** beyond
the repository's retained request/publication evidence.

PR #50 (NVD/PHP collector changes) remains a separate unmerged candidate; this
review does not claim those advisories are collected in production. Browser
interaction/visual QA was not performed; compiled SSR/API regression checks
passed. No production collection or dispatch was initiated by this review.
