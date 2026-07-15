from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass
class Provenance:
    field_name: str
    source_name: str
    value: Any
    collected_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        collected_at = ensure_utc(self.collected_at)
        data["collected_at"] = collected_at.isoformat() if collected_at else None
        return data


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
    collected_at: datetime = field(default_factory=utc_now)
    cve_ids: list[str] = field(default_factory=list)
    ghsa_ids: list[str] = field(default_factory=list)
    vendors: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    affected_versions: list[str] = field(default_factory=list)
    fixed_versions: list[str] = field(default_factory=list)
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
    weaknesses: list[str] = field(default_factory=list)
    ecosystems: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    detection_opportunities: list[str] = field(default_factory=list)
    blue_team_relevance: str = ""
    confidence: str = "medium"
    selection_score: int = 0
    selection_reasons: list[str] = field(default_factory=list)
    provenance: dict[str, list[Provenance]] = field(default_factory=dict)
    withdrawn: bool = False

    def __post_init__(self) -> None:
        for attribute in [
            "published_at",
            "modified_at",
            "collected_at",
            "kev_date_added",
        ]:
            setattr(self, attribute, ensure_utc(getattr(self, attribute)))

    def add_provenance(self, field_name: str, source: str, value: Any) -> None:
        self.provenance.setdefault(field_name, []).append(
            Provenance(field_name, source, value)
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for attribute in [
            "published_at",
            "modified_at",
            "collected_at",
            "kev_date_added",
        ]:
            value = ensure_utc(getattr(self, attribute))
            data[attribute] = value.isoformat() if value else None
        data["provenance"] = {
            key: [entry.to_dict() for entry in entries]
            for key, entries in self.provenance.items()
        }
        return data


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

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        started_at = ensure_utc(self.started_at)
        finished_at = ensure_utc(self.finished_at)
        data["started_at"] = started_at.isoformat() if started_at else None
        data["finished_at"] = finished_at.isoformat() if finished_at else None
        return data


@dataclass
class Report:
    generated_at: datetime
    coverage_start: datetime
    coverage_end: datetime
    items: list[IntelligenceItem]
    source_health: list[SourceHealth]
    degraded: bool = False

    def to_dict(self) -> dict[str, Any]:
        generated_at = ensure_utc(self.generated_at)
        coverage_start = ensure_utc(self.coverage_start)
        coverage_end = ensure_utc(self.coverage_end)
        return {
            "generated_at": generated_at.isoformat() if generated_at else None,
            "coverage_start": coverage_start.isoformat() if coverage_start else None,
            "coverage_end": coverage_end.isoformat() if coverage_end else None,
            "degraded": self.degraded,
            "items": [item.to_dict() for item in self.items],
            "source_health": [health.to_dict() for health in self.source_health],
        }

    def model_dump_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
