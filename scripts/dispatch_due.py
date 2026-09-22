"""Independent scheduler adapter. Preview by default; --apply sends one dispatch.

Run on infrastructure outside GitHub Actions. No scheduler is installed by this
file. Read docs/scheduler-incident-2026-09-21.md before activating it.
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

REPOSITORY = "JimBLogic/CyberDailyLog"
WORKFLOW = "daily-intelligence.yml"
MADRID = ZoneInfo("Europe/Madrid")
TIMING_URL = f"https://raw.githubusercontent.com/{REPOSITORY}/main/reports/publication-timing.json"
DISPATCH_URL = f"https://api.github.com/repos/{REPOSITORY}/actions/workflows/{WORKFLOW}/dispatches"


def decision(now, timing):
    local = now.astimezone(MADRID)
    target = local.replace(hour=12, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    # Three 5-minute launch windows: noon, 12:20 and 12:40 in Madrid.
    # An independent timer must invoke once per window, not every minute.
    if local.hour != 12 or not any(start <= local.minute < start + 5 for start in (0, 20, 40)):
        return {"dispatch": False, "reason": "outside launch window"}
    try:
        published = datetime.fromisoformat(str(timing.get("actual_publication_time", "")).replace("Z", "+00:00"))
        if (
            timing.get("schema_version") == 2
            and timing.get("status") in {"on_time", "delayed", "stale"}
            and published.tzinfo is not None
            and target <= published <= now + timedelta(minutes=5)
        ):
            return {"dispatch": False, "reason": "today's publication already exists"}
    except (ValueError, TypeError):
        pass
    return {
        "dispatch": True,
        "reason": "no measured publication since today's noon target",
        "scheduled_for": target.isoformat(),
        "payload": {
            "ref": "main",
            "inputs": {
                "dry_run": False,
                "lookback_hours": "24",
                "trigger_origin": "external",
                "dispatch_requested_at": now.astimezone(timezone.utc).isoformat(),
            },
        },
    }


def load_timing():
    try:
        with urlopen(Request(TIMING_URL, headers={"Accept": "application/json"}), timeout=15) as response:
            content = response.read(1_000_001)
            if len(content) > 1_000_000:
                return {}
            data = json.loads(content)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        # A read outage must not prevent a bounded recovery request. The
        # workflow's authenticated preflight remains the publication guard.
        return {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Send a workflow_dispatch using GH_ACTIONS_TOKEN")
    args = parser.parse_args()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    plan = decision(now, {})
    if plan["dispatch"]:
        plan = decision(now, load_timing())
    if not args.apply or not plan["dispatch"]:
        print(json.dumps({**plan, "mode": "preview" if not args.apply else "apply"}))
        return 0
    token = os.environ.get("GH_ACTIONS_TOKEN")
    if not token:
        parser.error("GH_ACTIONS_TOKEN is required for --apply; use a repository-scoped Actions write credential")
    request = Request(
        DISPATCH_URL,
        data=json.dumps(plan["payload"]).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CyberDailyLog-independent-scheduler",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            if response.status != 204:
                raise RuntimeError(f"Unexpected dispatch status: {response.status}")
    except HTTPError as error:
        raise SystemExit(f"GitHub dispatch failed: HTTP {error.code}") from None
    except OSError:
        raise SystemExit("GitHub dispatch response unavailable; reconcile workflow runs before retrying") from None
    print(json.dumps({"dispatch": "accepted", "scheduled_for": plan["scheduled_for"], "requested_at": now.isoformat()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
