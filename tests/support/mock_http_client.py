import json
from collections import deque
from typing import Any
from urllib.parse import urlparse

from automapa_map_services.exceptions import NetworkException
from automapa_map_services.http.request import HttpRequest
from automapa_map_services.http.response import HttpResponse


class MockHttpClient:
    """In-memory FIFO HTTP client for tests. Never makes real network calls."""

    def __init__(self) -> None:
        self._responses: dict[str, deque[HttpResponse | NetworkException]] = {}
        self._request_log: list[dict[str, Any]] = []

    def add_response(
        self,
        service: str,
        method: str,
        response_body: dict[str, Any],
        status_code: int = 200,
    ) -> None:
        self.queue(
            f"/v3/{service}/{method}",
            HttpResponse(
                status_code=status_code,
                body=json.dumps(response_body, separators=(",", ":")),
            ),
        )

    def add_raw_response(self, status_code: int, body: dict[str, Any]) -> None:
        self.queue(
            "*",
            HttpResponse(
                status_code=status_code,
                body=json.dumps(body, separators=(",", ":")),
            ),
        )

    def add_sequence(
        self,
        service: str,
        method: str,
        sequence: list[dict[str, Any]],
    ) -> None:
        path = f"/v3/{service}/{method}"
        for response in sequence:
            status_code = int(response["statusCode"])
            body = response["body"]
            if not isinstance(body, dict):
                raise TypeError("Mock response sequence body must be a dict")
            self.queue(
                path,
                HttpResponse(
                    status_code=status_code,
                    body=json.dumps(body, separators=(",", ":")),
                ),
            )

    def add_network_failure(self, message: str = "Connection refused", errno: int = 7) -> None:
        self._queue_item("*", NetworkException(message, errno))

    def queue(self, path: str, response: HttpResponse) -> None:
        self._queue_item(path, response)

    def send(self, request: HttpRequest) -> HttpResponse:
        path = urlparse(request.url).path
        payload = json.loads(request.body) if request.body else []
        self._request_log.append({"request": request, "path": path, "payload": payload})

        item = self._dequeue(path)
        if item is None:
            raise RuntimeError(f"No mock response queued for path: {path}")
        if isinstance(item, NetworkException):
            raise item
        return item

    def get_last_request_payload(self) -> Any:
        return self._last_log_entry()["payload"]

    def get_last_request(self) -> HttpRequest:
        request = self._last_log_entry()["request"]
        if not isinstance(request, HttpRequest):
            raise TypeError("Last request log entry is invalid")
        return request

    def get_all_request_payloads(self) -> list[Any]:
        return [entry["payload"] for entry in self._request_log]

    def get_request_count(self) -> int:
        return len(self._request_log)

    def assert_request_count(self, expected: int) -> None:
        actual = self.get_request_count()
        if actual != expected:
            raise AssertionError(f"Expected {expected} request(s), got {actual}.")

    def _queue_item(self, path: str, item: HttpResponse | NetworkException) -> None:
        self._responses.setdefault(path, deque()).append(item)

    def _dequeue(self, path: str) -> HttpResponse | NetworkException | None:
        if path in self._responses and self._responses[path]:
            return self._responses[path].popleft()
        if "*" in self._responses and self._responses["*"]:
            return self._responses["*"].popleft()
        return None

    def _last_log_entry(self) -> dict[str, Any]:
        if not self._request_log:
            raise RuntimeError("MockHttpClient: no requests have been made yet.")
        return self._request_log[-1]
