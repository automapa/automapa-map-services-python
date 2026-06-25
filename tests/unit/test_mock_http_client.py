import pytest

from automapa_map_services.exceptions import NetworkException
from automapa_map_services.http.request import HttpRequest
from automapa_map_services.http.response import HttpResponse
from tests.support.mock_http_client import MockHttpClient


def test_add_response_matches_endpoint_path_and_records_payload() -> None:
    client = MockHttpClient()
    client.add_response("Geocoder", "geocode", {"result": {"city": "Warszawa"}})

    response = client.send(
        HttpRequest(
            method="POST",
            url="https://api.automapa.pl/v3/Geocoder/geocode",
            headers={"Content-Type": "application/json"},
            body='{"address":{"city":"Warszawa"}}',
        )
    )

    assert response.status_code == 200
    assert response.body == '{"result":{"city":"Warszawa"}}'
    assert client.get_last_request_payload() == {"address": {"city": "Warszawa"}}
    assert client.get_request_count() == 1


def test_add_sequence_dequeues_fifo() -> None:
    client = MockHttpClient()
    client.add_sequence(
        "Session",
        "getSalt",
        [
            {"statusCode": 200, "body": {"result": {"salt": "one"}}},
            {"statusCode": 200, "body": {"result": {"salt": "two"}}},
        ],
    )
    request = HttpRequest("POST", "https://api.automapa.pl/v3/Session/getSalt", {}, "[]")

    assert client.send(request).body == '{"result":{"salt":"one"}}'
    assert client.send(request).body == '{"result":{"salt":"two"}}'


def test_raw_response_wildcard_is_used_when_endpoint_missing() -> None:
    client = MockHttpClient()
    client.add_raw_response(500, {"message": "Server error"})

    response = client.send(HttpRequest("POST", "https://api.automapa.pl/v3/Foo/bar", {}, "[]"))

    assert response.status_code == 500
    assert response.body == '{"message":"Server error"}'


def test_network_failure_is_raised() -> None:
    client = MockHttpClient()
    client.add_network_failure("Connection refused", 7)

    with pytest.raises(NetworkException):
        client.send(HttpRequest("POST", "https://api.automapa.pl/v3/Foo/bar", {}, "[]"))


def test_queue_accepts_explicit_response() -> None:
    client = MockHttpClient()
    client.queue("/v3/Foo/bar", HttpResponse(202, '{"result":"accepted"}'))

    response = client.send(HttpRequest("POST", "https://api.automapa.pl/v3/Foo/bar", {}, "[]"))

    assert response.status_code == 202
    assert response.body == '{"result":"accepted"}'
