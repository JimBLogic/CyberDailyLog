from datetime import datetime, timezone

from cyberdailylog.models import IntelligenceItem

from .base import BaseCollector


class GitHubReleaseCollector(BaseCollector):
    name = "github_releases"
    required = False

    def __init__(self, *args, repos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.repos = repos or []

    def _parse_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )

    def collect(self, since: datetime, until: datetime):
        started = datetime.now(timezone.utc)
        items = []
        received = 0
        try:
            if self.offline:
                data = self.fixture_json("github_releases.json")
            else:
                headers = (
                    {"Authorization": f"Bearer {self.token}"} if self.token else {}
                )
                data = {
                    repo: self.http.get(
                        f"https://api.github.com/repos/{repo}/releases",
                        headers=headers,
                        expect_json=True,
                    ).json()
                    for repo in self.repos
                }

            for repo, releases in data.items():
                for release in releases:
                    received += 1
                    published_at = self._parse_datetime(release["published_at"])
                    if not since <= published_at <= until:
                        continue

                    items.append(
                        IntelligenceItem(
                            canonical_id=f"release:{repo}:{release['tag_name']}",
                            title=f"{repo} {release['tag_name']}",
                            summary=release.get("name") or "",
                            category="tool_release",
                            source_name="GitHub Releases",
                            source_type="defensive_tool_release",
                            source_tier=3,
                            source_url=release["html_url"],
                            published_at=published_at,
                            modified_at=published_at,
                            references=[release["html_url"]],
                            blue_team_relevance=(
                                "Allowlisted defensive project release; review release "
                                "notes for detection or monitoring updates."
                            ),
                            detection_opportunities=[
                                "Review release notes for defensive content changes."
                            ],
                            confidence="medium",
                        )
                    )

            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy",
                started,
                received,
                len(items),
            )
        except Exception as exc:
            return items, self.timed_health(
                "degraded",
                started,
                received,
                len(items),
                err=exc,
            )
