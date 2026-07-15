from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
from .base import BaseCollector
from cyberdailylog.models import IntelligenceItem


class RssCollector(BaseCollector):
    name = "rss_official"
    required = False

    def __init__(self, *a, sources=None, **kw):
        super().__init__(*a, **kw)
        self.sources = [source for source in (sources or []) if source.get("enabled", True)]

    def collect(self, since, until):
        started = datetime.now(timezone.utc)
        items = []
        rec = rej = 0
        try:
            feeds = self.fixture_json("rss.json") if self.offline else None
            for src in self.sources or [
                {"name": "CISA Cybersecurity Advisories", "url": "https://www.cisa.gov/news.xml"}
            ]:
                text = feeds.get(src["name"], "") if self.offline else self.http.get(src["url"]).text
                root = ET.fromstring(text)
                for e in root.findall(".//item"):
                    rec += 1
                    title = e.findtext("title") or "Untitled"
                    link = e.findtext("link") or src.get("url", "")
                    pub = e.findtext("pubDate") or ""
                    try:
                        dt = parsedate_to_datetime(pub).astimezone(timezone.utc)
                    except Exception:
                        rej += 1
                        continue
                    if since <= dt <= until:
                        items.append(
                            IntelligenceItem(
                                canonical_id="url:" + link,
                                title=title,
                                summary=e.findtext("description") or "",
                                category="advisory",
                                source_name=src.get("name", "Official RSS"),
                                source_type="official_rss",
                                source_tier=2,
                                source_url=link,
                                published_at=dt,
                                modified_at=dt,
                                references=[link],
                                confidence="medium",
                            )
                        )
            return items, self.timed_health(
                "fixture_only" if self.offline else "healthy", started, rec, len(items), rej
            )
        except Exception as e:
            return items, self.timed_health("degraded", started, rec, len(items), rej, err=e)
