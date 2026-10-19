from pathlib import Path
import json
import re

import pytest
import yaml


def load_workflow(path: str):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_workflows_do_not_require_gh_pat_or_csv():
    text = "\n".join(path.read_text(errors="ignore") for path in Path(".github/workflows").glob("*.yml"))
    assert "custom GitHub personal access token" not in text
    assert "daily-log.csv" not in text
    assert "GH_PAT" not in text
    assert "PERSONAL_ACCESS_TOKEN" not in text


def test_readme_exposes_daily_outputs_and_integration():
    text = Path("README.md").read_text(encoding="utf-8")
    assert "reports/latest.md" in text
    assert "reports/portfolio-feed.json" in text
    assert "docs/INTEGRATION.md" in text
    assert "CYBERDAILYLOG:DAILY:START" in text
    assert "Free Cloud" not in text


def test_daily_workflow_safe_mode_and_publication_contract():
    workflow = load_workflow(".github/workflows/daily-intelligence.yml")
    assert workflow["on"]["schedule"] == [
        {"cron": "0 12 * * *", "timezone": "Europe/Madrid"},
        {"cron": "17 12 * * *", "timezone": "Europe/Madrid"},
        {"cron": "30 13 * * *", "timezone": "Europe/Madrid"},
    ]
    dispatch = workflow["on"]["workflow_dispatch"]["inputs"]
    assert dispatch["dry_run"]["type"] == "boolean"
    assert dispatch["dry_run"]["default"] is False
    assert dispatch["lookback_hours"]["required"] is True
    preflight = workflow["jobs"]["preflight"]
    collect = workflow["jobs"]["collect"]
    publish = workflow["jobs"]["publish"]
    assert preflight["permissions"] == {"contents": "read"}
    assert preflight["outputs"]["should_run"] == "${{ steps.freshness.outputs.should_run }}"
    preflight_steps = {step.get("name"): step for step in preflight["steps"]}
    freshness_script = preflight_steps["Check daily publication freshness"]["run"]
    assert 'INPUT_DRY_RUN" != "true"' in freshness_script
    assert 'published_date" = "$today"' in freshness_script
    assert 'should_run="false"' in freshness_script
    assert collect["needs"] == "preflight"
    assert collect["if"] == "${{ needs.preflight.outputs.should_run == 'true' }}"
    assert collect["permissions"] == {"contents": "read"}
    assert publish["permissions"] == {"contents": "write"}
    assert "needs.collect.outputs.dry_run == 'false'" in publish["if"]
    assert "github.ref == 'refs/heads/main'" in publish["if"]

    steps = {step.get("name", step.get("id")): step for step in collect["steps"]}
    mode_script = steps["Resolve execution mode"]["run"]
    assert 'EVENT_NAME" = "schedule"' in mode_script
    assert 'dry_run="false"' in mode_script
    assert 'dry_run="true"' in mode_script
    assert "lookback_hours must be a positive integer" in mode_script
    install_script = steps["Install application"]["run"]
    run_script = steps["Run collection"]["run"]
    assert "python -m pip install ." in install_script
    assert 'python -m cyberdailylog run --lookback-hours "$LOOKBACK_HOURS" --dry-run' in run_script
    assert "--fail-on-degraded" in run_script
    assert "--dry-run" in run_script
    assert steps["Generate compact portfolio feed"]["run"] == "python -m cyberdailylog.portfolio_feed"
    assert steps["Generate dashboard history feed"]["run"] == "python -m cyberdailylog.dashboard_feed"
    assert steps["Update repository landing snapshot"]["run"] == "python -m cyberdailylog.readme_snapshot"

    upload = steps["Upload generated outputs"]
    assert upload["with"]["name"] == "reports-${{ github.run_id }}"
    assert upload["with"]["path"] == "publication-output/"
    assert "cti-state.json" in steps["Stage bounded publication artifact"]["run"]
    assert "cti-state.json.gz" in freshness_script
    assert (
        steps["Check artifact file sizes"]["run"] == "python scripts/validate_publication.py --root publication-output"
    )
    assert upload["with"]["if-no-files-found"] == "error"
    assert upload["with"]["retention-days"] == 7
    assert "cat reports/source-health.json" in steps["Show source health"]["run"]

    publish_steps = {step.get("name"): step for step in publish["steps"]}
    download = publish_steps["Download generated outputs"]
    assert download["with"]["name"] == upload["with"]["name"]
    assert download["with"]["path"] == "incoming-publication"
    integrity = publish_steps["Verify bundle and historical integrity against current main"]["run"]
    assert "--baseline-ref HEAD" in integrity
    assert "verify_publication.py" in integrity
    publish_script = publish_steps["Commit and push generated outputs"]["run"]
    assert "git add README.md reports" in publish_script
    assert "git diff --cached --quiet" in publish_script
    assert "exit 0" in publish_script
    assert "git push" in publish_script
    assert "git add ." not in publish_script
    assert publish_script.index("publication-check.json") < publish_script.index(
        "cp -a incoming-publication/reports/. reports/"
    )
    assert publish_script.index("rm -f reports/cti-state.json") < publish_script.index("git add README.md reports")
    assert publish_script.index("validate_publication.py --staged") < publish_script.index("git commit")


