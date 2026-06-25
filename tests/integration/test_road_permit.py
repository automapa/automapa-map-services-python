"""Integration tests for the RoadPermit endpoint (mirrors PHP RoadPermitTest)."""

from __future__ import annotations

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

_SUITE = "road_permit"

# PHP IntegrationTestCase::TEST_AUTOMAPA_ENVIRONMENT = 'uat'
_TEST_ENV = "uat"

# Polygon used for add/overwrite – matches PHP test data exactly
_TEST_POLY: dict = {
    "type": "Polygon",
    "coordinates": [
        [
            [20.993155973821672, 50.01069571221776],
            [20.994428585759994, 50.01089900951218],
            [20.994138589184054, 50.011559010137475],
            [20.923253, 50.011827900000000],
            [20.993155973821672, 50.01069571221776],
        ]
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def road_permit_session_id(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    live_config: Config,
) -> str:
    """Session ID acquired once per module to reduce API calls."""
    return acquire_session(
        live_request_builder, live_http_client, live_config.key, live_config.password
    )


# ---------------------------------------------------------------------------
# Raw HTTP tests
# ---------------------------------------------------------------------------


@requires_live_api(_SUITE)
def test_list_returns_result_via_raw_http(
    live_request_builder: RequestBuilder,
    live_http_client: UrllibHttpClient,
    road_permit_session_id: str,
) -> None:
    response = send_request_with_retry(
        live_request_builder,
        live_http_client,
        "RoadPermit",
        "list",
        {"enviroment": _TEST_ENV},
        road_permit_session_id,
    )

    skip_if_no_permission(response)
    assert_success_response(response)

    import json

    body = json.loads(response.body)
    assert isinstance(body["result"], list), "result must be an array (empty or with items)"


# ---------------------------------------------------------------------------
# Facade tests
# ---------------------------------------------------------------------------


@requires_live_api(_SUITE)
def test_list_returns_result_via_api_client_facade() -> None:
    client = build_api_client()
    try:
        response = client.road_permit(_TEST_ENV).list()
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data = response.data()
    assert isinstance(data, list), "data() must return an array (empty or with items)"


@requires_live_api(_SUITE)
def test_add_and_remove_preserves_collection_state() -> None:
    """
    Mirrors PHP addAndRemovePreservesCollectionState.

    Mutating test that:
    1. records initial list length
    2. adds a permit
    3. verifies list grew by 1 and the new ID is present
    4. overwrites the permit (tr_tonnage 12 → 24) and verifies list count unchanged
    5. removes the permit and verifies list returned to original count

    Permission denied is an acceptable outcome (xfail-like skip).
    The test cleans up after itself (remove in step 5) so the live environment
    is left in its original state even on partial failures.
    The RoadPermit TEST environment ('uat') is used, never prod, so writes are safe.
    """
    client = build_api_client()
    new_id: str | None = None

    try:
        # 1. Initial list
        initial_response = client.road_permit(_TEST_ENV).list()
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    initial_items = initial_response.data()
    assert isinstance(initial_items, list)
    initial_count = len(initial_items)

    # 2. Add
    try:
        add_response = client.road_permit(_TEST_ENV).add(
            permissions={"tr_tonnage": 12},
            poly=_TEST_POLY,
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    new_id = str(add_response.raw().get("result", {}).get("id", ""))
    assert new_id, "add() must return a non-empty permit ID"

    try:
        # 3. List after add
        after_add_response = client.road_permit(_TEST_ENV).list()
        after_add_items = after_add_response.data()
        assert isinstance(after_add_items, list)
        assert len(after_add_items) == initial_count + 1, (
            "list() should have one more item after add()"
        )
        ids_after_add = [str(item.get("id", "")) for item in after_add_items]
        assert new_id in ids_after_add, "new ID must appear in list after add()"

        new_record = next(
            (item for item in after_add_items if str(item.get("id", "")) == new_id), None
        )
        assert new_record is not None, "Added record must be found in list by ID"
        assert new_record.get("permissions", {}).get("tr_tonnage") == 12, (
            "tr_tonnage must match the value sent to add()"
        )

        # 4. Overwrite (tr_tonnage 12 → 24)
        overwrite_response = client.road_permit(_TEST_ENV).overwrite(
            new_id,
            permissions={"tr_tonnage": 24},
            poly=_TEST_POLY,
        )
        assert str(overwrite_response.raw().get("result", {}).get("id", "")) == new_id, (
            "overwrite() must return the ID of the overwritten document"
        )

        after_overwrite_items = client.road_permit(_TEST_ENV).list().data()
        assert isinstance(after_overwrite_items, list)
        assert len(after_overwrite_items) == initial_count + 1, (
            "list() count must not change after overwrite()"
        )

        overwritten = next(
            (item for item in after_overwrite_items if str(item.get("id", "")) == new_id), None
        )
        assert overwritten is not None, "Overwritten record must still be in list"
        assert overwritten.get("permissions", {}).get("tr_tonnage") == 24, (
            "tr_tonnage must reflect the overwrite value"
        )

        # 5. Remove
        remove_response = client.road_permit(_TEST_ENV).remove(new_id)
        assert remove_response.raw().get("result", {}).get("deleted") is True, (
            "remove() must confirm deletion with deleted=true"
        )
        new_id = None  # mark as already cleaned up

        # 5b. Verify state restored
        after_remove_items = client.road_permit(_TEST_ENV).list().data()
        assert isinstance(after_remove_items, list)
        assert len(after_remove_items) == initial_count, (
            "list() should return to original count after remove()"
        )
        ids_after_remove = [str(item.get("id", "")) for item in after_remove_items]
        assert overwritten["id"] not in ids_after_remove, "removed ID must not appear in list"

    finally:
        # Cleanup: remove the test permit if an assertion failed mid-test
        if new_id is not None:
            try:
                client.road_permit(_TEST_ENV).remove(new_id)
            except Exception:
                pass
