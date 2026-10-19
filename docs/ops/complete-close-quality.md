# Publication punctuality versus complete CTI close

Keep the original historical `slo` and prospective_slo unchanged. Neither a
green workflow nor an on-time quorum report establishes full core coverage.

`publication-timing.json` adds these complementary, schema-compatible signals:
- `complete_close_status`: on_time, late, partial, not_published, unknown,
  skipped or fixture_only. Uses actual push, report generation, target and
  explicit core_complete (CISA KEV + NVD + GHSA healthy).
- `complete_close_on_time`: true only for a complete close pushed by 13:00
  Madrid; false for measured late/partial/unpublished closes; null for unknown,
  skipped or fixture evidence. A later skipped attempt retains the winning
  publication's signal and records its own status separately.
- `complete_close_slo`: a distinct 30-calendar-day quality measure starting
  20 October 2026. Every elapsed 13:00 Madrid deadline counts, including missing,
  failed and unknown days. Pending deadlines never enter the denominator early.
  Report generated before noon, future fixtures, unknown source health or a
  partial quorum cannot count as an on-time complete close.

The first full prospective window remains 20 October–18 November after the
18 November deadline. The flag cannot be met before all 30 deadlines elapsed.
29/30 complete punctual closes satisfy >=95%; one success does not.

Example from the existing production evidence, without rewriting history:
19 October quorum pushed at 12:29:02 Madrid, NVD failed: historical on_time,
complementary partial. Recovery with all core sources healthy pushed at
13:12:03: complementary late. That day remains 19/30 (63.3%) in the historical
publication SLO and was not transformed into an on-time complete close.

Site availability stays separate: the push milestone cannot prove propagation,
HTTP access, browser rendering or visitor experience. Record real-domain
generation/run/source evidence independently. These changes do not rebuild the
dashboard, alter public intelligence schemas/scoring or claim browser QA.

Recovery remains eligible until all core collectors succeed, and after that
preflight/publisher prevent another complete daily close from replacing it.
Existing noon/12:17/13:30 GitHub backup cron and personal tasks are unchanged.
