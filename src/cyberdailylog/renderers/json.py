from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from cyberdailylog.models import Report


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _coverage_date(payload: object) -> date:
    if not isinstance(payload, dict):
        raise ValueError("existing latest.json must contain an object")
    coverage_end = payload.get("coverage_end")
    if not isinstance(coverage_end, str):
        raise ValueError("existing latest.json is missing coverage_end")
    try:
        return date.fromisoformat(coverage_end[:10])
    except ValueError as exc:
        raise ValueError("existing latest.json has an invalid coverage_end") from exc


def _archive_previous_bundle(out: Path, incoming_date: date) -> None:
    latest_json = out / "latest.json"
    if not latest_json.exists():
        return

    latest_text = latest_json.read_text(encoding="utf-8")
    previous_date = _coverage_date(json.loads(latest_text))
    if previous_date == incoming_date:
        return

    archive_dir = out / "archive" / f"{previous_date:%Y}" / f"{previous_date:%m}"
    archive_json = archive_dir / f"{previous_date}.json"
    if archive_json.exists() and archive_json.read_text(encoding="utf-8") != latest_text:
        raise ValueError(f"historical JSON archive conflict for {previous_date}")
    if not archive_json.exists():
        _atomic_write(archive_json, latest_text)

    latest_health = out / "source-health.json"
    if latest_health.exists():
        health_text = latest_health.read_text(encoding="utf-8")
        archive_health = archive_dir / f"{previous_date}-source-health.json"
        if archive_health.exists() and archive_health.read_text(encoding="utf-8") != health_text:
            raise ValueError(f"historical source-health archive conflict for {previous_date}")
        if not archive_health.exists():
            _atomic_write(archive_health, health_text)


def write_json(report: Report, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    text = report.model_dump_json(indent=2) + "\n"
    health_text = json.dumps(
        [health.to_dict() for health in report.source_health],
        indent=2,
        sort_keys=True,
    ) + "\n"
    report_date = report.coverage_end.date()

    _archive_previous_bundle(out, report_date)

    archive_dir = out / "archive" / f"{report_date:%Y}" / f"{report_date:%m}"
    _atomic_write(archive_dir / f"{report_date}.json", text)
    _atomic_write(archive_dir / f"{report_date}-source-health.json", health_text)

    _atomic_write(out / "latest.json", text)
    _atomic_write(out / "source-health.json", health_text)
