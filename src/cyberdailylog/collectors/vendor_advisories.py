"""Corroborate urgent CVEs from the publisher's own public GitHub advisories.

This independent, bounded source must not make the NVD bulk collector appear
healthy. Records still use the existing ledger and provenance machinery.
"""

from datetime import datetime, timezone
import re

from cyberdailylog.exceptions import SourceError

from .github_advisories import GitHubAdvisoryCollector


class VendorAdvisoryCollector(GitHubAdvisoryCollector):
    name = "vendor_advisories"
    required = False

    def __init__(self, http=None, *, token=None, advisories=None, offline=False):
        super().__init__(http, token=token, offline=offline)
        self.advisories = advisories or []

    @staticmethod
    def _validated_watch(entry):
        if not isinstance(entry, dict):
            raise SourceError("Invalid configured vendor advisory")
        owner, repo, ghsa, cve = (entry.get(k) for k in ("owner", "repo", "ghsa_id", "cve_id"))
        if (
            not all(isinstance(v, str) for v in (owner, repo, ghsa, cve))
            or not re.fullmatch(r"[A-Za-z0-9-]{1,64}", owner)
            or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", repo)
            or not re.fullmatch(r"GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}", ghsa)
            or not re.fullmatch(r"CVE-20[0-9]{2}-[0-9]{4,}", cve)
        ):
            raise SourceError("Invalid configured vendor advisory identifier")
        return owner, repo, ghsa, cve

    def collect(self, since, until):
        started = datetime.now(timezone.utc)
        if self.offline:
            return [], self.timed_health("fixture_only", started)
        try:
            if not isinstance(self.advisories, list) or len(self.advisories) > 10:
                raise SourceError("Invalid vendor advisory watch budget")
            watches = [self._validated_watch(a) for a in self.advisories]
            items = []
            for owner, repo, ghsa, cve in watches:
                url = f"https://api.github.com/repos/{owner}/{repo}/security-advisories/{ghsa}"
                response = self.http.get(
                    url,
                    headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
                    expect_json=True,
                )
                payload = response.json()
                if (
                    not isinstance(payload, dict)
                    or payload.get("ghsa_id") != ghsa
                    or payload.get("cve_id") != cve
                    or payload.get("state") not in {None, "published"}
                    or not payload.get("published_at")
                ):
                    raise SourceError("Vendor advisory identity or published state mismatch")
                item = self._item(payload)
                item.source_name = "GitHub vendor security advisories"
                item.source_type = "vendor_advisory"
                item.source_url = f"https://github.com/{owner}/{repo}/security/advisories/{ghsa}"
                items.append(item)
            return items, self.timed_health("healthy", started, len(watches), len(items))
        except Exception as error:
            # Fail atomically: don't claim successful monitoring from a
            # partially fetched/ambiguous advisory watch list.
            return [], self.timed_health("failed", started, err=error)
