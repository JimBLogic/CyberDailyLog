from __future__ import annotations

import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from cyberdailylog.models import IntelligenceItem, Report


DEFAULT_CURATION = {
    "minimum_priority": 5.0,
    "max_immediate_attention": 5,
    "max_priority_vulnerabilities": 10,
    "max_official_advisories": 3,
    "max_human_context": 1,
    "max_community_pulse": 1,
    "max_defensive_releases": 3,
    "max_analyst_actions": 5,
    "max_total_unique_items": 15,
    "max_markdown_lines": 140,
    "max_markdown_bytes": 12288,
    "title_max_characters": 110,
    "reason_max_characters": 160,
    "excerpt_max_words": 24,
    "excerpt_max_characters": 240,
}


def _validated_curation(config: dict[str, Any] | None) -> dict[str, float | int]:
    raw = (config or {}).get("curation", {})
    values: dict[str, float | int] = dict(DEFAULT_CURATION)
    if isinstance(raw, dict):
        values.update(raw)

    minimum = float(values["minimum_priority"])
    if not 0.0 <= minimum <= 10.0:
        raise ValueError("curation.minimum_priority must be between 0 and 10")
    values["minimum_priority"] = minimum

    for key in DEFAULT_CURATION:
        if key == "minimum_priority":
            continue
        value = int(values[key])
        if value <= 0:
            raise ValueError(f"curation.{key} must be a positive integer")
        values[key] = value
    return values


def _truncate(value: str, limit: int) -> str:
    clean = " ".join(value.split())
    if len(clean) <= limit:
        return clean
    shortened = clean[: max(1, limit - 1)].rsplit(" ", 1)[0]
    return f"{shortened or clean[: max(1, limit - 1)]}…"


def _md_text(value: str) -> str:
    return escape(" ".join(value.split())).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _table_cell(value: str) -> str:
    return _md_text(value).replace("|", "\\|")


def _identifier(item: IntelligenceItem) -> str:
    identifiers = item.cve_ids + item.ghsa_ids
    return ", ".join(identifiers) if identifiers else item.canonical_id


def _qualifies(item: IntelligenceItem, minimum: float) -> bool:
    return bool(item.priority_score >= minimum or item.cisa_kev or item.known_exploited or item.known_ransomware_use)


def _why(item: IntelligenceItem, limit: int) -> str:
    reasons = item.priority_reasons or item.selection_reasons
    return _truncate("; ".join(reasons[:2]) or "source-backed defensive relevance", limit)


def _action(item: IntelligenceItem, limit: int) -> str:
    candidates = item.recommended_actions or item.detection_opportunities
    if candidates:
        return _truncate(candidates[0], limit)
    subject = ", ".join(item.products[:2]) or _identifier(item)
    return _truncate(f"Check {subject} against the asset inventory and apply vendor mitigation guidance.", limit)


def _take_unique(
    candidates: list[IntelligenceItem],
    limit: int,
    used: set[str],
    total_limit: int,
) -> list[IntelligenceItem]:
    chosen: list[IntelligenceItem] = []
    for item in candidates:
        if item.canonical_id in used:
            continue
        if len(used) >= total_limit or len(chosen) >= limit:
            break
        chosen.append(item)
        used.add(item.canonical_id)
    return chosen


def _published_sort(item: IntelligenceItem) -> datetime:
    return item.published_at or datetime.min.replace(tzinfo=timezone.utc)


def _human_candidates(report: Report) -> list[IntelligenceItem]:
    return sorted(
        [item for item in report.items if item.category in {"expert_commentary", "analyst_diary"}],
        key=lambda item: (_published_sort(item), item.source_name, item.canonical_id),
        reverse=True,
    )


def _community_candidates(report: Report) -> list[IntelligenceItem]:
    return sorted(
        [item for item in report.items if item.category == "community_pulse"],
        key=lambda item: (
            item.community_score or 0,
            item.community_comments or 0,
            _published_sort(item),
            item.canonical_id,
        ),
        reverse=True,
    )


def _excerpt(item: IntelligenceItem, max_words: int, max_characters: int) -> str:
    words = " ".join(item.summary.split()).split()
    text = " ".join(words[:max_words])
    if len(words) > max_words:
        text += "…"
    return _truncate(text, max_characters) if text else ""


def _health_summary(report: Report) -> str:
    core = [health for health in report.source_health if health.required]
    optional = [health for health in report.source_health if not health.required]
    core_healthy = sum(health.status in {"healthy", "fixture_only"} for health in core)
    optional_healthy = sum(health.status in {"healthy", "fixture_only"} for health in optional)
    optional_degraded = sum(health.status in {"degraded", "failed"} for health in optional)
    return (
        f"Core sources: **{core_healthy}/{len(core)} healthy**. "
        f"Optional sources: **{optional_healthy} healthy**, **{optional_degraded} degraded**."
    )


