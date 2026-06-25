from __future__ import annotations

import pytest

from automapa_map_services.client import ApiClient
from automapa_map_services.config import Config
from automapa_map_services.exceptions import (
    AuthenticationException,
    NetworkException,
    ServerException,
)
from automapa_map_services.formatter.google import GoogleFormatter
from automapa_map_services.formatter.registry import FormatterRegistry
from automapa_map_services.response.api_response import ApiResponse
from automapa_map_services.session.manager import SessionManager
from automapa_map_services.session.storage import InMemorySessionStorage
from tests.support.mock_http_client import MockHttpClient


def _make_client(mock_http: MockHttpClient, default_format: str = "native") -> ApiClient:
    storage = InMemorySessionStorage()
    storage.store("test-session-id")
    config = Config(key="test-key", password="test-pass", default_format=default_format)
    return ApiClient(
        config=config,
        http_client=mock_http,
        session_manager=SessionManager(config, mock_http, storage),
    )


@pytest.fixture
def mock_http() -> MockHttpClient:
    return MockHttpClient()


@pytest.fixture
def client(mock_http: MockHttpClient) -> ApiClient:
    return _make_client(mock_http)


def test_call_dispatches_to_correct_endpoint_url(
    mock_http: MockHttpClient, client: ApiClient
) -> None:
    mock_http.add_response("Geocoder", "geocode", {"result": {"city": "Warszawa"}})

    client.call("Geocoder", "geocode", {"address": {"city": "Warszawa"}})

    assert "/v3/Geocoder/geocode" in mock_http.get_last_request().url


def test_call_passes_params_as_json_body(mock_http: MockHttpClient, client: ApiClient) -> None:
    mock_http.add_response("Geocoder", "geocode", {"result": []})

    client.call("Geocoder", "geocode", {"address": {"city": "Test"}, "maxResults": 5})

    payload = mock_http.get_last_request_payload()
    assert payload["address"] == {"city": "Test"}
    assert payload["maxResults"] == 5


def test_call_passes_unknown_params_flat(mock_http: MockHttpClient, client: ApiClient) -> None:
    mock_http.add_response("Geocoder", "geocode", {"result": []})

    client.call("Geocoder", "geocode", {"unknownFutureParam": True, "anotherUnknown": 42})

    payload = mock_http.get_last_request_payload()
    assert payload["unknownFutureParam"] is True
    assert payload["anotherUnknown"] == 42


def test_call_returns_api_response_with_raw(mock_http: MockHttpClient, client: ApiClient) -> None:
    fixture = {"result": {"quality": 9, "x": 21.007, "y": 52.182}}
    mock_http.add_response("Geocoder", "geocode", fixture)

    response = client.call("Geocoder", "geocode", {})

    assert isinstance(response, ApiResponse)
    assert response.raw() == fixture


def test_data_returns_unwrapped_result(mock_http: MockHttpClient, client: ApiClient) -> None:
    result_data = {"quality": 9, "city": "Warszawa"}
    mock_http.add_response("Geocoder", "geocode", {"result": result_data})

    response = client.call("Geocoder", "geocode", {})

    assert response.data() == result_data


def test_call_throws_authentication_exception_on_401(
    mock_http: MockHttpClient, client: ApiClient
) -> None:
    mock_http.add_raw_response(401, {"message": "Invalid API key"})

    with pytest.raises(AuthenticationException):
        client.call("Geocoder", "geocode", {})


def test_call_throws_server_exception_on_500(mock_http: MockHttpClient, client: ApiClient) -> None:
    mock_http.add_raw_response(500, {"message": "Internal error"})

    with pytest.raises(ServerException):
        client.call("Geocoder", "geocode", {})


def test_request_uses_provided_path(mock_http: MockHttpClient, client: ApiClient) -> None:
    mock_http.add_raw_response(200, {"result": []})

    client.request("POST", "/v3/Foo/bar", {"x": 1})

    assert "/v3/Foo/bar" in mock_http.get_last_request().url


def test_request_passes_params_as_json_body(mock_http: MockHttpClient, client: ApiClient) -> None:
    mock_http.add_raw_response(200, {"result": "ok"})

    client.request("POST", "/v3/Foo/bar", {"x": 1})

    payload = mock_http.get_last_request_payload()
    assert payload["x"] == 1


def test_geocoder_factory_returns_geocoder_instance(client: ApiClient) -> None:
    from automapa_map_services.endpoints.geocoder import Geocoder

    assert isinstance(client.geocoder(), Geocoder)


def test_ping_pong_factory_returns_ping_pong_instance(client: ApiClient) -> None:
    from automapa_map_services.endpoints.ping_pong import PingPong

    assert isinstance(client.pingPong(), PingPong)


def test_ping_pong_alias_returns_ping_pong_instance(client: ApiClient) -> None:
    from automapa_map_services.endpoints.ping_pong import PingPong

    assert isinstance(client.ping_pong(), PingPong)


