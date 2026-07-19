from datetime import datetime, timedelta, timezone

from cyberdailylog.models import IntelligenceItem, Report, SourceHealth
from cyberdailylog.renderers.markdown import render_markdown
from cyberdailylog.scoring import compute_priority_score, score_item


NOW = datetime(2026, 7, 19, 8, 0, tzinfo=timezone.utc)


def make_item(
    canonical_id: str,
    *,
    cvss: float | None = None,
    severity: str | None = None,
    cisa_kev: bool = False,
    known_exploited: bool = False,
    known_ransomware_use: bool = False,
    category: str = "vulnerability",
) -> IntelligenceItem:
    item = IntelligenceItem(
        canonical_id=canonical_id,
        title=f"{canonical_id}: concise defensive test item",
        source_name="test",
        source_type="fixture",
        source_url=f"https://example.test/{canonical_id}",
        published_at=NOW,
        modified_at=NOW,
        cvss_score=cvss,
        severity=severity,
        cisa_kev=cisa_kev,
        known_exploited=known_exploited,
        known_ransomware_use=known_ransomware_use,
        category=category,
        cve_ids=[canonical_id] if canonical_id.startswith("CVE-") else [],
    )
    item.priority_score, item.priority_reasons = compute_priority_score(item, {})
    return item


def test_priority_score_uses_cvss_modifiers_and_exploitation_floors():
    item = make_item("CVE-2026-00001", cvss=8.2)
    item.epss_score = 0.75
    item.epss_percentile = 0.98
    item.priority_score, item.priority_reasons = compute_priority_score(item, {})

    assert item.priority_score == 9.7
    assert "EPSS >= 70%" in item.priority_reasons
    assert "EPSS percentile >= 95%" in item.priority_reasons

    kev = make_item("CVE-2026-00002", cvss=2.0, cisa_kev=True)
    exploited = make_item("CVE-2026-00003", cvss=2.0, known_exploited=True)
    ransomware = make_item("CVE-2026-00004", cvss=2.0, known_ransomware_use=True)

    assert kev.priority_score == 10.0
    assert exploited.priority_score == 9.5
    assert ransomware.priority_score == 9.0


def test_priority_score_uses_severity_fallback_and_clamps():
    critical = make_item("GHSA-test-critical", severity="critical")
    unknown = make_item("GHSA-test-unknown")

    assert critical.priority_score == 9.5
    assert unknown.priority_score == 0.0


def test_markdown_is_curated_and_keeps_low_priority_out_of_human_view():
    high_items = [make_item(f"CVE-2026-{number:05d}", cvss=9.0 - number / 100) for number in range(20)]
    low = make_item("CVE-2026-99999", cvss=4.0)
    health = SourceHealth(
        source="nvd",
        status="healthy",
        started_at=NOW,
        finished_at=NOW,
        duration_ms=10,
        items_accepted=21,
        required=True,
    )
    report = Report(
        generated_at=NOW,
        coverage_start=NOW,
        coverage_end=NOW,
        items=[*high_items, low],
        source_health=[health],
    )
    config = {
        "curation": {
            "minimum_priority": 5.0,
            "max_immediate_attention": 5,
            "max_priority_vulnerabilities": 10,
            "max_official_advisories": 3,
            "max_defensive_releases": 3,
            "max_analyst_actions": 5,
            "max_total_unique_items": 15,
            "max_markdown_lines": 140,
            "max_markdown_bytes": 12288,
            "title_max_characters": 110,
            "reason_max_characters": 160,
        }
    }

    text = render_markdown(report, config)

    assert "CVE-2026-99999" not in text
    assert text.count("| [CVE-") <= 10
    assert len(text.splitlines()) <= 140
    assert len(text.encode("utf-8")) <= 12288
    assert "**21** source-backed developments assessed" in text
    assert "<details>" in text


def test_score_item_preserves_raw_selection_and_adds_editorial_priority():
    item = make_item("CVE-2026-12345", cvss=8.0)
    item.products = ["Linux appliance"]
    item.detection_opportunities = ["Monitor authentication failures."]
    item.published_at = NOW - timedelta(hours=2)
    item.modified_at = NOW
    scoring = {
        "weights": {
            "cvss_high": 10,
            "priority_technology": 8,
            "official_primary_source": 5,
            "detection_opportunity": 5,
            "metadata_only_modified": -5,
        }
    }
    technologies = {"priority_terms": {"linux": ["linux"]}}

    scored = score_item(item, scoring, technologies, NOW - timedelta(days=1), NOW)

    assert scored is item
    assert item.selection_score == 23
    assert "priority technology: linux +8" in item.selection_reasons
    assert item.priority_score == 7.8
    assert "priority technology: linux" in item.priority_reasons


def test_score_item_excludes_irrelevant_and_handles_withdrawn():
    irrelevant = make_item("CVE-2025-00001", cvss=8.0)
    irrelevant.published_at = NOW - timedelta(days=10)
    irrelevant.modified_at = irrelevant.published_at
    assert score_item(irrelevant, {"weights": {}}, {}, NOW - timedelta(days=1), NOW) is None

    withdrawn = make_item("GHSA-withdrawn", severity="high")
    withdrawn.withdrawn = True
    scored = score_item(withdrawn, {"weights": {}}, {}, NOW - timedelta(days=1), NOW)
    assert scored is withdrawn
    assert withdrawn.priority_score == 0.0
