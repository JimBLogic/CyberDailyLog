from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

from cyberdailylog.exceptions import SourceError
from cyberdailylog.models import IntelligenceItem

from .base import BaseCollector


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs):
        del attrs
        if tag.lower() in {"script", "style", "noscript"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str):
        if tag.lower() in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str):
        if not self._ignored_depth:
            self.parts.append(data)


def _plain_text(value: str) -> str:
    parser = _TextExtractor()
    # Some publisher feeds insert a stray semicolon after the numeric marker,
    # including inside nested escapes (&#;x26;#;39;). Repair only numeric refs.
    decoded = value or ""
    for _ in range(4):
        normalized = re.sub(r"&#;(?=(?:[xX][0-9a-fA-F]+|[0-9]+);)", "&#", decoded)
        normalized = unescape(normalized)
        if normalized == decoded:
            break
        decoded = normalized
    parser.feed(decoded)
    parser.close()
    return " ".join(" ".join(parser.parts).split())


def _truncate_excerpt(value: str, max_words: int, max_characters: int) -> str:
    clean = _plain_text(value)
    words = clean.split()
    if len(words) > max_words:
        clean = " ".join(words[:max_words]) + "…"
    if len(clean) <= max_characters:
        return clean
    shortened = clean[: max(1, max_characters - 1)].rsplit(" ", 1)[0]
    return f"{shortened or clean[: max(1, max_characters - 1)]}…"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _first_text(element: ET.Element, names: set[str]) -> str:
    for child in element.iter():
        if _local_name(child.tag) in names and child.text:
            return child.text.strip()
    return ""


def _entry_link(element: ET.Element, fallback: str) -> str:
    for child in element.iter():
        if _local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        rel = child.attrib.get("rel", "alternate")
        if href and rel in {"alternate", ""}:
            return href.strip()
        if child.text and child.text.strip():
            return child.text.strip()
    return fallback


def _entry_datetime(element: ET.Element) -> datetime:
    raw = _first_text(element, {"pubdate", "published", "updated", "date"})
    if not raw:
        raise ValueError("feed entry has no publication timestamp")
    # CERT-EU uses these non-RFC abbreviations. Do not interpret Madrid time
    # as UTC (especially around the October DST change).
    raw = re.sub(r"\bCEST$", "+0200", raw)
    raw = re.sub(r"\bCET$", "+0100", raw)
    try:
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _feed_entries(root: ET.Element) -> list[ET.Element]:
    entries = [element for element in root.iter() if _local_name(element.tag) in {"item", "entry"}]
    return entries


def _health_name(source: dict) -> str:
    configured = str(source.get("health_name") or "").strip()
    if configured:
        return configured
    slug = re.sub(r"[^a-z0-9]+", "_", str(source.get("name") or "rss").lower()).strip("_")
    return f"rss_{slug or 'source'}"


class RssCollector(BaseCollector):
    name = "rss_context"
    required = False

    def __init__(self, *args, sources=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = [source for source in (sources or []) if source.get("enabled", True)]
        if len(self.sources) == 1:
            self.name = _health_name(self.sources[0])

    def collect(self, since, until):
        started = datetime.now(timezone.utc)
        items: list[IntelligenceItem] = []
        received = rejected = 0
        errors: list[str] = []
        fixtures = self.fixture_json("rss.json") if self.offline else None

        for source in self.sources:
            source_name = str(source.get("name") or "Curated RSS")
            try:
                text = (
                    str(fixtures.get(source_name, ""))
                    if self.offline and isinstance(fixtures, dict)
                    else self.http.get(str(source["url"]), max_bytes=2_000_000).text
                )
                if not text.strip():
                    raise SourceError("empty feed response")
                if re.search(r"<!\s*(DOCTYPE|ENTITY)\b", text, re.IGNORECASE):
                    raise SourceError("feed DTDs and entities are not permitted")
                root = ET.fromstring(text)
                if _local_name(root.tag) not in {"rss", "rdf", "feed"}:
                    raise SourceError("response is not an RSS or Atom feed")
                entries = _feed_entries(root)
                if source.get("require_entries") and not entries:
                    raise SourceError("feed contains no entries; payload is not verified")
                source_rejected = rejected
                for entry in entries:
                    received += 1
                    try:
                        published = _entry_datetime(entry)
                    except (TypeError, ValueError):
                        rejected += 1
                        continue
                    if not since <= published <= until:
                        continue

                    link = _entry_link(entry, "")
                    # Some older CERT-EU paths contain literal spaces.
                    # Percent-encode them before applying the same origin
                    # checks; other control characters remain rejected.
                    link = link.replace(" ", "%20")
                    try:
                        parsed = urlsplit(link)
                        safe = (
                            parsed.scheme == "https"
                            and bool(parsed.hostname)
                            and (
                                not source.get("allowed_entry_hosts")
                                or parsed.hostname in source["allowed_entry_hosts"]
                            )
                            and parsed.port in (None, 443)
                            and not parsed.username
                            and not parsed.password
                            and not any(ord(c) <= 32 for c in link)
                        )
                    except ValueError:
                        safe = False
                    if not safe:
                        rejected += 1
                        continue
                    title = _plain_text(_first_text(entry, {"title"})) or "Untitled"
                    raw_excerpt = _first_text(entry, {"description", "summary", "content", "encoded"})
                    excerpt = _truncate_excerpt(
                        raw_excerpt,
                        int(source.get("excerpt_max_words", 24)),
                        int(source.get("excerpt_max_characters", 240)),
                    )
                    if source.get("metadata_only"):
                        excerpt = ""
                    author = str(source.get("author") or _first_text(entry, {"creator", "author", "name"})).strip()
                    category = str(source.get("category") or "advisory")
                    items.append(
                        IntelligenceItem(
                            canonical_id="url:" + link,
                            title=title,
                            summary=excerpt,
                            category=category,
                            source_name=source_name,
                            source_type=str(source.get("source_type") or "curated_rss"),
                            source_tier=int(source.get("source_tier", 2)),
                            official_source=bool(source.get("official_source", False)),
                            source_url=link,
                            published_at=published,
                            modified_at=published,
                            author=author or None,
                            excerpt_origin="publisher_feed" if excerpt else None,
                            references=[link, *source.get("attribution_urls", [])],
                            blue_team_relevance=str(source.get("blue_team_relevance") or ""),
                            confidence="medium",
                        )
                    )
                if source.get("require_entries") and rejected > source_rejected:
                    errors.append(f"{source_name}: some feed entries failed date or link validation")
            except Exception as exc:
                errors.append(f"{source_name}: {exc}")

        if self.offline and not errors:
            status = "fixture_only"
        else:
            status = "degraded" if errors else "healthy"
        error = SourceError("; ".join(errors)) if errors else None
        return items, self.timed_health(
            status,
            started,
            received,
            len(items),
            rejected,
            err=error,
        )
