import hashlib
from urllib.parse import urlsplit, urlunsplit

from .models import IntelligenceItem


LIST_FIELDS = [
    "cve_ids",
    "ghsa_ids",
    "vendors",
    "products",
    "affected_versions",
    "fixed_versions",
    "weaknesses",
    "ecosystems",
    "references",
    "recommended_actions",
    "detection_opportunities",
    "selection_reasons",
]
BOOLEAN_FIELDS = ["cisa_kev", "known_exploited", "known_ransomware_use"]
OPTIONAL_FIELDS = [
    "epss_score",
    "epss_percentile",
    "kev_date_added",
    "cvss_score",
    "cvss_version",
    "cvss_vector",
    "severity",
]


def normalize_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def correlation_key(item: IntelligenceItem) -> str:
    if item.cve_ids:
        return "cve:" + sorted(item.cve_ids)[0]
    if item.ghsa_ids:
        return "ghsa:" + sorted(item.ghsa_ids)[0]
    if item.source_url:
        return "url:" + normalize_url(item.source_url)
    fingerprint = hashlib.sha256(
        (item.title + item.source_name).encode()
    ).hexdigest()[:16]
    return "fp:" + fingerprint


def merge_items(items: list[IntelligenceItem]) -> list[IntelligenceItem]:
    merged: dict[str, IntelligenceItem] = {}

    for item in items:
        item_key = correlation_key(item)
        if item_key not in merged:
            merged[item_key] = item
            continue

        current = merged[item_key]
        for field_name in LIST_FIELDS:
            values = getattr(current, field_name) + getattr(item, field_name)
            setattr(current, field_name, sorted({value for value in values if value}))

        for field_name in BOOLEAN_FIELDS:
            if getattr(item, field_name) is True:
                setattr(current, field_name, True)
                current.add_provenance(field_name, item.source_name, True)

        for field_name in OPTIONAL_FIELDS:
            value = getattr(item, field_name)
            current_value = getattr(current, field_name)
            if current_value is None and value is not None:
                setattr(current, field_name, value)
                current.add_provenance(field_name, item.source_name, value)
            elif value is not None and value != current_value:
                current.add_provenance(field_name, item.source_name, value)

        for field_name, entries in item.provenance.items():
            current.provenance.setdefault(field_name, []).extend(entries)

    return sorted(merged.values(), key=lambda item: item.canonical_id)
