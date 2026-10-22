from datetime import datetime, timezone

from cyberdailylog.collectors.vendor_advisories import VendorAdvisoryCollector
from cyberdailylog.portfolio_feed import build_portfolio_feed
from cyberdailylog.models import Report, SourceHealth
from cyberdailylog.scoring import score_items
from cyberdailylog.settings import load_yaml
from pathlib import Path

SINCE = datetime(2026, 10, 20, tzinfo=timezone.utc)
UNTIL = datetime(2026, 10, 22, tzinfo=timezone.utc)
WATCH = [
    {"owner": "php", "repo": "php-src", "ghsa_id": "GHSA-w8hw-w9fx-j79w", "cve_id": "CVE-2026-109618"},
    {"owner": "php", "repo": "php-src", "ghsa_id": "GHSA-6wmf-4rv5-p3rp", "cve_id": "CVE-2026-109619"},
]


def advisory(ghsa, cve):
    return {
        "ghsa_id": ghsa,
        "cve_id": cve,
        "state": "published",
        "summary": "Critical PHP request memory vulnerability",
        "description": "Remote code execution in a vulnerable PHP runtime",
        "severity": "critical",
        "html_url": f"https://github.com/php/php-src/security/advisories/{ghsa}",
        "published_at": "2026-10-21T13:40:00Z",
        "updated_at": "2026-10-21T13:40:00Z",
        "cvss_severities": {"cvss_v4": {"score": 9.2, "vector_string": "CVSS:4.0/AV:N"}},
        "vulnerabilities": [
            {
                "package": {"name": "php-src", "ecosystem": "other"},
                "vulnerable_version_range": "< 8.4.27",
                "first_patched_version": "8.4.27",
            }
        ],
    }


class FakeHttp:
    def __init__(self, payloads):
        self.payloads = iter(payloads)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        data = next(self.payloads)

        class Response:
            def json(self):
                return data

        return Response()


def test_php_vendor_advisories_are_independent_ranked_cve_items():
    http = FakeHttp([advisory(w["ghsa_id"], w["cve_id"]) for w in WATCH])
    items, health = VendorAdvisoryCollector(http, token="synthetic", advisories=WATCH).collect(SINCE, UNTIL)
    assert health.status == "healthy"
    assert {item.canonical_id for item in items} == {"CVE-2026-109618", "CVE-2026-109619"}
    assert all(item.cvss_score == 9.2 and item.severity == "critical" for item in items)
    assert all(item.fixed_versions == ["8.4.27"] and item.source_type == "vendor_advisory" for item in items)
    assert all(url.startswith("https://api.github.com/repos/php/php-src/security-advisories/") for url, _ in http.calls)
    assert all(kwargs["headers"] == {"Authorization": "Bearer synthetic"} for _, kwargs in http.calls)
    scored = score_items(items, load_yaml(Path("config/scoring.yml")), {}, SINCE, UNTIL)
    assert all(item.priority_score >= 9.0 for item in scored)
    health_rows = [
        health,
        SourceHealth("nvd", "failed", SINCE, UNTIL, 300000, required=True),
        SourceHealth("cisa_kev", "healthy", SINCE, UNTIL, 1, required=True),
        SourceHealth("github_advisories", "healthy", SINCE, UNTIL, 1, required=True),
    ]
    report = Report(
        generated_at=UNTIL,
        coverage_start=SINCE,
        coverage_end=UNTIL,
        items=scored,
        source_health=health_rows,
        degraded=True,
    )
    feed = build_portfolio_feed(report.to_dict())
    assert feed["pipeline_status"] == "degraded"
    assert {item["id"] for item in feed["top_vulnerabilities"]} == {"CVE-2026-109618", "CVE-2026-109619"}


def test_vendor_advisory_identity_mismatch_fails_atomically():
    fake = advisory(WATCH[0]["ghsa_id"], WATCH[0]["cve_id"])
    wrong = advisory(WATCH[1]["ghsa_id"], WATCH[0]["cve_id"])
    http = FakeHttp([fake, wrong])
    items, health = VendorAdvisoryCollector(http, advisories=WATCH).collect(SINCE, UNTIL)
    assert items == [] and health.status == "failed"
    assert len(http.calls) == 2


def test_vendor_watch_rejects_unreviewed_external_host_before_network_access():
    http = FakeHttp([])
    watch = [{"owner": "php", "repo": "../attacker", "ghsa_id": "GHSA-w8hw-w9fx-j79w", "cve_id": "CVE-2026-109618"}]
    items, health = VendorAdvisoryCollector(http, advisories=watch).collect(SINCE, UNTIL)
    assert items == [] and health.status == "failed"
    assert http.calls == []


def test_vendor_advisories_skip_network_in_offline_fixtures():
    http = FakeHttp([])
    items, health = VendorAdvisoryCollector(http, advisories=WATCH, offline=True).collect(SINCE, UNTIL)
    assert items == [] and health.status == "fixture_only"
    assert not http.calls
