from cyberdailylog.recovery import recovery_telemetry
from cyberdailylog.reliability import build_evidence

TARGET = "2026-10-28T11:00:00Z"


def attempt(run="101", outcome="failed", start="2026-10-28T11:00:00Z", finish="2026-10-28T11:01:00Z", **extra):
    return {
        "run_id": run,
        "run_attempt": "1",
        "trigger_origin": "schedule",
        "scheduled_for": TARGET,
        "workflow_actual_start": start,
        "workflow_created": start,
        "attempt_finished_at": finish,
        "status": outcome,
        "core_complete": outcome == "published",
        "commit_sha": "a" * 40,
        "actual_publication_time": finish if outcome in {"published", "partial"} else None,
        **extra,
    }


def test_failed_attempt_links_to_success_with_observed_recovery_time():
    result = recovery_telemetry(
        [attempt(), attempt("102", "published", "2026-10-28T11:01:30Z", "2026-10-28T11:03:00Z")], TARGET
    )
    first, retry = result["attempts"]
    assert first["publication_id"] is None
    assert retry["recovered_from"] == {"run_id": "101", "run_attempt": "1"}
    assert retry["publication_id"] == "a" * 40
    assert result["recovery_seconds"] == 120
    assert result["retry_count"] == 1


def test_partial_publication_and_explicit_rerun_preserve_both_attempts():
    first = attempt(outcome="partial")
    retry = attempt(outcome="published", start="2026-10-28T11:02:00Z", finish="2026-10-28T11:04:00Z", run_attempt="2")
    result = recovery_telemetry([first, retry], TARGET)
    assert len(result["attempts"]) == 2
    assert result["attempts"][0]["outcome"] == "partial"
    assert result["attempts"][1]["recovered_from"] == {"run_id": "101", "run_attempt": "1"}


def test_skipped_attempt_is_not_a_publication_or_recovery():
    result = recovery_telemetry(
        [attempt(outcome="published"), attempt("102", "skipped", "2026-10-28T11:02:00Z", "2026-10-28T11:03:00Z")],
        TARGET,
    )
    assert result["attempts"][-1]["publication_id"] is None
    assert result["attempts"][-1]["recovered_from"] is None
    assert result["retry_count"] == 0
    assert result["recovery_seconds"] is None


def test_unknown_finishes_and_overlap_cannot_prove_recovery():
    published = attempt("102", "published", "2026-10-28T11:00:30Z", "2026-10-28T11:02:00Z")
    for first in [attempt(finish=None), attempt()]:
        result = recovery_telemetry([first, published], TARGET)
        assert result["recovery_seconds"] is None
        assert result["attempts"][-1]["recovered_from"] is None


def test_other_days_dry_runs_and_missing_targets_do_not_create_primary_attempts():
    result = recovery_telemetry([attempt(scheduled_for="2026-10-27T11:00:00Z"), attempt(dry_run=True)], TARGET)
    assert result["attempts"] == []
    assert result["first_observed_run_id"] is None
    assert recovery_telemetry([], None) is None


def test_complete_first_attempt_does_not_claim_a_recovery():
    result = recovery_telemetry([attempt(outcome="published")], TARGET)
    assert result["retry_count"] == 0 and result["recovery_seconds"] is None
    assert result["attempts"][0]["recovered_from"] is None


def test_failure_finish_comes_from_completed_processing_jobs_not_clock_now():
    row = build_evidence(
        {"created_at": TARGET, "run_started_at": TARGET},
        [],
        {},
        {"GITHUB_EVENT_NAME": "workflow_dispatch", "COLLECT_RESULT": "failure"},
        {"jobs": [{"name": "collect", "started_at": TARGET, "completed_at": "2026-10-28T11:01:00Z"}]},
    )
    assert row["attempt_finished_at"] == "2026-10-28T11:01:00+00:00"


def test_unknown_coverage_does_not_become_partial_or_recovered():
    result = recovery_telemetry([attempt(outcome="published", core_complete=None)], TARGET)
    assert result["attempts"][0]["outcome"] == "unknown"
    assert result["recovery_seconds"] is None


def test_missing_start_keeps_known_finish_without_fabricating_start():
    row = attempt(workflow_actual_start=None, workflow_created=TARGET)
    result = recovery_telemetry([row], TARGET)
    assert result["attempts"][0]["started_at"] is None
    assert result["attempts"][0]["finished_at"] == "2026-10-28T11:01:00+00:00"
