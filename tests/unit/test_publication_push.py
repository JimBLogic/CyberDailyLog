"""Exercise publication races with local repositories; no network or credentials."""

import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess

from cyberdailylog.state import write_state

helpers = runpy.run_path("tests/unit/test_publication_integrity.py")
SCRIPTS = Path("scripts").resolve()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.STDOUT, text=True).strip()


def setup(tmp_path):
    remote, seed = tmp_path / "remote.git", tmp_path / "seed"
    git(tmp_path, "init", "--bare", str(remote))
    seed.mkdir()
    git(seed, "init", "-b", "main")
    git(seed, "config", "user.name", "Fixture")
    git(seed, "config", "user.email", "fixture@example.test")
    (seed / "scripts").mkdir()
    for name in ["push_publication.sh", "verify_publication.py", "validate_publication.py"]:
        shutil.copyfile(SCRIPTS / name, seed / "scripts" / name)
    (seed / "reports").mkdir()
    write_state(seed / "reports/cti-state.json.gz", helpers["state"]())
    (seed / "reports/latest.json").write_text(json.dumps({"generated_at": "2026-10-18T10:30:00Z", "items": []}))
    (seed / "README.md").write_text("Original")
    git(seed, "add", ".")
    git(seed, "commit", "-m", "baseline")
    git(seed, "remote", "add", "origin", str(remote))
    git(seed, "push", "-u", "origin", "main")
    git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
    publisher, writer = tmp_path / "publisher", tmp_path / "writer"
    for root in [publisher, writer]:
        git(tmp_path, "clone", str(remote), str(root))
        git(root, "config", "user.name", "Fixture")
        git(root, "config", "user.email", "fixture@example.test")
    artifact = helpers["artifact"](publisher / "incoming-publication")
    subprocess.run(
        ["python", str(SCRIPTS / "verify_publication.py"), "--root", str(artifact), "--write-manifest"],
        check=True,
        capture_output=True,
    )
    shutil.copytree(artifact / "reports", publisher / "reports", dirs_exist_ok=True)
    (publisher / "README.md").write_text("Generated")
    git(publisher, "add", "reports", "README.md")
    git(publisher, "commit", "-m", "generated")
    return remote, publisher, writer


def push(publisher):
    output = publisher / "actions-output"
    env = {**os.environ, "GITHUB_OUTPUT": str(output)}
    result = subprocess.run(
        ["bash", "scripts/push_publication.sh"], cwd=publisher, env=env, capture_output=True, text=True, timeout=30
    )
    return result, output.read_text() if output.exists() else ""


def test_code_only_race_revalidates_and_preserves_both_changes(tmp_path):
    remote, publisher, writer = setup(tmp_path)
    (writer / "code.txt").write_text("Intervening code must survive")
    git(writer, "add", "code.txt")
    git(writer, "commit", "-m", "code change")
    git(writer, "push")
    result, output = push(publisher)
    assert result.returncode == 0, result.stdout + result.stderr
    assert git(remote, "show", "main:code.txt") == "Intervening code must survive"
    assert git(remote, "show", "main:README.md") == "Generated"
    assert "push_completed=" in output and "commit_sha=" + git(remote, "rev-parse", "main") in output
    assert json.loads((publisher / "publication-retry-check.json").read_text())["history_preserved"]


def test_concurrent_complete_close_is_retained_without_fake_push_receipt(tmp_path):
    remote, publisher, writer = setup(tmp_path)
    shutil.copytree(publisher / "incoming-publication/reports", writer / "reports", dirs_exist_ok=True)
    git(writer, "add", "reports")
    git(writer, "commit", "-m", "another complete close")
    git(writer, "push")
    before = git(remote, "rev-parse", "main")
    result, output = push(publisher)
    assert result.returncode == 0, result.stdout + result.stderr
    assert git(remote, "rev-parse", "main") == before
    assert output == "duplicate_close=true\n"


def test_new_remote_history_blocks_stale_candidate(tmp_path):
    remote, publisher, writer = setup(tmp_path)
    state = helpers["state"]()
    state["vulnerabilities"]["CVE-2026-10000"]["transitions"].append({"event_id": "must-retain"})
    write_state(writer / "reports/cti-state.json.gz", state)
    git(writer, "add", "reports")
    git(writer, "commit", "-m", "new retained history")
    git(writer, "push")
    before = git(remote, "rev-parse", "main")
    result, output = push(publisher)
    assert result.returncode != 0
    assert "discard" in result.stderr or "rewrite" in result.stderr
    assert git(remote, "rev-parse", "main") == before and not output


def test_push_denial_without_remote_advance_is_not_retried(tmp_path):
    remote, publisher, _ = setup(tmp_path)
    hook = publisher / ".git/hooks/pre-push"
    hook.write_text("#!/bin/sh\necho invocation >> push-count\nexit 1\n")
    hook.chmod(0o755)
    before = git(remote, "rev-parse", "main")
    result, output = push(publisher)
    assert result.returncode != 0 and not output
    assert (publisher / "push-count").read_text().splitlines() == ["invocation"]
    assert git(remote, "rev-parse", "main") == before
