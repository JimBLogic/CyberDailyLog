from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_LIMIT = 5
SCHEMA_VERSION = 1
MINIMUM_PRIORITY = 5.0
REPOSITORY_URL = "https://github.com/JimBLogic/CyberDailyLog"
RAW_BASE_URL = "https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main"


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


def _truncate_words(value: str, limit: int = 180) -> str:
    clean = " ".join(value.split())
    if len(clean) <= limit:
        return clean
    shortened = clean[: limit - 1].rsplit(" ", 1)[0]
    return f"{shortened or clean[: limit - 1]}…"


def _clean_title(item: dict[str, Any]) -> str:
    identifier = _identifier(item)
    title = str(item.get("title") or identifier).strip()
    prefix = f"{identifier}:"
    if title.lower().startswith(prefix.lower()):
        title = title[len(prefix) :].strip()
    return _truncate_words(title or identifier)


def _priority_score(item: dict[str, Any]) -> float:
    priority = _number(item.get("priority_score"))
    if priority is not None:
        return round(max(0.0, min(10.0, priority)), 1)
    cvss = _number(item.get("cvss_score"))
    return round(max(0.0, min(10.0, cvss or 0.0)), 1)


def _why(item: dict[str, Any]) -> str:
    reasons = _string_list(item.get("priority_reasons")) or _string_list(item.get("selection_reasons"))
    return _truncate_words("; ".join(reasons[:2]) or "source-backed defensive relevance", 160)


def _defensive_action(item: dict[str, Any]) -> str:
    actions = _string_list(item.get("recommended_actions")) or _string_list(item.get("detection_opportunities"))
    if actions:
        return _truncate_words(actions[0], 180)
    subject = (
        _string_list(item.get("products"))
        or _string_list(item.get("ecosystems"))
        or _string_list(item.get("vendors"))
        or [_identifier(item)]
    )
    return _truncate_words(
        f"Check {', '.join(subject[:2])} against the asset inventory and follow vendor remediation guidance.",
        180,
    )


def _priority_item(item: dict[str, Any]) -> dict[str, Any]:
    products = (
        _string_list(item.get("products"))
        or _string_list(item.get("ecosystems"))
        or _string_list(item.get("vendors"))
    )
    return {
        "id": _identifier(item),
        "title": _clean_title(item),
        "cve_ids": _string_list(item.get("cve_ids")),
        "ghsa_ids": _string_list(item.get("ghsa_ids")),
        "products": products[:3],
        "cvss_score": _number(item.get("cvss_score")),
        "severity": str(item.get("severity") or "unknown"),
        "epss_score": _number(item.get("epss_score")),
        "epss_percentile": _number(item.get("epss_percentile")),
        "cisa_kev": bool(item.get("cisa_kev")),
        "known_exploited": bool(item.get("known_exploited")),
        "known_ransomware_use": bool(item.get("known_ransomware_use")),
        "source_name": str(item.get("source_name") or "unknown"),
        "source_url": str(item.get("source_url") or ""),
        "selection_score": int(item.get("selection_score") or 0),
        "selection_reasons": _string_list(item.get("selection_reasons"))[:3],
        "priority_score": _priority_score(item),
        "why_it_matters": _why(item),
        "defensive_action": _defensive_action(item),
    }


def _qualifies(item: dict[str, Any]) -> bool:
    return bool(
        _priority_score(item) >= MINIMUM_PRIORITY
        or item.get("known_exploited") is True
        or item.get("cisa_kev") is True
        or item.get("known_ransomware_use") is True
    )


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
        [item for item in items if _qualifies(item)],
        key=lambda item: (
            _priority_score(item),
            int(item.get("selection_score") or 0),
            str(item.get("canonical_id") or ""),
        ),
        reverse=True,
    )

    exploited = [
        item
        for item in items
        if item.get("known_exploited") is True
        or item.get("cisa_kev") is True
        or item.get("known_ransomware_use") is True
    ]
    if exploited:
        immediate_attention = f"{len(exploited)} item(s) include exploitation, KEV or ransomware signals."
    else:
        immediate_attention = "No confirmed exploitation, CISA KEV or ransomware-linked item qualified."

    health_counts: dict[str, int] = {}
    core = []
    optional = []
    for entry in health:
        status = str(entry.get("status") or "unknown")
        health_counts[status] = health_counts.get(status, 0) + 1
        (core if entry.get("required") is True else optional).append(entry)

    healthy_statuses = {"healthy", "fixture_only"}
    source_health = {
        "total": len(health),
        "status_counts": health_counts,
        "core": {
            "total": len(core),
            "healthy": sum(str(entry.get("status")) in healthy_statuses for entry in core),
        },
        "optional": {
            "total": len(optional),
            "healthy": sum(str(entry.get("status")) in healthy_statuses for entry in optional),
            "degraded": sum(str(entry.get("status")) in {"degraded", "failed"} for entry in optional),
        },
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "project": "CyberDailyLog",
        "title": "Blue Team Intelligence Digest",
        "generated_at": str(report["generated_at"]),
        "coverage_start": str(report["coverage_start"]),
        "coverage_end": str(report["coverage_end"]),
        "degraded": bool(report.get("degraded")),
        "pipeline_status": "degraded" if report.get("degraded") else "operational",
        "qualified_developments": len(items),
        "above_threshold": len(ranked),
        "minimum_priority": MINIMUM_PRIORITY,
        "immediate_attention_count": len(exploited),
        "immediate_attention": immediate_attention,
        "top_vulnerabilities": [_priority_item(item) for item in ranked[:limit]],
        "source_health": source_health,
        "report_url": f"{REPOSITORY_URL}/blob/main/reports/latest.md",
        "repository_url": REPOSITORY_URL,
        "endpoints": {
            "compact_feed": f"{RAW_BASE_URL}/reports/portfolio-feed.json",
            "full_report": f"{RAW_BASE_URL}/reports/latest.json",
            "source_health": f"{RAW_BASE_URL}/reports/source-health.json",
            "human_report": f"{REPOSITORY_URL}/blob/main/reports/latest.md",
        },
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
