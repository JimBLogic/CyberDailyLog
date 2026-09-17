from datetime import datetime, timedelta, timezone
import json
from types import SimpleNamespace
import pytest

from cyberdailylog.models import IntelligenceItem
from cyberdailylog.state import StateLedger, coverage_start
from cyberdailylog.pipeline import Pipeline
from cyberdailylog.operational_evidence import load_operational_evidence
from cyberdailylog.collectors.nvd import NvdCollector
from cyberdailylog.collectors.cisa_kev import CisaKevCollector

NOW = datetime(2026, 9, 17, 10, tzinfo=timezone.utc)


def item(**changes):
    values = dict(
        canonical_id="CVE-2026-12345",
        title="Example",
        cve_ids=["CVE-2026-12345"],
        source_name="NVD",
        source_type="vulnerability_database",
        source_url="https://nvd.nist.gov/vuln/detail/CVE-2026-12345",
        published_at=NOW,
        modified_at=NOW,
        cvss_score=7.5,
        exploitation_status="no_known_evidence",
    )
    values.update(changes)
    return IntelligenceItem(**values)


def observe(tmp_path, observations, when=NOW):
    ledger = StateLedger(tmp_path / "state.json")
    result = ledger.observe(observations, when, when - timedelta(days=1), when)
    ledger.save()
    return result


def test_new_and_unchanged_are_distinct(tmp_path):
    first = observe(tmp_path, [item()])[0]
    assert first.discovery_type == "new_vulnerability" and first.first_seen == NOW
    assert observe(tmp_path, [item()], NOW + timedelta(hours=1)) == []


def test_real_kev_ransomware_scoring_and_multiple_transition_history(tmp_path):
    observe(tmp_path, [item(cvss_score=10)])
    kev = observe(tmp_path, [item(cisa_kev=True, known_exploited=True, cvss_score=10)])[0]
    ransom = observe(tmp_path, [item(cisa_kev=True, known_exploited=True, known_ransomware_use=True, cvss_score=10)])[0]
    assert "entered_cisa_kev" in kev.transition_type
    assert kev.priority_before == 9.4 and kev.priority_after == 9.6
    assert ransom.transition_type == ["ransomware_linked"]
    assert ransom.priority_before == 9.6 and ransom.priority_after == 10
    assert ransom.priority_level_before == "HIGH" and ransom.priority_level == "EMERGENCY"
    assert len(ransom.state_transitions) == 2
    assert ransom.state_transitions[-1]["sources"][0]["url"].startswith("https://")
    assert (
        observe(tmp_path, [item(cisa_kev=True, known_exploited=True, known_ransomware_use=True, cvss_score=10)]) == []
    )


def test_late_kev_catalog_change_survives_old_date_and_optional_outage(tmp_path):
    observe(tmp_path, [item(epss_score=0.9, public_exploit=True)])
    kev = item(
        source_name="CISA",
        source_type="government_kev",
        cisa_kev=True,
        known_exploited=True,
        cvss_score=None,
        published_at=NOW - timedelta(days=100),
        modified_at=NOW - timedelta(days=100),
    )
    changed = observe(tmp_path, [kev])[0]
    assert changed.epss_score == 0.9 and changed.public_exploit is True
    assert "entered_cisa_kev" in changed.transition_type
    assert observe(tmp_path, []) == []
    assert observe(tmp_path, [kev]) == []
    ledger = StateLedger(tmp_path / "state.json")
    assert set(ledger.records[kev.canonical_id]["observations"]) == {"NVD", "CISA"}


def test_no_known_evidence_is_not_confirmed_absence_and_unknown_does_not_clear_positive(tmp_path):
    observe(tmp_path, [item(exploitation_status="unknown")])
    observe(tmp_path, [item(exploitation_status="confirmed_not_exploited")])
    ledger = StateLedger(tmp_path / "state.json")
    assert ledger.records["CVE-2026-12345"]["current_state"]["exploitation_status"] == "confirmed_not_exploited"
    assert observe(tmp_path, [item(known_exploited=True)])[0].transition_type
    assert observe(tmp_path, [item(known_exploited=None, exploitation_status="unknown")]) == []
    assert StateLedger(tmp_path / "state.json").records["CVE-2026-12345"]["current_state"]["known_exploited"] is True


@pytest.mark.parametrize(
    ("change", "event"),
    [
        ({"vendor_confirmed_exploitation": True}, "vendor_exploitation_confirmed"),
        ({"public_exploit": True}, "public_exploit_published"),
        ({"cvss_score": 9.1}, "cvss_material_change"),
        ({"severity": "critical"}, "severity_escalated"),
        ({"cisa_due_date": NOW + timedelta(days=14)}, "cisa_due_date_changed"),
        ({"cisa_required_action": "Disconnect affected appliances"}, "required_action_changed"),
        ({"fixed_versions": ["2.0.1"]}, "vendor_remediation_updated"),
        ({"withdrawn": True}, "advisory_withdrawn"),
        ({"critical_asset_exposure": True}, "critical_asset_exposure"),
    ],
)
def test_material_updates_and_replay(tmp_path, change, event):
    observe(tmp_path, [item()])
    changed = observe(tmp_path, [item(**change)])[0]
    assert event in changed.transition_type
    assert observe(tmp_path, [item(**change)]) == []


