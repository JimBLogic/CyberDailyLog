"""Deterministic HTTP transport guard tests: no external connections are made."""

from email.message import Message
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener
from urllib.response import addinfourl

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


class FixtureHTTPS(HTTPSHandler):
    """Exercise urllib's real redirect machinery without network or TLS bypass."""

    def __init__(self, routes):
        super().__init__()
        self.routes = routes
        self.requests = []

    def https_open(self, request):
        self.requests.append((request.full_url, request.get_header("Apikey")))
        status, location = self.routes.get(request.full_url, (200, None))
        headers = Message()
        headers["content-type"] = "application/json"
        if location:
            headers["Location"] = location
        response = addinfourl(BytesIO(b"{}"), headers, request.full_url, status)
        response.msg = "Found" if location else "OK"
        return response


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
@pytest.mark.parametrize("destination", ["https://unapproved.example/steal", "https://api.first.org/steal"])
def test_real_redirect_chain_never_sends_key_off_origin(status, destination):
    start = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    intermediate = start + "?after=one"
    transport = FixtureHTTPS({start: (status, intermediate), intermediate: (status, destination)})
    client = SafeHttpClient({"services.nvd.nist.gov", "api.first.org"})
    client._opener = build_opener(ProxyHandler({}), transport, _SameOriginRedirects(client.allowed_hosts))
    with pytest.raises(SourceError):
        client.get(start, headers={"apiKey": "synthetic-test-only"})
    assert transport.requests == [(start, "synthetic-test-only"), (intermediate, "synthetic-test-only")]
    assert all(urlsplit(url).hostname == "services.nvd.nist.gov" for url, _ in transport.requests)


def test_real_same_origin_redirect_still_delivers_valid_json():
    start = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    target = start + "?after=one"
    transport = FixtureHTTPS({start: (302, target)})
    client = SafeHttpClient({"services.nvd.nist.gov"})
    client._opener = build_opener(ProxyHandler({}), transport, _SameOriginRedirects(client.allowed_hosts))
    assert client.get(start, expect_json=True).json() == {}
    assert [url for url, _ in transport.requests] == [start, target]


@pytest.mark.parametrize("suffix", ["/\nsecret", "/\tsecret", "/bad path", "/\x7fsecret", "/" + "x" * 8192])
def test_initial_and_redirect_urls_reject_controls_and_oversized_inputs(suffix):
    url = "https://api.github.com" + suffix
    with pytest.raises(SourceError):
        _source_origin(url, {"api.github.com"})
    handler = _SameOriginRedirects({"api.github.com"})
    with pytest.raises(SourceError):
        handler.redirect_request(Request("https://api.github.com/advisories"), None, 302, "Found", {}, url)


@pytest.mark.parametrize("retry_after", ["-10", "nan", "inf", "garbage", "0"])
def test_retry_budget_stays_bounded_and_exhaustion_fails_without_secrets(monkeypatch, retry_after):
    client = SafeHttpClient({"api.github.com"})
    calls, delays = [], []
    headers = Message()
    headers["Retry-After"] = retry_after

    def unavailable(request, timeout):
        calls.append(request.full_url)
        raise HTTPError(request.full_url, 503, "SECRET", headers, BytesIO(b"SECRET"))

    monkeypatch.setattr(client._opener, "open", unavailable)
    monkeypatch.setattr("cyberdailylog.http.time.sleep", delays.append)
    with pytest.raises(SourceError, match="HTTP 503") as info:
        client.get("https://api.github.com/advisories", headers={"Authorization": "Bearer SECRET"})
    assert len(calls) == 3 and len(delays) == 2
    assert all(0 < delay <= 5 for delay in delays)
    assert "SECRET" not in str(info.value)


def test_transient_transport_retries_same_origin_with_provider_interval(monkeypatch):
    client = SafeHttpClient({"api.github.com"})
    calls, delays = [], []

    def temporary(request, timeout):
        calls.append(request.full_url)
        if len(calls) < 3:
            raise TimeoutError("SECRET")
        return FakeResponse()

    monkeypatch.setattr(client._opener, "open", temporary)
    monkeypatch.setattr("cyberdailylog.http.time.sleep", delays.append)
    assert client.get("https://api.github.com/advisories", retry_interval=6).json() == {}
    assert len(calls) == 3 and delays == [6, 6]


def test_certificate_failure_is_not_retried_and_never_relaxes_tls(monkeypatch):
    import ssl

    client = SafeHttpClient({"api.github.com"})
    calls, delays = [], []

    def invalid(request, timeout):
        calls.append(request.full_url)
        raise URLError(ssl.SSLCertVerificationError("certificate invalid"))

    monkeypatch.setattr(client._opener, "open", invalid)
    monkeypatch.setattr("cyberdailylog.http.time.sleep", delays.append)
    with pytest.raises(SourceError):
        client.get("https://api.github.com/advisories")
    assert len(calls) == 1 and delays == []


@pytest.mark.parametrize("retry_after", ["30", "120"])
def test_retry_after_is_honoured_or_fails_without_early_retry(monkeypatch, retry_after):
    client = SafeHttpClient({"api.github.com"})
    headers = Message()
    headers["Retry-After"] = retry_after
    calls, delays = [], []

    def busy(request, timeout):
        calls.append(request.full_url)
        raise HTTPError(request.full_url, 429, "busy", headers, None)

    monkeypatch.setattr(client._opener, "open", busy)
    monkeypatch.setattr("cyberdailylog.http.time.sleep", delays.append)
    with pytest.raises(SourceError):
        client.get("https://api.github.com/advisories", retry_interval=6)
    assert delays == ([30, 30] if retry_after == "30" else [])
    assert len(calls) == (3 if retry_after == "30" else 1)


def test_http_date_retry_after_uses_provider_time_without_early_request(monkeypatch):
    from datetime import datetime, timezone

    client = SafeHttpClient({"api.github.com"})
    calls = []
    delays = []
    headers = Message()
    headers["Retry-After"] = "Mon, 19 Oct 2026 12:00:30 GMT"
    monkeypatch.setattr(
        "cyberdailylog.http.time.time", lambda: datetime(2026, 10, 19, 12, tzinfo=timezone.utc).timestamp()
    )

    def busy(request, timeout):
        calls.append(1)
        if len(calls) == 1:
            raise HTTPError(request.full_url, 429, "busy", headers, None)
        return FakeResponse()

    monkeypatch.setattr(client._opener, "open", busy)
    monkeypatch.setattr("cyberdailylog.http.time.sleep", delays.append)
    assert client.get("https://api.github.com/advisories").json() == {}
    assert delays == [30]


def test_interrupted_response_retries_without_returning_partial_body(monkeypatch):
    from http.client import IncompleteRead

    client = SafeHttpClient({"api.github.com"})
    calls = []

    def interrupted(request, timeout):
        calls.append(1)
        if len(calls) == 1:
            raise IncompleteRead(b"partial", 10)
        return FakeResponse()

    monkeypatch.setattr(client._opener, "open", interrupted)
    monkeypatch.setattr("cyberdailylog.http.time.sleep", lambda _: None)
    assert client.get("https://api.github.com/advisories").json() == {} and len(calls) == 2
