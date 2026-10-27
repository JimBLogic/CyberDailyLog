from datetime import datetime, timezone
import re
from urllib.parse import urlsplit
from .base import BaseCollector
from cyberdailylog.models import IntelligenceItem


def reference_urls(notes, fallback):
    urls = []
    for match in re.findall(r"https?://[^\s<>\"']+", str(notes or "")):
        url = match.rstrip(";,. )")
        try:
            parsed = urlsplit(url)
            if parsed.hostname and not parsed.username and not parsed.password and url not in urls:
                urls.append(url)
        except ValueError:
            continue
    return urls or [fallback]


class CisaKevCollector(BaseCollector):
    name = "cisa_kev"
    required = True
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

    def collect(self, since, until):
        started = datetime.now(timezone.utc)
        try:
            data = (
                self.fixture_json("cisa_kev.json") if self.offline else self.http.get(self.url, expect_json=True).json()
            )
            if not isinstance(data.get("vulnerabilities"), list) or not data["vulnerabilities"]:
                raise ValueError("CISA full catalog is empty or malformed")
            if data.get("count") is not None and data["count"] != len(data["vulnerabilities"]):
                raise ValueError("CISA catalog count mismatch")
            items = []
            for v in data.get("vulnerabilities", []):
                date = datetime.fromisoformat(v.get("dateAdded", "1970-01-01")).replace(tzinfo=timezone.utc)
                cve = v["cveID"]
                title = f"{cve} exploited in CISA KEV: {v.get('vendorProject', '')} {v.get('product', '')}".strip()
                item = IntelligenceItem(
                    canonical_id=cve,
                    title=title,
                    summary=v.get("shortDescription", ""),
                    category="vulnerability",
                    source_name="CISA Known Exploited Vulnerabilities",
                    source_type="government_kev",
                    source_tier=1,
                    source_url=self.url,
                    published_at=date,
                    modified_at=date,
                    cve_ids=[cve],
                    vendors=[v.get("vendorProject", "")],
                    products=[v.get("product", "")],
                    cisa_kev=True,
                    kev_date_added=date,
                    known_exploited=True,
                    known_ransomware_use=True if v.get("knownRansomwareCampaignUse") == "Known" else None,
                    cisa_required_action=v.get("requiredAction") or None,
                    cisa_due_date=datetime.fromisoformat(v["dueDate"]).replace(tzinfo=timezone.utc)
                    if v.get("dueDate")
                    else None,
                    exploitation_status="confirmed_exploitation",
                    recommended_actions=[v.get("requiredAction", "")],
                    references=reference_urls(v.get("notes"), self.url),
                    confidence="high",
                )
                item.add_provenance("known_exploited", "CISA KEV", True)
                items.append(item)
            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy", started, len(data.get("vulnerabilities", [])), len(items)
            )
        except Exception as e:
            return [], self.timed_health("failed", started, err=e)
