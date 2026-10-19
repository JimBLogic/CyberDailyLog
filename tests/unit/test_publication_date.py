from datetime import datetime, timezone
import json
from pathlib import Path
import runpy

publication_date = runpy.run_path(str(Path("scripts/publication_date.py")))["publication_date"]


def publish(root, stamp="2026-09-04T22:15:00+00:00", degraded=False, mixed=False):
    report = {
        "generated_at": stamp,
        "degraded": degraded,
        "items": [],
        "source_health": [
            {"source": "cisa_kev", "status": "healthy"},
            {"source": "nvd", "status": "healthy"},
            {"source": "github_advisories", "status": "healthy"},
        ],
    }
    (root / "latest.json").write_text(json.dumps(report))
    for name in ("portfolio-feed.json", "dashboard-feed.json"):
        (root / name).write_text(json.dumps({"generated_at": "bad" if mixed else stamp, "project": "CyberDailyLog"}))


def test_uses_madrid_date_across_utc_midnight(tmp_path):
    publish(tmp_path)
    assert publication_date(tmp_path, datetime(2026, 9, 4, 23, tzinfo=timezone.utc)) == "2026-09-05"


def test_mixed_or_degraded_report_must_not_suppress_recovery(tmp_path):
    publish(tmp_path, degraded=True)
    assert publication_date(tmp_path) == ""
    publish(tmp_path, mixed=True)
    assert publication_date(tmp_path) == ""


def test_missing_or_future_report_must_not_suppress_recovery(tmp_path):
    assert publication_date(tmp_path) == ""
    publish(tmp_path, stamp="2099-01-01T00:00:00+00:00")
    assert publication_date(tmp_path) == ""


def test_morning_publication_does_not_suppress_noon_target_in_summer_or_winter(tmp_path):
    for morning, noon in [
        ("2026-09-05T09:59:59Z", "2026-09-05T10:00:00Z"),
        ("2026-01-05T10:59:59Z", "2026-01-05T11:00:00Z"),
    ]:
        now = datetime.fromisoformat(noon.replace("Z", "+00:00"))
        publish(tmp_path, stamp=morning)
        assert publication_date(tmp_path, now, require_after_noon=True) == ""
        publish(tmp_path, stamp=noon)
        assert publication_date(tmp_path, now, require_after_noon=True) == noon[:10]


def test_quorum_success_with_failed_core_keeps_recovery_eligible(tmp_path):
    publish(tmp_path)
    path = tmp_path / "latest.json"
    report = json.loads(path.read_text())
    for source in report["source_health"]:
        if source["source"] == "nvd":
            source["status"] = "failed"
    path.write_text(json.dumps(report))
    assert publication_date(tmp_path) == ""


def test_duplicate_scheduler_attempts_keep_same_complete_close(tmp_path):
    publish(tmp_path, stamp="2026-10-19T10:29:02Z")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    for _ in range(3):
        assert (
            publication_date(tmp_path, datetime(2026, 10, 19, 11, tzinfo=timezone.utc), require_after_noon=True)
            == "2026-10-19"
        )
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
