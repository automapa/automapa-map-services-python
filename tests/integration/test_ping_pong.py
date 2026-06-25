"""Integration smoke tests for the PingPong endpoint (mirrors PHP PingPongTest)."""

from __future__ import annotations

import json

import pytest

from automapa_map_services.config import Config
from automapa_map_services.http.builder import RequestBuilder
from automapa_map_services.http.urllib_client import UrllibHttpClient
from tests.integration.conftest import (
    acquire_session,
    assert_success_response,
    build_api_client,
    requires_live_api,
    send_request_with_retry,
    skip_if_no_permission,
    skip_on_permission_error,
    skip_on_server_error,
)


@pytest.fixture(scope="module")
def live_session_id(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    live_config: Config,
) -> str:
    """Session ID acquired once per test module to reduce API calls."""
    return acquire_session(
        live_request_builder, live_http_client, live_config.key, live_config.password
    )


@requires_live_api("pingpong")
def test_ping_returns_pong(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    live_session_id: str,
) -> None:
    response = send_request_with_retry(
        live_request_builder,
        live_http_client,
        "PingPong",
        "ping",
        {"msg": "ping"},
        live_session_id,
    )
    skip_if_no_permission(response)
    assert_success_response(response)
    body = json.loads(response.body)
    assert body["result"]["msg"] == "pong"


@requires_live_api("pingpong")
def test_ping_fails_without_session_header(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
) -> None:
    response = send_request_with_retry(
        live_request_builder, live_http_client, "PingPong", "ping", {"msg": "ping"}, None
    )
    assert not response.is_success, "PingPong/ping should fail without Session-Id header"


@requires_live_api("pingpong")
def test_ping_via_facade_returns_pong() -> None:
    client = build_api_client()
    try:
        response = client.ping_pong().ping("ping")
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise
    assert response.status() == 200
    assert response.data()["msg"] == "pong"
