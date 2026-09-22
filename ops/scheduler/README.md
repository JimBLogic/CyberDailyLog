# External publication wake-up

The active schedule is recorded here after activation. Target: **12:00 Europe/Madrid daily**, including daylight-saving changes. The independent scheduler uses the connected GitHub app; no new PAT or server is required for this route.

Each execution reads the latest `reports/publication-timing.json` and its current request file from `main`. If a successful measured publication exists for today's Madrid noon target, it exits. Otherwise it updates only `ops/scheduler/request.json` with schema version 1, origin `chatgpt_automation`, a daily request ID, the noon target in UTC and the current request timestamp. It uses the current blob SHA to prevent overwriting a concurrent change and the commit prefix `ops: request daily publication`. It must never modify reports, source, workflows, permissions or other files.

After a write, reconcile the returned commit and its `Daily Blue Team Intelligence` run. A connector timeout is an unknown outcome: read the current request and recent runs before another write. A request accepted by GitHub is not proof of publication. The workflow must finish, publish coherent reports and persist timing evidence. Requests before noon are activation checks only and cannot establish daily SLO success.

The scheduler should notify the owner only of a verified dispatch, workflow or publication failure, with commit/run evidence. Do not describe connector access errors as report corruption or emit a routine daily summary. The existing disabled health-watch automation is separate and remains unchanged.

## Optional systemd route

`cyberdailylog-dispatch.service` and `.timer` are templates for an independently operated Linux host, not an installed service. `scripts/dispatch_due.py` previews by default; `--apply` requires a repository-scoped Actions-write credential in the host environment. Its three opportunities are 12:00, 12:20 and 12:40 Madrid. Do not run this second route merely because templates exist; the connected scheduler already supplies an independent wake-up.
