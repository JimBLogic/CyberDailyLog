from datetime import datetime, timezone
import gzip
import json
from pathlib import Path

import pytest

from cyberdailylog import state
from cyberdailylog.models import IntelligenceItem
from cyberdailylog.state import StateLedger, read_state, write_state


def observed_ledger(path):
    ledger = StateLedger(path)
    now = datetime(2026, 10, 18, tzinfo=timezone.utc)
    first = IntelligenceItem(
        canonical_id="CVE-2026-12345",
        cve_ids=["CVE-2026-12345"],
        title="Tecnología / 漢字",
        source_name="Primary source",
        source_type="vendor_evidence",
        source_url="https://example.test/advisory",
        published_at=now,
        modified_at=now,
        cvss_score=7.5,
        known_exploited=None,
        fixed_versions=["2.1"],
    )
    ledger.observe([first], now, now, now)
    first.known_exploited = True
    ledger.observe([first], now, now, now)
    return ledger


def test_lossless_legacy_migration_replay_and_deterministic_gzip(tmp_path):
    legacy = tmp_path / "cti-state.json"
    baseline = observed_ledger(legacy)
    baseline.save()
    original = legacy.read_bytes()
    compressed = tmp_path / "cti-state.json.gz"
    ledger = StateLedger(compressed)
    assert ledger.data == baseline.data
    ledger.save()
    assert not legacy.exists()
    assert gzip.decompress(compressed.read_bytes()) == original
    previous = compressed.read_bytes()
    ledger.save()
    assert compressed.read_bytes() == previous
    # Old callers also discover the new storage without seeding a fresh ledger.
    reloaded = StateLedger(legacy)
    assert reloaded.path == compressed and reloaded.data == baseline.data
    record = reloaded.records["CVE-2026-12345"]
    assert len(record["transitions"]) == 1
    assert record["current_state"]["known_exploited"] is True
    now = datetime(2026, 10, 18, tzinfo=timezone.utc)
    observation = state.from_dict(next(iter(record["observations"].values())))
    assert reloaded.observe([observation], now, now, now) == []


def test_compressed_state_wins_over_stale_legacy_and_never_falls_back_on_corruption(tmp_path):
    compressed = tmp_path / "cti-state.json.gz"
    ledger = observed_ledger(compressed)
    ledger.save()
    legacy = compressed.with_suffix("")
    legacy.write_text('{"schema_version":2,"vulnerabilities":{},"catalog_baselined":false}')
    assert StateLedger(legacy).data == ledger.data
    stale = legacy.read_bytes()
    compressed.write_bytes(b"not a gzip file")
    with pytest.raises(gzip.BadGzipFile):
        StateLedger(compressed)
    assert legacy.read_bytes() == stale


def test_size_failure_preserves_both_baselines_and_removes_temporary_file(tmp_path, monkeypatch):
    path = tmp_path / "cti-state.json.gz"
    ledger = observed_ledger(path)
    ledger.save()
    legacy = path.with_suffix("")
    legacy.write_text("recoverable legacy copy")
    previous = path.read_bytes()
    monkeypatch.setattr(state, "MAX_STATE_BYTES", 1)
    with pytest.raises(ValueError, match="48 MiB"):
        ledger.save()
    assert path.read_bytes() == previous and legacy.read_text() == "recoverable legacy copy"
    assert not list(tmp_path.glob("*.tmp"))


def test_interrupted_replace_keeps_legacy_and_previous_compressed_state(tmp_path, monkeypatch):
    path = tmp_path / "cti-state.json.gz"
    ledger = observed_ledger(path)
    ledger.save()
    previous = path.read_bytes()
    legacy = path.with_suffix("")
    legacy.write_text("recoverable legacy copy")

    def denied(*args):
        raise OSError("simulated interrupted replacement")

    monkeypatch.setattr(Path, "replace", denied)
    with pytest.raises(OSError, match="interrupted"):
        ledger.save()
    assert path.read_bytes() == previous and legacy.exists()
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("compressed", [True, False])
def test_decoded_budget_applies_to_read_and_write(tmp_path, monkeypatch, compressed):
    path = tmp_path / ("state.json.gz" if compressed else "state.json")
    data = {"oversized": "x" * 100}
    payload = json.dumps(data).encode()
    path.write_bytes(gzip.compress(payload) if compressed else payload)
    before = path.read_bytes()
    monkeypatch.setattr(state, "MAX_DECODED_STATE_BYTES", 20)
    with pytest.raises(ValueError, match="decoded size budget"):
        read_state(path)
    with pytest.raises(ValueError, match="decoded size budget"):
        write_state(path, data)
    assert path.read_bytes() == before


def test_truncated_gzip_never_seeds_a_new_history(tmp_path):
    path = tmp_path / "state.json.gz"
    observed_ledger(path).save()
    path.write_bytes(path.read_bytes()[:-8])
    with pytest.raises(EOFError):
        StateLedger(path)
