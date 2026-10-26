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
        "CERT-EU Security Advisories",
        "CERT-EU Security Guidance",
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


def test_cert_eu_metadata_only_attribution_and_no_inferred_vulnerability_state():
    sources = load_yaml(Path("config/sources.yml"))["rss_sources"][:2]
    for source in sources:
        items, health = RssCollector(offline=True, sources=[source]).collect(SINCE, UNTIL)
        assert health.status == "fixture_only" and health.required is False
        assert len(items) == 1
        item = items[0]
        assert item.summary == "" and item.excerpt_origin is None
        assert item.author == "CERT-EU" and item.official_source
        assert item.category == "analyst_diary"
        assert item.published_at.hour == 9  # 11:00 CEST is 09:00 UTC
        assert "https://cert.europa.eu/legal-notice" in item.references
        assert "https://creativecommons.org/licenses/by/4.0/" in item.references
        assert not item.cve_ids and not item.fixed_versions
        assert item.known_exploited is None and item.cisa_kev is None


def test_cet_dates_are_converted_without_assuming_utc():
    from cyberdailylog.collectors.rss import _entry_datetime
    import xml.etree.ElementTree as ET

    item = ET.fromstring("<item><pubDate>Mon, 26 Oct 2026 11:00:00 CET</pubDate></item>")
    assert _entry_datetime(item) == datetime(2026, 10, 26, 10, tzinfo=timezone.utc)


def _configured_live_collector(payload):
    class FakeHttp:
        def get(self, url, max_bytes=0):
            return type("Response", (), {"text": payload})()

    source = load_yaml(Path("config/sources.yml"))["rss_sources"][0]
    return RssCollector(FakeHttp(), sources=[source])


def test_metadata_policy_does_not_fetch_article_bodies_or_copy_descriptions():
    payload = """<rss><channel><item><title>Reference</title>
    <link>https://cert.europa.eu/publications/test/</link>
    <pubDate>Wed, 15 Jul 2026 09:00:00 GMT</pubDate>
    <description>Entire article that must never be copied.</description></item></channel></rss>"""
    items, health = _configured_live_collector(payload).collect(SINCE, UNTIL)
    assert health.status == "healthy"
    assert items[0].summary == ""
    assert "Entire article" not in str(items[0].to_dict())


def test_new_feeds_reject_empty_or_masquerading_documents():
    for payload in ["<html>blocked</html>", "<rss><channel/></rss>", "<error>Unavailable</error>"]:
        items, health = _configured_live_collector(payload).collect(SINCE, UNTIL)
        assert items == [] and health.status == "degraded"
        assert health.required is False


def test_rss_rejects_dtd_entity_payload_before_parsing():
    payload = '<!DOCTYPE rss [<!ENTITY secret "injected">]><rss><channel/></rss>'
    items, health = _configured_live_collector(payload).collect(SINCE, UNTIL)
    assert items == [] and health.status == "degraded"
    assert "entities" in health.sanitized_error_message


def test_official_feed_cannot_attribute_external_or_unsafe_links_to_cert_eu():
    for link in [
        "https://attacker.example/test",
        "javascript:alert(1)",
        "https://user:pass@cert.europa.eu/test",
        "https://cert.europa.eu:8443/test",
        "https://cert.europa.eu:bad/test",
    ]:
        payload = f"""<rss><channel><item><title>Reference</title><link>{link}</link>
        <pubDate>Wed, 15 Jul 2026 09:00:00 GMT</pubDate></item></channel></rss>"""
        items, health = _configured_live_collector(payload).collect(SINCE, UNTIL)
        assert items == [] and health.items_rejected == 1
        assert health.status == "degraded"


def test_official_feed_encodes_legacy_path_spaces_without_relaxing_origin_checks():
    payload = """<rss><channel><item><title>Guidance reference</title>
    <link>https://cert.europa.eu/publications/legacy guidance/</link>
    <pubDate>Wed, 15 Jul 2026 09:00:00 GMT</pubDate></item></channel></rss>"""
    items, health = _configured_live_collector(payload).collect(SINCE, UNTIL)
    assert health.status == "healthy"
    assert items[0].source_url == "https://cert.europa.eu/publications/legacy%20guidance/"


def test_optional_rss_outage_does_not_break_complete_core_pipeline(tmp_path, monkeypatch):
    from cyberdailylog.pipeline import Pipeline
    from cyberdailylog.models import SourceHealth

    def failed(self, since, until):
        return [], SourceHealth(self.name, "degraded", SINCE, UNTIL, 1, required=False)

    monkeypatch.setattr(RssCollector, "collect", failed)
    report = Pipeline(output_dir=tmp_path, offline=True).run(SINCE, UNTIL)
    assert report.degraded is False
    assert all(h.status == "fixture_only" for h in report.source_health if h.required)
    assert len([h for h in report.source_health if h.source.startswith("rss_cert_eu")]) == 2
