"""One bounded recovery of a core source after exhausted transient HTTP retries."""

from dataclasses import replace
import re
import time


RECOVERY_WAIT_SECONDS = 20


def collect_with_recovery(collector, since, until):
    items, health = collector.collect(since, until)
    # Do not retry invalid payloads, auth/TLS failures, rate limits, or a
    # Retry-After exceeding the HTTP client's budget. Optional sources retain
    # their existing policy. A recovery always uses the SAME coverage window.
    message = health.sanitized_error_message or ""
    if (
        collector.offline
        or not health.required
        or health.status != "failed"
        or health.error_type != "SourceError"
        or not re.fullmatch(r"HTTP (500|502|503|504) from [a-z0-9.-]+", message)
    ):
        return items, health

    first_metrics = dict(getattr(collector, "metrics", {}))
    time.sleep(RECOVERY_WAIT_SECONDS)
    # Discard all results of the failed collection; never stitch partial pages.
    items, recovered = collector.collect(since, until)
    metrics = dict(getattr(collector, "metrics", {}))
    for key, value in first_metrics.items():
        current = metrics.get(key, 0)
        if type(value) in (int, float) and type(current) in (int, float):
            metrics[key] = value + current
    metrics.update(
        recovery_attempts=1,
        recovery_wait_seconds=RECOVERY_WAIT_SECONDS,
        recovery_initial_error=message,
        recovery_succeeded=recovered.status == "healthy",
    )
    collector.metrics = metrics
    if recovered.status != "healthy":
        items = []
    recovered = replace(
        recovered,
        started_at=health.started_at,
        duration_ms=int((recovered.finished_at - health.started_at).total_seconds() * 1000),
    )
    return items, recovered
