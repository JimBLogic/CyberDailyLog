from urllib.parse import urlencode

from cyberdailylog.collectors.epss import EpssCollector, _extract_scores, batch_cves


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class FakeHttp:
    def __init__(self, fail_call: int | None = None, empty: bool = False):
        self.calls = []
        self.fail_call = fail_call
        self.empty = empty

    def get(self, url, headers=None, params=None, expect_json=False, max_bytes=5_000_000):
        del headers, expect_json, max_bytes
        self.calls.append((url, params))
        if self.fail_call == len(self.calls):
            raise RuntimeError("simulated EPSS batch failure")
        if self.empty:
            return FakeResponse({"data": []})
        requested = str((params or {}).get("cve") or "").split(",")
        return FakeResponse(
            {
                "data": [
                    {
                        "cve": cve,
                        "epss": "0.72",
                        "percentile": "0.98",
                        "date": "2026-07-19",
                    }
                    for cve in requested
                    if cve
                ]
            }
        )


def test_batch_cves_respects_encoded_query_budget():
    cves = [f"CVE-2026-{number:05d}" for number in range(300)]

    batches = batch_cves(cves)

    assert len(batches) > 1
    assert [cve for batch in batches for cve in batch] == sorted(cves)
    assert all(len(urlencode({"cve": ",".join(batch)})) <= 1800 for batch in batches)


def test_epss_collector_batches_and_merges_all_scores():
    cves = [f"CVE-2026-{number:05d}" for number in range(300)]
    http = FakeHttp()

    scores, health = EpssCollector(http=http).collect_scores(cves)

    assert len(http.calls) > 1
    assert len(scores) == len(cves)
    assert health.status == "healthy"
    assert health.items_received == len(cves)
    assert health.items_accepted == len(cves)
    assert health.items_rejected == 0


def test_epss_collector_keeps_partial_results_and_degrades():
    cves = [f"CVE-2026-{number:05d}" for number in range(300)]
    http = FakeHttp(fail_call=2)

    scores, health = EpssCollector(http=http).collect_scores(cves)

    assert scores
    assert len(scores) < len(cves)
    assert health.status == "degraded"
    assert health.items_accepted == len(scores)
    assert health.items_rejected >= len(cves) - len(scores)
    assert "batches failed" in str(health.sanitized_error_message)


def test_epss_collector_marks_unexpected_empty_result_degraded():
    http = FakeHttp(empty=True)

    scores, health = EpssCollector(http=http).collect_scores(["CVE-2026-00001"])

    assert scores == {}
    assert health.status == "degraded"
    assert health.items_received == 1
    assert health.items_accepted == 0


def test_epss_collector_empty_input_is_healthy_without_request():
    http = FakeHttp()

    scores, health = EpssCollector(http=http).collect_scores([])

    assert scores == {}
    assert health.status == "healthy"
    assert http.calls == []


def test_extract_scores_rejects_malformed_rows_without_crashing():
    scores, malformed = _extract_scores(
        {
            "data": [
                {"cve": "CVE-2026-00001", "epss": "0.1", "percentile": "0.5"},
                {"cve": "", "epss": "bad", "percentile": "bad"},
                "invalid",
            ]
        }
    )

    assert list(scores) == ["CVE-2026-00001"]
    assert malformed == 2


def test_extract_scores_rejects_invalid_payload_shape():
    assert _extract_scores([]) == ({}, 1)
    assert _extract_scores({"data": "invalid"}) == ({}, 1)
