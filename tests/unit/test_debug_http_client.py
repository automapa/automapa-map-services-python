import io
from unittest.mock import MagicMock

from automapa_map_services.http.debug_client import DebugHttpClient
from automapa_map_services.http.request import HttpRequest
from automapa_map_services.http.response import HttpResponse


def _make_inner(response: HttpResponse) -> MagicMock:
    inner = MagicMock()
    inner.send.return_value = response
    return inner


def test_delegates_send_to_inner_client() -> None:
    request = HttpRequest(
        "POST", "https://example.com/v3/Foo/bar", {"Content-Type": "application/json"}, '{"x":1}'
    )
    response = HttpResponse(200, '{"status":"ok"}', {"Content-Type": "application/json"})
    inner = _make_inner(response)
    DebugHttpClient(inner, io.StringIO()).send(request)
    inner.send.assert_called_once_with(request)


def test_returns_response_from_inner() -> None:
    request = HttpRequest("POST", "https://example.com/v3/Foo/bar", {})
    response = HttpResponse(201, "created")
    inner = _make_inner(response)
    actual = DebugHttpClient(inner, io.StringIO()).send(request)
    assert actual is response


def test_writes_request_to_output() -> None:
    request = HttpRequest(
        "POST",
        "https://api.example.com/v3/Routes/route",
        {"Content-Type": "application/json"},
        '{"points":[]}',
    )
    response = HttpResponse(200, '{"result":"ok"}')
    output = io.StringIO()
    DebugHttpClient(_make_inner(response), output).send(request)
    written = output.getvalue()
    assert "=== REQUEST ===" in written
    assert "POST https://api.example.com/v3/Routes/route" in written
    assert "Content-Type: application/json" in written
    assert '{"points":[]}' in written


def test_writes_response_to_output() -> None:
    request = HttpRequest("POST", "https://example.com/", {})
    response = HttpResponse(200, '{"result":"ok"}', {"X-Custom": "value"})
    output = io.StringIO()
    DebugHttpClient(_make_inner(response), output).send(request)
    written = output.getvalue()
    assert "=== RESPONSE (200) ===" in written
    assert "X-Custom: value" in written
    assert '{"result":"ok"}' in written


def test_handles_empty_body_and_headers() -> None:
    request = HttpRequest("POST", "https://example.com/", {})
    response = HttpResponse(204, "")
    output = io.StringIO()
    DebugHttpClient(_make_inner(response), output).send(request)
    written = output.getvalue()
    assert "=== REQUEST ===" in written
    assert "=== RESPONSE (204) ===" in written
