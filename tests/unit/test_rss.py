from datetime import datetime, timezone
from pathlib import Path

from cyberdailylog.collectors.rss import RssCollector
from cyberdailylog.exceptions import SourceError
from cyberdailylog.settings import load_yaml


SINCE = datetime(2026, 7, 14, tzinfo=timezone.utc)
UNTIL = datetime(2026, 7, 16, tzinfo=timezone.utc)


def test_only_enabled_curated_rss_sources_are_active():
    sources = load_yaml(Path("config/sources.yml"))["rss_sources"]
    collector = RssCollector(offline=True, sources=sources)

    assert [source["name"] for source in collector.sources] == [
        "Krebs on Security",
        "SANS Internet Storm Center Handler's Diary",
    ]
    assert all("oval" not in source["url"] for source in collector.sources)


def test_rss_context_strips_html_limits_excerpt_and_attributes_author():
    sources = load_yaml(Path("config/sources.yml"))["rss_sources"]
    krebs = next(source for source in sources if source["name"] == "Krebs on Security")
    sans = next(source for source in sources if source["name"].startswith("SANS"))

    krebs_items, krebs_health = RssCollector(offline=True, sources=[krebs]).collect(SINCE, UNTIL)
    sans_items, sans_health = RssCollector(offline=True, sources=[sans]).collect(SINCE, UNTIL)

    assert krebs_health.status == "fixture_only"
    assert krebs_health.source == "rss_krebs"
    assert len(krebs_items) == 1
    assert krebs_items[0].category == "expert_commentary"
    assert krebs_items[0].author == "Brian Krebs"
    assert krebs_items[0].excerpt_origin == "publisher_feed"
    assert "<p>" not in krebs_items[0].summary
    assert "ignore me" not in krebs_items[0].summary
    assert len(krebs_items[0].summary.removesuffix("…").split()) <= 24

    assert sans_health.status == "fixture_only"
    assert sans_health.source == "rss_sans_isc"
    assert sans_items[0].category == "analyst_diary"
    assert sans_items[0].author == "Fixture Handler"


def test_rss_collector_preserves_successful_source_when_another_fails():
    feed = (
        "<?xml version='1.0'?><rss version='2.0'><channel><item>"
        "<title>Security analysis</title><link>https://example.test/security</link>"
        "<description>Publisher supplied context.</description>"
        "<pubDate>Wed, 15 Jul 2026 09:00:00 GMT</pubDate>"
        "</item></channel></rss>"
    )

    class FakeHttp:
        def get(self, url, max_bytes=0):
            del max_bytes
            if "bad" in url:
                raise SourceError("HTTP 503 from bad.example")
            return type("Response", (), {"text": feed})()

    sources = [
        {"name": "Good source", "url": "https://good.example/feed", "category": "expert_commentary"},
        {"name": "Bad source", "url": "https://bad.example/feed", "category": "expert_commentary"},
    ]
    items, health = RssCollector(FakeHttp(), sources=sources).collect(SINCE, UNTIL)

    assert len(items) == 1
    assert health.status == "degraded"
    assert health.items_accepted == 1
    assert "Bad source" in str(health.sanitized_error_message)


def test_rss_supports_atom_links_iso_dates_and_generated_health_names():
    atom = """<?xml version='1.0'?>
    <feed xmlns='http://www.w3.org/2005/Atom'>
      <entry>
        <title>Security engineering note</title>
        <link rel='alternate' href='https://example.test/atom-note'/>
        <summary type='html'>&lt;p&gt;Short publisher summary.&lt;/p&gt;</summary>
        <updated>2026-07-15T13:00:00Z</updated>
        <author><name>Example Analyst</name></author>
      </entry>
    </feed>"""

    class FakeHttp:
        def get(self, url, max_bytes=0):
            del url, max_bytes
            return type("Response", (), {"text": atom})()

    source = {
        "name": "Example Analyst Feed",
        "url": "https://example.test/feed.xml",
        "category": "analyst_diary",
    }
    items, health = RssCollector(FakeHttp(), sources=[source]).collect(SINCE, UNTIL)

    assert health.status == "healthy"
    assert health.source == "rss_example_analyst_feed"
    assert items[0].source_url == "https://example.test/atom-note"
    assert items[0].author == "Example Analyst"
    assert items[0].summary == "Short publisher summary."


def test_rss_empty_feed_is_degraded_without_crashing_pipeline():
    class EmptyHttp:
        def get(self, url, max_bytes=0):
            del url, max_bytes
            return type("Response", (), {"text": ""})()

    source = {"name": "Empty source", "url": "https://empty.example/feed"}
    items, health = RssCollector(EmptyHttp(), sources=[source]).collect(SINCE, UNTIL)

    assert items == []
    assert health.status == "degraded"
    assert health.error_type == "SourceError"
