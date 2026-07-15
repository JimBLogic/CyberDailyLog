from datetime import datetime, timezone
import json
import pathlib
from cyberdailylog.pipeline import Pipeline
from cyberdailylog.collectors.nvd import NvdCollector
from cyberdailylog.collectors.cisa_kev import CisaKevCollector
from cyberdailylog.collectors.github_advisories import GitHubAdvisoryCollector
from cyberdailylog.correlation import merge_items
from cyberdailylog.scoring import score_items
from cyberdailylog.settings import load_yaml


def window():
    return datetime(2026, 7, 14, tzinfo=timezone.utc), datetime(2026, 7, 16, tzinfo=timezone.utc)


def test_collectors_cover_required_cases():
    s, u = window()
    n, h = NvdCollector(offline=True).collect(s, u)
    assert h.items_received == 3 and h.items_rejected == 1
    assert any(i.cvss_score is None for i in n)
    k, kh = CisaKevCollector(offline=True).collect(s, u)
    assert k[0].known_exploited is True and kh.status == "fixture_only"
    g, gh = GitHubAdvisoryCollector(offline=True).collect(s, u)
    assert any(i.withdrawn for i in g) and gh.items_received == 2


def test_correlation_provenance_and_no_invented_fixed_versions():
    s, u = window()
    items = []
    for cls in (CisaKevCollector, NvdCollector, GitHubAdvisoryCollector):
        got, _ = cls(offline=True).collect(s, u)
        items += got
    merged = merge_items(items)
    one = [i for i in merged if "CVE-2099-0001" in i.cve_ids][0]
    assert len([i for i in merged if "CVE-2099-0001" in i.cve_ids]) == 1
    assert one.cisa_kev is True and one.fixed_versions == ["2.0.1"]
    assert "known_exploited" in one.provenance


def test_scoring_kev_outranks_high_cvss_and_reasons():
    s, u = window()
    items = []
    for cls in (CisaKevCollector, NvdCollector, GitHubAdvisoryCollector):
        got, _ = cls(offline=True).collect(s, u)
        items += got
    scored = score_items(
        merge_items(items),
        load_yaml(pathlib.Path("config/scoring.yml")),
        load_yaml(pathlib.Path("config/technologies.yml")),
        s,
        u,
    )
    assert scored[0].cisa_kev is True
    assert scored[0].selection_reasons
    assert scored[0].known_exploited is True


def test_offline_generation_and_schema(tmp_path):
    Pipeline(output_dir=tmp_path, offline=True).run(*window())
    assert (tmp_path / "latest.md").exists() and (tmp_path / "latest.json").exists()
    data = json.loads((tmp_path / "latest.json").read_text())
    assert data["items"][0]["selection_reasons"]
    assert (tmp_path / "archive" / "2026" / "07" / "2026-07-16.md").exists()
    text = (tmp_path / "latest.md").read_text()
    assert "Personal" not in text and "certification" not in text.lower()


def test_no_static_pipeline_regressions():
    src = "\n".join(p.read_text(errors="ignore") for p in pathlib.Path("src").rglob("*.py"))
    assert "git push" not in src
    assert "AZFREE2025" not in src
