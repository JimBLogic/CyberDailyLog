import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from cyberdailylog.models import IntelligenceItem, Report, SourceHealth
from cyberdailylog.portfolio_feed import build_portfolio_feed
from cyberdailylog.readme_snapshot import build_snapshot
from cyberdailylog.renderers.markdown import render_markdown
from cyberdailylog.settings import load_yaml


NOW = datetime(2026, 7, 15, 12, tzinfo=timezone.utc)


def _report() -> Report:
    vulnerability = IntelligenceItem(
        canonical_id="CVE-2026-10000",
        title="CVE-2026-10000: Critical test vulnerability",
        source_name="NVD",
        source_type="vulnerability_database",
        source_url="https://nvd.nist.gov/vuln/detail/CVE-2026-10000",
        published_at=NOW,
        modified_at=NOW,
        cve_ids=["CVE-2026-10000"],
        cvss_score=9.8,
        priority_score=9.8,
        priority_reasons=["CVSS 9.8"],
        detection_opportunities=["Verify exposure and apply vendor guidance."],
    )
    expert = IntelligenceItem(
        canonical_id="url:https://krebsonsecurity.com/example",
        title="Lessons from a public credential leak",
        source_name="Krebs on Security",
        source_type="expert_rss",
        source_url="https://krebsonsecurity.com/example",
        summary=(
            "A contractor exposed internal credentials in a public repository for months, "
            "highlighting continuous secret scanning, tested key rotation, and clear external "
            "reporting channels for security researchers and responders."
        ),
        category="expert_commentary",
        official_source=False,
        published_at=NOW,
        modified_at=NOW,
        author="Brian Krebs",
        excerpt_origin="publisher_feed",
    )
    community = IntelligenceItem(
        canonical_id="hn:101",
        title="Supply chain security lessons from a package compromise",
        source_name="Hacker News",
        source_type="community_signal",
        source_url="https://security.googleblog.com/example",
        summary="Hacker News discussion with 140 points and 55 comments.",
        category="community_pulse",
        official_source=False,
        published_at=NOW,
        modified_at=NOW,
        community_score=140,
        community_comments=55,
        discussion_url="https://news.ycombinator.com/item?id=101",
    )
    health = SourceHealth(
        source="nvd",
        status="healthy",
        started_at=NOW,
        finished_at=NOW,
        duration_ms=10,
        items_accepted=1,
        required=True,
    )
    return Report(
        generated_at=NOW,
        coverage_start=NOW,
        coverage_end=NOW,
        items=[vulnerability, expert, community],
        source_health=[health],
    )


def test_markdown_separates_human_and_community_context_from_threat_scoring():
    report = _report()
    text = render_markdown(report, load_yaml(Path("config/report.yml")))

    assert "## Human context" in text
    assert "Brian Krebs · Krebs on Security" in text
    assert "Publisher-provided RSS excerpt" in text
    assert "## Community pulse" in text
    assert "140 points · 55 comments" in text
    assert "Community interest signal only" in text
    assert text.count("| [CVE-") == 1
    assert len(text.splitlines()) <= 140
    assert len(text.encode("utf-8")) <= 12288


def test_compact_feed_and_readme_expose_context_as_additive_fields():
    feed = build_portfolio_feed(_report().to_dict())

    assert feed["human_context"]["author"] == "Brian Krebs"
    assert feed["human_context"]["excerpt_origin"] == "publisher_feed"
    assert len(feed["human_context"]["excerpt"].removesuffix("…").split()) <= 24
    assert feed["community_pulse"]["score"] == 140
    assert feed["community_pulse"]["comments"] == 55

    schema = json.loads(Path("schemas/portfolio-feed.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(feed)

    snapshot = build_snapshot(feed)
    assert "### Human context" in snapshot
    assert "### Community pulse" in snapshot
    assert "Open discussion" in snapshot
