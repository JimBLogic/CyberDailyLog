from datetime import datetime, timezone
from .base import BaseCollector


class EpssCollector(BaseCollector):
    name = "epss"
    required = False
    endpoint = "https://api.first.org/data/v1/epss"

    def collect_scores(self, cves):
        started = datetime.now(timezone.utc)
        try:
            data = (
                self.fixture_json("epss.json")
                if self.offline
                else self.http.get(self.endpoint, params={"cve": ",".join(sorted(cves))}, expect_json=True).json()
            )
            scores = {
                r["cve"]: {
                    "epss_score": float(r["epss"]),
                    "epss_percentile": float(r["percentile"]),
                    "date": r.get("date"),
                }
                for r in data.get("data", [])
            }
            return scores, self.timed_health(
                "fixture_only" if self.offline else "healthy", started, len(data.get("data", [])), len(scores)
            )
        except Exception as e:
            return {}, self.timed_health("degraded", started, err=e)

    def collect(self, since, until):
        return [], self.timed_health("skipped", datetime.now(timezone.utc))
