from datetime import datetime, timedelta, timezone
import pytest
from cyberdailylog.reliability import (
    daily_target,
    schedule_targets,
    publication_status,
    build_evidence,
    slo_summary,
    record_attempt,
    parse_timestamp,
)

NOW = datetime(2026, 9, 17, 13, tzinfo=timezone.utc)


def evidence(**overrides):
    env = dict(
        GITHUB_EVENT_NAME="schedule",
        TRIGGER_CRON="0 12 * * *",
        GITHUB_REPOSITORY="JimBLogic/CyberDailyLog",
        GITHUB_RUN_ID="35109073506",
        GITHUB_RUN_ATTEMPT="1",
        PREFLIGHT_RESULT="success",
        COLLECT_RESULT="success",
        PUBLISH_RESULT="success",
        COMMIT_CREATED="2026-09-16T14:32:02Z",
        PUSH_COMPLETED="2026-09-16T14:32:03Z",
    )
    env.update(overrides)
    return build_evidence(
        {"created_at": "2026-09-16T14:31:08Z", "run_started_at": "2026-09-16T14:31:08Z"},
        [{"started_at": "2026-09-16T14:31:26.391522Z", "finished_at": "2026-09-16T14:31:48.602814Z"}],
        {"generated_at": "2026-09-16T14:31:48Z"},
        env,
    )


def test_madrid_dst_transitions_and_slots():
    assert daily_target(parse_timestamp("2026-03-29T15:00:00Z")).hour == 10
    assert daily_target(parse_timestamp("2026-10-25T15:00:00Z")).hour == 11
    assert daily_target(NOW.replace(hour=8)).day == 16
    target, trigger = schedule_targets(NOW, "schedule", "17 12 * * *")
    assert target.hour == 10 and trigger.minute == 17
    target, trigger = schedule_targets(NOW.replace(hour=9), "schedule", "30 13 * * *")
    assert target.day == 16 and trigger.minute == 30
    assert schedule_targets(None, "schedule", "") == (None, None)
    assert schedule_targets(NOW, "schedule", "invalid") == (None, None)
    assert schedule_targets(NOW.replace(hour=8), "workflow_dispatch", "") == (None, None)
    assert schedule_targets(NOW, "workflow_dispatch", "")[0].hour == 10
    assert parse_timestamp("2026-09-17T10:00:00").tzinfo == timezone.utc


def test_status_bands_and_missing_milestones():
    target = NOW.replace(hour=10)
    for seconds, result in [
        (0, "on_time"),
        (3600, "on_time"),
        (3601, "delayed"),
        (10800, "delayed"),
        (10801, "stale"),
        (-1, "unknown"),
    ]:
        assert publication_status(target, target + timedelta(seconds=seconds), "success")[0] == result
    assert publication_status(target, None, "success") == ("unknown", None)
    assert publication_status(target, None, "failure") == ("failed", None)
    assert evidence(PUSH_COMPLETED="")["status"] == "unknown"
    assert evidence(PUBLISH_RESULT="failure")["actual_publication_time"] is None
    assert build_evidence({}, [], {}, {})["root_cause_stage"] == "unknown"


def test_observed_delay_is_before_workflow_creation():
    row = evidence()
    assert row["root_cause_stage"] == "scheduler" and row["status"] == "stale"
    assert row["publication_lag_seconds"] == 16323 and row["trigger_start_lag_seconds"] == 16268
    assert row["workflow_queue_seconds"] == 0 and row["fetch_duration_seconds"] == 22.211
    assert row["run_to_commit_seconds"] == 54


@pytest.mark.parametrize(
    ("started", "generated", "pushed", "stage"),
    [
        ("11:01:00", "11:01:10", "11:01:20", "workflow_queue"),
        ("10:00:00", "11:02:00", "11:02:10", "pipeline"),
        ("10:00:00", "10:00:10", "11:03:00", "publication"),
        ("10:00:00", "10:00:10", "10:00:20", "within_threshold"),
    ],
)
def test_distinguishes_queue_pipeline_and_publication(started, generated, pushed, stage):
    row = build_evidence(
        {"created_at": "2026-09-17T10:00:00Z", "run_started_at": f"2026-09-17T{started}Z"},
        [],
        {"generated_at": f"2026-09-17T{generated}Z"},
        {
            "GITHUB_EVENT_NAME": "schedule",
            "TRIGGER_CRON": "0 12 * * *",
            "PUBLISH_RESULT": "success",
            "PUSH_COMPLETED": f"2026-09-17T{pushed}Z",
        },
    )
    assert row["root_cause_stage"] == stage


def test_daily_slo_counts_failure_missing_dates_and_retries_once():
    first = evidence()
    on_time = {**first, "run_id": "2", "status": "on_time", "publication_lag_seconds": 40}
    preview = {**first, "scheduled_for": "2026-09-15T10:00:00Z", "dry_run": True}
    failed = {**first, "scheduled_for": "2026-09-17T10:00:00Z", "status": "failed"}
    result = slo_summary([first, on_time, preview, failed], NOW + timedelta(days=1))
    assert result["measured_publications"] == 3 and result["attainment_percentage"] == 33.3
    assert [r["status"] for r in result["days"]] == ["on_time", "failed", "missing"]
    assert result["full_window_observed"] is False and result["met"] is False
    assert slo_summary([], NOW)["attainment_percentage"] is None


def test_history_replaces_same_attempt_keeps_anchor_and_excludes_preview():
    first = evidence()
    assert len(record_attempt([first], first, NOW)) == 1
    assert len(record_attempt([first], {**first, "run_attempt": "2"}, NOW)) == 2
    assert record_attempt([], {**first, "dry_run": True}, NOW) == []
    with pytest.raises(ValueError):
        record_attempt({}, first, NOW)
    later = {**first, "scheduled_for": "2026-11-01T11:00:00Z", "status": "failed"}
    history = record_attempt([first], later, parse_timestamp("2026-11-01T15:00:00Z"))
    assert len(history) == 1
    assert slo_summary(history, parse_timestamp("2026-11-01T15:00:00Z"))["measured_publications"] == 30
