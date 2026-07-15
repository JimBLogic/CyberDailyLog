from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigurationError


class Settings:
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Malformed YAML in {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ConfigurationError(f"YAML configuration {path} must contain a top-level mapping")
    return loaded
