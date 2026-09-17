"""A small durable ledger: source observations, material CVE transitions and replay safety."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import fields
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path

from .correlation import merge_items
from .models import IntelligenceItem, ensure_utc
from .scoring import compute_priority_score, priority_level, score_item, score_items

DATE_FIELDS = {
    "published_at",
    "modified_at",
    "collected_at",
    "kev_date_added",
    "cisa_due_date",
    "first_seen",
    "last_seen",
    "state_changed_at",
}
FLAGS = {
    "cisa_kev": "entered_cisa_kev",
    "known_exploited": "exploitation_confirmed",
    "known_ransomware_use": "ransomware_linked",
    "vendor_confirmed_exploitation": "vendor_exploitation_confirmed",
    "public_exploit": "public_exploit_published",
    "critical_asset_exposure": "critical_asset_exposure",
}
EXCLUDED = {
    "provenance",
    "state_transitions",
    "previous_state",
    "current_state",
    "transition_type",
    "discovery_type",
    "first_seen",
    "last_seen",
    "state_changed_at",
    "priority_before",
    "priority_after",
    "priority_level_before",
}


def iso(value):
    return ensure_utc(value).isoformat() if value else None


def parse_date(value):
    return ensure_utc(datetime.fromisoformat(value.replace("Z", "+00:00"))) if value else None


def from_dict(value):
    allowed = {f.name for f in fields(IntelligenceItem)} - {"provenance"}
    data = {k: v for k, v in value.items() if k in allowed}
    for key in DATE_FIELDS & data.keys():
        data[key] = parse_date(data[key])
    return IntelligenceItem(**data)


def operational_state(item):
    return {
        **{flag: getattr(item, flag) for flag in FLAGS},
        "exploitation_status": "confirmed_exploitation"
        if item.known_exploited or item.vendor_confirmed_exploitation
        else item.exploitation_status or "unknown",
        "cvss_score": item.cvss_score,
        "severity": (item.severity or "unknown").lower(),
        "cisa_due_date": iso(item.cisa_due_date),
        "cisa_required_action": item.cisa_required_action,
        "fixed_versions": sorted(set(item.fixed_versions)),
        "withdrawn": item.withdrawn,
    }


def material_changes(previous, current):
    changes = [
        event for field, event in FLAGS.items() if previous.get(field) is not True and current.get(field) is True
    ]
    if (
        previous.get("exploitation_status") != current["exploitation_status"]
        and current["exploitation_status"] == "confirmed_exploitation"
    ):
        changes.append("exploitation_status_confirmed")
    old, new = previous.get("cvss_score"), current.get("cvss_score")
    if new is not None and (
        (old is None and new >= 7)
        or (old is not None and (abs(new - old) >= 1 or any(min(old, new) < cut <= max(old, new) for cut in (4, 7, 9))))
    ):
        changes.append("cvss_material_change")
    levels = {"unknown": 0, "low": 1, "medium": 2, "moderate": 2, "high": 3, "critical": 4}
    if levels.get(current["severity"], 0) > levels.get(previous.get("severity"), 0):
        changes.append("severity_escalated")
    for key, event in (("cisa_due_date", "cisa_due_date_changed"), ("cisa_required_action", "required_action_changed")):
        if current.get(key) and current[key] != previous.get(key):
            changes.append(event)
    if set(current["fixed_versions"]) - set(previous.get("fixed_versions", [])):
        changes.append("vendor_remediation_updated")
    if current["withdrawn"] and not previous.get("withdrawn"):
        changes.append("advisory_withdrawn")
    return changes


class StateLedger:
    def __init__(self, path: Path):
        self.path = path
        self.data = (
            json.loads(path.read_text())
            if path.exists()
            else {"schema_version": 2, "vulnerabilities": {}, "catalog_baselined": False}
        )
        if self.data.get("schema_version") != 2 or not isinstance(self.data.get("vulnerabilities"), dict):
            raise ValueError("Invalid CTI state; refusing to overwrite history")
        self.records = self.data["vulnerabilities"]

    def seed_archives(self, root: Path):
        if self.records or self.path.exists():
            return
        for path in [*sorted((root / "archive").glob("**/*.json")), root / "latest.json"]:
            if path.name.endswith("-source-health.json") or not path.exists():
                continue
            report = json.loads(path.read_text())
            observed = parse_date(report["generated_at"])
            for raw in report.get("items", []):
                if not raw.get("cve_ids") or raw.get("category") not in {"vulnerability", "advisory"}:
                    continue
                item = from_dict(raw)
                item.source_name, item.source_type = "Retained report", "archive"
                self.observe([item], observed, observed, observed, baseline=True)
            self.data["coverage_end"] = report.get("coverage_end")

    def observe(self, items, now, since, until, technologies=None, scoring=None, baseline=False):
        technologies, scoring = technologies or {}, scoring or {}
        grouped: dict[str, list[IntelligenceItem]] = {}
        other = []
        for item in items:
            if not item.cve_ids or item.category not in {"vulnerability", "advisory"}:
                other.append(item)
                continue
            for cve in item.cve_ids:
                single = deepcopy(item)
                single.canonical_id, single.cve_ids = cve, [cve]
                grouped.setdefault(cve, []).append(single)
        emitted = score_items(merge_items(other), scoring, technologies, since, until)
        for cve, incoming in sorted(grouped.items()):
            is_new = cve not in self.records
            record = deepcopy(
                self.records.get(cve)
                or {
                    "first_seen": iso(now),
                    "first_seen_basis": "retained report" if baseline else "collector observation",
                    "observations": {},
                    "transitions": [],
                }
            )
            for item in incoming:
                snapshot = {k: v for k, v in item.to_dict().items() if k not in EXCLUDED}
                previous_source = record["observations"].get(item.source_name)
                if previous_source:
                    old_date = parse_date(previous_source.get("modified_at"))
                    # CISA has no per-entry modified timestamp: compare its full catalog.
                    if (
                        item.source_type not in {"government_kev", "archive"}
                        and old_date
                        and item.modified_at
                        and item.modified_at < old_date
                    ):
                        continue
                    for key, value in previous_source.items():
                        if snapshot.get(key) is None:
                            snapshot[key] = value
                record["observations"][item.source_name] = snapshot
            merged = merge_items([from_dict(s) for s in record["observations"].values()])[0]
            previous = record.get("current_state", {})
            for flag in FLAGS:
                if previous.get(flag) is True:
                    setattr(merged, flag, True)
            if previous.get("exploitation_status") == "confirmed_exploitation":
                merged.exploitation_status = "confirmed_exploitation"
            current = operational_state(merged)
            changes = [] if is_new else material_changes(previous, current)
            merged.transition_type = changes
            if score_item(merged, scoring, technologies, since, until) is None:
                merged.priority_score, merged.priority_reasons = compute_priority_score(merged, technologies)
            merged.priority_level = priority_level(merged)
            merged.first_seen, merged.last_seen = parse_date(record["first_seen"]), now
            merged.current_state = current
            if changes:
                event = {
                    "changed_at": iso(now),
                    "transition_type": changes,
                    "previous_state": previous,
                    "current_state": current,
                    "sources": [
                        {"name": i.source_name, "url": i.source_url, "modified_at": iso(i.modified_at)}
                        for i in incoming
                    ],
                    "priority_before": record.get("priority_score"),
                    "priority_after": merged.priority_score,
                    "priority_level_before": record.get("priority_level"),
                    "priority_level_after": merged.priority_level,
                    "basis": "retained reports" if baseline else "collector observation",
                    "event_id": hashlib.sha256(
                        json.dumps([cve, previous, current], sort_keys=True).encode()
                    ).hexdigest()[:24],
                }
                if not record["transitions"] or record["transitions"][-1]["event_id"] != event["event_id"]:
                    record["transitions"].append(event)
                merged.previous_state, merged.state_changed_at = previous, now
                merged.priority_before, merged.priority_after = record.get("priority_score"), merged.priority_score
                merged.priority_level_before = record.get("priority_level")
            merged.state_transitions = record["transitions"]
            merged.discovery_type = "state_transition" if changes else "new_vulnerability" if is_new else None
            record.update(
                last_seen=iso(now),
                current_state=current,
                priority_score=merged.priority_score,
                priority_level=merged.priority_level,
            )
            self.records[cve] = record
            recent = any(
                (i.published_at and since <= i.published_at <= until)
                or (i.modified_at and since <= i.modified_at <= until)
                for i in incoming
            )
            first_catalog = not self.data["catalog_baselined"] and all(
                i.source_type == "government_kev" for i in incoming
            )
            if not baseline and (changes or (is_new and (recent or not first_catalog))):
                emitted.append(merged)
        if not baseline:
            self.data.update(
                updated_at=iso(now),
                coverage_end=iso(until),
                catalog_baselined=self.data["catalog_baselined"]
                or any(i.source_type == "government_kev" for i in items),
            )
        return sorted(
            emitted,
            key=lambda i: (i.priority_level == "EMERGENCY", i.priority_score, i.selection_score, i.canonical_id),
            reverse=True,
        )

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.data, sort_keys=True, indent=2) + "\n")
        temporary.replace(self.path)


def coverage_start(ledger, until, hours):
    since = until - timedelta(hours=hours)
    previous = parse_date(ledger.data.get("coverage_end"))
    if previous and previous <= until:
        since = min(since, previous - timedelta(hours=2))
    if until - since > timedelta(days=120):
        raise ValueError("Coverage gap exceeds NVD's 120-day window; explicit backfill required")
    return since
