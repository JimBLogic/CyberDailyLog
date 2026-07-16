from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_LIMIT = 5
SCHEMA_VERSION = 1


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _identifier(item: dict[str, Any]) -> str:
    cve_ids = _string_list(item.get("cve_ids"))
    if cve_ids:
        return cve_ids[0]
    ghsa_ids = _string_list(item.get("ghsa_ids"))
    if ghsa_ids:
        return ghsa_ids[0]
    return str(item.get("canonical_id") or "unidentified-item")


def _priority_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": _identifier(item),
        "title": str(item.get("title") or _identifier(item)),
        "cve_ids": _string_list(item.get("cve_ids")),
        "ghsa_ids": _string_list(item.get("ghsa_ids")),
        "products": _string_list(item.get("products"))[:3],
        "cvss_score": _number(item.get("cvss_score")),
        "severity": str(item.get("severity") or "unknown"),
        "epss_score": _number(item.get("epss_score")),
        "cisa_kev": bool(item.get("cisa_kev")),
        "known_exploited": bool(item.get("known_exploited")),
        "source_name": str(item.get("source_name") or "unknown"),
        "source_url": str(item.get("source_url") or ""),
        "selection_score": int(item.get("selection_score") or 0),
        "selection_reasons": _string_list(item.get("selection_reasons"))[:3],
    }


def build_portfolio_feed(report: dict[str, Any], limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    if limit <= 0:
        raise ValueError("limit must be a positive integer")

    required = ("generated_at", "coverage_start", "coverage_end", "items", "source_health")
    missing = [key for key in required if key not in report]
    if missing:
        raise ValueError(f"report is missing required keys: {', '.join(missing)}")

    raw_items = report.get("items")
    raw_health = report.get("source_health")
    if not isinstance(raw_items, list) or not isinstance(raw_health, list):
        raise ValueError("report items and source_health must be arrays")

    items = [item for item in raw_items if isinstance(item, dict)]
    health = [entry for entry in raw_health if isinstance(entry, dict)]
    ranked = sorted(
        items,
        key=lambda item: (
            int(item.get("selection_score") or 0),
            _number(item.get("cvss_score")) or 0.0,
            str(item.get("canonical_id") or ""),
        ),
        reverse=True,
    )

    exploited = [item for item in items if item.get("known_exploited") is True or item.get("cisa_kev") is True]
    if exploited:
        immediate_attention = f"{len(exploited)} qualified item(s) include confirmed exploitation or CISA KEV status."
    else:
        immediate_attention = "No confirmed exploitation or CISA KEV entries qualified in this run."

    health_counts: dict[str, int] = {}
    for entry in health:
        status = str(entry.get("status") or "unknown")
        health_counts[status] = health_counts.get(status, 0) + 1

    return {
        "schema_version": SCHEMA_VERSION,
        "project": "CyberDailyLog",
        "title": "Blue Team Intelligence Digest",
        "generated_at": str(report["generated_at"]),
        "coverage_start": str(report["coverage_start"]),
        "coverage_end": str(report["coverage_end"]),
        "degraded": bool(report.get("degraded")),
        "qualified_developments": len(items),
        "immediate_attention": immediate_attention,
        "top_vulnerabilities": [_priority_item(item) for item in ranked[:limit]],
        "source_health": {
            "total": len(health),
            "status_counts": health_counts,
        },
        "report_url": "https://github.com/JimBLogic/CyberDailyLog/blob/main/reports/latest.md",
        "repository_url": "https://github.com/JimBLogic/CyberDailyLog",
    }


def write_portfolio_feed(report_path: Path, output_path: Path, limit: int = DEFAULT_LIMIT) -> None:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise ValueError("report JSON root must be an object")

    feed = build_portfolio_feed(report, limit=limit)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    temporary_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary_path.replace(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the compact CyberDailyLog portfolio feed")
    parser.add_argument("--report", type=Path, default=Path("reports/latest.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/portfolio-feed.json"))
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()

    write_portfolio_feed(args.report, args.output, limit=args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
