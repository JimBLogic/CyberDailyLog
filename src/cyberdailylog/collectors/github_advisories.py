from datetime import datetime, timezone
import re
from urllib.parse import urlsplit
from .base import BaseCollector
from cyberdailylog.models import IntelligenceItem
from cyberdailylog.exceptions import SourceError


class GitHubAdvisoryCollector(BaseCollector):
    name = "github_advisories"
    required = True
    endpoint = "https://api.github.com/advisories"
    max_pages = 20

    def _dt(self, v):
        return datetime.fromisoformat(v.replace("Z", "+00:00")).astimezone(timezone.utc) if v else None

    def _item(self, a):
        ids = [i for i in [a.get("cve_id")] if i]
        gh = [a.get("ghsa_id")] if a.get("ghsa_id") else []
        if not ids and not gh:
            raise ValueError("Advisory has no stable identifier")
        vulns = a.get("vulnerabilities") or []
        severities = a.get("cvss_severities") or {}
        cvss = severities.get("cvss_v4") or severities.get("cvss_v3") or a.get("cvss") or {}
        item = IntelligenceItem(
            canonical_id=ids[0] if ids else gh[0],
            title=a.get("summary", ""),
            summary=a.get("description", ""),
            category="vulnerability",
            source_name="GitHub Global Security Advisories",
            source_type="reviewed_advisory",
            source_tier=1,
            source_url=a.get("html_url") or a.get("url"),
            published_at=self._dt(a.get("published_at")),
            modified_at=self._dt(a.get("updated_at")),
            cve_ids=ids,
            ghsa_ids=gh,
            ecosystems=[v.get("package", {}).get("ecosystem", "") for v in vulns if v.get("package")],
            products=[v.get("package", {}).get("name", "") for v in vulns if v.get("package")],
            affected_versions=[v.get("vulnerable_version_range", "") for v in vulns],
            fixed_versions=[
                v.get("first_patched_version") or v.get("patched_versions")
                for v in vulns
                if v.get("first_patched_version") or v.get("patched_versions")
            ],
            severity=a.get("severity"),
            cvss_score=cvss.get("score"),
            cvss_vector=cvss.get("vector_string"),
            cvss_version=(cvss.get("vector_string") or "").split("/")[0].removeprefix("CVSS:") or None,
            references=[r for r in a.get("references", [])],
            withdrawn=bool(a.get("withdrawn_at")),
            confidence="high",
        )
        item.add_provenance("fixed_versions", "GitHub reviewed advisory", item.fixed_versions)
        return item

    def _pages(self, since, until):
        if self.offline:
            yield self.fixture_json("github_advisories_page1.json")
            yield self.fixture_json("github_advisories_page2.json")
            return
        url = self.endpoint
        params = {
            "type": "reviewed",
            "per_page": 100,
            "modified": f"{since:%Y-%m-%d}..{until:%Y-%m-%d}",
            "sort": "updated",
            "direction": "desc",
        }
        seen = set()
        for _ in range(self.max_pages):
            parsed = urlsplit(url)
            if parsed.scheme != "https" or parsed.netloc != "api.github.com" or parsed.path != "/advisories":
                raise SourceError("Invalid advisory pagination destination")
            if url in seen:
                raise SourceError("Advisory pagination cursor repeated")
            seen.add(url)
            response = self.http.get(
                url,
                headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
                params=params,
                expect_json=True,
            )
            data = response.json()
            if not isinstance(data, list):
                raise SourceError("Invalid advisory response schema")
            yield data
            link = response.headers.get("Link") or response.headers.get("link") or ""
            match = re.search(r'<([^>]+)>;\s*rel="next"', link)
            if not match:
                return
            url = match.group(1)
            params = None
        raise SourceError("Advisory pagination exceeded the 20-page collection limit")

    def collect(self, since, until):
        started = datetime.now(timezone.utc)
        try:
            items = []
            rec = 0
            rej = 0
            for data in self._pages(since, until):
                for a in data:
                    rec += 1
                    try:
                        item = self._item(a)
                    except (ValueError, TypeError, KeyError, AttributeError, IndexError):
                        rej += 1
                        continue
                    items.append(item)
            return items, self.timed_health(
                "fixture_only" if self.offline else ("degraded" if rej else "healthy"), started, rec, len(items), rej
            )
        except Exception as e:
            return [], self.timed_health("failed", started, err=e)
