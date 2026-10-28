"""Bounded Git races use dummy local repositories; no external service."""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
from zoneinfo import ZoneInfo

SCRIPT = Path("scripts/publish_timing.sh").resolve()
GENERATOR = """import json
from pathlib import Path
p = Path('reports/publication-timing-history.json')
history = json.loads(p.read_text())
if 'current-run' not in history:
    history.append('current-run')
p.write_text(json.dumps(history))
Path('reports/publication-timing.json').write_text(json.dumps({'runs': history}))
"""


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.STDOUT, text=True).strip()


def setup(tmp_path, real=False):
    remote, seed = tmp_path / "remote.git", tmp_path / "seed"
    git(tmp_path, "init", "--bare", str(remote))
    seed.mkdir()
    git(seed, "init", "-b", "main")
    git(seed, "config", "user.name", "Fixture")
    git(seed, "config", "user.email", "fixture@example.invalid")
    (seed / "scripts").mkdir()
    shutil.copyfile(SCRIPT, seed / "scripts/publish_timing.sh")
    if real:
        shutil.copyfile(Path("scripts/publication_timing.py"), seed / "scripts/publication_timing.py")
        package = seed / "src/cyberdailylog"
        package.mkdir(parents=True)
        for name in ["__init__.py", "reliability.py", "recovery.py"]:
            shutil.copyfile(Path("src/cyberdailylog") / name, package / name)
    else:
        (seed / "scripts/publication_timing.py").write_text(GENERATOR)
    (seed / "reports").mkdir()
    (seed / "reports/publication-timing-history.json").write_text("[]" if real else '["previous-run"]')
    (seed / "reports/publication-timing.json").write_text("{}")
    (seed / "code.txt").write_text("original")
    git(seed, "add", ".")
    git(seed, "commit", "-m", "baseline")
    git(seed, "remote", "add", "origin", str(remote))
    git(seed, "push", "-u", "origin", "main")
    git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
    publisher, writer = tmp_path / "publisher", tmp_path / "writer"
    for root in [publisher, writer]:
        git(tmp_path, "clone", str(remote), str(root))
        git(root, "config", "user.name", "Fixture")
        git(root, "config", "user.email", "fixture@example.invalid")
    return remote, publisher, writer


def publish(root):
    return subprocess.run(["bash", "scripts/publish_timing.sh"], cwd=root, capture_output=True, text=True, timeout=30)


def test_race_regenerates_history_and_preserves_concurrent_code(tmp_path):
    remote, publisher, writer = setup(tmp_path)
    (writer / "reports/publication-timing-history.json").write_text('["previous-run", "concurrent-run"]')
    (writer / "code.txt").write_text("concurrent code")
    git(writer, "add", ".")
    git(writer, "commit", "-m", "concurrent update")
    git(writer, "push")
    result = publish(publisher)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(git(remote, "show", "main:reports/publication-timing-history.json")) == [
        "previous-run",
        "concurrent-run",
        "current-run",
    ]
    assert git(remote, "show", "main:code.txt") == "concurrent code"


def test_denied_push_without_remote_advance_is_not_retried(tmp_path):
    remote, publisher, _ = setup(tmp_path)
    hook = remote / "hooks/pre-receive"
    hook.write_text("#!/bin/sh\necho denied >&2\nexit 1\n")
    hook.chmod(0o700)
    result = publish(publisher)
    assert result.returncode != 0
    assert "refusing blind retry" in result.stderr
    assert json.loads(git(remote, "show", "main:reports/publication-timing-history.json")) == ["previous-run"]
    assert git(publisher, "rev-list", "--count", "origin/main..HEAD") == "1"


def test_dirty_worktree_is_preserved_without_publication(tmp_path):
    remote, publisher, _ = setup(tmp_path)
    (publisher / "code.txt").write_text("uncommitted work")
    before = git(remote, "rev-parse", "main")
    result = publish(publisher)
    assert result.returncode != 0
    assert (publisher / "code.txt").read_text() == "uncommitted work"
    assert git(remote, "rev-parse", "main") == before


