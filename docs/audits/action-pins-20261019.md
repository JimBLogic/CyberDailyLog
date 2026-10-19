# Reviewed artifact Action patch updates — 19 October 2026

The failures in runs 39242376648 (PR36) and 39242370690 (PR37) were stale
literal assertions, not evidence that the new Action SHAs were untrusted.
All 223 Python tests were reached; the single static pin test rejected the old
SHA's absence. Dashboard jobs passed. Do not disable that security check.

Verified against the official `actions` repositories:

| Action | Release | Full immutable commit | action.yml Git blob |
|---|---|---|---|
| upload-artifact | v7.0.2 | cf430e030ddbb5b0abf93d22962f4752f3646cd9 | 7cb4d1e81db55320b41217e1a78a1a46e3d2baef |
| download-artifact | v8.0.2 | 9000827ccba6bdab643e8b6fd33ac0654aef8333 | 8b8c65029ccad20750a29fecb438eca5a607fc57 |

Both official release tags resolve exactly to those commits. GitHub reports
both merge commits' signatures verified/valid (7 October). Some individual
contributor commits are unsigned; this is not a claim that every commit was
signed or an independent reproducible build of the upstream bundles.

Read both complete action.yml files: runtime remains node24. Current Ubuntu
24.04 hosted runners support it. All inputs used by this repository remain
supported. Upload still archives directories by default; download still
extracts by default and fails digest mismatch by default. Explicit error mode
is retained in the CI transport smoke. No publication paths/permissions change.

Reviewed official old-to-new comparisons: upload changes @actions/artifact
6.2.0 to 6.3.1; download changes 6.2.1 to 6.3.1 with retry/RPC dependency fixes,
regenerated bundles, lock/license changes and documentation. No application
scoring, ledger or collection change is part of this update.

`ops/supply-chain/actions.json` is a finite record of individually reviewed
SHAs. Baseline #47 pins remain listed for compatible rollback; no tag, SHA
prefix, semver range, arbitrary owner or unknown commit is accepted. The test
examines every Action usage, rather than finding one approved literal while
missing another unreviewed usage. Directed rejection cases guard that policy.

For future updates: compare the official tag and commit, verify release
provenance, read runtime/inputs and relevant source/bundle/lock changes, then
add only that exact SHA with review evidence. Require the full CI including
the real upload/download byte roundtrip. This registry is review evidence,
not an automated oracle of trust. Changes to it need the same code review.

Upstream evidence:
- https://github.com/actions/upload-artifact/releases/tag/v7.0.2
- https://github.com/actions/download-artifact/releases/tag/v8.0.2
- https://github.com/actions/upload-artifact/compare/043fb46d1a93c77aae656e7c1c64a875d1fc6a0a...cf430e030ddbb5b0abf93d22962f4752f3646cd9
- https://github.com/actions/download-artifact/compare/3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c...9000827ccba6bdab643e8b6fd33ac0654aef8333

Rollback: restore the prior two reviewed artifact SHAs without changing report
data, integrity gates or other Action pins. This change consolidates PR36/37;
those original Dependabot proposals must not be merged again over this state.
