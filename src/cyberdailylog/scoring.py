from datetime import datetime
from .models import IntelligenceItem


def score_item(
    item: IntelligenceItem, scoring: dict, technologies: dict, since: datetime, until: datetime
) -> IntelligenceItem | None:
    if item.withdrawn:
        item.selection_reasons.append("Withdrawn advisory retained for transparency but excluded from priority scoring")
        return item
    relevant = (
        (item.published_at and since <= item.published_at <= until)
        or (item.modified_at and since <= item.modified_at <= until)
        or item.cisa_kev
    )
    if not relevant:
        return None
    score = 0
    reasons = []
    w = scoring.get("weights", {})

    def add(k, txt):
        nonlocal score
        val = int(w.get(k, 0))
        score += val
        reasons.append(f"{txt} +{val}")

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
    for cat, words in technologies.get("priority_terms", {}).items():
        if any(str(x).lower() in text for x in words):
            add("priority_technology", f"priority technology: {cat}")
            break
    if item.official_source:
        add("official_primary_source", "official source")
    if item.detection_opportunities:
        add("detection_opportunity", "defensive detection opportunity")
    if item.modified_at and item.published_at and item.modified_at != item.published_at and not item.cisa_kev:
        score += int(w.get("metadata_only_modified", -5))
        reasons.append("modified metadata in window -5")
    item.selection_score = score
    item.selection_reasons = reasons or ["Included as source-backed advisory in coverage window"]
    if not item.detection_opportunities and item.category == "vulnerability":
        item.detection_opportunities = [
            "Analyst context generated from structured source fields: inventory affected products, review exposure, authentication and network telemetry where applicable, and follow vendor guidance."
        ]
    return item


def score_items(items, scoring, technologies, since, until):
    out = [x for i in items if (x := score_item(i, scoring, technologies, since, until))]
    return sorted(out, key=lambda i: (i.selection_score, i.cisa_kev is True, i.canonical_id), reverse=True)
