from datetime import datetime, timedelta, timezone
import json
from zoneinfo import ZoneInfo

from cyberdailylog.pipeline import Pipeline
from cyberdailylog.reliability import build_evidence, prospective_summary


def test_pipeline_metrics_are_separate_consistent_and_contain_no_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("NVD_API_KEY", "synthetic-private-value")
    pipeline = Pipeline(output_dir=tmp_path, offline=True)
    report = pipeline.run(datetime(2026, 7, 14, tzinfo=timezone.utc), datetime(2026, 7, 16, tzinfo=timezone.utc))
    raw = (tmp_path / "pipeline-metrics.json").read_text()
    metrics = json.loads(raw)
    assert "synthetic-private-value" not in raw
    assert metrics["outcome"] == "fixture_only" and metrics["report_generated"] == report.generated_at.isoformat()
    assert all(
        metrics["phases_ms"][p] >= 0
        for p in ["ledger_load", "prepare", "collection", "epss", "matching", "render", "ledger_write"]
    )
    assert metrics["sources"]["nvd"]["pages"] == 2
    assert len(metrics["sources"]) == len(report.source_health) == 8
    assert "pipeline_metrics" not in json.loads((tmp_path / "latest.json").read_text())


def test_job_step_timings_preserve_unknown_milestones_and_partial_core():
    jobs = {
        "jobs": [
            {
                "name": "collect",
                "started_at": "2026-10-19T10:00:00Z",
                "completed_at": "2026-10-19T10:05:00Z",
                "steps": [{"name": "Collection", "started_at": "2026-10-19T10:00:10Z", "completed_at": None}],
            }
        ]
    }
    health = [
        {"source": s, "status": "failed" if s == "nvd" else "healthy"} for s in ["cisa_kev", "nvd", "github_advisories"]
    ]
    metrics = {"outcome": "partial", "phases_ms": {"collection": 1000}}
    row = build_evidence({}, health, {}, {}, jobs, metrics)
    assert row["job_durations_seconds"]["collect"] == 300
    assert row["step_durations_seconds"]["collect"]["Collection"] is None
    assert row["core_complete"] is False and row["pipeline_metrics"] == metrics


def test_prospective_slo_requires_a_full_window_without_reclassifying_history():
    start = datetime(2026, 10, 20, 10, tzinfo=timezone.utc)
    madrid = ZoneInfo("Europe/Madrid")
    history = []
    for index in range(30):
        target = (start.astimezone(madrid) + timedelta(days=index)).replace(hour=12).astimezone(timezone.utc)
        history.append({"scheduled_for": target.isoformat(), "status": "on_time", "publication_lag_seconds": 60})
    old = {"scheduled_for": "2026-10-19T10:00:00Z", "status": "failed", "publication_lag_seconds": None}
    all_rows = [old, *history]
    assert prospective_summary(all_rows, start + timedelta(days=1), start)["met"] is False
    summary = prospective_summary(all_rows, datetime(2026, 11, 18, 13, tzinfo=timezone.utc), start)
    assert summary["full_window_observed"] and summary["met"] and summary["measured_publications"] == 30
    assert summary["earliest_full_window_date"] == "2026-11-18"
    assert old["status"] == "failed" and all("monitoring_started_at" not in r for r in all_rows)
    assert history[0]["scheduled_for"].startswith("2026-10-20T10:")
    assert history[-1]["scheduled_for"].startswith("2026-11-18T11:")


def test_publisher_duplicate_is_recorded_as_skipped_without_a_second_publication():
    row = build_evidence(
        {"created_at": "2026-10-19T10:35:00Z"},
        [],
        {},
        {
            "GITHUB_EVENT_NAME": "push",
            "PREFLIGHT_RESULT": "success",
            "COLLECT_RESULT": "success",
            "PUBLISH_RESULT": "success",
            "PUBLISH_DUPLICATE_CLOSE": "true",
        },
    )
    assert row["status"] == "skipped" and row["actual_publication_time"] is None


def test_prospective_window_counts_missing_days_even_if_scheduler_never_runs():
    start = datetime(2026, 10, 20, 10, tzinfo=timezone.utc)
    result = prospective_summary([], datetime(2026, 11, 18, 13, tzinfo=timezone.utc), start)
    assert result["measured_publications"] == 30 and result["attainment_percentage"] == 0
    assert result["full_window_observed"] is True and result["met"] is False
    assert all(row["status"] == "missing" for row in result["days"])
