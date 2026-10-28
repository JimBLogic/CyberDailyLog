from copy import deepcopy
import json
import runpy
import subprocess
import sys

import pytest
from cyberdailylog.state import write_state

guard = runpy.run_path("scripts/verify_publication.py")


def state():
    return {
        "schema_version": 2,
        "catalog_baselined": True,
        "coverage_end": "2026-10-19T10:00:00Z",
        "vulnerabilities": {
            "CVE-2026-10000": {
                "first_seen": "2026-09-01T10:00:00Z",
                "observations": {"NVD": {"modified_at": "2026-10-18T10:00:00Z"}},
                "transitions": [{"event_id": "retained"}],
            }
        },
    }


def artifact(root, nvd="healthy"):
    reports = root / "reports"
    reports.mkdir(parents=True)
    report = {
        "generated_at": "2026-10-19T10:30:00Z",
        "coverage_end": "2026-10-19T10:00:00Z",
        "degraded": False,
        "items": [],
        "source_health": [
            {"source": s, "status": nvd if s == "nvd" else "healthy"} for s in ["cisa_kev", "nvd", "github_advisories"]
        ],
    }
    for name, data in [
        ("latest.json", report),
        ("source-health.json", report["source_health"]),
        ("portfolio-feed.json", {"project": "CyberDailyLog", "generated_at": report["generated_at"]}),
        ("dashboard-feed.json", {"project": "CyberDailyLog", "generated_at": report["generated_at"]}),
        ("pipeline-metrics.json", {"report_generated": report["generated_at"]}),
    ]:
        (reports / name).write_text(json.dumps(data))
    (reports / "latest.md").write_text("Report")
    (root / "README.md").write_text("README")
    folder = reports / "archive/2026/10"
    folder.mkdir(parents=True)
    for name, suffix in [("latest.json", ".json"), ("latest.md", ".md"), ("source-health.json", "-source-health.json")]:
        (folder / ("2026-10-19" + suffix)).write_bytes((reports / name).read_bytes())
    write_state(reports / "cti-state.json.gz", state())
    return root


@pytest.mark.parametrize("change", ["cve", "first_seen", "source", "transition", "watermark", "modified"])
def test_history_regressions_are_rejected(change):
    before = state()
    after = deepcopy(before)
    row = after["vulnerabilities"]["CVE-2026-10000"]
    if change == "cve":
        after["vulnerabilities"].clear()
    elif change == "first_seen":
        row["first_seen"] = "2026-10-19T10:00:00Z"
    elif change == "source":
        row["observations"].clear()
    elif change == "transition":
        row["transitions"].clear()
    elif change == "watermark":
        after["coverage_end"] = "2026-10-18T10:00:00Z"
    else:
        row["observations"]["NVD"]["modified_at"] = "2026-10-17T10:00:00Z"
    with pytest.raises(ValueError):
        guard["preserve_history"](before, after)


def test_append_only_history_and_new_cves_are_accepted():
    before = state()
    after = deepcopy(before)
    after["vulnerabilities"]["CVE-2026-10000"]["transitions"].append({"event_id": "new"})
    after["vulnerabilities"]["CVE-2026-10001"] = deepcopy(after["vulnerabilities"]["CVE-2026-10000"])
    assert guard["preserve_history"](before, after) == {
        "baseline_cves": 1,
        "candidate_cves": 2,
        "history_preserved": True,
    }


@pytest.mark.parametrize("fault", ["missing", "timestamp", "health", "archive", "metrics", "symlink"])
def test_incomplete_or_mixed_artifacts_fail_closed(tmp_path, fault):
    root = artifact(tmp_path / "artifact")
    if fault == "missing":
        (root / "reports/dashboard-feed.json").unlink()
    elif fault == "timestamp":
        (root / "reports/portfolio-feed.json").write_text(
            '{"project":"CyberDailyLog","generated_at":"2026-10-18T10:00:00Z"}'
        )
    elif fault == "health":
        (root / "reports/source-health.json").write_text("[]")
    elif fault == "archive":
        (root / "reports/archive/2026/10/2026-10-19.md").write_text("Mixed report")
    elif fault == "metrics":
        (root / "reports/pipeline-metrics.json").write_text("{}")
    else:
        (root / "reports/link").symlink_to(root / "README.md")
    with pytest.raises(ValueError):
        guard["bundle"](root)


@pytest.mark.parametrize("baseline_complete", [False, True])
def test_real_publisher_gate_allows_recovery_but_skips_duplicate_close(tmp_path, monkeypatch, baseline_complete):
    baseline = artifact(tmp_path / "repo", "healthy" if baseline_complete else "failed")
    subprocess.run(["git", "init", "--quiet", str(baseline)], check=True)
    subprocess.run(["git", "-C", str(baseline), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(baseline),
            "-c",
            "user.name=QA",
            "-c",
            "user.email=qa@example.test",
            "commit",
            "--quiet",
            "-m",
            "baseline",
        ],
        check=True,
    )
    root = artifact(tmp_path / "incoming")
    manifest, _ = guard["bundle"](root)
    (root / "publication-manifest.json").write_text(json.dumps(manifest))
    evidence = tmp_path / "evidence.json"
    monkeypatch.chdir(baseline)
    before = (baseline / "reports/cti-state.json.gz").read_bytes()
    monkeypatch.setattr(
        sys, "argv", ["verify", "--root", str(root), "--baseline-ref", "HEAD", "--evidence", str(evidence)]
    )
    assert guard["main"]() == 0
    result = json.loads(evidence.read_text())
    assert result["duplicate_close"] == baseline_complete
    assert (baseline / "reports/cti-state.json.gz").read_bytes() == before
    if not baseline_complete:
        assert result["history_preserved"] is True


def test_manifest_detects_changed_bytes_even_when_json_semantics_match(tmp_path, monkeypatch):
    root = artifact(tmp_path / "artifact")
    manifest, _ = guard["bundle"](root)
    (root / "publication-manifest.json").write_text(json.dumps(manifest))
    (root / "README.md").write_text("Tampered README")
    monkeypatch.setattr(sys, "argv", ["verify", "--root", str(root)])
    with pytest.raises(ValueError, match="integrity mismatch"):
        guard["main"]()


@pytest.mark.parametrize("relative", ["reports/publication-manifest.json", "reports/archive/publication-manifest.json"])
def test_nested_manifest_cannot_bypass_artifact_allowlist(tmp_path, relative):
    root = artifact(tmp_path / "artifact")
    manifest, _ = guard["bundle"](root)
    (root / "publication-manifest.json").write_text(json.dumps(manifest))
    guard["bundle"](root)  # The root manifest is the sole intentional exception.
    (root / relative).write_text("{}")
    with pytest.raises(ValueError, match="unexpected publication artifact files"):
        guard["bundle"](root)
