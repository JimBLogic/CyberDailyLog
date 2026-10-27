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


@pytest.mark.parametrize("fault", ["total", "duplicate"])
def test_changed_window_restarts_once_without_mixing_records(monkeypatch, fault):
    fixtures = pages()
    abandoned = deepcopy(fixtures[0])
    abandoned["vulnerabilities"][0]["cve"]["id"] = "CVE-2026-99999"
    unstable = deepcopy(fixtures[1])
    if fault == "total":
        unstable["totalResults"] += 1
    else:
        unstable["vulnerabilities"][0] = deepcopy(abandoned["vulnerabilities"][0])
    responses = [abandoned, unstable, *fixtures]
    calls, waits = [], []

    class HTTP:
        def get(self, url, **kwargs):
            calls.append(deepcopy(kwargs["params"]))
            return Response(responses[len(calls) - 1])

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", waits.append)
    collector = NvdCollector(HTTP())
    items, health = collector.collect(START, END)
    expected, _ = NvdCollector(offline=True).collect(START, END)
    assert health.status == "healthy" and health.items_received == 3 and health.items_rejected == 1
    assert [i.canonical_id for i in items] == [i.canonical_id for i in expected]
    assert all(i.canonical_id != "CVE-2026-99999" for i in items)
    assert [p["startIndex"] for p in calls] == [0, 2, 0, 2]
    assert len({(p["lastModStartDate"], p["lastModEndDate"]) for p in calls}) == 1
    assert waits == [6, 6, 6]
    assert collector.metrics["requests"] == 4 and collector.metrics["window_restarts"] == 1


def test_persistently_changing_window_fails_after_two_attempts(monkeypatch):
    fixtures = pages()
    calls = []

    class HTTP:
        def get(self, url, **kwargs):
            index = kwargs["params"]["startIndex"]
            calls.append(index)
            data = deepcopy(fixtures[0 if index == 0 else 1])
            if index:
                data["totalResults"] += 1
            return Response(data)

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", lambda _: None)
    collector = NvdCollector(HTTP())
    items, health = collector.collect(START, END)
    assert items == [] and health.status == "failed" and health.items_accepted == 0
    assert calls == [0, 2, 0, 2] and collector.metrics["window_restarts"] == 1


def test_transport_failure_does_not_trigger_a_second_full_window(monkeypatch):
    calls = []

    class HTTP:
        def get(self, url, **kwargs):
            calls.append(kwargs["params"]["startIndex"])
            raise SourceError("Transport failure")

    monkeypatch.setattr("cyberdailylog.collectors.nvd.time.sleep", lambda _: None)
    collector = NvdCollector(HTTP())
    items, health = collector.collect(START, END)
    assert items == [] and health.status == "failed"
    assert calls == [0] and collector.metrics["window_restarts"] == 0
