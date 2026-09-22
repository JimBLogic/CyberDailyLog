# Publication incident: 21 September 2026

## Verified timeline

Evidence comes from the repository's publication timing file and GitHub's public workflow-run/job APIs, inspected on 22 September. All times below are Europe/Madrid (CEST, UTC+02:00).

| Milestone | Time | Evidence |
| --- | --- | --- |
| Daily target | 12:00:00 | Configured IANA schedule |
| Workflow created | 18:08:17 | Run `35623652203` |
| Workflow run started | 18:08:17 | Same run; zero run-level queue delay |
| Preflight job started | 18:08:21 | Job `106412553043`; 3 seconds after job creation |
| Collection job started | 18:08:35 | Job `106412644070` |
| Source fetch started | 18:08:48.355972 | Source-health timestamps |
| Source fetch finished | 18:09:12.695248 | 24.339 seconds total |
| Report generated | 18:09:13 | Published report |
| Commit created | 18:09:32 | `be43bcdafecf10f2691739dd43549c7349a3c609` |
| Push completed | 18:09:37 | Actual publication milestone |
| Later scheduled run created | 18:28:42 | Run `35625845577`; collection and timing skipped |
| Last scheduled run created | 19:09:00 | Run `35630143552`; collection and timing skipped |

The commit lag was 6 h 9 min 32 s; successful-push lag was 6 h 9 min 37 s. The delay before workflow creation was 6 h 8 min 17 s: 99.64% of total publication lag. Creation-to-push was 80 seconds. The job queues add seconds, not hours. The two later scheduled executions both arrived after publication and correctly skipped duplicate collection. Their exact cron-slot identity was not retained; do not infer it solely from arrival order.

Run links:

- https://github.com/JimBLogic/CyberDailyLog/actions/runs/35623652203
- https://github.com/JimBLogic/CyberDailyLog/actions/runs/35625845577
- https://github.com/JimBLogic/CyberDailyLog/actions/runs/35630143552

The current evidence locates the problem before workflow creation. It cannot identify GitHub's internal reason. The [official schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) supports IANA timezone scheduling and warns that scheduled events can be delayed or dropped. The workflow's Madrid timezone is valid; neither a fixed UTC offset nor a six-hour collector bottleneck is established by these observations.

## Recovery design failure

All three cron triggers depend on the same GitHub scheduling service. Their nominal spacing provides no independent wake-up mechanism. Repeating the same dependency is not a guarantee that one event arrives before 13:00. Keep the existing schedules as backup, without moving the noon objective or offsetting cron by an assumed delay.

There was also an observability defect: the timing job was disabled when freshness preflight skipped collection. The correction retains every scheduled attempt, its cron expression, creation/start timestamps, explicit creation lag, and preflight decision. `publication-timing-history.json` includes skipped attempts without counting them as publications. `publication-timing.json` preserves the last publication and adds `last_attempt`, so a late recovery cannot erase real publication evidence. The daily SLO still counts failed/missing days and never gains a success from a skipped job.

## Independent wake-up through the connected scheduler

The noon automation uses the existing GitHub connection to update only `ops/scheduler/request.json` on `main`, with the commit prefix `ops: request daily publication`. This push starts the daily workflow without GitHub's cron scheduler. It first checks the measured publication for the Madrid calendar day and does not send another request if a successful publication after noon already exists. The workflow's serialized freshness preflight is the final duplicate-publication guard. The request must not use `[skip ci]`, which would also suppress the publication workflow. The unrelated CI workflow ignores a push containing only this request file.

Timing records `trigger_origin: external_push` and GitHub's immutable triggering commit timestamp. It measures noon-to-request, request-to-workflow-creation, workflow queue and publication separately. A late external automation remains a late publication. An activation check before noon does not count as an on-time publication and does not suppress the noon collection. A successful test verifies the push route; daily delivery and the 30-day SLO still require observation.

The activation record and exact automation schedule are maintained in `ops/scheduler/README.md`. The three GitHub cron slots remain additional recovery opportunities. The external scheduler and GitHub's push events/runners can also fail; this arrangement removes the observed common cron dependency without claiming a timing guarantee.

## Optional independent host adapter, not installed

`scripts/dispatch_due.py` is a provider-neutral adapter for an independently scheduled `workflow_dispatch`. The systemd examples in `ops/scheduler/` invoke it at 12:00, 12:20 and 12:40 Madrid time, including DST. It exits if a measured publication already exists and uses GitHub's authenticated workflow preflight as the final duplicate-publication guard. There are at most three external dispatch opportunities daily. It does not keep an Actions runner waiting for noon.

The script previews by default. It sends a request only with `--apply` and `GH_ACTIONS_TOKEN` configured on the independent host. Use a fine-grained credential restricted to this repository with Actions read/write; it does not need contents write. Never put the credential in source, command arguments, reports or chat. The examples expect a dedicated `cyberdailylog` user, a reviewed checkout at `/opt/cyberdailylog`, and a root-readable environment file `/etc/cyberdailylog/scheduler.env`. Install the timer only on an authorized, continuously running host with working time synchronization. No host, timer or credential has been provisioned by adding these files.

The request timestamp travels with the dispatch. Timing separates external request-to-run-creation delay from run queue and publication delay, while retaining the original Madrid noon target. Invalid/future request timestamps cannot create an on-time result. HTTP 204 means accepted, not published; verify the resulting workflow, report and timing evidence.

The latest incident-time measured SLO is 0 of 6 days on time, a partial 30-day sample. Neither an enabled trigger nor a successful activation test establishes 95% attainment; measured daily publications must demonstrate improvement.
