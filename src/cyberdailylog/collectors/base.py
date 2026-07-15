
from datetime import datetime, timezone
from pathlib import Path
from abc import ABC, abstractmethod
import json, time
from cyberdailylog.models import SourceHealth
class BaseCollector(ABC):
    name="base"; required=False; source_tier=1
    def __init__(self, http=None, fixture_dir: Path|None=None, offline: bool=False, token: str|None=None): self.http=http; self.fixture_dir=fixture_dir or Path("tests/fixtures"); self.offline=offline; self.token=token
    def fixture_json(self, filename: str): return json.loads((self.fixture_dir/filename).read_text(encoding="utf-8"))
    def timed_health(self, status, started, received=0, accepted=0, rejected=0, http_status=None, err=None):
        fin=datetime.now(timezone.utc); return SourceHealth(source=self.name,status=status,started_at=started,finished_at=fin,duration_ms=int((fin-started).total_seconds()*1000),http_status=http_status,items_received=received,items_accepted=accepted,items_rejected=rejected,error_type=type(err).__name__ if err else None,sanitized_error_message=str(err)[:200] if err else None,required=self.required)
    @abstractmethod
    def collect(self, since: datetime, until: datetime): ...
