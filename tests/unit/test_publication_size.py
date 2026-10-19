from pathlib import Path
import runpy
import subprocess
import sys

import pytest

guard = runpy.run_path("scripts/validate_publication.py")


def test_size_budget_is_strict_and_diagnostic():
    guard["validate"]([("report.json", 50)], limit=50)
    with pytest.raises(ValueError, match=r"before commit.*ledger.gz: 51 bytes"):
        guard["validate"]([("ledger.gz", 51)], limit=50)


def test_artifact_checks_require_a_directory_and_reject_symlinks(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        list(guard["directory_sizes"](tmp_path / "missing"))
    report = tmp_path / "report.json"
    report.write_text("{}")
    assert list(guard["directory_sizes"](tmp_path)) == [("report.json", 2)]
    (tmp_path / "link").symlink_to(report)
    with pytest.raises(ValueError, match="symlinks"):
        list(guard["directory_sizes"](tmp_path))


def test_guard_checks_the_git_index_instead_of_the_working_copy(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    report = Path("report with spaces.json")
    report.write_text("oversized staged contents")
    subprocess.run(["git", "add", report.name], check=True)
    report.write_text("{}")
    with pytest.raises(ValueError, match="report with spaces.json"):
        guard["validate"](guard["staged_sizes"](), limit=5)
    subprocess.run(["git", "add", report.name], check=True)
    guard["validate"](guard["staged_sizes"](), limit=5)
    report.unlink()
    subprocess.run(["git", "add", report.name], check=True)
    assert list(guard["staged_sizes"]()) == []


def test_publication_guard_cli_and_rejection_exit(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["validate_publication.py", "--root", str(tmp_path)])
    assert guard["main"]() == 0
    assert "50 MiB" in capsys.readouterr().out
    (tmp_path / "link").symlink_to(tmp_path / "nonexistent")
    with pytest.raises(SystemExit) as error:
        guard["main"]()
    assert error.value.code == 1 and "symlinks" in capsys.readouterr().err
