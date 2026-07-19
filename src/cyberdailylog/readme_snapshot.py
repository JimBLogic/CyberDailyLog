from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


START_MARKER = "<!-- CYBERDAILYLOG:DAILY:START -->"
END_MARKER = "<!-- CYBERDAILYLOG:DAILY:END -->"


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    return float(value) if isinstance(value, (int, float)) else None


def _status_summary(feed: dict[str, Any]) -> str:
    health = feed.get("source_health")
    if not isinstance(health, dict):
        return "Source health details are available in the generated report."
    core = health.get("core")
    optional = health.get("optional")
    if isinstance(core, dict) and isinstance(optional, dict):
        return (
            f"Core sources: **{int(core.get('healthy') or 0)}/{int(core.get('total') or 0)} healthy**. "
            f"Optional sources: **{int(optional.get('healthy') or 0)} healthy**, "
            f"**{int(optional.get('degraded') or 0)} degraded**."
        )
    counts = health.get("status_counts")
    if isinstance(counts, dict):
        return ", ".join(f"**{count} {status}**" for status, count in sorted(counts.items())) + "."
    return "Source health details are available in the generated report."


def build_snapshot(feed: dict[str, Any]) -> str:
    required = ("generated_at", "coverage_start", "coverage_end", "top_vulnerabilities")
    missing = [key for key in required if key not in feed]
    if missing:
        raise ValueError(f"feed is missing required keys: {', '.join(missing)}")

    top = feed.get("top_vulnerabilities")
    if not isinstance(top, list):
        raise ValueError("feed top_vulnerabilities must be an array")

    pipeline_status = str(
        feed.get("pipeline_status") or ("degraded" if feed.get("degraded") else "operational")
    ).title()
    lines = [
        START_MARKER,
        "## Latest automated brief",
        "",
        f"**Updated:** {feed['generated_at']}  ",
        f"**Coverage:** {feed['coverage_start']} → {feed['coverage_end']}  ",
        f"**Pipeline:** **{pipeline_status}**",
        "",
        str(feed.get("immediate_attention") or "No immediate-attention summary is available."),
        "",
        f"- **Assessed:** {int(feed.get('qualified_developments') or 0)} source-backed developments",
        f"- **Above threshold:** {int(feed.get('above_threshold') or len(top))}",
        f"- {_status_summary(feed)}",
        "",
        "### Highest-priority items",
        "",
    ]

    if not top:
        lines.append("No item met the current publication threshold.")
    else:
        for raw in top[:5]:
            if not isinstance(raw, dict):
                continue
            identifier = str(raw.get("id") or "Unidentified item")
            title = str(raw.get("title") or identifier)
            source_url = str(raw.get("source_url") or "#")
            priority = _number(raw.get("priority_score"))
            if priority is None:
                priority = _number(raw.get("cvss_score")) or 0.0
            why = str(raw.get("why_it_matters") or "")
            suffix = f" — {why}" if why else ""
            lines.append(f"- **[{identifier}]({source_url}) · {priority:.1f}/10** — {title}{suffix}")

    lines += [
        "",
        "[Open the concise report](reports/latest.md) · "
        "[Use the compact JSON feed](reports/portfolio-feed.json) · "
        "[Inspect source health](reports/source-health.json) · "
        "[Integration guide](docs/INTEGRATION.md)",
        END_MARKER,
    ]
    return "\n".join(lines)


def update_readme(feed_path: Path, readme_path: Path) -> None:
    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    if not isinstance(feed, dict):
        raise ValueError("feed JSON root must be an object")

    text = readme_path.read_text(encoding="utf-8")
    if START_MARKER not in text or END_MARKER not in text:
        raise ValueError("README is missing CyberDailyLog daily markers")
    before, remainder = text.split(START_MARKER, 1)
    _, after = remainder.split(END_MARKER, 1)
    updated = f"{before}{build_snapshot(feed)}{after}"
    temporary = readme_path.with_suffix(f"{readme_path.suffix}.tmp")
    temporary.write_text(updated, encoding="utf-8")
    temporary.replace(readme_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the generated CyberDailyLog README snapshot")
    parser.add_argument("--feed", type=Path, default=Path("reports/portfolio-feed.json"))
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    args = parser.parse_args()
    update_readme(args.feed, args.readme)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
