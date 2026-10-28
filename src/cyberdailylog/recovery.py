"""Additive, evidence-only publication recovery timeline."""

from datetime import datetime, timezone


def stamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo is not None else None
    except (ValueError, TypeError, AttributeError):
        return None


def recovery_telemetry(history, target):
    target_time = stamp(target)
    if target_time is None:
        return None
    observed = []
    for row in history:
        if not isinstance(row, dict) or row.get("dry_run") or stamp(row.get("scheduled_for")) != target_time:
            continue
        started = stamp(row.get("workflow_actual_start"))
        ordered = started or stamp(row.get("workflow_created"))
        if not row.get("run_id") or ordered is None:
            continue
        published = stamp(row.get("actual_publication_time"))
        finished = published or stamp(row.get("attempt_finished_at"))
        if finished and finished < ordered:
            finished = None
        outcome = (
            (
                "published"
                if row.get("core_complete") is True
                else "partial"
                if row.get("core_complete") is False
                else "unknown"
            )
            if published
            else (
                "failed"
                if row.get("status") == "failed"
                else "skipped"
                if row.get("status") == "skipped"
                else "unknown"
            )
        )
        observed.append(
            (
                ordered,
                {
                    "run_id": str(row["run_id"]),
                    "run_attempt": str(row.get("run_attempt") or "1"),
                    "trigger": row.get("trigger_origin") or row.get("event") or "unknown",
                    "started_at": started.isoformat() if started else None,
                    "finished_at": finished.isoformat() if finished else None,
                    "outcome": outcome,
                    "recovered_from": None,
                    "publication_id": row.get("commit_sha") if published else None,
                },
            )
        )
    # Immutable run+attempt identity also handles explicit GitHub reruns.
    unique = {(item["run_id"], item["run_attempt"]): (at, item) for at, item in observed}
    attempts = [item for _, item in sorted(unique.values(), key=lambda entry: entry[0])]
    chain_start = None
    recovery_seconds = None
    for index, item in enumerate(attempts):
        prior = attempts[index - 1] if index else None
        start, finish = stamp(item["started_at"]), stamp(item["finished_at"])
        prior_finish = stamp(prior["finished_at"]) if prior else None
        linked = bool(
            prior and prior["outcome"] in {"failed", "partial"} and prior_finish and start and start >= prior_finish
        )
        if linked and item["outcome"] != "skipped":
            item["recovered_from"] = {"run_id": prior["run_id"], "run_attempt": prior["run_attempt"]}
            chain_start = chain_start or prior_finish
            if item["outcome"] == "published" and finish:
                recovery_seconds = round((finish - chain_start).total_seconds(), 3)
        elif item["outcome"] != "skipped":
            chain_start = None
            recovery_seconds = None
    return {
        "schema_version": 1,
        "scheduled_for": target_time.isoformat(),
        "attempts": attempts,
        "first_observed_run_id": attempts[0]["run_id"] if attempts else None,
        "retry_count": sum(item["recovered_from"] is not None for item in attempts),
        "recovery_seconds": recovery_seconds,
        "measurement_note": "Observed attempts only. Missing starts/finishes and unobserved primary attempts stay unknown. Recovery time starts at the first linked failure/partial finish; skipped runs are not publications.",
    }
