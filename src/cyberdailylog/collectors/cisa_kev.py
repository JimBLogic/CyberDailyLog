from datetime import datetime, timezone

from cyberdailylog.models import IntelligenceItem

from .base import BaseCollector


class CisaKevCollector(BaseCollector):
    name = "cisa_kev"
    required = True
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

    def collect(self, since: datetime, until: datetime):
        started = datetime.now(timezone.utc)
        try:
            if self.offline:
                data = self.fixture_json("cisa_kev.json")
            else:
                data = self.http.get(self.url, expect_json=True).json()

            items = []
            vulnerabilities = data.get("vulnerabilities", [])
            for vulnerability in vulnerabilities:
                date_added = datetime.fromisoformat(
                    vulnerability.get("dateAdded", "1970-01-01")
                ).replace(tzinfo=timezone.utc)
                if not since <= date_added <= until:
                    continue

                cve_id = vulnerability["cveID"]
                title = (
                    f"{cve_id} exploited in CISA KEV: "
                    f"{vulnerability.get('vendorProject', '')} "
                    f"{vulnerability.get('product', '')}"
                ).strip()
                item = IntelligenceItem(
                    canonical_id=cve_id,
                    title=title,
                    summary=vulnerability.get("shortDescription", ""),
                    category="vulnerability",
                    source_name="CISA Known Exploited Vulnerabilities",
                    source_type="government_kev",
                    source_tier=1,
                    source_url=self.url,
                    published_at=date_added,
                    modified_at=date_added,
                    cve_ids=[cve_id],
                    vendors=[vulnerability.get("vendorProject", "")],
                    products=[vulnerability.get("product", "")],
                    cisa_kev=True,
                    kev_date_added=date_added,
                    known_exploited=True,
                    known_ransomware_use=(
                        vulnerability.get("knownRansomwareCampaignUse") == "Known"
                    ),
                    exploitation_status="confirmed_exploitation",
                    recommended_actions=[vulnerability.get("requiredAction", "")],
                    references=[vulnerability.get("notes", "") or self.url],
                    confidence="high",
                )
                item.add_provenance("known_exploited", "CISA KEV", True)
                items.append(item)

            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy",
                started,
                len(vulnerabilities),
                len(items),
            )
        except Exception as exc:
            return [], self.timed_health("failed", started, err=exc)