def test_failed_prior_step_keeps_diagnostics_without_publishing(tmp_path):
    remote, publisher, _ = setup(tmp_path)
    before = git(remote, "rev-parse", "main")
    result = subprocess.run(
        ["bash", "scripts/publish_timing.sh"],
        cwd=publisher,
        env={**os.environ, "TIMING_CAN_PUBLISH": "false"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert git(remote, "rev-parse", "main") == before
    assert "current-run" in json.loads((publisher / "reports/publication-timing-history.json").read_text())


def real_generator_race(tmp_path, skipped):
    remote, publisher, writer = setup(tmp_path, real=True)
    target = (
        datetime.now(timezone.utc)
        .astimezone(ZoneInfo("Europe/Madrid"))
        .replace(hour=12, minute=0, second=0, microsecond=0)
        .astimezone(timezone.utc)
    )
    generated = (target + timedelta(minutes=2)).isoformat()
    pushed = (target + timedelta(minutes=3)).isoformat()
    winner = {
        "schema_version": 2,
        "run_id": "winner",
        "run_attempt": "1",
        "scheduled_for": target.isoformat(),
        "status": "on_time",
        "core_complete": True,
        "report_generated": generated,
        "actual_publication_time": pushed,
    }
    prior = {**winner, "run_id": "prior"}
    (writer / "reports/publication-timing-history.json").write_text(json.dumps([prior, winner]))
    (writer / "reports/publication-timing.json").write_text(json.dumps(winner))
    (writer / "code.txt").write_text("concurrent code")
    git(writer, "add", ".")
    git(writer, "commit", "-m", "concurrent real evidence")
    git(writer, "push")
    inputs = {
        "run": {"created_at": target.isoformat(), "run_started_at": target.isoformat()},
        "health": [{"source": name, "status": "healthy"} for name in ("cisa_kev", "nvd", "github_advisories")],
        "feed": {"generated_at": generated},
    }
    args = []
    for name, value in inputs.items():
        path = publisher / f"input-{name}.json"
        path.write_text(json.dumps(value))
        args.extend([f"--{name}", str(path)])
    args.extend(["--output", "reports/publication-timing.json", "--history", "reports/publication-timing-history.json"])
    env = {
        **os.environ,
        "TIMING_CAN_PUBLISH": "true",
        "GITHUB_RUN_ID": "current",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_REPOSITORY": "fixture/local",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "PREFLIGHT_RESULT": "success",
        "PREFLIGHT_SHOULD_RUN": "false" if skipped else "true",
        "COLLECT_RESULT": "skipped" if skipped else "success",
        "PUBLISH_RESULT": "skipped" if skipped else "success",
        "PUSH_COMPLETED": pushed,
        "COMMIT_CREATED": generated,
    }
    result = subprocess.run(
        ["bash", "scripts/publish_timing.sh", *args], cwd=publisher, env=env, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stdout + result.stderr
    history = json.loads(git(remote, "show", "main:reports/publication-timing-history.json"))
    assert {row["run_id"] for row in history} == {"prior", "winner", "current"}
    assert len(history) == 3
    view = json.loads(git(remote, "show", "main:reports/publication-timing.json"))
    assert view["last_attempt"]["run_id"] == "current"
    if skipped:
        assert view["run_id"] == "winner"
        assert view["actual_publication_time"] == pushed
        assert view["last_attempt"]["status"] == "skipped"
    else:
        assert view["run_id"] == "current"
        assert view["core_complete"] is True
    assert git(remote, "show", "main:code.txt") == "concurrent code"


def test_real_generator_preserves_concurrent_evidence(tmp_path):
    real_generator_race(tmp_path, skipped=False)


def test_real_generator_preserves_winner_when_recovery_is_skipped(tmp_path):
    real_generator_race(tmp_path, skipped=True)
