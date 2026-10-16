# Independent scheduled wake-up (candidate, NOT DEPLOYED)

This directory is a self-contained **Cloudflare Cron Trigger** adapter for the
existing GitHub `daily-intelligence.yml`. It is independent of ChatGPT personal
task capacity and independent of GitHub Actions' unreliable `schedule` wake-up.
The GitHub workflow still owns collection, source quorum, idempotent preflight,
report commit, archive and SLO evidence; this Worker **does not** write reports.

## Architecture and trigger policy

Cloudflare Cron expressions are **UTC**. `wrangler.jsonc` selects 10:00,
10:20, 10:40 and 11:00, 11:20, 11:40 UTC daily. Exactly three of those
normally fall between 12:00 and 13:00 Europe/Madrid, depending on daylight
saving. Other UTC slots are skipped. `planWakeup` uses the actual Madrid
calendar time and target, never a hardcoded summer or winter UTC offset.

At an eligible slot, the Worker (1) checks the latest immutable published
milestone in `reports/publication-timing.json`, (2) checks that no new daily
workflow is already running, and (3) issues one `workflow_dispatch` if the
daily publication has not succeeded. It supplies an explicit request timestamp,
which the existing workflow records as `external`. This reuses its existing
`concurrency` and publication preflight guard. An accepted GitHub dispatch is
**not proof of a published report**.

Only `scheduled()` can request the action. The HTTP `fetch()` handler returns
404; `workers_dev` is disabled and no routes are configured. There are no
publicly exposed write endpoints, D1 bindings, API keys or tokens in git.
The Worker's credential only needs **GitHub Actions: read/write** on
`JimBLogic/CyberDailyLog`. This permission does not allow changes to source
or repository contents. If GitHub read/validation or credentials fail, the
Worker fails closed; no blind dispatch is sent.

Cloudflare cron scheduling is also not an exact-delivery SLO guarantee.
The 12:20/12:40 attempts improve resilience, but we must measure real pushes.

## Read-only readiness and local checks

Run from this directory:

```bash
node --test worker.test.mjs
```

Inspect `wrangler.jsonc` and the GitHub Actions workflow before deployment.
**Nothing in this PR installs, activates or deploys the Worker.**

## Owner-authorized deployment ONLY after review

1. Verify the actual Cloudflare account's Cron Trigger eligibility, region,
   limits and billing, and create a dedicated Worker named
   `cyberdailylog-independent-wakeup` rather than editing ABCM/BrangeCycle.
2. Provision a *repository-only, fine-grained, expiring* GitHub token with
   **Actions write** (not Contents write, Workflows write, or Admin).
   Prefer a machine-managed GitHub App token service if short-lived tokens can
   be renewed safely. Never share a token through chat, logs, Issues, or git.
3. From this directory, install/run a reviewed pinned Wrangler version,
   securely run `wrangler secret put GITHUB_ACTIONS_TOKEN` to store the secret
   **in Cloudflare**, and only then deploy this isolated Worker and its cron.
4. Check the first true noon cron execution and Workers logs for accepted/skipped
   decisions, then cross-check GitHub workflow creation, `publish` job success,
   the repository push, and the timing ledger's `trigger_origin=external`,
   UTC `dispatch_requested_at` and Madrid SLO status. Re-check tomorrow and
   during the CET↔CEST switch. Log errors without authorization headers.
5. Only **after** multiple real punctual publications, reconcile the existing
   ChatGPT `Seguimiento unificado` automation: retain its iPhone/IBAVI tasks,
   and retire just its redundant noon/recovery prompts in a separate approved
   change. Keep GitHub schedule as passive recovery until safe to reduce it.
   Do not disable or overwrite unrelated tasks.

Keep weekly and 30-day SLO measurement; historical failures are immutable.
A Cloudflare Cron invocation success alone does not close issue #41.
