import json

import pytest

from automapa_map_services.exceptions import (
    AuthenticationException,
    ExceptionMapper,
    ServerException,
    UnknownResponseException,
)
from automapa_map_services.http.response import HttpResponse
from automapa_map_services.response.api_response import ApiResponse
from automapa_map_services.response.parser import ResponseParser


@pytest.fixture
def parser() -> ResponseParser:
    return ResponseParser(ExceptionMapper())


def test_parses_successful_response(parser: ResponseParser) -> None:
    body = json.dumps({"result": {"city": "Warszawa", "x": 21.01}})
    response = HttpResponse(status_code=200, body=body)
    api_response = parser.parse(response, {"service": "Geocoder", "method": "geocode"})
    assert isinstance(api_response, ApiResponse)
    assert api_response.status() == 200
    assert api_response.data() == {"city": "Warszawa", "x": 21.01}
    assert api_response.meta()["service"] == "Geocoder"


def test_raw_always_contains_full_response_including_unknown_fields(parser: ResponseParser) -> None:
    full_body = {"result": {"city": "Gdańsk"}, "unknownTopLevelField": "preserved"}
    response = HttpResponse(status_code=200, body=json.dumps(full_body))
    api_response = parser.parse(response)
    assert api_response.raw() == full_body
    assert "unknownTopLevelField" in api_response.raw()


def test_throws_authentication_exception_on_401(parser: ResponseParser) -> None:
    response = HttpResponse(
        status_code=401,
        body=json.dumps({"message": "Invalid API key"}),
    )
    with pytest.raises(AuthenticationException):
        parser.parse(response)


def test_throws_server_exception_on_500(parser: ResponseParser) -> None:
    response = HttpResponse(
        status_code=500,
        body=json.dumps({"message": "Internal server error"}),
    )
    with pytest.raises(ServerException):
        parser.parse(response)


def test_throws_unknown_response_exception_on_malformed_body(parser: ResponseParser) -> None:
    response = HttpResponse(status_code=200, body="not-valid-json{{{")
    with pytest.raises(UnknownResponseException, match="non-JSON"):
        parser.parse(response)


def test_unknown_response_exception_preserves_original_json_exception(
    parser: ResponseParser,
) -> None:
    response = HttpResponse(status_code=502, body="<html>Bad Gateway</html>")
    with pytest.raises(UnknownResponseException) as exc_info:
        parser.parse(response)
    e = exc_info.value
    assert e.code == 502
    assert isinstance(e.__cause__, json.JSONDecodeError)
    assert "502" in str(e)
