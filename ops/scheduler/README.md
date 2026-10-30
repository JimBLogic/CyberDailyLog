# External publication wake-up

## Current operating contract — 30 October 2026

One existing ChatGPT task runs with exact_schedule at **12:00 and 13:00,
Europe/Madrid**. Its reproducible definition is in automations.json; task IDs
and credentials remain outside the repository. It requires a complete,
consistent core close before skipping work.

Core collectors now get one additional collection attempt after **20 seconds**
only when their HTTP client exhausted retries on 500/502/503/504. The same
coverage dates are used; partial pages are discarded. Healthy and optional
collectors are not repeated. Authentication, TLS, malformed responses, rate
limits and Retry-After beyond budget retain their failure behavior. Per-source
pipeline metrics record recovery attempts, wait, initial error and outcome;
request/page/byte counters include both collections.

The task reconciles a finished partial/transiently failed workflow and, after
**90 seconds**, may issue one sequential recovery request without waiting for
13:00. At most two deterministic request IDs are allowed per invocation.
It checks for an active run and a winning complete publication before every
write, preserves the noon SLO target and never modifies files other than
ops/scheduler/request.json. These task-level retries cover failures remaining
after the pipeline's own bounded source recovery.

GitHub cron remains backup at 12:00, 12:17 and 13:30. GitHub and ChatGPT dispatch
may still be delayed; these changes do not guarantee punctuality or source
availability. Cloudflare Cron source/tests remain prepared but **not deployed
or production-verified**. No additional scheduler, token or paid service was
introduced.

The sections below preserve earlier observations, not the current task count.

## Historical status — 19 October 2026

The independent Cloudflare adapter from PR43 is reconciled against main after
PR47/48 in [cloudflare/](cloudflare/README.md). Source/tests are prepared;
deployment and a real provider-scheduled dispatch are **not verified** because
owned Cloudflare access and a managed Actions dispatch credential are absent.
The adapter now requires complete core coverage before suppressing recovery.
Existing GitHub cron remains backup; no personal automation was changed.

The two-task description below records the September setup, not a fresh claim
about current personal task state. PR43 recorded their later consolidation;
retain these definitions for audit and do not overwrite unrelated tasks.
See [complete-close quality](../../docs/ops/complete-close-quality.md) for the
separate prospective measure; historical publication SLO is unchanged.

Two independent task definitions were confirmed enabled on **22 September 2026**, starting on 23 September: **CyberDailyLog publicación 12:00** and **CyberDailyLog recuperación 13:00**, both daily in **Europe/Madrid**, including daylight-saving changes. Each has a single explicit hour. The publication objective remains noon; the 13:00 recovery does not extend the 60-minute SLO. The independent scheduler uses the connected GitHub app; no new PAT or server is required for this route. Reproducible task definitions are in [automations.json](automations.json); task identifiers and credentials are not stored in the repository.

The original combined 12:00/13:00 task produced no retained noon request on 22 September. Its prompt also aborted when started more than one minute early. Both issues are removed: the definitions now separate the two clock times, and a task starting up to ten minutes before noon waits, checking the actual clock at most every 30 seconds. It never writes before noon. Available records do not establish whether an early start caused the missed noon request; this is a corrected failure path, not a proven scheduler-internal diagnosis.

## Verified recovery, not SLO attainment

On 22 September the external request commit `0b6c71b7497a6e908dfa4b2e0fd7e29527df2293` was created at 11:04:28 UTC. [Run 35719431824](https://github.com/JimBLogic/CyberDailyLog/actions/runs/35719431824) was created and started three seconds later. Publication commit `1a686682dfb4ad99e7ce82749ae603245bb18c84` was successfully pushed at **13:06:39 Madrid**. The route worked, but publication was **3,999 seconds after noon**, outside the 3,600-second objective. The measured window remains **0/7 on-time days**, with no full 30-day sample. The corrected noon schedule needs its first daily observation; do not infer future punctuality from this recovery test.

Later GitHub cron runs correctly skipped duplicate collection and retained their own timing without replacing this publication. The dashboard exposes both records separately.

Each execution reads the latest `reports/publication-timing.json` and its current request file from `main`. If a successful measured publication exists for today's Madrid noon target, it exits. Otherwise it updates only `ops/scheduler/request.json` with schema version 1, origin `chatgpt_automation`, a daily request ID, the noon target in UTC and the current request timestamp. It uses the current blob SHA to prevent overwriting a concurrent change and the commit prefix `ops: request daily publication`. It must never modify reports, source, workflows, permissions or other files.

After a write, reconcile the returned commit and its `Daily Blue Team Intelligence` run. A connector timeout is an unknown outcome: read the current request and recent runs before another write. A request accepted by GitHub is not proof of publication. The workflow must finish, publish coherent reports and persist timing evidence. Requests before noon are activation checks only and cannot establish daily SLO success.

The scheduler should notify the owner only of a verified dispatch, workflow or publication failure, with commit/run evidence. Do not describe connector access errors as report corruption or emit a routine daily summary. The existing disabled health-watch automation is separate and remains unchanged.

## Optional systemd route

`cyberdailylog-dispatch.service` and `.timer` are templates for an independently operated Linux host, not an installed service. `scripts/dispatch_due.py` previews by default; `--apply` requires a repository-scoped Actions-write credential in the host environment. Its three opportunities are 12:00, 12:20 and 12:40 Madrid. Do not run this second route merely because templates exist; the connected scheduler already supplies an independent wake-up.
