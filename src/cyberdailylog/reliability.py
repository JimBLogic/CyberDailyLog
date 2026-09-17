"""Tested publication milestones and a retry-safe 30-calendar-day Madrid SLO."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
SLOTS = {"0 12 * * *": (12, 0), "17 12 * * *": (12, 17), "30 13 * * *": (13, 30)}


def parse_timestamp(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def iso(value):
    return value.astimezone(timezone.utc).isoformat() if value else None


def delta(end, start):
    return round((end - start).total_seconds(), 3) if end and start else None


def daily_target(reference):
    local = reference.astimezone(MADRID)
    target = local.replace(hour=12, minute=0, second=0, microsecond=0)
    if target > local:
        target -= timedelta(days=1)
    return target.astimezone(timezone.utc)


def schedule_targets(created, event, cron):
    if not created:
        return None, None
    if event != "schedule":
        return (daily_target(created), None) if created.astimezone(MADRID).hour >= 12 else (None, None)
    if cron not in SLOTS:
        return None, None
    hour, minute = SLOTS[cron]
    local = created.astimezone(MADRID)
    trigger = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if trigger > local:
        trigger -= timedelta(days=1)
    return trigger.replace(hour=12, minute=0).astimezone(timezone.utc), trigger.astimezone(timezone.utc)


def publication_status(scheduled, published, result):
    if result in {"failure", "cancelled", "timed_out"}:
        return "failed", None
    if not scheduled or not published or result != "success":
        return "unknown", None
    lag = delta(published, scheduled)
    return ("unknown" if lag < 0 else "on_time" if lag <= 3600 else "delayed" if lag <= 10800 else "stale"), lag


def build_evidence(run, health, feed, env):
    created, started = parse_timestamp(run.get("created_at")), parse_timestamp(run.get("run_started_at"))
    generated = parse_timestamp(feed.get("generated_at"))
    commit, pushed = parse_timestamp(env.get("COMMIT_CREATED")), parse_timestamp(env.get("PUSH_COMPLETED"))
    starts = [parse_timestamp(s["started_at"]) for s in health if s.get("started_at")]
    ends = [parse_timestamp(s["finished_at"]) for s in health if s.get("finished_at")]
    fetch_start, fetch_end = min(starts, default=None), max(ends, default=None)
    target, trigger = schedule_targets(created, env.get("GITHUB_EVENT_NAME"), env.get("TRIGGER_CRON"))
    results = [env.get(k) for k in ("PREFLIGHT_RESULT", "COLLECT_RESULT", "PUBLISH_RESULT")]
    result = "failure" if any(s in {"failure", "cancelled", "timed_out"} for s in results) else results[-1]
    actual = pushed if result == "success" else None
    status, lag = publication_status(target, actual, result)
    stage = "unknown"
    if lag is not None and 0 <= lag <= 3600:
        stage = "within_threshold"
    elif trigger and created and delta(created, trigger) > 3600:
        stage = "scheduler"
    elif started and created and delta(started, created) > 3600:
        stage = "workflow_queue"
    elif generated and started and delta(generated, started) > 3600:
        stage = "pipeline"
    elif actual and generated and delta(actual, generated) > 3600:
        stage = "publication"
    return {
        "schema_version": 2,
        "run_id": env.get("GITHUB_RUN_ID"),
        "run_attempt": env.get("GITHUB_RUN_ATTEMPT"),
        "run_url": f"https://github.com/{env.get('GITHUB_REPOSITORY')}/actions/runs/{env.get('GITHUB_RUN_ID')}",
        "event": env.get("GITHUB_EVENT_NAME"),
        "trigger_cron": env.get("TRIGGER_CRON") or None,
        "dry_run": env.get("DRY_RUN") == "true",
        "schedule_timezone": "Europe/Madrid",
        "target_time": "12:00 Europe/Madrid",
        "scheduled_for": iso(target),
        "trigger_scheduled_for": iso(trigger),
        "schedule_basis": "inferred from original run creation and IANA cron slot"
        if trigger
        else "manual recovery"
        if target
        else "unknown",
        "schedule_limitation": "GitHub exposes no nominal occurrence ID; delays over one day cannot be disambiguated.",
        "workflow_created": iso(created),
        "workflow_actual_start": iso(started),
        "fetch_start": iso(fetch_start),
        "fetch_end": iso(fetch_end),
        "report_generated": iso(generated),
        "commit_created": iso(commit),
        "commit_sha": env.get("COMMIT_SHA") or None,
        "push_completed": iso(pushed),
        "actual_publication_time": iso(actual),
        "status": status,
        "publication_lag_seconds": lag,
        "trigger_start_lag_seconds": delta(started, trigger),
        "workflow_queue_seconds": delta(started, created),
        "fetch_duration_seconds": delta(fetch_end, fetch_start),
        "run_to_commit_seconds": delta(commit, started),
        "preflight_result": results[0],
        "collect_result": results[1],
        "publish_result": results[2],
        "root_cause_stage": stage,
        "measurement_note": "Successful push measures repository publication, not dashboard visibility. Missing milestones stay null.",
    }


def slo_summary(history, now):
    today = now.astimezone(MADRID).date()
    cutoff = today - timedelta(days=29)
    days = {}
    beginning = None
    for row in history:
        target = parse_timestamp(row.get("scheduled_for"))
        if not target or row.get("dry_run") or row.get("status") == "skipped":
            continue
        start = parse_timestamp(row.get("monitoring_started_at")) or target
        beginning = min(beginning, start.date()) if beginning else start.date()
        day = target.astimezone(MADRID).date()
        if cutoff <= day <= today:
            days.setdefault(day, []).append(row)
    samples = []
    if beginning:
        day = max(beginning, cutoff)
        while day <= today:
            target = datetime(day.year, day.month, day.day, 12, tzinfo=MADRID).astimezone(timezone.utc)
            successes = [
                r
                for r in days.get(day, [])
                if r.get("status") in {"on_time", "delayed", "stale"}
                and isinstance(r.get("publication_lag_seconds"), (int, float))
            ]
            if successes:
                status = min(successes, key=lambda r: r["publication_lag_seconds"])["status"]
                samples.append({"date": day.isoformat(), "status": status})
            elif now >= target + timedelta(hours=1):
                samples.append({"date": day.isoformat(), "status": "failed" if day in days else "missing"})
            day += timedelta(days=1)
    count = len(samples)
    on_time = sum(r["status"] == "on_time" for r in samples)
    percentage = round(on_time * 100 / count, 1) if count else None
    return {
        "objective": ">=95% within 60 minutes of 12:00 Europe/Madrid",
        "target_percentage": 95,
        "window_days": 30,
        "measured_publications": count,
        "on_time_publications": on_time,
        "attainment_percentage": percentage,
        "met": percentage is not None and percentage >= 95,
        "full_window_observed": count == 30,
        "evaluated_at": iso(now),
        "days": samples,
    }


def record_attempt(history, evidence, now):
    if not isinstance(history, list):
        raise ValueError("Invalid timing history; refusing to overwrite it")
    if evidence.get("dry_run"):
        return history
    starts = [r.get("monitoring_started_at") or r.get("scheduled_for") for r in history + [evidence]]
    evidence["monitoring_started_at"] = min((s for s in starts if s), default=None)
    cutoff = now.astimezone(MADRID).date() - timedelta(days=29)
    rows = []
    for row in history:
        target = parse_timestamp(row.get("scheduled_for"))
        if (
            target
            and target.astimezone(MADRID).date() >= cutoff
            and (row.get("run_id"), row.get("run_attempt")) != (evidence.get("run_id"), evidence.get("run_attempt"))
        ):
            rows.append(row)
    rows.append(evidence)
    return rows
