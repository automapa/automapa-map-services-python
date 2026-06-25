"""Integration tests for the Geocoder endpoint (mirrors PHP GeocoderTest)."""

from __future__ import annotations

import json
from typing import Any

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

_SUITE = "geocoder"

# -- Fixtures ----------------------------------------------------------------


@pytest.fixture(scope="module")
def geocoder_session_id(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    live_config: Config,
) -> str:
    """Session ID acquired once per module to reduce API calls."""
    return acquire_session(
        live_request_builder, live_http_client, live_config.key, live_config.password
    )


# -- Raw-request tests -------------------------------------------------------


@requires_live_api(_SUITE)
def test_geocode_by_structured_address(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    geocoder_session_id: str,
) -> None:
    response = send_request_with_retry(
        live_request_builder,
        live_http_client,
        "Geocoder",
        "geocode",
        {
            "address": {"city": "Warszawa", "street": "Domaniewska", "house": "37"},
            "maxResults": 1,
        },
        geocoder_session_id,
    )
    skip_if_no_permission(response)
    assert_success_response(response)

    body: dict[str, Any] = json.loads(response.body)
    results: list[dict[str, Any]] = body["result"]

    assert isinstance(results, list)
    assert results, "Geocode should return at least one result"

    first = results[0]
    assert "x" in first
    assert "y" in first
    assert "quality" in first
    assert first["quality"] >= 5
    assert 20.8 < first["x"] < 21.3, "Longitude (x) should be in Warsaw range"
    assert 52.0 < first["y"] < 52.4, "Latitude (y) should be in Warsaw range"


@requires_live_api(_SUITE)
def test_revgeocode_returns_city(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    geocoder_session_id: str,
) -> None:
    response = send_request_with_retry(
        live_request_builder,
        live_http_client,
        "Geocoder",
        "revgeocode",
        {"point": [21.0073642, 52.18288], "params": []},
        geocoder_session_id,
    )
    skip_if_no_permission(response)
    assert_success_response(response)

    body: dict[str, Any] = json.loads(response.body)
    city = str(body["result"].get("city", ""))

    assert city, "Reverse geocode should return a city name"
    assert "warszawa" in city.lower(), f"Expected Warsaw, got: {city!r}"


@requires_live_api(_SUITE)
def test_geocode_without_session_fails(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
) -> None:
    response = send_request_with_retry(
        live_request_builder,
        live_http_client,
        "Geocoder",
        "geocode",
        {"address": {"city": "Warszawa"}, "maxResults": 1},
        None,
    )
    assert not response.is_success, "Geocoder/geocode without Session-Id should return non-2xx"


# -- Facade tests ------------------------------------------------------------


@requires_live_api(_SUITE)
def test_geocode_via_facade_returns_results() -> None:
    """
    Permission denied for geocoder is treated as an acceptable skip outcome:
    this account may not have access to the Geocoder service.
    Other exceptions are re-raised as failures.
    """
    client = build_api_client()
    try:
        response = client.geocoder().geocode(
            city="Warszawa", street="Domaniewska", house="37", max_results=1
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, list)
    assert data, "Geocoder facade should return at least one result"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_revgeocode_via_facade_returns_city() -> None:
    """
    Permission denied for geocoder is treated as an acceptable skip outcome.
    """
    client = build_api_client()
    try:
        response = client.geocoder().revgeocode(point=[21.0073642, 52.18288], snap_to_bld=True)
    except Exception as exc:
        skip_on_permission_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, dict)
    assert "city" in data, "revgeocode should return city field"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_geocodemulti_via_facade_returns_results() -> None:
    """
    Permission denied for geocoder is treated as an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.geocoder().geocodemulti(
            addresses=[
                {"city": "Warszawa", "street": "Domaniewska", "house": "37"},
                {"city": "Gdańsk", "street": "Długa", "house": "1"},
            ]
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, list)
    assert data, "geocodemulti() should return at least one result"

    first_group = data[0] if data else []
    first_result: dict[str, Any] = (
        first_group[0] if isinstance(first_group, list) and first_group else first_group
    )
    assert "x" in first_result, "Geocode result should have x coordinate"
    assert "y" in first_result, "Geocode result should have y coordinate"
    assert "result" in response.raw(), 'raw() must contain the "result" key'


@requires_live_api(_SUITE)
def test_revgeocodemulti_via_facade_returns_results() -> None:
    """
    Permission denied for geocoder is treated as an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.geocoder().revgeocodemulti(
            points=[
                [21.0073642, 52.18288],
                [18.6282, 54.3520],
            ]
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, list)
    assert data, "revgeocodemulti() should return at least one result"
    assert "result" in response.raw(), 'raw() must contain the "result" key'
