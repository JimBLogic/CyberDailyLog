from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

from cyberdailylog.models import IntelligenceItem

from .base import BaseCollector


class RssCollector(BaseCollector):
    name = "rss_official"
    required = False

    def __init__(self, *args, sources=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = sources or []

    def collect(self, since: datetime, until: datetime):
        started = datetime.now(timezone.utc)
        items = []
        received = 0
        rejected = 0
        try:
            feeds = self.fixture_json("rss.json") if self.offline else None
            sources = self.sources or [
                {
                    "name": "CISA Cybersecurity Advisories",
                    "url": "https://www.cisa.gov/news.xml",
                }
            ]
            for source in sources:
                if self.offline:
                    text = feeds.get(source["name"], "")
                else:
                    text = self.http.get(source["url"]).text

                root = ET.fromstring(text)
                for entry in root.findall(".//item"):
                    received += 1
                    title = entry.findtext("title") or "Untitled"
                    link = entry.findtext("link") or source.get("url", "")
                    published = entry.findtext("pubDate") or ""
                    try:
                        published_at = parsedate_to_datetime(published).astimezone(
                            timezone.utc
                        )
                    except Exception:
                        rejected += 1
                        continue

                    if not since <= published_at <= until:
                        continue

                    items.append(
                        IntelligenceItem(
                            canonical_id="url:" + link,
                            title=title,
                            summary=entry.findtext("description") or "",
                            category="advisory",
                            source_name=source.get("name", "Official RSS"),
                            source_type="official_rss",
                            source_tier=2,
                            source_url=link,
                            published_at=published_at,
                            modified_at=published_at,
                            references=[link],
                            confidence="medium",
                        )
                    )

            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy",
                started,
                received,
                len(items),
                rejected,
            )
        except Exception as exc:
            return items, self.timed_health(
                "degraded",
                started,
                received,
                len(items),
                rejected,
                err=exc,
            )
