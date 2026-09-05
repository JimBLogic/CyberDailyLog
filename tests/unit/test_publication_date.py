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
