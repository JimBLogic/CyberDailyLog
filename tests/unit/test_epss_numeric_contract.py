import pytest

from cyberdailylog.collectors.epss import _extract_scores


@pytest.mark.parametrize("field", ["epss", "percentile"])
@pytest.mark.parametrize("value", [True, False, None, "NaN", "Infinity", "-Infinity", -0.01, 1.01])
def test_invalid_probabilities_are_rejected(field, value):
    row = {"cve": "CVE-2026-12345", "epss": "0.5", "percentile": "0.9", field: value}
    assert _extract_scores({"data": [row]}) == ({}, 1)


@pytest.mark.parametrize("value", [0, 1, "0.125"])
def test_valid_probability_boundaries_are_preserved(value):
    row = {"cve": "CVE-2026-12345", "epss": value, "percentile": value}
    scores, rejected = _extract_scores({"data": [row]})
    assert rejected == 0
    assert scores["CVE-2026-12345"]["epss_score"] == float(value)
    assert scores["CVE-2026-12345"]["epss_percentile"] == float(value)
