import json
from pathlib import Path

import pytest

from cyberdailylog.readme_snapshot import (
    END_MARKER,
    START_MARKER,
    build_snapshot,
    update_readme,
)


def sample_feed() -> dict:
    return {
        "schema_version": 1,
        "generated_at": "2026-07-19T08:32:33+00:00",
        "coverage_start": "2026-07-18T08:32:31+00:00",
        "coverage_end": "2026-07-19T08:32:31+00:00",
        "pipeline_status": "operational",
        "qualified_developments": 100,
        "above_threshold": 12,
        "immediate_attention": "No confirmed exploitation signal.",
        "source_health": {
            "core": {"total": 3, "healthy": 3},
            "optional": {"total": 3, "healthy": 2, "degraded": 1},
        },
        "top_vulnerabilities": [
            {
                "id": "CVE-2026-00001",
                "title": "Example vulnerability",
                "source_url": "https://example.test/CVE-2026-00001",
                "priority_score": 9.5,
                "why_it_matters": "high impact",
            }
        ],
    }


def test_build_snapshot_is_compact_and_linked():
    text = build_snapshot(sample_feed())

    assert START_MARKER in text and END_MARKER in text
    assert "3/3 healthy" in text
    assert "CVE-2026-00001" in text
    assert "9.5/10" in text
    assert "docs/INTEGRATION.md" in text


def test_update_readme_replaces_only_generated_block(tmp_path: Path):
    readme = tmp_path / "README.md"
    feed = tmp_path / "feed.json"
    readme.write_text(
        f"# Project\n\n{START_MARKER}\nOUTDATED_BLOCK\n{END_MARKER}\n\n## Stable docs\n",
        encoding="utf-8",
    )
    feed.write_text(json.dumps(sample_feed()), encoding="utf-8")

    update_readme(feed, readme)

    updated = readme.read_text(encoding="utf-8")
    assert "OUTDATED_BLOCK" not in updated
    assert "Stable docs" in updated
    assert sample_feed()["generated_at"] in updated
    assert not readme.with_suffix(".md.tmp").exists()


def test_update_readme_requires_markers(tmp_path: Path):
    readme = tmp_path / "README.md"
    feed = tmp_path / "feed.json"
    readme.write_text("# Missing markers\n", encoding="utf-8")
    feed.write_text(json.dumps(sample_feed()), encoding="utf-8")

    with pytest.raises(ValueError, match="missing CyberDailyLog daily markers"):
        update_readme(feed, readme)


def test_build_snapshot_handles_legacy_health_and_empty_items():
    feed = sample_feed()
    feed["source_health"] = {"status_counts": {"healthy": 5, "degraded": 1}}
    feed["top_vulnerabilities"] = []

    text = build_snapshot(feed)

    assert "1 degraded" in text
    assert "No item met the current publication threshold." in text


def test_build_snapshot_rejects_missing_fields():
    with pytest.raises(ValueError, match="missing required keys"):
        build_snapshot({"top_vulnerabilities": []})


def test_build_snapshot_rejects_invalid_top_items():
    feed = sample_feed()
    feed["top_vulnerabilities"] = "invalid"

    with pytest.raises(ValueError, match="must be an array"):
        build_snapshot(feed)
