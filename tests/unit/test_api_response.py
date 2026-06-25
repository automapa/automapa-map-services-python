from automapa_map_services.response.api_response import ApiResponse


def test_raw_returns_full_dict() -> None:
    raw = {"result": {"city": "Warszawa"}, "extra": "data"}
    response = ApiResponse(raw=raw, status_code=200)
    assert response.raw() is raw


def test_data_returns_result_when_present() -> None:
    raw = {"result": {"city": "Warszawa"}}
    response = ApiResponse(raw=raw, status_code=200)
    assert response.data() == {"city": "Warszawa"}


def test_data_returns_raw_when_result_absent() -> None:
    raw: dict[str, object] = {"someOtherKey": "value"}
    response = ApiResponse(raw=raw, status_code=200)
    assert response.data() is raw


def test_data_returns_formatted_data_when_set() -> None:
    raw = {"result": {"city": "Warszawa"}}
    formatted = {"formatted": True}
    response = ApiResponse(raw=raw, status_code=200, formatted_data=formatted)
    assert response.data() == {"formatted": True}


def test_status_returns_status_code() -> None:
    response = ApiResponse(raw={}, status_code=200)
    assert response.status() == 200


def test_meta_returns_meta_dict() -> None:
    meta = {"service": "Geocoder", "method": "geocode"}
    response = ApiResponse(raw={}, status_code=200, meta=meta)
    assert response.meta() == meta


def test_meta_defaults_to_empty_dict() -> None:
    response = ApiResponse(raw={}, status_code=200)
    assert response.meta() == {}
