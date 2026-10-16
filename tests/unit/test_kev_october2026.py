"""Regression scenario from CISA's 14 October 2026 KEV additions and Ahsay's patch correction."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from cyberdailylog.collectors.cisa_kev import CisaKevCollector
from cyberdailylog.correlation import merge_items
from cyberdailylog.models import IntelligenceItem
from cyberdailylog.operational_evidence import load_operational_evidence
from cyberdailylog.state import StateLedger


TARGETS = {
    "CVE-2026-76519": ("Cisco", "Secure Email Gateway"),
    "CVE-2026-0322": ("Palo Alto Networks", "PAN-OS"),
    "CVE-2026-105133": ("Ahsay", "AhsayCBS"),
    "CVE-2026-105134": ("Ahsay", "AhsayCBS"),
}
ADVISORY = "https://www.ahsay.com/en/company/announcements/patch-cve-105133-105134-update"
OBSERVED_AT = datetime(2026, 10, 15, 14, 41, tzinfo=timezone.utc)


def kev_items():
    catalog = {
        "count": 4,
        "vulnerabilities": [
            {
                "cveID": cve,
                "dateAdded": "2026-10-14",
                "dueDate": "2026-10-17",
                "vendorProject": vendor,
                "product": product,
                "knownRansomwareCampaignUse": "Unknown",
                "requiredAction": "Apply mitigations in accordance with vendor instructions.",
            }
            for cve, (vendor, product) in TARGETS.items()
        ],
    }
    collector = CisaKevCollector()
    collector.http = SimpleNamespace(get=lambda *a, **kw: SimpleNamespace(json=lambda: catalog))
    result, health = collector.collect(OBSERVED_AT - timedelta(days=1), OBSERVED_AT)
    assert health.status == "healthy"
    return result


def test_four_kev_memberships_are_unique_and_kept_separate_from_disclosure():
    observed = kev_items()
    assert len(observed) == len({i.canonical_id for i in observed}) == 4
    for entry in observed:
        assert entry.cisa_kev is True and entry.known_exploited is True
        assert entry.kev_date_added == datetime(2026, 10, 14, tzinfo=timezone.utc)
        assert entry.published_at is None
        assert entry.modified_at is None
        assert entry.cisa_due_date == datetime(2026, 10, 17, tzinfo=timezone.utc)
        assert entry.known_ransomware_use is None

    disclosed = IntelligenceItem(
        canonical_id="CVE-2026-105133",
        title="Original disclosure",
        source_name="NVD",
        source_type="vulnerability_database",
        source_url="https://nvd.nist.gov/vuln/detail/CVE-2026-105133",
        cve_ids=["CVE-2026-105133"],
        published_at=datetime(2026, 10, 4, tzinfo=timezone.utc),
        modified_at=datetime(2026, 10, 5, tzinfo=timezone.utc),
    )
    merged = merge_items([*observed, disclosed])
    assert len(merged) == 4
    ahsay = next(i for i in merged if i.canonical_id == disclosed.canonical_id)
    assert ahsay.published_at == disclosed.published_at
    assert ahsay.kev_date_added == datetime(2026, 10, 14, tzinfo=timezone.utc)


def test_vendor_correction_creates_two_material_remediation_events_once(tmp_path):
    ledger = StateLedger(tmp_path / "state.json")
    initial = kev_items()
    ledger.observe(initial, OBSERVED_AT, OBSERVED_AT - timedelta(days=1), OBSERVED_AT)
    assert len(ledger.records) == 4
    ledger.save()

    remediation = [
        i
        for i in load_operational_evidence(Path("config/operational-evidence.yml"))
        if i.source_name.startswith("Vendor remediation:")
    ]
    assert {i.canonical_id for i in remediation} == {"CVE-2026-105133", "CVE-2026-105134"}
    assert all(i.source_url == ADVISORY and i.known_exploited is None for i in remediation)
    assert all(i.published_at is None for i in remediation)

    next_at = OBSERVED_AT + timedelta(hours=1)
    updated = StateLedger(tmp_path / "state.json")
    events = updated.observe(remediation, next_at, OBSERVED_AT, next_at)
    assert {event.canonical_id for event in events} == {"CVE-2026-105133", "CVE-2026-105134"}
    for event in events:
        assert "vendor_remediation_updated" in event.transition_type
        assert event.cisa_kev is True and event.known_exploited is True
        assert "AhsayCBS v10.3.4.45" in event.fixed_versions
        assert "AhsayCBS v9.15.2.70" in event.fixed_versions
        assert "INSUFFICIENT" in " ".join(event.recommended_actions)
        assert event.state_transitions[-1]["sources"][0]["url"] == ADVISORY
    updated.save()

    replay_at = next_at + timedelta(hours=1)
    replay = StateLedger(tmp_path / "state.json")
    assert replay.observe([*kev_items(), *remediation], replay_at, next_at, replay_at) == []
    assert len(replay.records) == 4
    assert all(
        len(replay.records[cve]["transitions"]) == 1 for cve in ("CVE-2026-105133", "CVE-2026-105134")
    )


def test_legacy_kev_timestamp_does_not_survive_2026_correction(tmp_path):
    old = kev_items()[0]
    old.published_at = old.kev_date_added
    old.modified_at = old.kev_date_added
    ledger = StateLedger(tmp_path / "state.json")
    ledger.observe([old], OBSERVED_AT, OBSERVED_AT, OBSERVED_AT)
    ledger.save()

    fixed = StateLedger(tmp_path / "state.json")
    fixed.observe([kev_items()[0]], OBSERVED_AT + timedelta(hours=1), OBSERVED_AT, OBSERVED_AT)
    source = fixed.records[old.canonical_id]["observations"][old.source_name]
    assert "published_at" not in source
    assert "modified_at" not in source
    assert source["kev_date_added"] == "2026-10-14T00:00:00+00:00"
