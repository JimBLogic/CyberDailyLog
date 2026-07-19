from datetime import datetime, timezone
import json
import pathlib
from importlib.resources import files

from cyberdailylog.collectors.cisa_kev import CisaKevCollector
from cyberdailylog.collectors.github_advisories import GitHubAdvisoryCollector
from cyberdailylog.collectors.nvd import NvdCollector
from cyberdailylog.correlation import merge_items
from cyberdailylog.pipeline import Pipeline
from cyberdailylog.scoring import score_items
from cyberdailylog.settings import load_yaml


def window():
    return datetime(2026, 7, 14, tzinfo=timezone.utc), datetime(2026, 7, 16, tzinfo=timezone.utc)


def test_collectors_cover_required_cases():
    since, until = window()
    nvd, health = NvdCollector(offline=True).collect(since, until)
    assert health.items_received == 3 and health.items_rejected == 1
    assert any(item.cvss_score is None for item in nvd)
    kev, kev_health = CisaKevCollector(offline=True).collect(since, until)
    assert kev[0].known_exploited is True and kev_health.status == "fixture_only"
    advisories, advisory_health = GitHubAdvisoryCollector(offline=True).collect(since, until)
    assert any(item.withdrawn for item in advisories) and advisory_health.items_received == 2


def test_correlation_provenance_and_no_invented_fixed_versions():
    since, until = window()
    items = []
    for collector in (CisaKevCollector, NvdCollector, GitHubAdvisoryCollector):
        got, _ = collector(offline=True).collect(since, until)
        items += got
    merged = merge_items(items)
    one = [item for item in merged if "CVE-2099-0001" in item.cve_ids][0]
    assert len([item for item in merged if "CVE-2099-0001" in item.cve_ids]) == 1
    assert one.cisa_kev is True and one.fixed_versions == ["2.0.1"]
    assert "known_exploited" in one.provenance


def test_scoring_kev_outranks_high_cvss_and_has_priority_reasons():
    since, until = window()
    items = []
    for collector in (CisaKevCollector, NvdCollector, GitHubAdvisoryCollector):
        got, _ = collector(offline=True).collect(since, until)
        items += got
    scored = score_items(
        merge_items(items),
        load_yaml(pathlib.Path("config/scoring.yml")),
        load_yaml(pathlib.Path("config/technologies.yml")),
        since,
        until,
    )
    assert scored[0].cisa_kev is True
    assert scored[0].selection_reasons
    assert scored[0].priority_score == 10.0
    assert scored[0].priority_reasons
    assert scored[0].known_exploited is True


def test_offline_generation_schema_curation_and_archives(tmp_path):
    Pipeline(output_dir=tmp_path, offline=True).run(*window())

    assert (tmp_path / "latest.md").exists()
    assert (tmp_path / "latest.json").exists()
    assert (tmp_path / "source-health.json").exists()
    data = json.loads((tmp_path / "latest.json").read_text())
    assert data["items"][0]["selection_reasons"]
    assert 0 <= data["items"][0]["priority_score"] <= 10
    assert data["items"][0]["priority_reasons"]

    archive_dir = tmp_path / "archive" / "2026" / "07"
    assert (archive_dir / "2026-07-16.md").exists()
    assert (archive_dir / "2026-07-16.json").exists()
    assert (archive_dir / "2026-07-16-source-health.json").exists()

    text = (tmp_path / "latest.md").read_text()
    assert "Personal" not in text and "certification" not in text.lower()
    assert len(text.splitlines()) <= 140
    assert len(text.encode("utf-8")) <= 12288


def test_schema_resource_matches_top_level_schema():
    package_schema = (
        files("cyberdailylog").joinpath("schemas/intelligence-item.schema.json").read_text(encoding="utf-8")
    )
    top_level_schema = pathlib.Path("schemas/intelligence-item.schema.json").read_text(encoding="utf-8")
    assert json.loads(package_schema) == json.loads(top_level_schema)


def test_no_static_pipeline_regressions():
    src = "\n".join(path.read_text(errors="ignore") for path in pathlib.Path("src").rglob("*.py"))
    assert "git push" not in src
    assert "AZFREE2025" not in src
