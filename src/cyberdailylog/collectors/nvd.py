from datetime import datetime, timezone

from cyberdailylog.models import IntelligenceItem

from .base import BaseCollector


class NvdCollector(BaseCollector):
    name = "nvd"
    required = True
    endpoint = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def _parse_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )

    def _item(self, obj: dict) -> IntelligenceItem:
        cve = obj["cve"]
        cve_id = cve["id"]
        metrics = cve.get("metrics", {})
        cvss_score = None
        cvss_version = None
        cvss_vector = None
        severity = None

        for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30"):
            if key not in metrics:
                continue
            metric = metrics[key][0]
            cvss_data = metric.get("cvssData", {})
            cvss_score = cvss_data.get("baseScore")
            cvss_version = cvss_data.get("version")
            cvss_vector = cvss_data.get("vectorString")
            severity = metric.get("baseSeverity") or cvss_data.get("baseSeverity")
            break

        description = next(
            (
                entry["value"]
                for entry in cve.get("descriptions", [])
                if entry.get("lang") == "en"
            ),
            "",
        )
        references = [
            reference.get("url", "")
            for reference in cve.get("references", [])
            if reference.get("url")
        ]
        item = IntelligenceItem(
            canonical_id=cve_id,
            title=f"{cve_id}: {description[:120]}",
            summary=description,
            category="vulnerability",
            source_name="NVD CVE API 2.0",
            source_type="vulnerability_database",
            source_tier=1,
            source_url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
            published_at=self._parse_datetime(cve["published"]),
            modified_at=self._parse_datetime(cve["lastModified"]),
            cve_ids=[cve_id],
            cvss_version=cvss_version,
            cvss_score=cvss_score,
            cvss_vector=cvss_vector,
            severity=severity,
            references=references,
            confidence="medium",
        )
        item.add_provenance("cvss_score", "NVD", cvss_score)
        return item

    def collect(self, since: datetime, until: datetime):
        started = datetime.now(timezone.utc)
        try:
            if self.offline:
                pages = [
                    self.fixture_json("nvd_page1.json"),
                    self.fixture_json("nvd_page2.json"),
                ]
            else:
                headers = {"apiKey": self.token} if self.token else {}
                params = {
                    "pubStartDate": since.strftime("%Y-%m-%dT%H:%M:%S.000"),
                    "pubEndDate": until.strftime("%Y-%m-%dT%H:%M:%S.000"),
                    "resultsPerPage": 2000,
                    "startIndex": 0,
                }
                pages = []
                while True:
                    data = self.http.get(
                        self.endpoint,
                        headers=headers,
                        params=params,
                        expect_json=True,
                    ).json()
                    pages.append(data)
                    page_size = data.get("resultsPerPage", 0)
                    total_results = data.get("totalResults", 0)
                    if params["startIndex"] + page_size >= total_results:
                        break
                    params["startIndex"] += page_size

            items = []
            received = 0
            rejected = 0
            for page in pages:
                for obj in page.get("vulnerabilities", []):
                    received += 1
                    if obj["cve"].get("vulnStatus") == "Rejected":
                        rejected += 1
                        continue
                    items.append(self._item(obj))

            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy",
                started,
                received,
                len(items),
                rejected,
            )
        except Exception as exc:
            return [], self.timed_health("failed", started, err=exc)
