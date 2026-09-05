from datetime import datetime, timezone
import json

from cyberdailylog.collectors.github_advisories import GitHubAdvisoryCollector
from cyberdailylog.http import Response

SINCE = datetime(2026, 9, 4, tzinfo=timezone.utc)
UNTIL = datetime(2026, 9, 5, tzinfo=timezone.utc)


def advisory(identifier="GHSA-1234-5678-9012"):
    return {
        "ghsa_id": identifier,
        "summary": "Test advisory",
        "html_url": "https://github.com/advisories/" + identifier,
        "published_at": "2026-09-04T12:00:00Z",
        "updated_at": "2026-09-04T13:00:00Z",
        "vulnerabilities": [{"package": {"name": "test", "ecosystem": "npm"}, "first_patched_version": "2.4.1"}],
        "cvss_severities": {"cvss_v4": {"score": 9.3, "vector_string": "CVSS:4.0/AV:N"}},
    }


class FakeHttp:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return next(self.pages)


def response(data, link=""):
    return Response(json.dumps(data).encode(), 200, {"Link": link})


def test_follows_cursor_and_retains_official_patch_and_cvss():
    next_url = "https://api.github.com/advisories?after=cursor"
    http = FakeHttp(
        [
            response([advisory()], f'<{next_url}>; rel="next"'),
            response([advisory("GHSA-2345-6789-0123")]),
        ]
    )
    items, health = GitHubAdvisoryCollector(http, token="test-token").collect(SINCE, UNTIL)
    assert len(items) == 2
    assert health.status == "healthy"
    assert items[0].fixed_versions == ["2.4.1"]
    assert items[0].cvss_version == "4.0"
    assert items[0].cvss_score == 9.3
    assert http.calls[0][1]["params"]["modified"] == "2026-09-04..2026-09-05"
    assert http.calls[1][0] == next_url
    assert http.calls[1][1]["params"] is None


def test_rejects_foreign_pagination_without_forwarding_token():
    http = FakeHttp([response([advisory()], '<https://example.com/advisories>; rel="next"')])
    items, health = GitHubAdvisoryCollector(http, token="test-token").collect(SINCE, UNTIL)
    assert items == []
    assert health.status == "failed"
    assert len(http.calls) == 1


def test_cursor_loop_cannot_report_complete_coverage():
    link = '<https://api.github.com/advisories?after=same>; rel="next"'
    http = FakeHttp([response([advisory()], link), response([advisory()], link)])
    items, health = GitHubAdvisoryCollector(http).collect(SINCE, UNTIL)
    assert not items
    assert health.status == "failed"
    assert len(http.calls) == 2


def test_invalid_row_is_visible_as_degraded_without_losing_good_rows():
    http = FakeHttp([response([{}, advisory()])])
    items, health = GitHubAdvisoryCollector(http).collect(SINCE, UNTIL)
    assert len(items) == 1
    assert health.status == "degraded"
    assert health.items_rejected == 1


def test_invalid_json_shape_fails_source():
    items, health = GitHubAdvisoryCollector(FakeHttp([response({"message": "bad"})])).collect(SINCE, UNTIL)
    assert not items
    assert health.status == "failed"


def test_page_budget_does_not_silently_claim_full_coverage():
    http = FakeHttp([response([advisory()], '<https://api.github.com/advisories?after=more>; rel="next"')])
    collector = GitHubAdvisoryCollector(http)
    collector.max_pages = 1
    items, health = collector.collect(SINCE, UNTIL)
    assert not items
    assert health.status == "failed"
