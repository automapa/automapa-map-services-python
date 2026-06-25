"""Integration tests for the Autocomplete endpoint (mirrors PHP AutocompleteTest)."""

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

_SUITE = "autocomplete"

# -- Fixtures ----------------------------------------------------------------


@pytest.fixture(scope="module")
def autocomplete_session_id(
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
def test_autocomplete_search_raw(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    autocomplete_session_id: str,
) -> None:
    response = send_request_with_retry(
        live_request_builder,
        live_http_client,
        "Autocomplete",
        "search",
        {"query": "Warszawa Domaniewska 37"},
        autocomplete_session_id,
    )
    skip_if_no_permission(response)
    assert_success_response(response)

    body: dict[str, Any] = json.loads(response.body)
    data: dict[str, Any] = body["result"]

    assert isinstance(data, dict)
    assert "items" in data, "search response must contain 'items'"
    assert data["items"], "search should return at least one result"

    first: dict[str, Any] = data["items"][0]
    assert "type" in first
    assert "name" in first
    assert "coords" in first
    assert "x" in first["coords"]
    assert "y" in first["coords"]


@requires_live_api(_SUITE)
def test_autocomplete_search_address_raw(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    autocomplete_session_id: str,
) -> None:
    response = send_request_with_retry(
        live_request_builder,
        live_http_client,
        "Autocomplete",
        "searchAddress",
        {
            "query": {
                "city": "Warszawa",
                "street": "Dom",
                "number": "",
                "zipcode": "",
            },
            "source": "street",
            "selected": ["city"],
        },
        autocomplete_session_id,
    )
    skip_if_no_permission(response)
    assert_success_response(response)

    body: dict[str, Any] = json.loads(response.body)
    data: dict[str, Any] = body["result"]

    assert isinstance(data, dict)
    assert "items" in data, "searchAddress response must contain 'items'"
    assert data["items"], "searchAddress should return at least one result"

    first: dict[str, Any] = data["items"][0]
    assert "city" in first
    assert "street" in first


# -- Facade tests ------------------------------------------------------------


@requires_live_api(_SUITE)
def test_autocomplete_search_via_facade() -> None:
    """
    Permission denied for autocomplete is an acceptable skip outcome -
    the account may not have access to this endpoint.
    Other exceptions are re-raised as failures.
    """
    client = build_api_client()
    try:
        response = client.autocomplete().search(query="Warszawa Domaniewska 37")
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    assert "result" in response.raw(), 'raw() must contain the "result" key'

    data = response.data()
    assert isinstance(data, dict)
    assert "items" in data, "search response must contain 'items'"
    assert data["items"], "search should return at least one result"

    first: dict[str, Any] = data["items"][0]
    assert "type" in first
    assert "name" in first
    assert "coords" in first
    assert "x" in first["coords"]
    assert "y" in first["coords"]


@requires_live_api(_SUITE)
def test_autocomplete_search_address_via_facade() -> None:
    """
    Permission denied for autocomplete is an acceptable skip outcome.
    Server errors (5xx) are also skipped as they indicate no API access.
    """
    client = build_api_client()
    try:
        response = client.autocomplete().search_address(
            query={
                "city": "Warszawa",
                "street": "Dom",
                "number": "",
                "zipcode": "",
            },
            source="street",
            selected=["city"],
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    assert "result" in response.raw(), 'raw() must contain the "result" key'

    data = response.data()
    assert isinstance(data, dict)
    assert "items" in data, "searchAddress response must contain 'items'"
    assert data["items"], "searchAddress should return at least one result"

    first: dict[str, Any] = data["items"][0]
    assert "city" in first
    assert "street" in first
