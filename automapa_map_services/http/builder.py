import json

from .request import HttpRequest


class RequestBuilder:
    def __init__(self, base_url: str, version: str = "v3") -> None:
        self._base_url = base_url.rstrip("/")
        self._version = version

    def build(
        self,
        service: str,
        method: str,
        params: dict[str, object] | None = None,
        session_id: str | None = None,
    ) -> HttpRequest:
        url = f"{self._base_url}/{self._version}/{service}/{method}"
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if session_id is not None:
            headers["Session-Id"] = session_id

        body = "[]" if not params else json.dumps(params, separators=(",", ":"))
        return HttpRequest(method="POST", url=url, headers=headers, body=body)
