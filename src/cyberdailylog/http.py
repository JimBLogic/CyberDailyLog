"""Bounded and origin-restricted client for official CTI sources.

All network traffic is GET-only over HTTPS. Unlike urllib.request.urlopen(),
redirects are independently checked before the next request, protecting CTI
API keys from a compromised upstream redirect to an attacker-controlled host.
"""
from urllib.parse import urlsplit, urlencode
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.error import HTTPError, URLError
import json
import time
import random
from .exceptions import SourceError


def _source_origin(url, allowed_hosts):
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise SourceError("Invalid source URL") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or port not in (None, 443)
        or parsed.hostname not in allowed_hosts
    ):
        raise SourceError("Source URL is not an approved HTTPS origin")
    return parsed.hostname


class _SameOriginRedirects(HTTPRedirectHandler):
    """Only follow same-origin HTTPS redirects (never forward tokens off host)."""

    def __init__(self, allowed_hosts):
        super().__init__()
        self.allowed_hosts = allowed_hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        original = _source_origin(req.full_url, self.allowed_hosts)
        destination = _source_origin(newurl, self.allowed_hosts)
        if destination != original:
            raise SourceError("Cross-origin CTI redirect rejected")
        # Delegate urllib's bounded redirect handling and RFC method behavior.
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Response:
    def __init__(self, data, status, headers):
        self.content = data
        self.status_code = status
        self.headers = headers
        self.text = data.decode("utf-8")

    def json(self):
        return json.loads(self.text)


class SafeHttpClient:
    def __init__(self, allowed_hosts, user_agent="CyberDailyLog/2.0 (+https://github.com/JimBLogic/CyberDailyLog)"):
        self.allowed_hosts = frozenset(str(host).lower() for host in allowed_hosts)
        self.headers = {"User-Agent": user_agent}
        self._opener = build_opener(_SameOriginRedirects(self.allowed_hosts))

    def get(self, url, headers=None, params=None, expect_json=False, max_bytes=5_000_000):
        if not isinstance(url, str):
            raise SourceError("Source URL must be a string")
        if params:
            url += ("&" if "?" in url else "?") + urlencode(params)
        host = _source_origin(url, self.allowed_hosts)
        if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or not 0 < max_bytes <= 10_000_000:
            raise SourceError("Invalid source response byte limit")
        if len(url) > 8192:
            raise SourceError("Source URL exceeds safe length")
        request_headers = {**self.headers, **(headers or {})}
        # Header overrides must not redirect routing or bypass the origin check.
        if any(str(key).lower() in {"host", "proxy-authorization"} for key in request_headers):
            raise SourceError("Routing or proxy override header not permitted")
        req = Request(url, headers=request_headers)
        for attempt in range(3):
            try:
                with self._opener.open(req, timeout=20) as response:
                    # Revalidate the final URL even if urllib internals change.
                    if _source_origin(response.geturl(), self.allowed_hosts) != host:
                        raise SourceError("Cross-origin CTI response rejected")
                    data = response.read(max_bytes + 1)
                    ct = response.headers.get("content-type", "")
                    if len(data) > max_bytes:
                        raise SourceError("Response too large")
                    if expect_json and "json" not in ct.lower():
                        raise SourceError("Unexpected content type")
                    return Response(data, response.status, response.headers)
            except HTTPError as error:
                if error.code in (429, 500, 502, 503, 504) and attempt < 2:
                    try:
                        delay = float(error.headers.get("Retry-After") or 0)
                    except (TypeError, ValueError, OverflowError):
                        delay = 0
                    if not 0 < delay <= 5:
                        delay = 2**attempt + random.random()
                    time.sleep(min(delay, 5))
                    continue
                raise SourceError(f"HTTP {error.code} from {host}") from None
            except (URLError, TimeoutError, OSError) as error:
                raise SourceError(f"Source transport failed for {host}") from error
        raise SourceError(f"Source fetch retry budget exceeded for {host}")
