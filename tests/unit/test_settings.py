from pathlib import Path

import pytest

from cyberdailylog.exceptions import ConfigurationError
from cyberdailylog.settings import load_yaml


def test_checked_in_sources_yaml_controls_source_configuration():
    data = load_yaml(Path("config/sources.yml"))
    rss_sources = {source["name"]: source for source in data["rss_sources"]}

    cisa = rss_sources["CISA Cybersecurity Advisories"]
    red_hat = rss_sources["Red Hat Security Advisories"]
    krebs = rss_sources["Krebs on Security"]
    sans = rss_sources["SANS Internet Storm Center Handler's Diary"]

    assert cisa["owner"] == "Cybersecurity and Infrastructure Security Agency"
    assert cisa["category"] == "government_advisory"
    assert cisa["primary"] is True
    assert cisa["enabled"] is False
    assert red_hat["enabled"] is False
    assert red_hat["reason"] == "disabled until parser supports OVAL safely"
    assert krebs["health_name"] == "rss_krebs"
    assert krebs["category"] == "expert_commentary"
    assert sans["health_name"] == "rss_sans_isc"
    assert sans["category"] == "analyst_diary"
    assert data["hacker_news"]["enabled"] is True
    assert data["hacker_news"]["minimum_score"] == 80
    assert data["hacker_news"]["minimum_comments"] == 20
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
