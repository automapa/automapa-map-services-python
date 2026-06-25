import hashlib

import pytest

from automapa_map_services.config import Config
from automapa_map_services.session.manager import SessionManager
from automapa_map_services.session.storage import InMemorySessionStorage
from tests.support.mock_http_client import MockHttpClient


@pytest.fixture()
def mock_http() -> MockHttpClient:
    return MockHttpClient()


@pytest.fixture()
def config() -> Config:
    return Config(key="test-key", password="test-pass")


def make_manager(
    config: Config,
    mock_http: MockHttpClient,
    storage: InMemorySessionStorage | None = None,
) -> SessionManager:
    return SessionManager(
        config=config,
        http_client=mock_http,
        storage=storage or InMemorySessionStorage(),
    )


def test_ensure_session_calls_salt_and_generate_session(
    mock_http: MockHttpClient, config: Config
) -> None:
    mock_http.add_response("Session", "getSalt", {"result": {"salt": "xNnlXNS3Bq"}})
    mock_http.add_response("Session", "generateSession", {"result": {"sessionId": "qPPdEpdtpb"}})

    session_id = make_manager(config, mock_http).ensure_session()

    assert session_id == "qPPdEpdtpb"
    assert mock_http.get_request_count() == 2


def test_ensure_session_returns_cached_session_id(
    mock_http: MockHttpClient, config: Config
) -> None:
    mock_http.add_response("Session", "getSalt", {"result": {"salt": "abc"}})
    mock_http.add_response("Session", "generateSession", {"result": {"sessionId": "first-id"}})

    manager = make_manager(config, mock_http)
    first = manager.ensure_session()
    second = manager.ensure_session()

    assert first == second
    assert mock_http.get_request_count() == 2


def test_clear_session_allows_reinit(mock_http: MockHttpClient, config: Config) -> None:
    mock_http.add_response("Session", "getSalt", {"result": {"salt": "s1"}})
    mock_http.add_response("Session", "generateSession", {"result": {"sessionId": "id-1"}})
    mock_http.add_response("Session", "getSalt", {"result": {"salt": "s2"}})
    mock_http.add_response("Session", "generateSession", {"result": {"sessionId": "id-2"}})

    manager = make_manager(config, mock_http)
    manager.ensure_session()
    manager.clear_session()
    second = manager.ensure_session()

    assert second == "id-2"
    assert mock_http.get_request_count() == 4


def test_requires_session_returns_true_for_ping_pong(
    config: Config, mock_http: MockHttpClient
) -> None:
    manager = make_manager(config, mock_http)

    assert manager.requires_session("PingPong", "ping") is True


def test_requires_session_returns_false_for_session_endpoints(
    config: Config, mock_http: MockHttpClient
) -> None:
    manager = make_manager(config, mock_http)

    assert manager.requires_session("Session", "getSalt") is False
    assert manager.requires_session("Session", "generateSession") is False


def test_requires_session_returns_true_for_geocoder(
    config: Config, mock_http: MockHttpClient
) -> None:
    manager = make_manager(config, mock_http)

    assert manager.requires_session("Geocoder", "geocode") is True


def test_init_session_hashes_password_correctly(mock_http: MockHttpClient, config: Config) -> None:
    salt = "xNnlXNS3Bq"
    expected_pass = hashlib.md5((hashlib.md5(b"test-pass").hexdigest() + salt).encode()).hexdigest()

    mock_http.add_response("Session", "getSalt", {"result": {"salt": salt}})
    mock_http.add_response("Session", "generateSession", {"result": {"sessionId": "any-id"}})

    make_manager(config, mock_http).ensure_session()

    payloads = mock_http.get_all_request_payloads()
    assert payloads[1]["pass"] == expected_pass


def test_storage_pre_populated_avoids_http_calls(mock_http: MockHttpClient, config: Config) -> None:
    storage = InMemorySessionStorage()
    storage.store("pre-existing-id")

    manager = make_manager(config, mock_http, storage)
    session_id = manager.ensure_session()

    assert session_id == "pre-existing-id"
    assert mock_http.get_request_count() == 0
