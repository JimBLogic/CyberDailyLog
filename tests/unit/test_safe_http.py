"""Deterministic HTTP transport guard tests: no external connections are made."""

from email.message import Message
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.request import Request

import pytest

from cyberdailylog.exceptions import SourceError
from cyberdailylog.http import SafeHttpClient, _SameOriginRedirects, _source_origin


class FakeResponse:
    def __init__(self, url="https://api.github.com/advisories", payload=b"{}", content_type="application/json"):
        self._url = url
        self._body = BytesIO(payload)
        self.headers = Message()
        self.headers["content-type"] = content_type
        self.status = 200

    def geturl(self):
        return self._url

    def read(self, max_length):
        return self._body.read(max_length)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


@pytest.mark.parametrize(
    "url",
    [
        "http://api.github.com/advisories",
        "ftp://api.github.com/advisories",
        "https://evil.example/advisories",
        "https://api.github.com.evil.example/advisories",
        "https://api.github.com:8443/advisories",
        "https://user:password@api.github.com/advisories",
        "https://api.github.com/advisories#credentials",
        "https://[unmatched/advisories",
        "https://api.github.com:invalid/advisories",
    ],
)
def test_initial_url_must_be_explicit_allowlisted_https(url):
    with pytest.raises(SourceError):
        _source_origin(url, {"api.github.com"})


@pytest.mark.parametrize(
    "target",
    [
        "https://evil.example/steal",
        "https://api.first.org/steal",  # also allowlisted, but credentials MUST stay on origin
        "http://api.github.com/advisories",
        "https://api.github.com:444/steal",
        "https://user@api.github.com/steal",
    ],
)
def test_redirects_cannot_leak_api_key_to_other_origin_or_plaintext(target):
    handler = _SameOriginRedirects({"api.github.com", "api.first.org"})
    original = Request("https://api.github.com/advisories", headers={"Authorization": "Bearer SECRET"})
    with pytest.raises(SourceError):
        handler.redirect_request(original, None, 302, "Found", {}, target)


def test_https_same_host_redirect_works_and_keeps_origin():
    handler = _SameOriginRedirects({"api.github.com"})
    req = Request("https://api.github.com/advisories")
    next_req = handler.redirect_request(req, None, 302, "Found", {}, "https://api.github.com/advisories?after=one")
    assert next_req.full_url == "https://api.github.com/advisories?after=one"


def test_http_client_validates_final_url_even_if_upstream_library_redirects(monkeypatch):
    client = SafeHttpClient({"api.github.com", "api.first.org"})
    monkeypatch.setattr(
        client._opener,
        "open",
        lambda *_args, **_kwargs: FakeResponse("https://api.first.org/secret"),
    )
    with pytest.raises(SourceError, match="Cross-origin"):
        client.get("https://api.github.com/advisories", headers={"Authorization": "Bearer SECRET"})


def test_client_accepts_bounded_official_json_without_outbound_network(monkeypatch):
    client = SafeHttpClient({"api.github.com"})
    seen = []

    def fake_open(request, timeout):
        seen.append((request.full_url, request.get_header("Authorization"), timeout))
        return FakeResponse(payload=b'{"items":[]}')

    monkeypatch.setattr(client._opener, "open", fake_open)
    result = client.get(
        "https://api.github.com/advisories",
        headers={"Authorization": "Bearer TEST"},
        params={"per_page": 20},
        expect_json=True,
    )
    assert result.json() == {"items": []}
    assert seen == [("https://api.github.com/advisories?per_page=20", "Bearer TEST", 20)]


def test_invalid_body_headers_and_limits_fail_closed_without_network(monkeypatch):
    client = SafeHttpClient({"api.github.com"})
    attempts = []
    monkeypatch.setattr(client._opener, "open", lambda *_args, **_kwargs: attempts.append(1))
    for args in [
        {"max_bytes": 0},
        {"max_bytes": 12_000_000},
        {"headers": {"Host": "evil.example"}},
        {"headers": {"Proxy-Authorization": "secret"}},
    ]:
        with pytest.raises(SourceError):
            client.get("https://api.github.com/advisories", **args)
    assert attempts == []


def test_responses_reject_wrong_content_type_or_more_than_declared_limit(monkeypatch):
    client = SafeHttpClient({"api.github.com"})
    monkeypatch.setattr(
        client._opener,
        "open",
        lambda *_args, **_kwargs: FakeResponse(payload=b"<html>oops</html>", content_type="text/html"),
    )
    with pytest.raises(SourceError, match="content type"):
        client.get("https://api.github.com/advisories", expect_json=True)
    with pytest.raises(SourceError, match="too large"):
        client.get("https://api.github.com/advisories", max_bytes=4)


def test_retry_after_invalid_string_falls_back_to_bounded_retry(monkeypatch):
    client = SafeHttpClient({"api.github.com"})
    calls = []
    delays = []
    headers = Message()
    headers["Retry-After"] = "garbage"

    def fake_open(request, timeout):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise HTTPError(request.full_url, 429, "Too Many Requests", headers, None)
        return FakeResponse()

    monkeypatch.setattr(client._opener, "open", fake_open)
    monkeypatch.setattr("cyberdailylog.http.time.sleep", lambda s: delays.append(s))
    assert client.get("https://api.github.com/advisories").json() == {}
    assert len(calls) == 2
    assert len(delays) == 1 and 0 < delays[0] <= 5


def test_connection_errors_omit_credentials_in_collector_health(monkeypatch):
    client = SafeHttpClient({"api.github.com"})

    def fake_fail(_request, timeout):
        raise URLError("Bearer SECRET")

    monkeypatch.setattr(client._opener, "open", fake_fail)
    with pytest.raises(SourceError, match="Source transport failed") as info:
        client.get("https://api.github.com/advisories", headers={"Authorization": "Bearer SECRET"})
    assert "SECRET" not in str(info.value)
