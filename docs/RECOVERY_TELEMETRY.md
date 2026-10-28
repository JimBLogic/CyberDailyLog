# Recovery telemetry contract v1

Additive `recovery_telemetry` in schema-v2 publication timing. Existing SLO fields,
publication identity and last_attempt remain unchanged. Legacy timing without
this object remains valid and displays the declared telemetry gap.

Each observed attempt exposes `run_id`, `trigger`, `started_at`, `finished_at`,
`outcome`, `recovered_from`, `publication_id`; `run_attempt` distinguishes GitHub
reruns of the same run. `recovered_from` is null or {run_id, run_attempt}.
All times are zoned UTC strings or null. Never substitute retrieval time.

- started_at: actual workflow start, not its creation timestamp.
- finished_at: successful repository publication time; otherwise the latest
  completed preflight/collect/publish job when the attempt has failed or skipped.
  It is not completion of the timing job itself.
- outcome: published (explicitly complete core), partial (explicitly incomplete
  core), failed, skipped or unknown. Missing core coverage stays unknown.
- publication_id: original report publication commit SHA, never the metrics commit.
- recovered_from: immediate preceding observed failed/partial attempt in the same
  noon target, only when finish/start evidence establishes non-overlapping order.
  A skipped attempt is neither a retry nor another publication.

The retained first observed attempt is not proof that the planned primary cron ran.
An absent primary is not fabricated. Attempts are deduplicated by run+attempt.
Recovery duration runs from the first linked failed/partial finish to restored
complete publication, including intervening queue time. Missing milestones keep
it null, never zero. Retry count measures evidenced links, not all later cron runs.
The dashboard independently validates links and derives duration from milestones.

This measures repository publication recovery, not Site availability, source
connection retries or a statistical guarantee. It does not alter historical SLO.

The producer adds telemetry on the next normal timing publication after integration.
No historical reports are rewritten to invent missing starts/finishes. The dashboard
shows known fields and unknown markers until sufficient observed evidence exists.
