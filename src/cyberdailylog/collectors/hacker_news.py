from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

from cyberdailylog.exceptions import SourceError
from cyberdailylog.models import IntelligenceItem

from .base import BaseCollector


DEFAULT_BASE_URL = "https://hacker-news.firebaseio.com/v0"


def _safe_url(value: object, fallback: str) -> str:
    candidate = str(value or "").strip()
    parsed = urlparse(candidate)
    if parsed.scheme in {"http", "https"} and parsed.hostname:
        return candidate
    return fallback


def _domain_matches(host: str, allowed_domains: list[str]) -> bool:
    normalized = host.lower().strip(".")
    return any(normalized == domain or normalized.endswith(f".{domain}") for domain in allowed_domains)


def _matches_topic(title: str, url: str, config: dict) -> bool:
    lowered = title.casefold()
    keywords = [str(value).casefold() for value in config.get("security_keywords", [])]
    if any(keyword and keyword in lowered for keyword in keywords):
        return True
    host = (urlparse(url).hostname or "").lower()
    domains = [str(value).lower().strip(".") for value in config.get("allowed_domains", [])]
    return _domain_matches(host, domains)


class HackerNewsCollector(BaseCollector):
    name = "hacker_news"
    required = False
    source_tier = 3

    def __init__(self, *args, config=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config or {}

    def _story_ids(self, fixture: dict | None) -> list[int]:
        if fixture is not None:
            raw = fixture.get("topstories", [])
        else:
            base_url = str(self.config.get("base_url") or DEFAULT_BASE_URL).rstrip("/")
            raw = self.http.get(f"{base_url}/topstories.json", expect_json=True).json()
        if not isinstance(raw, list):
            raise SourceError("Hacker News topstories response must be an array")
        return [int(value) for value in raw if isinstance(value, int) and not isinstance(value, bool)]

    def _story(self, story_id: int, fixture: dict | None) -> dict:
        if fixture is not None:
            items = fixture.get("items", {})
            raw = items.get(str(story_id), {}) if isinstance(items, dict) else {}
        else:
            base_url = str(self.config.get("base_url") or DEFAULT_BASE_URL).rstrip("/")
            raw = self.http.get(f"{base_url}/item/{story_id}.json", expect_json=True).json()
        return raw if isinstance(raw, dict) else {}

    def collect(self, since, until):
        started = datetime.now(timezone.utc)
        fixture = self.fixture_json("hacker_news.json") if self.offline else None
        received = rejected = 0
        errors: list[str] = []
        selected: list[IntelligenceItem] = []

        try:
            story_ids = self._story_ids(fixture)
        except Exception as exc:
            return [], self.timed_health("degraded", started, err=exc)

        minimum_score = int(self.config.get("minimum_score", 80))
        minimum_comments = int(self.config.get("minimum_comments", 20))
        max_scan = int(self.config.get("max_story_ids", 40))
        max_items = int(self.config.get("max_items", 3))

        for story_id in story_ids[:max_scan]:
            try:
                story = self._story(story_id, fixture)
                received += 1
                if story.get("type") != "story" or story.get("deleted") or story.get("dead"):
                    rejected += 1
                    continue
                score = int(story.get("score") or 0)
                comments = int(story.get("descendants") or 0)
                published = datetime.fromtimestamp(int(story.get("time") or 0), tz=timezone.utc)
                if not since <= published <= until or score < minimum_score or comments < minimum_comments:
                    rejected += 1
                    continue

                discussion_url = f"https://news.ycombinator.com/item?id={story_id}"
                article_url = _safe_url(story.get("url"), discussion_url)
                title = " ".join(str(story.get("title") or "Untitled").split())
                if not _matches_topic(title, article_url, self.config):
                    rejected += 1
                    continue

                selected.append(
                    IntelligenceItem(
                        canonical_id=f"hn:{story_id}",
                        title=title,
                        summary=f"Hacker News discussion with {score} points and {comments} comments.",
                        category="community_pulse",
                        source_name="Hacker News",
                        source_type="community_signal",
                        source_tier=self.source_tier,
                        official_source=False,
                        source_url=article_url,
                        published_at=published,
                        modified_at=published,
                        author=str(story.get("by") or "").strip() or None,
                        community_score=score,
                        community_comments=comments,
                        discussion_url=discussion_url,
                        references=list(dict.fromkeys([article_url, discussion_url])),
                        blue_team_relevance="Community interest signal; validate claims against primary sources.",
                        confidence="low",
                    )
                )
                if len(selected) >= max_items:
                    break
            except Exception as exc:
                errors.append(f"story {story_id}: {exc}")

        selected.sort(
            key=lambda item: (
                item.community_score or 0,
                item.community_comments or 0,
                item.published_at or datetime.min.replace(tzinfo=timezone.utc),
            ),
            reverse=True,
        )
        if self.offline and not errors:
            status = "fixture_only"
        else:
            status = "degraded" if errors else "healthy"
        error = SourceError("; ".join(errors)) if errors else None
        return selected, self.timed_health(
            status,
            started,
            received,
            len(selected),
            rejected,
            err=error,
        )
