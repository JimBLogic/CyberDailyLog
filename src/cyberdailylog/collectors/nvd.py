from datetime import datetime, timezone
from typing import Any
import time

from .base import BaseCollector
from cyberdailylog.models import IntelligenceItem
from cyberdailylog.exceptions import SourceError


def extract_reference_urls(references: Any) -> list[str]:
    if isinstance(references, dict):
        raw_refs = references.get("referenceData", [])
    else:
        raw_refs = references
    if not isinstance(raw_refs, list):
        return []
    urls: list[str] = []
    seen: set[str] = set()
    for ref in raw_refs:
        if not isinstance(ref, dict):
            continue
        url = ref.get("url")
        if not isinstance(url, str):
            continue
        url = url.strip()
        if not url or url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


class NvdCollector(BaseCollector):
    name = "nvd"
    required = True
    endpoint = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def _parse_dt(self, v):
        parsed = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)

    def _item(self, obj):
        cve = obj["cve"]
        cid = cve["id"]
        metrics = cve.get("metrics", {})
        cvss = None
        ver = None
        vec = None
        sev = None
        for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30"):
            if key in metrics:
                m = metrics[key][0]
                d = m.get("cvssData", {})
                cvss = d.get("baseScore")
                ver = d.get("version")
                vec = d.get("vectorString")
                sev = m.get("baseSeverity") or d.get("baseSeverity")
                break
        desc = next((d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"), "")
        refs = extract_reference_urls(cve.get("references"))
        item = IntelligenceItem(
            canonical_id=cid,
            title=f"{cid}: {desc[:120]}",
            summary=desc,
            category="vulnerability",
            source_name="NVD CVE API 2.0",
            source_type="vulnerability_database",
            source_tier=1,
            source_url=f"https://nvd.nist.gov/vuln/detail/{cid}",
            published_at=self._parse_dt(cve["published"]),
            modified_at=self._parse_dt(cve["lastModified"]),
            cve_ids=[cid],
            cvss_version=ver,
            cvss_score=cvss,
            cvss_vector=vec,
            severity=sev,
            references=refs,
            public_exploit=True
            if any(isinstance(ref, dict) and "Exploit" in ref.get("tags", []) for ref in (cve.get("references") or []))
            else None,
            confidence="medium",
        )
        item.add_provenance("cvss_score", "NVD", cvss)
        return item

    def collect(self, since, until):
        started = datetime.now(timezone.utc)
        try:
            if self.offline:
                data = self.fixture_json("nvd_page1.json")
                pages = [data, self.fixture_json("nvd_page2.json")]
            else:
                headers = {"apiKey": self.token} if self.token else {}
                params = {
                    "lastModStartDate": since.strftime("%Y-%m-%dT%H:%M:%S.000"),
                    "lastModEndDate": until.strftime("%Y-%m-%dT%H:%M:%S.000"),
                    # Modified CVEs can contain large CPE trees. Stay within
                    # the HTTP client's byte bound without discarding a page.
                    "resultsPerPage": 500,
                    "startIndex": 0,
                }
                pages = []
                requested = False
                while True:
                    if requested:
                        time.sleep(0.6 if self.token else 6.0)
                    requested = True
                    try:
                        data = self.http.get(self.endpoint, headers=headers, params=params, expect_json=True).json()
                    except SourceError as error:
                        if str(error) != "Response too large" or params["resultsPerPage"] == 1:
                            raise
                        params["resultsPerPage"] = max(1, params["resultsPerPage"] // 2)
                        continue
                    pages.append(data)
                    if params["startIndex"] + data.get("resultsPerPage", 0) >= data.get("totalResults", 0):
                        break
                    if data.get("resultsPerPage", 0) <= 0:
                        raise ValueError("NVD pagination made no progress")
                    params["startIndex"] += data.get("resultsPerPage", 0)
            items = []
            received = 0
            rejected = 0
            for data in pages:
                for obj in data.get("vulnerabilities", []):
                    received += 1
                    if obj["cve"].get("vulnStatus") == "Rejected":
                        rejected += 1
                        continue
                    items.append(self._item(obj))
            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy", started, received, len(items), rejected
            )
        except Exception as e:
            return [], self.timed_health("failed", started, err=e)
