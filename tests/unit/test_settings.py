from pathlib import Path

import pytest

from cyberdailylog.exceptions import ConfigurationError
from cyberdailylog.settings import load_yaml


def test_checked_in_sources_yaml_controls_source_configuration():
    data = load_yaml(Path("config/sources.yml"))
    assert len(data["rss_sources"]) == 2
    cisa = data["rss_sources"][0]
    red_hat = data["rss_sources"][1]
    assert cisa["owner"] == "Cybersecurity and Infrastructure Security Agency"
    assert cisa["category"] == "government_advisory"
    assert cisa["primary"] is True
    assert red_hat["enabled"] is False
    assert red_hat["reason"] == "disabled until parser supports OVAL safely"
    assert data["github_releases"] == ["SigmaHQ/sigma", "elastic/detection-rules", "wazuh/wazuh"]
    assert len(data["optional_future_sources"]) >= 5


def test_safe_yaml_parser_handles_nested_lists_booleans_and_quotes(tmp_path):
    path = tmp_path / "config.yml"
    path.write_text(
        """
root:
  enabled: true
  quoted: "value: with colon"
  owners:
    - blue
    - team
  sources:
    - name: one
      enabled: false
      metadata:
        tags:
          - cve
          - advisory
""",
        encoding="utf-8",
    )
    data = load_yaml(path)
    assert data["root"]["enabled"] is True
    assert data["root"]["quoted"] == "value: with colon"
    assert data["root"]["owners"] == ["blue", "team"]
    assert data["root"]["sources"][0]["enabled"] is False
    assert data["root"]["sources"][0]["metadata"]["tags"] == ["cve", "advisory"]


def test_empty_yaml_file_returns_empty_mapping(tmp_path):
    path = tmp_path / "empty.yml"
    path.write_text("", encoding="utf-8")
    assert load_yaml(path) == {}


def test_non_mapping_yaml_is_rejected(tmp_path):
    path = tmp_path / "list.yml"
    path.write_text("- one\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="top-level mapping"):
        load_yaml(path)


def test_malformed_yaml_raises_configuration_error(tmp_path):
    path = tmp_path / "bad.yml"
    path.write_text("root: [unterminated\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Malformed YAML"):
        load_yaml(path)
