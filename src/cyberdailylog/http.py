from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json
import time
import random
from .exceptions import SourceError


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
        self.allowed_hosts = allowed_hosts
        self.headers = {"User-Agent": user_agent}

    def get(self, url, headers=None, params=None, expect_json=False, max_bytes=5_000_000):
        if params:
            url += ("&" if "?" in url else "?") + urlencode(params)
        host = urlparse(url).hostname or ""
        if host not in self.allowed_hosts:
            raise SourceError(f"Host not allowlisted: {host}")
        req = Request(url, headers={**self.headers, **(headers or {})})
        for attempt in range(3):
            try:
                with urlopen(req, timeout=20) as r:
                    data = r.read(max_bytes + 1)
                    ct = r.headers.get("content-type", "")
                    if len(data) > max_bytes:
                        raise SourceError("Response too large")
                    if expect_json and "json" not in ct.lower():
                        raise SourceError("Unexpected content type")
                    return Response(data, r.status, r.headers)
            except HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(min(float(e.headers.get("Retry-After") or 0) or 2**attempt + random.random(), 5))
                    continue
                raise SourceError(f"HTTP {e.code} from {host}")
