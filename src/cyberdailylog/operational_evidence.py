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

    # A verified vendor remediation correction is not equivalent to vendor-
    # confirmed exploitation. Track it separately so the ledger emits a
    # material remediation transition without manufacturing exploit evidence.
    for row in load_yaml(path).get("remediation_updates", []):
        cve, url = row["cve"], row["source_url"]
        parsed = urlsplit(url)
        if not re.fullmatch(r"CVE-\d{4}-\d{4,}", cve) or parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("Vendor remediation requires a CVE and HTTPS primary-source advisory")
        versions = row.get("fixed_versions")
        if (
            not isinstance(versions, list)
            or not versions
            or any(
                not isinstance(version, str)
                or not 1 <= len(version) <= 100
                or any(ord(char) < 32 for char in version)
                for version in versions
            )
        ):
            raise ValueError("Vendor remediation requires explicitly confirmed fixed versions")
        action = row.get("required_action")
        if not isinstance(action, str) or not action.strip():
            raise ValueError("Vendor remediation requires an explicit analyst-verified action")
        stamp = ensure_utc(datetime.fromisoformat(str(row["confirmed_at"]).replace("Z", "+00:00")))
        item = IntelligenceItem(
            canonical_id=cve,
            title=f"{cve}: vendor remediation correction",
            source_name="Vendor remediation: " + parsed.hostname,
            source_type="vendor_evidence",
            source_url=url,
            cve_ids=[cve],
            # Confirmation date is not the original CVE disclosure date.
            published_at=None,
            modified_at=stamp,
            fixed_versions=sorted(set(versions)),
            recommended_actions=[action.strip()],
            summary=str(row.get("evidence", "")),
            references=[url],
            confidence="high",
        )
        item.add_provenance("fixed_versions", url, item.fixed_versions)
        result.append(item)
    return result
