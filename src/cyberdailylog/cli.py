import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .pipeline import Pipeline


def parse_datetime(value: str) -> datetime:
    """Parse an ISO-8601 datetime and normalize it to UTC."""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--since")
    parser.add_argument("--until")
    parser.add_argument("--lookback-hours", type=int, default=24)
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--config-dir", default="config")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--offline-fixtures", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--fail-on-degraded", action="store_true")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    for name in ["collect", "generate", "run", "validate", "source-health"]:
        add_common_arguments(subparsers.add_parser(name))

    args = parser.parse_args(argv)

    if args.cmd in {"run", "collect", "generate", "source-health"}:
        report = Pipeline(
            Path(args.config_dir),
            Path(args.output_dir),
            args.offline_fixtures,
        ).run(
            parse_datetime(args.since) if args.since else None,
            parse_datetime(args.until) if args.until else None,
            args.lookback_hours,
            args.dry_run,
            args.fail_on_degraded,
        )
        if args.cmd == "source-health":
            print(json.dumps([health.to_dict() for health in report.source_health], indent=2))
        else:
            print(f"Generated {len(report.items)} selected items; degraded={report.degraded}")
        return

    output_dir = Path(args.output_dir)
    for path in [output_dir / "latest.json", output_dir / "source-health.json"]:
        if path.exists():
            json.loads(path.read_text(encoding="utf-8"))
    print("Validation OK")


if __name__ == "__main__":
    main()