def approved_action_pins():
    registry = json.loads(Path("ops/supply-chain/actions.json").read_text())
    assert registry["schema_version"] == 1
    approved = set()
    for action, versions in registry["actions"].items():
        assert action.startswith("actions/") and versions
        for version in versions:
            assert re.fullmatch(r"[0-9a-f]{40}", version["sha"])
            assert version["runtime"] == "node24"
            assert re.fullmatch(r"v\d+\.\d+\.\d+", version["version"])
            assert version.get("review") or (
                version.get("release_commit_verified") is True
                and version.get("action_yml_blob")
                and version.get("tag_url")
                and version.get("compare_url")
            )
            approved.add(f"{action}@{version['sha']}")
    return approved


def assert_reviewed_action_pin(uses):
    assert isinstance(uses, str) and re.fullmatch(r"actions/[a-z-]+@[0-9a-f]{40}", uses)
    assert uses in approved_action_pins(), f"Unreviewed Action commit: {uses}"


def assert_workflow_actions_reviewed(directory):
    seen = set()
    for path in sorted([*directory.glob("*.yml"), *directory.glob("*.yaml")]):
        workflow = load_workflow(str(path))
        assert "ubuntu-latest" not in path.read_text()
        for job in workflow["jobs"].values():
            if "uses" in job:
                assert_reviewed_action_pin(job["uses"])
            for step in job.get("steps", []):
                if "uses" in step:
                    assert_reviewed_action_pin(step["uses"])
                    seen.add(step["uses"].split("@")[0])
    return seen


def test_workflow_runtime_actions_use_current_node24_pins():
    seen = assert_workflow_actions_reviewed(Path(".github/workflows"))
    assert seen == set(json.loads(Path("ops/supply-chain/actions.json").read_text())["actions"])


@pytest.mark.parametrize("suffix", [".yml", ".yaml"])
def test_unknown_action_is_rejected_in_both_supported_workflow_extensions(tmp_path, suffix):
    (tmp_path / f"unreviewed{suffix}").write_text(
        "name: isolated-adversarial-fixture\njobs:\n  test:\n    runs-on: ubuntu-24.04\n    steps:\n"
        "      - uses: actions/checkout@" + "a" * 40 + "\n"
    )
    with pytest.raises(AssertionError, match="Unreviewed Action commit"):
        assert_workflow_actions_reviewed(tmp_path)


@pytest.mark.parametrize(
    "uses",
    [
        "actions/upload-artifact@v7",
        "actions/download-artifact@9000827",
        "actions/upload-artifact@" + "a" * 40,
        "attacker/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9",
        "${{ inputs.action }}",
    ],
)
def test_mutable_unknown_short_or_foreign_actions_are_rejected(uses):
    with pytest.raises(AssertionError):
        assert_reviewed_action_pin(uses)


def test_both_explicitly_reviewed_artifact_patch_versions_are_accepted():
    for action in ["actions/upload-artifact", "actions/download-artifact"]:
        versions = json.loads(Path("ops/supply-chain/actions.json").read_text())["actions"][action]
        assert len(versions) == 2
        for entry in versions:
            assert_reviewed_action_pin(f"{action}@{entry['sha']}")


def test_ci_installs_runtime_and_dev_dependencies_and_strict_audit():
    workflow = load_workflow(".github/workflows/ci.yml")
    steps = {step.get("name"): step for step in workflow["jobs"]["test"]["steps"]}
    install = steps["Install dependencies"]["run"]
    assert "python -m pip install ." in install
    assert "python -m pip install -r requirements-dev.txt" in install
    assert "python -m pip install -e" not in install
    assert steps["Ruff lint"]["run"] == "ruff check ."
    assert steps["Ruff format check"]["run"] == "ruff format --check ."
    assert steps["Mypy"]["run"] == "mypy src"
    assert steps["Pytest with coverage"]["run"] == "pytest"
    assert (
        steps["Offline fixture report"]["run"]
        == "python -m cyberdailylog run --offline-fixtures --output-dir tmp/reports"
    )
    assert steps["Validate generated report"]["run"] == "python -m cyberdailylog validate --output-dir tmp/reports"
    assert "python -m cyberdailylog.readme_snapshot" in steps["Generate fixture README snapshot"]["run"]
    assert steps["Build wheel"]["run"] == "python -m build"
    smoke = steps["Installed wheel smoke test"]["run"]
    assert "python -m venv /tmp/cyberdailylog-wheel-test" in smoke
    assert "/tmp/cyberdailylog-wheel-test/bin/python -m pip install dist/*.whl" in smoke
    assert "/tmp/cyberdailylog-wheel-test/bin/python -m cyberdailylog run" in smoke
    assert "/tmp/cyberdailylog-wheel-test/bin/python -m cyberdailylog validate" in smoke
    assert "/tmp/cyberdailylog-wheel-test/bin/python -m cyberdailylog.readme_snapshot" in smoke
    assert "test -f /tmp/cyberdailylog-wheel-reports/latest.md" in smoke
    assert "test -f /tmp/cyberdailylog-wheel-reports/latest.json" in smoke
    assert "test -f /tmp/cyberdailylog-wheel-reports/source-health.json" in smoke
    audit = steps["Dependency audit"]["run"]
    assert audit == "python -m pip_audit -r requirements.txt -r requirements-dev.txt"
    assert "|| echo" not in audit
