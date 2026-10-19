from copy import deepcopy
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from cyberdailylog.reliability import complete_close_status, complete_close_summary, slo_summary, publication_view

START = datetime(2026, 10, 20, 10, tzinfo=timezone.utc)


def row(day=0, seconds=60, core=True):
    target = (START.astimezone(ZoneInfo("Europe/Madrid")) + timedelta(days=day)).replace(hour=12)
    return {
        "scheduled_for": target.isoformat(),
        "report_generated": (target + timedelta(seconds=30)).isoformat(),
        "actual_publication_time": (target + timedelta(seconds=seconds)).isoformat(),
        "publication_lag_seconds": seconds,
        "core_complete": core,
        "status": "on_time" if seconds <= 3600 else "delayed",
    }


@pytest.mark.parametrize(
    "seconds,core,expected",
    [
        (60, True, "on_time"),
        (3600, True, "on_time"),
        (3601, True, "late"),
        (60, False, "partial"),
        (60, None, "unknown"),
    ],
)
def test_green_quorum_on_time_and_complete_on_time_are_distinct(seconds, core, expected):
    assert complete_close_status(row(seconds=seconds, core=core)) == expected


def test_partial_on_time_then_late_complete_does_not_improve_historical_slo_or_quality():
    history = [row(core=False), row(seconds=4323)]
    before = deepcopy(history)
    now = START + timedelta(hours=2)
    assert slo_summary(history, now)["on_time_publications"] == 1
    quality = complete_close_summary(history, now, START)
    assert quality["on_time_complete_closes"] == 0 and quality["days"][0]["status"] == "late"
    assert history == before


def test_partial_then_complete_in_window_counts_once_even_with_duplicate_skips():
    history = [row(core=False), row(seconds=3599), dict(row(), status="skipped"), dict(row(), dry_run=True)]
    result = complete_close_summary(history, START + timedelta(hours=2), START)
    assert result["measured_days"] == result["on_time_complete_closes"] == 1
    assert result["met"] is False


def test_missing_unknown_and_failed_days_stay_in_the_denominator():
    history = [row(core=None), dict(row(day=1), status="failed", actual_publication_time=None)]
    result = complete_close_summary(history, START + timedelta(days=2, hours=2), START)
    assert result["measured_days"] == 3 and result["attainment_percentage"] == 0
    assert [day["status"] for day in result["days"]] == ["unknown", "failed", "missing"]


def test_window_does_not_count_open_deadlines_or_future_fixture_rows():
    history = [row(index) for index in range(30)]
    assert complete_close_summary(history, START - timedelta(seconds=1), START)["measured_days"] == 0
    assert complete_close_summary(history, START + timedelta(minutes=59), START)["measured_days"] == 0
    assert complete_close_summary(history, START + timedelta(hours=1), START)["measured_days"] == 1
    end = datetime(2026, 11, 18, 12, tzinfo=timezone.utc)
    result = complete_close_summary(history, end, START)
    assert result["met"] and result["full_window_observed"] and result["measured_days"] == 30
    assert result["earliest_full_window_date"] == "2026-11-18"
    assert result["days"][0]["date"] == "2026-10-20" and result["days"][-1]["date"] == "2026-11-18"


def test_invalid_order_missing_provenance_and_fixture_are_never_confirmed_complete():
    for change in [
        {"report_generated": "broken"},
        {"report_generated": "2026-10-20T09:59:00Z"},
        {"report_generated": "2026-10-20T10:02:00Z"},
        {"actual_publication_time": None},
        {"core_complete": "true"},
    ]:
        assert complete_close_status(dict(row(), **change)) == "unknown"
    assert complete_close_status(dict(row(), dry_run=True)) == "fixture_only"


def test_skipped_recovery_preserves_real_late_winner_and_new_quality_signal():
    previous = dict(row(seconds=4323), schema_version=2)
    view = publication_view(previous, {"status": "skipped"}, [], START + timedelta(hours=2))
    assert view["complete_close_status"] == "late" and view["complete_close_on_time"] is False
    assert view["actual_publication_time"] == previous["actual_publication_time"]
    assert "complete_close_status" not in previous
