from cyberdailylog.correlation import merge_items, norm_url
from cyberdailylog.models import IntelligenceItem


def story(identifier):
    return IntelligenceItem(
        canonical_id=f"hn:{identifier}",
        title="Security discussion",
        source_name="Hacker News",
        source_type="community_signal",
        source_url=f"https://news.ycombinator.com/item?id={identifier}",
        category="community_pulse",
    )


def test_distinct_query_identified_stories_remain_distinct():
    assert len(merge_items([story(123), story(456)])) == 2
    assert len(merge_items([story(123), story(123)])) == 1


def test_tracking_parameters_do_not_change_resource_identity():
    assert norm_url("https://example.invalid/article?id=123&utm_source=feed&gclid=abc#section") == (
        "https://example.invalid/article?id=123"
    )
    assert norm_url("https://example.invalid/article?%75tm_source=feed&item=2") == (
        "https://example.invalid/article?item=2"
    )


def test_semantic_queries_preserve_order_duplicates_and_encoding():
    value = "https://example.invalid/article?item=a%26b&item=c+d&lang=es"
    assert norm_url(value) == value
    assert norm_url("https://example.invalid/article?item=1") != norm_url("https://example.invalid/article?item=2")
