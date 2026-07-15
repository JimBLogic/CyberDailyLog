from cyberdailylog.collectors.rss import RssCollector
from cyberdailylog.settings import load_yaml
from pathlib import Path


def test_disabled_red_hat_oval_source_is_not_active_rss_feed():
    sources = load_yaml(Path("config/sources.yml"))["rss_sources"]
    collector = RssCollector(offline=True, sources=sources)
    assert [source["name"] for source in collector.sources] == ["CISA Cybersecurity Advisories"]
    assert all("oval" not in source["url"] for source in collector.sources)
