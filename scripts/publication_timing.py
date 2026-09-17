"""Persist only this run's milestones. Run with PYTHONPATH=src in Actions."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from cyberdailylog.reliability import build_evidence, record_attempt, slo_summary


def read_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def main():
    parser = argparse.ArgumentParser()
    for name in ("run", "health", "feed", "output", "history"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    evidence = build_evidence(
        read_json(args.run, {}), read_json(args.health, []), read_json(args.feed, {}), dict(os.environ)
    )
    history = record_attempt(read_json(args.history, []), evidence, now)
    args.history.write_text(json.dumps(history, indent=2, sort_keys=True) + "\n")
    evidence["slo"] = slo_summary(history, now)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
