from datetime import datetime
from typing import Any

from .models import IntelligenceItem


def score_item(
    item: IntelligenceItem,
    scoring: dict[str, Any],
    technologies: dict[str, Any],
    since: datetime,
    until: datetime,
) -> IntelligenceItem | None:
    if item.withdrawn:
        item.selection_reasons.append(
            "Withdrawn advisory retained for transparency but excluded from priority scoring"
        )
        return item

    relevant = bool(
        (item.published_at and since <= item.published_at <= until)
        or (item.modified_at and since <= item.modified_at <= until)
        or item.cisa_kev
    )
    if not relevant:
        return None

    score = 0
    reasons: list[str] = []
    weights = scoring.get("weights", {})

    def add(weight_key: str, explanation: str) -> None:
        nonlocal score
        value = int(weights.get(weight_key, 0))
        score += value
        reasons.append(f"{explanation} +{value}")

    if item.cisa_kev:
        add("cisa_kev", "CISA KEV")
    if item.known_exploited:
        add("confirmed_exploitation", "confirmed exploitation")
    if item.known_ransomware_use:
        add("known_ransomware_use", "known ransomware use")

    if item.cvss_score is not None:
        if item.cvss_score >= 9:
            add("cvss_critical", "critical CVSS")
        elif item.cvss_score >= 7:
            add("cvss_high", "high CVSS")

    if item.epss_score is not None:
        if item.epss_score >= 0.70:
            add("epss_very_high", "EPSS >= 0.70")
        elif item.epss_score >= 0.30:
            add("epss_high", "EPSS >= 0.30")

    if item.epss_percentile is not None and item.epss_percentile >= 0.95:
        add("epss_percentile_high", "EPSS percentile >= 0.95")

    text = " ".join(item.products + item.vendors + [item.title, item.summary]).lower()
    for category, words in technologies.get("priority_terms", {}).items():
        if any(str(word).lower() in text for word in words):
            add("priority_technology", f"priority technology: {category}")
            break

    if item.official_source:
        add("official_primary_source", "official source")
    if item.detection_opportunities:
        add("detection_opportunity", "defensive detection opportunity")

    metadata_only = (
        item.modified_at
        and item.published_at
        and item.modified_at != item.published_at
        and not item.cisa_kev
    )
    if metadata_only:
        score += int(weights.get("metadata_only_modified", -5))
        reasons.append("modified metadata in window -5")

    item.selection_score = score
    item.selection_reasons = reasons or [
        "Included as source-backed advisory in coverage window"
    ]
    if not item.detection_opportunities and item.category == "vulnerability":
        item.detection_opportunities = [
            "Analyst context generated from structured source fields: inventory "
            "affected products, review exposure, authentication and network telemetry "
            "where applicable, and follow vendor guidance."
        ]
    return item


def score_items(
    items: list[IntelligenceItem],
    scoring: dict[str, Any],
    technologies: dict[str, Any],
    since: datetime,
    until: datetime,
) -> list[IntelligenceItem]:
    scored = []
    for item in items:
        result = score_item(item, scoring, technologies, since, until)
        if result is not None:
            scored.append(result)
    return sorted(
        scored,
        key=lambda item: (
            item.selection_score,
            item.cisa_kev is True,
            item.canonical_id,
        ),
        reverse=True,
    )
