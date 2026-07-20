from datetime import datetime, timezone
from pathlib import Path

from cyberdailylog.collectors.hacker_news import HackerNewsCollector
from cyberdailylog.settings import load_yaml


SINCE = datetime(2026, 7, 14, tzinfo=timezone.utc)
UNTIL = datetime(2026, 7, 16, tzinfo=timezone.utc)


def test_hacker_news_offline_filters_by_engagement_and_security_relevance():
    config = load_yaml(Path("config/sources.yml"))["hacker_news"]
    items, health = HackerNewsCollector(offline=True, config=config).collect(SINCE, UNTIL)

    assert health.status == "fixture_only"
    assert health.items_received == 4
    assert health.items_accepted == 2
    assert [item.canonical_id for item in items] == ["hn:101", "hn:104"]
    assert items[0].category == "community_pulse"
    assert items[0].community_score == 140
    assert items[0].community_comments == 55
    assert items[0].discussion_url == "https://news.ycombinator.com/item?id=101"
    assert items[0].confidence == "low"


def test_hacker_news_does_not_treat_unrelated_popularity_as_threat_evidence():
    config = load_yaml(Path("config/sources.yml"))["hacker_news"]
    items, _ = HackerNewsCollector(offline=True, config=config).collect(SINCE, UNTIL)

    titles = {item.title for item in items}
    assert "A new database query language" not in titles
    assert all(item.official_source is False for item in items)
    assert all("validate claims" in item.blue_team_relevance.lower() for item in items)


def test_hacker_news_live_client_uses_official_endpoints_and_falls_back_to_discussion_url():
    config = {
        "base_url": "https://hacker-news.firebaseio.com/v0",
        "minimum_score": 80,
        "minimum_comments": 20,
        "max_story_ids": 5,
        "max_items": 1,
        "security_keywords": ["security"],
        "allowed_domains": [],
    }

    class JsonResponse:
        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    class FakeHttp:
        def __init__(self):
            self.urls = []

        def get(self, url, expect_json=False):
            assert expect_json is True
            self.urls.append(url)
            if url.endswith("topstories.json"):
                return JsonResponse([501])
            return JsonResponse(
                {
                    "id": 501,
                    "type": "story",
                    "by": "analyst",
                    "time": int(datetime(2026, 7, 15, 12, tzinfo=timezone.utc).timestamp()),
                    "score": 120,
                    "descendants": 30,
                    "title": "Security incident discussion",
                }
            )

    http = FakeHttp()
    items, health = HackerNewsCollector(http, config=config).collect(SINCE, UNTIL)

    assert health.status == "healthy"
    assert items[0].source_url == "https://news.ycombinator.com/item?id=501"
    assert http.urls == [
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        "https://hacker-news.firebaseio.com/v0/item/501.json",
    ]


def test_hacker_news_invalid_story_index_degrades_cleanly():
    class InvalidHttp:
        def get(self, url, expect_json=False):
            del url, expect_json
            return type("Response", (), {"json": lambda self: {"not": "a list"}})()

    items, health = HackerNewsCollector(InvalidHttp(), config={}).collect(SINCE, UNTIL)

    assert items == []
    assert health.status == "degraded"
    assert health.error_type == "SourceError"
