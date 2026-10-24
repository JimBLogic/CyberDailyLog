from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import weakref

import pytest

from cyberdailylog.collectors.nvd import NvdCollector
from cyberdailylog.exceptions import SourceError

START = datetime(2026, 10, 18, tzinfo=timezone.utc)
END = datetime(2026, 10, 19, tzinfo=timezone.utc)


class Page(dict):
    pass


class Response:
    def __init__(self, data):
        self.data = data
        self.content = json.dumps(data).encode()

    def json(self):
        return self.data


def pages():
    return [json.loads(Path("tests/fixtures", name).read_text()) for name in ("nvd_page1.json", "nvd_page2.json")]


def test_live_pagination_preserves_fixture_records_rejections_and_rate_limits(monkeypatch):
    fixtures = pages()
    calls = []
    waits = []

    class HTTP:
        def get(self, url, **kwargs):
            calls.append(deepcopy(kwargs))
            return Response(fixtures[len(calls) - 1])

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", waits.append)
    collector = NvdCollector(HTTP())
    items, health = collector.collect(START, END)
    expected, _ = NvdCollector(offline=True).collect(START, END)
    assert [i.canonical_id for i in items] == [i.canonical_id for i in expected]
    assert health.status == "healthy" and health.items_received == 3 and health.items_rejected == 1
    assert [c["params"]["startIndex"] for c in calls] == [0, 2]
    assert all(c["retry_interval"] == 6 for c in calls) and waits == [6]
    assert collector.metrics["pages"] == 2 and collector.metrics["requests"] == 2


def test_oversized_page_retries_same_offset_without_dropping_cves(monkeypatch):
    fixtures = pages()
    calls = []

    class HTTP:
        def get(self, url, **kwargs):
            calls.append(deepcopy(kwargs["params"]))
            if len(calls) == 1:
                raise SourceError("Response too large")
            return Response(fixtures[len(calls) - 2])

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", lambda _: None)
    c = NvdCollector(HTTP())
    items, health = c.collect(START, END)
    assert health.status == "healthy" and len(items) == 2
    assert [(r["startIndex"], r["resultsPerPage"]) for r in calls] == [(0, 500), (0, 250), (2, 250)]
    assert c.metrics["page_size_reductions"] == 1


@pytest.mark.parametrize("fault", ["offset", "total", "no_progress", "count", "duplicate", "transport"])
def test_incomplete_or_unstable_result_set_is_never_reported_healthy(monkeypatch, fault):
    fixtures = pages()
    calls = []

    class HTTP:
        def get(self, url, **kwargs):
            calls.append(1)
            if len(calls) == 1:
                return Response(fixtures[0])
            d = fixtures[1]
            if fault == "offset":
                d["startIndex"] = 0
            elif fault == "total":
                d["totalResults"] += 1
            elif fault == "no_progress":
                d.update(resultsPerPage=0, vulnerabilities=[])
            elif fault == "count":
                d["resultsPerPage"] = 999
            elif fault == "duplicate":
                d["vulnerabilities"][0] = fixtures[0]["vulnerabilities"][0]
            else:
                raise SourceError("Source transport failed for services.nvd.nist.gov")
            return Response(d)

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", lambda _: None)
    items, health = NvdCollector(HTTP()).collect(START, END)
    assert items == [] and health.status == "failed"


def test_raw_cpe_pages_are_released_while_items_are_accumulated(monkeypatch):
    template = pages()[0]["vulnerabilities"][0]
    refs = []

    class HTTP:
        def get(self, url, **kwargs):
            if len(refs) >= 2:
                assert refs[-2]() is None, "Older raw CPE page is still retained"
            index = kwargs["params"]["startIndex"]
            record = deepcopy(template)
            record["cve"]["id"] = f"CVE-2026-{10000 + index}"
            data = Page(resultsPerPage=1, startIndex=index, totalResults=4, vulnerabilities=[record])
            refs.append(weakref.ref(data))
            return Response(data)

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", lambda _: None)
    items, health = NvdCollector(HTTP()).collect(START, END)
    assert health.status == "healthy" and len(items) == 4


def test_php_critical_cves_survive_an_unstable_page_count_after_full_restart(monkeypatch):
    # Mirrors a NVD feed changing while the first walk is in progress.
    # Never combine the obsolete first page with the new snapshot.
    fixture = pages()[0]["vulnerabilities"][0]
    calls = []
    cves = ("CVE-2026-109618", "CVE-2026-109619")

    class HTTP:
        def get(self, url, **kwargs):
            index = kwargs["params"]["startIndex"]
            calls.append(index)
            record = deepcopy(fixture)
            record["cve"]["id"] = cves[0 if index == 0 else 1]
            record["cve"]["published"] = "2026-10-21T13:40:00.000"
            record["cve"]["lastModified"] = "2026-10-21T13:40:00.000"
            record["cve"]["metrics"] = {
                "cvssMetricV40": [{"cvssData": {"baseScore": 9.2, "version": "4.0"}, "baseSeverity": "CRITICAL"}]
            }
            total = 3 if len(calls) == 1 else 4 if len(calls) == 2 else 2
            return Response(
                {"totalResults": total, "resultsPerPage": 1, "startIndex": index, "vulnerabilities": [record]}
            )

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", lambda _: None)
    collector = NvdCollector(HTTP(), token="test")
    items, health = collector.collect(
        datetime(2026, 10, 20, tzinfo=timezone.utc),
        datetime(2026, 10, 22, tzinfo=timezone.utc),
    )
    assert health.status == "healthy"
    assert [item.canonical_id for item in items] == list(cves)
    assert all(item.cvss_score == 9.2 for item in items)
    assert calls == [0, 1, 0, 1]
    assert collector.metrics["pagination_restarts"] == 1


def test_unstable_nvd_only_restarts_once_and_never_returns_partial_rows(monkeypatch):
    fixture = pages()[0]["vulnerabilities"][0]
    calls = []

    class HTTP:
        def get(self, url, **kwargs):
            offset = kwargs["params"]["startIndex"]
            calls.append(offset)
            # Every second page changes totalResults. Even after the
            # bounded replay, do not report incomplete coverage as healthy.
            total = 2 if offset == 0 else 3
            return Response(
                {
                    "totalResults": total,
                    "resultsPerPage": 1,
                    "startIndex": offset,
                    "vulnerabilities": [deepcopy(fixture)],
                }
            )

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", lambda _: None)
    collector = NvdCollector(HTTP())
    items, health = collector.collect(START, END)
    assert items == [] and health.status == "failed"
    assert collector.metrics["pagination_restarts"] == 1
    assert calls == [0, 1, 0, 1]