def test_source_order_metadata_only_and_stale_observation(tmp_path):
    nvd, kev = item(), item(source_name="CISA", source_type="government_kev", cisa_kev=True)
    observe(tmp_path, [nvd, kev])
    nvd.modified_at += timedelta(minutes=5)
    assert observe(tmp_path, [kev, nvd], NOW + timedelta(minutes=5)) == []
    nvd.cvss_score, nvd.modified_at = 3, NOW - timedelta(days=1)
    assert observe(tmp_path, [nvd]) == []


def test_multicve_advisory_and_first_full_catalog_baseline(tmp_path):
    results = observe(tmp_path, [item(cve_ids=["CVE-2026-12345", "CVE-2026-12346"])])
    assert {r.canonical_id for r in results} == {"CVE-2026-12345", "CVE-2026-12346"}
    other = tmp_path / "other"
    other.mkdir()
    assert (
        observe(
            other,
            [
                item(
                    source_name="CISA",
                    source_type="government_kev",
                    published_at=NOW - timedelta(days=500),
                    modified_at=NOW - timedelta(days=500),
                )
            ],
        )
        == []
    )


def test_bootstrap_coverage_overlap_and_corruption(tmp_path):
    old = NOW - timedelta(days=5)
    (tmp_path / "latest.json").write_text(
        json.dumps({"generated_at": old.isoformat(), "coverage_end": old.isoformat(), "items": [item().to_dict()]})
    )
    ledger = StateLedger(tmp_path / "state.json")
    ledger.seed_archives(tmp_path)
    assert ledger.records["CVE-2026-12345"]["first_seen"] == old.isoformat()
    assert coverage_start(ledger, NOW, 24) == old - timedelta(hours=2)
    with pytest.raises(ValueError, match="backfill"):
        coverage_start(ledger, NOW + timedelta(days=121), 24)
    ledger.path.write_text('{"schema_version":999,"vulnerabilities":{}}')
    with pytest.raises(ValueError, match="refusing"):
        StateLedger(ledger.path)


def test_dry_run_does_not_advance_ledger_and_rejected_run_does_not_write(tmp_path, monkeypatch):
    since, until = datetime(2026, 7, 14, tzinfo=timezone.utc), datetime(2026, 7, 16, tzinfo=timezone.utc)
    Pipeline(output_dir=tmp_path, offline=True).run(since, until, dry_run=True)
    assert not (tmp_path / "cti-state.json").exists()
    monkeypatch.setattr("cyberdailylog.pipeline.quorum_ok", lambda health: False)
    with pytest.raises(SystemExit):
        Pipeline(output_dir=tmp_path, offline=True).run(since, until, fail_on_degraded=True)
    assert not (tmp_path / "cti-state.json").exists()


def test_nvd_queries_modified_window_and_exploit_tags_without_claiming_active():
    collector = NvdCollector()
    calls = []

    def get(url, **kw):
        calls.append(kw["params"].copy())
        return SimpleNamespace(json=lambda: {"resultsPerPage": 2000, "totalResults": 0, "vulnerabilities": []})

    collector.http = SimpleNamespace(get=get)
    items, health = collector.collect(NOW - timedelta(days=1), NOW)
    assert health.status == "healthy" and not items
    assert "lastModStartDate" in calls[0] and "pubStartDate" not in calls[0]
    raw = {
        "cve": {
            "id": "CVE-2026-12345",
            "published": "2025-01-01T00:00:00",
            "lastModified": "2026-09-17T10:00:00",
            "references": [{"url": "https://example.test/poc", "tags": ["Exploit"]}],
        }
    }
    parsed = collector._item(raw)
    assert parsed.public_exploit is True and parsed.known_exploited is None
    assert parsed.modified_at == NOW


def test_cisa_unknown_and_invalid_catalog():
    collector = CisaKevCollector()

    def get(url, **kw):
        return SimpleNamespace(json=lambda: {"vulnerabilities": []})

    collector.http = SimpleNamespace(get=get)
    assert collector.collect(NOW, NOW)[1].status == "failed"
    collector.http = SimpleNamespace(
        get=lambda *args, **kwargs: SimpleNamespace(
            json=lambda: {
                "vulnerabilities": [
                    {"cveID": "CVE-2026-12345", "dateAdded": "2025-01-01", "knownRansomwareCampaignUse": "Unknown"}
                ]
            }
        )
    )
    found, health = collector.collect(NOW, NOW)
    assert health.status == "healthy" and found[0].known_ransomware_use is None


def test_verified_vendor_evidence_requires_explicit_positive_statement(tmp_path):
    path = tmp_path / "evidence.yml"
    assert load_operational_evidence(path) == []
    row = dict(
        cve="CVE-2026-12345",
        source_url="https://vendor.example/advisory",
        confirmed_at=NOW.isoformat(),
        vendor_confirmed_exploitation=True,
        required_action="Patch",
    )
    path.write_text(json.dumps({"observations": [row]}))
    result = load_operational_evidence(path)[0]
    assert result.vendor_confirmed_exploitation is True and result.known_exploited is True
    row["vendor_confirmed_exploitation"] = False
    path.write_text(json.dumps({"observations": [row]}))
    with pytest.raises(ValueError):
        load_operational_evidence(path)
