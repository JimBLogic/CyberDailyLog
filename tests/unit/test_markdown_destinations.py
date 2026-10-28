import pytest

from cyberdailylog.readme_snapshot import build_snapshot, markdown_url


@pytest.mark.parametrize(
    "value", ["javascript:alert(1)", "https://user:secret@example.invalid/", "https://example.invalid/\ntext"]
)
def test_unsafe_markdown_destinations_are_not_emitted(value):
    assert markdown_url(value) == "#"


def test_delimiters_are_encoded_without_changing_normal_query_semantics():
    value = "https://example.invalid/a(b)?id=1&next=[notice]"
    assert markdown_url(value) == "https://example.invalid/a%28b%29?id=1&next=%5Bnotice%5D"
    assert markdown_url(markdown_url(value)) == markdown_url(value)


def test_readme_community_url_cannot_add_a_markdown_link():
    feed = {
        "generated_at": "2026-10-28T11:00:00Z",
        "coverage_start": "2026-10-27T11:00:00Z",
        "coverage_end": "2026-10-28T11:00:00Z",
        "top_vulnerabilities": [],
        "community_pulse": {
            "title": "Security discussion",
            "source_url": "https://example.invalid/)[NOTICE](https://example.invalid/",
        },
    }
    rendered = build_snapshot(feed)
    assert ")[NOTICE](" not in rendered
    assert "%29%5BNOTICE%5D%28" in rendered