def test_road_permit_alias_returns_road_permit_instance(client: ApiClient) -> None:
    from automapa_map_services.endpoints.road_permit import RoadPermit

    assert isinstance(client.road_permit(), RoadPermit)


def test_meta_contains_service_and_method(mock_http: MockHttpClient, client: ApiClient) -> None:
    mock_http.add_response("PingPong", "ping", {"result": "pong"})

    response = client.call("PingPong", "ping", {})

    assert response.meta()["service"] == "PingPong"
    assert response.meta()["method"] == "ping"


def test_call_injects_session_id_header_for_session_requiring_endpoints(
    mock_http: MockHttpClient, client: ApiClient
) -> None:
    mock_http.add_response("Geocoder", "geocode", {"result": {"city": "Warszawa"}})

    client.call("Geocoder", "geocode", {})

    headers = mock_http.get_last_request().headers
    assert "Session-Id" in headers
    assert headers["Session-Id"] == "test-session-id"


def test_call_does_not_send_format_param_to_api(
    mock_http: MockHttpClient, client: ApiClient
) -> None:
    mock_http.add_response("Geocoder", "geocode", {"result": {"city": "Wrocław"}})

    client.call("Geocoder", "geocode", {"address": {"city": "Wrocław"}, "format": "google"})

    payload = mock_http.get_last_request_payload()
    assert "format" not in payload
    assert "address" in payload


def test_call_uses_native_format_by_default(mock_http: MockHttpClient, client: ApiClient) -> None:
    result_data = {"city": "Poznań", "x": 16.92, "y": 52.40}
    mock_http.add_response("Geocoder", "geocode", {"result": result_data})

    response = client.call("Geocoder", "geocode", {})

    assert response.data() == result_data


def test_call_applies_google_formatter_when_configured(mock_http: MockHttpClient) -> None:
    registry = FormatterRegistry()
    registry.register("google", GoogleFormatter())

    storage = InMemorySessionStorage()
    storage.store("test-session-id")
    config = Config(key="test-key", password="test-pass", default_format="google")
    google_client = ApiClient(
        config=config,
        http_client=mock_http,
        session_manager=SessionManager(config, mock_http, storage),
        formatter_registry=registry,
    )

    mock_http.add_response(
        "Geocoder",
        "geocode",
        {
            "result": {
                "x": 21.0122,
                "y": 52.2297,
                "city": "Warszawa",
                "quality": 9,
            }
        },
    )

    response = google_client.call("Geocoder", "geocode", {})
    data = response.data()

    assert isinstance(data, dict)
    assert data["status"] == "OK"
    assert "results" in data
    assert "_raw" in data


def test_network_exception_propagates_through_call(
    mock_http: MockHttpClient, client: ApiClient
) -> None:
    mock_http.add_network_failure("Connection refused", 7)

    with pytest.raises(NetworkException, match="Connection refused"):
        client.call("Geocoder", "geocode", {})


def test_network_exception_propagates_through_request(
    mock_http: MockHttpClient, client: ApiClient
) -> None:
    mock_http.add_network_failure("Operation timed out", 28)

    with pytest.raises(NetworkException, match="Operation timed out"):
        client.request("POST", "/v3/Foo/bar", {})


def test_network_exception_code_is_preserved(mock_http: MockHttpClient, client: ApiClient) -> None:
    mock_http.add_network_failure("cURL error (28): Operation timed out", 28)

    with pytest.raises(NetworkException) as exc_info:
        client.call("Geocoder", "geocode", {})

    assert exc_info.value.code == 28


def test_call_retries_with_new_session_on_403(mock_http: MockHttpClient) -> None:
    mock_http.add_sequence(
        "Geocoder",
        "geocode",
        [
            {"statusCode": 403, "body": {"message": "Session expired"}},
            {"statusCode": 200, "body": {"result": {"city": "Warszawa"}}},
        ],
    )
    mock_http.add_response("Session", "getSalt", {"result": {"salt": "newsalt"}})
    mock_http.add_response(
        "Session",
        "generateSession",
        {"result": {"sessionId": "new-session-id"}},
    )

    storage = InMemorySessionStorage()
    storage.store("test-session-id")
    config = Config(key="test-key", password="test-pass")
    retry_client = ApiClient(
        config=config,
        http_client=mock_http,
        session_manager=SessionManager(config, mock_http, storage),
    )

    response = retry_client.call("Geocoder", "geocode", {})

    assert isinstance(response, ApiResponse)
    assert mock_http.get_request_count() == 4

    headers = mock_http.get_last_request().headers
    assert headers["Session-Id"] == "new-session-id"


def test_call_with_none_params_treated_as_empty(
    mock_http: MockHttpClient, client: ApiClient
) -> None:
    mock_http.add_response("PingPong", "ping", {"result": "pong"})

    response = client.call("PingPong", "ping")

    assert isinstance(response, ApiResponse)


def test_get_config_returns_config(client: ApiClient) -> None:
    assert client.get_config().key == "test-key"


def test_config_property_returns_config(client: ApiClient) -> None:
    assert client.config.key == "test-key"
