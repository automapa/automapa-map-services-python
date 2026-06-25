"""
Integration tests for Geocoder with Google format (mirrors PHP GeocoderGoogleFormatTest).

Verifies that geocoder().geocode() with format=google returns a structure
compliant with the Google Geocoding API JSON specification.

Known SDK limitations (fields not provided by Automapa, always null/absent):
  - place_id      → None  (Automapa does not provide Google place IDs)
  - geometry.viewport → None
  - geometry.location_type → field absent
  - plus_code     → field absent

If the API returns permission denied for the geocoder service on the current
account, each test is skipped as an acceptable outcome - the account simply
may not have access to Geocoder.  Other exceptions are re-raised as failures.
"""

from __future__ import annotations

from typing import Any

import pytest

from automapa_map_services.config import Config
from tests.integration.conftest import (
    build_api_client,
    requires_live_api,
    skip_on_permission_error,
)

_SUITE = "geocoder"

_VALID_GOOGLE_TYPES: frozenset[str] = frozenset(
    [
        "street_address",
        "route",
        "locality",
        "administrative_area_level_1",
        "administrative_area_level_2",
        "country",
        "postal_code",
        "political",
        "sublocality",
        "neighborhood",
        "premise",
        "natural_feature",
        "airport",
        "park",
        "point_of_interest",
        "geometric_center",
        "approximate",
    ]
)

# -- Shared fixture ----------------------------------------------------------


@pytest.fixture(scope="module")
def google_geocode_data(live_config: Config) -> dict[str, Any]:
    """
    Geocode Domaniewska 37, Warszawa once per module using the Google formatter.

    Depends on ``live_config`` (session-scoped) so this fixture is automatically
    skipped when API credentials are not set.

    Permission denied for geocoder is treated as an acceptable skip outcome.
    """
    client = build_api_client("google")
    try:
        response = client.geocoder().geocode(
            city="Warszawa", street="Domaniewska", house="37", max_results=1
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        raise
    data: dict[str, Any] = response.data()
    return data


# -- Tests -------------------------------------------------------------------


@requires_live_api(_SUITE)
def test_google_format_returns_top_level_shape(
    google_geocode_data: dict[str, Any],
) -> None:
    """
    Google top-level response shape: { "status": "OK", "results": [...] }
    SDK extension: "_raw" contains the original Automapa response.
    """
    data = google_geocode_data

    assert isinstance(data, dict)
    assert "status" in data, 'Google format must include "status"'
    assert "results" in data, 'Google format must include "results"'
    assert "_raw" in data, 'SDK must include "_raw" with original response'

    assert data["status"] == "OK"
    assert isinstance(data["results"], list)
    assert data["results"], "Geocode should return at least one result"

    assert isinstance(data["_raw"], dict)
    assert "result" in data["_raw"], '_raw must preserve native "result" key'


@requires_live_api(_SUITE)
def test_google_format_result_has_all_required_fields(
    google_geocode_data: dict[str, Any],
) -> None:
    """Every result object must contain the fields required by Google Geocoding API spec."""
    result = google_geocode_data["results"][0]

    assert "formatted_address" in result
    assert "address_components" in result
    assert "geometry" in result
    assert "place_id" in result
    assert "types" in result

    assert isinstance(result["address_components"], list)
    assert isinstance(result["geometry"], dict)
    assert isinstance(result["types"], list)


@requires_live_api(_SUITE)
def test_google_format_formatted_address_is_non_empty_string(
    google_geocode_data: dict[str, Any],
) -> None:
    """formatted_address must be a non-empty human-readable string."""
    result = google_geocode_data["results"][0]

    assert isinstance(result["formatted_address"], str)
    assert result["formatted_address"], "formatted_address must not be empty"


@requires_live_api(_SUITE)
def test_google_format_address_components_match_google_spec(
    google_geocode_data: dict[str, Any],
) -> None:
    """
    Every address_component must have: long_name (str), short_name (str), types (non-empty list).
    Source: Google Geocoding API spec - address_components structure.
    """
    components: list[dict[str, Any]] = google_geocode_data["results"][0]["address_components"]

    assert components, "address_components must not be empty"

    for idx, component in enumerate(components):
        assert "long_name" in component, f"Component #{idx} missing long_name"
        assert "short_name" in component, f"Component #{idx} missing short_name"
        assert "types" in component, f"Component #{idx} missing types"

        assert isinstance(component["long_name"], str), f"Component #{idx} long_name must be str"
        assert isinstance(component["short_name"], str), f"Component #{idx} short_name must be str"
        assert isinstance(component["types"], list), f"Component #{idx} types must be list"
        assert component["types"], f"Component #{idx} types must not be empty"


@requires_live_api(_SUITE)
def test_google_format_address_components_contain_locality(
    google_geocode_data: dict[str, Any],
) -> None:
    """When geocoding a city, at least one address_component must carry the 'locality' type."""
    components: list[dict[str, Any]] = google_geocode_data["results"][0]["address_components"]

    all_types: list[str] = [t for comp in components for t in comp.get("types", [])]

    assert "locality" in all_types, "A city geocode must yield a 'locality' address_component"


@requires_live_api(_SUITE)
def test_google_format_geometry_location_has_lat_lng(
    google_geocode_data: dict[str, Any],
) -> None:
    """
    geometry.location must have numeric lat and lng fields - matches Google spec:
    { "location": { "lat": float, "lng": float } }
    """
    geometry: dict[str, Any] = google_geocode_data["results"][0]["geometry"]

    assert "location" in geometry
    location = geometry["location"]
    assert "lat" in location, 'geometry.location must have "lat"'
    assert "lng" in location, 'geometry.location must have "lng"'

    assert isinstance(location["lat"], float)
    assert isinstance(location["lng"], float)


@requires_live_api(_SUITE)
def test_google_format_coordinates_mapped_correctly() -> None:
    """
    Google format maps Automapa coordinates: lat = native y (latitude), lng = native x (longitude).
    Tested with a fresh per-test client to verify coordinate mapping independently.
    Permission denied for geocoder is treated as an acceptable skip outcome.
    """
    client = build_api_client("google")
    try:
        response = client.geocoder().geocode(city="Warszawa", max_results=1)
    except Exception as exc:
        skip_on_permission_error(exc)
        raise

    data: dict[str, Any] = response.data()
    raw: dict[str, Any] = response.raw()

    native_result = raw["result"]
    first: dict[str, Any] = (
        native_result[0]
        if isinstance(native_result, list) and isinstance(native_result[0], dict)
        else native_result
    )
    google_location = data["results"][0]["geometry"]["location"]

    assert abs(float(first["y"]) - google_location["lat"]) < 0.0001, (
        "lat must equal native y (latitude)"
    )
    assert abs(float(first["x"]) - google_location["lng"]) < 0.0001, (
        "lng must equal native x (longitude)"
    )


@requires_live_api(_SUITE)
def test_google_format_types_contain_valid_google_type(
    google_geocode_data: dict[str, Any],
) -> None:
    """The result 'types' array must contain at least one recognised Google geocode type string."""
    types: list[str] = google_geocode_data["results"][0]["types"]

    assert isinstance(types, list)
    assert types, "types must not be empty"

    intersection = _VALID_GOOGLE_TYPES & set(types)
    assert intersection, f"types must contain at least one Google type; got: {types}"
