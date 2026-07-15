import json
import subprocess
import sys
from datetime import datetime, timezone

import pytest

from cyberdailylog.cli import dt, validate_reports
from cyberdailylog.exceptions import ValidationError
from cyberdailylog.pipeline import Pipeline


def test_timestamp_parsing_normalizes_to_utc():
    expected = datetime(2026, 7, 15, tzinfo=timezone.utc)
    assert dt("2026-07-15T00:00:00") == expected
    assert dt("2026-07-15T00:00:00Z") == expected
    assert dt("2026-07-15T02:00:00+02:00") == expected


def test_invalid_timestamp_reports_argparse_error():
    with pytest.raises(Exception, match="invalid ISO-8601 timestamp"):
        dt("not-a-date")


def test_validate_reports_requires_files(tmp_path):
    with pytest.raises(ValidationError, match="required report file is missing"):
        validate_reports(tmp_path)


def test_validate_reports_rejects_bad_source_health_shape(tmp_path):
    Pipeline(output_dir=tmp_path, offline=True).run()
    (tmp_path / "source-health.json").write_text(json.dumps({"bad": "shape"}), encoding="utf-8")
    with pytest.raises(ValidationError, match="must contain a list"):
        validate_reports(tmp_path)


def test_cli_entrypoint_run_and_validate(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "cyberdailylog", "run", "--offline-fixtures", "--output-dir", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "latest.md").exists()
    assert (tmp_path / "latest.json").exists()
    assert (tmp_path / "source-health.json").exists()
    validate = subprocess.run(
        [sys.executable, "-m", "cyberdailylog", "validate", "--output-dir", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert validate.returncode == 0, validate.stderr
    assert "Validation OK" in validate.stdout


def test_cli_validate_missing_reports_returns_non_zero(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "cyberdailylog", "validate", "--output-dir", str(tmp_path / "missing")],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "required report file is missing" in result.stderr


def test_cli_accepts_naive_since_until(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cyberdailylog",
            "run",
            "--offline-fixtures",
            "--since",
            "2026-07-15T00:00:00",
            "--until",
            "2026-07-16T00:00:00Z",
            "--output-dir",
            str(tmp_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads((tmp_path / "latest.json").read_text(encoding="utf-8"))
    assert data["coverage_start"] == "2026-07-15T00:00:00+00:00"


def test_fail_on_degraded_exits_before_publication(tmp_path, monkeypatch):
    monkeypatch.setattr("cyberdailylog.pipeline.quorum_ok", lambda _health: False)
    with pytest.raises(SystemExit) as exc:
        Pipeline(output_dir=tmp_path, offline=True).run(fail_on_degraded=True)
    assert exc.value.code == 2
    assert not (tmp_path / "latest.json").exists()


def test_cli_main_run_validate_and_source_health(tmp_path, capsys):
    from cyberdailylog.cli import main

    assert main(["run", "--offline-fixtures", "--output-dir", str(tmp_path)]) == 0
    assert main(["validate", "--output-dir", str(tmp_path)]) == 0
    assert main(["source-health", "--offline-fixtures", "--output-dir", str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "Validation OK" in captured.out
    assert "cisa_kev" in captured.out


def test_cli_main_dry_run_writes_reports(tmp_path):
    from cyberdailylog.cli import main

    assert main(["run", "--offline-fixtures", "--dry-run", "--output-dir", str(tmp_path)]) == 0
    assert (tmp_path / "latest.json").exists()


def test_cli_main_validate_bad_reports_raises_system_exit(tmp_path):
    from cyberdailylog.cli import main

    with pytest.raises(SystemExit):
        main(["validate", "--output-dir", str(tmp_path)])
