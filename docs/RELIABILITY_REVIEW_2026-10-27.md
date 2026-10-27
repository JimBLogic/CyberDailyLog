# Reliability review — 27 October 2026

Evidence checked before the Madrid noon publication window. The latest report dated 26 October is therefore expected, not evidence of a missed 27 October close.

## Observed state

- Public `/api/intelligence` returned HTTP 200, live data and an operational pipeline. Its complete-close indicator agrees with the canonical timing artifact: 57.1% over seven measured days. This is a short observation window and below the 90% project objective.
- Last published collection recorded ten healthy sources. Zero accepted recent entries in a nonempty RSS or releases response does not indicate an outage.
- Direct bounded checks on 27 October: all four configured RSS feeds parsed; NVD, GitHub Advisories, FIRST EPSS, Hacker News and the three configured release repositories returned nonempty expected JSON arrays. These checks establish connectivity and basic structure, not exhaustive ingestion completeness.
- CISA KEV returned HTTP 403 from the review environment. The last production collection had succeeded. Current connectivity from the production runner is not established by this local probe.
- GitHub scheduled run 40381129021 started at 18:49:13 UTC for nominal 12:30 UTC on 26 October, approximately 6h19m late. Its successful skip reflects an already completed report, not punctual scheduling.
- The existing QA automation is enabled; its latest inspected recorded run completed on 26 October. Delivery status is unknown. A null next-run field alone does not establish stoppage. No duplicate automation was created.
- Independent Cloudflare scheduler source and twenty tests pass. Deployment, managed secret availability and a real external dispatch remain unverified; source code alone does not prove an active scheduler.

## Changes

- Validate RSS/Atom document roots, require nonempty configured Krebs/SANS feeds and restrict article origins. Reject missing article links instead of silently falling back to the feed URL. Optional-source failures remain nonblocking and visible as degraded health.
- Extract separate CISA reference URLs from note text and remove credential-bearing links. Normalize existing compound references at the dashboard boundary without rewriting historical records.
- Supply explicit CERT-EU names, links and government provenance in the contextual lane; RSS does not establish confirmed exploitation.

## Validation

Python suite: 252 passing, 94.30% coverage. Scheduler: 20 passing. Dashboard regression tests cover compound references, encoded separators, legitimate encoded spaces, unsafe links and CERT-EU attribution. Run the dashboard build and complete tests before publication.

## Remaining operational work

Punctuality is degraded. Verify the independent scheduler in its actual Cloudflare account and correlate an observed dispatch with a GitHub workflow run before declaring it active. Continue measuring complete daily closes; no reliability percentage was reset or inflated. Guard remains paused.

## Follow-up after recovery publication

Run 40503898871 completed successfully. Public API subsequently reported generation 12:29:52 UTC and publication 12:30:29 UTC (13:30:29 Europe/Madrid), 5,429 seconds after the noon objective. `coreComplete=false`: NVD failed while CISA and GitHub Advisories were healthy. Complete-close SLO is now 50% over eight measured days, still an incomplete observation window. A successful workflow and a recent partial report do not establish a complete daily close.

## Publication race found during final checks

Run 40508422492 collected all ten sources successfully (including NVD), but `Commit and push generated outputs` failed with `main -> main (fetch first)` after another main commit landed. This is a publication race, not a provider failure. No complete-close receipt was produced.

The publisher now permits at most three ordinary pushes. After a rejected push it retries only when origin/main actually advanced, revalidates the immutable bundle and retained ledger against that exact new baseline, suppresses publication if another complete daily close exists, and rebases without force. A conflict, history regression, authorization failure without a main advance or exhausted attempts stops publication. Successful push timestamps are emitted only after a successful push; duplicate closes emit only the duplicate receipt.

Local Git integration tests reproduce code-only concurrent advancement, a concurrent complete close, a newer remote ledger and a push denial. They verify both branches' changes survive the successful recovery, duplicate/newer history remains untouched, and failures never produce a successful push receipt.

## Bounded NVD window recovery

The latest failed NVD capture reported a changing total during pagination, rather than a connection failure. Retry a changed total or duplicate-CVE window once from offset zero using the same original dates. Discard the entire abandoned attempt, keep pacing and metrics cumulative across the restart, and record `window_restarts`. Invalid metadata, no progress and transport errors do not restart the full window (transport retries remain owned by the HTTP client). Persistent instability returns no items and a failed source; it never becomes healthy by merging partial pages.

Regression tests cover total and duplicate recovery without mixed CVEs, identical date bounds, rate pacing across the restart, persistent instability bounded to two attempts, and no extra full-window retry for transport failures. This improves recovery but does not establish an immutable provider snapshot or punctual daily publication; reliability measurements and Guard's paused state remain unchanged.
