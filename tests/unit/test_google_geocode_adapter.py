import pytest

from automapa_map_services.adapter.google_geocode import GoogleGeocodeAdapter
from automapa_map_services.client import ApiClient
from automapa_map_services.config import Config
from automapa_map_services.session.manager import SessionManager
from automapa_map_services.session.storage import InMemorySessionStorage
from tests.support.mock_http_client import MockHttpClient

_GEOCODE_SUCCESS = {
    "result": {
        "x": 21.0122,
        "y": 52.2297,
        "city": "Warszawa",
        "street": "Domaniewska",
        "house": "17A",
        "pcode": "02-672",
        "country": "Polska",
        "province": "mazowieckie",
        "district": "Mokotów",
        "quality": 9,
    }
}


def _make_adapter() -> tuple[GoogleGeocodeAdapter, MockHttpClient]:
    mock_http = MockHttpClient()
    storage = InMemorySessionStorage()
    storage.store("test-session-id")
    config = Config(key="test-key", password="test-pass")
    client = ApiClient(
        config=config,
        http_client=mock_http,
        session_manager=SessionManager(config, mock_http, storage),
    )
    return GoogleGeocodeAdapter(client), mock_http


@pytest.fixture()
def adapter_and_http() -> tuple[GoogleGeocodeAdapter, MockHttpClient]:
    return _make_adapter()


def _stub_geocode(mock_http: MockHttpClient) -> None:
    mock_http.add_response("Geocoder", "geocode", _GEOCODE_SUCCESS)


# ------------------------------------------------------------------ #
# Address parsing - components string
# ------------------------------------------------------------------ #


def test_geocode_with_components_string_parses_correctly(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"components": "locality:Warszawa|route:Domaniewska|street_number:37"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Warszawa"
    assert payload["address"]["street"] == "Domaniewska"
    assert payload["address"]["house"] == "37"


def test_geocode_with_components_string_maps_all_supported_keys(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode(
        {
            "components": (
                "locality:Kraków|route:Floriańska|street_number:1"
                "|postal_code:31-019|administrative_area_level_1:małopolskie|country:Polska"
            )
        }
    )

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Kraków"
    assert payload["address"]["street"] == "Floriańska"
    assert payload["address"]["house"] == "1"
    assert payload["address"]["pcode"] == "31-019"
    assert payload["address"]["province"] == "małopolskie"
    assert payload["address"]["country"] == "Polska"


# ------------------------------------------------------------------ #
# Address parsing - free-form string
# ------------------------------------------------------------------ #


def test_geocode_with_address_string_parses_street_and_city(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"address": "Domaniewska 37, Warszawa"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Warszawa"
    assert payload["address"]["street"] == "Domaniewska"
    assert payload["address"]["house"] == "37"


def test_geocode_with_address_string_with_postal_code(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"address": "Domaniewska 37, 02-672 Warszawa"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Warszawa"
    assert payload["address"]["pcode"] == "02-672"
    assert payload["address"]["street"] == "Domaniewska"
    assert payload["address"]["house"] == "37"


def test_geocode_with_city_only_string_returns_city_only(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"address": "Gdańsk"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Gdańsk"


# ------------------------------------------------------------------ #
# Address parsing - structured dict pass-through
# ------------------------------------------------------------------ #


def test_geocode_with_address_dict_passes_through(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    structured = {"city": "Gdańsk", "street": "Długa", "house": "1"}
    adapter.geocode({"address": structured})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Gdańsk"
    assert payload["address"]["street"] == "Długa"
    assert payload["address"]["house"] == "1"


# ------------------------------------------------------------------ #
# Components take priority over address string
# ------------------------------------------------------------------ #


def test_components_take_priority_over_address_string(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"address": "This should be ignored", "components": "locality:Kraków"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Kraków"


# ------------------------------------------------------------------ #
# Format is always google
# ------------------------------------------------------------------ #


def test_geocode_always_returns_google_format(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    result = adapter.geocode({"address": "Warszawa"})

    assert "status" in result
    assert "results" in result
    assert result["status"] == "OK"


def test_geocode_format_is_not_sent_to_api(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"address": "Warszawa"})

    payload = mock_http.get_last_request_payload()
    assert "format" not in payload, '"format" must be stripped before sending to API'


# ------------------------------------------------------------------ #
# Google-specific params are stripped from the API call
# ------------------------------------------------------------------ #


def test_google_params_are_stripped_from_api_call(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode(
        {"address": "Warszawa", "language": "pl", "key": "google-api-key", "region": "pl"}
    )

    payload = mock_http.get_last_request_payload()
    assert "language" not in payload
    assert "key" not in payload
    assert "region" not in payload


def test_max_results_is_forwarded_to_api(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"address": "Warszawa", "maxResults": 5})

    payload = mock_http.get_last_request_payload()
    assert payload["maxResults"] == 5


def test_max_results_defaults_to_one_when_not_provided(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"address": "Warszawa"})

    payload = mock_http.get_last_request_payload()
    assert payload["maxResults"] == 1


# ------------------------------------------------------------------ #
# Error: no address provided
# ------------------------------------------------------------------ #


def test_geocode_with_no_address_raises_value_error(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, _ = adapter_and_http

    with pytest.raises(ValueError, match='"address"|"components"'):
        adapter.geocode({"language": "pl", "key": "some-key"})


# ------------------------------------------------------------------ #
# Address parsing edge cases
# ------------------------------------------------------------------ #


def test_parse_components_ignores_unknown_keys(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"components": "locality:Warszawa|unknown_key:something"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Warszawa"


def test_parse_components_ignores_parts_without_colon(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"components": "locality:Warszawa|malformed"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Warszawa"


def test_parse_components_neighborhood_maps_to_district(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"components": "locality:Warszawa|neighborhood:Mokotów"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["district"] == "Mokotów"


def test_parse_address_string_street_without_number(
    adapter_and_http: tuple[GoogleGeocodeAdapter, MockHttpClient],
) -> None:
    adapter, mock_http = adapter_and_http
    _stub_geocode(mock_http)

    adapter.geocode({"address": "Domaniewska, Warszawa"})

    payload = mock_http.get_last_request_payload()
    assert payload["address"]["city"] == "Warszawa"
    assert payload["address"]["street"] == "Domaniewska"
    assert "house" not in payload["address"]