def render_markdown(report: Report, config: dict[str, Any] | None = None) -> str:
    curation = _validated_curation(config)
    minimum = float(curation["minimum_priority"])
    total_limit = int(curation["max_total_unique_items"])
    title_limit = int(curation["title_max_characters"])
    reason_limit = int(curation["reason_max_characters"])

    used: set[str] = set()
    immediate = _take_unique(
        [item for item in report.items if item.cisa_kev or item.known_exploited or item.known_ransomware_use],
        int(curation["max_immediate_attention"]),
        used,
        total_limit,
    )
    human_context = _take_unique(
        _human_candidates(report),
        int(curation["max_human_context"]),
        used,
        total_limit,
    )
    community_pulse = _take_unique(
        _community_candidates(report),
        int(curation["max_community_pulse"]),
        used,
        total_limit,
    )
    vulnerabilities = _take_unique(
        [item for item in report.items if item.category == "vulnerability" and _qualifies(item, minimum)],
        int(curation["max_priority_vulnerabilities"]),
        used,
        total_limit,
    )
    advisories = _take_unique(
        [item for item in report.items if item.category == "advisory" and _qualifies(item, minimum)],
        int(curation["max_official_advisories"]),
        used,
        total_limit,
    )
    releases = _take_unique(
        [item for item in report.items if item.category == "tool_release"],
        int(curation["max_defensive_releases"]),
        used,
        total_limit,
    )
    displayed = immediate + human_context + community_pulse + vulnerabilities + advisories + releases
    actionable = immediate + vulnerabilities + advisories + releases
    above_threshold = sum(_qualifies(item, minimum) for item in report.items)

    lines = [
        f"# CyberDailyLog — Daily Blue Team Brief · {report.coverage_end.date()}",
        "",
        "> Automated, source-backed defensive intelligence for the previous 24 hours.",
        "",
        f"**Updated:** {report.generated_at.isoformat()}  ",
        f"**Coverage:** {report.coverage_start.isoformat()} → {report.coverage_end.isoformat()}  ",
        f"**Status:** {'Degraded — inspect source health' if report.degraded else 'Operational'}",
        "",
        "[Full JSON](latest.json) · [Compact feed](portfolio-feed.json) · "
        "[Source health](source-health.json) · [Archive](archive/)",
        "",
        "## Today in 30 seconds",
        "",
        f"- **{len(report.items)}** source-backed developments assessed.",
        f"- **{above_threshold}** met the editorial threshold of **{minimum:.1f}/10** or an exploitation override.",
        f"- **{len(displayed)}** unique items are displayed after curation.",
        f"- {_health_summary(report)}",
        "",
        "## Immediate attention",
        "",
    ]

    if immediate:
        for item in immediate:
            title = _md_text(_truncate(item.title, title_limit))
            link = item.source_url or "#"
            lines.append(
                f"- **[{_md_text(_identifier(item))}]({link}) · {item.priority_score:.1f}/10** — "
                f"{title}. **Action:** {_md_text(_action(item, reason_limit))}"
            )
    else:
        lines.append("No confirmed exploitation, CISA KEV or ransomware-linked item qualified in this run.")

    lines += [
        "",
        f"## Priority vulnerabilities — {minimum:.1f}/10 or higher",
        "",
        "| Threat | Priority | CVSS | EPSS | Signal | Why it matters |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    if vulnerabilities:
        for item in vulnerabilities:
            title = _truncate(item.title, title_limit)
            label = f"{_identifier(item)} — {title}"
            epss = f"{item.epss_score:.1%}" if item.epss_score is not None else "n/a"
            cvss = f"{item.cvss_score:.1f}" if item.cvss_score is not None else "n/a"
            if item.cisa_kev:
                signal = "KEV"
            elif item.known_exploited:
                signal = "Exploited"
            elif item.known_ransomware_use:
                signal = "Ransomware"
            else:
                signal = "—"
            lines.append(
                f"| [{_table_cell(label)}]({item.source_url or '#'}) | {item.priority_score:.1f} | "
                f"{cvss} | {epss} | {signal} | {_table_cell(_why(item, reason_limit))} |"
            )
    else:
        lines.append("| No qualifying vulnerability items. | — | — | — | — | — |")

    lines += ["", "## Human context", ""]
    if human_context:
        item = human_context[0]
        byline = " · ".join(part for part in [item.author, item.source_name] if part)
        lines.extend(
            [
                f"### [{_md_text(_truncate(item.title, title_limit))}]({item.source_url or '#'})",
                "",
                f"**{_md_text(byline or item.source_name)}**",
                "",
            ]
        )
        excerpt = _excerpt(
            item,
            int(curation["excerpt_max_words"]),
            int(curation["excerpt_max_characters"]),
        )
        if excerpt:
            lines.append(f"> {_md_text(excerpt)}")
            lines.append("")
            lines.append("_Publisher-provided RSS excerpt; open the original article for full context._")
        else:
            lines.append("No publisher excerpt was supplied; open the original article for context.")
    else:
        lines.append("No recent expert or analyst commentary qualified in this coverage window.")

    lines += ["", "## Community pulse", ""]
    if community_pulse:
        item = community_pulse[0]
        metrics = f"{item.community_score or 0} points · {item.community_comments or 0} comments"
        lines.append(f"- **[{_md_text(_truncate(item.title, title_limit))}]({item.source_url or '#'})**")
        discussion = item.discussion_url or item.source_url or "#"
        lines.append(f"  Hacker News · {metrics} · [Open discussion]({discussion})")
        lines.append("  _Community interest signal only; validate claims against primary sources._")
    else:
        lines.append("No security-focused Hacker News discussion met the engagement threshold.")

    lines += ["", "## Notable official advisories", ""]
    if advisories:
        lines.extend(
            f"- [{_md_text(_truncate(item.title, title_limit))}]({item.source_url}) — "
            f"{_md_text(_why(item, reason_limit))}"
            for item in advisories
        )
    else:
        lines.append("No additional official advisory qualified after de-duplication.")

    lines += ["", "## Defensive tooling and detection content", ""]
    if releases:
        lines.extend(
            f"- [{_md_text(_truncate(item.title, title_limit))}]({item.source_url})"
            + (
                f" — {_md_text(_truncate(item.blue_team_relevance, reason_limit))}"
                if item.blue_team_relevance
                else ""
            )
            for item in releases
        )
    else:
        lines.append("No allowlisted defensive release qualified in this coverage window.")

    lines += ["", "## Analyst next actions", ""]
    for item in actionable[: int(curation["max_analyst_actions"])]:
        lines.append(f"- **{_md_text(_identifier(item))}:** {_md_text(_action(item, reason_limit))}")
    if not actionable:
        lines.append("- Confirm source health and reassess when new evidence is available.")

    lines += [
        "",
        "## Source health",
        "",
        _health_summary(report),
        "",
        "<details>",
        "<summary>Collector details</summary>",
        "",
        "| Source | Required | Status | Accepted | Duration | Detail |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    lines.extend(
        f"| {_table_cell(health.source)} | {'yes' if health.required else 'no'} | "
        f"{_table_cell(health.status)} | {health.items_accepted} | {health.duration_ms} ms | "
        f"{_table_cell(health.sanitized_error_message or '')} |"
        for health in report.source_health
    )
    lines += [
        "",
        "</details>",
        "",
        "<details>",
        "<summary>Methodology and limitations</summary>",
        "",
        "The 0–10 priority score is an editorial triage aid, not asset-specific risk. "
        "EPSS is probabilistic, and source-backed findings still require asset, exposure and vendor validation. "
        "Expert RSS excerpts and Hacker News engagement are contextual signals, not verified threat evidence.",
        "",
        "</details>",
    ]

    text = "\n".join(lines) + "\n"
    if len(lines) > int(curation["max_markdown_lines"]):
        raise ValueError("curated Markdown exceeds configured line limit")
    if len(text.encode("utf-8")) > int(curation["max_markdown_bytes"]):
        raise ValueError("curated Markdown exceeds configured byte limit")
    return text


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _archive_previous_latest(out: Path, incoming_date) -> None:
    latest = out / "latest.md"
    if not latest.exists():
        return
    existing = latest.read_text(encoding="utf-8")
    match = re.search(r"(\d{4}-\d{2}-\d{2})", existing.splitlines()[0] if existing else "")
    if not match:
        raise ValueError("existing latest.md does not expose a coverage date")
    previous_date = match.group(1)
    if previous_date == str(incoming_date):
        return
    archive = out / "archive" / previous_date[:4] / previous_date[5:7] / f"{previous_date}.md"
    if archive.exists() and archive.read_text(encoding="utf-8") != existing:
        raise ValueError(f"historical Markdown archive conflict for {previous_date}")
    if not archive.exists():
        _atomic_write(archive, existing)


def write_markdown(
    report: Report,
    out: Path,
    config: dict[str, Any] | None = None,
    template_dir: Path = Path("templates"),
):
    del template_dir
    text = render_markdown(report, config)
    out.mkdir(parents=True, exist_ok=True)
    date = report.coverage_end.date()
    _archive_previous_latest(out, date)
    archive = out / "archive" / f"{date:%Y}" / f"{date:%m}" / f"{date}.md"
    _atomic_write(archive, text)
    _atomic_write(out / "latest.md", text)
