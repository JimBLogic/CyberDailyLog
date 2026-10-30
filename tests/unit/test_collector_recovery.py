from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from cyberdailylog.collector_recovery import collect_with_recovery
from cyberdailylog.collectors.nvd import NvdCollector
from cyberdailylog.exceptions import SourceError
from cyberdailylog.models import SourceHealth


START = datetime(2026, 10, 29, tzinfo=timezone.utc)
END = START + timedelta(days=1)


def health(status, offset=0, error=None, required=True):
    return SourceHealth(
        source="nvd",
        status=status,
        started_at=START + timedelta(seconds=offset),
        finished_at=START + timedelta(seconds=offset + 5),
        duration_ms=5000,
        required=required,
        error_type="SourceError" if error else None,
        sanitized_error_message=error,
    )


class Collector:
    offline = False

    def __init__(self, results):
        self.results = iter(results)
        self.calls = []

    def collect(self, since, until):
        self.calls.append((since, until))
        self.metrics = {"requests": 3, "response_bytes": 100}
        return next(self.results)


class CollectorRecoveryTests(unittest.TestCase):
    def test_transient_failure_recovers_without_mixing_partial_items(self):
        collector = Collector([
            (["discard-me"], health("failed", error="HTTP 503 from services.nvd.nist.gov")),
            (["complete"], health("healthy", offset=25)),
        ])
        with patch("cyberdailylog.collector_recovery.time.sleep") as sleep:
            items, result = collect_with_recovery(collector, START, END)
        self.assertEqual(items, ["complete"])
        self.assertEqual(result.status, "healthy")
        self.assertEqual(collector.calls, [(START, END), (START, END)])
        sleep.assert_called_once_with(20)
        self.assertEqual(result.duration_ms, 30000)
        self.assertEqual(result.started_at, START)
        self.assertEqual(collector.metrics["requests"], 6)
        self.assertEqual(collector.metrics["response_bytes"], 200)
        self.assertTrue(collector.metrics["recovery_succeeded"])

    def test_persistent_failure_stops_after_one_recovery(self):
        failure = health("failed", error="HTTP 503 from services.nvd.nist.gov")
        collector = Collector([([], failure), (["incomplete"], health("failed", 25, failure.sanitized_error_message))])
        with patch("cyberdailylog.collector_recovery.time.sleep"):
            items, result = collect_with_recovery(collector, START, END)
        self.assertEqual(items, [])
        self.assertEqual(result.status, "failed")
        self.assertEqual(len(collector.calls), 2)
        self.assertFalse(collector.metrics["recovery_succeeded"])

    def test_auth_rate_limit_tls_schema_optional_and_offline_are_not_retried(self):
        cases = [
            ("HTTP 403 from services.nvd.nist.gov", True, False),
            ("HTTP 429 from services.nvd.nist.gov", True, False),
            ("HTTP 503 retry delay exceeds source budget for services.nvd.nist.gov", True, False),
            ("Source transport failed for services.nvd.nist.gov", True, False),
            ("Invalid NVD pagination metadata", True, False),
            ("HTTP 503 from services.nvd.nist.gov", False, False),
            ("HTTP 503 from services.nvd.nist.gov", True, True),
        ]
        for message, required, offline in cases:
            with self.subTest(message=message, required=required, offline=offline):
                collector = Collector([([], health("failed", error=message, required=required))])
                collector.offline = offline
                with patch("cyberdailylog.collector_recovery.time.sleep") as sleep:
                    _, result = collect_with_recovery(collector, START, END)
                self.assertEqual(result.status, "failed")
                self.assertEqual(len(collector.calls), 1)
                sleep.assert_not_called()

    def test_healthy_source_is_collected_only_once(self):
        collector = Collector([(["ok"], health("healthy"))])
        with patch("cyberdailylog.collector_recovery.time.sleep") as sleep:
            self.assertEqual(collect_with_recovery(collector, START, END)[0], ["ok"])
        sleep.assert_not_called()
        self.assertEqual(len(collector.calls), 1)

    def test_real_nvd_discards_failed_second_page_and_restarts_complete_window(self):
        fixtures = [
            json.loads(Path("tests/fixtures", name).read_text())
            for name in ("nvd_page1.json", "nvd_page2.json")
        ]
        calls = []

        class Response:
            def __init__(self, data):
                self.data = data
                self.content = json.dumps(data).encode()

            def json(self):
                return self.data

        class HTTP:
            def get(self, url, **kwargs):
                calls.append(deepcopy(kwargs["params"]))
                if len(calls) == 2:
                    raise SourceError("HTTP 503 from services.nvd.nist.gov")
                return Response(fixtures[1 if len(calls) == 4 else 0])

        collector = NvdCollector(HTTP())
        with patch("time.sleep"):
            items, result = collect_with_recovery(collector, START, END)
        self.assertEqual(result.status, "healthy")
        self.assertEqual(result.items_received, 3)
        self.assertEqual(result.items_rejected, 1)
        self.assertEqual(len(items), 2)
        self.assertEqual([c["startIndex"] for c in calls], [0, 2, 0, 2])
        self.assertEqual(len({(c["lastModStartDate"], c["lastModEndDate"]) for c in calls}), 1)
        self.assertEqual(collector.metrics["pages"], 3)
        self.assertEqual(collector.metrics["requests"], 4)
        self.assertEqual(collector.metrics["recovery_attempts"], 1)


if __name__ == "__main__":
    unittest.main()
