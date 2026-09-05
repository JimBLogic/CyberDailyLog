# CyberDailyLog release review — 2026-09-05

This release fixes concrete failure paths found during a review of the public dashboard and its daily collection pipeline.

## Data correctness and recovery

- Repository JSON is parsed and validated before a delivery route is marked successful. Invalid JSON and malformed or future-dated reports can fall through to the alternate transport.
- Source health comes from the same report as the displayed items. Companion editorial content is accepted only when generation timestamps match. Counts are computed from the authoritative report.
- Stale reports and unavailable core-source health cannot report an operational pipeline or high coverage confidence.
- Automatic refresh retries after errors, bounds requests to 30 seconds, prevents overlapping requests, pauses network refresh in background/offline tabs and resumes when the page is visible/online.
- Refresh checks published information. It does not invoke GitHub Actions. The server retains its 15-minute shared cache; the API has no second HTTP cache hiding updates.

## Interface, access and privacy

- Native modal dialog provides keyboard containment, Escape dismissal and focus restoration. Search has an accessible label; filter and sorting state is exposed to assistive technology.
- Main-content navigation, back/forward navigation, document language, touch controls and reduced-motion behavior are handled explicitly.
- The briefing identifies its bounded selection and offers a filter reset. Headline sizing leaves more space for the working content; dialog and regular text are more readable.
- Only the small countdown updates each second; the full dashboard no longer rerenders on every tick.
- Storage access errors preserve a usable interface. Language/watchlist remain device-local, written after user actions, with no new storage keys.
- External feed links accept only absolute HTTP(S) destinations without embedded credentials. CSV cells neutralize formula prefixes before spreadsheet export.
- Existing canonical URLs, robots, sitemap and bilingual privacy disclosure are retained and covered by production HTML/privacy tests. No tracking or consent controls were added.

## Automation and collection

- GitHub advisory collection follows validated pagination cursors within a bounded collection window. Partial or looping pagination cannot claim healthy full coverage.
- Official first-patched-version and current CVSS fields are preserved.
- Recovery is skipped only for a coherent, non-degraded publication with live core-source quorum, using the Madrid calendar date.
- README updates regenerate the dynamic block against current main instead of replacing current prose with an older artifact.
- The 12:00 primary and 13:30 recovery schedule remain in Europe/Madrid. GitHub scheduling is best-effort, not a publication SLA.

## Release checks

The release gate consists of the existing Python CI, production Worker rendering, data failure scenarios, privacy guards, Worker-aware TypeScript checking and dependency audits. The GitHub PR records final results. No interactive browser or visual-compliance certification is implied by these automated checks.

## Operational boundaries

This dashboard is a bounded public intelligence briefing. It does not inventory a visitor's systems, prove their exposure or guarantee exhaustive internet coverage. A green collector status describes collection health. Runtime caches reset with Worker isolates. If live routes fail, the explicitly dated bundled snapshot remains available and is labelled as fallback.

Sites can record platform-level operational/visitor information independently of application code. The existing privacy page describes this limit; application controls do not claim to disable platform analytics.

## Reproduce and rollback

Run `npm ci`, `npm test`, `npm run typecheck`, `npm run lint`, and `npm audit --omit=dev --audit-level=high` in `dashboard/`. Run the Python commands in `docs/operations.md` from the repository root. The dashboard mirror includes the exact source, lockfile and regression tests. Use `npm run verify:mirror -- /path/to/other/dashboard` to compare checkouts.

Rollback application code by reverting the release PR and deploying the previous saved Sites version. Keep daily generated reports and the previous report archive; rollback does not require deleting history or changing access settings.

## Primary references

- [GitHub workflow schedule and queue limits](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [GitHub global advisories: filters, cursors, patched versions and CVSS](https://docs.github.com/en/rest/security-advisories/global-advisories#list-global-security-advisories)
