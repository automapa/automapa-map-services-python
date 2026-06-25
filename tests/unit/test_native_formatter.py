import pytest

from automapa_map_services.formatter.native import NativeFormatter


@pytest.fixture()
def formatter() -> NativeFormatter:
    return NativeFormatter()


def test_passes_array_result_through(formatter: NativeFormatter) -> None:
    raw = {"result": {"city": "Kraków", "x": 19.94}}
    output = formatter.format(raw, "Geocoder.geocode")

    assert output["city"] == "Kraków"
    assert output["x"] == 19.94


def test_appends_raw_key(formatter: NativeFormatter) -> None:
    raw = {"result": {"city": "Gdańsk"}}
    output = formatter.format(raw, "Geocoder.geocode")

    assert "_raw" in output
    assert output["_raw"] is raw


def test_wraps_scalar_result_in_data_key(formatter: NativeFormatter) -> None:
    raw = {"result": "pong"}
    output = formatter.format(raw, "PingPong.ping")

    assert "data" in output
    assert output["data"] == "pong"
    assert output["_raw"] is raw


def test_raw_key_overrides_existing_raw_in_result(formatter: NativeFormatter) -> None:
    raw = {"result": {"city": "Łódź", "_raw": "old-value"}}
    output = formatter.format(raw, "Geocoder.geocode")

    assert output["_raw"] is raw


def test_missing_result_key_returns_raw_with_raw_appended(formatter: NativeFormatter) -> None:
    raw = {"error": "something"}
    output = formatter.format(raw, "SomeService.someMethod")

    # raw['result'] ?? raw => uses raw itself
    assert output["_raw"] is raw
    assert output["error"] == "something"
