import argparse
import json
from importlib.resources import files
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


from .exceptions import ValidationError
from .pipeline import Pipeline


def dt(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"required report file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def _validate_latest_schema_subset(latest: dict[str, Any], schema: Any) -> None:
    if not isinstance(schema, dict):
        raise ValidationError("latest.json schema file must contain a JSON object")
    for key in schema.get("required", []):
        if key not in latest:
            raise ValidationError(f"latest.json schema validation failed: missing required key {key}")
    if not isinstance(latest.get("items"), list):
        raise ValidationError("latest.json schema validation failed: items must be a list")
    item_required = schema.get("properties", {}).get("items", {}).get("items", {}).get("required", [])
    for index, item in enumerate(latest.get("items", [])):
        if not isinstance(item, dict):
            raise ValidationError(f"latest.json item {index} must be an object")
        for key in item_required:
            if key not in item:
                raise ValidationError(f"latest.json item {index} missing required key {key}")


def validate_reports(output_dir: Path) -> None:
    latest_path = output_dir / "latest.json"
    health_path = output_dir / "source-health.json"
    latest = _load_json(latest_path)
    health = _load_json(health_path)
    if not isinstance(latest, dict):
        raise ValidationError("latest.json must contain a JSON object")
    schema_resource = files("cyberdailylog").joinpath("schemas/intelligence-item.schema.json")
    try:
        schema = json.loads(schema_resource.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(
            "required package schema resource is missing: schemas/intelligence-item.schema.json"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in package schema resource: {exc}") from exc
    _validate_latest_schema_subset(latest, schema)
    if not isinstance(health, list):
        raise ValidationError("source-health.json must contain a list")
    required = {
        "source",
        "status",
        "started_at",
        "finished_at",
        "duration_ms",
        "items_received",
        "items_accepted",
        "items_rejected",
        "required",
    }
    for index, record in enumerate(health):
        if not isinstance(record, dict):
            raise ValidationError(f"source-health.json record {index} must be an object")
        missing = sorted(required - record.keys())
        if missing:
            raise ValidationError(f"source-health.json record {index} missing keys: {', '.join(missing)}")
        if not isinstance(record["source"], str) or not record["source"]:
            raise ValidationError(f"source-health.json record {index} has invalid source")
        if record["status"] not in {"healthy", "degraded", "failed", "fixture_only"}:
            raise ValidationError(f"source-health.json record {index} has invalid status")


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("lookback hours must be a positive integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("lookback hours must be a positive integer")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ["collect", "generate", "run", "validate", "source-health"]:
        sp = sub.add_parser(name)
        sp.add_argument("--since", type=dt)
        sp.add_argument("--until", type=dt)
        sp.add_argument("--lookback-hours", type=positive_int, default=24)
        sp.add_argument("--output-dir", default="reports")
        sp.add_argument("--config-dir", default="config")
        sp.add_argument("--dry-run", action="store_true")
        sp.add_argument("--offline-fixtures", action="store_true")
        sp.add_argument("--log-level", default="INFO")
        sp.add_argument("--fail-on-degraded", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd in {"run", "collect", "generate", "source-health"}:
        report = Pipeline(Path(args.config_dir), Path(args.output_dir), args.offline_fixtures).run(
            args.since,
            args.until,
            args.lookback_hours,
            args.dry_run,
            args.fail_on_degraded,
        )
        if args.cmd == "source-health":
            print(json.dumps([h.to_dict() for h in report.source_health], indent=2))
        else:
            print(f"Generated {len(report.items)} selected items; degraded={report.degraded}")
        return 0
    try:
        validate_reports(Path(args.output_dir))
    except ValidationError as exc:
        parser.error(str(exc))
    print("Validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
