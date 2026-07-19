import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cyberdailylog.models import IntelligenceItem, Report, SourceHealth
from cyberdailylog.renderers.json import write_json
from cyberdailylog.renderers.markdown import write_markdown


def make_report(day: int, canonical_id: str) -> Report:
    end = datetime(2026, 7, day, 8, tzinfo=timezone.utc)
    item = IntelligenceItem(
        canonical_id=canonical_id,
        title=f"{canonical_id}: archive test",
        source_name="test",
        source_type="fixture",
        source_url=f"https://example.test/{canonical_id}",
        published_at=end,
        modified_at=end,
        cve_ids=[canonical_id],
        cvss_score=9.0,
        priority_score=9.0,
        priority_reasons=["CVSS 9.0"],
        selection_score=20,
        selection_reasons=["critical CVSS"],
    )
    health = SourceHealth(
        source="nvd",
        status="healthy",
        started_at=end,
        finished_at=end,
        duration_ms=1,
        items_accepted=1,
        required=True,
    )
    return Report(
        generated_at=end,
        coverage_start=end - timedelta(hours=24),
        coverage_end=end,
        items=[item],
        source_health=[health],
    )


def test_previous_bundle_is_archived_before_new_latest(tmp_path: Path):
    report_18 = make_report(18, "CVE-2026-00018")
    write_markdown(report_18, tmp_path)
    write_json(report_18, tmp_path)
    previous_markdown = (tmp_path / "latest.md").read_text(encoding="utf-8")
    previous_json = (tmp_path / "latest.json").read_text(encoding="utf-8")

    report_19 = make_report(19, "CVE-2026-00019")
    write_markdown(report_19, tmp_path)
    write_json(report_19, tmp_path)

    archive = tmp_path / "archive" / "2026" / "07"
    assert (archive / "2026-07-18.md").read_text(encoding="utf-8") == previous_markdown
    assert (archive / "2026-07-18.json").read_text(encoding="utf-8") == previous_json
    assert (archive / "2026-07-18-source-health.json").exists()
    assert "CVE-2026-00019" in (tmp_path / "latest.json").read_text(encoding="utf-8")


def test_conflicting_previous_json_archive_fails_safely(tmp_path: Path):
    report_18 = make_report(18, "CVE-2026-00018")
    write_markdown(report_18, tmp_path)
    write_json(report_18, tmp_path)

    archive_json = tmp_path / "archive" / "2026" / "07" / "2026-07-18.json"
    archive_json.write_text(json.dumps({"conflict": True}), encoding="utf-8")
    original_latest = (tmp_path / "latest.json").read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="historical JSON archive conflict"):
        write_json(make_report(19, "CVE-2026-00019"), tmp_path)

    assert (tmp_path / "latest.json").read_text(encoding="utf-8") == original_latest
