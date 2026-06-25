"""Integration tests for the Road endpoint (mirrors PHP RoadTest)."""

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

_SUITE = "road"

# -- Fixtures ----------------------------------------------------------------


@pytest.fixture(scope="module")
def road_session_id(
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
def test_get_segment_info_via_facade_returns_segment() -> None:
    """
    Permission denied for road is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.road().getSegmentInfo(
            {
                "x": 21.00736,
                "y": 52.18288,
            }
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, dict), "getSegmentInfo() should return a dict"
    assert "segment" in data, "getSegmentInfo() should return segment"
    assert "attractedX" in data, "getSegmentInfo() should return attractedX"
    assert "pureDistance" in data, "getSegmentInfo() should return pureDistance"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_speed_check_via_facade_returns_speed_limit() -> None:
    """
    Permission denied for road is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.road().speedCheck(
            {
                "x": 15.2154636,
                "y": 52.3118895,
                "dir": 350,
            }
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, dict), "speedCheck() should return a dict"
    assert "speedLimit" in data, "speedCheck() should return speedLimit"
    assert "speedLimitTruck" in data, "speedCheck() should return speedLimitTruck"
    assert "urbanArea" in data, "speedCheck() should return urbanArea"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_speed_check_multi_via_facade_returns_array() -> None:
    """
    Permission denied for road is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.road().speedCheckMulti(
            {
                "points": [
                    {"x": 15.2154636, "y": 52.3118895, "dir": 350},
                    {"x": 13.8412285, "y": 52.3111549},
                ],
            }
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, list), "speedCheckMulti() should return a list"
    assert data, "speedCheckMulti() should return at least one entry"
    assert "result" in response.raw(), 'raw() must contain the "result" key'
