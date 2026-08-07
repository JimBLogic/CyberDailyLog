from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from cyberdailylog.dashboard_feed import build_dashboard_feed, summarize_report, write_dashboard_feed


def report(date: str, *, critical: int = 1, high: int = 1, low: int = 1, degraded: bool = False) -> dict:
    items = [
        *[
            {
                "canonical_id": f"CVE-{date}-C-{index}",
                "category": "vulnerability",
                "severity": "critical",
                "priority_score": 9.5,
                "cisa_kev": index == 0,
            }
            for index in range(critical)
        ],
        *[
            {
                "canonical_id": f"CVE-{date}-H-{index}",
                "category": "vulnerability",
                "severity": "high",
                "priority_score": 7.5,
            }
            for index in range(high)
        ],
        *[
            {
                "canonical_id": f"CVE-{date}-L-{index}",
                "category": "vulnerability",
                "severity": "low",
                "priority_score": 2.0,
            }
            for index in range(low)
        ],
        {
            "canonical_id": f"context-{date}",
            "category": "expert_commentary",
            "priority_score": 10,
        },
    ]
    return {
        "generated_at": f"{date}T08:17:00+00:00",
        "coverage_start": f"{date}T00:00:00+00:00",
        "coverage_end": f"{date}T08:00:00+00:00",
        "degraded": degraded,
        "items": items,
        "source_health": [
            {"source": "nvd", "status": "healthy", "required": True},
            {"source": "rss", "status": "degraded" if degraded else "healthy", "required": False},
        ],
    }


def test_summarize_report_separates_security_items_and_context() -> None:
    point = summarize_report(report("2026-07-21", critical=2, high=3, low=4))

    assert point["assessed"] == 10
    assert point["security_items"] == 9
    assert point["above_threshold"] == 5
    assert point["immediate_attention"] == 1
    assert point["critical"] == 2
    assert point["high"] == 3
    assert point["low"] == 4
    assert point["sources_healthy"] == 2


def test_build_dashboard_feed_deduplicates_date_and_prefers_latest(tmp_path: Path) -> None:
    archive = tmp_path / "2026-07-21.json"
    latest = tmp_path / "latest.json"
    archive.write_text(json.dumps(report("2026-07-21", critical=1)), encoding="utf-8")
    latest.write_text(json.dumps(report("2026-07-21", critical=3)), encoding="utf-8")

    feed = build_dashboard_feed([archive], latest_path=latest)

    assert feed["schema_version"] == 1
    assert len(feed["history"]) == 1
    assert feed["history"][0]["critical"] == 3
    assert feed["endpoints"]["dashboard_feed"].endswith("reports/dashboard-feed.json")


def test_write_dashboard_feed_limits_history_and_ignores_health_archives(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    archive_root.mkdir()
    for day in range(1, 5):
        (archive_root / f"2026-07-0{day}.json").write_text(
            json.dumps(report(f"2026-07-0{day}", high=day)),
            encoding="utf-8",
        )
    (archive_root / "2026-07-03-source-health.json").write_text("[]", encoding="utf-8")
    latest = tmp_path / "latest.json"
    latest.write_text(json.dumps(report("2026-07-05", high=5)), encoding="utf-8")
    output = tmp_path / "dashboard-feed.json"

    write_dashboard_feed(archive_root, latest, output, days=3)

    feed = json.loads(output.read_text(encoding="utf-8"))
    assert [point["date"] for point in feed["history"]] == [
        "2026-07-03",
        "2026-07-04",
        "2026-07-05",
    ]
    assert not output.with_suffix(".json.tmp").exists()


def test_dashboard_feed_matches_public_schema() -> None:
    packaged_schema = json.loads(
        files("cyberdailylog").joinpath("schemas/dashboard-feed.schema.json").read_text(encoding="utf-8")
    )
    public_schema = json.loads(Path("schemas/dashboard-feed.schema.json").read_text(encoding="utf-8"))
    assert packaged_schema == public_schema

    validator = Draft202012Validator(packaged_schema, format_checker=FormatChecker())
    validator.check_schema(packaged_schema)
    validator.validate(build_dashboard_feed([], latest_path=Path("reports/latest.json")))


@pytest.mark.parametrize("days", [0, -1])
def test_build_dashboard_feed_rejects_invalid_days(tmp_path: Path, days: int) -> None:
    latest = tmp_path / "latest.json"
    latest.write_text(json.dumps(report("2026-07-21")), encoding="utf-8")

    with pytest.raises(ValueError, match="positive integer"):
        build_dashboard_feed([], latest_path=latest, days=days)
