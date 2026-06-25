"""
Integration test infrastructure.

Tests in this directory are skipped by default when AUTOMAPA_API_KEY and
AUTOMAPA_API_PASSWORD are not set in the environment (or in a .env file at
the project root). Set those variables to run live API tests.

Optional: AUTOMAPA_API_REQUIRED_ACCESS - comma-separated list of suite names
whose tests are mandatory (not skipped on permission errors). Example:
  AUTOMAPA_API_REQUIRED_ACCESS=geocoder,autocomplete
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import pytest

from automapa_map_services.client import ApiClient
from automapa_map_services.config import Config
from automapa_map_services.exceptions import ServerException, SessionException
from automapa_map_services.http.builder import RequestBuilder
from automapa_map_services.http.response import HttpResponse
from automapa_map_services.http.urllib_client import UrllibHttpClient

_BASE_URL = "https://api.automapa.pl/"
_VERSION = "v3"
_TIMEOUT = 10


def _load_env_file() -> None:
    """Load .env from the project root into os.environ if not already set."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def _get_required_access() -> list[str]:
    raw = os.environ.get("AUTOMAPA_API_REQUIRED_ACCESS", "")
    return [s.strip() for s in raw.split(",") if s.strip()] if raw else []


def requires_live_api(suite_name: str | None = None) -> pytest.MarkDecorator:
    """
    Pytest mark that skips the test when live API credentials are absent.

    Usage:
        @requires_live_api()
        def test_something(live_api_client): ...

        @requires_live_api("geocoder")
        def test_geocode(live_api_client): ...
    """
    _load_env_file()
    reasons: list[str] = []

    if not os.environ.get("AUTOMAPA_API_KEY"):
        reasons.append("AUTOMAPA_API_KEY not set")
    if not os.environ.get("AUTOMAPA_API_PASSWORD"):
        reasons.append("AUTOMAPA_API_PASSWORD not set")

    if not reasons and suite_name is not None:
        required = _get_required_access()
        if required and suite_name not in required:
            reasons.append(f"Suite '{suite_name}' not listed in AUTOMAPA_API_REQUIRED_ACCESS")

    if reasons:
        return pytest.mark.skip(reason="; ".join(reasons))
    return pytest.mark.live_api()


@pytest.fixture(scope="session")
def live_config() -> Config:
    """Session-scoped Config built from environment variables."""
    _load_env_file()
    key = os.environ.get("AUTOMAPA_API_KEY", "")
    password = os.environ.get("AUTOMAPA_API_PASSWORD", "")
    if not key or not password:
        pytest.skip("AUTOMAPA_API_KEY / AUTOMAPA_API_PASSWORD not set - skipping integration tests")
    return Config(
        key=key,
        password=password,
        base_url=_BASE_URL,
        version=_VERSION,
        timeout_seconds=_TIMEOUT,
    )


@pytest.fixture(scope="session")
def live_http_client() -> UrllibHttpClient:
    return UrllibHttpClient(timeout=_TIMEOUT)


@pytest.fixture(scope="session")
def live_api_client(live_config: Config) -> ApiClient:
    """Ready-to-use ApiClient wired to the real Automapa API."""
    return ApiClient(config=live_config)


@pytest.fixture(scope="session")
def live_request_builder() -> RequestBuilder:
    return RequestBuilder(base_url=_BASE_URL, version=_VERSION)


def build_api_client(default_format: str = "native") -> ApiClient:
    """Helper for tests that need a fresh per-test client."""
    _load_env_file()
    return ApiClient(
        config=Config(
            key=os.environ.get("AUTOMAPA_API_KEY", ""),
            password=os.environ.get("AUTOMAPA_API_PASSWORD", ""),
            timeout_seconds=_TIMEOUT,
            default_format=default_format,
        )
    )


def acquire_session(
    request_builder: RequestBuilder,
    http_client: UrllibHttpClient,
    api_key: str,
    api_password: str,
) -> str:
    """Manually acquire a session ID from the API (mirrors PHP acquireSession())."""
    import hashlib

    salt_request = request_builder.build("Session", "getSalt", {"key": api_key})
    salt_response = http_client.send(salt_request)
    salt_body: dict[str, Any] = json.loads(salt_response.body)
    salt: str = salt_body["result"]["salt"]

    hashed = hashlib.md5(
        (hashlib.md5(api_password.encode()).hexdigest() + salt).encode()
    ).hexdigest()

    session_request = request_builder.build(
        "Session", "generateSession", {"key": api_key, "pass": hashed}
    )
    session_response = http_client.send(session_request)
    session_body: dict[str, Any] = json.loads(session_response.body)
    return str(session_body["result"]["sessionId"])


def assert_success_response(response: HttpResponse) -> None:
    """Assert response is 2xx with a 'result' key in the body."""
    assert response.is_success, (
        f"Expected 2xx response, got HTTP {response.status_code}. Body: {response.body}"
    )
    decoded: Any = json.loads(response.body)
    assert isinstance(decoded, dict), "Response body is not a JSON object"
    assert "result" in decoded, f"Response missing 'result' key. Body: {response.body}"


def skip_if_no_permission(response: HttpResponse) -> None:
    """Skip the current test if the API returned 403 with a 'no permission' message."""
    if response.status_code == 403:
        try:
            body: Any = json.loads(response.body)
            message = body.get("message", "") if isinstance(body, dict) else ""
        except (json.JSONDecodeError, AttributeError):
            message = ""
        if "no permission" in message:
            pytest.skip(
                f"API key lacks permission for this endpoint - skipping. Body: {response.body}"
            )


_RATE_LIMIT_RETRY_WAIT = 30


def send_request(
    request_builder: RequestBuilder,
    http_client: UrllibHttpClient,
    service: str,
    method: str,
    params: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> HttpResponse:
    """Build and send a raw API request (mirrors PHP sendRequest())."""
    request = request_builder.build(service, method, params or {}, session_id)
    return http_client.send(request)


def send_request_with_retry(
    request_builder: RequestBuilder,
    http_client: UrllibHttpClient,
    service: str,
    method: str,
    params: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> HttpResponse:
    """Send a raw API request, retrying once after ~30 s on rate limit (HTTP 429)."""
    response = send_request(request_builder, http_client, service, method, params, session_id)
    if response.status_code == 429:
        time.sleep(_RATE_LIMIT_RETRY_WAIT)
        response = send_request(request_builder, http_client, service, method, params, session_id)
    return response


def skip_on_permission_error(exc: Exception) -> None:
    """Skip the current test when the exception indicates 'no permission'."""
    if isinstance(exc, SessionException) and "no permission" in str(exc):
        pytest.skip(f"API key lacks permission for this endpoint: {exc}")


def skip_on_server_error(exc: Exception) -> None:
    """Skip the current test when a server error suggests no API access."""
    if isinstance(exc, ServerException):
        pytest.skip(f"Endpoint returned server error - likely no API access: {exc}")
