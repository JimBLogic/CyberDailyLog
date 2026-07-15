import json
import random
import time
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from .exceptions import SourceError


class Response:
    def __init__(self, data: bytes, status: int, headers: Any) -> None:
        self.content = data
        self.status_code = status
        self.headers = headers
        self.text = data.decode("utf-8")

    def json(self) -> Any:
        return json.loads(self.text)


class SafeHttpClient:
    def __init__(
        self,
        allowed_hosts: set[str],
        user_agent: str = "CyberDailyLog/2.0 (+https://github.com/JimBLogic/CyberDailyLog)",
    ) -> None:
        self.allowed_hosts = allowed_hosts
        self.headers = {"User-Agent": user_agent}

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        expect_json: bool = False,
        max_bytes: int = 5_000_000,
    ) -> Response:
        if params:
            separator = "&" if "?" in url else "?"
            url += separator + urlencode(params)

        host = urlparse(url).hostname or ""
        if host not in self.allowed_hosts:
            raise SourceError(f"Host not allowlisted: {host}")

        request = Request(url, headers={**self.headers, **(headers or {})})
        for attempt in range(3):
            try:
                with urlopen(request, timeout=20) as response:  # noqa: S310
                    data = response.read(max_bytes + 1)
                    content_type = response.headers.get("content-type", "")
                    if len(data) > max_bytes:
                        raise SourceError("Response too large")
                    if expect_json and "json" not in content_type.lower():
                        raise SourceError("Unexpected content type")
                    return Response(data, response.status, response.headers)
            except HTTPError as exc:
                retryable = exc.code in {429, 500, 502, 503, 504}
                if retryable and attempt < 2:
                    retry_after = float(exc.headers.get("Retry-After") or 0)
                    delay = retry_after or 2**attempt + random.random()
                    time.sleep(min(delay, 5))
                    continue
                raise SourceError(f"HTTP {exc.code} from {host}") from exc

        raise SourceError(f"Request failed for {host}")
