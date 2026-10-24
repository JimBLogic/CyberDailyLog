# CyberDailyLog — read-only checkout security candidate (2026-10-16)

**Scope:** Original, non-fork `JimBLogic/CyberDailyLog` at `main` baseline `5f2f6a3ea972e2365b8d611b5a656e515bbd8ee4`. Candidate `audit/read-only-checkout-boundaries-20261016`. Only GitHub workflow credential handling and deterministic regression tests are changed. **No merge, scheduled collection, data output update, dashboard deployment or publication.**

## Audited separation of privileges

The active `daily-intelligence.yml` already has a useful privilege split: `preflight` and `collect` use `contents: read`, while `publish` and `timing` have deliberate `contents: write` and check `refs/heads/main`. The Python pipeline receives the built-in GITHUB_TOKEN for **read-only GitHub API collection**. Its publication uses the built-in GitHub token; no personal PAT is required.

However, `actions/checkout` on the **read-only** jobs defaulted to `persist-credentials: true`, leaving an authenticated Git credential helper available to all subsequent process steps, including code that consumes remote feeds and (for CI) package installations. The same unnecessary credential persistence existed in the two `ci.yml` jobs. While the job tokens were already read-only, explicit credential separation limits accidental token availability to later commands. This was an unnecessary credential-exposure surface, **not evidence of credential theft or a demonstrated exploitation**.

## Candidate-only remediation

- Set `persist-credentials: false` in four checkouts: daily `preflight` and `collect`, CI `test` and `dashboard`. Preserve the exact SHA-pinned `actions/checkout` revision, path, job, runtime and original permissions.
- Preserve Git authentication for trusted `publish` and `timing` jobs, because those jobs push generated artifacts to main; do not break the existing schedule or its Madrid timezone, 12:17/13:30 recoveries, manual `dry_run`, source quorum, history or write paths.
- Add three tests in a **new** `tests/integration/test_readonly_checkout.py` file to enforce those invariants. Existing `tests/integration/test_workflow_static.py` is left intact.
- The existing independent [DRAFT security PR #38](https://github.com/JimBLogic/CyberDailyLog/pull/38) handles Next.js, Cloudflare, HTTP redirects and other dependencies; it is **not modified**, merged or reimplemented here.
- The remaining pipeline still has deliberate `contents:write` for publishing from main, meaning GitHub configuration/branch rules, generated artifact allowlist and upstream feed integrity remain separate review tasks. This is **not** a claim of end-to-end supply-chain protection.

## Verification

Expected validation is the repository's existing `CI` workflow on PR head, including both the Python tests and dashboard checks. Because `daily-intelligence.yml` has **no pull_request trigger**, real collection and publication cannot run on this PR. Do not trigger the production workflow or use live secrets to test this candidate. Verify GitHub run IDs and logs on the exact final head before reporting PASS.

**Review-only DRAFT: NO merge/deploy/publish.**
