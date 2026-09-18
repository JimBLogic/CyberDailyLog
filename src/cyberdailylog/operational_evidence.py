"""Optional analyst-verified vendor statements; never infer exploitation from prose."""

from datetime import datetime
from urllib.parse import urlsplit
import re
from .models import IntelligenceItem, ensure_utc
from .settings import load_yaml


def load_operational_evidence(path):
    if not path.exists():
        return []
    result = []
    for row in load_yaml(path).get("observations", []):
        cve, url = row["cve"], row["source_url"]
        if not re.fullmatch(r"CVE-\d{4}-\d{4,}", cve) or urlsplit(url).scheme != "https" or not urlsplit(url).hostname:
            raise ValueError("Operational evidence requires a valid CVE and an HTTPS vendor advisory")
        if row.get("vendor_confirmed_exploitation") is not True:
            raise ValueError("Only explicitly verified positive vendor evidence is accepted")
        stamp = ensure_utc(datetime.fromisoformat(str(row["confirmed_at"]).replace("Z", "+00:00")))
        item = IntelligenceItem(
            canonical_id=cve,
            title=f"{cve}: vendor-confirmed exploitation",
            source_name="Verified vendor: " + urlsplit(url).hostname,
            source_type="vendor_evidence",
            source_url=url,
            cve_ids=[cve],
            published_at=stamp,
            modified_at=stamp,
            vendor_confirmed_exploitation=True,
            known_exploited=True,
            exploitation_status="confirmed_exploitation",
            recommended_actions=[row["required_action"]] if row.get("required_action") else [],
            summary=str(row.get("evidence", "")),
            references=[url],
            confidence="high",
        )
        item.add_provenance("vendor_confirmed_exploitation", url, True)
        result.append(item)
    return result
