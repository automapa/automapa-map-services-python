"""Integration tests for the Routes endpoint (mirrors PHP RoutesTest)."""

from __future__ import annotations

import pytest

from automapa_map_services.config import Config
from automapa_map_services.http.builder import RequestBuilder
from automapa_map_services.http.urllib_client import UrllibHttpClient
from tests.integration.conftest import (
    acquire_session,
    build_api_client,
    requires_live_api,
    skip_on_permission_error,
    skip_on_server_error,
)

_SUITE = "routes"

# -- Fixtures ----------------------------------------------------------------


@pytest.fixture(scope="module")
def routes_session_id(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    live_config: Config,
) -> str:
    """Session ID acquired once per module to reduce API calls."""
    return acquire_session(
        live_request_builder, live_http_client, live_config.key, live_config.password
    )


# -- Facade tests ------------------------------------------------------------


@requires_live_api(_SUITE)
def test_route_via_facade_returns_length_and_eta() -> None:
    """
    Permission denied for routes is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.routes().route(
            points=[
                [21.0073642, 52.2297],
                [18.6282, 54.3520],
            ],
            route={"type": "short", "traffic": True},
            object={"type": "car"},
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, dict), "route() should return a dict"
    assert "length" in data, "route() should return length"
    assert "eta" in data, "route() should return eta"
    assert data["length"] > 0, "length should be positive"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_matrix_via_facade_returns_result_array() -> None:
    """
    Permission denied for routes is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.routes().matrix(
            points=[
                [21.0073642, 52.2297],
                [18.6282, 54.3520],
                [16.9252, 52.4064],
                [19.9448, 50.0647],
            ],
            type=1,
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, list), "matrix() should return a list"
    assert data, "matrix() should return at least one entry"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_optimize_via_facade_returns_optimized_points() -> None:
    """
    Permission denied for routes is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.routes().optimize(
            points=[
                [21.0073642, 52.2297],
                [18.6282, 54.3520],
                [16.9252, 52.4064],
            ],
            type=1,
            fixed_end=False,
            object={"type": "car"},
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, dict), "optimize() should return a dict"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_optimize_queue_via_facade_returns_request_id() -> None:
    """
    Permission denied for routes is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.routes().optimizeQueue(
            {
                "points": [
                    {"id": "Warsaw", "x": 21.0073642, "y": 52.2297},
                    {"id": "Gdansk", "x": 18.6282, "y": 54.3520},
                    {"id": "Poznan", "x": 16.9252, "y": 52.4064},
                    {"id": "Krakow", "x": 19.9448, "y": 50.0647},
                ],
                "optimizeBy": "time",
                "fixedEnd": False,
                "route": {"avoidTolls": False, "start": "NOW"},
                "object": {"type": "car"},
            }
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, dict), "optimizeQueue() should return a dict"
    assert "requestId" in data, "optimizeQueue() should return requestId"
    assert data["requestId"], "requestId should not be empty"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_optimize_queue_result_via_facade_returns_progress() -> None:
    """
    Submits an optimize-queue job then immediately polls for its result.
    Permission denied for routes is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        queue_response = client.routes().optimizeQueue(
            {
                "points": [
                    {"id": "Warsaw", "x": 21.0073642, "y": 52.2297},
                    {"id": "Gdansk", "x": 18.6282, "y": 54.3520},
                    {"id": "Poznan", "x": 16.9252, "y": 52.4064},
                    {"id": "Krakow", "x": 19.9448, "y": 50.0647},
                ],
                "optimizeBy": "time",
                "fixedEnd": False,
                "route": {"avoidTolls": False, "start": "NOW"},
                "object": {"type": "car"},
            }
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    request_id = str(queue_response.data()["requestId"])

    try:
        result_response = client.routes().optimizeQueueResult({"requestId": request_id})
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert result_response.status() == 200
    data = result_response.data()
    assert isinstance(data, dict), "optimizeQueueResult() should return a dict"
    assert "result" in result_response.raw(), 'raw() must contain the "result" key'
