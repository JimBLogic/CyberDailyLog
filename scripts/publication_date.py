"""Return the Madrid date only for a complete, consistent live publication."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def publication_date(root=Path("reports"), now=None):
    now = now or datetime.now(timezone.utc)
    try:
        report, compact, history = [
            json.loads((root / name).read_text(encoding="utf-8"))
            for name in ("latest.json", "portfolio-feed.json", "dashboard-feed.json")
        ]
        stamp = report["generated_at"]
        generated = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if generated.tzinfo is None or generated > now + timedelta(minutes=5):
            return ""
        if report.get("degraded") is not False or not isinstance(report.get("items"), list):
            return ""
        if any(
            feed.get("generated_at") != stamp or feed.get("project") != "CyberDailyLog" for feed in (compact, history)
        ):
            return ""
        healthy = {source["source"] for source in report["source_health"] if source.get("status") == "healthy"}
        if "cisa_kev" not in healthy or not healthy.intersection({"nvd", "github_advisories"}):
            return ""
        return generated.astimezone(ZoneInfo("Europe/Madrid")).date().isoformat()
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return ""


if __name__ == "__main__":
    print(publication_date())
