# Functional and accessibility review — 27 October 2026

Scope: CyberDailyLog original, desktop browser interaction, compiled Worker/API regression tests and responsive source review. This is an engineering review, not a WCAG conformance certification. Guard remains paused.

## Findings and changes

| Finding | Effect | Change |
| --- | --- | --- |
| Fresh partial report had no prominent warning | Recent publication could be mistaken for complete coverage | Visible, announced limited-coverage banner on every view, including affected source labels |
| Identical watchlist button names | Assistive technology could not identify the advisory | Include advisory ID and expose pressed state in details |
| Detail button name included the full description | Excessively long keyboard/screen-reader navigation | Concise name with action, ID and title; visible description remains readable |
| Native modal selected the first control instead of the intended close button | Initial focus differed from the UI intent | Explicit close-button focus after showModal; native trapping, Escape and return focus preserved |
| Clearing filters removed the focused button | Focus fell to BODY | Restore focus to search; watchlist removals in the filtered list focus the watchlist filter |
| Intro H2 preceded the page H1 | Misleading heading order | Treat decorative intro title as styled text |
| Chart values available only through graphic/tooltips | Incomplete equivalent access | Expandable table with caption, column and row headers, focusable horizontal scroll region |
| Source metrics had visually separated headers but no spoken labels | Received/accepted/latency ambiguous | Add metric labels for assistive technology |
| Export scope unspecified | Users could assume filters applied | Explicitly state that exports contain all advisories in the selection |
| History labelled eight days while feed can hold thirty | Misleading chart title | Use daily history label |

Existing skip link, focus outlines, labelled native search/select, pressed states, reduced-motion rules, self-hosted fonts, decorative empty alt text and touch targets were preserved. Add system forced-colors boundaries without overriding the user's colors. Light/dark token contrast checks remain in the automated suite; these checks do not prove contrast of every rendered combination.

## Verification and boundaries

- Baseline live UI: page navigation, search for a specific CVE, no-results state, medium severity filter, modal open, Escape and return focus exercised. The filter reset focus loss was reproduced before repair.
- Compiled production tests cover API and export contracts, CSV formula neutralization, safe URL boundaries, partial/failed/stale/future/missing data, complete-close metric semantics, archive table output, theme persistence and blocked local storage.
- Responsive CSS reviewed at mobile (680px), tablet (681–1180px) and desktop boundaries, including dialog dynamic viewport, safe areas, wrapping and horizontal regions. Physical iPad/Safari, VoiceOver, NVDA and real touch interaction have not been tested. Managed preview navigation timed out; do not count that as a successful browser test of the patch.
- Operational reliability remains degraded: recent publication is partial due to NVD failure; see the reliability review. No historical evidence was rewritten, scheduler secretly activated or measurement reset.

Final production interaction checks and deployment/PR references are recorded in the delivery response. No claim of full accessibility compliance is made.
