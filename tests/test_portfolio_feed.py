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
                "title": "CVE-2026-10001: Critical Linux vulnerability",
                "source_name": "nvd",
                "source_url": "https://example.test/CVE-2026-10001",
                "cve_ids": ["CVE-2026-10001"],
                "ghsa_ids": [],
                "products": ["linux"],
                "cvss_score": 9.8,
                "severity": "critical",
                "epss_score": 0.72,
                "epss_percentile": 0.98,
                "cisa_kev": True,
                "known_exploited": True,
                "known_ransomware_use": False,
                "selection_score": 42,
                "selection_reasons": ["confirmed exploitation", "critical CVSS", "official source"],
                "priority_score": 10.0,
                "priority_reasons": ["CVSS 9.8", "CISA KEV"],
                "recommended_actions": ["Patch exposed Linux systems immediately."],
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
                "epss_percentile": None,
                "cisa_kev": False,
                "known_exploited": False,
                "known_ransomware_use": False,
                "selection_score": 25,
                "selection_reasons": ["high CVSS", "priority technology", "official source", "extra"],
                "priority_score": 8.6,
                "priority_reasons": ["CVSS 8.1", "priority technology: cloud"],
            },
            {
                "canonical_id": "CVE-2026-LOW",
                "title": "Low-priority item",
                "source_name": "nvd",
                "source_url": "https://example.test/CVE-2026-LOW",
                "cve_ids": ["CVE-2026-LOW"],
                "ghsa_ids": [],
                "products": [],
                "cvss_score": 3.0,
                "severity": "low",
                "epss_score": None,
                "epss_percentile": None,
                "cisa_kev": False,
                "known_exploited": False,
                "known_ransomware_use": False,
                "selection_score": 5,
                "selection_reasons": ["official source"],
                "priority_score": 3.0,
                "priority_reasons": ["CVSS 3.0"],
            },
        ],
        "source_health": [
            {"source": "nvd", "status": "healthy", "required": True},
            {"source": "rss_official", "status": "degraded", "required": False},
        ],
    }


def test_build_portfolio_feed_is_compact_ranked_and_enriched() -> None:
    feed = build_portfolio_feed(sample_report(), limit=1)

    assert feed["schema_version"] == 1
    assert feed["project"] == "CyberDailyLog"
    assert feed["qualified_developments"] == 3
    assert feed["above_threshold"] == 2
    assert feed["degraded"] is True
    assert feed["pipeline_status"] == "degraded"
    assert feed["top_vulnerabilities"][0]["id"] == "CVE-2026-10001"
    assert feed["top_vulnerabilities"][0]["title"] == "Critical Linux vulnerability"
    assert feed["top_vulnerabilities"][0]["priority_score"] == 10.0
    assert feed["top_vulnerabilities"][0]["epss_percentile"] == 0.98
    assert feed["top_vulnerabilities"][0]["defensive_action"].startswith("Patch exposed")
    assert len(feed["top_vulnerabilities"]) == 1
    assert feed["source_health"]["core"] == {"total": 1, "healthy": 1}
    assert feed["source_health"]["optional"] == {"total": 1, "healthy": 0, "degraded": 1}
    assert "exploitation" in feed["immediate_attention"]
    assert feed["endpoints"]["compact_feed"].endswith("reports/portfolio-feed.json")


def test_build_portfolio_feed_filters_below_threshold() -> None:
    feed = build_portfolio_feed(sample_report(), limit=5)

    assert [item["id"] for item in feed["top_vulnerabilities"]] == [
        "CVE-2026-10001",
        "GHSA-abcd-efgh-ijkl",
    ]
    assert feed["top_vulnerabilities"][1]["products"] == ["package-a", "package-b", "package-c"]
    assert feed["top_vulnerabilities"][1]["why_it_matters"] == "CVSS 8.1; priority technology: cloud"


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


def test_build_portfolio_feed_uses_cvss_fallback_and_vendor_context():
    report = sample_report()
    item = report["items"][1]
    item.pop("priority_score")
    item["products"] = []
    item["vendors"] = ["Example Vendor"]
    item["priority_reasons"] = []

    feed = build_portfolio_feed(report, limit=5)
    selected = next(entry for entry in feed["top_vulnerabilities"] if entry["id"] == "GHSA-abcd-efgh-ijkl")

    assert selected["priority_score"] == 8.1
    assert selected["products"] == ["Example Vendor"]
    assert selected["why_it_matters"].startswith("high CVSS")


def test_build_portfolio_feed_reports_no_exploitation():
    report = sample_report()
    for item in report["items"]:
        item["known_exploited"] = False
        item["cisa_kev"] = False
        item["known_ransomware_use"] = False

    feed = build_portfolio_feed(report)

    assert feed["immediate_attention_count"] == 0
    assert feed["immediate_attention"].startswith("No confirmed exploitation")
