from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
DEFAULT_DAYS = 30
MINIMUM_PRIORITY = 5.0
REPOSITORY_URL = "https://github.com/JimBLogic/CyberDailyLog"
RAW_BASE_URL = "https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main"
SCHEMA_URL = f"{RAW_BASE_URL}/schemas/dashboard-feed.schema.json"
SECURITY_CATEGORIES = {"vulnerability", "advisory"}


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _priority_score(item: dict[str, Any]) -> float:
    priority = _number(item.get("priority_score"))
    cvss = _number(item.get("cvss_score"))
    return max(0.0, min(10.0, priority if priority is not None else (cvss or 0.0)))


def _security_items(report: dict[str, Any]) -> list[dict[str, Any]]:
    items = report.get("items")
    if not isinstance(items, list):
        raise ValueError("report items must be an array")
    return [
        item
        for item in items
        if isinstance(item, dict) and str(item.get("category") or "vulnerability") in SECURITY_CATEGORIES
    ]


def _severity(item: dict[str, Any]) -> str:
    value = str(item.get("severity") or "UNKNOWN").upper()
    return value if value in {"CRITICAL", "HIGH", "MEDIUM", "LOW"} else "UNKNOWN"


def summarize_report(report: dict[str, Any]) -> dict[str, Any]:
    generated_at = str(report.get("generated_at") or "")
    if len(generated_at) < 10:
        raise ValueError("report generated_at must be an ISO date-time")
    raw_items = report.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("report items must be an array")

    items = _security_items(report)
    immediate = [
        item
        for item in items
        if item.get("known_exploited") is True
        or item.get("cisa_kev") is True
        or item.get("known_ransomware_use") is True
    ]
    above_threshold = [
        item
        for item in items
        if _priority_score(item) >= MINIMUM_PRIORITY
        or item.get("known_exploited") is True
        or item.get("cisa_kev") is True
        or item.get("known_ransomware_use") is True
    ]
    severity_counts = {
        severity: sum(_severity(item) == severity for item in items)
        for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")
    }
    health = report.get("source_health")
    health_rows = [entry for entry in health if isinstance(entry, dict)] if isinstance(health, list) else []

    return {
        "date": generated_at[:10],
        "generated_at": generated_at,
        "assessed": len(raw_items),
        "security_items": len(items),
        "above_threshold": len(above_threshold),
        "minimum_priority": MINIMUM_PRIORITY,
        "immediate_attention": len(immediate),
        "critical": severity_counts["CRITICAL"],
        "high": severity_counts["HIGH"],
        "medium": severity_counts["MEDIUM"],
        "low": severity_counts["LOW"],
        "unknown": severity_counts["UNKNOWN"],
        "sources_total": len(health_rows),
        "sources_healthy": sum(str(entry.get("status") or "") in {"healthy", "fixture_only"} for entry in health_rows),
        "degraded": bool(report.get("degraded")),
    }


def _read_report(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def build_dashboard_feed(
    report_paths: Iterable[Path],
    latest_path: Path,
    days: int = DEFAULT_DAYS,
) -> dict[str, Any]:
    if days <= 0:
        raise ValueError("days must be a positive integer")
    if not latest_path.exists():
        raise ValueError(f"latest report does not exist: {latest_path}")

    points_by_date: dict[str, dict[str, Any]] = {}
    for path in [*sorted(report_paths), latest_path]:
        if path.name.endswith("-source-health.json"):
            continue
        point = summarize_report(_read_report(path))
        points_by_date[point["date"]] = point

    history = sorted(
        points_by_date.values(),
        key=lambda point: (point["date"], point["generated_at"]),
    )[-days:]
    latest = summarize_report(_read_report(latest_path))
    return {
        "schema_version": SCHEMA_VERSION,
        "schema_url": SCHEMA_URL,
        "project": "CyberDailyLog",
        "generated_at": latest["generated_at"],
        "minimum_priority": MINIMUM_PRIORITY,
        "history": history,
        "endpoints": {
            "dashboard_feed": f"{RAW_BASE_URL}/reports/dashboard-feed.json",
            "compact_feed": f"{RAW_BASE_URL}/reports/portfolio-feed.json",
            "full_report": f"{RAW_BASE_URL}/reports/latest.json",
            "source_health": f"{RAW_BASE_URL}/reports/source-health.json",
            "repository": REPOSITORY_URL,
        },
    }


def write_dashboard_feed(
    archive_root: Path,
    latest_path: Path,
    output_path: Path,
    days: int = DEFAULT_DAYS,
) -> None:
    report_paths = archive_root.glob("**/*.json") if archive_root.exists() else []
    feed = build_dashboard_feed(report_paths, latest_path=latest_path, days=days)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    temporary_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary_path.replace(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the CyberDailyLog dashboard history feed")
    parser.add_argument("--archive-root", type=Path, default=Path("reports/archive"))
    parser.add_argument("--latest", type=Path, default=Path("reports/latest.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/dashboard-feed.json"))
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    args = parser.parse_args()

    write_dashboard_feed(
        archive_root=args.archive_root,
        latest_path=args.latest,
        output_path=args.output,
        days=args.days,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
