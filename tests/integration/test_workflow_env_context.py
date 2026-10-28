"""Status-check functions are legal in if, not environment expressions."""

from pathlib import Path
import re

import yaml

STATUS_FUNCTION = re.compile(r"\b(?:success|failure|always|cancelled)\s*\(")


def invalid_environment_expressions(node):
    invalid = []
    if isinstance(node, dict):
        env = node.get("env")
        if isinstance(env, dict):
            for name, value in env.items():
                for expression in re.findall(r"\$\{\{(.*?)\}\}", str(value), re.DOTALL):
                    if STATUS_FUNCTION.search(expression):
                        invalid.append(name)
        for value in node.values():
            invalid.extend(invalid_environment_expressions(value))
    elif isinstance(node, list):
        for value in node:
            invalid.extend(invalid_environment_expressions(value))
    return invalid


def test_status_functions_are_rejected_in_env_but_allowed_in_if():
    assert invalid_environment_expressions({"env": {"FLAG": "${{ success() }}"}}) == ["FLAG"]
    assert (
        invalid_environment_expressions(
            {"if": "${{ always() }}", "env": {"FLAG": "${{ steps.read_timing.outcome == 'success' }}"}}
        )
        == []
    )


def test_repository_environment_expressions_use_supported_contexts():
    for path in Path(".github/workflows").iterdir():
        if path.suffix in {".yml", ".yaml"}:
            assert invalid_environment_expressions(yaml.safe_load(path.read_text())) == [], str(path)
