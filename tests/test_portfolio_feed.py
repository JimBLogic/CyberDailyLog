from __future__ import annotations

import json
from pathlib import Path

import pytest

from cyberdailylog.portfolio_feed import build_portfolio_feed, write_portfolio_feed


def sample_report() -> dict:
    return {
        "generated_at": "2026-07-16T08:34:06+00:00",
        "coverage_start": "2026-07-15T08:33:48+00:00",
        "coverage_end": "2026-07-16T08:33:48+00:00",
        "degraded": True,
        "items": [
            {
                "canonical_id": "CVE-2026-10001",
                "title": "Critical Linux vulnerability",
                "source_name": "nvd",
                "source_url": "https://example.test/CVE-2026-10001",
                "cve_ids": ["CVE-2026-10001"],
                "ghsa_ids": [],
                "products": ["linux"],
                "cvss_score": 9.8,
                "severity": "critical",
                "epss_score": 0.72,
                "cisa_kev": True,
                "known_exploited": True,
                "selection_score": 42,
                "selection_reasons": ["confirmed exploitation", "critical CVSS", "official source"],
            },
            {
                "canonical_id": "GHSA-abcd-efgh-ijkl",
                "title": "Cloud package advisory",
                "source_name": "github_advisories",
                "source_url": "https://example.test/GHSA-abcd-efgh-ijkl",
                "cve_ids": [],
                "ghsa_ids": ["GHSA-abcd-efgh-ijkl"],
                "products": ["package-a", "package-b", "package-c", "package-d"],
                "cvss_score": 8.1,
                "severity": "high",
                "epss_score": None,
                "cisa_kev": False,
                "known_exploited": False,
                "selection_score": 25,
                "selection_reasons": ["high CVSS", "priority technology", "official source", "extra"],
            },
        ],
        "source_health": [
            {"source": "nvd", "status": "healthy"},
            {"source": "rss_official", "status": "degraded"},
        ],
    }


def test_build_portfolio_feed_is_compact_and_ranked() -> None:
    feed = build_portfolio_feed(sample_report(), limit=1)

    assert feed["schema_version"] == 1
    assert feed["project"] == "CyberDailyLog"
    assert feed["qualified_developments"] == 2
    assert feed["degraded"] is True
    assert feed["top_vulnerabilities"][0]["id"] == "CVE-2026-10001"
    assert feed["top_vulnerabilities"][0]["cisa_kev"] is True
    assert len(feed["top_vulnerabilities"]) == 1
    assert feed["source_health"] == {
        "total": 2,
        "status_counts": {"healthy": 1, "degraded": 1},
    }
    assert "confirmed exploitation" in feed["immediate_attention"]


def test_build_portfolio_feed_reports_no_exploitation() -> None:
    report = sample_report()
    for item in report["items"]:
        item["known_exploited"] = False
        item["cisa_kev"] = False

    feed = build_portfolio_feed(report)

    assert feed["immediate_attention"] == "No confirmed exploitation or CISA KEV entries qualified in this run."
    assert feed["top_vulnerabilities"][1]["products"] == ["package-a", "package-b", "package-c"]
    assert feed["top_vulnerabilities"][1]["selection_reasons"] == [
        "high CVSS",
        "priority technology",
        "official source",
    ]


def test_write_portfolio_feed_writes_valid_json(tmp_path: Path) -> None:
    report_path = tmp_path / "latest.json"
    output_path = tmp_path / "portfolio-feed.json"
    report_path.write_text(json.dumps(sample_report()), encoding="utf-8")

    write_portfolio_feed(report_path, output_path, limit=2)

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["generated_at"] == "2026-07-16T08:34:06+00:00"
    assert len(written["top_vulnerabilities"]) == 2
    assert not output_path.with_suffix(".json.tmp").exists()


@pytest.mark.parametrize("limit", [0, -1])
def test_build_portfolio_feed_rejects_invalid_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        build_portfolio_feed(sample_report(), limit=limit)


def test_build_portfolio_feed_rejects_missing_report_keys() -> None:
    with pytest.raises(ValueError, match="missing required keys"):
        build_portfolio_feed({"items": []})
