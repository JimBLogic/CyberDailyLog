from pathlib import Path

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
    dispatch = workflow["on"]["workflow_dispatch"]["inputs"]
    assert dispatch["dry_run"]["type"] == "boolean"
    assert dispatch["dry_run"]["default"] is True
    assert dispatch["lookback_hours"]["required"] is True
    collect = workflow["jobs"]["collect"]
    publish = workflow["jobs"]["publish"]
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
    assert 'python -m cyberdailylog run --lookback-hours "$LOOKBACK_HOURS"\n' in run_script
    assert "--fail-on-degraded" in run_script
    assert "--dry-run" not in run_script
    assert steps["Generate compact portfolio feed"]["run"] == "python -m cyberdailylog.portfolio_feed"
    assert steps["Update repository landing snapshot"]["run"] == "python -m cyberdailylog.readme_snapshot"

    upload = steps["Upload generated outputs"]
    assert upload["with"]["name"] == "reports-${{ github.run_id }}"
    assert "README.md" in upload["with"]["path"]
    assert "reports/" in upload["with"]["path"]
    assert upload["with"]["if-no-files-found"] == "error"
    assert upload["with"]["retention-days"] == 7
    assert "cat reports/source-health.json" in steps["Show source health"]["run"]

    publish_steps = {step.get("name"): step for step in publish["steps"]}
    download = publish_steps["Download generated outputs"]
    assert download["with"]["name"] == upload["with"]["name"]
    assert download["with"]["path"] == "."
    publish_script = publish_steps["Commit and push generated outputs"]["run"]
    assert "git add README.md reports" in publish_script
    assert "git diff --cached --quiet" in publish_script
    assert "exit 0" in publish_script
    assert "git push" in publish_script
    assert "git add ." not in publish_script


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
