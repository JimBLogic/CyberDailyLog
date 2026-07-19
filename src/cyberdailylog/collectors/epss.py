from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlencode

from .base import BaseCollector


MAX_ENCODED_QUERY_LENGTH = 1800


def batch_cves(cves: list[str], max_query_length: int = MAX_ENCODED_QUERY_LENGTH) -> list[list[str]]:
    unique = sorted({str(cve).strip().upper() for cve in cves if str(cve).strip()})
    batches: list[list[str]] = []
    current: list[str] = []

    for cve in unique:
        candidate = [*current, cve]
        encoded = urlencode({"cve": ",".join(candidate)})
        if current and len(encoded) > max_query_length:
            batches.append(current)
            current = [cve]
        else:
            current = candidate

    if current:
        batches.append(current)
    return batches


def _extract_scores(data: object) -> tuple[dict[str, dict[str, float | str | None]], int]:
    if not isinstance(data, dict):
        return {}, 1
    rows = data.get("data", [])
    if not isinstance(rows, list):
        return {}, 1

    scores: dict[str, dict[str, float | str | None]] = {}
    malformed = 0
    for row in rows:
        if not isinstance(row, dict):
            malformed += 1
            continue
        try:
            cve = str(row["cve"]).strip().upper()
            if not cve:
                raise ValueError("empty CVE")
            scores[cve] = {
                "epss_score": float(row["epss"]),
                "epss_percentile": float(row["percentile"]),
                "date": str(row["date"]) if row.get("date") is not None else None,
            }
        except (KeyError, TypeError, ValueError):
            malformed += 1
    return scores, malformed


class EpssCollector(BaseCollector):
    name = "epss"
    required = False
    endpoint = "https://api.first.org/data/v1/epss"

    def collect_scores(self, cves):
        started = datetime.now(timezone.utc)
        unique = sorted({str(cve).strip().upper() for cve in cves if str(cve).strip()})
        if not unique:
            return {}, self.timed_health("fixture_only" if self.offline else "healthy", started)

        if self.offline:
            scores, malformed = _extract_scores(self.fixture_json("epss.json"))
            selected = {cve: scores[cve] for cve in unique if cve in scores}
            return selected, self.timed_health(
                "fixture_only",
                started,
                received=len(unique),
                accepted=len(selected),
                rejected=max(0, len(unique) - len(selected)) + malformed,
            )

        scores: dict[str, dict[str, float | str | None]] = {}
        failed_batches = 0
        malformed = 0
        batches = batch_cves(unique)

        for batch in batches:
            try:
                response = self.http.get(
                    self.endpoint,
                    params={"cve": ",".join(batch)},
                    expect_json=True,
                )
                parsed, rejected = _extract_scores(response.json())
                scores.update(parsed)
                malformed += rejected
            except Exception:
                failed_batches += 1

        unexpected_empty = bool(unique) and not scores
        degraded = failed_batches > 0 or unexpected_empty or malformed > 0
        error = None
        if degraded:
            error = RuntimeError(
                f"EPSS enrichment incomplete: {len(scores)}/{len(unique)} scores returned; "
                f"{failed_batches}/{len(batches)} batches failed"
            )

        return scores, self.timed_health(
            "degraded" if degraded else "healthy",
            started,
            received=len(unique),
            accepted=len(scores),
            rejected=max(0, len(unique) - len(scores)) + malformed,
            err=error,
        )

    def collect(self, since, until):
        return [], self.timed_health("skipped", datetime.now(timezone.utc))
