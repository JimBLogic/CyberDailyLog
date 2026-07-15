from datetime import datetime, timezone

from .base import BaseCollector


class EpssCollector(BaseCollector):
    name = "epss"
    required = False
    endpoint = "https://api.first.org/data/v1/epss"

    def collect_scores(self, cves: list[str]):
        started = datetime.now(timezone.utc)
        try:
            if self.offline:
                data = self.fixture_json("epss.json")
            else:
                data = self.http.get(
                    self.endpoint,
                    params={"cve": ",".join(sorted(cves))},
                    expect_json=True,
                ).json()

            scores = {
                record["cve"]: {
                    "epss_score": float(record["epss"]),
                    "epss_percentile": float(record["percentile"]),
                    "date": record.get("date"),
                }
                for record in data.get("data", [])
            }
            return scores, self.timed_health(
                "fixture_only" if self.offline else "healthy",
                started,
                len(data.get("data", [])),
                len(scores),
            )
        except Exception as exc:
            return {}, self.timed_health("degraded", started, err=exc)

    def collect(self, since: datetime, until: datetime):
        del since, until
        return [], self.timed_health("skipped", datetime.now(timezone.utc))
