from datetime import datetime, timezone

from cyberdailylog.models import IntelligenceItem

from .base import BaseCollector


class GitHubAdvisoryCollector(BaseCollector):
    name = "github_advisories"
    required = True
    endpoint = "https://api.github.com/advisories"

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )

    def _item(self, advisory: dict) -> IntelligenceItem:
        cve_ids = [advisory["cve_id"]] if advisory.get("cve_id") else []
        ghsa_ids = [advisory["ghsa_id"]] if advisory.get("ghsa_id") else []
        vulnerabilities = advisory.get("vulnerabilities") or []
        source_url = advisory.get("html_url") or advisory.get("url") or ""
        item = IntelligenceItem(
            canonical_id=cve_ids[0] if cve_ids else ghsa_ids[0],
            title=advisory.get("summary", ""),
            summary=advisory.get("description", ""),
            category="vulnerability",
            source_name="GitHub Global Security Advisories",
            source_type="reviewed_advisory",
            source_tier=1,
            source_url=source_url,
            published_at=self._parse_datetime(advisory.get("published_at")),
            modified_at=self._parse_datetime(advisory.get("updated_at")),
            cve_ids=cve_ids,
            ghsa_ids=ghsa_ids,
            ecosystems=[
                vulnerability.get("package", {}).get("ecosystem", "")
                for vulnerability in vulnerabilities
                if vulnerability.get("package")
            ],
            products=[
                vulnerability.get("package", {}).get("name", "")
                for vulnerability in vulnerabilities
                if vulnerability.get("package")
            ],
            affected_versions=[
                vulnerability.get("vulnerable_version_range", "")
                for vulnerability in vulnerabilities
            ],
            fixed_versions=[
                vulnerability.get("patched_versions", "")
                for vulnerability in vulnerabilities
                if vulnerability.get("patched_versions")
            ],
            severity=advisory.get("severity"),
            cvss_score=(advisory.get("cvss") or {}).get("score"),
            cvss_vector=(advisory.get("cvss") or {}).get("vector_string"),
            references=list(advisory.get("references", [])),
            withdrawn=bool(advisory.get("withdrawn_at")),
            confidence="high",
        )
        item.add_provenance(
            "fixed_versions",
            "GitHub reviewed advisory",
            item.fixed_versions,
        )
        return item

    def collect(self, since: datetime, until: datetime):
        del since, until
        started = datetime.now(timezone.utc)
        try:
            if self.offline:
                pages = [
                    self.fixture_json("github_advisories_page1.json"),
                    self.fixture_json("github_advisories_page2.json"),
                ]
            else:
                headers = (
                    {"Authorization": f"Bearer {self.token}"} if self.token else {}
                )
                pages = [
                    self.http.get(
                        self.endpoint,
                        headers=headers,
                        params={"type": "reviewed", "per_page": 100},
                        expect_json=True,
                    ).json()
                ]

            items = []
            received = 0
            rejected = 0
            for page in pages:
                for advisory in page:
                    received += 1
                    items.append(self._item(advisory))

            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy",
                started,
                received,
                len(items),
                rejected,
            )
        except Exception as exc:
            return [], self.timed_health("failed", started, err=exc)
