from html import escape
from pathlib import Path

from cyberdailylog.models import IntelligenceItem, Report


def _safe_join(values: list[str], separator: str = ", ") -> str:
    return escape(separator.join(values))


def _vulnerability_row(priority: int, item: IntelligenceItem) -> str:
    identifiers = _safe_join(item.cve_ids + item.ghsa_ids)
    products = _safe_join(item.products)
    cvss = item.cvss_score if item.cvss_score is not None else "n/a"
    epss = item.epss_score if item.epss_score is not None else "n/a"
    kev = "yes" if item.cisa_kev else "no"
    reasons = escape("; ".join(item.selection_reasons))
    return (
        f"| {priority} | {identifiers} | {products} | {cvss} | {epss} | "
        f"{kev} | {reasons} |"
    )


def write_markdown(
    report: Report,
    output_dir: Path,
    template_dir: Path = Path("templates"),
) -> None:
    del template_dir
    items = report.items
    summary = (
        f"{len(items)} source-backed developments qualified for this coverage window."
    )
    if report.degraded:
        summary += " This report is degraded; review Source Health before operational use."

    lines = [
        f"# Blue Team Intelligence Digest — {report.coverage_end.date()}",
        "",
        "Coverage:",
        f"{report.coverage_start.isoformat()} → {report.coverage_end.isoformat()}",
        "",
        "Generated:",
        report.generated_at.isoformat(),
        "",
        "## Executive Summary",
        "",
        summary,
        "",
        "## 1. Immediate Attention",
        "",
    ]

    immediate = [item for item in items if item.cisa_kev]
    if immediate:
        lines.extend(
            f"- **{escape(item.canonical_id)}** — {escape(item.title)}. "
            f"Selected because: {escape(' + '.join(item.selection_reasons))}"
            for item in immediate[:10]
        )
    else:
        lines.append("No confirmed exploitation or new KEV entries qualified in this run.")

    lines.extend(
        [
            "",
            "## 2. Vulnerability Priorities",
            "",
            "| Priority | CVE/GHSA | Product | CVSS | EPSS | KEV | Reason |",
            "| --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    vulnerabilities = [item for item in items if item.category == "vulnerability"]
    if vulnerabilities:
        lines.extend(
            _vulnerability_row(priority, item)
            for priority, item in enumerate(vulnerabilities, 1)
        )
    else:
        lines.append("| — | — | — | — | — | — | No qualifying vulnerability items. |")

    ransomware_items = [item for item in items if item.known_ransomware_use]
    lines.extend(
        [
            "",
            "## 3. Threat and Ransomware Activity",
            "",
            "Only verified and source-backed activity is shown.",
        ]
    )
    if ransomware_items:
        lines.extend(f"- {escape(item.title)}" for item in ransomware_items)
    else:
        lines.append("No reliable ransomware-linked item qualified.")

    detection_items = [item for item in items if item.detection_opportunities]
    lines.extend(
        [
            "",
            "## 4. Detection Opportunities",
            "",
            "Analyst context generated from structured source fields.",
        ]
    )
    if detection_items:
        lines.extend(
            f"- **{escape(item.title)}**: "
            f"{escape(' '.join(item.detection_opportunities))}"
            for item in detection_items
        )
    else:
        lines.append("No detection-specific opportunities were derived.")

    advisories = [item for item in items if item.category == "advisory"]
    lines.extend(["", "## 5. Vendor and Government Advisories", ""])
    if advisories:
        lines.extend(
            f"- [{escape(item.title)}]({item.source_url}) — {escape(item.source_name)}"
            for item in advisories
        )
    else:
        lines.append("No official advisory feed entries qualified.")

    releases = [item for item in items if item.category == "tool_release"]
    lines.extend(["", "## 6. Blue Team Tools and Detection Content", ""])
    if releases:
        lines.extend(
            f"- [{escape(item.title)}]({item.source_url}) — "
            f"{escape(item.blue_team_relevance)}"
            for item in releases
        )
    else:
        lines.append("No allowlisted defensive project releases qualified.")

    lines.extend(["", "## 7. Analyst Queue", ""])
    if items:
        lines.extend(
            f"- Review {escape(item.canonical_id)} against asset inventory and "
            "vendor guidance."
            for item in items[:10]
        )
    else:
        lines.append("- No qualifying items; verify source health and coverage window.")

    lines.extend(
        [
            "",
            "## 8. Source Health",
            "",
            "| Source | Status | Items | Duration | Detail |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    lines.extend(
        f"| {health.source} | {health.status} | {health.items_accepted} | "
        f"{health.duration_ms} ms | "
        f"{escape(health.sanitized_error_message or '')} |"
        for health in report.source_health
    )

    lines.extend(
        [
            "",
            "## Methodology and Limitations",
            "",
            "Ranking assists prioritisation and does not replace asset-specific risk "
            "assessment. EPSS is a probability signal, not proof of exploitation. "
            "This product uses data from the NVD API but is not endorsed or certified "
            "by the NVD.",
        ]
    )

    text = "\n".join(lines) + "\n"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest.md").write_text(text, encoding="utf-8")

    report_date = report.coverage_end.date()
    archive_dir = output_dir / "archive" / f"{report_date:%Y}" / f"{report_date:%m}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / f"{report_date}.md").write_text(text, encoding="utf-8")
