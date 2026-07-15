from cyberdailylog.collectors.nvd import extract_reference_urls


def test_nvd_reference_data_mapping_supported():
    assert extract_reference_urls({"referenceData": [{"url": "https://example.test"}]}) == ["https://example.test"]


def test_nvd_direct_reference_list_supported_and_deduplicated():
    refs = [
        {"url": "https://example.test"},
        {"url": ""},
        {"url": "https://example.test"},
        {"url": " https://two.test "},
    ]
    assert extract_reference_urls(refs) == ["https://example.test", "https://two.test"]


def test_nvd_malformed_references_return_empty_list():
    assert extract_reference_urls(None) == []
    assert extract_reference_urls({"referenceData": "bad"}) == []
    assert extract_reference_urls(["bad", {"url": None}]) == []
