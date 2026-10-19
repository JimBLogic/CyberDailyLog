# Independent wake-up — reviewed source, NOT DEPLOYED

Reconciles all six files of PR43 against main after PR47/48. The original PR43
was 11 commits ahead and 25 behind baseline b4e2f8b; GitHub reported mergeable.
Its old timing guard stopped after any quorum publication and its last-30-runs
scan could miss an active daily workflow. Preserve the existing main code,
read-only checkouts, reviewed Node24 Action pins and publication integrity gate.
Do not restore the older branch's dependency or dashboard snapshots.

## Policy

The one UTC cron `0,20,40 10,11 * * *` gives six invocations; only the actual
12:00/12:20/12:40 Europe/Madrid hour can request work. IANA conversion handles
CET/CEST; a delayed invocation after 13:00 skips, not a backdated request.
Logs record actual and nominal scheduled times separately.

Read public timing without a credential. Stop only for a same-day report
generated after noon, pushed successfully and explicitly core_complete=true
(CISA KEV, NVD and GHSA healthy). A green/on-time partial quorum stays eligible.
The timing file's complete_close_status is complementary; the underlying
completeness and timestamps remain authoritative for this guard.

Before dispatch, query the daily workflow specifically for each of in_progress,
queued, waiting, pending and requested, with per_page=1. Any active run, including
one started before noon, suppresses duplicate work; completed CI runs cannot
hide it. Malformed or unavailable evidence fails closed. Reads are bounded to
512 KiB and 15 s. Redirects are rejected. There is no immediate retry storm.

Use the documented GitHub API 2026-03-10 dispatch response (200 with a run ID
and repository-bound URLs), rather than treating a legacy empty 204 as current
proof. Record the returned run for correlation. Do not retry an ambiguous POST:
the next cron must reconcile before trying again. Acceptance is not publication.

The adapter is stateless, and suppression is best effort: simultaneous provider
retries can race before a GitHub run is visible. Existing non-cancelling workflow
concurrency, complete-close preflight and publisher history/duplicate gates
enforce the idempotent published result. Do not promise exactly-once dispatch or
add a database merely to make that claim. GitHub cron remains backup unchanged.

## Permissions and secrets

Use a repository-only fine-grained expiring token with **Actions: read/write**;
Metadata read is implicit. No Contents write/read, Workflows write, Administration
or other repository permissions are needed by this code. Public timing goes to
the fixed raw.githubusercontent.com URL without Authorization; the token is
sent only to the fixed api.github.com repository Actions endpoints.

Actions write is GitHub's smallest endpoint permission, not a single-workflow
restriction: a stolen token can affect other Actions in this repository. Limit
repository selection, expiration and rotation accordingly. Long-lived managed
GitHub App credentials can replace the token later if a supported renewal
service is actually available; none is provisioned here. A PAT needs rotation
and is not maintenance-free.

Only scheduled() wakes GitHub. HTTP GET/POST/PUT/DELETE return 404 and cannot
write. workers_dev=false, preview_urls=false, routes=[]; no D1, KV or public
writer. Store GITHUB_ACTIONS_TOKEN as a Cloudflare Secret. No credential is
embedded in source, error text, query strings, returned results or logs.
Unknown transport errors are logged as fixed codes, without upstream bodies.

## Current evidence and missing capability

20 Node tests passed, including four DST boundary dates, partial recovery,
filtered active runs, credentials, redirects, oversized JSON, ambiguous POST,
receipt validation, no HTTP writer and scheduled timestamp/log sanitization.
Original PR43's seven tests also passed before reconciliation; they did not
detect its obsolete quorum guard. Wrangler 4.151.0 validated the bundle with
deploy --dry-run (8.21 KiB / gzip 3.07 KiB, no bindings). **No deployment or real
Cloudflare scheduled invocation occurred.** Mocked scheduled() tests are local.

Wrangler whoami returned unauthenticated. No connected Cloudflare plugin was
found. Sites-managed hosting does not grant access to an owned Cloudflare
account or a scheduler secret. No temporary account, duplicate Site or substitute
public Worker was deployed. Code preparation is complete; activation is blocked.

## Minimal owner actions, official interfaces only

1. In [GitHub fine-grained tokens](https://github.com/settings/personal-access-tokens),
   generate a token for resource owner JimBLogic, **Only select repositories →
   CyberDailyLog**, Actions read/write, with an expiry after the observation
   window (for example 60 days). Leave other optional permissions unset.
2. In [Cloudflare Workers & Pages](https://dash.cloudflare.com/?to=/:account/workers),
   use your existing account to create/select `cyberdailylog-independent-wakeup`.
   In its code editor deploy this directory's reviewed worker.mjs as an ES module.
   In Settings → Variables and Secrets → Add → Secret, put the GitHub token
   directly as GITHUB_ACTIONS_TOKEN. Disable workers.dev/preview URLs, leave all
   routes empty, and preserve the configuration in wrangler.jsonc. Add the Cron
   Trigger `0,20,40 10,11 * * *` under Settings → Triggers. No payment/DNS change
   is authorized. If account limits require payment, stop activation.
3. Clear the clipboard after pasting, retain the secret in the managed setting,
   and rotate before expiry. Share only the Worker name/deployment ID and
   non-secret scheduled event/run IDs for verification; **never paste the token
   in chat, git, Issues, screenshots or public settings**.

Prefer publishing code and managed secret before adding the cron so an initial
event cannot run unconfigured. If a Worker with this name already exists,
inspect it and preserve its previous version before replacing anything.

## Operational acceptance and rollback

Wait for a **true provider Cron event**, not a dashboard Test Trigger/manual
dispatch. Correlate nominal/actual event times, the logged accepted run_id,
GitHub event=workflow_dispatch with external timestamp, healthy source evidence,
report/ledger commit and real Site data. Check both ordinary publication SLO and
complete-close quality; separately record Site visibility. A skipped event after
an existing complete close validates suppression but not the dispatch path.
Cloudflare changes can take up to 15 minutes to propagate; measure actual
delivery over multiple days. Maintain GitHub schedules and personal automations.

Rollback activation by removing this Worker's Cron Trigger or restoring its
previous version, then revoking its dedicated token. Keep GitHub backups and
all reports/ledger. A code rollback must retain the ledger, schemas and PR45–48
controls; never restore old data to revert scheduler code.

Primary references:
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
- https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-workflow
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- https://developers.cloudflare.com/workers/configuration/cron-triggers/
- https://developers.cloudflare.com/workers/configuration/secrets/
