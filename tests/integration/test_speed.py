"""Integration tests for the Speed endpoint (mirrors PHP SpeedTest)."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, TypeVar

from automapa_map_services.exceptions import RateLimitException
from tests.integration.conftest import (
    _RATE_LIMIT_RETRY_WAIT,
    build_api_client,
    requires_live_api,
    skip_on_permission_error,
    skip_on_server_error,
)

_SUITE = "speed"

_T = TypeVar("_T")

_POINTS_3 = [
    {"x": 21.0073642, "y": 52.2297000, "t": 1700000000},
    {"x": 21.0120000, "y": 52.2310000, "t": 1700000060},
    {"x": 21.0170000, "y": 52.2325000, "t": 1700000120},
]

_POINTS_2 = [
    {"x": 21.0073642, "y": 52.2297000, "t": 1700000000},
    {"x": 21.0120000, "y": 52.2310000, "t": 1700000060},
]


def _call_with_retry(fn: Callable[..., _T], *args: Any, **kwargs: Any) -> _T:
    """Call fn(*args, **kwargs), retrying once after ~30 s on RateLimitException."""
    try:
        return fn(*args, **kwargs)
    except RateLimitException:
        time.sleep(_RATE_LIMIT_RETRY_WAIT)
        return fn(*args, **kwargs)


@requires_live_api(_SUITE)
def test_speed_report_via_facade_returns_request_id() -> None:
    """
    speedReport() must return requestID and objID.

    Permission denied is an acceptable skip outcome - the account may not have
    access to the Speed service.  Server errors are also skipped as they
    indicate no API access.
    """
    client = build_api_client()
    try:
        response = _call_with_retry(
            client.speed().speed_report,
            obj_id="test-vehicle-001",
            obj_name="Test Vehicle",
            obj_group="TestGroup",
            points=_POINTS_3,
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert response.status() == 200
    data: dict[str, Any] = response.data()
    assert isinstance(data, dict)
    assert "requestID" in data, "speedReport() should return requestID"
    assert "objID" in data, "speedReport() should return objID"
    assert data["requestID"], "requestID must not be empty"


@requires_live_api(_SUITE)
def test_speed_report_result_via_facade_returns_progress() -> None:
    """
    speedReportResult() must return requestID and progress.

    Submits a speed report first, then polls for its result.
    Permission denied and server errors are acceptable skip outcomes.
    """
    client = build_api_client()
    try:
        report_response = _call_with_retry(
            client.speed().speed_report,
            obj_id="test-vehicle-002",
            obj_name="Test Vehicle 2",
            obj_group="TestGroup",
            points=_POINTS_2,
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    request_id = str(report_response.data()["requestID"])

    try:
        result_response = _call_with_retry(
            client.speed().speed_report_result,
            request_id=request_id,
            limit=1,
        )
    except Exception as exc:
        skip_on_permission_error(exc)
        skip_on_server_error(exc)
        raise

    assert result_response.status() == 200
    result_data: dict[str, Any] = result_response.data()
    assert isinstance(result_data, dict)
    assert "requestID" in result_data, "speedReportResult() should return requestID"
    assert "progress" in result_data, "speedReportResult() should return progress"
