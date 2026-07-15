import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cyberdailylog.models import SourceHealth


class BaseCollector(ABC):
    name = "base"
    required = False
    source_tier = 1

    def __init__(
        self,
        http: Any = None,
        fixture_dir: Path | None = None,
        offline: bool = False,
        token: str | None = None,
    ) -> None:
        self.http = http
        self.fixture_dir = fixture_dir or Path("tests/fixtures")
        self.offline = offline
        self.token = token

    def fixture_json(self, filename: str) -> Any:
        return json.loads((self.fixture_dir / filename).read_text(encoding="utf-8"))

    def timed_health(
        self,
        status: str,
        started: datetime,
        received: int = 0,
        accepted: int = 0,
        rejected: int = 0,
        http_status: int | None = None,
        err: Exception | None = None,
    ) -> SourceHealth:
        finished = datetime.now(timezone.utc)
        return SourceHealth(
            source=self.name,
            status=status,
            started_at=started,
            finished_at=finished,
            duration_ms=int((finished - started).total_seconds() * 1000),
            http_status=http_status,
            items_received=received,
            items_accepted=accepted,
            items_rejected=rejected,
            error_type=type(err).__name__ if err else None,
            sanitized_error_message=str(err)[:200] if err else None,
            required=self.required,
        )

    @abstractmethod
    def collect(self, since: datetime, until: datetime) -> Any:
        """Collect source records for the requested coverage window."""
