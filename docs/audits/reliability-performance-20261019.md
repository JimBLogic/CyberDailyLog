# Reliability, performance and integrity — 19 October 2026

Baseline main: `716561839cba226e7d7e8fafc02b646ab15f00dc`, including PR #46.
Scope: original public CyberDailyLog pipeline. Private Guard, scoring, source
selection, public feed schemas, state format and noon objective are unchanged.

## Measured baseline

Reviewed all 184 daily workflow runs from 20 August through 19 October and their
job/step metadata: 151 schedule, 33 push; 175 succeeded and nine failed. All 184
job records were accessible. Provider-level historical timings are available for
36 attempts in the retained 30-day history; missing milestones remain unknown.
See `docs/evidence/reliability-baseline-20261019.json` for the measured summary
and exact run IDs. The complete per-run extraction is reproducible through the
GitHub run jobs API; records expose public timings, never credentials.

Three largest costs:

1. Native cron creation delay: median 18,798 s, p95 32,010 s across 82 recorded
   cron attempts in 30 days. Workflow queue median/p95/max: zero seconds in all
   184 runs. The provider's trigger delivery, rather than runner queue, dominates.
2. Latest external request arrived 1,291 s after noon; workflow creation followed
   two seconds later. External request p95: 4,575 s over 27 recorded requests.
3. Latest source collection took 403.938 s; NVD consumed 393.848 s and **failed**
   with a transport error. Seven sources were healthy; quorum publication still
   succeeded. A green workflow did not establish eight-source coverage.

Across available jobs, install median/p95 4/7 s; collection 27/286 s; artifact
upload 2/3 s; publish commit/push 5/10 s. Caching or replacing the package installer
cannot fix a five-hour trigger delay and offers little benefit versus NVD work.

The latest baseline publication was 12:29:02 Madrid, run 39236885511, commit
`df89deafeebc5db38f0976a643fb0343709fa6ef`. Historical SLO: 19/30, 63.3%.
It was on time as a quorum publication; its NVD coverage was incomplete. Preserve
that original SLO definition and evidence, rather than relabelling its history.

## Changes and security properties

- A report with a failed core source no longer suppresses daily recovery. A
  complete close requires CISA KEV, NVD and GHSA healthy. Useful quorum feeds can
  still be published with source health and retained catch-up watermark.
- HTTP retries cover transient transport failures, stay on the approved HTTPS
  origin, never relax TLS, and observe the provider interval. Certificate errors
  fail immediately. Retry-After up to 60 s is honoured; a longer delay fails the
  bounded operation rather than retrying prematurely. Secrets remain excluded
  from errors and metrics.
- NVD parses each bounded raw page before requesting the next and releases raw
  CPE trees. It preserves every mapped field, rejection and provenance. Duplicate
  CVEs, inconsistent totals/offsets and non-progressing pages fail the source
  rather than claiming complete coverage. All-or-nothing source failure preserves
  the ledger catch-up watermark for the next attempt.
- A separate `pipeline-metrics.json` records monotonic phase timings, source
  status, page requests, provider waits, HTTP attempts/retries and ledger bytes.
  Public feed schemas remain unchanged. Timing evidence also records GitHub job
  and step durations; unfinished milestones remain null.
- Each uploaded bundle has a SHA-256 manifest covering its exact file set,
  feeds, metrics and daily archive. The main-only publisher downloads into an
  isolated directory, verifies it against current main and checks historical
  CVEs, first_seen, source keys/modified dates, transition prefixes and watermark
  before copying or staging. Truncated/mixed/stale artifacts fail closed.
- A second publisher encountering an already complete Madrid daily close skips
  replacement, preserves the winner and records its attempt as skipped. Partial
  coverage can be recovered; a successful daily close is not rewritten by a late
  recovery. The README dynamic block is regenerated against current main so
  intervening editorial changes remain intact.

## Performance evidence and limits

