from pathlib import Path
from html import escape


def write_markdown(report, out: Path, template_dir: Path = Path("templates")):
    items = report.items
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
        f"{len(items)} source-backed developments qualified for this coverage window."
        + (" This report is degraded; review Source Health before operational use." if report.degraded else ""),
        "",
        "## 1. Immediate Attention",
        "",
    ]
    imm = [i for i in items if i.cisa_kev]
    lines += [
        f"- **{escape(i.canonical_id)}** — {escape(i.title)}. Selected because: {escape(' + '.join(i.selection_reasons))}"
        for i in imm[:10]
    ] or ["No confirmed exploitation or new KEV entries qualified in this run."]
    lines += [
        "",
        "## 2. Vulnerability Priorities",
        "",
        "| Priority | CVE/GHSA | Product | CVSS | EPSS | KEV | Reason |",
        "| --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    vul = [i for i in items if i.category == "vulnerability"]
    if vul:
        for n, i in enumerate(vul, 1):
            lines.append(
                f"| {n} | {escape(', '.join(i.cve_ids + i.ghsa_ids))} | {escape(', '.join(i.products))} | {i.cvss_score if i.cvss_score is not None else 'n/a'} | {i.epss_score if i.epss_score is not None else 'n/a'} | {'yes' if i.cisa_kev else 'no'} | {escape('; '.join(i.selection_reasons))} |"
            )
    else:
        lines.append("| — | — | — | — | — | — | No qualifying vulnerability items. |")
    lines += ["", "## 3. Threat and Ransomware Activity", "", "Only verified and source-backed activity is shown."] + (
        [f"- {escape(i.title)}" for i in items if i.known_ransomware_use]
        or ["No reliable ransomware-linked item qualified."]
    )
    lines += ["", "## 4. Detection Opportunities", "", "Analyst context generated from structured source fields."] + (
        [
            f"- **{escape(i.title)}**: {escape(' '.join(i.detection_opportunities))}"
            for i in items
            if i.detection_opportunities
        ]
        or ["No detection-specific opportunities were derived."]
    )
    lines += ["", "## 5. Vendor and Government Advisories", ""] + (
        [f"- [{escape(i.title)}]({i.source_url}) — {escape(i.source_name)}" for i in items if i.category == "advisory"]
        or ["No official advisory feed entries qualified."]
    )
    lines += ["", "## 6. Blue Team Tools and Detection Content", ""] + (
        [
            f"- [{escape(i.title)}]({i.source_url}) — {escape(i.blue_team_relevance)}"
            for i in items
            if i.category == "tool_release"
        ]
        or ["No allowlisted defensive project releases qualified."]
    )
    lines += ["", "## 7. Analyst Queue", ""] + (
        [f"- Review {escape(i.canonical_id)} against asset inventory and vendor guidance." for i in items[:10]]
        or ["- No qualifying items; verify source health and coverage window."]
    )
    lines += [
        "",
        "## 8. Source Health",
        "",
        "| Source | Status | Items | Duration | Detail |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    lines += [
        f"| {h.source} | {h.status} | {h.items_accepted} | {h.duration_ms} ms | {escape(h.sanitized_error_message or '')} |"
        for h in report.source_health
    ]
    lines += [
        "",
        "## Methodology and Limitations",
        "",
        "Ranking assists prioritisation and does not replace asset-specific risk assessment. EPSS is a probability signal, not proof of exploitation. This product uses data from the NVD API but is not endorsed or certified by the NVD.",
    ]
    text = "\n".join(lines) + "\n"
    out.mkdir(parents=True, exist_ok=True)
    (out / "latest.md").write_text(text, encoding="utf-8")
    d = report.coverage_end.date()
    ad = out / "archive" / f"{d:%Y}" / f"{d:%m}"
    ad.mkdir(parents=True, exist_ok=True)
    (ad / f"{d}.md").write_text(text, encoding="utf-8")
