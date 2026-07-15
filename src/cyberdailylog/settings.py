from pathlib import Path
from typing import Any


class Settings:
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    """Load the small project configuration format used by the current MVP.

    This intentionally remains a minimal parser until a dedicated YAML dependency
    is introduced. Source lists are supplied explicitly for the current schema.
    """
    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(0, data)]

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        while stack and indent < stack[-1][0]:
            stack.pop()
        current = stack[-1][1]

        if line.startswith("- "):
            continue
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            current[key] = {}
            stack.append((indent + 2, current[key]))
        elif value.startswith("["):
            current[key] = [
                item.strip()
                for item in value.strip("[]").split(",")
                if item.strip()
            ]
        else:
            try:
                current[key] = int(value)
            except ValueError:
                current[key] = value.strip('"')

    if path.name == "sources.yml":
        data["rss_sources"] = [
            {
                "name": "CISA Cybersecurity Advisories",
                "url": "https://www.cisa.gov/news.xml",
            }
        ]
        data["github_releases"] = [
            "SigmaHQ/sigma",
            "elastic/detection-rules",
            "wazuh/wazuh",
        ]
    return data
