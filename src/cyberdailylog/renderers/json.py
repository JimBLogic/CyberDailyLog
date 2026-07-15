import json
from pathlib import Path

from cyberdailylog.models import Report


def write_json(report: Report, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    text = report.model_dump_json(indent=2)
    (output_dir / "latest.json").write_text(text + "\n", encoding="utf-8")
    (output_dir / "source-health.json").write_text(
        json.dumps(
            [health.to_dict() for health in report.source_health],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report_date = report.coverage_end.date()
    archive_dir = output_dir / "archive" / f"{report_date:%Y}" / f"{report_date:%m}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / f"{report_date}.json").write_text(
        text + "\n",
        encoding="utf-8",
    )
