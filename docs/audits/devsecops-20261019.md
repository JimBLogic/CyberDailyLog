# CyberDailyLog DevSecOps verification — 19 October 2026

## Scope and rollback

Original public CyberDailyLog repository and its existing Site. Baseline:
`4eb868d392accf957216f780b81d12dbd82dbe21`, after the successful CTI storage
repair in PR #45. Preserve that commit and the complete compressed CTI ledger.
No changes to private Guard, authentication, plans, DNS, external services,
scoring, output schemas, source selection, retention or Madrid cron.

## Confirmed transport boundary and correction

The previous `SafeHttpClient` checked the initial hostname but delegated
redirects to urllib's default handler. An entirely simulated HTTPS transport
reproduced forwarding of a synthetic NVD apiKey header from the approved NVD
origin to an unapproved redirect destination. There were no real network calls,
real credentials or evidence of a historical compromise. Exploitation would
require a redirect from an approved source or a separately controlled source URL.

Selectively reconciled the transport candidate from PR #38, preserving the newer
dependency versions already merged by PR #45. The client now requires approved
HTTPS hosts on port 443, forbids URL userinfo, fragments, controls, whitespace,
oversized URLs and routing-header overrides, and rejects cross-origin redirects
before the next request. This also applies when the other host is allowlisted.
The effective response origin is rechecked. Same-origin redirects, bounded
response bodies and the existing retry/timeout budgets remain supported.
Malformed Retry-After values cannot cause an unbounded delay, and transport
errors expose the source hostname rather than a credential-bearing error body.

Tests exercise the real urllib redirect dispatch with an in-memory HTTPS
handler for 301/302/303/307/308 and a valid intermediate hop. The forbidden
destination never receives a request. This is neither a TLS bypass nor a
substitute for subsequent real collection with the managed source credentials.

## Least privilege in CI and collection

Selectively reconciled PR #39's credential boundary: the two read-only CI jobs
and daily preflight/collect checkouts use `persist-credentials: false`.
Their permissions remain `contents: read`. The trusted main-only publish and
timing jobs retain the Git authentication needed to publish. Collection still
receives its explicit read-only GitHub API token only in its existing step.
Regression tests enforce those boundaries and the unchanged cron/dry-run paths.

## Verification performed before pull request

- Python: 186 tests passed, 93.76% coverage; Ruff lint/format and mypy passed.
- Dashboard: clean `npm ci`, production build/Worker artifact verification,
  21 production/privacy tests, ESLint and Worker/TypeScript checks passed.
- `npm audit --omit=dev --audit-level=low`: zero reported advisories.
- Full npm audit: eight inherited high package findings, all from the single
  braces advisory below; zero critical/moderate/low findings. This is not zero.
- Fresh CI and a real post-merge collection/publication are still required;
  record exact run/commit identifiers in the pull request after completion.

## Residual risks and hosting limitation

`braces@3.0.3` / GHSA-vfj7-8cjw-p6xm remains the latest published version on
19 October. The advisory lists no fixed version. Its maintainer disputes the
threat model; that disagreement does not remove the reported finding.
The affected glob libraries are build/lint transitives, absent from the npm
production graph. Do not accept arbitrary visitor-defined glob patterns or
force the proposed unsupported Next/Vinext downgrades. Keep the full finding
visible and review a compatible upstream release before changing the lockfile.

- https://github.com/advisories/GHSA-vfj7-8cjw-p6xm
- https://github.com/micromatch/braces/issues/70

The existing public Site's UI deployment
`appgdep_6ad267b2245481918c1698728d87c52f` remains `publishing` since
16 October 18:07 UTC, without a failure message. Latest saved Site version: 26.
The native capabilities available here provide no cancel/restart operation;
continue that deployment rather than starting a duplicate or replacing the Site.
The working public Site can independently consume newly published repository
feeds. This code change does not claim a new UI deployment.

Managed browser control is unavailable in this session. Browser, screenshot,
viewport, keyboard, touch, zoom/reflow and visual accessibility checks are unrun.
Anonymous automated access is separately subject to Cloudflare blocking;
service-authenticated HTTPS checks must be labelled as such. These limitations
do not turn an unverified visual release into a completed one.
