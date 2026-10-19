"""Small, credential-free operational timings, separate from public feed schemas."""

from datetime import datetime, timezone
from time import perf_counter


class PipelineTiming:
    def __init__(self):
        self.started = self.previous = perf_counter()
        self.data = {"schema_version": 1, "started_at": datetime.now(timezone.utc).isoformat(), "phases_ms": {}}

    def mark(self, phase):
        now = perf_counter()
        self.data["phases_ms"][phase] = round((now - self.previous) * 1000, 3)
        self.previous = now

    def finish(self, outcome):
        self.data.update(
            outcome=outcome,
            finished_at=datetime.now(timezone.utc).isoformat(),
            total_ms=round((perf_counter() - self.started) * 1000, 3),
        )
        return self.data
