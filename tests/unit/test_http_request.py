from automapa_map_services.http.request import HttpRequest


def test_getters_return_constructor_values() -> None:
    request = HttpRequest(
        method="POST",
        url="https://api.automapa.pl/v3/Geocoder/geocode",
        headers={"Content-Type": "application/json", "Session-Id": "abc123"},
        body='{"address":"Warszawa"}',
    )

    assert request.method == "POST"
    assert request.url == "https://api.automapa.pl/v3/Geocoder/geocode"
    assert request.headers == {"Content-Type": "application/json", "Session-Id": "abc123"}
    assert request.body == '{"address":"Warszawa"}'


def test_body_defaults_to_empty_string() -> None:
    request = HttpRequest(
        method="POST",
        url="https://api.automapa.pl/v3/PingPong/ping",
        headers={},
    )

    assert request.body == ""