A deterministic workload of 600 CVEs / 12 pages with 20 KB of unused CPE data per
CVE reduced traced peak allocation from 15,370,308 to 7,172,360 bytes (53.3%). All
mapped fields had the same SHA-256 after normalizing collection timestamps.
This is a **synthetic memory benchmark**, not a real-provider latency test or a
measurement of total process RSS. CPU was approximately 0.13 versus 0.12 s under
tracemalloc; that small difference is not treated as a reliable speedup.

The state serializer/compression format is unchanged, byte-preserving and atomic.
No historical pruning or database migration was introduced. Runner publication
checks add bounded validation cost in exchange for rejecting history loss before
Git commit. Record actual runtime/source metrics and gzip size from the release
run before claiming a production performance improvement.

## Scheduler strategy and prospective measurement

Keep the autonomous GitHub noon schedule and 12:17 / 13:30 Madrid recovery slots,
non-cancelling concurrency and immutable action pins. Recovery preflight avoids
unnecessary collection after a complete close. DST tests preserve noon through
the March/October transitions. GitHub officially supports the configured IANA
timezone but warns that scheduled events can be delayed/dropped:
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

Reliable independent wake-up remains an infrastructure blocker. Existing PR #43
contains a separate Cloudflare Cron adapter with repository-only Actions-write
dispatch, no public writer and DST/idempotency tests. It is not deployed. Here
Wrangler reports unauthenticated, and the public Site has runtime env revision 0
with no entries; no provider account/dispatch credential is provisioned. Native
Sites exposes personal cloud-task schedules, not an independent Cron credential.
Do not use temporary Wrangler accounts or personal ChatGPT automations as the
permanent solution. Existing personal tasks are preserved during migration.

Next infrastructure action: provision an existing owned Cloudflare account and
repository-scoped dispatch credential through secure platform settings, then
exercise the adapter's intended scheduled access and read back the real GitHub
run. This is justified by the measured trigger delays, but cannot be activated
from source code alone. Keep GitHub cron until independent scheduled evidence
proves recovery; no DNS changes or new public write endpoint are needed.

A separate prospective SLO starts with the first full treated day, **20 October**.
Its first full 30-day window ends **18 November 2026** after the day's 13:00
Madrid deadline. At least 29/30 on-time days are needed for the >=95% criterion.
The prospective flag cannot be met with an incomplete window. This operational
window is not a statistical guarantee of future reliability. The historical
denominator, objective and classifications are not changed.

## Sites, visual QA and release gates

Existing public Site: appgprj_6a63172b53c88191b00398c6ccafb36c. Deployment
appgdep_6ad267b2245481918c1698728d87c52f remains publishing since 16 October
18:07 UTC, failure_message null; latest saved version is 26. Cause is unknown:
the visible state does not distinguish provider/integration/permission defects.
Native capabilities expose no cancel/restart. Escalate this project/deployment
and timestamp through OpenAI Help support; preserve prior versions. Do not create
another Site, alter audience/DNS or deploy an unrelated Worker as a substitute.

Managed browser capability is unavailable. Browser/viewport/keyboard/touch/
screen-reader/contrast/reflow checks remain unrun. Service-authenticated real
HTTPS checks and local rendered-HTML tests must be labelled separately from
anonymous browser QA. Follow Sites SKILL.md's explicit no-browser fallback rule.

Before merge: full Python/coverage/Ruff/mypy, fixtures/schemas/wheel, full dashboard
build/lint/types/tests and audits; meaningful corruption, duplicate, failure,
provider and DST tests. After merge: exact-head CI, a real recovery collection,
ledger preservation, coherent published feeds and real-domain readback. A 403
anonymous check is a blocked check, not a successful visitor check.

Rollback: revert only this focused code change through a reviewed commit. The
baseline above and all earlier public Site versions remain recoverable and read
the unchanged gzip ledger. Never reset/reseed data or remove later transitions.

Development risk: braces GHSA-vfj7-8cjw-p6xm remains unpatched in the audited
build/lint graph (eight inherited high package entries, one advisory). Production
audit is zero. Keep the finding visible; do not force old Next/Vinext downgrades.
https://github.com/advisories/GHSA-vfj7-8cjw-p6xm
