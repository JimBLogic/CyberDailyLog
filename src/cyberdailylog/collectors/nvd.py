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
        self.metrics = {"requests": 0, "pages": 0, "page_size_reductions": 0, "response_bytes": 0, "wait_seconds": 0.0}
        try:
            if self.offline:
                pages = (self.fixture_json(name) for name in ("nvd_page1.json", "nvd_page2.json"))
            else:
                pages = self._pages(since, until)
            items = []
            received = 0
            rejected = 0
            seen = set()
            for data in pages:
                self.metrics["pages"] += 1
                for obj in data["vulnerabilities"]:
                    received += 1
                    cid = obj["cve"]["id"]
                    if cid in seen:
                        raise SourceError("NVD pagination returned a duplicate CVE; refusing incomplete coverage")
                    seen.add(cid)
                    if obj["cve"].get("vulnStatus") == "Rejected":
                        rejected += 1
                        continue
                    items.append(self._item(obj))
                # Do not retain unused CPE trees from every raw page in memory.
            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy", started, received, len(items), rejected
            )
        except Exception as e:
            return [], self.timed_health("failed", started, err=e)

    def _pages(self, since, until):
        headers = {"apiKey": self.token} if self.token else {}
        interval = 0.6 if self.token else 6.0
        params = {
            "lastModStartDate": since.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "lastModEndDate": until.strftime("%Y-%m-%dT%H:%M:%S.000"),
            # Modified CVEs can contain large CPE trees. Stay within
            # the HTTP client's byte bound without discarding a page.
            "resultsPerPage": 500,
            "startIndex": 0,
        }
        total = None
        while True:
            if self.metrics["requests"]:
                time.sleep(interval)
                self.metrics["wait_seconds"] += interval
            self.metrics["requests"] += 1
            try:
                response = self.http.get(
                    self.endpoint, headers=headers, params=params, expect_json=True, retry_interval=interval
                )
                data = response.json()
                self.metrics["response_bytes"] += len(response.content)
            except SourceError as error:
                if str(error) != "Response too large" or params["resultsPerPage"] == 1:
                    raise
                params["resultsPerPage"] = max(1, params["resultsPerPage"] // 2)
                self.metrics["page_size_reductions"] += 1
                continue
            current_total = data.get("totalResults")
            count = data.get("resultsPerPage")
            records = data.get("vulnerabilities")
            if (
                not isinstance(current_total, int)
                or isinstance(current_total, bool)
                or current_total < 0
                or not isinstance(count, int)
                or isinstance(count, bool)
                or not 0 <= count <= params["resultsPerPage"]
                or not isinstance(records, list)
                or len(records) != count
                or data.get("startIndex") != params["startIndex"]
            ):
                raise SourceError("Invalid NVD pagination metadata")
            if total is not None and total != current_total:
                raise SourceError("NVD result set changed during pagination; retry the complete window")
            total = current_total
            if params["startIndex"] + count > total or (count == 0 and params["startIndex"] < total):
                raise SourceError("NVD pagination made no progress")
            yield data
            params["startIndex"] += count
            if params["startIndex"] == total:
                return
