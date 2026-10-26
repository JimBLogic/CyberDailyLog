# Signal Archive responsive UI

The original CyberDailyLog dashboard retains its data contracts, source links, privacy controls and complete-close SLO semantics.

- Desktop: illustrated briefing, ranked case cards and direct evidence access.
- Tablet: navigation on a second row and a single-column hero below 1180 CSS pixels.
- Mobile: stacked case cards, touch targets, 16 px search input and full-height evidence dialog with safe-area padding.
- Operational measurements remain available in a native disclosure; stale-data warnings stay visible.
- CVSS, EPSS and KEV remain separate. Unknown values use a dash, never a fabricated zero.

Ten original editorial images are stored locally in `public/illustrations` as optimized WebP, with empty decorative alt text. Only relevant images are mounted per view. The original generated PNGs and concept catalog are retained in the previously delivered design package. No third-party media requests are introduced.

Validation: build, dashboard regression suite, TypeScript and browser interaction/visual review. Responsive CSS can be checked in browser device tools at 390, 768, 820, 1024 and 1440 pixels. Physical iPad/Safari validation requires the device.

Run locally and self-host using README.md and docs/SELF_HOSTING.md. Compare the complete dashboard tree using `npm run verify:mirror -- /path/to/other/dashboard`. Only the existing retirement response is retained under `guard-site`; unused public-test bundles and historical product documents were removed from the dashboard checkout to restore source parity. Private Guard is unchanged.
