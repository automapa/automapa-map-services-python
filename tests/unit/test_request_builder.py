import json
from urllib.parse import urlparse

import pytest

from automapa_map_services.http.builder import RequestBuilder


@pytest.fixture
def builder() -> RequestBuilder:
    return RequestBuilder(base_url="https://api.automapa.pl/", version="v3")


def test_builds_correct_url(builder: RequestBuilder) -> None:
    request = builder.build("Geocoder", "geocode")
    assert request.url == "https://api.automapa.pl/v3/Geocoder/geocode"


def test_url_contains_no_double_slash_when_base_url_has_trailing_slash() -> None:
    b = RequestBuilder("https://api.automapa.pl/", "v3")
    request = b.build("PingPong", "ping")
    path = urlparse(request.url).path
    assert "//" not in path
    assert "/v3/PingPong/ping" in request.url


def test_method_is_post(builder: RequestBuilder) -> None:
    request = builder.build("Geocoder", "geocode")
    assert request.method == "POST"


def test_sets_content_type_header(builder: RequestBuilder) -> None:
    request = builder.build("Geocoder", "geocode")
    assert "Content-Type" in request.headers
    assert request.headers["Content-Type"] == "application/json"


def test_sets_session_id_header_when_provided(builder: RequestBuilder) -> None:
    request = builder.build("Geocoder", "geocode", {}, "my-session-id")
    assert "Session-Id" in request.headers
    assert request.headers["Session-Id"] == "my-session-id"


def test_omits_session_id_header_when_none(builder: RequestBuilder) -> None:
    request = builder.build("PingPong", "ping", {}, None)
    assert "Session-Id" not in request.headers


def test_body_is_json_encoded_params(builder: RequestBuilder) -> None:
    params = {"address": {"city": "Warszawa", "street": "Domaniewska"}, "maxResults": 5}
    request = builder.build("Geocoder", "geocode", params)
    assert json.loads(request.body) == params


def test_empty_params_produce_empty_json_array(builder: RequestBuilder) -> None:
    request = builder.build("PingPong", "ping", {})
    assert request.body == "[]"


def test_unknown_params_passed_flat_without_envelope(builder: RequestBuilder) -> None:
    params: dict[str, object] = {
        "address": {"city": "Test"},
        "unknownFutureParam": True,
        "anotherUnknown": {"nested": "value"},
    }
    request = builder.build("Geocoder", "geocode", params)
    decoded = json.loads(request.body)
    assert "address" in decoded
    assert "unknownFutureParam" in decoded
    assert "anotherUnknown" in decoded
    assert "extra" not in decoded
    assert "extended" not in decoded
    assert "params" not in decoded
