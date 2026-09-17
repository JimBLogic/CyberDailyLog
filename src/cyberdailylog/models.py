from __future__ import annotations
from dataclasses import asdict, dataclass, field as dataclass_field
from datetime import datetime, timezone
from typing import Any
import json


def utc_now():
    return datetime.now(timezone.utc)


def ensure_utc(v):
    if v is None:
        return None
    return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v.astimezone(timezone.utc)


def serial(obj):
    if isinstance(obj, datetime):
        return ensure_utc(obj).isoformat()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    raise TypeError(str(type(obj)))


@dataclass
class Provenance:
    field: str
    source_name: str
    value: Any
    collected_at: datetime = dataclass_field(default_factory=utc_now)

    def to_dict(self):
        d = asdict(self)
        d["collected_at"] = ensure_utc(self.collected_at).isoformat()
        return d


@dataclass
class IntelligenceItem:
    canonical_id: str
    title: str
    source_name: str
    source_type: str
    source_url: str
    summary: str = ""
    category: str = "vulnerability"
    source_tier: int = 1
    official_source: bool = True
    published_at: datetime | None = None
    modified_at: datetime | None = None
    collected_at: datetime = dataclass_field(default_factory=utc_now)
    author: str | None = None
    excerpt_origin: str | None = None
    community_score: int | None = None
    community_comments: int | None = None
    discussion_url: str | None = None
    cve_ids: list[str] = dataclass_field(default_factory=list)
    ghsa_ids: list[str] = dataclass_field(default_factory=list)
    vendors: list[str] = dataclass_field(default_factory=list)
    products: list[str] = dataclass_field(default_factory=list)
    affected_versions: list[str] = dataclass_field(default_factory=list)
    fixed_versions: list[str] = dataclass_field(default_factory=list)
    cvss_version: str | None = None
    cvss_score: float | None = None
    cvss_vector: str | None = None
    severity: str | None = None
    epss_score: float | None = None
    epss_percentile: float | None = None
    cisa_kev: bool | None = None
    kev_date_added: datetime | None = None
    known_exploited: bool | None = None
    known_ransomware_use: bool | None = None
    exploitation_status: str | None = None
    vendor_confirmed_exploitation: bool | None = None
    public_exploit: bool | None = None
    critical_asset_exposure: bool | None = None
    cisa_due_date: datetime | None = None
    cisa_required_action: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    state_changed_at: datetime | None = None
    discovery_type: str | None = None
    transition_type: list[str] = dataclass_field(default_factory=list)
    previous_state: dict[str, Any] | None = None
    current_state: dict[str, Any] | None = None
    state_transitions: list[dict[str, Any]] = dataclass_field(default_factory=list)
    priority_before: float | None = None
    priority_after: float | None = None
    priority_level: str = "NORMAL"
    priority_level_before: str | None = None
    weaknesses: list[str] = dataclass_field(default_factory=list)
    ecosystems: list[str] = dataclass_field(default_factory=list)
    references: list[str] = dataclass_field(default_factory=list)
    recommended_actions: list[str] = dataclass_field(default_factory=list)
    detection_opportunities: list[str] = dataclass_field(default_factory=list)
    blue_team_relevance: str = ""
    confidence: str = "medium"
    selection_score: int = 0
    selection_reasons: list[str] = dataclass_field(default_factory=list)
    priority_score: float = 0.0
    priority_reasons: list[str] = dataclass_field(default_factory=list)
    provenance: dict[str, list[Provenance]] = dataclass_field(default_factory=dict)
    withdrawn: bool = False

    def __post_init__(self):
        for k in [
            "published_at",
            "modified_at",
            "collected_at",
            "kev_date_added",
            "cisa_due_date",
            "first_seen",
            "last_seen",
            "state_changed_at",
        ]:
            setattr(self, k, ensure_utc(getattr(self, k)))

    def add_provenance(self, field_name, source, value):
        self.provenance.setdefault(field_name, []).append(Provenance(field_name, source, value))

    def to_dict(self):
        d = asdict(self)
        for k in [
            "published_at",
            "modified_at",
            "collected_at",
            "kev_date_added",
            "cisa_due_date",
            "first_seen",
            "last_seen",
            "state_changed_at",
        ]:
            d[k] = ensure_utc(getattr(self, k)).isoformat() if getattr(self, k) else None
        d["provenance"] = {k: [p.to_dict() for p in v] for k, v in self.provenance.items()}
        return d


@dataclass
class SourceHealth:
    source: str
    status: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    http_status: int | None = None
    items_received: int = 0
    items_accepted: int = 0
    items_rejected: int = 0
    cache_status: str | None = None
    error_type: str | None = None
    sanitized_error_message: str | None = None
    required: bool = False

    def to_dict(self):
        d = asdict(self)
        d["started_at"] = ensure_utc(self.started_at).isoformat()
        d["finished_at"] = ensure_utc(self.finished_at).isoformat()
        return d


@dataclass
class Report:
    generated_at: datetime
    coverage_start: datetime
    coverage_end: datetime
    items: list[IntelligenceItem]
    source_health: list[SourceHealth]
    degraded: bool = False
    cti_summary: dict[str, int] = dataclass_field(default_factory=dict)

    def to_dict(self):
        return {
            "generated_at": ensure_utc(self.generated_at).isoformat(),
            "coverage_start": ensure_utc(self.coverage_start).isoformat(),
            "coverage_end": ensure_utc(self.coverage_end).isoformat(),
            "degraded": self.degraded,
            "cti_summary": self.cti_summary,
            "items": [i.to_dict() for i in self.items],
            "source_health": [h.to_dict() for h in self.source_health],
        }

    def model_dump_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
