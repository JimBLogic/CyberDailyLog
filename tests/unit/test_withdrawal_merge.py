from cyberdailylog.correlation import merge_items
from cyberdailylog.models import IntelligenceItem
from cyberdailylog.scoring import compute_priority_score


def advisory(source, withdrawn, kev=False):
    return IntelligenceItem(
        canonical_id="CVE-2026-12345",
        title="Example",
        source_name=source,
        source_type="government_kev" if kev else "reviewed_advisory",
        source_url="https://example.invalid/advisory",
        cve_ids=["CVE-2026-12345"],
        withdrawn=withdrawn,
        cisa_kev=kev,
    )


def test_withdrawn_ghsa_does_not_silence_active_kev():
    active = advisory("CISA", False, kev=True)
    withdrawn = advisory("GHSA", True)
    for observations in ([active, withdrawn], [withdrawn, active]):
        merged = merge_items(observations)[0]
        assert merged.withdrawn is False
        assert compute_priority_score(merged, {})[0] >= 9.6
        assert {(p.source_name, p.value) for p in merged.provenance["withdrawn"]} == {("CISA", False), ("GHSA", True)}
    assert withdrawn.withdrawn is True
    assert active.provenance == {}


def test_all_withdrawn_advisories_stay_withdrawn():
    merged = merge_items([advisory("GHSA-A", True), advisory("GHSA-B", True)])[0]
    assert merged.withdrawn is True
    assert compute_priority_score(merged, {})[0] == 0.0
