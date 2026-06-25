"""Integration smoke tests for the Session endpoint (mirrors PHP SessionTest)."""

from __future__ import annotations

import hashlib
import json

from automapa_map_services.client import ApiClient
from automapa_map_services.config import Config
from automapa_map_services.http.builder import RequestBuilder
from automapa_map_services.http.urllib_client import UrllibHttpClient
from tests.integration.conftest import (
    acquire_session,
    assert_success_response,
    requires_live_api,
    send_request_with_retry,
)


@requires_live_api()
def test_get_salt_returns_non_empty_salt(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    live_config: Config,
) -> None:
    response = send_request_with_retry(
        live_request_builder, live_http_client, "Session", "getSalt", {"key": live_config.key}
    )
    assert_success_response(response)
    body = json.loads(response.body)
    salt = body["result"]["salt"]
    assert isinstance(salt, str) and salt


@requires_live_api()
def test_generate_session_returns_session_id(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    live_config: Config,
) -> None:
    session_id = acquire_session(
        live_request_builder, live_http_client, live_config.key, live_config.password
    )
    assert session_id


@requires_live_api()
def test_get_salt_via_facade_returns_non_empty_salt(
    live_api_client: ApiClient,
    live_config: Config,
) -> None:
    response = live_api_client.session().getSalt(live_config.key)
    assert response.status() == 200
    salt = response.data()["salt"]
    assert isinstance(salt, str) and salt


@requires_live_api()
def test_generate_session_via_facade_returns_session_id(
    live_api_client: ApiClient,
    live_config: Config,
) -> None:
    salt_response = live_api_client.session().getSalt(live_config.key)
    salt = str(salt_response.data()["salt"])
    pass_hash = hashlib.md5(
        (hashlib.md5(live_config.password.encode()).hexdigest() + salt).encode()
    ).hexdigest()
    response = live_api_client.session().generateSession(live_config.key, pass_hash)
    assert response.status() == 200
    assert response.data()["sessionId"]


@requires_live_api()
def test_salt_is_unique_on_each_call(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    live_config: Config,
) -> None:
    first = send_request_with_retry(
        live_request_builder, live_http_client, "Session", "getSalt", {"key": live_config.key}
    )
    second = send_request_with_retry(
        live_request_builder, live_http_client, "Session", "getSalt", {"key": live_config.key}
    )
    first_salt = str(json.loads(first.body)["result"]["salt"])
    second_salt = str(json.loads(second.body)["result"]["salt"])
    assert first_salt != second_salt, "Each getSalt call should return a unique salt"
