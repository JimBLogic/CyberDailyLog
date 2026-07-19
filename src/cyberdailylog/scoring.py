from datetime import datetime

from .models import IntelligenceItem


SEVERITY_BASE = {
    "critical": 9.5,
    "high": 8.0,
    "medium": 5.5,
    "moderate": 5.5,
    "low": 3.0,
}


def _priority_technology(item: IntelligenceItem, technologies: dict) -> str | None:
    text = " ".join(item.products + item.vendors + item.ecosystems + [item.title, item.summary]).lower()
    for category, words in technologies.get("priority_terms", {}).items():
        if any(str(word).lower() in text for word in words):
            return str(category)
    return None


def compute_priority_score(item: IntelligenceItem, technologies: dict) -> tuple[float, list[str]]:
    if item.withdrawn:
        return 0.0, ["withdrawn advisory"]

    if item.cvss_score is not None:
        score = float(item.cvss_score)
        reasons = [f"CVSS {item.cvss_score:.1f}"]
    else:
        severity = str(item.severity or "unknown").lower()
        score = SEVERITY_BASE.get(severity, 0.0)
        reasons = [f"{severity} severity fallback"] if score else ["no severity score"]

    if item.epss_score is not None:
        if item.epss_score >= 0.70:
            score += 1.0
            reasons.append("EPSS >= 70%")
        elif item.epss_score >= 0.30:
            score += 0.5
            reasons.append("EPSS >= 30%")

    if item.epss_percentile is not None and item.epss_percentile >= 0.95:
        score += 0.5
        reasons.append("EPSS percentile >= 95%")

    technology = _priority_technology(item, technologies)
    if technology:
        score += 0.5
        reasons.append(f"priority technology: {technology}")

    if item.detection_opportunities:
        score += 0.25
        reasons.append("detection opportunity")

    if item.modified_at and item.published_at and item.modified_at != item.published_at and not item.cisa_kev:
        score -= 1.0
        reasons.append("metadata-only update")

    floor = 0.0
    if item.cisa_kev:
        floor = 10.0
        reasons.append("CISA KEV")
    elif item.known_exploited:
        floor = 9.5
        reasons.append("confirmed exploitation")
    elif item.known_ransomware_use:
        floor = 9.0
        reasons.append("known ransomware use")

    score = max(score, floor)
    return round(max(0.0, min(10.0, score)), 1), reasons


def score_item(
    item: IntelligenceItem, scoring: dict, technologies: dict, since: datetime, until: datetime
) -> IntelligenceItem | None:
    if item.withdrawn:
        item.selection_reasons.append("Withdrawn advisory retained for transparency but excluded from priority scoring")
        item.priority_score, item.priority_reasons = compute_priority_score(item, technologies)
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
    technology = _priority_technology(item, technologies)
    if technology:
        add("priority_technology", f"priority technology: {technology}")
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
            "Inventory affected products, verify exposure and follow the vendor remediation or mitigation guidance."
        ]
    item.priority_score, item.priority_reasons = compute_priority_score(item, technologies)
    return item


def score_items(items, scoring, technologies, since, until):
    out = [x for i in items if (x := score_item(i, scoring, technologies, since, until))]
    return sorted(
        out,
        key=lambda i: (i.priority_score, i.selection_score, i.cisa_kev is True, i.canonical_id),
        reverse=True,
    )
