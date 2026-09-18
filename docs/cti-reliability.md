# CTI state and publication reliability

## Durable intelligence

`reports/cti-state.json` stores schema-2 per-CVE observations and transition history. Multi-CVE advisories are split before correlation. CISA, vendor evidence, NVD, GHSA and retained archive observations have deterministic precedence. Repeating unchanged input does not emit another daily discovery. Older source revisions cannot overwrite a newer revision; confirmed positive exploitation evidence survives unknown values and optional-source outages.

Material changes include KEV entry, confirmed exploitation, ransomware association, vendor-confirmed exploitation, a source-tagged public exploit, explicitly configured critical-asset exposure, meaningful CVSS changes (at least one point or crossing 4/7/9), severity escalation, CISA deadline/action changes, new fixed versions and withdrawal. A transition contains before/after state, source links and priority before/after, including HIGH to EMERGENCY. Initial discoveries carry their observed state without inventing an earlier state.

NVD is queried by modification time. CISA's full catalog is compared because entries have no per-record modification timestamp. The next window overlaps the last successful coverage by two hours and expands after missed runs. Gaps beyond NVD's 120-day limit fail explicitly and require a controlled backfill. A failed core quorum or dry run cannot advance the persisted baseline. Publication concurrency is serialized.

The first live migration on 18 September exposed a response-size failure in NVD's larger modified-record payloads. NVD now requests 500 records per page, halves an oversized page at the same offset, and respects request spacing. The byte limit remains enforced. When a core source fails but the remaining quorum can publish, its catch-up watermark is retained until all core collectors succeed. An early-morning manual or code-change publication does not suppress the noon target.

On the first run, retained report archives seed `first_seen` and known evidence. These are observation dates, not original disclosure dates. Old catalog entries and legacy CISA deadline fields are baselined without presenting the entire catalog as new events. Existing records can still emit genuine newly observed operational changes. The compact ledger keeps its event history; monitor repository size and migrate storage before approaching GitHub's per-file size limit.

`config/operational-evidence.yml` supports analyst-verified vendor statements with a CVE, HTTPS primary-source URL, confirmation timestamp and explicit confirmation. It is empty by default: RSS prose is never automatically converted into confirmed exploitation. `config/technologies.yml` accepts explicitly confirmed critical-asset CVEs; a technology keyword alone does not establish exposure. NVD's Exploit reference tag establishes a public exploit reference, not exploitation in the wild. Positive historical evidence is retained; retractions require an audited correction rather than silent removal on a missing feed.

## Observed delay

The [16 September run](https://github.com/JimBLogic/CyberDailyLog/actions/runs/35109073506), artifact `10451417324`, supplies the original milestones. The original evidence is retained as a test fixture and normalized in the initial publication timing report.

| Milestone | UTC on 2026-09-16 |
| --- | --- |
| Target (12:00 Europe/Madrid) | 10:00:00 |
| Workflow creation and start | 14:31:08 |
| Fetch start | 14:31:26.391522 |
| Fetch end | 14:31:48.602814 |
| Report generated | 14:31:48 |
| Commit created | 14:32:02 |
| Push completed | 14:32:03 |

The publication lag was 16,323 seconds (4 h 32 min 3 s). The delay before workflow creation was 16,268 seconds; runner queue time was zero, collection took 22.211 seconds and start-to-commit took 54 seconds. The evidence locates the delay before workflow creation. It does not identify GitHub's internal scheduling cause and does not prove a four-hour timezone error.

[GitHub's schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) supports IANA timezones and warns of delayed or dropped scheduled jobs, especially around the start of the hour. The workflow keeps noon in `Europe/Madrid`, adds an off-peak 12:17 recovery inside the objective, and retains 13:30 recovery. It does not compensate by blindly moving the cron four hours earlier. All three events use the same freshness guard. They still depend on GitHub scheduling, so recovery is a mitigation rather than independent scheduling redundancy.

## Measurement contract

The objective is at least 95% of eligible Madrid calendar days published within 60 minutes of noon, over a rolling 30-day window. One day contributes at most one result; the earliest successful publication wins. Failed and missing days count after the deadline. Dry runs and skipped recovery checks do not create successes. Days before monitoring began are excluded and a partial observation window is clearly labelled. Monitoring's original start is preserved when old attempts age out.

Publication means a successful repository push. It does not measure when every browser sees the new dashboard. Status is `on_time` at up to 60 minutes, `delayed` up to three hours, `stale` after three hours, `failed` on a failed publication path, or `unknown` when essential evidence is missing. Missing milestones are null. Original run creation is used for retries and DST-aware target inference. GitHub exposes no nominal occurrence ID, so a scheduled event delayed by more than a day cannot be unambiguously assigned.

The timing job runs after successful or failed collection/publication, commits the evidence/history and uploads a bounded diagnostic artifact. The dashboard shows target, measured publication, lag, delay stage, SLO sample size and evaluation date. It marks missing current-day measurement after the deadline. Core source coverage is separate from optional enrichment; old healthy snapshots are not shown as currently healthy. Legacy reports without CTI counters show unavailable measurements.

## Validation and operational limits

Automated tests cover baseline/new CVEs, unchanged replay, KEV, exploitation, ransomware, vendor evidence, public exploits, CVSS/severity changes, deadline/action/remediation changes, multi-CVE correlation, stale source revisions, unknown evidence, optional-source failure, source ordering, migration, dry runs and rejected core quorum. Timing tests cover DST, delayed creation, runner queue, collection/publication delay, missing milestones, retries, failed/missing days and retention of the monitoring start. Dashboard tests cover hostile data, partial coverage, unavailable measurements, rendering and privacy controls.

Run the matrix in [operations](operations.md), then the dashboard's `npm test`, `npm run typecheck`, `npm run lint`, `npm audit` and `npm run verify:mirror -- <Sites checkout>`. The Sites version must be built from the matching source commit and confirmed deployed. A real main-branch collection must validate report, ledger and timing publication. Passing tests or one successful live run does not establish 30-day reliability: continue observing the SLO, and do not claim 95% attainment before the measured evidence supports it.
