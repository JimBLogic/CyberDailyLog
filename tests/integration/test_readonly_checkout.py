"""Prevent accidental token persistence in read-only CI/collection jobs.

These tests deliberately *do not* remove write credentials from the two trusted
main-branch publishing jobs: they need Git's credential helper to push.
"""

from pathlib import Path

import yaml


def _load(name: str) -> dict:
    return yaml.safe_load(Path(".github/workflows", name).read_text(encoding="utf-8"))


def _checkout_steps(job: dict) -> list[dict]:
    return [step for step in job["steps"] if str(step.get("uses", "")).startswith("actions/checkout@")]


def test_all_readonly_jobs_use_ephemeral_checkout_without_git_credentials() -> None:
    daily = _load("daily-intelligence.yml")
    ci = _load("ci.yml")
    for name in ("preflight", "collect"):
        job = daily["jobs"][name]
        assert job["permissions"] == {"contents": "read"}
        checkouts = _checkout_steps(job)
        assert len(checkouts) == 1
        assert checkouts[0]["with"]["ref"] == "main"
        assert checkouts[0]["with"]["persist-credentials"] is False
    for name in ("test", "dashboard"):
        job = ci["jobs"][name]
        checkouts = _checkout_steps(job)
        assert len(checkouts) == 1
        assert checkouts[0]["with"]["persist-credentials"] is False
    assert ci["permissions"] == {"contents": "read"}


def test_only_trusted_main_publication_jobs_require_writer_tokens() -> None:
    workflow = _load("daily-intelligence.yml")
    assert workflow["permissions"] == {"contents": "read"}
    jobs = workflow["jobs"]
    assert set(jobs) == {"preflight", "collect", "publish", "timing"}
    for name in ("publish", "timing"):
        job = jobs[name]
        assert job["permissions"]["contents"] == "write"
        assert "github.ref == 'refs/heads/main'" in job["if"]
        assert len(_checkout_steps(job)) == 1
        # Writer checkouts must keep their existing Git authentication.
        assert _checkout_steps(job)[0].get("with", {}).get("persist-credentials", True) is not False
    assert "needs.collect.outputs.dry_run == 'false'" in jobs["publish"]["if"]
    assert "inputs.dry_run != true" in jobs["timing"]["if"]
    assert all(job["permissions"]["contents"] == "read" for job in (jobs["preflight"], jobs["collect"]))


def test_publication_schedule_and_manual_preview_are_unchanged() -> None:
    workflow = _load("daily-intelligence.yml")
    assert workflow["on"]["schedule"] == [
        {"cron": "0 12 * * *", "timezone": "Europe/Madrid"},
        {"cron": "17 12 * * *", "timezone": "Europe/Madrid"},
        {"cron": "30 13 * * *", "timezone": "Europe/Madrid"},
    ]
    assert workflow["on"]["workflow_dispatch"]["inputs"]["dry_run"]["default"] is False
    assert workflow["on"]["workflow_dispatch"]["inputs"]["dry_run"]["type"] == "boolean"
    collect = workflow["jobs"]["collect"]
    mode = next(step["run"] for step in collect["steps"] if step.get("id") == "mode")
    assert 'dry_run="true"' in mode
    assert 'dry_run="false"' in mode
    assert 'lookback_hours must be a positive integer' in mode
